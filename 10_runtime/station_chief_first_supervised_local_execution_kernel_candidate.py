from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_MODULE_VERSION = "5.1.0"
FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_STATUS = "FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_LOCAL_OUTPUT_ONLY"
FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_PHASE = "First Supervised Local Execution Kernel Candidate"
FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE"
DEFAULT_SYNTHETIC_TASK_LABEL = "station-chief-sandbox-status-note-task"
DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME = "first_supervised_local_execution_kernel_output_record.json"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str, default_label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", (label or "").strip().lower()).strip("-")
    return normalized or default_label


def safe_output_record_name(record_name: str | None) -> str:
    candidate = (record_name or DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME).strip()
    if not candidate or candidate in {".", ".."}:
        return DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME
    if "/" in candidate or "\\" in candidate:
        return DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME
    if not candidate.endswith(".json"):
        return DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME
    if Path(candidate).name != candidate:
        return DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME
    return candidate


def generate_supervised_local_execution_kernel_id(
    command: str,
    synthetic_task_label: str,
    runtime_version: str = "5.1.0",
) -> str:
    normalized_label = normalize_label(synthetic_task_label, DEFAULT_SYNTHETIC_TASK_LABEL)
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "synthetic_task_label": synthetic_task_label,
        }
    )
    return f"first-supervised-local-execution-kernel-v5-1-{normalized_label}-{digest[:12]}"


