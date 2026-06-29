# components/muscle_heatmap.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.muscle_mapper import get_muscle_group, MUSCLE_GROUPS

def create_muscle_heatmap(workout_data):
    """Create an interactive muscle heat map from workout data"""
    if not workout_data or len(workout_data) == 0:
        return None
    
    # Initialize muscle counts
    muscle_counts = {muscle: 0 for muscle in MUSCLE_GROUPS.keys()}
    muscle_counts['other'] = 0
    
    # Count exercises by muscle group
    for row in workout_data:
        exercise = row[1]  # exercise name is at index 1
        muscle = get_muscle_group(exercise)
        muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
    
    # Calculate total for percentages
    total = sum(muscle_counts.values())
    if total == 0:
        return None
    
    # Prepare data for visualization
    muscles = list(muscle_counts.keys())
    counts = list(muscle_counts.values())
    percentages = [(count/total)*100 for count in counts]
    
    # Create custom color scale based on percentage
    max_percent = max(percentages) if percentages else 1
    
    # Define muscle group emojis
    muscle_emojis = {
        'chest': '💪',
        'back': '🔙',
        'shoulders': '🏋️',
        'biceps': '💪',
        'triceps': '💪',
        'legs': '🦵',
        'glutes': '🍑',
        'core': '🎯',
        'forearms': '🤲',
        'cardio': '❤️',
        'other': '📌'
    }
    
    # Create labels with emojis
    labels = [f"{muscle_emojis.get(m, '📌')} {m.capitalize()}" for m in muscles]
    
    # Create figure
    fig = go.Figure()
    
    # Add bars with gradient colors
    fig.add_trace(go.Bar(
        x=labels,
        y=percentages,
        text=[f'{pct:.1f}%' for pct in percentages],
        textposition='outside',
        textfont=dict(color='white', size=12),
        marker=dict(
            color=percentages,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Training Focus %",
                x=1.02,
                len=0.8,
                tickfont=dict(color='white')
            ),
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      'Workouts: %{customdata[0]}<br>' +
                      'Percentage: %{y:.1f}%<extra></extra>',
        customdata=list(zip(counts))
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '💪 Muscle Group Distribution',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': 'white', 'family': 'Arial Black'}
        },
        xaxis_title='Muscle Group',
        yaxis_title='Percentage of Workouts (%)',
        yaxis_range=[0, max(percentages) * 1.2 if percentages else 100],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        showlegend=False,
        height=500,
        margin=dict(t=80, b=80, l=60, r=100),
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font_size=14,
            font_family='Arial'
        )
    )
    
    # Update axes
    # Update axes
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            gridcolor='rgba(255,255,255,0.1)',
            showline=True,
            linecolor='rgba(255,255,255,0.2)',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            showline=True,
            linecolor='rgba(255,255,255,0.2)',
            tickfont=dict(size=11)
        )
    )
    
    return fig

def display_muscle_heatmap(workout_data):
    """Display the muscle heat map in Streamlit"""
    fig = create_muscle_heatmap(workout_data)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Add summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            unique_exercises = len(set(row[1] for row in workout_data))
            st.metric("🏋️ Total Exercises", unique_exercises)
        with col2:
            unique_muscles = len(set(get_muscle_group(row[1]) for row in workout_data))
            st.metric("🎯 Muscle Groups", unique_muscles)
        with col3:
            if workout_data:
                most_trained = max(set(row[1] for row in workout_data), key=lambda x: sum(1 for row in workout_data if row[1] == x))
                st.metric("⭐ Most Trained", most_trained[:20] + "..." if len(most_trained) > 20 else most_trained)
    else:
        st.info("No workout data available to display muscle heat map. Start logging your workouts!")