from src.llm_extract import generate_baseline_prompt
from src.validator import validate_json
import json

def generate_repair_prompt(original_text, broken_output, error_message, schema):
    """
    Створює prompt для виправлення помилок у JSON.
    """
    return f"""Ти отримав завдання витягти дані у JSON, але твій попередній результат містив синтаксичну помилку або не відповідав схемі.
Виправ помилку і поверни ТІЛЬКИ валідний JSON. Нічого зайвого.

Оригінальний текст:
"{original_text}"

Твій попередній (помилковий) вихід:
{broken_output}

Помилка валідації, яку тобі потрібно виправити:
{error_message}

Вимоги JSON Schema:
{json.dumps(schema, indent=2, ensure_ascii=False)}
"""

def run_extraction_with_repair(model, text, schema, max_attempts=2):
    """
    Виконує екстракцію з підтримкою Repair Loop.
    Повертає словник з усіма метриками та історією спроб.
    """
    # 1. Запускаємо baseline extraction
    prompt = generate_baseline_prompt(text, schema)
    try:
        llm_output = model.generate_content(prompt).text
    except Exception as e:
        llm_output = str(e)
    
    # Перевіряємо результат
    is_json, is_schema, data, error = validate_json(llm_output, schema)
    
    # Зберігаємо початкові метрики
    metrics = {
        "raw_valid_json": is_json,
        "raw_valid_schema": is_schema,
        "repairs_needed": 0,
        "final_valid_schema": is_schema,
        "final_data": data,
        "history": [{"output": llm_output, "error": error}]
    }
    
    # Якщо все валідно з першого разу — повертаємо результат
    if is_schema:
        return metrics
        
    # 2. Repair Loop
    current_output = llm_output
    current_error = error
    
    for attempt in range(max_attempts):
        metrics["repairs_needed"] += 1
        
        # Формуємо repair prompt
        repair_prompt = generate_repair_prompt(text, current_output, current_error, schema)
        
        try:
            current_output = model.generate_content(repair_prompt).text
        except Exception as e:
            current_output = str(e)
            
        # Знову перевіряємо
        is_json, is_schema, data, current_error = validate_json(current_output, schema)
        
        metrics["history"].append({"output": current_output, "error": current_error})
        
        # Якщо JSON став валідним - виходимо з циклу
        if is_schema:
            metrics["final_valid_schema"] = True
            metrics["final_data"] = data
            break
            
    return metrics