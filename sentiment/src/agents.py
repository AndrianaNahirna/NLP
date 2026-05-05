import json
import uuid

class TriagerAgent:
    """
    Агент-маршрутизатор. Аналізує текст і визначає тип задачі та складність.
    """
    def __init__(self, llm_caller):
        self.call_llm = llm_caller
        self.system_prompt = """Ти — Triager (Маршрутизатор) для системи аналізу відгуків.
Твоє завдання:
1. Прочитати вхідний текст.
2. Визначити тип маршруту (route): 'full_schema' (нормальний відгук), 'simple_schema' (дуже короткий, 1-2 слова) або 'empty' (немає змісту).
3. Визначити складність (difficulty): 'low', 'medium', 'high' (якщо є сарказм, суперечності або дуже нестандартна лексика).
Поверни ЛИШЕ валідний JSON у такому форматі:
{"route": "full_schema|simple_schema|empty", "difficulty": "low|medium|high", "notes": "короткий коментар"}"""

    def process(self, text: str) -> dict:
        prompt = f"{self.system_prompt}\n\nТекст відгуку:\n{text}"
        try:
            response_text = self.call_llm(prompt)
            # Спроба очистити JSON, якщо LLM додала Markdown
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            # Fallback для самого Triager, якщо LLM видала не JSON
            return {"route": "full_schema", "difficulty": "high", "notes": f"Triager parsing failed: {e}"}

class ExtractorAgent:
    """
    Агент-екстрактор. Витягує дані за заданою схемою.
    """
    def __init__(self, llm_caller):
        self.call_llm = llm_caller
        self.base_prompt = """Ти — Extractor для аналізу відгуків. 
Твоя задача — витягти інформацію у форматі JSON.
Схема вимагає:
- sentiment_type (enum: "positive", "negative", "neutral")
- mentioned_aspects (array of strings)
- advantages (string або null. НЕ МАСИВ!)
- disadvantages (string або null. НЕ МАСИВ!)
- rating_mentioned (number або null)

ПРАВИЛО: Якщо переваг чи недоліків декілька, об'єднай їх у ЄДИНИЙ РЯДОК через кому.
ПРАВИЛО: Не вигадуй дані. Якщо чогось немає, став null.
Поверни ЛИШЕ валідний JSON."""

    def process(self, text: str, route: str) -> dict:
        if route == 'empty':
             return {
                "sentiment_type": "neutral", "mentioned_aspects": [],
                "advantages": None, "disadvantages": None, "rating_mentioned": None,
                "confidence_note": "Text was empty."
             }
        
        prompt = f"{self.base_prompt}\n\nRoute: {route}\n\nТекст відгуку:\n{text}"
        try:
            response_text = self.call_llm(prompt)
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            # Додаємо confidence_note, якщо модель його не додала
            if "confidence_note" not in data:
                 data["confidence_note"] = "Extracted successfully."
            return data
        except Exception as e:
            # Повертаємо інформацію про помилку, щоб Reviewer міг її зловити
            return {"error": "JSON Parse Error", "raw_output": response_text, "details": str(e)}