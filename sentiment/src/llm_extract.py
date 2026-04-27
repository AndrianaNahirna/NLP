import json
import google.generativeai as genai

API_KEY = "AIzaSyDiggjJfW8sTopQjqFGhlYKHR39xVi3iAA"

genai.configure(api_key=API_KEY)

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
1. Поверни ТІЛЬКИ чистий JSON без блоків коду (```json ... ```).
2. Не додавай жодних пояснень, привітань чи тексту до або після JSON.
3. Якщо значення для поля відсутнє, використовуй null (крім масивів, де має бути порожній список []).
4. Дотримуйся типів даних, вказаних у схемі.
"""
    return prompt.strip()

def call_llm(prompt):
    """
    Звертається до API Gemini для отримання результату.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0, 
            )
        )
        
        raw_text = response.text.strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return raw_text.strip()
        
    except Exception as e:
        print(f"Помилка API: {e}")
        return f'{{"error": "API Error: {str(e)}"}}'