# adk_server.py
"""
ADK-based Stash Server demonstrating proper agent orchestration patterns.
This serves as an example of how to use the ADK agents in a production environment.
"""
import os
from typing import Dict, Any
try:
    from google.adk import Session  # type: ignore
    ADK_AVAILABLE = True
except ImportError:
    # Mock Session class for when ADK is not available
    class Session:
        def __init__(self, *args, **kwargs):
            self.state = {}
    ADK_AVAILABLE = False
from agents.root_agent import RootAgent
from agents.receipt_agent import ReceiptAgent
from agents.analytics_agent import AnalyticsAgent
from agents.game_agent import GameAgent
from agents.wallet_agent import WalletAgent


class StashADKServer:
    """
    ADK-powered Stash server demonstrating multi-agent coordination.
    """
    
    def __init__(self):
        # Initialize the root agent with proper ADK patterns
        self.root_agent = RootAgent()
        
        # Initialize individual agents for direct access if needed
        self.receipt_agent = ReceiptAgent()
        self.analytics_agent = AnalyticsAgent()
        self.game_agent = GameAgent()
        self.wallet_agent = WalletAgent()
    
    async def process_receipt_workflow(self, image_url: str, user_id: str) -> Dict[str, Any]:
        """
        Complete receipt processing workflow using ADK patterns.
        
        This demonstrates a sequential workflow:
        1. Process receipt -> 2. Award points -> 3. Update wallet
        """
        try:
            # Create ADK session for the workflow
            session = Session()
            
            # Step 1: Process receipt
            receipt_request = {
                "operation": "process_receipt",
                "imageUrl": image_url,
                "userId": user_id
            }
            
            receipt_result = await self.receipt_agent.process(receipt_request)
            
            if receipt_result["status"] != "success":
                return {
                    "status": "error",
                    "error": f"Receipt processing failed: {receipt_result.get('error')}",
                    "step": "receipt_processing"
                }
            
            # Step 2: Award points based on receipt data
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
            
            # Compile comprehensive workflow result
            return {
                "status": "success",
                "workflow_complete": True,
                "receipt_processing": receipt_result,
                "points_awarded": game_result,
                "wallet_status": wallet_result,
                "summary": self._generate_workflow_summary(receipt_result, game_result, wallet_result)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Workflow failed: {str(e)}",
                "step": "coordination"
            }
    
    async def generate_analytics_report(self, user_id: str) -> Dict[str, Any]:
        """Generate spending analytics using ADK agent."""
        request = {
            "operation": "generate_report",
            "userId": user_id
        }
        
        return await self.analytics_agent.process(request)
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user dashboard by coordinating multiple agents.
        This demonstrates parallel agent coordination.
        """
        try:
            # Get wallet balance
            wallet_request = {"operation": "get_balance", "userId": user_id}
            wallet_result = await self.wallet_agent.process(wallet_request)
            
            # Get analytics report
            analytics_request = {"operation": "generate_report", "userId": user_id}
            analytics_result = await self.analytics_agent.process(analytics_request)
            
            # Get achievements
            game_request = {"operation": "get_achievements", "userId": user_id}
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
                "dashboard": dashboard
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Dashboard generation failed: {str(e)}"
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


# Example usage demonstrating ADK patterns
async def main():
    """Example of using the ADK-based Stash server."""
    server = StashADKServer()
    
    # Example 1: Process a receipt with full workflow
    print("=== Processing Receipt Workflow ===")
    result = await server.process_receipt_workflow(
        image_url="gs://stash-receipts/example-receipt.jpg",
        user_id="user123"
    )
    print(f"Workflow Result: {result}")
    
    # Example 2: Generate analytics report
    print("\n=== Generating Analytics Report ===")
    analytics = await server.generate_analytics_report("user123")
    print(f"Analytics: {analytics}")
    
    # Example 3: Get user dashboard
    print("\n=== Getting User Dashboard ===")
    dashboard = await server.get_user_dashboard("user123")
    print(f"Dashboard: {dashboard}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
