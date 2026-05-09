"""
Station Chief Runtime v11.0 Permissioned Tool / Task / Queue Layer Module.
Introduces the permissioned tool/task/queue control layer candidate.
Metadata only. Non-executing.
"""

import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION = "11.0.0"
STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_STATUS = "STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_LOCAL_DETERMINISTIC_ONLY"
STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_PHASE = "Station Chief v11.0 Permissioned Tool / Task / Queue Control Layer Candidate"

STATION_CHIEF_V11_SANDBOX_TOOL_IDS = [
    "station-chief-permissioned-tool-noop-inspector-001",
    "station-chief-permissioned-tool-policy-checker-002",
    "station-chief-permissioned-tool-ledger-summarizer-003"
]

STATION_CHIEF_V11_TASK_ENVELOPE_IDS = [
    "station-chief-permissioned-task-envelope-001",
    "station-chief-permissioned-task-envelope-002",
    "station-chief-permissioned-task-envelope-003"
]

STATION_CHIEF_V11_VIRTUAL_QUEUE_ID = "station-chief-virtual-permissioned-queue-001"
STATION_CHIEF_V11_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v11.1 or v12.0 requires explicit operator instruction"

def canonical_json(data: object) -> str:
    """Returns a canonical JSON string for stable hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    """Returns the SHA-256 digest of the canonical JSON representation of the data."""
    content = canonical_json(data)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    """Normalizes a label string to be lowercase and alphanumeric with hyphens."""
    if not label:
        return default_label
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")

def create_permissioned_sandbox_tool_registry() -> dict:
    """Creates exactly three tool descriptors for the v11.0 registry."""
    registry = {}
    
    # Tool 001
    registry["station-chief-permissioned-tool-noop-inspector-001"] = {
        "tool_id": "station-chief-permissioned-tool-noop-inspector-001",
        "tool_name": "noop_inspector",
        "tool_type": "metadata_only_sandbox_tool_descriptor",
        "permitted_operation": "inspect_noop_task_metadata",
        "descriptor_only": True,
        "tool_invoked": False,
        "live_invocation_allowed": False,
        "external_tool_allowed": False,
        "api_allowed": False,
        "network_allowed": False,
        "filesystem_mutation_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "production_allowed": False,
        "arbitrary_task_allowed": False,
        "user_task_allowed": False
    }
    
    # Tool 002
    registry["station-chief-permissioned-tool-policy-checker-002"] = {
        "tool_id": "station-chief-permissioned-tool-policy-checker-002",
        "tool_name": "policy_checker",
        "tool_type": "metadata_only_sandbox_tool_descriptor",
        "permitted_operation": "check_policy_metadata",
        "descriptor_only": True,
        "tool_invoked": False,
        "live_invocation_allowed": False,
        "external_tool_allowed": False,
        "api_allowed": False,
        "network_allowed": False,
        "filesystem_mutation_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "production_allowed": False,
        "arbitrary_task_allowed": False,
        "user_task_allowed": False
    }
    
    # Tool 003
    registry["station-chief-permissioned-tool-ledger-summarizer-003"] = {
        "tool_id": "station-chief-permissioned-tool-ledger-summarizer-003",
        "tool_name": "ledger_summarizer",
        "tool_type": "metadata_only_sandbox_tool_descriptor",
        "permitted_operation": "summarize_virtual_queue_ledger_metadata",
        "descriptor_only": True,
        "tool_invoked": False,
        "live_invocation_allowed": False,
        "external_tool_allowed": False,
        "api_allowed": False,
        "network_allowed": False,
        "filesystem_mutation_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "production_allowed": False,
        "arbitrary_task_allowed": False,
        "user_task_allowed": False
    }
    
    return registry

def create_permissioned_task_envelopes() -> dict:
    """Creates exactly three task envelopes for the v11.0 registry."""
    envelopes = {}
    
    tool_ids = [
        "station-chief-permissioned-tool-noop-inspector-001",
        "station-chief-permissioned-tool-policy-checker-002",
        "station-chief-permissioned-tool-ledger-summarizer-003"
    ]
    
    for i in range(1, 4):
        task_id = f"station-chief-permissioned-task-envelope-00{i}"
        
        envelopes[task_id] = {
            "task_envelope_id": task_id,
            "task_type": "permissioned_synthetic_noop_task_envelope",
            "task_source": "station_chief_v11_permissioned_tool_task_queue_layer",
            "task_index": i,
            "required_tool_id": tool_ids[i-1],
            "virtual_queue_id": "station-chief-virtual-permissioned-queue-001",
            "task_payload": {"operation": "permissioned_noop_metadata", "expected_receipt": "permission_receipt_recorded"},
            "arbitrary_user_content_allowed": False,
            "shell_command_allowed": False,
            "subprocess_allowed": False,
            "network_allowed": False,
            "api_allowed": False,
            "filesystem_mutation_allowed": False,
            "production_allowed": False,
            "live_execution_allowed": False,
            "execution_mode": "metadata_permission_receipt_only"
        }
        
    return envelopes

def create_virtual_queue_manifest(task_envelopes: dict) -> dict:
    """Creates a metadata-only virtual queue manifest."""
    return {
        "virtual_queue_id": "station-chief-virtual-permissioned-queue-001",
        "queue_type": "metadata_only_virtual_permissioned_queue",
        "queue_mode": "deterministic_non_live_queue_manifest",
        "task_envelope_count": len(task_envelopes),
        "task_envelope_ids": sorted(list(task_envelopes.keys())),
        "real_queue_created": False,
        "queue_write_performed": False,
        "live_enqueue_performed": False,
        "live_dequeue_performed": False,
        "live_routing_performed": False,
        "live_orchestration_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False
    }

def create_permission_policy_gate(tool_registry: dict, task_envelopes: dict, virtual_queue_manifest: dict) -> dict:
    """Validates the permission policy and returns the policy gate status."""
    tool_count_ok = len(tool_registry) == 3
    task_count_ok = len(task_envelopes) == 3
    queue_count_ok = virtual_queue_manifest.get("virtual_queue_id") == "station-chief-virtual-permissioned-queue-001"
    
    all_tools_descriptor_only = all(t.get("descriptor_only") is True for t in tool_registry.values())
    all_tools_not_invoked = all(t.get("tool_invoked") is False for t in tool_registry.values())
    all_tasks_not_live = all(t.get("live_execution_allowed") is False for t in task_envelopes.values())
    
    expected_tool_ids = set(STATION_CHIEF_V11_SANDBOX_TOOL_IDS)
    actual_tool_ids = set(tool_registry.keys())
    tool_ids_match = expected_tool_ids == actual_tool_ids
    
    expected_task_ids = set(STATION_CHIEF_V11_TASK_ENVELOPE_IDS)
    actual_task_ids = set(task_envelopes.keys())
    task_ids_match = expected_task_ids == actual_task_ids
    
    all_tasks_reference_tools = all(t.get("required_tool_id") in expected_tool_ids for t in task_envelopes.values())
    all_tasks_reference_queue = all(t.get("virtual_queue_id") == "station-chief-virtual-permissioned-queue-001" for t in task_envelopes.values())
    
    no_user_content = all(t.get("arbitrary_user_content_allowed") is False for t in task_envelopes.values())
    no_shell = all(t.get("shell_command_allowed") is False for t in task_envelopes.values())
    no_subprocess = all(t.get("subprocess_allowed") is False for t in task_envelopes.values())
    no_network = all(t.get("network_allowed") is False for t in task_envelopes.values())
    no_api = all(t.get("api_allowed") is False for t in task_envelopes.values())
    no_production = all(t.get("production_allowed") is False for t in task_envelopes.values())
    
    real_queue_false = virtual_queue_manifest.get("real_queue_created") is False
    queue_write_false = virtual_queue_manifest.get("queue_write_performed") is False
    live_enqueue_false = virtual_queue_manifest.get("live_enqueue_performed") is False
    live_routing_false = virtual_queue_manifest.get("live_routing_performed") is False

    authorized = all([
        tool_count_ok, task_count_ok, queue_count_ok,
        all_tools_descriptor_only, all_tools_not_invoked, all_tasks_not_live,
        tool_ids_match, task_ids_match, all_tasks_reference_tools, all_tasks_reference_queue,
        no_user_content, no_shell, no_subprocess, no_network, no_api, no_production,
        real_queue_false, queue_write_false, live_enqueue_false, live_routing_false
    ])
    
    return {
        "permission_metadata_authorized": authorized,
        "real_tool_invocation_authorized": False,
        "external_tool_invocation_authorized": False,
        "real_execution_authorized": False,
        "arbitrary_execution_authorized": False,
        "user_task_execution_authorized": False,
        "real_queue_authorized": False,
        "queue_write_authorized": False,
        "live_routing_authorized": False,
        "live_orchestration_authorized": False
    }

def create_deterministic_dispatch_plan(tool_registry: dict, task_envelopes: dict, virtual_queue_manifest: dict, policy_gate: dict) -> dict:
    """Creates a deterministic dispatch plan metadata."""
    context = {
        "tool_registry": tool_registry,
        "task_envelopes": task_envelopes,
        "virtual_queue_manifest": virtual_queue_manifest,
        "version": STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION
    }
    dispatch_plan_id = f"sc-v11-dispatch-{sha256_digest(context)[:16]}"
    
    dispatch_entries = {}
    for task_id, task in task_envelopes.items():
        dispatch_entries[task_id] = task.get("required_tool_id")
        
    return {
        "dispatch_plan_id": dispatch_plan_id,
        "dispatch_plan_type": "metadata_only_permissioned_dispatch_plan",
        "runtime_version": STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION,
        "virtual_queue_id": virtual_queue_manifest.get("virtual_queue_id"),
        "dispatch_count": len(dispatch_entries),
        "dispatch_strategy": "deterministic_task_envelope_to_permissioned_tool_descriptor",
        "dispatch_entries": dispatch_entries,
        "permission_metadata_authorized": policy_gate.get("permission_metadata_authorized"),
        "real_dispatch_performed": False,
        "live_tool_invocation_performed": False,
        "live_task_routing_performed": False,
        "live_orchestration_performed": False,
        "queue_write_performed": False,
        "task_executed": False
    }

def create_permission_receipts(tool_registry: dict, task_envelopes: dict, dispatch_plan: dict, policy_gate: dict) -> dict:
    """Creates metadata-only permission receipts."""
    receipts = {}
    authorized = policy_gate.get("permission_metadata_authorized", False)
    
    for task_id, tool_id in dispatch_plan.get("dispatch_entries", {}).items():
        context = {
            "task_id": task_id,
            "tool_id": tool_id,
            "version": STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION
        }
        receipt_id = f"sc-v11-receipt-{sha256_digest(context)[:16]}"
        
        receipts[receipt_id] = {
            "receipt_id": receipt_id,
            "receipt_type": "metadata_only_permission_receipt",
            "task_envelope_id": task_id,
            "tool_id": tool_id,
            "receipt_status": "PERMISSION_METADATA_RECORDED" if authorized else "POLICY_DENIED",
            "permission_receipt_generated": bool(authorized),
            "tool_invoked": False,
            "external_tool_invocation_performed": False,
            "live_dispatch_performed": False,
            "task_executed": False,
            "api_call_performed": False,
            "network_access_performed": False,
            "filesystem_mutation_performed": False,
            "production_execution_performed": False,
            "arbitrary_task_execution_performed": False,
            "user_task_execution_performed": False
        }
        
    return receipts

def create_permissioned_queue_task_tool_audit_record(tool_registry: dict, task_envelopes: dict, virtual_queue_manifest: dict, policy_gate: dict, dispatch_plan: dict, permission_receipts: dict) -> dict:
    """Creates an audit record for the permissioned tool/task/queue layer."""
    context = {
        "tool_registry": tool_registry,
        "task_envelopes": task_envelopes,
        "virtual_queue_manifest": virtual_queue_manifest,
        "policy_gate": policy_gate,
        "dispatch_plan": dispatch_plan,
        "permission_receipts": permission_receipts
    }
    audit_id = f"sc-v11-audit-{sha256_digest(context)[:16]}"
    
    return {
        "audit_id": audit_id,
        "audit_type": "permissioned_queue_task_tool_layer_audit",
        "runtime_version": STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION,
        "tool_descriptor_count": len(tool_registry),
        "task_envelope_count": len(task_envelopes),
        "virtual_queue_count": 1,
        "permission_receipt_count": len(permission_receipts),
        "permission_metadata_authorized": policy_gate.get("permission_metadata_authorized"),
        "all_receipts_recorded": len(permission_receipts) == 3,
        "no_real_tool_invocation": True,
        "no_external_tool_invocation": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_shell_executed": True,
        "no_subprocess_started": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_filesystem_mutation": True,
        "no_production_execution": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True
    }

def create_permissioned_tool_task_queue_safety_boundary_matrix() -> dict:
    """Creates the safety boundary matrix for the v11.0 layer."""
    return {
        "real_tool_invocation": "DENIED",
        "external_tool_invocation": "DENIED",
        "worker_process_start": "DENIED",
        "daemon_start": "DENIED",
        "background_process_start": "DENIED",
        "agent_start": "DENIED",
        "subprocess_start": "DENIED",
        "shell_execution": "DENIED",
        "arbitrary_command_execution": "DENIED",
        "arbitrary_task_execution": "DENIED",
        "user_task_execution": "DENIED",
        "real_queue_creation": "DENIED",
        "queue_write": "DENIED",
        "scheduler_write": "DENIED",
        "cron_write": "DENIED",
        "live_task_enqueue": "DENIED",
        "live_task_dequeue": "DENIED",
        "live_task_execution": "DENIED",
        "live_worker_routing": "DENIED",
        "live_orchestration": "DENIED",
        "api_call": "DENIED",
        "network_access": "DENIED",
        "socket_access": "DENIED",
        "dns_resolution": "DENIED",
        "credential_use": "DENIED",
        "secret_read": "DENIED",
        "environment_read": "DENIED",
        "deployment": "DENIED",
        "production_execution": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v11_1_creation": "DENIED",
        "v12_creation": "DENIED"
    }

def create_permissioned_tool_task_queue_readiness_summary(audit_record: dict) -> dict:
    """Creates a readiness summary for the v11.0 layer."""
    return {
        "permissioned_tool_descriptors_registered": audit_record.get("tool_descriptor_count") == 3,
        "permissioned_task_envelopes_registered": audit_record.get("task_envelope_count") == 3,
        "virtual_queue_manifest_created": audit_record.get("virtual_queue_count") == 1,
        "deterministic_dispatch_plan_created": True,
        "permission_receipts_generated": audit_record.get("permission_receipt_count") == 3,
        "safety_boundaries_enforced": True,
        "ready_for_next_permission_milestone": True
    }

def create_station_chief_v11_permissioned_tool_task_queue_layer_schema() -> dict:
    """Creates the schema for the v11.0 permissioned tool/task/queue layer."""
    return {
        "schema_version": "11.0.0",
        "schema_type": "station_chief_v11_permissioned_tool_task_queue_layer",
        "required_sections": {
            "permissioned_sandbox_tool_registry": "Tool Registry",
            "permissioned_task_envelopes": "Task Envelopes",
            "virtual_queue_manifest": "Virtual Queue Manifest",
            "permission_policy_gate": "Policy Gate",
            "deterministic_dispatch_plan": "Dispatch Plan",
            "permission_receipts": "Permission Receipts",
            "permissioned_queue_task_tool_audit_record": "Audit Record",
            "permissioned_tool_task_queue_safety_boundary_matrix": "Safety Boundary Matrix",
            "permissioned_tool_task_queue_readiness_summary": "Readiness Summary"
        },
        "no_real_tool_invocation_authorized": True,
        "no_external_tool_invocation_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_user_task_execution_authorized": True,
        "no_worker_process_start_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_live_routing_authorized": True,
        "no_live_orchestration_authorized": True,
        "no_API_network_deployment_production_authorized": True,
        "v11_1_created": False,
        "v12_created": False
    }

def create_station_chief_v11_permissioned_tool_task_queue_layer_bundle() -> dict:
    """Assembles the full bundle for the v11.0 permissioned tool/task/queue layer."""
    registry = create_permissioned_sandbox_tool_registry()
    envelopes = create_permissioned_task_envelopes()
    queue = create_virtual_queue_manifest(envelopes)
    gate = create_permission_policy_gate(registry, envelopes, queue)
    plan = create_deterministic_dispatch_plan(registry, envelopes, queue, gate)
    receipts = create_permission_receipts(registry, envelopes, plan, gate)
    audit = create_permissioned_queue_task_tool_audit_record(registry, envelopes, queue, gate, plan, receipts)
    matrix = create_permissioned_tool_task_queue_safety_boundary_matrix()
    summary = create_permissioned_tool_task_queue_readiness_summary(audit)
    schema = create_station_chief_v11_permissioned_tool_task_queue_layer_schema()

    bundle = {
        "runtime_version": "11.0.0",
        "permission_layer_status": "PERMISSIONED_TOOL_TASK_QUEUE_LAYER_READY",
        "permissioned_tool_descriptors_registered": True,
        "permissioned_task_envelopes_registered": True,
        "virtual_queue_manifest_created": True,
        "deterministic_dispatch_plan_created": True,
        "permission_receipts_generated": True,
        "tool_descriptor_count": 3,
        "task_envelope_count": 3,
        "virtual_queue_count": 1,
        "permission_receipt_count": 3,
        "schema": schema,
        "permissioned_sandbox_tool_registry": registry,
        "permissioned_task_envelopes": envelopes,
        "virtual_queue_manifest": queue,
        "permission_policy_gate": gate,
        "deterministic_dispatch_plan": plan,
        "permission_receipts": receipts,
        "permissioned_queue_task_tool_audit_record": audit,
        "permissioned_tool_task_queue_safety_boundary_matrix": matrix,
        "permissioned_tool_task_queue_readiness_summary": summary,
        "real_tool_invocation_performed": False,
        "external_tool_invocation_performed": False,
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
        "api_call_performed": False,
        "network_access_performed": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "filesystem_mutation_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "full_workforce_activation_performed": False,
        "v11_1_created": False,
        "v12_created": False
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
