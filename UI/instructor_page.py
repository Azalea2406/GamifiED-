import streamlit as st
from firebase_config import db
from Learning.course_data import COURSES
import datetime
from main import get_user_xp  # move this safely here

# Utility: Get all users with 'learner' role from Firebase
def get_all_students():
    users = db.child("users").get().val()
    if not users:
        return {}
    return {uid: data for uid, data in users.items() if data.get("role") == "learner"}

# Streamlit UI for instructor dashboard
def instructor_dashboard():
    st.title("📊 Instructor Dashboard")

    # Step 1: Show list of all students
    st.subheader("👥 Student List")
    students = get_all_students()

    if not students:
        st.warning("No students found.")
        return

    student_names = [data.get("username", uid) for uid, data in students.items()]
    student_ids = list(students.keys())

    selected_student = st.selectbox("Select a student", options=student_names)
    selected_id = student_ids[student_names.index(selected_student)]

    # Step 2: Assign a course (mock functionality)
    st.subheader("📚 Assign Learning Path")
    course_options = list(COURSES.keys())
    assigned_course = st.selectbox("Select a course to assign", course_options)

    if st.button("Assign Course"):
        try:
            timestamp = datetime.datetime.now().isoformat()
            db.child("assignments").child(selected_id).update({
                "course": assigned_course,
                "assigned_at": timestamp
            })
            st.success(f"{assigned_course} assigned to {selected_student}.")
        except Exception as e:
            st.error(f"Failed to assign course: {e}")

    # Granite-assisted suggestion
    st.markdown("---")
    st.subheader("🤖 Course Suggestion Assistant")
    query = st.text_input("Ask AI: What course should I assign next?")

    if query:
        from Backend.granite_utils import query_granite
        with st.spinner("Thinking..."):
            suggestion = query_granite(query)
            if isinstance(suggestion, list):
                st.success("💡 Granite Suggestion:")
                st.markdown(suggestion[0]["generated_text"])
            else:
                st.warning("No response from Granite.")

# Instructor Leaderboard Page
def instructor_leaderboard_page():
    st.title("🏆 Group Leaderboard")
    students = get_all_students()

    leaderboard = []
    for uid, data in students.items():
        xp = get_user_xp(uid)
        leaderboard.append({
            "username": data.get("username", "Unknown"),
            "xp": xp
        })

    sorted_leaderboard = sorted(leaderboard, key=lambda x: x["xp"], reverse=True)

    if not sorted_leaderboard:
        st.info("No XP data available yet.")
        return

    for i, entry in enumerate(sorted_leaderboard, start=1):
        st.write(f"**#{i}** - {entry['username']} | XP: {entry['xp']}")

# Instructor Quests Placeholder
def instructor_quests_page():
    st.title("🧭 Instructor Quests Overview")
    st.info("This section will allow instructors to track student quest progress, view submissions, and optionally create course-wide quests. Coming soon!")
