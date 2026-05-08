#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_MODULE_VERSION = "6.3.0"
STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_STATUS = "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_LOCAL_PACKET_ONLY"
STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PHASE = "Station Chief v6.3 Post-MVP Expansion Lane Readiness Packet Candidate"
STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET"

DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL = "station-chief-v6-2-lane-scope-packet-reference"
DEFAULT_SELECTED_EXPANSION_LANE_LABEL = "local-worker-persona-expansion-readiness"
DEFAULT_READINESS_CHECKLIST_LABEL = "metadata-only-readiness-checklist"
DEFAULT_READINESS_BLOCKER_LABEL = "metadata-only-readiness-blocker-review"
DEFAULT_READINESS_EVIDENCE_LABEL = "metadata-only-readiness-evidence-review"
DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL = "metadata-only-no-readiness-execution-boundary"
DEFAULT_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_NAME = "station_chief_v6_3_post_mvp_expansion_lane_readiness_packet.json"

SUPPORTED_READINESS_LABELS = [
    "readiness_metadata_only",
    "v6_2_lane_scope_packet_reference_only",
    "selected_expansion_lane_only",
    "readiness_checklist_only",
    "readiness_blocker_only",
    "readiness_evidence_only",
    "readiness_non_execution_boundary_only",
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


def safe_readiness_packet_name(packet_name: str | None) -> str:
    default = DEFAULT_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_NAME
    if packet_name is None:
        return default
    if not packet_name.endswith(".json"):
        return default
    if "/" in packet_name or "\\" in packet_name:
        return default
    if packet_name in (".", ".."):
        return default
    return packet_name


def generate_station_chief_v6_3_post_mvp_expansion_lane_readiness_id(
    command: str,
    v6_2_lane_scope_packet_reference_label: str,
    selected_expansion_lane_label: str,
    readiness_checklist_label: str,
    readiness_blocker_label: str,
    readiness_evidence_label: str,
    readiness_non_execution_boundary_label: str,
    runtime_version: str = "6.3.0",
) -> str:
    prefix = "station-chief-v6-3-post-mvp-expansion-lane-readiness-"
    parts = [
        prefix,
        normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(readiness_checklist_label, DEFAULT_READINESS_CHECKLIST_LABEL),
        normalize_label(readiness_blocker_label, DEFAULT_READINESS_BLOCKER_LABEL),
        normalize_label(readiness_evidence_label, DEFAULT_READINESS_EVIDENCE_LABEL),
        normalize_label(readiness_non_execution_boundary_label, DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL),
    ]
    digest_input = ":".join([
        command or "",
        normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL),
        normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL),
        normalize_label(readiness_checklist_label, DEFAULT_READINESS_CHECKLIST_LABEL),
        normalize_label(readiness_blocker_label, DEFAULT_READINESS_BLOCKER_LABEL),
        normalize_label(readiness_evidence_label, DEFAULT_READINESS_EVIDENCE_LABEL),
        normalize_label(readiness_non_execution_boundary_label, DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL),
        runtime_version,
    ])
    parts.append(sha256_digest(digest_input)[:12])
    return "-".join(parts)


def create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema() -> dict:
    return {
        "schema_version": "6.3.0",
        "status": "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_LOCAL_PACKET_ONLY",
        "readiness_type": "station_chief_v6_3_post_mvp_expansion_lane_readiness",
        "readiness_execution_type": "none_readiness_metadata_only",
        "supported_readiness_labels": list(SUPPORTED_READINESS_LABELS),
        "required_sections": [
            "readiness_approval_gate",
            "readiness_contracts",
            "readiness_permission_denial_record",
            "readiness_packet_record",
            "readiness_audit_record",
            "readiness_summary",
            "station_chief_v6_4_candidate_bridge",
        ],
        "required_labels": [
            "v6_2_lane_scope_packet_reference_label",
            "selected_expansion_lane_label",
            "readiness_checklist_label",
            "readiness_blocker_label",
            "readiness_evidence_label",
            "readiness_non_execution_boundary_label",
        ],
        "required_token": STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "locked_175_family_baseline_preserved": True,
        "local_readiness_packet_written": False,
        "station_chief_v6_3_readiness_created": False,
        "post_mvp_expansion_lane_readiness_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
    }


