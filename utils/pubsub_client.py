# utils/pubsub_client.py
import os
import json
from google.cloud import pubsub_v1

def get_pubsub_client():
    """Get Pub/Sub client with proper authentication."""
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return pubsub_v1.PublisherClient()
    else:
        # Return a mock client for testing without credentials
        return None

def publish_message(project_id, topic_id, data):
    """
    Publishes a message to a Pub/Sub topic.
    """
    publisher = get_pubsub_client()
    if not publisher:
        # Mock response for testing
        print(f"Mock: Publishing message to {project_id}/{topic_id}")
        return {"message_id": "mock-message-id"}
    
    # Use project ID from environment if not provided
    if not project_id:
        project_id = os.getenv("FIRESTORE_PROJECT_ID") or os.getenv("PROJECT_ID")
    
    if not project_id:
        raise ValueError("Project ID not provided and not found in environment")
    
    topic_path = publisher.topic_path(project_id, topic_id)
    
    # Data must be a bytestring
    if isinstance(data, dict):
        data = json.dumps(data).encode("utf-8")

    future = publisher.publish(topic_path, data)
    message_id = future.result()
    print(f"Published message ID: {message_id}")
    return {"message_id": message_id}
