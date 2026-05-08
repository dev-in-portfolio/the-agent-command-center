import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_MODULE_VERSION = "6.2.0"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_STATUS = "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PHASE = "Station Chief v6.2 Post-MVP Expansion Lane Scope Candidate"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE"
DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL = "station-chief-v6-1-post-mvp-expansion-review-packet-reference"
DEFAULT_SELECTED_EXPANSION_LANE_LABEL = "local_worker_persona_expansion_scope"
DEFAULT_LANE_SCOPE_LABEL = "station-chief-v6-2-lane-scope-reference"
DEFAULT_LANE_CONSTRAINT_LABEL = "metadata-only-expansion-lane-constraints"
DEFAULT_LANE_SUCCESS_CRITERIA_LABEL = "metadata-only-expansion-lane-success-criteria"
DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL = "metadata-only-no-lane-execution-boundary"
DEFAULT_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_NAME = "station_chief_v6_2_post_mvp_expansion_lane_scope_packet.json"

SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS = [
    "local_worker_persona_expansion_scope",
    "multi_sandbox_worker_scope",
    "richer_task_packet_scope",
    "local_queue_simulation_scope",
    "local_execution_replay_scope",
    "dashboard_surface_scope",
    "validator_hardening_scope",
    "controlled_real_local_worker_execution_scope",
    "optional_future_api_tool_integration_scope",
]

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2)

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode()).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    res = re.sub(r'[^a-zA-Z0-9]', '-', label.lower())
    res = re.sub(r'-+', '-', res).strip('-')
    return res if res else default_label

def normalize_scope_lane_label(label: str | None) -> str:
    if not label:
        return DEFAULT_SELECTED_EXPANSION_LANE_LABEL
    label = label.lower().replace('-', '_').replace(' ', '_')
    label = re.sub(r'[^a-z0-9_]', '', label)
    if label not in SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS:
        return DEFAULT_SELECTED_EXPANSION_LANE_LABEL
    return label

def safe_lane_scope_packet_name(packet_name: str | None) -> str:
    if not packet_name or not packet_name.endswith('.json') or '/' in packet_name or '\\' in packet_name or packet_name in ('.', '..'):
        return DEFAULT_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_NAME
    return packet_name

def generate_station_chief_v6_2_post_mvp_expansion_lane_scope_id(
    command: str,
    v6_1_review_packet_reference_label: str,
    selected_expansion_lane_label: str,
    lane_scope_label: str,
    lane_constraint_label: str,
    lane_success_criteria_label: str,
    lane_non_execution_boundary_label: str,
    runtime_version: str = "6.2.0"
) -> str:
    data = {
        "c": command,
        "v61": v6_1_review_packet_reference_label,
        "sel": selected_expansion_lane_label,
        "sc": lane_scope_label,
        "lc": lane_constraint_label,
        "ls": lane_success_criteria_label,
        "lb": lane_non_execution_boundary_label,
        "rv": runtime_version
    }
    digest = sha256_digest(data)
    return f"station-chief-v6-2-post-mvp-expansion-lane-scope-{normalize_label(v6_1_review_packet_reference_label, '')}-{normalize_label(selected_expansion_lane_label, '')}-{normalize_label(lane_scope_label, '')}-{normalize_label(lane_constraint_label, '')}-{normalize_label(lane_success_criteria_label, '')}-{normalize_label(lane_non_execution_boundary_label, '')}-{digest[:12]}"

def create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema() -> dict:
    return {
        "schema_version": "6.2.0",
        "status": STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_STATUS,
        "scope_type": "station_chief_v6_2_post_mvp_expansion_lane_scope",
        "lane_execution_type": "none_metadata_scope_only",
        "supported_lane_scope_labels": SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS,
        "required_sections": [
            "lane_scope_approval_gate",
            "v6_1_review_packet_reference_contract",
            "selected_expansion_lane_scope_contract",
            "lane_scope_contract",
            "lane_constraint_contract",
            "lane_success_criteria_contract",
            "lane_non_execution_boundary_contract",
            "post_mvp_expansion_lane_scope_contract",
            "non_execution_lane_scope_boundary",
            "lane_scope_permission_denial_record",
            "lane_scope_plan_record",
            "lane_scope_packet_record",
            "lane_scope_audit_record",
            "lane_scope_readiness_summary",
            "station_chief_v6_3_candidate_bridge"
        ],
        "required_token": STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "locked_175_family_baseline_preserved": True,
        "local_lane_scope_packet_written": False,
        "station_chief_v6_2_lane_scope_created": False,
        "post_mvp_expansion_lane_scope_recorded": False,
        "post_mvp_expansion_executed": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "v6_1_review_packet_mutated": False,
        "v6_1_review_packet_executed": False,
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
        "v6_3_created": False
    }

# ... (the rest of the implementation would go here)
