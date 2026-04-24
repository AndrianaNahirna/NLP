import json
import re
from jsonschema import validate, ValidationError

def extract_json_string(text):
    """
    Витягує JSON-рядок із тексту.
    Це захищає систему у випадках, коли LLM додає markdown форматування 
    або пише зайвий текст до/після JSON.
    """
    pattern = r'\x60\x60\x60(?:json)?\s*(.*?)\s*\x60\x60\x60'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return text.strip()

def validate_json(llm_output, schema):
    """
    Головний валідатор.
    Перевіряє 2 речі: чи парситься JSON і чи валідний він за схемою.
    Повертає кортеж: (is_valid_json, is_valid_schema, parsed_data, error_message)
    """
    json_str = extract_json_string(llm_output)
    
    # 1. Parse JSON (Чи це взагалі формат JSON?)
    try:
        parsed_data = json.loads(json_str)
        is_valid_json = True
    except json.JSONDecodeError as e:
        return False, False, None, f"JSON Parse Error: {str(e)}"
    
    # 2. Validate against schema (Чи правильні поля та їх типи?)
    try:
        validate(instance=parsed_data, schema=schema)
        is_valid_schema = True
        return True, True, parsed_data, None
    except ValidationError as e:
        return True, False, parsed_data, f"Schema Validation Error: Поле '{e.json_path}' -> {e.message}"