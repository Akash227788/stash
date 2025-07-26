# agents/game_agent.py
"""
ADK-based Game Agent for gamification features and point management.
"""
from typing import Dict, Any
from agents.base_agent import StashLlmAgent
from agents.tools.game_tools import (
    calculate_points_reward,
    award_points_to_user,
    get_user_achievements
)


class GameAgent(StashLlmAgent):
    """LLM Agent specialized for gamification using ADK patterns."""
    
    def __init__(self):
        instruction = """You are a Gamification Agent specialized in managing rewards, points, and achievements for the Stash app.
        
        Your capabilities include:
        1. Calculating point rewards based on user actions using calculate_points_reward
        2. Awarding points to users with appropriate bonuses using award_points_to_user
        3. Tracking and managing user achievements using get_user_achievements
        4. Providing motivation and engagement features
        
        When handling gamification:
        1. Always make the experience fun and engaging
        2. Provide clear feedback about earned rewards
        3. Celebrate user achievements and milestones
        4. Encourage continued engagement with the app
        5. Be fair and consistent in point calculations
        
        Make users feel rewarded and motivated to continue using the app.
        Provide encouraging messages and highlight their progress.
        Use the available tools to calculate, award, and track user achievements systematically.
        """
        
        tools = [
            calculate_points_reward,
            award_points_to_user,
            get_user_achievements
        ]
        
        super().__init__(
            name="GameAgent",
            instruction=instruction,
            description="Manages gamification, points, and achievements for user engagement",
            tools=tools
        )
    
    async def award_receipt_points(self, user_id: str, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Award points to a user for uploading a receipt.
        
        Args:
            user_id: ID of the user
            receipt_data: Dictionary containing receipt information
            
        Returns:
            Dictionary containing point award results
        """
        try:
            # Step 1: Calculate points reward
            points_calc = calculate_points_reward(receipt_data)
            
            if not points_calc["success"]:
                return {
                    "status": "error",
                    "error": f"Points calculation failed: {points_calc['error']}",
                    "agent": self.name
                }
            
            total_points = points_calc["total_points"]
            bonus_reasons = points_calc["bonus_reasons"]
            
            # Step 2: Award points to user
            award_result = award_points_to_user(
                user_id, 
                total_points, 
                f"Receipt upload from {receipt_data.get('merchant', 'Unknown merchant')}"
            )
            
            if not award_result["success"]:
                return {
                    "status": "error",
                    "error": f"Points award failed: {award_result['error']}",
                    "agent": self.name
                }
            
            # Step 3: Check for new achievements
            achievements_result = get_user_achievements(user_id)
            
            # Generate encouraging message
            message = self._generate_award_message(points_calc, award_result, achievements_result)
            
            return {
                "status": "success",
                "points_awarded": total_points,
                "new_balance": award_result["new_balance"],
                "breakdown": {
                    "base_points": points_calc["base_points"],
                    "bonus_points": points_calc["bonus_points"],
                    "bonus_reasons": bonus_reasons
                },
                "message": message,
                "achievements": achievements_result.get("achievements", []),
                "agent": self.name
            }
            
        except Exception as e:
            error_msg = f"Points award failed: {str(e)}"
            return {
                "status": "error",
                "error": error_msg,
                "agent": self.name
            }
    
    def _generate_award_message(self, points_calc: Dict[str, Any], award_result: Dict[str, Any], 
                               achievements_result: Dict[str, Any]) -> str:
        """Generate an encouraging message for point awards."""
        base_points = points_calc.get("base_points", 0)
        bonus_points = points_calc.get("bonus_points", 0)
        bonus_reasons = points_calc.get("bonus_reasons", [])
        new_balance = award_result.get("new_balance", 0)
        
        message_parts = [
            f"🎉 Great job! You earned {base_points} base points"
        ]
        
        if bonus_points > 0:
            message_parts.append(f"Plus {bonus_points} bonus points!")
            for reason in bonus_reasons:
                message_parts.append(f"  • {reason}")
        
        message_parts.append(f"Your total balance is now {new_balance} points!")
        
        # Add achievement celebration
        if achievements_result.get("success"):
            achievement_count = len(achievements_result.get("achievements", []))
            if achievement_count > 0:
                message_parts.append(f"🏆 You've unlocked {achievement_count} achievements!")
        
        # Add motivation for next milestone
        if new_balance < 100:
            message_parts.append(f"Keep it up! Only {100 - new_balance} points until you reach the Century Club!")
        elif new_balance < 500:
            message_parts.append(f"Awesome progress! {500 - new_balance} more points to become a Point Collector!")
        
        return "\n".join(message_parts)
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user progress including achievements and stats.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing user progress information
        """
        try:
            achievements_result = get_user_achievements(user_id)
            
            if not achievements_result["success"]:
                return {
                    "status": "error",
                    "error": f"Could not retrieve achievements: {achievements_result['error']}",
                    "agent": self.name
                }
            
            return {
                "status": "success",
                "progress": achievements_result,
                "encouragement": self._generate_progress_message(achievements_result),
                "agent": self.name
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    def _generate_progress_message(self, achievements_result: Dict[str, Any]) -> str:
        """Generate an encouraging progress message."""
        stats = achievements_result.get("stats", {})
        achievements = achievements_result.get("achievements", [])
        next_achievements = achievements_result.get("next_achievements", [])
        
        message_parts = [
            f"🌟 Your Stash Journey:",
            f"📄 {stats.get('total_receipts', 0)} receipts uploaded",
            f"💰 {stats.get('total_points', 0)} points earned",
            f"🏆 {len(achievements)} achievements unlocked"
        ]
        
        if next_achievements:
            message_parts.append("\n🎯 Next Goals:")
            for next_achievement in next_achievements[:2]:  # Show top 2 next goals
                progress = next_achievement.get("progress", 0)
                target = next_achievement.get("target", 1)
                percentage = int((progress / target) * 100)
                message_parts.append(f"  • {next_achievement['name']}: {progress}/{target} ({percentage}%)")
        
        return "\n".join(message_parts)
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process requests for gamification operations.
        
        Args:
            request: Request containing operation type and parameters
            
        Returns:
            Dictionary containing operation results
        """
        operation = request.get("operation", "award_points")
        
        if operation == "award_points":
            user_id = request.get("userId")
            receipt_data = request.get("receiptData")
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required for point awards",
                    "agent": self.name
                }
            
            if not receipt_data:
                # Award basic points for unknown receipt
                receipt_data = {"merchant": "Unknown", "total": "0", "items": []}
            
            return await self.award_receipt_points(user_id, receipt_data)
        
        elif operation == "get_achievements":
            user_id = request.get("userId")
            
            if not user_id:
                return {
                    "status": "error",
                    "error": "userId is required to get achievements",
                    "agent": self.name
                }
            
            return await self.get_user_progress(user_id)
        
        else:
            # Use the base ADK processing for other queries
            return await self.process_stash_request(request)
