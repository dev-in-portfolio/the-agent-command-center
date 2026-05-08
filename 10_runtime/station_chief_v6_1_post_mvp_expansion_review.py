import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_MODULE_VERSION = "6.1.0"
STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_STATUS = "STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PHASE = "Station Chief v6.1 Post-MVP Expansion Review Candidate"
STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW"
DEFAULT_V6_0_MVP_LOCK_REFERENCE_LABEL = "station-chief-v6-0-mvp-lock-reference"
DEFAULT_POST_MVP_EXPANSION_REVIEW_LABEL = "station-chief-v6-1-post-mvp-expansion-review-reference"
DEFAULT_REQUESTED_EXPANSION_LANE_LABEL = "local-worker-persona-expansion-review"
DEFAULT_EXPANSION_BOUNDARY_LABEL = "metadata-only-no-execution-boundary"
DEFAULT_EXPANSION_SAFETY_POSTURE_LABEL = "post-mvp-review-deny-execution-by-default"
DEFAULT_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_NAME = "station_chief_v6_1_post_mvp_expansion_review_packet.json"

SUPPORTED_POST_MVP_EXPANSION_REVIEW_LANES = [
    "local_worker_persona_expansion_review",
    "multi_sandbox_worker_review",
    "richer_task_packet_review",
    "local_queue_simulation_review",
    "local_execution_replay_review",
    "dashboard_surface_review",
    "validator_hardening_review",
    "controlled_real_local_worker_execution_review",
    "optional_future_api_tool_integration_review",
]

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

def normalize_lane_label(label: str | None) -> str:
    if not label:
        return "local_worker_persona_expansion_review"
    normalized = label.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = normalized.strip("_")
    if normalized in SUPPORTED_POST_MVP_EXPANSION_REVIEW_LANES:
        return normalized
    return "local_worker_persona_expansion_review"

def safe_post_mvp_expansion_review_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_NAME
    if not packet_name.endswith(".json"):
        return DEFAULT_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_NAME
    if "/" in packet_name or "\\" in packet_name:
        return DEFAULT_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_NAME
    if packet_name in [".", ".."]:
        return DEFAULT_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_NAME
    return packet_name

def generate_station_chief_v6_1_post_mvp_expansion_review_id(
    command: str,
    v6_0_mvp_lock_reference_label: str,
    post_mvp_expansion_review_label: str,
    requested_expansion_lane_label: str,
    expansion_boundary_label: str,
    expansion_safety_posture_label: str,
    runtime_version: str = "6.1.0"
) -> str:
    salt = f"station-chief-v6-1-post-mvp-expansion-review-{runtime_version}"
    context = {
        "salt": salt,
        "command": command,
        "v6_0_mvp_lock": v6_0_mvp_lock_reference_label,
        "post_mvp_review": post_mvp_expansion_review_label,
        "expansion_lane": requested_expansion_lane_label,
        "boundary": expansion_boundary_label,
        "safety_posture": expansion_safety_posture_label
    }
    digest = sha256_digest(context)
    
    parts = [
        normalize_label(v6_0_mvp_lock_reference_label, "v6-0"),
        normalize_label(post_mvp_expansion_review_label, "v6-1-review"),
        normalize_label(requested_expansion_lane_label, "lane"),
        normalize_label(expansion_boundary_label, "boundary"),
        normalize_label(expansion_safety_posture_label, "safety")
    ]
    
    return f"station-chief-v6-1-post-mvp-expansion-review-{'-'.join(parts)}-{digest[:12]}"

def create_station_chief_v6_1_post_mvp_expansion_review_schema() -> dict:
    return {
        "schema_version": "6.1.0",
        "status": STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_STATUS,
        "review_type": "station_chief_v6_1_post_mvp_expansion_review",
        "post_mvp_expansion_execution_type": "none_metadata_review_only",
        "supported_review_lanes": SUPPORTED_POST_MVP_EXPANSION_REVIEW_LANES,
        "required_sections": [
            "post_mvp_expansion_review_approval_gate",
            "v6_0_mvp_lock_reference_contract",
            "requested_expansion_lane_contract",
            "expansion_boundary_contract",
            "expansion_safety_posture_contract",
            "post_mvp_expansion_review_scope_contract",
            "non_execution_post_mvp_expansion_boundary",
            "post_mvp_expansion_permission_denial_record",
            "post_mvp_expansion_review_plan_record",
            "post_mvp_expansion_review_packet_record",
            "post_mvp_expansion_review_audit_record",
            "post_mvp_expansion_review_readiness_summary",
            "station_chief_v6_2_candidate_bridge"
        ],
        "required_token": STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "locked_175_family_baseline_preserved": True,
        "local_post_mvp_expansion_review_packet_written": False,
        "station_chief_v6_1_post_mvp_expansion_review_created": False,
        "post_mvp_expansion_review_recorded": False,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
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
        "v6_2_created": False
    }

