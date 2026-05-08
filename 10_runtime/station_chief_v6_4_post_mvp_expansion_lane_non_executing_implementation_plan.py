#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_MODULE_VERSION = "6.4.0"
STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_STATUS = "STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PHASE = "Station Chief v6.4 Post-MVP Expansion Lane Non-Executing Implementation Plan Candidate"
STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN"

DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL = "station-chief-v6-3-post-mvp-expansion-lane-readiness-packet-reference"
DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL = "station-chief-v6-2-post-mvp-expansion-lane-scope-packet-reference"
DEFAULT_SELECTED_EXPANSION_LANE_LABEL = "local-worker-persona-expansion-implementation-plan"
DEFAULT_IMPLEMENTATION_PLAN_LABEL = "metadata-only-non-executing-implementation-plan"
DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL = "metadata-only-implementation-step-list"
DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL = "metadata-only-implementation-risk-register"
DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL = "metadata-only-implementation-rollback-plan"
DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL = "metadata-only-no-implementation-execution-boundary"
DEFAULT_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PACKET_NAME = "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_packet.json"


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


def safe_implementation_plan_packet_name(packet_name: str | None) -> str:
    default = DEFAULT_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PACKET_NAME
    if packet_name is None:
        return default
    if not packet_name.endswith(".json"):
        return default
    if "/" in packet_name or "\\" in packet_name:
        return default
    if packet_name in (".", ".."):
        return default
    return packet_name


def generate_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_id(
    command: str,
    v6_3_readiness_packet_reference_label: str,
    v6_2_lane_scope_packet_reference_label: str,
    selected_expansion_lane_label: str,
    implementation_plan_label: str,
    implementation_step_list_label: str,
    implementation_risk_register_label: str,
    implementation_rollback_plan_label: str,
    implementation_non_execution_boundary_label: str,
    runtime_version: str = "6.4.0",
) -> str:
    prefix = "station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan-"
    parts = [
        prefix,
        normalize_label(v6_3_readiness_packet_reference_label, DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL),
        normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(implementation_plan_label, DEFAULT_IMPLEMENTATION_PLAN_LABEL),
        normalize_label(implementation_step_list_label, DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL),
        normalize_label(implementation_risk_register_label, DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL),
        normalize_label(implementation_rollback_plan_label, DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL),
        normalize_label(implementation_non_execution_boundary_label, DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL),
    ]
    digest_input = ":".join([
        command or "",
        normalize_label(v6_3_readiness_packet_reference_label, DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL),
        normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(implementation_plan_label, DEFAULT_IMPLEMENTATION_PLAN_LABEL),
        normalize_label(implementation_step_list_label, DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL),
        normalize_label(implementation_risk_register_label, DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL),
        normalize_label(implementation_rollback_plan_label, DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL),
        normalize_label(implementation_non_execution_boundary_label, DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL),
        runtime_version,
    ])
    parts.append(sha256_digest(digest_input)[:12])
    return "-".join(parts)


