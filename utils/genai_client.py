# utils/genai_client.py
import os
try:
    import google.generativeai as genai  # type: ignore
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# Global model instance
_model = None

def get_generative_model():
    """Get GenerativeModel instance with lazy initialization."""
    global _model
    if _model is None:
        # Configure only when needed
        api_key = os.getenv("GENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GENAI_MODEL", "gemini-pro")
        
        if api_key and GENAI_AVAILABLE and genai is not None:
            try:
                genai.configure(api_key=api_key)  # type: ignore
                _model = genai.GenerativeModel(model_name)  # type: ignore
            except Exception as e:
                print(f"Warning: Failed to configure GenAI: {e}")
                _model = _create_mock_model()
        else:
            # Return a mock for testing without API key or if genai is not available
            print("Warning: Using mock GenAI model (no API key or genai package not available)")
            _model = _create_mock_model()
    return _model

def _create_mock_model():
    """Create a mock model for testing purposes."""
    class MockModel:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self, text_content):
                    self.text = text_content
            return MockResponse(f"Mock response for: {prompt[:50]}...")
    return MockModel()

# Example of where to add ADK tool definitions for Generative AI
def get_spending_insights(receipt_data: dict) -> str:
    """Analyzes spending data to provide insights and budget forecasts."""
    try:
        model = get_generative_model()
        prompt = f"Analyze this receipt and provide spending insights: {receipt_data}"
        response = model.generate_content(prompt)
        
        # Handle both real and mock responses
        if hasattr(response, 'text'):
            return response.text
        else:
            return str(response)
    except Exception as e:
        return f"Error generating spending insights: {str(e)}"
