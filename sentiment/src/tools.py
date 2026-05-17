import re

def classify_ticket(text: str) -> dict:
    """Класифікує тип звернення користувача."""
    text_lower = text.lower()
    try:
        if any(word in text_lower for word in ["оплата", "гроші", "рахунок", "повернення", "картка", "грн"]):
            return {"category": "billing", "confidence": 0.9}
        elif any(word in text_lower for word in ["помилка", "не працює", "баг", "зависає", "збій"]):
            return {"category": "technical", "confidence": 0.9}
        elif any(word in text_lower for word in ["пароль", "логін", "профіль", "доступ", "акаунт"]):
            return {"category": "account", "confidence": 0.8}
        else:
            return {"category": "general_inquiry", "confidence": 0.5}
    except Exception as e:
        raise RuntimeError(f"Classification error: {str(e)}")

def extract_entities(text: str) -> dict:
    """Витягує сутності: email та номер замовлення."""
    try:
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        order_ids = re.findall(r'(?:замовлення|order|№|#)(?:\s*:?\s*)(\d{4,8})', text.lower())
        
        return {
            "emails": emails if emails else None,
            "order_ids": order_ids if order_ids else None
        }
    except Exception as e:
        raise RuntimeError(f"Extraction error: {str(e)}")

def validate_required_fields(extracted_data: dict) -> dict:
    """Перевіряє, чи вистачає даних для обробки (наприклад, чи є номер замовлення)."""
    try:
        missing = []
        if not extracted_data.get("order_ids"):
            missing.append("order_id")
        
        return {
            "is_valid": len(missing) == 0,
            "missing_fields": missing
        }
    except Exception as e:
        raise RuntimeError(f"Validation error: {str(e)}")