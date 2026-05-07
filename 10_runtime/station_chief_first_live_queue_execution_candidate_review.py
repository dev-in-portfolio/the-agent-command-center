from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_MODULE_VERSION = "5.0.0"
FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_STATUS = "FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_LOCAL_RECORD_ONLY"
FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_PHASE = "First Live Queue Execution Candidate Review"
FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY"
DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL = "station-chief-v4-9-sandbox-orchestration-review-reference"
DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME = "first_live_queue_execution_candidate_review_record.json"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str, default_label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", (label or "").strip().lower()).strip("-")
    return normalized or default_label


def safe_review_record_name(record_name: str | None) -> str:
    candidate = (record_name or DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME).strip()
    if not candidate or candidate in {".", ".."}:
        return DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME
    if "/" in candidate or "\\" in candidate:
        return DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME
    if not candidate.endswith(".json"):
        return DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME
    if Path(candidate).name != candidate:
        return DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME
    return candidate


def generate_execution_candidate_review_id(
    command: str,
    v4_9_orchestration_review_reference_label: str,
    runtime_version: str = "5.0.0",
) -> str:
    normalized_label = normalize_label(
        v4_9_orchestration_review_reference_label,
        DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL,
    )
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "v4_9_orchestration_review_reference_label": v4_9_orchestration_review_reference_label,
        }
    )
    return f"first-live-queue-execution-candidate-review-v5-0-{normalized_label}-{digest[:12]}"


def _dangerous_false_flags() -> dict:
    return {
        "baseline_preserved": True,
        "local_execution_candidate_review_record_written": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
    }


def create_first_live_queue_execution_candidate_review_schema() -> dict:
    return {
        "schema_version": FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_MODULE_VERSION,
        "status": FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_STATUS,
        "review_type": "first_live_queue_execution_candidate_review",
        "required_sections": [
            "execution_candidate_review_approval_gate",
            "v4_9_orchestration_review_reference_contract",
            "execution_candidate_review_scope_contract",
            "non_execution_execution_boundary",
            "execution_permission_denial_record",
            "execution_candidate_review_record",
            "execution_candidate_review_audit_record",
            "execution_candidate_readiness_summary",
            "first_supervised_local_execution_kernel_candidate_bridge",
        ],
        "required_token": FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_execution_candidate_review_record_written": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_execution_candidate_review_approval_gate(
    v4_9_orchestration_review_reference_label: str,
    review_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_APPROVAL_TOKEN
    has_reference = bool(v4_9_orchestration_review_reference_label)
    has_operator = bool(human_operator)
    has_output_dir = bool(review_output_directory)
    local_records_authorized = token_valid and has_reference and has_operator
    write_authorized = local_records_authorized and has_output_dir and review_requested
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_EXECUTION_CANDIDATE_REVIEW_RECORD"
        if local_records_authorized
        else "BLOCKED_PENDING_V5_0_EXECUTION_CANDIDATE_REVIEW_APPROVAL"
    )
    return {
        "gate_status": gate_status,
        "token_valid": token_valid,
        "human_operator": human_operator,
        "v4_9_orchestration_review_reference_label": v4_9_orchestration_review_reference_label,
        "review_output_directory": review_output_directory,
        "review_requested": review_requested,
        "local_execution_candidate_review_records_authorized": local_records_authorized,
        "local_execution_candidate_review_record_write_authorized": write_authorized,
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
        "supervised_local_execution_authorized": False,
        "full_workforce_activation_authorized": False,
    }


def create_v4_9_orchestration_review_reference_contract(approval_gate: dict) -> dict:
    authorized = bool(approval_gate.get("local_execution_candidate_review_records_authorized"))
    label = approval_gate.get("v4_9_orchestration_review_reference_label") or DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL
    normalized = normalize_label(label, DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL)
    return {
        "contract_status": "CREATED" if authorized else "BLOCKED",
        "v4_9_orchestration_review_reference_label": label,
        "v4_9_orchestration_review_reference_label_normalized": normalized,
        "reference_metadata_only": True,
        "record_mutated": False,
        "record_executed": False,
        "record_enqueued": False,
        "record_routed": False,
        "execution_authorized": False,
    }


def create_execution_candidate_review_scope_contract(approval_gate: dict, v4_9_reference_contract: dict) -> dict:
    gate_ok = bool(approval_gate.get("local_execution_candidate_review_records_authorized"))
    reference_ok = v4_9_reference_contract.get("contract_status") == "CREATED"
    return {
        "scope_status": "PASS" if gate_ok and reference_ok else "BLOCKED",
        "exactly_one_v4_9_orchestration_review_reference": True,
        "candidate_review_only": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_scheduler_write": True,
        "no_cron_write": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_live_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_worker_process_start": True,
        "no_supervised_local_execution": True,
        "no_full_workforce_activation": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
    }


