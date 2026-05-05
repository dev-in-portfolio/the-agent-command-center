#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re

SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION = "3.6.0"
SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_STATUS = "SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PREVIEW_ONLY"
SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PHASE = "Supervised Production Pilot Readiness Review"
SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_production_readiness_label(label: str) -> str:
    normalized = label.lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized or "supervised-production-pilot-readiness-review"


def generate_supervised_production_pilot_readiness_review_id(
    command: str,
    production_readiness_label: str,
    runtime_version: str = "3.6.0",
) -> str:
    normalized_label = normalize_production_readiness_label(production_readiness_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{production_readiness_label}")
    return f"supervised-production-pilot-readiness-review-v3-6-{normalized_label}-{digest[:12]}"


def _gate_is_valid(approval_gate: dict) -> bool:
    return bool(
        approval_gate.get("confirmation_token_valid") is True
        and approval_gate.get("local_production_readiness_records_authorized") is True
        and approval_gate.get("gate_status")
        == "APPROVED_FOR_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_RECORDS"
    )


def create_supervised_production_pilot_readiness_review_schema() -> dict:
    return {
        "supervised_production_pilot_readiness_review_schema_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "schema_status": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_STATUS,
        "required_sections": [
            "supervised_production_pilot_readiness_review_approval_gate",
            "minimum_viable_production_candidate_contract",
            "human_production_pilot_review_gate",
            "production_blast_radius_analysis",
            "live_action_denial_review",
            "rollback_availability_review",
            "credential_secret_readiness_denial_proof",
            "network_socket_readiness_denial_proof",
            "production_pilot_audit_proof",
            "production_pilot_readiness_ledger",
            "production_pilot_readiness_summary",
            "credential_vault_denial_secret_handling_proof_bridge",
        ],
        "allowed_production_readiness_modes": [
            "schema_only",
            "local_production_readiness_records",
            "approved_production_readiness_records",
            "minimum_viable_candidate_preview",
            "blast_radius_analysis_preview",
            "live_action_denial_review",
            "rollback_availability_review",
            "credential_secret_denial_review",
            "network_socket_denial_review",
            "production_pilot_audit_preview",
        ],
        "blocked_production_readiness_modes": [
            "production_execution",
            "production_activation",
            "live_deployment",
            "deployment_rollback",
            "real_rollback_execution",
            "real_recovery_execution",
            "process_termination",
            "worker_termination",
            "production_state_change",
            "live_api_call",
            "network_access",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "real_external_tool_invocation",
            "real_task_execution",
            "live_task_assignment",
            "live_worker_routing",
            "live_orchestration",
            "worker_process_start",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "full_workforce_activation",
        ],
        "required_confirmation_tokens": [
            SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN,
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_supervised_production_pilot_readiness_review_approval_gate(
    production_readiness_label: str,
    confirmation_token: str | None = None,
) -> dict:
    token_valid = confirmation_token == SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN
    gate_status = (
        "APPROVED_FOR_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_RECORDS"
        if token_valid
        else "BLOCKED_PENDING_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL"
    )
    return {
        "supervised_production_pilot_readiness_review_approval_gate_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "production_readiness_label": production_readiness_label,
        "gate_status": gate_status,
        "confirmation_token_required": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_production_readiness_records_authorized": token_valid,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "deployment_authorized": False,
        "deployment_rollback_authorized": False,
        "real_rollback_authorized": False,
        "real_recovery_authorized": False,
        "process_termination_authorized": False,
        "worker_termination_authorized": False,
        "production_state_change_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "real_external_tool_invocation_authorized": False,
        "real_task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "worker_process_start_authorized": False,
        "repo_mutation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_minimum_viable_production_candidate_contract(
    approval_gate: dict,
    candidate_label: str | None = None,
) -> dict:
    candidate_label = candidate_label or "minimum viable production candidate preview"
    created = _gate_is_valid(approval_gate)
    return {
        "minimum_viable_production_candidate_contract_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "contract_status": "MINIMUM_VIABLE_PRODUCTION_CANDIDATE_CONTRACT_CREATED" if created else "BLOCKED",
        "candidate_label": candidate_label,
        "candidate_preview_only": True,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "deployment_allowed": False,
        "live_action_allowed": False,
        "execution_authorized": False,
    }


def create_human_production_pilot_review_gate(
    approval_gate: dict,
    required_production_pilot_reviewer: str | None = None,
) -> dict:
    required_production_pilot_reviewer = required_production_pilot_reviewer or "Devin O’Rourke / explicit human operator"
    created = _gate_is_valid(approval_gate)
    return {
        "human_production_pilot_review_gate_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "review_gate_status": "HUMAN_PRODUCTION_PILOT_REVIEW_REQUIREMENT_CREATED" if created else "BLOCKED",
        "required_production_pilot_reviewer": required_production_pilot_reviewer,
        "human_production_pilot_review_required": True,
        "current_review_grants_production_execution": False,
        "current_review_grants_production_activation": False,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "deployment_authorized": False,
        "live_action_authorized": False,
        "approval_bypass_allowed": False,
        "execution_authorized": False,
    }


def create_production_blast_radius_analysis(
    approval_gate: dict,
    blast_radius_label: str | None = None,
) -> dict:
    blast_radius_label = blast_radius_label or "preview production blast-radius analysis"
    created = _gate_is_valid(approval_gate)
    return {
        "production_blast_radius_analysis_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "analysis_status": "PRODUCTION_BLAST_RADIUS_ANALYSIS_CREATED" if created else "BLOCKED",
        "blast_radius_label": blast_radius_label,
        "analysis_preview_only": True,
        "production_surface_reviewed": created,
        "live_systems_touched": False,
        "production_state_changed": False,
        "deployment_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "execution_authorized": False,
    }


def create_live_action_denial_review(approval_gate: dict) -> dict:
    created = _gate_is_valid(approval_gate)
    return {
        "live_action_denial_review_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "review_status": "LIVE_ACTION_DENIAL_REVIEW_CREATED" if created else "BLOCKED",
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "deployment_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "real_external_tool_invocation_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "worker_process_start_allowed": False,
        "external_actions_taken": False,
        "execution_authorized": False,
    }


def create_rollback_availability_review(approval_gate: dict) -> dict:
    created = _gate_is_valid(approval_gate)
    return {
        "rollback_availability_review_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "review_status": "ROLLBACK_AVAILABILITY_REVIEW_CREATED" if created else "BLOCKED",
        "rollback_review_only": True,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "deployment_rollback_performed": False,
        "production_state_changed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "execution_authorized": False,
    }


def create_credential_secret_readiness_denial_proof(approval_gate: dict) -> dict:
    created = _gate_is_valid(approval_gate)
    return {
        "credential_secret_readiness_denial_proof_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "proof_status": "CREDENTIAL_SECRET_READINESS_DENIAL_PROOF_CREATED" if created else "BLOCKED",
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "credential_vault_access_allowed": False,
        "credential_vault_access_performed": False,
        "execution_authorized": False,
    }


def create_network_socket_readiness_denial_proof(approval_gate: dict) -> dict:
    created = _gate_is_valid(approval_gate)
    return {
        "network_socket_readiness_denial_proof_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "proof_status": "NETWORK_SOCKET_READINESS_DENIAL_PROOF_CREATED" if created else "BLOCKED",
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "live_api_call_allowed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "live_api_call_performed": False,
        "execution_authorized": False,
    }


def create_production_pilot_audit_proof(
    approval_gate: dict,
    minimum_candidate_contract: dict,
    human_review_gate: dict,
    blast_radius_analysis: dict,
    live_action_denial_review: dict,
    rollback_availability_review: dict,
    credential_secret_denial_proof: dict,
    network_socket_denial_proof: dict,
) -> dict:
    safety_checks = {
        "approval_gate_valid": _gate_is_valid(approval_gate),
        "minimum_viable_production_candidate_contract_created": minimum_candidate_contract.get("contract_status") == "MINIMUM_VIABLE_PRODUCTION_CANDIDATE_CONTRACT_CREATED",
        "human_production_pilot_review_required": human_review_gate.get("review_gate_status") == "HUMAN_PRODUCTION_PILOT_REVIEW_REQUIREMENT_CREATED",
        "production_blast_radius_analysis_created": blast_radius_analysis.get("analysis_status") == "PRODUCTION_BLAST_RADIUS_ANALYSIS_CREATED",
        "live_action_denial_review_created": live_action_denial_review.get("review_status") == "LIVE_ACTION_DENIAL_REVIEW_CREATED",
        "rollback_availability_review_created": rollback_availability_review.get("review_status") == "ROLLBACK_AVAILABILITY_REVIEW_CREATED",
        "credential_secret_denial_proof_created": credential_secret_denial_proof.get("proof_status") == "CREDENTIAL_SECRET_READINESS_DENIAL_PROOF_CREATED",
        "network_socket_denial_proof_created": network_socket_denial_proof.get("proof_status") == "NETWORK_SOCKET_READINESS_DENIAL_PROOF_CREATED",
        "no_production_execution": not any(
            [
                minimum_candidate_contract.get("production_execution_allowed"),
                human_review_gate.get("production_execution_authorized"),
                blast_radius_analysis.get("production_execution_performed"),
                live_action_denial_review.get("production_execution_allowed"),
            ]
        ),
        "no_production_activation": not any(
            [
                minimum_candidate_contract.get("production_activation_allowed"),
                human_review_gate.get("production_activation_authorized"),
                live_action_denial_review.get("production_activation_allowed"),
            ]
        ),
        "no_deployment": not any(
            [
                minimum_candidate_contract.get("deployment_allowed"),
                human_review_gate.get("deployment_authorized"),
                blast_radius_analysis.get("deployment_performed"),
                live_action_denial_review.get("deployment_allowed"),
            ]
        ),
        "no_deployment_rollback": not any(
            [
                rollback_availability_review.get("deployment_rollback_performed"),
            ]
        ),
        "no_real_rollback": not any(
            [
                rollback_availability_review.get("real_rollback_performed"),
            ]
        ),
        "no_real_recovery": not any(
            [
                rollback_availability_review.get("real_recovery_performed"),
            ]
        ),
        "no_processes_terminated": not any(
            [
                rollback_availability_review.get("processes_terminated"),
            ]
        ),
        "no_workers_terminated": not any(
            [
                rollback_availability_review.get("workers_terminated"),
            ]
        ),
        "no_production_state_changed": not any(
            [
                minimum_candidate_contract.get("production_state_changed"),
                human_review_gate.get("production_state_changed"),
                blast_radius_analysis.get("production_state_changed"),
                live_action_denial_review.get("production_state_change_allowed"),
                rollback_availability_review.get("production_state_changed"),
                credential_secret_denial_proof.get("environment_read"),
                network_socket_denial_proof.get("live_api_call_performed"),
            ]
        ),
        "no_live_api_call": not any(
            [
                live_action_denial_review.get("live_api_call_allowed"),
                credential_secret_denial_proof.get("credential_vault_access_performed"),
                network_socket_denial_proof.get("live_api_call_performed"),
            ]
        ),
        "no_network_access": not any(
            [
                live_action_denial_review.get("network_access_allowed"),
                credential_secret_denial_proof.get("environment_read_allowed"),
                network_socket_denial_proof.get("network_access_performed"),
            ]
        ),
        "no_socket_opened": not any(
            [
                live_action_denial_review.get("socket_access_allowed"),
                network_socket_denial_proof.get("socket_opened"),
            ]
        ),
        "no_credentials_used": not any(
            [
                live_action_denial_review.get("credential_use_allowed"),
                credential_secret_denial_proof.get("credentials_used"),
                network_socket_denial_proof.get("live_api_call_allowed"),
            ]
        ),
        "no_secrets_read": not any(
            [
                live_action_denial_review.get("secret_read_allowed"),
                credential_secret_denial_proof.get("secrets_read"),
            ]
        ),
        "no_environment_read": not any(
            [
                live_action_denial_review.get("environment_read_allowed"),
                credential_secret_denial_proof.get("environment_read"),
            ]
        ),
        "no_real_external_tool_invocation": not any(
            [
                live_action_denial_review.get("real_external_tool_invocation_allowed"),
                credential_secret_denial_proof.get("credential_vault_access_allowed"),
            ]
        ),
        "no_real_task_execution": not any(
            [
                live_action_denial_review.get("live_task_assignment_allowed"),
                human_review_gate.get("current_review_grants_production_execution"),
            ]
        ),
        "no_live_task_assignment": not any(
            [
                live_action_denial_review.get("live_task_assignment_allowed"),
            ]
        ),
        "no_live_worker_routing": not any(
            [
                live_action_denial_review.get("live_worker_routing_allowed"),
            ]
        ),
        "no_live_orchestration": not any(
            [
                live_action_denial_review.get("live_orchestration_allowed"),
            ]
        ),
        "no_repo_modifications": not any(
            [
                approval_gate.get("repo_files_modified"),
                minimum_candidate_contract.get("repo_files_modified"),
                human_review_gate.get("repo_files_modified"),
                live_action_denial_review.get("repo_files_modified"),
                credential_secret_denial_proof.get("credential_vault_access_performed"),
                network_socket_denial_proof.get("execution_authorized"),
            ]
        ),
    }
    audit_status = "PASS" if all(safety_checks.values()) else "BLOCKED"
    return {
        "production_pilot_audit_proof_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "audit_status": audit_status,
        "approval_gate_digest": sha256_digest(approval_gate),
        "minimum_candidate_contract_digest": sha256_digest(minimum_candidate_contract),
        "human_review_gate_digest": sha256_digest(human_review_gate),
        "blast_radius_analysis_digest": sha256_digest(blast_radius_analysis),
        "live_action_denial_review_digest": sha256_digest(live_action_denial_review),
        "rollback_availability_review_digest": sha256_digest(rollback_availability_review),
        "credential_secret_denial_proof_digest": sha256_digest(credential_secret_denial_proof),
        "network_socket_denial_proof_digest": sha256_digest(network_socket_denial_proof),
        "combined_production_pilot_audit_digest": sha256_digest(
            {
                "approval_gate": approval_gate,
                "minimum_candidate_contract": minimum_candidate_contract,
                "human_review_gate": human_review_gate,
                "blast_radius_analysis": blast_radius_analysis,
                "live_action_denial_review": live_action_denial_review,
                "rollback_availability_review": rollback_availability_review,
                "credential_secret_denial_proof": credential_secret_denial_proof,
                "network_socket_denial_proof": network_socket_denial_proof,
            }
        ),
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_production_pilot_readiness_ledger(
    approval_gate: dict,
    minimum_candidate_contract: dict,
    human_review_gate: dict,
    blast_radius_analysis: dict,
    live_action_denial_review: dict,
    rollback_availability_review: dict,
    credential_secret_denial_proof: dict,
    network_socket_denial_proof: dict,
    production_pilot_audit_proof: dict,
) -> dict:
    ledger_status = (
        "SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_LEDGER"
        if production_pilot_audit_proof.get("audit_status") == "PASS"
        else "BLOCKED"
    )
    entries = [
        "supervised production pilot readiness approval gate entry",
        "minimum viable production candidate contract entry",
        "human production pilot review gate entry",
        "production blast-radius analysis entry",
        "live action denial review entry",
        "rollback availability review entry",
        "credential/secret readiness denial proof entry",
        "network/socket readiness denial proof entry",
        "production pilot audit proof entry",
    ]
    return {
        "production_pilot_readiness_ledger_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(
            {
                "approval_gate": approval_gate,
                "minimum_candidate_contract": minimum_candidate_contract,
                "human_review_gate": human_review_gate,
                "blast_radius_analysis": blast_radius_analysis,
                "live_action_denial_review": live_action_denial_review,
                "rollback_availability_review": rollback_availability_review,
                "credential_secret_denial_proof": credential_secret_denial_proof,
                "network_socket_denial_proof": network_socket_denial_proof,
                "production_pilot_audit_proof": production_pilot_audit_proof,
            }
        ),
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "production_state_changed": False,
        "execution_authorized": False,
    }


def create_production_pilot_readiness_summary(
    approval_gate: dict,
    production_pilot_audit_proof: dict,
    production_pilot_readiness_ledger: dict,
) -> dict:
    ready = (
        _gate_is_valid(approval_gate)
        and production_pilot_audit_proof.get("audit_status") == "PASS"
        and production_pilot_readiness_ledger.get("ledger_status")
        == "SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_LEDGER"
    )
    return {
        "production_pilot_readiness_summary_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED",
        "ready_for_credential_vault_denial_secret_handling_proof": ready,
        "gate_status": approval_gate.get("gate_status"),
        "audit_status": production_pilot_audit_proof.get("audit_status"),
        "ledger_status": production_pilot_readiness_ledger.get("ledger_status"),
        "next_layer": "Credential Vault Denial and Secret Handling Proof",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "production_state_changed": False,
        "execution_authorized": False,
    }


def create_credential_vault_denial_secret_handling_proof_bridge(
    result: dict,
    production_pilot_readiness_summary: dict,
) -> dict:
    ready = production_pilot_readiness_summary.get("ready_for_credential_vault_denial_secret_handling_proof") is True
    return {
        "credential_vault_denial_secret_handling_proof_bridge_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "current_layer": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PHASE,
        "next_layer": "Credential Vault Denial and Secret Handling Proof",
        "ready_for_credential_vault_denial_secret_handling_proof": ready,
        "required_next_capabilities": [
            "credential vault denial schema",
            "secret handling proof schema",
            "credential access denial contract",
            "secret read denial contract",
            "environment variable denial contract",
            "credential vault audit proof",
            "secret handling audit proof",
            "credential and secret denial ledger",
        ],
        "non_goals_for_next_layer": [
            "no real credential access",
            "no secret reads",
            "no environment reads",
            "no live API calls",
            "no network access",
            "no deployment",
            "no production execution",
            "no full workforce activation",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "production_execution_performed": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }


def create_supervised_production_pilot_readiness_review_bundle(
    result: dict,
    command: str | None = None,
    production_readiness_label: str | None = None,
    confirmation_token: str | None = None,
    candidate_label: str | None = None,
    required_production_pilot_reviewer: str | None = None,
    blast_radius_label: str | None = None,
) -> dict:
    command = command if command is not None else result.get("command", "")
    production_readiness_label = production_readiness_label or "station-chief-supervised-production-pilot-readiness-review"
    schema = create_supervised_production_pilot_readiness_review_schema()
    approval_gate = create_supervised_production_pilot_readiness_review_approval_gate(
        production_readiness_label,
        confirmation_token=confirmation_token,
    )
    minimum_candidate_contract = create_minimum_viable_production_candidate_contract(
        approval_gate,
        candidate_label=candidate_label,
    )
    human_review_gate = create_human_production_pilot_review_gate(
        approval_gate,
        required_production_pilot_reviewer=required_production_pilot_reviewer,
    )
    blast_radius_analysis = create_production_blast_radius_analysis(
        approval_gate,
        blast_radius_label=blast_radius_label,
    )
    live_action_denial_review = create_live_action_denial_review(approval_gate)
    rollback_availability_review = create_rollback_availability_review(approval_gate)
    credential_secret_readiness_denial_proof = create_credential_secret_readiness_denial_proof(approval_gate)
    network_socket_readiness_denial_proof = create_network_socket_readiness_denial_proof(approval_gate)
    production_pilot_audit_proof = create_production_pilot_audit_proof(
        approval_gate,
        minimum_candidate_contract,
        human_review_gate,
        blast_radius_analysis,
        live_action_denial_review,
        rollback_availability_review,
        credential_secret_readiness_denial_proof,
        network_socket_readiness_denial_proof,
    )
    production_pilot_readiness_ledger = create_production_pilot_readiness_ledger(
        approval_gate,
        minimum_candidate_contract,
        human_review_gate,
        blast_radius_analysis,
        live_action_denial_review,
        rollback_availability_review,
        credential_secret_readiness_denial_proof,
        network_socket_readiness_denial_proof,
        production_pilot_audit_proof,
    )
    production_pilot_readiness_summary = create_production_pilot_readiness_summary(
        approval_gate,
        production_pilot_audit_proof,
        production_pilot_readiness_ledger,
    )
    credential_vault_denial_secret_handling_proof_bridge = create_credential_vault_denial_secret_handling_proof_bridge(
        result,
        production_pilot_readiness_summary,
    )
    bundle = {
        "supervised_production_pilot_readiness_review_bundle_version": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION,
        "supervised_production_pilot_readiness_review_status": SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_STATUS,
        "command": command,
        "production_readiness_label": production_readiness_label,
        "supervised_production_pilot_readiness_review_schema": schema,
        "supervised_production_pilot_readiness_review_approval_gate": approval_gate,
        "minimum_viable_production_candidate_contract": minimum_candidate_contract,
        "human_production_pilot_review_gate": human_review_gate,
        "production_blast_radius_analysis": blast_radius_analysis,
        "live_action_denial_review": live_action_denial_review,
        "rollback_availability_review": rollback_availability_review,
        "credential_secret_readiness_denial_proof": credential_secret_readiness_denial_proof,
        "network_socket_readiness_denial_proof": network_socket_readiness_denial_proof,
        "production_pilot_audit_proof": production_pilot_audit_proof,
        "production_pilot_readiness_ledger": production_pilot_readiness_ledger,
        "production_pilot_readiness_summary": production_pilot_readiness_summary,
        "credential_vault_denial_secret_handling_proof_bridge": credential_vault_denial_secret_handling_proof_bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    return bundle
