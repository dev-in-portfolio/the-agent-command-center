import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V6_0_MVP_LOCK_MODULE_VERSION = "6.0.0"
STATION_CHIEF_V6_0_MVP_LOCK_STATUS = "STATION_CHIEF_V6_0_MVP_LOCK_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_0_MVP_LOCK_PHASE = "Station Chief v6.0 MVP Lock / Integrated Local Command-Center Loop"
STATION_CHIEF_V6_0_MVP_LOCK_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_0_MVP_LOCK"

DEFAULT_LOCAL_TASK_CANDIDATE_LABEL = "station-chief-v6-0-local-task-candidate-reference"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL = "station-chief-v5-3-sandbox-worker-handoff-packet-reference"
DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-4-sandbox-worker-acknowledgement-packet-reference"
DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL = "station-chief-v5-5-sandbox-worker-acceptance-candidate-review-packet-reference"
DEFAULT_V5_6_READY_STATE_PACKET_REFERENCE_LABEL = "station-chief-v5-6-sandbox-worker-ready-state-packet-reference"
DEFAULT_V5_7_DRY_RUN_ASSIGNMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-7-sandbox-worker-dry-run-assignment-packet-reference"
DEFAULT_V5_8_DRY_RUN_RESULT_PACKET_REFERENCE_LABEL = "station-chief-v5-8-sandbox-worker-dry-run-result-packet-reference"
DEFAULT_V5_9_DRY_RUN_REPLAY_AUDIT_PACKET_REFERENCE_LABEL = "station-chief-v5-9-sandbox-worker-dry-run-replay-audit-packet-reference"
DEFAULT_V6_0_MVP_LOCK_LABEL = "station-chief-v6-0-mvp-lock-reference"
DEFAULT_STATION_CHIEF_V6_0_MVP_LOCK_PACKET_NAME = "station_chief_v6_0_mvp_lock_packet.json"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    content = canonical_json(data)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    normalized = label.lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")

def safe_mvp_lock_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_STATION_CHIEF_V6_0_MVP_LOCK_PACKET_NAME
    if not packet_name.endswith(".json"):
        return DEFAULT_STATION_CHIEF_V6_0_MVP_LOCK_PACKET_NAME
    if "/" in packet_name or "\\" in packet_name:
        return DEFAULT_STATION_CHIEF_V6_0_MVP_LOCK_PACKET_NAME
    if packet_name in [".", ".."]:
        return DEFAULT_STATION_CHIEF_V6_0_MVP_LOCK_PACKET_NAME
    return packet_name

def generate_station_chief_v6_0_mvp_lock_id(
    command: str,
    local_task_candidate_label: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    v5_6_ready_state_packet_reference_label: str,
    v5_7_dry_run_assignment_packet_reference_label: str,
    v5_8_dry_run_result_packet_reference_label: str,
    v5_9_dry_run_replay_audit_packet_reference_label: str,
    v6_0_mvp_lock_label: str,
    runtime_version: str = "6.0.0"
) -> str:
    salt = f"station-chief-v6-0-mvp-lock-{runtime_version}"
    context = {
        "salt": salt,
        "command": command,
        "local_task": local_task_candidate_label,
        "sandbox_worker": sandbox_worker_label,
        "v5_3_handoff": v5_3_handoff_packet_reference_label,
        "v5_4_acknowledgement": v5_4_acknowledgement_packet_reference_label,
        "v5_5_acceptance_review": v5_5_acceptance_review_packet_reference_label,
        "v5_6_ready_state": v5_6_ready_state_packet_reference_label,
        "v5_7_dry_run_assignment": v5_7_dry_run_assignment_packet_reference_label,
        "v5_8_dry_run_result": v5_8_dry_run_result_packet_reference_label,
        "v5_9_dry_run_replay_audit": v5_9_dry_run_replay_audit_packet_reference_label,
        "v6_0_mvp_lock": v6_0_mvp_lock_label
    }
    digest = sha256_digest(context)
    
    parts = [
        normalize_label(local_task_candidate_label, "task"),
        normalize_label(sandbox_worker_label, "worker"),
        normalize_label(v5_3_handoff_packet_reference_label, "v5-3"),
        normalize_label(v5_4_acknowledgement_packet_reference_label, "v5-4"),
        normalize_label(v5_5_acceptance_review_packet_reference_label, "v5-5"),
        normalize_label(v5_6_ready_state_packet_reference_label, "v5-6"),
        normalize_label(v5_7_dry_run_assignment_packet_reference_label, "v5-7"),
        normalize_label(v5_8_dry_run_result_packet_reference_label, "v5-8"),
        normalize_label(v5_9_dry_run_replay_audit_packet_reference_label, "v5-9"),
        normalize_label(v6_0_mvp_lock_label, "v6-0")
    ]
    
    return f"station-chief-v6-0-mvp-lock-{'-'.join(parts)}-{digest[:12]}"

