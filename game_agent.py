# game_agent.py - FastAPI Router with ADK Agent Integration
from fastapi import APIRouter, HTTPException
from agents.game_agent import GameAgent

router = APIRouter()

# Initialize the ADK-based game agent
game_agent = GameAgent()

@router.post("/award-points")
async def award_points(payload: dict):
    """
    Awards points to a user for uploading a receipt using the ADK-based GameAgent.
    """
    user_id = payload.get("userId")
    receipt_data = payload.get("receiptData", {})

    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    try:
        # Use the ADK-based agent to award points
        request = {
            "operation": "award_points",
            "userId": user_id,
            "receiptData": receipt_data
        }
        
        result = await game_agent.process(request)
        
        if result["status"] == "success":
            return {
                "status": "points awarded",
                "points": result.get("points_awarded"),
                "new_balance": result.get("new_balance"),
                "breakdown": result.get("breakdown"),
                "message": result.get("message"),
                "achievements": result.get("achievements"),
                "agent": result.get("agent")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Points award failed"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to award points: {e}")

@router.get("/achievements/{user_id}")
async def get_achievements(user_id: str):
    """
    Gets achievements and progress for a user.
    """
    try:
        request = {
            "operation": "get_achievements",
            "userId": user_id
        }
        
        result = await game_agent.process(request)
        
        if result["status"] == "success":
            progress = result.get("progress", {})
            return {
                "achievements": progress.get("achievements", []),
                "next_achievements": progress.get("next_achievements", []),
                "stats": progress.get("stats", {}),
                "encouragement": result.get("encouragement", ""),
                "agent": result.get("agent")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get achievements"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get achievements: {e}")
