import json

def run_evaluation(crew_workflow, test_cases, log_file_path="docs/crew_logs_lab13.jsonl"):
    results = []
    
    with open(log_file_path, "w", encoding="utf-8") as f:
        for case in test_cases:
            print(f"Processing {case['case_id']}...")
            log_entry = crew_workflow.process_case(case['case_id'], case['input'])
            results.append(log_entry)
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
    print(f"\nProcessing complete. Logs saved to {log_file_path}")
    return results

def calculate_metrics(results):
    total = len(results)
    if total == 0: return {}
    
    valid_final = sum(1 for r in results if r['status'] in ['accepted', 'accepted_after_repair'])
    reviewer_caught = sum(1 for r in results if r['reviewer_output']['verdict'] != 'accept')
    fallback_activated = sum(1 for r in results if r.get('fallback_triggered', False))
    fallback_success = sum(1 for r in results if r['status'] == 'accepted_after_repair')
    manual_review = sum(1 for r in results if r['status'] in ['manual_review_required', 'failed_after_repair', 'failed_repair_exception'])
    
    metrics = {
        "Total Cases": total,
        "Valid Final Output Rate": valid_final / total,
        "Reviewer Catch Rate": reviewer_caught / total,
        "Fallback Activation Rate": fallback_activated / total,
        "Fallback Success Rate": fallback_success / fallback_activated if fallback_activated > 0 else 0,
        "Manual Review Rate": manual_review / total
    }
    return metrics