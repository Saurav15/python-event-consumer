"""
process_message.py
Defines the process_message callback for RabbitMQ. Handles message processing, S3 download, PDF analysis, and publishing status updates.

This function expects a message with the following structure:
{
    "data": {
        "documentId": str,
        "s3Key": str,  # S3 object key (not URL)
        "attemptId": int,
        "userId": str
    }
}

On success, publishes a status update event with status 'completed'.
On failure, publishes a status update event with status 'failed' and error details.
"""
import json
import os
import tempfile
from app.aws.s3_utils import download_from_s3
from app.pdf_analyzer.analyzer import extract_text_from_pdf, summarize_text_with_gemini
from app.rabbitmq.publisher import publish_status_update
from app.enum.enums import IngestionStatus

def process_message(ch, method, properties,body):
    """
    Callback for processing a single RabbitMQ message.
    Downloads a PDF from S3, extracts text, summarizes, and publishes a status update event.
    On failure, publishes a failed status update event with error details.
    """
    try:
        if body is None:
            raise ValueError("Received empty message body (None)")
        event = json.loads(body)
        data = event.get('data', {})
        document_id = data.get('documentId')
        s3_key = data.get('s3Key')
        attempt_id = data.get('attemptId')
        user_id = data.get('userId')
        if not document_id or not s3_key:
            raise ValueError(f'Missing documentId or s3Key in event: {event}')
        print(f"[INFO] Processing document: {document_id}\n  S3 Key: {s3_key}\n  Attempt: {attempt_id}\n  User: {user_id}")
        if not isinstance(s3_key, str) or not s3_key:
            raise ValueError(f"s3_key is not a valid string: {s3_key}")
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            print(f"[INFO] Downloading from S3: {s3_key} -> {tmp_path}")
            try:
                download_from_s3(s3_key, tmp_path)
            except Exception as s3err:
                raise RuntimeError(f"Failed to download from S3: {s3err}")
            print(f"[INFO] Extracting text from PDF: {tmp_path}")
            text = extract_text_from_pdf(tmp_path)
            try:
                summary = summarize_text_with_gemini(text)
                print(f"[SUCCESS] Gemini summary generated for document {document_id} (first 100 chars): {summary[:100]}...")
            except Exception as gemini_err:
                print(f"[WARN] Gemini summarization failed, using full text. Reason: {gemini_err}")
                summary = text if text else "No summary available."
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        result = {
            'documentId': document_id,
            'status': IngestionStatus.COMPLETED,
            'details': 'Document analysis completed',
            'summary': summary,
            'attemptId': attempt_id,
            'userId': user_id,
        }
        publish_status_update(ch, result)
        print(f"[SUCCESS] Published completed status for document {document_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[ERROR] Failed to process document. Reason: {e}")
        # On error, publish a failed status update event
        result = {
            'documentId': data.get('documentId') if 'data' in locals() else None,
            'status': IngestionStatus.FAILED,
            'details': f'Failed to process document: {str(e)}',
            'summary': None,
            'attemptId': data.get('attemptId') if 'data' in locals() else None,
            'userId': data.get('userId') if 'data' in locals() else None,
            'error': str(e),
        }
        publish_status_update(ch, result)
        print(f"[ERROR] Published failed status for document {result['documentId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
