from firebase_config import db

def get_user_xp(user_id):
    progress = db.child("progress").child(user_id).get().val()
    total_xp = 0
    if progress:
        for course in progress.values():
            for level in course.values():
                total_xp += level.get("xp", 0)
    return total_xp
