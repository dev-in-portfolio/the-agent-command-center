from __future__ import annotations

import re
from pathlib import Path

from product_runtime.persistence.sqlite_adapter import SQLiteRequestPersistenceAdapter


DEFAULT_LIFECYCLE_STATES = [
    "request_received",
    "request_validated",
    "storage_not_configured",
    "dry_run_plan_generated",
    "approval_required",
    "audit_event_prepared",
    "blocked_before_execution",
    "ready_for_human_review",
]


def validate_request_payload(payload):
    required = ["title", "intent", "requested_action"]
    missing = [field for field in required if not str(payload.get(field, "")).strip()]
    combined = " ".join(
        str(payload.get(field, ""))
        for field in ["title", "intent", "requested_action", "scope", "target_system"]
    ).lower()
    forbidden_terms = ["execute", "execution", "deploy", "merge", "push", "create_pr", "mutate", "shell"]
    blocked_terms = [
        term for term in forbidden_terms
        if re.search(rf"\\b{re.escape(term)}\\b", combined)
    ]
    return {
        "valid": not missing and not blocked_terms,
        "missing_fields": missing,
        "blocked_terms": blocked_terms,
        "status": "request_validated" if not missing and not blocked_terms else "request_rejected",
    }


class RequestRepository:
    def __init__(self, db_path=None, adapter=None):
        self.adapter = adapter or SQLiteRequestPersistenceAdapter(db_path=db_path)

    def initialize_local_dev_database(self):
        return self.adapter.initialize_local_dev_database()

    def create_request(self, payload):
        validation = validate_request_payload(payload)
        if not validation["valid"]:
            return {
                "ok": False,
                "error": "REQUEST_VALIDATION_FAILED",
                "validation_result": validation,
            }
        request_payload = dict(payload)
        request_payload.setdefault("lifecycle_state", "request_received")
        stored = self.adapter.create_request(request_payload)
        return {
            "ok": True,
            "validation_result": validation,
            "request": stored,
        }

    def get_request(self, request_id):
        request = self.adapter.get_request(request_id)
        return {
            "ok": bool(request),
            "request": request,
        }

    def list_requests(self, limit=50):
        return {
            "ok": True,
            "requests": self.adapter.list_requests(limit=limit),
        }

    def transition_request_state(self, request_id, next_state, event_summary=None):
        updated = self.adapter.update_request_state(request_id, next_state, event_summary=event_summary)
        return {
            "ok": True,
            "request": updated,
            "next_state": next_state,
        }

    def record_lifecycle_event(self, request_id, event_type, event_summary):
        event = self.adapter.add_lifecycle_event(request_id, event_type, event_summary)
        return {
            "ok": True,
            "event": event,
        }

    def get_lifecycle_events(self, request_id):
        return {
            "ok": True,
            "events": self.adapter.get_lifecycle_events(request_id),
        }

    def close(self):
        self.adapter.close()
