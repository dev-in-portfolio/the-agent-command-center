import hashlib
import json
import re
from pathlib import Path

SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION = "5.4.0"
SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_STATUS = "SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_LOCAL_PACKET_ONLY"
SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_PHASE = "Sandbox Worker Acknowledgement Candidate"
SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL = "station-chief-v5-3-repeatability-proof-reference"
DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME = "sandbox_worker_acknowledgement_candidate_packet.json"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", (label or "").lower()).strip("-")
    return value or default_label


def safe_acknowledgement_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME
    if packet_name in {".", ".."}:
        return DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME
    if "/" in packet_name or "\\" in packet_name:
        return DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME
    if not packet_name.endswith(".json"):
        return DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME
    if Path(packet_name).name != packet_name:
        return DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME
    return packet_name


def generate_sandbox_worker_acknowledgement_candidate_id(
    command: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    runtime_version: str = "5.4.0",
) -> str:
    command_digest = sha256_digest(
        {
            "command": command,
            "sandbox_worker_label": sandbox_worker_label,
            "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
            "runtime_version": runtime_version,
        }
    )
    return (
        "sandbox-worker-acknowledgement-candidate-v5-4-"
        f"{normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL)}-"
        f"{normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL)}-"
        f"{command_digest[:12]}"
    )