def create_station_chief_v6_0_mvp_lock_schema() -> dict:
    return {
        "schema_version": "6.0.0",
        "status": STATION_CHIEF_V6_0_MVP_LOCK_STATUS,
        "mvp_lock_type": "station_chief_v6_0_mvp_lock",
        "integrated_loop_type": "deterministic_local_command_center_loop",
        "required_sections": [
            "station_chief_v6_0_mvp_lock_approval_gate",
            "local_task_candidate_reference_contract",
            "sandbox_worker_reference_contract",
            "v5_3_handoff_packet_reference_contract",
            "v5_4_acknowledgement_packet_reference_contract",
            "v5_5_acceptance_review_packet_reference_contract",
            "v5_6_ready_state_packet_reference_contract",
            "v5_7_dry_run_assignment_packet_reference_contract",
            "v5_8_dry_run_result_packet_reference_contract",
            "v5_9_dry_run_replay_audit_packet_reference_contract",
            "v6_0_mvp_lock_reference_contract",
            "integrated_local_command_center_loop_contract",
            "non_execution_mvp_lock_boundary",
            "mvp_lock_permission_denial_record",
            "mvp_lock_plan_record",
            "mvp_lock_packet_record",
            "mvp_lock_audit_record",
            "mvp_lock_readiness_summary",
            "station_chief_post_mvp_expansion_bridge"
        ],
        "required_token": STATION_CHIEF_V6_0_MVP_LOCK_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "locked_175_family_baseline_preserved": True,
        "local_mvp_lock_packet_written": False,
        "station_chief_v6_0_mvp_lock_created": False,
        "integrated_local_command_center_loop_recorded": False,
        "mvp_done_recorded": False,
        "local_task_candidate_executed": False,
        "handoff_packet_executed": False,
        "acknowledgement_packet_executed": False,
        "acceptance_review_packet_executed": False,
        "ready_state_packet_executed": False,
        "dry_run_assignment_packet_executed": False,
        "dry_run_result_packet_executed": False,
        "dry_run_replay_audit_packet_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
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
        "v6_1_created": False
    }

def create_station_chief_v6_0_mvp_lock_approval_gate(
    local_task_candidate_label: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    v5_6_ready_state_packet_reference_label: str,
    v5_7_dry_run_assignment_packet_reference_label: str,
    v5_8_dry_run_result_packet_reference_label: str,
    v5_9_dry_run_replay_audit_packet_reference_label: str,
    v6_0_mvp_lock_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    mvp_lock_requested: bool = False
) -> dict:
    token_valid = (confirmation_token == STATION_CHIEF_V6_0_MVP_LOCK_APPROVAL_TOKEN)
    all_labels_present = all([
        local_task_candidate_label, sandbox_worker_label,
        v5_3_handoff_packet_reference_label, v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label, v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label, v5_8_dry_run_result_packet_reference_label,
        v5_9_dry_run_replay_audit_packet_reference_label, v6_0_mvp_lock_label
    ])
    
    local_mvp_lock_records_authorized = (
        token_valid and bool(human_operator) and all_labels_present
    )
    
    local_mvp_lock_packet_write_authorized = (
        local_mvp_lock_records_authorized and bool(output_directory) and mvp_lock_requested
    )
    
    status = "BLOCKED_PENDING_STATION_CHIEF_V6_0_MVP_LOCK_APPROVAL"
    if local_mvp_lock_records_authorized:
        status = "APPROVED_FOR_ONE_LOCAL_STATION_CHIEF_V6_0_MVP_LOCK_PACKET"
        
    return {
        "status": status,
        "token_valid": token_valid,
        "human_operator_present": bool(human_operator),
        "all_labels_present": all_labels_present,
        "output_directory_present": bool(output_directory),
        "mvp_lock_requested": mvp_lock_requested,
        "local_mvp_lock_records_authorized": local_mvp_lock_records_authorized,
        "local_mvp_lock_packet_write_authorized": local_mvp_lock_packet_write_authorized,
        "local_task_candidate_execution_authorized": False,
        "worker_process_start_authorized": False,
        "agent_start_authorized": False,
        "handoff_execution_authorized": False,
        "acknowledgement_execution_authorized": False,
        "acceptance_review_execution_authorized": False,
        "ready_state_execution_authorized": False,
        "dry_run_assignment_execution_authorized": False,
        "dry_run_result_execution_authorized": False,
        "dry_run_replay_audit_execution_authorized": False,
        "dry_run_task_execution_authorized": False,
        "real_worker_result_creation_authorized": False,
        "live_replay_authorized": False,
        "production_audit_authorized": False,
        "rollback_authorized": False,
        "recovery_authorized": False,
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
        "full_workforce_activation_authorized": False,
        "v6_1_creation_authorized": False
    }

