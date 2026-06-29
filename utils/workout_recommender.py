# utils/workout_recommender.py

import random
from datetime import datetime, timedelta
from collections import Counter

class WorkoutRecommender:
    def __init__(self, workout_data):
        """
        Initialize with workout history data
        workout_data: list of tuples (id, exercise, weight, reps, sets, volume, xp, rank, date)
        """
        self.workout_data = workout_data
        self.exercise_history = self._analyze_history()
    
    def _analyze_history(self):
        """Analyze workout history to understand patterns"""
        history = {}
        
        for row in self.workout_data:
            exercise = row[1]
            weight = row[2]
            date = row[8]
            
            if exercise not in history:
                history[exercise] = {
                    'count': 0,
                    'avg_weight': 0,
                    'last_done': None,
                    'weights': []
                }
            
            history[exercise]['count'] += 1
            history[exercise]['weights'].append(weight)
            history[exercise]['last_done'] = date
        
        # Calculate average weights
        for exercise in history:
            if history[exercise]['weights']:
                history[exercise]['avg_weight'] = sum(history[exercise]['weights']) / len(history[exercise]['weights'])
        
        return history
    
    def get_weak_muscles(self):
        """Identify muscle groups that need more training"""
        from utils.muscle_mapper import get_muscle_group
        
        muscle_counts = {}
        muscle_weights = {}
        
        for row in self.workout_data:
            exercise = row[1]
            muscle = get_muscle_group(exercise)
            weight = row[2]
            
            muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
            if muscle not in muscle_weights:
                muscle_weights[muscle] = []
            muscle_weights[muscle].append(weight)
        
        # Calculate average weight per muscle
        avg_weights = {}
        for muscle, weights in muscle_weights.items():
            avg_weights[muscle] = sum(weights) / len(weights) if weights else 0
        
        return {
            'counts': muscle_counts,
            'avg_weights': avg_weights
        }
    
    def suggest_exercises(self, num_suggestions=5):
        """Suggest exercises based on workout history"""
        suggestions = []
        
        # 1. Exercises you haven't done in a while
        today = datetime.today().date()
        for exercise, data in self.exercise_history.items():
            if data['last_done']:
                last_date = datetime.strptime(data['last_done'], "%Y-%m-%d").date()
                days_ago = (today - last_date).days
                if days_ago > 7:  # Not done in a week
                    suggestions.append({
                        'exercise': exercise,
                        'reason': f"Not done in {days_ago} days",
                        'priority': min(days_ago / 30, 1.0)  # Higher priority for longer absence
                    })
        
        # 2. Exercises you're getting stronger at (good for PR attempts)
        for exercise, data in self.exercise_history.items():
            if len(data['weights']) >= 3:
                recent_avg = sum(data['weights'][-3:]) / 3
                overall_avg = data['avg_weight']
                if recent_avg > overall_avg * 1.05:  # 5% improvement
                    suggestions.append({
                        'exercise': exercise,
                        'reason': f"You're improving! Recent avg: {recent_avg:.1f}kg",
                        'priority': 0.8
                    })
        
        # 3. Suggest exercises for weak muscles
        weak_muscles = self.get_weak_muscles()
        if weak_muscles['counts']:
            min_count = min(weak_muscles['counts'].values()) if weak_muscles['counts'] else 0
            for muscle, count in weak_muscles['counts'].items():
                if count <= min_count + 1 and count > 0:
                    # Suggest an exercise for this muscle
                    from utils.muscle_mapper import MUSCLE_GROUPS
                    exercises_for_muscle = MUSCLE_GROUPS.get(muscle, [])
                    if exercises_for_muscle:
                        # Pick an exercise not done recently
                        for ex in exercises_for_muscle[:3]:
                            if ex not in self.exercise_history or self.exercise_history[ex]['last_done']:
                                days_ago = 0
                                if ex in self.exercise_history and self.exercise_history[ex]['last_done']:
                                    last_date = datetime.strptime(self.exercise_history[ex]['last_done'], "%Y-%m-%d").date()
                                    days_ago = (today - last_date).days
                                if days_ago > 3:  # Not done in 3 days
                                    suggestions.append({
                                        'exercise': ex.capitalize(),
                                        'reason': f"Target {muscle.capitalize()} (low training frequency)",
                                        'priority': 0.9
                                    })
                                    break
        
        # Remove duplicates and sort by priority
        unique_suggestions = {}
        for s in suggestions:
            if s['exercise'] not in unique_suggestions or unique_suggestions[s['exercise']]['priority'] < s['priority']:
                unique_suggestions[s['exercise']] = s
        
        # Sort by priority
        sorted_suggestions = sorted(unique_suggestions.values(), key=lambda x: x['priority'], reverse=True)
        
        # Return top suggestions
        return sorted_suggestions[:num_suggestions]
    
    def get_progressive_overload_suggestion(self):
        """Suggest weight increase for exercises you're consistent with"""
        suggestions = []
        
        for exercise, data in self.exercise_history.items():
            if len(data['weights']) >= 4:
                # Check if weights have been consistent
                recent_weights = data['weights'][-4:]
                if len(set(recent_weights)) <= 2:  # Mostly same weight
                    avg_weight = sum(recent_weights) / len(recent_weights)
                    # Suggest 2.5kg increase if all reps were completed
                    suggestions.append({
                        'exercise': exercise,
                        'current_weight': avg_weight,
                        'suggested_weight': avg_weight + 2.5,
                        'reason': f"Consistent at {avg_weight:.1f}kg - time to increase!",
                        'priority': 0.7
                    })
        
        return suggestions[:3]
    
    def get_volume_suggestion(self):
        """Suggest volume adjustments based on recent training"""
        if len(self.workout_data) < 5:
            return None
        
        # Calculate average volume per week
        today = datetime.today().date()
        weekly_volumes = []
        
        for i in range(4):  # Last 4 weeks
            week_start = today - timedelta(days=(i+1)*7)
            week_end = today - timedelta(days=i*7)
            week_volume = 0
            week_count = 0
            
            for row in self.workout_data:
                workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                if week_start <= workout_date < week_end:
                    week_volume += row[5]  # volume
                    week_count += 1
            
            if week_count > 0:
                weekly_volumes.append(week_volume / week_count)
        
        if weekly_volumes:
            avg_volume = sum(weekly_volumes) / len(weekly_volumes)
            last_week_volume = weekly_volumes[0] if weekly_volumes else 0
            
            if last_week_volume < avg_volume * 0.8:
                return {
                    'type': 'increase',
                    'message': f"📈 Your volume was {last_week_volume:.0f}kg last week vs {avg_volume:.0f}kg average. Try adding an extra set or exercise!",
                    'priority': 0.6
                }
            elif last_week_volume > avg_volume * 1.3:
                return {
                    'type': 'maintain',
                    'message': f"🔥 Great volume last week! Consider a lighter week for recovery.",
                    'priority': 0.5
                }
        
        return None