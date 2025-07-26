# utils/firestore_client.py
import os
from google.cloud import firestore

def get_firestore_client():
    """
    Initializes and returns a Firestore client.
    Uses PROJECT_ID or FIRESTORE_PROJECT_ID from environment.
    """
    project_id = os.getenv("FIRESTORE_PROJECT_ID") or os.getenv("PROJECT_ID")
    
    if project_id:
        return firestore.Client(project=project_id)
    else:
        # Use default project from environment or service account
        return firestore.Client()
