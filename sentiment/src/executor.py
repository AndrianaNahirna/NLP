from .flow_state import FlowState

def execute(state: FlowState) -> FlowState:
    if state.route == "support_classification":
        try:
            text = state.clean_text.lower()
            prediction = {}
            
            if "оплата" in text or "гроші" in text or "карта" in text:
                prediction = {"predicted_class": "Billing", "confidence": 0.92, "explanation": "Mentions payment or money."}
            elif "пароль" in text or "не працює" in text or "помилка" in text:
                prediction = {"predicted_class": "Technical", "confidence": 0.85, "explanation": "Mentions technical issues."}
            else:
                prediction = {"predicted_class": "General Inquiry", "confidence": 0.45, "explanation": "No specific category keywords found."}
                
            state.tool_outputs = prediction
            state.add_step("execute", "ok", {"method": "mock_classifier", "class": prediction["predicted_class"]})
            
        except Exception as e:
            state.errors.append(f"Classification failed: {str(e)}")
            state.status = "execution_error"
            state.add_step("execute", "error", {"error": str(e)})
    else:
        state.add_step("execute", "skipped", {"reason": "unknown_route"})
    
    return state