def create_post_mvp_expansion_review_approval_gate(
    v6_0_mvp_lock_reference_label: str,
    post_mvp_expansion_review_label: str,
    requested_expansion_lane_label: str,
    expansion_boundary_label: str,
    expansion_safety_posture_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    post_mvp_expansion_review_requested: bool = False
) -> dict:
    token_valid = (confirmation_token == STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_APPROVAL_TOKEN)
    all_labels_present = all([
        v6_0_mvp_lock_reference_label,
        post_mvp_expansion_review_label,
        requested_expansion_lane_label,
        expansion_boundary_label,
        expansion_safety_posture_label
    ])
    
    local_post_mvp_expansion_review_records_authorized = (
        token_valid and bool(human_operator) and all_labels_present
    )
    
    local_post_mvp_expansion_review_packet_write_authorized = (
        local_post_mvp_expansion_review_records_authorized and bool(output_directory) and post_mvp_expansion_review_requested
    )
    
    status = "BLOCKED_PENDING_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_APPROVAL"
    if local_post_mvp_expansion_review_records_authorized:
        status = "APPROVED_FOR_ONE_LOCAL_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET"
        
    return {
        "status": status,
        "token_valid": token_valid,
        "human_operator_present": bool(human_operator),
        "all_labels_present": all_labels_present,
        "output_directory_present": bool(output_directory),
        "post_mvp_expansion_review_requested": post_mvp_expansion_review_requested,
        "local_post_mvp_expansion_review_records_authorized": local_post_mvp_expansion_review_records_authorized,
        "local_post_mvp_expansion_review_packet_write_authorized": local_post_mvp_expansion_review_packet_write_authorized,
        "post_mvp_expansion_execution_authorized": False,
        "selected_expansion_lane_execution_authorized": False,
        "v6_0_mvp_lock_mutation_authorized": False,
        "v6_0_mvp_lock_execution_authorized": False,
        "local_task_candidate_execution_authorized": False,
        "worker_process_start_authorized": False,
        "agent_start_authorized": False,
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
        "v6_2_creation_authorized": False
    }

def create_v6_0_mvp_lock_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_post_mvp_expansion_review_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "reference_type": "v6_0_mvp_lock_label",
        "is_metadata_only": True,
        "no_read_from_disk": True,
        "no_mutation": True,
        "no_execution": True,
        "no_deployment": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_queue_creation": True,
        "no_v6_2_authorization": True
    }

def create_requested_expansion_lane_contract(approval_gate: dict, lane_label: str) -> dict:
    if not approval_gate.get("local_post_mvp_expansion_review_records_authorized"):
        return {"status": "BLOCKED"}
    
    normalized_lane = normalize_lane_label(lane_label)
    
    return {
        "status": "PASS",
        "selected_lane": normalized_lane,
        "is_metadata_only": True,
        "no_execution": True,
        "no_implementation": True,
        "no_live_runtime_mode": True,
        "no_file_creation_outside_packet": True,
        "no_worker_start": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_deployment": True,
        "no_production_access": True
    }

def create_expansion_boundary_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_post_mvp_expansion_review_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "boundary_type": "metadata_only",
        "no_execution": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_queue_creation": True,
        "no_task_execution": True,
        "no_api_network_deployment_production": True,
        "no_v6_2_creation": True
    }

def create_expansion_safety_posture_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_post_mvp_expansion_review_records_authorized"):
        return {"status": "BLOCKED"}
    return {
        "status": "PASS",
        "deny_execution_by_default": True,
        "deny_worker_start_by_default": True,
        "deny_agent_start_by_default": True,
        "deny_queue_creation_by_default": True,
        "deny_api_network_deployment_production_by_default": True,
        "deny_v6_2_creation_by_default": True,
        "future_expansion_requires_explicit_operator_instruction": True
    }

