# game_agent.py
from fastapi import APIRouter, HTTPException
from utils.firestore_client import get_firestore_client
from google.cloud import firestore
import random

router = APIRouter()
firestore_client = get_firestore_client()

@router.post("/award-points")
async def award_points(payload: dict):
    """
    Awards points to a user for uploading a receipt.
    """
    user_id = payload.get("userId")
    receipt_id = payload.get("receiptId")

    if not user_id or not receipt_id:
        raise HTTPException(status_code=400, detail="userId and receiptId are required")

    try:
        points = random.randint(5, 20)
        user_ref = firestore_client.collection("users").document(user_id)
        user_ref.update({"points": firestore.Increment(points)})
        
        return {"status": "points awarded", "points": points}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to award points: {e}")
