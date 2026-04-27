from sentiment.src.llm_extract import get_baseline_prompt, call_llm
from sentiment.src.validator import validate_extraction
import json

def get_repair_prompt(original_text, broken_output, error_message, schema_str):
    """
    Формує промпт для виправлення помилок у JSON.
    """
    prompt = f"""
Ти намагався витягти дані з тексту, але згенерував невалідний JSON або порушив схему.

Оригінальний текст відгуку:
\"\"\"{original_text}\"\"\"

Твій попередній (зламаний) вихід:
{broken_output}

Системна помилка (що саме треба виправити):
{error_message}

Будь ласка, виправ цю помилку та поверни валідний JSON згідно зі схемою:
{schema_str}

КРИТИЧНЕ ПРАВИЛО: 
Поверни ТІЛЬКИ виправлений JSON. Не пиши "Ось виправлений JSON", не додавай тегів форматування (```json). Починай одразу з {{ і закінчуй }}.
"""
    return prompt.strip()

def run_extraction_pipeline(text, schema, max_repairs=2):
    """
    Основний інженерний пайплайн: Extraction -> Validation -> (Repair Loop)
    """
    schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
    prompt = get_baseline_prompt(text, schema_str)
    
    # Перша спроба
    current_output = call_llm(prompt)
    
    repairs_made = 0
    while repairs_made <= max_repairs:
        is_valid, data, error = validate_extraction(current_output, schema)
        
        if is_valid:
            return {
                "status": "success",
                "data": data,
                "repairs_needed": repairs_made,
                "raw_output": current_output
            }
        
        repairs_made += 1
        if repairs_made <= max_repairs:
            repair_prompt = get_repair_prompt(text, current_output, error, schema_str)
            current_output = call_llm(repair_prompt)
        else:
            return {
                "status": "fail",
                "error": error,
                "repairs_attempted": max_repairs,
                "last_output": current_output
            }