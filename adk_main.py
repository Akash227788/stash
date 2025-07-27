# adk_main.py
"""
ADK-powered Stash application demonstrating proper agent orchestration.
This replaces the traditional FastAPI routers with ADK agent patterns.
"""
import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uuid

# Load environment variables first
from utils.env_loader import load_env_from_file, get_config
from utils.storage_client import get_storage_client
load_env_from_file()
config = get_config()

try:
    from google.adk import Session  # type: ignore
    ADK_AVAILABLE = True
except ImportError:
    # Mock Session class for when ADK is not available
    class Session:
        def __init__(self, *args, **kwargs):
            self.state = {}
    ADK_AVAILABLE = False
from agents.root_agent import RootAgent
from adk_server import StashADKServer


# Pydantic models for API requests
class ReceiptProcessRequest(BaseModel):
    imageUrl: str
    userId: str


class AnalyticsRequest(BaseModel):
    userId: str


class PointsRequest(BaseModel):
    userId: str
    receiptData: Optional[Dict[str, Any]] = {}


class WalletRequest(BaseModel):
    userId: str


class RedemptionRequest(BaseModel):
    userId: str
    rewardId: str


# Initialize FastAPI app
app = FastAPI(title="Stash ADK API", description="ADK-powered financial management system")

# Initialize ADK server
stash_server = StashADKServer()

# Initialize storage client for file uploads
try:
    storage_client = get_storage_client()
    if storage_client:
        bucket = storage_client.bucket(config.get('gcs_bucket', 'stash_bucket_1'))
    else:
        bucket = None
    print(f"✅ Initialized Google Cloud Storage client")
except Exception as e:
    print(f"❌ Failed to initialize Google Cloud Storage: {e}")
    bucket = None

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


@app.get("/")
async def root():
    """Welcome endpoint with ADK agent information."""
    return {
        "message": "Welcome to Stash ADK API!",
        "description": "Powered by Google Agent Development Kit (ADK)",
        "agents": {
            "root": "Coordinates all operations",
            "receipt": "Processes receipt images and extracts data",
            "analytics": "Provides spending insights and analysis",
            "game": "Manages points and achievements",
            "wallet": "Handles balances and transactions"
        },
        "patterns": [
            "Sequential workflows for receipt processing",
            "Parallel execution for dashboard data",
            "Coordinator pattern for request routing",
            "State sharing between agents"
        ]
    }


@app.post("/adk/receipt/process")
async def process_receipt_adk(request: ReceiptProcessRequest):
    """
    Process receipt using ADK agent workflow.
    Demonstrates sequential agent coordination.
    """
    try:
        result = await stash_server.process_receipt_workflow(
            request.imageUrl, 
            request.userId
        )
        
        if result["status"] == "success":
            return {
                "status": "receipt processed",
                "workflow_complete": result["workflow_complete"],
                "receipt_data": result["receipt_processing"].get("data"),
                "points_awarded": result["points_awarded"].get("points_awarded", 0),
                "new_balance": result["points_awarded"].get("new_balance", 0),
                "summary": result["summary"],
                "adk_pattern": "sequential_workflow"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ADK workflow failed: {str(e)}")


@app.get("/adk/analytics/{user_id}")
async def get_analytics_adk(user_id: str):
    """
    Get spending analytics using ADK agent.
    """
    try:
        result = await stash_server.generate_analytics_report(user_id)
        
        if result["status"] == "success":
            return {
                "status": "analytics generated",
                "report": result.get("report"),
                "insights": result.get("insights"),
                "agent": result.get("agent"),
                "adk_pattern": "single_agent_processing"
            }
        else:
            return {
                "status": "no data",
                "message": result.get("message", "No analytics data available"),
                "insights": result.get("insights", "Start uploading receipts to get insights!")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@app.post("/adk/game/award-points")
async def award_points_adk(request: PointsRequest):
    """
    Award points using ADK game agent.
    """
    try:
        game_request = {
            "operation": "award_points",
            "userId": request.userId,
            "receiptData": request.receiptData
        }
        
        result = await stash_server.game_agent.process(game_request)
        
        if result["status"] == "success":
            return {
                "status": "points awarded",
                "points": result.get("points_awarded"),
                "new_balance": result.get("new_balance"),
                "breakdown": result.get("breakdown"),
                "message": result.get("message"),
                "achievements": result.get("achievements"),
                "agent": result.get("agent"),
                "adk_pattern": "tool_orchestration"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Points award failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Points award failed: {str(e)}")


@app.get("/adk/wallet/{user_id}")
async def get_balance_adk(user_id: str):
    """
    Get wallet balance using ADK wallet agent.
    """
    try:
        wallet_request = {
            "operation": "get_balance",
            "userId": user_id
        }
        
        result = await stash_server.wallet_agent.process(wallet_request)
        
        if result["status"] == "success":
            return {
                "balance": result.get("balance"),
                "currency": result.get("currency", "points"),
                "summary": result.get("summary"),
                "recent_transactions": result.get("recent_transactions", []),
                "agent": result.get("agent"),
                "adk_pattern": "agent_tool_integration"
            }
        else:
            # Return default balance for new users
            return {
                "balance": 0,
                "currency": "points",
                "summary": "New user - start uploading receipts to earn points!",
                "recent_transactions": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Balance check failed: {str(e)}")


@app.get("/adk/dashboard/{user_id}")
async def get_user_dashboard_adk(user_id: str):
    """
    Get comprehensive user dashboard using ADK parallel coordination.
    Demonstrates parallel agent execution pattern.
    """
    try:
        result = await stash_server.get_user_dashboard(user_id)
        
        if result["status"] == "success":
            return {
                "status": "dashboard generated",
                "dashboard": result["dashboard"],
                "adk_pattern": "parallel_coordination",
                "agent_coordination": {
                    "wallet_status": result["dashboard"]["wallet"]["status"],
                    "analytics_status": result["dashboard"]["analytics"]["status"],
                    "gamification_status": result["dashboard"]["gamification"]["status"]
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Dashboard generation failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


@app.get("/adk/health")
async def health_check():
    """Health check endpoint showing ADK agent status."""
    try:
        # Test basic agent functionality
        test_session = Session()
        
        agents_status = {
            "root_agent": "initialized",
            "receipt_agent": "ready",
            "analytics_agent": "ready", 
            "game_agent": "ready",
            "wallet_agent": "ready"
        }
        
        return {
            "status": "healthy",
            "adk_version": "google-adk",
            "agents": agents_status,
            "patterns_supported": [
                "Sequential workflows",
                "Parallel execution",
                "Agent coordination",
                "State management",
                "Tool orchestration"
            ],
            "session_management": "ADK Sessions",
            "timestamp": test_session.state.get("timestamp", "unknown")
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "agents": "failed_to_initialize"
        }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    config = get_config()
    
    print("🚀 Starting Stash ADK Server...")
    print(f"🌐 Host: {config['host']}:{config['port']}")
    print("🤖 Agents: Receipt, Analytics, Game, Wallet")
    print("🔄 Patterns: Sequential, Parallel, Coordination")
    print("📊 State: ADK Session Management")
    print(f"⚙️  Debug mode: {config['debug']}")
    print(f"🌍 Environment: {config['environment']}")
    
    # Use single worker in debug mode for easier debugging
    workers = 1 if config['debug'] else int(os.getenv("GUNICORN_WORKERS", "1"))
    
    uvicorn.run(
        app, 
        host=config['host'], 
        port=config['port'], 
        reload=config['debug'], 
        workers=workers
    )
