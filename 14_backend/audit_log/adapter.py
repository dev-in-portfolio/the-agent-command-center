import json
import os
import hashlib
from datetime import datetime

class AuditStorageAdapter:
    def __init__(self):
        self.mode = "AUDIT_FOUNDATION_ONLY"
        self.durable = False
        self.hash_algorithm = "SHA256"

    def get_status(self):
        return {
            "audit_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
            "durable_audit_storage_configured": self.durable,
            "append_endpoint_enabled": False,
            "immutable_chain_verified": False,
            "persistence_verified": False,
            "hash_algorithm": self.hash_algorithm,
            "current_mode": self.mode
        }

    def validate_audit_event(self, payload):
        required = ["audit_event_id", "timestamp", "actor_id", "event_type", "event_category"]
        for field in required:
            if field not in payload:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Forbidden category check
        category = payload.get("event_category")
        forbidden = [
            "command_executed", "backend_mutated", "github_mutated", "netlify_mutated",
            "deployment_triggered", "branch_merged", "branch_pushed", "pr_created"
        ]
        if category in forbidden:
            return {"valid": False, "error": f"Forbidden event category for current phase: {category}"}
            
        return {"valid": True}

    def compute_event_hash(self, payload):
        # Canonical serialization
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def append_audit_event(self, payload):
        return {"ok": False, "error": "AUDIT_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def get_audit_event(self, audit_event_id):
        return {"ok": False, "error": "AUDIT_STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def list_audit_events(self):
        return []

    def verify_audit_chain(self):
        return {"ok": False, "error": "NO_DURABLE_CHAIN_CONFIGURED", "current_mode": self.mode}

def get_retention_policy():
    return {
        "retention_class": "STANDARD_OPERATIONAL",
        "redaction_allowed_for_payload_summary": True,
        "immutable_core_fields": True,
        "pii_policy": "NO_PII_ALLOWED",
        "secret_redaction_required": True,
        "token_redaction_required": True,
        "no_secret_storage": True
    }
