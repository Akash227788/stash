# analytics_agent.py
from fastapi import APIRouter, HTTPException
from utils.firestore_client import get_firestore_client
from utils.genai_client import get_generative_model, get_spending_insights

router = APIRouter()
firestore_client = get_firestore_client()
model = get_generative_model()

@router.get("/spending-report/{user_id}")
async def get_spending_report(user_id: str):
    """
    Generates a spending report for a given user.
    """
    try:
        receipts_ref = firestore_client.collection("receipts")
        query = receipts_ref.where("userId", "==", user_id)
        receipts = [doc.to_dict() for doc in query.stream()]

        if not receipts:
            return {"message": "No receipts found for this user."}

        # Use the generative model to get insights
        insights = get_spending_insights(receipt_data={"receipts": receipts})

        return {"report": insights, "receipts": receipts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate spending report: {e}")
