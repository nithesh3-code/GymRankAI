# pages/07_AI_Coach.py

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
from utils.workout_recommender import WorkoutRecommender
from utils.muscle_mapper import get_muscle_group, MUSCLE_GROUPS

st.set_page_config(
    page_title="AI Coach - GymRank AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Coach")
st.markdown("Get personalized workout recommendations based on your training history")

# Connect to database
conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

# Load workout data
cursor.execute("SELECT * FROM workouts ORDER BY workout_date DESC")
data = cursor.fetchall()

if data:
    # Create recommender instance
    recommender = WorkoutRecommender(data)
    
    # Stats summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_exercises = len(set(row[1] for row in data))
        st.metric("Total Exercises", total_exercises)
    with col2:
        total_workouts = len(data)
        st.metric("Total Workouts", total_workouts)
    with col3:
        today = datetime.today().date()
        recent = sum(1 for row in data if (today - datetime.strptime(row[8], "%Y-%m-%d").date()).days <= 7)
        st.metric("Workouts (7 Days)", recent)
    with col4:
        unique_muscles = len(set(get_muscle_group(row[1]) for row in data))
        st.metric("Muscles Trained", unique_muscles)
    
    st.markdown("---")
    
    # Three main recommendation sections
    tab1, tab2, tab3 = st.tabs(["💡 Exercise Suggestions", "📈 Progressive Overload", "📊 Volume Analysis"])
    
    with tab1:
        st.subheader("💡 Smart Exercise Suggestions")
        st.markdown("Based on your training patterns, here are exercises you should consider:")
        
        exercise_suggestions = recommender.suggest_exercises(num_suggestions=5)
        
        if exercise_suggestions:
            for suggestion in exercise_suggestions:
                priority_color = "🔴" if suggestion['priority'] > 0.8 else "🟡" if suggestion['priority'] > 0.5 else "🟢"
                st.markdown(f"""
                <div style="background:#1E1E1E; padding:20px; border-radius:10px; border-left: 4px solid #2563eb; margin:10px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h3 style="margin:0; color:#60A5FA;">{suggestion['exercise']}</h3>
                            <p style="margin:5px 0 0 0; color:#9CA3AF;">{suggestion['reason']}</p>
                        </div>
                        <div style="font-size:1.5rem;">{priority_color}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ You're doing great! No exercise suggestions at this time.")
        
        # Show muscle balance
        st.subheader("⚖️ Muscle Balance")
        weak_muscles = recommender.get_weak_muscles()
        if weak_muscles['counts']:
            cols = st.columns(3)
            for idx, (muscle, count) in enumerate(sorted(weak_muscles['counts'].items(), key=lambda x: x[1])):
                with cols[idx % 3]:
                    if muscle != 'other' and muscle in MUSCLE_GROUPS:
                        total = sum(weak_muscles['counts'].values())
                        percentage = (count / total) * 100
                        bar_color = "🟢" if percentage > 10 else "🟡" if percentage > 5 else "🔴"
                        st.markdown(f"""
                        <div style="background:#1E1E1E; padding:15px; border-radius:10px; margin:5px 0;">
                            <strong style="color:#9CA3AF;">{muscle.capitalize()}</strong>
                            <div style="display:flex; justify-content:space-between;">
                                <span>{bar_color} {count} exercises</span>
                                <span style="color:#9CA3AF;">{percentage:.1f}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📈 Progressive Overload Opportunities")
        st.markdown("Increase weight gradually to build strength:")
        
        overload_suggestions = recommender.get_progressive_overload_suggestion()
        
        if overload_suggestions:
            for suggestion in overload_suggestions:
                st.markdown(f"""
                <div style="background:#1E1E1E; padding:20px; border-radius:10px; border-left: 4px solid #10B981; margin:10px 0;">
                    <h3 style="margin:0; color:#34D399;">{suggestion['exercise']}</h3>
                    <div style="display:flex; gap:20px; margin-top:10px;">
                        <div>
                            <span style="color:#9CA3AF;">Current: </span>
                            <strong>{suggestion['current_weight']:.1f}kg</strong>
                        </div>
                        <div>
                            <span style="color:#9CA3AF;">Suggested: </span>
                            <strong style="color:#FBBF24;">{suggestion['suggested_weight']:.1f}kg</strong>
                        </div>
                        <div>
                            <span style="color:#9CA3AF;">Increase: </span>
                            <strong style="color:#34D399;">+{suggestion['suggested_weight'] - suggestion['current_weight']:.1f}kg</strong>
                        </div>
                    </div>
                    <p style="margin:10px 0 0 0; color:#9CA3AF;">{suggestion['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Keep training consistently and we'll suggest overload opportunities!")
        
        # Additional tips
        st.subheader("💪 Progressive Overload Tips")
        tips = [
            "📊 Add 2.5-5kg to compound exercises when you can complete all reps",
            "📈 Increase reps before increasing weight for isolation exercises",
            "📅 Track your weights to ensure steady progression",
            "🎯 Focus on form before adding weight"
        ]
        for tip in tips:
            st.markdown(f"✅ {tip}")
    
    with tab3:
        st.subheader("📊 Training Volume Analysis")
        
        volume_suggestion = recommender.get_volume_suggestion()
        if volume_suggestion:
            st.info(volume_suggestion['message'])
        
        # Show weekly volume chart
        import plotly.express as px
        import pandas as pd
        
        today = datetime.today().date()
        weekly_data = []
        
        for i in range(8):  # Last 8 weeks
            week_start = today - timedelta(days=(i+1)*7)
            week_end = today - timedelta(days=i*7)
            week_volume = 0
            week_count = 0
            
            for row in data:
                workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                if week_start <= workout_date < week_end:
                    week_volume += row[5]
                    week_count += 1
            
            if week_count > 0:
                weekly_data.append({
                    'Week': f"Week {8-i}",
                    'Average Volume': week_volume / week_count,
                    'Workouts': week_count
                })
        
        if weekly_data:
            df = pd.DataFrame(weekly_data)
            
            fig = px.line(
                df,
                x='Week',
                y='Average Volume',
                title='Average Weekly Training Volume',
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show workout frequency
            st.subheader("📅 Workout Frequency")
            freq_fig = px.bar(
                df,
                x='Week',
                y='Workouts',
                title='Workouts per Week',
                color='Workouts',
                color_continuous_scale='Viridis'
            )
            freq_fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=300
            )
            st.plotly_chart(freq_fig, use_container_width=True)

else:
    st.info("No workout data available. Start logging your workouts to get AI coaching!")

conn.close()