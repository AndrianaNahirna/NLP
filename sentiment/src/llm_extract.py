import torch
from transformers import pipeline

def get_baseline_prompt(text, schema_str):
    """
    Формує базовий промпт для extraction-задачі.
    """
    prompt = f"""
Витягни структуровану інформацію з наступного відгуку українською мовою.
Використовуй наступну JSON схему для виходу:
{schema_str}

Текст відгуку:
\"\"\"{text}\"\"\"

Правила:
1. Поверни ТІЛЬКИ чистий JSON. 
2. Не додавай жодних пояснень чи тексту до або після JSON. 
3. Якщо значення для поля відсутнє, використовуй null (крім масивів).
"""
    return prompt.strip()

model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit"
pipe = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"dtype": torch.bfloat16}, 
    device_map="auto",
)

def call_llm(prompt):
    """
    Звертається до локальної Llama для отримання результату.
    """
    messages = [
        {"role": "system", "content": "Ти — помічник, який повертає ТІЛЬКИ чистий JSON згідно зі схемою."},
        {"role": "user", "content": prompt},
    ]
    
    outputs = pipe(
        messages,
        max_new_tokens=512,
        do_sample=False, 
    )
    
    raw_text = outputs[0]["generated_text"][-1]["content"].strip()
    
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
        
    return raw_text.strip()