def print_inference_results(results, title="NER Output", limit=15):
    """Виводить результати inference у зручному форматі."""
    print(f"{title}\n")
    for i, res in enumerate(results[:limit]):
        print(f"{i+1}. Текст: {res['text']}")
        print(f"    Expected : {res['expected']}")
        print(f"    Predicted: {res['predicted'] if res['predicted'] else '[] (Нічого не знайдено)'}")

def compare_models_output(baseline_results, hybrid_results, indices_to_show):
    """Виводить порівняння двох моделей для вибраних речень."""
    print("Порівняння (Baseline vs Hybrid) на вибраних реченнях")
    for i in indices_to_show:
        print(f"\nТекст: {baseline_results[i]['text']}")
        print(f"Baseline: {baseline_results[i]['predicted']}")
        print(f"Hybrid:   {hybrid_results[i]['predicted']}")