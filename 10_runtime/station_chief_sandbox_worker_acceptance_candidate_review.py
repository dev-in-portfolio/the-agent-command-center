"""
Station Chief Runtime v5.5.0 Sandbox Worker Acceptance Candidate Review Module
"""

import json
import hashlib
import re
from pathlib import Path

SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_MODULE_VERSION = "5.5.0"
SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_STATUS = "SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_LOCAL_PACKET_ONLY"
SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PHASE = "Sandbox Worker Acceptance Candidate Review"
SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL = "station-chief-v5-3-sandbox-worker-handoff-packet-reference"
DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-4-sandbox-worker-acknowledgement-packet-reference"
DEFAULT_SANDBOX_ACCEPTANCE_REVIEW_PACKET_NAME = "sandbox_worker_acceptance_candidate_review_packet.json"


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


def safe_acceptance_review_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_SANDBOX_ACCEPTANCE_REVIEW_PACKET_NAME
    if not packet_name.endswith('.json'):
        return DEFAULT_SANDBOX_ACCEPTANCE_REVIEW_PACKET_NAME
    if '/' in packet_name or '\\' in packet_name:
        return DEFAULT_SANDBOX_ACCEPTANCE_REVIEW_PACKET_NAME
    if packet_name in ('.', '..'):
        return DEFAULT_SANDBOX_ACCEPTANCE_REVIEW_PACKET_NAME
    return packet_name


def generate_sandbox_worker_acceptance_candidate_review_id(
    command: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    runtime_version: str = "5.5.0"
) -> str:
    norm_worker = normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL)
    norm_handoff = normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL)
    norm_ack = normalize_label(v5_4_acknowledgement_packet_reference_label, DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL)
    h = sha256_digest({
        "command": command,
        "worker": norm_worker,
        "handoff": norm_handoff,
        "ack": norm_ack,
        "version": runtime_version
    })[:12]
    return f"sandbox-worker-acceptance-candidate-review-v5-5-{norm_worker}-{norm_handoff}-{norm_ack}-{h}"


def create_sandbox_worker_acceptance_candidate_review_schema() -> dict:
    return {
        "schema_version": "5.5.0",
        "status": "SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_LOCAL_PACKET_ONLY",
        "acceptance_review_type": "sandbox_worker_acceptance_candidate_review",
        "required_sections": [
            "sandbox_worker_acceptance_review_approval_gate",
            "v5_3_handoff_packet_reference_contract",
            "v5_4_acknowledgement_packet_reference_contract",
            "sandbox_worker_acceptance_review_reference_contract",
            "acceptance_review_scope_contract",
            "non_execution_acceptance_review_boundary",
            "acceptance_review_permission_denial_record",
            "acceptance_review_plan_record",
            "acceptance_review_packet_record",
            "acceptance_review_audit_record",
            "acceptance_review_readiness_summary",
            "sandbox_worker_ready_state_packet_candidate_bridge"
        ],
        "required_token": SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_acceptance_review_packet_written": False,
        "sandbox_worker_acceptance_review_performed": False,
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_sandbox_worker_acceptance_review_approval_gate(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acceptance_review_requested: bool = False
) -> dict:
    token_valid = (confirmation_token == SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_APPROVAL_TOKEN)
    has_operator = bool(human_operator)
    has_worker = bool(sandbox_worker_label)
    has_handoff = bool(v5_3_handoff_packet_reference_label)
    has_ack = bool(v5_4_acknowledgement_packet_reference_label)
    has_outdir = bool(output_directory)

    records_auth = bool(token_valid and has_operator and has_worker and has_handoff and has_ack)
    write_auth = bool(records_auth and has_outdir and acceptance_review_requested)

    status = "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PACKET" if write_auth else "BLOCKED_PENDING_V5_5_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_APPROVAL"

    return {
        "status": status,
        "local_acceptance_review_records_authorized": records_auth,
        "local_acceptance_review_packet_write_authorized": write_auth,
        "sandbox_worker_acceptance_authorized": False,
        "sandbox_worker_ready_state_authorized": False,
        "ready_state_packet_creation_authorized": False,
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
    if not approval_gate.get("local_acceptance_review_records_authorized"):
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
    if not approval_gate.get("local_acceptance_review_records_authorized"):
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
        "reference_does_not_start_worker": True,
        "reference_does_not_mark_worker_accepted": True,
        "reference_does_not_create_ready_state": True
    }


def create_sandbox_worker_acceptance_review_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_acceptance_review_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "references_exactly_one_sandbox_worker_label": True,
        "worker_is_metadata_only": True,
        "worker_is_not_a_running_process": True,
        "worker_is_not_started": True,
        "worker_is_not_accepted_in_v5_5": True,
        "worker_is_not_marked_ready_in_v5_5": True,
        "worker_acceptance_review_is_local_metadata_only": True,
        "worker_cannot_call_tools": True,
        "worker_cannot_access_apis": True,
        "worker_cannot_access_network": True,
        "worker_cannot_access_credentials_secrets_environment": True,
        "worker_cannot_execute_tasks": True,
        "worker_cannot_route_live_work": True
    }


