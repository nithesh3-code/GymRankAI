# pages/06_Muscle_Analysis.py

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from components.muscle_heatmap import create_muscle_heatmap, display_muscle_heatmap
from utils.muscle_mapper import get_muscle_group, MUSCLE_GROUPS

st.set_page_config(
    page_title="Muscle Analysis - GymRank AI",
    page_icon="💪",
    layout="wide"
)

st.title("💪 Muscle Group Analysis")
st.markdown("Analyze your training distribution across different muscle groups")

# Connect to database
conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

# Load workout data
cursor.execute("SELECT * FROM workouts ORDER BY workout_date DESC")
data = cursor.fetchall()

if data:
    # Time filter
    col1, col2 = st.columns([2, 1])
    with col1:
        time_filter = st.selectbox(
            "📅 Select Time Period",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            index=0
        )
        
        # Apply filter
        filtered_data = data
        if time_filter != "All Time":
            days = int(time_filter.split()[1])
            cutoff = datetime.today().date() - timedelta(days=days)
            filtered_data = []
            for row in data:
                workout_date = datetime.strptime(row[8], "%Y-%m-%d").date()
                if workout_date >= cutoff:
                    filtered_data.append(row)
    
    # Display heatmap
    display_muscle_heatmap(filtered_data)
    
    # Detailed breakdown
    st.markdown("---")
    st.subheader("📊 Detailed Muscle Group Breakdown")
    
    # Create detailed breakdown
    muscle_counts = {}
    for row in filtered_data:
        exercise = row[1]
        muscle = get_muscle_group(exercise)
        muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
    
    # Create dataframe for display
    if muscle_counts:
        detail_df = pd.DataFrame({
            'Muscle Group': [m.capitalize() for m in muscle_counts.keys()],
            'Total Exercises': list(muscle_counts.values())
        }).sort_values('Total Exercises', ascending=False)
        
        # Add percentage and emojis
        total = detail_df['Total Exercises'].sum()
        detail_df['Percentage'] = (detail_df['Total Exercises'] / total * 100).round(1)
        
        # Add muscle emojis
        emoji_map = {
            'Chest': '💪',
            'Back': '🔙',
            'Shoulders': '🏋️',
            'Biceps': '💪',
            'Triceps': '💪',
            'Legs': '🦵',
            'Glutes': '🍑',
            'Core': '🎯',
            'Forearms': '🤲',
            'Cardio': '❤️',
            'Other': '📌'
        }
        detail_df['Muscle'] = detail_df['Muscle Group'].map(lambda x: f"{emoji_map.get(x, '📌')} {x}")
        
        st.dataframe(
            detail_df[['Muscle', 'Total Exercises', 'Percentage']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Muscle": st.column_config.TextColumn("Muscle Group"),
                "Total Exercises": st.column_config.NumberColumn("Exercises"),
                "Percentage": st.column_config.NumberColumn("Distribution", format="%.1f%%")
            }
        )
        
        # Recommendations based on muscle distribution
        st.markdown("---")
        st.subheader("💡 Training Insights")
        
        # Find least trained muscles
        if len(detail_df) > 1:
            avg_percentage = detail_df['Percentage'].mean()
            least_trained = detail_df[detail_df['Percentage'] < avg_percentage * 0.5]
            
            if not least_trained.empty:
                st.warning(f"⚡ **Consider adding more exercises for:** {', '.join(least_trained['Muscle Group'].values)}")
                st.info("💡 Tip: Balanced training helps prevent muscle imbalances and reduces injury risk.")
            else:
                st.success("✅ **Great balance across all muscle groups!** Keep up the excellent work!")
            
            # Most trained muscle
            most_trained = detail_df.iloc[0]
            st.info(f"🏆 **Your most trained muscle group is {most_trained['Muscle Group']}** with {most_trained['Total Exercises']} exercises ({most_trained['Percentage']:.1f}% of total)")
        
        # Training volume by muscle
        st.markdown("---")
        st.subheader("📈 Training Volume by Muscle Group")
        
        # Calculate volume by muscle group
        muscle_volume = {}
        for row in filtered_data:
            exercise = row[1]
            muscle = get_muscle_group(exercise)
            volume = row[5]  # volume is at index 5
            muscle_volume[muscle] = muscle_volume.get(muscle, 0) + volume
        
        if muscle_volume:
            volume_df = pd.DataFrame({
                'Muscle Group': [m.capitalize() for m in muscle_volume.keys()],
                'Total Volume (kg)': list(muscle_volume.values())
            }).sort_values('Total Volume (kg)', ascending=False)
            
            # Create bar chart for volume
            import plotly.express as px
            fig = px.bar(
                volume_df,
                x='Muscle Group',
                y='Total Volume (kg)',
                title='Total Volume by Muscle Group',
                color='Total Volume (kg)',
                color_continuous_scale='Viridis',
                text_auto=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=400,
                xaxis_tickangle=45
            )
            st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("No workout data available. Start logging your workouts to see muscle analysis!")

conn.close()