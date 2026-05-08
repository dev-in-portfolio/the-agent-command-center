#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_MODULE_VERSION = "6.2.0"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_STATUS = "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PHASE = "Station Chief v6.2 Post-MVP Expansion Lane Scope Candidate"
STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE"

DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL = "station-chief-v6-1-post-mvp-expansion-review-packet-reference"
DEFAULT_SELECTED_EXPANSION_LANE_LABEL = "local-worker-persona-expansion-scope"
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
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    if label is None or not label.strip():
        return default_label
    normalized = label.lower().strip()
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized or default_label


def normalize_scope_lane_label(label: str | None) -> str:
    if label is None or not label.strip():
        return "local_worker_persona_expansion_scope"
    normalized = label.lower().strip()
    normalized = re.sub(r"[\s-]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    normalized = normalized.strip("_")
    if not normalized or normalized not in SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS:
        return "local_worker_persona_expansion_scope"
    return normalized


def safe_lane_scope_packet_name(packet_name: str | None) -> str:
    default = DEFAULT_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_NAME
    if packet_name is None:
        return default
    if not packet_name.endswith(".json"):
        return default
    if "/" in packet_name or "\\" in packet_name:
        return default
    if packet_name in (".", ".."):
        return default
    return packet_name


def generate_station_chief_v6_2_post_mvp_expansion_lane_scope_id(
    command: str,
    v6_1_review_packet_reference_label: str,
    selected_expansion_lane_label: str,
    lane_scope_label: str,
    lane_constraint_label: str,
    lane_success_criteria_label: str,
    lane_non_execution_boundary_label: str,
    runtime_version: str = "6.2.0",
) -> str:
    prefix = "station-chief-v6-2-post-mvp-expansion-lane-scope-"
    parts = [
        prefix,
        normalize_label(v6_1_review_packet_reference_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(lane_scope_label, DEFAULT_LANE_SCOPE_LABEL),
        normalize_label(lane_constraint_label, DEFAULT_LANE_CONSTRAINT_LABEL),
        normalize_label(lane_success_criteria_label, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL),
        normalize_label(lane_non_execution_boundary_label, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL),
    ]
    digest_input = ":".join([
        command or "",
        normalize_label(v6_1_review_packet_reference_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(lane_scope_label, DEFAULT_LANE_SCOPE_LABEL),
        normalize_label(lane_constraint_label, DEFAULT_LANE_CONSTRAINT_LABEL),
        normalize_label(lane_success_criteria_label, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL),
        normalize_label(lane_non_execution_boundary_label, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL),
        runtime_version,
    ])
    parts.append(sha256_digest(digest_input)[:12])
    return "-".join(parts)


def create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema() -> dict:
    return {
        "schema_version": "6.2.0",
        "status": "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_LOCAL_PACKET_ONLY",
        "scope_type": "station_chief_v6_2_post_mvp_expansion_lane_scope",
        "lane_execution_type": "none_metadata_scope_only",
        "supported_lane_scope_labels": list(SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS),
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
            "station_chief_v6_3_candidate_bridge",
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
        "v6_3_created": False,
    }


def create_lane_scope_approval_gate(
    v6_1_review_packet_reference_label: str,
    selected_expansion_lane_label: str,
    lane_scope_label: str,
    lane_constraint_label: str,
    lane_success_criteria_label: str,
    lane_non_execution_boundary_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    lane_scope_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL_TOKEN
    labels_present = bool(
        v6_1_review_packet_reference_label
        and selected_expansion_lane_label
        and lane_scope_label
        and lane_constraint_label
        and lane_success_criteria_label
        and lane_non_execution_boundary_label
    )
    local_lane_scope_records_authorized = token_valid and bool(human_operator) and labels_present
    local_lane_scope_packet_write_authorized = (
        token_valid
        and bool(human_operator)
        and labels_present
        and bool(output_directory)
        and lane_scope_requested
    )

    if local_lane_scope_packet_write_authorized:
        gate_status = "APPROVED_FOR_ONE_LOCAL_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET"
    else:
        gate_status = "BLOCKED_PENDING_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL"

    return {
        "gate_version": "6.2.0",
        "gate_status": gate_status,
        "v6_1_review_packet_reference_label": normalize_label(v6_1_review_packet_reference_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL) if v6_1_review_packet_reference_label else None,
        "selected_expansion_lane_label": normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL) if selected_expansion_lane_label else None,
        "lane_scope_label": normalize_label(lane_scope_label, DEFAULT_LANE_SCOPE_LABEL) if lane_scope_label else None,
        "lane_constraint_label": normalize_label(lane_constraint_label, DEFAULT_LANE_CONSTRAINT_LABEL) if lane_constraint_label else None,
        "lane_success_criteria_label": normalize_label(lane_success_criteria_label, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL) if lane_success_criteria_label else None,
        "lane_non_execution_boundary_label": normalize_label(lane_non_execution_boundary_label, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL) if lane_non_execution_boundary_label else None,
        "output_directory": output_directory,
        "confirmation_token_provided": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "human_operator": human_operator,
        "lane_scope_requested": lane_scope_requested,
        "local_lane_scope_records_authorized": local_lane_scope_records_authorized,
        "local_lane_scope_packet_write_authorized": local_lane_scope_packet_write_authorized,
        "post_mvp_expansion_execution_authorized": False,
        "selected_expansion_lane_implementation_authorized": False,
        "selected_expansion_lane_execution_authorized": False,
        "v6_1_review_packet_mutation_authorized": False,
        "v6_1_review_packet_execution_authorized": False,
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
        "v6_3_creation_authorized": False,
    }


def create_v6_1_review_packet_reference_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "v6_1_review_packet_reference_label": None,
            "v6_1_review_packet_reference_label_normalized": None,
            "reference_is_metadata_only": False,
            "v6_1_review_packet_mutated": False,
            "v6_1_review_packet_executed": False,
            "v6_3_authorized": False,
        }
    raw_label = approval_gate.get("v6_1_review_packet_reference_label", DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL)
    normalized = normalize_label(raw_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL)
    return {
        "contract_created": True,
        "v6_1_review_packet_reference_label": raw_label,
        "v6_1_review_packet_reference_label_normalized": normalized,
        "reference_is_metadata_only": True,
        "reference_not_read_from_disk": True,
        "reference_not_mutated": True,
        "reference_not_executed": True,
        "reference_not_deployed": True,
        "reference_does_not_start_workers": True,
        "reference_does_not_start_agents": True,
        "reference_does_not_create_queues": True,
        "reference_does_not_authorize_v6_3": True,
        "v6_1_review_packet_mutated": False,
        "v6_1_review_packet_executed": False,
        "v6_3_authorized": False,
    }


def create_selected_expansion_lane_scope_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "selected_expansion_lane_label": None,
            "selected_expansion_lane_label_normalized": None,
            "selected_expansion_lane_supported": False,
            "selected_lane_is_metadata_only": False,
            "selected_lane_is_scoped_only": False,
            "selected_lane_is_not_implemented": False,
            "selected_lane_is_not_executed": False,
        }
    raw_label = approval_gate.get("selected_expansion_lane_label", DEFAULT_SELECTED_EXPANSION_LANE_LABEL)
    normalized = normalize_scope_lane_label(raw_label)
    supported = normalized in SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS
    return {
        "contract_created": True,
        "selected_expansion_lane_label": raw_label,
        "selected_expansion_lane_label_normalized": normalized,
        "selected_expansion_lane_supported": supported,
        "selected_lane_is_metadata_only": True,
        "selected_lane_is_scoped_only": True,
        "selected_lane_is_not_implemented": True,
        "selected_lane_is_not_executed": True,
        "selected_lane_is_not_live_runtime_mode": True,
        "selected_lane_does_not_create_files_outside_v6_2_packet": True,
        "selected_lane_does_not_start_workers": True,
        "selected_lane_does_not_create_queues": True,
        "selected_lane_does_not_call_apis": True,
        "selected_lane_does_not_access_network": True,
        "selected_lane_does_not_deploy": True,
        "selected_lane_does_not_touch_production": True,
    }


def create_lane_scope_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "lane_scope_label": None,
            "lane_scope_label_normalized": None,
            "scope_is_metadata_only": False,
            "scope_defines_future_review_boundaries_only": False,
        }
    raw_label = approval_gate.get("lane_scope_label", DEFAULT_LANE_SCOPE_LABEL)
    normalized = normalize_label(raw_label, DEFAULT_LANE_SCOPE_LABEL)
    return {
        "contract_created": True,
        "lane_scope_label": raw_label,
        "lane_scope_label_normalized": normalized,
        "scope_is_metadata_only": True,
        "scope_defines_future_review_boundaries_only": True,
        "scope_does_not_implement_code": True,
        "scope_does_not_mutate_runtime_behavior": True,
        "scope_does_not_create_workers": True,
        "scope_does_not_create_queues": True,
        "scope_does_not_execute_tasks": True,
        "scope_does_not_call_apis_network_deployment_production": True,
    }


