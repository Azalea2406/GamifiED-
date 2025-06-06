# backend/granite_client.py

def get_feedback_from_granite(user_input):
    if USE_MOCK:
        return random.choice([
            "✅ Great explanation! You’ve got the concept.",
            "🛠 Try elaborating more on step 2.",
            "🧠 Good attempt! Consider checking the formula used.",
            "🔁 Let's revise the logic in your second paragraph."
        ])
    
    # TODO: Connect to IBM Granite API here
    # Example:
    # response = granite_chain.invoke(user_input)
    # return response.get("feedback")

    return "⚠️ Live API not yet connected. Using mock feedback."