def create_readiness_approval_gate(
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    readiness_checklist_label: str | None = None,
    readiness_blocker_label: str | None = None,
    readiness_evidence_label: str | None = None,
    readiness_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    readiness_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN
    labels_present = bool(
        v6_2_lane_scope_packet_reference_label
        and selected_expansion_lane_label
        and readiness_checklist_label
        and readiness_blocker_label
        and readiness_evidence_label
        and readiness_non_execution_boundary_label
    )
    local_readiness_records_authorized = token_valid and bool(human_operator) and labels_present
    local_readiness_packet_write_authorized = (
        token_valid
        and bool(human_operator)
        and labels_present
        and bool(output_directory)
        and readiness_requested
    )

    if local_readiness_packet_write_authorized:
        gate_status = "APPROVED_FOR_ONE_LOCAL_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET"
    else:
        gate_status = "BLOCKED_PENDING_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL"

    return {
        "gate_version": "6.3.0",
        "gate_status": gate_status,
        "v6_2_lane_scope_packet_reference_label": normalize_label(v6_2_lane_scope_packet_reference_label, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL) if v6_2_lane_scope_packet_reference_label else None,
        "selected_expansion_lane_label": normalize_label(selected_expansion_lane_label, DEFAULT_SELECTED_EXPANSION_LANE_LABEL) if selected_expansion_lane_label else None,
        "readiness_checklist_label": normalize_label(readiness_checklist_label, DEFAULT_READINESS_CHECKLIST_LABEL) if readiness_checklist_label else None,
        "readiness_blocker_label": normalize_label(readiness_blocker_label, DEFAULT_READINESS_BLOCKER_LABEL) if readiness_blocker_label else None,
        "readiness_evidence_label": normalize_label(readiness_evidence_label, DEFAULT_READINESS_EVIDENCE_LABEL) if readiness_evidence_label else None,
        "readiness_non_execution_boundary_label": normalize_label(readiness_non_execution_boundary_label, DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL) if readiness_non_execution_boundary_label else None,
        "output_directory": output_directory,
        "confirmation_token_provided": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "human_operator": human_operator,
        "readiness_requested": readiness_requested,
        "local_readiness_records_authorized": local_readiness_records_authorized,
        "local_readiness_packet_write_authorized": local_readiness_packet_write_authorized,
        "selected_expansion_lane_implementation_authorized": False,
        "selected_expansion_lane_execution_authorized": False,
        "post_mvp_expansion_execution_authorized": False,
        "v6_2_lane_scope_packet_mutation_authorized": False,
        "v6_2_lane_scope_packet_execution_authorized": False,
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
        "v6_4_creation_authorized": False,
    }


def create_readiness_contracts(approval_gate: dict) -> dict:
    """Create all six required v6.3 readiness contracts."""

    def _build_v6_2_lane_scope_packet_reference_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "v6_2_lane_scope_packet_reference_label": None,
                "v6_2_lane_scope_packet_reference_label_normalized": None,
                "reference_is_metadata_only": False,
                "v6_2_lane_scope_packet_mutated": False,
                "v6_2_lane_scope_packet_executed": False,
                "v6_4_authorized": False,
            }
        raw = approval_gate.get("v6_2_lane_scope_packet_reference_label", DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL)
        normalized = normalize_label(raw, DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL)
        return {
            "contract_created": True,
            "v6_2_lane_scope_packet_reference_label": raw,
            "v6_2_lane_scope_packet_reference_label_normalized": normalized,
            "reference_is_metadata_only": True,
            "reference_not_read_from_disk": True,
            "reference_not_mutated": True,
            "reference_not_executed": True,
            "reference_not_deployed": True,
            "reference_does_not_start_workers": True,
            "reference_does_not_start_agents": True,
            "reference_does_not_create_queues": True,
            "reference_does_not_authorize_v6_4": True,
            "v6_2_lane_scope_packet_mutated": False,
            "v6_2_lane_scope_packet_executed": False,
            "v6_4_authorized": False,
        }

    def _build_selected_expansion_lane_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "selected_expansion_lane_label": None,
                "selected_expansion_lane_label_normalized": None,
                "lane_is_metadata_only": False,
            }
        raw = approval_gate.get("selected_expansion_lane_label", DEFAULT_SELECTED_EXPANSION_LANE_LABEL)
        normalized = normalize_label(raw, DEFAULT_SELECTED_EXPANSION_LANE_LABEL)
        return {
            "contract_created": True,
            "selected_expansion_lane_label": raw,
            "selected_expansion_lane_label_normalized": normalized,
            "lane_is_metadata_only": True,
            "lane_not_implemented": True,
            "lane_not_executed": True,
            "lane_does_not_start_workers": True,
            "lane_does_not_start_agents": True,
            "lane_does_not_create_queues": True,
            "lane_does_not_execute_tasks": True,
            "lane_does_not_call_apis_network_deployment_production": True,
        }

    def _build_readiness_checklist_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "readiness_checklist_label": None,
                "readiness_checklist_label_normalized": None,
                "checklist_is_metadata_only": False,
            }
        raw = approval_gate.get("readiness_checklist_label", DEFAULT_READINESS_CHECKLIST_LABEL)
        normalized = normalize_label(raw, DEFAULT_READINESS_CHECKLIST_LABEL)
        return {
            "contract_created": True,
            "readiness_checklist_label": raw,
            "readiness_checklist_label_normalized": normalized,
            "checklist_is_metadata_only": True,
            "checklist_does_not_implement_lane": True,
            "checklist_does_not_execute_lane": True,
            "checklist_does_not_start_workers": True,
            "checklist_does_not_create_queues": True,
            "checklist_does_not_execute_tasks": True,
            "checklist_does_not_call_apis_network_deployment_production": True,
        }

    def _build_readiness_blocker_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "readiness_blocker_label": None,
                "readiness_blocker_label_normalized": None,
                "blocker_review_is_metadata_only": False,
            }
        raw = approval_gate.get("readiness_blocker_label", DEFAULT_READINESS_BLOCKER_LABEL)
        normalized = normalize_label(raw, DEFAULT_READINESS_BLOCKER_LABEL)
        return {
            "contract_created": True,
            "readiness_blocker_label": raw,
            "readiness_blocker_label_normalized": normalized,
            "blocker_review_is_metadata_only": True,
            "blocker_does_not_block_anything_real": True,
            "blocker_does_not_start_workers": True,
            "blocker_does_not_create_queues": True,
            "blocker_does_not_execute_tasks": True,
            "blocker_does_not_call_apis_network_deployment_production": True,
        }

    def _build_readiness_evidence_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "readiness_evidence_label": None,
                "readiness_evidence_label_normalized": None,
                "evidence_status": "BLOCKED",
            }
        raw = approval_gate.get("readiness_evidence_label", DEFAULT_READINESS_EVIDENCE_LABEL)
        normalized = normalize_label(raw, DEFAULT_READINESS_EVIDENCE_LABEL)
        all_dangerous_false = all(
            not approval_gate.get(key)
            for key in [
                "selected_expansion_lane_implementation_authorized",
                "selected_expansion_lane_execution_authorized",
                "post_mvp_expansion_execution_authorized",
                "v6_2_lane_scope_packet_mutation_authorized",
                "v6_2_lane_scope_packet_execution_authorized",
                "v6_1_review_packet_mutation_authorized",
                "v6_1_review_packet_execution_authorized",
                "v6_0_mvp_lock_mutation_authorized",
                "v6_0_mvp_lock_execution_authorized",
                "worker_process_start_authorized",
                "agent_start_authorized",
                "real_queue_creation_authorized",
                "task_execution_authorized",
                "v6_4_creation_authorized",
            ]
        )
        evidence_status = "PASS" if all_dangerous_false else "BLOCKED"
        return {
            "contract_created": True,
            "readiness_evidence_label": raw,
            "readiness_evidence_label_normalized": normalized,
            "evidence_status": evidence_status,
            "metadata_only": True,
            "no_execution": True,
            "no_worker_start": True,
            "no_agent_start": True,
            "no_queue_creation": True,
            "no_task_execution": True,
            "no_api_network_deployment_production": True,
            "no_v6_4_creation": True,
        }

    def _build_readiness_non_execution_boundary_contract() -> dict:
        if not approval_gate.get("local_readiness_records_authorized"):
            return {
                "contract_created": False,
                "readiness_non_execution_boundary_label": None,
                "readiness_non_execution_boundary_label_normalized": None,
            }
        raw = approval_gate.get("readiness_non_execution_boundary_label", DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL)
        normalized = normalize_label(raw, DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL)
        return {
            "contract_created": True,
            "readiness_non_execution_boundary_label": raw,
            "readiness_non_execution_boundary_label_normalized": normalized,
            "boundary_is_metadata_only": True,
            "deny_execution_by_default": True,
            "deny_worker_start_by_default": True,
            "deny_agent_start_by_default": True,
            "deny_queue_creation_by_default": True,
            "deny_api_network_deployment_production_by_default": True,
            "deny_v6_4_creation_by_default": True,
            "future_implementation_requires_explicit_operator_instruction": True,
        }

    return {
        "v6_2_lane_scope_packet_reference_contract": _build_v6_2_lane_scope_packet_reference_contract(),
        "selected_expansion_lane_contract": _build_selected_expansion_lane_contract(),
        "readiness_checklist_contract": _build_readiness_checklist_contract(),
        "readiness_blocker_contract": _build_readiness_blocker_contract(),
        "readiness_evidence_contract": _build_readiness_evidence_contract(),
        "readiness_non_execution_boundary_contract": _build_readiness_non_execution_boundary_contract(),
    }