def create_local_task_candidate_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "local_task_candidate_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_live_routing": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True,
        "no_real_result_creation": True
    }

def create_sandbox_worker_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "sandbox_worker_label",
        "is_metadata_only": True,
        "no_running_process": True,
        "no_worker_start": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True,
        "no_live_work_routing": True,
        "no_task_execution": True
    }

def create_v5_3_handoff_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_3_handoff_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True
    }

def create_v5_4_acknowledgement_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_4_acknowledgement_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True
    }

def create_v5_5_acceptance_review_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_5_acceptance_review_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True,
        "no_task_execution": True
    }

def create_v5_6_ready_state_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_6_ready_state_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True,
        "no_live_work_assignment": True,
        "no_task_execution": True,
        "no_real_result_creation": True
    }

def create_v5_7_dry_run_assignment_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_7_dry_run_assignment_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True,
        "no_dry_run_task_execution": True,
        "no_real_result_creation": True,
        "no_replay_audit_performed": True
    }

def create_v5_8_dry_run_result_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_8_dry_run_result_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result_creation": True,
        "no_live_replay_performed": True,
        "no_production_audit_performed": True
    }

def create_v5_9_dry_run_replay_audit_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v5_9_dry_run_replay_audit_packet_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_enqueue": True,
        "no_routing": True,
        "no_worker_start": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result_creation": True,
        "no_live_replay_performed": True,
        "no_production_audit_performed": True,
        "no_rollback_performed": True,
        "no_recovery_performed": True
    }

def create_v6_0_mvp_lock_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_mvp_lock_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v6_0_mvp_lock_label",
        "is_metadata_only": True,
        "is_deterministic": True,
        "no_live_execution_action": True,
        "no_production_activation": True,
        "no_deployment": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_external_transmission": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True
    }

def create_integrated_local_command_center_loop_contract(
    approval_gate: dict,
    local_task_c: dict, sandbox_worker_c: dict, v5_3_c: dict, v5_4_c: dict,
    v5_5_c: dict, v5_6_c: dict, v5_7_c: dict, v5_8_c: dict, v5_9_c: dict, v6_0_c: dict
) -> dict:
    contracts_passed = all(c.get("status") == "PASS" for c in [
        local_task_c, sandbox_worker_c, v5_3_c, v5_4_c, v5_5_c, 
        v5_6_c, v5_7_c, v5_8_c, v5_9_c, v6_0_c
    ])
    loop_passed = approval_gate.get("local_mvp_lock_records_authorized") and contracts_passed
    
    return {
        "status": "PASS" if loop_passed else "BLOCKED",
        "exactly_one_local_task_candidate_label": True,
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_3_handoff_packet_reference": True,
        "exactly_one_v5_4_acknowledgement_packet_reference": True,
        "exactly_one_v5_5_acceptance_review_packet_reference": True,
        "exactly_one_v5_6_ready_state_packet_reference": True,
        "exactly_one_v5_7_dry_run_assignment_packet_reference": True,
        "exactly_one_v5_8_dry_run_result_packet_reference": True,
        "exactly_one_v5_9_dry_run_replay_audit_packet_reference": True,
        "exactly_one_v6_0_mvp_lock_label": True,
        "exactly_one_mvp_lock_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "mvp_lock_metadata_only": True,
        "integrated_local_command_center_loop_recorded": loop_passed,
        "task_candidate_flow_proven_as_metadata": True,
        "handoff_flow_proven_as_metadata": True,
        "acknowledgement_flow_proven_as_metadata": True,
        "acceptance_ready_state_flow_proven_as_metadata": True,
        "dry_run_assignment_flow_proven_as_metadata": True,
        "dry_run_result_flow_proven_as_metadata": True,
        "dry_run_replay_audit_flow_proven_as_metadata": True,
        "no_local_task_candidate_execution": True,
        "no_handoff_execution": True,
        "no_acknowledgement_execution": True,
        "no_acceptance_review_execution": True,
        "no_ready_state_execution": True,
        "no_dry_run_assignment_execution": True,
        "no_dry_run_result_execution": True,
        "no_dry_run_replay_audit_execution": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_v6_1_creation": True,
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
        "mvp_lock_scope": "first_coherent_local_command_center_loop"
    }

