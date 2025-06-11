import streamlit as st
from Backend.granite_client import get_feedback_from_granite as query_granite  # AI feedback

def quests_page(user):
    st.title("🗡️ Quests")

    # Example quests (can be dynamically fetched from DB or API later)
    quests = [
        {"title": "Complete Lesson 1", "xp": 50, "completed": True},
        {"title": "Score 80% on Quiz 1", "xp": 100, "completed": False},
        {"title": "Participate in Discussion", "xp": 30, "completed": False},
        {"title": "Submit Project Proposal", "xp": 150, "completed": False},
    ]

    completed_xp = sum(q["xp"] for q in quests if q["completed"])
    total_xp = sum(q["xp"] for q in quests)
    progress = completed_xp / total_xp if total_xp else 0

    st.markdown(f"### Progress: {completed_xp} / {total_xp} XP")
    st.progress(progress)
    st.markdown("---")

    for quest in quests:
        if quest["completed"]:
            st.success(f"✅ {quest['title']} (+{quest['xp']} XP)")
        else:
            if st.button(f"Start Quest: {quest['title']}"):
                st.info(f"🚀 Starting quest: {quest['title']}")

                # 🔮 Generate user input prompt
                user_input = f"User '{user.get('email', 'unknown')}' is starting the quest: {quest['title']}. Give feedback on their learning attempt."
                
                # 🧠 Call Granite model for feedback
                feedback = query_granite(user_input)

                st.markdown("### 🤖 AI Feedback")
                st.success(feedback)

            st.write(f"🎯 Reward: {quest['xp']} XP")

    st.markdown("---")
    st.info("Complete quests to earn XP, level up, and unlock badges!")
