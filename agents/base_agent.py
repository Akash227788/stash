# agents/base_agent.py
"""
Base agent configuration for the Stash system using official ADK patterns.
"""
import os
from typing import Dict, Any, Optional, List, Callable
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
try:
    from google.genai import types
except ImportError:
    types = None
from utils.genai_client import get_generative_model


class StashLlmAgent(LlmAgent):
    """
    Stash-specific LLM Agent extending official ADK LlmAgent.
    Provides custom processing methods while maintaining ADK compatibility.
    """
    
    def __init__(self, 
                 name: str,
                 model_name: Optional[str] = None,
                 instruction: str = "",
                 description: Optional[str] = None,
                 tools: Optional[List[Callable]] = None,
                 system_instruction: Optional[str] = None):
        """
        Initialize Stash LLM Agent with ADK patterns.
        """
        import os
        
        # Use environment variable for model if not specified
        if not model_name:
            model_name = os.getenv("GENAI_MODEL", "gemini-pro")
        
        # Use system_instruction if provided, otherwise use instruction
        final_instruction = system_instruction or instruction
        
        super().__init__(
            name=name,
            model=model_name,  # Use model name string instead of model instance
            instruction=final_instruction,
            description=description or f"{name} specialized agent for Stash financial management"
        )
        
        # Store additional attributes
        self.model_name = model_name
        self._tools = tools or []
    
    async def process_stash_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Stash-specific requests with consistent response format.
        
        Args:
            request: Request dictionary containing operation and parameters
            
        Returns:
            Dictionary with status, result, and agent information
        """
        try:
            # Extract message from request for ADK processing
            if isinstance(request, dict):
                if "message" in request:
                    message = request["message"]
                else:
                    # Convert request to a descriptive message
                    operation = request.get("operation", "unknown")
                    message = f"Handle operation: {operation} with parameters: {request}"
            else:
                message = str(request)
            
            # Use ADK's built-in processing
            # Note: In real ADK usage, you'd typically use session.run() or similar
            # This provides backward compatibility with existing Stash patterns
            response = await self._generate_response(message, request)
            
            return {
                "status": "success",
                "response": response,
                "agent": self.name,
                "request": request
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "agent": self.name,
                "request": request
            }
    
    async def _generate_response(self, message: str, request: Dict[str, Any]) -> str:
        """
        Generate response using the underlying model.
        This is a simplified version - in production you'd use ADK sessions.
        """
        # Build context-aware prompt
        prompt = self._build_context_prompt(message, request)
        
        # Generate using the configured model
        model = get_generative_model()
        response = model.generate_content(prompt)
        
        return response.text if hasattr(response, 'text') else str(response)
    
    def _build_context_prompt(self, message: str, request: Dict[str, Any]) -> str:
        """Build a contextualized prompt for the agent."""
        prompt_parts = [
            f"Agent Instructions: {self.instruction}",
            f"Agent Name: {self.name}",
            "",
            f"User Request: {message}",
            "",
            "Additional Context:",
            f"- Operation: {request.get('operation', 'N/A')}",
            f"- Request Data: {request}",
            "",
            "Response (provide helpful, accurate information based on your role):"
        ]
        
        return "\n".join(prompt_parts)
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard process method that delegates to process_stash_request.
        This provides compatibility with different calling patterns.
        """
        return await self.process_stash_request(request)

    
class StashSequentialAgent(SequentialAgent):
    """
    Stash-specific Sequential Agent for workflow orchestration.
    """
    
    def __init__(self, name: str, sub_agents: List, description: Optional[str] = None):
        super().__init__(
            name=name,
            sub_agents=sub_agents,
            description=description or f"{name} sequential workflow agent"
        )


class StashParallelAgent(ParallelAgent):
    """
    Stash-specific Parallel Agent for concurrent execution.
    """
    
    def __init__(self, name: str, sub_agents: List, description: Optional[str] = None):
        super().__init__(
            name=name,
            sub_agents=sub_agents,
            description=description or f"{name} parallel execution agent"
        )
