"""
Station Chief Runtime v5.6.0 Sandbox Worker Ready-State Packet Candidate Module
"""

import json
import hashlib
import re
from pathlib import Path

SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_MODULE_VERSION = "5.6.0"
SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_STATUS = "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_LOCAL_PACKET_ONLY"
SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_PHASE = "Sandbox Worker Ready-State Packet Candidate"
SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL = "station-chief-v5-3-sandbox-worker-handoff-packet-reference"
DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-4-sandbox-worker-acknowledgement-packet-reference"
DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL = "station-chief-v5-5-sandbox-worker-acceptance-candidate-review-packet-reference"
DEFAULT_SANDBOX_READY_STATE_PACKET_NAME = "sandbox_worker_ready_state_packet_candidate.json"


def canonical_json(data: object) -> str:
    return json.dumps(data, separators=(',', ':'), sort_keys=True)


def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode('utf-8')).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    normalized = label.lower()
    normalized = re.sub(r'[^a-z0-9]+', '-', normalized)
    normalized = normalized.strip('-')
    if not normalized:
        return default_label
    return normalized


def safe_ready_state_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_SANDBOX_READY_STATE_PACKET_NAME
    if not packet_name.endswith('.json'):
        return DEFAULT_SANDBOX_READY_STATE_PACKET_NAME
    if '/' in packet_name or '\\' in packet_name:
        return DEFAULT_SANDBOX_READY_STATE_PACKET_NAME
    if packet_name in ('.', '..'):
        return DEFAULT_SANDBOX_READY_STATE_PACKET_NAME
    return packet_name


def generate_sandbox_worker_ready_state_packet_candidate_id(
    command: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    runtime_version: str = "5.6.0"
) -> str:
    norm_worker = normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL)
    norm_handoff = normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL)
    norm_ack = normalize_label(v5_4_acknowledgement_packet_reference_label, DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL)
    norm_acceptance = normalize_label(v5_5_acceptance_review_packet_reference_label, DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL)
    h = sha256_digest({
        "command": command,
        "worker": norm_worker,
        "handoff": norm_handoff,
        "ack": norm_ack,
        "acceptance": norm_acceptance,
        "version": runtime_version
    })[:12]
    return f"sandbox-worker-ready-state-packet-candidate-v5-6-{norm_worker}-{norm_handoff}-{norm_ack}-{norm_acceptance}-{h}"


def create_sandbox_worker_ready_state_packet_candidate_schema() -> dict:
    return {
        "schema_version": "5.6.0",
        "status": "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_LOCAL_PACKET_ONLY",
        "ready_state_type": "sandbox_worker_ready_state_packet_candidate",
        "required_sections": [
            "sandbox_worker_ready_state_packet_approval_gate",
            "v5_3_handoff_packet_reference_contract",
            "v5_4_acknowledgement_packet_reference_contract",
            "v5_5_acceptance_review_packet_reference_contract",
            "sandbox_worker_ready_state_reference_contract",
            "ready_state_scope_contract",
            "non_execution_ready_state_boundary",
            "ready_state_permission_denial_record",
            "ready_state_plan_record",
            "ready_state_packet_record",
            "ready_state_audit_record",
            "ready_state_readiness_summary",
            "sandbox_worker_dry_run_assignment_candidate_bridge"
        ],
        "required_token": SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_ready_state_packet_written": False,
        "sandbox_worker_ready_state_packet_created": False,
        "sandbox_worker_ready_state_candidate_recorded": False,
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }


def create_sandbox_worker_ready_state_packet_approval_gate(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    ready_state_packet_requested: bool = False
) -> dict:
    token_valid = (confirmation_token == SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL_TOKEN)
    has_operator = bool(human_operator)
    has_worker = bool(sandbox_worker_label)
    has_handoff = bool(v5_3_handoff_packet_reference_label)
    has_ack = bool(v5_4_acknowledgement_packet_reference_label)
    has_acceptance = bool(v5_5_acceptance_review_packet_reference_label)
    has_outdir = bool(output_directory)

    records_auth = bool(token_valid and has_operator and has_worker and has_handoff and has_ack and has_acceptance)
    write_auth = bool(records_auth and has_outdir and ready_state_packet_requested)

    status = "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE" if write_auth else "BLOCKED_PENDING_V5_6_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL"

    return {
        "status": status,
        "local_ready_state_records_authorized": records_auth,
        "local_ready_state_packet_write_authorized": write_auth,
        "dry_run_assignment_authorized": False,
        "dry_run_task_assignment_authorized": False,
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
        "production_execution_authorized": False
    }


