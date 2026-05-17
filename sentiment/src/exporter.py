from .flow_state import FlowState

def export(state: FlowState) -> dict:
    if state.status in ["validated", "validated_with_warning"]:
        export_status = "exported" if state.status == "validated" else "exported_with_warning"
        result = {
            "case_id": state.case_id,
            "route": state.route,
            "prediction": state.final_output,
            "status": export_status,
            "warnings": state.warnings
        }
        state.status = export_status
    else:
        # Safe failure [cite: 312-321]
        result = {
            "case_id": state.case_id,
            "status": "failed",
            "reason": state.errors[-1] if state.errors else "Unknown failure",
            "prediction": None,
            "needs_manual_review": True
        }
        state.status = "failed"
        
    state.add_step("export", state.status)
    return result