import streamlit as st
from firebase_config import db
from Backend.granite_utils import query_granite
from Backend.granite_client import get_feedback_from_granite
from datetime import datetime

# 🔧 Config
XP_PER_QUEST = 50  # Default XP per completed quest

def get_assigned_course(user_id):
    assignment = db.child("assignments").child(user_id).get().val()
    return assignment.get("course") if assignment else None

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
    user_id = user.get("user_id") or user.get("localId") or st.session_state.get("user", {}).get("uid")
    if not user_id:
        st.error("User ID not found.")
        return

    assigned_course = get_assigned_course(user_id)
    if not assigned_course:
        st.warning("No course assigned.")
        return

    st.markdown(f"📘 **Course Context:** {assigned_course}")
    existing_quests = get_user_quests(user_id)

    # ✅ Generate quests from Granite if not already done
    if st.button("🎯 Generate Quests"):
        with st.spinner("Generating quests from Granite..."):
            prompt = f"Create 3 engaging quests for a student learning '{assigned_course}'. Use simple language. Format each like: 1. <Quest Title>"
            result = query_granite(prompt)
            if isinstance(result, list):
                lines = result[0]["generated_text"].split("\n")
                new_quests = [line.strip("0123456789. ").strip() for line in lines if line.strip()]
                st.session_state.generated_quests = new_quests[:3]
                st.success("Quests generated!")
            else:
                st.error("Failed to generate quests from Granite.")

    quests = st.session_state.get("generated_quests", [])

    # 📊 Show progress
    completed_quests = [q for q in existing_quests]
    st.markdown(f"**Progress:** {len(completed_quests)} / {len(quests)} quests completed")
    if quests:
        st.progress(len(completed_quests) / len(quests))

    st.markdown("---")

    for quest in quests:
        completed = quest in existing_quests
        with st.expander(f"📝 {quest} {'✅' if completed else ''}"):
            if completed:
                st.success("Quest already completed.")
                st.markdown(f"**🧠 Feedback:** {existing_quests[quest]['feedback']}")
                st.markdown(f"🕒 Completed on: {existing_quests[quest]['completed_at']}")
                continue

            user_input = st.text_area(f"✍️ Submit your response for: '{quest}'", key=f"input_{quest}")
            if st.button(f"🚀 Submit Quest: {quest}", key=f"submit_{quest}"):
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
    st.info("🎮 Earn XP by completing AI-generated learning quests based on your course!")
