"""
Station Chief Runtime v13.0 External Tool / API Pilot Hardening Candidate Module.
Metadata only. Deterministic. Non-executing.
"""

import hashlib
import json
import re
from pathlib import Path

STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION = "13.0.0"
STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_STATUS = "STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_LOCAL_DETERMINISTIC_ONLY"
STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_PHASE = "Station Chief v13.0 External Tool / API Pilot Hardening Candidate"
STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS = [
    "station-chief-external-interface-tool-adapter-preview-001",
    "station-chief-external-interface-api-contract-preview-002",
    "station-chief-external-interface-credential-denial-proof-003",
    "station-chief-external-interface-network-lockdown-proof-004",
]
STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS = [
    "station-chief-external-action-envelope-001",
    "station-chief-external-action-envelope-002",
    "station-chief-external-action-envelope-003",
    "station-chief-external-action-envelope-004",
]
STATION_CHIEF_V13_EXTERNAL_PILOT_DRY_RUN_PLAN_ID = "station-chief-external-pilot-dry-run-plan-001"
STATION_CHIEF_V13_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v13.1 or v14.0 requires explicit operator instruction"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = canonical_json(data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or default_label


def _interface_descriptor(interface_id: str, interface_name: str, interface_purpose: str) -> dict:
    return {
        "interface_id": interface_id,
        "interface_name": interface_name,
        "interface_type": "metadata_only_external_interface_descriptor",
        "interface_purpose": interface_purpose,
        "descriptor_only": True,
        "external_interface_registered": True,
        "real_tool_invocation_allowed": False,
        "external_tool_invocation_allowed": False,
        "api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "dns_resolution_allowed": False,
        "credential_access_allowed": False,
        "credential_vault_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "filesystem_mutation_allowed": False,
        "subprocess_allowed": False,
        "shell_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "arbitrary_task_allowed": False,
        "user_task_allowed": False,
    }


def create_external_interface_descriptor_registry() -> dict:
    registry = {
        STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[0]: _interface_descriptor(
            STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[0],
            "external_tool_adapter_preview",
            "Describe future supervised external tool adapter boundary without invoking a tool.",
        ),
        STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[1]: _interface_descriptor(
            STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[1],
            "api_contract_preview",
            "Describe future supervised API contract boundary without making a request.",
        ),
        STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[2]: _interface_descriptor(
            STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[2],
            "credential_denial_proof",
            "Describe credential/secret denial boundary without reading secrets or environment variables.",
        ),
        STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[3]: _interface_descriptor(
            STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[3],
            "network_lockdown_proof",
            "Describe network/socket/DNS denial boundary without network access.",
        ),
    }
    return registry


def _action_envelope(interface_id: str, envelope_id: str, envelope_index: int) -> dict:
    return {
        "external_action_envelope_id": envelope_id,
        "envelope_type": "metadata_only_external_action_envelope",
        "envelope_index": envelope_index,
        "bound_interface_id": interface_id,
        "envelope_payload": {
            "operation": "external_boundary_dry_run_metadata",
            "expected_result": "external_permission_receipt_recorded",
        },
        "descriptor_only": True,
        "dry_run_only": True,
        "live_execution_allowed": False,
        "real_tool_invocation_allowed": False,
        "external_tool_invocation_allowed": False,
        "api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "dns_resolution_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "filesystem_mutation_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "arbitrary_user_content_allowed": False,
        "arbitrary_task_allowed": False,
        "user_task_allowed": False,
        "execution_mode": "metadata_external_permission_receipt_only",
    }


def create_external_action_envelopes(interface_registry: dict) -> dict:
    envelopes = {}
    for index, envelope_id in enumerate(STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS, start=1):
        interface_id = STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[index - 1]
        envelopes[envelope_id] = _action_envelope(interface_id, envelope_id, index)
    return envelopes