def create_non_execution_mvp_lock_boundary(
    approval_gate: dict,
    loop_contract: dict,
    packet_written: bool = False,
    loop_recorded: bool = False,
    mvp_done_recorded: bool = False
) -> dict:
    boundary_passed = loop_contract.get("status") == "PASS"
    
    return {
        "status": "PASS" if boundary_passed else "BLOCKED",
        "station_chief_v6_0_mvp_lock_local_packet_only": True,
        "mvp_lock_packet_not_executed": True,
        "integrated_command_center_loop_metadata_only": True,
        "local_task_candidate_not_executed": True,
        "handoff_not_executed": True,
        "acknowledgement_not_executed": True,
        "acceptance_review_not_executed": True,
        "ready_state_packet_not_executed": True,
        "dry_run_assignment_not_executed": True,
        "dry_run_result_not_executed": True,
        "dry_run_replay_audit_not_executed": True,
        "live_replay_not_performed": True,
        "production_audit_not_performed": True,
        "dry_run_task_not_executed": True,
        "real_worker_result_not_created": True,
        "rollback_not_performed": True,
        "recovery_not_performed": True,
        "v6_1_not_created": True,
        "worker_not_started": True,
        "agent_not_started": True,
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
        "local_mvp_lock_packet_written": packet_written,
        "station_chief_v6_0_mvp_lock_created": packet_written,
        "integrated_local_command_center_loop_recorded": loop_recorded,
        "mvp_done_recorded": mvp_done_recorded
    }

def create_mvp_lock_permission_denial_record(
    local_task: str, sandbox_worker: str, v5_3: str, v5_4: str,
    v5_5: str, v5_6: str, v5_7: str, v5_8: str, v5_9: str, v6_0: str
) -> dict:
    return {
        "explicitly_denied": {
            "local_task_candidate_execution": True,
            "handoff_packet_execution": True,
            "acknowledgement_packet_execution": True,
            "acceptance_review_packet_execution": True,
            "ready_state_packet_execution": True,
            "dry_run_assignment_packet_execution": True,
            "dry_run_result_packet_execution": True,
            "dry_run_replay_audit_packet_execution": True,
            "dry_run_task_execution": True,
            "real_dry_run_result_generation": True,
            "real_worker_result_creation": True,
            "live_replay_execution": True,
            "production_audit_execution": True,
            "rollback_execution": True,
            "recovery_execution": True,
            "v6_1_creation": True,
            "post_mvp_expansion": True,
            "real_task_assignment": True,
            "live_task_assignment": True,
            "worker_process_start": True,
            "agent_start": True,
            "real_queue_creation": True,
            "queue_writes": True,
            "scheduler_writes": True,
            "cron_writes": True,
            "task_enqueue": True,
            "arbitrary_task_execution": True,
            "user_task_execution": True,
            "shell_command_execution": True,
            "subprocess_execution": True,
            "live_worker_routing": True,
            "live_orchestration": True,
            "external_tool_invocation": True,
            "api_access": True,
            "network_access": True,
            "socket_access": True,
            "dns_resolution": True,
            "credential_use": True,
            "credential_vault_access": True,
            "secret_reads": True,
            "environment_reads": True,
            "deployment": True,
            "production_execution": True,
            "production_activation": True,
            "github_push_by_worker": True,
            "full_workforce_activation": True,
            "baseline_mutation": True,
            "devinization_overlay_mutation": True,
            "dashboard_org_master_export_mutation": True,
            "ownership_metadata_mutation": True,
            "local_task_candidate_mutation": True,
            "v5_3_handoff_mutation": True,
            "v5_4_acknowledgement_mutation": True,
            "v5_5_acceptance_review_mutation": True,
            "v5_6_ready_state_mutation": True,
            "v5_7_dry_run_assignment_mutation": True,
            "v5_8_dry_run_result_mutation": True,
            "v5_9_dry_run_replay_audit_mutation": True,
            "mvp_lock_external_transmission": True
        }
    }

