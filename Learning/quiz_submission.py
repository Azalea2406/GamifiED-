from Learning.course_data import COURSES
from Learning.progress_tracker import submit_level

def submit_quiz(user_id, course_name, level_index, correct_answers, total_questions=5):
    if course_name not in COURSES:
        return {"success": False, "message": "Invalid course."}

    course = COURSES[course_name]
    if level_index >= len(course["levels"]):
        return {"success": False, "message": "Invalid level index."}

    # Calculate score
    score = (correct_answers / total_questions) * 100

    # Save progress
    result = submit_level(user_id, course_name, level_index, score)
    return result
