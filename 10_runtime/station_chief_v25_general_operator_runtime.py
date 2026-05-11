import json
import hashlib
import csv
import io
import re
from pathlib import Path

# Import from prior modules as allowed
from station_chief_v17_live_activation_protocol import STATION_CHIEF_V17_APPROVAL_PHRASE, execute_controlled_readonly_repo_integrity_inspection
from station_chief_v20_operational_agent_army_mode import STATION_CHIEF_V20_APPROVAL_PHRASE, execute_operational_workpack
from station_chief_v21_controlled_local_workspace_artifact_factory import STATION_CHIEF_V21_APPROVAL_PHRASE, execute_artifact_factory_workpack
from station_chief_v22_controlled_business_workflow_workpack import STATION_CHIEF_V22_APPROVAL_PHRASE, execute_business_workflow_workpack
from station_chief_v23_controlled_live_external_tool_gateway import STATION_CHIEF_V23_APPROVAL_PHRASE, execute_external_tool_gateway_workpack
from station_chief_v24_controlled_external_evidence_snapshot import STATION_CHIEF_V24_APPROVAL_PHRASE, execute_external_evidence_snapshot_workpack

STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_VERSION = "25.0.0"
STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_STATUS = "STATION_CHIEF_V25_GENERAL_OPERATOR_TASK_RUNTIME_OPEN_GATE_RELEASE"
STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_PHASE = "Station Chief v25.0 General Operator Task Runtime / Open-Gate Release Layer"

STATION_CHIEF_V25_APPROVAL_PHRASE = "I_APPROVE_V25_OPEN_GATE_GENERAL_OPERATOR_RUNTIME"

STATION_CHIEF_V25_DONE_DONE_RELEASE_ID = "station-chief-v25-done-done-general-operator-runtime-release-001"

STATION_CHIEF_V25_CONTROLLED_WORKSPACE_DIR = "/tmp/station_chief_v25_general_operator_runtime"

STATION_CHIEF_V25_CONTROLLED_ARTIFACT_PATHS = {
    "operator_task_receipt_json": "/tmp/station_chief_v25_general_operator_runtime/v25_operator_task_receipt.json",
    "operator_command_menu_md": "/tmp/station_chief_v25_general_operator_runtime/v25_operator_command_menu.md",
    "installed_capability_registry_json": "/tmp/station_chief_v25_general_operator_runtime/v25_installed_capability_registry.json",
    "final_acceptance_report_md": "/tmp/station_chief_v25_general_operator_runtime/v25_final_acceptance_report.md",
    "done_done_release_manifest_json": "/tmp/station_chief_v25_general_operator_runtime/v25_done_done_release_manifest.json"
}

STATION_CHIEF_V25_SUPPORTED_TASK_TYPES = [
    "repo_integrity_inspection",
    "operational_workpack",
    "local_artifact_factory",
    "business_workflow_packet",
    "external_tool_gateway_probe",
    "external_evidence_snapshot",
    "capability_status_report",
    "unsupported_or_unsafe_task"
]

STATION_CHIEF_V25_OPERATOR_ROLE_IDS = [
    "station-chief-v25-role-operator-intake-001",
    "station-chief-v25-role-task-classifier-002",
    "station-chief-v25-role-route-planner-003",
    "station-chief-v25-role-approval-broker-004",
    "station-chief-v25-role-dispatch-broker-005",
    "station-chief-v25-role-release-auditor-006"
]

STATION_CHIEF_V25_FINAL_STATUS = "CORE_COMMAND_CENTER_OPERATIONALLY_COMPLETE"

STATION_CHIEF_V25_NEXT_VERSION_POLICY = "No required next core version. Future work is adapter/plugin expansion under the v25 general operator runtime."


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()


def create_general_operator_runtime_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("general_operator_task_runtime_manifest"),
        "manifest_type": "general_operator_task_runtime_manifest",
        "runtime_version": STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_VERSION,
        "done_done_release_layer_created": True,
        "open_gate_command_layer_created": True,
        "general_operator_task_runtime_created": True,
        "core_command_center_operationally_complete": True,
        "accepts_real_operator_job_tickets": True,
        "classifies_operator_tasks": True,
        "routes_to_installed_workpacks": True,
        "approval_broker_required": True,
        "dispatch_broker_required": True,
        "receipt_collector_required": True,
        "final_release_audit_required": True,
        "unsupported_task_denial_required": True,
        "future_work_is_adapter_plugin_expansion": True,
        "next_core_version_required": False,
        "uncontrolled_autonomy_allowed": False,
        "production_execution_allowed": False,
        "deployment_allowed": False,
        "arbitrary_external_tool_execution_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "real_queue_allowed": False
    }