def _all_false_flags(*, supervised_local_execution_performed: bool = False) -> dict:
    return {
        "baseline_preserved": True,
        "local_supervised_output_record_written": False,
        "supervised_local_execution_performed": supervised_local_execution_performed,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_first_supervised_local_execution_kernel_candidate_schema() -> dict:
    return {
        "schema_version": FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_MODULE_VERSION,
        "status": FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_STATUS,
        "execution_type": "first_supervised_local_execution_kernel_candidate",
        "required_sections": [
            "supervised_execution_kernel_approval_gate",
            "synthetic_task_contract",
            "sandbox_output_scope_contract",
            "non_external_execution_boundary",
            "execution_permission_denial_record",
            "supervised_local_execution_plan_record",
            "supervised_local_execution_result_record",
            "supervised_local_execution_audit_record",
            "supervised_local_execution_readiness_summary",
            "controlled_repeatable_local_execution_candidate_bridge",
        ],
        "required_token": FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_supervised_output_record_written": False,
        "supervised_local_execution_performed": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_supervised_execution_kernel_approval_gate(
    synthetic_task_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execution_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_APPROVAL_TOKEN
    has_label = bool(synthetic_task_label)
    has_operator = bool(human_operator)
    has_output_dir = bool(output_directory)
    records_authorized = token_valid and has_label and has_operator
    write_authorized = records_authorized and has_output_dir and execution_requested
    gate_status = (
        "APPROVED_FOR_ONE_SUPERVISED_LOCAL_OUTPUT_RECORD"
        if records_authorized
        else "BLOCKED_PENDING_V5_1_SUPERVISED_LOCAL_EXECUTION_APPROVAL"
    )
    return {
        "gate_status": gate_status,
        "token_valid": token_valid,
        "human_operator": human_operator,
        "synthetic_task_label": synthetic_task_label,
        "output_directory": output_directory,
        "execution_requested": execution_requested,
        "local_supervised_execution_records_authorized": records_authorized,
        "local_supervised_output_record_write_authorized": write_authorized,
        "arbitrary_task_execution_authorized": False,
        "user_task_execution_authorized": False,
        "real_queue_creation_authorized": False,
        "queue_write_authorized": False,
        "scheduler_write_authorized": False,
        "cron_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "worker_process_start_authorized": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
    }


def create_synthetic_task_contract(approval_gate: dict) -> dict:
    authorized = bool(approval_gate.get("local_supervised_execution_records_authorized"))
    label = approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL
    normalized = normalize_label(label, DEFAULT_SYNTHETIC_TASK_LABEL)
    return {
        "contract_status": "CREATED" if authorized else "BLOCKED",
        "synthetic_task_label": label,
        "synthetic_task_label_normalized": normalized,
        "synthetic_task_is_synthetic": True,
        "task_has_no_user_data": True,
        "task_has_no_external_dependency": True,
        "task_is_not_enqueued": True,
        "task_is_not_arbitrary_code": True,
        "task_is_not_shell_command": True,
        "task_is_not_executed_as_process": True,
        "execution_mode": "deterministic_local_output_record_only",
    }


def create_sandbox_output_scope_contract(approval_gate: dict, synthetic_task_contract: dict) -> dict:
    gate_ok = bool(approval_gate.get("local_supervised_execution_records_authorized"))
    task_ok = synthetic_task_contract.get("contract_status") == "CREATED"
    return {
        "scope_status": "PASS" if gate_ok and task_ok else "BLOCKED",
        "exactly_one_synthetic_task": True,
        "exactly_one_output_record": True,
        "explicit_output_directory_required": True,
        "output_record_json_only": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_scheduler_write": True,
        "no_cron_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_worker_process_start": True,
        "no_api_network_deployment_production": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
    }


def create_non_external_execution_boundary(approval_gate: dict, sandbox_output_scope_contract: dict) -> dict:
    scope_ok = sandbox_output_scope_contract.get("scope_status") == "PASS"
    return {
        "boundary_status": "PASS" if scope_ok else "BLOCKED",
        "local_output_only": True,
        "no_real_queue": True,
        "no_queue_writes": True,
        "no_scheduler_writes": True,
        "no_cron_writes": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_worker_start": True,
        "no_shell": True,
        "no_subprocess": True,
        "no_tool_calls": True,
        "no_api_access": True,
        "no_network": True,
        "no_sockets": True,
        "no_dns": True,
        "no_credentials": True,
        "no_secrets": True,
        "no_environment": True,
        "no_deployment": True,
        "no_production_execution": True,
        "supervised_local_execution_performed": False,
        **_all_false_flags(),
    }


def create_execution_permission_denial_record(synthetic_task_label: str) -> dict:
    return {
        "permission_status": "DENIED",
        "synthetic_task_label": synthetic_task_label,
        "denied_behaviors": [
            "real queue creation",
            "queue writes",
            "scheduler writes",
            "cron writes",
            "task enqueue",
            "arbitrary task execution",
            "user task execution",
            "shell command execution",
            "subprocess execution",
            "live task assignment",
            "live worker routing",
            "live orchestration",
            "worker process start",
            "agent start",
            "external tool invocation",
            "API access",
            "network access",
            "socket access",
            "DNS resolution",
            "credential use",
            "credential vault access",
            "secret reads",
            "environment reads",
            "deployment",
            "production execution",
            "production activation",
            "GitHub push by worker",
            "full workforce activation",
            "baseline mutation",
            "Devinization overlay mutation",
            "dashboard/org/master export mutation",
            "ownership metadata mutation",
        ],
        "real_queue_creation_denied": True,
        "queue_write_denied": True,
        "scheduler_write_denied": True,
        "cron_write_denied": True,
        "task_enqueue_denied": True,
        "arbitrary_task_execution_denied": True,
        "user_task_execution_denied": True,
        "shell_command_execution_denied": True,
        "subprocess_execution_denied": True,
        "live_task_assignment_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "worker_process_start_denied": True,
        "agent_start_denied": True,
        "external_tool_invocation_denied": True,
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
        "github_push_by_worker_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "referenced_record_mutation_denied": True,
    }


def create_supervised_local_execution_plan_record(
    command: str,
    approval_gate: dict,
    synthetic_task_contract: dict,
    sandbox_output_scope_contract: dict,
    non_external_execution_boundary: dict,
) -> dict:
    created = (
        approval_gate.get("local_supervised_execution_records_authorized") is True
        and synthetic_task_contract.get("contract_status") == "CREATED"
        and sandbox_output_scope_contract.get("scope_status") == "PASS"
        and non_external_execution_boundary.get("boundary_status") == "PASS"
    )
    label = approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL
    normalized = normalize_label(label, DEFAULT_SYNTHETIC_TASK_LABEL)
    kernel_id = generate_supervised_local_execution_kernel_id(command, label)
    return {
        "plan_status": "LOCAL_SUPERVISED_EXECUTION_PLAN_CREATED" if created else "BLOCKED",
        "execution_kernel_id": kernel_id,
        "synthetic_task_label": label,
        "synthetic_task_label_normalized": normalized,
        "human_operator": approval_gate.get("human_operator"),
        "execution_mode": "deterministic_local_output_record_only",
        "output_runtime_state": "not_written",
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
        "unsafe_execution_prohibited": True,
    }


def build_supervised_local_execution_output_payload(
    command: str,
    approval_gate: dict,
    execution_permission_denial_record: dict,
    supervised_local_execution_audit_record: dict,
    supervised_local_execution_result_record: dict,
) -> dict:
    label = approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL
    normalized = normalize_label(label, DEFAULT_SYNTHETIC_TASK_LABEL)
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_MODULE_VERSION,
        "execution_type": "first_supervised_local_execution_kernel_candidate",
        "execution_mode": "deterministic_local_output_record_only",
        "synthetic_task_label": label,
        "synthetic_task_label_normalized": normalized,
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("token_valid"),
        "execution_kernel_id": supervised_local_execution_result_record.get("execution_kernel_id"),
        "output_message": "Station Chief supervised local execution kernel wrote this deterministic sandbox output record.",
        "execution_permission_denial_record": execution_permission_denial_record,
        "supervised_local_execution_audit_digest": supervised_local_execution_audit_record.get("audit_digest"),
        "local_supervised_output_record_written": True,
        "supervised_local_execution_performed": True,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_first_supervised_local_execution_kernel_output_record(
    output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_output_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    if record_path != output_dir and output_dir not in record_path.parents:
        safe_name = DEFAULT_SUPERVISED_LOCAL_OUTPUT_RECORD_NAME
        record_path = (output_dir / safe_name).resolve()
    record_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "supervised_local_execution_write_record_version": FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_MODULE_VERSION,
        "write_status": "SUPERVISED_LOCAL_OUTPUT_RECORD_WRITTEN",
        "local_supervised_output_record_written": True,
        "supervised_local_execution_performed": True,
        "files_written_count": 1,
        "record_name": safe_name,
        "record_path": str(record_path),
        "output_directory": str(output_dir),
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
    }


def create_blocked_supervised_local_execution_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_supervised_output_record_written": False,
        "supervised_local_execution_performed": False,
        "files_written_count": 0,
        **_all_false_flags(),
    }


def create_supervised_local_execution_result_record(
    command: str,
    approval_gate: dict,
    synthetic_task_contract: dict,
    sandbox_output_scope_contract: dict,
    non_external_execution_boundary: dict,
    execution_permission_denial_record: dict,
    supervised_local_execution_plan_record: dict,
    output_record_name: str | None = None,
) -> dict:
    approved = (
        approval_gate.get("local_supervised_output_record_write_authorized") is True
        and synthetic_task_contract.get("contract_status") == "CREATED"
        and sandbox_output_scope_contract.get("scope_status") == "PASS"
        and non_external_execution_boundary.get("boundary_status") == "PASS"
        and supervised_local_execution_plan_record.get("plan_status") == "LOCAL_SUPERVISED_EXECUTION_PLAN_CREATED"
    )
    execution_kernel_id = supervised_local_execution_plan_record.get("execution_kernel_id") or generate_supervised_local_execution_kernel_id(
        command,
        approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL,
    )
    result = {
        "result_status": "SUPERVISED_LOCAL_OUTPUT_RECORD_WRITTEN" if approved else "BLOCKED",
        "execution_kernel_id": execution_kernel_id,
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "synthetic_task_label_normalized": synthetic_task_contract.get("synthetic_task_label_normalized"),
        "human_operator": approval_gate.get("human_operator"),
        "execution_mode": "deterministic_local_output_record_only",
        "output_runtime_state": "written" if approved else "not_written",
        "payload_digest": None,
        "supervised_local_execution_write_record": None,
        "local_supervised_output_record_written": False,
        "supervised_local_execution_performed": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }
    payload = None
    if approved:
        result_for_digest = dict(result)
        result_for_digest.pop("supervised_local_execution_write_record", None)
        result_for_digest.pop("local_supervised_output_record_written", None)
        result_for_digest.pop("supervised_local_execution_performed", None)
        result_for_digest.pop("result_status", None)
        result_for_digest.pop("output_runtime_state", None)
        result_for_digest.pop("payload_digest", None)
        section_digests = {
            "supervised_execution_kernel_approval_gate": sha256_digest(approval_gate),
            "synthetic_task_contract": sha256_digest(synthetic_task_contract),
            "sandbox_output_scope_contract": sha256_digest(sandbox_output_scope_contract),
            "non_external_execution_boundary": sha256_digest(non_external_execution_boundary),
            "execution_permission_denial_record": sha256_digest(execution_permission_denial_record),
            "supervised_local_execution_plan_record": sha256_digest(supervised_local_execution_plan_record),
            "supervised_local_execution_result_record": sha256_digest(result_for_digest),
        }
        audit_placeholder = {"audit_digest": sha256_digest(section_digests)}
        payload = build_supervised_local_execution_output_payload(
            command,
            approval_gate,
            execution_permission_denial_record,
            audit_placeholder,
            result,
        )
        write_record = write_first_supervised_local_execution_kernel_output_record(
            approval_gate.get("output_directory") or "",
            safe_output_record_name(output_record_name),
            payload,
        )
        result["payload_digest"] = payload["payload_digest"]
        result["supervised_local_execution_write_record"] = write_record
        result["local_supervised_output_record_written"] = write_record.get("local_supervised_output_record_written", False)
        result["supervised_local_execution_performed"] = write_record.get("supervised_local_execution_performed", False)
        result["output_runtime_state"] = "written"
    else:
        result["supervised_local_execution_write_record"] = create_blocked_supervised_local_execution_write_record(
            "supervised local output record write blocked"
        )
    result["supervised_local_execution_output_payload"] = payload
    return result


def create_supervised_local_execution_audit_record(
    approval_gate: dict,
    synthetic_task_contract: dict,
    sandbox_output_scope_contract: dict,
    non_external_execution_boundary: dict,
    execution_permission_denial_record: dict,
    supervised_local_execution_plan_record: dict,
    supervised_local_execution_result_record: dict,
) -> dict:
    result_for_digest = dict(supervised_local_execution_result_record)
    result_for_digest.pop("supervised_local_execution_output_payload", None)
    result_for_digest.pop("supervised_local_execution_write_record", None)
    result_for_digest.pop("local_supervised_output_record_written", None)
    result_for_digest.pop("supervised_local_execution_performed", None)
    result_for_digest.pop("result_status", None)
    result_for_digest.pop("output_runtime_state", None)
    result_for_digest.pop("payload_digest", None)
    section_digests = {
        "supervised_execution_kernel_approval_gate": sha256_digest(approval_gate),
        "synthetic_task_contract": sha256_digest(synthetic_task_contract),
        "sandbox_output_scope_contract": sha256_digest(sandbox_output_scope_contract),
        "non_external_execution_boundary": sha256_digest(non_external_execution_boundary),
        "execution_permission_denial_record": sha256_digest(execution_permission_denial_record),
        "supervised_local_execution_plan_record": sha256_digest(supervised_local_execution_plan_record),
        "supervised_local_execution_result_record": sha256_digest(result_for_digest),
    }
    dangerous_keys = [
        "real_queue_created",
        "queue_write_performed",
        "scheduler_write_performed",
        "cron_write_performed",
        "task_enqueued",
        "task_executed",
        "arbitrary_task_execution_performed",
        "user_task_execution_performed",
        "live_task_assignment_performed",
        "live_worker_routing_performed",
        "live_orchestration_performed",
        "worker_process_started",
        "external_tool_invocation_performed",
        "api_call_performed",
        "network_access_performed",
        "deployment_performed",
        "production_execution_performed",
        "full_workforce_activation_performed",
    ]
    all_dangerous_false = all(supervised_local_execution_result_record.get(key) is False for key in dangerous_keys)
    approved_write_path = supervised_local_execution_result_record.get("result_status") == "SUPERVISED_LOCAL_OUTPUT_RECORD_WRITTEN"
    audit_status = "PASS" if all_dangerous_false and (approved_write_path or supervised_local_execution_result_record.get("result_status") == "BLOCKED") else "BLOCKED"
    return {
        "audit_status": audit_status,
        "section_digests": section_digests,
        "audit_digest": sha256_digest(section_digests),
        "all_dangerous_external_booleans_false": all_dangerous_false,
        "approved_write_path": approved_write_path,
    }


def create_supervised_local_execution_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "readiness_status": (
            "READY_FOR_CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "next_layer": "Controlled Repeatable Local Execution Candidate Review",
        "v5_2_not_built": True,
        "one_deterministic_supervised_local_output_record_permitted_only_under_v5_1_token": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_worker_start": True,
        "no_api_network_deployment_production": True,
        "all_dangerous_external_booleans_false": ready,
    }


def create_controlled_repeatable_local_execution_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_REVIEW_ONLY"
    return {
        "bridge_status": "READY_FOR_CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_REVIEW_ONLY" if ready else "BLOCKED",
        "bridge_target": "v5.2 review only",
        "no_repeatable_local_execution_loop_in_v5_1": True,
        "no_queue_creation_in_v5_1": True,
        "no_task_enqueue_in_v5_1": True,
        "no_arbitrary_task_execution_in_v5_1": True,
        "no_user_task_execution_in_v5_1": True,
        "no_worker_routing_in_v5_1": True,
        "no_worker_process_start_in_v5_1": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_first_supervised_local_execution_kernel_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    synthetic_task_label: str | None = None,
    output_directory: str | None = None,
    output_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execution_requested: bool = False,
    write_output_record: bool = False,
) -> dict:
    command = command or (result or {}).get("command") or "check please"
    label = synthetic_task_label or DEFAULT_SYNTHETIC_TASK_LABEL
    gate = create_supervised_execution_kernel_approval_gate(
        label,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execution_requested=execution_requested,
    )
    synthetic_task_contract = create_synthetic_task_contract(gate)
    sandbox_output_scope_contract = create_sandbox_output_scope_contract(gate, synthetic_task_contract)
    non_external_execution_boundary = create_non_external_execution_boundary(gate, sandbox_output_scope_contract)
    execution_permission_denial_record = create_execution_permission_denial_record(label)
    supervised_local_execution_plan_record = create_supervised_local_execution_plan_record(
        command,
        gate,
        synthetic_task_contract,
        sandbox_output_scope_contract,
        non_external_execution_boundary,
    )
    supervised_local_execution_result_record = create_supervised_local_execution_result_record(
        command,
        gate,
        synthetic_task_contract,
        sandbox_output_scope_contract,
        non_external_execution_boundary,
        execution_permission_denial_record,
        supervised_local_execution_plan_record,
        output_record_name=output_record_name,
    )
    supervised_local_execution_audit_record = create_supervised_local_execution_audit_record(
        gate,
        synthetic_task_contract,
        sandbox_output_scope_contract,
        non_external_execution_boundary,
        execution_permission_denial_record,
        supervised_local_execution_plan_record,
        supervised_local_execution_result_record,
    )
    supervised_local_execution_readiness_summary = create_supervised_local_execution_readiness_summary(
        supervised_local_execution_audit_record
    )
    controlled_repeatable_local_execution_candidate_bridge = create_controlled_repeatable_local_execution_candidate_bridge(
        supervised_local_execution_readiness_summary
    )

    if write_output_record:
        if all(
            [
                gate.get("local_supervised_output_record_write_authorized") is True,
                synthetic_task_contract.get("contract_status") == "CREATED",
                sandbox_output_scope_contract.get("scope_status") == "PASS",
                non_external_execution_boundary.get("boundary_status") == "PASS",
                execution_permission_denial_record.get("permission_status") == "DENIED",
                supervised_local_execution_plan_record.get("plan_status") == "LOCAL_SUPERVISED_EXECUTION_PLAN_CREATED",
                supervised_local_execution_result_record.get("result_status") == "SUPERVISED_LOCAL_OUTPUT_RECORD_WRITTEN",
                supervised_local_execution_audit_record.get("audit_status") == "PASS",
            ]
        ):
            write_record = supervised_local_execution_result_record["supervised_local_execution_write_record"]
        else:
            write_record = create_blocked_supervised_local_execution_write_record("supervised local output record write blocked")
    else:
        write_record = create_blocked_supervised_local_execution_write_record("supervised local output record write not requested")

    return {
        "schema": create_first_supervised_local_execution_kernel_candidate_schema(),
        "supervised_execution_kernel_approval_gate": gate,
        "synthetic_task_contract": synthetic_task_contract,
        "sandbox_output_scope_contract": sandbox_output_scope_contract,
        "non_external_execution_boundary": non_external_execution_boundary,
        "execution_permission_denial_record": execution_permission_denial_record,
        "supervised_local_execution_plan_record": supervised_local_execution_plan_record,
        "supervised_local_execution_result_record": supervised_local_execution_result_record,
        "supervised_local_execution_audit_record": supervised_local_execution_audit_record,
        "supervised_local_execution_readiness_summary": supervised_local_execution_readiness_summary,
        "controlled_repeatable_local_execution_candidate_bridge": controlled_repeatable_local_execution_candidate_bridge,
        "supervised_local_execution_output_payload": supervised_local_execution_result_record.get("supervised_local_execution_output_payload"),
        "supervised_local_execution_write_record": write_record,
        "local_supervised_output_record_written": write_record.get("local_supervised_output_record_written", False),
        "supervised_local_execution_performed": write_record.get("supervised_local_execution_performed", False),
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }
