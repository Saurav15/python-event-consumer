"""
settings.py
Configuration loader for environment variables using python-dotenv and os.environ.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_rabbitmq_url():
    """Return the RabbitMQ connection URL from environment variables."""
    return os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

def get_document_ingestion_queue():
    """Return the name of the document ingestion queue."""
    return os.getenv('DOCUMENT_INGESTION_QUEUE', 'document_ingestion_queue')

def get_document_status_queue():
    """Return the name of the document status queue."""
    return os.getenv('DOCUMENT_STATUS_QUEUE', 'document_status_queue')

def get_dlq_queue():
    """Return the name of the dead letter queue (DLQ)."""
    return os.getenv('DLQ_QUEUE', 'document_dlq')

def get_aws_access_key_id():
    return os.getenv('AWS_ACCESS_KEY_ID')

def get_aws_secret_access_key():
    return os.getenv('AWS_SECRET_ACCESS_KEY')

def get_aws_region():
    return os.getenv('AWS_REGION', 'us-east-1')

def get_s3_bucket():
    """Return the S3 bucket name from environment variables."""
    return os.getenv('AWS_S3_BUCKET') 