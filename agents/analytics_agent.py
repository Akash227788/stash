# agents/analytics_agent.py
"""Analytics agent for spending analysis and insights."""

import asyncio
from typing import Dict, Any, List
from agents.base_agent import StashLlmAgent
from agents.tools.analytics_tools import (
    get_user_receipts,
    analyze_spending_patterns,
    generate_budget_forecast
)


class AnalyticsAgent(StashLlmAgent):
    """
    Analytics Agent responsible for analyzing spending patterns,
    generating insights, and providing financial recommendations.
    """
    
    def __init__(self):
        tools = [
            get_user_receipts,
            analyze_spending_patterns,
            generate_budget_forecast
        ]
        super().__init__(
            name="AnalyticsAgent",
            tools=tools,
            instruction="You are an expert financial analytics agent for the Stash app.",
            system_instruction="""
            You are an expert financial analytics agent for the Stash app.
            
            Your responsibilities:
            - Analyze spending patterns and trends
            - Generate comprehensive spending reports
            - Detect unusual spending patterns or anomalies
            - Provide budget optimization suggestions
            - Identify opportunities for savings
            
            Always provide actionable insights and clear explanations
            for your analysis and recommendations.
            """
        )
    
    async def analyze_spending_patterns(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user spending patterns and provide insights.
        
        Args:
            request_data: Dictionary containing user_id and analysis parameters
        
        Returns:
            Dictionary with spending analysis results
        """
        try:
            user_id = request_data.get("user_id")
            period = request_data.get("period", "month")
            
            # Process the request through ADK
            analysis_request = {
                "message": f"Analyze spending patterns for user {user_id} over the {period}",
                "context": request_data
            }
            
            result = await self.process_stash_request(analysis_request)
            
            return {
                "status": "success",
                "user_id": user_id,
                "period": period,
                "analysis": result.get("response", "Analysis completed"),
                "insights": result.get("insights", []),
                "recommendations": result.get("recommendations", [])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to analyze spending patterns"
            }
    
    async def generate_report(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive spending report.
        
        Args:
            request_data: Dictionary containing report parameters
        
        Returns:
            Dictionary with the generated report
        """
        try:
            report_type = request_data.get("report_type", "monthly")
            
            # Process the request through ADK
            report_request = {
                "message": f"Generate a {report_type} spending report",
                "context": request_data
            }
            
            result = await self.process_stash_request(report_request)
            
            return {
                "status": "success",
                "report_type": report_type,
                "report": result.get("response", "Report generated"),
                "charts": result.get("charts", []),
                "summary": result.get("summary", {})
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to generate spending report"
            }


    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requests for analytics operations.
        
        Args:
            request: Request containing operation type and parameters
            
        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "spending_report")
        
        if operation == "spending_report":
            user_id = request.get("userId")
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required for spending report",
                    "agent": self.name
                }
            
            return await self.analyze_spending_patterns(request)
        
        elif operation == "generate_report":
            return await self.generate_report(request)
        
        else:
            # Use the base ADK processing for other queries
            return await self.process_stash_request(request)


# Example usage
async def example_analytics_usage():
    """Example of how to use the AnalyticsAgent."""
    agent = AnalyticsAgent()
    
    # Analyze spending patterns
    analysis_request = {
        "user_id": "user123",
        "period": "month",
        "categories": ["food", "transportation", "entertainment"]
    }
    
    result = await agent.analyze_spending_patterns(analysis_request)
    print("Spending Analysis:", result)
    
    # Generate report
    report_request = {
        "user_id": "user123",
        "report_type": "quarterly",
        "include_charts": True
    }
    
    report = await agent.generate_report(report_request)
    print("Spending Report:", report)


if __name__ == "__main__":
    asyncio.run(example_analytics_usage())
