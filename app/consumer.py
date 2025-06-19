import os
import signal
import sys
import json
import pathlib
from datetime import datetime
from .rabbitmq_consumer import start_rabbitmq_consumer

HEALTH_CHECK_FILE = os.getenv('HEALTH_CHECK_FILE', '/tmp/health.json')


def ensure_health_check_file():
    pathlib.Path(os.path.dirname(HEALTH_CHECK_FILE)).mkdir(parents=True, exist_ok=True)
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
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        print("Consumer service started successfully!")
        update_health_status()
        start_rabbitmq_consumer()
    except Exception as e:
        update_health_status("unhealthy", f"Error: {str(e)}")
        raise 