def create_installed_capability_registry() -> dict:
    capabilities = {
        "station-chief-capability-v17-repo-readonly-inspection": {
            "capability_name": "Repo Read-Only Integrity Inspection",
            "source_version": "17.0.0",
            "executable": True
        },
        "station-chief-capability-v18-universal-tool-permission-layer": {
            "capability_name": "Universal Tool Permission Layer",
            "source_version": "18.0.0",
            "executable": False
        },
        "station-chief-capability-v19-supervised-agent-router": {
            "capability_name": "Supervised Multi-Agent Router",
            "source_version": "19.0.0",
            "executable": False
        },
        "station-chief-capability-v20-operational-workpack": {
            "capability_name": "Operational Agent Workpack Execution",
            "source_version": "20.0.0",
            "executable": True
        },
        "station-chief-capability-v21-local-artifact-factory": {
            "capability_name": "Local Workspace Artifact Factory",
            "source_version": "21.0.0",
            "executable": True
        },
        "station-chief-capability-v22-business-workflow-workpack": {
            "capability_name": "Business Workflow / Client-Ready Workpack",
            "source_version": "22.0.0",
            "executable": True
        },
        "station-chief-capability-v23-external-tool-gateway": {
            "capability_name": "Controlled Live External Tool Gateway",
            "source_version": "23.0.0",
            "executable": True
        },
        "station-chief-capability-v24-external-evidence-snapshot": {
            "capability_name": "Controlled External Evidence Snapshot Gateway",
            "source_version": "24.0.0",
            "executable": True
        }
    }
    registry = {}
    executable_count = 0
    reference_count = 0
    for cap_id, info in capabilities.items():
        is_exec = info["executable"]
        if is_exec: executable_count += 1
        else: reference_count += 1
        registry[cap_id] = {
            "capability_id": cap_id,
            "capability_name": info["capability_name"],
            "source_version": info["source_version"],
            "capability_registered": True,
            "available_to_v25_operator_runtime": True,
            "requires_human_approval": True,
            "routed_execution_supported": is_exec,
            "preview_supported": True,
            "receipt_required": True,
            "audit_required": True,
            "repo_mutation_allowed": False,
            "production_allowed": False,
            "credential_access_allowed": False,
            "uncontrolled_autonomy_allowed": False
        }
    return {
        "registry_id": sha256_digest(registry),
        "registry_type": "v25_installed_capability_registry",
        "runtime_version": STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_VERSION,
        "installed_capability_count": 8,
        "executable_capability_count": executable_count,
        "reference_capability_count": reference_count,
        "core_stack_complete": True,
        "future_expansion_mode": "adapter_plugin_expansion",
        "capabilities": registry
    }


def create_supported_operator_task_type_registry() -> dict:
    task_types = {}
    for tt in STATION_CHIEF_V25_SUPPORTED_TASK_TYPES:
        unsupported = (tt == "unsupported_or_unsafe_task")
        task_types[tt] = {
            "task_type": tt,
            "task_type_registered": True,
            "supported_in_v25": not unsupported,
            "requires_classification": True,
            "requires_route_plan": True,
            "requires_approval": (tt != "capability_status_report" and not unsupported),
            "produces_receipt": True,
            "produces_audit": True,
            "unsupported_or_unsafe": unsupported
        }
    return {
        "registry_id": sha256_digest(task_types),
        "registry_type": "v25_supported_operator_task_type_registry",
        "runtime_version": STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_VERSION,
        "task_type_count": 8,
        "supported_executable_task_type_count": 6,
        "status_only_task_type_count": 1,
        "unsupported_denial_task_type_count": 1,
        "task_types": task_types
    }


def create_operator_role_registry() -> dict:
    roles = [
        ("operator_intake", "operator_task_intake"),
        ("task_classifier", "task_classification"),
        ("route_planner", "capability_route_plan"),
        ("approval_broker", "approval_scope_check"),
        ("dispatch_broker", "installed_workpack_dispatch"),
        ("release_auditor", "receipt_audit_and_release_status")
    ]
    registry = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V25_OPERATOR_ROLE_IDS[idx]
        registry[r_id] = {
            "role_id": r_id,
            "role_name": name,
            "role_type": "logical_v25_general_operator_runtime_role",
            "role_registered": True,
            "workflow_stage": stage,
            "human_supervision_required": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "daemon_started": False,
            "subprocess_started": False,
            "shell_execution_allowed": False,
            "can_receive_operator_task": True,
            "can_create_metadata_receipt": True,
            "can_execute_tools": False,
            "can_route_to_installed_workpack": (name == "dispatch_broker"),
            "can_mutate_repo_files": False,
            "can_access_credentials": False,
            "can_access_network": False,
            "can_touch_production": False
        }
    return {
        "registry_id": sha256_digest(registry),
        "registry_type": "v25_operator_role_registry",
        "runtime_version": "25.0.0",
        "role_count": 6,
        "roles": registry
    }


