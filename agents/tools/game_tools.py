# agents/tools/game_tools.py
"""
ADK-style tools for gamification features.
"""
import os
import random
from typing import Dict, Any
from functools import wraps
from utils.firestore_client import get_firestore_client
from google.cloud import firestore


def tool(func):
    """Simple tool decorator following ADK patterns."""
    class ToolWrapper:
        def __init__(self, func):
            self.func = func
            self.is_tool = True
            self.tool_name = func.__name__
            self.tool_description = func.__doc__
            # Copy function attributes
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
        
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
    
    return ToolWrapper(func)


@tool
def calculate_points_reward(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates points reward based on receipt data and gamification rules.
    
    Args:
        receipt_data: Dictionary containing receipt information
        
    Returns:
        Dictionary containing calculated points and bonus information
    """
    try:
        # Get configuration from environment variables
        base_points_per_receipt = int(os.getenv("POINTS_PER_RECEIPT", "10"))
        bonus_multiplier = float(os.getenv("BONUS_POINTS_MULTIPLIER", "1.5"))
        
        base_points = random.randint(max(1, base_points_per_receipt - 5), base_points_per_receipt + 10)
        bonus_points = 0
        bonus_reasons = []
        
        # Parse total amount for bonus calculation
        total_str = receipt_data.get("total", "0")
        try:
            total_amount = float(total_str.replace("$", "").replace(",", ""))
            
            # Bonus for larger purchases (using environment configuration)
            large_purchase_threshold = float(os.getenv("LARGE_PURCHASE_THRESHOLD", "100"))
            medium_purchase_threshold = float(os.getenv("MEDIUM_PURCHASE_THRESHOLD", "50"))
            large_purchase_bonus = int(os.getenv("LARGE_PURCHASE_BONUS", "10"))
            medium_purchase_bonus = int(os.getenv("MEDIUM_PURCHASE_BONUS", "5"))
            
            if total_amount > large_purchase_threshold:
                bonus_points += large_purchase_bonus
                bonus_reasons.append(f"Large purchase bonus (+{large_purchase_bonus})")
            elif total_amount > medium_purchase_threshold:
                bonus_points += medium_purchase_bonus
                bonus_reasons.append(f"Medium purchase bonus (+{medium_purchase_bonus})")
            
            # Bonus for specific merchants (encourage certain spending)
            merchant = receipt_data.get("merchant", "").lower()
            grocery_bonus = int(os.getenv("GROCERY_BONUS_POINTS", "3"))
            if any(grocery in merchant for grocery in ["grocery", "market", "food"]):
                bonus_points += grocery_bonus
                bonus_reasons.append(f"Grocery shopping bonus (+{grocery_bonus})")
            
        except ValueError:
            pass  # Invalid total amount, skip bonus calculations
        
        # Random streak bonus (simulate daily/weekly streaks)
        streak_enabled = os.getenv("STREAK_BONUS_ENABLED", "true").lower() == "true"
        if streak_enabled and random.random() < 0.3:  # 30% chance
            max_streak_bonus = int(os.getenv("MAX_STREAK_BONUS", "8"))
            streak_bonus = random.randint(2, max_streak_bonus)
            bonus_points += int(bonus_points * bonus_multiplier) if bonus_points > 0 else streak_bonus
            bonus_reasons.append(f"Streak bonus (+{streak_bonus})")
        
        total_points = base_points + bonus_points
        
        return {
            "success": True,
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": total_points,
            "bonus_reasons": bonus_reasons,
            "calculation_details": {
                "receipt_total": receipt_data.get("total", "0"),
                "merchant": receipt_data.get("merchant", "Unknown"),
                "multiplier_applied": bonus_multiplier
            }
        }
    except Exception as e:
        fallback_points = int(os.getenv("FALLBACK_POINTS", "5"))
        return {
            "success": False,
            "error": str(e),
            "total_points": fallback_points  # Fallback minimum points
        }


@tool
def award_points_to_user(user_id: str, points: int, reason: str) -> Dict[str, Any]:
    """
    Awards points to a user and updates their balance in Firestore.
    
    Args:
        user_id: ID of the user to award points to
        points: Number of points to award
        reason: Reason for awarding points
        
    Returns:
        Dictionary containing award result and new balance
    """
    try:
        firestore_client = get_firestore_client()
        user_ref = firestore_client.collection("users").document(user_id)
        
        # Update user points using Firestore increment
        user_ref.update({"points": firestore.Increment(points)})
        
        # Get updated balance
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            new_balance = user_data.get("points", 0) if user_data else points
        else:
            new_balance = points
        
        # Log the points transaction
        transaction_ref = firestore_client.collection("point_transactions").document()
        transaction_ref.set({
            "userId": user_id,
            "points": points,
            "reason": reason,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "type": "earned"
        })
        
        return {
            "success": True,
            "points_awarded": points,
            "new_balance": new_balance,
            "reason": reason,
            "user_id": user_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "points_awarded": 0
        }


@tool
def get_user_achievements(user_id: str) -> Dict[str, Any]:
    """
    Retrieves and calculates user achievements based on their activity.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary containing user achievements and progress
    """
    try:
        firestore_client = get_firestore_client()
        
        # Get user's receipts for achievement calculation
        receipts_ref = firestore_client.collection("receipts")
        user_receipts = list(receipts_ref.where("userId", "==", user_id).stream())
        
        # Get user's current points
        user_ref = firestore_client.collection("users").document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            current_points = user_data.get("points", 0) if user_data else 0
        else:
            current_points = 0
        
        # Calculate achievements
        achievements = []
        receipt_count = len(user_receipts)
        
        # Receipt milestones
        if receipt_count >= 1:
            achievements.append({"name": "First Receipt", "description": "Uploaded your first receipt", "unlocked": True})
        if receipt_count >= 10:
            achievements.append({"name": "Receipt Collector", "description": "Uploaded 10 receipts", "unlocked": True})
        if receipt_count >= 50:
            achievements.append({"name": "Receipt Master", "description": "Uploaded 50 receipts", "unlocked": True})
        
        # Points milestones
        if current_points >= 100:
            achievements.append({"name": "Century Club", "description": "Earned 100 points", "unlocked": True})
        if current_points >= 500:
            achievements.append({"name": "Point Collector", "description": "Earned 500 points", "unlocked": True})
        
        # Calculate progress towards next achievements
        next_achievements = []
        if receipt_count < 10:
            next_achievements.append({
                "name": "Receipt Collector",
                "description": "Upload 10 receipts",
                "progress": receipt_count,
                "target": 10
            })
        elif receipt_count < 50:
            next_achievements.append({
                "name": "Receipt Master", 
                "description": "Upload 50 receipts",
                "progress": receipt_count,
                "target": 50
            })
        
        return {
            "success": True,
            "achievements": achievements,
            "next_achievements": next_achievements,
            "stats": {
                "total_receipts": receipt_count,
                "total_points": current_points,
                "achievements_unlocked": len(achievements)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "achievements": [],
            "next_achievements": []
        }
