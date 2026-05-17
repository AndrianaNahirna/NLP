import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .tools import classify_ticket, extract_entities, validate_required_fields
from .tool_logger import log_tool_call

# Завантаження моделі
MODEL_ID = "unsloth/llama-3-8b-Instruct-bnb-4bit"
print("Завантаження моделі...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16
)

def _generate_llm_response(prompt: str) -> str:
    """Допоміжна функція для генерації тексту через локальну модель."""
    messages = [
        {"role": "system", "content": "Ти - ввічливий агент служби підтримки. Відповідай українською коротко і по суті."},
        {"role": "user", "content": prompt}
    ]
    
    inputs = tokenizer.apply_chat_template(
        messages, 
        add_generation_prompt=True, 
        return_tensors="pt",
        return_dict=True
    ).to(model.device)
    
    outputs = model.generate(
        **inputs, 
        max_new_tokens=150, 
        temperature=0.2, 
        pad_token_id=tokenizer.eos_token_id
    )
    
    prompt_length = inputs["input_ids"].shape[1]
    
    return tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True)

def run_baseline(user_text: str) -> str:
    """Варіант 1: LLM без tools (модель відповідає лише за промптом)."""
    prompt = f"Користувач написав: '{user_text}'. Сформуй відповідь служби підтримки."
    return _generate_llm_response(prompt)

def run_agent(task_id: str, user_text: str) -> str:
    """Варіант 2: Single-agent + tools."""
    tools_results = {}
    
    # Виклик Tool 1: Класифікація
    try:
        class_res = classify_ticket(user_text)
        log_tool_call(task_id, "classify_ticket", {"text": user_text}, class_res, True)
        tools_results['classification'] = class_res
    except Exception as e:
        log_tool_call(task_id, "classify_ticket", {"text": user_text}, None, False, str(e))
        
    # Виклик Tool 2: Витяг сутностей
    try:
        ent_res = extract_entities(user_text)
        log_tool_call(task_id, "extract_entities", {"text": user_text}, ent_res, True)
        tools_results['entities'] = ent_res
    except Exception as e:
        log_tool_call(task_id, "extract_entities", {"text": user_text}, None, False, str(e))

    # Виклик Tool 3: Валідація (чи є номер замовлення)
    if 'entities' in tools_results:
        try:
            val_res = validate_required_fields(tools_results['entities'])
            log_tool_call(task_id, "validate_required_fields", tools_results['entities'], val_res, True)
            tools_results['validation'] = val_res
        except Exception as e:
            log_tool_call(task_id, "validate_required_fields", tools_results['entities'], None, False, str(e))

    # Формування підсумкового промпту на основі результатів tools
    missing_info_str = ""
    if tools_results.get('validation') and not tools_results['validation']['is_valid']:
        missing_info_str = "ОБОВ'ЯЗКОВО попроси користувача надати номер замовлення, бо його не знайдено."

    prompt = f"""
    Користувач написав: "{user_text}"
    
    Дані від внутрішніх систем (Tools):
    - Категорія: {tools_results.get('classification', {}).get('category')}
    - Сутності: {tools_results.get('entities')}
    
    Сформуй відповідь. Враховуй категорію. Якщо знайдено номер замовлення - згадай його.
    {missing_info_str}
    """
    return _generate_llm_response(prompt)