"""
consumer.py
RabbitMQ consumer logic. Starts the consumer and binds the process_message callback.
"""
import pika
import time
from app.config import settings
from app.rabbitmq.process_message import process_message

MAX_RETRIES = 60  # or higher
RETRY_DELAY = 5   # seconds

def start_rabbitmq_consumer():
    """Start the RabbitMQ consumer and listen for messages on the ingestion queue. Retries connection if RabbitMQ is not ready."""
    params = pika.URLParameters(settings.get_rabbitmq_url())
    connection = None
    for i in range(MAX_RETRIES):
        try:
            connection = pika.BlockingConnection(params)
            print(f"[INFO] Connected to RabbitMQ on attempt {i+1}.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"[WARN] RabbitMQ not ready, retrying ({i+1}/{MAX_RETRIES}) in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    else:
        print(f"[ERROR] Could not connect to RabbitMQ after {MAX_RETRIES} attempts.")
        exit(1)
    channel = connection.channel()
    channel.queue_declare(queue=settings.get_document_ingestion_queue(), durable=True)
    channel.queue_declare(queue=settings.get_document_status_queue(), durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.get_document_ingestion_queue(), on_message_callback=process_message)
    print(f'Waiting for messages in {settings.get_document_ingestion_queue()}...')
    channel.start_consuming() 