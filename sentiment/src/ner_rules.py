def get_hybrid_patterns():
    """Повертає список словникових та regex правил для EntityRuler."""
    return [
        # Правило для MONEY
        {"label": "MONEY", "pattern": [{"IS_DIGIT": True}, {"LOWER": {"IN": ["грн", "гривень", "баксів", "грн."]}}]},
        # Правила для ORDER_ID
        {"label": "ORDER_ID", "pattern": [{"ORTH": "№"}, {"IS_SPACE": True, "OP": "?"}, {"IS_DIGIT": True}]},
        {"label": "ORDER_ID", "pattern": [{"LOWER": "замовлення"}, {"IS_DIGIT": True}]},
        # Словникові правила для ORG (українські бренди)
        {"label": "ORG", "pattern": [{"LOWER": {"IN": ["розетка", "розетці", "цитрус", "приватбанк", "монобанк"]}}]},
        # Правило для Нової Пошти з урахуванням відмінків
        {"label": "ORG", "pattern": [{"LOWER": {"IN": ["нова", "нову"]}}, {"LOWER": {"IN": ["пошта", "пошту"]}}]},
        # Правило для числових дат
        {"label": "DATE", "pattern": [{"SHAPE": "dd.dd.dddd"}]}
    ]

def add_hybrid_rules(nlp):
    """Додає EntityRuler з нашими правилами перед стандартним NER."""
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(get_hybrid_patterns())
    return nlp