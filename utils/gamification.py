# utils/gamification.py

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

class GamificationSystem:
    def __init__(self, workout_data, total_xp, strength_score):
        self.workout_data = workout_data
        self.total_xp = total_xp
        self.strength_score = strength_score
        
    def get_tier_info(self):
        """Get current tier and progress to next tier"""
        tiers = [
            {"name": "Bronze", "min_xp": 0, "emoji": "🥉", "color": "#CD7F32"},
            {"name": "Silver", "min_xp": 1000, "emoji": "🥈", "color": "#C0C0C0"},
            {"name": "Gold", "min_xp": 3000, "emoji": "🥇", "color": "#FFD700"},
            {"name": "Platinum", "min_xp": 6000, "emoji": "💎", "color": "#E5E4E2"},
            {"name": "Diamond", "min_xp": 10000, "emoji": "💠", "color": "#B9F2FF"},
            {"name": "Master", "min_xp": 20000, "emoji": "👑", "color": "#FF6B00"},
            {"name": "Grandmaster", "min_xp": 50000, "emoji": "🌟", "color": "#FFD700"},
            {"name": "Legend", "min_xp": 100000, "emoji": "🏆", "color": "#FF004D"}
        ]
        
        current_tier = tiers[0]
        next_tier = tiers[1] if len(tiers) > 1 else None
        
        for i, tier in enumerate(tiers):
            if self.total_xp >= tier["min_xp"]:
                current_tier = tier
                if i + 1 < len(tiers):
                    next_tier = tiers[i + 1]
                else:
                    next_tier = None
        
        if next_tier:
            xp_to_next = next_tier["min_xp"] - self.total_xp
            xp_in_tier = self.total_xp - current_tier["min_xp"]
            tier_progress = xp_in_tier / (next_tier["min_xp"] - current_tier["min_xp"])
        else:
            xp_to_next = 0
            tier_progress = 1.0
        
        return {
            "current": current_tier,
            "next": next_tier,
            "xp_to_next": xp_to_next,
            "progress": min(tier_progress, 1.0),
            "xp_in_tier": self.total_xp - current_tier["min_xp"]
        }
    
    def get_challenges(self):
        """Generate active and upcoming challenges"""
        today = datetime.now().date()
        
        challenges = []
        
        # 1. Streak challenge
        streak = self._calculate_streak()
        if streak > 0:
            challenges.append({
                "id": "streak",
                "name": "🔥 Streak Master",
                "description": f"Maintain your {streak}-day streak for {max(0, 7 - streak)} more days",
                "progress": min(streak / 7, 1.0),
                "reward": "500 XP + Streak Badge",
                "completed": streak >= 7,
                "type": "daily"
            })
        
        # 2. Volume challenge
        weekly_volume = self._get_weekly_volume()
        if weekly_volume > 0:
            target_volume = 5000  # 5,000 kg target
            challenges.append({
                "id": "volume",
                "name": "💪 Volume King",
                "description": f"Lift {target_volume}kg this week (Current: {weekly_volume:.0f}kg)",
                "progress": min(weekly_volume / target_volume, 1.0),
                "reward": "300 XP + Volume Badge",
                "completed": weekly_volume >= target_volume,
                "type": "weekly"
            })
        
        # 3. Exercise variety challenge
        unique_exercises = len(set(row[1] for row in self.workout_data))
        if unique_exercises > 0:
            target_exercises = 10
            challenges.append({
                "id": "variety",
                "name": "🎯 Variety Master",
                "description": f"Perform {target_exercises} different exercises (Current: {unique_exercises})",
                "progress": min(unique_exercises / target_exercises, 1.0),
                "reward": "200 XP + Variety Badge",
                "completed": unique_exercises >= target_exercises,
                "type": "progress"
            })
        
        # 4. PR challenge
        prs = self._get_pr_count()
        if prs > 0:
            target_prs = 5
            challenges.append({
                "id": "pr",
                "name": "🏆 PR Hunter",
                "description": f"Set {target_prs} personal records (Current: {prs})",
                "progress": min(prs / target_prs, 1.0),
                "reward": "400 XP + PR Badge",
                "completed": prs >= target_prs,
                "type": "progress"
            })
        
        # 5. Consistency challenge
        days_active = self._get_active_days()
        if days_active > 0:
            target_days = 14
            challenges.append({
                "id": "consistency",
                "name": "📅 Consistency King",
                "description": f"Workout {target_days} days this month (Current: {days_active})",
                "progress": min(days_active / target_days, 1.0),
                "reward": "250 XP + Consistency Badge",
                "completed": days_active >= target_days,
                "type": "monthly"
            })
        
        return challenges
    
    def _calculate_streak(self):
        """Calculate current streak from workout data"""
        if not self.workout_data:
            return 0
        
        dates = []
        for row in self.workout_data:
            workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
            dates.append(workout_date)
        
        dates = sorted(set(dates), reverse=True)
        
        if not dates:
            return 0
        
        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i+1]).days == 1:
                streak += 1
            else:
                break
        
        return streak
    
    def _get_weekly_volume(self):
        """Calculate current week's volume"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_volume = 0
        for row in self.workout_data:
            workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
            if workout_date >= week_start:
                weekly_volume += row[5]  # volume
        
        return weekly_volume
    
    def _get_pr_count(self):
        """Count number of personal records set"""
        pr_exercises = set()
        for row in self.workout_data:
            pr_exercises.add(row[1])  # exercise name
        return len(pr_exercises)
    
    def _get_active_days(self):
        """Count active days in current month"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        active_days = set()
        for row in self.workout_data:
            workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
            if workout_date >= month_start:
                active_days.add(workout_date)
        
        return len(active_days)
    
    def get_achievement_stats(self):
        """Get detailed achievement statistics"""
        stats = {
            "total_achievements": 0,
            "unlocked": [],
            "locked": [],
            "progress_percentage": 0
        }
        
        all_achievements = [
            {"id": "first_workout", "name": "First Workout", "emoji": "🎉", "condition": lambda x: len(x.workout_data) >= 1},
            {"id": "streak_3", "name": "3-Day Streak", "emoji": "🔥", "condition": lambda x: x._calculate_streak() >= 3},
            {"id": "streak_7", "name": "7-Day Streak", "emoji": "🔥", "condition": lambda x: x._calculate_streak() >= 7},
            {"id": "streak_30", "name": "30-Day Warrior", "emoji": "⚡", "condition": lambda x: x._calculate_streak() >= 30},
            {"id": "volume_1000", "name": "1,000kg Club", "emoji": "💪", "condition": lambda x: sum(row[5] for row in x.workout_data) >= 1000},
            {"id": "volume_10000", "name": "10,000kg Club", "emoji": "🏋️", "condition": lambda x: sum(row[5] for row in x.workout_data) >= 10000},
            {"id": "exercises_10", "name": "Exercise Variety", "emoji": "🎯", "condition": lambda x: len(set(row[1] for row in x.workout_data)) >= 10},
            {"id": "exercises_25", "name": "Exercise Master", "emoji": "🌟", "condition": lambda x: len(set(row[1] for row in x.workout_data)) >= 25},
            {"id": "pr_5", "name": "PR Hunter", "emoji": "🏆", "condition": lambda x: len(set(row[1] for row in x.workout_data)) >= 5},
            {"id": "pr_10", "name": "PR Collector", "emoji": "👑", "condition": lambda x: len(set(row[1] for row in x.workout_data)) >= 10},
            {"id": "xp_1000", "name": "1K XP", "emoji": "🥈", "condition": lambda x: x.total_xp >= 1000},
            {"id": "xp_5000", "name": "5K XP", "emoji": "🥇", "condition": lambda x: x.total_xp >= 5000},
            {"id": "xp_10000", "name": "10K XP Master", "emoji": "💎", "condition": lambda x: x.total_xp >= 10000},
            {"id": "strength_500", "name": "Strong Athlete", "emoji": "💪", "condition": lambda x: x.strength_score >= 500},
            {"id": "strength_800", "name": "Elite Athlete", "emoji": "⚡", "condition": lambda x: x.strength_score >= 800},
            {"id": "workout_50", "name": "50 Workouts", "emoji": "🔥", "condition": lambda x: len(x.workout_data) >= 50},
            {"id": "workout_100", "name": "100 Workouts", "emoji": "🌟", "condition": lambda x: len(x.workout_data) >= 100},
        ]
        
        for achievement in all_achievements:
            try:
                unlocked = achievement["condition"](self)
                if unlocked:
                    stats["unlocked"].append(achievement)
                else:
                    stats["locked"].append(achievement)
            except:
                pass
        
        stats["total_achievements"] = len(all_achievements)
        stats["progress_percentage"] = (len(stats["unlocked"]) / len(all_achievements)) * 100 if all_achievements else 0
        
        return stats
    
    def get_social_stats(self):
        """Generate social-friendly statistics for sharing"""
        total_workouts = len(self.workout_data)
        total_volume = sum(row[5] for row in self.workout_data)
        unique_exercises = len(set(row[1] for row in self.workout_data))
        best_lift = max((row[2] for row in self.workout_data), default=0)
        
        tier_info = self.get_tier_info()
        
        return {
            "tier": tier_info["current"]["name"],
            "tier_emoji": tier_info["current"]["emoji"],
            "total_workouts": total_workouts,
            "total_volume": f"{total_volume:.0f}kg",
            "unique_exercises": unique_exercises,
            "best_lift": f"{best_lift:.0f}kg",
            "total_xp": self.total_xp,
            "strength_score": self.strength_score,
            "share_text": f"💪 Just reached {tier_info['current']['name']} tier in GymRank AI! 🏋️\n"
                         f"{total_workouts} workouts • {total_volume:.0f}kg volume • {unique_exercises} exercises\n"
                         f"Best lift: {best_lift:.0f}kg • XP: {self.total_xp}\n"
                         f"#GymRankAI #FitnessJourney 💪"
        }