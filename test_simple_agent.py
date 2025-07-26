# Test simple agent to understand ADK pattern
from google.adk.agents import LlmAgent
from typing import Optional, List, Callable

class SimpleTestAgent(LlmAgent):
    """Simple test agent following ADK patterns."""
    
    # Define class attributes for ADK
    name: str = "SimpleTestAgent"
    model_name: str = "gemini-pro"
    instruction: str = "You are a simple test agent."
    description: str = "A test agent for understanding ADK patterns"

if __name__ == "__main__":
    agent = SimpleTestAgent()
    print(f"✅ Agent created: {agent.name}")
    print(f"✅ Model: {agent.model_name}")
    print(f"✅ Instruction: {agent.instruction}")
