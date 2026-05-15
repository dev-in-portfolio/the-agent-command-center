import json
import os
from datetime import datetime

class DryRunAdapter:
    def __init__(self):
        self.mode = "DRY_RUN_FOUNDATION_ONLY"
        self.durable = False

    def get_status(self):
        return {
            "dry_run_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
            "dry_run_execution_enabled": False,
            "durable_dry_run_storage_configured": self.durable,
            "command_execution_enabled": False,
            "external_api_simulation_enabled": False,
            "evidence_persistence_verified": False,
            "current_mode": self.mode
        }

    def validate_dry_run_request(self, payload):
        required = ["dry_run_request_id", "request_id", "requested_by", "requested_at", "requested_action_type"]
        for field in required:
            if field not in payload:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Forbidden check
        action = payload.get("requested_action_type", "").lower()
        forbidden_actions = ["execute", "mutate", "deploy", "merge", "push", "create_pr"]
        if any(a in action for a in forbidden_actions):
             return {"valid": False, "error": f"Forbidden action type for dry-run: {action}"}
             
        return {"valid": True}

    def generate_dry_run_plan(self, payload):
        # Deterministic no-op planner
        return {
            "dry_run_plan_id": f"PLAN-NOOP-{datetime.now().strftime('%Y%m%d')}",
            "plan_type": "deterministic_noop",
            "target_system": payload.get("target_system", "unknown"),
            "planned_steps": [{"step": 1, "action": "noop_simulation", "description": "Deterministic foundation no-op."}],
            "expected_noop_behavior": "safe_contract_validation_only"
        }

    def run_dry_run(self, payload):
        return {"ok": False, "error": "DRY_RUN_EXECUTION_NOT_CONFIGURED", "current_mode": self.mode}

    def get_dry_run_result(self, dry_run_result_id):
        return {"ok": False, "error": "DRY_RUN_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def list_dry_run_results(self):
        return []

    def package_dry_run_evidence(self, dry_run_result_id):
        return {"ok": False, "error": "DRY_RUN_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}