def create_lane_constraint_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "lane_constraint_label": None,
            "lane_constraint_label_normalized": None,
            "constraint_status": "BLOCKED",
        }
    raw_label = approval_gate.get("lane_constraint_label", DEFAULT_LANE_CONSTRAINT_LABEL)
    normalized = normalize_label(raw_label, DEFAULT_LANE_CONSTRAINT_LABEL)
    all_dangerous_false = all(
        not approval_gate.get(key)
        for key in [
            "post_mvp_expansion_execution_authorized",
            "selected_expansion_lane_implementation_authorized",
            "selected_expansion_lane_execution_authorized",
            "v6_1_review_packet_mutation_authorized",
            "v6_1_review_packet_execution_authorized",
            "v6_0_mvp_lock_mutation_authorized",
            "v6_0_mvp_lock_execution_authorized",
            "worker_process_start_authorized",
            "agent_start_authorized",
            "real_queue_creation_authorized",
            "task_execution_authorized",
            "v6_3_creation_authorized",
        ]
    )
    constraint_status = "PASS" if all_dangerous_false else "BLOCKED"
    return {
        "contract_created": True,
        "lane_constraint_label": raw_label,
        "lane_constraint_label_normalized": normalized,
        "constraint_status": constraint_status,
        "metadata_only": True,
        "no_execution": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_queue_creation": True,
        "no_task_execution": True,
        "no_api_network_deployment_production": True,
        "no_v6_3_creation": True,
    }


