"""
s3_utils.py
Provides utilities for interacting with AWS S3.
"""
import boto3
from app.config import settings

def download_from_s3(s3_key, destination_path):
    """Download a file from S3 to the given destination path using boto3. Expects bucket from config and s3_key as the object path."""
    bucket = settings.get_s3_bucket()
    if not bucket:
        raise ValueError("S3 bucket name is not set in environment variables!")
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.get_aws_access_key_id(),
        aws_secret_access_key=settings.get_aws_secret_access_key(),
        region_name=settings.get_aws_region(),
    )
    try:
        s3.download_file(bucket, s3_key, destination_path)
        print(f"Downloaded {s3_key} from bucket {bucket} to {destination_path}")
    except Exception as e:
        print(f"Failed to download {s3_key} from S3 bucket {bucket}: {e}")
        raise 