def create_acceptance_review_scope_contract(
    approval_gate: dict,
    v5_3_handoff_packet_reference_contract: dict,
    v5_4_acknowledgement_packet_reference_contract: dict,
    sandbox_worker_acceptance_review_reference_contract: dict
) -> dict:
    records_auth = approval_gate.get("local_acceptance_review_records_authorized", False)
    all_contracts_pass = (
        v5_3_handoff_packet_reference_contract.get("status") == "PASS" and
        v5_4_acknowledgement_packet_reference_contract.get("status") == "PASS" and
        sandbox_worker_acceptance_review_reference_contract.get("status") == "PASS"
    )
    if not (records_auth and all_contracts_pass):
        return {"status": "BLOCKED"}

    return {
        "status": "PASS",
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_3_handoff_packet_reference": True,
        "exactly_one_v5_4_acknowledgement_packet_reference": True,
        "exactly_one_acceptance_review_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "acceptance_review_metadata_only": True,
        "no_worker_acceptance": True,
        "no_ready_state_packet": True,
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


def create_non_execution_acceptance_review_boundary(
    approval_gate: dict,
    acceptance_review_scope_contract: dict
) -> dict:
    if acceptance_review_scope_contract.get("status") != "PASS":
        return {"status": "BLOCKED"}
    
    write_auth = approval_gate.get("local_acceptance_review_packet_write_authorized", False)

    return {
        "status": "PASS",
        "sandbox_worker_acceptance_candidate_review_is_local_packet_only": True,
        "acceptance_review_packet_is_not_executed": True,
        "worker_is_not_accepted": True,
        "worker_is_not_marked_ready": True,
        "ready_state_packet_is_not_created": True,
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
        "sandbox_worker_acceptance_review_performed": write_auth,
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
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False
    }


def create_acceptance_review_permission_denial_record(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str
) -> dict:
    return {
        "denied_permissions": [
            "sandbox worker acceptance",
            "sandbox worker ready-state creation",
            "ready-state packet creation",
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
            "execution of the referenced v5.4 acknowledgement packet"
        ]
    }


def create_acceptance_review_plan_record(
    approval_gate: dict,
    v5_3_contract: dict,
    v5_4_contract: dict,
    worker_contract: dict,
    scope: dict,
    boundary: dict,
    candidate_id: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    human_operator: str
) -> dict:
    if (approval_gate.get("local_acceptance_review_records_authorized") and
        v5_3_contract.get("status") == "PASS" and
        v5_4_contract.get("status") == "PASS" and
        worker_contract.get("status") == "PASS" and
        scope.get("status") == "PASS" and
        boundary.get("status") == "PASS"):
        status = "LOCAL_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PLAN_CREATED"
    else:
        status = "BLOCKED"

    write_auth = approval_gate.get("local_acceptance_review_packet_write_authorized", False)
    
    return {
        "status": status,
        "acceptance_review_candidate_id": candidate_id,
        "sandbox_worker_label": sandbox_worker_label,
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker_label, DEFAULT_SANDBOX_WORKER_LABEL),
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "v5_3_handoff_packet_reference_label_normalized": normalize_label(v5_3_handoff_packet_reference_label, DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL),
        "v5_4_acknowledgement_packet_reference_label": v5_4_acknowledgement_packet_reference_label,
        "v5_4_acknowledgement_packet_reference_label_normalized": normalize_label(v5_4_acknowledgement_packet_reference_label, DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL),
        "human_operator": human_operator,
        "acceptance_review_mode": "deterministic_local_acceptance_candidate_review_packet_only",
        "packet_runtime_state": "written" if write_auth else "not_written",
        "worker_runtime_state": "not_started",
        "worker_acceptance_state": "not_accepted",
        "worker_ready_state": "not_created",
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
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "live_task_assignment_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "external_tool_invocation_performed": False
    }


