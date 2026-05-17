from .flow_state import FlowState

def route(state: FlowState) -> FlowState:
    text = state.clean_text.lower()
    
    keywords = ["допоможіть", "помилка", "оплата", "не працює", "питання", "гроші", "пароль"]
    if any(word in text for word in keywords):
        state.route = "support_classification"
        state.schema_name = "ticket_classification_schema"
        state.routing_reason = "Detected support request intent based on keywords"
    else:
        state.route = "unknown"
        state.routing_reason = "Input does not match support classification patterns"

    state.add_step("route", "ok", {"route": state.route, "reason": state.routing_reason})
    return state