def create_v5_3_handoff_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_ready_state_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "references_exactly_one_v5_3_handoff_packet_label": True,
        "reference_is_metadata_only": True,
        "reference_is_not_read_from_disk": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "reference_does_not_start_worker": True
    }


def create_v5_4_acknowledgement_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_ready_state_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "references_exactly_one_v5_4_acknowledgement_packet_label": True,
        "reference_is_metadata_only": True,
        "reference_is_not_read_from_disk": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "reference_does_not_start_worker": True
    }


def create_v5_5_acceptance_review_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_ready_state_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "references_exactly_one_v5_5_acceptance_candidate_review_packet_label": True,
        "reference_is_metadata_only": True,
        "reference_is_not_read_from_disk": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "reference_does_not_start_worker": True,
        "reference_does_not_assign_dry_run_work": True,
        "reference_does_not_execute_tasks": True
    }


def create_sandbox_worker_ready_state_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_ready_state_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "references_exactly_one_sandbox_worker_label": True,
        "worker_is_metadata_only": True,
        "worker_is_not_a_running_process": True,
        "worker_is_not_started": True,
        "worker_ready_state_packet_candidate_is_local_metadata_only": True,
        "worker_is_not_assigned_dry_run_work_in_v5_6": True,
        "worker_cannot_call_tools": True,
        "worker_cannot_access_apis": True,
        "worker_cannot_access_network": True,
        "worker_cannot_access_credentials_secrets_environment": True,
        "worker_cannot_execute_tasks": True,
        "worker_cannot_route_live_work": True
    }


def create_ready_state_scope_contract(
    approval_gate: dict,
    v5_3_contract: dict,
    v5_4_contract: dict,
    v5_5_contract: dict,
    worker_contract: dict
) -> dict:
    records_auth = approval_gate.get("local_ready_state_records_authorized", False)
    all_contracts_pass = (
        v5_3_contract.get("status") == "PASS" and
        v5_4_contract.get("status") == "PASS" and
        v5_5_contract.get("status") == "PASS" and
        worker_contract.get("status") == "PASS"
    )
    if not (records_auth and all_contracts_pass):
        return {"status": "BLOCKED"}

    return {
        "status": "PASS",
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_3_handoff_packet_reference": True,
        "exactly_one_v5_4_acknowledgement_packet_reference": True,
        "exactly_one_v5_5_acceptance_review_packet_reference": True,
        "exactly_one_ready_state_packet_candidate": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "ready_state_metadata_only": True,
        "no_dry_run_assignment": True,
        "no_dry_run_task_assignment": True,
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
        "full_workforce_activation_allowed": False
    }


def create_non_execution_ready_state_boundary(
    approval_gate: dict,
    ready_state_scope_contract: dict
) -> dict:
    if ready_state_scope_contract.get("status") != "PASS":
        return {"status": "BLOCKED"}
    
    write_auth = approval_gate.get("local_ready_state_packet_write_authorized", False)

    return {
        "status": "PASS",
        "sandbox_worker_ready_state_packet_candidate_is_local_packet_only": True,
        "ready_state_packet_candidate_is_not_executed": True,
        "dry_run_assignment_is_not_created": True,
        "dry_run_task_is_not_assigned": True,
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
        "sandbox_worker_ready_state_packet_created": write_auth,
        "sandbox_worker_ready_state_candidate_recorded": write_auth,
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
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False
    }


def create_ready_state_permission_denial_record(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str
) -> dict:
    return {
        "denied_permissions": [
            "dry-run assignment",
            "dry-run task assignment",
            "worker process start",
            "agent start",
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
            "mutation of the referenced v5.3 handoff packet",
            "execution of the referenced v5.3 handoff packet",
            "mutation of the referenced v5.4 acknowledgement packet",
            "execution of the referenced v5.4 acknowledgement packet",
            "mutation of the referenced v5.5 acceptance review packet",
            "execution of the referenced v5.5 acceptance review packet"
        ]
    }


