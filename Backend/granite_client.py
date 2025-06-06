# backend/granite_client.py
import random

USE_MOCK = True

def get_feedback_from_granite(user_input):
    if USE_MOCK:
        return random.choice([
            "✅ Great explanation! You’ve got the concept.",
            "🛠 Try elaborating more on step 2.",
            "🧠 Good attempt! Consider checking the formula used.",
            "🔁 Let's revise the logic in your second paragraph."
        ])
    
    # Live IBM Granite API logic (not active for now)

    return "⚠️ Live API not yet connected. Using mock feedback."
