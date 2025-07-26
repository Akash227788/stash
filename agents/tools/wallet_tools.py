# agents/tools/wallet_tools.py
"""
ADK-style tools for digital wallet functionality.
"""
from typing import Dict, Any, List
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
def get_user_balance(user_id: str) -> Dict[str, Any]:
    """
    Retrieves the current point balance for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary containing user balance and account information
    """
    try:
        firestore_client = get_firestore_client()
        user_ref = firestore_client.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # Create new user with 0 balance
            user_ref.set({"points": 0, "created_at": firestore.SERVER_TIMESTAMP})
            balance = 0
        else:
            user_data = user_doc.to_dict()
            balance = user_data.get("points", 0) if user_data else 0
        
        return {
            "success": True,
            "balance": balance,
            "user_id": user_id,
            "currency": "points"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "balance": 0
        }


@tool
def get_transaction_history(user_id: str, limit: int = 20) -> Dict[str, Any]:
    """
    Retrieves transaction history for a user's point account.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of transactions to retrieve
        
    Returns:
        Dictionary containing transaction history
    """
    try:
        firestore_client = get_firestore_client()
        transactions_ref = firestore_client.collection("point_transactions")
        
        query = (transactions_ref
                .where("userId", "==", user_id)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit))
        
        transactions = []
        for doc in query.stream():
            transaction_data = doc.to_dict()
            transaction_data["id"] = doc.id
            transactions.append(transaction_data)
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions),
            "user_id": user_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "transactions": [],
            "count": 0
        }


@tool
def spend_points(user_id: str, points: int, reason: str) -> Dict[str, Any]:
    """
    Deducts points from a user's balance for redemptions or spending.
    
    Args:
        user_id: ID of the user
        points: Number of points to spend (positive number)
        reason: Reason for spending points
        
    Returns:
        Dictionary containing spending result and new balance
    """
    try:
        firestore_client = get_firestore_client()
        user_ref = firestore_client.collection("users").document(user_id)
        
        # Get current balance first
        user_doc = user_ref.get()
        if not user_doc.exists:
            return {
                "success": False,
                "error": "User not found",
                "new_balance": 0
            }
        
        user_data = user_doc.to_dict()
        current_balance = user_data.get("points", 0) if user_data else 0
        
        # Check if user has enough points
        if current_balance < points:
            return {
                "success": False,
                "error": f"Insufficient balance. Current: {current_balance}, Required: {points}",
                "new_balance": current_balance
            }
        
        # Deduct points
        user_ref.update({"points": firestore.Increment(-points)})
        new_balance = current_balance - points
        
        # Log the spending transaction
        transaction_ref = firestore_client.collection("point_transactions").document()
        transaction_ref.set({
            "userId": user_id,
            "points": -points,  # Negative for spending
            "reason": reason,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "type": "spent"
        })
        
        return {
            "success": True,
            "points_spent": points,
            "new_balance": new_balance,
            "reason": reason,
            "user_id": user_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "points_spent": 0
        }


@tool
def get_redemption_options() -> Dict[str, Any]:
    """
    Retrieves available point redemption options/rewards.
    
    Returns:
        Dictionary containing available redemption options
    """
    try:
        # This could be stored in Firestore in a real application
        redemption_options = [
            {
                "id": "gift_card_10",
                "name": "$10 Gift Card",
                "description": "Redeem for a $10 gift card to popular retailers",
                "cost": 1000,
                "category": "gift_cards",
                "available": True
            },
            {
                "id": "gift_card_25",
                "name": "$25 Gift Card", 
                "description": "Redeem for a $25 gift card to popular retailers",
                "cost": 2500,
                "category": "gift_cards",
                "available": True
            },
            {
                "id": "discount_5",
                "name": "5% Cashback Boost",
                "description": "Get 5% extra cashback on your next 3 receipts",
                "cost": 500,
                "category": "boosts",
                "available": True
            },
            {
                "id": "premium_insights",
                "name": "Premium Analytics Report",
                "description": "Get detailed spending insights and budgeting advice",
                "cost": 300,
                "category": "services",
                "available": True
            }
        ]
        
        return {
            "success": True,
            "options": redemption_options,
            "categories": ["gift_cards", "boosts", "services"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "options": []
        }


@tool
def redeem_reward(user_id: str, reward_id: str) -> Dict[str, Any]:
    """
    Processes a reward redemption for a user.
    
    Args:
        user_id: ID of the user
        reward_id: ID of the reward to redeem
        
    Returns:
        Dictionary containing redemption result
    """
    try:
        # Get redemption options to find the reward
        options_result = get_redemption_options()
        if not options_result["success"]:
            return {
                "success": False,
                "error": "Could not load redemption options"
            }
        
        # Find the specific reward
        reward = None
        for option in options_result["options"]:
            if option["id"] == reward_id:
                reward = option
                break
        
        if not reward:
            return {
                "success": False,
                "error": f"Reward {reward_id} not found"
            }
        
        if not reward["available"]:
            return {
                "success": False,
                "error": f"Reward {reward['name']} is currently unavailable"
            }
        
        # Spend the points
        spend_result = spend_points(user_id, reward["cost"], f"Redeemed: {reward['name']}")
        
        if not spend_result["success"]:
            return spend_result
        
        # Log the redemption (in a real app, this would trigger fulfillment)
        firestore_client = get_firestore_client()
        redemption_ref = firestore_client.collection("redemptions").document()
        redemption_ref.set({
            "userId": user_id,
            "rewardId": reward_id,
            "rewardName": reward["name"],
            "pointsCost": reward["cost"],
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "pending_fulfillment"
        })
        
        return {
            "success": True,
            "reward_redeemed": reward["name"],
            "points_spent": reward["cost"],
            "new_balance": spend_result["new_balance"],
            "fulfillment_status": "pending"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
