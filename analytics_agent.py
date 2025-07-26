# analytics_agent.py - FastAPI Router with ADK Agent Integration
from fastapi import APIRouter, HTTPException
from agents.analytics_agent import AnalyticsAgent

router = APIRouter()

# Initialize the ADK-based analytics agent
analytics_agent = AnalyticsAgent()

@router.get("/spending-report/{user_id}")
async def get_spending_report(user_id: str):
    """
    Generates a spending report for a given user using the ADK-based AnalyticsAgent.
    """
    try:
        # Use the ADK-based agent to generate the report
        request = {
            "operation": "spending_report",
            "userId": user_id
        }
        
        result = await analytics_agent.process(request)
        
        if result["status"] == "success":
            report = result.get("report", {})
            return {
                "report": report.get("spending_analysis", ""),
                "summary": report.get("spending_summary", {}),
                "receipts": report.get("receipts", []),
                "recommendations": report.get("recommendations", []),
                "agent": result.get("agent")
            }
        else:
            if "No receipts found" in result.get("message", ""):
                return {"message": result["message"]}
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate spending report: {e}")

@router.get("/budget-forecast/{user_id}")
async def get_budget_forecast(user_id: str, period: str = "monthly"):
    """
    Generates a budget forecast for a given user.
    """
    try:
        request = {
            "operation": "budget_forecast",
            "userId": user_id,
            "period": period
        }
        
        result = await analytics_agent.process(request)
        
        if result["status"] == "success":
            return {
                "forecast": result.get("forecast", {}),
                "agent": result.get("agent")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Forecast generation failed"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate budget forecast: {e}")
