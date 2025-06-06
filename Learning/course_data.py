# Simulated course structure
COURSES = {
    "Python Basics": {
        "levels": [
            {"name": "Variables", "questions": 5},
            {"name": "Loops", "questions": 5},
            {"name": "Functions", "questions": 5}
        ]
    },
    "Web Development": {
        "levels": [
            {"name": "HTML Basics", "questions": 5},
            {"name": "CSS Styling", "questions": 5},
            {"name": "JS Intro", "questions": 5}
        ]
    }
}
def get_level_index(course_name, level_name):
    course = COURSES.get(course_name, {})
    levels = course.get("levels", [])
    for idx, level in enumerate(levels):
        if level["name"] == level_name:
            return idx
    return -1  # Not found
