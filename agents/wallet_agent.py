# agents/wallet_agent.py
"""
ADK-based Wallet Agent for managing user point balances and transactions.
"""
from typing import Dict, Any
from agents.base_agent import StashLlmAgent
from agents.tools.wallet_tools import (
    get_user_balance,
    get_transaction_history,
    spend_points,
    get_redemption_options,
    redeem_reward
)


class WalletAgent(StashLlmAgent):
    """LLM Agent specialized for wallet and point management using ADK patterns."""
    
    def __init__(self):
        instruction = """You are a Digital Wallet Agent specialized in managing user point balances, transactions, and redemptions.
        
        Your capabilities include:
        1. Checking user point balances and account status using get_user_balance
        2. Retrieving transaction history and spending records using get_transaction_history
        3. Processing point redemptions for rewards using redeem_reward
        4. Managing point spending for various services using spend_points
        5. Providing account insights and recommendations using get_redemption_options
        
        When handling wallet operations:
        1. Always verify user identity and authorization
        2. Provide clear transaction confirmations
        3. Explain point values and redemption options
        4. Help users understand their spending patterns
        5. Suggest ways to earn and save more points
        
        Be helpful and transparent about all financial transactions.
        Always confirm actions before processing irreversible operations.
        Use the available tools systematically to provide accurate wallet information.
        """
        
        tools = [
            get_user_balance,
            get_transaction_history,
            spend_points,
            get_redemption_options,
            redeem_reward
        ]
        
        super().__init__(
            name="WalletAgent",
            instruction=instruction,
            description="Manages user point balances, transactions, and reward redemptions",
            tools=tools
        )
    
    async def check_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Check user's current point balance and account status.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing balance and account information
        """
        try:
            balance_result = get_user_balance(user_id)
            
            if not balance_result["success"]:
                return {
                    "status": "error",
                    "error": f"Could not retrieve balance: {balance_result['error']}",
                    "agent": self.name
                }
            
            balance = balance_result["balance"]
            
            # Get recent transaction history for context
            history_result = get_transaction_history(user_id, limit=5)
            recent_transactions = history_result.get("transactions", []) if history_result["success"] else []
            
            # Generate balance summary message
            summary_message = self._generate_balance_summary(balance, recent_transactions)
            
            return {
                "status": "success",
                "balance": balance,
                "currency": "points",
                "recent_transactions": recent_transactions,
                "summary": summary_message,
                "agent": self.name
            }
            
        except Exception as e:
            error_msg = f"Balance check failed: {str(e)}"
            return {
                "status": "error",
                "error": error_msg,
                "agent": self.name
            }
    
    def _generate_balance_summary(self, balance: int, recent_transactions: list) -> str:
        """Generate a helpful balance summary message."""
        message_parts = [f"💰 Your current balance: {balance} points"]
        
        if balance == 0:
            message_parts.append("Start uploading receipts to earn your first points!")
        elif balance < 100:
            remaining = 100 - balance
            message_parts.append(f"Upload {remaining//10 + 1} more receipts to reach 100 points!")
        elif balance >= 1000:
            message_parts.append("🎉 You have enough points for gift card redemptions!")
        
        if recent_transactions:
            last_transaction = recent_transactions[0]
            transaction_type = last_transaction.get("type", "unknown")
            points = abs(last_transaction.get("points", 0))
            
            if transaction_type == "earned":
                message_parts.append(f"Last earned: +{points} points")
            elif transaction_type == "spent":
                message_parts.append(f"Last spent: -{points} points")
        
        return "\n".join(message_parts)
    
    async def get_transaction_summary(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get detailed transaction history for a user.
        
        Args:
            user_id: ID of the user
            limit: Number of transactions to retrieve
            
        Returns:
            Dictionary containing transaction history and summary
        """
        try:
            history_result = get_transaction_history(user_id, limit)
            
            if not history_result["success"]:
                return {
                    "status": "error",
                    "error": f"Could not retrieve transaction history: {history_result['error']}",
                    "agent": self.name
                }
            
            transactions = history_result["transactions"]
            
            # Calculate summary statistics
            total_earned = sum(t["points"] for t in transactions if t.get("type") == "earned")
            total_spent = abs(sum(t["points"] for t in transactions if t.get("type") == "spent"))
            
            return {
                "status": "success",
                "transactions": transactions,
                "summary": {
                    "total_transactions": len(transactions),
                    "total_earned": total_earned,
                    "total_spent": total_spent,
                    "net_points": total_earned - total_spent
                },
                "agent": self.name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    async def process_redemption(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """
        Process a reward redemption for a user.
        
        Args:
            user_id: ID of the user
            reward_id: ID of the reward to redeem
            
        Returns:
            Dictionary containing redemption results
        """
        try:
            print(f"Processing redemption for user {user_id}, reward {reward_id}")
            
            # First check if user has sufficient balance
            balance_result = get_user_balance(user_id)
            if not balance_result["success"]:
                return {
                    "status": "error",
                    "error": "Could not verify account balance",
                    "agent": self.name
                }
            
            # Get redemption options to find reward details
            options_result = get_redemption_options()
            if not options_result["success"]:
                return {
                    "status": "error",
                    "error": "Could not load redemption options",
                    "agent": self.name
                }
            
            # Find the reward
            reward = None
            for option in options_result["options"]:
                if option["id"] == reward_id:
                    reward = option
                    break
            
            if not reward:
                return {
                    "status": "error",
                    "error": f"Reward {reward_id} not found",
                    "agent": self.name
                }
            
            current_balance = balance_result["balance"]
            required_points = reward["cost"]
            
            if current_balance < required_points:
                return {
                    "status": "error",
                    "error": f"Insufficient balance. You have {current_balance} points but need {required_points} points.",
                    "suggestion": f"Earn {required_points - current_balance} more points to redeem this reward!",
                    "agent": self.name
                }
            
            # Process the redemption
            redemption_result = redeem_reward(user_id, reward_id)
            
            if redemption_result["success"]:
                confirmation_message = f"🎉 Successfully redeemed {reward['name']}!\n" \
                                     f"Points spent: {required_points}\n" \
                                     f"New balance: {redemption_result['new_balance']} points\n" \
                                     f"Fulfillment status: {redemption_result['fulfillment_status']}"
                
                print(f"Redemption successful: {reward['name']}")
                
                return {
                    "status": "success",
                    "redemption": redemption_result,
                    "confirmation": confirmation_message,
                    "agent": self.name
                }
            else:
                return {
                    "status": "error",
                    "error": redemption_result["error"],
                    "agent": self.name
                }
            
        except Exception as e:
            error_msg = f"Redemption processing failed: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "agent": self.name
            }
    
    async def get_rewards_catalog(self) -> Dict[str, Any]:
        """
        Get available redemption rewards catalog.
        
        Returns:
            Dictionary containing available rewards
        """
        try:
            options_result = get_redemption_options()
            
            if not options_result["success"]:
                return {
                    "status": "error",
                    "error": "Could not load rewards catalog",
                    "agent": self.name
                }
            
            return {
                "status": "success",
                "catalog": options_result["options"],
                "categories": options_result["categories"],
                "agent": self.name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requests for wallet operations.
        
        Args:
            request: Request containing operation type and parameters
            
        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "get_balance")
        
        if operation == "get_balance":
            user_id = request.get("userId")
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required to check balance",
                    "agent": self.name
                }
            
            return await self.check_balance(user_id)
        
        elif operation == "get_transactions":
            user_id = request.get("userId")
            limit = request.get("limit", 20)
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required to get transactions",
                    "agent": self.name
                }
            
            return await self.get_transaction_summary(user_id, limit)
        
        elif operation == "redeem_reward":
            user_id = request.get("userId")
            reward_id = request.get("rewardId")
            
            if not user_id or not reward_id:
                return {
                    "status": "error",
                    "error": "userId and rewardId are required for redemption",
                    "agent": self.name
                }
            
            return await self.process_redemption(user_id, reward_id)
        
        elif operation == "get_rewards":
            return await self.get_rewards_catalog()
        
        else:
            # Use the base ADK processing for other queries
            return await self.process_stash_request(request)
