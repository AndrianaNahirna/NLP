import torch
from transformers import pipeline

model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit" 

pipe = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

def call_llm(prompt):
    messages = [
        {"role": "system", "content": "Ти — помічник, який повертає ТІЛЬКИ чистий JSON згідно зі схемою."},
        {"role": "user", "content": prompt},
    ]
    
    terminators = [
        pipe.tokenizer.eos_token_id,
        pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = pipe(
        messages,
        max_new_tokens=512,
        eos_token_id=terminators,
        do_sample=False,
    )
    
    raw_text = outputs[0]["generated_text"][-1]["content"].strip()
    
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
        
    return raw_text.strip()