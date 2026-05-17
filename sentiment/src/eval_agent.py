from .agent import run_agent, run_baseline

def run_evaluation(TEST_CASES):
    print("Початок тестування")
    
    for case in TEST_CASES:
        print(f"\nTask ID: {case['id']}")
        print(f"User Input: {case['text']}")
        
        # 1. Запуск Baseline (Тільки LLM)
        print("\n[BASELINE - Без Tools]:")
        baseline_answer = run_baseline(case['text'])
        print(baseline_answer)
        
        # 2. Запуск Агента (Tools + LLM)
        print("\n[AGENT - З Tools]:")
        agent_answer = run_agent(case['id'], case['text'])
        print(agent_answer)
        print("-" * 50)
        
    print("\nТестування завершено. Логи збережено у docs/tool_logs_lab12.jsonl")