def create_non_execution_execution_boundary(approval_gate: dict, execution_candidate_review_scope_contract: dict) -> dict:
    scope_ok = execution_candidate_review_scope_contract.get("scope_status") == "PASS"
    return {
        "boundary_status": "PASS" if scope_ok else "BLOCKED",
        "local_metadata_only": True,
        "no_real_queue": True,
        "no_queue_writes": True,
        "no_scheduler_writes": True,
        "no_cron_writes": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_worker_start": True,
        "no_supervised_local_execution": True,
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
        **_dangerous_false_flags(),
    }


def create_execution_permission_denial_record(v4_9_orchestration_review_reference_label: str) -> dict:
    return {
        "permission_status": "DENIED",
        "v4_9_orchestration_review_reference_label": v4_9_orchestration_review_reference_label,
        "denied_behaviors": [
            "real queue creation",
            "queue writes",
            "scheduler writes",
            "cron writes",
            "task enqueue",
            "task execution",
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
            "mutation of the referenced v4.9 orchestration review record",
        ],
        "real_queue_creation_denied": True,
        "queue_write_denied": True,
        "scheduler_write_denied": True,
        "cron_write_denied": True,
        "task_enqueue_denied": True,
        "task_execution_denied": True,
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
        "referenced_v4_9_record_mutation_denied": True,
    }


def create_execution_candidate_review_record(
    command: str,
    approval_gate: dict,
    v4_9_reference_contract: dict,
    execution_candidate_review_scope_contract: dict,
    non_execution_execution_boundary: dict,
    execution_permission_denial_record: dict,
) -> dict:
    created = (
        approval_gate.get("local_execution_candidate_review_records_authorized") is True
        and v4_9_reference_contract.get("contract_status") == "CREATED"
        and execution_candidate_review_scope_contract.get("scope_status") == "PASS"
        and non_execution_execution_boundary.get("boundary_status") == "PASS"
    )
    label = approval_gate.get("v4_9_orchestration_review_reference_label") or DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL
    normalized = normalize_label(label, DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL)
    review_id = generate_execution_candidate_review_id(command, label)
    return {
        "candidate_status": "LOCAL_EXECUTION_CANDIDATE_REVIEW_RECORD_CREATED" if created else "BLOCKED",
        "execution_candidate_review_id": review_id,
        "v4_9_orchestration_review_reference_label": label,
        "v4_9_orchestration_review_reference_label_normalized": normalized,
        "human_operator": approval_gate.get("human_operator"),
        "review_mode": "local_metadata_only",
        "queue_runtime_state": "not_created",
        "task_runtime_state": "not_enqueued_not_executed",
        "worker_runtime_state": "not_started",
        "orchestration_runtime_state": "not_started",
        "execution_runtime_state": "not_executed",
        **_dangerous_false_flags(),
    }


def create_execution_candidate_review_audit_record(
    approval_gate: dict,
    v4_9_reference_contract: dict,
    execution_candidate_review_scope_contract: dict,
    non_execution_execution_boundary: dict,
    execution_permission_denial_record: dict,
    execution_candidate_review_record: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "v4_9_orchestration_review_reference_contract": sha256_digest(v4_9_reference_contract),
        "execution_candidate_review_scope_contract": sha256_digest(execution_candidate_review_scope_contract),
        "non_execution_execution_boundary": sha256_digest(non_execution_execution_boundary),
        "execution_permission_denial_record": sha256_digest(execution_permission_denial_record),
        "execution_candidate_review_record": sha256_digest(execution_candidate_review_record),
    }
    all_dangerous_false = all(
        value is False
        for key, value in execution_candidate_review_record.items()
        if key.endswith("_performed")
        or key.endswith("_denied")
        or key.startswith("no_")
    )
    audit_status = "PASS" if execution_candidate_review_record.get("candidate_status") == "LOCAL_EXECUTION_CANDIDATE_REVIEW_RECORD_CREATED" and all_dangerous_false else "BLOCKED"
    return {
        "audit_status": audit_status,
        "section_digests": section_digests,
        "audit_digest": sha256_digest(section_digests),
        "all_dangerous_booleans_false": all_dangerous_false,
    }


def create_execution_candidate_readiness_summary(
    audit_record: dict,
) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "readiness_status": "READY_FOR_FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_REVIEW_ONLY" if ready else "BLOCKED",
        "next_layer": "First Supervised Local Execution Kernel Candidate Review",
        "v5_1_not_built": True,
        "no_real_queue_created_yet": True,
        "no_queue_write_yet": True,
        "no_task_enqueue_yet": True,
        "no_task_execution_yet": True,
        "no_live_routing_yet": True,
        "no_live_orchestration_yet": True,
        "no_worker_start_yet": True,
        "no_supervised_local_execution_yet": True,
        "all_dangerous_booleans_false": ready,
    }


def create_first_supervised_local_execution_kernel_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_REVIEW_ONLY"
    return {
        "bridge_status": "READY_FOR_FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_REVIEW_ONLY" if ready else "BLOCKED",
        "bridge_target": "v5.1 review only",
        "no_supervised_local_execution_in_v5_0": True,
        "no_queue_creation_in_v5_0": True,
        "no_task_enqueue_in_v5_0": True,
        "no_task_execution_in_v5_0": True,
        "no_worker_routing_in_v5_0": True,
        "no_worker_process_start_in_v5_0": True,
        **_dangerous_false_flags(),
    }


