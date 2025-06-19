"""
publisher.py
Publishes document status updates to the status queue.
"""
import json
import pika
from app.config import settings

STATUS_UPDATE_QUEUE = settings.get_document_status_queue()

def publish_status_update(channel, result):
    """Publish a document status update message to the status queue."""
    message = {
        "pattern": "document_status_update",
        "data": result
    }
    channel.basic_publish(
        exchange='',
        routing_key=STATUS_UPDATE_QUEUE,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print("Published status update with event and data keys") 