def create_ready_state_plan_record(
    approval_gate: dict,
    v5_3_contract: dict,
    v5_4_contract: dict,
    v5_5_contract: dict,
    worker_contract: dict,
    scope: dict,
    boundary: dict,
    candidate_id: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    human_operator: str
) -> dict:
    if (approval_gate.get("local_ready_state_records_authorized") and
        v5_3_contract.get("status") == "PASS" and
        v5_4_contract.get("status") == "PASS" and
        v5_5_contract.get("status") == "PASS" and
        worker_contract.get("status") == "PASS" and
        scope.get("status") == "PASS" and
        boundary.get("status") == "PASS"):
        status = "LOCAL_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_PLAN_CREATED"
    else:
        status = "BLOCKED"

    write_auth = approval_gate.get("local_ready_state_packet_write_authorized", False)
    
    return {
        "status": status,
        "ready_state_packet_candidate_id": candidate_id,
        "sandbox_worker_label": sandbox_worker_label,
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "v5_3_handoff_packet_reference_label_normalized": normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL),
        "v5_4_acknowledgement_packet_reference_label": v5_4_acknowledgement_packet_reference_label,
        "v5_4_acknowledgement_packet_reference_label_normalized": normalize_label(v5_4_acknowledgement_packet_reference_label, DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL),
        "v5_5_acceptance_review_packet_reference_label": v5_5_acceptance_review_packet_reference_label,
        "v5_5_acceptance_review_packet_reference_label_normalized": normalize_label(v5_5_acceptance_review_packet_reference_label, DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL),
        "human_operator": human_operator,
        "ready_state_mode": "deterministic_local_ready_state_packet_candidate_only",
        "packet_runtime_state": "written" if write_auth else "not_written",
        "worker_runtime_state": "not_started",
        "dry_run_assignment_state": "not_created",
        "dry_run_task_assignment_state": "not_assigned",
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
        "sandbox_worker_ready_state_packet_created": write_auth,
        "sandbox_worker_ready_state_candidate_recorded": write_auth,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "live_task_assignment_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "external_tool_invocation_performed": False,
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False
    }


def build_ready_state_packet_payload(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    human_operator: str,
    candidate_id: str,
    approval_token_valid: bool
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "5.6.0",
        "ready_state_type": "sandbox_worker_ready_state_packet_candidate",
        "ready_state_mode": "deterministic_local_ready_state_packet_candidate_only",
        "sandbox_worker_label": sandbox_worker_label,
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "v5_4_acknowledgement_packet_reference_label": v5_4_acknowledgement_packet_reference_label,
        "v5_5_acceptance_review_packet_reference_label": v5_5_acceptance_review_packet_reference_label,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "ready_state_packet_candidate_id": candidate_id,
        "ready_state_message": "Station Chief sandbox worker ready-state packet candidate wrote this deterministic local ready-state packet. No worker was started, assigned, or executed.",
        "ready_state_result": "READY_FOR_SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_REVIEW_ONLY",
        "local_ready_state_packet_written": True,
        "sandbox_worker_ready_state_packet_created": True,
        "sandbox_worker_ready_state_candidate_recorded": True,
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_sandbox_worker_ready_state_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    try:
        out_dir = Path(output_directory).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = safe_ready_state_packet_name(packet_name)
        packet_path = out_dir / safe_name
        
        # Ensure it's inside output_directory
        if not str(packet_path.resolve()).startswith(str(out_dir)):
            return create_blocked_ready_state_packet_write_record("path traversal prevented")
        
        packet_path.write_text(canonical_json(payload))
        
        return {
            "sandbox_worker_ready_state_write_record_version": "5.6.0",
            "write_status": "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_WRITTEN",
            "local_ready_state_packet_written": True,
            "sandbox_worker_ready_state_packet_created": True,
            "sandbox_worker_ready_state_candidate_recorded": True,
            "dry_run_assignment_created": False,
            "dry_run_task_assigned": False,
            "files_written_count": 1,
            "worker_process_started": False,
            "agent_started": False,
            "arbitrary_task_execution_performed": False,
            "user_task_execution_performed": False,
            "task_executed": False,
            "real_queue_created": False,
            "queue_write_performed": False,
            "live_worker_routing_performed": False,
            "live_orchestration_performed": False,
            "api_call_performed": False,
            "network_access_performed": False,
            "deployment_performed": False,
            "production_execution_performed": False,
            "scheduler_write_performed": False,
            "cron_write_performed": False,
            "task_enqueued": False,
            "live_task_assignment_performed": False,
            "external_tool_invocation_performed": False,
            "full_workforce_activation_performed": False
        }
    except Exception as e:
        return create_blocked_ready_state_packet_write_record(f"write failed: {e}")


def create_blocked_ready_state_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_ready_state_packet_written": False,
        "sandbox_worker_ready_state_packet_created": False,
        "sandbox_worker_ready_state_candidate_recorded": False,
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }


