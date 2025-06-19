# granite_client.py

import requests
import os

# WatsonX / IBM Granite Config
GRANITE_API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation"
API_KEY = os.getenv("WATSONX_API_KEY") or "your_api_key_here"

# Get IAM token from API Key
def get_iam_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "apikey": API_KEY,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")

# Query Granite Model
def get_feedback_from_granite(prompt, model_id="granite-13b-chat-v1"):
    token = get_iam_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_id": model_id,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200
        }
    }
    response = requests.post(GRANITE_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["results"][0]["generated_text"]
    else:
        return f"⚠️ Error {response.status_code}: {response.text}"
