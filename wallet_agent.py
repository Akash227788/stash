# wallet_agent.py - FastAPI Router with ADK Agent Integration
from fastapi import APIRouter, HTTPException
from agents.wallet_agent import WalletAgent

router = APIRouter()

# Initialize the ADK-based wallet agent
wallet_agent = WalletAgent()

@router.get("/balance/{user_id}")
async def get_balance(user_id: str):
    """
    Gets the current balance for a user using the ADK-based WalletAgent.
    """
    try:
        # Use the ADK-based agent to get balance
        request = {
            "operation": "get_balance",
            "userId": user_id
        }
        
        result = await wallet_agent.process(request)
        
        if result["status"] == "success":
            return {
                "balance": result.get("balance"),
                "currency": result.get("currency", "points"),
                "summary": result.get("summary", ""),
                "recent_transactions": result.get("recent_transactions", []),
                "agent": result.get("agent")
            }
        else:
            # Return 0 balance if user doesn't exist yet
            return {"balance": 0, "currency": "points"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")

@router.get("/transactions/{user_id}")
async def get_transactions(user_id: str, limit: int = 20):
    """
    Gets transaction history for a user.
    """
    try:
        request = {
            "operation": "get_transactions",
            "userId": user_id,
            "limit": limit
        }
        
        result = await wallet_agent.process(request)
        
        if result["status"] == "success":
            return {
                "transactions": result.get("transactions", []),
                "summary": result.get("summary", {}),
                "agent": result.get("agent")
            }
        else:
            return {"transactions": [], "summary": {}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {e}")

@router.get("/rewards")
async def get_rewards():
    """
    Gets available redemption rewards.
    """
    try:
        request = {"operation": "get_rewards"}
        
        result = await wallet_agent.process(request)
        
        if result["status"] == "success":
            return {
                "catalog": result.get("catalog", []),
                "categories": result.get("categories", []),
                "agent": result.get("agent")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get rewards"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rewards: {e}")

@router.post("/redeem")
async def redeem_reward(payload: dict):
    """
    Processes a reward redemption.
    """
    user_id = payload.get("userId")
    reward_id = payload.get("rewardId")

    if not user_id or not reward_id:
        raise HTTPException(status_code=400, detail="userId and rewardId are required")

    try:
        request = {
            "operation": "redeem_reward",
            "userId": user_id,
            "rewardId": reward_id
        }
        
        result = await wallet_agent.process(request)
        
        if result["status"] == "success":
            return {
                "status": "redemption successful",
                "redemption": result.get("redemption"),
                "confirmation": result.get("confirmation"),
                "agent": result.get("agent")
            }
        else:
            error_msg = result.get("error", "Redemption failed")
            if "Insufficient balance" in error_msg:
                raise HTTPException(status_code=400, detail=error_msg)
            else:
                raise HTTPException(status_code=500, detail=error_msg)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process redemption: {e}")
