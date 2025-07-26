# receipt_agent.py - FastAPI Router with ADK Agent Integration
from fastapi import APIRouter, HTTPException
from agents.receipt_agent import ReceiptAgent

router = APIRouter()

# Initialize the ADK-based receipt agent
receipt_agent = ReceiptAgent()

@router.post("/process-receipt")
async def process_receipt(payload: dict):
    """
    Process a receipt image using the ADK-based ReceiptAgent.
    """
    image_url = payload.get("imageUrl")
    user_id = payload.get("userId")

    if not image_url or not user_id:
        raise HTTPException(status_code=400, detail="imageUrl and userId are required")

    try:
        # Use the ADK-based agent to process the receipt
        request = {
            "operation": "process_receipt",
            "imageUrl": image_url,
            "userId": user_id
        }
        
        result = await receipt_agent.process(request)
        
        if result["status"] == "success":
            return {
                "status": "receipt processed",
                "receiptId": result.get("receipt_id"),
                "data": result.get("data"),
                "processing_summary": result.get("processing_summary"),
                "agent": result.get("agent")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process receipt: {e}")