def create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema() -> dict:
    return {
        "schema_version": "6.4.0",
        "status": "STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_LOCAL_PACKET_ONLY",
        "plan_type": "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan",
        "plan_execution_type": "none_implementation_plan_metadata_only",
        "required_token": STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "locked_175_family_baseline_preserved": True,
        "required_sections": [
            "implementation_plan_approval_gate",
            "implementation_plan_contracts",
            "implementation_plan_permission_denial_record",
            "implementation_plan_packet_record",
            "implementation_plan_audit_record",
            "implementation_plan_summary",
            "station_chief_v6_5_candidate_bridge",
        ],
        "required_labels": [
            "v6_3_readiness_packet_reference_label",
            "v6_2_lane_scope_packet_reference_label",
            "selected_expansion_lane_label",
            "implementation_plan_label",
            "implementation_step_list_label",
            "implementation_risk_register_label",
            "implementation_rollback_plan_label",
            "implementation_non_execution_boundary_label",
        ],
        "local_implementation_plan_packet_written": False,
        "station_chief_v6_4_implementation_plan_created": False,
        "post_mvp_expansion_lane_implementation_plan_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_rollback_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_5_created": False,
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


def create_implementation_plan_approval_gate(
    v6_3_readiness_packet_reference_label: str | None = None,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    implementation_plan_label: str | None = None,
    implementation_step_list_label: str | None = None,
    implementation_risk_register_label: str | None = None,
    implementation_rollback_plan_label: str | None = None,
    implementation_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    implementation_plan_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN
    labels_present = bool(
        v6_3_readiness_packet_reference_label
        and v6_2_lane_scope_packet_reference_label
        and selected_expansion_lane_label
        and implementation_plan_label
        and implementation_step_list_label
        and implementation_risk_register_label
        and implementation_rollback_plan_label
        and implementation_non_execution_boundary_label
    )
    local_implementation_plan_records_authorized = token_valid and bool(human_operator) and labels_present
    local_implementation_plan_packet_write_authorized = (
        token_valid
        and bool(human_operator)
        and labels_present
        and bool(output_directory)
        and implementation_plan_requested
    )

    if local_implementation_plan_packet_write_authorized:
        gate_status = "APPROVED_FOR_ONE_LOCAL_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PACKET"
    else:
        gate_status = "BLOCKED_PENDING_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL"

    return {
        "gate_version": "6.4.0",
        "gate_status": gate_status,
        "v6_3_readiness_packet_reference_label": normalize_label(v6_3_readiness_packet_reference_label, DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL) if v6_3_readiness_packet_reference_label else None,
        "v6_2_lane_scope_packet_reference_label": normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL) if v6_2_lane_scope_packet_reference_label else None,
        "selected_expansion_lane_label": normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL) if selected_expansion_lane_label else None,
        "implementation_plan_label": normalize_label(implementation_plan_label, DEFAULT_IMPLEMENTATION_PLAN_LABEL) if implementation_plan_label else None,
        "implementation_step_list_label": normalize_label(implementation_step_list_label, DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL) if implementation_step_list_label else None,
        "implementation_risk_register_label": normalize_label(implementation_risk_register_label, DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL) if implementation_risk_register_label else None,
        "implementation_rollback_plan_label": normalize_label(implementation_rollback_plan_label, DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL) if implementation_rollback_plan_label else None,
        "implementation_non_execution_boundary_label": normalize_label(implementation_non_execution_boundary_label, DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL) if implementation_non_execution_boundary_label else None,
        "output_directory": output_directory,
        "confirmation_token_provided": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "human_operator": human_operator,
        "implementation_plan_requested": implementation_plan_requested,
        "local_implementation_plan_records_authorized": local_implementation_plan_records_authorized,
        "local_implementation_plan_packet_write_authorized": local_implementation_plan_packet_write_authorized,
        "selected_expansion_lane_implementation_authorized": False,
        "selected_expansion_lane_execution_authorized": False,
        "implementation_plan_execution_authorized": False,
        "implementation_step_execution_authorized": False,
        "implementation_rollback_execution_authorized": False,
        "v6_3_readiness_packet_mutation_authorized": False,
        "v6_3_readiness_packet_execution_authorized": False,
        "v6_2_lane_scope_packet_mutation_authorized": False,
        "v6_2_lane_scope_packet_execution_authorized": False,
        "v6_5_creation_authorized": False,
        "worker_process_start_authorized": False,
        "agent_start_authorized": False,
        "real_queue_creation_authorized": False,
        "queue_write_authorized": False,
        "scheduler_write_authorized": False,
        "cron_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "arbitrary_task_execution_authorized": False,
        "user_task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
        "full_workforce_activation_authorized": False,
    }


