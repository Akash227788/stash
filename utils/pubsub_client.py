# utils/pubsub_client.py
import os
from google.cloud import pubsub_v1

def publish_message(project_id, topic_id, data):
    """
    Publishes a message to a Pub/Sub topic.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    
    # Data must be a bytestring
    if isinstance(data, dict):
        data = json.dumps(data).encode("utf-8")

    future = publisher.publish(topic_path, data)
    print(f"Published message ID: {future.result()}")
