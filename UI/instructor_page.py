import streamlit as st
from firebase_config import db
from Learning.course_data import COURSES
import datetime

# Utility: Get all users with 'learner' role from Firebase
def get_all_students():
    users = db.child("users").get().val()
    if not users:
        return {}
    return {uid: data for uid, data in users.items() if data.get("role") == "learner"}

# Utility: Get XP of a student
def get_user_xp(user_id):
    progress = db.child("progress").child(user_id).get().val()
    total_xp = 0
    if progress:
        for course in progress.values():
            for level in course.values():
                total_xp += level.get("xp", 0)
    return total_xp

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
    course_options = ["Python Basics", "Web Development"]
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

    # Step 3: View leaderboard
    st.subheader("🏆 Group Leaderboard")
    leaderboard = []
    for uid, data in students.items():
        xp = get_user_xp(uid)
        leaderboard.append({
            "username": data.get("username", "Unknown"),
            "xp": xp
        })

    sorted_leaderboard = sorted(leaderboard, key=lambda x: x["xp"], reverse=True)

    for i, entry in enumerate(sorted_leaderboard, start=1):
        st.write(f"**#{i}** - {entry['username']} | XP: {entry['xp']}")
