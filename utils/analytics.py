# utils/analytics.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class PerformanceAnalytics:
    def __init__(self, workout_data):
        """
        Initialize with workout data
        workout_data: list of tuples (id, exercise, weight, reps, sets, volume, xp, rank, date)
        """
        self.workout_data = workout_data
        self.df = self._create_dataframe()
    
    def _create_dataframe(self):
        """Convert workout data to pandas DataFrame"""
        if not self.workout_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(
            self.workout_data,
            columns=['id', 'exercise', 'weight', 'reps', 'sets', 'volume', 'xp', 'rank', 'date']
        )
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_performance_trends(self):
        """Calculate performance trends for each exercise"""
        if self.df.empty:
            return {}
        
        trends = {}
        for exercise in self.df['exercise'].unique():
            exercise_df = self.df[self.df['exercise'] == exercise].sort_values('date')
            
            if len(exercise_df) >= 3:
                # Calculate trend using linear regression
                x = np.arange(len(exercise_df))
                y = exercise_df['weight'].values
                
                if len(x) > 1:
                    slope = np.polyfit(x, y, 1)[0]
                    trend = '📈 Increasing' if slope > 0.1 else '📉 Decreasing' if slope < -0.1 else '➡️ Stable'
                    
                    # Calculate improvement percentage
                    first_weight = exercise_df['weight'].iloc[0]
                    last_weight = exercise_df['weight'].iloc[-1]
                    improvement = ((last_weight - first_weight) / first_weight * 100) if first_weight > 0 else 0
                    
                    trends[exercise] = {
                        'trend': trend,
                        'improvement': improvement,
                        'current_weight': last_weight,
                        'best_weight': exercise_df['weight'].max(),
                        'total_workouts': len(exercise_df),
                        'slope': slope
                    }
        
        return trends
    
    def get_volume_trends(self):
        """Analyze training volume trends"""
        if self.df.empty:
            return {}
        
        # Group by week
        self.df['week'] = self.df['date'].dt.isocalendar().week
        self.df['year'] = self.df['date'].dt.year
        
        weekly_volume = self.df.groupby(['year', 'week'])['volume'].sum().reset_index()
        weekly_volume['week_label'] = weekly_volume.apply(
            lambda x: f"W{x['week']}", axis=1
        )
        
        if len(weekly_volume) >= 3:
            x = np.arange(len(weekly_volume))
            y = weekly_volume['volume'].values
            slope = np.polyfit(x, y, 1)[0]
            
            return {
                'trend': '📈 Increasing' if slope > 100 else '📉 Decreasing' if slope < -100 else '➡️ Stable',
                'current_volume': weekly_volume['volume'].iloc[-1] if not weekly_volume.empty else 0,
                'avg_volume': weekly_volume['volume'].mean() if not weekly_volume.empty else 0,
                'best_week': weekly_volume.loc[weekly_volume['volume'].idxmax()] if not weekly_volume.empty else None,
                'data': weekly_volume
            }
        
        return {}
    
    def get_exercise_frequency(self):
        """Analyze exercise frequency patterns"""
        if self.df.empty:
            return {}
        
        # Count exercises per day of week
        self.df['day_of_week'] = self.df['date'].dt.day_name()
        frequency = self.df.groupby(['exercise', 'day_of_week']).size().reset_index(name='count')
        
        # Find most common days for each exercise
        exercise_days = {}
        for exercise in self.df['exercise'].unique():
            ex_df = frequency[frequency['exercise'] == exercise]
            if not ex_df.empty:
                most_common = ex_df.loc[ex_df['count'].idxmax()]
                exercise_days[exercise] = {
                    'most_common_day': most_common['day_of_week'],
                    'frequency': most_common['count'],
                    'total': len(self.df[self.df['exercise'] == exercise])
                }
        
        return exercise_days
    
    def get_estimated_1rm(self, exercise):
        """Calculate estimated 1RM for an exercise"""
        if self.df.empty:
            return None
        
        exercise_df = self.df[self.df['exercise'] == exercise]
        if exercise_df.empty:
            return None
        
        # Use Epley formula: 1RM = weight * (1 + reps/30)
        exercise_df['estimated_1rm'] = exercise_df['weight'] * (1 + exercise_df['reps'] / 30)
        
        best = exercise_df.loc[exercise_df['estimated_1rm'].idxmax()]
        
        return {
            'exercise': exercise,
            'estimated_1rm': best['estimated_1rm'],
            'actual_weight': best['weight'],
            'reps': best['reps'],
            'date': best['date'],
            'progress': exercise_df['estimated_1rm'].tolist(),
            'dates': exercise_df['date'].tolist()
        }
    
    def get_workout_quality_score(self):
        """Calculate workout quality score based on various metrics"""
        if self.df.empty:
            return 0
        
        # Factors: volume, progression, consistency, variety
        score = 0
        
        # 1. Volume consistency (max 30 points)
        weekly_volume = self.df.groupby(self.df['date'].dt.isocalendar().week)['volume'].sum()
        if len(weekly_volume) > 1:
            consistency = 1 - (weekly_volume.std() / weekly_volume.mean() if weekly_volume.mean() > 0 else 0)
            score += min(consistency * 30, 30)
        
        # 2. Progression (max 25 points)
        trends = self.get_performance_trends()
        if trends:
            improving = sum(1 for t in trends.values() if 'Increasing' in t['trend'])
            total = len(trends)
            if total > 0:
                progression_score = (improving / total) * 25
                score += progression_score
        
        # 3. Exercise variety (max 20 points)
        unique_exercises = len(self.df['exercise'].unique())
        variety_score = min((unique_exercises / 10) * 20, 20)
        score += variety_score
        
        # 4. Frequency (max 25 points)
        workouts_per_week = len(self.df) / max(1, (self.df['date'].max() - self.df['date'].min()).days / 7)
        frequency_score = min((workouts_per_week / 5) * 25, 25)
        score += frequency_score
        
        return min(int(score), 100)
    
    def get_predictions(self):
        """Generate simple predictions for future performance"""
        if self.df.empty or len(self.df) < 3:
            return {}
        
        predictions = {}
        
        # Predict next best lift for each exercise
        for exercise in self.df['exercise'].unique():
            exercise_df = self.df[self.df['exercise'] == exercise].sort_values('date')
            
            if len(exercise_df) >= 3:
                x = np.arange(len(exercise_df))
                y = exercise_df['weight'].values
                
                # Simple linear regression
                slope, intercept = np.polyfit(x, y, 1)
                
                # Predict next workout weight
                next_x = len(exercise_df)
                predicted_weight = slope * next_x + intercept
                
                # Ensure prediction is reasonable (at least current weight)
                current_weight = exercise_df['weight'].iloc[-1]
                if predicted_weight < current_weight:
                    predicted_weight = current_weight + 0.5  # Small increase
                
                predictions[exercise] = {
                    'predicted_weight': round(predicted_weight, 1),
                    'current_weight': round(current_weight, 1),
                    'improvement': round(predicted_weight - current_weight, 1),
                    'confidence': min(abs(slope) * 10, 100)  # Higher slope = higher confidence
                }
        
        return predictions
    
    def get_weekly_summary(self):
        """Generate weekly training summary"""
        if self.df.empty:
            return None
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        week_df = self.df[self.df['date'].dt.date >= week_ago]
        
        if week_df.empty:
            return None
        
        summary = {
            'total_workouts': len(week_df),
            'total_volume': week_df['volume'].sum(),
            'total_xp': week_df['xp'].sum(),
            'unique_exercises': len(week_df['exercise'].unique()),
            'best_lift': week_df.loc[week_df['weight'].idxmax()] if not week_df.empty else None,
            'avg_weight': week_df['weight'].mean() if not week_df.empty else 0,
            'exercises': week_df['exercise'].tolist()
        }
        
        return summary