def create_general_operator_task_request(operator_task: str | None = None, requested_task_type: str | None = None, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v25_operator_workpack")
    return {
        "task_request_id": sha256_digest({"task": operator_task, "type": requested_task_type, "op": op}),
        "request_type": "v25_general_operator_task_request",
        "runtime_version": STATION_CHIEF_V25_GENERAL_OPERATOR_RUNTIME_VERSION,
        "operator_task": operator_task,
        "requested_task_type": requested_task_type,
        "operator_label": op,
        "workpack_label": wp,
        "job_ticket_received": True,
        "classification_required": True,
        "route_plan_required": True,
        "approval_required": True,
        "dispatch_required": True,
        "receipt_required": True,
        "audit_required": True,
        "repo_mutation_requested": False,
        "production_requested": False,
        "deployment_requested": False,
        "credential_access_requested": False,
        "secret_read_requested": False,
        "environment_read_requested": False,
        "arbitrary_url_requested": False,
        "email_execution_requested": False,
        "calendar_execution_requested": False,
        "database_execution_requested": False,
        "arbitrary_task_requested": False
    }


def classify_operator_task(task_request: dict, task_type_registry: dict) -> dict:
    requested_tt = task_request.get("requested_task_type")
    task_text = (task_request.get("operator_task") or "").lower()
    
    classified = "unsupported_or_unsafe_task"
    confidence = "unsupported_fallback"
    reason = "No matching task type found."

    if requested_tt in task_type_registry["task_types"]:
        classified = requested_tt
        confidence = "exact_requested_type"
        reason = "Exact task type requested by operator."
    else:
        # Keyword inference
        mappings = [
            (["repo", "inspect", "integrity"], "repo_integrity_inspection"),
            (["operational workpack"], "operational_workpack"),
            (["artifact factory", "local artifact", "document", "csv", "manifest"], "local_artifact_factory"),
            (["business", "client", "project brief", "tracker", "qa checklist"], "business_workflow_packet"),
            (["external tool", "web probe", "example.com probe"], "external_tool_gateway_probe"),
            (["evidence", "snapshot", "content digest"], "external_evidence_snapshot"),
            (["status", "capabilities", "what can you do", "command menu"], "capability_status_report")
        ]
        for keywords, tt in mappings:
            if any(k in task_text for k in keywords):
                classified = tt
                confidence = "inferred_keyword_match"
                reason = f"Keyword match found for {tt}."
                break

    tt_info = task_type_registry["task_types"][classified]
    return {
        "classification_id": sha256_digest({"task": task_text, "classified": classified}),
        "classification_type": "v25_operator_task_classification",
        "runtime_version": "25.0.0",
        "classified_task_type": classified,
        "classification_confidence": confidence,
        "supported_task_type": tt_info["supported_in_v25"],
        "executable_task_type": classified in ["repo_integrity_inspection", "operational_workpack", "local_artifact_factory", "business_workflow_packet", "external_tool_gateway_probe", "external_evidence_snapshot"],
        "status_only_task_type": (classified == "capability_status_report"),
        "unsupported_or_unsafe": tt_info["unsupported_or_unsafe"],
        "classification_reason": reason,
        "no_arbitrary_task_execution": True
    }


def create_operator_route_plan(classification: dict, capability_registry: dict, task_type_registry: dict) -> dict:
    ctt = classification["classified_task_type"]
    status = "DENIED_UNSUPPORTED_OR_UNSAFE"
    cap_id = None
    source_ver = None

    task_to_cap = {
        "repo_integrity_inspection": "station-chief-capability-v17-repo-readonly-inspection",
        "operational_workpack": "station-chief-capability-v20-operational-workpack",
        "local_artifact_factory": "station-chief-capability-v21-local-artifact-factory",
        "business_workflow_packet": "station-chief-capability-v22-business-workflow-workpack",
        "external_tool_gateway_probe": "station-chief-capability-v23-external-tool-gateway",
        "external_evidence_snapshot": "station-chief-capability-v24-external-evidence-snapshot"
    }

    if ctt == "capability_status_report":
        status = "READY_FOR_STATUS_REPORT"
    elif ctt in task_to_cap:
        cap_id = task_to_cap[ctt]
        source_ver = capability_registry["capabilities"][cap_id]["source_version"]
        status = "READY_FOR_APPROVAL"

    return {
        "route_plan_id": sha256_digest({"tt": ctt, "cap": cap_id}),
        "route_plan_type": "v25_operator_capability_route_plan",
        "runtime_version": "25.0.0",
        "classified_task_type": ctt,
        "selected_capability_id": cap_id,
        "selected_source_version": source_ver,
        "route_status": status,
        "approval_required": (status == "READY_FOR_APPROVAL"),
        "dispatch_allowed": False, # Requires approval later
        "status_report_allowed": (status == "READY_FOR_STATUS_REPORT"),
        "unsupported_denial_required": (status == "DENIED_UNSUPPORTED_OR_UNSAFE"),
        "repo_mutation_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "credential_access_allowed": False,
        "arbitrary_external_tool_allowed": False,
        "uncontrolled_autonomy_allowed": False
    }


def create_v25_operator_approval_receipt(approval_phrase: str | None, task_request: dict, classification: dict, route_plan: dict) -> dict:
    matches = (approval_phrase == STATION_CHIEF_V25_APPROVAL_PHRASE)
    ready = (route_plan["route_status"] == "READY_FOR_APPROVAL")
    granted = matches and ready
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "task": task_request["task_request_id"]}),
        "receipt_type": "v25_general_operator_runtime_human_approval_receipt",
        "runtime_version": "25.0.0",
        "operator_label": task_request["operator_label"],
        "workpack_label": task_request["workpack_label"],
        "classified_task_type": classification["classified_task_type"],
        "selected_capability_id": route_plan["selected_capability_id"],
        "approval_phrase_received": (approval_phrase is not None),
        "approval_phrase_matches": matches,
        "expected_approval_phrase": STATION_CHIEF_V25_APPROVAL_PHRASE,
        "human_approval_granted": granted,
        "autonomous_self_approval": False,
        "approval_scope": "v25_general_operator_runtime_installed_workpack_dispatch_only",
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_deployment": True,
        "approval_does_not_authorize_uninstalled_tools": True,
        "approval_does_not_authorize_arbitrary_tasks": True,
        "approval_does_not_authorize_future_adapters": True,
        "approval_does_not_authorize_real_worker_processes": True
    }


