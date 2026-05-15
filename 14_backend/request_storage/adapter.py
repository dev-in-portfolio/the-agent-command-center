import json
import os
from datetime import datetime

class RequestStorageAdapter:
    def __init__(self):
        self.mode = "STORAGE_FOUNDATION_ONLY"
        self.durable = False

    def get_status(self):
        return {
            "storage_foundation_status": "READY_FOR_FOUNDATION_REVIEW_ONLY",
            "durable_storage_configured": self.durable,
            "write_endpoint_enabled": False,
            "persistence_verified": False,
            "current_mode": self.mode
        }

    def validate_request_draft(self, payload):
        # Implementation of validation logic
        required = ["title", "intent", "scope", "requested_action_type"]
        for field in required:
            if field not in payload:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Forbidden checks
        intent = payload.get("intent", "").lower()
        forbidden_keywords = ["execute", "mutate", "deploy", "merge", "push", "delete"]
        for kw in forbidden_keywords:
            if kw in intent:
                return {"valid": False, "error": f"Forbidden intent keyword: {kw}"}
        
        return {"valid": True}

    def create_request_draft(self, payload):
        return {"ok": False, "error": "STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def get_request_draft(self, request_id):
        return {"ok": False, "error": "STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def list_request_drafts(self):
        return []

    def update_request_draft(self, request_id, payload):
        return {"ok": False, "error": "STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

    def archive_request_draft(self, request_id):
        return {"ok": False, "error": "STORAGE_NOT_CONFIGURED", "current_mode": self.mode}

def generate_request_id():
    now = datetime.now()
    return f"REQ-DEMO-{now.strftime('%Y%m%d-%H%M%S')}"
