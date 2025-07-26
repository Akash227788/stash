# Test receipt agent with correct ADK pattern
from google.adk.agents import LlmAgent

class TestReceiptAgent(LlmAgent):
    """Test receipt agent following ADK patterns."""
    
    # Define class attributes for ADK
    name: str = "TestReceiptAgent"
    model_name: str = "gemini-pro"
    instruction: str = "You are a receipt processing agent."
    description: str = "Processes receipt images to extract merchant, items, and financial data"

if __name__ == "__main__":
    agent = TestReceiptAgent()
    print(f"✅ Agent created: {agent.name}")
    print(f"✅ Model: {agent.model_name}")
    print(f"✅ Test successful!")
