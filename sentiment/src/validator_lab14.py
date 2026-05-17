from .flow_state import FlowState

def validate(state: FlowState) -> FlowState:
    if state.route != "support_classification":
        state.validation_result = {"valid": False, "reason": "No execution for unknown route"}
        state.add_step("validate", "failed", state.validation_result)
        return state
        
    outputs = state.tool_outputs
    issues = []
    
    if "predicted_class" not in outputs:
        issues.append("Missing required field: predicted_class")
    if "confidence" not in outputs:
        issues.append("Missing required field: confidence")
        
    if outputs.get("confidence", 0) < 0.70:
        issues.append(f"Low confidence ({outputs.get('confidence')}). Needs review.")
        
    if issues:
        state.validation_result = {
            "valid": False,
            "schema_ok": True,
            "issues": issues,
            "recommended_action": "manual_review"
        }
        state.status = "validation_failed"
        state.warnings.extend(issues)
        state.add_step("validate", "warning", state.validation_result)
    else:
        state.validation_result = {"valid": True}
        state.status = "validated"
        state.final_output = outputs
        state.add_step("validate", "ok")
        
    return state