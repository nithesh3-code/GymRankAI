# utils/ai_exercise_tracker.py

import random
from datetime import datetime, timedelta
from collections import defaultdict
from utils.muscle_mapper import get_muscle_group, MUSCLE_GROUPS
import numpy as np

class AIExerciseTracker:
    def __init__(self, workout_data):
        """
        Initialize with workout history
        workout_data: list of tuples (id, exercise, weight, reps, sets, volume, xp, rank, date)
        """
        self.workout_data = workout_data
        self.exercise_history = self._analyze_history()
        self.today = datetime.today().date()
    
    def _analyze_history(self):
        """Analyze workout history for patterns"""
        history = {}
        
        for row in self.workout_data:
            exercise = row[1]
            weight = row[2]
            reps = row[3]
            sets = row[4]
            date = row[8]
            muscle = get_muscle_group(exercise)
            
            if exercise not in history:
                history[exercise] = {
                    'count': 0,
                    'weights': [],
                    'reps': [],
                    'sets': [],
                    'last_done': None,
                    'muscle': muscle,
                    'dates': [],
                    'max_weight': 0,
                    'avg_weight': 0,
                    'best_reps': 0,
                    'total_volume': 0,
                    'recent_weights': []  # Track recent progress
                }
            
            history[exercise]['count'] += 1
            history[exercise]['weights'].append(weight)
            history[exercise]['reps'].append(reps)
            history[exercise]['sets'].append(sets)
            history[exercise]['dates'].append(date)
            history[exercise]['last_done'] = date
            history[exercise]['max_weight'] = max(history[exercise]['max_weight'], weight)
            history[exercise]['best_reps'] = max(history[exercise]['best_reps'], reps)
            history[exercise]['total_volume'] += weight * reps * sets
            history[exercise]['recent_weights'].append(weight)
            
            # Keep only last 10 weights for trend analysis
            if len(history[exercise]['recent_weights']) > 10:
                history[exercise]['recent_weights'] = history[exercise]['recent_weights'][-10:]
        
        # Calculate averages
        for exercise in history:
            if history[exercise]['weights']:
                history[exercise]['avg_weight'] = sum(history[exercise]['weights']) / len(history[exercise]['weights'])
        
        return history
    
    def get_today_analysis(self):
        """Analyze today's workout and provide insights"""
        today_str = self.today.strftime("%Y-%m-%d")
        today_workouts = []
        
        for row in self.workout_data:
            if row[8] == today_str:
                today_workouts.append(row)
        
        if not today_workouts:
            return {
                'has_workout': False,
                'message': "No workout logged today. Time to get moving! 💪",
                'suggestion': "Start your workout and track your progress."
            }
        
        # Analyze today's exercises
        exercises_done = []
        muscles_worked = set()
        total_volume = 0
        total_xp = 0
        prs_today = []
        exercise_details = []
        
        for row in today_workouts:
            exercise = row[1]
            weight = row[2]
            reps = row[3]
            sets = row[4]
            volume = row[5]
            xp = row[6]
            muscle = get_muscle_group(exercise)
            
            exercises_done.append(exercise)
            muscles_worked.add(muscle)
            total_volume += volume
            total_xp += xp
            
            exercise_details.append({
                'exercise': exercise,
                'weight': weight,
                'reps': reps,
                'sets': sets,
                'muscle': muscle
            })
            
            # Check if this was a PR
            if exercise in self.exercise_history:
                if weight >= self.exercise_history[exercise]['max_weight'] and weight > 0:
                    prs_today.append(exercise)
        
        return {
            'has_workout': True,
            'exercises': exercises_done,
            'muscles': list(muscles_worked),
            'total_volume': total_volume,
            'total_xp': total_xp,
            'prs': prs_today,
            'exercise_count': len(exercises_done),
            'muscle_count': len(muscles_worked),
            'exercise_details': exercise_details
        }
    
    def get_muscle_suggestions(self):
        """Suggest exercises for muscle groups that need attention"""
        suggestions = []
        
        # Get all muscles trained
        muscle_training = defaultdict(lambda: {'count': 0, 'last_done': None, 'exercises': [], 'total_volume': 0})
        
        for exercise, data in self.exercise_history.items():
            muscle = data['muscle']
            muscle_training[muscle]['count'] += data['count']
            muscle_training[muscle]['last_done'] = data['last_done']
            muscle_training[muscle]['exercises'].append(exercise)
            muscle_training[muscle]['total_volume'] += data['total_volume']
        
        # Find muscles that need work
        all_muscles = list(MUSCLE_GROUPS.keys())
        trained_muscles = list(muscle_training.keys())
        
        # Muscles never trained
        for muscle in all_muscles:
            if muscle not in trained_muscles and muscle != 'other':
                suggestions.append({
                    'muscle': muscle,
                    'reason': 'Never trained',
                    'priority': 'high',
                    'suggested_exercises': MUSCLE_GROUPS.get(muscle, [])[:3],
                    'emoji': '🚨'
                })
        
        # Muscles with low frequency
        for muscle, data in muscle_training.items():
            if muscle == 'other':
                continue
            if data['count'] < 3:  # Less than 3 times
                suggestions.append({
                    'muscle': muscle,
                    'reason': f'Only trained {data["count"]} times',
                    'priority': 'medium',
                    'suggested_exercises': MUSCLE_GROUPS.get(muscle, [])[:3],
                    'emoji': '⚠️'
                })
        
        # Muscles not trained recently (7+ days)
        for muscle, data in muscle_training.items():
            if muscle == 'other':
                continue
            if data['last_done']:
                last_date = datetime.strptime(data['last_done'], "%Y-%m-%d").date()
                days_ago = (self.today - last_date).days
                if days_ago > 7:
                    suggestions.append({
                        'muscle': muscle,
                        'reason': f'Not trained in {days_ago} days',
                        'priority': 'medium',
                        'suggested_exercises': MUSCLE_GROUPS.get(muscle, [])[:3],
                        'emoji': '⏰'
                    })
        
        return suggestions
    
    def get_exercise_suggestions_for_muscle(self, muscle):
        """Get specific exercise suggestions for a muscle group"""
        exercises = MUSCLE_GROUPS.get(muscle, [])
        
        # Filter out exercises already done recently
        recent_exercises = []
        for exercise, data in self.exercise_history.items():
            if data['muscle'] == muscle and data['last_done']:
                last_date = datetime.strptime(data['last_done'], "%Y-%m-%d").date()
                days_ago = (self.today - last_date).days
                if days_ago < 7:
                    recent_exercises.append(exercise)
        
        # Suggest exercises not done recently
        suggestions = []
        for exercise in exercises:
            if exercise not in recent_exercises:
                suggestions.append(exercise)
        
        return suggestions[:5]
    
    def get_workout_recommendation(self):
        """Generate a complete workout recommendation"""
        today_analysis = self.get_today_analysis()
        muscle_suggestions = self.get_muscle_suggestions()
        
        recommendation = {
            'has_workout_today': today_analysis['has_workout'],
            'today_summary': today_analysis,
            'muscle_improvements': muscle_suggestions,
            'recommended_workout': []
        }
        
        # Generate recommended workout based on muscle suggestions
        if muscle_suggestions:
            # Prioritize high priority suggestions
            high_priority = [s for s in muscle_suggestions if s['priority'] == 'high']
            medium_priority = [s for s in muscle_suggestions if s['priority'] == 'medium']
            
            selected_muscles = high_priority[:2] + medium_priority[:2]
            
            for muscle_data in selected_muscles:
                muscle = muscle_data['muscle']
                exercises = self.get_exercise_suggestions_for_muscle(muscle)
                if exercises:
                    recommendation['recommended_workout'].append({
                        'muscle': muscle,
                        'exercises': exercises[:2],
                        'reason': muscle_data['reason'],
                        'emoji': muscle_data['emoji']
                    })
        
        return recommendation
    
    def get_fatigue_analysis(self):
        """Analyze training fatigue and suggest recovery"""
        if len(self.workout_data) < 3:
            return {
                'fatigue_level': 'low',
                'message': 'Keep building your training history!',
                'suggestion': 'Continue with your regular routine.',
                'emoji': '💪',
                'recent_workouts': len(self.workout_data),
                'recent_volume': sum(row[5] for row in self.workout_data)
            }
        
        # Calculate recent training volume (last 7 days)
        week_ago = self.today - timedelta(days=7)
        recent_volume = 0
        recent_workouts = 0
        muscle_volume = defaultdict(float)
        
        for row in self.workout_data:
            workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
            if workout_date >= week_ago:
                recent_volume += row[5]
                recent_workouts += 1
                muscle = get_muscle_group(row[1])
                muscle_volume[muscle] += row[5]
        
        # Calculate average volume per workout
        avg_volume = recent_volume / recent_workouts if recent_workouts > 0 else 0
        
        # Determine fatigue level
        if recent_workouts > 5 and avg_volume > 2000:
            fatigue = {
                'fatigue_level': 'high',
                'message': f'You\'ve had {recent_workouts} workouts with high volume recently.',
                'suggestion': 'Take a light day or active recovery. Focus on mobility.',
                'emoji': '🔴',
                'recent_workouts': recent_workouts,
                'recent_volume': recent_volume,
                'muscle_volume': dict(muscle_volume)
            }
        elif recent_workouts > 4 and avg_volume > 1000:
            fatigue = {
                'fatigue_level': 'medium',
                'message': f'Consistent training with {recent_workouts} workouts this week.',
                'suggestion': 'Consider a lighter session or focus on different muscle groups',
                'emoji': '🟡',
                'recent_workouts': recent_workouts,
                'recent_volume': recent_volume,
                'muscle_volume': dict(muscle_volume)
            }
        else:
            fatigue = {
                'fatigue_level': 'low',
                'message': f'You\'re in good shape! Keep up the consistency.',
                'suggestion': 'Great time to push for new PRs!',
                'emoji': '🟢',
                'recent_workouts': recent_workouts,
                'recent_volume': recent_volume,
                'muscle_volume': dict(muscle_volume)
            }
        
        return fatigue
    
    # ============================================
    # NEW AI FEATURES
    # ============================================
    
    def predict_next_pr(self, exercise):
        """Predict when you'll hit your next PR and at what weight"""
        if exercise not in self.exercise_history:
            return None
        
        data = self.exercise_history[exercise]
        weights = data['weights']
        
        if len(weights) < 3:
            return {
                'exercise': exercise,
                'prediction': 'Need more data',
                'current_pr': data['max_weight'],
                'suggestion': 'Log more workouts for this exercise'
            }
        
        # Calculate trend using recent weights
        recent = weights[-5:] if len(weights) >= 5 else weights
        if len(recent) > 1:
            # Simple linear regression
            x = np.arange(len(recent))
            y = np.array(recent)
            slope = np.polyfit(x, y, 1)[0]
            
            # Predict next weight
            next_weight = recent[-1] + slope * 2  # Predict 2 workouts ahead
            
            # Ensure prediction is reasonable
            if next_weight <= recent[-1]:
                next_weight = recent[-1] + 2.5  # Minimum 2.5kg increase
            
            # Calculate estimated time (workouts needed)
            improvement_needed = next_weight - data['max_weight']
            workouts_needed = max(1, int(improvement_needed / (slope if slope > 0 else 2.5)))
            
            return {
                'exercise': exercise,
                'current_pr': data['max_weight'],
                'predicted_next': round(next_weight, 1),
                'workouts_needed': workouts_needed,
                'confidence': min(abs(slope) * 10, 100),
                'trend': '📈 Increasing' if slope > 0.1 else '📉 Decreasing' if slope < -0.1 else '➡️ Stable'
            }
        
        return None
    
    def detect_plateaus(self):
        """Detect if you're plateauing on any exercises"""
        plateaus = []
        
        for exercise, data in self.exercise_history.items():
            weights = data['weights']
            if len(weights) >= 5:
                # Check if last 3-5 workouts are at similar weights
                recent = weights[-5:]
                if len(set(recent)) <= 2:  # Mostly same weight
                    recent_avg = sum(recent) / len(recent)
                    overall_avg = data['avg_weight']
                    
                    # If recent is not higher than overall average
                    if recent_avg <= overall_avg * 1.02:
                        plateaus.append({
                            'exercise': exercise,
                            'current_weight': recent[-1],
                            'plateau_since': len(weights) - len(recent),
                            'suggestion': 'Try changing rep range, increasing sets, or adding variation',
                            'muscle': data['muscle']
                        })
        
        return plateaus
    
    def get_volume_optimizer(self):
        """Suggest optimal volume for each muscle group"""
        if len(self.workout_data) < 5:
            return None
        
        muscle_volume = defaultdict(list)
        
        for row in self.workout_data:
            muscle = get_muscle_group(row[1])
            volume = row[5]
            muscle_volume[muscle].append(volume)
        
        suggestions = []
        for muscle, volumes in muscle_volume.items():
            if muscle == 'other':
                continue
            if len(volumes) >= 3:
                avg_volume = sum(volumes) / len(volumes)
                max_volume = max(volumes)
                min_volume = min(volumes)
                
                # Suggest optimal volume
                optimal = avg_volume * 1.2  # 20% more than average
                suggestions.append({
                    'muscle': muscle,
                    'current_avg': round(avg_volume, 0),
                    'suggested': round(optimal, 0),
                    'increase': round(optimal - avg_volume, 0),
                    'max_recorded': round(max_volume, 0),
                    'emoji': '💪' if optimal > avg_volume else '✅'
                })
        
        return suggestions
    
    def get_exercise_form_tips(self):
        """Generate form tips based on exercise patterns"""
        tips = []
        
        for exercise, data in self.exercise_history.items():
            if data['count'] >= 3:
                # Check if weight is increasing but reps are decreasing
                weights = data['weights'][-3:] if len(data['weights']) >= 3 else data['weights']
                reps = data['reps'][-3:] if len(data['reps']) >= 3 else data['reps']
                
                if len(weights) >= 3 and len(reps) >= 3:
                    weight_increasing = weights[-1] > weights[0]
                    reps_decreasing = reps[-1] < reps[0]
                    
                    if weight_increasing and reps_decreasing:
                        tips.append({
                            'exercise': exercise,
                            'issue': 'Weight increasing but reps decreasing',
                            'tip': 'Maintain form quality. Consider lowering weight slightly to ensure full range of motion.',
                            'muscle': data['muscle'],
                            'severity': 'medium'
                        })
                    
                    # Check if reps are too low (strength focus)
                    if data['best_reps'] < 6 and data['count'] > 5:
                        tips.append({
                            'exercise': exercise,
                            'issue': 'Very low reps consistently',
                            'tip': 'Try incorporating higher rep ranges (8-12) for muscle growth and joint health.',
                            'muscle': data['muscle'],
                            'severity': 'low'
                        })
        
        return tips[:5]  # Return top 5 tips
    
    def get_ai_coach_summary(self):
        """Get overall AI coach summary"""
        fatigue = self.get_fatigue_analysis()
        plateaus = self.detect_plateaus()
        muscle_suggestions = self.get_muscle_suggestions()
        volume_optimizer = self.get_volume_optimizer()
        
        summary = {
            'fatigue': fatigue,
            'plateaus': plateaus,
            'muscle_suggestions': muscle_suggestions[:3],
            'volume_optimizer': volume_optimizer[:3] if volume_optimizer else [],
            'overall_status': 'good'
        }
        
        # Determine overall status
        if fatigue['fatigue_level'] == 'high':
            summary['overall_status'] = 'warning'
        elif len(plateaus) > 2:
            summary['overall_status'] = 'needs_attention'
        elif fatigue['fatigue_level'] == 'low' and len(plateaus) == 0:
            summary['overall_status'] = 'excellent'
        
        return summary