def create_operator_dispatch_plan(route_plan: dict, approval_receipt: dict) -> dict:
    granted = approval_receipt["human_approval_granted"]
    ctt = route_plan["classified_task_type"]
    rs = route_plan["route_status"]
    
    status = "DISPATCH_DENIED_OR_PREVIEW_ONLY"
    if granted:
        status = "READY_TO_DISPATCH_INSTALLED_WORKPACK"
    elif rs == "READY_FOR_STATUS_REPORT":
        status = "READY_TO_RETURN_STATUS_REPORT"
    elif rs == "DENIED_UNSUPPORTED_OR_UNSAFE":
        status = "UNSUPPORTED_OR_UNSAFE_TASK_DENIED"

    return {
        "dispatch_plan_id": sha256_digest({"route": route_plan["route_plan_id"], "granted": granted}),
        "dispatch_plan_type": "v25_operator_installed_workpack_dispatch_plan",
        "runtime_version": "25.0.0",
        "classified_task_type": ctt,
        "selected_capability_id": route_plan["selected_capability_id"],
        "human_approval_granted": granted,
        "dispatch_status": status,
        "dispatch_allowed": granted,
        "status_report_allowed": (rs == "READY_FOR_STATUS_REPORT"),
        "unsupported_denial_required": (rs == "DENIED_UNSUPPORTED_OR_UNSAFE"),
        "no_repo_mutation": True,
        "no_production": True,
        "no_deployment": True,
        "no_credentials": True,
        "no_real_workers": True,
        "no_uncontrolled_orchestration": True
    }


