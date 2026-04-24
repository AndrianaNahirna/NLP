import google.generativeai as genai
import json

def setup_llm(api_key, model_name="gemini-1.5-flash"):
    """Ініціалізує та повертає модель Gemini."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def generate_baseline_prompt(text, schema):
    """
    Створює базовий prompt для видобування даних.
    """
    return f"""Ти — інженер з видобування даних. Твоє завдання — витягти інформацію з наданого тексту та повернути її ВИНЯТКОВО у форматі валідного JSON.

Правила:
1. Витягни інформацію чітко згідно з JSON Schema, наведеною нижче.
2. Якщо певне значення відсутнє у тексті, використовуй `null`, як вказано у схемі.
3. Не пиши жодного тексту до або після JSON (ніяких привітань, пояснень чи markdown-блоків). Тільки чистий JSON.

JSON Schema:
{json.dumps(schema, indent=2, ensure_ascii=False)}

Текст для аналізу:
"{text}"
"""

def extract_raw(model, text, schema):
    """
    Виконує "сиру" екстракцію без repair loop.
    """
    prompt = generate_baseline_prompt(text, schema)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)