import uuid
from .flow_state import FlowState
from .router import route
from .executor import execute
from .validator_lab14 import validate
from .fallback_lab14 import apply_fallback
from .exporter import export
from .flow_logger import log_flow

def ingest(raw_text: str) -> FlowState:
    """Етап 1: Прийняти input і підготувати його до обробки"""
    case_id = f"case_{uuid.uuid4().hex[:6]}"
    clean_text = raw_text.strip().replace("\n", " ")
    
    state = FlowState(case_id=case_id, raw_text=raw_text, clean_text=clean_text)
    state.status = "ingested"
    
    if not clean_text:
        state.errors.append("Input is empty")
        state.status = "ingestion_failed"
        state.add_step("ingest", "failed", {"reason": "empty_input"})
        return state
        
    state.add_step("ingest", "ok", {"case_id": case_id})
    return state

def run_classification_flow(raw_text: str, log_file: str = "data/flow_logs_lab14.jsonl") -> dict:
    """Оркестрація процесу класифікації."""
    # 1. Ingest
    state = ingest(raw_text)
    
    if state.status == "ingested":
        # 2. Route
        state = route(state)
        
        # 3. Execute
        state = execute(state)
        
        # 4. Validate
        state = validate(state)
        
        # 5. Fallback
        if not state.validation_result.get("valid", False) or state.status == "execution_error":
            state = apply_fallback(state)
            
    # 6. Export
    final_result = export(state)
    
    # Логування
    log_flow(state, log_file)
    
    return final_result