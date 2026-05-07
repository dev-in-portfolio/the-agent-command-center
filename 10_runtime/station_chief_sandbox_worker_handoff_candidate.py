#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION = "5.3.0"
SANDBOX_WORKER_HANDOFF_CANDIDATE_STATUS = "SANDBOX_WORKER_HANDOFF_CANDIDATE_LOCAL_PACKET_ONLY"
SANDBOX_WORKER_HANDOFF_CANDIDATE_PHASE = "Sandbox Worker Handoff Candidate"
SANDBOX_WORKER_HANDOFF_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_HANDOFF_CANDIDATE"
DEFAULT_SYNTHETIC_TASK_LABEL = "station-chief-sandbox-worker-handoff-status-note-task"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_2_REPEATABILITY_PROOF_REFERENCE_LABEL = "station-chief-v5-2-repeatability-proof-reference"
DEFAULT_SANDBOX_HANDOFF_PACKET_NAME = "sandbox_worker_handoff_candidate_packet.json"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str, default_label: str) -> str:
    text = (label or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or default_label


def safe_handoff_packet_name(packet_name: str | None) -> str:
    default = DEFAULT_SANDBOX_HANDOFF_PACKET_NAME
    if not packet_name:
        return default
    candidate = str(packet_name).strip()
    if candidate in {"", ".", ".."}:
        return default
    if "/" in candidate or "\\" in candidate:
        return default
    if not candidate.endswith(".json"):
        return default
    return candidate


def generate_sandbox_worker_handoff_candidate_id(
    command: str,
    synthetic_task_label: str,
    sandbox_worker_label: str,
    v5_2_repeatability_proof_reference_label: str,
    runtime_version: str = SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_task_label = normalize_label(synthetic_task_label, DEFAULT_SYNTHETIC_TASK_LABEL)
    normalized_worker_label = normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL)
    normalized_reference_label = normalize_label(
        v5_2_repeatability_proof_reference_label,
        DEFAULT_V5_2_REPEATABILITY_PROOF_REFERENCE_LABEL,
    )
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "synthetic_task_label": normalized_task_label,
            "sandbox_worker_label": normalized_worker_label,
            "v5_2_repeatability_proof_reference_label": normalized_reference_label,
        }
    )
    return f"sandbox-worker-handoff-candidate-v5-3-{normalized_task_label}-{normalized_worker_label}-{digest[:12]}"


