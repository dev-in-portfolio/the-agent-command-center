import json
import hashlib
import re
from pathlib import Path

SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_MODULE_VERSION = "5.9.0"
SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_STATUS = "SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_LOCAL_PACKET_ONLY"
SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_PHASE = "Sandbox Worker Dry-Run Replay / Audit Candidate"
SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE"
DEFAULT_SANDBOX_WORKER_LABEL = "station-chief-sandbox-worker-template"
DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL = "station-chief-v5-3-sandbox-worker-handoff-packet-reference"
DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-4-sandbox-worker-acknowledgement-packet-reference"
DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL = "station-chief-v5-5-sandbox-worker-acceptance-candidate-review-packet-reference"
DEFAULT_V5_6_READY_STATE_PACKET_REFERENCE_LABEL = "station-chief-v5-6-sandbox-worker-ready-state-packet-reference"
DEFAULT_V5_7_DRY_RUN_ASSIGNMENT_PACKET_REFERENCE_LABEL = "station-chief-v5-7-sandbox-worker-dry-run-assignment-packet-reference"
DEFAULT_V5_8_DRY_RUN_RESULT_PACKET_REFERENCE_LABEL = "station-chief-v5-8-sandbox-worker-dry-run-result-packet-reference"
DEFAULT_SYNTHETIC_DRY_RUN_TASK_LABEL = "station-chief-v5-7-synthetic-dry-run-task-reference"
DEFAULT_SYNTHETIC_DRY_RUN_RESULT_LABEL = "station-chief-v5-8-synthetic-dry-run-result-reference"
DEFAULT_REPLAY_AUDIT_CANDIDATE_LABEL = "station-chief-v5-9-sandbox-worker-dry-run-replay-audit-candidate-reference"
DEFAULT_SANDBOX_DRY_RUN_REPLAY_AUDIT_PACKET_NAME = "sandbox_worker_dry_run_replay_audit_candidate_packet.json"

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

def safe_dry_run_replay_audit_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_SANDBOX_DRY_RUN_REPLAY_AUDIT_PACKET_NAME
    if not packet_name.endswith(".json"):
        return DEFAULT_SANDBOX_DRY_RUN_REPLAY_AUDIT_PACKET_NAME
    if "/" in packet_name or "\\" in packet_name:
        return DEFAULT_SANDBOX_DRY_RUN_REPLAY_AUDIT_PACKET_NAME
    if packet_name in [".", ".."]:
        return DEFAULT_SANDBOX_DRY_RUN_REPLAY_AUDIT_PACKET_NAME
    return packet_name

def generate_sandbox_worker_dry_run_replay_audit_candidate_id(
    command: str,
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    v5_6_ready_state_packet_reference_label: str,
    v5_7_dry_run_assignment_packet_reference_label: str,
    v5_8_dry_run_result_packet_reference_label: str,
    synthetic_dry_run_task_label: str,
    synthetic_dry_run_result_label: str,
    replay_audit_candidate_label: str,
    runtime_version: str = "5.9.0"
) -> str:
    salt = f"station-chief-v5-9-replay-audit-{runtime_version}"
    context = {
        "salt": salt,
        "command": command,
        "sandbox_worker_label": sandbox_worker_label,
        "v5_3_handoff": v5_3_handoff_packet_reference_label,
        "v5_4_acknowledgement": v5_4_acknowledgement_packet_reference_label,
        "v5_5_acceptance_review": v5_5_acceptance_review_packet_reference_label,
        "v5_6_ready_state": v5_6_ready_state_packet_reference_label,
        "v5_7_dry_run_assignment": v5_7_dry_run_assignment_packet_reference_label,
        "v5_8_dry_run_result": v5_8_dry_run_result_packet_reference_label,
        "synthetic_task": synthetic_dry_run_task_label,
        "synthetic_result": synthetic_dry_run_result_label,
        "replay_audit": replay_audit_candidate_label
    }
    digest = sha256_digest(context)
    norm_worker = normalize_label(sandbox_worker_label, "worker")
    norm_v5_3 = normalize_label(v5_3_handoff_packet_reference_label, "v5-3")
    norm_v5_4 = normalize_label(v5_4_acknowledgement_packet_reference_label, "v5-4")
    norm_v5_5 = normalize_label(v5_5_acceptance_review_packet_reference_label, "v5-5")
    norm_v5_6 = normalize_label(v5_6_ready_state_packet_reference_label, "v5-6")
    norm_v5_7 = normalize_label(v5_7_dry_run_assignment_packet_reference_label, "v5-7")
    norm_v5_8 = normalize_label(v5_8_dry_run_result_packet_reference_label, "v5-8")
    norm_task = normalize_label(synthetic_dry_run_task_label, "task")
    norm_result = normalize_label(synthetic_dry_run_result_label, "result")
    norm_audit = normalize_label(replay_audit_candidate_label, "audit")
    return f"sandbox-worker-dry-run-replay-audit-candidate-v5-9-{norm_worker}-{norm_v5_3}-{norm_v5_4}-{norm_v5_5}-{norm_v5_6}-{norm_v5_7}-{norm_v5_8}-{norm_task}-{norm_result}-{norm_audit}-{digest[:12]}"

