import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "ibm-granite/granite-3.3-2b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Auto fallback to CPU if CUDA not available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map=None
).to(device)

def query_granite(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return [{"generated_text": response}]
