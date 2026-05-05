import uuid

class CrewWorkflow:
    def __init__(self, triager, extractor, reviewer, fallback_handler):
        self.triager = triager
        self.extractor = extractor
        self.reviewer = reviewer
        self.fallback = fallback_handler

    def process_case(self, case_id: str, input_text: str) -> dict:
        log_entry = {
            "case_id": case_id,
            "input": input_text,
            "fallback_triggered": False,
            "status": "pending"
        }

        # 1. Triager
        triage_res = self.triager.process(input_text)
        log_entry["triager_output"] = triage_res
        
        # 2. Extractor
        extract_res = self.extractor.process(input_text, triage_res.get("route", "full_schema"))
        log_entry["extractor_output"] = extract_res

        # 3. Reviewer
        review_res = self.reviewer.review(input_text, extract_res)
        log_entry["reviewer_output"] = review_res

        # 4. Fallback / Repair Logic
        final_output = extract_res
        
        if review_res["verdict"] == "accept":
            log_entry["status"] = "accepted"
            
        elif review_res["verdict"] == "repair_needed":
            log_entry["fallback_triggered"] = True
            repair_res = self.fallback.run_repair(input_text, extract_res, review_res["issues"])
            
            if repair_res:
                 second_review = self.reviewer.review(input_text, repair_res)
                 if second_review["verdict"] == "accept":
                     final_output = repair_res
                     log_entry["status"] = "accepted_after_repair"
                     log_entry["fallback_output"] = {"action": "repair_success", "repaired_data": repair_res}
                 else:
                     final_output = self.fallback.get_safe_failure(input_text, "Repair failed to fix all issues", repair_res)
                     log_entry["status"] = "failed_after_repair"
                     log_entry["fallback_output"] = {"action": "safe_failure"}
            else:
                 final_output = self.fallback.get_safe_failure(input_text, "Repair exception", extract_res)
                 log_entry["status"] = "failed_repair_exception"
                 
        elif review_res["verdict"] == "fallback_needed":
             log_entry["fallback_triggered"] = True
             final_output = self.fallback.get_safe_failure(input_text, "Reviewer flagged for manual review (Contradiction)", extract_res)
             log_entry["status"] = "manual_review_required"
             log_entry["fallback_output"] = {"action": "sent_to_manual_review"}

        log_entry["final_output"] = final_output
        return log_entry