def create_readiness_permission_denial_record(approval_gate: dict, contracts: dict) -> dict:
    denials = {}

    def _deny(label: str, reason: str) -> None:
        denials[label] = {
            "denied": True,
            "reason": reason,
        }

    if not approval_gate.get("local_readiness_records_authorized"):
        for key in [
            "selected_expansion_lane_implementation",
            "selected_expansion_lane_execution",
            "readiness_checklist_execution",
            "readiness_blocker_execution",
            "readiness_evidence_execution",
            "v6_2_lane_scope_packet_mutation",
            "v6_2_lane_scope_packet_execution",
            "v6_4_creation",
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
            _deny(key, "Readiness approval gate blocked all operations")

    approval_gate_denied = not approval_gate.get("local_readiness_records_authorized", False)
    if approval_gate_denied:
        return {
            "permission_denial_record_version": "6.3.0",
            "all_operations_denied": True,
            "denials": denials,
        }

    for label_key, authorized_key, reason_text in [
        ("selected_expansion_lane_implementation", "selected_expansion_lane_implementation_authorized", "Selected expansion lane implementation not authorized"),
        ("selected_expansion_lane_execution", "selected_expansion_lane_execution_authorized", "Selected expansion lane execution not authorized"),
        ("readiness_checklist_execution", "task_execution_authorized", "Readiness checklist execution not authorized"),
        ("readiness_blocker_execution", "task_execution_authorized", "Readiness blocker execution not authorized"),
        ("readiness_evidence_execution", "task_execution_authorized", "Readiness evidence execution not authorized"),
        ("v6_2_lane_scope_packet_mutation", "v6_2_lane_scope_packet_mutation_authorized", "v6.2 lane scope packet mutation not authorized"),
        ("v6_2_lane_scope_packet_execution", "v6_2_lane_scope_packet_execution_authorized", "v6.2 lane scope packet execution not authorized"),
        ("v6_4_creation", "v6_4_creation_authorized", "v6.4 creation not authorized"),
        ("worker_start", "worker_process_start_authorized", "Worker start not authorized"),
        ("agent_start", "agent_start_authorized", "Agent start not authorized"),
        ("queue_creation", "real_queue_creation_authorized", "Queue creation not authorized"),
        ("queue_write", "queue_write_authorized", "Queue write not authorized"),
        ("scheduler_write", "scheduler_write_authorized", "Scheduler write not authorized"),
        ("cron_write", "cron_write_authorized", "Cron write not authorized"),
        ("task_enqueue", "task_enqueue_authorized", "Task enqueue not authorized"),
        ("task_execution", "task_execution_authorized", "Task execution not authorized"),
        ("arbitrary_execution", "arbitrary_task_execution_authorized", "Arbitrary execution not authorized"),
        ("user_task_execution", "user_task_execution_authorized", "User task execution not authorized"),
        ("api_access", "api_call_authorized", "API access not authorized"),
        ("network_access", "network_access_authorized", "Network access not authorized"),
        ("socket_access", "network_access_authorized", "Socket access not authorized"),
        ("dns_resolution", "network_access_authorized", "DNS resolution not authorized"),
        ("credentials_read", "deployment_authorized", "Credentials read not authorized"),
        ("secrets_read", "deployment_authorized", "Secrets read not authorized"),
        ("environment_reads", "deployment_authorized", "Environment reads not authorized"),
        ("deployment", "deployment_authorized", "Deployment not authorized"),
        ("production_execution", "production_execution_authorized", "Production execution not authorized"),
        ("full_workforce_activation", "full_workforce_activation_authorized", "Full workforce activation not authorized"),
    ]:
        if not approval_gate.get(authorized_key, False):
            _deny(label_key, reason_text)

    return {
        "permission_denial_record_version": "6.3.0",
        "all_operations_denied": all(d["denied"] for d in denials.values()) if denials else True,
        "denials": denials,
    }


def build_readiness_packet_payload(
    approval_gate: dict,
    contracts: dict,
    readiness_id: str,
) -> dict:
    payload = {
        "schema_version": "6.3.0",
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "6.3.0",
        "readiness_type": "station_chief_v6_3_post_mvp_expansion_lane_readiness",
        "readiness_mode": "deterministic_local_readiness_packet_only",
        "v6_2_lane_scope_packet_reference_label": approval_gate.get("v6_2_lane_scope_packet_reference_label"),
        "selected_expansion_lane_label": approval_gate.get("selected_expansion_lane_label"),
        "readiness_checklist_label": approval_gate.get("readiness_checklist_label"),
        "readiness_blocker_label": approval_gate.get("readiness_blocker_label"),
        "readiness_evidence_label": approval_gate.get("readiness_evidence_label"),
        "readiness_non_execution_boundary_label": approval_gate.get("readiness_non_execution_boundary_label"),
        "human_operator": approval_gate.get("human_operator"),
        "approval_token_valid": approval_gate.get("confirmation_token_valid"),
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_id": readiness_id,
        "readiness_message": "Station Chief v6.3 post-MVP expansion lane readiness wrote this deterministic local readiness packet. The selected expansion lane is recorded as readiness metadata only. No worker was started and no task was executed.",
        "readiness_value": "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_RECORDED_METADATA_ONLY",
        "next_review": "V6_4_REQUIRES_EXPLICIT_OPERATOR_INSTRUCTION",
        "local_readiness_packet_written": True,
        "station_chief_v6_3_readiness_created": True,
        "post_mvp_expansion_lane_readiness_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet(
    output_directory: str,
    packet_name: str,
    payload: dict,
) -> dict:
    safe_name = safe_readiness_packet_name(packet_name)
    out_dir = Path(output_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = out_dir / safe_name
    packet_path.write_text(canonical_json(payload), encoding="utf-8")

    return {
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_write_record_version": "6.3.0",
        "write_status": "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_WRITTEN",
        "local_readiness_packet_written": True,
        "station_chief_v6_3_readiness_created": True,
        "post_mvp_expansion_lane_readiness_recorded": True,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
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


def create_blocked_readiness_packet_write_record(reason: str) -> dict:
    return {
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_write_record_version": "6.3.0",
        "write_status": "BLOCKED",
        "reason": reason,
        "local_readiness_packet_written": False,
        "station_chief_v6_3_readiness_created": False,
        "post_mvp_expansion_lane_readiness_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
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


def create_readiness_packet_record(
    write_record: dict,
    payload: dict | None = None,
) -> dict:
    written = write_record.get("local_readiness_packet_written", False)
    packet_status = "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_WRITTEN" if written else "BLOCKED"
    return {
        "packet_record_version": "6.3.0",
        "packet_status": packet_status,
        "write_record": write_record,
        "payload_digest": payload.get("payload_digest") if payload else None,
        "local_readiness_packet_written": write_record.get("local_readiness_packet_written", False),
        "station_chief_v6_3_readiness_created": write_record.get("station_chief_v6_3_readiness_created", False),
        "post_mvp_expansion_lane_readiness_recorded": write_record.get("post_mvp_expansion_lane_readiness_recorded", False),
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
        "worker_process_started": False,
        "agent_started": False,
        "task_executed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
    }


def create_readiness_audit_record(
    readiness_approval_gate: dict,
    readiness_contracts: dict,
    readiness_packet_record: dict,
) -> dict:
    def _digest(record: dict) -> str:
        return sha256_digest(record)

    audit_pass = True
    dangerous_keys = [
        ("selected_expansion_lane_implemented", readiness_packet_record),
        ("selected_expansion_lane_executed", readiness_packet_record),
        ("post_mvp_expansion_executed", readiness_packet_record),
        ("v6_2_lane_scope_packet_mutated", readiness_packet_record),
        ("v6_2_lane_scope_packet_executed", readiness_packet_record),
        ("v6_1_review_packet_mutated", readiness_packet_record),
        ("v6_1_review_packet_executed", readiness_packet_record),
        ("v6_0_mvp_lock_mutated", readiness_packet_record),
        ("v6_0_mvp_lock_executed", readiness_packet_record),
        ("local_task_candidate_executed", readiness_packet_record),
        ("dry_run_task_executed", readiness_packet_record),
        ("real_worker_result_created", readiness_packet_record),
        ("live_replay_performed", readiness_packet_record),
        ("production_audit_performed", readiness_packet_record),
        ("rollback_performed", readiness_packet_record),
        ("recovery_performed", readiness_packet_record),
        ("v6_4_created", readiness_packet_record),
        ("worker_process_started", readiness_packet_record),
        ("agent_started", readiness_packet_record),
        ("task_executed", readiness_packet_record),
        ("arbitrary_task_execution_performed", readiness_packet_record),
        ("user_task_execution_performed", readiness_packet_record),
    ]
    for key, record in dangerous_keys:
        if record.get(key) is True:
            audit_pass = False

    audit_status = "PASS" if audit_pass else "BLOCKED"

    return {
        "audit_version": "6.3.0",
        "audit_status": audit_status,
        "section_digests": {
            "readiness_approval_gate": _digest(readiness_approval_gate),
            "readiness_contracts": _digest(readiness_contracts),
            "readiness_packet_record": _digest(readiness_packet_record),
        },
        "local_readiness_packet_written": readiness_packet_record.get("local_readiness_packet_written", False),
        "station_chief_v6_3_readiness_created": readiness_packet_record.get("station_chief_v6_3_readiness_created", False),
        "post_mvp_expansion_lane_readiness_recorded": readiness_packet_record.get("post_mvp_expansion_lane_readiness_recorded", False),
    }


def create_readiness_summary(readiness_audit_record: dict) -> dict:
    audit_pass = readiness_audit_record.get("audit_status") == "PASS"
    ready = audit_pass
    readiness_status = "READY_FOR_V6_4_REVIEW_ONLY" if ready else "BLOCKED"

    return {
        "readiness_version": "6.3.0",
        "readiness_status": readiness_status,
        "current_layer": "Station Chief v6.3 Post-MVP Expansion Lane Readiness Packet Candidate",
        "v6_3_built_only_as_readiness_packet": True,
        "one_deterministic_readiness_packet_permitted_under_v6_3_token": True,
        "references_one_v6_2_lane_scope_packet_reference_label": True,
        "uses_one_selected_expansion_lane_label": True,
        "uses_one_readiness_checklist_label": True,
        "uses_one_readiness_blocker_label": True,
        "uses_one_readiness_evidence_label": True,
        "uses_one_readiness_non_execution_boundary_label": True,
        "no_selected_expansion_lane_implementation": True,
        "no_selected_expansion_lane_execution": True,
        "no_post_mvp_expansion_execution": True,
        "no_v6_2_lane_scope_packet_mutation": True,
        "no_v6_2_lane_scope_packet_execution": True,
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
        "no_v6_4_creation": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_station_chief_v6_4_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_V6_4_REVIEW_ONLY"
    return {
        "bridge_version": "6.3.0",
        "bridge_to_v6_4_review_only": ready,
        "v6_4_not_created_in_v6_3": True,
        "no_selected_expansion_lane_implementation_in_v6_3": True,
        "no_selected_expansion_lane_execution_in_v6_3": True,
        "no_real_worker_start_in_v6_3": True,
        "no_real_task_execution_in_v6_3": True,
        "no_queue_creation_in_v6_3": True,
        "no_task_enqueue_in_v6_3": True,
        "no_arbitrary_task_execution_in_v6_3": True,
        "no_user_task_execution_in_v6_3": True,
        "no_worker_routing_in_v6_3": True,
        "all_dangerous_external_booleans_false": True,
    }


def create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
    result: dict | None,
    command: str | None = None,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    readiness_checklist_label: str | None = None,
    readiness_blocker_label: str | None = None,
    readiness_evidence_label: str | None = None,
    readiness_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    readiness_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    readiness_requested: bool = False,
    write_readiness_packet: bool = False,
) -> dict:
    schema = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema()

    approval_gate = create_readiness_approval_gate(
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label or DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        readiness_checklist_label=readiness_checklist_label or DEFAULT_READINESS_CHECKLIST_LABEL,
        readiness_blocker_label=readiness_blocker_label or DEFAULT_READINESS_BLOCKER_LABEL,
        readiness_evidence_label=readiness_evidence_label or DEFAULT_READINESS_EVIDENCE_LABEL,
        readiness_non_execution_boundary_label=readiness_non_execution_boundary_label or DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        readiness_requested=readiness_requested,
    )

    readiness_contracts = create_readiness_contracts(approval_gate)
    permission_denial = create_readiness_permission_denial_record(approval_gate, readiness_contracts)

    readiness_id = generate_station_chief_v6_3_post_mvp_expansion_lane_readiness_id(
        command=command or "",
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label or DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=selected_expansion_lane_label or DEFAULT_SELECTED_EXPANSION_LANE_LABEL,
        readiness_checklist_label=readiness_checklist_label or DEFAULT_READINESS_CHECKLIST_LABEL,
        readiness_blocker_label=readiness_blocker_label or DEFAULT_READINESS_BLOCKER_LABEL,
        readiness_evidence_label=readiness_evidence_label or DEFAULT_READINESS_EVIDENCE_LABEL,
        readiness_non_execution_boundary_label=readiness_non_execution_boundary_label or DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL,
    )

    payload = None
    write_record = None

    if write_readiness_packet:
        write_authorized = approval_gate.get("local_readiness_packet_write_authorized", False)
        if write_authorized:
            packet_name = safe_readiness_packet_name(readiness_packet_name or DEFAULT_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_NAME)
            payload = build_readiness_packet_payload(
                approval_gate,
                readiness_contracts,
                readiness_id,
            )
            write_record = write_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet(
                output_directory=output_directory or "/tmp",
                packet_name=packet_name,
                payload=payload,
            )
        else:
            write_record = create_blocked_readiness_packet_write_record(
                "Station Chief v6.3 post-MVP expansion lane readiness packet write not authorized or plan blocked"
            )
    else:
        write_record = create_blocked_readiness_packet_write_record(
            "Station Chief v6.3 post-MVP expansion lane readiness packet write not requested"
        )

    packet_record = create_readiness_packet_record(write_record, payload)

    audit_record = create_readiness_audit_record(
        approval_gate,
        readiness_contracts,
        packet_record,
    )

    summary = create_readiness_summary(audit_record)
    v6_4_bridge = create_station_chief_v6_4_candidate_bridge(summary)

    top_level = {
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_schema": schema,
        "readiness_approval_gate": approval_gate,
        "readiness_contracts": readiness_contracts,
        "readiness_permission_denial_record": permission_denial,
        "readiness_packet_record": packet_record,
        "readiness_audit_record": audit_record,
        "readiness_summary": summary,
        "station_chief_v6_4_candidate_bridge": v6_4_bridge,
        "readiness_packet_payload": payload,
        "readiness_packet_write_record": write_record,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle": True,
        "local_readiness_packet_written": write_record.get("local_readiness_packet_written", False) if write_record else False,
        "station_chief_v6_3_readiness_created": write_record.get("station_chief_v6_3_readiness_created", False) if write_record else False,
        "post_mvp_expansion_lane_readiness_recorded": write_record.get("post_mvp_expansion_lane_readiness_recorded", False) if write_record else False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_2_lane_scope_packet_mutated": False,
        "v6_2_lane_scope_packet_executed": False,
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
        "v6_4_created": False,
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
