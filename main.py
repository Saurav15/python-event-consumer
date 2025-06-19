"""
main.py
Entry point for the event consumer service.
"""
from app.rabbitmq.consumer import start_rabbitmq_consumer

if __name__ == "__main__":
    start_rabbitmq_consumer()
