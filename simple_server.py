# simple_server.py - Simple FastAPI server for testing data flow
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import json
import os
from datetime import datetime
import uuid
import base64
import io
from utils.env_loader import load_env_from_file, get_config
from utils.firestore_client import get_firestore_client
from utils.storage_client import get_storage_client
from utils.genai_client import get_generative_model

# Load environment
load_env_from_file('.env')
config = get_config()

app = FastAPI(
    title="Stash API - Simple Test Server",
    description="Simple server for testing data flow to Google Cloud",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
try:
    db = get_firestore_client()
    storage_client = get_storage_client()
    if storage_client:
        bucket = storage_client.bucket(config.get('gcs_bucket', 'stash_bucket_1'))
    else:
        bucket = None
    print(f"✅ Initialized Google Cloud clients")
except Exception as e:
    print(f"❌ Failed to initialize Google Cloud clients: {e}")
    db = None
    storage_client = None
    bucket = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stash API Test Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "firestore": "connected" if db else "disconnected",
            "storage": "connected" if bucket else "disconnected"
        },
        "config": {
            "project_id": config.get('project_id'),
            "bucket": config.get('gcs_bucket'),
            "environment": config.get('environment', 'development')
        }
    }

@app.post("/test/upload-dummy-receipt")
async def upload_dummy_receipt():
    """Upload dummy receipt data to test data flow"""
    if not db or not bucket:
        raise HTTPException(status_code=503, detail="Google Cloud services not available")
    
    try:
        # Generate dummy receipt data
        receipt_id = str(uuid.uuid4())
        user_id = "test_user_123"
        
        dummy_receipt_data = {
            "receipt_id": receipt_id,
            "user_id": user_id,
            "merchant_name": "Test Grocery Store",
            "transaction_date": datetime.now().isoformat(),
            "total_amount": 45.67,
            "items": [
                {"name": "Milk", "price": 4.99, "quantity": 1},
                {"name": "Bread", "price": 3.50, "quantity": 2},
                {"name": "Eggs", "price": 5.99, "quantity": 1},
                {"name": "Bananas", "price": 2.99, "quantity": 1}
            ],
            "category": "grocery",
            "payment_method": "credit_card",
            "created_at": datetime.now().isoformat(),
            "processed": True,
            "points_earned": 10
        }
        
        # 1. Store in Firestore
        receipt_ref = db.collection('receipts').document(receipt_id)
        receipt_ref.set(dummy_receipt_data)
        print(f"✅ Stored receipt {receipt_id} in Firestore")
        
        # 2. Create dummy receipt image (simple text file for testing)
        dummy_image_content = f"""
RECEIPT
{dummy_receipt_data['merchant_name']}
Date: {dummy_receipt_data['transaction_date']}
Total: ${dummy_receipt_data['total_amount']}
Items:
{chr(10).join([f"- {item['name']}: ${item['price']}" for item in dummy_receipt_data['items']])}
Thank you for shopping!
        """.strip()
        
        # 3. Upload to Cloud Storage
        blob_name = f"receipts/{user_id}/{receipt_id}.txt"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(dummy_image_content, content_type='text/plain')
        print(f"✅ Uploaded receipt {receipt_id} to Cloud Storage")
        
        # 4. Update user stats
        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get()
        
        if user_data.exists:
            # Update existing user
            current_data = user_data.to_dict() or {}
            updated_data = {
                "total_receipts": current_data.get("total_receipts", 0) + 1,
                "total_points": current_data.get("total_points", 0) + dummy_receipt_data["points_earned"],
                "total_spent": current_data.get("total_spent", 0) + dummy_receipt_data["total_amount"],
                "last_receipt_date": dummy_receipt_data["created_at"]
            }
            user_ref.update(updated_data)
        else:
            # Create new user
            user_data = {
                "user_id": user_id,
                "total_receipts": 1,
                "total_points": dummy_receipt_data["points_earned"],
                "total_spent": dummy_receipt_data["total_amount"],
                "created_at": datetime.now().isoformat(),
                "last_receipt_date": dummy_receipt_data["created_at"]
            }
            user_ref.set(user_data)
        
        print(f"✅ Updated user {user_id} stats")
        
        return {
            "success": True,
            "receipt_id": receipt_id,
            "user_id": user_id,
            "data_stored": {
                "firestore": f"receipts/{receipt_id}",
                "storage": f"gs://{config.get('gcs_bucket')}/{blob_name}",
                "user_stats": f"users/{user_id}"
            },
            "receipt_data": dummy_receipt_data
        }
        
    except Exception as e:
        print(f"❌ Error uploading dummy receipt: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading receipt: {str(e)}")

@app.get("/test/get-user-data/{user_id}")
async def get_user_data(user_id: str):
    """Get user data from Firestore"""
    if not db:
        raise HTTPException(status_code=503, detail="Firestore not available")
    
    try:
        # Get user stats
        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get()
        
        if not user_data.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user receipts
        receipts_ref = db.collection('receipts').where('user_id', '==', user_id).limit(10)
        receipts = [doc.to_dict() for doc in receipts_ref.stream()]
        
        return {
            "user_stats": user_data.to_dict(),
            "recent_receipts": receipts,
            "total_receipts": len(receipts)
        }
        
    except Exception as e:
        print(f"❌ Error getting user data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user data: {str(e)}")

