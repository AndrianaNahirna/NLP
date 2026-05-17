from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FlowState:
    case_id: str
    raw_text: str
    clean_text: str = ""
    status: str = "initialized"
    
    route: Optional[str] = None
    schema_name: Optional[str] = None
    routing_reason: Optional[str] = None
    
    tool_outputs: Dict[str, Any] = field(default_factory=dict)
    validation_result: Dict[str, Any] = field(default_factory=dict)
    fallback_result: Dict[str, Any] = field(default_factory=dict)
    final_output: Optional[Dict[str, Any]] = None
    
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fallback_triggered: bool = False
    
    steps: List[Dict[str, Any]] = field(default_factory=list)

    def add_step(self, step_name: str, status: str, details: Dict[str, Any] = None):
        step_data = {"step": step_name, "status": status}
        if details:
            step_data.update(details)
        self.steps.append(step_data)