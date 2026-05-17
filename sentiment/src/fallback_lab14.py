from .flow_state import FlowState

def apply_fallback(state: FlowState) -> FlowState:
    state.fallback_triggered = True
    
    if state.route == "unknown" or state.status == "execution_error":
        state.status = "failed"
        state.errors.append("Fallback safe failure: could not classify request.")
        state.add_step("fallback", "failed", {"reason": "safe_failure"})
        return state
        
    if state.status == "validation_failed":
        recovered_output = state.tool_outputs.copy()
        recovered_output["predicted_class"] = "Needs Manual Review"
        recovered_output["needs_manual_review"] = True
        
        state.fallback_result = {"action": "assigned_manual_review"}
        state.final_output = recovered_output
        state.status = "validated_with_warning"
        state.add_step("fallback", "applied_manual_review_route", state.fallback_result)
        
    return state