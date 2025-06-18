import streamlit as st
from datetime import datetime
from firebase_config import db
from Backend.granite_client import get_feedback_from_granite as query_granite

# -- Get assigned course from Firebase
def get_assigned_course(user_id):
    assignment = db.child("assignments").child(user_id).get().val()
    return assignment.get("course") if assignment else None

# -- Load AI-based quests (generate from Granite or hardcoded fallback)
def generate_ai_quests(course_name):
    try:
        prompt = f"Generate 3 short learning quests with titles and XP for a student in the course: {course_name}"
        response = query_granite(prompt)

        if isinstance(response, list):
            raw = response[0]["generated_text"]
            quests = []
            for line in raw.strip().split("\n"):
                if line.strip():
                    # Expecting format: "1. Do XYZ (XP: 50)"
                    title = line.split("(XP")[0].split(".", 1)[-1].strip()
                    xp = int(line.split("XP:")[-1].split(")")[0].strip())
                    quests.append({"title": title, "xp": xp})
            return quests
    except:
        pass  # Fallback below

    # Fallback static list
    return [
        {"title": "Watch Lesson 1 and summarize", "xp": 50},
        {"title": "Write key takeaways from Topic 2", "xp": 70},
        {"title": "Submit 3 doubts or questions", "xp": 30}
    ]

# -- Get quest progress from Firebase
def get_quest_progress(user_id):
    path = f"progress/quests/{user_id}"
    data = db.child(path).get().val()
    return data if data else {}

# -- Save quest submission
def save_quest_submission(user_id, quest_id, quest, user_text, feedback):
    path = f"progress/quests/{user_id}/{quest_id}"
    data = {
        "title": quest["title"],
        "xp": quest["xp"],
        "completed": True,
        "submitted_text": user_text,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }
    db.child(path).set(data)

# -- Main UI
def quests_page(user):
    st.title("🗡️ AI Quests")
    user_id = user.get("user_id") or user.get("localId") or user.get("uid")

    if not user_id:
        st.error("User ID not found.")
        return

    course = get_assigned_course(user_id)
    if not course:
        st.warning("No course assigned yet.")
        return

    # Load quests dynamically
    quests = generate_ai_quests(course)
    quest_progress = get_quest_progress(user_id)

    # XP calculation
    total_xp = sum(q["xp"] for q in quests)
    completed_xp = sum(quest_progress[qid]["xp"] for qid in quest_progress)
    st.markdown(f"### Progress: {completed_xp} / {total_xp} XP")
    st.progress(completed_xp / total_xp if total_xp else 0.0)
    st.markdown("---")

    for i, quest in enumerate(quests):
        quest_id = f"quest_{i}"
        if quest_id in quest_progress:
            st.success(f"✅ {quest['title']} (+{quest['xp']} XP)")
            st.markdown(f"📝 Your Submission: `{quest_progress[quest_id]['submitted_text']}`")
            st.markdown(f"🧠 AI Feedback: _{quest_progress[quest_id]['feedback']}_")
        else:
            with st.expander(f"🎯 {quest['title']}"):
                user_input = st.text_area(f"✍️ Your response to this quest:", key=f"input_{i}")
                if st.button(f"🚀 Submit Quest", key=f"submit_{i}"):
                    if not user_input.strip():
                        st.warning("Please enter a meaningful response before submitting.")
                    else:
                        with st.spinner("Submitting and generating feedback..."):
                            feedback_prompt = f"A student submitted this for a learning quest: '{quest['title']}'\nSubmission:\n{user_input}\nGive constructive, positive feedback."
                            feedback = query_granite(feedback_prompt)
                            feedback_text = feedback[0]["generated_text"] if isinstance(feedback, list) else "Good effort! Keep learning."

                            # Save to Firebase
                            save_quest_submission(user_id, quest_id, quest, user_input, feedback_text)

                            st.success("✅ Quest Submitted!")
                            st.markdown(f"🧠 Feedback: _{feedback_text}_")
                            st.rerun()

    st.markdown("---")
    st.info("Complete AI-generated quests to earn XP and receive personalized feedback!")
