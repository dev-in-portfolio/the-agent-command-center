#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION = "4.3.0"
LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_STATUS = "LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_LOCAL_RECORD_ONLY"
LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_PHASE = "Limited Live Worker Activation Candidate"
LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE"
DEFAULT_WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
DEFAULT_WORKER_ACTIVATION_RECORD_NAME = "limited_live_worker_activation_candidate_record.json"

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


def normalize_worker_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.strip().lower()).strip("-")
    return normalized or DEFAULT_WORKER_TEMPLATE_LABEL


def safe_activation_record_name(record_name: str | None) -> str:
    if not record_name:
        return DEFAULT_WORKER_ACTIVATION_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_WORKER_ACTIVATION_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_WORKER_ACTIVATION_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_WORKER_ACTIVATION_RECORD_NAME
    return record_name


def generate_limited_live_worker_activation_candidate_id(
    command: str,
    worker_template_label: str,
    runtime_version: str = LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_label = normalize_worker_label(worker_template_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{worker_template_label}")
    return f"limited-live-worker-activation-candidate-v4-3-{normalized_label}-{digest[:12]}"


def create_limited_live_worker_activation_candidate_schema() -> dict:
    return {
        "limited_live_worker_activation_candidate_schema_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "schema_status": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_STATUS,
        "activation_type": "limited_local_worker_activation_record",
        "required_sections": [
            "limited_live_worker_activation_candidate_approval_gate",
            "worker_template_reference_contract",
            "one_worker_activation_scope_contract",
            "non_execution_worker_boundary",
            "worker_permission_denial_record",
            "worker_activation_candidate_record",
            "worker_activation_audit_record",
            "worker_activation_ledger",
            "worker_activation_readiness_summary",
            "permissioned_worker_task_assignment_candidate_bridge",
        ],
        "required_confirmation_token": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_worker_activation_record_written": False,
        "worker_process_started": False,
        "live_worker_routing_performed": False,
        "live_task_assignment_performed": False,
        **_false_booleans(),
    }


def create_limited_live_worker_activation_candidate_approval_gate(
    worker_template_label: str,
    activation_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    activation_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_APPROVAL_TOKEN
    worker_template_present = bool(worker_template_label and str(worker_template_label).strip())
    human_present = bool(human_operator and str(human_operator).strip())
    activation_output_present = bool(activation_output_directory and str(activation_output_directory).strip())
    local_worker_activation_records_authorized = token_valid and human_present and worker_template_present
    local_worker_activation_record_write_authorized = (
        token_valid
        and human_present
        and worker_template_present
        and activation_output_present
        and bool(activation_requested)
    )
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_WORKER_ACTIVATION_RECORD"
        if local_worker_activation_records_authorized
        else "BLOCKED_PENDING_V4_3_WORKER_ACTIVATION_APPROVAL"
    )
    return {
        "limited_live_worker_activation_candidate_approval_gate_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_worker_label(worker_template_label),
        "activation_output_directory": activation_output_directory,
        "human_operator": human_operator,
        "activation_requested": bool(activation_requested),
        "gate_status": gate_status,
        "confirmation_token_required": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "worker_template_label_present": worker_template_present,
        "local_worker_activation_records_authorized": local_worker_activation_records_authorized,
        "local_worker_activation_record_write_authorized": local_worker_activation_record_write_authorized,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "full_workforce_activation_authorized": False,
        "baseline_preserved": True,
        "local_worker_activation_record_written": False,
        **_false_booleans(),
    }


def create_worker_template_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_worker_activation_records_authorized", False)
    return {
        "worker_template_reference_contract_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "contract_status": "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "worker_template_label": approval_gate.get("worker_template_label"),
        "worker_template_label_normalized": approval_gate.get("worker_template_label_normalized"),
        "worker_template_is_design_record": True,
        "worker_template_is_running_process": False,
        "no_worker_process_start": True,
        "no_task_assignment": True,
        "no_worker_routing": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_one_worker_activation_scope_contract(approval_gate: dict, worker_template_reference_contract: dict) -> dict:
    pass_ok = approval_gate.get("local_worker_activation_records_authorized", False) and worker_template_reference_contract.get("contract_status") == "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED"
    return {
        "one_worker_activation_scope_contract_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "scope_status": "PASS" if pass_ok else "BLOCKED",
        "exactly_one_worker_template": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
        "no_batch_activation": True,
        "no_department_wide_activation": True,
        "no_routing_activation": True,
        "no_task_activation": True,
        "no_process_activation": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_execution_worker_boundary(approval_gate: dict, one_worker_activation_scope_contract: dict) -> dict:
    pass_ok = approval_gate.get("local_worker_activation_records_authorized", False) and one_worker_activation_scope_contract.get("scope_status") == "PASS"
    return {
        "non_execution_worker_boundary_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "boundary_status": "PASS" if pass_ok else "BLOCKED",
        "worker_activation_record_is_local_metadata_only": True,
        "worker_is_not_executable": True,
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


def create_worker_permission_denial_record(worker_template_label: str) -> dict:
    return {
        "worker_permission_denial_record_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "worker_template_label": worker_template_label,
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
        "live_task_assignment_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "worker_process_start_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_worker_activation_candidate_record(
    command: str,
    approval_gate: dict,
    worker_template_reference_contract: dict,
    one_worker_activation_scope_contract: dict,
    non_execution_worker_boundary: dict,
    worker_permission_denial_record: dict,
) -> dict:
    record_created = (
        approval_gate.get("confirmation_token_valid", False)
        and worker_template_reference_contract.get("contract_status") == "WORKER_TEMPLATE_REFERENCE_CONTRACT_CREATED"
        and one_worker_activation_scope_contract.get("scope_status") == "PASS"
        and non_execution_worker_boundary.get("boundary_status") == "PASS"
    )
    worker_template_label = approval_gate.get("worker_template_label")
    record = {
        "worker_activation_candidate_record_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "candidate_status": "LOCAL_WORKER_ACTIVATION_CANDIDATE_RECORD_CREATED" if record_created else "BLOCKED",
        "activation_candidate_id": generate_limited_live_worker_activation_candidate_id(command, worker_template_label or DEFAULT_WORKER_TEMPLATE_LABEL),
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_worker_label(worker_template_label or DEFAULT_WORKER_TEMPLATE_LABEL),
        "human_operator": approval_gate.get("human_operator"),
        "activation_mode": "local_record_only",
        "worker_runtime_state": "not_started",
        "worker_process_started": False,
        "worker_ready_for_task_assignment": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    return record


def create_worker_activation_audit_record(
    approval_gate: dict,
    worker_template_reference_contract: dict,
    one_worker_activation_scope_contract: dict,
    non_execution_worker_boundary: dict,
    worker_permission_denial_record: dict,
    worker_activation_candidate_record: dict,
) -> dict:
    audit_ok = worker_activation_candidate_record.get("candidate_status") == "LOCAL_WORKER_ACTIVATION_CANDIDATE_RECORD_CREATED"
    record = {
        "worker_activation_audit_record_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "approval_gate_digest": sha256_digest(approval_gate),
        "worker_template_reference_contract_digest": sha256_digest(worker_template_reference_contract),
        "one_worker_activation_scope_contract_digest": sha256_digest(one_worker_activation_scope_contract),
        "non_execution_worker_boundary_digest": sha256_digest(non_execution_worker_boundary),
        "worker_permission_denial_record_digest": sha256_digest(worker_permission_denial_record),
        "worker_activation_candidate_record_digest": sha256_digest(worker_activation_candidate_record),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    record["audit_digest"] = sha256_digest(record)
    return record


def create_worker_activation_ledger(worker_activation_audit_record: dict) -> dict:
    ledger = {
        "worker_activation_ledger_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "ledger_status": "PASS" if worker_activation_audit_record.get("audit_status") == "PASS" else "BLOCKED",
        "worker_activation_audit_record_digest": sha256_digest(worker_activation_audit_record),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    ledger["ledger_digest"] = sha256_digest(ledger)
    return ledger


def create_worker_activation_readiness_summary(worker_activation_ledger: dict) -> dict:
    ready = worker_activation_ledger.get("ledger_status") == "PASS"
    return {
        "worker_activation_readiness_summary_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Permissioned Worker Task Assignment Candidate",
        "v4_4_built": False,
        "ready_for_next_layer": ready,
        "no_task_assignment_yet": True,
        "no_worker_routing_yet": True,
        "no_process_start": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_permissioned_worker_task_assignment_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("ready_for_next_layer", False)
    return {
        "permissioned_worker_task_assignment_candidate_bridge_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_4_PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "v4.4 permissioned worker task assignment candidate",
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def build_worker_activation_record_payload(
    command: str,
    worker_template_label: str,
    human_operator: str,
    activation_output_directory: str,
    record_name: str,
    approval_gate: dict,
    worker_permission_denial_record: dict,
    worker_activation_audit_record: dict,
    activation_candidate_id: str,
) -> dict:
    payload = {
        "runtime_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "activation_type": "limited_local_worker_activation_record",
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "command": command,
        "worker_template_label": worker_template_label,
        "worker_template_label_normalized": normalize_worker_label(worker_template_label),
        "human_operator": human_operator,
        "activation_output_directory": activation_output_directory,
        "record_name": record_name,
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "activation_candidate_id": activation_candidate_id,
        "worker_permission_denial_record": worker_permission_denial_record,
        "activation_audit_digest": worker_activation_audit_record.get("audit_digest"),
        "local_worker_activation_record_written": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        "safety_booleans": {
            **_false_booleans(),
            "local_worker_activation_record_written": False,
            "worker_process_started": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "full_workforce_activation_performed": False,
        },
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_limited_live_worker_activation_record(
    activation_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(activation_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_activation_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    try:
        record_path.relative_to(output_dir)
    except ValueError as exc:
        raise ValueError("activation record path escaped approved output directory") from exc
    record_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "worker_activation_write_record_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "write_status": "LOCAL_WORKER_ACTIVATION_RECORD_WRITTEN",
        "local_worker_activation_record_written": True,
        "files_written_count": 1,
        "record_name": safe_name,
        "record_path": str(record_path),
        "activation_output_directory": str(output_dir),
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_blocked_worker_activation_write_record(reason: str) -> dict:
    return {
        "worker_activation_write_record_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "block_reason": reason,
        "local_worker_activation_record_written": False,
        "files_written_count": 0,
        "record_path": None,
        "activation_output_directory": None,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_limited_live_worker_activation_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    worker_template_label: str | None = None,
    activation_output_directory: str | None = None,
    activation_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    activation_requested: bool = False,
    write_activation_record: bool = False,
) -> dict:
    result = dict(result or {})
    command = command or result.get("command", "check please")
    worker_template_label = worker_template_label or DEFAULT_WORKER_TEMPLATE_LABEL
    activation_record_name = safe_activation_record_name(activation_record_name)
    approval_gate = create_limited_live_worker_activation_candidate_approval_gate(
        worker_template_label,
        activation_output_directory=activation_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        activation_requested=activation_requested,
    )
    worker_template_reference_contract = create_worker_template_reference_contract(approval_gate)
    one_worker_activation_scope_contract = create_one_worker_activation_scope_contract(approval_gate, worker_template_reference_contract)
    non_execution_worker_boundary = create_non_execution_worker_boundary(approval_gate, one_worker_activation_scope_contract)
    worker_permission_denial_record = create_worker_permission_denial_record(worker_template_label)
    worker_activation_candidate_record = create_worker_activation_candidate_record(
        command,
        approval_gate,
        worker_template_reference_contract,
        one_worker_activation_scope_contract,
        non_execution_worker_boundary,
        worker_permission_denial_record,
    )
    worker_activation_audit_record = create_worker_activation_audit_record(
        approval_gate,
        worker_template_reference_contract,
        one_worker_activation_scope_contract,
        non_execution_worker_boundary,
        worker_permission_denial_record,
        worker_activation_candidate_record,
    )
    worker_activation_ledger = create_worker_activation_ledger(worker_activation_audit_record)
    worker_activation_readiness_summary = create_worker_activation_readiness_summary(worker_activation_ledger)
    permissioned_worker_task_assignment_candidate_bridge = create_permissioned_worker_task_assignment_candidate_bridge(worker_activation_readiness_summary)
    write_record = create_blocked_worker_activation_write_record("activation record write not requested")
    payload = None
    if write_activation_record:
        if worker_activation_ledger.get("ledger_status") == "PASS" and activation_output_directory:
            payload = build_worker_activation_record_payload(
                command,
                worker_template_label,
                human_operator or "",
                activation_output_directory,
                activation_record_name,
                approval_gate,
                worker_permission_denial_record,
                worker_activation_audit_record,
                worker_activation_candidate_record["activation_candidate_id"],
            )
            write_record = write_limited_live_worker_activation_record(activation_output_directory, activation_record_name, payload)
        else:
            write_record = create_blocked_worker_activation_write_record("activation record write not authorized")
    bundle = {
        "limited_live_worker_activation_candidate_bundle_version": LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_MODULE_VERSION,
        "schema": create_limited_live_worker_activation_candidate_schema(),
        "limited_live_worker_activation_candidate_approval_gate": approval_gate,
        "worker_template_reference_contract": worker_template_reference_contract,
        "one_worker_activation_scope_contract": one_worker_activation_scope_contract,
        "non_execution_worker_boundary": non_execution_worker_boundary,
        "worker_permission_denial_record": worker_permission_denial_record,
        "worker_activation_candidate_record": worker_activation_candidate_record,
        "worker_activation_audit_record": worker_activation_audit_record,
        "worker_activation_ledger": worker_activation_ledger,
        "worker_activation_readiness_summary": worker_activation_readiness_summary,
        "permissioned_worker_task_assignment_candidate_bridge": permissioned_worker_task_assignment_candidate_bridge,
        "worker_activation_write_record": write_record,
        "local_worker_activation_record_written": bool(write_record.get("local_worker_activation_record_written")),
        "worker_activation_record_payload": payload if write_record.get("local_worker_activation_record_written") else None,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
