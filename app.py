import streamlit as st
import sqlite3
from database import create_database
from datetime import date
from datetime import datetime ,timedelta
import pandas as pd
import plotly.express as px
if "last_completed_date" not in st.session_state:
    st.session_state.last_completed_date = None

if "workout_completed" not in st.session_state:
    st.session_state.workout_completed = False

st.set_page_config(
    page_title="AI Workout Tracker",
    page_icon="💪",
    layout="wide"
)

st.markdown("""
<style>
    /* ============================================
       MOBILE-FIRST DESIGN
       ============================================ */
    
    /* Main background */
    .main {
        background-color: #0A0A0F;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ============================================
       MOBILE RESPONSIVE STYLES
       ============================================ */
    
    /* Default: Mobile First */
    .stApp {
        max-width: 100%;
        padding: 0;
    }
    
    /* Premium gradient cards */
    .premium-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        margin: 8px 0;
    }
    
    .premium-card:hover {
        transform: translateY(-3px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
    }
    
    /* Today's workout card */
    .today-workout {
        background: linear-gradient(135deg, #1a1a2e, #0f3460);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        position: relative;
        overflow: hidden;
        margin: 8px 0;
    }
    
    .today-workout::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1), transparent);
        pointer-events: none;
    }
    
    /* Stat cards */
    .stat-premium {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        margin: 4px 0;
    }
    
    .stat-premium:hover {
        border-color: rgba(59, 130, 246, 0.3);
        transform: scale(1.02);
    }
    
    /* Activity cards */
    .activity-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
        margin: 4px 0;
    }
    
    .activity-card:hover {
        border-color: rgba(59, 130, 246, 0.2);
        background: linear-gradient(135deg, #1e1e3a, #16213e);
    }
    
    .activity-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: linear-gradient(135deg, #2563eb33, #7c3aed33);
        flex-shrink: 0;
    }
    
    /* Progress bars */
    .progress-premium {
        height: 8px;
        border-radius: 4px;
        background: #2d2d44;
        overflow: hidden;
        margin: 8px 0;
    }
    
    .progress-premium .fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        transition: width 1s ease;
    }
    
    /* Quick stat cards - Mobile optimized */
    .quick-stat {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 10px;
        padding: 10px 8px;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        text-align: center;
        margin: 2px 0;
    }
    
    .quick-stat:hover {
        border-color: rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    
    .quick-stat .value {
        font-size: 1.3rem;
        font-weight: bold;
        margin: 0;
    }
    
    .quick-stat .label {
        font-size: 0.6rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-top: 2px;
    }
    
    /* Greeting text */
    .greeting {
        font-size: 1.3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Bottom navigation - Mobile style */
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 6px 8px;
        border-radius: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        color: #6B7280;
        text-decoration: none;
        font-size: 0.7rem;
    }
    
    .nav-item:hover, .nav-item.active {
        color: white;
        background: rgba(59, 130, 246, 0.1);
    }
    
    .nav-item .icon {
        font-size: 1.3rem;
    }
    
    .nav-item .label {
        font-size: 0.6rem;
        margin-top: 2px;
    }
    
    /* Sidebar - Mobile optimized */
    .css-1d391kg {
        padding-top: 0;
    }
    
    .css-1d391kg .css-1v3fvcr {
        padding: 8px;
    }
    
    /* Buttons - Mobile friendly */
    .stButton > button {
        width: 100%;
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* Input fields - Mobile friendly */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 16px; /* Prevents zoom on iOS */
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }
    
    /* Metrics - Mobile optimized */
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        margin: 4px 0;
    }
    
    .stMetric > div {
        padding: 0;
    }
    
    .stMetric .css-1xarl3l {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Tabs - Mobile friendly */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        flex-wrap: wrap;
        padding: 4px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.75rem;
        white-space: nowrap;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border-color: transparent;
    }
    
    /* Expanders - Mobile friendly */
    .streamlit-expanderHeader {
        padding: 12px 16px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        padding: 12px 16px;
    }
    
    /* ============================================
       TABLET & DESKTOP OPTIMIZATIONS
       ============================================ */
    
    @media (min-width: 768px) {
        /* Tablet */
        .stApp {
            max-width: 100%;
            padding: 0 20px;
        }
        
        .quick-stat .value {
            font-size: 1.6rem;
        }
        
        .quick-stat .label {
            font-size: 0.7rem;
        }
        
        .premium-card {
            padding: 20px;
            border-radius: 20px;
        }
        
        .today-workout {
            padding: 25px;
            border-radius: 20px;
        }
        
        .activity-card {
            padding: 15px;
            gap: 15px;
        }
        
        .activity-icon {
            width: 50px;
            height: 50px;
            font-size: 24px;
        }
        
        .greeting {
            font-size: 1.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        /* Desktop */
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 40px;
        }
        
        .quick-stat .value {
            font-size: 1.8rem;
        }
        
        .quick-stat {
            padding: 15px 20px;
        }
        
        .premium-card {
            padding: 25px;
            border-radius: 24px;
        }
        
        .today-workout {
            padding: 30px;
            border-radius: 24px;
        }
    }
    
    /* ============================================
       MOBILE BOTTOM NAVIGATION BAR
       ============================================ */
    
    @media (max-width: 768px) {
        /* Hide default sidebar on mobile */
        .css-1d391kg {
            display: none !important;
        }
        
        /* Main content full width */
        .main > div {
            padding: 0 8px;
        }
        
        /* Mobile bottom nav - will be added via code */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(10, 10, 15, 0.95);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-around;
            padding: 8px 4px 12px;
            z-index: 1000;
            border-radius: 20px 20px 0 0;
        }
        
        .mobile-nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #6B7280;
            text-decoration: none;
            font-size: 0.6rem;
            padding: 4px 8px;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            min-width: 44px;
        }
        
        .mobile-nav-item.active {
            color: #60A5FA;
            background: rgba(59, 130, 246, 0.1);
        }
        
        .mobile-nav-item .icon {
            font-size: 1.3rem;
        }
        
        .mobile-nav-item .label {
            margin-top: 2px;
        }
        
        /* Add padding to main content for bottom nav */
        .main .block-container {
            padding-bottom: 80px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Functions
# -----------------------------

def get_todays_workout():

    day = datetime.today().strftime("%A")

    workout_plan = {

        "Monday": {
            "title": "Back & Biceps",
            "exercises": [
                "Pull Ups",
                "Lat Pulldown",
                "T-Bar Row",
                "Machine Row (Wide Grip)",
                "Seated Dumbbell Curl",
                "Preacher Curl",
                "Cable Curl",
                "Hammer Curl"
            ]
        },

        "Tuesday": {
            "title": "Chest, Triceps & Forearms",
            "exercises": [
                "Incline Bench Press",
                "Smith Machine Bench Press",
                "Decline Press",
                "Machine Fly",
                "Rod Pushdown",
                "Rope Overhead (Pasha Bhai Technique)",
                "Wrist Curl",
                "Reverse Wrist Curl",
                "Farmer Carry"
            ]
        },

        "Wednesday": {
            "title": "Shoulders & Legs",
            "exercises": [
                "Lateral Raise",
                "Front Raise",
                "Face Pull",
                "Barbell Squat",
                "Romanian Deadlift",
                "Adductor Machine",
                "Lying Leg Curl",
                "Leg Extension",
                "Calf Raise"
            ]
        },

        "Thursday": {
            "title": "Back & Biceps",
            "exercises": [
                "Pull Ups",
                "Lat Pulldown",
                "T-Bar Row",
                "Machine Row (Wide Grip)",
                "Barbell Curl",
                "Concentration Curl",
                "Cable Curl",
                "Hammer Curl"
            ]
        },

        "Friday": {
            "title": "Chest, Triceps & Forearms",
            "exercises": [
                "Incline Dumbbell Press",
                "Smith Machine Bench Press",
                "Decline Press",
                "Machine Fly",
                "Rod Pushdown",
                "Rope Overhead (Pasha Bhai Technique)",
                "Wrist Curl",
                "Reverse Wrist Curl",
                "Farmer Carry"
            ]
        },

        "Saturday": {
            "title": "Shoulders & Legs",
            "exercises": [
                "Behind The Neck Barbell Press",
                "Lateral Raise",
                "Face Pull",
                "Dumbbell Squat",
                "Romanian Deadlift",
                "Adductor Machine",
                "Lying Leg Curl",
                "Leg Extension",
                "Calf Raise"
            ]
        },

        "Sunday": {
            "title": "Rest Day",
            "exercises": []
        }
    }

    return workout_plan.get(day)

def get_rank(weight):
    if weight < 20:
        return "Beginner 🟢"
    elif weight < 40:
        return "Bronze 🟤"
    elif weight < 60:
        return "Silver ⚪"
    elif weight < 80:
        return "Gold 🟡"
    elif weight < 100:
        return "Platinum 🔷"
    else:
        return "Diamond 💎"


def calculate_xp(weight, reps, sets):
    return int(weight * reps * sets / 10)

def calculate_strength_score(data):

    if len(data) == 0:
        return 0

    total_weight = 0

    for row in data:
        total_weight += row[2]

    avg_weight = total_weight / len(data)

    score = min(int(avg_weight * 10), 1000)

    return score

def get_personal_records(data):

    prs = {}

    for row in data:

        exercise = row[1]
        weight = row[2]

        if exercise not in prs:
            prs[exercise] = weight

        elif weight > prs[exercise]:
            prs[exercise] = weight

    return prs

def get_leaderboard(prs):

    leaderboard = sorted(
        prs.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return leaderboard

def get_athlete_rank(score):

    if score < 100:
        return "Beginner 🟢"

    elif score < 250:
        return "Novice 🔵"

    elif score < 400:
        return "Intermediate 🟣"

    elif score < 600:
        return "Advanced 🔥"

    elif score < 800:
        return "Elite ⚡"

    else:
        return "GOAT 👑"
    
def calculate_streak(data):

    if len(data) == 0:
        return 0

    dates = []

    for row in data:

        workout_date = row[0]

        dates.append(
            datetime.strptime(
                workout_date,
                "%Y-%m-%d"
            ).date()
        )

    dates = sorted(list(set(dates)))

    streak = 1

    for i in range(
        len(dates)-1,
        0,
        -1
    ):

        diff = (
            dates[i]
            - dates[i-1]
        ).days

        if diff == 1:
            streak += 1
        else:
            break

    return streak

def get_badges(
    total_xp,
    streak,
    strength_score
):

    badges = []

    if total_xp >= 100:
        badges.append("🥉 100 XP Club")

    if total_xp >= 1000:
        badges.append("🥈 1K XP Club")

    if total_xp >= 5000:
        badges.append("🥇 5K XP Club")

    if total_xp >= 10000:
        badges.append("👑 10K XP Master")

    if streak >= 3:
        badges.append("🔥 3 Day Streak")

    if streak >= 7:
        badges.append("🔥 7 Day Streak")

    if streak >= 30:
        badges.append("🔥 30 Day Warrior")

    if strength_score >= 500:
        badges.append("💪 Strong Athlete")

    if strength_score >= 800:
        badges.append("⚡ Elite Athlete")

    if total_xp >= 50000:
        badges.append("🐐 GOAT Status")

    return badges

def get_weekly_stats(data):

    today = datetime.today().date()

    week_ago = today - timedelta(days=7)

    workouts = 0
    volume = 0
    xp = 0

    for row in data:

        workout_date = datetime.strptime(
            row[8],
            "%Y-%m-%d"
        ).date()

        if workout_date >= week_ago:

            workouts += 1
            volume += row[5]
            xp += row[6]

    return workouts, volume, xp


# -----------------------------
# Database
# -----------------------------

create_database()

# -----------------------------
# Database Connection
# -----------------------------

conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

cursor.execute("""SELECT * FROM workouts""")
data = cursor.fetchall()

cursor.execute("""
SELECT workout_date,xp
FROM completed_workouts
""")

completed_data = cursor.fetchall()
data.sort(key=lambda x: x[3], reverse=True)
total_workouts = len(data)
completed_workouts = 0

if total_workouts > 0:
    completed_workouts = total_workouts

completion_rate = 0

if total_workouts > 0:
    completion_rate = round((completed_workouts / total_workouts) * 100)

# -----------------------------
# Calculate Stats
# -----------------------------

total_volume = sum(row[5] for row in data)
total_xp = sum(row[6] for row in data)

level = total_xp // 500 + 1
strength_score = calculate_strength_score(data)
prs = get_personal_records(data)
leaderboard = get_leaderboard(prs)
athlete_rank = get_athlete_rank(strength_score)
streak = calculate_streak(completed_data)
badges = get_badges(
    total_xp,
    streak,
    strength_score
)
today_workout = get_todays_workout()
weekly_workouts, weekly_volume, weekly_xp = get_weekly_stats(data)

# ============================================
# SIDEBAR - MOBILE OPTIMIZED
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0; text-align: center;">
        <div style="font-size: 2rem;">💪</div>
        <h2 style="margin: 0; color: white; font-size: 1.3rem;">GymRank AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Page navigation
    page_options = [
        "Dashboard",
        "Add Workout",
        "History",
        "Leaderboard",
        "BMI Calculator",
        "Progress",
        "Goals",
        "AI Coach",
        "Gamification"
    ]
    
    # Check if page is in session state (for navigation from buttons)
    if "page" in st.session_state and st.session_state.page:
        page = st.session_state.page
        st.session_state.page = None
    else:
        # Use radio with icons for better mobile display
        page = st.sidebar.radio(
            "Navigation",
            page_options,
            format_func=lambda x: {
                "Dashboard": "🏠 Dashboard",
                "Add Workout": "➕ Add Workout",
                "History": "📜 History",
                "Leaderboard": "🏆 Leaderboard",
                "BMI Calculator": "⚖️ BMI Calculator",
                "Progress": "📈 Progress",
                "Goals": "🎯 Goals",
                "AI Coach": "🤖 AI Coach",
                "Gamification": "🏅 Gamification"
            }.get(x, x)
        )
    
    st.sidebar.markdown("---")
    
    # Display user stats in sidebar
    st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
            <span style="color: #9CA3AF;">Level</span>
            <span style="color: white; font-weight: bold;">{level}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 4px;">
            <span style="color: #9CA3AF;">XP</span>
            <span style="color: #F59E0B; font-weight: bold;">{total_xp}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 4px;">
            <span style="color: #9CA3AF;">Rank</span>
            <span style="color: #A78BFA; font-weight: bold;">{athlete_rank}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Quick Tip in sidebar (mobile friendly)
    st.sidebar.markdown("---")
    try:
        from utils.ai_exercise_tracker import AIExerciseTracker
        ai_tracker = AIExerciseTracker(data)
        fatigue = ai_tracker.get_fatigue_analysis()
        
        emoji = fatigue.get('emoji', '💪')
        suggestion = fatigue.get('suggestion', 'Keep training!')
        fatigue_level = fatigue.get('fatigue_level', 'low')
        
        color_map = {
            'low': '#34D399',
            'medium': '#F59E0B',
            'high': '#EF4444'
        }
        
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 0.6rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;">🤖 AI Coach</div>
            <div style="font-size: 0.8rem; color: {color_map.get(fatigue_level, '#9CA3AF')}; margin-top: 4px;">
                {emoji} {suggestion[:35]}...
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

# ============================================
# MOBILE BOTTOM NAVIGATION
# ============================================

# Display mobile navigation on small screens
st.markdown("""
<div class="mobile-nav" id="mobileNav">
    <a href="#" class="mobile-nav-item active" data-page="Dashboard">
        <span class="icon">🏠</span>
        <span class="label">Home</span>
    </a>
    <a href="#" class="mobile-nav-item" data-page="Add Workout">
        <span class="icon">➕</span>
        <span class="label">Add</span>
    </a>
    <a href="#" class="mobile-nav-item" data-page="History">
        <span class="icon">📜</span>
        <span class="label">History</span>
    </a>
    <a href="#" class="mobile-nav-item" data-page="Progress">
        <span class="icon">📈</span>
        <span class="label">Progress</span>
    </a>
    <a href="#" class="mobile-nav-item" data-page="AI Coach">
        <span class="icon">🤖</span>
        <span class="label">AI</span>
    </a>
</div>

<script>
    // Mobile navigation click handler
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            // Update active state
            document.querySelectorAll('.mobile-nav-item').forEach(el => el.classList.remove('active'));
            this.classList.add('active');
            // Navigate using Streamlit
            if (window.parent && window.parent.postMessage) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: page
                }, '*');
            }
        });
    });