def create_ready_state_packet_record(write_record: dict, payload_digest: str | None) -> dict:
    if write_record.get("write_status") == "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_WRITTEN":
        status = "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_WRITTEN"
    else:
        status = "BLOCKED"
        
    return {
        "status": status,
        "write_record": write_record,
        "payload_digest": payload_digest,
        "local_ready_state_packet_written": write_record.get("local_ready_state_packet_written", False),
        "sandbox_worker_ready_state_packet_created": write_record.get("sandbox_worker_ready_state_packet_created", False),
        "sandbox_worker_ready_state_candidate_recorded": write_record.get("sandbox_worker_ready_state_candidate_recorded", False),
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }


def create_ready_state_audit_record(
    approval_gate: dict,
    v5_3_contract: dict,
    v5_4_contract: dict,
    v5_5_contract: dict,
    worker_contract: dict,
    scope_contract: dict,
    boundary: dict,
    denial_record: dict,
    plan_record: dict,
    packet_record: dict
) -> dict:
    write_auth = approval_gate.get("local_ready_state_packet_write_authorized", False)
    
    pass_audit = True
    for rec in [plan_record, packet_record]:
        if rec.get("worker_process_started") or rec.get("agent_started"):
            pass_audit = False
        if rec.get("arbitrary_task_execution_performed") or rec.get("user_task_execution_performed"):
            pass_audit = False
        if rec.get("dry_run_assignment_created") or rec.get("dry_run_task_assigned"):
            pass_audit = False

    return {
        "status": "PASS" if pass_audit else "BLOCKED",
        "section_digests": {
            "approval_gate": sha256_digest(approval_gate),
            "v5_3_handoff_packet_reference_contract": sha256_digest(v5_3_contract),
            "v5_4_acknowledgement_packet_reference_contract": sha256_digest(v5_4_contract),
            "v5_5_acceptance_review_packet_reference_contract": sha256_digest(v5_5_contract),
            "sandbox_worker_ready_state_reference_contract": sha256_digest(worker_contract),
            "ready_state_scope_contract": sha256_digest(scope_contract),
            "non_execution_ready_state_boundary": sha256_digest(boundary),
            "ready_state_permission_denial_record": sha256_digest(denial_record),
            "ready_state_plan_record": sha256_digest(plan_record),
            "ready_state_packet_record": sha256_digest(packet_record)
        },
        "sandbox_worker_ready_state_packet_created": write_auth,
        "sandbox_worker_ready_state_candidate_recorded": write_auth,
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }


def create_ready_state_readiness_summary(audit_record: dict) -> dict:
    if audit_record.get("status") == "PASS":
        status = "READY_FOR_SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_REVIEW_ONLY"
    else:
        status = "BLOCKED"
        
    return {
        "status": status,
        "next_layer": "Sandbox Worker Dry-Run Assignment Candidate",
        "v5_7_not_built": True,
        "one_deterministic_sandbox_worker_ready_state_packet_candidate_permitted_only_under_v5_6_token": True,
        "no_dry_run_assignment": True,
        "no_dry_run_task_assignment": True,
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
        "full_workforce_activation_performed": False
    }


def create_sandbox_worker_dry_run_assignment_candidate_bridge(summary: dict) -> dict:
    return {
        "bridge_status": "READY" if summary.get("status") == "READY_FOR_SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_REVIEW_ONLY" else "BLOCKED",
        "bridge_to_v5_7_review_only": True,
        "no_sandbox_worker_dry_run_assignment_in_v5_6": True,
        "no_dry_run_task_assignment_in_v5_6": True,
        "no_worker_start_in_v5_6": True,
        "no_agent_start_in_v5_6": True,
        "no_queue_creation_in_v5_6": True,
        "no_task_enqueue_in_v5_6": True,
        "no_arbitrary_task_execution_in_v5_6": True,
        "no_user_task_execution_in_v5_6": True,
        "no_worker_routing_in_v5_6": True,
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
        "full_workforce_activation_performed": False
    }