def build_acceptance_review_packet_payload(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    human_operator: str,
    candidate_id: str,
    approval_token_valid: bool
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "5.5.0",
        "acceptance_review_type": "sandbox_worker_acceptance_candidate_review",
        "acceptance_review_mode": "deterministic_local_acceptance_candidate_review_packet_only",
        "sandbox_worker_label": sandbox_worker_label,
        "v5_3_handoff_packet_reference_label": v5_3_handoff_packet_reference_label,
        "v5_4_acknowledgement_packet_reference_label": v5_4_acknowledgement_packet_reference_label,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "acceptance_review_candidate_id": candidate_id,
        "acceptance_review_message": "Station Chief sandbox worker acceptance candidate review wrote this deterministic local review packet. No worker was accepted, readied, or started.",
        "acceptance_review_result": "READY_FOR_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_REVIEW_ONLY",
        "local_acceptance_review_packet_written": True,
        "sandbox_worker_acceptance_review_performed": True,
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def write_sandbox_worker_acceptance_review_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    try:
        out_dir = Path(output_directory).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = safe_acceptance_review_packet_name(packet_name)
        packet_path = out_dir / safe_name
        
        # Ensure it's inside output_directory
        if not str(packet_path.resolve()).startswith(str(out_dir)):
            return create_blocked_acceptance_review_packet_write_record("path traversal prevented")
        
        packet_path.write_text(canonical_json(payload))
        
        return {
            "sandbox_worker_acceptance_review_write_record_version": "5.5.0",
            "write_status": "SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PACKET_WRITTEN",
            "local_acceptance_review_packet_written": True,
            "sandbox_worker_acceptance_review_performed": True,
            "sandbox_worker_accepted": False,
            "sandbox_worker_ready_state_created": False,
            "ready_state_packet_written": False,
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
        return create_blocked_acceptance_review_packet_write_record(f"write failed: {e}")


def create_blocked_acceptance_review_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_acceptance_review_packet_written": False,
        "sandbox_worker_acceptance_review_performed": False,
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_acceptance_review_packet_record(write_record: dict, payload_digest: str | None) -> dict:
    if write_record.get("write_status") == "SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PACKET_WRITTEN":
        status = "SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PACKET_WRITTEN"
    else:
        status = "BLOCKED"
        
    return {
        "status": status,
        "write_record": write_record,
        "payload_digest": payload_digest,
        "local_acceptance_review_packet_written": write_record.get("local_acceptance_review_packet_written", False),
        "sandbox_worker_acceptance_review_performed": write_record.get("sandbox_worker_acceptance_review_performed", False),
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_acceptance_review_audit_record(
    approval_gate: dict,
    v5_3_contract: dict,
    v5_4_contract: dict,
    worker_contract: dict,
    scope_contract: dict,
    boundary: dict,
    denial_record: dict,
    plan_record: dict,
    packet_record: dict
) -> dict:
    write_auth = approval_gate.get("local_acceptance_review_packet_write_authorized", False)
    
    pass_audit = True
    for rec in [plan_record, packet_record]:
        if rec.get("sandbox_worker_accepted") or rec.get("worker_process_started") or rec.get("agent_started"):
            pass_audit = False
        if rec.get("arbitrary_task_execution_performed") or rec.get("user_task_execution_performed"):
            pass_audit = False

    return {
        "status": "PASS" if pass_audit else "BLOCKED",
        "section_digests": {
            "approval_gate": sha256_digest(approval_gate),
            "v5_3_handoff_packet_reference_contract": sha256_digest(v5_3_contract),
            "v5_4_acknowledgement_packet_reference_contract": sha256_digest(v5_4_contract),
            "sandbox_worker_acceptance_review_reference_contract": sha256_digest(worker_contract),
            "acceptance_review_scope_contract": sha256_digest(scope_contract),
            "non_execution_acceptance_review_boundary": sha256_digest(boundary),
            "acceptance_review_permission_denial_record": sha256_digest(denial_record),
            "acceptance_review_plan_record": sha256_digest(plan_record),
            "acceptance_review_packet_record": sha256_digest(packet_record)
        },
        "sandbox_worker_acceptance_review_performed": write_auth,
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_acceptance_review_readiness_summary(audit_record: dict) -> dict:
    if audit_record.get("status") == "PASS":
        status = "READY_FOR_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_REVIEW_ONLY"
    else:
        status = "BLOCKED"
        
    return {
        "status": status,
        "next_layer": "Sandbox Worker Ready-State Packet Candidate",
        "v5_6_not_built": True,
        "one_deterministic_sandbox_worker_acceptance_candidate_review_packet_permitted_only_under_v5_5_token": True,
        "no_worker_acceptance": True,
        "no_worker_ready_state_creation": True,
        "no_ready_state_packet_creation": True,
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
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_sandbox_worker_ready_state_packet_candidate_bridge(summary: dict) -> dict:
    return {
        "bridge_status": "READY" if summary.get("status") == "READY_FOR_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_REVIEW_ONLY" else "BLOCKED",
        "bridge_to_v5_6_review_only": True,
        "no_sandbox_worker_ready_state_packet_in_v5_5": True,
        "no_sandbox_worker_acceptance_in_v5_5": True,
        "no_worker_start_in_v5_5": True,
        "no_agent_start_in_v5_5": True,
        "no_queue_creation_in_v5_5": True,
        "no_task_enqueue_in_v5_5": True,
        "no_arbitrary_task_execution_in_v5_5": True,
        "no_user_task_execution_in_v5_5": True,
        "no_worker_routing_in_v5_5": True,
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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


def create_sandbox_worker_acceptance_candidate_review_bundle(
    result: dict | None,
    command: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    acceptance_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acceptance_review_requested: bool = False,
    write_acceptance_review_packet: bool = False
) -> dict:
    command_str = command or "unknown"
    worker_label = sandbox_worker_label or ""
    handoff_label = v5_3_handoff_packet_reference_label or ""
    ack_label = v5_4_acknowledgement_packet_reference_label or ""
    
    approval_gate = create_sandbox_worker_acceptance_review_approval_gate(
        worker_label, handoff_label, ack_label, output_directory,
        confirmation_token, human_operator, acceptance_review_requested
    )
    v5_3_contract = create_v5_3_handoff_packet_reference_contract(approval_gate)
    v5_4_contract = create_v5_4_acknowledgement_packet_reference_contract(approval_gate)
    worker_contract = create_sandbox_worker_acceptance_review_reference_contract(approval_gate)
    scope = create_acceptance_review_scope_contract(approval_gate, v5_3_contract, v5_4_contract, worker_contract)
    boundary = create_non_execution_acceptance_review_boundary(approval_gate, scope)
    denial = create_acceptance_review_permission_denial_record(worker_label, handoff_label, ack_label)
    
    candidate_id = generate_sandbox_worker_acceptance_candidate_review_id(
        command_str, worker_label, handoff_label, ack_label
    )
    
    plan = create_acceptance_review_plan_record(
        approval_gate, v5_3_contract, v5_4_contract, worker_contract, scope, boundary,
        candidate_id, worker_label, handoff_label, ack_label, human_operator or ""
    )

    write_record = None
    payload_digest = None
    
    if write_acceptance_review_packet:
        if plan.get("status") == "LOCAL_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_PLAN_CREATED" and approval_gate.get("local_acceptance_review_packet_write_authorized"):
            payload = build_acceptance_review_packet_payload(
                worker_label, handoff_label, ack_label, human_operator or "", candidate_id, True
            )
            payload_digest = payload["payload_digest"]
            write_record = write_sandbox_worker_acceptance_review_packet(
                output_directory or "", acceptance_review_packet_name or "", payload
            )
        else:
            write_record = create_blocked_acceptance_review_packet_write_record("requirements not met")
    else:
        write_record = create_blocked_acceptance_review_packet_write_record("sandbox worker acceptance candidate review packet write not requested")

    packet_record = create_acceptance_review_packet_record(write_record, payload_digest)
    
    audit = create_acceptance_review_audit_record(
        approval_gate, v5_3_contract, v5_4_contract, worker_contract, scope, boundary, denial, plan, packet_record
    )
    summary = create_acceptance_review_readiness_summary(audit)
    bridge = create_sandbox_worker_ready_state_packet_candidate_bridge(summary)

    bundle = {
        "schema": create_sandbox_worker_acceptance_candidate_review_schema(),
        "approval_gate": approval_gate,
        "v5_3_handoff_packet_reference_contract": v5_3_contract,
        "v5_4_acknowledgement_packet_reference_contract": v5_4_contract,
        "sandbox_worker_acceptance_review_reference_contract": worker_contract,
        "acceptance_review_scope_contract": scope,
        "non_execution_acceptance_review_boundary": boundary,
        "acceptance_review_permission_denial_record": denial,
        "acceptance_review_plan_record": plan,
        "acceptance_review_packet_record": packet_record,
        "acceptance_review_audit_record": audit,
        "acceptance_review_readiness_summary": summary,
        "sandbox_worker_ready_state_packet_candidate_bridge": bridge,
        "local_acceptance_review_packet_written": packet_record.get("local_acceptance_review_packet_written", False),
        "sandbox_worker_acceptance_review_performed": packet_record.get("sandbox_worker_acceptance_review_performed", False),
        "sandbox_worker_accepted": False,
        "sandbox_worker_ready_state_created": False,
        "ready_state_packet_written": False,
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
        result["sandbox_worker_acceptance_candidate_review"] = bundle
        
    return bundle
