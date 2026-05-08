import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_MODULE_VERSION = "6.5.0"
STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_STATUS = "STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_PHASE = "Station Chief v6.5 Post-MVP Expansion Lane Non-Executing Implementation Plan Review Candidate"
STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW"

DEFAULT_V6_4_IMPLEMENTATION_PLAN_PACKET_REFERENCE_LABEL = "station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan-packet-reference"
DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL = "station-chief-v6-3-post-mvp-expansion-lane-readiness-packet-reference"
DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL = "station-chief-v6-2-post-mvp-expansion-lane-scope-packet-reference"
DEFAULT_SELECTED_EXPANSION_LANE_LABEL = "local-worker-persona-expansion-implementation-plan-review"
DEFAULT_IMPLEMENTATION_PLAN_REVIEW_LABEL = "metadata-only-non-executing-implementation-plan-review"
DEFAULT_REVIEW_FINDING_LIST_LABEL = "metadata-only-review-finding-list"
DEFAULT_REVIEW_DECISION_LABEL = "metadata-only-review-decision"
DEFAULT_REVIEW_RISK_DISPOSITION_LABEL = "metadata-only-review-risk-disposition"
DEFAULT_REVIEW_NON_EXECUTION_BOUNDARY_LABEL = "metadata-only-no-review-execution-boundary"
DEFAULT_STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_PACKET_NAME = "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_packet.json"

def canonical_json(data: object) -> str:
    return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if label is None:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '-', str(label).strip()).lower()

def safe_implementation_plan_review_packet_name(packet_name: str | None) -> str:
    if not packet_name:
        return DEFAULT_STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_PACKET_NAME
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', str(packet_name).strip())
    if not safe_name.endswith(".json"):
        safe_name += ".json"
    return safe_name

def generate_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_id(
    command: str,
    v6_4_implementation_plan_packet_reference_label: str,
    v6_3_readiness_packet_reference_label: str,
    v6_2_lane_scope_packet_reference_label: str,
    selected_expansion_lane_label: str,
    implementation_plan_review_label: str,
    review_finding_list_label: str,
    review_decision_label: str,
    review_risk_disposition_label: str,
    review_non_execution_boundary_label: str,
    runtime_version: str = "6.5.0"
) -> str:
    base = {
        "command": command,
        "v6_4_implementation_plan_packet_reference_label": v6_4_implementation_plan_packet_reference_label,
        "v6_3_readiness_packet_reference_label": v6_3_readiness_packet_reference_label,
        "v6_2_lane_scope_packet_reference_label": v6_2_lane_scope_packet_reference_label,
        "selected_expansion_lane_label": selected_expansion_lane_label,
        "implementation_plan_review_label": implementation_plan_review_label,
        "review_finding_list_label": review_finding_list_label,
        "review_decision_label": review_decision_label,
        "review_risk_disposition_label": review_risk_disposition_label,
        "review_non_execution_boundary_label": review_non_execution_boundary_label,
        "runtime_version": runtime_version,
        "timestamp_mode": "deterministic_no_wall_clock_timestamp"
    }
    return f"station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_{sha256_digest(base)[:16]}"