def create_sandbox_worker_ready_state_packet_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    ready_state_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    ready_state_packet_requested: bool = False,
    write_ready_state_packet: bool = False
) -> dict:
    command_str = command or "unknown"
    worker_label = sandbox_worker_label or ""
    handoff_label = v5_3_handoff_packet_reference_label or ""
    ack_label = v5_4_acknowledgement_packet_reference_label or ""
    acceptance_label = v5_5_acceptance_review_packet_reference_label or ""
    
    approval_gate = create_sandbox_worker_ready_state_packet_approval_gate(
        worker_label, handoff_label, ack_label, acceptance_label, output_directory,
        confirmation_token, human_operator, ready_state_packet_requested
    )
    v5_3_contract = create_v5_3_handoff_packet_reference_contract(approval_gate)
    v5_4_contract = create_v5_4_acknowledgement_packet_reference_contract(approval_gate)
    v5_5_contract = create_v5_5_acceptance_review_packet_reference_contract(approval_gate)
    worker_contract = create_sandbox_worker_ready_state_reference_contract(approval_gate)
    scope = create_ready_state_scope_contract(approval_gate, v5_3_contract, v5_4_contract, v5_5_contract, worker_contract)
    boundary = create_non_execution_ready_state_boundary(approval_gate, scope)
    denial = create_ready_state_permission_denial_record(worker_label, handoff_label, ack_label, acceptance_label)
    
    candidate_id = generate_sandbox_worker_ready_state_packet_candidate_id(
        command_str, worker_label, handoff_label, ack_label, acceptance_label
    )
    
    plan = create_ready_state_plan_record(
        approval_gate, v5_3_contract, v5_4_contract, v5_5_contract, worker_contract, scope, boundary,
        candidate_id, worker_label, handoff_label, ack_label, acceptance_label, human_operator or ""
    )

    write_record = None
    payload_digest = None
    
    if write_ready_state_packet:
        if plan.get("status") == "LOCAL_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_PLAN_CREATED" and approval_gate.get("local_ready_state_packet_write_authorized"):
            payload = build_ready_state_packet_payload(
                worker_label, handoff_label, ack_label, acceptance_label, human_operator or "", candidate_id, True
            )
            payload_digest = payload["payload_digest"]
            write_record = write_sandbox_worker_ready_state_packet(
                output_directory or "", ready_state_packet_name or "", payload
            )
        else:
            write_record = create_blocked_ready_state_packet_write_record("requirements not met")
    else:
        write_record = create_blocked_ready_state_packet_write_record("sandbox worker ready-state packet candidate write not requested")

    packet_record = create_ready_state_packet_record(write_record, payload_digest)
    
    audit = create_ready_state_audit_record(
        approval_gate, v5_3_contract, v5_4_contract, v5_5_contract, worker_contract, scope, boundary, denial, plan, packet_record
    )
    summary = create_ready_state_readiness_summary(audit)
    bridge = create_sandbox_worker_dry_run_assignment_candidate_bridge(summary)

    bundle = {
        "schema": create_sandbox_worker_ready_state_packet_candidate_schema(),
        "approval_gate": approval_gate,
        "v5_3_handoff_packet_reference_contract": v5_3_contract,
        "v5_4_acknowledgement_packet_reference_contract": v5_4_contract,
        "v5_5_acceptance_review_packet_reference_contract": v5_5_contract,
        "sandbox_worker_ready_state_reference_contract": worker_contract,
        "ready_state_scope_contract": scope,
        "non_execution_ready_state_boundary": boundary,
        "ready_state_permission_denial_record": denial,
        "ready_state_plan_record": plan,
        "ready_state_packet_record": packet_record,
        "ready_state_audit_record": audit,
        "ready_state_readiness_summary": summary,
        "sandbox_worker_dry_run_assignment_candidate_bridge": bridge,
        "local_ready_state_packet_written": packet_record.get("local_ready_state_packet_written", False),
        "sandbox_worker_ready_state_packet_created": packet_record.get("sandbox_worker_ready_state_packet_created", False),
        "sandbox_worker_ready_state_candidate_recorded": packet_record.get("sandbox_worker_ready_state_candidate_recorded", False),
        "dry_run_assignment_created": False,
        "dry_run_task_assigned": False,
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
        "full_workforce_activation_performed": False
    }
    
    if result is not None:
        result["sandbox_worker_ready_state_packet_candidate"] = bundle
        
    return bundle
