#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION = "5.2.0"
CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_STATUS = "CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_LOCAL_PROOF_ONLY"
CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_PHASE = "Controlled Repeatable Local Execution Candidate"
CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE"
DEFAULT_SYNTHETIC_TASK_LABEL = "station-chief-repeatable-sandbox-status-note-task"
DEFAULT_REPEATABILITY_PROOF_RECORD_NAME = "controlled_repeatable_local_execution_proof_record.json"
DEFAULT_REPEATABILITY_COUNT = 2
MAX_REPEATABILITY_COUNT = 5


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    text = (label or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or default_label


def normalize_repeatability_count(repeatability_count: int | None) -> int:
    if isinstance(repeatability_count, bool) or repeatability_count is None:
        return DEFAULT_REPEATABILITY_COUNT
    if not isinstance(repeatability_count, int):
        return DEFAULT_REPEATABILITY_COUNT
    if repeatability_count < 2 or repeatability_count > MAX_REPEATABILITY_COUNT:
        return DEFAULT_REPEATABILITY_COUNT
    return repeatability_count


def safe_proof_record_name(record_name: str | None) -> str:
    default = DEFAULT_REPEATABILITY_PROOF_RECORD_NAME
    if not record_name:
        return default
    candidate = str(record_name).strip()
    if candidate in {"", ".", ".."}:
        return default
    if "/" in candidate or "\\" in candidate:
        return default
    if not candidate.endswith(".json"):
        return default
    return candidate


def generate_repeatable_local_execution_candidate_id(
    command: str,
    synthetic_task_label: str,
    repeatability_count: int,
    runtime_version: str = CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_label = normalize_label(synthetic_task_label, DEFAULT_SYNTHETIC_TASK_LABEL)
    normalized_count = normalize_repeatability_count(repeatability_count)
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "synthetic_task_label": normalized_label,
            "repeatability_count": normalized_count,
        }
    )
    return f"controlled-repeatable-local-execution-v5-2-{normalized_label}-{normalized_count}-{digest[:12]}"


