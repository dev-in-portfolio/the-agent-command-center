import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from approval_gate.adapter import ApprovalStorageAdapter
from audit_log.adapter import AuditStorageAdapter
from auth.permission_check import check_permission
from dry_run.adapter import DryRunAdapter
from request_storage.adapter import RequestStorageAdapter

ROOT = Path(__file__).resolve().parent


def _load_json(filename):
    path = ROOT / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


STATE_MODEL = _load_json("state_model.json")
RUNTIME_RESULT_SCHEMA = _load_json("runtime_result_schema.json")
PERSISTENCE_STRATEGY = _load_json("persistence_adapter_strategy.json")
DEMO_FIXTURE = _load_json("demo_fixture.json")


class RequestLifecycleOrchestrator:
    def __init__(self, persistence_adapter=None):
        self.request_storage = RequestStorageAdapter()
        self.dry_run = DryRunAdapter()
        self.approval_gate = ApprovalStorageAdapter()
        self.audit_log = AuditStorageAdapter()
        self.persistence_adapter = persistence_adapter

    def validate_request_structure(self, payload):
        required = ["title", "intent", "requested_action"]
        missing = [field for field in required if not str(payload.get(field, "")).strip()]
        forbidden_terms = [
            "execute",
            "execution",
            "deploy",
            "merge",
            "push",
            "create_pr",
            "mutate",
            "shell",
        ]
        combined = " ".join(
            str(payload.get(field, ""))
            for field in ["title", "intent", "requested_action", "scope", "target_system"]
        ).lower()
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

    def attach_demo_auth_context(self, payload):
        actor_id = str(payload.get("actor_id") or DEMO_FIXTURE.get("actor_id") or "demo_operator")
        actor_role = str(payload.get("actor_role") or DEMO_FIXTURE.get("actor_role") or "operator")
        permission_preview = check_permission(actor_id, "draft_request")
        return {
            "actor_id": actor_id,
            "actor_role": actor_role,
            "auth_mode": "DEMO_DETERMINISTIC",
            "permission_preview": permission_preview,
            "live_auth_configured": False,
        }

    def classify_risk(self, payload):
        requested_action = str(payload.get("requested_action") or payload.get("requested_action_type") or "").lower()
        if any(term in requested_action for term in ["execute", "deploy", "merge", "push", "create_pr", "mutate"]):
            level = "high"
        else:
            level = "low"
        return {
            "risk_level": level,
            "risk_classification": "placeholder",
            "reason": "No real auth provider or durable persistence is configured yet.",
        }

    def _persist_local_lifecycle(self, payload, auth_context, validation_result, dry_run_result):
        adapter = self.persistence_adapter
        if adapter is None:
            return {
                "available": False,
                "storage_state": "storage_not_configured",
                "local_persistence_enabled": False,
                "production_persistence_configured": False,
                "request_record": None,
                "transition_states": [],
            }

        request_payload = {
            "request_id": str(payload.get("request_id") or DEMO_FIXTURE.get("request_id") or "mvp1-request"),
            "actor_id": auth_context["actor_id"],
            "actor_role": auth_context["actor_role"],
            "title": payload.get("title", ""),
            "intent": payload.get("intent", ""),
            "requested_action": payload.get("requested_action_type") or payload.get("requested_action", "planning_review_only"),
            "lifecycle_state": "request_received",
        }

        create_result = adapter.create_request(request_payload)
        request_record = create_result.get("request") if isinstance(create_result, dict) else create_result
        request_id = (request_record or {}).get("id") or request_payload["request_id"]
        transition_states = [
            "request_received",
            "request_validated",
            "storage_not_configured",
            "dry_run_plan_generated",
            "approval_required",
            "audit_event_prepared",
            "blocked_before_execution",
            "ready_for_human_review",
        ]
        transition_results = []
        for state in transition_states[1:]:
            if hasattr(adapter, "transition_request_state"):
                transition_results.append(
                    adapter.transition_request_state(
                        request_id,
                        state,
                        event_summary=f"Local runtime transition: {state}.",
                    )
                )
            elif hasattr(adapter, "update_request_state"):
                transition_results.append(
                    adapter.update_request_state(
                        request_id,
                        state,
                        event_summary=f"Local runtime transition: {state}.",
                    )
                )
        final_request = None
        if hasattr(adapter, "get_request"):
            request_lookup = adapter.get_request(request_id)
            final_request = request_lookup.get("request") if isinstance(request_lookup, dict) else request_lookup

        lifecycle_events = []
        if hasattr(adapter, "get_lifecycle_events"):
            event_lookup = adapter.get_lifecycle_events(request_id)
            lifecycle_events = event_lookup.get("events") if isinstance(event_lookup, dict) else event_lookup

        return {
            "available": True,
            "storage_state": "local_sqlite_persistence_available",
            "local_persistence_enabled": True,
            "production_persistence_configured": False,
            "validation_result": validation_result,
            "dry_run_preview": dry_run_result.get("plan", {}),
            "request_record": final_request or request_record,
            "transition_states": transition_states,
            "transition_results": transition_results,
            "lifecycle_events": lifecycle_events,
        }

    def build_storage_result(self, payload, auth_context=None, validation_result=None, dry_run_result=None):
        storage_payload = {
            "title": payload.get("title", ""),
            "intent": payload.get("intent", ""),
            "scope": payload.get("scope", "mvp1-request-lifecycle"),
            "requested_action_type": payload.get("requested_action_type") or payload.get("requested_action", "planning_review_only"),
        }
        validation = self.request_storage.validate_request_draft(storage_payload)
        create_attempt = self.request_storage.create_request_draft(storage_payload)
        local_persistence = self._persist_local_lifecycle(
            payload,
            auth_context or {"actor_id": "demo_operator", "actor_role": "operator"},
            validation_result or validation,
            dry_run_result or {},
        )
        return {
            "validation": validation,
            "create_attempt": create_attempt,
            "storage_state": local_persistence.get("storage_state", "storage_not_configured"),
            "persistence_enabled": bool(self.persistence_adapter),
            "durable_storage_configured": bool(self.persistence_adapter),
            "local_persistence": local_persistence,
        }

    def build_dry_run_result(self, payload):
        now = _utc_now()
        dry_run_request = {
            "dry_run_request_id": f"DRYREQ-{payload.get('request_id', 'mvp1-demo')}",
            "request_id": payload.get("request_id", "mvp1-demo-request"),
            "requested_by": payload.get("actor_id", "demo_operator"),
            "requested_by_role": payload.get("actor_role", "operator"),
            "requested_at": now,
            "source_phase": "MVP-1",
            "requested_action_type": payload.get("requested_action_type") or payload.get("requested_action", "planning_review_only"),
            "planning_scope": [payload.get("scope", "dashboard-planning")],
            "target_system": payload.get("target_system", "the-agent-command-center-dashboard"),
            "risk_classification": "low",
            "approval_reference": "approval_required",
            "audit_reference": "audit_event_prepared",
            "no_go_flags": [
                "no_real_deploy",
                "no_external_mutation",
                "no_live_auth_provider",
                "no_durable_persistence"
            ],
            "current_state": "request_validated",
            "reason_summary": "Planning-only request blocked before execution.",
        }
        validation = self.dry_run.validate_dry_run_request(dry_run_request)
        plan = self.dry_run.generate_dry_run_plan(dry_run_request)
        return {
            "validation": validation,
            "plan": plan,
            "execution_enabled": False,
            "storage_enabled": False,
            "blocked_before_execution": True,
        }

    def build_approval_requirement(self, payload):
        gate = self.approval_gate.check_approval_gate(
            payload.get("request_id", "mvp1-demo-request"),
            payload.get("requested_action_type") or payload.get("requested_action", "planning_review_only"),
        )
        return {
            "gate": gate,
            "approval_required": True,
            "reason": "Real auth and durable approval storage are not configured.",
        }

    def build_audit_summary(self, payload):
        event = {
            "audit_event_id": f"AUDIT-{payload.get('request_id', 'mvp1-demo-request')}",
            "timestamp": _utc_now(),
            "actor_id": payload.get("actor_id", "demo_operator"),
            "event_type": "request_lifecycle_preview",
            "event_category": "planning_event",
            "request_id": payload.get("request_id", "mvp1-demo-request"),
            "lifecycle_state": "blocked_before_execution",
            "details": "Request reviewed by the MVP-1 runtime scaffold.",
        }
        validation = self.audit_log.validate_audit_event(event)
        return {
            "validation": validation,
            "event_hash": self.audit_log.compute_event_hash(event),
            "append_attempt": {"ok": False, "error": "AUDIT_STORAGE_NOT_CONFIGURED"},
            "audit_state": "audit_event_prepared",
        }

    def run(self, payload):
        received_at = _utc_now()
        request_id = str(payload.get("request_id") or DEMO_FIXTURE.get("request_id") or "mvp1-request")
        auth_context = self.attach_demo_auth_context(payload)
        validation_result = self.validate_request_structure(payload)
        risk = self.classify_risk(payload)
        dry_run_result = self.build_dry_run_result(payload)
        storage_result = self.build_storage_result(
            payload,
            auth_context=auth_context,
            validation_result=validation_result,
            dry_run_result=dry_run_result,
        )
        approval_requirement = self.build_approval_requirement(payload)
        audit_summary = self.build_audit_summary(payload)
        blocked_operations = [
            "execute_command",
            "mutate_backend",
            "mutate_github",
            "mutate_netlify",
            "deploy_site",
            "merge_branch",
            "push_branch",
            "create_pr",
            "trigger_workflow",
            "local_process_execution",
        ]
        no_go_flags = [
            "real_auth_provider_missing",
            "durable_persistence_missing",
            "dry_run_execution_disabled",
            "external_mutation_disabled",
            "real_automation_disabled",
        ]
        return {
            "runtime_result_id": f"RUNTIME-{request_id}",
            "request_id": request_id,
            "actor_id": auth_context["actor_id"],
            "actor_role": auth_context["actor_role"],
            "received_at": received_at,
            "lifecycle_state": "ready_for_human_review",
            "blocked_state": "blocked_before_execution",
            "validation_result": validation_result,
            "storage_result": storage_result,
            "dry_run_result": dry_run_result,
            "approval_requirement": approval_requirement,
            "audit_summary": audit_summary,
            "no_go_flags": no_go_flags,
            "blocked_operations": blocked_operations,
            "recommended_next_action": "choose_storage_provider_and_auth_provider_then_build_real_request_persistence",
            "real_execution_enabled": False,
            "external_mutation_enabled": False,
            "persistence_enabled": bool(self.persistence_adapter),
            "local_persistence_enabled": bool(self.persistence_adapter),
            "production_persistence_configured": False,
            "risk_classification": risk,
            "demo_auth_context": auth_context,
            "state_flow": STATE_MODEL.get("lifecycle_states", []),
            "current_recommendation": STATE_MODEL.get("current_recommendation", []),
        }


def load_demo_fixture():
    return dict(DEMO_FIXTURE)


def main():
    runtime = RequestLifecycleOrchestrator()
    result = runtime.run(load_demo_fixture())
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=False))
