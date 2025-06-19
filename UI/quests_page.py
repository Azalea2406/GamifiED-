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
    if st.button("🎯 Generate New Quests"):
        with st.spinner("Contacting Granite AI..."):
            prompt = (
                f"You are an educational game designer. Create 3 engaging quest titles "
                f"for a student learning '{assigned_course}'. Just list them like:\n"
                f"1. <Quest Title>\n2. <Quest Title>\n3. <Quest Title>"
            )
            result = query_granite(prompt)
            if isinstance(result, list):
                # Clean result: extract numbered titles
                lines = result[0]["generated_text"].split("\n")
                new_quests = []
                for line in lines:
                    if line.strip().startswith(tuple("123")):
                        # Extract after number and period
                        quest = line.split(".", 1)[-1].strip()
                        if quest:
                            new_quests.append(quest)
                if new_quests:
                    st.session_state.generated_quests = new_quests
                    st.success("✅ Quests generated!")
                else:
                    st.warning("Granite response received but no quests were extracted.")
            else:
                st.error("Failed to get quest ideas from Granite.")

    quests = st.session_state.get("generated_quests", [])

    # 📊 Show progress
    completed_quests = [q for q in existing_quests]
    st.markdown(f"**Progress:** {len(completed_quests)} / {len(quests)} quests completed")
    if quests:
        st.progress(len(completed_quests) / len(quests))

    st.markdown("---")

    for i, quest in enumerate(quests):
        completed = quest in existing_quests
        with st.expander(f"📝 {quest} {'✅' if completed else ''}"):
            if completed:
                st.success("Quest already completed.")
                st.markdown(f"**🧠 Feedback:** {existing_quests[quest]['feedback']}")
                st.markdown(f"🕒 Completed on: {existing_quests[quest]['completed_at']}")
                continue

            user_input = st.text_area(f"✍️ Submit your response for: '{quest}'", key=f"input_{i}")
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
    st.info("🎮 Earn XP by completing AI-generated learning quests based on your course!")
