import json
from jsonschema import validate, ValidationError

def validate_extraction(json_str, schema):
    """
    Перевіряє, чи є рядок валідним JSON та чи відповідає він схемі.
    Повертає (is_valid, data, error_message)
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return False, None, f"JSON Parse Error: {str(e)}"
    
    try:
        validate(instance=data, schema=schema)
        return True, data, None
    except ValidationError as e:
        return False, data, f"Schema Validation Error: {e.message}"