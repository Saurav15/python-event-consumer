import pika
import os
import time
from datetime import datetime
import json
import signal
import sys
import pathlib

HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
HEALTH_CHECK_FILE = os.getenv('HEALTH_CHECK_FILE', '/tmp/health.json')

def ensure_health_check_file():
    # Create directory if it doesn't exist
    pathlib.Path(os.path.dirname(HEALTH_CHECK_FILE)).mkdir(parents=True, exist_ok=True)
    # Create file if it doesn't exist
    if not os.path.exists(HEALTH_CHECK_FILE):
        with open(HEALTH_CHECK_FILE, 'w') as f:
            json.dump({"status": "initializing", "last_updated": datetime.now().isoformat()}, f)

def update_health_status(status="healthy", message="Service is running"):
    health_data = {
        "status": status,
        "last_updated": datetime.now().isoformat(),
        "message": message,
        "service": "python-event-consumer"
    }
    try:
        ensure_health_check_file()
        with open(HEALTH_CHECK_FILE, "w") as f:
            json.dump(health_data, f)
    except Exception as e:
        print(f"Error updating health status: {str(e)}")

def signal_handler(signum, frame):
    print("Received shutdown signal, updating health status...")
    update_health_status("shutting_down", "Service is shutting down")
    sys.exit(0)

def start_consumer():
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print("Consumer service started successfully!")
        print("RabbitMQ connection will be implemented later.")
        print("Current environment variables:")
        print(f"RABBITMQ_HOST: {os.getenv('RABBITMQ_HOST', 'localhost')}")
        print(f"RABBITMQ_PORT: {os.getenv('RABBITMQ_PORT', '5672')}")
        print(f"RABBITMQ_QUEUE: {os.getenv('RABBITMQ_QUEUE', 'documents_queue')}")
        
        # Initialize health check
        update_health_status()
        
        # Keep the service running and update health status
        while True:
            time.sleep(HEALTH_CHECK_INTERVAL)
            update_health_status()
            
    except Exception as e:
        update_health_status("unhealthy", f"Error: {str(e)}")
        raise
    