def create_lane_success_criteria_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "lane_success_criteria_label": None,
            "lane_success_criteria_label_normalized": None,
        }
    raw_label = approval_gate.get("lane_success_criteria_label", DEFAULT_LANE_SUCCESS_CRITERIA_LABEL)
    normalized = normalize_label(raw_label, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL)
    return {
        "contract_created": True,
        "lane_success_criteria_label": raw_label,
        "lane_success_criteria_label_normalized": normalized,
        "success_criteria_is_metadata_only": True,
        "success_criteria_are_non_executing_review_criteria_only": True,
        "success_criteria_do_not_trigger_implementation": True,
        "success_criteria_do_not_approve_worker_start": True,
        "success_criteria_do_not_approve_task_execution": True,
        "success_criteria_do_not_approve_queues": True,
        "success_criteria_do_not_approve_apis_network_deployment_production": True,
    }


def create_lane_non_execution_boundary_contract(approval_gate: dict) -> dict:
    if not approval_gate.get("local_lane_scope_records_authorized"):
        return {
            "contract_created": False,
            "lane_non_execution_boundary_label": None,
            "lane_non_execution_boundary_label_normalized": None,
        }
    raw_label = approval_gate.get("lane_non_execution_boundary_label", DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL)
    normalized = normalize_label(raw_label, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL)
    return {
        "contract_created": True,
        "lane_non_execution_boundary_label": raw_label,
        "lane_non_execution_boundary_label_normalized": normalized,
        "boundary_is_metadata_only": True,
        "deny_execution_by_default": True,
        "deny_worker_start_by_default": True,
        "deny_agent_start_by_default": True,
        "deny_queue_creation_by_default": True,
        "deny_api_network_deployment_production_by_default": True,
        "deny_v6_3_creation_by_default": True,
        "future_implementation_requires_explicit_operator_instruction": True,
    }


def create_post_mvp_expansion_lane_scope_contract(
    approval_gate: dict,
    v6_1_review_packet_reference_contract: dict,
    selected_expansion_lane_scope_contract: dict,
    lane_scope_contract: dict,
    lane_constraint_contract: dict,
    lane_success_criteria_contract: dict,
    lane_non_execution_boundary_contract: dict,
) -> dict:
    gate_authorized = approval_gate.get("local_lane_scope_records_authorized", False)
    contracts_created = all(
        c.get("contract_created")
        for c in [
            v6_1_review_packet_reference_contract,
            selected_expansion_lane_scope_contract,
            lane_scope_contract,
            lane_constraint_contract,
            lane_success_criteria_contract,
            lane_non_execution_boundary_contract,
        ]
    )
    scope_pass = gate_authorized and contracts_created
    return {
        "scope_contract_version": "6.2.0",
        "scope_contract_pass": scope_pass,
        "exactly_one_v6_1_review_packet_reference": True,
        "exactly_one_selected_expansion_lane": True,
        "exactly_one_lane_scope_label": True,
        "exactly_one_lane_constraint_label": True,
        "exactly_one_lane_success_criteria_label": True,
        "exactly_one_lane_non_execution_boundary_label": True,
        "exactly_one_lane_scope_packet": True,
        "explicit_output_directory_required": True,
        "packet_json_only": True,
        "post_mvp_expansion_lane_scope_metadata_only": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_1_review_packet_mutated": False,
        "v6_1_review_packet_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "no_local_task_candidate_execution": True,
        "no_dry_run_task_execution": True,
        "no_real_worker_result": True,
        "no_live_replay": True,
        "no_production_audit": True,
        "no_rollback": True,
        "no_recovery": True,
        "no_v6_3_creation": True,
        "no_worker_start": True,
        "no_agent_start": True,
        "no_real_queue": True,
        "no_queue_write": True,
        "no_scheduler_write": True,
        "no_cron_write": True,
        "no_task_enqueue": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_live_task_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_api_network_deployment_production": True,
        "no_full_workforce_activation": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
        "scope_mode": "post_mvp_expansion_lane_scope_candidate_metadata_only",
    }


