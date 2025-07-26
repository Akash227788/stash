# agents/root_agent.py
"""
ADK-based Root Agent for coordinating all Stash system operations.
"""
from typing import Dict, Any, Optional
from agents.base_agent import StashLlmAgent, StashSequentialAgent
from agents.receipt_agent import ReceiptAgent
from agents.analytics_agent import AnalyticsAgent
from agents.game_agent import GameAgent
from agents.wallet_agent import WalletAgent


class RootAgent(StashLlmAgent):
    """Root coordinator agent implementing ADK multi-agent patterns."""
    
    def __init__(self):
        instruction = """You are the Root Agent for the Stash financial management system. You coordinate between specialized agents
        to provide comprehensive financial services.
        
        Available specialized agents:
        1. ReceiptAgent - Processes receipt images and extracts financial data
        2. AnalyticsAgent - Provides spending insights and financial analysis
        3. GameAgent - Manages gamification, points, and achievements
        4. WalletAgent - Handles point balances, transactions, and redemptions
        
        Your role is to:
        1. Route user requests to the appropriate specialized agent
        2. Coordinate multi-agent workflows when needed
        3. Provide unified responses combining multiple agent outputs
        4. Handle general queries about the Stash system
        5. Ensure smooth user experience across all features
        
        When a user uploads a receipt, coordinate the following workflow:
        1. ReceiptAgent processes the image and extracts data
        2. GameAgent awards points based on the receipt data
        3. WalletAgent updates the user's balance
        4. Provide a unified response with processing results and point awards
        
        For analytics requests, delegate to AnalyticsAgent.
        For wallet operations, delegate to WalletAgent.
        For gamification features, delegate to GameAgent.
        
        Always provide helpful, coordinated responses that demonstrate the value of the Stash system.
        """
        
        super().__init__(
            name="RootAgent",
            instruction=instruction,
            description="Main coordinator for all Stash financial management operations"
        )
        
        # Initialize specialized agents
        self.receipt_agent = ReceiptAgent()
        self.analytics_agent = AnalyticsAgent()
        self.game_agent = GameAgent()
        self.wallet_agent = WalletAgent()
        
        # Agent routing map
        self.agent_routes = {
            "receipt": self.receipt_agent,
            "analytics": self.analytics_agent,
            "game": self.game_agent,
            "wallet": self.wallet_agent
        }
    
    async def process_receipt_workflow(self, image_url: str, user_id: str) -> Dict[str, Any]:
        """
        Orchestrate the complete receipt processing workflow.
        
        This follows ADK Sequential Agent patterns where multiple agents work in sequence.
        
        Args:
            image_url: URL of the receipt image
            user_id: ID of the user uploading the receipt
            
        Returns:
            Dictionary containing complete workflow results
        """
        try:
            # Log workflow start (using print instead of memory)
            print(f"Starting receipt workflow for user {user_id}")
            
            # Step 1: Process receipt with ReceiptAgent
            receipt_request = {
                "operation": "process_receipt",
                "imageUrl": image_url,
                "userId": user_id
            }
            
            receipt_result = await self.receipt_agent.process(receipt_request)
            
            if receipt_result["status"] != "success":
                return {
                    "status": "error",
                    "error": f"Receipt processing failed: {receipt_result.get('error', 'Unknown error')}",
                    "workflow_step": "receipt_processing",
                    "agent": self.name
                }
            
            # Step 2: Award points with GameAgent
            game_request = {
                "operation": "award_points",
                "userId": user_id,
                "receiptData": receipt_result.get("data", {})
            }
            
            game_result = await self.game_agent.process(game_request)
            
            # Step 3: Get updated wallet balance
            wallet_request = {
                "operation": "get_balance",
                "userId": user_id
            }
            
            wallet_result = await self.wallet_agent.process(wallet_request)
            
            # Compile comprehensive response
            workflow_summary = self._generate_workflow_summary(
                receipt_result, game_result, wallet_result
            )
            
            return {
                "status": "success",
                "workflow_complete": True,
                "receipt_processing": receipt_result,
                "points_awarded": game_result,
                "wallet_status": wallet_result,
                "summary": workflow_summary,
                "agent": self.name
            }
            
        except Exception as e:
            error_msg = f"Receipt workflow failed: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "workflow_step": "coordination",
                "agent": self.name
            }
    
    def _generate_workflow_summary(self, receipt_result: Dict[str, Any], 
                                  game_result: Dict[str, Any], 
                                  wallet_result: Dict[str, Any]) -> str:
        """Generate a user-friendly summary of the workflow results."""
        summary_parts = ["✅ Receipt Successfully Processed!"]
        
        # Receipt processing summary
        if receipt_result["status"] == "success":
            data = receipt_result.get("data", {})
            merchant = data.get("merchant", "Unknown")
            total = data.get("total", "N/A")
            items_count = len(data.get("items", []))
            
            summary_parts.extend([
                f"🏪 Merchant: {merchant}",
                f"💵 Total: {total}",
                f"📝 Items processed: {items_count}"
            ])
        
        # Points summary
        if game_result["status"] == "success":
            points = game_result.get("points_awarded", 0)
            balance = game_result.get("new_balance", 0)
            message = game_result.get("message", "")
            
            summary_parts.extend([
                f"🎉 Points earned: {points}",
                f"💰 New balance: {balance} points"
            ])
            
            if message:
                summary_parts.append(message)
        
        return "\n".join(summary_parts)
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Create a comprehensive user dashboard by coordinating multiple agents.
        
        This follows ADK Parallel Agent patterns where multiple agents work simultaneously.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing dashboard data from all agents
        """
        try:
            print(f"Building dashboard for user {user_id}")
            
            # Parallel requests to different agents
            wallet_request = {"operation": "get_balance", "userId": user_id}
            analytics_request = {"operation": "spending_report", "userId": user_id}
            game_request = {"operation": "get_achievements", "userId": user_id}
            
            # Execute requests (in a real ADK implementation, these would be parallel)
            wallet_result = await self.wallet_agent.process(wallet_request)
            analytics_result = await self.analytics_agent.process(analytics_request)
            game_result = await self.game_agent.process(game_request)
            
            # Compile dashboard
            dashboard = {
                "user_id": user_id,
                "wallet": {
                    "balance": wallet_result.get("balance", 0) if wallet_result["status"] == "success" else 0,
                    "status": wallet_result["status"]
                },
                "analytics": {
                    "summary": analytics_result.get("report", {}).get("spending_summary", {}) if analytics_result["status"] == "success" else {},
                    "status": analytics_result["status"]
                },
                "gamification": {
                    "achievements": game_result.get("progress", {}).get("achievements", []) if game_result["status"] == "success" else [],
                    "stats": game_result.get("progress", {}).get("stats", {}) if game_result["status"] == "success" else {},
                    "status": game_result["status"]
                }
            }
            
            return {
                "status": "success",
                "dashboard": dashboard,
                "agent": self.name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    def _route_to_agent(self, agent_type: str) -> Optional[StashLlmAgent]:
        """Route request to the appropriate specialized agent."""
        return self.agent_routes.get(agent_type.lower())
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requests by routing to appropriate agents or handling coordination.
        
        Args:
            request: Request containing operation type and parameters
            
        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "")
        
        # Handle multi-agent workflows
        if operation == "process_receipt":
            image_url = request.get("imageUrl")
            user_id = request.get("userId")
            
            if not image_url or not user_id:
                return {
                    "status": "error",
                    "error": "imageUrl and userId are required for receipt processing",
                    "agent": self.name
                }
            
            return await self.process_receipt_workflow(image_url, user_id)
        
        elif operation == "get_dashboard":
            user_id = request.get("userId")
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required for dashboard",
                    "agent": self.name
                }
            
            return await self.get_user_dashboard(user_id)
        
        # Route to specialized agents
        elif "agent" in request:
            agent_type = request["agent"]
            agent = self._route_to_agent(agent_type)
            
            if agent:
                return await agent.process(request)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown agent type: {agent_type}",
                    "agent": self.name
                }
        
        # Handle general queries with LLM
        else:
            # Add system context about available capabilities
            enhanced_request = request.copy()
            enhanced_request["message"] = f"""
            {request.get('message', '')}
            
            Available capabilities:
            - Receipt processing and data extraction
            - Financial analytics and spending insights
            - Points and achievements system
            - Digital wallet and redemptions
            
            How can I help you with your financial management needs?
            """
            
            return await self.process_stash_request(enhanced_request)