def create_external_access_policy_gate(interface_registry: dict, action_envelopes: dict) -> dict:
    expected_interface_ids = list(STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS)
    expected_envelope_ids = list(STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS)
    interface_ids_ok = list(interface_registry.keys()) == expected_interface_ids
    envelope_ids_ok = list(action_envelopes.keys()) == expected_envelope_ids
    interface_fields_ok = all(
        interface.get("descriptor_only") is True
        and interface.get("external_interface_registered") is True
        and interface.get("real_tool_invocation_allowed") is False
        and interface.get("external_tool_invocation_allowed") is False
        and interface.get("api_call_allowed") is False
        and interface.get("network_access_allowed") is False
        and interface.get("socket_access_allowed") is False
        and interface.get("dns_resolution_allowed") is False
        and interface.get("credential_access_allowed") is False
        and interface.get("credential_vault_access_allowed") is False
        and interface.get("secret_read_allowed") is False
        and interface.get("environment_read_allowed") is False
        and interface.get("filesystem_mutation_allowed") is False
        and interface.get("subprocess_allowed") is False
        and interface.get("shell_allowed") is False
        and interface.get("production_allowed") is False
        and interface.get("deployment_allowed") is False
        and interface.get("arbitrary_task_allowed") is False
        and interface.get("user_task_allowed") is False
        for interface in interface_registry.values()
    )
    envelope_fields_ok = all(
        envelope.get("descriptor_only") is True
        and envelope.get("dry_run_only") is True
        and envelope.get("live_execution_allowed") is False
        and envelope.get("real_tool_invocation_allowed") is False
        and envelope.get("external_tool_invocation_allowed") is False
        and envelope.get("api_call_allowed") is False
        and envelope.get("network_access_allowed") is False
        and envelope.get("socket_access_allowed") is False
        and envelope.get("dns_resolution_allowed") is False
        and envelope.get("credential_access_allowed") is False
        and envelope.get("secret_read_allowed") is False
        and envelope.get("environment_read_allowed") is False
        and envelope.get("filesystem_mutation_allowed") is False
        and envelope.get("production_allowed") is False
        and envelope.get("deployment_allowed") is False
        and envelope.get("arbitrary_user_content_allowed") is False
        and envelope.get("arbitrary_task_allowed") is False
        and envelope.get("user_task_allowed") is False
        for envelope in action_envelopes.values()
    )
    bound_interfaces_ok = all(
        action_envelopes[envelope_id]["bound_interface_id"] == expected_interface_ids[index - 1]
        for index, envelope_id in enumerate(expected_envelope_ids, start=1)
    )
    external_metadata_authorized = all([
        len(interface_registry) == 4,
        len(action_envelopes) == 4,
        interface_ids_ok,
        envelope_ids_ok,
        interface_fields_ok,
        envelope_fields_ok,
        bound_interfaces_ok,
    ])
    return {
        "policy_gate_id": f"station-chief-v13-policy-gate-{sha256_digest({'interface_registry': interface_registry, 'action_envelopes': action_envelopes})[:16]}",
        "policy_gate_type": "metadata_only_external_tool_api_policy_gate",
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "interface_descriptor_count": len(interface_registry),
        "action_envelope_count": len(action_envelopes),
        "external_metadata_authorized": external_metadata_authorized,
        "real_tool_invocation_authorized": False,
        "external_tool_invocation_authorized": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "dns_resolution_authorized": False,
        "credential_access_authorized": False,
        "credential_vault_access_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "production_execution_authorized": False,
        "arbitrary_execution_authorized": False,
        "user_task_execution_authorized": False,
        "live_orchestration_authorized": False,
    }


def create_credential_secret_denial_proof(interface_registry: dict, action_envelopes: dict, policy_gate: dict) -> dict:
    context = {
        "interface_registry": interface_registry,
        "action_envelopes": action_envelopes,
        "policy_gate": policy_gate,
        "proof": "credential_secret_environment_denial",
    }
    return {
        "credential_secret_denial_proof_id": sha256_digest(context),
        "proof_type": "metadata_only_credential_secret_denial_proof",
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "credential_access_attempted": False,
        "credential_vault_access_attempted": False,
        "secret_read_attempted": False,
        "environment_read_attempted": False,
        "credential_access_authorized": False,
        "credential_vault_access_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "proof_status": "CREDENTIAL_SECRET_ENVIRONMENT_ACCESS_DENIED",
        "external_metadata_authorized": policy_gate.get("external_metadata_authorized") is True,
    }


