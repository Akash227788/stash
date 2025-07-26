# receipt_agent.py
from fastapi import APIRouter, HTTPException
import os
import uuid
import datetime
import json
from utils.vision_utils import extract_text_from_image
from utils.genai_client import get_generative_model
from utils.firestore_client import get_firestore_client
from utils.pubsub_client import publish_message

router = APIRouter()
firestore_client = get_firestore_client()
model = get_generative_model()

@router.post("/process-receipt")
async def process_receipt(payload: dict):
    image_url = payload.get("imageUrl")
    user_id = payload.get("userId")

    if not image_url or not user_id:
        raise HTTPException(status_code=400, detail="imageUrl and userId are required")

    try:
        # Use the ADK tool to extract text from the image
        vision_response = extract_text_from_image(image_url=image_url)
        
        if not vision_response.text_annotations:
            raise HTTPException(status_code=400, detail="No text found in image")

        full_text = vision_response.full_text_annotation.text
        
        # Use a generative model to parse the text
        prompt = f"""
        Extract the merchant name, a list of items (with prices), and the total amount 
        from the following receipt text. Return the result as a JSON object with keys 
        'merchant', 'items', and 'total'.

        Receipt Text:
        {full_text}

        JSON Output:
        """
        
        response = model.generate_content(prompt)
        
        try:
            # The model's response might include markdown, so we need to clean it
            parsed_response = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            merchant = parsed_response.get("merchant", "Unknown")
            items = parsed_response.get("items", [])
            total = parsed_response.get("total", "0.00")
        except (json.JSONDecodeError, AttributeError) as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse receipt data from generative model: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process receipt: {e}")

    receipt_id = str(uuid.uuid4())
    receipt_data = {
        "userId": user_id,
        "receiptId": receipt_id,
        "merchant": merchant,
        "items": items,
        "total": total,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "imageUrl": image_url,
    }

    # Save to Firestore
    firestore_client.collection("receipts").document(receipt_id).set(receipt_data)

    # Publish a message to Pub/Sub for further processing
    publish_message(
        project_id=os.getenv("FIRESTORE_PROJECT_ID", "local-dev"),
        topic_id="receipt-processed",
        data=json.dumps(receipt_data).encode("utf-8")
    )

    return {"status": "receipt processed", "receiptId": receipt_id, "data": receipt_data}
