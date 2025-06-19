import pika
import json
import tempfile
import os
from .config import get_rabbitmq_url, get_document_ingestion_queue, get_document_status_queue, get_aws_config
from .s3_utils import download_from_s3
from .pdf_analyzer import extract_text_from_pdf, summarize_text_with_gemini
from enum import Enum

DLQ_QUEUE = 'document_status_update_dlq'  # Use your actual DLQ queue name
STATUS_UPDATE_QUEUE = 'document_status_queue'

class IngestionStatus(str, Enum):
    PENDING = 'pending'
    STARTED = 'started'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

def publish_status_update(channel, result):
    message = {
        "pattern": "document_status_update",
        "data": result
    }
    # // Pretty print the message for debugging
    print(f"Publishing status update: {json.dumps(message, indent=2)}")
    channel.basic_publish(
        exchange='',
        routing_key=STATUS_UPDATE_QUEUE,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print("Published status update with event and data keys")

def send_to_dlq(channel, original_body, error_message):
    dlq_event = {
        'event': 'PROCESSING_FAILED',
        'error': error_message,
        'original_body': original_body.decode() if isinstance(original_body, bytes) else str(original_body)
    }
    channel.basic_publish(
        exchange='',
        routing_key=DLQ_QUEUE,
        body=json.dumps(dlq_event)
    )
    print(f"Sent failed event to DLQ: {dlq_event}")

def process_message(ch, method, properties, body):
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
        print(f"Received event for document_id={document_id}, s3_key={s3_key}, attempt_id={attempt_id}, user_id={user_id}")
        if not isinstance(s3_key, str) or not s3_key:
            raise ValueError(f"s3_key is not a valid string: {s3_key}")
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            print(f"About to download from S3: s3_key={s3_key}, tmp_file={tmp_path}")
            try:
                download_from_s3(s3_key, tmp_path)
            except Exception as s3err:
                raise RuntimeError(f"Failed to download from S3: {s3err}")
            text = extract_text_from_pdf(tmp_path)
            # summary = summarize_text_with_gemini(text)
            summary = "Yoo"
            print(f"Summary generated for document_id={document_id}: {summary[:100]}...")  # Print first 100 chars of summary
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        result = {
            'documentId': document_id,
            'status': IngestionStatus.COMPLETED,  # Use Enum for status
            'details': 'Document analysis completed',
            'summary': summary,
            'attemptId': attempt_id,
            'userId': user_id,
        } 
        publish_status_update(ch, result)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        send_to_dlq(ch, body, str(e))

def start_rabbitmq_consumer():
    params = pika.URLParameters(get_rabbitmq_url())
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    # Declare the ingestion queue
    channel.queue_declare(queue=get_document_ingestion_queue(), durable=True)
    
    # Declare the status queue (NestJS will handle the binding)
    channel.queue_declare(queue=get_document_status_queue(), durable=True)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=get_document_ingestion_queue(), on_message_callback=process_message)
    print(f'Waiting for messages in {get_document_ingestion_queue()}...')
    channel.start_consuming() 