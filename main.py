import streamlit as st
from Authentication.login_page import login_page
from UI.dashboard_page import learner_dashboard, get_user_xp, get_badge
from UI.instructor_page import instructor_dashboard
from UI.quests_page import quests_page
from UI.profile_page import profile_page
from Backend.granite_client import get_feedback_from_granite as query_granite
import os
import requests

HUGGINGFACE_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Missing Hugging Face API token in environment variables!")

API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.3-2b-instruct"
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
}

def query_granite(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


# Custom CSS for game look & feel
def inject_game_css():
    st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #53354a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e0e0e0;
    }

    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px #00ffff;
        color: #00ffff;
    }

    p, div, span, label {
        font-family: 'Rajdhani', sans-serif !important;
        color: #c0c0c0;
    }

    [data-testid="stSidebar"] {
        background-color: #0f3460;
        color: #00ffff;
        border-right: 3px solid #00ffff;
        font-family: 'Rajdhani', sans-serif !important;
    }

    .css-1d391kg h2 {
        color: #00ffff !important;
        text-align: center;
        margin-bottom: 20px;
    }

    button[kind="primary"] {
        background-color: #00ffff !important;
        color: #0f3460 !important;
        font-weight: 700;
        border-radius: 12px !important;
        box-shadow: 0 0 10px #00ffff;
        transition: 0.3s;
    }
    button[kind="primary"]:hover {
        background-color: #00c2c2 !important;
        box-shadow: 0 0 20px #00ffff;
    }

    div[role="progressbar"] > div {
        background: linear-gradient(90deg, #00ffff, #00c2c2);
        box-shadow: 0 0 10px #00ffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with HUD info
def sidebar_hud(user):
    st.sidebar.title("🎮 GamifiED HUD")
    st.sidebar.markdown(f"👤 User: **{user.get('email')}**")
    st.sidebar.markdown(f"🧑‍💼 Role: **{user.get('role')}**")

    user_id = user.get("user_id") or user.get("localId") or user.get("uid") or st.session_state.get("user", {}).get("uid")
    if user_id:
        total_xp = get_user_xp(user_id)
        badge = get_badge(total_xp)
        st.sidebar.markdown(f"🌟 XP: **{total_xp}**")
        st.sidebar.markdown(f"🏅 Badge: **{badge}**")

    st.sidebar.markdown("---")
    return st.sidebar.radio("📋 Navigation", ["Dashboard", "Quests", "Leaderboard", "Profile", "Logout"])

# Main app
def main():
    st.set_page_config(page_title="GamifiED", layout="wide")
    inject_game_css()

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = {}

    if not st.session_state["authenticated"]:
        login_page()
        return

    user = st.session_state.user
    role = user.get("role", "")
    choice = sidebar_hud(user)

    if choice == "Logout":
        st.session_state["authenticated"] = False
        st.session_state["user"] = {}
        st.rerun()

    # Role-based page routing + menu selection
    if role == "Learner":
        if choice == "Dashboard":
            learner_dashboard(user)
        elif choice == "Quests":
            quests_page(user)
        elif choice == "Leaderboard":
            st.info("🏆 Leaderboard coming soon!")
        elif choice == "Profile":
            profile_page(user)

    elif role == "Instructor":
        if choice in ["Dashboard", "Leaderboard"]:  # reuse instructor_dashboard for now
            instructor_dashboard()
        elif choice == "Profile":
            st.info("🧑‍🏫 Instructor profile coming soon!")

    else:
        st.error("⚠️ Unknown role detected.")

if __name__ == "__main__":
    main()

