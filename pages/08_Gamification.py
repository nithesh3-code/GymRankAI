# pages/08_Gamification.py

import streamlit as st
import sqlite3
from utils.gamification import GamificationSystem

st.set_page_config(
    page_title="Gamification - GymRank AI",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Gamification Hub")
st.markdown("Track your progress, complete challenges, and unlock achievements!")

# Connect to database
conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

# Load data
cursor.execute("SELECT * FROM workouts")
data = cursor.fetchall()

if data:
    # Calculate stats
    total_xp = sum(row[6] for row in data)
    strength_score = 0
    if data:
        total_weight = sum(row[2] for row in data)
        strength_score = min(int((total_weight / len(data)) * 10), 1000)
    
    # Initialize gamification
    gamification = GamificationSystem(data, total_xp, strength_score)
    
    # Tier Section
    st.subheader("👑 Your Tier Progress")
    tier_info = gamification.get_tier_info()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:20px;">
            <div style="font-size:4rem;">{tier_info['current']['emoji']}</div>
            <h2 style="color:{tier_info['current']['color']};">{tier_info['current']['name']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if tier_info['next']:
            st.progress(tier_info['progress'], text=f"Progress to {tier_info['next']['name']}")
            st.caption(f"📊 {tier_info['xp_in_tier']:.0f} / {tier_info['xp_to_next'] + tier_info['xp_in_tier']:.0f} XP in current tier")
            st.caption(f"🎯 {tier_info['xp_to_next']:.0f} XP needed for {tier_info['next']['name']}")
        else:
            st.success("🏆 You've reached the highest tier! You're a Legend!")
    
    with col3:
        st.metric("Total XP", f"{total_xp:,}")
        st.metric("Strength Score", strength_score)
    
    st.markdown("---")
    
    # Challenges Section
    st.subheader("🎯 Active Challenges")
    challenges = gamification.get_challenges()
    
    if challenges:
        # Create a grid of challenges
        for i in range(0, len(challenges), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(challenges):
                    challenge = challenges[i + j]
                    with cols[j]:
                        status = "✅ Completed!" if challenge['completed'] else f"{challenge['progress']*100:.0f}%"
                        status_color = "#10B981" if challenge['completed'] else "#3B82F6"
                        
                        st.markdown(f"""
                        <div style="background:#1E1E1E; padding:20px; border-radius:10px; margin:10px 0; 
                                    border: 2px solid {'#10B981' if challenge['completed'] else '#374151'};">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h4 style="margin:0; color:{'#10B981' if challenge['completed'] else '#F59E0B'};">{challenge['name']}</h4>
                                <span style="background:{status_color}22; padding:5px 10px; border-radius:20px; 
                                      color:{status_color}; font-size:0.8rem;">{status}</span>
                            </div>
                            <p style="color:#9CA3AF; margin-top:10px;">{challenge['description']}</p>
                            <div style="margin:10px 0;">
                                <div style="background:#374151; height:8px; border-radius:4px; overflow:hidden;">
                                    <div style="background:{status_color}; width:{challenge['progress']*100}%; 
                                         height:100%; transition: width 0.3s;"></div>
                                </div>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#9CA3AF;">
                                <span>🎁 Reward: {challenge['reward']}</span>
                                <span>{'✅' if challenge['completed'] else '🔄 In Progress'}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No active challenges. Keep training to unlock challenges!")
    
    st.markdown("---")
    
    # Achievements Section
    st.subheader("🏅 Achievement Gallery")
    achievement_stats = gamification.get_achievement_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Achievements", achievement_stats["total_achievements"])
    with col2:
        st.metric("Unlocked", len(achievement_stats["unlocked"]))
    with col3:
        st.metric("Progress", f"{achievement_stats['progress_percentage']:.0f}%")
    
    # Progress bar for achievements
    st.progress(achievement_stats["progress_percentage"] / 100)
    
    # Display achievements in grid
    st.markdown("### 🎖️ Unlocked Achievements")
    if achievement_stats["unlocked"]:
        cols = st.columns(4)
        for idx, achievement in enumerate(achievement_stats["unlocked"]):
            with cols[idx % 4]:
                st.markdown(f"""
                <div style="background:#1E1E1E; padding:15px; border-radius:10px; text-align:center; 
                            margin:5px 0; border: 1px solid #10B981;">
                    <div style="font-size:3rem;">{achievement['emoji']}</div>
                    <div style="color:white; font-weight:bold; margin-top:5px;">{achievement['name']}</div>
                    <div style="color:#10B981; font-size:0.8rem;">✅ Unlocked</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No achievements unlocked yet. Start your fitness journey!")
    
    # Locked achievements
    if achievement_stats["locked"]:
        with st.expander("🔒 Locked Achievements"):
            cols = st.columns(4)
            for idx, achievement in enumerate(achievement_stats["locked"][:8]):  # Show first 8
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background:#1E1E1E; padding:15px; border-radius:10px; text-align:center; 
                                margin:5px 0; opacity:0.5; border: 1px solid #374151;">
                        <div style="font-size:3rem;">{achievement['emoji']}</div>
                        <div style="color:#6B7280; margin-top:5px;">{achievement['name']}</div>
                        <div style="color:#4B5563; font-size:0.8rem;">🔒 Locked</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Share Progress Section
    st.subheader("📱 Share Your Progress")
    social_stats = gamification.get_social_stats()
    
    # Preview share card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E1E1E, #2D2D2D); 
                padding: 30px; border-radius: 15px; border: 1px solid #374151; margin: 20px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:3rem;">{social_stats['tier_emoji']}</div>
                <h2 style="color:white; margin:0;">{social_stats['tier']} Tier</h2>
            </div>
            <div style="text-align:right;">
                <div style="color:#9CA3AF;">💪 {social_stats['total_workouts']} workouts</div>
                <div style="color:#9CA3AF;">📦 {social_stats['total_volume']} volume</div>
                <div style="color:#F59E0B;">⭐ {social_stats['best_lift']} best lift</div>
            </div>
        </div>
        <div style="margin-top:15px; padding-top:15px; border-top: 1px solid #374151;">
            <div style="color:#9CA3AF; font-size:0.9rem;">🎯 XP: {social_stats['total_xp']} • Strength Score: {social_stats['strength_score']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📤 Generate Share Text", use_container_width=True):
        st.code(social_stats['share_text'], language='text')
        st.success("✅ Copy this text and share with your friends!")

else:
    st.info("No workout data available. Start logging your workouts to unlock gamification features!")

conn.close()