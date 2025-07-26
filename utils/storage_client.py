# utils/storage_client.py
import os
from google.cloud import storage

def get_storage_client():
    """
    Initializes and returns a Storage client with proper project configuration.
    """
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        project_id = os.getenv("FIRESTORE_PROJECT_ID") or os.getenv("PROJECT_ID")
        if project_id:
            return storage.Client(project=project_id)
        else:
            return storage.Client()
    else:
        print("Warning: No Google Application Credentials found, using mock storage client")
        return None

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = get_storage_client()
    if not storage_client:
        # Mock response for testing
        print(f"Mock: Downloading gs://{bucket_name}/{source_blob_name} to {destination_file_name}")
        return destination_file_name
    
    # Use bucket name from environment if not provided
    if not bucket_name:
        bucket_name = os.getenv("GCLOUD_STORAGE_BUCKET") or os.getenv("GCS_BUCKET_NAME")
    
    if not bucket_name:
        raise ValueError("Bucket name not provided and not found in environment")
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")
    return destination_file_name

def upload_file(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage.
    """
    storage_client = get_storage_client()
    if not storage_client:
        # Mock response for testing
        print(f"Mock: Uploading {source_file_name} to gs://{bucket_name}/{destination_blob_name}")
        return f"gs://{bucket_name}/{destination_blob_name}"
    
    # Use bucket name from environment if not provided
    if not bucket_name:
        bucket_name = os.getenv("GCLOUD_STORAGE_BUCKET") or os.getenv("GCS_BUCKET_NAME")
    
    if not bucket_name:
        raise ValueError("Bucket name not provided and not found in environment")
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)
    
    print(f"File {source_file_name} uploaded to gs://{bucket_name}/{destination_blob_name}")
    return f"gs://{bucket_name}/{destination_blob_name}"
