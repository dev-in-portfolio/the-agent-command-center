#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION = "4.4.0"
PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_STATUS = "PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_LOCAL_RECORD_ONLY"
PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_PHASE = "Permissioned Worker Task Assignment Candidate"
PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE"
DEFAULT_WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
DEFAULT_TASK_LABEL = "station-chief-sandbox-observation-task"
DEFAULT_TASK_ASSIGNMENT_RECORD_NAME = "permissioned_worker_task_assignment_candidate_record.json"

DANGEROUS_BOOLEAN_FIELDS = [
    "external_actions_taken",
    "live_external_action_performed",
    "live_api_call_performed",
    "network_access_performed",
    "socket_opened",
    "dns_resolution_performed",
    "outbound_connection_performed",
    "inbound_connection_performed",
    "webhook_call_performed",
    "credential_vault_access_performed",
    "credentials_used",
    "secrets_read",
    "environment_read",
    "tokens_read",
    "api_keys_read",
    "oauth_used",
    "service_account_used",
    "deployment_performed",
    "deployment_rollback_performed",
    "production_execution_performed",
    "production_activation_performed",
    "real_external_tool_invocation_performed",
    "real_task_execution_performed",
    "live_task_assignment_performed",
    "live_worker_routing_performed",
    "live_orchestration_performed",
    "worker_processes_started",
    "worker_process_started",
    "task_executed",
    "task_enqueued",
    "real_rollback_performed",
    "real_recovery_performed",
    "processes_terminated",
    "workers_terminated",
    "production_state_changed",
    "repo_files_modified",
    "execution_authorized",
    "full_workforce_activation_performed",
]


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _false_booleans() -> dict:
    return {name: False for name in DANGEROUS_BOOLEAN_FIELDS}