@app.get("/test/list-storage-files")
async def list_storage_files():
    """List files in Cloud Storage bucket"""
    if not bucket:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        blobs = list(bucket.list_blobs(prefix="receipts/", max_results=20))
        files = []
        
        for blob in blobs:
            files.append({
                "name": blob.name,
                "size": blob.size,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "content_type": blob.content_type,
                "public_url": f"gs://{bucket.name}/{blob.name}"
            })
        
        return {
            "bucket": bucket.name,
            "total_files": len(files),
            "files": files
        }
        
    except Exception as e:
        print(f"❌ Error listing storage files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
    userId: str = Form(...)
):
    """
    Upload a receipt image and return the image URL and user ID.
    This endpoint uploads the file to Google Cloud Storage and returns the required response format.
    """
    if not bucket:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        # Validate file type (optional - you can modify this based on your requirements)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate unique filename
        if file.filename and '.' in file.filename:
            file_extension = file.filename.split('.')[-1]
        else:
            file_extension = 'jpg'  # Default extension
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        blob_name = f"receipts/{userId}/{unique_filename}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloud Storage
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            file_content,
            content_type=file.content_type
        )
        
        # Generate the Cloud Storage URL
        image_url = f"gs://{bucket.name}/{blob_name}"
        
        print(f"✅ Successfully uploaded file to {image_url}")
        
        # Return the required response format
        return {
            "imageUrl": image_url,
            "userId": userId
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/upload-binary")
async def upload_receipt_binary(
    request: Request,
    userId: str = Header(..., alias="X-User-Id"),
    content_type: Optional[str] = Header(None, alias="Content-Type")
):
    """
    Upload a receipt image from binary data in request body and return the image URL and user ID.
    This endpoint accepts binary image data directly in the request body.
    
    Headers required:
    - X-User-Id: User ID
    - Content-Type: Image content type (e.g., image/jpeg, image/png)
    """
    if not bucket:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        # Validate content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid Content-Type header. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read binary data from request body
        binary_data = await request.body()
        
        if not binary_data:
            raise HTTPException(status_code=400, detail="No binary data found in request body")
        
        # Determine file extension from content type
        extension_mapping = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg', 
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp'
        }
        file_extension = extension_mapping.get(content_type, 'jpg')
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        blob_name = f"receipts/{userId}/{unique_filename}"
        
        # Upload to Cloud Storage
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            binary_data,
            content_type=content_type
        )
        
        # Generate the Cloud Storage URL
        image_url = f"gs://{bucket.name}/{blob_name}"
        
        print(f"✅ Successfully uploaded binary file to {image_url}")
        
        # Return the required response format
        return {
            "imageUrl": image_url,
            "userId": userId
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Error uploading binary file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading binary file: {str(e)}")

@app.post("/upload-binary-query")
async def upload_receipt_binary_query(
    request: Request,
    userId: str,
    contentType: str = "image/jpeg"
):
    """
    Upload a receipt image from binary data in request body using query parameters.
    This endpoint accepts binary image data directly in the request body with user info as query params.
    
    Query parameters:
    - userId: User ID (required)
    - contentType: Image content type (optional, defaults to image/jpeg)
    """
    if not bucket:
        raise HTTPException(status_code=503, detail="Cloud Storage not available")
    
    try:
        # Validate content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if contentType not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid contentType parameter. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read binary data from request body
        binary_data = await request.body()
        
        if not binary_data:
            raise HTTPException(status_code=400, detail="No binary data found in request body")
        
        # Determine file extension from content type
        extension_mapping = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg', 
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp'
        }
        file_extension = extension_mapping.get(contentType, 'jpg')
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        blob_name = f"receipts/{userId}/{unique_filename}"
        
        # Upload to Cloud Storage
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            binary_data,
            content_type=contentType
        )
        
        # Generate the Cloud Storage URL
        image_url = f"gs://{bucket.name}/{blob_name}"
        
        print(f"✅ Successfully uploaded binary file to {image_url}")
        
        # Return the required response format
        return {
            "imageUrl": image_url,
            "userId": userId
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Error uploading binary file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading binary file: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Stash Test Server...")
    print(f"📋 Configuration loaded: {len(config)} settings")
    
    # Get port from environment (Cloud Run sets this)
    port = int(os.environ.get('PORT', config.get('port', 8080)))
    host = os.environ.get('HOST', config.get('host', '0.0.0.0'))
    
    print(f"🏠 Server will run on: http://{host}:{port}")
    
    # Use different settings for Cloud Run vs local development
    is_cloud_run = os.environ.get('K_SERVICE') is not None
    
    if is_cloud_run:
        print("☁️  Running in Google Cloud Run environment")
        # Cloud Run configuration
        uvicorn.run(
            "simple_server:app",
            host=host,
            port=port,
            reload=False,  # Don't reload in production
            log_level="info",
            access_log=True
        )
    else:
        print("💻 Running in local development environment")
        # Local development configuration
        uvicorn.run(
            "simple_server:app",
            host=host,
            port=port,
            reload=True,
            log_level="debug"
        )
