#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re

LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_MODULE_VERSION = "3.5.0"
LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_STATUS = "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PREVIEW_ONLY"
LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PHASE = "Limited External Tool Supervised Pilot"
LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN = "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_tool_pilot_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "limited-external-tool-supervised-pilot"


def generate_limited_external_tool_supervised_pilot_id(
    command: str,
    tool_pilot_label: str,
    runtime_version: str = "3.5.0",
) -> str:
    normalized_tool_pilot_label = normalize_tool_pilot_label(tool_pilot_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{normalized_tool_pilot_label}")[:12]
    return f"limited-external-tool-supervised-pilot-v3-4-{normalized_tool_pilot_label}-{digest}"


def create_limited_external_tool_supervised_pilot_schema() -> dict:
    return {
        "limited_external_tool_supervised_pilot_schema_version": "3.5.0",
        "schema_status": LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_STATUS,
        "required_sections": [
            "limited_external_tool_supervised_pilot_approval_gate",
            "single_external_tool_category_contract",
            "tool_invocation_denial_by_default",
            "human_tool_use_preflight_gate",
            "tool_request_envelope_preview",
            "tool_response_quarantine_preview",
            "tool_audit_proof",
            "tool_pilot_ledger",
            "tool_pilot_readiness_summary",
            "supervised_external_api_pilot_bridge",
        ],
        "allowed_tool_pilot_modes": [
            "schema_only",
            "local_tool_pilot_records",
            "approved_tool_pilot_records",
            "single_tool_category_contract_preview",
            "tool_request_envelope_preview",
            "tool_response_quarantine_preview",
            "tool_audit_preview",
        ],
        "blocked_tool_pilot_modes": [
            "real_external_tool_invocation",
            "live_api_call",
            "network_access",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "deployment",
            "production_execution",
            "production_activation",
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
            "external_tool_replay",
            "full_workforce_activation",
        ],
        "required_confirmation_tokens": [
            LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN,
        ],
        "single_tool_category_limit": 1,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_limited_external_tool_supervised_pilot_approval_gate(
    tool_pilot_label: str,
    confirmation_token: str | None = None,
) -> dict:
    token_valid = confirmation_token == LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN
    gate_status = (
        "APPROVED_FOR_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_RECORDS"
        if token_valid
        else "BLOCKED_PENDING_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL"
    )
    return {
        "limited_external_tool_supervised_pilot_approval_gate_version": "3.5.0",
        "tool_pilot_label": tool_pilot_label,
        "gate_status": gate_status,
        "confirmation_token_required": LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_tool_pilot_records_authorized": token_valid,
        "real_external_tool_invocation_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
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


def create_single_external_tool_category_contract(
    approval_gate: dict,
    tool_category_label: str | None = None,
) -> dict:
    if tool_category_label is None:
        tool_category_label = "local-json-artifact-review"
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    contract_status = "TOOL_CATEGORY_CONTRACT_CREATED" if gate_valid else "BLOCKED"
    return {
        "single_external_tool_category_contract_version": "3.5.0",
        "contract_status": contract_status,
        "tool_category_label": tool_category_label,
        "single_tool_category_limit": 1,
        "tool_category_count": 1 if gate_valid else 0,
        "preview_only": True,
        "real_external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "execution_authorized": False,
    }


def create_tool_invocation_denial_by_default(
    approval_gate: dict,
    tool_category_contract: dict,
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    contract_created = tool_category_contract.get("contract_status") == "TOOL_CATEGORY_CONTRACT_CREATED"
    denial_status = "TOOL_INVOCATION_DENIED_BY_DEFAULT" if gate_valid and contract_created else "BLOCKED"
    return {
        "tool_invocation_denial_by_default_version": "3.5.0",
        "denial_status": denial_status,
        "external_tool_invocation_default": "DENIED",
        "real_external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "shell_command_allowed": False,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }


def create_human_tool_use_preflight_gate(
    approval_gate: dict,
    required_tool_preflight_approver: str | None = None,
) -> dict:
    if required_tool_preflight_approver is None:
        required_tool_preflight_approver = "Devin O’Rourke / explicit human operator"
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    preflight_status = "TOOL_USE_PREFLIGHT_REQUIREMENT_CREATED" if gate_valid else "BLOCKED"
    return {
        "human_tool_use_preflight_gate_version": "3.5.0",
        "preflight_status": preflight_status,
        "required_tool_preflight_approver": required_tool_preflight_approver,
        "human_tool_use_preflight_required": True,
        "current_preflight_grants_tool_invocation": False,
        "external_tool_invocation_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "approval_bypass_allowed": False,
        "execution_authorized": False,
    }


def create_tool_request_envelope_preview(
    approval_gate: dict,
    tool_category_contract: dict,
    tool_request_label: str | None = None,
) -> dict:
    if tool_request_label is None:
        tool_request_label = "single supervised tool request preview"
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    contract_created = tool_category_contract.get("contract_status") == "TOOL_CATEGORY_CONTRACT_CREATED"
    envelope_status = "TOOL_REQUEST_ENVELOPE_PREVIEW_CREATED" if gate_valid and contract_created else "BLOCKED"
    return {
        "tool_request_envelope_preview_version": "3.5.0",
        "envelope_status": envelope_status,
        "tool_request_label": tool_request_label,
        "request_preview_only": True,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }


def create_tool_response_quarantine_preview(
    approval_gate: dict,
    quarantine_labels: list[str] | None = None,
) -> dict:
    if quarantine_labels is None:
        quarantine_labels = [
            "quarantine tool request envelope",
            "deny tool invocation",
            "deny live-API call",
            "deny network access",
            "deny credential use",
            "require human review",
            "preserve tool pilot audit ledger",
            "preserve locked baseline",
        ]
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    preview_status = "TOOL_RESPONSE_QUARANTINE_PREVIEW_CREATED" if gate_valid else "BLOCKED"
    return {
        "tool_response_quarantine_preview_version": "3.5.0",
        "preview_status": preview_status,
        "quarantine_records": list(quarantine_labels),
        "quarantine_record_count": len(quarantine_labels),
        "quarantine_preview_only": True,
        "real_external_response_received": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rolled_back": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_tool_audit_proof(
    approval_gate: dict,
    tool_category_contract: dict,
    tool_invocation_denial: dict,
    human_tool_use_preflight_gate: dict,
    tool_request_envelope_preview: dict,
    tool_response_quarantine_preview: dict,
) -> dict:
    approval_gate_valid = approval_gate.get("confirmation_token_valid") is True
    single_tool_category_contract_created = tool_category_contract.get("contract_status") == "TOOL_CATEGORY_CONTRACT_CREATED"
    tool_invocation_denied_by_default = tool_invocation_denial.get("denial_status") == "TOOL_INVOCATION_DENIED_BY_DEFAULT"
    human_tool_use_preflight_required = human_tool_use_preflight_gate.get("preflight_status") == "TOOL_USE_PREFLIGHT_REQUIREMENT_CREATED"
    tool_request_envelope_preview_created = tool_request_envelope_preview.get("envelope_status") == "TOOL_REQUEST_ENVELOPE_PREVIEW_CREATED"
    tool_response_quarantine_preview_created = tool_response_quarantine_preview.get("preview_status") == "TOOL_RESPONSE_QUARANTINE_PREVIEW_CREATED"

    safety_checks = {
        "approval_gate_valid": approval_gate_valid,
        "single_tool_category_contract_created": single_tool_category_contract_created,
        "tool_invocation_denied_by_default": tool_invocation_denied_by_default,
        "human_tool_use_preflight_required": human_tool_use_preflight_required,
        "tool_request_envelope_preview_created": tool_request_envelope_preview_created,
        "tool_response_quarantine_preview_created": tool_response_quarantine_preview_created,
        "no_real_external_tool_invocation": all(
            section.get("real_external_tool_invocation_performed", False) is False
            and section.get("external_tool_invocation_performed", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_live_api_call": all(
            section.get("live_api_call_performed", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_network_access": all(
            section.get("network_access_performed", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_socket_opened": all(
            section.get("socket_opened", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
                tool_response_quarantine_preview,
            ]
        ),
        "no_credentials_used": all(
            section.get("credentials_used", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_secrets_read": all(
            section.get("secrets_read", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_environment_read": all(
            section.get("environment_read", False) is False
            for section in [
                tool_invocation_denial,
                tool_request_envelope_preview,
            ]
        ),
        "no_deployment": all(
            section.get("deployment_performed", False) is False
            and section.get("deployment_allowed", False) is False
            for section in [
                tool_category_contract,
                tool_invocation_denial,
                tool_request_envelope_preview,
                tool_response_quarantine_preview,
            ]
        ),
        "no_production_execution": tool_category_contract.get("execution_authorized") is False,
        "no_production_activation": approval_gate.get("production_activation_authorized", False) is False,
        "no_real_task_execution": approval_gate.get("real_task_execution_authorized", False) is False,
        "no_live_task_assignment": approval_gate.get("live_task_assignment_authorized", False) is False,
        "no_live_worker_routing": approval_gate.get("live_worker_routing_authorized", False) is False,
        "no_live_orchestration": approval_gate.get("live_orchestration_authorized", False) is False,
        "no_repo_modifications": all(
            section.get("repo_files_modified", False) is False
            for section in [
                approval_gate,
                tool_category_contract,
                tool_invocation_denial,
                human_tool_use_preflight_gate,
                tool_request_envelope_preview,
                tool_response_quarantine_preview,
            ]
            if isinstance(section, dict)
        ),
    }
    pass_all = all(safety_checks.values())
    approval_digest = sha256_digest(approval_gate)
    category_digest = sha256_digest(tool_category_contract)
    denial_digest = sha256_digest(tool_invocation_denial)
    preflight_digest = sha256_digest(human_tool_use_preflight_gate)
    request_digest = sha256_digest(tool_request_envelope_preview)
    quarantine_digest = sha256_digest(tool_response_quarantine_preview)
    combined_tool_audit_digest = sha256_digest(
        {
            "approval_gate": approval_digest,
            "tool_category_contract": category_digest,
            "tool_invocation_denial": denial_digest,
            "human_tool_use_preflight_gate": preflight_digest,
            "tool_request_envelope_preview": request_digest,
            "tool_response_quarantine_preview": quarantine_digest,
        }
    )
    return {
        "tool_audit_proof_version": "3.5.0",
        "audit_status": "PASS" if pass_all else "BLOCKED",
        "approval_gate_digest": approval_digest,
        "tool_category_contract_digest": category_digest,
        "tool_invocation_denial_digest": denial_digest,
        "human_tool_use_preflight_gate_digest": preflight_digest,
        "tool_request_envelope_preview_digest": request_digest,
        "tool_response_quarantine_preview_digest": quarantine_digest,
        "combined_tool_audit_digest": combined_tool_audit_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_tool_pilot_ledger(
    approval_gate: dict,
    tool_category_contract: dict,
    tool_invocation_denial: dict,
    human_tool_use_preflight_gate: dict,
    tool_request_envelope_preview: dict,
    tool_response_quarantine_preview: dict,
    tool_audit_proof: dict,
) -> dict:
    ledger_status = (
        "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_LEDGER"
        if tool_audit_proof.get("audit_status") == "PASS"
        else "BLOCKED"
    )
    entries = [
        {
            "entry_type": "limited external tool supervised pilot approval gate entry",
            "digest": sha256_digest(approval_gate),
        },
        {
            "entry_type": "single external tool category contract entry",
            "digest": sha256_digest(tool_category_contract),
        },
        {
            "entry_type": "tool invocation denial by default entry",
            "digest": sha256_digest(tool_invocation_denial),
        },
        {
            "entry_type": "human tool-use preflight gate entry",
            "digest": sha256_digest(human_tool_use_preflight_gate),
        },
        {
            "entry_type": "tool request envelope preview entry",
            "digest": sha256_digest(tool_request_envelope_preview),
        },
        {
            "entry_type": "tool response quarantine preview entry",
            "digest": sha256_digest(tool_response_quarantine_preview),
        },
        {
            "entry_type": "tool audit proof entry",
            "digest": sha256_digest(tool_audit_proof),
        },
    ]
    ledger_digest = sha256_digest(entries)
    return {
        "tool_pilot_ledger_version": "3.5.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": ledger_digest,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False,
    }


def create_tool_pilot_readiness_summary(
    approval_gate: dict,
    tool_category_contract: dict,
    tool_audit_proof: dict,
    tool_pilot_ledger: dict,
) -> dict:
    ready = (
        approval_gate.get("confirmation_token_valid") is True
        and tool_category_contract.get("contract_status") == "TOOL_CATEGORY_CONTRACT_CREATED"
        and tool_audit_proof.get("audit_status") == "PASS"
        and tool_pilot_ledger.get("ledger_status") == "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_LEDGER"
    )
    return {
        "tool_pilot_readiness_summary_version": "3.5.0",
        "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED",
        "ready_for_supervised_external_api_pilot": ready,
        "gate_status": approval_gate.get("gate_status"),
        "tool_category_contract_status": tool_category_contract.get("contract_status"),
        "audit_status": tool_audit_proof.get("audit_status"),
        "ledger_status": tool_pilot_ledger.get("ledger_status"),
        "next_layer": "Supervised External API Pilot",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False,
    }


def create_supervised_external_api_pilot_bridge(
    result: dict,
    tool_pilot_readiness_summary: dict,
) -> dict:
    ready = tool_pilot_readiness_summary.get("readiness_status") == "READY_FOR_NEXT_LAYER"
    return {
        "supervised_external_api_pilot_bridge_version": "3.5.0",
        "current_layer": LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PHASE,
        "next_layer": "Supervised External API Pilot",
        "ready_for_supervised_external_api_pilot": ready,
        "required_next_capabilities": [
            "supervised external API pilot schema",
            "single API category contract",
            "credential denial by default",
            "secret handling denial by default",
            "network/socket denial by default",
            "human API-use preflight gate",
            "API request envelope preview",
            "API response quarantine preview",
            "API audit proof",
            "API pilot ledger",
        ],
        "non_goals_for_next_layer": [
            "no uncontrolled API access",
            "no live credentials",
            "no secret reads",
            "no unsupervised network calls",
            "no autonomous deployment",
            "no unsupervised orchestration",
            "no full workforce activation",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False,
        "command": result.get("command", ""),
    }


def create_limited_external_tool_supervised_pilot_bundle(
    result: dict,
    command: str | None = None,
    tool_pilot_label: str | None = None,
    confirmation_token: str | None = None,
    tool_category_label: str | None = None,
    required_tool_preflight_approver: str | None = None,
    tool_request_label: str | None = None,
    quarantine_labels: list[str] | None = None,
) -> dict:
    if command is None:
        command = result.get("command", "")
    if tool_pilot_label is None:
        tool_pilot_label = "station-chief-limited-external-tool-supervised-pilot"

    schema = create_limited_external_tool_supervised_pilot_schema()
    approval_gate = create_limited_external_tool_supervised_pilot_approval_gate(
        tool_pilot_label=tool_pilot_label,
        confirmation_token=confirmation_token,
    )
    tool_category_contract = create_single_external_tool_category_contract(
        approval_gate=approval_gate,
        tool_category_label=tool_category_label,
    )
    tool_invocation_denial = create_tool_invocation_denial_by_default(approval_gate, tool_category_contract)
    human_tool_use_preflight_gate = create_human_tool_use_preflight_gate(
        approval_gate=approval_gate,
        required_tool_preflight_approver=required_tool_preflight_approver,
    )
    tool_request_envelope_preview = create_tool_request_envelope_preview(
        approval_gate=approval_gate,
        tool_category_contract=tool_category_contract,
        tool_request_label=tool_request_label,
    )
    tool_response_quarantine_preview = create_tool_response_quarantine_preview(
        approval_gate=approval_gate,
        quarantine_labels=quarantine_labels,
    )
    tool_audit_proof = create_tool_audit_proof(
        approval_gate=approval_gate,
        tool_category_contract=tool_category_contract,
        tool_invocation_denial=tool_invocation_denial,
        human_tool_use_preflight_gate=human_tool_use_preflight_gate,
        tool_request_envelope_preview=tool_request_envelope_preview,
        tool_response_quarantine_preview=tool_response_quarantine_preview,
    )
    tool_pilot_ledger = create_tool_pilot_ledger(
        approval_gate=approval_gate,
        tool_category_contract=tool_category_contract,
        tool_invocation_denial=tool_invocation_denial,
        human_tool_use_preflight_gate=human_tool_use_preflight_gate,
        tool_request_envelope_preview=tool_request_envelope_preview,
        tool_response_quarantine_preview=tool_response_quarantine_preview,
        tool_audit_proof=tool_audit_proof,
    )
    tool_pilot_readiness_summary = create_tool_pilot_readiness_summary(
        approval_gate=approval_gate,
        tool_category_contract=tool_category_contract,
        tool_audit_proof=tool_audit_proof,
        tool_pilot_ledger=tool_pilot_ledger,
    )
    supervised_external_api_pilot_bridge = create_supervised_external_api_pilot_bridge(
        result=result,
        tool_pilot_readiness_summary=tool_pilot_readiness_summary,
    )
    pilot_id = generate_limited_external_tool_supervised_pilot_id(
        command=command,
        tool_pilot_label=tool_pilot_label,
    )
    return {
        "limited_external_tool_supervised_pilot_bundle_version": "3.5.0",
        "limited_external_tool_supervised_pilot_status": LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_STATUS,
        "limited_external_tool_supervised_pilot_id": pilot_id,
        "command": command,
        "tool_pilot_label": tool_pilot_label,
        "limited_external_tool_supervised_pilot_schema": schema,
        "limited_external_tool_supervised_pilot_approval_gate": approval_gate,
        "single_external_tool_category_contract": tool_category_contract,
        "tool_invocation_denial_by_default": tool_invocation_denial,
        "human_tool_use_preflight_gate": human_tool_use_preflight_gate,
        "tool_request_envelope_preview": tool_request_envelope_preview,
        "tool_response_quarantine_preview": tool_response_quarantine_preview,
        "tool_audit_proof": tool_audit_proof,
        "tool_pilot_ledger": tool_pilot_ledger,
        "tool_pilot_readiness_summary": tool_pilot_readiness_summary,
        "supervised_external_api_pilot_bridge": supervised_external_api_pilot_bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
