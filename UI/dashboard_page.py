import streamlit as st
from firebase_config import db
from Quiz.quiz_engine import take_quiz
from Quiz.quiz_data import QUIZ_QUESTIONS
from Learning.course_data import COURSES
import pandas as pd
import altair as alt
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

def inject_neon_css():
    st.markdown("""
    <style>
    /* Neon progress bar container */
    div[data-testid="stProgress"] > div > div {
        background: #111 !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px #00ffff, 0 0 30px #00ffff !important;
        height: 25px !important;
    }
    /* Neon progress fill */
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #00ffff, #00ccff) !important;
        box-shadow: 0 0 15px #00ffff, 0 0 20px #00ccff !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ✅ Set Gaming Background Theme
def set_gaming_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://static.vecteezy.com/system/resources/previews/022/370/881/non_2x/modern-dark-flow-blue-purple-and-pink-light-on-black-abstract-background-popular-dynamic-background-eps10-vector.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def set_gaming_fonts():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Rajdhani:wght@400&family=Roboto&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #E0E0E0 !important;
        text-shadow: 1px 1px 3px #000000;
    }

    p, div, span, label {
        font-family: 'Roboto', sans-serif !important;
        color: #F2F2F2 !important;
    }

    .stButton>button, .stRadio label, .stSelectbox label, .stTextInput>div>div>input {
        font-family: 'Rajdhani', sans-serif !important;
        color: #FFFFFF !important;
    }

    .icon { font-size: 20px; margin-right: 8px; }
    .icon-purple { color: #A29BFE; }
    .icon-pink { color: #FF6B81; }
    .icon-cyan { color: #00FFFF; }

    </style>
    """, unsafe_allow_html=True)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def get_badge(xp):
    if xp >= 300:
        return "🥇 Master"
    elif xp >= 200:
        return "🥈 Expert"
    elif xp >= 100:
        return "🥉 Intermediate"
    else:
        return "🎓 Beginner"

def get_user_xp(user_id):
    progress = db.child("progress").child(user_id).get().val()
    total_xp = 0
    if progress:
        for course in progress.values():
            for level in course.values():
                total_xp += level.get("xp", 0)
    return total_xp

def get_xp_over_time(user_id):
    progress = db.child("progress").child(user_id).get().val()
    data = []

    if progress:
        for course, levels in progress.items():
            for level, details in levels.items():
                timestamp = details.get("timestamp") or "1970-01-01T00:00:00"
                xp = details.get("xp", 0)
                data.append({"Date": timestamp, "XP": xp, "Level": level})

    return pd.DataFrame(data)

def get_assigned_course(user_id):
    data = db.child("assignments").child(user_id).get().val()
    if data and isinstance(data, dict):
        return data.get("course")
    return None

def has_completed_level(user_id, course, level_index):
    path = f"progress/{user_id}/{course}/level_{level_index}"
    return db.child(path).get().val() is not None