def _dangerous_flags() -> dict:
    return {
        "local_acknowledgement_packet_written": False,
        "sandbox_worker_acknowledgement_performed": False,
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


def create_sandbox_worker_acknowledgement_candidate_schema() -> dict:
    schema = {
        "schema_version": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION,
        "status": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_STATUS,
        "acknowledgement_type": "sandbox_worker_acknowledgement_candidate",
        "required_sections": [
            "sandbox_worker_acknowledgement_approval_gate",
            "v5_3_handoff_packet_reference_contract",
            "sandbox_worker_acknowledgement_reference_contract",
            "acknowledgement_scope_contract",
            "non_execution_acknowledgement_boundary",
            "acknowledgement_permission_denial_record",
            "acknowledgement_plan_record",
            "acknowledgement_packet_record",
            "acknowledgement_audit_record",
            "acknowledgement_readiness_summary",
            "sandbox_worker_acceptance_candidate_bridge",
        ],
        "required_token": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
    }
    schema.update(_dangerous_flags())
    return schema


def create_sandbox_worker_acknowledgement_approval_gate(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acknowledgement_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN
    has_operator = bool((human_operator or "").strip())
    has_worker_label = bool((sandbox_worker_label or "").strip())
    has_reference_label = bool((v5_3_handoff_packet_reference_label or "").strip())
    has_output_directory = bool((output_directory or "").strip())
    local_records_authorized = token_valid and has_operator and has_worker_label and has_reference_label
    local_packet_authorized = local_records_authorized and has_output_directory and acknowledgement_requested
    return {
        "approval_token": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN,
        "token_valid": token_valid,
        "human_operator": human_operator,
        "sandbox_worker_label": sandbox_worker_label,
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "v5_3_handoff_packet_reference_label_normalized": normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL),
        "output_directory": output_directory,
        "acknowledgement_requested": bool(acknowledgement_requested),
        "local_acknowledgement_records_authorized": local_records_authorized,
        "local_acknowledgement_packet_write_authorized": local_packet_authorized,
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
        "gate_status": "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET" if local_records_authorized else "BLOCKED_PENDING_V5_4_SANDBOX_WORKER_ACKNOWLEDGEMENT_APPROVAL",
    }


def create_v5_3_handoff_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_acknowledgement_records_authorized"):
        return {
            "contract_status": "BLOCKED",
            "contract_type": "v5_3_handoff_packet_reference_contract",
            "reason": "v5.3 handoff packet reference metadata not authorized.",
        }
    return {
        "contract_status": "CREATED",
        "contract_type": "v5_3_handoff_packet_reference_contract",
        "v5_3_handoff_packet_reference_label": approval_gate["v5_3_handoff_packet_reference_label"],
        "v5_3_handoff_packet_reference_label_normalized": approval_gate["v5_3_handoff_packet_reference_label_normalized"],
        "reference_is_metadata_only": True,
        "reference_is_not_read_from_disk": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "reference_does_not_start_worker": True,
    }


def create_sandbox_worker_acknowledgement_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_acknowledgement_records_authorized"):
        return {
            "contract_status": "BLOCKED",
            "contract_type": "sandbox_worker_acknowledgement_reference_contract",
            "reason": "sandbox worker acknowledgement metadata not authorized.",
        }
    return {
        "contract_status": "CREATED",
        "contract_type": "sandbox_worker_acknowledgement_reference_contract",
        "sandbox_worker_label": approval_gate["sandbox_worker_label"],
        "sandbox_worker_label_normalized": approval_gate["sandbox_worker_label_normalized"],
        "worker_is_metadata_only": True,
        "worker_is_not_running": True,
        "worker_is_not_started": True,
        "worker_cannot_call_tools": True,
        "worker_cannot_access_apis": True,
        "worker_cannot_access_network": True,
        "worker_cannot_access_credentials": True,
        "worker_cannot_access_secrets": True,
        "worker_cannot_access_environment": True,
        "worker_cannot_execute_tasks": True,
        "worker_cannot_route_live_work": True,
    }


def create_acknowledgement_scope_contract(approval_gate: dict, v5_3_handoff_packet_reference_contract: dict, sandbox_worker_acknowledgement_reference_contract: dict) -> dict:
    scope_pass = (
        approval_gate.get("local_acknowledgement_records_authorized")
        and v5_3_handoff_packet_reference_contract.get("contract_status") == "CREATED"
        and sandbox_worker_acknowledgement_reference_contract.get("contract_status") == "CREATED"
    )
    return {
        "scope_status": "PASS" if scope_pass else "BLOCKED",
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_3_handoff_packet_reference": True,
        "exactly_one_acknowledgement_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "acknowledgement_metadata_only": True,
        "no_worker_start": True,
        "no_agent_start": True,
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
        "no_api_network_deployment_production": True,
        "no_full_workforce_activation": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
    }


def create_non_execution_acknowledgement_boundary(approval_gate: dict, acknowledgement_scope_contract: dict) -> dict:
    boundary_pass = acknowledgement_scope_contract.get("scope_status") == "PASS" and approval_gate.get("local_acknowledgement_records_authorized")
    return {
        "boundary_status": "PASS" if boundary_pass else "BLOCKED",
        "sandbox_worker_acknowledgement_candidate_is_local_packet_only": True,
        "acknowledgement_packet_is_not_executed": True,
        "worker_is_not_started": True,
        "agent_is_not_started": True,
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
        "no_credentials_secrets_environment": True,
        "no_deployment": True,
        "no_production_execution": True,
        "sandbox_worker_acknowledgement_performed": False,
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
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_acknowledgement_permission_denial_record(sandbox_worker_label: str, v5_3_handoff_packet_reference_label: str) -> dict:
    return {
        "denial_status": "DENIED",
        "sandbox_worker_label": sandbox_worker_label,
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "worker_process_start": False,
        "agent_start": False,
        "real_queue_creation": False,
        "queue_writes": False,
        "scheduler_writes": False,
        "cron_writes": False,
        "task_enqueue": False,
        "arbitrary_task_execution": False,
        "user_task_execution": False,
        "shell_command_execution": False,
        "subprocess_execution": False,
        "live_task_assignment": False,
        "live_worker_routing": False,
        "live_orchestration": False,
        "external_tool_invocation": False,
        "api_access": False,
        "network_access": False,
        "socket_access": False,
        "dns_resolution": False,
        "credential_use": False,
        "credential_vault_access": False,
        "secret_reads": False,
        "environment_reads": False,
        "deployment": False,
        "production_execution": False,
        "production_activation": False,
        "github_push_by_worker": False,
        "full_workforce_activation": False,
        "baseline_mutation": False,
        "devinization_overlay_mutation": False,
        "dashboard_org_master_export_mutation": False,
        "ownership_metadata_mutation": False,
        "mutation_of_v5_3_handoff_packet": False,
        "execution_of_v5_3_handoff_packet": False,
    }


def create_acknowledgement_plan_record(
    command: str,
    approval_gate: dict,
    v5_3_handoff_packet_reference_contract: dict,
    sandbox_worker_acknowledgement_reference_contract: dict,
    acknowledgement_scope_contract: dict,
    non_execution_acknowledgement_boundary: dict,
    acknowledgement_permission_denial_record: dict,
) -> dict:
    ready = (
        approval_gate.get("local_acknowledgement_records_authorized")
        and v5_3_handoff_packet_reference_contract.get("contract_status") == "CREATED"
        and sandbox_worker_acknowledgement_reference_contract.get("contract_status") == "CREATED"
        and acknowledgement_scope_contract.get("scope_status") == "PASS"
        and non_execution_acknowledgement_boundary.get("boundary_status") == "PASS"
        and acknowledgement_permission_denial_record.get("denial_status") == "DENIED"
    )
    candidate_id = generate_sandbox_worker_acknowledgement_candidate_id(
        command=command or "",
        sandbox_worker_label=approval_gate.get("sandbox_worker_label", ""),
        v5_3_handoff_packet_reference_label=approval_gate.get("v5_3_handoff_packet_reference_label", ""),
    )
    return {
        "plan_status": "LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PLAN_CREATED" if ready else "BLOCKED",
        "acknowledgement_candidate_id": candidate_id,
        "synthetic_task_label": approval_gate.get("sandbox_worker_label", ""),
        "synthetic_task_label_normalized": approval_gate.get("sandbox_worker_label_normalized", DEFAULT_SANDBOX_WORKER_LABEL),
        "sandbox_worker_label": approval_gate.get("sandbox_worker_label", ""),
        "sandbox_worker_label_normalized": approval_gate.get("sandbox_worker_label_normalized", DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_3_handoff_packet_reference_label": approval_gate.get("v5_3_handoff_packet_reference_label", ""),
        "v5_3_handoff_packet_reference_label_normalized": approval_gate.get("v5_3_handoff_packet_reference_label_normalized", DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL),
        "human_operator": approval_gate.get("human_operator"),
        "acknowledgement_mode": "deterministic_local_acknowledgement_packet_only",
        "packet_runtime_state": "not_written",
        "worker_runtime_state": "not_started",
        "agent_runtime_state": "not_started",
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "agent_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
    }


def build_acknowledgement_packet_payload(
    command: str,
    approval_gate: dict,
    acknowledgement_plan_record: dict,
    output_directory: str,
    packet_name: str,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION,
        "acknowledgement_type": "sandbox_worker_acknowledgement_candidate",
        "acknowledgement_mode": "deterministic_local_acknowledgement_packet_only",
        "sandbox_worker_label": approval_gate.get("sandbox_worker_label", ""),
        "sandbox_worker_label_normalized": approval_gate.get("sandbox_worker_label_normalized", DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_3_handoff_packet_reference_label": approval_gate.get("v5_3_handoff_packet_reference_label", ""),
        "v5_3_handoff_packet_reference_label_normalized": approval_gate.get("v5_3_handoff_packet_reference_label_normalized", DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": bool(approval_gate.get("token_valid")),
        "acknowledgement_candidate_id": acknowledgement_plan_record.get("acknowledgement_candidate_id"),
        "packet_name": packet_name,
        "output_directory": output_directory,
        "acknowledgement_message": "Station Chief sandbox worker acknowledgement candidate wrote this deterministic local acknowledgement packet. No worker was started.",
        "command": command,
        "local_acknowledgement_packet_written": True,
        "sandbox_worker_acknowledgement_performed": True,
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


def write_sandbox_worker_acknowledgement_packet(output_directory: str, packet_name: str, payload: dict) -> dict:
    output_dir_path = Path(output_directory)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_dir_resolved = output_dir_path.resolve()
    packet_name = safe_acknowledgement_packet_name(packet_name)
    packet_path = (output_dir_path / packet_name).resolve()
    if output_dir_resolved != packet_path and output_dir_resolved not in packet_path.parents:
        raise ValueError("acknowledgement packet escaped output directory")
    packet_path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    return {
        "sandbox_worker_acknowledgement_write_record_version": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION,
        "write_status": "SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET_WRITTEN",
        "execution_status": "SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET_WRITTEN",
        "local_acknowledgement_packet_written": True,
        "sandbox_worker_acknowledgement_performed": True,
        "files_written_count": 1,
        "files_written": [packet_path.name],
        "packet_name": packet_path.name,
        "record_name": packet_path.name,
        "output_directory": str(output_dir_path.resolve()),
        "record_path": str(packet_path),
        "worker_process_started": False,
        "agent_started": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "task_executed": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
    }


def create_blocked_acknowledgement_packet_write_record(reason: str) -> dict:
    return {
        "sandbox_worker_acknowledgement_write_record_version": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "execution_status": "BLOCKED",
        "reason": reason,
        "local_acknowledgement_packet_written": False,
        "sandbox_worker_acknowledgement_performed": False,
        "files_written_count": 0,
        "files_written": [],
        "worker_process_started": False,
        "agent_started": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "task_executed": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
    }


def create_acknowledgement_packet_record(acknowledgement_packet_write_record: dict, payload: dict | None = None) -> dict:
    return {
        "packet_status": acknowledgement_packet_write_record.get("write_status", "BLOCKED"),
        "write_record": acknowledgement_packet_write_record,
        "payload_digest": None if payload is None else payload.get("payload_digest"),
        "local_acknowledgement_packet_written": bool(acknowledgement_packet_write_record.get("local_acknowledgement_packet_written")),
        "sandbox_worker_acknowledgement_performed": bool(acknowledgement_packet_write_record.get("sandbox_worker_acknowledgement_performed")),
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
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
    }


def create_acknowledgement_audit_record(
    approval_gate: dict,
    v5_3_handoff_packet_reference_contract: dict,
    sandbox_worker_acknowledgement_reference_contract: dict,
    acknowledgement_scope_contract: dict,
    non_execution_acknowledgement_boundary: dict,
    acknowledgement_permission_denial_record: dict,
    acknowledgement_plan_record: dict,
    acknowledgement_packet_record: dict,
) -> dict:
    dangerous_flags = _dangerous_flags()
    allowed_write = acknowledgement_packet_record.get("packet_status") == "SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET_WRITTEN"
    pass_all = (
        v5_3_handoff_packet_reference_contract.get("contract_status") == "CREATED"
        and sandbox_worker_acknowledgement_reference_contract.get("contract_status") == "CREATED"
        and acknowledgement_scope_contract.get("scope_status") == "PASS"
        and non_execution_acknowledgement_boundary.get("boundary_status") == "PASS"
        and acknowledgement_permission_denial_record.get("denial_status") == "DENIED"
        and acknowledgement_plan_record.get("plan_status") in {"LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PLAN_CREATED", "BLOCKED"}
        and all(value is False for value in dangerous_flags.values())
        and acknowledgement_packet_record.get("worker_process_started") is False
        and acknowledgement_packet_record.get("agent_started") is False
        and acknowledgement_packet_record.get("task_executed") is False
        and acknowledgement_packet_record.get("arbitrary_task_execution_performed") is False
        and acknowledgement_packet_record.get("user_task_execution_performed") is False
        and acknowledgement_packet_record.get("real_queue_created") is False
        and acknowledgement_packet_record.get("queue_write_performed") is False
        and acknowledgement_packet_record.get("scheduler_write_performed") is False
        and acknowledgement_packet_record.get("cron_write_performed") is False
        and acknowledgement_packet_record.get("task_enqueued") is False
        and acknowledgement_packet_record.get("live_task_assignment_performed") is False
        and acknowledgement_packet_record.get("live_worker_routing_performed") is False
        and acknowledgement_packet_record.get("live_orchestration_performed") is False
        and acknowledgement_packet_record.get("api_call_performed") is False
        and acknowledgement_packet_record.get("network_access_performed") is False
        and acknowledgement_packet_record.get("deployment_performed") is False
        and acknowledgement_packet_record.get("production_execution_performed") is False
        and acknowledgement_packet_record.get("full_workforce_activation_performed") is False
        and (not allowed_write or acknowledgement_packet_record.get("local_acknowledgement_packet_written") is True)
    )
    section_digests = {
        "approval_gate_digest": sha256_digest(approval_gate),
        "v5_3_handoff_packet_reference_contract_digest": sha256_digest(v5_3_handoff_packet_reference_contract),
        "sandbox_worker_acknowledgement_reference_contract_digest": sha256_digest(sandbox_worker_acknowledgement_reference_contract),
        "acknowledgement_scope_contract_digest": sha256_digest(acknowledgement_scope_contract),
        "non_execution_acknowledgement_boundary_digest": sha256_digest(non_execution_acknowledgement_boundary),
        "acknowledgement_permission_denial_record_digest": sha256_digest(acknowledgement_permission_denial_record),
        "acknowledgement_plan_record_digest": sha256_digest(acknowledgement_plan_record),
        "acknowledgement_packet_record_digest": sha256_digest(acknowledgement_packet_record),
    }
    record = {
        "audit_status": "PASS" if pass_all else "BLOCKED",
        "audit_reason": "Dangerous external booleans remain false." if pass_all else "One or more acknowledgement safety checks failed.",
        "allowed_write": allowed_write,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "section_digests": section_digests,
        "dangerous_booleans": dangerous_flags,
    }
    record["audit_digest"] = sha256_digest(record)
    return record


def create_acknowledgement_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "readiness_status": "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY" if ready else "BLOCKED",
        "next_layer": "Sandbox Worker Acceptance Candidate Review",
        "v5_5_not_built": True,
        "one_deterministic_local_sandbox_worker_acknowledgement_packet_permitted_only_under_v5_4_token": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_api_network_deployment_production": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_sandbox_worker_acceptance_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY"
    return {
        "bridge_status": "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY" if ready else "BLOCKED",
        "bridge_to": "Sandbox Worker Acceptance Candidate Review",
        "v5_5_review_only": True,
        "no_sandbox_worker_acceptance_in_v5_4": True,
        "no_worker_start_in_v5_4": True,
        "no_agent_start_in_v5_4": True,
        "no_queue_creation_in_v5_4": True,
        "no_task_enqueue_in_v5_4": True,
        "no_arbitrary_task_execution_in_v5_4": True,
        "no_user_task_execution_in_v5_4": True,
        "no_worker_routing_in_v5_4": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_sandbox_worker_acknowledgement_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    acknowledgement_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acknowledgement_requested: bool = False,
    write_acknowledgement_packet: bool = False,
) -> dict:
    command = command or ""
    sandbox_worker_label = sandbox_worker_label or ""
    v5_3_handoff_packet_reference_label = v5_3_handoff_packet_reference_label or ""
    packet_name = safe_acknowledgement_packet_name(acknowledgement_packet_name)
    schema = create_sandbox_worker_acknowledgement_candidate_schema()
    approval_gate = create_sandbox_worker_acknowledgement_approval_gate(
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        acknowledgement_requested=acknowledgement_requested,
    )
    v5_3_handoff_packet_reference_contract = create_v5_3_handoff_packet_reference_contract(approval_gate)
    sandbox_worker_acknowledgement_reference_contract = create_sandbox_worker_acknowledgement_reference_contract(approval_gate)
    acknowledgement_scope_contract = create_acknowledgement_scope_contract(
        approval_gate,
        v5_3_handoff_packet_reference_contract,
        sandbox_worker_acknowledgement_reference_contract,
    )
    non_execution_acknowledgement_boundary = create_non_execution_acknowledgement_boundary(
        approval_gate,
        acknowledgement_scope_contract,
    )
    acknowledgement_permission_denial_record = create_acknowledgement_permission_denial_record(
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
    )
    acknowledgement_plan_record = create_acknowledgement_plan_record(
        command=command,
        approval_gate=approval_gate,
        v5_3_handoff_packet_reference_contract=v5_3_handoff_packet_reference_contract,
        sandbox_worker_acknowledgement_reference_contract=sandbox_worker_acknowledgement_reference_contract,
        acknowledgement_scope_contract=acknowledgement_scope_contract,
        non_execution_acknowledgement_boundary=non_execution_acknowledgement_boundary,
        acknowledgement_permission_denial_record=acknowledgement_permission_denial_record,
    )
    if write_acknowledgement_packet:
        if not (
            approval_gate.get("local_acknowledgement_packet_write_authorized")
            and v5_3_handoff_packet_reference_contract.get("contract_status") == "CREATED"
            and sandbox_worker_acknowledgement_reference_contract.get("contract_status") == "CREATED"
            and acknowledgement_scope_contract.get("scope_status") == "PASS"
            and non_execution_acknowledgement_boundary.get("boundary_status") == "PASS"
            and acknowledgement_permission_denial_record.get("denial_status") == "DENIED"
            and acknowledgement_plan_record.get("plan_status") == "LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PLAN_CREATED"
        ):
            acknowledgement_packet_write_record = create_blocked_acknowledgement_packet_write_record(
                "sandbox worker acknowledgement packet write not authorized"
            )
            acknowledgement_payload = None
        else:
            acknowledgement_payload = build_acknowledgement_packet_payload(
                command=command,
                approval_gate=approval_gate,
                acknowledgement_plan_record=acknowledgement_plan_record,
                output_directory=output_directory or "",
                packet_name=packet_name,
            )
            acknowledgement_packet_write_record = write_sandbox_worker_acknowledgement_packet(
                output_directory=output_directory or "",
                packet_name=packet_name,
                payload=acknowledgement_payload,
            )
    else:
        acknowledgement_packet_write_record = create_blocked_acknowledgement_packet_write_record(
            "sandbox worker acknowledgement packet write not requested"
        )
        acknowledgement_payload = None
    acknowledgement_packet_record = create_acknowledgement_packet_record(
        acknowledgement_packet_write_record,
        payload=acknowledgement_payload,
    )
    acknowledgement_audit_record = create_acknowledgement_audit_record(
        approval_gate,
        v5_3_handoff_packet_reference_contract,
        sandbox_worker_acknowledgement_reference_contract,
        acknowledgement_scope_contract,
        non_execution_acknowledgement_boundary,
        acknowledgement_permission_denial_record,
        acknowledgement_plan_record,
        acknowledgement_packet_record,
    )
    acknowledgement_readiness_summary = create_acknowledgement_readiness_summary(acknowledgement_audit_record)
    sandbox_worker_acceptance_candidate_bridge = create_sandbox_worker_acceptance_candidate_bridge(acknowledgement_readiness_summary)
    bundle = {
        "sandbox_worker_acknowledgement_candidate_bundle_version": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION,
        "schema": schema,
        "sandbox_worker_acknowledgement_approval_gate": approval_gate,
        "v5_3_handoff_packet_reference_contract": v5_3_handoff_packet_reference_contract,
        "sandbox_worker_acknowledgement_reference_contract": sandbox_worker_acknowledgement_reference_contract,
        "acknowledgement_scope_contract": acknowledgement_scope_contract,
        "non_execution_acknowledgement_boundary": non_execution_acknowledgement_boundary,
        "acknowledgement_permission_denial_record": acknowledgement_permission_denial_record,
        "acknowledgement_plan_record": acknowledgement_plan_record,
        "acknowledgement_packet_record": acknowledgement_packet_record,
        "acknowledgement_audit_record": acknowledgement_audit_record,
        "acknowledgement_readiness_summary": acknowledgement_readiness_summary,
        "sandbox_worker_acceptance_candidate_bridge": sandbox_worker_acceptance_candidate_bridge,
        "acknowledgement_packet_write_record": acknowledgement_packet_write_record,
        "acknowledgement_packet_payload": acknowledgement_payload,
        "sandbox_worker_acknowledgement_candidate_id": acknowledgement_plan_record["acknowledgement_candidate_id"],
        "local_acknowledgement_packet_written": acknowledgement_packet_write_record.get("local_acknowledgement_packet_written", False),
        "sandbox_worker_acknowledgement_performed": acknowledgement_packet_write_record.get("sandbox_worker_acknowledgement_performed", False),
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
        "acknowledgement_candidate_status": SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_STATUS,
        "acknowledgement_candidate_next_step": "Next step: sandbox worker acceptance candidate review only.",
        "sandbox_worker_acknowledgement_candidate_next_step": "Next step: sandbox worker acceptance candidate review only.",
    }
    if result is not None:
        result = dict(result)
        result["sandbox_worker_acknowledgement_candidate_bundle"] = bundle
        result["sandbox_worker_acknowledgement_candidate_write_summary"] = acknowledgement_packet_write_record
        result["sandbox_worker_acknowledgement_candidate_schema"] = schema
        result["schema"] = schema
        result["acknowledgement_packet_write_record"] = acknowledgement_packet_write_record
        result["acknowledgement_packet_payload"] = acknowledgement_payload
        result["acknowledgement_candidate_id"] = bundle["sandbox_worker_acknowledgement_candidate_id"]
        result["sandbox_worker_acknowledgement_candidate_id"] = bundle["sandbox_worker_acknowledgement_candidate_id"]
        result["acknowledgement_candidate_next_step"] = bundle["acknowledgement_candidate_next_step"]
        result["sandbox_worker_acknowledgement_candidate_next_step"] = bundle["sandbox_worker_acknowledgement_candidate_next_step"]
        result["acknowledgement_candidate_status"] = SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_STATUS
        result["sandbox_worker_acknowledgement_approval_gate"] = approval_gate
        result["v5_3_handoff_packet_reference_contract"] = v5_3_handoff_packet_reference_contract
        result["sandbox_worker_acknowledgement_reference_contract"] = sandbox_worker_acknowledgement_reference_contract
        result["acknowledgement_scope_contract"] = acknowledgement_scope_contract
        result["non_execution_acknowledgement_boundary"] = non_execution_acknowledgement_boundary
        result["acknowledgement_permission_denial_record"] = acknowledgement_permission_denial_record
        result["acknowledgement_plan_record"] = acknowledgement_plan_record
        result["acknowledgement_packet_record"] = acknowledgement_packet_record
        result["acknowledgement_audit_record"] = acknowledgement_audit_record
        result["acknowledgement_readiness_summary"] = acknowledgement_readiness_summary
        result["sandbox_worker_acceptance_candidate_bridge"] = sandbox_worker_acceptance_candidate_bridge
        result["local_acknowledgement_packet_written"] = bundle["local_acknowledgement_packet_written"]
        result["sandbox_worker_acknowledgement_performed"] = bundle["sandbox_worker_acknowledgement_performed"]
        result["worker_process_started"] = False
        result["agent_started"] = False
        result["real_queue_created"] = False
        result["queue_write_performed"] = False
        result["scheduler_write_performed"] = False
        result["cron_write_performed"] = False
        result["task_enqueued"] = False
        result["task_executed"] = False
        result["arbitrary_task_execution_performed"] = False
        result["user_task_execution_performed"] = False
        result["live_task_assignment_performed"] = False
        result["live_worker_routing_performed"] = False
        result["live_orchestration_performed"] = False
        result["api_call_performed"] = False
        result["network_access_performed"] = False
        result["deployment_performed"] = False
        result["production_execution_performed"] = False
        result["full_workforce_activation_performed"] = False
        return result
    return bundle