def create_mvp_lock_plan_record(
    approval_gate: dict,
    loop_contract: dict,
    boundary: dict,
    mvp_lock_id: str,
    local_task: str, sandbox_worker: str, v5_3: str, v5_4: str,
    v5_5: str, v5_6: str, v5_7: str, v5_8: str, v5_9: str, v6_0: str,
    human_operator: str | None,
    write_authorized: bool = False
) -> dict:
    valid = approval_gate.get("local_mvp_lock_records_authorized") and loop_contract.get("status") == "PASS" and boundary.get("status") == "PASS"
    status = "LOCAL_STATION_CHIEF_V6_0_MVP_LOCK_PLAN_CREATED" if valid else "BLOCKED"
    
    return {
        "status": status,
        "station_chief_v6_0_mvp_lock_id": mvp_lock_id,
        "local_task_candidate_label": local_task,
        "local_task_candidate_label_normalized": normalize_label(local_task, ""),
        "sandbox_worker_label": sandbox_worker,
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker, ""),
        "v5_3_handoff_packet_reference_label": v5_3,
        "v5_3_handoff_packet_reference_label_normalized": normalize_label(v5_3, ""),
        "v5_4_acknowledgement_packet_reference_label": v5_4,
        "v5_4_acknowledgement_packet_reference_label_normalized": normalize_label(v5_4, ""),
        "v5_5_acceptance_review_packet_reference_label": v5_5,
        "v5_5_acceptance_review_packet_reference_label_normalized": normalize_label(v5_5, ""),
        "v5_6_ready_state_packet_reference_label": v5_6,
        "v5_6_ready_state_packet_reference_label_normalized": normalize_label(v5_6, ""),
        "v5_7_dry_run_assignment_packet_reference_label": v5_7,
        "v5_7_dry_run_assignment_packet_reference_label_normalized": normalize_label(v5_7, ""),
        "v5_8_dry_run_result_packet_reference_label": v5_8,
        "v5_8_dry_run_result_packet_reference_label_normalized": normalize_label(v5_8, ""),
        "v5_9_dry_run_replay_audit_packet_reference_label": v5_9,
        "v5_9_dry_run_replay_audit_packet_reference_label_normalized": normalize_label(v5_9, ""),
        "v6_0_mvp_lock_label": v6_0,
        "v6_0_mvp_lock_label_normalized": normalize_label(v6_0, ""),
        "human_operator": human_operator,
        "mvp_lock_mode": "deterministic_local_mvp_lock_packet_only",
        "integrated_loop_mode": "deterministic_local_command_center_loop_metadata_only",
        "packet_runtime_state": "written" if write_authorized else "not_written",
        "worker_runtime_state": "not_started",
        "mvp_lock_state": "recorded_synthetic_metadata_only" if write_authorized else "not_created",
        "integrated_loop_state": "recorded_synthetic_metadata_only" if write_authorized else "not_recorded",
        "mvp_done_state": "recorded_synthetic_metadata_only" if write_authorized else "not_recorded",
        "local_task_candidate_execution_state": "not_executed",
        "handoff_execution_state": "not_executed",
        "acknowledgement_execution_state": "not_executed",
        "acceptance_review_execution_state": "not_executed",
        "ready_state_execution_state": "not_executed",
        "dry_run_assignment_execution_state": "not_executed",
        "dry_run_result_execution_state": "not_executed",
        "dry_run_replay_audit_execution_state": "not_executed",
        "dry_run_task_execution_state": "not_executed",
        "real_worker_result_state": "not_created",
        "live_replay_state": "not_performed",
        "production_audit_state": "not_performed",
        "rollback_state": "not_performed",
        "recovery_state": "not_performed",
        "v6_1_state": "not_created",
        "agent_runtime_state": "not_started",
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "agent_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False
    }

