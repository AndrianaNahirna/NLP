import json
import os
from .flow_state import FlowState

def log_flow(state: FlowState, log_file: str = "data/flow_logs_lab14.jsonl"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    log_entry = {
        "case_id": state.case_id,
        "input": state.raw_text,
        "steps": state.steps,
        "route": state.route,
        "validation_result": state.validation_result,
        "fallback_triggered": state.fallback_triggered,
        "final_status": state.status,
        "export_output": state.final_output,
        "errors": state.errors,
        "warnings": state.warnings
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')