</script>
""", unsafe_allow_html=True)

# -----------------------------
# Dashboard Page
# -----------------------------

if page == "Dashboard":

    # ============================================
    # PREMIUM MINIMAL HOMEPAGE
    # ============================================
    
    # --- Time-based Greeting ---
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning 🌅"
    elif hour < 17:
        greeting = "Good Afternoon ☀️"
    elif hour < 21:
        greeting = "Good Evening 🌆"
    else:
        greeting = "Good Night 🌙"

    st.markdown(f"""
    <div style="padding: 5px 0 10px 0;">
        <span class="greeting">{greeting}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Header ---
    st.markdown("""
    <div style="padding: 5px 0 20px 0;">
        <h1 style="font-size: 2.8rem; margin: 0; background: linear-gradient(135deg, #60A5FA, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
            💪 GymRank AI
        </h1>
        <p style="color: #9CA3AF; margin: 5px 0 0 0; font-size: 1.1rem;">Train Smarter. Track Everything.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- START WORKOUT Button ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏋️ Start Workout", use_container_width=True, type="primary"):
            st.session_state.page = "Add Workout"
            st.rerun()
    
    st.markdown("---")
    
    # --- Quick Stats Row (4 small cards) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="quick-stat">
            <div class="value" style="color: #60A5FA;">{len(data)}</div>
            <div class="label">🏋️ Total Workouts</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="quick-stat">
            <div class="value" style="color: #34D399;">{total_volume:.0f}</div>
            <div class="label">📦 Total Volume</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="quick-stat">
            <div class="value" style="color: #F59E0B;">{total_xp}</div>
            <div class="label">⭐ Total XP</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="quick-stat">
            <div class="value" style="color: #A78BFA;">{len(set(row[1] for row in data)) if data else 0}</div>
            <div class="label">💪 Exercises</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # PERSONAL RECORDS SECTION
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">📊 Personal Records</h3>
    """, unsafe_allow_html=True)

    cursor.execute("""
        SELECT exercise, MAX(weight) as max_weight,
            COUNT(*) as total_workouts,
            MAX(workout_date) as last_date
        FROM workouts 
        WHERE weight > 0
        GROUP BY exercise
        ORDER BY max_weight DESC
        LIMIT 5
    """)
    pr_data = cursor.fetchall()

    if pr_data:
        best_exercise = pr_data[0][0] if pr_data else "N/A"
        best_weight = pr_data[0][1] if pr_data else 0
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 25px; text-align: center; border: 1px solid rgba(251, 191, 36, 0.2);">
                <div style="font-size: 0.7rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px;">💪 Best Lift</div>
                <div style="font-size: 2.8rem; font-weight: bold; color: #FBBF24; margin: 5px 0;">{best_weight} kg</div>
                <div style="font-size: 1rem; color: #9CA3AF;">{best_exercise}</div>
                <div style="font-size: 0.7rem; color: #6B7280; margin-top: 5px;">🏆 Personal Record</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-size: 0.7rem; color: #9CA3AF; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">🏆 Top 3 Exercises</div>
            """, unsafe_allow_html=True)
            
            for idx, (exercise, weight, workouts, last_date) in enumerate(pr_data[:3], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"
                bar_width = min((weight / 150) * 100, 100)
                bar_color = "#FFD700" if idx == 1 else "#C0C0C0" if idx == 2 else "#CD7F32"
                
                st.markdown(f"""
                <div style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.2rem;">{medal}</span>
                            <span style="color: #E5E7EB; font-weight: 500;">{exercise}</span>
                        </div>
                        <span style="color: #F59E0B; font-weight: 600;">{weight}kg</span>
                    </div>
                    <div style="background: #2d2d44; height: 4px; border-radius: 2px; overflow: hidden; margin-top: 4px;">
                        <div style="background: {bar_color}; width: {bar_width}%; height: 100%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.6rem; color: #6B7280; margin-top: 2px;">
                        <span>{workouts} workouts</span>
                        <span>📅 {last_date}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No personal records yet. Start logging workouts!")
    
    st.markdown("---")
    
    # ============================================
    # STATS SECTION
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">📈 Your Stats</h3>
    """, unsafe_allow_html=True)
    
    current_level_xp = total_xp % 500
    level_progress = current_level_xp / 500 if total_xp > 0 else 0
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 22px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 0.8rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px;">Level {level}</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: white;">{total_xp} XP</div>
                    <div style="font-size: 0.8rem; color: #9CA3AF;">{streak} day streak 🔥</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.8rem; color: #9CA3AF;">Progress</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #60A5FA;">{int(level_progress * 100)}%</div>
                </div>
            </div>
            <div style="background: #2d2d44; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 12px;">
                <div style="background: linear-gradient(90deg, #2563eb, #7c3aed); width: {level_progress * 100}%; height: 100%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #6B7280; margin-top: 5px;">
                <span>{current_level_xp} XP</span>
                <span>500 XP to next level</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                    <div style="font-size: 0.65rem; color: #9CA3AF; text-transform: uppercase;">Strength</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: #60A5FA;">{strength_score}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                    <div style="font-size: 0.65rem; color: #9CA3AF; text-transform: uppercase;">Rank</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #A78BFA;">{athlete_rank}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                    <div style="font-size: 0.65rem; color: #9CA3AF; text-transform: uppercase;">Volume</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: #34D399;">{total_volume:.0f}</div>
                </div>
                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                    <div style="font-size: 0.65rem; color: #9CA3AF; text-transform: uppercase;">Completed</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: #F59E0B;">{len(data)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # ACHIEVEMENTS SECTION
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">🏅 Achievements</h3>
    """, unsafe_allow_html=True)
    
    from utils.gamification import GamificationSystem
    gamification = GamificationSystem(data, total_xp, strength_score)
    achievement_stats = gamification.get_achievement_stats()
    
    if achievement_stats["unlocked"]:
        cols = st.columns(4)
        for idx, achievement in enumerate(achievement_stats["unlocked"][:4]):
            with cols[idx]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(52, 211, 153, 0.2);">
                    <div style="font-size: 2.5rem;">{achievement['emoji']}</div>
                    <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 5px;">{achievement['name']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        total_achievements = achievement_stats["total_achievements"]
        unlocked_count = len(achievement_stats["unlocked"])
        
        st.markdown(f"""
        <div style="margin-top: 15px; background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #9CA3AF;">
                <span>Achievement Progress</span>
                <span>{unlocked_count}/{total_achievements}</span>
            </div>
            <div style="background: #2d2d44; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 5px;">
                <div style="background: linear-gradient(90deg, #F59E0B, #FBBF24); width: {(unlocked_count/total_achievements)*100 if total_achievements > 0 else 0}%; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if achievement_stats["locked"]:
            next_achievement = achievement_stats["locked"][0]
            st.info(f"🔜 Next: {next_achievement['emoji']} {next_achievement['name']}")
    else:
        st.info("Start working out to unlock achievements! 💪")
    
    st.markdown("---")
    
    # ============================================
    # TODAY'S WORKOUT
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">📅 Today's Workout</h3>
    """, unsafe_allow_html=True)

    if today_workout and today_workout["exercises"]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(59, 130, 246, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #60A5FA;">{today_workout['title']}</h4>
                <span style="background: rgba(59, 130, 246, 0.1); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2); font-size: 0.8rem; color: #60A5FA;">
                    {len(today_workout['exercises'])} exercises
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        for exercise in today_workout["exercises"]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
                <span style="color: #60A5FA;">▸</span>
                <span style="color: #E5E7EB;">{exercise}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 30px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size: 3rem;">😴</div>
            <h4 style="color: #9CA3AF; margin: 10px 0 5px 0;">Rest Day</h4>
            <p style="color: #6B7280; margin: 0;">Take a break and recover!</p>
        </div>
        """, unsafe_allow_html=True)

    
    # ============================================
    # AI EXERCISE TRACKER & SUGGESTIONS
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">🤖 AI Exercise Tracker</h3>
    """, unsafe_allow_html=True)
    
    from utils.ai_exercise_tracker import AIExerciseTracker
    ai_tracker = AIExerciseTracker(data)
    
    # Get today's analysis
    today_analysis = ai_tracker.get_today_analysis()
    
    # Display today's status
    if today_analysis['has_workout']:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(52, 211, 153, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="color: #34D399; font-weight: bold;">✅ Workout Logged Today</span>
                    <div style="color: #9CA3AF; font-size: 0.9rem; margin-top: 5px;">
                        {today_analysis['exercise_count']} exercises • {today_analysis['muscle_count']} muscle groups
                    </div>
                </div>
                <div style="display: flex; gap: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.7rem; color: #9CA3AF;">Volume</div>
                        <div style="font-weight: bold; color: #60A5FA;">{today_analysis['total_volume']:.0f}kg</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.7rem; color: #9CA3AF;">XP Earned</div>
                        <div style="font-weight: bold; color: #F59E0B;">{today_analysis['total_xp']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show PRs if any
        if today_analysis['prs']:
            st.markdown(f"""
            <div style="margin-top: 10px; background: rgba(251, 191, 36, 0.1); border-radius: 8px; padding: 10px; border: 1px solid rgba(251, 191, 36, 0.2);">
                <span style="color: #FBBF24;">🏆 New PRs today: {', '.join(today_analysis['prs'])}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 2rem;">⏰</span>
                <div>
                    <div style="color: #9CA3AF; font-weight: bold;">No workout logged today</div>
                    <div style="color: #6B7280; font-size: 0.9rem;">Time to hit the gym! 💪</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================
    # MUSCLE IMPROVEMENT SUGGESTIONS
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">💪 Muscle Improvement Suggestions</h3>
    """, unsafe_allow_html=True)
    
    muscle_suggestions = ai_tracker.get_muscle_suggestions()
    
    if muscle_suggestions:
        # Show top suggestions
        cols = st.columns(2)
        for idx, suggestion in enumerate(muscle_suggestions[:4]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.5rem;">{suggestion['emoji']}</span>
                        <div>
                            <div style="font-weight: bold; color: white; text-transform: capitalize;">{suggestion['muscle']}</div>
                            <div style="font-size: 0.8rem; color: #9CA3AF;">{suggestion['reason']}</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="font-size: 0.7rem; color: #9CA3AF;">Try these:</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px;">
                            {''.join([f'<span style="background: rgba(59, 130, 246, 0.1); color: #60A5FA; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem;">{ex}</span>' for ex in suggestion['suggested_exercises']])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎉 Great balance across all muscle groups! Keep up the excellent work!")
    
    st.markdown("---")
    
    # ============================================
    # FATIGUE ANALYSIS
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">📊 Fatigue & Recovery Analysis</h3>
    """, unsafe_allow_html=True)
    
    fatigue = ai_tracker.get_fatigue_analysis()
    
    color_map = {
        'low': '#34D399',
        'medium': '#F59E0B',
        'high': '#EF4444'
    }
    
    # Ensure emoji exists
    if 'emoji' not in fatigue:
        fatigue['emoji'] = '💪'
    if 'message' not in fatigue:
        fatigue['message'] = 'Keep training consistently!'
    if 'suggestion' not in fatigue:
        fatigue['suggestion'] = 'Continue with your regular routine.'
    if 'fatigue_level' not in fatigue:
        fatigue['fatigue_level'] = 'low'
    if 'recent_workouts' not in fatigue:
        fatigue['recent_workouts'] = 0
    if 'recent_volume' not in fatigue:
        fatigue['recent_volume'] = 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 2rem;">{fatigue['emoji']}</span>
                <div>
                    <div style="font-weight: bold; color: {color_map.get(fatigue['fatigue_level'], '#9CA3AF')}; text-transform: uppercase;">
                        {fatigue['fatigue_level'].upper()} Fatigue
                    </div>
                    <div style="color: #9CA3AF; font-size: 0.9rem;">{fatigue['message']}</div>
                </div>
            </div>
            <div style="display: flex; gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 0.7rem; color: #9CA3AF;">Workouts (7 days)</div>
                    <div style="font-weight: bold; color: #60A5FA;">{fatigue['recent_workouts']}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.7rem; color: #9CA3AF;">Volume (7 days)</div>
                    <div style="font-weight: bold; color: #34D399;">{fatigue['recent_volume']:.0f}kg</div>
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.02); border-radius: 8px;">
            <span style="color: #9CA3AF; font-size: 0.9rem;">💡 {fatigue['suggestion']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ============================================
    # AI PLATEAU DETECTOR
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">🚨 Plateau Detector</h3>
    """, unsafe_allow_html=True)
    
    plateaus = ai_tracker.detect_plateaus()
    
    if plateaus:
        for plateau in plateaus[:3]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold; color: white;">{plateau['exercise']}</span>
                        <span style="color: #9CA3AF; font-size: 0.9rem;"> - {plateau['current_weight']}kg</span>
                    </div>
                    <span style="background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem;">⚠️ Plateau</span>
                </div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 5px;">💡 {plateau['suggestion']}</div>
                <div style="color: #6B7280; font-size: 0.7rem; margin-top: 5px;">🎯 Target muscle: {plateau['muscle'].capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 No plateaus detected! You're making consistent progress!")
    
    st.markdown("---")
    
    # ============================================
    # AI PR PREDICTOR
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">🎯 PR Predictor</h3>
    """, unsafe_allow_html=True)
    
    # Get exercises with enough data
    exercises_with_data = [ex for ex, data in ai_tracker.exercise_history.items() if len(data['weights']) >= 3]
    
    if exercises_with_data:
        # Show predictions for top 3 exercises
        predictions = []
        for exercise in exercises_with_data[:5]:
            pred = ai_tracker.predict_next_pr(exercise)
            if pred:
                predictions.append(pred)
        
        if predictions:
            cols = st.columns(3)
            for idx, pred in enumerate(predictions[:3]):
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; border: 1px solid rgba(251, 191, 36, 0.2); text-align: center;">
                        <div style="font-weight: bold; color: white;">{pred['exercise']}</div>
                        <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 5px;">Current PR</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #F59E0B;">{pred['current_pr']}kg</div>
                        <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 5px;">Predicted Next</div>
                        <div style="font-size: 1.3rem; font-weight: bold; color: #34D399;">{pred['predicted_next']}kg</div>
                        <div style="font-size: 0.7rem; color: #6B7280; margin-top: 5px;">📊 {pred['workouts_needed']} workouts to reach</div>
                        <div style="font-size: 0.7rem; color: #6B7280;">🎯 {pred['trend']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Log more workouts for PR predictions!")
    else:
        st.info("Need at least 3 workouts per exercise for PR predictions. Keep logging!")
    
    st.markdown("---")
    
    # ============================================
    # AI VOLUME OPTIMIZER
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">📊 Volume Optimizer</h3>
    """, unsafe_allow_html=True)
    
    volume_suggestions = ai_tracker.get_volume_optimizer()
    
    if volume_suggestions:
        cols = st.columns(2)
        for idx, suggestion in enumerate(volume_suggestions[:4]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; color: white; text-transform: capitalize;">{suggestion['muscle']}</span>
                        <span>{suggestion['emoji']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 5px;">
                        <span style="color: #9CA3AF;">Current: {suggestion['current_avg']}kg</span>
                        <span style="color: #60A5FA;">Suggested: {suggestion['suggested']}kg</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #6B7280; margin-top: 5px;">
                        <span>Max: {suggestion['max_recorded']}kg</span>
                        <span style="color: #34D399;">+{suggestion['increase']}kg increase</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Log more workouts for volume optimization!")
    
    st.markdown("---")
    
    # ============================================
    # AI FORM TIPS
    # ============================================
    st.markdown("""
    <h3 style="color: white; margin-bottom: 15px; font-weight: 600;">🧠 Form Tips</h3>
    """, unsafe_allow_html=True)
    
    form_tips = ai_tracker.get_exercise_form_tips()
    
    if form_tips:
        for tip in form_tips:
            severity_color = "#EF4444" if tip['severity'] == 'high' else "#F59E0B" if tip['severity'] == 'medium' else "#60A5FA"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; border-left: 4px solid {severity_color}; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: white;">{tip['exercise']}</span>
                    <span style="color: #9CA3AF; font-size: 0.7rem;">🎯 {tip['muscle'].capitalize()}</span>
                </div>
                <div style="color: #9CA3AF; font-size: 0.85rem; margin-top: 5px;">⚠️ {tip['issue']}</div>
                <div style="color: #60A5FA; font-size: 0.85rem; margin-top: 5px;">💡 {tip['tip']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💪 Your form looks great! Keep up the good work!")

    
    # ============================================
    # MOTIVATIONAL QUOTE
    # ============================================
    import random
    
    quotes = [
        "💪 \"The only bad workout is the one that didn't happen.\"",
        "🔥 \"Success starts with self-discipline.\"",
        "🏆 \"Your only competition is yourself.\"",
        "⚡ \"Small progress is still progress.\"",
        "🌟 \"Believe in yourself and all that you are.\"",
        "💯 \"Consistency over intensity.\"",
        "🚀 \"The best time to start was yesterday. The next best time is now.\"",
        "🎯 \"Focus on progress, not perfection.\""
    ]
    
    daily_quote = random.choice(quotes)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
        <span style="color: #9CA3AF; font-style: italic; font-size: 0.95rem;">{daily_quote}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # QUICK TIPS
    # ============================================
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px;">
            <ul style="color: #9CA3AF; line-height: 1.8; margin: 0;">
                <li>🎯 <strong>Set goals</strong> - Track your progress and stay motivated</li>
                <li>📊 <strong>Log consistently</strong> - Every workout builds your history</li>
                <li>🏆 <strong>Beat your PRs</strong> - Push yourself to new records</li>
                <li>🔥 <strong>Maintain your streak</strong> - Consistency is key</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Add Workout Page
# -----------------------------

elif page == "Add Workout":

    st.title("➕ Log New Workout")
    st.markdown("Track your lifts, set PRs, and earn XP!")
    
    # Get existing exercises for suggestions
    cursor.execute("SELECT DISTINCT exercise FROM workouts WHERE weight > 0 ORDER BY exercise")
    existing_exercises = [row[0] for row in cursor.fetchall()]
    
    # Premium form layout
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px; padding: 25px; border: 1px solid rgba(255,255,255,0.05);">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Exercise input with autocomplete suggestions
            # Initialize session state for exercise if not exists
            if 'template_exercise' not in st.session_state:
                st.session_state.template_exercise = ""
            
            if existing_exercises:
                # Create a list with the current template value if it exists
                options = ["Enter new exercise..."] + existing_exercises
                
                # If there's a template exercise selected, use it
                if st.session_state.template_exercise and st.session_state.template_exercise in existing_exercises:
                    default_index = options.index(st.session_state.template_exercise)
                else:
                    default_index = 0
                
                exercise = st.selectbox(
                    "🏋️ Exercise Name",
                    options,
                    index=default_index,
                    help="Select an existing exercise or type a new one"
                )
                
                if exercise == "Enter new exercise...":
                    exercise = st.text_input(
                        "Type new exercise name", 
                        placeholder="e.g., Deadlift, Bench Press...",
                        value=st.session_state.template_exercise if st.session_state.template_exercise not in existing_exercises else ""
                    )
                else:
                    # Clear template if an existing exercise was selected
                    if st.session_state.template_exercise:
                        st.session_state.template_exercise = ""
            else:
                exercise = st.text_input(
                    "🏋️ Exercise Name",
                    placeholder="e.g., Deadlift, Bench Press...",
                    help="Enter the name of your exercise",
                    value=st.session_state.template_exercise
                )
            
            # Quick exercise templates
            # Quick exercise templates with session state
            with st.expander("📋 Quick Templates"):
                st.markdown("Click to auto-fill common exercises:")
                template_cols = st.columns(3)
                templates = [
                    ("🏋️ Bench Press", "Bench Press"),
                    ("🦵 Squat", "Squat"),
                    ("💪 Deadlift", "Deadlift"),
                    ("🏋️ OHP", "Overhead Press"),
                    ("💪 Pull Up", "Pull Ups"),
                    ("🦵 Leg Press", "Leg Press"),
                    ("🏋️ Incline Press", "Incline Bench Press"),
                    ("💪 Barbell Row", "Barbell Row"),
                    ("🦵 Leg Extension", "Leg Extension"),
                ]
                for idx, (label, value) in enumerate(templates):
                    with template_cols[idx % 3]:
                        if st.button(label, key=f"template_{idx}"):
                            # Store the selected exercise in session state
                            st.session_state.template_exercise = value
                            st.rerun()
        
        with col2:
            # Quick stats preview
            st.markdown("""
            <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-size: 0.8rem; color: #9CA3AF; text-align: center;">💡 Quick Tips</div>
                <ul style="color: #9CA3AF; font-size: 0.8rem; padding-left: 15px; margin: 5px 0;">
                    <li>Track your 1RM progress</li>
                    <li>Earn XP for every lift</li>
                    <li>Set new personal records</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Input fields with better layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            weight = st.number_input(
                "🏋️ Weight (kg)",
                min_value=0.0,
                step=2.5,
                format="%.1f",
                help="Enter the weight you lifted"
            )
        
        with col2:
            reps = st.number_input(
                "🔄 Reps",
                min_value=1,
                step=1,
                help="Number of repetitions performed"
            )
        
        with col3:
            sets = st.number_input(
                "📊 Sets",
                min_value=1,
                step=1,
                help="Number of sets performed"
            )
        
        # Live stats preview (show while user types)
        if weight > 0 and reps > 0 and sets > 0:
            st.markdown("---")
            st.markdown("### 📊 Workout Preview")
            
            volume = weight * reps * sets
            xp = calculate_xp(weight, reps, sets)
            one_rm = round(weight * (1 + reps / 30), 1)
            rank = get_rank(weight)
            
            # Check for PR
            cursor.execute("SELECT MAX(weight) FROM workouts WHERE exercise=?", (exercise,))
            previous_pr = cursor.fetchone()[0]
            is_pr = previous_pr is None or weight > previous_pr
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📦 Volume", f"{volume:.0f}kg", delta=f"{reps}×{sets}")
            
            with col2:
                st.metric("⭐ XP Earned", xp)
            
            with col3:
                st.metric("💪 1RM", f"{one_rm}kg", delta="Estimate")
            
            with col4:
                if is_pr and weight > 0:
                    st.metric("🏆 PR", "NEW RECORD!", delta=f"{weight}kg", delta_color="normal")
                else:
                    st.metric("📊 Rank", rank)
            
            # Progress bar for rank
            rank_progress = min(weight / 150, 1.0)
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #9CA3AF;">
                    <span>Rank Progress</span>
                    <span>{rank}</span>
                </div>
                <div style="background: #2d2d44; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #2563eb, #7c3aed); width: {rank_progress * 100}%; height: 100%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # PR Alert
            if is_pr and weight > 0:
                st.success(f"🎯 This would be a NEW PERSONAL RECORD for {exercise}!")
        
        st.markdown("---")
        
        # Save button with premium styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            save_button = st.button(
                "💪 Save Workout",
                use_container_width=True,
                type="primary"
            )
        
        if save_button:
            if not exercise or exercise == "Enter new exercise...":
                st.error("⚠️ Please enter an exercise name")
            elif weight <= 0:
                st.error("⚠️ Please enter a valid weight")
            elif reps <= 0:
                st.error("⚠️ Please enter valid reps")
            elif sets <= 0:
                st.error("⚠️ Please enter valid sets")
            else:
                volume = weight * reps * sets
                xp = calculate_xp(weight, reps, sets)
                one_rm = round(weight * (1 + reps / 30), 1)
                rank = get_rank(weight)
                workout_date = str(date.today())
                
                # Check for PR
                cursor.execute("SELECT MAX(weight) FROM workouts WHERE exercise=?", (exercise,))
                previous_pr = cursor.fetchone()[0]
                is_pr = previous_pr is None or weight > previous_pr
                
                # Insert workout
                cursor.execute(
                    """
                    INSERT INTO workouts
                    (exercise, weight, reps, sets, volume, xp, rank, workout_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (exercise, weight, reps, sets, volume, xp, rank, workout_date)
                )
                conn.commit()
                
                # Show success with animations
                if is_pr:
                    st.balloons()
                    st.success(f"🏆 NEW PERSONAL RECORD! {exercise}: {weight}kg")
                    st.audio("https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3", format="audio/mp3", autoplay=True)
                else:
                    st.success(f"✅ Workout logged successfully!")
                
                # Show detailed stats
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 20px; margin: 10px 0; border: 1px solid rgba(59, 130, 246, 0.2);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px;">
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">Exercise</div>
                            <div style="font-weight: bold; color: white;">{exercise}</div>
                        </div>
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">Weight</div>
                            <div style="font-weight: bold; color: #F59E0B;">{weight}kg</div>
                        </div>
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">Volume</div>
                            <div style="font-weight: bold; color: #60A5FA;">{volume:.0f}kg</div>
                        </div>
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">XP Earned</div>
                            <div style="font-weight: bold; color: #34D399;">+{xp} XP</div>
                        </div>
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">1RM</div>
                            <div style="font-weight: bold; color: #A78BFA;">{one_rm}kg</div>
                        </div>
                        <div>
                            <div style="color: #9CA3AF; font-size: 0.8rem;">Rank</div>
                            <div style="font-weight: bold; color: #FBBF24;">{rank}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Option to add another
                if st.button("➕ Add Another Set", use_container_width=True):
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent workouts for reference
    st.markdown("---")
    with st.expander("📜 Recent Workouts", expanded=False):
        cursor.execute("""
            SELECT exercise, weight, reps, sets, workout_date 
            FROM workouts 
            ORDER BY id DESC 
            LIMIT 5
        """)
        recent_workouts = cursor.fetchall()
        
        if recent_workouts:
            for workout in recent_workouts:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #3B82F6;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold; color: white;">{workout[0]}</span>
                        <span style="color: #9CA3AF;">{workout[3]}×{workout[2]} reps</span>
                        <span style="color: #F59E0B;">{workout[1]}kg</span>
                        <span style="color: #6B7280; font-size: 0.8rem;">{workout[4]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent workouts. Start logging!")


elif page == "History":

    st.title("📜 Workout History")
    st.markdown("View and manage your workout history")

    search = st.text_input("🔍 Search Exercise", placeholder="Type exercise name...")
    selected_date = st.date_input("📅 Filter by date", value=None)

    filtered_data = data

    if search:
        filtered_data = [
            row for row in filtered_data
            if search.lower() in row[1].lower()
        ]

    if selected_date:
        filtered_data = [
            row for row in filtered_data
            if row[8] == str(selected_date)
        ]

    st.markdown(f"### 📊 Found {len(filtered_data)} workout(s)")

    if len(filtered_data) > 0:
        # Summary stats
        max_weight = max(row[2] for row in filtered_data)
        total_volume = sum(row[5] for row in filtered_data)
        times_performed = len(filtered_data)
        average_weight = sum(row[2] for row in filtered_data) / len(filtered_data)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏆 Personal Best", f"{max_weight} kg")
        with col2:
            st.metric("📦 Total Volume", f"{total_volume:.0f} kg")
        with col3:
            st.metric("🔁 Times Performed", times_performed)
        with col4:
            st.metric("📊 Average Weight", f"{average_weight:.1f} kg")

        st.markdown("---")

        # Progress Chart
        chart_data = pd.DataFrame(
            filtered_data,
            columns=["ID", "Exercise", "Weight", "Reps", "Sets", "Volume", "XP", "Rank", "Date"]
        )

        fig = px.line(
            chart_data,
            x="Date",
            y="Weight",
            title="📈 Weight Progress Over Time",
            markers=True
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Display workouts
        for row in filtered_data:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                with col1:
                    st.markdown(f"**{row[1]}**")
                with col2:
                    st.markdown(f"🏋️ {row[2]} kg")
                with col3:
                    st.markdown(f"🔄 {row[3]} reps")
                with col4:
                    st.markdown(f"📊 {row[4]} sets")
                with col5:
                    if st.button(f"🗑 Delete", key=f"del_{row[0]}"):
                        cursor.execute("DELETE FROM workouts WHERE id=?", (row[0],))
                        conn.commit()
                        st.success(f"✅ Deleted {row[1]}!")
                        st.rerun()
                st.divider()
    else:
        st.info("No workouts found. Start logging your workouts!")

    # Show recent workouts summary
    with st.expander("📈 Quick Stats", expanded=False):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                <div style="text-align: center;">
                    <div style="color: #9CA3AF; font-size: 0.8rem;">Total Workouts</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #60A5FA;">{len(data)}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #9CA3AF; font-size: 0.8rem;">Total Volume</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #34D399;">{sum(row[5] for row in data):.0f} kg</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #9CA3AF; font-size: 0.8rem;">Total XP</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #F59E0B;">{sum(row[6] for row in data)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


elif page == "Leaderboard":
    
    st.title("🏆 Personal Records Leaderboard")
    st.markdown("Track your best lifts and compare your progress across all exercises")
    
    # Get all exercises and their PRs
    cursor.execute("""
        SELECT exercise, MAX(weight) as max_weight, 
               COUNT(*) as total_workouts,
               MAX(workout_date) as last_date,
               AVG(weight) as avg_weight
        FROM workouts 
        WHERE weight > 0
        GROUP BY exercise
        ORDER BY max_weight DESC
    """)
    pr_data = cursor.fetchall()
    
    if pr_data:
        # Summary stats
        total_exercises = len(pr_data)
        total_pr_weight = sum(row[1] for row in pr_data if row[1] is not None)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 15px; text-align: center; border: 1px solid rgba(59, 130, 246, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">🏋️ Total Exercises</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #60A5FA;">{total_exercises}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 15px; text-align: center; border: 1px solid rgba(52, 211, 153, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">📦 Total PR Weight</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #34D399;">{total_pr_weight:.0f}kg</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Find strongest exercise
            strongest = max(pr_data, key=lambda x: x[1] if x[1] is not None else 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 15px; text-align: center; border: 1px solid rgba(251, 191, 36, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">💪 Strongest Lift</div>
                <div style="font-size: 1.3rem; font-weight: bold; color: #FBBF24;">{strongest[0]}</div>
                <div style="font-size: 1rem; color: #F59E0B;">{strongest[1]}kg</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Find exercise with most workouts
            most_frequent = max(pr_data, key=lambda x: x[2] if x[2] is not None else 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 15px; text-align: center; border: 1px solid rgba(167, 139, 250, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">🔥 Most Trained</div>
                <div style="font-size: 1.3rem; font-weight: bold; color: #A78BFA;">{most_frequent[0]}</div>
                <div style="font-size: 1rem; color: #9CA3AF;">{most_frequent[2]} workouts</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Search and filter
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            search_exercise = st.text_input("🔍 Search Exercise", placeholder="Type exercise name...")
        with col_filter:
            sort_by = st.selectbox(
                "Sort By",
                ["Weight (Highest)", "Weight (Lowest)", "Most Workouts", "Recent"],
                index=0
            )
        
        # Filter and sort data
        filtered_data = pr_data
        if search_exercise:
            filtered_data = [row for row in pr_data if search_exercise.lower() in row[0].lower()]
        
        # Apply sorting
        if sort_by == "Weight (Highest)":
            filtered_data = sorted(filtered_data, key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
        elif sort_by == "Weight (Lowest)":
            filtered_data = sorted(filtered_data, key=lambda x: x[1] if x[1] is not None else 0)
        elif sort_by == "Most Workouts":
            filtered_data = sorted(filtered_data, key=lambda x: x[2] if x[2] is not None else 0, reverse=True)
        elif sort_by == "Recent":
            filtered_data = sorted(filtered_data, key=lambda x: x[3] if x[3] is not None else "", reverse=True)
        
        # Display leaderboard
        st.markdown(f"### 📊 {len(filtered_data)} Personal Records")
        
        # Create columns for each record with rank badges
        for idx, row in enumerate(filtered_data, start=1):
            exercise = row[0]
            max_weight = row[1] if row[1] is not None else 0
            total_workouts = row[2] if row[2] is not None else 0
            last_date = row[3] if row[3] is not None else "N/A"
            avg_weight = row[4] if row[4] is not None else 0
            
            # Determine rank badge
            if idx == 1:
                rank_badge = "🥇"
                rank_color = "#FFD700"
            elif idx == 2:
                rank_badge = "🥈"
                rank_color = "#C0C0C0"
            elif idx == 3:
                rank_badge = "🥉"
                rank_color = "#CD7F32"
            else:
                rank_badge = f"#{idx}"
                rank_color = "#6B7280"
            
            # Determine weight tier
            if max_weight >= 100:
                tier_emoji = "💎"
                tier_color = "#B9F2FF"
            elif max_weight >= 70:
                tier_emoji = "🥇"
                tier_color = "#FFD700"
            elif max_weight >= 40:
                tier_emoji = "🥈"
                tier_color = "#C0C0C0"
            else:
                tier_emoji = "💪"
                tier_color = "#CD7F32"
            
            # Calculate volume score (workouts × avg weight)
            volume_score = int(total_workouts * avg_weight) if avg_weight > 0 else 0
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; margin: 8px 0; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: {rank_color}; min-width: 40px;">{rank_badge}</div>
                        <div>
                            <div style="font-size: 1.1rem; font-weight: bold; color: white;">{exercise}</div>
                            <div style="font-size: 0.8rem; color: #9CA3AF;">📅 Last: {last_date}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.7rem; color: #9CA3AF;">PR</div>
                            <div style="font-size: 1.3rem; font-weight: bold; color: #F59E0B;">{max_weight:.1f}kg</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.7rem; color: #9CA3AF;">Workouts</div>
                            <div style="font-size: 1.1rem; font-weight: bold; color: #60A5FA;">{total_workouts}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.7rem; color: #9CA3AF;">Avg Weight</div>
                            <div style="font-size: 1.1rem; font-weight: bold; color: #34D399;">{avg_weight:.1f}kg</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 5px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
                            <span style="font-size: 1.2rem;">{tier_emoji}</span>
                        </div>
                    </div>
                </div>
                <!-- Progress bar showing PR progress -->
                <div style="margin-top: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #6B7280;">
                        <span>Progress</span>
                        <span>{max_weight:.0f}kg</span>
                    </div>
                    <div style="background: #2d2d44; height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, {tier_color}, #7c3aed); width: {min(max_weight / 150 * 100, 100)}%; height: 100%;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # View all exercises button
        if len(filtered_data) > 10:
            if st.button("📊 View All Exercises", use_container_width=True):
                st.write("All exercises displayed above")
        
        # Add statistics section
        st.markdown("---")
        st.subheader("📊 Leaderboard Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # Average PR weight
            avg_pr = sum(row[1] for row in pr_data if row[1] is not None) / len(pr_data) if pr_data else 0
            st.metric("📊 Average PR Weight", f"{avg_pr:.1f}kg")
        
        with col2:
            # Total workouts across all exercises
            total_all_workouts = sum(row[2] for row in pr_data if row[2] is not None)
            st.metric("🏋️ Total Workouts", total_all_workouts)
        
        with col3:
            # Most recent PR
            recent_pr = max((row[3] for row in pr_data if row[3] is not None), default="N/A")
            st.metric("🕐 Latest PR", recent_pr)
        
        # Export option
        if st.button("📤 Export Leaderboard Data", use_container_width=True):
            export_data = []
            for row in pr_data:
                export_data.append({
                    "Exercise": row[0],
                    "PR Weight": row[1],
                    "Total Workouts": row[2],
                    "Last Date": row[3],
                    "Average Weight": row[4]
                })
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="leaderboard_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        st.info("No personal records yet. Start logging workouts to build your leaderboard!")

# -----------------------------
# BMI Calculator
# -----------------------------

elif page == "BMI Calculator":

    st.title("⚖️ BMI Calculator")
    st.markdown("Track your Body Mass Index and maintain a healthy weight")
    
    # ============================================
    # BMI INPUT SECTION
    # ============================================
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <h3 style="color: white; margin: 0 0 5px 0;">📏 Enter Your Details</h3>
        <p style="color: #9CA3AF; margin: 0 0 20px 0;">Enter your weight and height to calculate your BMI</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input(
            "⚖️ Weight (kg)",
            min_value=1.0,
            max_value=300.0,
            step=0.5,
            format="%.1f",
            help="Enter your weight in kilograms",
            key="bmi_weight"
        )
        
        # Quick weight presets
        st.markdown("""
        <div style="margin-top: 5px; display: flex; gap: 5px; flex-wrap: wrap;">
            <span style="color: #6B7280; font-size: 0.7rem;">Quick:</span>
        """, unsafe_allow_html=True)
        weight_presets = [50, 60, 70, 80, 90, 100]
        cols = st.columns(6)
        for idx, preset in enumerate(weight_presets):
            with cols[idx]:
                if st.button(f"{preset}kg", key=f"w_{preset}", use_container_width=True):
                    st.session_state.bmi_weight = float(preset)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        height = st.number_input(
            "📏 Height (cm)",
            min_value=50.0,
            max_value=250.0,
            step=0.5,
            format="%.1f",
            help="Enter your height in centimeters",
            key="bmi_height"
        )
        
        # Quick height presets
        st.markdown("""
        <div style="margin-top: 5px; display: flex; gap: 5px; flex-wrap: wrap;">
            <span style="color: #6B7280; font-size: 0.7rem;">Quick:</span>
        """, unsafe_allow_html=True)
        height_presets = [150, 160, 170, 180, 190, 200]
        cols = st.columns(6)
        for idx, preset in enumerate(height_presets):
            with cols[idx]:
                if st.button(f"{preset}cm", key=f"h_{preset}", use_container_width=True):
                    st.session_state.bmi_height = float(preset)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ============================================
    # CALCULATE BUTTON
    # ============================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("📊 Calculate BMI", use_container_width=True, type="primary")
    
    # ============================================
    # RESULTS SECTION
    # ============================================
    if calculate:
        if weight > 0 and height > 0:
            bmi = weight / ((height / 100) ** 2)
            
            # Determine BMI category
            if bmi < 18.5:
                category = "Underweight"
                color = "#60A5FA"
                emoji = "⚠️"
                advice = "You may need to gain some weight. Consider consulting a nutritionist."
                bg_color = "rgba(96, 165, 250, 0.1)"
                border_color = "rgba(96, 165, 250, 0.3)"
            elif bmi < 25:
                category = "Normal Weight"
                color = "#34D399"
                emoji = "✅"
                advice = "Great job! You're in the healthy weight range. Keep it up!"
                bg_color = "rgba(52, 211, 153, 0.1)"
                border_color = "rgba(52, 211, 153, 0.3)"
            elif bmi < 30:
                category = "Overweight"
                color = "#F59E0B"
                emoji = "⚡"
                advice = "Consider incorporating more exercise and a balanced diet."
                bg_color = "rgba(245, 158, 11, 0.1)"
                border_color = "rgba(245, 158, 11, 0.3)"
            else:
                category = "Obese"
                color = "#EF4444"
                emoji = "🔴"
                advice = "We recommend consulting a healthcare professional for guidance."
                bg_color = "rgba(239, 68, 68, 0.1)"
                border_color = "rgba(239, 68, 68, 0.3)"
            
            # Calculate healthy weight range
            min_healthy = 18.5 * ((height / 100) ** 2)
            max_healthy = 24.9 * ((height / 100) ** 2)
            
            st.markdown("---")
            
            # ============================================
            # BMI RESULT CARD
            # ============================================
            st.markdown(f"""
            <div style="background: {bg_color}; border-radius: 20px; padding: 30px; border: 2px solid {border_color}; text-align: center; margin: 20px 0;">
                <div style="font-size: 0.8rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 2px;">Your BMI Result</div>
                <div style="font-size: 4rem; font-weight: bold; color: {color}; margin: 10px 0;">{bmi:.1f}</div>
                <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5rem;">{emoji}</span>
                    <span style="font-size: 1.5rem; font-weight: bold; color: {color};">{category}</span>
                </div>
                <p style="color: #9CA3AF; margin-top: 10px;">{advice}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ============================================
            # BMI METER (Visual Gauge)
            # ============================================
            st.markdown("""
            <h4 style="color: white; margin: 20px 0 10px 0;">📊 BMI Scale</h4>
            """, unsafe_allow_html=True)
            
            # Create a visual BMI scale
            bmi_percent = min((bmi / 40) * 100, 100)
            
            st.markdown(f"""
            <div style="background: #2d2d44; border-radius: 10px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="position: relative; height: 20px; background: linear-gradient(90deg, #60A5FA, #34D399 30%, #F59E0B 60%, #EF4444 80%); border-radius: 10px; overflow: hidden;">
                    <div style="position: absolute; left: {bmi_percent}%; top: -5px; transform: translateX(-50%); width: 4px; height: 30px; background: white; border-radius: 2px; box-shadow: 0 0 10px rgba(255,255,255,0.5);"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #6B7280; margin-top: 5px;">
                    <span>Underweight</span>
                    <span>Normal</span>
                    <span>Overweight</span>
                    <span>Obese</span>
                </div>
                <div style="text-align: center; margin-top: 10px; color: #9CA3AF; font-size: 0.8rem;">
                    Current BMI: <strong style="color: {color};">{bmi:.1f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ============================================
            # HEALTHY WEIGHT RANGE
            # ============================================
            st.markdown("""
            <h4 style="color: white; margin: 20px 0 10px 0;">💡 Healthy Weight Range</h4>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background: #1E1E1E; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.7rem; color: #9CA3AF;">Min Healthy</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #60A5FA;">{min_healthy:.1f} kg</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: #1E1E1E; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.7rem; color: #9CA3AF;">Your Weight</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #F59E0B;">{weight:.1f} kg</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: #1E1E1E; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 0.7rem; color: #9CA3AF;">Max Healthy</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #34D399;">{max_healthy:.1f} kg</div>
                </div>
                """, unsafe_allow_html=True)
            
            # ============================================
            # RECOMMENDATIONS
            # ============================================
            st.markdown("""
            <h4 style="color: white; margin: 20px 0 10px 0;">📋 Recommendations</h4>
            """, unsafe_allow_html=True)
            
            if bmi < 18.5:
                st.markdown("""
                <div style="background: rgba(96, 165, 250, 0.05); border-radius: 12px; padding: 15px; border-left: 4px solid #60A5FA;">
                    <ul style="color: #9CA3AF; margin: 0; line-height: 1.8;">
                        <li>🍎 <strong>Increase calorie intake</strong> - Add healthy fats and proteins to your diet</li>
                        <li>💪 <strong>Strength training</strong> - Build muscle mass with resistance exercises</li>
                        <li>🥑 <strong>Healthy fats</strong> - Include avocados, nuts, and olive oil in your meals</li>
                        <li>📅 <strong>Regular meals</strong> - Eat 5-6 smaller meals throughout the day</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif bmi < 25:
                st.markdown("""
                <div style="background: rgba(52, 211, 153, 0.05); border-radius: 12px; padding: 15px; border-left: 4px solid #34D399;">
                    <ul style="color: #9CA3AF; margin: 0; line-height: 1.8;">
                        <li>🏃 <strong>Stay active</strong> - Maintain your current exercise routine</li>
                        <li>🥗 <strong>Balanced diet</strong> - Continue eating a variety of nutritious foods</li>
                        <li>💧 <strong>Stay hydrated</strong> - Drink plenty of water throughout the day</li>
                        <li>😴 <strong>Quality sleep</strong> - Aim for 7-8 hours of sleep per night</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif bmi < 30:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.05); border-radius: 12px; padding: 15px; border-left: 4px solid #F59E0B;">
                    <ul style="color: #9CA3AF; margin: 0; line-height: 1.8;">
                        <li>🏋️ <strong>Increase exercise</strong> - Aim for 150+ minutes of moderate activity per week</li>
                        <li>🥦 <strong>Healthy eating</strong> - Focus on whole foods and reduce processed foods</li>
                        <li>📱 <strong>Track calories</strong> - Monitor your daily calorie intake</li>
                        <li>📅 <strong>Set goals</strong> - Aim for 0.5-1kg weight loss per week</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.05); border-radius: 12px; padding: 15px; border-left: 4px solid #EF4444;">
                    <ul style="color: #9CA3AF; margin: 0; line-height: 1.8;">
                        <li>🏥 <strong>Consult a doctor</strong> - Get professional medical advice</li>
                        <li>🍽️ <strong>Portion control</strong> - Be mindful of portion sizes</li>
                        <li>🚶 <strong>Start walking</strong> - Begin with daily walks and gradually increase intensity</li>
                        <li>📊 <strong>Track progress</strong> - Monitor your weight weekly and adjust accordingly</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # ============================================
            # BMI TABLE
            # ============================================
            with st.expander("📊 BMI Categories Reference", expanded=False):
                st.markdown("""
                <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px;">
                    <table style="width: 100%; color: #E5E7EB; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <th style="padding: 8px; text-align: left; color: #9CA3AF;">Category</th>
                            <th style="padding: 8px; text-align: left; color: #9CA3AF;">BMI Range</th>
                            <th style="padding: 8px; text-align: left; color: #9CA3AF;">Status</th>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding: 8px;">Underweight</td>
                            <td style="padding: 8px;">Below 18.5</td>
                            <td style="padding: 8px; color: #60A5FA;">⚠️ Needs attention</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding: 8px;">Normal Weight</td>
                            <td style="padding: 8px;">18.5 – 24.9</td>
                            <td style="padding: 8px; color: #34D399;">✅ Healthy</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding: 8px;">Overweight</td>
                            <td style="padding: 8px;">25.0 – 29.9</td>
                            <td style="padding: 8px; color: #F59E0B;">⚡ Needs improvement</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;">Obese</td>
                            <td style="padding: 8px;">30.0 and above</td>
                            <td style="padding: 8px; color: #EF4444;">🔴 Needs attention</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Please enter valid weight and height values.")
    
    # ============================================
    # QUICK TIPS
    # ============================================
    with st.expander("💡 BMI Tips", expanded=False):
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px;">
            <ul style="color: #9CA3AF; line-height: 1.8; margin: 0;">
                <li>📊 <strong>Track regularly</strong> - Check your BMI monthly to monitor progress</li>
                <li>🏋️ <strong>Muscle matters</strong> - BMI doesn't distinguish between muscle and fat</li>
                <li>🥗 <strong>Balanced approach</strong> - Focus on overall health, not just numbers</li>
                <li>📱 <strong>Stay consistent</strong> - Regular exercise and healthy eating are key</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif page == "Progress":
    
    st.title("📈 Advanced Analytics Dashboard")
    
    # Load data with connection
    conn = sqlite3.connect("workouts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts ORDER BY workout_date")
    data = cursor.fetchall()
    
    if data:
        from utils.analytics import PerformanceAnalytics
        
        # Initialize analytics
        analytics = PerformanceAnalytics(data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            quality_score = analytics.get_workout_quality_score()
            st.metric(
                "🏆 Quality Score",
                f"{quality_score}/100",
                delta="Excellent" if quality_score > 80 else "Good" if quality_score > 60 else "Needs Work"
            )
        
        with col2:
            trends = analytics.get_performance_trends()
            improving = sum(1 for t in trends.values() if 'Increasing' in t['trend'])
            total = len(trends)
            improvement_rate = (improving / total * 100) if total > 0 else 0
            st.metric(
                "📈 Improvement Rate",
                f"{improvement_rate:.0f}%",
                delta=f"{improving}/{total} exercises"
            )
        
        with col3:
            summary = analytics.get_weekly_summary()
            if summary:
                st.metric(
                    "📊 Weekly Workouts",
                    summary['total_workouts'],
                    delta=f"{summary['total_volume']:.0f}kg volume"
                )
            else:
                st.metric("📊 Weekly Workouts", 0)
        
        with col4:
            predictions = analytics.get_predictions()
            if predictions:
                best_prediction = max(predictions.items(), key=lambda x: x[1]['improvement'])
                st.metric(
                    "🎯 Next PR Prediction",
                    f"{best_prediction[1]['predicted_weight']:.1f}kg",
                    delta=f"{best_prediction[0]} +{best_prediction[1]['improvement']:.1f}kg"
                )
            else:
                st.metric("🎯 Next PR Prediction", "N/A")
        
        st.markdown("---")
        
        # Tabs for different analytics views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Trends", "📈 Volume Analysis", "🎯 1RM Estimator", "📅 Weekly Summary"])
        
        with tab1:
            st.subheader("📊 Exercise Performance Trends")
            
            trends = analytics.get_performance_trends()
            if trends:
                # Create trend dataframe
                trend_data = []
                for exercise, data in trends.items():
                    trend_data.append({
                        'Exercise': exercise,
                        'Trend': data['trend'],
                        'Improvement': f"{data['improvement']:.1f}%",
                        'Current Weight': f"{data['current_weight']:.1f}kg",
                        'Best Weight': f"{data['best_weight']:.1f}kg",
                        'Workouts': data['total_workouts']
                    })
                
                df_trends = pd.DataFrame(trend_data)
                st.dataframe(
                    df_trends,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Exercise": st.column_config.TextColumn("Exercise"),
                        "Trend": st.column_config.TextColumn("Trend"),
                        "Improvement": st.column_config.TextColumn("Improvement"),
                        "Current Weight": st.column_config.TextColumn("Current"),
                        "Best Weight": st.column_config.TextColumn("Best"),
                        "Workouts": st.column_config.NumberColumn("Workouts")
                    }
                )
                
                # Plot top 3 improving exercises
                improving_exercises = [e for e, d in trends.items() if 'Increasing' in d['trend']]
                if improving_exercises:
                    st.subheader("🚀 Top Improving Exercises")
                    top_exercises = sorted(
                        [(e, trends[e]['improvement']) for e in improving_exercises],
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                    
                    for exercise, improvement in top_exercises:
                        st.progress(min(improvement / 50, 1.0), text=f"{exercise}: {improvement:.1f}% improvement")
            else:
                st.info("Not enough data to show trends. Keep logging workouts!")
        
        with tab2:
            st.subheader("📈 Training Volume Analysis")
            
            volume_trends = analytics.get_volume_trends()
            if volume_trends and 'data' in volume_trends:
                # Plot weekly volume
                import plotly.express as px
                
                fig = px.line(
                    volume_trends['data'],
                    x='week_label',
                    y='volume',
                    title='Weekly Training Volume Trend',
                    markers=True
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Weekly Volume", f"{volume_trends['current_volume']:.0f}kg")
                with col2:
                    st.metric("Average Weekly Volume", f"{volume_trends['avg_volume']:.0f}kg")
                with col3:
                    st.metric("Trend", volume_trends['trend'])
                
                # Exercise frequency analysis
                st.subheader("📅 Exercise Frequency Patterns")
                freq_data = analytics.get_exercise_frequency()
                
                if freq_data:
                    freq_df = pd.DataFrame([
                        {
                            'Exercise': ex,
                            'Most Common Day': info['most_common_day'],
                            'Frequency': info['frequency']
                        }
                        for ex, info in list(freq_data.items())[:10]
                    ])
                    st.dataframe(freq_df, use_container_width=True, hide_index=True)
            else:
                st.info("Not enough volume data to analyze. Log more workouts!")
        
        with tab3:
            st.subheader("🎯 Estimated 1RM (One Rep Max)")
            st.markdown("Based on the Epley formula: 1RM = Weight × (1 + Reps/30)")
            
            # Get unique exercises
            exercises = list(set(row[1] for row in data))
            selected_exercise = st.selectbox("Select Exercise", exercises)
            
            if selected_exercise:
                rm_data = analytics.get_estimated_1rm(selected_exercise)
                if rm_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Estimated 1RM",
                            f"{rm_data['estimated_1rm']:.1f}kg",
                            delta=f"Based on {rm_data['reps']} reps"
                        )
                    with col2:
                        st.metric(
                            "Actual Weight Used",
                            f"{rm_data['actual_weight']:.1f}kg"
                        )
                    with col3:
                        st.metric(
                            "Date Set",
                            rm_data['date'].strftime("%Y-%m-%d")
                        )
                    
                    # Show 1RM progress chart
                    if len(rm_data['progress']) > 1:
                        progress_df = pd.DataFrame({
                            'Date': rm_data['dates'],
                            'Estimated 1RM': rm_data['progress']
                        })
                        
                        fig = px.line(
                            progress_df,
                            x='Date',
                            y='Estimated 1RM',
                            title=f'1RM Progress - {selected_exercise}',
                            markers=True
                        )
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'white'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for this exercise.")
        
        with tab4:
            st.subheader("📅 Weekly Training Summary")
            
            summary = analytics.get_weekly_summary()
            if summary:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Workouts", summary['total_workouts'])
                with col2:
                    st.metric("Total Volume", f"{summary['total_volume']:.0f}kg")
                with col3:
                    st.metric("Total XP", f"{summary['total_xp']}")
                with col4:
                    st.metric("Unique Exercises", summary['unique_exercises'])
                
                if summary['best_lift'] is not None:
                    st.success(
                        f"🏆 Best Lift This Week: {summary['best_lift']['exercise']} "
                        f"at {summary['best_lift']['weight']:.1f}kg"
                    )
                
                # Show exercises done this week
                st.subheader("📋 Exercises Completed This Week")
                exercises_done = pd.DataFrame({
                    'Exercise': summary['exercises']
                })
                st.dataframe(exercises_done, use_container_width=True, hide_index=True)
                
                # Prediction section
                st.subheader("🎯 Performance Predictions")
                predictions = analytics.get_predictions()
                if predictions:
                    pred_data = []
                    for exercise, pred in predictions.items():
                        pred_data.append({
                            'Exercise': exercise,
                            'Current Weight': f"{pred['current_weight']:.1f}kg",
                            'Predicted Next': f"{pred['predicted_weight']:.1f}kg",
                            'Expected Increase': f"+{pred['improvement']:.1f}kg",
                            'Confidence': f"{pred['confidence']:.0f}%"
                        })
                    
                    pred_df = pd.DataFrame(pred_data)
                    st.dataframe(
                        pred_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Exercise": st.column_config.TextColumn("Exercise"),
                            "Current Weight": st.column_config.TextColumn("Current"),
                            "Predicted Next": st.column_config.TextColumn("Prediction"),
                            "Expected Increase": st.column_config.TextColumn("Increase"),
                            "Confidence": st.column_config.TextColumn("Confidence")
                        }
                    )
                else:
                    st.info("Not enough data for accurate predictions. Log more workouts!")
            else:
                st.info("No data for this week. Start logging workouts!")
    
    else:
        st.info("No workout data available. Start logging your workouts to see analytics!")
    
    conn.close()


elif page == "Goals":

    st.title("🎯 Goals & Targets")
    st.markdown("Set your fitness goals and track your progress!")
    
    # Get current stats for comparison
    cursor.execute("SELECT exercise, MAX(weight) FROM workouts GROUP BY exercise")
    current_prs = {row[0]: row[1] for row in cursor.fetchall()}
    
    # --- Add New Goal Section ---
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px; padding: 25px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
        <h3 style="color: white; margin: 0 0 15px 0;">🎯 Set New Goal</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Get existing exercises for suggestions
        cursor.execute("SELECT DISTINCT exercise FROM workouts WHERE weight > 0 ORDER BY exercise")
        existing_exercises = [row[0] for row in cursor.fetchall()]
        
        if existing_exercises:
            exercise = st.selectbox(
                "🏋️ Select Exercise",
                ["Enter new exercise..."] + existing_exercises,
                key="goal_exercise_select",
                help="Choose an existing exercise or create a new one"
            )
            if exercise == "Enter new exercise...":
                exercise = st.text_input("Type new exercise name", placeholder="e.g., Deadlift, Bench Press...", key="goal_exercise_new")
        else:
            exercise = st.text_input(
                "🏋️ Exercise Name",
                placeholder="e.g., Deadlift, Bench Press...",
                key="goal_exercise",
                help="Enter the exercise you want to set a goal for"
            )
    
    with col2:
        target = st.number_input(
            "🎯 Target Weight (kg)",
            min_value=1.0,
            step=2.5,
            format="%.1f",
            key="goal_target",
            help="What weight do you want to achieve?"
        )
    
    with col3:
        # Show current PR if exists
        if exercise and exercise != "Enter new exercise...":
            current_pr = current_prs.get(exercise, 0)
            if current_pr > 0:
                st.metric(
                    "📊 Current PR",
                    f"{current_pr}kg",
                    delta=f"{target - current_pr:.1f}kg to go" if target > current_pr else "🎯 Target reached!",
                    delta_color="normal" if target > current_pr else "off"
                )
            else:
                st.info("No PR yet for this exercise")
    
    # Add Goal Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Add Goal", use_container_width=True, type="primary", key="add_goal"):
            if not exercise or exercise == "Enter new exercise...":
                st.error("⚠️ Please enter an exercise name")
            elif target <= 0:
                st.error("⚠️ Please enter a valid target weight")
            else:
                cursor.execute(
                    "INSERT INTO goals (exercise, target) VALUES (?, ?)",
                    (exercise, target)
                )
                conn.commit()
                st.success(f"✅ Goal set for {exercise}: {target}kg!")
                st.balloons()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Display Goals Section ---
    st.markdown("---")
    st.subheader("📋 Your Goals")
    
    cursor.execute("SELECT * FROM goals ORDER BY id DESC")
    goals = cursor.fetchall()
    
    if len(goals) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.02); border-radius: 15px; border: 2px dashed rgba(255,255,255,0.1);">
            <div style="font-size: 3rem;">🎯</div>
            <h3 style="color: #9CA3AF;">No Goals Set Yet</h3>
            <p style="color: #6B7280;">Set your first goal above to start tracking your progress!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary stats
        total_goals = len(goals)
        completed_goals = 0
        total_progress = 0
        
        for goal in goals:
            goal_exercise = goal[1]
            target_weight = goal[2]
            current_weight = current_prs.get(goal_exercise, 0)
            if current_weight >= target_weight:
                completed_goals += 1
            progress = min((current_weight / target_weight) * 100, 100) if target_weight > 0 else 0
            total_progress += progress
        
        avg_progress = total_progress / total_goals if total_goals > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(59, 130, 246, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">🎯 Total Goals</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #60A5FA;">{total_goals}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(52, 211, 153, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">✅ Completed</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #34D399;">{completed_goals}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(251, 191, 36, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">📊 Avg Progress</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #FBBF24;">{avg_progress:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(167, 139, 250, 0.2);">
                <div style="font-size: 0.8rem; color: #9CA3AF;">🏆 Success Rate</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #A78BFA;">{(completed_goals/total_goals*100) if total_goals > 0 else 0:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display each goal as a premium card
        for idx, goal in enumerate(goals):
            goal_id = goal[0]
            exercise = goal[1]
            target = goal[2]
            
            # Get current progress
            current = current_prs.get(exercise, 0)
            progress = min((current / target) * 100, 100) if target > 0 else 0
            is_completed = current >= target
            
            # Determine status
            if is_completed:
                status_emoji = "✅"
                status_text = "Completed!"
                status_color = "#34D399"
                border_color = "rgba(52, 211, 153, 0.3)"
            elif progress > 0:
                status_emoji = "🔄"
                status_text = f"{progress:.0f}% Complete"
                status_color = "#60A5FA"
                border_color = "rgba(59, 130, 246, 0.3)"
            else:
                status_emoji = "⏳"
                status_text = "Not Started"
                status_color = "#9CA3AF"
                border_color = "rgba(255,255,255,0.05)"
            
            # Calculate remaining
            remaining = target - current if current < target else 0
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; padding: 20px; margin: 12px 0; border: 1px solid {border_color}; transition: all 0.3s ease;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="font-size: 2rem;">{status_emoji}</div>
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: white;">{exercise}</div>
                            <div style="font-size: 0.9rem; color: #9CA3AF;">🎯 Target: {target}kg</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                        <div style="text-align: center;">
                            <div style="font-size: 0.7rem; color: #9CA3AF;">Current PR</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #F59E0B;">{current}kg</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 0.7rem; color: #9CA3AF;">Remaining</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #60A5FA;">{remaining:.1f}kg</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 5px 15px; border-radius: 20px; border: 1px solid {status_color}33;">
                            <span style="color: {status_color}; font-weight: bold; font-size: 0.9rem;">{status_text}</span>
                        </div>
                    </div>
                </div>
                <!-- Progress bar -->
                <div style="margin-top: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #6B7280;">
                        <span>Progress</span>
                        <span>{progress:.0f}%</span>
                    </div>
                    <div style="background: #2d2d44; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: {'linear-gradient(90deg, #34D399, #10B981)' if is_completed else 'linear-gradient(90deg, #2563eb, #7c3aed)'}; width: {progress}%; height: 100%; transition: width 1s ease;"></div>
                    </div>
                </div>
                <!-- Quick action buttons -->
                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px;">
                    <button onclick="window.location.reload()" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); color: #60A5FA; padding: 5px 15px; border-radius: 8px; cursor: pointer; font-size: 0.8rem;">
                        📊 Track Progress
                    </button>
            """, unsafe_allow_html=True)
            
            # Delete button with confirmation
            if st.button(f"🗑 Delete Goal", key=f"delete_goal_{goal_id}"):
                cursor.execute("DELETE FROM goals WHERE id=?", (goal_id,))
                conn.commit()
                st.success(f"🗑 Goal for {exercise} deleted!")
                st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Motivational message based on progress
        st.markdown("---")
        if completed_goals == total_goals and total_goals > 0:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #34D39922, #10B98122); border-radius: 15px; padding: 20px; text-align: center; border: 2px solid #34D399;">
                <div style="font-size: 2rem;">🏆</div>
                <h3 style="color: #34D399;">🎉 All Goals Completed!</h3>
                <p style="color: #9CA3AF;">Amazing work! Time to set new, bigger goals!</p>
            </div>
            """, unsafe_allow_html=True)
        elif avg_progress > 50:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F59E0B22, #FBBF2422); border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #F59E0B;">
                <div style="font-size: 2rem;">💪</div>
                <h3 style="color: #FBBF24;">Keep Going! {avg_progress:.0f}% Complete</h3>
                <p style="color: #9CA3AF;">You're making great progress toward your goals!</p>
            </div>
            """, unsafe_allow_html=True)
        elif total_goals > 0:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #2563eb22, #7c3aed22); border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #2563eb;">
                <div style="font-size: 2rem;">🚀</div>
                <h3 style="color: #60A5FA;">Start Your Journey!</h3>
                <p style="color: #9CA3AF;">Every workout brings you closer to your goals. Stay consistent!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # --- Quick Stats Section ---
    st.markdown("---")
    with st.expander("📊 Goal Achievement Tips", expanded=False):
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 20px;">
            <h4 style="color: white;">💡 Tips for Reaching Your Goals</h4>
            <ul style="color: #9CA3AF; line-height: 1.8;">
                <li>📅 <strong>Be Consistent:</strong> Train regularly to build strength progressively</li>
                <li>📈 <strong>Track Progress:</strong> Log every workout to see your improvement</li>
                <li>🎯 <strong>Set SMART Goals:</strong> Make them Specific, Measurable, Achievable, Relevant, and Time-bound</li>
                <li>💪 <strong>Progressive Overload:</strong> Gradually increase weight or reps each week</li>
                <li>🔄 <strong>Vary Your Routine:</strong> Change exercises every 4-6 weeks to avoid plateaus</li>
                <li>🥗 <strong>Nutrition & Recovery:</strong> Proper diet and rest are essential for progress</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- Achievement Unlock Section ---
    if goals:
        st.markdown("---")
        st.subheader("🏅 Goal Achievements")
        
        achievement_cols = st.columns(3)
        achievements = []
        
        # Check for achievement unlocks
        if completed_goals >= 1:
            achievements.append(("🎯 First Goal Complete", "You completed your first goal!", "#34D399"))
        if completed_goals >= 3:
            achievements.append(("🏆 Goal Hunter", "You completed 3 goals!", "#60A5FA"))
        if completed_goals >= 5:
            achievements.append(("💪 Goal Master", "You completed 5 goals!", "#A78BFA"))
        if completed_goals == total_goals and total_goals >= 3:
            achievements.append(("👑 Goal Champion", "You completed all your goals!", "#FBBF24"))
        
        if achievements:
            for idx, (title, desc, color) in enumerate(achievements[:3]):
                with achievement_cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {color}22, {color}11); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid {color}33;">
                        <div style="font-size: 2.5rem;">{title.split()[0]}</div>
                        <div style="font-weight: bold; color: {color};">{title}</div>
                        <div style="font-size: 0.8rem; color: #9CA3AF;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💪 Complete your first goal to unlock achievements!")


elif page == "AI Coach":
    st.title("🤖 AI Coach")
    st.markdown("Get personalized workout recommendations based on your training history")
    
    if len(data) > 0:
        from utils.workout_recommender import WorkoutRecommender
        recommender = WorkoutRecommender(data)
        
        # Stats summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_exercises = len(set(row[1] for row in data))
            st.metric("🏋️ Total Exercises", total_exercises)
        with col2:
            st.metric("📊 Total Workouts", len(data))
        with col3:
            today = datetime.today().date()
            recent = sum(1 for row in data if (today - datetime.strptime(row[8], "%Y-%m-%d").date()).days <= 7)
            st.metric("📅 Workouts (7 Days)", recent)
        with col4:
            from utils.muscle_mapper import get_muscle_group
            unique_muscles = len(set(get_muscle_group(row[1]) for row in data))
            st.metric("💪 Muscles Trained", unique_muscles)
        
        st.markdown("---")
        
        # Three main recommendation sections
        tab1, tab2, tab3 = st.tabs(["💡 Exercise Suggestions", "📈 Progressive Overload", "📊 Volume Analysis"])
        
        with tab1:
            st.subheader("💡 Smart Exercise Suggestions")
            exercise_suggestions = recommender.suggest_exercises(num_suggestions=5)
            
            if exercise_suggestions:
                for suggestion in exercise_suggestions:
                    priority_color = "🔴" if suggestion['priority'] > 0.8 else "🟡" if suggestion['priority'] > 0.5 else "🟢"
                    st.markdown(f"""
                    <div style="background:#1E1E1E; padding:15px; border-radius:10px; border-left: 4px solid #2563eb; margin:10px 0;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0; color:#60A5FA;">{suggestion['exercise']}</h4>
                                <p style="margin:5px 0 0 0; color:#9CA3AF;">{suggestion['reason']}</p>
                            </div>
                            <div style="font-size:1.5rem;">{priority_color}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ You're doing great! No exercise suggestions at this time.")
        
        with tab2:
            st.subheader("📈 Progressive Overload Opportunities")
            overload_suggestions = recommender.get_progressive_overload_suggestion()
            
            if overload_suggestions:
                for suggestion in overload_suggestions:
                    st.markdown(f"""
                    <div style="background:#1E1E1E; padding:15px; border-radius:10px; border-left: 4px solid #10B981; margin:10px 0;">
                        <h4 style="margin:0; color:#34D399;">{suggestion['exercise']}</h4>
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
        
        with tab3:
            st.subheader("📊 Training Volume Analysis")
            volume_suggestion = recommender.get_volume_suggestion()
            if volume_suggestion:
                st.info(volume_suggestion['message'])
            else:
                st.info("Keep logging workouts for volume analysis!")
    else:
        st.info("No workout data available. Start logging your workouts to get AI coaching!")

elif page == "Gamification":
    st.title("🏆 Gamification Hub")
    st.markdown("Track your progress, complete challenges, and unlock achievements!")
    
    if len(data) > 0:
        from utils.gamification import GamificationSystem
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
            for challenge in challenges:
                status = "✅ Completed!" if challenge['completed'] else f"{challenge['progress']*100:.0f}%"
                status_color = "#10B981" if challenge['completed'] else "#3B82F6"
                
                st.markdown(f"""
                <div style="background:#1E1E1E; padding:15px; border-radius:10px; margin:10px 0; border: 2px solid {'#10B981' if challenge['completed'] else '#374151'};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:{'#10B981' if challenge['completed'] else '#F59E0B'};">{challenge['name']}</h4>
                        <span style="background:{status_color}22; padding:5px 10px; border-radius:20px; color:{status_color}; font-size:0.8rem;">{status}</span>
                    </div>
                    <p style="color:#9CA3AF; margin-top:10px;">{challenge['description']}</p>
                    <div style="margin:10px 0;">
                        <div style="background:#374151; height:8px; border-radius:4px; overflow:hidden;">
                            <div style="background:{status_color}; width:{challenge['progress']*100}%; height:100%;"></div>
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
        
        st.progress(achievement_stats["progress_percentage"] / 100)
        
        if achievement_stats["unlocked"]:
            st.markdown("### 🎖️ Unlocked Achievements")
            cols = st.columns(4)
            for idx, achievement in enumerate(achievement_stats["unlocked"][:8]):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background:#1E1E1E; padding:15px; border-radius:10px; text-align:center; border: 1px solid #10B981;">
                        <div style="font-size:3rem;">{achievement['emoji']}</div>
                        <div style="color:white; font-weight:bold; margin-top:5px;">{achievement['name']}</div>
                        <div style="color:#10B981; font-size:0.8rem;">✅ Unlocked</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No achievements unlocked yet. Start your fitness journey!")
        
        # Share Section
        st.markdown("---")
        st.subheader("📱 Share Your Progress")
        social_stats = gamification.get_social_stats()
        
        if st.button("📤 Generate Share Text", use_container_width=True):
            st.code(social_stats['share_text'], language='text')
            st.success("✅ Copy this text and share with your friends!")
    else:
        st.info("No workout data available. Start logging your workouts to unlock gamification features!")

# -----------------------------
# Close DB
# -----------------------------

conn.close()