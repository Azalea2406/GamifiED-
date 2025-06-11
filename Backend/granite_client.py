# backend/granite_client.py
import requests
import random
import os

# Toggle between mock or live Granite usage
USE_MOCK = False  # Set to False to use Hugging Face live

# Hugging Face API credentials (use environment variable for safety)
HF_API_TOKEN = os.getenv("HF_API_TOKEN") or "your_huggingface_token_here"
GRANITE_MODEL_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-13b-chat-v1"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

def get_feedback_from_granite(user_input):
    if USE_MOCK:
        return random.choice([
            "✅ You’ve got the concept.",
            "🛠 Check out more examples",
            "🧠 Good attempt!",
            "🔁 Revisit the concept"
        ])

    try:
        response = requests.post(
            GRANITE_MODEL_URL,
            headers=HEADERS,
            json={"inputs": user_input, "options": {"wait_for_model": True}}
        )
        if response.status_code == 200:
            output = response.json()
            return output[0]["generated_text"]
        else:
            return f"⚠️ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Request failed: {e}"
