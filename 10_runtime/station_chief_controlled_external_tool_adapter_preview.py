#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re

CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_MODULE_VERSION = "3.0.0"
CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_STATUS = "CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_ONLY"
CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_PHASE = "Controlled External Tool Adapter Preview"
CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    payload = data if isinstance(data, str) else canonical_json(data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_external_tool_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "controlled-external-tool-adapter-preview"


def generate_external_tool_preview_id(command: str, tool_label: str, runtime_version: str = "3.0.0") -> str:
    normalized_tool_label = normalize_external_tool_label(tool_label)
    digest = hashlib.sha256(f"{runtime_version}:{command}:{tool_label}".encode("utf-8")).hexdigest()
    return f"external-tool-preview-v3-0-{normalized_tool_label}-{digest[:12]}"


def create_controlled_external_tool_adapter_preview_schema() -> dict:
    return {
        "controlled_external_tool_adapter_preview_schema_version": "3.0.0",
        "schema_status": CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_STATUS,
        "required_sections": [
            "external_tool_adapter_preview_approval_gate",
            "external_tool_dry_run_adapter_registry",
            "per_tool_external_permission_gate",
            "external_request_preview_contract",
            "external_response_validation_schema",
            "external_response_validation_preview_result",
            "external_tool_abort_contract",
            "external_tool_audit_proof",
            "external_tool_preview_ledger",
            "external_tool_preview_readiness_summary",
            "permissioned_external_api_dry_run_preview_readiness_bridge",
        ],
        "allowed_preview_modes": [
            "schema_only",
            "local_external_tool_preview",
            "approved_external_tool_adapter_preview_records",
            "external_request_contract_preview",
            "external_response_validation_preview",
            "external_tool_audit_preview",
        ],
        "blocked_preview_modes": [
            "live_external_api_execution",
            "real_external_tool_invocation",
            "network_request",
            "sock_connection",
            "shell_command_adapter",
            "repo_mutating_adapter",
            "deployment_adapter",
            "secret_read_adapter",
            "background_adapter_process",
            "autonomous_external_retry",
            "production_external_tool_execution",
        ],
        "required_confirmation_tokens": [
            CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL_TOKEN,
        ],
        "safety_invariants": [
            "preview records only",
            "no live-API calls",
            "no external tool invocation",
            "no network access",
            "no-sock-access",
            "no shell commands",
            "no secret reads",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "no live orchestration",
            "external tool adapter preview does not authorize external execution",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }


def create_external_tool_adapter_preview_approval_gate(
    tool_label: str,
    confirmation_token: str | None = None,
) -> dict:
    token_valid = confirmation_token == CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL_TOKEN
    return {
        "external_tool_adapter_preview_approval_gate_version": "3.0.0",
        "tool_label": tool_label,
        "gate_status": (
            "APPROVED_FOR_EXTERNAL_TOOL_ADAPTER_PREVIEW_RECORDS"
            if token_valid
            else "BLOCKED_PENDING_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL"
        ),
        "confirmation_token_required": CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_external_tool_preview_records_authorized": token_valid,
        "external_tool_invocation_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "sock_access_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "broad_worker_activation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_external_tool_dry_run_adapter_registry(
    approval_gate: dict,
    requested_tools: list[str] | None = None,
) -> dict:
    requested_tools = requested_tools or [
        "github_read_preview",
        "gmail_read_preview",
        "calendar_read_preview",
        "file_search_preview",
        "web_search_preview",
    ]
    token_valid = approval_gate.get("confirmation_token_valid") is True
    adapter_entries: list[dict] = []
    if token_valid:
        for index, tool_id in enumerate(requested_tools, start=1):
            adapter_entries.append(
                {
                    "tool_id": tool_id,
                    "tool_status": "PREVIEW_ONLY",
                    "live_invocation_allowed": False,
                    "external_actions_taken": False,
                    "tool_preview_id": generate_external_tool_preview_id(tool_id, tool_id),
                    "tool_index": index,
                }
            )
        registry_status = "REGISTRY_CREATED"
    else:
        registry_status = "BLOCKED"
    registry = {
        "external_tool_dry_run_adapter_registry_version": "3.0.0",
        "registry_status": registry_status,
        "requested_tools": requested_tools,
        "adapter_entries": adapter_entries,
        "adapter_count": len(adapter_entries),
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    registry["registry_digest"] = sha256_digest({k: v for k, v in registry.items() if k != "registry_digest"})
    return registry


def create_per_tool_external_permission_gate(
    approval_gate: dict,
    tool_id: str,
    requested_external_action: str | None = None,
) -> dict:
    requested_external_action = requested_external_action or "preview_request_contract"
    token_valid = approval_gate.get("confirmation_token_valid") is True
    permission_status = "PREVIEW_PERMISSION_BOUND" if token_valid and requested_external_action == "preview_request_contract" else "BLOCKED"
    return {
        "per_tool_external_permission_gate_version": "3.0.0",
        "tool_id": tool_id,
        "requested_external_action": requested_external_action,
        "permission_status": permission_status,
        "allowed_preview_actions": [
            "preview_request_contract",
            "preview_response_validation",
            "preview_audit_record",
        ],
        "blocked_live_actions": [
            "live_api_call",
            "network_request",
            "sock_connection",
            "credential_read",
            "shell_command",
            "repo_mutation",
            "deployment",
            "production_tool_execution",
        ],
        "external_tool_invocation_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "sock_access_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_external_request_preview_contract(
    approval_gate: dict,
    tool_id: str,
    request_label: str | None = None,
    request_payload: dict | None = None,
) -> dict:
    request_label = request_label or "preview-request"
    request_payload = request_payload or {}
    token_valid = approval_gate.get("confirmation_token_valid") is True
    request_contract_status = "CONTRACT_CREATED" if token_valid else "BLOCKED"
    payload_digest = sha256_digest(request_payload)
    request_preview_digest = sha256_digest(
        {
            "tool_id": tool_id,
            "request_label": request_label,
            "request_payload_digest": payload_digest,
        }
    )
    return {
        "external_request_preview_contract_version": "3.0.0",
        "tool_id": tool_id,
        "request_label": request_label,
        "request_contract_status": request_contract_status,
        "request_payload_digest": payload_digest,
        "request_preview_digest": request_preview_digest,
        "request_sent": False,
        "network_access_performed": False,
        "sock_opened": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_external_response_validation_schema() -> dict:
    return {
        "external_response_validation_schema_version": "3.0.0",
        "schema_status": "VALIDATION_SCHEMA_ONLY",
        "required_response_fields": [
            "tool_id",
            "response_status",
            "response_payload",
            "response_digest",
            "external_actions_taken",
            "live_api_call_performed",
            "repo_files_modified",
            "execution_authorized",
        ],
        "blocked_response_content": [
            "secrets",
            "credentials",
            "API-keys",
            "tokens",
            "private keys",
            "env-vars",
            "shell output",
            "deployment URLs from live deployment",
            "real network response bodies",
        ],
        "safety_checks": [
            "required fields present",
            "response digest matches payload",
            "external actions false",
            "live-API call false",
            "repo files modified false",
            "execution authorized false",
            "no blocked content indicators",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "execution_authorized": False,
    }


def create_external_response_validation_preview_result(
    response_preview: dict | None = None,
    validation_schema: dict | None = None,
) -> dict:
    response_preview = response_preview or {}
    validation_schema = validation_schema or create_external_response_validation_schema()
    response_preview_present = bool(response_preview)
    if not response_preview_present:
        return {
            "external_response_validation_preview_result_version": "3.0.0",
            "validation_status": "PASS",
            "response_preview_present": False,
            "response_count": 0,
            "response_checks": ["empty preview accepted"],
            "blocked_indicators": [],
            "response_fetch_performed": False,
            "external_tool_invoked": False,
            "live_api_call_performed": False,
            "network_access_performed": False,
            "external_actions_taken": False,
            "repo_files_modified": False,
            "execution_authorized": False,
        }
    response_checks: list[str] = []
    blocked_indicators: list[str] = []
    required_fields = validation_schema.get("required_response_fields", [])
    missing_fields = [field for field in required_fields if field not in response_preview]
    if missing_fields:
        response_checks.append(f"missing fields: {', '.join(missing_fields)}")
    else:
        response_checks.append("required fields present")
    payload = response_preview.get("response_payload", {})
    expected_digest = sha256_digest(payload)
    digest_matches = response_preview.get("response_digest") == expected_digest
    response_checks.append("response digest matches payload" if digest_matches else "response digest mismatch")
    lowered = canonical_json(response_preview).lower()
    for needle in ["secret", "api_key", "token=", "password", "begin private key", "credential", "shell output", "deployment_url"]:
        if needle in lowered:
            blocked_indicators.append(needle)
    if response_preview.get("external_actions_taken"):
        response_checks.append("external actions detected")
    else:
        response_checks.append("external actions false")
    if response_preview.get("live_api_call_performed"):
        response_checks.append("live api call detected")
    else:
        response_checks.append("live api call false")
    if response_preview.get("repo_files_modified"):
        response_checks.append("repo files modified")
    else:
        response_checks.append("repo files modified false")
    if response_preview.get("execution_authorized"):
        response_checks.append("execution authorized")
    else:
        response_checks.append("execution authorized false")
    valid = not missing_fields and digest_matches and not blocked_indicators and response_preview.get("external_actions_taken") is False and response_preview.get("live_api_call_performed") is False and response_preview.get("repo_files_modified") is False and response_preview.get("execution_authorized") is False
    return {
        "external_response_validation_preview_result_version": "3.0.0",
        "validation_status": "PASS" if valid else "BLOCKED",
        "response_preview_present": True,
        "response_count": 1,
        "response_checks": response_checks,
        "blocked_indicators": blocked_indicators,
        "response_fetch_performed": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_external_tool_abort_contract(
    approval_gate: dict,
    permission_gate: dict,
    abort_reason: str | None = None,
) -> dict:
    abort_reason = abort_reason or "No external tool action started; abort contract prepared."
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    return {
        "external_tool_abort_contract_version": "3.0.0",
        "contract_status": "READY" if gate_valid else "BLOCKED",
        "abort_reason": abort_reason,
        "abort_steps": [
            "stop creating new external preview records",
            "mark preview as blocked if validation fails",
            "preserve request preview contract",
            "preserve response validation result",
            "require human review",
            "do not retry automatically",
        ],
        "external_request_cancelled": False,
        "processes_terminated": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_external_tool_audit_proof(
    approval_gate: dict,
    adapter_registry: dict,
    permission_gate: dict,
    request_contract: dict,
    validation_schema: dict,
    validation_result: dict,
    abort_contract: dict,
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    registry_created = adapter_registry.get("registry_status") == "REGISTRY_CREATED"
    permission_bound = permission_gate.get("permission_status") == "PREVIEW_PERMISSION_BOUND"
    request_created = request_contract.get("request_contract_status") == "CONTRACT_CREATED"
    validation_passed = validation_result.get("validation_status") == "PASS"
    abort_ready = abort_contract.get("contract_status") == "READY"
    no_external_actions = not any(
        [
            approval_gate.get("external_actions_taken"),
            adapter_registry.get("external_actions_taken"),
            permission_gate.get("external_actions_taken"),
            request_contract.get("external_actions_taken"),
            validation_result.get("external_actions_taken"),
            abort_contract.get("external_actions_taken"),
        ]
    )
    no_external_tool_invocation = not any(
        [
            adapter_registry.get("external_tool_invoked"),
            permission_gate.get("external_tool_invocation_authorized"),
            request_contract.get("external_tool_invoked"),
            validation_result.get("external_tool_invoked"),
            abort_contract.get("external_tool_invoked"),
        ]
    )
    no_live_api_call = not any(
        [
            adapter_registry.get("live_api_call_performed"),
            permission_gate.get("live_api_call_authorized"),
            request_contract.get("live_api_call_performed"),
            validation_result.get("live_api_call_performed"),
            abort_contract.get("live_api_call_performed"),
        ]
    )
    no_network_access = not any(
        [
            adapter_registry.get("network_access_performed"),
            permission_gate.get("network_access_authorized"),
            request_contract.get("network_access_performed"),
            validation_result.get("network_access_performed"),
        ]
    )
    no_sock_opened = not any(
        [
            approval_gate.get("sock_access_authorized"),
            request_contract.get("sock_opened"),
            validation_result.get("sock_opened"),
        ]
    )
    no_repo_modifications = not any(
        [
            adapter_registry.get("repo_files_modified"),
            permission_gate.get("repo_files_modified"),
            request_contract.get("repo_files_modified"),
            validation_result.get("repo_files_modified"),
            abort_contract.get("repo_files_modified"),
        ]
    )
    no_deployment = not any(
        [
            approval_gate.get("deployment_authorized"),
            adapter_registry.get("deployment_performed"),
            permission_gate.get("deployment_authorized"),
        ]
    )
    audit_status = "PASS" if all([
        gate_valid,
        registry_created,
        permission_bound,
        request_created,
        validation_passed,
        abort_ready,
        no_external_actions,
        no_external_tool_invocation,
        no_live_api_call,
        no_network_access,
        no_sock_opened,
        no_repo_modifications,
        no_deployment,
    ]) else "BLOCKED"
    proof = {
        "external_tool_audit_proof_version": "3.0.0",
        "audit_status": audit_status,
        "approval_gate_digest": sha256_digest(approval_gate),
        "adapter_registry_digest": sha256_digest(adapter_registry),
        "permission_gate_digest": sha256_digest(permission_gate),
        "request_contract_digest": sha256_digest(request_contract),
        "validation_schema_digest": sha256_digest(validation_schema),
        "validation_result_digest": sha256_digest(validation_result),
        "abort_contract_digest": sha256_digest(abort_contract),
        "combined_external_tool_audit_digest": sha256_digest(
            {
                "approval_gate": approval_gate,
                "adapter_registry": adapter_registry,
                "permission_gate": permission_gate,
                "request_contract": request_contract,
                "validation_schema": validation_schema,
                "validation_result": validation_result,
                "abort_contract": abort_contract,
            }
        ),
        "safety_checks": {
            "approval_gate_valid": gate_valid,
            "adapter_registry_created": registry_created,
            "permission_gate_bound": permission_bound,
            "request_contract_created": request_created,
            "validation_result_passed": validation_passed,
            "abort_contract_available": abort_ready,
            "no_external_actions": no_external_actions,
            "no_external_tool_invocation": no_external_tool_invocation,
            "no_live_api_call": no_live_api_call,
            "no_network_access": no_network_access,
            "no_sock_opened": no_sock_opened,
            "no_repo_modifications": no_repo_modifications,
            "no_deployment": no_deployment,
        },
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }
    return proof


def create_external_tool_preview_ledger(
    approval_gate: dict,
    adapter_registry: dict,
    permission_gate: dict,
    request_contract: dict,
    validation_result: dict,
    audit_proof: dict,
) -> dict:
    status = "CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_LEDGER" if audit_proof.get("audit_status") == "PASS" else "BLOCKED"
    ledger = {
        "external_tool_preview_ledger_version": "3.0.0",
        "ledger_status": status,
        "entries": [
            {"entry_type": "external_tool_adapter_preview_approval_gate", "entry_digest": sha256_digest(approval_gate)},
            {"entry_type": "external_tool_dry_run_adapter_registry", "entry_digest": sha256_digest(adapter_registry)},
            {"entry_type": "per_tool_external_permission_gate", "entry_digest": sha256_digest(permission_gate)},
            {"entry_type": "external_request_preview_contract", "entry_digest": sha256_digest(request_contract)},
            {"entry_type": "external_response_validation_preview_result", "entry_digest": sha256_digest(validation_result)},
            {"entry_type": "external_tool_audit_proof", "entry_digest": sha256_digest(audit_proof)},
        ],
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    ledger["ledger_digest"] = sha256_digest({k: v for k, v in ledger.items() if k != "ledger_digest"})
    return ledger


def create_external_tool_preview_readiness_summary(
    approval_gate: dict,
    audit_proof: dict,
    preview_ledger: dict,
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid") is True
    audit_status = audit_proof.get("audit_status")
    ledger_status = preview_ledger.get("ledger_status")
    ready = gate_valid and audit_status == "PASS" and ledger_status == "CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_LEDGER"
    return {
        "external_tool_preview_readiness_summary_version": "3.0.0",
        "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED",
        "ready_for_permissioned_external_api_dry_run_preview": ready,
        "gate_status": approval_gate.get("gate_status"),
        "audit_status": audit_status,
        "ledger_status": ledger_status,
        "next_layer": "Permissioned External API Dry-Run Preview",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_permissioned_external_api_dry_run_preview_readiness_bridge(
    result: dict,
    readiness_summary: dict,
) -> dict:
    ready = readiness_summary.get("ready_for_permissioned_external_api_dry_run_preview") is True
    return {
        "permissioned_external_api_dry_run_preview_readiness_bridge_version": "3.0.0",
        "current_layer": "Controlled External Tool Adapter Preview",
        "next_layer": "Permissioned External API Dry-Run Preview",
        "ready_for_permissioned_external_api_dry_run_preview": ready,
        "required_next_capabilities": [
            "permissioned external API dry-run schema",
            "API endpoint preview registry",
            "request envelope validation",
            "credential absence proof",
            "outbound call prevention proof",
            "dry-run response fixture contract",
            "external API audit proof",
            "still no live-API execution by default",
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no credential use",
            "no secret reads",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no live production orchestration",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_controlled_external_tool_adapter_preview_bundle(
    result: dict,
    command: str | None = None,
    tool_label: str | None = None,
    tool_id: str | None = None,
    confirmation_token: str | None = None,
    requested_tools: list[str] | None = None,
    requested_external_action: str | None = None,
    request_label: str | None = None,
    request_payload: dict | None = None,
    response_preview: dict | None = None,
    abort_reason: str | None = None,
) -> dict:
    command = command if command is not None else result.get("command", "")
    tool_label = tool_label or "station-chief-external-tool-preview"
    tool_id = tool_id or "web_search_preview"
    schema = create_controlled_external_tool_adapter_preview_schema()
    gate = create_external_tool_adapter_preview_approval_gate(tool_label, confirmation_token=confirmation_token)
    registry = create_external_tool_dry_run_adapter_registry(gate, requested_tools=requested_tools)
    permission_gate = create_per_tool_external_permission_gate(gate, tool_id, requested_external_action=requested_external_action)
    request_contract = create_external_request_preview_contract(gate, tool_id, request_label=request_label, request_payload=request_payload)
    validation_schema = create_external_response_validation_schema()
    validation_result = create_external_response_validation_preview_result(response_preview=response_preview, validation_schema=validation_schema)
    abort_contract = create_external_tool_abort_contract(gate, permission_gate, abort_reason=abort_reason)
    audit_proof = create_external_tool_audit_proof(gate, registry, permission_gate, request_contract, validation_schema, validation_result, abort_contract)
    preview_ledger = create_external_tool_preview_ledger(gate, registry, permission_gate, request_contract, validation_result, audit_proof)
    readiness_summary = create_external_tool_preview_readiness_summary(gate, audit_proof, preview_ledger)
    bridge = create_permissioned_external_api_dry_run_preview_readiness_bridge(result, readiness_summary)
    bundle = {
        "controlled_external_tool_adapter_preview_bundle_version": "3.0.0",
        "controlled_external_tool_adapter_preview_status": CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_STATUS,
        "command": command,
        "controlled_external_tool_adapter_preview_schema": schema,
        "external_tool_adapter_preview_approval_gate": gate,
        "external_tool_dry_run_adapter_registry": registry,
        "per_tool_external_permission_gate": permission_gate,
        "external_request_preview_contract": request_contract,
        "external_response_validation_schema": validation_schema,
        "external_response_validation_preview_result": validation_result,
        "external_tool_abort_contract": abort_contract,
        "external_tool_audit_proof": audit_proof,
        "external_tool_preview_ledger": preview_ledger,
        "external_tool_preview_readiness_summary": readiness_summary,
        "permissioned_external_api_dry_run_preview_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }
    bundle["controlled_external_tool_adapter_preview_bundle_digest"] = sha256_digest({k: v for k, v in bundle.items() if k != "controlled_external_tool_adapter_preview_bundle_digest"})
    return bundle
