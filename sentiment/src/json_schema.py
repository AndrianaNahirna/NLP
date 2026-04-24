REVIEW_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "shop_name": {
            "type": ["string", "null"],
            "description": "Назва магазину (наприклад, Розетка, Цитрус). null якщо не вказано."
        },
        "product_name": {
            "type": ["string", "null"],
            "description": "Назва товару (наприклад, iPhone 13). null якщо не вказано."
        },
        "price": {
            "type": ["number", "null"],
            "description": "Ціна товару у вигляді числа без валюти. null якщо не вказано."
        },
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
            "description": "Тональність відгуку."
        },
        "order_id": {
            "type": ["string", "null"],
            "description": "Номер замовлення, якщо він є у тексті. null якщо немає."
        },
        "issue_reported": {
            "type": "boolean",
            "description": "true, якщо клієнт повідомляє про проблему (поломка, затримка тощо), інакше false."
        }
    },
    "required": ["shop_name", "sentiment", "issue_reported"],
    "additionalProperties": False
}