def create_non_execution_lane_scope_boundary(
    approval_gate: dict,
    post_mvp_expansion_lane_scope_contract: dict,
) -> dict:
    scope_pass = post_mvp_expansion_lane_scope_contract.get("scope_contract_pass", False)
    boundary_pass = scope_pass
    return {
        "boundary_version": "6.2.0",
        "boundary_status": "PASS" if boundary_pass else "BLOCKED",
        "station_chief_v6_2_post_mvp_expansion_lane_scope_is_local_packet_only": True,
        "scope_packet_is_not_executed": True,
        "selected_expansion_lane_is_not_implemented": True,
        "selected_expansion_lane_is_not_executed": True,
        "post_mvp_expansion_is_not_executed": True,
        "v6_1_review_packet_is_not_mutated": True,
        "v6_1_review_packet_is_not_executed": True,
        "v6_0_mvp_lock_is_not_mutated": True,
        "v6_0_mvp_lock_is_not_executed": True,
        "local_task_candidate_is_not_executed": True,
        "dry_run_task_is_not_executed": True,
        "real_worker_result_is_not_created": True,
        "live_replay_is_not_performed": True,
        "production_audit_is_not_performed": True,
        "rollback_is_not_performed": True,
        "recovery_is_not_performed": True,
        "v6_3_is_not_created": True,
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
        "local_lane_scope_packet_written_may_be_true_in_approved_write_path": True,
        "station_chief_v6_2_lane_scope_created_may_be_true_in_approved_write_path": True,
        "post_mvp_expansion_lane_scope_recorded_may_be_true_in_approved_write_path": True,
    }


def create_lane_scope_permission_denial_record(
    v6_1_review_packet_reference_label: str,
    selected_expansion_lane_label: str,
    lane_scope_label: str,
    lane_constraint_label: str,
    lane_success_criteria_label: str,
    lane_non_execution_boundary_label: str,
) -> dict:
    return {
        "denial_record_version": "6.2.0",
        "v6_1_review_packet_reference_label": normalize_label(v6_1_review_packet_reference_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL) if v6_1_review_packet_reference_label else None,
        "selected_expansion_lane_label": normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL) if selected_expansion_lane_label else None,
        "lane_scope_label": normalize_label(lane_scope_label, DEFAULT_LANE_SCOPE_LABEL) if lane_scope_label else None,
        "lane_constraint_label": normalize_label(lane_constraint_label, DEFAULT_LANE_CONSTRAINT_LABEL) if lane_constraint_label else None,
        "lane_success_criteria_label": normalize_label(lane_success_criteria_label, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL) if lane_success_criteria_label else None,
        "lane_non_execution_boundary_label": normalize_label(lane_non_execution_boundary_label, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL) if lane_non_execution_boundary_label else None,
        "selected_expansion_lane_implementation_denied": True,
        "selected_expansion_lane_execution_denied": True,
        "post_mvp_expansion_execution_denied": True,
        "v6_1_review_packet_mutation_denied": True,
        "v6_1_review_packet_execution_denied": True,
        "v6_0_mvp_lock_mutation_denied": True,
        "v6_0_mvp_lock_execution_denied": True,
        "v6_3_creation_denied": True,
        "post_mvp_implementation_file_creation_denied": True,
        "local_task_candidate_execution_denied": True,
        "dry_run_task_execution_denied": True,
        "real_dry_run_result_generation_denied": True,
        "real_worker_result_creation_denied": True,
        "live_replay_execution_denied": True,
        "production_audit_execution_denied": True,
        "rollback_execution_denied": True,
        "recovery_execution_denied": True,
        "real_task_assignment_denied": True,
        "live_task_assignment_denied": True,
        "worker_process_start_denied": True,
        "agent_start_denied": True,
        "real_queue_creation_denied": True,
        "queue_writes_denied": True,
        "scheduler_writes_denied": True,
        "cron_writes_denied": True,
        "task_enqueue_denied": True,
        "arbitrary_task_execution_denied": True,
        "user_task_execution_denied": True,
        "shell_command_execution_denied": True,
        "subprocess_execution_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "external_tool_invocation_denied": True,
        "api_access_denied": True,
        "network_access_denied": True,
        "socket_access_denied": True,
        "dns_resolution_denied": True,
        "credential_use_denied": True,
        "credential_vault_access_denied": True,
        "secret_reads_denied": True,
        "environment_reads_denied": True,
        "deployment_denied": True,
        "production_execution_denied": True,
        "production_activation_denied": True,
        "github_push_by_worker_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "mutation_of_referenced_v6_1_review_packet_denied": True,
        "execution_of_referenced_v6_1_review_packet_denied": True,
        "external_transmission_of_scope_labels_denied": True,
    }


