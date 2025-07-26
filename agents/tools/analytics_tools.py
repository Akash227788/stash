# agents/tools/analytics_tools.py
"""
ADK-style tools for financial analytics.
"""
import os
import json
from typing import Dict, Any, List
from functools import wraps
from utils.firestore_client import get_firestore_client
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
def get_user_receipts(user_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Retrieves receipts for a specific user from Firestore.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of receipts to retrieve
        
    Returns:
        Dictionary containing user receipts and metadata
    """
    try:
        firestore_client = get_firestore_client()
        receipts_ref = firestore_client.collection("receipts")
        query = receipts_ref.where("userId", "==", user_id).limit(limit)
        receipts = [doc.to_dict() for doc in query.stream()]
        
        return {
            "success": True,
            "receipts": receipts,
            "count": len(receipts),
            "user_id": user_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "receipts": [],
            "count": 0
        }


@tool
def analyze_spending_patterns(receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes spending patterns using LLM to provide insights.
    
    Args:
        receipts: List of receipt data dictionaries
        
    Returns:
        Dictionary containing spending analysis and insights
    """
    try:
        if not receipts:
            return {
                "success": False,
                "error": "No receipts provided for analysis",
                "insights": "No data available for analysis"
            }
        
        model = get_generative_model()
        
        # Prepare data for analysis
        receipt_summary = []
        total_spending = 0
        merchants = {}
        
        for receipt in receipts:
            merchant = receipt.get("merchant", "Unknown")
            total = float(receipt.get("total", "0").replace("$", "").replace(",", ""))
            
            receipt_summary.append({
                "merchant": merchant,
                "total": total,
                "date": receipt.get("timestamp", "")
            })
            
            total_spending += total
            merchants[merchant] = merchants.get(merchant, 0) + total
        
        # Create analysis prompt
        prompt = f"""
        Analyze the following spending data and provide insights:
        
        Total Receipts: {len(receipts)}
        Total Spending: ${total_spending:.2f}
        
        Spending by Merchant:
        {json.dumps(merchants, indent=2)}
        
        Recent Transactions:
        {json.dumps(receipt_summary[:10], indent=2)}
        
        Provide analysis including:
        1. Spending trends
        2. Top categories/merchants
        3. Budget recommendations
        4. Potential savings opportunities
        
        Format as a structured analysis with clear sections.
        """
        
        response = model.generate_content(prompt)
        insights = response.text if hasattr(response, 'text') else str(response)
        
        return {
            "success": True,
            "insights": insights,
            "summary": {
                "total_receipts": len(receipts),
                "total_spending": total_spending,
                "top_merchants": sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5],
                "average_transaction": total_spending / len(receipts) if receipts else 0
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "insights": f"Error analyzing spending: {str(e)}"
        }


@tool
def generate_budget_forecast(receipts: List[Dict[str, Any]], forecast_period: str = "monthly") -> Dict[str, Any]:
    """
    Generates budget forecasts based on historical spending data.
    
    Args:
        receipts: List of receipt data dictionaries
        forecast_period: Period for forecast (monthly, weekly, yearly)
        
    Returns:
        Dictionary containing budget forecast and recommendations
    """
    try:
        if not receipts:
            return {
                "success": False,
                "error": "No receipts provided for forecasting",
                "forecast": "No data available for forecasting"
            }
        
        model = get_generative_model()
        
        # Calculate spending metrics
        total_spending = sum(float(r.get("total", "0").replace("$", "").replace(",", "")) for r in receipts)
        
        # Create forecast prompt
        prompt = f"""
        Based on the spending data of ${total_spending:.2f} across {len(receipts)} transactions,
        generate a {forecast_period} budget forecast.
        
        Include:
        1. Projected {forecast_period} spending
        2. Budget allocation recommendations by category
        3. Savings goals and targets
        4. Spending limit suggestions
        5. Financial health assessment
        
        Provide practical, actionable advice for better financial management.
        """
        
        response = model.generate_content(prompt)
        forecast = response.text if hasattr(response, 'text') else str(response)
        
        return {
            "success": True,
            "forecast": forecast,
            "period": forecast_period,
            "base_data": {
                "historical_spending": total_spending,
                "transaction_count": len(receipts),
                "average_transaction": total_spending / len(receipts) if receipts else 0
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "forecast": f"Error generating forecast: {str(e)}"
        }
