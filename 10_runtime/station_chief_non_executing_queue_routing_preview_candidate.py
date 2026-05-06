import json
import hashlib
import re
from pathlib import Path

NON_EXECUTING_QUEUE_ROUTING_PREVIEW_CANDIDATE_MODULE_VERSION = "4.8.0"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_STATUS = "NON_EXECUTING_QUEUE_ROUTING_PREVIEW_LOCAL_RECORD_ONLY"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_PHASE = "Non-Executing Queue Routing Preview Candidate"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_NON_EXECUTING_QUEUE_ROUTING_PREVIEW_CANDIDATE"
DEFAULT_TASK_CANDIDATE_LABEL = "station-chief-sandbox-observation-task-candidate"
DEFAULT_WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME = "non_executing_queue_routing_preview_candidate_record.json"

def _false_booleans() -> dict:
    return {
        "external_actions_taken": False,
        "live_external_action_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "dns_resolution_performed": False,
        "outbound_connection_performed": False,
        "inbound_connection_performed": False,
        "webhook_call_performed": False,
        "credential_vault_access_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "tokens_read": False,
        "api_keys_read": False,
        "oauth_used": False,
        "service_account_used": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "worker_processes_started": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "full_workforce_activation_performed": False,
    }

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str, default_label: str) -> str:
    if not label or not isinstance(label, str):
        return default_label
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", label.lower()).strip("-")
    if not normalized:
        return default_label
    return normalized

def safe_preview_record_name(record_name: str | None) -> str:
    if not record_name or not isinstance(record_name, str):
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if record_name in [".", ".."]:
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    return record_name

def generate_queue_routing_preview_candidate_id(
    command: str,
    task_candidate_label: str,
    worker_template_label: str,
    runtime_version: str = "4.8.0"
) -> str:
    task_norm = normalize_label(task_candidate_label, DEFAULT_TASK_CANDIDATE_LABEL)
    worker_norm = normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL)
    digest = sha256_digest({"command": command, "task": task_norm, "worker": worker_norm, "version": runtime_version})
    return f"non-executing-queue-routing-preview-v4-8-{task_norm}-{worker_norm}-{digest[:12]}"

def create_non_executing_queue_routing_preview_schema() -> dict:
    return {
        "schema_version": "4.8.0",
        "status": "local_record_only",
        "preview_type": "non_executing_queue_routing_preview",
        "required_sections": [
            "queue_routing_preview_approval_gate",
            "hypothetical_task_candidate_reference",
            "worker_template_reference_contract",
            "queue_preview_scope_contract",
            "non_execution_routing_boundary",
            "routing_permission_denial_record",
            "routing_preview_candidate_record",
            "routing_preview_audit_record",
            "routing_preview_readiness_summary",
            "live_queue_orchestration_candidate_bridge",
        ],
        "required_token": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_queue_routing_preview_record_written": False,
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_worker_routing_performed": False,
        "live_task_assignment_performed": False,
        "worker_process_started": False,
        **_false_booleans(),
    }

def create_queue_routing_preview_approval_gate(
    task_candidate_label: str,
    worker_template_label: str,
    preview_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    preview_requested: bool = False
) -> dict:
    token_valid = confirmation_token == NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN
    human_operator_present = bool(human_operator and isinstance(human_operator, str) and human_operator.strip())
    
    local_auth = token_valid and human_operator_present and bool(task_candidate_label) and bool(worker_template_label)
    write_auth = local_auth and bool(preview_output_directory) and preview_requested
    
    return {
        "gate_status": "APPROVED_FOR_ONE_LOCAL_QUEUE_ROUTING_PREVIEW_RECORD" if local_auth else "BLOCKED_PENDING_V4_8_QUEUE_ROUTING_PREVIEW_APPROVAL",
        "local_queue_routing_preview_records_authorized": local_auth,
        "local_queue_routing_preview_record_write_authorized": write_auth,
        **_false_booleans()
    }

def create_hypothetical_task_candidate_reference(approval_gate: dict) -> dict:
    return {"contract_created": approval_gate.get("local_queue_routing_preview_records_authorized"), "task_candidate_is_metadata_only": True, **_false_booleans()}

def create_worker_template_reference_contract(approval_gate: dict) -> dict:
    return {"contract_created": approval_gate.get("local_queue_routing_preview_records_authorized"), "worker_template_is_design_record": True, **_false_booleans()}

def create_queue_preview_scope_contract(approval_gate: dict, task_ref: dict, worker_ref: dict) -> dict:
    passed = approval_gate.get("local_queue_routing_preview_records_authorized") and task_ref.get("contract_created") and worker_ref.get("contract_created")
    return {"scope_status": "PASS" if passed else "BLOCKED", "queue_preview_only": True, **_false_booleans()}