def create_network_api_denial_proof(interface_registry: dict, action_envelopes: dict, policy_gate: dict) -> dict:
    context = {
        "interface_registry": interface_registry,
        "action_envelopes": action_envelopes,
        "policy_gate": policy_gate,
        "proof": "network_api_socket_dns_denial",
    }
    return {
        "network_api_denial_proof_id": sha256_digest(context),
        "proof_type": "metadata_only_network_api_denial_proof",
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "api_call_attempted": False,
        "network_access_attempted": False,
        "socket_access_attempted": False,
        "dns_resolution_attempted": False,
        "outbound_connection_attempted": False,
        "inbound_connection_attempted": False,
        "webhook_call_attempted": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "dns_resolution_authorized": False,
        "proof_status": "NETWORK_API_SOCKET_DNS_ACCESS_DENIED",
        "external_metadata_authorized": policy_gate.get("external_metadata_authorized") is True,
    }


def create_external_pilot_dry_run_plan(interface_registry: dict, action_envelopes: dict, policy_gate: dict, credential_secret_denial_proof: dict, network_api_denial_proof: dict) -> dict:
    context = {
        "interface_registry": interface_registry,
        "action_envelopes": action_envelopes,
        "policy_gate": policy_gate,
        "credential_secret_denial_proof": credential_secret_denial_proof,
        "network_api_denial_proof": network_api_denial_proof,
    }
    return {
        "external_pilot_dry_run_plan_id": STATION_CHIEF_V13_EXTERNAL_PILOT_DRY_RUN_PLAN_ID,
        "dry_run_plan_type": "metadata_only_external_tool_api_pilot_hardening_plan",
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "interface_count": len(interface_registry),
        "action_envelope_count": len(action_envelopes),
        "dry_run_step_count": 6,
        "dry_run_steps": [
            "register_external_interface_descriptors_metadata",
            "register_external_action_envelopes_metadata",
            "enforce_external_access_policy_gate_metadata",
            "record_credential_secret_denial_proof_metadata",
            "record_network_api_denial_proof_metadata",
            "record_external_permission_receipts_metadata",
        ],
        "external_metadata_authorized": policy_gate.get("external_metadata_authorized") is True,
        "real_tool_invocation_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "dry_run_execution_only": True,
        "live_execution_performed": False,
        "context_digest": sha256_digest(context),
    }