def build_execution_candidate_review_record_payload(
    command: str,
    approval_gate: dict,
    execution_permission_denial_record: dict,
    execution_candidate_review_audit_record: dict,
    execution_candidate_review_record: dict,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_MODULE_VERSION,
        "review_type": "first_live_queue_execution_candidate_review",
        "v4_9_orchestration_review_reference_label": approval_gate.get("v4_9_orchestration_review_reference_label"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("token_valid"),
        "execution_candidate_review_id": execution_candidate_review_record.get("execution_candidate_review_id"),
        "execution_permission_denial_record": execution_permission_denial_record,
        "execution_candidate_review_audit_digest": execution_candidate_review_audit_record.get("audit_digest"),
        "safety_booleans": {
            "real_queue_created": False,
            "queue_write_performed": False,
            "scheduler_write_performed": False,
            "cron_write_performed": False,
            "task_enqueued": False,
            "task_executed": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "live_orchestration_performed": False,
            "worker_process_started": False,
            "supervised_local_execution_performed": False,
            "full_workforce_activation_performed": False,
        },
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_first_live_queue_execution_candidate_review_record(
    review_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(review_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_review_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    if output_dir not in record_path.parents and record_path != output_dir:
        safe_name = DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME
        record_path = (output_dir / safe_name).resolve()
    record_path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    return {
        "execution_candidate_review_write_record_version": FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_MODULE_VERSION,
        "write_status": "LOCAL_EXECUTION_CANDIDATE_REVIEW_RECORD_WRITTEN",
        "local_execution_candidate_review_record_written": True,
        "files_written_count": 1,
        "record_name": safe_name,
        "record_path": str(record_path),
        "review_output_directory": str(output_dir),
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
    }


def create_blocked_execution_candidate_review_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_execution_candidate_review_record_written": False,
        "files_written_count": 0,
        **_dangerous_false_flags(),
    }


def create_first_live_queue_execution_candidate_review_bundle(
    result: dict | None,
    command: str | None = None,
    v4_9_orchestration_review_reference_label: str | None = None,
    review_output_directory: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
    write_review_record: bool = False,
) -> dict:
    command = command or (result or {}).get("command") or "check please"
    label = v4_9_orchestration_review_reference_label or DEFAULT_V4_9_ORCHESTRATION_REVIEW_REFERENCE_LABEL
    gate = create_execution_candidate_review_approval_gate(
        label,
        review_output_directory=review_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=review_requested,
    )
    reference = create_v4_9_orchestration_review_reference_contract(gate)
    scope = create_execution_candidate_review_scope_contract(gate, reference)
    boundary = create_non_execution_execution_boundary(gate, scope)
    denial = create_execution_permission_denial_record(label)
    candidate = create_execution_candidate_review_record(command, gate, reference, scope, boundary, denial)
    audit = create_execution_candidate_review_audit_record(gate, reference, scope, boundary, denial, candidate)
    summary = create_execution_candidate_readiness_summary(audit)
    bridge = create_first_supervised_local_execution_kernel_candidate_bridge(summary)
    payload = build_execution_candidate_review_record_payload(command, gate, denial, audit, candidate)

    if write_review_record:
        if all([
            gate.get("local_execution_candidate_review_record_write_authorized") is True,
            reference.get("contract_status") == "CREATED",
            scope.get("scope_status") == "PASS",
            boundary.get("boundary_status") == "PASS",
            denial.get("permission_status") == "DENIED",
            candidate.get("candidate_status") == "LOCAL_EXECUTION_CANDIDATE_REVIEW_RECORD_CREATED",
            audit.get("audit_status") == "PASS",
        ]):
            write_record = write_first_live_queue_execution_candidate_review_record(
                review_output_directory or "",
                review_record_name or DEFAULT_EXECUTION_CANDIDATE_REVIEW_RECORD_NAME,
                payload,
            )
        else:
            write_record = create_blocked_execution_candidate_review_write_record(
                "execution candidate review record write not requested"
                if not review_requested
                else "execution candidate review record write blocked"
            )
    else:
        write_record = create_blocked_execution_candidate_review_write_record(
            "execution candidate review record write not requested"
        )

    return {
        "schema": create_first_live_queue_execution_candidate_review_schema(),
        "execution_candidate_review_approval_gate": gate,
        "v4_9_orchestration_review_reference_contract": reference,
        "execution_candidate_review_scope_contract": scope,
        "non_execution_execution_boundary": boundary,
        "execution_permission_denial_record": denial,
        "execution_candidate_review_record": candidate,
        "execution_candidate_review_audit_record": audit,
        "execution_candidate_readiness_summary": summary,
        "first_supervised_local_execution_kernel_candidate_bridge": bridge,
        "execution_candidate_review_record_payload": payload,
        "execution_candidate_review_write_record": write_record,
        "local_execution_candidate_review_record_written": write_record.get("local_execution_candidate_review_record_written", False),
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "supervised_local_execution_performed": False,
        "full_workforce_activation_performed": False,
    }
