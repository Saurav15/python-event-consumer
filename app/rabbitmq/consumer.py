"""
consumer.py
RabbitMQ consumer logic. Starts the consumer and binds the process_message callback.
"""
import pika
from app.config import settings
from app.rabbitmq.process_message import process_message

def start_rabbitmq_consumer():
    """Start the RabbitMQ consumer and listen for messages on the ingestion queue."""
    params = pika.URLParameters(settings.get_rabbitmq_url())
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=settings.get_document_ingestion_queue(), durable=True)
    channel.queue_declare(queue=settings.get_document_status_queue(), durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.get_document_ingestion_queue(), on_message_callback=process_message)
    print(f'Waiting for messages in {settings.get_document_ingestion_queue()}...')
    channel.start_consuming() 