def create_post_mvp_expansion_review_scope_contract(
    approval_gate: dict,
    v6_0_c: dict, lane_c: dict, boundary_c: dict, safety_c: dict
) -> dict:
    contracts_passed = all(c.get("status") == "PASS" for c in [v6_0_c, lane_c, boundary_c, safety_c])
    scope_passed = approval_gate.get("local_post_mvp_expansion_review_records_authorized") and contracts_passed
    
    return {
        "status": "PASS" if scope_passed else "BLOCKED",
        "exactly_one_v6_0_mvp_lock_reference": True,
        "exactly_one_post_mvp_expansion_review_label": True,
        "exactly_one_requested_expansion_lane": True,
        "exactly_one_expansion_boundary": True,
        "exactly_one_expansion_safety_posture": True,
        "exactly_one_post_mvp_expansion_review_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "post_mvp_expansion_review_metadata_only": True,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "no_local_task_candidate_execution": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_v6_2_creation": True,
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
        "review_scope": "post_mvp_expansion_review_candidate_metadata_only"
    }

def create_non_execution_post_mvp_expansion_boundary(
    approval_gate: dict,
    scope_contract: dict,
    packet_written: bool = False,
    review_recorded: bool = False
) -> dict:
    boundary_passed = scope_contract.get("status") == "PASS"
    
    return {
        "status": "PASS" if boundary_passed else "BLOCKED",
        "station_chief_v6_1_post_mvp_expansion_review_local_packet_only": True,
        "review_packet_not_executed": True,
        "post_mvp_expansion_not_executed": True,
        "selected_expansion_lane_not_executed": True,
        "v6_0_mvp_lock_not_mutated": True,
        "v6_0_mvp_lock_not_executed": True,
        "local_task_candidate_not_executed": True,
        "dry_run_task_not_executed": True,
        "real_worker_result_not_created": True,
        "live_replay_not_performed": True,
        "production_audit_not_performed": True,
        "rollback_not_performed": True,
        "recovery_not_performed": True,
        "v6_2_not_created": True,
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
        "local_post_mvp_expansion_review_packet_written": packet_written,
        "station_chief_v6_1_post_mvp_expansion_review_created": packet_written,
        "post_mvp_expansion_review_recorded": review_recorded
    }

def create_post_mvp_expansion_permission_denial_record(
    v6_0: str, review: str, lane: str, boundary: str, safety: str
) -> dict:
    return {
        "explicitly_denied": {
            "post_mvp_expansion_execution": True,
            "selected_expansion_lane_execution": True,
            "v6_0_mvp_lock_mutation": True,
            "v6_0_mvp_lock_execution": True,
            "v6_2_creation": True,
            "post_mvp_implementation_file_creation": True,
            "local_task_candidate_execution": True,
            "dry_run_task_execution": True,
            "real_dry_run_result_generation": True,
            "real_worker_result_creation": True,
            "live_replay_execution": True,
            "production_audit_execution": True,
            "rollback_execution": True,
            "recovery_execution": True,
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
            "v6_0_mvp_lock_mutation": True,
            "v6_0_mvp_lock_execution": True,
            "external_transmission_of_review_labels": True
        }
    }

