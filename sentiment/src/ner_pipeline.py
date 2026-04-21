import spacy
from .ner_rules import add_hybrid_rules

def load_baseline_model(model_name="uk_core_news_sm"):
    """Завантажує базову модель spaCy."""
    return spacy.load(model_name)

def create_hybrid_model(model_name="uk_core_news_sm"):
    """Завантажує базову модель та додає до неї гібридні правила."""
    nlp = spacy.load(model_name)
    return add_hybrid_rules(nlp)

def run_inference(nlp_model, eval_data):
    """
    Проганяє список словників (eval_data) через модель.
    Повертає список результатів з передбаченнями.
    """
    results = []
    for data in eval_data:
        text = data["text"]
        expected_ents = list(zip(data["expected_entities"], data["expected_types"]))
        
        doc = nlp_model(text)
        predicted_ents = [(ent.text, ent.label_) for ent in doc.ents]
        
        results.append({
            "text": text,
            "expected": expected_ents,
            "predicted": predicted_ents
        })
    return results