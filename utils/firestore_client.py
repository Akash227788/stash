# utils/firestore_client.py
import os
from google.cloud import firestore

def get_firestore_client():
    """
    Initializes and returns a Firestore client.
    """
    # The client uses the project ID from the environment automatically.
    return firestore.Client()