def create_implementation_plan_contracts(approval_gate: dict) -> dict:
    if not approval_gate.get("local_implementation_plan_records_authorized"):
        return {
            "v6_3_readiness_packet_reference_contract": {"contract_created": False},
            "v6_2_lane_scope_packet_reference_contract": {"contract_created": False},
            "selected_expansion_lane_contract": {"contract_created": False},
            "implementation_plan_contract": {"contract_created": False},
            "implementation_step_list_contract": {"contract_created": False},
            "implementation_risk_register_contract": {"contract_created": False},
            "implementation_rollback_plan_contract": {"contract_created": False},
            "implementation_non_execution_boundary_contract": {"contract_created": False},
        }

    def make_contract(label_key: str, default: str) -> dict:
        raw = approval_gate.get(label_key, default)
        normalized = normalize_label(raw, default)
        return {
            "contract_created": True,
            "label": raw,
            "label_normalized": normalized,
            "metadata_only": True,
            "not_implemented": True,
            "not_executed": True,
            "not_mutated": True,
            "no_worker_start": True,
            "no_agent_start": True,
            "no_queue_creation": True,
            "no_queue_write": True,
            "no_task_execution": True,
            "no_api_network_deployment_production": True,
            "no_v6_5_creation": True,
        }

    return {
        "v6_3_readiness_packet_reference_contract": make_contract("v6_3_readiness_packet_reference_label", DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL),
        "v6_2_lane_scope_packet_reference_contract": make_contract("v6_2_lane_scope_packet_reference_label", DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL),
        "selected_expansion_lane_contract": make_contract("selected_expansion_lane_label", DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        "implementation_plan_contract": make_contract("implementation_plan_label", DEFAULT_IMPLEMENTATION_PLAN_LABEL),
        "implementation_step_list_contract": make_contract("implementation_step_list_label", DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL),
        "implementation_risk_register_contract": make_contract("implementation_risk_register_label", DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL),
        "implementation_rollback_plan_contract": make_contract("implementation_rollback_plan_label", DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL),
        "implementation_non_execution_boundary_contract": make_contract("implementation_non_execution_boundary_label", DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL),
    }


def create_implementation_plan_permission_denial_record(approval_gate: dict) -> dict:
    denials = {}
    for key in [
        "selected_expansion_lane_implementation",
        "selected_expansion_lane_execution",
        "implementation_plan_execution",
        "implementation_step_execution",
        "implementation_rollback_execution",
        "v6_3_readiness_packet_mutation",
        "v6_3_readiness_packet_execution",
        "v6_2_lane_scope_packet_mutation",
        "v6_2_lane_scope_packet_execution",
        "v6_5_creation",
        "worker_start",
        "agent_start",
        "queue_creation",
        "queue_write",
        "scheduler_write",
        "cron_write",
        "task_enqueue",
        "task_execution",
        "arbitrary_execution",
        "user_task_execution",
        "api_access",
        "network_access",
        "socket_access",
        "dns_resolution",
        "credentials_read",
        "secrets_read",
        "environment_reads",
        "deployment",
        "production_execution",
        "full_workforce_activation",
    ]:
        denials[key] = {"denied": True, "reason": f"{key} not authorized in v6.4 non-executing implementation plan layer"}

    return {
        "permission_denial_record_version": "6.4.0",
        "all_operations_denied": True,
        "denials": denials,
    }


def build_implementation_plan_packet_payload(
    approval_gate: dict,
    implementation_plan_contracts: dict,
    implementation_plan_id: str,
) -> dict:
    payload = {
        "schema_version": "6.4.0",
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "6.4.0",
        "plan_type": "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan",
        "plan_mode": "deterministic_local_non_executing_implementation_plan_packet_only",
        "v6_3_readiness_packet_reference_label": approval_gate.get("v6_3_readiness_packet_reference_label"),
        "v6_2_lane_scope_packet_reference_label": approval_gate.get("v6_2_lane_scope_packet_reference_label"),
        "selected_expansion_lane_label": approval_gate.get("selected_expansion_lane_label"),
        "implementation_plan_label": approval_gate.get("implementation_plan_label"),
        "implementation_step_list_label": approval_gate.get("implementation_step_list_label"),
        "implementation_risk_register_label": approval_gate.get("implementation_risk_register_label"),
        "implementation_rollback_plan_label": approval_gate.get("implementation_rollback_plan_label"),
        "implementation_non_execution_boundary_label": approval_gate.get("implementation_non_execution_boundary_label"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("confirmation_token_valid"),
        "implementation_plan_id": implementation_plan_id,
        "implementation_plan_message": "Station Chief v6.4 post-MVP expansion lane non-executing implementation plan wrote this deterministic local plan packet. The selected expansion lane is recorded as implementation planning metadata only. No implementation was performed and no task was executed.",
        "local_implementation_plan_packet_written": True,
        "station_chief_v6_4_implementation_plan_created": True,
        "post_mvp_expansion_lane_implementation_plan_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_rollback_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_5_created": False,
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


def write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_packet(
    output_directory: str,
    packet_name: str,
    payload: dict,
) -> dict:
    safe_name = safe_implementation_plan_packet_name(packet_name)
    out_dir = Path(output_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = out_dir / safe_name
    packet_path.write_text(canonical_json(payload), encoding="utf-8")

    return {
        "implementation_plan_packet_version": "6.4.0",
        "write_status": "STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PACKET_WRITTEN",
        "local_implementation_plan_packet_written": True,
        "station_chief_v6_4_implementation_plan_created": True,
        "post_mvp_expansion_lane_implementation_plan_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_rollback_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_5_created": False,
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


def create_blocked_implementation_plan_packet_write_record(reason: str) -> dict:
    return {
        "implementation_plan_packet_version": "6.4.0",
        "write_status": "BLOCKED",
        "reason": reason,
        "local_implementation_plan_packet_written": False,
        "station_chief_v6_4_implementation_plan_created": False,
        "post_mvp_expansion_lane_implementation_plan_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_rollback_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_5_created": False,
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


def create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle(
    result: dict | None,
    command: str | None = None,
    v6_3_readiness_packet_reference_label: str | None = None,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    implementation_plan_label: str | None = None,
    implementation_step_list_label: str | None = None,
    implementation_risk_register_label: str | None = None,
    implementation_rollback_plan_label: str | None = None,
    implementation_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    implementation_plan_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    implementation_plan_requested: bool = False,
    write_implementation_plan_packet: bool = False,
) -> dict:
    schema = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema()

    approval_gate = create_implementation_plan_approval_gate(
        v6_3_readiness_packet_reference_label=v6_3_readiness_packet_reference_label or DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL,
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label or DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        implementation_plan_label=implementation_plan_label or DEFAULT_IMPLEMENTATION_PLAN_LABEL,
        implementation_step_list_label=implementation_step_list_label or DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL,
        implementation_risk_register_label=implementation_risk_register_label or DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL,
        implementation_rollback_plan_label=implementation_rollback_plan_label or DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL,
        implementation_non_execution_boundary_label=implementation_non_execution_boundary_label or DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        implementation_plan_requested=implementation_plan_requested,
    )

    implementation_plan_contracts = create_implementation_plan_contracts(approval_gate)
    permission_denial = create_implementation_plan_permission_denial_record(approval_gate)

    implementation_plan_id = generate_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_id(
        command=command or "",
        v6_3_readiness_packet_reference_label=v6_3_readiness_packet_reference_label or DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL,
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label or DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        implementation_plan_label=implementation_plan_label or DEFAULT_IMPLEMENTATION_PLAN_LABEL,
        implementation_step_list_label=implementation_step_list_label or DEFAULT_IMPLEMENTATION_STEP_LIST_LABEL,
        implementation_risk_register_label=implementation_risk_register_label or DEFAULT_IMPLEMENTATION_RISK_REGISTER_LABEL,
        implementation_rollback_plan_label=implementation_rollback_plan_label or DEFAULT_IMPLEMENTATION_ROLLBACK_PLAN_LABEL,
        implementation_non_execution_boundary_label=implementation_non_execution_boundary_label or DEFAULT_IMPLEMENTATION_NON_EXECUTION_BOUNDARY_LABEL,
    )

    payload = None
    write_record = None

    if write_implementation_plan_packet:
        write_authorized = approval_gate.get("local_implementation_plan_packet_write_authorized", False)
        if write_authorized:
            packet_name = safe_implementation_plan_packet_name(
                implementation_plan_packet_name or DEFAULT_STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_PACKET_NAME
            )
            payload = build_implementation_plan_packet_payload(
                approval_gate,
                implementation_plan_contracts,
                implementation_plan_id,
            )
            write_record = write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_packet(
                output_directory=output_directory or "/tmp",
                packet_name=packet_name,
                payload=payload,
            )
        else:
            write_record = create_blocked_implementation_plan_packet_write_record(
                "Implementation plan packet write not authorized"
            )
    else:
        write_record = create_blocked_implementation_plan_packet_write_record(
            "Implementation plan packet write not requested"
        )

    return {
        "station_chief_v6_4_implementation_plan_schema": schema,
        "implementation_plan_approval_gate": approval_gate,
        "implementation_plan_contracts": implementation_plan_contracts,
        "implementation_plan_permission_denial_record": permission_denial,
        "implementation_plan_packet_write_record": write_record,
        "implementation_plan_payload": payload,
        "station_chief_v6_4_implementation_plan_bundle": True,
        "local_implementation_plan_packet_written": write_record.get("local_implementation_plan_packet_written", False),
        "station_chief_v6_4_implementation_plan_created": write_record.get("station_chief_v6_4_implementation_plan_created", False),
        "post_mvp_expansion_lane_implementation_plan_recorded": write_record.get("post_mvp_expansion_lane_implementation_plan_recorded", False),
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "implementation_plan_executed": False,
        "implementation_steps_executed": False,
        "implementation_rollback_executed": False,
        "v6_3_readiness_packet_mutated": False,
        "v6_3_readiness_packet_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
        "v6_5_created": False,
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