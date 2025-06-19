import streamlit as st
from firebase_config import db
from Backend.granite_client import get_feedback_from_granite
from datetime import datetime

# 🔧 Config
XP_PER_QUEST = 50  # Default XP per completed quest

# Static quests
STATIC_QUESTS = [
    "Complete your course introduction activity",
    "Write a summary of the first module",
    "Explain a concept from the course in your own words"
]

def get_user_id(user):
    return user.get("user_id") or user.get("localId") or st.session_state.get("user", {}).get("uid")

def get_user_quests(user_id):
    return db.child("progress").child("quests").child(user_id).get().val() or {}

def save_quest_completion(user_id, quest_title, user_input, feedback):
    path = f"progress/quests/{user_id}/{quest_title}"
    db.child(path).set({
        "input": user_input,
        "feedback": feedback,
        "completed_at": datetime.now().isoformat(),
        "xp": XP_PER_QUEST
    })

def quests_page(user):
    st.title("🗡️ Quests")
    user_id = get_user_id(user)
    if not user_id:
        st.error("User ID not found.")
        return

    existing_quests = get_user_quests(user_id)
    completed_quests = [q for q in existing_quests]

    st.markdown(f"**Progress:** {len(completed_quests)} / {len(STATIC_QUESTS)} quests completed")
    st.progress(len(completed_quests) / len(STATIC_QUESTS))
    st.markdown("---")

    for i, quest in enumerate(STATIC_QUESTS):
        completed = quest in existing_quests
        with st.expander(f"📝 {quest} {'✅' if completed else ''}"):
            if completed:
                st.success("Quest already completed.")
                st.markdown(f"**🧠 Feedback:** {existing_quests[quest]['feedback']}")
                st.markdown(f"🕒 Completed on: {existing_quests[quest]['completed_at']}")
                continue

            user_input = st.text_area(f"✍️ Submit your response", key=f"input_{i}")
            if st.button(f"🚀 Submit Quest: {quest}", key=f"submit_{i}"):
                if not user_input.strip():
                    st.warning("Please enter your work before submitting.")
                else:
                    with st.spinner("Getting feedback from Granite..."):
                        feedback = get_feedback_from_granite(user_input)
                        save_quest_completion(user_id, quest, user_input, feedback)
                        st.success("✅ Quest submitted and XP awarded!")
                        st.markdown(f"**🧠 AI Feedback:** {feedback}")
                        st.rerun()

    st.markdown("---")
    st.info("🎮 Earn XP by completing learning quests and get AI-powered feedback!")