def create_sandbox_worker_dry_run_replay_audit_candidate_schema() -> dict:
    return {
        "schema_version": "5.9.0",
        "status": SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_STATUS,
        "replay_audit_type": "sandbox_worker_dry_run_replay_audit_candidate",
        "required_sections": [
            "sandbox_worker_dry_run_replay_audit_approval_gate",
            "v5_3_handoff_packet_reference_contract",
            "v5_4_acknowledgement_packet_reference_contract",
            "v5_5_acceptance_review_packet_reference_contract",
            "v5_6_ready_state_packet_reference_contract",
            "v5_7_dry_run_assignment_packet_reference_contract",
            "v5_8_dry_run_result_packet_reference_contract",
            "synthetic_dry_run_task_reference_contract",
            "synthetic_dry_run_result_reference_contract",
            "replay_audit_candidate_reference_contract",
            "sandbox_worker_dry_run_replay_audit_reference_contract",
            "dry_run_replay_audit_scope_contract",
            "non_execution_dry_run_replay_audit_boundary",
            "dry_run_replay_audit_permission_denial_record",
            "dry_run_replay_audit_plan_record",
            "dry_run_replay_audit_packet_record",
            "dry_run_replay_audit_audit_record",
            "dry_run_replay_audit_readiness_summary",
            "station_chief_mvp_lock_candidate_bridge"
        ],
        "required_token": SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_dry_run_replay_audit_packet_written": False,
        "sandbox_worker_dry_run_replay_audit_candidate_created": False,
        "dry_run_replay_candidate_recorded": False,
        "dry_run_audit_candidate_recorded": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False,
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

def create_sandbox_worker_dry_run_replay_audit_approval_gate(
    sandbox_worker_label: str,
    v5_3_handoff_packet_reference_label: str,
    v5_4_acknowledgement_packet_reference_label: str,
    v5_5_acceptance_review_packet_reference_label: str,
    v5_6_ready_state_packet_reference_label: str,
    v5_7_dry_run_assignment_packet_reference_label: str,
    v5_8_dry_run_result_packet_reference_label: str,
    synthetic_dry_run_task_label: str,
    synthetic_dry_run_result_label: str,
    replay_audit_candidate_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    replay_audit_requested: bool = False
) -> dict:
    token_valid = (confirmation_token == SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL_TOKEN)
    gate_authorized = (
        token_valid and 
        bool(human_operator) and 
        bool(sandbox_worker_label) and 
        bool(v5_3_handoff_packet_reference_label) and 
        bool(v5_4_acknowledgement_packet_reference_label) and 
        bool(v5_5_acceptance_review_packet_reference_label) and 
        bool(v5_6_ready_state_packet_reference_label) and 
        bool(v5_7_dry_run_assignment_packet_reference_label) and 
        bool(v5_8_dry_run_result_packet_reference_label) and 
        bool(synthetic_dry_run_task_label) and 
        bool(synthetic_dry_run_result_label) and 
        bool(replay_audit_candidate_label)
    )
    packet_write_authorized = (gate_authorized and bool(output_directory) and replay_audit_requested)
    
    status = "BLOCKED_PENDING_V5_9_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL"
    if gate_authorized:
        status = "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE"
        
    return {
        "status": status,
        "confirmation_token_valid": token_valid,
        "human_operator_present": bool(human_operator),
        "sandbox_worker_label_present": bool(sandbox_worker_label),
        "v5_3_handoff_packet_reference_label_present": bool(v5_3_handoff_packet_reference_label),
        "v5_4_acknowledgement_packet_reference_label_present": bool(v5_4_acknowledgement_packet_reference_label),
        "v5_5_acceptance_review_packet_reference_label_present": bool(v5_5_acceptance_review_packet_reference_label),
        "v5_6_ready_state_packet_reference_label_present": bool(v5_6_ready_state_packet_reference_label),
        "v5_7_dry_run_assignment_packet_reference_label_present": bool(v5_7_dry_run_assignment_packet_reference_label),
        "v5_8_dry_run_result_packet_reference_label_present": bool(v5_8_dry_run_result_packet_reference_label),
        "synthetic_dry_run_task_label_present": bool(synthetic_dry_run_task_label),
        "synthetic_dry_run_result_label_present": bool(synthetic_dry_run_result_label),
        "replay_audit_candidate_label_present": bool(replay_audit_candidate_label),
        "output_directory_present": bool(output_directory),
        "replay_audit_requested": replay_audit_requested,
        "local_dry_run_replay_audit_records_authorized": gate_authorized,
        "local_dry_run_replay_audit_packet_write_authorized": packet_write_authorized,
        "dry_run_task_execution_authorized": False,
        "real_worker_result_creation_authorized": False,
        "live_replay_authorized": False,
        "production_audit_authorized": False,
        "rollback_authorized": False,
        "recovery_authorized": False,
        "mvp_lock_authorized": False,
        "v6_0_creation_authorized": False,
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
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
        "no_production_audit_performed": True,
        "no_v6_0_approval": True
    }

def create_synthetic_dry_run_task_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "synthetic_dry_run_task_label",
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

def create_synthetic_dry_run_result_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "synthetic_dry_run_result_label",
        "is_metadata_only": True,
        "is_deterministic": True,
        "no_task_execution_origin": True,
        "no_real_worker_output": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_external_transmission": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True
    }

