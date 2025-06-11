# Backend/granite_utils.py
"""
Using hugging face
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
"""

#Locally

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load the model locally
model_id = "ibm-granite/granite-3.3-2b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16
)
device = torch.device("cpu")
model = model.to(device)
def query_granite(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return [{"generated_text": response}]