def normalize_label(label: str, default: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", str(label).strip().lower()).strip("-")
    return normalized or default


def safe_task_assignment_record_name(record_name: str | None) -> str:
    if not record_name:
        return DEFAULT_TASK_ASSIGNMENT_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_TASK_ASSIGNMENT_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_TASK_ASSIGNMENT_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_TASK_ASSIGNMENT_RECORD_NAME
    return record_name


def generate_permissioned_worker_task_assignment_candidate_id(
    command: str,
    worker_template_label: str,
    task_label: str,
    runtime_version: str = PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_worker = normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL)
    normalized_task = normalize_label(task_label, DEFAULT_TASK_LABEL)
    digest = sha256_digest(f"{runtime_version}:{command}:{worker_template_label}:{task_label}")
    return (
        "permissioned-worker-task-assignment-candidate-v4-4-"
        f"{normalized_worker}-{normalized_task}-{digest[:12]}"
    )


def create_permissioned_worker_task_assignment_candidate_schema() -> dict:
    return {
        "permissioned_worker_task_assignment_candidate_schema_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "schema_status": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_STATUS,
        "assignment_type": "permissioned_local_worker_task_assignment_record",
        "required_sections": [
            "permissioned_worker_task_assignment_candidate_approval_gate",
            "worker_template_reference_contract",
            "task_label_reference_contract",
            "one_worker_one_task_assignment_scope_contract",
            "non_execution_task_boundary",
            "task_permission_denial_record",
            "worker_task_assignment_candidate_record",
            "task_assignment_audit_record",
            "task_assignment_ledger",
            "task_assignment_readiness_summary",
            "task_assignment_audit_closeout_candidate_bridge",
        ],
        "required_confirmation_token": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_task_assignment_record_written": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_worker_routing_performed": False,
        "live_task_assignment_performed": False,
        **_false_booleans(),
    }


def create_permissioned_worker_task_assignment_candidate_approval_gate(
    worker_template_label: str,
    task_label: str,
    task_assignment_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    assignment_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN
    worker_template_present = bool(worker_template_label and str(worker_template_label).strip())
    task_label_present = bool(task_label and str(task_label).strip())
    human_present = bool(human_operator and str(human_operator).strip())
    output_directory_present = bool(task_assignment_output_directory and str(task_assignment_output_directory).strip())
    local_task_assignment_records_authorized = token_valid and human_present and worker_template_present and task_label_present
    local_task_assignment_record_write_authorized = (
        token_valid
        and human_present
        and worker_template_present
        and task_label_present
        and output_directory_present
        and bool(assignment_requested)
    )
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_WORKER_TASK_ASSIGNMENT_RECORD"
        if local_task_assignment_records_authorized
        else "BLOCKED_PENDING_V4_4_TASK_ASSIGNMENT_APPROVAL"
    )
    return {
        "permissioned_worker_task_assignment_candidate_approval_gate_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL),
        "task_label": task_label,
        "task_label_normalized": normalize_label(task_label, DEFAULT_TASK_LABEL),
        "task_assignment_output_directory": task_assignment_output_directory,
        "human_operator": human_operator,
        "assignment_requested": bool(assignment_requested),
        "gate_status": gate_status,
        "confirmation_token_required": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "worker_template_label_present": worker_template_present,
        "task_label_present": task_label_present,
        "human_operator_present": human_present,
        "local_task_assignment_records_authorized": local_task_assignment_records_authorized,
        "local_task_assignment_record_write_authorized": local_task_assignment_record_write_authorized,
        "task_execution_authorized": False,
        "task_enqueue_authorized": False,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "full_workforce_activation_authorized": False,
        "baseline_preserved": True,
        "local_task_assignment_record_written": False,
        **_false_booleans(),
    }


def create_worker_template_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_task_assignment_records_authorized", False)
    return {
        "worker_template_reference_contract_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "contract_status": "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "worker_template_label": approval_gate.get("worker_template_label"),
        "worker_template_label_normalized": approval_gate.get("worker_template_label_normalized"),
        "worker_template_is_design_record": True,
        "worker_template_is_running_process": False,
        "no_worker_process_start": True,
        "no_task_assignment": True,
        "no_task_execution": True,
        "no_worker_routing": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_label_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_task_assignment_records_authorized", False)
    return {
        "task_label_reference_contract_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "contract_status": "TASK_LABEL_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "task_label": approval_gate.get("task_label"),
        "task_label_normalized": approval_gate.get("task_label_normalized"),
        "task_label_is_metadata_only": True,
        "task_is_enqueued": False,
        "task_is_executed": False,
        "no_tool_calls": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_one_worker_one_task_assignment_scope_contract(
    approval_gate: dict,
    worker_template_reference_contract: dict,
    task_label_reference_contract: dict,
) -> dict:
    pass_ok = (
        approval_gate.get("local_task_assignment_records_authorized", False)
        and worker_template_reference_contract.get("contract_status") == "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED"
        and task_label_reference_contract.get("contract_status") == "TASK_LABEL_REFERENCE_CONTRACT_CREATED"
    )
    return {
        "one_worker_one_task_assignment_scope_contract_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "scope_status": "PASS" if pass_ok else "BLOCKED",
        "exactly_one_worker_template": True,
        "exactly_one_task_label": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
        "no_batch_task_assignment": True,
        "no_department_wide_assignment": True,
        "no_routing_activation": True,
        "no_queue_activation": True,
        "no_process_activation": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_execution_task_boundary(
    approval_gate: dict,
    one_worker_one_task_assignment_scope_contract: dict,
) -> dict:
    pass_ok = (
        approval_gate.get("local_task_assignment_records_authorized", False)
        and one_worker_one_task_assignment_scope_contract.get("scope_status") == "PASS"
    )
    return {
        "non_execution_task_boundary_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "boundary_status": "PASS" if pass_ok else "BLOCKED",
        "task_assignment_record_is_local_metadata_only": True,
        "task_is_not_executable": True,
        "task_is_not_queued": True,
        "task_is_not_running": True,
        "worker_is_not_running": True,
        "worker_cannot_call_tools": True,
        "worker_cannot_route_tasks": True,
        "worker_cannot_access_apis": True,
        "worker_cannot_access_network": True,
        "worker_cannot_access_credentials_secrets_environment": True,
        "worker_cannot_deploy": True,
        "worker_cannot_execute_production": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_permission_denial_record(worker_template_label: str, task_label: str) -> dict:
    return {
        "task_permission_denial_record_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "worker_template_label": worker_template_label,
        "task_label": task_label,
        "task_execution_denied": True,
        "task_enqueue_denied": True,
        "queue_write_denied": True,
        "scheduler_write_denied": True,
        "live_task_assignment_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "worker_process_start_denied": True,
        "api_access_denied": True,
        "network_access_denied": True,
        "socket_access_denied": True,
        "dns_resolution_denied": True,
        "credential_use_denied": True,
        "credential_vault_access_denied": True,
        "secret_reads_denied": True,
        "environment_reads_denied": True,
        "deployment_denied": True,
        "production_execution_denied": True,
        "production_activation_denied": True,
        "github_push_denied": True,
        "external_tool_invocation_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_worker_task_assignment_candidate_record(
    command: str,
    approval_gate: dict,
    worker_template_reference_contract: dict,
    task_label_reference_contract: dict,
    one_worker_one_task_assignment_scope_contract: dict,
    non_execution_task_boundary: dict,
    task_permission_denial_record: dict,
) -> dict:
    candidate_ok = (
        approval_gate.get("local_task_assignment_records_authorized", False)
        and worker_template_reference_contract.get("contract_status") == "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED"
        and task_label_reference_contract.get("contract_status") == "TASK_LABEL_REFERENCE_CONTRACT_CREATED"
        and one_worker_one_task_assignment_scope_contract.get("scope_status") == "PASS"
        and non_execution_task_boundary.get("boundary_status") == "PASS"
    )
    worker_template_label = approval_gate.get("worker_template_label") or DEFAULT_WORKER_TEMPLATE_LABEL
    task_label = approval_gate.get("task_label") or DEFAULT_TASK_LABEL
    candidate_id = generate_permissioned_worker_task_assignment_candidate_id(command, worker_template_label, task_label)
    record = {
        "task_assignment_candidate_id": candidate_id,
        "candidate_status": "LOCAL_WORKER_TASK_ASSIGNMENT_CANDIDATE_RECORD_CREATED" if candidate_ok else "BLOCKED",
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL),
        "task_label": task_label,
        "task_label_normalized": normalize_label(task_label, DEFAULT_TASK_LABEL),
        "human_operator": approval_gate.get("human_operator"),
        "task_permission_denial_record": task_permission_denial_record,
        "assignment_mode": "local_record_only",
        "worker_runtime_state": "not_started",
        "task_runtime_state": "not_started",
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "worker_ready_for_live_assignment": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    record["task_assignment_candidate_digest"] = sha256_digest({k: v for k, v in record.items() if k != "task_assignment_candidate_digest"})
    return record


def create_task_assignment_audit_record(
    approval_gate: dict,
    worker_template_reference_contract: dict,
    task_label_reference_contract: dict,
    one_worker_one_task_assignment_scope_contract: dict,
    non_execution_task_boundary: dict,
    task_permission_denial_record: dict,
    worker_task_assignment_candidate_record: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "worker_template_reference_contract": sha256_digest(worker_template_reference_contract),
        "task_label_reference_contract": sha256_digest(task_label_reference_contract),
        "one_worker_one_task_assignment_scope_contract": sha256_digest(one_worker_one_task_assignment_scope_contract),
        "non_execution_task_boundary": sha256_digest(non_execution_task_boundary),
        "task_permission_denial_record": sha256_digest(task_permission_denial_record),
        "worker_task_assignment_candidate_record": sha256_digest(worker_task_assignment_candidate_record),
    }
    audit_ok = (
        worker_task_assignment_candidate_record.get("candidate_status") == "LOCAL_WORKER_TASK_ASSIGNMENT_CANDIDATE_RECORD_CREATED"
        and not any(worker_task_assignment_candidate_record.get(name, False) for name in DANGEROUS_BOOLEAN_FIELDS)
    )
    audit_record = {
        "task_assignment_audit_record_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "section_digests": section_digests,
        "candidate_record_digest": sha256_digest(worker_task_assignment_candidate_record),
        "candidate_record_created": worker_task_assignment_candidate_record.get("candidate_status") == "LOCAL_WORKER_TASK_ASSIGNMENT_CANDIDATE_RECORD_CREATED",
        "all_dangerous_booleans_false": True,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    audit_record["audit_digest"] = sha256_digest({k: v for k, v in audit_record.items() if k != "audit_digest"})
    return audit_record


def create_task_assignment_ledger(task_assignment_audit_record: dict) -> dict:
    ledger_ok = task_assignment_audit_record.get("audit_status") == "PASS"
    ledger_record = {
        "task_assignment_ledger_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "ledger_status": "PASS" if ledger_ok else "BLOCKED",
        "audit_record_digest": sha256_digest(task_assignment_audit_record),
        "all_dangerous_booleans_false": True,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    ledger_record["ledger_digest"] = sha256_digest({k: v for k, v in ledger_record.items() if k != "ledger_digest"})
    return ledger_record


def create_task_assignment_readiness_summary(task_assignment_ledger: dict) -> dict:
    ready = task_assignment_ledger.get("ledger_status") == "PASS"
    return {
        "task_assignment_readiness_summary_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Task Assignment Audit Closeout Candidate",
        "v4_5_built": False,
        "no_task_execution_yet": True,
        "no_task_enqueue_yet": True,
        "no_live_task_assignment_yet": True,
        "no_worker_routing_yet": True,
        "no_process_start": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_assignment_audit_closeout_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE"
    return {
        "task_assignment_audit_closeout_candidate_bridge_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_5_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE" if ready else "BLOCKED",
        "ready_for_v4_5": ready,
        "no_task_execution_in_v4_4": True,
        "no_task_enqueue_in_v4_4": True,
        "no_worker_routing_in_v4_4": True,
        "no_worker_process_start_in_v4_4": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def build_task_assignment_record_payload(
    command: str,
    worker_template_label: str,
    task_label: str,
    human_operator: str | None,
    task_assignment_output_directory: str | None,
    task_assignment_record_name: str | None,
    approval_gate: dict,
    worker_task_assignment_candidate_record: dict,
    task_assignment_audit_record: dict,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "assignment_type": "permissioned_local_worker_task_assignment_record",
        "command": command,
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL),
        "task_label": task_label,
        "task_label_normalized": normalize_label(task_label, DEFAULT_TASK_LABEL),
        "human_operator": human_operator,
        "task_assignment_output_directory": task_assignment_output_directory,
        "task_assignment_record_name": safe_task_assignment_record_name(task_assignment_record_name),
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "task_assignment_candidate_id": worker_task_assignment_candidate_record.get("task_assignment_candidate_id"),
        "task_permission_denial_record": worker_task_assignment_candidate_record.get("task_permission_denial_record"),
        "task_assignment_audit_digest": task_assignment_audit_record.get("audit_digest"),
        "worker_task_assignment_candidate_record": worker_task_assignment_candidate_record,
        "task_assignment_audit_record": task_assignment_audit_record,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "safety_booleans": {
            "task_executed": False,
            "task_enqueued": False,
            "worker_process_started": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "full_workforce_activation_performed": False,
            **_false_booleans(),
        },
        "baseline_preserved": True,
    }
    payload["payload_digest"] = sha256_digest({k: v for k, v in payload.items() if k != "payload_digest"})
    return payload


def write_permissioned_worker_task_assignment_record(
    task_assignment_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(task_assignment_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_task_assignment_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    try:
        record_path.relative_to(output_dir)
    except ValueError:
        return create_blocked_task_assignment_write_record("record path escaped approved output directory")
    record_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "task_assignment_write_record_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "write_status": "LOCAL_WORKER_TASK_ASSIGNMENT_RECORD_WRITTEN",
        "local_task_assignment_record_written": True,
        "files_written_count": 1,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "record_name": safe_name,
        "record_path": str(record_path),
        "task_assignment_output_directory": str(output_dir),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_task_assignment_write_record(reason: str) -> dict:
    return {
        "task_assignment_write_record_version": PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "reason": reason,
        "local_task_assignment_record_written": False,
        "files_written_count": 0,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_permissioned_worker_task_assignment_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    worker_template_label: str | None = None,
    task_label: str | None = None,
    task_assignment_output_directory: str | None = None,
    task_assignment_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    assignment_requested: bool = False,
    write_task_assignment_record: bool = False,
) -> dict:
    command = command or "check please"
    worker_template_label = worker_template_label or DEFAULT_WORKER_TEMPLATE_LABEL
    task_label = task_label or DEFAULT_TASK_LABEL
    approval_gate = create_permissioned_worker_task_assignment_candidate_approval_gate(
        worker_template_label=worker_template_label,
        task_label=task_label,
        task_assignment_output_directory=task_assignment_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        assignment_requested=assignment_requested,
    )
    worker_template_reference_contract = create_worker_template_reference_contract(approval_gate)
    task_label_reference_contract = create_task_label_reference_contract(approval_gate)
    one_worker_one_task_assignment_scope_contract = create_one_worker_one_task_assignment_scope_contract(
        approval_gate,
        worker_template_reference_contract,
        task_label_reference_contract,
    )
    non_execution_task_boundary = create_non_execution_task_boundary(
        approval_gate,
        one_worker_one_task_assignment_scope_contract,
    )
    task_permission_denial_record = create_task_permission_denial_record(worker_template_label, task_label)
    worker_task_assignment_candidate_record = create_worker_task_assignment_candidate_record(
        command,
        approval_gate,
        worker_template_reference_contract,
        task_label_reference_contract,
        one_worker_one_task_assignment_scope_contract,
        non_execution_task_boundary,
        task_permission_denial_record,
    )
    task_assignment_audit_record = create_task_assignment_audit_record(
        approval_gate,
        worker_template_reference_contract,
        task_label_reference_contract,
        one_worker_one_task_assignment_scope_contract,
        non_execution_task_boundary,
        task_permission_denial_record,
        worker_task_assignment_candidate_record,
    )
    task_assignment_ledger = create_task_assignment_ledger(task_assignment_audit_record)
    task_assignment_readiness_summary = create_task_assignment_readiness_summary(task_assignment_ledger)
    task_assignment_audit_closeout_candidate_bridge = create_task_assignment_audit_closeout_candidate_bridge(task_assignment_readiness_summary)
    task_assignment_record_payload = build_task_assignment_record_payload(
        command,
        worker_template_label,
        task_label,
        human_operator,
        task_assignment_output_directory,
        task_assignment_record_name,
        approval_gate,
        worker_task_assignment_candidate_record,
        task_assignment_audit_record,
    )
    if write_task_assignment_record and approval_gate.get("local_task_assignment_record_write_authorized", False):
        if not task_assignment_output_directory:
            task_assignment_write_record = create_blocked_task_assignment_write_record("task assignment output directory missing")
        else:
            task_assignment_write_record = write_permissioned_worker_task_assignment_record(
                task_assignment_output_directory,
                task_assignment_record_name or DEFAULT_TASK_ASSIGNMENT_RECORD_NAME,
                task_assignment_record_payload,
            )
    elif write_task_assignment_record:
        task_assignment_write_record = create_blocked_task_assignment_write_record("task assignment write not authorized")
    else:
        task_assignment_write_record = create_blocked_task_assignment_write_record("task assignment record write not requested")
    local_task_assignment_record_written = task_assignment_write_record.get("local_task_assignment_record_written", False)
    bundle = {
        "schema": create_permissioned_worker_task_assignment_candidate_schema(),
        "permissioned_worker_task_assignment_candidate_approval_gate": approval_gate,
        "worker_template_reference_contract": worker_template_reference_contract,
        "task_label_reference_contract": task_label_reference_contract,
        "one_worker_one_task_assignment_scope_contract": one_worker_one_task_assignment_scope_contract,
        "non_execution_task_boundary": non_execution_task_boundary,
        "task_permission_denial_record": task_permission_denial_record,
        "worker_task_assignment_candidate_record": worker_task_assignment_candidate_record,
        "task_assignment_audit_record": task_assignment_audit_record,
        "task_assignment_ledger": task_assignment_ledger,
        "task_assignment_readiness_summary": task_assignment_readiness_summary,
        "task_assignment_audit_closeout_candidate_bridge": task_assignment_audit_closeout_candidate_bridge,
        "task_assignment_record_payload": task_assignment_record_payload,
        "task_assignment_write_record": task_assignment_write_record,
        "local_task_assignment_record_written": local_task_assignment_record_written,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest({k: v for k, v in bundle.items() if k != "bundle_digest"})
    return bundle
