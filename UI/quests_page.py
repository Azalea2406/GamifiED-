import streamlit as st
from firebase_config import db
from Backend.granite_utils import query_granite
from Backend.granite_client import get_feedback_from_granite
from datetime import datetime

# 🔧 Config
XP_PER_QUEST = 50  # Default XP per completed quest

def get_user_id(user):
    return (
        user.get("user_id")
        or user.get("localId")
        or user.get("uid")
        or st.session_state.get("user", {}).get("uid")
    )

def get_assigned_course(user_id):
    assignment = db.child("assignments").child(user_id).get().val()
    return assignment.get("course") if assignment else None

def get_user_quests(user_id):
    return db.child("progress").child("quests").child(user_id).get().val() or {}

def save_quest_completion(user_id, quest_title, user_input, feedback):
    db.child("progress").child("quests").child(user_id).child(quest_title).set({
        "input": user_input,
        "feedback": feedback,
        "completed_at": datetime.now().isoformat(),
        "xp": XP_PER_QUEST
    })

def quests_page(user):
    st.title("🗡️ AI-Powered Quests")
    user_id = get_user_id(user)

    if not user_id:
        st.error("User ID not found.")
        return

    assigned_course = get_assigned_course(user_id)
    if not assigned_course:
        st.warning("⚠️ No course assigned yet.")
        return

    st.markdown(f"📘 **Learning Track:** `{assigned_course}`")
    existing_quests = get_user_quests(user_id)

    # 🎯 Generate quests button
    if st.button("🎯 Generate New Quests"):
        with st.spinner("Contacting Granite AI..."):
            prompt = (
                f"Create 3 engaging quests for a student learning '{assigned_course}'. "
                "Use simple language. Format each like: 1. <Quest Title>"
            )
            result = query_granite(prompt)
            if isinstance(result, list):
                lines = result[0]["generated_text"].split("\n")
                new_quests = [line.strip("1234567890. ").strip() for line in lines if line.strip()]
                st.session_state.generated_quests = new_quests[:3]
                st.success("✅ Quests generated!")
            else:
                st.error("Failed to get quest ideas from Granite.")

    quests = st.session_state.get("generated_quests", [])
    completed_quests = list(existing_quests.keys())

    # 📊 Progress tracker
    if quests:
        st.markdown(f"**Progress:** `{len(completed_quests)} / {len(quests)}` quests completed")
        st.progress(len(completed_quests) / len(quests))

    st.markdown("---")

    # 📝 Display each quest with completion/feedback logic
    for quest in quests:
        completed = quest in existing_quests
        with st.expander(f"📝 {quest} {'✅' if completed else ''}"):
            if completed:
                st.success("Quest already completed.")
                st.markdown(f"**🧠 Feedback:** {existing_quests[quest]['feedback']}")
                st.markdown(f"🕒 Submitted on: `{existing_quests[quest]['completed_at']}`")
            else:
                user_input = st.text_area("✍️ Your Submission:", key=f"input_{quest}")
                if st.button(f"🚀 Submit: {quest}", key=f"submit_{quest}"):
                    if not user_input.strip():
                        st.warning("Please enter your work before submitting.")
                    else:
                        with st.spinner("Getting AI feedback..."):
                            feedback = get_feedback_from_granite(user_input)
                            save_quest_completion(user_id, quest, user_input, feedback)
                            st.success("✅ Quest submitted! XP awarded.")
                            st.markdown(f"**🧠 Granite Feedback:** {feedback}")
                            st.rerun()

    st.markdown("---")
    st.info("🎮 Complete quests to earn XP and level up!")
