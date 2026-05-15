import json
import os
from datetime import datetime, timedelta

class ApprovalStorageAdapter:
    def __init__(self):
        self.mode = "APPROVAL_FOUNDATION_ONLY"
        self.durable = False

    def get_status(self):
        return {
            "approval_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
            "durable_approval_storage_configured": self.durable,
            "approval_write_endpoint_enabled": False,
            "approval_record_persistence_verified": False,
            "current_mode": self.mode
        }

    def validate_approval_request(self, payload):
        required = ["approval_request_id", "request_id", "requested_by", "requested_at", "approval_scope", "approval_type"]
        for field in required:
            if field not in payload:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Forbidden scope check
        scope = payload.get("approval_scope")
        forbidden = [
            "live_execution", "backend_mutation", "github_mutation", "netlify_mutation",
            "deploy_site", "merge_branch", "push_branch", "create_pr"
        ]
        if scope in forbidden:
            return {"valid": False, "error": f"Forbidden approval scope for current phase: {scope}"}
            
        return {"valid": True}

    def create_approval_request(self, payload):
        return {"ok": False, "error": "APPROVAL_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def get_approval_request(self, approval_request_id):
        return {"ok": False, "error": "APPROVAL_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def list_approval_requests(self):
        return []

    def record_approval_decision(self, payload):
        return {"ok": False, "error": "APPROVAL_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def revoke_approval(self, approval_id):
        return {"ok": False, "error": "APPROVAL_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def check_approval_gate(self, request_id, requested_action_type):
        # Always block execution/mutation in foundation phase
        forbidden_actions = ["execute", "mutate", "deploy", "merge", "push", "create_pr"]
        if any(a in requested_action_type.lower() for a in forbidden_actions):
            return {"allowed": False, "reason": "Execution/Mutation actions are strictly forbidden in this phase."}
        
        return {"allowed": False, "reason": "APPROVAL_STORAGE_NOT_CONFIGURED"}

def get_expiration_policy():
    return {
        "default_expiration_window_minutes": 60,
        "max_expiration_window_minutes": 480,
        "revocation_allowed": True,
        "revocation_audit_required": True,
        "expired_approval_blocks_action": True,
        "approval_cannot_authorize_forbidden_scope": True,
        "no_go_overrides_approval": True
    }