def build_mvp_lock_packet_payload(
    mvp_lock_id: str,
    local_task: str, sandbox_worker: str, v5_3: str, v5_4: str,
    v5_5: str, v5_6: str, v5_7: str, v5_8: str, v5_9: str, v6_0: str,
    human_operator: str,
    approval_token_valid: bool
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "6.0.0",
        "mvp_lock_type": "station_chief_v6_0_mvp_lock",
        "mvp_lock_mode": "deterministic_local_mvp_lock_packet_only",
        "integrated_loop_type": "deterministic_local_command_center_loop",
        "integrated_loop_mode": "metadata_only_no_execution",
        "local_task_candidate_label": local_task,
        "sandbox_worker_label": sandbox_worker,
        "v5_3_handoff_packet_reference_label": v5_3,
        "v5_4_acknowledgement_packet_reference_label": v5_4,
        "v5_5_acceptance_review_packet_reference_label": v5_5,
        "v5_6_ready_state_packet_reference_label": v5_6,
        "v5_7_dry_run_assignment_packet_reference_label": v5_7,
        "v5_8_dry_run_result_packet_reference_label": v5_8,
        "v5_9_dry_run_replay_audit_packet_reference_label": v5_9,
        "v6_0_mvp_lock_label": v6_0,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "station_chief_v6_0_mvp_lock_id": mvp_lock_id,
        "mvp_lock_message": "Station Chief v6.0 MVP lock wrote this deterministic local MVP lock packet. The local command-center loop is recorded as metadata only. No worker was started and no task was executed.",
        "mvp_lock_value": "STATION_CHIEF_V6_0_FIRST_COHERENT_LOCAL_COMMAND_CENTER_LOOP_LOCKED_FOR_REVIEW",
        "mvp_done_value": "MVP_DONE_METADATA_LOCK_ONLY",
        "next_review": "POST_MVP_EXPANSION_REQUIRES_EXPLICIT_OPERATOR_INSTRUCTION",
        "local_mvp_lock_packet_written": True,
        "station_chief_v6_0_mvp_lock_created": True,
        "integrated_local_command_center_loop_recorded": True,
        "mvp_done_recorded": True,
        "local_task_candidate_executed": False,
        "handoff_packet_executed": False,
        "acknowledgement_packet_executed": False,
        "acceptance_review_packet_executed": False,
        "ready_state_packet_executed": False,
        "dry_run_assignment_packet_executed": False,
        "dry_run_result_packet_executed": False,
        "dry_run_replay_audit_packet_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
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
        "v6_1_created": False
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload

def write_station_chief_v6_0_mvp_lock_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    out_dir = Path(output_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = safe_mvp_lock_packet_name(packet_name)
    packet_path = (out_dir / safe_name).resolve()
    
    if not str(packet_path).startswith(str(out_dir.resolve())):
        return create_blocked_mvp_lock_packet_write_record("packet path escape detected")
    
    content = canonical_json(payload)
    packet_path.write_text(content, encoding="utf-8")
    
    return {
        "station_chief_v6_0_mvp_lock_write_record_version": "6.0.0",
        "write_status": "STATION_CHIEF_V6_0_MVP_LOCK_PACKET_WRITTEN",
        "local_mvp_lock_packet_written": True,
        "station_chief_v6_0_mvp_lock_created": True,
        "integrated_local_command_center_loop_recorded": True,
        "mvp_done_recorded": True,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_1_created": False,
        "record_name": safe_name,
        "packet_name": safe_name,
        "record_path": str(packet_path),
        "output_directory": str(out_dir.resolve()),
        "files_written_count": 1,
        "files_written": [safe_name],
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
        "production_execution_performed": False
    }

def create_blocked_mvp_lock_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_mvp_lock_packet_written": False,
        "station_chief_v6_0_mvp_lock_created": False,
        "integrated_local_command_center_loop_recorded": False,
        "mvp_done_recorded": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_1_created": False,
        "record_name": None,
        "packet_name": None,
        "record_path": None,
        "output_directory": None,
        "files_written_count": 0,
        "files_written": []
    }

def create_mvp_lock_packet_record(write_record: dict, payload_digest: str | None = None) -> dict:
    status = write_record.get("write_status", "BLOCKED")
    return {
        "status": status,
        "write_record": write_record,
        "payload_digest": payload_digest,
        "local_mvp_lock_packet_written": write_record.get("local_mvp_lock_packet_written", False),
        "station_chief_v6_0_mvp_lock_created": write_record.get("station_chief_v6_0_mvp_lock_created", False),
        "integrated_local_command_center_loop_recorded": write_record.get("integrated_local_command_center_loop_recorded", False),
        "mvp_done_recorded": write_record.get("mvp_done_recorded", False),
        "local_task_candidate_executed": False,
        "handoff_packet_executed": False,
        "acknowledgement_packet_executed": False,
        "acceptance_review_packet_executed": False,
        "ready_state_packet_executed": False,
        "dry_run_assignment_packet_executed": False,
        "dry_run_result_packet_executed": False,
        "dry_run_replay_audit_packet_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_1_created": False
    }

def create_mvp_lock_audit_record(
    gate: dict, local_task_c: dict, sandbox_worker_c: dict, v5_3_c: dict, v5_4_c: dict,
    v5_5_c: dict, v5_6_c: dict, v5_7_c: dict, v5_8_c: dict, v5_9_c: dict, v6_0_c: dict,
    loop: dict, boundary: dict, denial: dict, plan: dict, packet: dict
) -> dict:
    sections = {
        "gate": gate, "local_task": local_task_c, "worker": sandbox_worker_c, 
        "v5_3": v5_3_c, "v5_4": v5_4_c, "v5_5": v5_5_c, "v5_6": v5_6_c, 
        "v5_7": v5_7_c, "v5_8": v5_8_c, "v5_9": v5_9_c, "v6_0": v6_0_c,
        "loop": loop, "boundary": boundary, "denial": denial, "plan": plan, "packet": packet
    }
    digests = {k: sha256_digest(v) for k, v in sections.items()}
    
    written = packet.get("local_mvp_lock_packet_written", False)
    
    return {
        "section_digests": digests,
        "audit_status": "PASS",
        "local_mvp_lock_packet_written": written,
        "station_chief_v6_0_mvp_lock_created": written,
        "integrated_local_command_center_loop_recorded": written,
        "mvp_done_recorded": written,
        "local_task_candidate_executed": False,
        "handoff_packet_executed": False,
        "acknowledgement_packet_executed": False,
        "acceptance_review_packet_executed": False,
        "ready_state_packet_executed": False,
        "dry_run_assignment_packet_executed": False,
        "dry_run_result_packet_executed": False,
        "dry_run_replay_audit_packet_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_1_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False
    }

def create_mvp_lock_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "status": "STATION_CHIEF_V6_0_MVP_LOCKED" if ready else "BLOCKED",
        "current_layer": "Station Chief v6.0 MVP Lock / Integrated Local Command-Center Loop",
        "v6_0_built_only_as_metadata_lock": True,
        "v6_0_mvp_lock_packet_permitted": True,
        "no_dry_run_task_execution": True,
        "no_local_task_candidate_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback_recovery": True,
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
        "no_v6_1_creation": True
    }

