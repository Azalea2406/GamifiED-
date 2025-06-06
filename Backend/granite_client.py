# backend/granite_client.py
import random

USE_MOCK = True

def get_feedback_from_granite(user_input):
    if USE_MOCK:
        return random.choice([
            "✅ You’ve got the concept.",
            "🛠 Check out more examples",
            "🧠 Good attempt!",
            "🔁 Revisit the concept"
        ])
    
    # Live IBM Granite API logic (not active for now)

    return "⚠️ Live API not yet connected. Using mock feedback."
