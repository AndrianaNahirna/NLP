import json

class ReviewerAgent:
    """
    Агент, який перевіряє результати Extractor на відповідність схемі та логіці.
    """
    def __init__(self, llm_caller=None):
        pass

    def review(self, original_text: str, extraction: dict) -> dict:
        issues = []
        is_valid = True
        verdict = "accept"
        
        # 1. Перевірка на помилки парсингу
        if "error" in extraction:
             return {
                 "verdict": "repair_needed", "valid_json": False, "schema_ok": False, "consistency_ok": False,
                 "issues": [{"field": "all", "problem": "Extractor returned invalid JSON."}],
                 "recommended_action": "run_repair"
             }

        # 2. Schema Validation (перевірка типів)
        required_fields = ["sentiment_type", "mentioned_aspects", "advantages", "disadvantages", "rating_mentioned"]
        for field in required_fields:
            if field not in extraction:
                issues.append({"field": field, "problem": "Missing required field."})
                is_valid = False

        if "advantages" in extraction and isinstance(extraction["advantages"], list):
             issues.append({"field": "advantages", "problem": "Expected string or null, got array."})
             is_valid = False
             
        if "disadvantages" in extraction and isinstance(extraction["disadvantages"], list):
             issues.append({"field": "disadvantages", "problem": "Expected string or null, got array."})
             is_valid = False

        # 3. Consistency Checks (Логічні перевірки)
        sentiment = extraction.get("sentiment_type")
        rating = extraction.get("rating_mentioned")
        
        if sentiment == "negative" and isinstance(rating, (int, float)) and rating >= 4:
             issues.append({"field": "sentiment_type", "problem": f"Contradiction: Negative sentiment but high rating ({rating})."})
             verdict = "fallback_needed"
             is_valid = False

        if not is_valid and verdict != "fallback_needed":
             verdict = "repair_needed"

        return {
            "verdict": verdict,
            "valid_json": True,
            "schema_ok": len([i for i in issues if "Missing" in i['problem'] or "array" in i['problem']]) == 0,
            "consistency_ok": len([i for i in issues if "Contradiction" in i['problem']]) == 0,
            "issues": issues,
            "recommended_action": "run_repair" if verdict == "repair_needed" else "manual_review" if verdict == "fallback_needed" else "none"
        }