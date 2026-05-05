import json

class FallbackHandler:
    def __init__(self, llm_caller):
        self.call_llm = llm_caller
        
    def run_repair(self, original_text: str, broken_output: dict, review_issues: list) -> dict:
        """Спроба відремонтувати JSON за допомогою LLM."""
        prompt = f"""Ти — Repair Agent. Тобі потрібно виправити JSON.
Оригінальний текст: {original_text}

Попередній результат (з помилками):
{json.dumps(broken_output, ensure_ascii=False, indent=2) if isinstance(broken_output, dict) else broken_output}

Знайдені проблеми:
{json.dumps(review_issues, ensure_ascii=False, indent=2)}

Виправ помилки (особливо зверни увагу на те, щоб advantages/disadvantages були РЯДКАМИ, а не масивами). 
Поверни ЛИШЕ виправлений валідний JSON."""

        try:
            response_text = self.call_llm(prompt)
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            data["repaired"] = True
            return data
        except Exception:
            return None # Repair failed

    def get_safe_failure(self, original_text: str, reason: str, partial_output: dict = None) -> dict:
        """Формує безпечний результат у разі повного збою."""
        return {
            "status": "failed",
            "reason": reason,
            "partial_output": partial_output or {},
            "needs_manual_review": True
        }