def create_lane_scope_plan_record(
    approval_gate: dict,
    v6_1_review_packet_reference_contract: dict,
    selected_expansion_lane_scope_contract: dict,
    lane_scope_contract: dict,
    lane_constraint_contract: dict,
    lane_success_criteria_contract: dict,
    lane_non_execution_boundary_contract: dict,
    post_mvp_expansion_lane_scope_contract: dict,
    non_execution_lane_scope_boundary: dict,
) -> dict:
    gate_ok = approval_gate.get("local_lane_scope_records_authorized", False)
    contracts_ok = all(
        c.get("contract_created")
        for c in [
            v6_1_review_packet_reference_contract,
            selected_expansion_lane_scope_contract,
            lane_scope_contract,
            lane_constraint_contract,
            lane_success_criteria_contract,
            lane_non_execution_boundary_contract,
        ]
    )
    scope_ok = post_mvp_expansion_lane_scope_contract.get("scope_contract_pass", False)
    boundary_ok = non_execution_lane_scope_boundary.get("boundary_status") == "PASS"
    plan_ok = gate_ok and contracts_ok and scope_ok and boundary_ok

    if plan_ok:
        plan_status = "LOCAL_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PLAN_CREATED"
    else:
        plan_status = "BLOCKED"

    v6_1_label = approval_gate.get("v6_1_review_packet_reference_label", DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL)
    selected_lane = approval_gate.get("selected_expansion_lane_label", DEFAULT_SELECTED_EXPANSION_LANE_LABEL)
    lane_scope_raw = approval_gate.get("lane_scope_label", DEFAULT_LANE_SCOPE_LABEL)
    constraint_raw = approval_gate.get("lane_constraint_label", DEFAULT_LANE_CONSTRAINT_LABEL)
    success_raw = approval_gate.get("lane_success_criteria_label", DEFAULT_LANE_SUCCESS_CRITERIA_LABEL)
    boundary_raw = approval_gate.get("lane_non_execution_boundary_label", DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL)
    selected_lane_normalized = normalize_scope_lane_label(selected_lane)
    selected_supported = selected_lane_normalized in SUPPORTED_POST_MVP_EXPANSION_LANE_SCOPE_LABELS

    return {
        "plan_version": "6.2.0",
        "plan_status": plan_status,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_id": generate_station_chief_v6_2_post_mvp_expansion_lane_scope_id(
            command="",
            v6_1_review_packet_reference_label=v6_1_label,
            selected_expansion_lane_label=selected_lane,
            lane_scope_label=lane_scope_raw,
            lane_constraint_label=constraint_raw,
            lane_success_criteria_label=success_raw,
            lane_non_execution_boundary_label=boundary_raw,
        ),
        "v6_1_review_packet_reference_label": v6_1_label,
        "v6_1_review_packet_reference_label_normalized": normalize_label(v6_1_label, DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL),
        "selected_expansion_lane_label": selected_lane,
        "selected_expansion_lane_label_normalized": selected_lane_normalized,
        "selected_expansion_lane_supported": selected_supported,
        "lane_scope_label": lane_scope_raw,
        "lane_scope_label_normalized": normalize_label(lane_scope_raw, DEFAULT_LANE_SCOPE_LABEL),
        "lane_constraint_label": constraint_raw,
        "lane_constraint_label_normalized": normalize_label(constraint_raw, DEFAULT_LANE_CONSTRAINT_LABEL),
        "lane_success_criteria_label": success_raw,
        "lane_success_criteria_label_normalized": normalize_label(success_raw, DEFAULT_LANE_SUCCESS_CRITERIA_LABEL),
        "lane_non_execution_boundary_label": boundary_raw,
        "lane_non_execution_boundary_label_normalized": normalize_label(boundary_raw, DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL),
        "human_operator": approval_gate.get("human_operator"),
        "scope_mode": "deterministic_local_post_mvp_expansion_lane_scope_packet_only",
        "packet_runtime_state": "not_written",
        "post_mvp_expansion_lane_scope_state": "recorded_synthetic_metadata_only" if approval_gate.get("local_lane_scope_packet_write_authorized") else "not_recorded",
        "selected_expansion_lane_implementation_state": "not_implemented",
        "selected_expansion_lane_execution_state": "not_executed",
        "post_mvp_expansion_execution_state": "not_executed",
        "v6_1_review_packet_mutation_state": "not_mutated",
        "v6_1_review_packet_execution_state": "not_executed",
        "v6_0_mvp_lock_mutation_state": "not_mutated",
        "v6_0_mvp_lock_execution_state": "not_executed",
        "local_task_candidate_execution_state": "not_executed",
        "dry_run_task_execution_state": "not_executed",
        "real_worker_result_state": "not_created",
        "live_replay_state": "not_performed",
        "production_audit_state": "not_performed",
        "rollback_state": "not_performed",
        "recovery_state": "not_performed",
        "v6_3_state": "not_created",
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
        "network_access_performed": False,
    }


