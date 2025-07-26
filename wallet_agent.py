# wallet_agent.py
from fastapi import APIRouter, HTTPException
from utils.firestore_client import get_firestore_client

router = APIRouter()
firestore_client = get_firestore_client()

@router.get("/balance/{user_id}")
async def get_balance(user_id: str):
    """
    Gets the current balance for a user.
    """
    try:
        user_ref = firestore_client.collection("users").document(user_id)
        user = user_ref.get()
        if not user.exists:
            return {"balance": 0}
        
        return {"balance": user.to_dict().get("points", 0)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")