def _false_booleans() -> dict:
    return {
        "local_handoff_packet_written": False,
        "sandbox_worker_handoff_performed": False,
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
        "agent_started": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_sandbox_worker_handoff_candidate_schema() -> dict:
    return {
        "schema_version": SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION,
        "status": SANDBOX_WORKER_HANDOFF_CANDIDATE_STATUS,
        "handoff_type": "sandbox_worker_handoff_candidate",
        "required_token": SANDBOX_WORKER_HANDOFF_CANDIDATE_APPROVAL_TOKEN,
        "required_sections": [
            "sandbox_worker_handoff_approval_gate",
            "v5_2_repeatability_proof_reference_contract",
            "synthetic_task_handoff_contract",
            "sandbox_worker_reference_contract",
            "handoff_scope_contract",
            "non_execution_handoff_boundary",
            "handoff_permission_denial_record",
            "handoff_plan_record",
            "handoff_packet_record",
            "handoff_audit_record",
            "handoff_readiness_summary",
            "sandbox_worker_acknowledgement_candidate_bridge",
        ],
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_sandbox_worker_handoff_approval_gate(
    synthetic_task_label: str,
    sandbox_worker_label: str,
    v5_2_repeatability_proof_reference_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    handoff_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == SANDBOX_WORKER_HANDOFF_CANDIDATE_APPROVAL_TOKEN
    records_authorized = bool(
        token_valid
        and human_operator
        and synthetic_task_label
        and sandbox_worker_label
        and v5_2_repeatability_proof_reference_label
    )
    packet_write_authorized = bool(
        records_authorized and output_directory and handoff_requested
    )
    return {
        "gate_status": (
            "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_HANDOFF_PACKET"
            if records_authorized
            else "BLOCKED_PENDING_V5_3_SANDBOX_WORKER_HANDOFF_APPROVAL"
        ),
        "approval_token_valid": token_valid,
        "human_operator": human_operator,
        "synthetic_task_label": synthetic_task_label,
        "sandbox_worker_label": sandbox_worker_label,
        "v5_2_repeatability_proof_reference_label": v5_2_repeatability_proof_reference_label,
        "synthetic_task_label_normalized": normalize_label(synthetic_task_label, DEFAULT_SYNTHETIC_TASK_LABEL),
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_2_repeatability_proof_reference_label_normalized": normalize_label(
            v5_2_repeatability_proof_reference_label,
            DEFAULT_V5_2_REPEATABILITY_PROOF_REFERENCE_LABEL,
        ),
        "output_directory": output_directory,
        "handoff_requested": bool(handoff_requested),
        "local_handoff_records_authorized": records_authorized,
        "local_handoff_packet_write_authorized": packet_write_authorized,
        "worker_process_start_authorized": False,
        "agent_start_authorized": False,
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
        "api_call_authorized": False,
        "network_access_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
    }


def create_v5_2_repeatability_proof_reference_contract(approval_gate: dict) -> dict:
    created = bool(approval_gate.get("local_handoff_records_authorized"))
    return {
        "contract_status": "CREATED" if created else "BLOCKED",
        "contract_created": created,
        "reference_type": "v5_2_repeatability_proof_reference_label",
        "reference_is_metadata_only": True,
        "reference_is_not_read_from_disk": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "reference_label": approval_gate.get("v5_2_repeatability_proof_reference_label"),
        "reference_label_normalized": approval_gate.get("v5_2_repeatability_proof_reference_label_normalized"),
    }


def create_synthetic_task_handoff_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_handoff_records_authorized"):
        return {
            "contract_status": "BLOCKED",
            "contract_created": False,
            "handoff_mode": "deterministic_local_handoff_packet_only",
            "task_is_synthetic": True,
            "task_has_no_user_data": True,
            "task_has_no_external_dependency": True,
            "task_is_not_enqueued": True,
            "task_is_not_arbitrary_code": True,
            "task_is_not_shell_command": True,
            "task_is_not_executed_as_process": True,
            "synthetic_task_label": approval_gate.get("synthetic_task_label"),
            "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
        }
    return {
        "contract_status": "CREATED",
        "contract_created": True,
        "handoff_mode": "deterministic_local_handoff_packet_only",
        "task_is_synthetic": True,
        "task_has_no_user_data": True,
        "task_has_no_external_dependency": True,
        "task_is_not_enqueued": True,
        "task_is_not_arbitrary_code": True,
        "task_is_not_shell_command": True,
        "task_is_not_executed_as_process": True,
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
    }


def create_sandbox_worker_reference_contract(approval_gate: dict) -> dict:
    created = bool(approval_gate.get("local_handoff_records_authorized"))
    return {
        "contract_status": "CREATED" if created else "BLOCKED",
        "contract_created": created,
        "sandbox_worker_label": approval_gate.get("sandbox_worker_label"),
        "sandbox_worker_label_normalized": approval_gate.get("sandbox_worker_label_normalized"),
        "worker_is_metadata_only": True,
        "worker_is_not_running_process": True,
        "worker_can_not_call_tools": True,
        "worker_can_not_access_apis": True,
        "worker_can_not_access_network": True,
        "worker_can_not_access_credentials_secrets_or_environment": True,
        "worker_can_not_execute_tasks": True,
        "worker_can_not_route_live_work": True,
    }


def create_handoff_scope_contract(
    approval_gate: dict,
    v5_2_repeatability_proof_reference_contract: dict,
    synthetic_task_handoff_contract: dict,
    sandbox_worker_reference_contract: dict,
) -> dict:
    scope_pass = bool(
        approval_gate.get("local_handoff_records_authorized")
        and v5_2_repeatability_proof_reference_contract.get("contract_created")
        and synthetic_task_handoff_contract.get("contract_created")
        and sandbox_worker_reference_contract.get("contract_created")
    )
    return {
        "scope_status": "PASS" if scope_pass else "BLOCKED",
        "scope_pass": scope_pass,
        "exactly_one_synthetic_task": True,
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_2_reference": True,
        "exactly_one_handoff_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
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
        "no_agent_start": True,
        "no_api_network_deployment_production": True,
    }


def create_non_execution_handoff_boundary(
    approval_gate: dict,
    handoff_scope_contract: dict,
) -> dict:
    boundary_pass = bool(handoff_scope_contract.get("scope_pass"))
    return {
        "boundary_status": "PASS" if boundary_pass else "BLOCKED",
        "boundary_pass": boundary_pass,
        "sandbox_worker_handoff_performed": False,
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
        "no_agent_start": True,
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
        **_false_booleans(),
    }


def create_handoff_permission_denial_record(
    synthetic_task_label: str,
    sandbox_worker_label: str,
) -> dict:
    return {
        "synthetic_task_label": synthetic_task_label,
        "sandbox_worker_label": sandbox_worker_label,
        "worker_process_start": "denied",
        "agent_start": "denied",
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
        "live_work_orchestration": "denied",
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
    }


def create_handoff_plan_record(
    command: str,
    approval_gate: dict,
    v5_2_repeatability_proof_reference_contract: dict,
    synthetic_task_handoff_contract: dict,
    sandbox_worker_reference_contract: dict,
    handoff_scope_contract: dict,
    non_execution_handoff_boundary: dict,
) -> dict:
    planned = bool(
        approval_gate.get("local_handoff_records_authorized")
        and v5_2_repeatability_proof_reference_contract.get("contract_created")
        and synthetic_task_handoff_contract.get("contract_created")
        and sandbox_worker_reference_contract.get("contract_created")
        and handoff_scope_contract.get("scope_pass")
        and non_execution_handoff_boundary.get("boundary_pass")
    )
    candidate_id = generate_sandbox_worker_handoff_candidate_id(
        command,
        approval_gate.get("synthetic_task_label") or DEFAULT_SYNTHETIC_TASK_LABEL,
        approval_gate.get("sandbox_worker_label") or DEFAULT_SANDBOX_WORKER_LABEL,
        approval_gate.get("v5_2_repeatability_proof_reference_label")
        or DEFAULT_V5_2_REPEATABILITY_PROOF_REFERENCE_LABEL,
    )
    return {
        "plan_status": "LOCAL_SANDBOX_WORKER_HANDOFF_PLAN_CREATED" if planned else "BLOCKED",
        "candidate_planned": planned,
        "handoff_candidate_id": candidate_id,
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "synthetic_task_label_normalized": approval_gate.get("synthetic_task_label_normalized"),
        "sandbox_worker_label": approval_gate.get("sandbox_worker_label"),
        "sandbox_worker_label_normalized": approval_gate.get("sandbox_worker_label_normalized"),
        "v5_2_repeatability_proof_reference_label": approval_gate.get("v5_2_repeatability_proof_reference_label"),
        "v5_2_repeatability_proof_reference_label_normalized": approval_gate.get("v5_2_repeatability_proof_reference_label_normalized"),
        "human_operator": approval_gate.get("human_operator"),
        "handoff_mode": "deterministic_local_handoff_packet_only",
        "packet_runtime_state": "not_written",
        "worker_runtime_state": "not_started",
        "agent_runtime_state": "not_started",
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "agent_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
    }


def build_handoff_packet_payload(
    command: str,
    approval_gate: dict,
    handoff_plan_record: dict,
    handoff_packet_record: dict,
    write_record: dict | None = None,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION,
        "handoff_type": "sandbox_worker_handoff_candidate",
        "handoff_mode": "deterministic_local_handoff_packet_only",
        "synthetic_task_label": approval_gate.get("synthetic_task_label"),
        "sandbox_worker_label": approval_gate.get("sandbox_worker_label"),
        "v5_2_repeatability_proof_reference_label": approval_gate.get("v5_2_repeatability_proof_reference_label"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("approval_token_valid"),
        "handoff_candidate_id": handoff_plan_record.get("handoff_candidate_id"),
        "packet_message": "Station Chief sandbox worker handoff candidate wrote this deterministic local handoff packet. No worker was started.",
        "local_handoff_packet_written": bool(write_record and write_record.get("local_handoff_packet_written")),
        "sandbox_worker_handoff_performed": bool(write_record and write_record.get("sandbox_worker_handoff_performed")),
        "worker_process_started": False,
        "agent_started": False,
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
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_sandbox_worker_handoff_packet(
    output_directory: str,
    packet_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_handoff_packet_name(packet_name)
    packet_path = (output_dir / safe_name).resolve()
    packet_path.relative_to(output_dir)
    packet_path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    return {
        "sandbox_worker_handoff_write_record_version": SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION,
        "write_status": "SANDBOX_WORKER_HANDOFF_PACKET_WRITTEN",
        "local_handoff_packet_written": True,
        "sandbox_worker_handoff_performed": True,
        "files_written_count": 1,
        "output_directory": str(output_dir),
        "packet_name": safe_name,
        "record_path": str(packet_path),
        "worker_process_started": False,
        "agent_started": False,
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
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_blocked_handoff_packet_write_record(reason: str) -> dict:
    return {
        "sandbox_worker_handoff_write_record_version": SANDBOX_WORKER_HANDOFF_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "reason": reason,
        "local_handoff_packet_written": False,
        "sandbox_worker_handoff_performed": False,
        "files_written_count": 0,
        "worker_process_started": False,
        "agent_started": False,
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
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_handoff_packet_record(
    approval_gate: dict,
    handoff_plan_record: dict,
    payload: dict | None,
    write_record: dict,
) -> dict:
    packet_status = write_record.get("write_status", "BLOCKED")
    return {
        "packet_status": packet_status,
        "write_record": write_record,
        "payload_digest": payload.get("payload_digest") if payload else None,
        "handoff_candidate_id": handoff_plan_record.get("handoff_candidate_id"),
        "local_handoff_packet_written": bool(write_record.get("local_handoff_packet_written")),
        "sandbox_worker_handoff_performed": bool(write_record.get("sandbox_worker_handoff_performed")),
        "worker_process_started": False,
        "agent_started": False,
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
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_handoff_audit_record(
    approval_gate: dict,
    v5_2_repeatability_proof_reference_contract: dict,
    synthetic_task_handoff_contract: dict,
    sandbox_worker_reference_contract: dict,
    handoff_scope_contract: dict,
    non_execution_handoff_boundary: dict,
    handoff_permission_denial_record: dict,
    handoff_plan_record: dict,
    handoff_packet_record: dict,
) -> dict:
    section_digests = {
        "sandbox_worker_handoff_approval_gate": sha256_digest(approval_gate),
        "v5_2_repeatability_proof_reference_contract": sha256_digest(v5_2_repeatability_proof_reference_contract),
        "synthetic_task_handoff_contract": sha256_digest(synthetic_task_handoff_contract),
        "sandbox_worker_reference_contract": sha256_digest(sandbox_worker_reference_contract),
        "handoff_scope_contract": sha256_digest(handoff_scope_contract),
        "non_execution_handoff_boundary": sha256_digest(non_execution_handoff_boundary),
        "handoff_permission_denial_record": sha256_digest(handoff_permission_denial_record),
        "handoff_plan_record": sha256_digest(handoff_plan_record),
        "handoff_packet_record": sha256_digest(handoff_packet_record),
    }
    dangerous_clear = all(
        value is False
        for value in [
            handoff_packet_record.get("worker_process_started"),
            handoff_packet_record.get("agent_started"),
            handoff_packet_record.get("real_queue_created"),
            handoff_packet_record.get("queue_write_performed"),
            handoff_packet_record.get("scheduler_write_performed"),
            handoff_packet_record.get("cron_write_performed"),
            handoff_packet_record.get("task_enqueued"),
            handoff_packet_record.get("task_executed"),
            handoff_packet_record.get("arbitrary_task_execution_performed"),
            handoff_packet_record.get("user_task_execution_performed"),
            handoff_packet_record.get("live_task_assignment_performed"),
            handoff_packet_record.get("live_worker_routing_performed"),
            handoff_packet_record.get("live_orchestration_performed"),
            handoff_packet_record.get("external_tool_invocation_performed"),
            handoff_packet_record.get("api_call_performed"),
            handoff_packet_record.get("network_access_performed"),
            handoff_packet_record.get("deployment_performed"),
            handoff_packet_record.get("production_execution_performed"),
            handoff_packet_record.get("full_workforce_activation_performed"),
        ]
    )
    return {
        "audit_status": "PASS" if dangerous_clear else "BLOCKED",
        "audit_digest": sha256_digest(section_digests),
        "section_digests": section_digests,
        "sandbox_worker_handoff_performed": bool(handoff_packet_record.get("sandbox_worker_handoff_performed")),
        "local_handoff_packet_written": bool(handoff_packet_record.get("local_handoff_packet_written")),
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_handoff_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "readiness_status": (
            "READY_FOR_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "next_layer": "Sandbox Worker Acknowledgement Candidate Review",
        "v5_4_not_built": True,
        "one_deterministic_handoff_packet_permitted_only_under_token_gated_temp_dir_write_path": True,
        "sandbox_worker_handoff_performed": bool(audit_record.get("sandbox_worker_handoff_performed")),
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
        "no_agent_start": True,
        "no_api_network_deployment_production": True,
        **_false_booleans(),
    }


def create_sandbox_worker_acknowledgement_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_REVIEW_ONLY"
    return {
        "bridge_status": (
            "READY_FOR_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "bridge_ready": ready,
        "v5_4_not_built": True,
        "no_sandbox_worker_acknowledgement_in_v5_3": True,
        "no_worker_start_in_v5_3": True,
        "no_agent_start_in_v5_3": True,
        "no_real_queue_in_v5_3": True,
        "no_queue_write_in_v5_3": True,
        "no_task_enqueue_in_v5_3": True,
        "no_arbitrary_task_execution_in_v5_3": True,
        "no_user_task_execution_in_v5_3": True,
        "no_live_routing_in_v5_3": True,
        "no_live_orchestration_in_v5_3": True,
        **_false_booleans(),
    }


def create_sandbox_worker_handoff_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    synthetic_task_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_2_repeatability_proof_reference_label: str | None = None,
    output_directory: str | None = None,
    handoff_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    handoff_requested: bool = False,
    write_handoff_packet: bool = False,
) -> dict:
    command = command or "check please"
    synthetic_task_label = synthetic_task_label or DEFAULT_SYNTHETIC_TASK_LABEL
    sandbox_worker_label = sandbox_worker_label or DEFAULT_SANDBOX_WORKER_LABEL
    v5_2_repeatability_proof_reference_label = (
        v5_2_repeatability_proof_reference_label
        or DEFAULT_V5_2_REPEATABILITY_PROOF_REFERENCE_LABEL
    )
    approval_gate = create_sandbox_worker_handoff_approval_gate(
        synthetic_task_label=synthetic_task_label,
        sandbox_worker_label=sandbox_worker_label,
        v5_2_repeatability_proof_reference_label=v5_2_repeatability_proof_reference_label,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        handoff_requested=handoff_requested,
    )
    v5_2_repeatability_proof_reference_contract = create_v5_2_repeatability_proof_reference_contract(approval_gate)
    synthetic_task_handoff_contract = create_synthetic_task_handoff_contract(approval_gate)
    sandbox_worker_reference_contract = create_sandbox_worker_reference_contract(approval_gate)
    handoff_scope_contract = create_handoff_scope_contract(
        approval_gate,
        v5_2_repeatability_proof_reference_contract,
        synthetic_task_handoff_contract,
        sandbox_worker_reference_contract,
    )
    non_execution_handoff_boundary = create_non_execution_handoff_boundary(
        approval_gate,
        handoff_scope_contract,
    )
    handoff_permission_denial_record = create_handoff_permission_denial_record(
        approval_gate.get("synthetic_task_label") or synthetic_task_label,
        approval_gate.get("sandbox_worker_label") or sandbox_worker_label,
    )
    handoff_plan_record = create_handoff_plan_record(
        command,
        approval_gate,
        v5_2_repeatability_proof_reference_contract,
        synthetic_task_handoff_contract,
        sandbox_worker_reference_contract,
        handoff_scope_contract,
        non_execution_handoff_boundary,
    )
    write_record = create_blocked_handoff_packet_write_record("sandbox worker handoff packet write not requested")
    payload = None
    if write_handoff_packet:
        if (
            approval_gate.get("local_handoff_packet_write_authorized")
            and v5_2_repeatability_proof_reference_contract.get("contract_created")
            and synthetic_task_handoff_contract.get("contract_created")
            and sandbox_worker_reference_contract.get("contract_created")
            and handoff_scope_contract.get("scope_pass")
            and non_execution_handoff_boundary.get("boundary_pass")
            and handoff_plan_record.get("plan_status") == "LOCAL_SANDBOX_WORKER_HANDOFF_PLAN_CREATED"
        ):
            payload = build_handoff_packet_payload(
                command,
                approval_gate,
                handoff_plan_record,
                {"packet_status": "SANDBOX_WORKER_HANDOFF_PACKET_WRITTEN"},
                {"local_handoff_packet_written": True, "sandbox_worker_handoff_performed": True},
            )
            write_record = write_sandbox_worker_handoff_packet(
                output_directory=str(output_directory),
                packet_name=handoff_packet_name or DEFAULT_SANDBOX_HANDOFF_PACKET_NAME,
                payload=payload,
            )
        else:
            write_record = create_blocked_handoff_packet_write_record("sandbox worker handoff packet write not authorized")
    handoff_packet_record = create_handoff_packet_record(
        approval_gate,
        handoff_plan_record,
        payload,
        write_record,
    )
    handoff_audit_record = create_handoff_audit_record(
        approval_gate,
        v5_2_repeatability_proof_reference_contract,
        synthetic_task_handoff_contract,
        sandbox_worker_reference_contract,
        handoff_scope_contract,
        non_execution_handoff_boundary,
        handoff_permission_denial_record,
        handoff_plan_record,
        handoff_packet_record,
    )
    if payload is None and write_record.get("local_handoff_packet_written"):
        payload = build_handoff_packet_payload(
            command,
            approval_gate,
            handoff_plan_record,
            handoff_packet_record,
            write_record,
        )
    if payload is not None and "payload_digest" not in payload:
        payload["payload_digest"] = sha256_digest(payload)
    handoff_packet_record = create_handoff_packet_record(
        approval_gate,
        handoff_plan_record,
        payload,
        write_record,
    )
    handoff_audit_record = create_handoff_audit_record(
        approval_gate,
        v5_2_repeatability_proof_reference_contract,
        synthetic_task_handoff_contract,
        sandbox_worker_reference_contract,
        handoff_scope_contract,
        non_execution_handoff_boundary,
        handoff_permission_denial_record,
        handoff_plan_record,
        handoff_packet_record,
    )
    handoff_readiness_summary = create_handoff_readiness_summary(handoff_audit_record)
    sandbox_worker_acknowledgement_candidate_bridge = create_sandbox_worker_acknowledgement_candidate_bridge(
        handoff_readiness_summary
    )
    result = dict(result or {})
    result.update(
        {
            "schema": create_sandbox_worker_handoff_candidate_schema(),
            "sandbox_worker_handoff_approval_gate": approval_gate,
            "v5_2_repeatability_proof_reference_contract": v5_2_repeatability_proof_reference_contract,
            "synthetic_task_handoff_contract": synthetic_task_handoff_contract,
            "sandbox_worker_reference_contract": sandbox_worker_reference_contract,
            "handoff_scope_contract": handoff_scope_contract,
            "non_execution_handoff_boundary": non_execution_handoff_boundary,
            "handoff_permission_denial_record": handoff_permission_denial_record,
            "handoff_plan_record": handoff_plan_record,
            "handoff_packet_record": handoff_packet_record,
            "handoff_audit_record": handoff_audit_record,
            "handoff_readiness_summary": handoff_readiness_summary,
            "sandbox_worker_acknowledgement_candidate_bridge": sandbox_worker_acknowledgement_candidate_bridge,
            "handoff_packet_payload": payload,
            "handoff_packet_write_record": write_record,
            "local_handoff_packet_written": bool(write_record.get("local_handoff_packet_written")),
            "sandbox_worker_handoff_performed": bool(write_record.get("sandbox_worker_handoff_performed")),
            "worker_process_started": False,
            "agent_started": False,
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
            "external_tool_invocation_performed": False,
            "api_call_performed": False,
            "network_access_performed": False,
            "deployment_performed": False,
            "production_execution_performed": False,
            "full_workforce_activation_performed": False,
            "handoff_candidate_id": handoff_plan_record.get("handoff_candidate_id"),
            "sandbox_worker_handoff_candidate_id": handoff_plan_record.get("handoff_candidate_id"),
            "synthetic_task_label": approval_gate.get("synthetic_task_label"),
            "sandbox_worker_label": approval_gate.get("sandbox_worker_label"),
            "v5_2_repeatability_proof_reference_label": approval_gate.get("v5_2_repeatability_proof_reference_label"),
            "handoff_packet_name": write_record.get("packet_name"),
            "handoff_packet_record_status": handoff_packet_record.get("packet_status"),
            "sandbox_worker_handoff_candidate_next_step": "Next step: sandbox worker acknowledgement candidate review only.",
        }
    )
    return result