def build_lane_scope_packet_payload(
    approval_gate: dict,
    v6_1_review_packet_reference_contract: dict,
    selected_expansion_lane_scope_contract: dict,
    lane_scope_contract: dict,
    lane_constraint_contract: dict,
    lane_success_criteria_contract: dict,
    lane_non_execution_boundary_contract: dict,
    post_mvp_expansion_lane_scope_contract: dict,
    lane_scope_plan_record: dict,
) -> dict:
    payload = {
        "schema_version": "6.2.0",
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "6.2.0",
        "scope_type": "station_chief_v6_2_post_mvp_expansion_lane_scope",
        "scope_mode": "deterministic_local_post_mvp_expansion_lane_scope_packet_only",
        "lane_execution_type": "none_metadata_scope_only",
        "v6_1_review_packet_reference_label": approval_gate.get("v6_1_review_packet_reference_label"),
        "selected_expansion_lane_label": approval_gate.get("selected_expansion_lane_label"),
        "selected_expansion_lane_label_normalized": selected_expansion_lane_scope_contract.get("selected_expansion_lane_label_normalized"),
        "selected_expansion_lane_supported": selected_expansion_lane_scope_contract.get("selected_expansion_lane_supported"),
        "lane_scope_label": approval_gate.get("lane_scope_label"),
        "lane_constraint_label": approval_gate.get("lane_constraint_label"),
        "lane_success_criteria_label": approval_gate.get("lane_success_criteria_label"),
        "lane_non_execution_boundary_label": approval_gate.get("lane_non_execution_boundary_label"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("confirmation_token_valid"),
        "station_chief_v6_2_post_mvp_expansion_lane_scope_id": lane_scope_plan_record.get("station_chief_v6_2_post_mvp_expansion_lane_scope_id"),
        "scope_message": "Station Chief v6.2 post-MVP expansion lane scope wrote this deterministic local scope packet. The selected expansion lane is recorded as metadata only. No worker was started and no task was executed.",
        "scope_value": "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_RECORDED_METADATA_ONLY",
        "next_review": "V6_3_REQUIRES_EXPLICIT_OPERATOR_INSTRUCTION",
        "local_lane_scope_packet_written": True,
        "station_chief_v6_2_lane_scope_created": True,
        "post_mvp_expansion_lane_scope_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
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
        "v6_3_created": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_station_chief_v6_2_post_mvp_expansion_lane_scope_packet(
    output_directory: str,
    packet_name: str,
    payload: dict,
) -> dict:
    safe_name = safe_lane_scope_packet_name(packet_name)
    out_dir = Path(output_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = out_dir / safe_name
    packet_path.write_text(canonical_json(payload), encoding="utf-8")

    return {
        "station_chief_v6_2_post_mvp_expansion_lane_scope_write_record_version": "6.2.0",
        "write_status": "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_WRITTEN",
        "local_lane_scope_packet_written": True,
        "station_chief_v6_2_lane_scope_created": True,
        "post_mvp_expansion_lane_scope_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
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
        "v6_3_created": False,
        "record_name": safe_name,
        "packet_name": safe_name,
        "record_path": str(packet_path),
        "output_directory": str(out_dir),
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
        "production_execution_performed": False,
    }


def create_blocked_lane_scope_packet_write_record(reason: str) -> dict:
    return {
        "station_chief_v6_2_post_mvp_expansion_lane_scope_write_record_version": "6.2.0",
        "write_status": "BLOCKED",
        "reason": reason,
        "local_lane_scope_packet_written": False,
        "station_chief_v6_2_lane_scope_created": False,
        "post_mvp_expansion_lane_scope_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
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
        "v6_3_created": False,
        "record_name": None,
        "packet_name": None,
        "record_path": None,
        "output_directory": None,
        "files_written_count": 0,
        "files_written": [],
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
    }


def create_lane_scope_packet_record(
    write_record: dict,
    payload: dict | None = None,
) -> dict:
    written = write_record.get("local_lane_scope_packet_written", False)
    packet_status = "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_WRITTEN" if written else "BLOCKED"
    return {
        "packet_record_version": "6.2.0",
        "packet_status": packet_status,
        "write_record": write_record,
        "payload_digest": payload.get("payload_digest") if payload else None,
        "local_lane_scope_packet_written": write_record.get("local_lane_scope_packet_written", False),
        "station_chief_v6_2_lane_scope_created": write_record.get("station_chief_v6_2_lane_scope_created", False),
        "post_mvp_expansion_lane_scope_recorded": write_record.get("post_mvp_expansion_lane_scope_recorded", False),
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
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
        "v6_3_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
    }


def create_lane_scope_audit_record(
    lane_scope_approval_gate: dict,
    v6_1_review_packet_reference_contract: dict,
    selected_expansion_lane_scope_contract: dict,
    lane_scope_contract: dict,
    lane_constraint_contract: dict,
    lane_success_criteria_contract: dict,
    lane_non_execution_boundary_contract: dict,
    post_mvp_expansion_lane_scope_contract: dict,
    non_execution_lane_scope_boundary: dict,
    lane_scope_permission_denial_record: dict,
    lane_scope_plan_record: dict,
    lane_scope_packet_record: dict,
) -> dict:
    def _digest(record: dict) -> str:
        return sha256_digest(record)

    audit_pass = True
    dangerous_keys = [
        ("selected_expansion_lane_implemented", lane_scope_packet_record),
        ("selected_expansion_lane_executed", lane_scope_packet_record),
        ("post_mvp_expansion_executed", lane_scope_packet_record),
        ("v6_1_review_packet_mutated", lane_scope_packet_record),
        ("v6_1_review_packet_executed", lane_scope_packet_record),
        ("v6_0_mvp_lock_mutated", lane_scope_packet_record),
        ("v6_0_mvp_lock_executed", lane_scope_packet_record),
        ("local_task_candidate_executed", lane_scope_packet_record),
        ("dry_run_task_executed", lane_scope_packet_record),
        ("real_worker_result_created", lane_scope_packet_record),
        ("live_replay_performed", lane_scope_packet_record),
        ("production_audit_performed", lane_scope_packet_record),
        ("rollback_performed", lane_scope_packet_record),
        ("recovery_performed", lane_scope_packet_record),
        ("v6_3_created", lane_scope_packet_record),
        ("worker_process_started", lane_scope_packet_record),
        ("agent_started", lane_scope_packet_record),
        ("task_executed", lane_scope_packet_record),
        ("arbitrary_task_execution_performed", lane_scope_packet_record),
        ("user_task_execution_performed", lane_scope_packet_record),
    ]
    for key, record in dangerous_keys:
        if record.get(key) is True:
            audit_pass = False

    audit_status = "PASS" if audit_pass else "BLOCKED"

    return {
        "audit_version": "6.2.0",
        "audit_status": audit_status,
        "section_digests": {
            "lane_scope_approval_gate": _digest(lane_scope_approval_gate),
            "v6_1_review_packet_reference_contract": _digest(v6_1_review_packet_reference_contract),
            "selected_expansion_lane_scope_contract": _digest(selected_expansion_lane_scope_contract),
            "lane_scope_contract": _digest(lane_scope_contract),
            "lane_constraint_contract": _digest(lane_constraint_contract),
            "lane_success_criteria_contract": _digest(lane_success_criteria_contract),
            "lane_non_execution_boundary_contract": _digest(lane_non_execution_boundary_contract),
            "post_mvp_expansion_lane_scope_contract": _digest(post_mvp_expansion_lane_scope_contract),
            "non_execution_lane_scope_boundary": _digest(non_execution_lane_scope_boundary),
            "lane_scope_permission_denial_record": _digest(lane_scope_permission_denial_record),
            "lane_scope_plan_record": _digest(lane_scope_plan_record),
            "lane_scope_packet_record": _digest(lane_scope_packet_record),
        },
        "local_lane_scope_packet_written": lane_scope_packet_record.get("local_lane_scope_packet_written", False),
        "station_chief_v6_2_lane_scope_created": lane_scope_packet_record.get("station_chief_v6_2_lane_scope_created", False),
        "post_mvp_expansion_lane_scope_recorded": lane_scope_packet_record.get("post_mvp_expansion_lane_scope_recorded", False),
    }


def create_lane_scope_readiness_summary(lane_scope_audit_record: dict) -> dict:
    audit_pass = lane_scope_audit_record.get("audit_status") == "PASS"
    ready = audit_pass
    readiness_status = "READY_FOR_V6_3_REVIEW_ONLY" if ready else "BLOCKED"

    return {
        "readiness_version": "6.2.0",
        "readiness_status": readiness_status,
        "current_layer": "Station Chief v6.2 Post-MVP Expansion Lane Scope Candidate",
        "v6_2_built_only_as_metadata_scope_packet": True,
        "one_deterministic_lane_scope_packet_permitted_under_v6_2_token": True,
        "no_selected_expansion_lane_implementation": True,
        "no_selected_expansion_lane_execution": True,
        "no_post_mvp_expansion_execution": True,
        "no_v6_1_review_packet_mutation": True,
        "no_v6_1_review_packet_execution": True,
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
        "no_v6_3_creation": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_station_chief_v6_3_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_V6_3_REVIEW_ONLY"
    return {
        "bridge_version": "6.2.0",
        "bridge_to_v6_3_review_only": ready,
        "v6_3_not_created_in_v6_2": True,
        "no_selected_expansion_lane_implementation_in_v6_2": True,
        "no_selected_expansion_lane_execution_in_v6_2": True,
        "no_real_worker_start_in_v6_2": True,
        "no_real_task_execution_in_v6_2": True,
        "no_queue_creation_in_v6_2": True,
        "no_task_enqueue_in_v6_2": True,
        "no_arbitrary_task_execution_in_v6_2": True,
        "no_user_task_execution_in_v6_2": True,
        "no_worker_routing_in_v6_2": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_station_chief_v6_2_post_mvp_expansion_lane_scope_bundle(
    result: dict | None,
    command: str | None = None,
    v6_1_review_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    lane_scope_label: str | None = None,
    lane_constraint_label: str | None = None,
    lane_success_criteria_label: str | None = None,
    lane_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    lane_scope_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    lane_scope_requested: bool = False,
    write_lane_scope_packet: bool = False,
) -> dict:
    schema = create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema()

    approval_gate = create_lane_scope_approval_gate(
        v6_1_review_packet_reference_label=v6_1_review_packet_reference_label or DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        lane_scope_label=lane_scope_label or DEFAULT_LANE_SCOPE_LABEL,
        lane_constraint_label=lane_constraint_label or DEFAULT_LANE_CONSTRAINT_LABEL,
        lane_success_criteria_label=lane_success_criteria_label or DEFAULT_LANE_SUCCESS_CRITERIA_LABEL,
        lane_non_execution_boundary_label=lane_non_execution_boundary_label or DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        lane_scope_requested=lane_scope_requested,
    )

    v6_1_contract = create_v6_1_review_packet_reference_contract(approval_gate)
    selected_lane_contract = create_selected_expansion_lane_scope_contract(approval_gate)
    lane_scope = create_lane_scope_contract(approval_gate)
    lane_constraint = create_lane_constraint_contract(approval_gate)
    lane_success = create_lane_success_criteria_contract(approval_gate)
    lane_boundary = create_lane_non_execution_boundary_contract(approval_gate)

    scope_contract = create_post_mvp_expansion_lane_scope_contract(
        approval_gate,
        v6_1_contract,
        selected_lane_contract,
        lane_scope,
        lane_constraint,
        lane_success,
        lane_boundary,
    )

    non_exec_boundary = create_non_execution_lane_scope_boundary(approval_gate, scope_contract)

    denial_record = create_lane_scope_permission_denial_record(
        v6_1_review_packet_reference_label or DEFAULT_V6_1_REVIEW_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        lane_scope_label or DEFAULT_LANE_SCOPE_LABEL,
        lane_constraint_label or DEFAULT_LANE_CONSTRAINT_LABEL,
        lane_success_criteria_label or DEFAULT_LANE_SUCCESS_CRITERIA_LABEL,
        lane_non_execution_boundary_label or DEFAULT_LANE_NON_EXECUTION_BOUNDARY_LABEL,
    )

    plan_record = create_lane_scope_plan_record(
        approval_gate,
        v6_1_contract,
        selected_lane_contract,
        lane_scope,
        lane_constraint,
        lane_success,
        lane_boundary,
        scope_contract,
        non_exec_boundary,
    )

    payload = None
    write_record = None

    if write_lane_scope_packet:
        write_authorized = approval_gate.get("local_lane_scope_packet_write_authorized", False)
        plan_ok = plan_record.get("plan_status") == "LOCAL_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PLAN_CREATED"
        if write_authorized and plan_ok:
            packet_name = safe_lane_scope_packet_name(lane_scope_packet_name or DEFAULT_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_PACKET_NAME)
            payload = build_lane_scope_packet_payload(
                approval_gate,
                v6_1_contract,
                selected_lane_contract,
                lane_scope,
                lane_constraint,
                lane_success,
                lane_boundary,
                scope_contract,
                plan_record,
            )
            write_record = write_station_chief_v6_2_post_mvp_expansion_lane_scope_packet(
                output_directory=output_directory or "/tmp",
                packet_name=packet_name,
                payload=payload,
            )
        else:
            write_record = create_blocked_lane_scope_packet_write_record(
                "Station Chief v6.2 post-MVP expansion lane scope packet write not authorized or plan blocked"
            )
    else:
        write_record = create_blocked_lane_scope_packet_write_record(
            "Station Chief v6.2 post-MVP expansion lane scope packet write not requested"
        )

    packet_record = create_lane_scope_packet_record(write_record, payload)

    audit_record = create_lane_scope_audit_record(
        approval_gate,
        v6_1_contract,
        selected_lane_contract,
        lane_scope,
        lane_constraint,
        lane_success,
        lane_boundary,
        scope_contract,
        non_exec_boundary,
        denial_record,
        plan_record,
        packet_record,
    )

    summary = create_lane_scope_readiness_summary(audit_record)
    v6_3_bridge = create_station_chief_v6_3_candidate_bridge(summary)

    top_level = {
        "schema": schema,
        "approval_gate": approval_gate,
        "v6_1_review_packet_reference_contract": v6_1_contract,
        "selected_expansion_lane_scope_contract": selected_lane_contract,
        "lane_scope_contract": lane_scope,
        "lane_constraint_contract": lane_constraint,
        "lane_success_criteria_contract": lane_success,
        "lane_non_execution_boundary_contract": lane_boundary,
        "post_mvp_expansion_lane_scope_contract": scope_contract,
        "non_execution_lane_scope_boundary": non_exec_boundary,
        "lane_scope_permission_denial_record": denial_record,
        "lane_scope_plan_record": plan_record,
        "lane_scope_packet_record": packet_record,
        "lane_scope_audit_record": audit_record,
        "lane_scope_readiness_summary": summary,
        "station_chief_v6_3_candidate_bridge": v6_3_bridge,
        "lane_scope_packet_payload": payload,
        "lane_scope_packet_write_record": write_record,
        "local_lane_scope_packet_written": write_record.get("local_lane_scope_packet_written", False) if write_record else False,
        "station_chief_v6_2_lane_scope_created": write_record.get("station_chief_v6_2_lane_scope_created", False) if write_record else False,
        "post_mvp_expansion_lane_scope_recorded": write_record.get("post_mvp_expansion_lane_scope_recorded", False) if write_record else False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
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
        "v6_3_created": False,
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
    return top_level