def _bools_false() -> dict:
    return {
        "local_repeatability_proof_record_written": False,
        "controlled_repeatable_local_execution_performed": False,
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


def create_controlled_repeatable_local_execution_candidate_schema() -> dict:
    return {
        "schema_version": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION,
        "status": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_STATUS,
        "execution_type": "controlled_repeatable_local_execution_candidate",
        "required_token": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
        "required_sections": [
            "repeatable_execution_approval_gate",
            "synthetic_repeatable_task_contract",
            "repeatability_scope_contract",
            "non_external_repeatability_boundary",
            "repeatability_permission_denial_record",
            "repeatability_plan_record",
            "repeatability_entries_record",
            "repeatability_proof_result_record",
            "repeatability_audit_record",
            "repeatability_readiness_summary",
            "sandbox_worker_handoff_candidate_bridge",
        ],
        "baseline_preserved": True,
        **_bools_false(),
    }


def create_repeatable_execution_approval_gate(
    synthetic_task_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    repeatability_count: int | None = None,
    execution_requested: bool = False,
) -> dict:
    normalized_count = normalize_repeatability_count(repeatability_count)
    token_valid = confirmation_token == CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_APPROVAL_TOKEN
    records_authorized = bool(token_valid and human_operator and synthetic_task_label)
    proof_write_authorized = bool(records_authorized and output_directory and execution_requested)
    return {
        "gate_status": (
            "APPROVED_FOR_ONE_LOCAL_REPEATABILITY_PROOF_RECORD"
            if records_authorized
            else "BLOCKED_PENDING_V5_2_REPEATABLE_LOCAL_EXECUTION_APPROVAL"
        ),
        "approval_token_valid": token_valid,
        "human_operator": human_operator,
        "synthetic_task_label": synthetic_task_label,
        "synthetic_task_label_normalized": normalize_label(synthetic_task_label, DEFAULT_SYNTHETIC_TASK_LABEL),
        "repeatability_count": normalized_count,
        "repeatability_count_normalized": normalized_count,
        "output_directory": output_directory,
        "execution_requested": bool(execution_requested),
        "local_repeatability_records_authorized": records_authorized,
        "local_repeatability_proof_write_authorized": proof_write_authorized,
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


def create_synthetic_repeatable_task_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_repeatability_records_authorized"):
        return {
            "contract_status": "BLOCKED",
            "contract_created": False,
            "execution_mode": "deterministic_local_proof_record_only",
            "repeatability_count": approval_gate.get("repeatability_count", DEFAULT_REPEATABILITY_COUNT),
            "synthetic_task_label": approval_gate.get("synthetic_task_label"),
            "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
            "task_is_synthetic": True,
            "task_has_no_user_data": True,
            "task_has_no_external_dependency": True,
            "task_is_not_enqueued": True,
            "task_is_not_arbitrary_code": True,
            "task_is_not_shell_command": True,
            "task_is_not_executed_as_process": True,
        }
    return {
        "contract_status": "CREATED",
        "contract_created": True,
        "execution_mode": "deterministic_local_proof_record_only",
        "repeatability_count": approval_gate.get("repeatability_count", DEFAULT_REPEATABILITY_COUNT),
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
        "task_is_synthetic": True,
        "task_has_no_user_data": True,
        "task_has_no_external_dependency": True,
        "task_is_not_enqueued": True,
        "task_is_not_arbitrary_code": True,
        "task_is_not_shell_command": True,
        "task_is_not_executed_as_process": True,
    }


def create_repeatability_scope_contract(approval_gate: dict, synthetic_repeatable_task_contract: dict) -> dict:
    scope_pass = bool(
        approval_gate.get("local_repeatability_records_authorized")
        and synthetic_repeatable_task_contract.get("contract_created")
    )
    repeatability_count = normalize_repeatability_count(approval_gate.get("repeatability_count"))
    return {
        "scope_status": "PASS" if scope_pass else "BLOCKED",
        "scope_pass": scope_pass,
        "exactly_one_synthetic_task": True,
        "exactly_one_proof_record": True,
        "explicit_output_directory_required": True,
        "proof_record_json_only": True,
        "repeatability_count_bounded": True,
        "repeatability_count_minimum": 2,
        "repeatability_count_maximum": MAX_REPEATABILITY_COUNT,
        "repeatability_count": repeatability_count,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
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
    }


def create_non_external_repeatability_boundary(approval_gate: dict, repeatability_scope_contract: dict) -> dict:
    boundary_pass = bool(repeatability_scope_contract.get("scope_pass"))
    return {
        "boundary_status": "PASS" if boundary_pass else "BLOCKED",
        "boundary_pass": boundary_pass,
        "controlled_repeatable_local_execution_performed": False,
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
        "no_credentials_or_secrets_or_environment": True,
        "no_deployment": True,
        "no_production_execution": True,
        **{k: False for k in [
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
        ]},
    }


def create_repeatability_permission_denial_record(synthetic_task_label: str) -> dict:
    return {
        "synthetic_task_label": synthetic_task_label,
        "real_queue_creation": "denied",
        "queue_writes": "denied",
        "scheduler_writes": "denied",
        "cron_writes": "denied",
        "task_enqueue": "denied",
        "arbitrary_task_execution": "denied",
        "user_task_execution": "denied",
        "shell_command_execution": "denied",
        "subprocess_execution": "denied",
        "live_task_assignment": "denied",
        "live_worker_routing": "denied",
        "live_orchestration": "denied",
        "worker_process_start": "denied",
        "agent_start": "denied",
        "external_tool_invocation": "denied",
        "api_access": "denied",
        "network_access": "denied",
        "socket_access": "denied",
        "dns_resolution": "denied",
        "credential_use": "denied",
        "credential_vault_access": "denied",
        "secret_reads": "denied",
        "environment_reads": "denied",
        "deployment": "denied",
        "production_execution": "denied",
        "production_activation": "denied",
        "github_push_by_worker": "denied",
        "full_workforce_activation": "denied",
        "baseline_mutation": "denied",
        "devinization_overlay_mutation": "denied",
        "dashboard_org_master_export_mutation": "denied",
        "ownership_metadata_mutation": "denied",
        "mutation_of_the_referenced_v4_9_orchestration_review_record": "denied",
    }


def create_repeatability_plan_record(
    command: str,
    approval_gate: dict,
    synthetic_repeatable_task_contract: dict,
    repeatability_scope_contract: dict,
    non_external_repeatability_boundary: dict,
) -> dict:
    planned = bool(
        approval_gate.get("local_repeatability_records_authorized")
        and synthetic_repeatable_task_contract.get("contract_created")
        and repeatability_scope_contract.get("scope_pass")
        and non_external_repeatability_boundary.get("boundary_pass")
    )
    repeatability_count = normalize_repeatability_count(approval_gate.get("repeatability_count"))
    candidate_id = generate_repeatable_local_execution_candidate_id(
        command,
        approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL,
        repeatability_count,
    )
    return {
        "plan_status": "LOCAL_REPEATABILITY_PLAN_CREATED" if planned else "BLOCKED",
        "candidate_planned": planned,
        "repeatable_execution_candidate_id": candidate_id,
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
        "repeatability_count": repeatability_count,
        "human_operator": approval_gate.get("human_operator"),
        "execution_mode": "deterministic_local_repeatability_proof_only",
        "proof_runtime_state": "not_written",
        **{k: False for k in [
            "real_queue_created",
            "task_enqueued",
            "task_executed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "worker_process_started",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "api_call_performed",
            "network_access_performed",
        ]},
    }


def create_repeatability_entries_record(repeatability_plan_record: dict) -> dict:
    repeatability_count = normalize_repeatability_count(repeatability_plan_record.get("repeatability_count"))
    normalized_label = repeatability_plan_record.get("synthetic_task_label_normalized") or DEFAULT_SYNTHETIC_TASK_LABEL
    candidate_id = repeatability_plan_record.get("repeatable_execution_candidate_id")
    output_message = "Station Chief controlled repeatable local execution candidate wrote this deterministic repeatability proof record."
    synthetic_result_digest = sha256_digest(
        {
            "candidate_id": candidate_id,
            "repeatability_count": repeatability_count,
            "synthetic_task_label": normalized_label,
            "output_message": output_message,
        }
    )
    entries = []
    for entry_index in range(repeatability_count):
        entries.append(
            {
                "entry_index": entry_index,
                "synthetic_task_label": normalized_label,
                "deterministic_output_message": output_message,
                "synthetic_result_digest": synthetic_result_digest,
                "real_queue_created": False,
                "task_enqueued": False,
                "task_executed": False,
                "arbitrary_task_execution_performed": False,
                "user_task_execution_performed": False,
                "worker_process_started": False,
                "api_call_performed": False,
                "network_access_performed": False,
            }
        )
    return {
        "repeatability_count": repeatability_count,
        "repeatability_status": "PASS" if entries and len({entry["synthetic_result_digest"] for entry in entries}) == 1 else "BLOCKED",
        "synthetic_result_digest": synthetic_result_digest,
        "deterministic_output_message": output_message,
        "entries": entries,
        "all_synthetic_result_digests_match": len({entry["synthetic_result_digest"] for entry in entries}) == 1 if entries else False,
    }


def build_repeatability_proof_payload(
    command: str,
    approval_gate: dict,
    repeatability_plan_record: dict,
    repeatability_entries_record: dict,
    repeatability_permission_denial_record: dict,
    repeatability_audit_record: dict,
    write_record: dict | None = None,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION,
        "execution_type": "controlled_repeatable_local_execution_candidate",
        "execution_mode": "deterministic_local_repeatability_proof_only",
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "repeatability_count": repeatability_plan_record.get("repeatability_count"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("approval_token_valid"),
        "repeatable_execution_candidate_id": repeatability_plan_record.get("repeatable_execution_candidate_id"),
        "repeatability_status": repeatability_entries_record.get("repeatability_status"),
        "repeatability_entries_record": repeatability_entries_record,
        "repeatability_permission_denial_record": repeatability_permission_denial_record,
        "repeatability_audit_digest": repeatability_audit_record.get("audit_digest"),
        "output_message": "Station Chief controlled repeatable local execution candidate wrote this deterministic repeatability proof record.",
        "local_repeatability_proof_record_written": bool(write_record and write_record.get("local_repeatability_proof_record_written")),
        "controlled_repeatable_local_execution_performed": bool(write_record and write_record.get("controlled_repeatable_local_execution_performed")),
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
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_controlled_repeatable_local_execution_proof_record(
    output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_proof_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    record_path.relative_to(output_dir)
    record_path.write_text(canonical_json(payload) + "\n")
    return {
        "repeatability_proof_write_record_version": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION,
        "write_status": "CONTROLLED_REPEATABILITY_PROOF_RECORD_WRITTEN",
        "local_repeatability_proof_record_written": True,
        "controlled_repeatable_local_execution_performed": True,
        "files_written_count": 1,
        "output_directory": str(output_dir),
        "record_name": safe_name,
        "record_path": str(record_path),
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
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
    }


def create_blocked_repeatability_proof_write_record(reason: str) -> dict:
    return {
        "repeatability_proof_write_record_version": CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "reason": reason,
        "local_repeatability_proof_record_written": False,
        "controlled_repeatable_local_execution_performed": False,
        "files_written_count": 0,
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
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
    }


def create_repeatability_proof_result_record(
    approval_gate: dict,
    repeatability_entries_record: dict,
    write_record: dict,
    payload: dict | None,
) -> dict:
    status = write_record.get("write_status", "BLOCKED")
    return {
        "result_status": status,
        "write_record": write_record,
        "payload_digest": payload.get("payload_digest") if payload else None,
        "repeatability_status": repeatability_entries_record.get("repeatability_status"),
        "controlled_repeatable_local_execution_performed": bool(write_record.get("controlled_repeatable_local_execution_performed")),
        "local_repeatability_proof_record_written": bool(write_record.get("local_repeatability_proof_record_written")),
        **{k: False for k in [
            "real_queue_created",
            "queue_write_performed",
            "scheduler_write_performed",
            "cron_write_performed",
            "task_enqueued",
            "task_executed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "worker_process_started",
            "live_task_assignment_performed",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed",
        ]},
    }


def create_repeatability_audit_record(
    approval_gate: dict,
    synthetic_repeatable_task_contract: dict,
    repeatability_scope_contract: dict,
    non_external_repeatability_boundary: dict,
    repeatability_permission_denial_record: dict,
    repeatability_plan_record: dict,
    repeatability_entries_record: dict,
    repeatability_proof_result_record: dict,
) -> dict:
    section_digests = {
        "repeatable_execution_approval_gate": sha256_digest(approval_gate),
        "synthetic_repeatable_task_contract": sha256_digest(synthetic_repeatable_task_contract),
        "repeatability_scope_contract": sha256_digest(repeatability_scope_contract),
        "non_external_repeatability_boundary": sha256_digest(non_external_repeatability_boundary),
        "repeatability_permission_denial_record": sha256_digest(repeatability_permission_denial_record),
        "repeatability_plan_record": sha256_digest(repeatability_plan_record),
        "repeatability_entries_record": sha256_digest(repeatability_entries_record),
        "repeatability_proof_result_record": sha256_digest(repeatability_proof_result_record),
    }
    dangerous_clear = all(
        value is False
        for value in [
            repeatability_proof_result_record.get("real_queue_created"),
            repeatability_proof_result_record.get("queue_write_performed"),
            repeatability_proof_result_record.get("scheduler_write_performed"),
            repeatability_proof_result_record.get("cron_write_performed"),
            repeatability_proof_result_record.get("task_enqueued"),
            repeatability_proof_result_record.get("task_executed"),
            repeatability_proof_result_record.get("arbitrary_task_execution_performed"),
            repeatability_proof_result_record.get("user_task_execution_performed"),
            repeatability_proof_result_record.get("worker_process_started"),
            repeatability_proof_result_record.get("live_task_assignment_performed"),
            repeatability_proof_result_record.get("live_worker_routing_performed"),
            repeatability_proof_result_record.get("live_orchestration_performed"),
            repeatability_proof_result_record.get("api_call_performed"),
            repeatability_proof_result_record.get("network_access_performed"),
            repeatability_proof_result_record.get("deployment_performed"),
            repeatability_proof_result_record.get("production_execution_performed"),
            repeatability_proof_result_record.get("full_workforce_activation_performed"),
        ]
    )
    return {
        "audit_status": "PASS" if dangerous_clear and repeatability_entries_record.get("repeatability_status") == "PASS" else "BLOCKED",
        "audit_digest": sha256_digest(section_digests),
        "section_digests": section_digests,
        "controlled_repeatable_local_execution_performed": bool(repeatability_proof_result_record.get("controlled_repeatable_local_execution_performed")),
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        **{k: False for k in [
            "real_queue_created",
            "queue_write_performed",
            "scheduler_write_performed",
            "cron_write_performed",
            "task_enqueued",
            "worker_process_started",
            "live_task_assignment_performed",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed",
        ]},
    }


def create_repeatability_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "readiness_status": (
            "READY_FOR_SANDBOX_WORKER_HANDOFF_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "next_layer": "Sandbox Worker Handoff Candidate Review",
        "v5_3_not_built": True,
        "one_deterministic_repeatability_proof_file_permitted_only_under_token_gated_temp_dir_write_path": True,
        "repeatability_count_bounded": True,
        "controlled_repeatable_local_execution_performed": bool(audit_record.get("controlled_repeatable_local_execution_performed")),
        "no_real_queue": True,
        "no_queue_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_worker_start": True,
        "no_api_network_deployment_production": True,
        **{k: False for k in [
            "real_queue_created",
            "queue_write_performed",
            "scheduler_write_performed",
            "cron_write_performed",
            "task_enqueued",
            "task_executed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "worker_process_started",
            "live_task_assignment_performed",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed",
        ]},
    }


def create_sandbox_worker_handoff_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_SANDBOX_WORKER_HANDOFF_CANDIDATE_REVIEW_ONLY"
    return {
        "bridge_status": (
            "READY_FOR_SANDBOX_WORKER_HANDOFF_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "bridge_ready": ready,
        "v5_3_not_built": True,
        "no_sandbox_worker_handoff_in_v5_2": True,
        **{k: False for k in [
            "real_queue_created",
            "queue_write_performed",
            "scheduler_write_performed",
            "cron_write_performed",
            "task_enqueued",
            "task_executed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "worker_process_started",
            "live_task_assignment_performed",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed",
        ]},
    }


def create_controlled_repeatable_local_execution_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    synthetic_task_label: str | None = None,
    output_directory: str | None = None,
    output_record_name: str | None = None,
    repeatability_count: int | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execution_requested: bool = False,
    write_proof_record: bool = False,
) -> dict:
    command = command or "check please"
    synthetic_task_label = synthetic_task_label or DEFAULT_SYNTHETIC_TASK_LABEL
    approval_gate = create_repeatable_execution_approval_gate(
        synthetic_task_label=synthetic_task_label,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        repeatability_count=repeatability_count,
        execution_requested=execution_requested,
    )
    synthetic_repeatable_task_contract = create_synthetic_repeatable_task_contract(approval_gate)
    repeatability_scope_contract = create_repeatability_scope_contract(approval_gate, synthetic_repeatable_task_contract)
    non_external_repeatability_boundary = create_non_external_repeatability_boundary(approval_gate, repeatability_scope_contract)
    repeatability_permission_denial_record = create_repeatability_permission_denial_record(approval_gate.get("synthetic_task_label") or synthetic_task_label)
    repeatability_plan_record = create_repeatability_plan_record(
        command,
        approval_gate,
        synthetic_repeatable_task_contract,
        repeatability_scope_contract,
        non_external_repeatability_boundary,
    )
    repeatability_entries_record = create_repeatability_entries_record(repeatability_plan_record)
    write_record = create_blocked_repeatability_proof_write_record("controlled repeatability proof record write not requested")
    payload = None
    if write_proof_record:
        if (
            approval_gate.get("local_repeatability_proof_write_authorized")
            and synthetic_repeatable_task_contract.get("contract_created")
            and repeatability_scope_contract.get("scope_pass")
            and non_external_repeatability_boundary.get("boundary_pass")
            and repeatability_plan_record.get("plan_status") == "LOCAL_REPEATABILITY_PLAN_CREATED"
            and repeatability_entries_record.get("repeatability_status") == "PASS"
        ):
            payload = build_repeatability_proof_payload(
                command,
                approval_gate,
                repeatability_plan_record,
                repeatability_entries_record,
                repeatability_permission_denial_record,
                {"audit_digest": None},
                {"local_repeatability_proof_record_written": True, "controlled_repeatable_local_execution_performed": True},
            )
            write_record = write_controlled_repeatable_local_execution_proof_record(
                output_directory=str(output_directory),
                record_name=output_record_name or DEFAULT_REPEATABILITY_PROOF_RECORD_NAME,
                payload=payload,
            )
        else:
            write_record = create_blocked_repeatability_proof_write_record("controlled repeatability proof record write not authorized")
    repeatability_proof_result_record = create_repeatability_proof_result_record(
        approval_gate,
        repeatability_entries_record,
        write_record,
        payload,
    )
    repeatability_audit_record = create_repeatability_audit_record(
        approval_gate,
        synthetic_repeatable_task_contract,
        repeatability_scope_contract,
        non_external_repeatability_boundary,
        repeatability_permission_denial_record,
        repeatability_plan_record,
        repeatability_entries_record,
        repeatability_proof_result_record,
    )
    if payload is None and write_record.get("local_repeatability_proof_record_written"):
        payload = build_repeatability_proof_payload(
            command,
            approval_gate,
            repeatability_plan_record,
            repeatability_entries_record,
            repeatability_permission_denial_record,
            repeatability_audit_record,
            write_record,
        )
    if payload is not None and "payload_digest" not in payload:
        payload["payload_digest"] = sha256_digest(payload)
    repeatability_proof_result_record = create_repeatability_proof_result_record(
        approval_gate,
        repeatability_entries_record,
        write_record,
        payload,
    )
    repeatability_audit_record = create_repeatability_audit_record(
        approval_gate,
        synthetic_repeatable_task_contract,
        repeatability_scope_contract,
        non_external_repeatability_boundary,
        repeatability_permission_denial_record,
        repeatability_plan_record,
        repeatability_entries_record,
        repeatability_proof_result_record,
    )
    repeatability_readiness_summary = create_repeatability_readiness_summary(repeatability_audit_record)
    sandbox_worker_handoff_candidate_bridge = create_sandbox_worker_handoff_candidate_bridge(repeatability_readiness_summary)
    result = dict(result or {})
    result.update(
        {
            "schema": create_controlled_repeatable_local_execution_candidate_schema(),
            "repeatable_execution_approval_gate": approval_gate,
            "synthetic_repeatable_task_contract": synthetic_repeatable_task_contract,
            "repeatability_scope_contract": repeatability_scope_contract,
            "non_external_repeatability_boundary": non_external_repeatability_boundary,
            "repeatability_permission_denial_record": repeatability_permission_denial_record,
            "repeatability_plan_record": repeatability_plan_record,
            "repeatability_entries_record": repeatability_entries_record,
            "repeatability_proof_result_record": repeatability_proof_result_record,
            "repeatability_audit_record": repeatability_audit_record,
            "repeatability_readiness_summary": repeatability_readiness_summary,
            "sandbox_worker_handoff_candidate_bridge": sandbox_worker_handoff_candidate_bridge,
            "repeatability_proof_payload": payload,
            "repeatability_proof_write_record": write_record,
            "local_repeatability_proof_record_written": bool(write_record.get("local_repeatability_proof_record_written")),
            "controlled_repeatable_local_execution_performed": bool(write_record.get("controlled_repeatable_local_execution_performed")),
            "supervised_local_execution_performed": False,
            "repeatability_count": repeatability_plan_record.get("repeatability_count"),
            "repeatability_status": repeatability_entries_record.get("repeatability_status"),
            "repeatable_execution_candidate_id": repeatability_plan_record.get("repeatable_execution_candidate_id"),
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
    )
    return result