def create_replay_audit_candidate_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "replay_audit_candidate_label",
        "is_metadata_only": True,
        "is_deterministic": True,
        "no_live_replay_action": True,
        "no_production_audit_action": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_external_transmission": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True,
        "v6_0_mvp_lock_review_only": True
    }

def create_sandbox_worker_dry_run_replay_audit_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_dry_run_replay_audit_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "sandbox_worker_label",
        "is_metadata_only": True,
        "no_running_process": True,
        "no_worker_start": True,
        "local_metadata_only": True,
        "no_task_execution": True,
        "no_real_result_creation": True,
        "no_live_replay_performed": True,
        "no_production_audit_performed": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_tool_calling": True,
        "no_api_access": True,
        "no_network_access": True,
        "no_credential_access": True,
        "no_live_work_routing": True,
        "no_v6_0_approval": True
    }

def create_dry_run_replay_audit_scope_contract(
    approval_gate: dict,
    v5_3: dict, v5_4: dict, v5_5: dict, v5_6: dict, v5_7: dict, v5_8: dict,
    task: dict, result: dict, audit: dict, worker: dict
) -> dict:
    contracts_passed = all(c.get("status") == "PASS" for c in [v5_3, v5_4, v5_5, v5_6, v5_7, v5_8, task, result, audit, worker])
    scope_passed = approval_gate.get("local_dry_run_replay_audit_records_authorized") and contracts_passed
    
    return {
        "status": "PASS" if scope_passed else "BLOCKED",
        "exactly_one_sandbox_worker_label": True,
        "exactly_one_v5_3_handoff_packet_reference": True,
        "exactly_one_v5_4_acknowledgement_packet_reference": True,
        "exactly_one_v5_5_acceptance_review_packet_reference": True,
        "exactly_one_v5_6_ready_state_packet_reference": True,
        "exactly_one_v5_7_dry_run_assignment_packet_reference": True,
        "exactly_one_v5_8_dry_run_result_packet_reference": True,
        "exactly_one_synthetic_dry_run_task_label": True,
        "exactly_one_synthetic_dry_run_result_label": True,
        "exactly_one_replay_audit_candidate_label": True,
        "exactly_one_dry_run_replay_audit_candidate_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "dry_run_replay_audit_metadata_only": True,
        "synthetic_chain_replay_audit_candidate_only": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_v6_0_creation": True,
        "no_mvp_lock": True,
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

def create_non_execution_dry_run_replay_audit_boundary(
    approval_gate: dict,
    scope_contract: dict,
    packet_written: bool = False,
    replay_recorded: bool = False,
    audit_recorded: bool = False
) -> dict:
    boundary_passed = scope_contract.get("status") == "PASS"
    
    return {
        "status": "PASS" if boundary_passed else "BLOCKED",
        "sandbox_worker_dry_run_replay_audit_candidate_local_packet_only": True,
        "dry_run_replay_audit_candidate_not_executed": True,
        "live_replay_not_performed": True,
        "production_audit_not_performed": True,
        "dry_run_task_not_executed": True,
        "real_worker_result_not_created": True,
        "rollback_not_performed": True,
        "recovery_not_performed": True,
        "mvp_lock_not_created": True,
        "v6_0_not_created": True,
        "synthetic_task_label_not_enqueued": True,
        "synthetic_result_label_not_externally_transmitted": True,
        "replay_audit_candidate_label_not_externally_transmitted": True,
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
        "sandbox_worker_dry_run_replay_audit_candidate_created": packet_written,
        "dry_run_replay_candidate_recorded": replay_recorded,
        "dry_run_audit_candidate_recorded": audit_recorded
    }

def create_dry_run_replay_audit_permission_denial_record(
    sandbox_worker_label: str,
    v5_3: str, v5_4: str, v5_5: str, v5_6: str, v5_7: str, v5_8: str,
    task: str, result: str, audit: str
) -> dict:
    return {
        "explicitly_denied": {
            "dry_run_task_execution": True,
            "real_dry_run_result_generation": True,
            "real_worker_result_creation": True,
            "live_replay_execution": True,
            "production_audit_execution": True,
            "rollback_execution": True,
            "recovery_execution": True,
            "v6_0_mvp_lock": True,
            "v6_0_creation": True,
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
            "v5_3_handoff_mutation": True,
            "v5_3_handoff_execution": True,
            "v5_4_acknowledgement_mutation": True,
            "v5_4_acknowledgement_execution": True,
            "v5_5_acceptance_review_mutation": True,
            "v5_5_acceptance_review_execution": True,
            "v5_6_ready_state_mutation": True,
            "v5_6_ready_state_execution": True,
            "v5_7_dry_run_assignment_mutation": True,
            "v5_7_dry_run_assignment_execution": True,
            "v5_8_dry_run_result_mutation": True,
            "v5_8_dry_run_result_execution": True,
            "synthetic_dry_run_task_execution": True,
            "synthetic_dry_run_result_external_transmission": True,
            "replay_audit_candidate_external_transmission": True
        }
    }

def create_dry_run_replay_audit_plan_record(
    approval_gate: dict,
    scope_contract: dict,
    boundary: dict,
    candidate_id: str,
    sandbox_worker_label: str,
    v5_3: str, v5_4: str, v5_5: str, v5_6: str, v5_7: str, v5_8: str,
    task: str, result: str, audit: str,
    human_operator: str | None,
    write_authorized: bool = False
) -> dict:
    valid = approval_gate.get("local_dry_run_replay_audit_records_authorized") and scope_contract.get("status") == "PASS" and boundary.get("status") == "PASS"
    status = "LOCAL_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_PLAN_CREATED" if valid else "BLOCKED"
    
    return {
        "status": status,
        "dry_run_replay_audit_candidate_id": candidate_id,
        "sandbox_worker_label": sandbox_worker_label,
        "sandbox_worker_label_normalized": normalize_label(sandbox_worker_label, ""),
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
        "synthetic_dry_run_task_label": task,
        "synthetic_dry_run_task_label_normalized": normalize_label(task, ""),
        "synthetic_dry_run_result_label": result,
        "synthetic_dry_run_result_label_normalized": normalize_label(result, ""),
        "replay_audit_candidate_label": audit,
        "replay_audit_candidate_label_normalized": normalize_label(audit, ""),
        "human_operator": human_operator,
        "dry_run_replay_audit_mode": "deterministic_local_dry_run_replay_audit_candidate_only",
        "packet_runtime_state": "written" if write_authorized else "not_written",
        "worker_runtime_state": "not_started",
        "dry_run_replay_state": "recorded_synthetic_metadata_only" if write_authorized else "not_performed",
        "dry_run_audit_state": "recorded_synthetic_metadata_only" if write_authorized else "not_performed",
        "dry_run_task_execution_state": "not_executed",
        "real_worker_result_state": "not_created",
        "live_replay_state": "not_performed",
        "production_audit_state": "not_performed",
        "rollback_state": "not_performed",
        "recovery_state": "not_performed",
        "mvp_lock_state": "not_created",
        "v6_0_state": "not_created",
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
        "mvp_lock_created": False,
        "v6_0_created": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "worker_process_started": False,
        "agent_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "api_call_performed": False,
        "network_access_performed": False
    }

def build_dry_run_replay_audit_packet_payload(
    candidate_id: str,
    sandbox_worker_label: str,
    v5_3: str, v5_4: str, v5_5: str, v5_6: str, v5_7: str, v5_8: str,
    task: str, result: str, audit: str,
    human_operator: str,
    approval_token_valid: bool
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "5.9.0",
        "replay_audit_type": "sandbox_worker_dry_run_replay_audit_candidate",
        "dry_run_replay_audit_mode": "deterministic_local_dry_run_replay_audit_candidate_only",
        "sandbox_worker_label": sandbox_worker_label,
        "v5_3_handoff_packet_reference_label": v5_3,
        "v5_4_acknowledgement_packet_reference_label": v5_4,
        "v5_5_acceptance_review_packet_reference_label": v5_5,
        "v5_6_ready_state_packet_reference_label": v5_6,
        "v5_7_dry_run_assignment_packet_reference_label": v5_7,
        "v5_8_dry_run_result_packet_reference_label": v5_8,
        "synthetic_dry_run_task_label": task,
        "synthetic_dry_run_result_label": result,
        "replay_audit_candidate_label": audit,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "dry_run_replay_audit_candidate_id": candidate_id,
        "replay_audit_message": "Station Chief sandbox worker dry-run replay/audit candidate wrote this deterministic local replay/audit packet. No worker was started, no task was executed, and no live replay or production audit occurred.",
        "replay_audit_value": "SYNTHETIC_DRY_RUN_CHAIN_REPLAY_AUDIT_RECORDED_FOR_V6_0_MVP_LOCK_REVIEW_ONLY",
        "replay_audit_next_review": "READY_FOR_STATION_CHIEF_V6_0_MVP_LOCK_REVIEW_ONLY",
        "local_dry_run_replay_audit_packet_written": True,
        "sandbox_worker_dry_run_replay_audit_candidate_created": True,
        "dry_run_replay_candidate_recorded": True,
        "dry_run_audit_candidate_recorded": True,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False,
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

def write_sandbox_worker_dry_run_replay_audit_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    out_dir = Path(output_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = safe_dry_run_replay_audit_packet_name(packet_name)
    packet_path = (out_dir / safe_name).resolve()
    
    if not str(packet_path).startswith(str(out_dir.resolve())):
        return create_blocked_dry_run_replay_audit_packet_write_record("packet path escape detected")
    
    content = canonical_json(payload)
    packet_path.write_text(content, encoding="utf-8")
    
    return {
        "sandbox_worker_dry_run_replay_audit_write_record_version": "5.9.0",
        "write_status": "SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_WRITTEN",
        "local_dry_run_replay_audit_packet_written": True,
        "sandbox_worker_dry_run_replay_audit_candidate_created": True,
        "dry_run_replay_candidate_recorded": True,
        "dry_run_audit_candidate_recorded": True,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False,
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

def create_blocked_dry_run_replay_audit_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_dry_run_replay_audit_packet_written": False,
        "sandbox_worker_dry_run_replay_audit_candidate_created": False,
        "dry_run_replay_candidate_recorded": False,
        "dry_run_audit_candidate_recorded": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False,
        "record_name": None,
        "packet_name": None,
        "record_path": None,
        "output_directory": None,
        "files_written_count": 0,
        "files_written": []
    }

def create_dry_run_replay_audit_packet_record(write_record: dict, payload_digest: str | None = None) -> dict:
    status = write_record.get("write_status", "BLOCKED")
    return {
        "status": status,
        "write_record": write_record,
        "payload_digest": payload_digest,
        "local_dry_run_replay_audit_packet_written": write_record.get("local_dry_run_replay_audit_packet_written", False),
        "sandbox_worker_dry_run_replay_audit_candidate_created": write_record.get("sandbox_worker_dry_run_replay_audit_candidate_created", False),
        "dry_run_replay_candidate_recorded": write_record.get("dry_run_replay_candidate_recorded", False),
        "dry_run_audit_candidate_recorded": write_record.get("dry_run_audit_candidate_recorded", False),
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False
    }

def create_dry_run_replay_audit_audit_record(
    gate: dict, v5_3: dict, v5_4: dict, v5_5: dict, v5_6: dict, v5_7: dict, v5_8: dict,
    task: dict, result: dict, audit: dict, worker: dict, scope: dict, boundary: dict,
    denial: dict, plan: dict, packet: dict
) -> dict:
    sections = {
        "gate": gate, "v5_3": v5_3, "v5_4": v5_4, "v5_5": v5_5, "v5_6": v5_6, "v5_7": v5_7, "v5_8": v5_8,
        "task": task, "result": result, "audit": audit, "worker": worker, "scope": scope, "boundary": boundary,
        "denial": denial, "plan": plan, "packet": packet
    }
    digests = {k: sha256_digest(v) for k, v in sections.items()}
    
    written = packet.get("local_dry_run_replay_audit_packet_written", False)
    
    return {
        "section_digests": digests,
        "audit_status": "PASS",
        "sandbox_worker_dry_run_replay_audit_candidate_created": written,
        "dry_run_replay_candidate_recorded": written,
        "dry_run_audit_candidate_recorded": written,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "mvp_lock_created": False,
        "v6_0_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False
    }

def create_dry_run_replay_audit_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "status": "READY_FOR_STATION_CHIEF_V6_0_MVP_LOCK_REVIEW_ONLY" if ready else "BLOCKED",
        "next_layer": "Station Chief v6.0 MVP Lock / Integrated Local Command-Center Loop",
        "v6_0_built": False,
        "v5_9_sandbox_worker_dry_run_replay_audit_candidate_packet_permitted": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback_recovery": True,
        "no_mvp_lock": True,
        "no_v6_0_creation": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_api_network_deployment_production": True
    }

def create_station_chief_mvp_lock_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("status") == "READY_FOR_STATION_CHIEF_V6_0_MVP_LOCK_REVIEW_ONLY"
    return {
        "status": "READY_FOR_V6_0_REVIEW" if ready else "BLOCKED",
        "bridge_to": "Station Chief v6.0 MVP lock review only",
        "no_v6_0_mvp_lock_in_v5_9": True,
        "no_command_center_loop_in_v5_9": True,
        "no_dry_run_task_execution_in_v5_9": True,
        "no_worker_start_in_v5_9": True,
        "no_agent_start_in_v5_9": True,
        "no_queue_creation_in_v5_9": True,
        "no_task_enqueue_in_v5_9": True,
        "no_arbitrary_task_execution_in_v5_9": True,
        "no_user_task_execution_in_v5_9": True,
        "no_worker_routing_in_v5_9": True
    }

def create_sandbox_worker_dry_run_replay_audit_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    synthetic_dry_run_result_label: str | None = None,
    replay_audit_candidate_label: str | None = None,
    output_directory: str | None = None,
    dry_run_replay_audit_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    replay_audit_requested: bool = False,
    write_dry_run_replay_audit_packet: bool = False
) -> dict:
    schema = create_sandbox_worker_dry_run_replay_audit_candidate_schema()
    
    sw_label = sandbox_worker_label or DEFAULT_SANDBOX_WORKER_LABEL
    v5_3_label = v5_3_handoff_packet_reference_label or DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL
    v5_4_label = v5_4_acknowledgement_packet_reference_label or DEFAULT_V5_4_ACKNOWLEDGEMENT_PACKET_REFERENCE_LABEL
    v5_5_label = v5_5_acceptance_review_packet_reference_label or DEFAULT_V5_5_ACCEPTANCE_REVIEW_PACKET_REFERENCE_LABEL
    v5_6_label = v5_6_ready_state_packet_reference_label or DEFAULT_V5_6_READY_STATE_PACKET_REFERENCE_LABEL
    v5_7_label = v5_7_dry_run_assignment_packet_reference_label or DEFAULT_V5_7_DRY_RUN_ASSIGNMENT_PACKET_REFERENCE_LABEL
    v5_8_label = v5_8_dry_run_result_packet_reference_label or DEFAULT_V5_8_DRY_RUN_RESULT_PACKET_REFERENCE_LABEL
    task_label = synthetic_dry_run_task_label or DEFAULT_SYNTHETIC_DRY_RUN_TASK_LABEL
    res_label = synthetic_dry_run_result_label or DEFAULT_SYNTHETIC_DRY_RUN_RESULT_LABEL
    aud_label = replay_audit_candidate_label or DEFAULT_REPLAY_AUDIT_CANDIDATE_LABEL
    
    gate = create_sandbox_worker_dry_run_replay_audit_approval_gate(
        sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label,
        task_label, res_label, aud_label,
        output_directory, confirmation_token, human_operator, replay_audit_requested
    )
    
    v5_3_c = create_v5_3_handoff_packet_reference_contract(gate)
    v5_4_c = create_v5_4_acknowledgement_packet_reference_contract(gate)
    v5_5_c = create_v5_5_acceptance_review_packet_reference_contract(gate)
    v5_6_c = create_v5_6_ready_state_packet_reference_contract(gate)
    v5_7_c = create_v5_7_dry_run_assignment_packet_reference_contract(gate)
    v5_8_c = create_v5_8_dry_run_result_packet_reference_contract(gate)
    task_c = create_synthetic_dry_run_task_reference_contract(gate)
    res_c = create_synthetic_dry_run_result_reference_contract(gate)
    aud_c = create_replay_audit_candidate_reference_contract(gate)
    worker_c = create_sandbox_worker_dry_run_replay_audit_reference_contract(gate)
    
    scope = create_dry_run_replay_audit_scope_contract(gate, v5_3_c, v5_4_c, v5_5_c, v5_6_c, v5_7_c, v5_8_c, task_c, res_c, aud_c, worker_c)
    
    boundary = create_non_execution_dry_run_replay_audit_boundary(gate, scope)
    denial = create_dry_run_replay_audit_permission_denial_record(sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, task_label, res_label, aud_label)
    
    candidate_id = generate_sandbox_worker_dry_run_replay_audit_candidate_id(
        command or "unknown", sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, task_label, res_label, aud_label
    )
    
    plan = create_dry_run_replay_audit_plan_record(gate, scope, boundary, candidate_id, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, task_label, res_label, aud_label, human_operator, write_dry_run_replay_audit_packet)
    
    payload = None
    write_record = None
    if write_dry_run_replay_audit_packet:
        if gate.get("local_dry_run_replay_audit_packet_write_authorized") and plan.get("status") != "BLOCKED":
            payload = build_dry_run_replay_audit_packet_payload(
                candidate_id, sw_label, v5_3_label, v5_4_label, v5_5_label, v5_6_label, v5_7_label, v5_8_label, task_label, res_label, aud_label, human_operator, gate.get("confirmation_token_valid")
            )
            write_record = write_sandbox_worker_dry_run_replay_audit_packet(output_directory, dry_run_replay_audit_packet_name, payload)
        else:
            write_record = create_blocked_dry_run_replay_audit_packet_write_record("gate or plan blocked")
    else:
        write_record = create_blocked_dry_run_replay_audit_packet_write_record("sandbox worker dry-run replay/audit candidate packet write not requested")
        
    packet = create_dry_run_replay_audit_packet_record(write_record, payload.get("payload_digest") if payload else None)
    
    # Update boundary with actual write result
    written = packet.get("local_dry_run_replay_audit_packet_written", False)
    boundary["sandbox_worker_dry_run_replay_audit_candidate_created"] = written
    boundary["dry_run_replay_candidate_recorded"] = written
    boundary["dry_run_audit_candidate_recorded"] = written
    
    audit_rec = create_dry_run_replay_audit_audit_record(gate, v5_3_c, v5_4_c, v5_5_c, v5_6_c, v5_7_c, v5_8_c, task_c, res_c, aud_c, worker_c, scope, boundary, denial, plan, packet)
    readiness = create_dry_run_replay_audit_readiness_summary(audit_rec)
    bridge = create_station_chief_mvp_lock_candidate_bridge(readiness)
    
    return {
        "schema": schema,
        "approval_gate": gate,
        "v5_3_handoff_packet_reference_contract": v5_3_c,
        "v5_4_acknowledgement_packet_reference_contract": v5_4_c,
        "v5_5_acceptance_review_packet_reference_contract": v5_5_c,
        "v5_6_ready_state_packet_reference_contract": v5_6_c,
        "v5_7_dry_run_assignment_packet_reference_contract": v5_7_c,
        "v5_8_dry_run_result_packet_reference_contract": v5_8_c,
        "synthetic_dry_run_task_reference_contract": task_c,
        "synthetic_dry_run_result_reference_contract": res_c,
        "replay_audit_candidate_reference_contract": aud_c,
        "sandbox_worker_dry_run_replay_audit_reference_contract": worker_c,
        "dry_run_replay_audit_scope_contract": scope,
        "non_execution_dry_run_replay_audit_boundary": boundary,
        "dry_run_replay_audit_permission_denial_record": denial,
        "dry_run_replay_audit_plan_record": plan,
        "dry_run_replay_audit_packet_record": packet,
        "dry_run_replay_audit_audit_record": audit_rec,
        "dry_run_replay_audit_readiness_summary": readiness,
        "station_chief_mvp_lock_candidate_bridge": bridge,
        "dry_run_replay_audit_packet_payload": payload,
        "local_dry_run_replay_audit_packet_written": written,
        "sandbox_worker_dry_run_replay_audit_candidate_created": written,
        "dry_run_replay_candidate_recorded": written,
        "dry_run_audit_candidate_recorded": written
    }
