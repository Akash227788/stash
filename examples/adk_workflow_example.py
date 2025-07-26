# examples/adk_workflow_example.py
"""
Comprehensive example demonstrating ADK agent patterns and workflows.
"""
import os
import asyncio
from typing import Dict, Any
try:
    from google.adk import Session, SequentialAgent, ParallelAgent  # type: ignore
    ADK_AVAILABLE = True
except ImportError:
    # Mock classes for when ADK is not available
    class Session:
        def __init__(self, *args, **kwargs):
            self.state = {}
    
    class SequentialAgent:
        def __init__(self, *args, **kwargs):
            pass
    
    class ParallelAgent:
        def __init__(self, *args, **kwargs):
            pass
    
    ADK_AVAILABLE = False
from agents.receipt_agent import ReceiptAgent
from agents.analytics_agent import AnalyticsAgent
from agents.game_agent import GameAgent
from agents.wallet_agent import WalletAgent


class StashWorkflowExamples:
    """Examples of different ADK workflow patterns in Stash."""
    
    def __init__(self):
        self.receipt_agent = ReceiptAgent()
        self.analytics_agent = AnalyticsAgent()
        self.game_agent = GameAgent()
        self.wallet_agent = WalletAgent()
    
    async def sequential_receipt_workflow(self, image_url: str, user_id: str):
        """
        Example: Sequential workflow using ADK SequentialAgent pattern.
        Receipt -> Points -> Wallet (in sequence)
        """
        print("🔄 Sequential Receipt Workflow")
        
        # This would be the ADK way using SequentialAgent
        # sequential_workflow = SequentialAgent(
        #     name="ReceiptProcessingWorkflow",
        #     sub_agents=[self.receipt_agent, self.game_agent, self.wallet_agent]
        # )
        
        # For now, demonstrate the pattern manually
        session = Session()
        
        # Step 1: Process receipt
        session.state["image_url"] = image_url
        session.state["user_id"] = user_id
        
        receipt_result = await self.receipt_agent.process({
            "operation": "process_receipt",
            "imageUrl": image_url,
            "userId": user_id
        })
        
        print(f"Receipt processed: {receipt_result['status']}")
        
        if receipt_result["status"] == "success":
            # Step 2: Award points
            session.state["receipt_data"] = receipt_result.get("data", {})
            
            game_result = await self.game_agent.process({
                "operation": "award_points",
                "userId": user_id,
                "receiptData": session.state["receipt_data"]
            })
            
            print(f"Points awarded: {game_result.get('points_awarded', 0)}")
            
            # Step 3: Check updated balance
            wallet_result = await self.wallet_agent.process({
                "operation": "get_balance",
                "userId": user_id
            })
            
            print(f"New balance: {wallet_result.get('balance', 0)} points")
            
            return {
                "workflow": "sequential",
                "receipt": receipt_result,
                "game": game_result,
                "wallet": wallet_result
            }
        else:
            # Return error result when receipt processing fails
            return {
                "workflow": "sequential",
                "receipt": receipt_result,
                "game": {"status": "skipped", "reason": "receipt processing failed"},
                "wallet": {"status": "skipped", "reason": "receipt processing failed"}
            }
    
    async def parallel_dashboard_workflow(self, user_id: str):
        """
        Example: Parallel workflow for gathering user dashboard data.
        Analytics + Wallet + Achievements (in parallel)
        """
        print("⚡ Parallel Dashboard Workflow")
        
        # This demonstrates what would happen with ADK ParallelAgent
        # parallel_workflow = ParallelAgent(
        #     name="DashboardDataGathering", 
        #     sub_agents=[self.analytics_agent, self.wallet_agent, self.game_agent]
        # )
        
        # Manual demonstration of parallel execution
        tasks = [
            self.analytics_agent.process({"operation": "generate_report", "userId": user_id}),
            self.wallet_agent.process({"operation": "get_balance", "userId": user_id}),
            self.game_agent.process({"operation": "get_achievements", "userId": user_id})
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        analytics_result, wallet_result, game_result = results
        
        # Handle potential exceptions in results
        analytics_status = analytics_result.get('status', 'error') if isinstance(analytics_result, dict) else 'error'
        wallet_status = wallet_result.get('status', 'error') if isinstance(wallet_result, dict) else 'error'
        game_status = game_result.get('status', 'error') if isinstance(game_result, dict) else 'error'
        
        print(f"Analytics: {analytics_status}")
        print(f"Wallet: {wallet_status}")
        print(f"Achievements: {game_status}")
        
        return {
            "workflow": "parallel",
            "analytics": analytics_result if isinstance(analytics_result, dict) else {"status": "error", "error": str(analytics_result)},
            "wallet": wallet_result if isinstance(wallet_result, dict) else {"status": "error", "error": str(wallet_result)}, 
            "game": game_result if isinstance(game_result, dict) else {"status": "error", "error": str(game_result)}
        }
    
    async def coordinator_pattern_example(self, user_query: str, user_id: str):
        """
        Example: Coordinator/Dispatcher pattern.
        Root agent decides which specialized agent to route to.
        """
        print(f"🎯 Coordinator Pattern for query: '{user_query}'")
        
        # Simple routing logic (in real ADK, this would be LLM-driven)
        if "receipt" in user_query.lower() or "upload" in user_query.lower():
            print("Routing to ReceiptAgent")
            return await self.receipt_agent.process_stash_request({
                "message": user_query,
                "userId": user_id
            })
        
        elif "spending" in user_query.lower() or "analytics" in user_query.lower():
            print("Routing to AnalyticsAgent")
            return await self.analytics_agent.process_stash_request({
                "message": user_query,
                "userId": user_id
            })
        
        elif "points" in user_query.lower() or "rewards" in user_query.lower():
            print("Routing to GameAgent")
            return await self.game_agent.process_stash_request({
                "message": user_query,
                "userId": user_id
            })
        
        elif "balance" in user_query.lower() or "wallet" in user_query.lower():
            print("Routing to WalletAgent")
            return await self.wallet_agent.process_stash_request({
                "message": user_query,
                "userId": user_id
            })
        
        else:
            return {
                "status": "error",
                "error": "Could not determine appropriate agent for query",
                "suggestion": "Try asking about receipts, spending, points, or wallet balance"
            }
    
    async def state_sharing_example(self, user_id: str):
        """
        Example: Shared state between agents using ADK session patterns.
        """
        print("📊 State Sharing Example")
        
        # Create session with shared state
        session = Session()
        session.state["user_id"] = user_id
        session.state["workflow_start"] = "analytics_with_context"
        
        # Agent 1: Get receipts and store in state
        receipt_data = await self.analytics_agent.process({
            "operation": "generate_report",
            "userId": user_id
        })
        
        if receipt_data["status"] == "success":
            session.state["spending_data"] = receipt_data.get("report", {})
            
            # Agent 2: Use the spending data for personalized rewards
            if "categories" in session.state["spending_data"]:
                categories = session.state["spending_data"]["categories"]
                top_category = max(categories, key=categories.get) if categories else "general"
                
                # This could influence point calculations or achievements
                session.state["user_preference"] = top_category
                print(f"Detected user preference: {top_category}")
        
        return {
            "workflow": "state_sharing",
            "shared_state": dict(session.state),
            "analytics": receipt_data
        }


async def main():
    """Run comprehensive ADK workflow examples."""
    examples = StashWorkflowExamples()
    
    print("🚀 ADK Workflow Examples for Stash\n")
    
    # Example 1: Sequential workflow
    sequential_result = await examples.sequential_receipt_workflow(
        "gs://stash-receipts/example.jpg", 
        "demo_user"
    )
    if sequential_result:
        print(f"Sequential result: {sequential_result['workflow']}\n")
    else:
        print("Sequential workflow failed\n")
    
    # Example 2: Parallel workflow  
    parallel_result = await examples.parallel_dashboard_workflow("demo_user")
    if parallel_result:
        print(f"Parallel result: {parallel_result['workflow']}\n")
    else:
        print("Parallel workflow failed\n")
    
    # Example 3: Coordinator pattern
    queries = [
        "How much did I spend this month?",
        "Upload my grocery receipt",
        "What's my point balance?",
        "Show me my achievements"
    ]
    
    for query in queries:
        coordinator_result = await examples.coordinator_pattern_example(query, "demo_user")
        print(f"Query: '{query}' -> Status: {coordinator_result.get('status', 'unknown')}\n")
    
    # Example 4: State sharing
    state_result = await examples.state_sharing_example("demo_user")
    print(f"State sharing result: {state_result['workflow']}\n")
    
    print("✅ All ADK workflow examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