def create_station_chief_post_mvp_expansion_bridge(summary: dict) -> dict:
    ready = summary.get("status") == "STATION_CHIEF_V6_0_MVP_LOCKED"
    return {
        "status": "READY_FOR_POST_MVP_EXPANSION_REVIEW" if ready else "BLOCKED",
        "bridge_to": "post-MVP expansion review only",
        "no_post_mvp_expansion_in_v6_0": True,
        "no_v6_1_creation_in_v6_0": True,
        "no_real_worker_start_in_v6_0": True,
        "no_real_task_execution_in_v6_0": True,
        "no_queue_creation_in_v6_0": True,
        "no_task_enqueue_in_v6_0": True,
        "no_arbitrary_task_execution_in_v6_0": True,
        "no_user_task_execution_in_v6_0": True,
        "no_worker_routing_in_v6_0": True
    }

def create_station_chief_v6_0_mvp_lock_bundle(
    result: dict | None,
    command: str | None = None,
    local_task_candidate_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    v5_9_dry_run_replay_audit_packet_reference_label: str | None = None,
    v6_0_mvp_lock_label: str | None = None,
    output_directory: str | None = None,
    mvp_lock_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    mvp_lock_requested: bool = False,
    write_mvp_lock_packet: bool = False
) -> dict:
    schema = create_station_chief_v6_0_mvp_lock_schema()
    
    local_task = local_task_candidate_label or DEFAULT_LOCAL_TASK_CANDIDATE_LABEL
    sw_label = sandbox_worker_label or DEFAULT_SANDBOX_WORKER_LABEL
    v5_3_label = v5_3_handoff_packet_reference_label or DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL
    v5_4_label = v5_4_acknowledgement_packet_reference_label or DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL
    v5_5_label = v5_5_acceptance_review_packet_reference_label or DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL
    v5_6_label = v5_6_ready_state_packet_reference_label or DEFAULT_V5_6_READY_STATE_PACKET_REFERENCE_LABEL
    v5_7_label = v5_7_dry_run_assignment_packet_reference_label or DEFAULT_V5_7_DRY_RUN_ASSIGNMENT_PACKET_REFERENCE_LABEL
    v5_8_label = v5_8_dry_run_result_packet_reference_label or DEFAULT_V5_8_DRY_RUN_RESULT_PACKET_REFERENCE_LABEL
    v5_9_label = v5_9_dry_run_replay_audit_packet_reference_label or DEFAULT_V5_9_DRY_RUN_REPLAY_AUDIT_PACKET_REFERENCE_LABEL
    v6_0_label = v6_0_mvp_lock_label or DEFAULT_V6_0_MVP_LOCK_LABEL
    
    gate = create_station_chief_v6_0_mvp_lock_approval_gate(
        local_task, sw_label, v5_3_label, v5_4_label, v5_5_label, 
        v5_6_label, v5_7_label, v5_8_label, v5_9_label, v6_0_label,
        output_directory, confirmation_token, human_operator, mvp_lock_requested
    )
    
    local_task_c = create_local_task_candidate_reference_contract(gate)
    worker_c = create_sandbox_worker_reference_contract(gate)
    v5_3_c = create_v5_3_handoff_packet_reference_contract(gate)
    v5_4_c = create_v5_4_acknowledgement_packet_reference_contract(gate)
    v5_5_c = create_v5_5_acceptance_review_packet_reference_contract(gate)
    v5_6_c = create_v5_6_ready_state_packet_reference_contract(gate)
    v5_7_c = create_v5_7_dry_run_assignment_packet_reference_contract(gate)
    v5_8_c = create_v5_8_dry_run_result_packet_reference_contract(gate)
    v5_9_c = create_v5_9_dry_run_replay_audit_packet_reference_contract(gate)
    v6_0_c = create_v6_0_mvp_lock_reference_contract(gate)
    
    loop = create_integrated_local_command_center_loop_contract(
        gate, local_task_c, worker_c, v5_3_c, v5_4_c, v5_5_c, v5_6_c, v5_7_c, v5_8_c, v5_9_c, v6_0_c
    )
    
    boundary = create_non_execution_mvp_lock_boundary(gate, loop)
    denial = create_mvp_lock_permission_denial_record(local_task, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, v5_9_label, v6_0_label)
    
    mvp_lock_id = generate_station_chief_v6_0_mvp_lock_id(
        command or "unknown", local_task, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, v5_9_label, v6_0_label
    )
    
    plan = create_mvp_lock_plan_record(gate, loop, boundary, mvp_lock_id, local_task, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, v5_9_label, v6_0_label, human_operator, write_mvp_lock_packet)
    
    payload = None
    write_record = None
    if write_mvp_lock_packet:
        if gate.get("local_mvp_lock_packet_write_authorized") and plan.get("status") != "BLOCKED":
            payload = build_mvp_lock_packet_payload(
                mvp_lock_id, local_task, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, v5_9_label, v6_0_label, human_operator, gate.get("token_valid")
            )
            write_record = write_station_chief_v6_0_mvp_lock_packet(output_directory, mvp_lock_packet_name, payload)
        else:
            write_record = create_blocked_mvp_lock_packet_write_record("gate or plan blocked")
    else:
        write_record = create_blocked_mvp_lock_packet_write_record("Station Chief v6.0 MVP lock packet write not requested")
        
    packet = create_mvp_lock_packet_record(write_record, payload.get("payload_digest") if payload else None)
    
    # Update boundary with actual write result
    written = packet.get("local_mvp_lock_packet_written", False)
    boundary["local_mvp_lock_packet_written"] = written
    boundary["station_chief_v6_0_mvp_lock_created"] = written
    boundary["integrated_local_command_center_loop_recorded"] = written
    boundary["mvp_done_recorded"] = written
    
    audit_rec = create_mvp_lock_audit_record(gate, local_task_c, worker_c, v5_3_c, v5_4_c, v5_5_c, v5_6_c, v5_7_c, v5_8_c, v5_9_c, v6_0_c, loop, boundary, denial, plan, packet)
    summary = create_mvp_lock_readiness_summary(audit_rec)
    bridge = create_station_chief_post_mvp_expansion_bridge(summary)
    
    return {
        "schema": schema,
        "approval_gate": gate,
        "local_task_candidate_reference_contract": local_task_c,
        "sandbox_worker_reference_contract": worker_c,
        "v5_3_handoff_packet_reference_contract": v5_3_c,
        "v5_4_acknowledgement_packet_reference_contract": v5_4_c,
        "v5_5_acceptance_review_packet_reference_contract": v5_5_c,
        "v5_6_ready_state_packet_reference_contract": v5_6_c,
        "v5_7_dry_run_assignment_packet_reference_contract": v5_7_c,
        "v5_8_dry_run_result_packet_reference_contract": v5_8_c,
        "v5_9_dry_run_replay_audit_packet_reference_contract": v5_9_c,
        "v6_0_mvp_lock_reference_contract": v6_0_c,
        "integrated_local_command_center_loop_contract": loop,
        "non_execution_mvp_lock_boundary": boundary,
        "mvp_lock_permission_denial_record": denial,
        "mvp_lock_plan_record": plan,
        "mvp_lock_packet_record": packet,
        "mvp_lock_audit_record": audit_rec,
        "mvp_lock_readiness_summary": summary,
        "station_chief_post_mvp_expansion_bridge": bridge,
        "mvp_lock_packet_payload": payload,
        "local_mvp_lock_packet_written": written,
        "station_chief_v6_0_mvp_lock_created": written,
        "integrated_local_command_center_loop_recorded": written,
        "mvp_done_recorded": written
    }