def create_external_permission_receipts(interface_registry: dict, action_envelopes: dict, dry_run_plan: dict, policy_gate: dict) -> dict:
    receipts = {}
    for envelope_id in STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS:
        interface_id = action_envelopes[envelope_id]["bound_interface_id"]
        receipt_id = sha256_digest({"envelope_id": envelope_id, "interface_id": interface_id, "version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION})
        receipts[receipt_id] = {
            "receipt_id": receipt_id,
            "receipt_type": "metadata_only_external_permission_receipt",
            "external_action_envelope_id": envelope_id,
            "interface_id": interface_id,
            "receipt_status": "EXTERNAL_PERMISSION_METADATA_RECORDED" if policy_gate.get("external_metadata_authorized") is True else "EXTERNAL_PERMISSION_METADATA_DENIED",
            "external_permission_receipt_generated": policy_gate.get("external_metadata_authorized") is True,
            "real_tool_invocation_performed": False,
            "external_tool_invocation_performed": False,
            "api_call_performed": False,
            "network_access_performed": False,
            "socket_access_performed": False,
            "dns_resolution_performed": False,
            "credential_access_performed": False,
            "secret_read_performed": False,
            "environment_read_performed": False,
            "filesystem_mutation_performed": False,
            "deployment_performed": False,
            "production_execution_performed": False,
            "arbitrary_task_execution_performed": False,
            "user_task_execution_performed": False,
        }
    return receipts


def create_external_pilot_hardening_audit_record(interface_registry: dict, action_envelopes: dict, policy_gate: dict, credential_secret_denial_proof: dict, network_api_denial_proof: dict, dry_run_plan: dict, permission_receipts: dict) -> dict:
    context = {
        "interface_registry": interface_registry,
        "action_envelopes": action_envelopes,
        "policy_gate": policy_gate,
        "credential_secret_denial_proof": credential_secret_denial_proof,
        "network_api_denial_proof": network_api_denial_proof,
        "dry_run_plan": dry_run_plan,
        "permission_receipts": permission_receipts,
        "audit": "external_tool_api_pilot_hardening_audit",
    }
    return {
        "audit_id": sha256_digest(context),
        "audit_type": "external_tool_api_pilot_hardening_audit",
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "interface_descriptor_count": len(interface_registry),
        "action_envelope_count": len(action_envelopes),
        "permission_receipt_count": len(permission_receipts),
        "external_metadata_authorized": policy_gate.get("external_metadata_authorized") is True,
        "all_permission_receipts_recorded": len(permission_receipts) == 4,
        "no_real_tool_invocation": True,
        "no_external_tool_invocation": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_socket_access": True,
        "no_dns_resolution": True,
        "no_credential_access": True,
        "no_credential_vault_access": True,
        "no_secret_read": True,
        "no_environment_read": True,
        "no_filesystem_mutation": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_worker_process_started": True,
        "no_agent_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_full_external_prod_agent_army_activation": True,
    }


def create_external_tool_api_pilot_safety_boundary_matrix() -> dict:
    actions = [
        "full_external_prod_agent_army_activation",
        "real_tool_invocation",
        "external_tool_invocation",
        "api_call",
        "network_access",
        "socket_access",
        "dns_resolution",
        "outbound_connection",
        "inbound_connection",
        "webhook_call",
        "credential_use",
        "credential_vault_access",
        "secret_read",
        "environment_read",
        "worker_process_start",
        "daemon_start",
        "background_process_start",
        "agent_start",
        "subprocess_start",
        "shell_execution",
        "arbitrary_command_execution",
        "arbitrary_task_execution",
        "user_task_execution",
        "real_queue_creation",
        "queue_write",
        "scheduler_write",
        "cron_write",
        "live_task_enqueue",
        "live_task_dequeue",
        "live_task_execution",
        "live_worker_routing",
        "live_orchestration",
        "filesystem_mutation",
        "deployment",
        "production_execution",
        "database_mutation",
        "full_workforce_activation",
        "v13_1_creation",
        "v14_creation",
    ]
    return {action: "DENIED" for action in actions}


def create_station_chief_v13_external_tool_api_pilot_hardening_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "schema_type": "station_chief_v13_external_tool_api_pilot_hardening",
        "required_sections": [
            "external_interface_descriptor_registry",
            "external_action_envelopes",
            "external_access_policy_gate",
            "credential_secret_denial_proof",
            "network_api_denial_proof",
            "external_pilot_dry_run_plan",
            "external_permission_receipts",
            "external_pilot_hardening_audit_record",
            "external_tool_api_pilot_safety_boundary_matrix",
            "external_tool_api_pilot_readiness_summary",
        ],
        "no_real_tool_invocation_authorized": True,
        "no_external_tool_invocation_authorized": True,
        "no_api_call_authorized": True,
        "no_network_access_authorized": True,
        "no_socket_access_authorized": True,
        "no_dns_resolution_authorized": True,
        "no_credential_access_authorized": True,
        "no_credential_vault_access_authorized": True,
        "no_secret_read_authorized": True,
        "no_environment_read_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_user_task_execution_authorized": True,
        "no_worker_process_start_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_live_routing_authorized": True,
        "no_live_orchestration_authorized": True,
        "no_deployment_authorized": True,
        "no_production_execution_authorized": True,
        "v13_1_created": False,
        "v14_created": False,
    }


def create_station_chief_v13_external_tool_api_pilot_hardening_bundle() -> dict:
    interface_registry = create_external_interface_descriptor_registry()
    action_envelopes = create_external_action_envelopes(interface_registry)
    policy_gate = create_external_access_policy_gate(interface_registry, action_envelopes)
    credential_secret_denial_proof = create_credential_secret_denial_proof(interface_registry, action_envelopes, policy_gate)
    network_api_denial_proof = create_network_api_denial_proof(interface_registry, action_envelopes, policy_gate)
    dry_run_plan = create_external_pilot_dry_run_plan(interface_registry, action_envelopes, policy_gate, credential_secret_denial_proof, network_api_denial_proof)
    permission_receipts = create_external_permission_receipts(interface_registry, action_envelopes, dry_run_plan, policy_gate)
    audit_record = create_external_pilot_hardening_audit_record(interface_registry, action_envelopes, policy_gate, credential_secret_denial_proof, network_api_denial_proof, dry_run_plan, permission_receipts)
    safety_boundary_matrix = create_external_tool_api_pilot_safety_boundary_matrix()
    readiness_summary = {
        "external_interface_descriptors_registered": True,
        "external_action_envelopes_registered": True,
        "external_access_policy_gate_created": True,
        "credential_secret_denial_proof_created": True,
        "network_api_denial_proof_created": True,
        "external_pilot_dry_run_plan_created": True,
        "external_permission_receipts_generated": True,
        "no_real_tool_invocation": True,
        "no_external_tool_invocation": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_socket_access": True,
        "no_dns_resolution": True,
        "no_credential_access": True,
        "no_credential_vault_access": True,
        "no_secret_read": True,
        "no_environment_read": True,
        "no_worker_process_started": True,
        "no_daemon_started": True,
        "no_background_process_started": True,
        "no_agent_started": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True,
        "no_shell_executed": True,
        "no_subprocess_started": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_v13_1": True,
        "no_v14": True,
    }
    bundle = {
        "runtime_version": STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
        "external_pilot_hardening_status": "EXTERNAL_TOOL_API_PILOT_HARDENING_READY",
        "external_interface_descriptor_registry": interface_registry,
        "external_action_envelopes": action_envelopes,
        "external_access_policy_gate": policy_gate,
        "credential_secret_denial_proof": credential_secret_denial_proof,
        "network_api_denial_proof": network_api_denial_proof,
        "external_pilot_dry_run_plan": dry_run_plan,
        "external_permission_receipts": permission_receipts,
        "external_pilot_hardening_audit_record": audit_record,
        "external_tool_api_pilot_safety_boundary_matrix": safety_boundary_matrix,
        "external_tool_api_pilot_readiness_summary": readiness_summary,
        "interface_descriptor_count": len(interface_registry),
        "action_envelope_count": len(action_envelopes),
        "permission_receipt_count": len(permission_receipts),
        "external_interface_descriptors_registered": True,
        "external_action_envelopes_registered": True,
        "external_access_policy_gate_created": True,
        "credential_secret_denial_proof_created": True,
        "network_api_denial_proof_created": True,
        "external_pilot_dry_run_plan_created": True,
        "external_permission_receipts_generated": True,
        "real_tool_invocation_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "socket_access_performed": False,
        "dns_resolution_performed": False,
        "credential_access_performed": False,
        "credential_vault_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "real_worker_process_started": False,
        "daemon_started": False,
        "background_process_started": False,
        "agent_started": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "live_task_enqueued": False,
        "live_task_dequeued": False,
        "live_task_executed": False,
        "task_executed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "shell_executed": False,
        "subprocess_started": False,
        "filesystem_mutation_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "full_external_prod_agent_army_activation_performed": False,
        "v13_1_created": False,
        "v14_created": False,
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