def create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_schema() -> dict:
    return {
        "schema_version": "6.5.0",
        "review_type": "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review",
        "required_token": STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_APPROVAL_TOKEN,
        "required_sections": [
            "implementation_plan_review_approval_gate",
            "implementation_plan_review_contracts",
            "implementation_plan_review_permission_denial_record",
            "implementation_plan_review_packet_record",
            "implementation_plan_review_audit_record",
            "implementation_plan_review_summary",
            "station_chief_v6_6_candidate_bridge"
        ],
        "required_label_fields": [
            "v6_4_implementation_plan_packet_reference_label",
            "v6_3_readiness_packet_reference_label",
            "v6_2_lane_scope_packet_reference_label",
            "selected_expansion_lane_label",
            "implementation_plan_review_label",
            "review_finding_list_label",
            "review_decision_label",
            "review_risk_disposition_label",
            "review_non_execution_boundary_label"
        ],
        "local_implementation_plan_review_packet_written": False,
        "station_chief_v6_5_implementation_plan_review_created": False,
        "post_mvp_expansion_lane_implementation_plan_review_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_plan_review_executed": False,
        "review_findings_executed": False,
        "review_decision_executed": False,
        "review_risk_disposition_executed": False,
        "implementation_rollback_executed": False,
        "v6_4_implementation_plan_packet_mutated": False,
        "v6_4_implementation_plan_packet_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_6_created": False,
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

def create_implementation_plan_review_approval_gate(
    v6_4_implementation_plan_packet_reference_label: str | None,
    v6_3_readiness_packet_reference_label: str | None,
    v6_2_lane_scope_packet_reference_label: str | None,
    selected_expansion_lane_label: str | None,
    implementation_plan_review_label: str | None,
    review_finding_list_label: str | None,
    review_decision_label: str | None,
    review_risk_disposition_label: str | None,
    review_non_execution_boundary_label: str | None,
    output_directory: str | None,
    confirmation_token: str | None,
    human_operator: str | None,
    implementation_plan_review_requested: bool
) -> dict:
    has_labels = all([
        v6_4_implementation_plan_packet_reference_label,
        v6_3_readiness_packet_reference_label,
        v6_2_lane_scope_packet_reference_label,
        selected_expansion_lane_label,
        implementation_plan_review_label,
        review_finding_list_label,
        review_decision_label,
        review_risk_disposition_label,
        review_non_execution_boundary_label
    ])
    token_valid = (confirmation_token == STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_APPROVAL_TOKEN)
    has_human = bool(human_operator)
    has_output = bool(output_directory)

    records_auth = token_valid and has_human and has_labels
    write_auth = records_auth and has_output and implementation_plan_review_requested

    return {
        "approval_token_valid": token_valid,
        "human_operator_present": has_human,
        "required_labels_present": has_labels,
        "output_directory_present": has_output,
        "implementation_plan_review_requested": implementation_plan_review_requested,
        "local_implementation_plan_review_records_authorized": records_auth,
        "local_implementation_plan_review_packet_write_authorized": write_auth,
        "selected_expansion_lane_implementation_authorized": False,
        "selected_expansion_lane_execution_authorized": False,
        "implementation_plan_execution_authorized": False,
        "implementation_step_execution_authorized": False,
        "implementation_plan_review_execution_authorized": False,
        "review_findings_execution_authorized": False,
        "review_decision_execution_authorized": False,
        "review_risk_disposition_execution_authorized": False,
        "implementation_rollback_execution_authorized": False,
        "v6_6_creation_authorized": False,
        "worker_process_start_authorized": False,
        "agent_start_authorized": False,
        "real_queue_creation_authorized": False,
        "queue_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "api_access_authorized": False,
        "network_access_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
        "full_workforce_activation_authorized": False
    }

def create_implementation_plan_review_contracts(approval_gate: dict) -> dict:
    if not approval_gate.get("local_implementation_plan_review_records_authorized"):
        return {"contracts_established": False}

    return {
        "contracts_established": True,
        "v6_4_implementation_plan_packet_reference_contract": "metadata only, review only, not mutated",
        "v6_3_readiness_packet_reference_contract": "metadata only, review only, not mutated",
        "v6_2_lane_scope_packet_reference_contract": "metadata only, review only, not mutated",
        "selected_expansion_lane_contract": "metadata only, review only, not implemented, not executed",
        "implementation_plan_review_contract": "metadata only, review only, not executed",
        "review_finding_list_contract": "metadata only, review only, not executed",
        "review_decision_contract": "metadata only, review only, not executed",
        "review_risk_disposition_contract": "metadata only, review only, not executed",
        "review_non_execution_boundary_contract": "metadata only, review only, not executed",
        "system_boundary_contract": "no worker start, no agent start, no queue creation, no queue write, no task execution, no API/network/deployment/production, no v6.6 creation"
    }

def create_implementation_plan_review_permission_denial_record(approval_gate: dict) -> dict:
    return {
        "selected_expansion_lane_implementation_denied": True,
        "selected_expansion_lane_execution_denied": True,
        "implementation_plan_execution_denied": True,
        "implementation_step_execution_denied": True,
        "implementation_plan_review_execution_beyond_metadata_packet_creation_denied": True,
        "review_finding_execution_denied": True,
        "review_decision_execution_denied": True,
        "review_risk_disposition_execution_denied": True,
        "implementation_rollback_execution_denied": True,
        "v6_4_implementation_plan_packet_mutation_denied": True,
        "v6_4_implementation_plan_packet_execution_denied": True,
        "v6_3_readiness_packet_mutation_denied": True,
        "v6_3_readiness_packet_execution_denied": True,
        "v6_2_lane_scope_packet_mutation_denied": True,
        "v6_2_lane_scope_packet_execution_denied": True,
        "v6_6_creation_denied": True,
        "worker_start_denied": True,
        "agent_start_denied": True,
        "queue_creation_denied": True,
        "queue_write_denied": True,
        "scheduler_write_denied": True,
        "cron_write_denied": True,
        "task_enqueue_denied": True,
        "task_execution_denied": True,
        "arbitrary_execution_denied": True,
        "user_task_execution_denied": True,
        "api_access_denied": True,
        "network_access_denied": True,
        "socket_access_denied": True,
        "dns_resolution_denied": True,
        "credentials_denied": True,
        "secrets_denied": True,
        "environment_reads_denied": True,
        "deployment_denied": True,
        "production_execution_denied": True,
        "full_workforce_activation_denied": True
    }

def build_implementation_plan_review_packet_payload(
    v6_4_implementation_plan_packet_reference_label: str,
    v6_3_readiness_packet_reference_label: str,
    v6_2_lane_scope_packet_reference_label: str,
    selected_expansion_lane_label: str,
    implementation_plan_review_label: str,
    review_finding_list_label: str,
    review_decision_label: str,
    review_risk_disposition_label: str,
    review_non_execution_boundary_label: str,
    human_operator: str,
    approval_token_valid: bool,
    implementation_plan_review_id: str
) -> dict:
    payload = {
        "runtime_version": "6.5.0",
        "schema_version": "6.5.0",
        "review_type": "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review",
        "review_mode": "deterministic_local_non_executing_implementation_plan_review_packet_only",
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "v6_4_implementation_plan_packet_reference_label": v6_4_implementation_plan_packet_reference_label,
        "v6_3_readiness_packet_reference_label": v6_3_readiness_packet_reference_label,
        "v6_2_lane_scope_packet_reference_label": v6_2_lane_scope_packet_reference_label,
        "selected_expansion_lane_label": selected_expansion_lane_label,
        "implementation_plan_review_label": implementation_plan_review_label,
        "review_finding_list_label": review_finding_list_label,
        "review_decision_label": review_decision_label,
        "review_risk_disposition_label": review_risk_disposition_label,
        "review_non_execution_boundary_label": review_non_execution_boundary_label,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "implementation_plan_review_id": implementation_plan_review_id,
        "implementation_plan_review_message": "Station Chief v6.5 post-MVP expansion lane non-executing implementation plan review wrote this deterministic local review packet. The selected expansion lane remains review metadata only. No implementation was performed and no task was executed.",
        "local_implementation_plan_review_packet_written": True,
        "station_chief_v6_5_implementation_plan_review_created": True,
        "post_mvp_expansion_lane_implementation_plan_review_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_plan_review_executed": False,
        "review_findings_executed": False,
        "review_decision_executed": False,
        "review_risk_disposition_executed": False,
        "implementation_rollback_executed": False,
        "v6_4_implementation_plan_packet_mutated": False,
        "v6_4_implementation_plan_packet_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_6_created": False,
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

def write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_packet(
    output_directory: str,
    packet_name: str,
    payload: dict
) -> dict:
    try:
        out_dir = Path(output_directory).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = safe_implementation_plan_review_packet_name(packet_name)
        packet_path = (out_dir / safe_name).resolve()

        if not str(packet_path).startswith(str(out_dir)):
            return create_blocked_implementation_plan_review_packet_write_record("path_escape_attempted")

        packet_path.write_text(canonical_json(payload), encoding="utf-8")

        return {
            "write_status": "STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_PACKET_WRITTEN",
            "local_implementation_plan_review_packet_written": True,
            "station_chief_v6_5_implementation_plan_review_created": True,
            "post_mvp_expansion_lane_implementation_plan_review_recorded": True,
            "record_name": safe_name,
            "record_path": str(packet_path),
            "output_directory": str(out_dir),
            "files_written_count": 1,
            "files_written": [safe_name],
            "selected_expansion_lane_implemented": False,
            "selected_expansion_lane_executed": False,
            "implementation_plan_executed": False,
            "implementation_steps_executed": False,
            "implementation_plan_review_executed": False,
            "review_findings_executed": False,
            "review_decision_executed": False,
            "review_risk_disposition_executed": False,
            "implementation_rollback_executed": False,
            "v6_6_created": False,
            "worker_process_started": False,
            "agent_started": False,
            "real_queue_created": False,
            "queue_write_performed": False,
            "scheduler_write_performed": False,
            "cron_write_performed": False,
            "task_enqueued": False,
            "task_executed": False,
            "api_call_performed": False,
            "network_access_performed": False,
            "deployment_performed": False,
            "production_execution_performed": False
        }
    except Exception as e:
        return create_blocked_implementation_plan_review_packet_write_record(f"write_error: {e}")

def create_blocked_implementation_plan_review_packet_write_record(reason: str) -> dict:
    return {
        "write_status": "BLOCKED",
        "reason": reason,
        "local_implementation_plan_review_packet_written": False,
        "files_written_count": 0,
        "files_written": [],
        "record_path": None,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_plan_review_executed": False,
        "review_findings_executed": False,
        "review_decision_executed": False,
        "review_risk_disposition_executed": False,
        "implementation_rollback_executed": False,
        "v6_6_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False
    }

def create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_bundle(
    result: dict,
    command: str,
    v6_4_implementation_plan_packet_reference_label: str | None,
    v6_3_readiness_packet_reference_label: str | None,
    v6_2_lane_scope_packet_reference_label: str | None,
    selected_expansion_lane_label: str | None,
    implementation_plan_review_label: str | None,
    review_finding_list_label: str | None,
    review_decision_label: str | None,
    review_risk_disposition_label: str | None,
    review_non_execution_boundary_label: str | None,
    output_directory: str | None,
    implementation_plan_review_packet_name: str | None,
    confirmation_token: str | None,
    human_operator: str | None,
    implementation_plan_review_requested: bool,
    write_implementation_plan_review_packet: bool
) -> dict:
    
    lbl_v6_4 = normalize_label(v6_4_implementation_plan_packet_reference_label, DEFAULT_V6_4_IMPLEMENTATION_PLAN_PACKET_REFERENCE_LABEL)
    lbl_v6_3 = normalize_label(v6_3_readiness_packet_reference_label, DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL)
    lbl_v6_2 = normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL)
    lbl_sel = normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL)
    lbl_rev = normalize_label(implementation_plan_review_label, DEFAULT_IMPLEMENTATION_PLAN_REVIEW_LABEL)
    lbl_find = normalize_label(review_finding_list_label, DEFAULT_REVIEW_FINDING_LIST_LABEL)
    lbl_dec = normalize_label(review_decision_label, DEFAULT_REVIEW_DECISION_LABEL)
    lbl_risk = normalize_label(review_risk_disposition_label, DEFAULT_REVIEW_RISK_DISPOSITION_LABEL)
    lbl_bound = normalize_label(review_non_execution_boundary_label, DEFAULT_REVIEW_NON_EXECUTION_BOUNDARY_LABEL)

    gate = create_implementation_plan_review_approval_gate(
        v6_4_implementation_plan_packet_reference_label=lbl_v6_4,
        v6_3_readiness_packet_reference_label=lbl_v6_3,
        v6_2_lane_scope_packet_reference_label=lbl_v6_2,
        selected_expansion_lane_label=lbl_sel,
        implementation_plan_review_label=lbl_rev,
        review_finding_list_label=lbl_find,
        review_decision_label=lbl_dec,
        review_risk_disposition_label=lbl_risk,
        review_non_execution_boundary_label=lbl_bound,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        implementation_plan_review_requested=implementation_plan_review_requested
    )

    contracts = create_implementation_plan_review_contracts(gate)
    denials = create_implementation_plan_review_permission_denial_record(gate)

    if gate.get("local_implementation_plan_review_packet_write_authorized") and write_implementation_plan_review_packet and output_directory:
        rev_id = generate_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_id(
            command=command,
            v6_4_implementation_plan_packet_reference_label=lbl_v6_4,
            v6_3_readiness_packet_reference_label=lbl_v6_3,
            v6_2_lane_scope_packet_reference_label=lbl_v6_2,
            selected_expansion_lane_label=lbl_sel,
            implementation_plan_review_label=lbl_rev,
            review_finding_list_label=lbl_find,
            review_decision_label=lbl_dec,
            review_risk_disposition_label=lbl_risk,
            review_non_execution_boundary_label=lbl_bound
        )
        payload = build_implementation_plan_review_packet_payload(
            v6_4_implementation_plan_packet_reference_label=lbl_v6_4,
            v6_3_readiness_packet_reference_label=lbl_v6_3,
            v6_2_lane_scope_packet_reference_label=lbl_v6_2,
            selected_expansion_lane_label=lbl_sel,
            implementation_plan_review_label=lbl_rev,
            review_finding_list_label=lbl_find,
            review_decision_label=lbl_dec,
            review_risk_disposition_label=lbl_risk,
            review_non_execution_boundary_label=lbl_bound,
            human_operator=human_operator if human_operator else "unknown",
            approval_token_valid=gate.get("approval_token_valid", False),
            implementation_plan_review_id=rev_id
        )
        write_record = write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_packet(
            output_directory=output_directory,
            packet_name=safe_implementation_plan_review_packet_name(implementation_plan_review_packet_name),
            payload=payload
        )
        payload["implementation_plan_review_packet_write_record"] = write_record
        result["station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review"] = payload
        
        result["local_implementation_plan_review_packet_written"] = write_record.get("local_implementation_plan_review_packet_written", False)
        result["station_chief_v6_5_implementation_plan_review_created"] = write_record.get("station_chief_v6_5_implementation_plan_review_created", False)
        result["post_mvp_expansion_lane_implementation_plan_review_recorded"] = write_record.get("post_mvp_expansion_lane_implementation_plan_review_recorded", False)
    else:
        blocked_record = create_blocked_implementation_plan_review_packet_write_record("write_not_requested_or_unauthorized")
        result["station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review"] = {
            "implementation_plan_review_packet_write_record": blocked_record
        }
        result["local_implementation_plan_review_packet_written"] = False
        result["station_chief_v6_5_implementation_plan_review_created"] = False
        result["post_mvp_expansion_lane_implementation_plan_review_recorded"] = False

    result["implementation_plan_review_approval_gate"] = gate
    result["implementation_plan_review_contracts"] = contracts
    result["implementation_plan_review_permission_denial_record"] = denials

    # Global denials
    result["selected_expansion_lane_implemented"] = False
    result["selected_expansion_lane_executed"] = False
    result["implementation_plan_executed"] = False
    result["implementation_steps_executed"] = False
    result["implementation_plan_review_executed"] = False
    result["review_findings_executed"] = False
    result["review_decision_executed"] = False
    result["review_risk_disposition_executed"] = False
    result["implementation_rollback_executed"] = False
    result["v6_4_implementation_plan_packet_mutated"] = False
    result["v6_4_implementation_plan_packet_executed"] = False
    result["v6_3_readiness_packet_mutated"] = False
    result["v6_3_readiness_packet_executed"] = False
    result["v6_2_lane_scope_packet_mutated"] = False
    result["v6_2_lane_scope_packet_executed"] = False
    result["v6_6_created"] = False
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
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False

    return result
