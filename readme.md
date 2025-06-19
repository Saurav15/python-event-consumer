# Python Event Consumer

## Overview

This service is a Python-based event consumer that listens to document ingestion events from a RabbitMQ queue, processes PDF files from AWS S3, generates summaries (optionally using Gemini AI), and sends status updates back to the backend service.

---

## Architectural Flow

1. The Backend Service publishes a `document_ingestion` event.
2. The Python Event Consumer receives the event.
3. The Python Event Consumer downloads the PDF from the S3 Bucket.
4. The Python Event Consumer extracts text and summarizes it (optionally using Gemini AI).
5. The Python Event Consumer publishes a `document_status_update` event back to the Backend Service.

---

- **Backend Service**: Publishes ingestion events to RabbitMQ and receives status updates.
- **Python Event Consumer**: Listens for events, processes documents, and sends status updates.
- **S3 Bucket**: Stores PDF files to be processed.
- **Gemini AI**: (Optional) Used for advanced summarization.

---

## Prerequisites

- **Python 3.8+** (recommended: Python 3.10 or newer)
- **pip** (Python package manager)
- **RabbitMQ** instance (local or remote)
- **AWS S3 bucket** and credentials
- (Optional) **Google Gemini API key** for advanced summarization

---

## How It Works

1. **Backend** publishes a `document_ingestion` event to RabbitMQ with document details and S3 key.
2. **Python Event Consumer** receives the event, downloads the PDF from S3, extracts text, and (optionally) summarizes it using Gemini.
3. The consumer publishes a `document_status_update` event back to RabbitMQ, which the backend listens for to update the document's status.

---

## Environment Variables

Create a `.env` file (see `.env.example`) with the following:

```
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
DOCUMENT_INGESTION_QUEUE=document_ingestion_queue
DOCUMENT_STATUS_QUEUE=document_status_queue
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
GEMINI_API_KEY=your-gemini-api-key  # Optional, for Gemini summarization
```

---

## Setup & Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd python-event-consumer
```

### 2. (Recommended) Create and activate a Python virtual environment

#### On **Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

#### On **macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

> **Tip:** If you see an error about `venv` not being found, make sure Python 3.8+ is installed and available in your PATH.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

- Copy `.env.example` to `.env` and fill in your values.

### 5. Run the service

```bash
python main.py
```

---

## Example Event Payloads

### Ingestion Event (from backend to consumer)

```json
{
  "pattern": "document_ingestion",
  "data": {
    "documentId": "abc-123",
    "userId": "user-xyz",
    "attemptId": 1,
    "s3Key": "users/user-xyz/documents/abc-123.pdf"
  }
}
```

### Status Update Event (from consumer to backend)

```json
{
  "pattern": "document_status_update",
  "data": {
    "documentId": "abc-123",
    "status": "completed",
    "details": "Document analysis completed",
    "summary": "...summary text...",
    "attemptId": 1,
    "userId": "user-xyz"
  }
}
```

---

## Error Handling

- If processing fails (e.g., S3 download error, PDF extraction error), the consumer publishes a `document_status_update` event with status `failed` and error details.
- The backend handles retries and DLQ logic.

---

## Extending with Gemini

- If `GEMINI_API_KEY` is set, the service will use Gemini AI to summarize extracted text.
- If Gemini is unavailable or fails, it falls back to the full extracted text.

---

## Troubleshooting

- **403 Forbidden from S3**: Check your AWS credentials and bucket permissions.
- **RabbitMQ connection errors**: Ensure RabbitMQ is running and accessible.
- **Gemini errors**: Ensure your API key is valid and the model is available.
- **Process shuts down with TypeError**: Ensure the `process_message` function has the correct signature: `(ch, method, properties, body)`.
- **venv activation issues**: If you see `command not found` or `is not recognized as an internal or external command`, ensure you are using the correct activation command for your OS and that your terminal is running with the correct permissions.

---

## License

MIT
