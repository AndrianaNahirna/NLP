import json

# Схема для витягування даних з відгуків
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment_type": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
            "description": "Загальна тональність відгуку"
        },
        "mentioned_aspects": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Список аспектів продукту/послуги, що згадуються"
        },
        "advantages": {
            "type": ["string", "null"],
            "description": "Конкретні переваги, згадані у тексті"
        },
        "disadvantages": {
            "type": ["string", "null"],
            "description": "Конкретні недоліки, згадані у тексті"
        },
        "rating_mentioned": {
            "type": ["number", "null"],
            "description": "Числова оцінка, якщо вона явно або неявно вказана в тексті"
        }
    },
    "required": [
        "sentiment_type",
        "mentioned_aspects",
        "advantages",
        "disadvantages",
        "rating_mentioned"
    ],
    "additionalProperties": False
}

def get_schema_string():
    return json.dumps(EXTRACTION_SCHEMA, indent=2, ensure_ascii=False)