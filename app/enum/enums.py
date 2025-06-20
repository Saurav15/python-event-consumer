"""
enums.py
Enum definitions for the event consumer.
"""
from enum import Enum

class IngestionStatus(str, Enum):
    PENDING = 'pending'
    STARTED = 'started'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed' 