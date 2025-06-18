import streamlit as st
from firebase_config import db
from Backend.granite_client import get_feedback_from_granite as query_granite
import random

def get_assigned_course(user_id):
    data = db.child("assignments").child(user_id).get().val()
    if data and isinstance(data, dict):
        return data.get("course")
    return None

def generate_quests(course):
    prompt = f"Generate 4 gamified learning quests for the course '{course}'. Each quest should have a short title and XP value. Format it as a list of dictionaries with 'title' and 'xp'."
    result = query_granite(prompt)

    # Fallback static quests if Granite fails
    if not isinstance(result, list):
        return [
            {"title": "Complete Lesson 1", "xp": 50},
            {"title": "Score 80% on Quiz 1", "xp": 100},
            {"title": "Participate in Discussion", "xp": 30},
            {"title": "Submit Project Proposal", "xp": 150},
        ]

    try:
        import ast
        quests = ast.literal_eval(result[0]["generated_text"])
        return quests if isinstance(quests, list) else []
    except Exception:
        return []

def quests_page(user):
    st.title("🗡️ Quests")

    user_id = user.get("user_id") or user.get("localId") or user.get("uid")
    assigned_course = get_assigned_course(user_id)

    if not assigned_course:
        st.warning("No course assigned. Please ask your instructor to assign a course.")
        return

    st.markdown(f"📚 Assigned Course: **{assigned_course}**")

    # Generate quests via AI
    with st.spinner("🧠 Generating quests..."):
        quests = generate_quests(assigned_course)

    # Display progress
    completed_keys = [f"quest_{i}_completed" for i in range(len(quests)) if st.session_state.get(f"quest_{i}_completed")]
    completed_xp = sum(quests[i]["xp"] for i in range(len(quests)) if f"quest_{i}_completed" in st.session_state)
    total_xp = sum(q["xp"] for q in quests)

    st.markdown(f"### Progress: {completed_xp} / {total_xp} XP")
    st.progress(completed_xp / total_xp if total_xp else 0.0)
    st.markdown("---")

    for i, quest in enumerate(quests):
        key = f"quest_{i}_completed"
        if st.session_state.get(key):
            st.success(f"✅ {quest['title']} (+{quest['xp']} XP)")
        else:
            if st.button(f"🚀 Start Quest: {quest['title']}", key=f"start_{i}"):
                st.info(f"🔄 Quest Started: {quest['title']}")
                st.session_state[key] = True  # Mark as completed

                with st.spinner("Generating feedback..."):
                    user_input = f"A learner completed the quest: '{quest['title']}' in the course '{assigned_course}'. Provide motivational feedback."
                    feedback = query_granite(user_input)

                st.markdown("### 🤖 AI Feedback")
                if isinstance(feedback, list):
                    st.success(feedback[0]["generated_text"])
                else:
                    st.warning("Could not fetch feedback from Granite.")

            st.write(f"🎯 Reward: {quest['xp']} XP")

    st.markdown("---")
    st.info("Complete quests to earn XP, level up, and unlock badges!")
