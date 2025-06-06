from Learning.xp_logic import calculate_xp
from firebase_config import db  # create firebase_config.py to reuse firebase setup
from datetime import datetime

def submit_level(user_id, course_name, level_index, score):
    path = f"progress/{user_id}/{course_name}/level_{level_index}"
    level_data = db.child(path).get().val()

    if level_data:
        return {"success": False, "message": "Level already completed."}

    xp_earned = calculate_xp(score)
    db.child("progress").child(user_id).child(course_name).child(f"level_{level_index}").set({
    "score": score,
    "xp": xp_earned,
    "timestamp": datetime.now().isoformat()
})

    return {"success": True, "xp": xp_earned}