def create_post_mvp_expansion_review_plan_record(
    approval_gate: dict,
    scope_contract: dict,
    boundary: dict,
    review_id: str,
    v6_0: str, review: str, lane: str, lane_norm: str, supported: bool, boundary_label: str, safety_label: str,
    human_operator: str | None,
    write_authorized: bool = False
) -> dict:
    valid = approval_gate.get("local_post_mvp_expansion_review_records_authorized") and scope_contract.get("status") == "PASS" and boundary.get("status") == "PASS"
    status = "LOCAL_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PLAN_CREATED" if valid else "BLOCKED"
    
    return {
        "status": status,
        "station_chief_v6_1_post_mvp_expansion_review_id": review_id,
        "v6_0_mvp_lock_reference_label": v6_0,
        "v6_0_mvp_lock_reference_label_normalized": normalize_label(v6_0, ""),
        "post_mvp_expansion_review_label": review,
        "post_mvp_expansion_review_label_normalized": normalize_label(review, ""),
        "requested_expansion_lane_label": lane,
        "requested_expansion_lane_label_normalized": lane_norm,
        "requested_expansion_lane_supported": supported,
        "expansion_boundary_label": boundary_label,
        "expansion_boundary_label_normalized": normalize_label(boundary_label, ""),
        "expansion_safety_posture_label": safety_label,
        "expansion_safety_posture_label_normalized": normalize_label(safety_label, ""),
        "human_operator": human_operator,
        "review_mode": "deterministic_local_post_mvp_expansion_review_packet_only",
        "packet_runtime_state": "written" if write_authorized else "not_written",
        "post_mvp_expansion_review_state": "recorded_synthetic_metadata_only" if write_authorized else "not_recorded",
        "post_mvp_expansion_execution_state": "not_executed",
        "selected_expansion_lane_execution_state": "not_executed",
        "v6_0_mvp_lock_mutation_state": "not_mutated",
        "v6_0_mvp_lock_execution_state": "not_executed",
        "local_task_candidate_execution_state": "not_executed",
        "dry_run_task_execution_state": "not_executed",
        "real_worker_result_state": "not_created",
        "live_replay_state": "not_performed",
        "production_audit_state": "not_performed",
        "rollback_state": "not_performed",
        "recovery_state": "not_performed",
        "v6_2_state": "not_created",
        "worker_runtime_state": "not_started",
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

def build_post_mvp_expansion_review_packet_payload(
    review_id: str,
    v6_0: str, review: str, lane: str, lane_norm: str, supported: bool, boundary: str, safety: str,
    human_operator: str,
    approval_token_valid: bool
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "6.1.0",
        "review_type": "station_chief_v6_1_post_mvp_expansion_review",
        "review_mode": "deterministic_local_post_mvp_expansion_review_packet_only",
        "post_mvp_expansion_execution_type": "none_metadata_review_only",
        "v6_0_mvp_lock_reference_label": v6_0,
        "post_mvp_expansion_review_label": review,
        "requested_expansion_lane_label": lane,
        "requested_expansion_lane_label_normalized": lane_norm,
        "requested_expansion_lane_supported": supported,
        "expansion_boundary_label": boundary,
        "expansion_safety_posture_label": safety,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "station_chief_v6_1_post_mvp_expansion_review_id": review_id,
        "review_message": "Station Chief v6.1 post-MVP expansion review wrote this deterministic local review packet. The expansion is recorded as metadata only. No worker was started and no task was executed.",
        "review_value": "STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_RECORDED_METADATA_ONLY",
        "next_review": "V6_2_REQUIRES_EXPLICIT_OPERATOR_INSTRUCTION",
        "local_post_mvp_expansion_review_packet_written": True,
        "station_chief_v6_1_post_mvp_expansion_review_created": True,
        "post_mvp_expansion_review_recorded": True,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
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
        "v6_2_created": False
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload

def write_station_chief_v6_1_post_mvp_expansion_review_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    out_dir = Path(output_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = safe_post_mvp_expansion_review_packet_name(packet_name)
    packet_path = (out_dir / safe_name).resolve()
    
    if not str(packet_path).startswith(str(out_dir.resolve())):
        return create_blocked_post_mvp_expansion_review_packet_write_record("packet path escape detected")
    
    content = canonical_json(payload)
    packet_path.write_text(content, encoding="utf-8")
    
    return {
        "station_chief_v6_1_post_mvp_expansion_review_write_record_version": "6.1.0",
        "write_status": "STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_PACKET_WRITTEN",
        "local_post_mvp_expansion_review_packet_written": True,
        "station_chief_v6_1_post_mvp_expansion_review_created": True,
        "post_mvp_expansion_review_recorded": True,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_2_created": False,
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

def create_blocked_post_mvp_expansion_review_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_post_mvp_expansion_review_packet_written": False,
        "station_chief_v6_1_post_mvp_expansion_review_created": False,
        "post_mvp_expansion_review_recorded": False,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_2_created": False,
        "record_name": None,
        "packet_name": None,
        "record_path": None,
        "output_directory": None,
        "files_written_count": 0,
        "files_written": []
    }

def create_post_mvp_expansion_review_packet_record(write_record: dict, payload_digest: str | None = None) -> dict:
    status = write_record.get("write_status", "BLOCKED")
    return {
        "status": status,
        "write_record": write_record,
        "payload_digest": payload_digest,
        "local_post_mvp_expansion_review_packet_written": write_record.get("local_post_mvp_expansion_review_packet_written", False),
        "station_chief_v6_1_post_mvp_expansion_review_created": write_record.get("station_chief_v6_1_post_mvp_expansion_review_created", False),
        "post_mvp_expansion_review_recorded": write_record.get("post_mvp_expansion_review_recorded", False),
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_2_created": False
    }

def create_post_mvp_expansion_review_audit_record(
    gate: dict, v6_0_c: dict, lane_c: dict, boundary_c: dict, safety_c: dict,
    scope: dict, boundary: dict, denial: dict, plan: dict, packet: dict
) -> dict:
    sections = {
        "gate": gate, "v6_0": v6_0_c, "lane": lane_c, "boundary_label": boundary_c, "safety": safety_c,
        "scope": scope, "boundary": boundary, "denial": denial, "plan": plan, "packet": packet
    }
    digests = {k: sha256_digest(v) for k, v in sections.items()}
    
    written = packet.get("local_post_mvp_expansion_review_packet_written", False)
    
    return {
        "section_digests": digests,
        "audit_status": "PASS",
        "local_post_mvp_expansion_review_packet_written": written,
        "station_chief_v6_1_post_mvp_expansion_review_created": written,
        "post_mvp_expansion_review_recorded": written,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_2_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False
    }

def create_post_mvp_expansion_review_readiness_summary(audit_record: dict) -> dict:
    ready = audit_record.get("audit_status") == "PASS"
    return {
        "status": "READY_FOR_V6_2_REVIEW_ONLY" if ready else "BLOCKED",
        "current_layer": "Station Chief v6.1 Post-MVP Expansion Review Candidate",
        "v6_1_built_only_as_metadata_review_packet": True,
        "v6_1_post_mvp_expansion_review_packet_permitted": True,
        "no_post_mvp_expansion_execution": True,
        "no_selected_expansion_lane_execution": True,
        "no_v6_0_mvp_lock_mutation": True,
        "no_v6_0_mvp_lock_execution": True,
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
        "no_v6_2_creation": True
    }

def create_station_chief_v6_2_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("status") == "READY_FOR_V6_2_REVIEW_ONLY"
    return {
        "status": "READY_FOR_V6_2_REVIEW" if ready else "BLOCKED",
        "bridge_to": "v6.2 review only",
        "no_v6_2_creation_in_v6_1": True,
        "no_selected_expansion_lane_execution_in_v6_1": True,
        "no_real_worker_start_in_v6_1": True,
        "no_real_task_execution_in_v6_1": True,
        "no_queue_creation_in_v6_1": True,
        "no_task_enqueue_in_v6_1": True,
        "no_arbitrary_task_execution_in_v6_1": True,
        "no_user_task_execution_in_v6_1": True,
        "no_worker_routing_in_v6_1": True
    }

def create_station_chief_v6_1_post_mvp_expansion_review_bundle(
    result: dict | None,
    command: str | None = None,
    v6_0_mvp_lock_reference_label: str | None = None,
    post_mvp_expansion_review_label: str | None = None,
    requested_expansion_lane_label: str | None = None,
    expansion_boundary_label: str | None = None,
    expansion_safety_posture_label: str | None = None,
    output_directory: str | None = None,
    post_mvp_expansion_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    post_mvp_expansion_review_requested: bool = False,
    write_post_mvp_expansion_review_packet: bool = False
) -> dict:
    schema = create_station_chief_v6_1_post_mvp_expansion_review_schema()
    
    v6_0 = v6_0_mvp_lock_reference_label or DEFAULT_V6_0_MVP_LOCK_REFERENCE_LABEL
    review = post_mvp_expansion_review_label or DEFAULT_POST_MVP_EXPANSION_REVIEW_LABEL
    lane = requested_expansion_lane_label or DEFAULT_REQUESTED_EXPANSION_LANE_LABEL
    lane_norm = normalize_lane_label(lane)
    supported = lane_norm in SUPPORTED_POST_MVP_EXPANSION_REVIEW_LANES
    boundary_label = expansion_boundary_label or DEFAULT_EXPANSION_BOUNDARY_LABEL
    safety_label = expansion_safety_posture_label or DEFAULT_EXPANSION_SAFETY_POSTURE_LABEL
    
    gate = create_post_mvp_expansion_review_approval_gate(
        v6_0, review, lane, boundary_label, safety_label,
        output_directory, confirmation_token, human_operator, post_mvp_expansion_review_requested
    )
    
    v6_0_c = create_v6_0_mvp_lock_reference_contract(gate)
    lane_c = create_requested_expansion_lane_contract(gate, lane)
    boundary_c = create_expansion_boundary_contract(gate)
    safety_c = create_expansion_safety_posture_contract(gate)
    
    scope = create_post_mvp_expansion_review_scope_contract(gate, v6_0_c, lane_c, boundary_c, safety_c)
    boundary = create_non_execution_post_mvp_expansion_boundary(gate, scope)
    denial = create_post_mvp_expansion_permission_denial_record(v6_0, review, lane, boundary_label, safety_label)
    
    review_id = generate_station_chief_v6_1_post_mvp_expansion_review_id(
        command or "unknown", v6_0, review, lane, boundary_label, safety_label
    )
    
    plan = create_post_mvp_expansion_review_plan_record(
        gate, scope, boundary, review_id, v6_0, review, lane, lane_norm, supported, boundary_label, safety_label, human_operator, write_post_mvp_expansion_review_packet
    )
    
    payload = None
    write_record = None
    if write_post_mvp_expansion_review_packet:
        if gate.get("local_post_mvp_expansion_review_packet_write_authorized") and plan.get("status") != "BLOCKED":
            payload = build_post_mvp_expansion_review_packet_payload(
                review_id, v6_0, review, lane, lane_norm, supported, boundary_label, safety_label, human_operator, gate.get("token_valid")
            )
            write_record = write_station_chief_v6_1_post_mvp_expansion_review_packet(output_directory, post_mvp_expansion_review_packet_name, payload)
        else:
            write_record = create_blocked_post_mvp_expansion_review_packet_write_record("gate or plan blocked")
    else:
        write_record = create_blocked_post_mvp_expansion_review_packet_write_record("Station Chief v6.1 post-MVP expansion review packet write not requested")
        
    packet = create_post_mvp_expansion_review_packet_record(write_record, payload.get("payload_digest") if payload else None)
    
    # Update boundary with actual write result
    written = packet.get("local_post_mvp_expansion_review_packet_written", False)
    boundary["local_post_mvp_expansion_review_packet_written"] = written
    boundary["station_chief_v6_1_post_mvp_expansion_review_created"] = written
    boundary["post_mvp_expansion_review_recorded"] = written
    
    audit_rec = create_post_mvp_expansion_review_audit_record(gate, v6_0_c, lane_c, boundary_c, safety_c, scope, boundary, denial, plan, packet)
    summary = create_post_mvp_expansion_review_readiness_summary(audit_rec)
    bridge = create_station_chief_v6_2_candidate_bridge(summary)
    
    return {
        "schema": schema,
        "approval_gate": gate,
        "v6_0_mvp_lock_reference_contract": v6_0_c,
        "requested_expansion_lane_contract": lane_c,
        "expansion_boundary_contract": boundary_c,
        "expansion_safety_posture_contract": safety_c,
        "post_mvp_expansion_review_scope_contract": scope,
        "non_execution_post_mvp_expansion_boundary": boundary,
        "post_mvp_expansion_permission_denial_record": denial,
        "post_mvp_expansion_review_plan_record": plan,
        "post_mvp_expansion_review_packet_record": packet,
        "post_mvp_expansion_review_audit_record": audit_rec,
        "post_mvp_expansion_review_readiness_summary": summary,
        "station_chief_v6_2_candidate_bridge": bridge,
        "post_mvp_expansion_review_packet_payload": payload,
        "local_post_mvp_expansion_review_packet_written": written,
        "station_chief_v6_1_post_mvp_expansion_review_created": written,
        "post_mvp_expansion_review_recorded": written
    }
