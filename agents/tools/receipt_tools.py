# agents/tools/receipt_tools.py
"""
ADK-style tools for receipt processing.
"""
import json
import uuid
import datetime
from typing import Dict, Any, Optional
from functools import wraps
from utils.vision_utils import detect_text
from utils.firestore_client import get_firestore_client
from utils.pubsub_client import publish_message
from utils.genai_client import get_generative_model


def tool(func):
    """Simple tool decorator following ADK patterns."""
    class ToolWrapper:
        def __init__(self, func):
            self.func = func
            self.is_tool = True
            self.tool_name = func.__name__
            self.tool_description = func.__doc__
            # Copy function attributes
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
        
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
    
    return ToolWrapper(func)


@tool
def extract_receipt_text(image_url: str) -> Dict[str, Any]:
    """
    Extracts text from a receipt image using Google Cloud Vision API.
    
    Args:
        image_url: URL or GCS path to the receipt image
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    try:
        vision_response = detect_text(image_url)
        
        # Handle mock response (dict) vs real Vision API response
        if isinstance(vision_response, dict):
            # Mock response case
            return {
                "success": True,
                "extracted_text": vision_response.get("text", ""),
                "confidence": 0.9
            }
        
        # Real Vision API response case
        if not hasattr(vision_response, 'text_annotations') or not vision_response.text_annotations:
            return {
                "success": False,
                "error": "No text found in image",
                "extracted_text": ""
            }
        
        full_text = vision_response.full_text_annotation.text if hasattr(vision_response, 'full_text_annotation') else ""
        
        return {
            "success": True,
            "extracted_text": full_text,
            "confidence": vision_response.text_annotations[0].confidence if vision_response.text_annotations else 0.0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "extracted_text": ""
        }


@tool
def parse_receipt_data(text: str) -> Dict[str, Any]:
    """
    Parses receipt text to extract structured data using LLM.
    
    Args:
        text: Raw text extracted from receipt
        
    Returns:
        Dictionary containing parsed receipt data
    """
    try:
        model = get_generative_model()
        
        prompt = f"""
        Extract the merchant name, a list of items (with prices), and the total amount 
        from the following receipt text. Return the result as a JSON object with keys 
        'merchant', 'items', and 'total'. Items should be a list of objects with 'name' and 'price'.

        Receipt Text:
        {text}

        JSON Output:
        """
        
        response = model.generate_content(prompt)
        
        # Clean and parse the response
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        parsed_data = json.loads(response_text)
        
        return {
            "success": True,
            "merchant": parsed_data.get("merchant", "Unknown"),
            "items": parsed_data.get("items", []),
            "total": parsed_data.get("total", "0.00"),
            "raw_response": response_text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "merchant": "Unknown",
            "items": [],
            "total": "0.00"
        }


@tool
def store_receipt_data(user_id: str, receipt_data: Dict[str, Any], image_url: str) -> Dict[str, Any]:
    """
    Stores processed receipt data in Firestore.
    
    Args:
        user_id: ID of the user who uploaded the receipt
        receipt_data: Parsed receipt data
        image_url: URL of the original receipt image
        
    Returns:
        Dictionary containing storage result and receipt ID
    """
    try:
        firestore_client = get_firestore_client()
        receipt_id = str(uuid.uuid4())
        
        complete_receipt_data = {
            "userId": user_id,
            "receiptId": receipt_id,
            "merchant": receipt_data.get("merchant", "Unknown"),
            "items": receipt_data.get("items", []),
            "total": receipt_data.get("total", "0.00"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "imageUrl": image_url,
            "processed": True
        }
        
        # Store in Firestore
        firestore_client.collection("receipts").document(receipt_id).set(complete_receipt_data)
        
        return {
            "success": True,
            "receipt_id": receipt_id,
            "data": complete_receipt_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "receipt_id": None
        }


@tool
def publish_receipt_processed_event(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publishes a receipt processed event to Pub/Sub for downstream processing.
    
    Args:
        receipt_data: Complete receipt data to publish
        
    Returns:
        Dictionary containing publish result
    """
    try:
        import os
        
        project_id = os.getenv("FIRESTORE_PROJECT_ID", "local-dev")
        topic_id = "receipt-processed"
        
        # Publish message
        message_data = json.dumps(receipt_data).encode("utf-8")
        publish_message(project_id, topic_id, message_data)
        
        return {
            "success": True,
            "message": "Receipt processed event published successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to publish receipt processed event"
        }
