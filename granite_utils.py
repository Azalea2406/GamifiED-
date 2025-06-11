# Backend/granite_utils.py
import requests
import os

API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.3-2b-instruct"
headers = {
    "Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"
}

def query_granite(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
