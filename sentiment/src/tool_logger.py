import json
import datetime
import os

LOG_FILE = "../docs/tool_logs_lab12.jsonl"

def log_tool_call(task_id: str, tool_name: str, input_data: dict, output_data: dict, success: bool, error_msg: str = None):
    """Зберігає лог виклику інструмента у JSONL форматі."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Формуємо запис
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "task_id": task_id,
        "tool_name": tool_name,
        "input": input_data,
        "output": output_data,
        "success": success,
        "error": error_msg
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")