def learner_dashboard(user):
    set_gaming_background()
    set_gaming_fonts()
    inject_neon_css()
    st.title("🎓 Learner Dashboard")

    user_id = user.get("user_id") or user.get("localId") or st.session_state.get("user", {}).get("uid")
    username = user.get("username") or user.get("email") or "Learner"

    if not user_id:
        st.error("User ID not found. Please log in again.")
        return

    assigned_course = get_assigned_course(user_id)
    if not assigned_course:
        st.warning("No course assigned yet. Please wait for your instructor to assign one.")
        return

    st.subheader(f"📚 Assigned Course: {assigned_course}")

    total_xp = get_user_xp(user_id)
    st.success(f"🌟 Total XP: {total_xp}")

    # ✅ Display Badge
    badge = get_badge(total_xp)
    st.info(f"🏅 Your Badge: **{badge}**")

    # ✅ XP Over Time Chart
    xp_df = get_xp_over_time(user_id)
    st.write("📊 XP Raw Data (debug):", xp_df)

    if not xp_df.empty:
        st.markdown("### 📈 XP Progress Over Time")

        xp_df["Date"] = pd.to_datetime(xp_df["Date"], errors="coerce")
        xp_df = xp_df.dropna(subset=["Date"])
        xp_df = xp_df.sort_values("Date")

        if len(xp_df) > 1:
            chart = alt.Chart(xp_df).mark_line(
                point=alt.OverlayMarkDef(color="#00FFFF", size=50),
                color="#00FFFF",
                strokeWidth=2
            ).encode(
                x=alt.X("Date:T", axis=alt.Axis(labelColor="#E0FFFF", titleColor="#E0FFFF")),
                y=alt.Y("XP:Q", axis=alt.Axis(labelColor="#E0FFFF", titleColor="#E0FFFF")),
                tooltip=["Level", "XP", "Date"]
            ).properties(width=800, height=400, background="#111").configure_axis(grid=True)

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Not enough data points to plot a meaningful chart.")
    else:
        st.warning("No XP data available to display.")

    st.markdown("---")
    st.subheader("📈 Progress & Quizzes")

    course = COURSES.get(assigned_course)
    if not course:
        st.error("Course data not found.")
        return

    for idx, level in enumerate(course["levels"]):
        level_name = level["name"]
        completed = has_completed_level(user_id, assigned_course, idx)

        with st.expander(f"Level {idx + 1}: {level_name} {'✅' if completed else ''}"):
            st.markdown("""
            <div style='padding: 10px; border-radius: 15px; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); margin-bottom: 15px;'>
            """, unsafe_allow_html=True)

            required_xp = level.get("xp_required", 100)
            current_xp = 100 if completed else 0
            st.markdown(f"**XP Progress:** {current_xp} / {required_xp}")
            st.progress(min(current_xp / required_xp, 1.0))

            if completed:
                st.info("Level already completed.")
                st.markdown("</div>", unsafe_allow_html=True)
                continue

            questions = QUIZ_QUESTIONS.get(assigned_course, {}).get(level_name, [])
            if not questions:
                st.warning("No questions found for this level.")
                st.markdown("</div>", unsafe_allow_html=True)
                continue

            st.markdown("### 📝 Quiz Questions")
            answers = []
            all_answered = True

            for q_index, q in enumerate(questions):
                ans = st.radio(
                    f"{q_index + 1}. {q['question']}",
                    options=q['options'],
                    key=f"{level_name}_{q_index}"
                )
                answers.append(ans)
                if not ans:
                    all_answered = False

            if st.button(f"🚀 Submit Quiz - {level_name}", key=f"submit_{level_name}"):
                if not all_answered:
                    st.warning("⛔ Please answer all questions before submitting.")
                else:
                    with st.spinner("Submitting your quiz..."):
                        result = take_quiz(user_id, assigned_course, level_name, answers)
                        st.success("✅ Quiz Submitted!")
                        st.markdown(f"🎯 **Score:** `{result['score']}%`")
                        st.markdown(f"🏆 **XP Earned:** `{result['xp_result']['xp']}`")

                        lottie_confetti = load_lottieurl("https://lottie.host/60f5cb9c-56c0-4a6d-8ea1-53d312a2c213/VkhvxEiBBk.json")
                        if lottie_confetti:
                            st_lottie(lottie_confetti, height=200, key=f"confetti_{idx}")

                        st.markdown("### 📋 Feedback per Question")
                        for i, fb in enumerate(result["feedback"]):
                            st.markdown(f"**{i+1}. {fb['question']}**")
                            if fb["is_correct"]:
                                st.markdown(f":green[- Your Answer: {fb['your_answer']}] ✅ Correct")
                            else:
                                st.markdown(f":red[- Your Answer: {fb['your_answer']}] ❌ Incorrect")
                                st.markdown(f":green[- Correct Answer: {fb['correct_answer']}]")
                            st.divider()

            st.markdown("</div>", unsafe_allow_html=True)
