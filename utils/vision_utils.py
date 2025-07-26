# utils/vision_utils.py
from google.cloud import vision
import os

# Initialize client only when needed
def get_vision_client():
    """Get Vision client with proper authentication."""
    # Check if Vision API is enabled
    vision_enabled = os.getenv("VISION_API_ENABLED", "true").lower() == "true"
    if not vision_enabled:
        print("Vision API is disabled via environment configuration")
        return None
        
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            project_id = os.getenv("FIRESTORE_PROJECT_ID") or os.getenv("PROJECT_ID")
            if project_id:
                return vision.ImageAnnotatorClient()
            else:
                return vision.ImageAnnotatorClient()
        except Exception as e:
            print(f"Failed to initialize Vision client: {e}")
            return None
    else:
        # Return None for testing without credentials
        print("No Vision API credentials found, using mock responses")
        return None

def detect_text(image_uri):
    """
    Performs text detection on an image.
    In a real implementation, image_uri would be a GCS URI.
    """
    vision_client = get_vision_client()
    if not vision_client:
        # Mock response for testing
        mock_enabled = os.getenv("MOCK_VISION_API", "false").lower() == "true"
        if mock_enabled:
            return {"text": "Sample receipt text for testing purposes", "mock": True}
        else:
            return {"text": "", "error": "Vision API not available", "mock": False}
    
    try:
        # Get confidence threshold from environment
        confidence_threshold = float(os.getenv("VISION_CONFIDENCE_THRESHOLD", "0.7"))
        max_results = int(os.getenv("VISION_MAX_RESULTS", "50"))
        
        # Create image object for Vision API
        image = vision.Image(source=vision.ImageSource(image_uri=image_uri))
        # Use the correct Vision API method name
        response = vision_client.text_detection(image=image)  # type: ignore
        
        # Check for errors in the response
        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")
        
        # Extract text from the response with confidence filtering
        if response.text_annotations:
            full_text = response.text_annotations[0].description
            # Filter annotations by confidence if available
            filtered_annotations = []
            for annotation in response.text_annotations[:max_results]:
                # Some annotations might not have confidence scores
                if not hasattr(annotation, 'confidence') or annotation.confidence >= confidence_threshold:
                    filtered_annotations.append(annotation)
            
            return {
                "text": full_text, 
                "annotations": filtered_annotations,
                "total_annotations": len(response.text_annotations),
                "filtered_count": len(filtered_annotations)
            }
        else:
            return {"text": "", "annotations": [], "total_annotations": 0}
            
    except AttributeError:
        # Fallback if the method name is different
        try:
            response = vision_client.document_text_detection(image=image)  # type: ignore
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            return {"text": response.full_text_annotation.text if response.full_text_annotation else ""}
        except Exception as e:
            print(f"Vision API error: {e}")
            return {"text": f"Error processing image: {str(e)}", "error": str(e)}

# Example of where to add ADK tool definitions for Vision
def extract_text_from_image(image_url: str):
    """Extracts text from an image using the Vision API."""
    # In a real tool, you would handle the GCS URI
    return detect_text(image_url)