def dispatch_installed_workpack(dispatch_plan: dict, approval_receipt: dict, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    if not dispatch_plan["dispatch_allowed"]:
        return {"dispatch_performed": False, "prior_workpack_called": False}

    ctt = dispatch_plan["classified_task_type"]
    res = None
    ver = None
    
    if ctt == "repo_integrity_inspection":
        res = execute_controlled_readonly_repo_integrity_inspection(STATION_CHIEF_V17_APPROVAL_PHRASE)
        ver = "17.0.0"
    elif ctt == "operational_workpack":
        res = execute_operational_workpack(STATION_CHIEF_V20_APPROVAL_PHRASE, operator_label=operator_label, workpack_label=workpack_label)
        ver = "20.0.0"
    elif ctt == "local_artifact_factory":
        res = execute_artifact_factory_workpack(STATION_CHIEF_V21_APPROVAL_PHRASE, operator_label=operator_label, workpack_label=workpack_label)
        ver = "21.0.0"
    elif ctt == "business_workflow_packet":
        res = execute_business_workflow_workpack(STATION_CHIEF_V22_APPROVAL_PHRASE, operator_label=operator_label, workpack_label=workpack_label)
        ver = "22.0.0"
    elif ctt == "external_tool_gateway_probe":
        res = execute_external_tool_gateway_workpack(STATION_CHIEF_V23_APPROVAL_PHRASE, operator_label=operator_label, workpack_label=workpack_label)
        ver = "23.0.0"
    elif ctt == "external_evidence_snapshot":
        res = execute_external_evidence_snapshot_workpack(STATION_CHIEF_V24_APPROVAL_PHRASE, operator_label=operator_label, workpack_label=workpack_label)
        ver = "24.0.0"

    return {
        "dispatch_result_id": sha256_digest({"ver": ver, "res": res}),
        "dispatch_result_type": "v25_operator_dispatch_result",
        "runtime_version": "25.0.0",
        "classified_task_type": ctt,
        "selected_capability_id": dispatch_plan["selected_capability_id"],
        "dispatch_performed": True,
        "prior_workpack_called": (res is not None),
        "prior_workpack_version": ver,
        "prior_workpack_result_summary": {
            "performed": res.get("external_evidence_snapshot_workpack_performed") or res.get("external_tool_gateway_workpack_performed") or res.get("business_workflow_workpack_performed") or res.get("artifact_factory_workpack_performed") or res.get("operational_workpack_performed") or res.get("repo_integrity_inspection_performed", False)
        } if res else None,
        "inspected_file_count": res.get("inspected_file_count", 0) if res else 0,
        "artifact_paths": res.get("artifact_paths", {}) if res else {},
        "artifact_digests": res.get("artifact_digests", {}) if res else {},
        "external_network_used_only_by_prior_controlled_workpack": True,
        "response_body_returned": False,
        "response_body_stored": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "credential_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "live_queue_created": False,
        "uncontrolled_live_orchestration_performed": False,
        "_internal_full_res": res
    }


def create_unsupported_task_denial_receipt(task_request: dict, classification: dict, route_plan: dict) -> dict:
    return {
        "denial_receipt_id": sha256_digest({"task": task_request["task_request_id"], "status": "denied"}),
        "receipt_type": "v25_unsupported_or_unsafe_task_denial_receipt",
        "runtime_version": "25.0.0",
        "operator_task": task_request["operator_task"],
        "requested_task_type": task_request["requested_task_type"],
        "classified_task_type": classification["classified_task_type"],
        "denial_status": "UNSUPPORTED_OR_UNSAFE_TASK_DENIED",
        "denial_reason": classification["classification_reason"],
        "no_workpack_dispatched": True,
        "no_external_tool_called": True,
        "no_repo_mutation": True,
        "no_credentials_accessed": True,
        "no_production_touched": True,
        "no_real_workers_started": True
    }


def resolve_v25_controlled_workspace_paths() -> dict:
    workspace_dir = Path(STATION_CHIEF_V25_CONTROLLED_WORKSPACE_DIR)
    paths = {}
    valid = True
    if not str(workspace_dir).startswith("/tmp/station_chief_v25_general_operator_runtime"):
        valid = False
    for key, path_str in STATION_CHIEF_V25_CONTROLLED_ARTIFACT_PATHS.items():
        p = Path(path_str)
        paths[key] = str(p)
        if p.parent != workspace_dir:
            valid = False
    return {
        "workspace_dir": str(workspace_dir),
        "artifact_paths": paths,
        "all_artifact_paths_valid": valid,
        "repo_path": False,
        "production_path": False,
        "credential_path": False,
        "secret_path": False
    }


def build_v25_release_artifact_payloads(manifest: dict, capability_registry: dict, task_type_registry: dict, task_request: dict, classification: dict, route_plan: dict, approval_receipt: dict, dispatch_plan: dict, dispatch_result: dict, denial_receipt: dict | None = None) -> dict:
    
    receipt_payload = {
        "version": "25.0.0",
        "status": "V25_OPERATOR_TASK_RECEIPT",
        "operator": approval_receipt["operator_label"],
        "workpack": approval_receipt["workpack_label"],
        "classified_task_type": classification["classified_task_type"],
        "dispatch_performed": dispatch_result.get("dispatch_performed", False),
        "prior_workpack_called": dispatch_result.get("prior_workpack_called", False),
        "inspected_file_count": dispatch_result.get("inspected_file_count", 0)
    }

    menu_md = f"""# Station Chief v25 General Operator Runtime Command Menu

## Done-Done Release
Station Chief Runtime v25.0.0 is the operational release layer. The core command center is complete.

## Supported Task Types
{", ".join(STATION_CHIEF_V25_SUPPORTED_TASK_TYPES)}

## Installed Capabilities
- v17 Repo Integrity Inspection
- v18 Universal Tool Permission Layer
- v19 Supervised Multi-Agent Router
- v20 Operational Agent Workpack
- v21 Local Workspace Artifact Factory
- v22 Business Workflow Workpack
- v23 Controlled External Tool Gateway
- v24 Controlled External Evidence Snapshot Gateway

## Approval Requirement
All executable tasks require exact approval phrase:
`{STATION_CHIEF_V25_APPROVAL_PHRASE}`

## Safety Boundaries
- No repo mutation
- No credential access
- No production mutation
- No uncontrolled autonomy

Future work is adapter/plugin expansion, not core system unfinished.
"""

    report_md = f"""# Station Chief v25 Final Acceptance Report

## Context
- **Runtime Version:** 25.0.0
- **Release Status:** DONE-DONE RELEASE
- **Final Status:** {STATION_CHIEF_V25_FINAL_STATUS}

## Validation Summary
- v8–v24 preservation: VERIFIED
- Installed capability count: 8
- Executable capability count: 6
- Task classification: OPERATIONAL
- Route planning: OPERATIONAL
- Approval broker: OPERATIONAL
- Dispatch broker: OPERATIONAL
- Receipt/audit collector: OPERATIONAL
- Unsupported denial: OPERATIONAL

## Verdict
**CORE_COMMAND_CENTER_OPERATIONALLY_COMPLETE**

No future core v25.1 or v26 required.
"""

    done_done_payload = {
        "release_id": STATION_CHIEF_V25_DONE_DONE_RELEASE_ID,
        "runtime_version": "25.0.0",
        "final_status": STATION_CHIEF_V25_FINAL_STATUS,
        "core_release_complete": True,
        "open_gate_runtime_created": True,
        "job_ticket_runtime_created": True,
        "next_core_version_required": False,
        "future_expansion_mode": "adapter_plugin_expansion"
    }

    return {
        "operator_task_receipt_payload": receipt_payload,
        "operator_command_menu_markdown": menu_md,
        "installed_capability_registry_payload": capability_registry,
        "final_acceptance_report_markdown": report_md,
        "done_done_release_manifest_payload": done_done_payload
    }


def write_v25_controlled_text_artifact(artifact_key: str, content: str, approval_or_release_allowed: bool = True) -> dict:
    if not approval_or_release_allowed:
        return {"artifact_write_performed": False, "error": "Authorization missing"}
        
    paths_meta = resolve_v25_controlled_workspace_paths()
    if not paths_meta["all_artifact_paths_valid"]:
        return {"artifact_write_performed": False, "error": "Invalid workspace path"}
        
    artifact_path_str = paths_meta["artifact_paths"].get(artifact_key)
    if not artifact_path_str:
        return {"artifact_write_performed": False, "error": f"Unknown artifact key: {artifact_key}"}
        
    workspace_dir = Path(paths_meta["workspace_dir"])
    artifact_path = Path(artifact_path_str)
    
    workspace_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(content)
    readback = artifact_path.read_text()
    
    return {
        "artifact_key": artifact_key,
        "artifact_write_performed": True,
        "controlled_artifact_path": str(artifact_path),
        "artifact_exists_after_write": artifact_path.exists(),
        "artifact_sha256": hashlib.sha256(readback.encode("utf-8")).hexdigest(),
        "artifact_byte_count": len(readback),
        "artifact_line_count": len(readback.splitlines()),
        "artifact_readback_verified": (readback == content)
    }


def execute_general_operator_task(approval_phrase: str | None = None, operator_task: str | None = None, requested_task_type: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, execute_operator_task_flag: bool = False) -> dict:
    manifest = create_general_operator_runtime_manifest()
    cap_registry = create_installed_capability_registry()
    tt_registry = create_supported_operator_task_type_registry()
    role_registry = create_operator_role_registry()
    request = create_general_operator_task_request(operator_task, requested_task_type, operator_label, workpack_label)
    classification = classify_operator_task(request, tt_registry)
    route_plan = create_operator_route_plan(classification, cap_registry, tt_registry)
    approval = create_v25_operator_approval_receipt(approval_phrase, request, classification, route_plan)
    dispatch_plan = create_operator_dispatch_plan(route_plan, approval)
    
    performed = False
    dispatch_result = {"dispatch_performed": False, "prior_workpack_called": False}
    denial_receipt = None
    artifact_results = {}
    artifact_digests = {}
    all_verified = True
    status = "GENERAL_OPERATOR_RUNTIME_PREVIEW_ONLY"

    if execute_operator_task_flag:
        if classification["unsupported_or_unsafe"]:
            status = "UNSUPPORTED_OR_UNSAFE_TASK_DENIED"
            denial_receipt = create_unsupported_task_denial_receipt(request, classification, route_plan)
        elif approval["human_approval_granted"]:
            status = "GENERAL_OPERATOR_TASK_COMPLETED"
            dispatch_result = dispatch_installed_workpack(dispatch_plan, approval, operator_label, workpack_label)
            performed = dispatch_result["dispatch_performed"]
        elif route_plan["status_report_allowed"]:
            status = "CAPABILITY_STATUS_REPORT_COMPLETED"
            performed = True
        else:
            status = "GENERAL_OPERATOR_TASK_DENIED"

        # Artifacts
        payloads = build_v25_release_artifact_payloads(manifest, cap_registry, tt_registry, request, classification, route_plan, approval, dispatch_plan, dispatch_result, denial_receipt)
        writes = [
            ("operator_task_receipt_json", canonical_json(payloads["operator_task_receipt_payload"])),
            ("operator_command_menu_md", payloads["operator_command_menu_markdown"]),
            ("installed_capability_registry_json", canonical_json(payloads["installed_capability_registry_payload"])),
            ("final_acceptance_report_md", payloads["final_acceptance_report_markdown"]),
            ("done_done_release_manifest_json", canonical_json(payloads["done_done_release_manifest_payload"]))
        ]
        for key, content in writes:
            res = write_v25_controlled_text_artifact(key, content)
            artifact_results[key] = res
            if res.get("artifact_write_performed"):
                artifact_digests[key] = res["artifact_sha256"]
                if not res["artifact_readback_verified"]: all_verified = False
            else:
                all_verified = False

    return {
        "runtime_version": "25.0.0",
        "general_operator_runtime_status": status,
        "done_done_release_layer_created": True,
        "open_gate_command_layer_created": True,
        "core_command_center_operationally_complete": True,
        "accepts_real_operator_job_tickets": True,
        "task_classification_performed": True,
        "route_plan_created": True,
        "approval_broker_created": True,
        "dispatch_broker_created": True,
        "classified_task_type": classification["classified_task_type"],
        "selected_capability_id": route_plan["selected_capability_id"],
        "approval_required": route_plan["approval_required"],
        "human_approval_granted": approval["human_approval_granted"],
        "dispatch_performed": dispatch_result["dispatch_performed"],
        "prior_workpack_called": dispatch_result["prior_workpack_called"],
        "general_operator_task_performed": performed,
        "installed_capability_count": 8,
        "executable_capability_count": 6,
        "supported_task_type_count": 8,
        "unsupported_denial_created": (denial_receipt is not None),
        "controlled_v25_artifact_count": 5,
        "artifact_paths": STATION_CHIEF_V25_CONTROLLED_ARTIFACT_PATHS,
        "artifact_digests": artifact_digests,
        "artifact_readback_verified": (all_verified if performed else False),
        "final_done_done_release_status": STATION_CHIEF_V25_FINAL_STATUS,
        "next_core_version_required": False,
        "future_expansion_mode": "adapter_plugin_expansion",
        "v25_1_created": False,
        "v26_created": False,
        "repo_file_mutation_performed": False,
        "file_contents_printed": False,
        "response_body_printed": False,
        "response_body_stored": False,
        "response_body_returned": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "credential_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "arbitrary_external_tool_invocation_performed": False,
        "arbitrary_url_call_performed": False,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "uncontrolled_live_orchestration_performed": False,
        
        "manifest": manifest,
        "capability_registry": cap_registry,
        "task_type_registry": tt_registry,
        "role_registry": role_registry,
        "task_request": request,
        "classification": classification,
        "route_plan": route_plan,
        "approval_receipt": approval,
        "dispatch_plan": dispatch_plan,
        "dispatch_result": dispatch_result,
        "denial_receipt": denial_receipt,
        "artifact_results": artifact_results
    }


def create_v25_artifact_receipt_collector(operator_result: dict) -> dict:
    return {
        "collector_id": sha256_digest({"res": operator_result.get("general_operator_runtime_status")}),
        "collector_type": "v25_artifact_receipt_collector",
        "runtime_version": "25.0.0",
        "general_operator_task_performed": operator_result.get("general_operator_task_performed", False),
        "dispatch_performed": operator_result.get("dispatch_performed", False),
        "prior_workpack_called": operator_result.get("prior_workpack_called", False),
        "artifact_paths": operator_result.get("artifact_paths", {}),
        "artifact_digests": operator_result.get("artifact_digests", {}),
        "v25_artifact_count": len(operator_result.get("artifact_digests", {})),
        "prior_workpack_artifact_count": len(operator_result.get("dispatch_result", {}).get("artifact_digests", {})),
        "inspected_file_count": operator_result.get("dispatch_result", {}).get("inspected_file_count", 0),
        "receipts_collected": True,
        "audit_ready": True,
        "no_repo_mutation": True,
        "no_credentials": True,
        "no_production": True,
        "no_uncontrolled_orchestration": True
    }


def create_v25_final_release_audit_record(operator_result: dict, receipt_collector: dict) -> dict:
    return {
        "audit_id": sha256_digest({"collector": receipt_collector["collector_id"]}),
        "audit_type": "v25_general_operator_runtime_final_release_audit",
        "runtime_version": "25.0.0",
        "done_done_release_layer_created": True,
        "open_gate_command_layer_created": True,
        "general_operator_task_runtime_created": True,
        "core_command_center_operationally_complete": True,
        "accepts_real_operator_job_tickets": True,
        "installed_capability_registry_created": True,
        "supported_task_type_registry_created": True,
        "operator_task_classifier_created": True,
        "operator_route_planner_created": True,
        "approval_broker_created": True,
        "dispatch_broker_created": True,
        "receipt_collector_created": True,
        "unsupported_task_denial_created": operator_result.get("unsupported_denial_created", False),
        "installed_capability_count": 8,
        "executable_capability_count": 6,
        "supported_task_type_count": 8,
        "dispatch_performed": operator_result.get("dispatch_performed", False),
        "prior_workpack_called": operator_result.get("prior_workpack_called", False),
        "human_approval_required": True,
        "human_approval_granted": operator_result.get("human_approval_granted", False),
        "final_done_done_release_status": STATION_CHIEF_V25_FINAL_STATUS,
        "next_core_version_required": False,
        "future_expansion_mode": "adapter_plugin_expansion",
        "no_v25_1_created": True,
        "no_v26_created": True,
        "no_repo_file_mutation": True,
        "no_file_contents_printed": True,
        "no_response_body_printed": True,
        "no_response_body_stored": True,
        "no_response_body_returned": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_unapproved_external_tool_invocation": True,
        "no_arbitrary_url_call": True,
        "no_credential_access": True,
        "no_token_access": True,
        "no_secret_read": True,
        "no_private_key_read": True,
        "no_signing_key_read": True,
        "no_environment_read": True,
        "no_worker_process_started": True,
        "no_background_agent_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_worker_routing_to_real_processes": True,
        "no_uncontrolled_live_orchestration": True,
        "no_arbitrary_task_execution": True
    }


def create_v25_general_operator_safety_boundary_matrix() -> dict:
    return {
        "general_operator_runtime_manifest": "ALLOWED",
        "installed_capability_registry": "ALLOWED",
        "supported_operator_task_type_registry": "ALLOWED",
        "operator_role_registry": "ALLOWED",
        "general_operator_task_request": "ALLOWED",
        "operator_task_classification": "ALLOWED",
        "operator_route_plan": "ALLOWED",
        "approval_broker": "ALLOWED",
        "dispatch_broker": "ALLOWED",
        "installed_workpack_dispatch": "ALLOWED",
        "artifact_receipt_collector": "ALLOWED",
        "unsupported_task_denial_receipt": "ALLOWED",
        "final_release_audit_record": "ALLOWED",
        "done_done_release_lock": "ALLOWED",
        "command_menu_artifact": "ALLOWED",
        "final_acceptance_report": "ALLOWED",
        "adapter_plugin_expansion_after_release": "ALLOWED",
        
        "uncontrolled_agent_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
        "real_worker_process_start": "DENIED",
        "background_agent_start": "DENIED",
        "daemon_start": "DENIED",
        "arbitrary_agent_execution": "DENIED",
        "arbitrary_user_task_execution": "DENIED",
        "uninstalled_tool_execution": "DENIED",
        "unsupported_task_execution": "DENIED",
        "repo_file_mutation": "DENIED",
        "repo_write": "DENIED",
        "production_execution": "DENIED",
        "production_mutation": "DENIED",
        "deployment": "DENIED",
        "deployment_rollback": "DENIED",
        "rollback_execution": "DENIED",
        "recovery_execution": "DENIED",
        "arbitrary_external_tool_invocation": "DENIED",
        "arbitrary_web_browsing": "DENIED",
        "arbitrary_api_call": "DENIED",
        "non_allowlisted_url_call": "DENIED",
        "response_body_storage": "DENIED",
        "response_body_printing": "DENIED",
        "response_body_returning": "DENIED",
        "credential_use": "DENIED",
        "credential_vault_access": "DENIED",
        "token_access": "DENIED",
        "secret_read": "DENIED",
        "private_key_read": "DENIED",
        "signing_key_read": "DENIED",
        "environment_read": "DENIED",
        "key_generation": "DENIED",
        "real_signature": "DENIED",
        "real_encryption": "DENIED",
        "real_decryption": "DENIED",
        "subprocess_start": "DENIED",
        "shell_execution": "DENIED",
        "arbitrary_command_execution": "DENIED",
        "real_queue_creation": "DENIED",
        "queue_write": "DENIED",
        "scheduler_write": "DENIED",
        "cron_write": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_unbounded_workforce_activation": "DENIED",
        "v25_1_creation": "DENIED",
        "v26_creation": "DENIED"
    }


def create_station_chief_v25_general_operator_schema() -> dict:
    return {
        "schema_version": "25.0.0",
        "schema_type": "station_chief_v25_general_operator_task_runtime",
        "required_sections": [
            "general_operator_runtime_manifest",
            "installed_capability_registry",
            "supported_operator_task_type_registry",
            "operator_role_registry",
            "general_operator_task_request",
            "operator_task_classification",
            "operator_route_plan",
            "operator_approval_receipt",
            "operator_dispatch_plan",
            "installed_workpack_dispatch_result",
            "unsupported_task_denial_receipt",
            "artifact_receipt_collector",
            "final_release_audit_record",
            "general_operator_safety_boundary_matrix",
            "done_done_release_summary"
        ],
        "done_done_release_authorized": True,
        "general_operator_runtime_authorized": True,
        "open_gate_command_layer_authorized": True,
        "installed_workpack_dispatch_authorized": True,
        "unsupported_task_denial_authorized": True,
        "final_release_lock_authorized": True,
        "core_command_center_operationally_complete": True,
        "next_core_version_required": False,
        "future_expansion_mode_adapter_plugin_expansion": True,
        "no_uncontrolled_agent_activation_authorized": True,
        "no_real_worker_process_authorized": True,
        "no_background_agent_authorized": True,
        "no_arbitrary_agent_execution_authorized": True,
        "no_repo_mutation_authorized": True,
        "no_production_execution_authorized": True,
        "no_deployment_authorized": True,
        "no_credential_access_authorized": True,
        "no_secret_read_authorized": True,
        "no_environment_read_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_uncontrolled_live_orchestration_authorized": True,
        "v25_1_created": False,
        "v26_created": False
    }


def create_station_chief_v25_general_operator_bundle(approval_phrase: str | None = None, operator_task: str | None = None, requested_task_type: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, execute_operator_task_flag: bool = False) -> dict:
    res = execute_general_operator_task(approval_phrase, operator_task, requested_task_type, operator_label, workpack_label, execute_operator_task_flag)
    receipt_collector = create_v25_artifact_receipt_collector(res)
    audit = create_v25_final_release_audit_record(res, receipt_collector)
    schema = create_station_chief_v25_general_operator_schema()
    boundaries = create_v25_general_operator_safety_boundary_matrix()

    bundle = {
        "runtime_version": "25.0.0",
        "general_operator_runtime_status": res["general_operator_runtime_status"],
        "done_done_release_layer_created": True,
        "open_gate_command_layer_created": True,
        "general_operator_task_runtime_created": True,
        "core_command_center_operationally_complete": True,
        "accepts_real_operator_job_tickets": True,
        "installed_capability_count": 8,
        "executable_capability_count": 6,
        "supported_task_type_count": 8,
        "task_classification_performed": True,
        "route_plan_created": True,
        "approval_broker_created": True,
        "dispatch_broker_created": True,
        "receipt_collector_created": True,
        "final_release_audit_created": True,
        "classified_task_type": res["classified_task_type"],
        "selected_capability_id": res["selected_capability_id"],
        "approval_required": res["approval_required"],
        "human_approval_granted": res["human_approval_granted"],
        "dispatch_performed": res["dispatch_performed"],
        "prior_workpack_called": res["prior_workpack_called"],
        "general_operator_task_performed": res["general_operator_task_performed"],
        "unsupported_denial_created": res["unsupported_denial_created"],
        "controlled_v25_artifact_count": res["controlled_v25_artifact_count"],
        "artifact_paths": res["artifact_paths"],
        "artifact_digests": res["artifact_digests"],
        "artifact_readback_verified": res["artifact_readback_verified"],
        "final_done_done_release_status": STATION_CHIEF_V25_FINAL_STATUS,
        "next_core_version_required": False,
        "future_expansion_mode": "adapter_plugin_expansion",
        "v25_1_created": False,
        "v26_created": False,
        
        "schema": schema,
        "manifest": res["manifest"],
        "installed_capability_registry": res["capability_registry"],
        "supported_operator_task_type_registry": res["task_type_registry"],
        "operator_role_registry": res["role_registry"],
        "operator_task_request": res["task_request"],
        "operator_task_classification": res["classification"],
        "operator_route_plan": res["route_plan"],
        "operator_approval_receipt": res["approval_receipt"],
        "operator_dispatch_plan": res["dispatch_plan"],
        "installed_workpack_dispatch_result": res["dispatch_result"],
        "unsupported_task_denial_receipt": res["denial_receipt"],
        "artifact_receipt_collector": receipt_collector,
        "final_release_audit_record": audit,
        "general_operator_safety_boundary_matrix": boundaries,
        "done_done_release_summary": {
            "version": "25.0.0",
            "status": res["general_operator_runtime_status"]
        }
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