def create_non_execution_routing_boundary(approval_gate: dict, scope: dict) -> dict:
    passed = scope.get("scope_status") == "PASS"
    return {"boundary_status": "PASS" if passed else "BLOCKED", **_false_booleans()}

def create_routing_permission_denial_record(task_label: str, worker_label: str) -> dict:
    return {"denial_active": True, **_false_booleans()}

def create_routing_preview_candidate_record(
    command: str,
    approval_gate: dict,
    task_ref: dict,
    worker_ref: dict,
    scope: dict,
    boundary: dict,
    denial: dict
) -> dict:
    passed = approval_gate.get("local_queue_routing_preview_records_authorized")
    return {"candidate_status": "LOCAL_QUEUE_ROUTING_PREVIEW_CANDIDATE_RECORD_CREATED" if passed else "BLOCKED", **_false_booleans()}

def create_routing_preview_audit_record(candidate: dict) -> dict:
    return {"audit_status": "PASS" if candidate.get("candidate_status") == "LOCAL_QUEUE_ROUTING_PREVIEW_CANDIDATE_RECORD_CREATED" else "BLOCKED", **_false_booleans()}

def create_routing_preview_readiness_summary(audit: dict) -> dict:
    return {"readiness_status": "READY_FOR_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY" if audit.get("audit_status") == "PASS" else "BLOCKED", **_false_booleans()}

def create_live_queue_orchestration_candidate_bridge(summary: dict) -> dict:
    return {"bridge_status": "READY" if summary.get("readiness_status") == "READY_FOR_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY" else "BLOCKED", **_false_booleans()}

def build_queue_routing_preview_record_payload(command: str, task_label: str, worker_label: str, approval_gate: dict, audit: dict) -> dict:
    payload = {"runtime_version": "4.8.0", "preview_type": "non_executing_queue_routing_preview", "command": command, **_false_booleans()}
    payload["payload_digest"] = sha256_digest(payload)
    return payload

def write_non_executing_queue_routing_preview_record(output_dir: str, name: str, payload: dict) -> dict:
    try:
        p = Path(output_dir) / safe_preview_record_name(name)
        p.write_text(canonical_json(payload), encoding="utf-8")
        return {"write_status": "LOCAL_QUEUE_ROUTING_PREVIEW_RECORD_WRITTEN", "local_queue_routing_preview_record_written": True, **_false_booleans()}
    except:
        return {"write_status": "BLOCKED", "local_queue_routing_preview_record_written": False, **_false_booleans()}

def create_non_executing_queue_routing_preview_bundle(
    result: dict | None,
    command: str = "check please",
    task_candidate_label: str = DEFAULT_TASK_CANDIDATE_LABEL,
    worker_template_label: str = DEFAULT_WORKER_TEMPLATE_LABEL,
    preview_output_directory: str | None = None,
    preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    preview_requested: bool = False,
    write_preview_record: bool = False
) -> dict:
    gate = create_queue_routing_preview_approval_gate(task_candidate_label, worker_template_label, preview_output_directory, confirmation_token, human_operator, preview_requested)
    task_ref = create_hypothetical_task_candidate_reference(gate)
    worker_ref = create_worker_template_reference_contract(gate)
    scope = create_queue_preview_scope_contract(gate, task_ref, worker_ref)
    boundary = create_non_execution_routing_boundary(gate, scope)
    denial = create_routing_permission_denial_record(task_candidate_label, worker_template_label)
    candidate = create_routing_preview_candidate_record(command, gate, task_ref, worker_ref, scope, boundary, denial)
    audit = create_routing_preview_audit_record(candidate)
    summary = create_queue_preview_readiness_summary(audit)
    bridge = create_live_queue_orchestration_candidate_bridge(summary)
    payload = build_queue_routing_preview_record_payload(command, task_candidate_label, worker_template_label, gate, audit)
    
    write_res = {"local_queue_routing_preview_record_written": False}
    if write_preview_record and gate.get("local_queue_routing_preview_record_write_authorized"):
        write_res = write_non_executing_queue_routing_preview_record(preview_output_directory, preview_record_name, payload) # type: ignore
        
    return {
        "schema": create_non_executing_queue_routing_preview_schema(),
        "queue_routing_preview_approval_gate": gate,
        "local_queue_routing_preview_record_written": write_res.get("local_queue_routing_preview_record_written", False),
        **_false_booleans()
    }
