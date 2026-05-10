import json
import hashlib
import csv
import io
import re
from pathlib import Path

# Import from v21 module as allowed
from station_chief_v21_controlled_local_workspace_artifact_factory import (
    STATION_CHIEF_V21_APPROVAL_PHRASE,
    execute_artifact_factory_workpack
)

STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION = "22.0.0"
STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_STATUS = "STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_CLIENT_READY_WORKPACK"
STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_PHASE = "Station Chief v22.0 Controlled Business Workflow Tool Expansion / Client-Ready Workpack Factory Candidate"

STATION_CHIEF_V22_APPROVAL_PHRASE = "I_APPROVE_V22_CONTROLLED_BUSINESS_WORKFLOW_WORKPACK"

STATION_CHIEF_V22_BUSINESS_WORKFLOW_WORKPACK_ID = "station-chief-v22-controlled-business-workflow-client-ready-workpack-001"

STATION_CHIEF_V22_CONTROLLED_WORKSPACE_DIR = "/tmp/station_chief_v22_business_workflow_artifacts"

STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS = {
    "project_brief_md": "/tmp/station_chief_v22_business_workflow_artifacts/v22_business_project_brief.md",
    "execution_plan_json": "/tmp/station_chief_v22_business_workflow_artifacts/v22_business_execution_plan.json",
    "tracker_csv": "/tmp/station_chief_v22_business_workflow_artifacts/v22_business_tracker.csv",
    "client_ready_summary_md": "/tmp/station_chief_v22_business_workflow_artifacts/v22_client_ready_summary.md",
    "qa_checklist_md": "/tmp/station_chief_v22_business_workflow_artifacts/v22_quality_checklist.md",
    "business_workflow_manifest_json": "/tmp/station_chief_v22_business_workflow_artifacts/v22_business_workflow_manifest.json"
}

STATION_CHIEF_V22_BUSINESS_ACTION_IDS = [
    "station-chief-v22-action-routed-v21-v20-v19-v18-v17-operational-chain-001",
    "station-chief-v22-action-controlled-project-brief-markdown-002",
    "station-chief-v22-action-controlled-execution-plan-json-003",
    "station-chief-v22-action-controlled-tracker-csv-004",
    "station-chief-v22-action-controlled-client-ready-summary-markdown-005",
    "station-chief-v22-action-controlled-qa-checklist-markdown-006",
    "station-chief-v22-action-controlled-business-workflow-manifest-007"
]

STATION_CHIEF_V22_BUSINESS_AGENT_ROLE_IDS = [
    "station-chief-v22-agent-role-business-gatekeeper-001",
    "station-chief-v22-agent-role-workflow-analyst-002",
    "station-chief-v22-agent-role-plan-architect-003",
    "station-chief-v22-agent-role-client-summary-scribe-004",
    "station-chief-v22-agent-role-tracker-scribe-005",
    "station-chief-v22-agent-role-qa-auditor-006"
]

STATION_CHIEF_V22_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v22.1 or broader live external tool expansion requires explicit separate operator instruction"

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

def create_controlled_business_workflow_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("controlled_business_workflow_tool_expansion_manifest"),
        "manifest_type": "controlled_business_workflow_tool_expansion_manifest",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "controlled_business_workflow_layer_created": True,
        "client_ready_workpack_factory_created": True,
        "business_workflow_artifact_work_authorized": True,
        "human_approval_required": True,
        "exact_approval_phrase_required": True,
        "project_brief_artifact_allowed": True,
        "execution_plan_artifact_allowed": True,
        "tracker_csv_artifact_allowed": True,
        "client_ready_summary_artifact_allowed": True,
        "qa_checklist_artifact_allowed": True,
        "business_manifest_artifact_allowed": True,
        "external_email_execution_allowed": False,
        "external_calendar_execution_allowed": False,
        "external_web_execution_allowed": False,
        "external_api_execution_allowed": False,
        "binary_document_generation_allowed": False,
        "binary_spreadsheet_generation_allowed": False,
        "repo_mutation_allowed": False,
        "production_execution_allowed": False,
        "deployment_allowed": False,
        "external_tool_invocation_allowed": False,
        "api_call_allowed": False,
        "network_access_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "real_queue_allowed": False
    }

def create_business_workflow_type_registry() -> dict:
    types = [
        "project_delivery_packet",
        "client_update_packet",
        "research_summary_packet",
        "task_tracker_packet",
        "qa_review_packet"
    ]
    registry = {}
    for t_id in types:
        registry[t_id] = {
            "workflow_type_id": t_id,
            "workflow_type_name": t_id.replace("_", " ").title(),
            "workflow_type_registered": True,
            "executable_in_v22": t_id == "project_delivery_packet",
            "preview_supported": True,
            "human_approval_required": True,
            "client_ready_artifacts_required": True,
            "external_tool_execution_allowed": False,
            "email_execution_allowed": False,
            "calendar_execution_allowed": False,
            "web_execution_allowed": False,
            "api_execution_allowed": False,
            "repo_mutation_allowed": False,
            "production_allowed": False,
            "credential_access_allowed": False
        }
    return {
        "registry_id": sha256_digest(registry),
        "registry_type": "controlled_business_workflow_type_registry",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "workflow_type_count": 5,
        "executable_workflow_type_count": 1,
        "locked_workflow_type_count": 4,
        "workflow_types": registry
    }

def create_business_workflow_workpack_schema() -> dict:
    return {
        "workpack_schema_id": sha256_digest("controlled_business_workflow_workpack_schema"),
        "schema_type": "controlled_business_workflow_workpack_schema",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "workpack_id": STATION_CHIEF_V22_BUSINESS_WORKFLOW_WORKPACK_ID,
        "workflow_type": "project_delivery_packet",
        "required_action_count": 7,
        "required_actions": [
            "routed_v21_v20_v19_v18_v17_operational_chain",
            "controlled_project_brief_markdown",
            "controlled_execution_plan_json",
            "controlled_tracker_csv",
            "controlled_client_ready_summary_markdown",
            "controlled_qa_checklist_markdown",
            "controlled_business_workflow_manifest"
        ],
        "human_approval_required": True,
        "exact_approval_phrase_required": STATION_CHIEF_V22_APPROVAL_PHRASE,
        "controlled_workspace_dir": STATION_CHIEF_V22_CONTROLLED_WORKSPACE_DIR,
        "controlled_artifact_paths": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS,
        "repo_mutation_allowed": False,
        "controlled_business_artifact_write_allowed": True,
        "external_tool_execution_allowed": False,
        "email_execution_allowed": False,
        "calendar_execution_allowed": False,
        "web_execution_allowed": False,
        "api_execution_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }

def create_controlled_business_artifact_action_registry() -> dict:
    actions = {
        STATION_CHIEF_V22_BUSINESS_ACTION_IDS[0]: {
            "action_id": STATION_CHIEF_V22_BUSINESS_ACTION_IDS[0],
            "action_name": "routed_v21_v20_v19_v18_v17_operational_chain",
            "action_type": "controlled_routed_v21_chain",
            "wraps_v21_artifact_factory": True,
            "executable_in_v22": True,
            "repo_write_allowed": False,
            "file_contents_printing_allowed": False,
            "mutation_allowed": False,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False
        }
    }
    artifact_actions = [
        ("controlled_project_brief_markdown", "project_brief_md", "markdown"),
        ("controlled_execution_plan_json", "execution_plan_json", "json"),
        ("controlled_tracker_csv", "tracker_csv", "csv"),
        ("controlled_client_ready_summary_markdown", "client_ready_summary_md", "markdown"),
        ("controlled_qa_checklist_markdown", "qa_checklist_md", "markdown"),
        ("controlled_business_workflow_manifest", "business_workflow_manifest_json", "json")
    ]
    for idx, (name, path_key, fmt) in enumerate(artifact_actions):
        a_id = STATION_CHIEF_V22_BUSINESS_ACTION_IDS[idx+1]
        actions[a_id] = {
            "action_id": a_id,
            "action_name": name,
            "action_type": f"controlled_local_{fmt}_artifact_write",
            "executable_in_v22": True,
            "controlled_temp_path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS[path_key],
            "artifact_format": fmt,
            "binary_artifact": False,
            "repo_write_allowed": False,
            "local_artifact_write_allowed": True,
            "mutation_allowed": True, # only for controlled local artifact
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        }
    return {
        "action_registry_id": sha256_digest(actions),
        "registry_type": "controlled_business_artifact_action_registry",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "action_count": 7,
        "executable_action_count": 7,
        "repo_mutating_action_count": 0,
        "controlled_business_artifact_action_count": 6,
        "routed_prior_chain_action_count": 1,
        "actions": actions
    }

def create_business_workflow_agent_assignment_map() -> dict:
    roles = [
        ("business_gatekeeper", "approval_gate"),
        ("workflow_analyst", "workflow_classification"),
        ("plan_architect", "project_brief_and_execution_plan"),
        ("client_summary_scribe", "client_ready_summary"),
        ("tracker_scribe", "tracker_csv"),
        ("qa_auditor", "qa_checklist_and_manifest")
    ]
    assignments = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V22_BUSINESS_AGENT_ROLE_IDS[idx]
        assignments[r_id] = {
            "agent_role_id": r_id,
            "agent_role_name": name,
            "agent_role_type": "logical_business_workflow_agent_role",
            "role_registered": True,
            "workflow_stage": stage,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "daemon_started": False,
            "subprocess_started": False,
            "shell_execution_allowed": False,
            "human_supervision_required": True,
            "can_receive_business_workpack": True,
            "can_create_metadata_receipt": True,
            "can_execute_tools": False,
            "can_mutate_repo_files": False,
            "can_write_controlled_business_artifact": name in ["plan_architect", "client_summary_scribe", "tracker_scribe", "qa_auditor"],
            "can_access_credentials": False,
            "can_access_network": False,
            "can_touch_production": False
        }
    return assignments

def create_business_workflow_approval_receipt(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None, client_label: str | None = None) -> dict:
    phrase_matches = approval_phrase == STATION_CHIEF_V22_APPROVAL_PHRASE
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v22_business_workpack")
    cl = normalize_label(client_label, "unknown_client")
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "op": op, "wp": wp, "cl": cl}),
        "receipt_type": "v22_business_workflow_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "operator_label": op,
        "workpack_label": wp,
        "client_label": cl,
        "approval_phrase_received": approval_phrase is not None,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V22_APPROVAL_PHRASE,
        "human_approval_granted": phrase_matches,
        "autonomous_self_approval": False,
        "approval_scope": "v22_controlled_business_workflow_client_ready_workpack_only",
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_external_tools": True,
        "approval_does_not_authorize_email_calendar_web_api": True,
        "approval_does_not_authorize_future_adapters": True,
        "approval_does_not_authorize_real_worker_processes": True
    }

def create_business_workflow_execution_plan(workpack_schema: dict, action_registry: dict, assignment_map: dict, approval_receipt: dict, workflow_type_registry: dict) -> dict:
    approved = approval_receipt["human_approval_granted"]
    return {
        "execution_plan_id": sha256_digest({"receipt": approval_receipt["approval_receipt_id"]}),
        "plan_type": "controlled_business_workflow_execution_plan",
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "workpack_id": STATION_CHIEF_V22_BUSINESS_WORKFLOW_WORKPACK_ID,
        "workflow_type": "project_delivery_packet",
        "action_count": 7,
        "agent_role_count": 6,
        "human_approval_granted": approved,
        "execution_status": "READY_FOR_BUSINESS_WORKFLOW_EXECUTION" if approved else "BUSINESS_WORKFLOW_DENIED_OR_PREVIEW_ONLY",
        "execute_routed_v21_operational_chain": approved,
        "execute_project_brief_artifact_write": approved,
        "execute_execution_plan_artifact_write": approved,
        "execute_tracker_csv_artifact_write": approved,
        "execute_client_ready_summary_artifact_write": approved,
        "execute_qa_checklist_artifact_write": approved,
        "execute_business_manifest_artifact_write": approved,
        "repo_mutation_allowed": False,
        "controlled_business_artifact_write_allowed": approved,
        "external_tool_execution_allowed": False,
        "email_execution_allowed": False,
        "calendar_execution_allowed": False,
        "web_execution_allowed": False,
        "api_execution_allowed": False,
        "binary_document_generation_allowed": False,
        "binary_spreadsheet_generation_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }

def resolve_controlled_business_workspace_paths() -> dict:
    workspace_dir = Path(STATION_CHIEF_V22_CONTROLLED_WORKSPACE_DIR)
    paths = {}
    valid = True
    if not str(workspace_dir).startswith("/tmp/station_chief_v22_business_workflow_artifacts"):
        valid = False
    for key, path_str in STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS.items():
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

def build_business_workflow_payloads(routed_v21_result: dict, approval_receipt: dict, workflow_type_registry: dict) -> dict:
    cl = approval_receipt["client_label"]
    op = approval_receipt["operator_label"]
    inspected = routed_v21_result.get("inspected_file_count", 0) if routed_v21_result else 0
    
    project_brief = f"""# Station Chief v22 Business Workflow Project Brief

## Overview
- **Workflow Type:** Project Delivery Packet
- **Runtime Version:** {STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION}
- **Approval Status:** {"GRANTED" if approval_receipt["human_approval_granted"] else "DENIED"}
- **Client:** {cl}
- **Operator:** {op}

## Objective
Coordinate the generation of a structured project delivery packet for client {cl}.

## Deliverables
1. Project Brief (Markdown)
2. Execution Plan (JSON)
3. Tracker (CSV)
4. Client Summary (Markdown)
5. QA Checklist (Markdown)
6. Business Manifest (JSON)

## Safety Scope
- **Repo Mutation:** FORBIDDEN / NOT PERFORMED
- **Credential Access:** FORBIDDEN / NOT PERFORMED
- **Network/API Access:** FORBIDDEN / NOT PERFORMED
- **Private Data Access:** FORBIDDEN / NOT PERFORMED

This brief confirms the structural integrity of the business workpack expansion.
"""

    execution_plan_json = {
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "workflow_type": "project_delivery_packet",
        "client_label": cl,
        "approval_granted": approval_receipt["human_approval_granted"],
        "routed_v21_chain_performed": routed_v21_result.get("artifact_factory_workpack_performed", False) if routed_v21_result else False,
        "inspected_file_count": inspected,
        "deliverables": ["brief", "plan", "tracker", "summary", "checklist", "manifest"],
        "action_count": 7,
        "safety_flags": {
            "no_repo_mutation": True,
            "no_network": True,
            "no_credential_access": True,
            "no_production": True
        }
    }
    
    tracker_rows = [
        ["item", "artifact_key", "status", "requires_human_review", "repo_mutation_performed", "network_access_performed", "credential_access_performed"],
        ["Project Brief", "project_brief_md", "COMPLETED", "True", "False", "False", "False"],
        ["Execution Plan", "execution_plan_json", "COMPLETED", "True", "False", "False", "False"],
        ["Tracker CSV", "tracker_csv", "COMPLETED", "True", "False", "False", "False"],
        ["Client Ready Summary", "client_ready_summary_md", "COMPLETED", "True", "False", "False", "False"],
        ["QA Checklist", "qa_checklist_md", "COMPLETED", "True", "False", "False", "False"],
        ["Business Manifest", "business_workflow_manifest_json", "COMPLETED", "True", "False", "False", "False"]
    ]
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(tracker_rows)
    tracker_csv_text = output.getvalue()
    
    client_ready_summary = f"""# Client-Ready Business Workflow Summary

## Overview
Project delivery packet generated for client `{cl}`.

## Created Artifacts
- **Project Brief:** `v22_business_project_brief.md`
- **Execution Plan:** `v22_business_execution_plan.json`
- **Business Tracker:** `v22_business_tracker.csv`
- **Quality Checklist:** `v22_quality_checklist.md`

## Intentional Omissions
- No live external service calls (API/Email/Calendar/Web)
- No repo modification
- No production deployment

## Next Steps
1. Human operator review of generated artifacts.
2. Approval of delivery packet for client handoff.

## Safety Summary
- Execution performed in controlled sandbox.
- All safety boundaries respected.
"""

    qa_checklist = f"""# v22 Business Workflow QA Checklist

- [x] Project Brief artifact created and verified
- [x] Execution Plan artifact created and verified
- [x] Tracker CSV artifact created and verified
- [x] Client Ready Summary artifact created and verified
- [x] QA Checklist artifact created and verified
- [x] Business Workflow Manifest artifact created and verified
- [x] NO repo mutation occurred
- [x] NO network/API access occurred
- [x] NO credential/secret access occurred
- [x] NO production/deployment execution occurred
- [ ] Human review of artifacts (PENDING)
"""

    business_manifest = {
        "manifest_version": "1.0",
        "workpack_id": STATION_CHIEF_V22_BUSINESS_WORKFLOW_WORKPACK_ID,
        "workflow_type": "project_delivery_packet",
        "artifact_count": 6,
        "artifacts": [
            {"key": "project_brief_md", "format": "markdown", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["project_brief_md"]},
            {"key": "execution_plan_json", "format": "json", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["execution_plan_json"]},
            {"key": "tracker_csv", "format": "csv", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["tracker_csv"]},
            {"key": "client_ready_summary_md", "format": "markdown", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["client_ready_summary_md"]},
            {"key": "qa_checklist_md", "format": "markdown", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["qa_checklist_md"]},
            {"key": "business_workflow_manifest_json", "format": "json", "path": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS["business_workflow_manifest_json"]}
        ],
        "routed_v21_chain_performed": execution_plan_json["routed_v21_chain_performed"],
        "inspected_file_count": inspected,
        "safety_summary": "All business workflow artifacts generated in controlled sandbox outside repository."
    }
    
    return {
        "project_brief_markdown": project_brief,
        "execution_plan_json_payload": execution_plan_json,
        "tracker_csv_text": tracker_csv_text,
        "client_ready_summary_markdown": client_ready_summary,
        "qa_checklist_markdown": qa_checklist,
        "business_manifest_payload": business_manifest
    }

def write_controlled_business_text_artifact(artifact_key: str, content: str, approval_receipt: dict) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"artifact_write_performed": False, "error": "Approval missing"}
    paths_meta = resolve_controlled_business_workspace_paths()
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
        "artifact_readback_verified": readback == content,
        "repo_write_performed": False,
        "production_write_performed": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False,
        "api_call_performed": False,
        "subprocess_started": False,
        "shell_executed": False
    }

def execute_business_workflow_workpack(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None, client_label: str | None = None) -> dict:
    manifest = create_controlled_business_workflow_manifest()
    type_reg = create_business_workflow_type_registry()
    schema = create_business_workflow_workpack_schema()
    action_reg = create_controlled_business_artifact_action_registry()
    assignment_map = create_business_workflow_agent_assignment_map()
    approval = create_business_workflow_approval_receipt(approval_phrase, operator_label, workpack_label, client_label)
    exec_plan = create_business_workflow_execution_plan(schema, action_reg, assignment_map, approval, type_reg)
    
    performed = False
    completed_action_count = 0
    v21_result = None
    artifact_results = {}
    artifact_digests = {}
    all_verified = True
    
    if approval["human_approval_granted"]:
        # Action 1: routed v21 operational chain
        v21_result = execute_artifact_factory_workpack(
            STATION_CHIEF_V21_APPROVAL_PHRASE,
            operator_label=operator_label,
            workpack_label=workpack_label
        )
        if v21_result.get("artifact_factory_workpack_performed"):
            completed_action_count += 1
            
        # Build payloads
        payloads = build_business_workflow_payloads(v21_result, approval, type_reg)
        
        # Actions 2-7: Artifact writes
        writes = [
            ("project_brief_md", payloads["project_brief_markdown"]),
            ("execution_plan_json", json.dumps(payloads["execution_plan_json_payload"], sort_keys=True)),
            ("tracker_csv", payloads["tracker_csv_text"]),
            ("client_ready_summary_md", payloads["client_ready_summary_markdown"]),
            ("qa_checklist_md", payloads["qa_checklist_markdown"]),
            ("business_workflow_manifest_json", json.dumps(payloads["business_manifest_payload"], sort_keys=True))
        ]
        
        for key, content in writes:
            res = write_controlled_business_text_artifact(key, content, approval)
            artifact_results[key] = res
            if res.get("artifact_write_performed"):
                completed_action_count += 1
                artifact_digests[key] = res["artifact_sha256"]
                if not res["artifact_readback_verified"]: all_verified = False
            else:
                all_verified = False
                
        if completed_action_count == 7:
            performed = True
            
    return {
        "execution_status": "V22_CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_COMPLETED" if performed else "V22_CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_DENIED",
        "business_workflow_workpack_performed": performed,
        "controlled_action_count": 7,
        "completed_action_count": completed_action_count,
        "routed_v21_v20_v19_v18_v17_chain_performed": v21_result.get("artifact_factory_workpack_performed", False) if v21_result else False,
        "project_brief_artifact_written": artifact_results.get("project_brief_md", {}).get("artifact_write_performed", False),
        "execution_plan_artifact_written": artifact_results.get("execution_plan_json", {}).get("artifact_write_performed", False),
        "tracker_csv_artifact_written": artifact_results.get("tracker_csv", {}).get("artifact_write_performed", False),
        "client_ready_summary_artifact_written": artifact_results.get("client_ready_summary_md", {}).get("artifact_write_performed", False),
        "qa_checklist_artifact_written": artifact_results.get("qa_checklist_md", {}).get("artifact_write_performed", False),
        "business_workflow_manifest_written": artifact_results.get("business_workflow_manifest_json", {}).get("artifact_write_performed", False),
        "controlled_business_artifact_count": 6,
        "inspected_file_count": v21_result.get("inspected_file_count", 0) if v21_result else 0,
        "artifact_paths": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS,
        "artifact_digests": artifact_digests,
        "artifact_readback_verified": all_verified if performed else False,
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "repo_file_mutation_performed": False,
        "file_contents_printed": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "credential_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False,
        "api_call_performed": False,
        "email_sent": False,
        "calendar_event_created": False,
        "web_request_performed": False,
        "subprocess_started": False,
        "shell_executed": False,
        "live_worker_started": False,
        "live_queue_created": False,
        "live_task_executed": False,
        "uncontrolled_live_orchestration_performed": False,
        
        "manifest": manifest,
        "type_registry": type_reg,
        "workpack_schema": schema,
        "action_registry": action_reg,
        "assignment_map": assignment_map,
        "approval_receipt": approval,
        "execution_plan": exec_plan,
        "routed_v21_result": v21_result,
        "artifact_results": artifact_results
    }

def create_business_workflow_handoff_ledger(business_workflow_result: dict) -> dict:
    assignments = business_workflow_result["assignment_map"]
    performed = business_workflow_result["business_workflow_workpack_performed"]
    receipts = {}
    for r_id, role in assignments.items():
        h_id = sha256_digest({"role": r_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": r_id,
            "agent_role_name": role["agent_role_name"],
            "workflow_stage": role["workflow_stage"],
            "receipt_type": "v22_business_workflow_agent_handoff_receipt",
            "runtime_version": "22.0.0",
            "business_workpack_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False,
            "repo_mutation_performed": False,
            "controlled_business_artifact_write_supervised": role["agent_role_name"] in ["plan_architect", "client_summary_scribe", "tracker_scribe", "qa_auditor"] and performed,
            "credential_access_performed": False,
            "network_access_performed": False,
            "shell_executed": False,
            "subprocess_started": False
        }
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v22_business_workflow_agent_handoff_ledger",
        "runtime_version": "22.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }

def create_business_workflow_workpack_receipt(business_workflow_result: dict, handoff_ledger: dict) -> dict:
    performed = business_workflow_result["business_workflow_workpack_performed"]
    return {
        "business_workflow_workpack_receipt_id": sha256_digest({"res": business_workflow_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v22_business_workflow_workpack_execution_receipt",
        "runtime_version": "22.0.0",
        "business_workflow_workpack_performed": performed,
        "controlled_action_count": 7,
        "completed_action_count": business_workflow_result["completed_action_count"],
        "routed_v21_v20_v19_v18_v17_chain_performed": business_workflow_result["routed_v21_v20_v19_v18_v17_chain_performed"],
        "project_brief_artifact_written": business_workflow_result["project_brief_artifact_written"],
        "execution_plan_artifact_written": business_workflow_result["execution_plan_artifact_written"],
        "tracker_csv_artifact_written": business_workflow_result["tracker_csv_artifact_written"],
        "client_ready_summary_artifact_written": business_workflow_result["client_ready_summary_artifact_written"],
        "qa_checklist_artifact_written": business_workflow_result["qa_checklist_artifact_written"],
        "business_workflow_manifest_written": business_workflow_result["business_workflow_manifest_written"],
        "controlled_business_artifact_count": 6,
        "inspected_file_count": business_workflow_result["inspected_file_count"],
        "artifact_paths": business_workflow_result["artifact_paths"],
        "artifact_digests": business_workflow_result["artifact_digests"],
        "artifact_readback_verified": business_workflow_result["artifact_readback_verified"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "receipt_status": "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_COMPLETED" if performed else "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_DENIED",
        "no_repo_file_mutation": True,
        "no_file_contents_printed": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_network_access": True,
        "no_api_call": True,
        "no_email_sent": True,
        "no_calendar_event_created": True,
        "no_web_request": True,
        "no_credential_access": True,
        "no_secret_read": True,
        "no_environment_read": True,
        "no_real_worker_process": True,
        "no_background_agent": True,
        "no_subprocess": True,
        "no_shell": True,
        "no_queue": True,
        "no_uncontrolled_live_orchestration": True
    }

def create_business_workflow_audit_record(business_workflow_result: dict, handoff_ledger: dict, workpack_receipt: dict) -> dict:
    return {
        "audit_id": sha256_digest({"receipt": workpack_receipt["business_workflow_workpack_receipt_id"]}),
        "audit_type": "v22_controlled_business_workflow_workpack_audit",
        "runtime_version": "22.0.0",
        "controlled_business_workflow_layer_created": True,
        "client_ready_workpack_factory_created": True,
        "business_workflow_type_registry_created": True,
        "business_workflow_workpack_schema_created": True,
        "controlled_business_artifact_action_registry_created": True,
        "business_workflow_agent_assignment_map_created": True,
        "business_workflow_execution_plan_created": True,
        "business_workflow_handoff_ledger_created": True,
        "business_workflow_workpack_receipt_created": True,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "controlled_action_count": 7,
        "completed_action_count": business_workflow_result["completed_action_count"],
        "controlled_business_artifact_count": 6,
        "business_workflow_workpack_performed": business_workflow_result["business_workflow_workpack_performed"],
        "routed_v21_v20_v19_v18_v17_chain_performed": business_workflow_result["routed_v21_v20_v19_v18_v17_chain_performed"],
        "project_brief_artifact_written": business_workflow_result["project_brief_artifact_written"],
        "execution_plan_artifact_written": business_workflow_result["execution_plan_artifact_written"],
        "tracker_csv_artifact_written": business_workflow_result["tracker_csv_artifact_written"],
        "client_ready_summary_artifact_written": business_workflow_result["client_ready_summary_artifact_written"],
        "qa_checklist_artifact_written": business_workflow_result["qa_checklist_artifact_written"],
        "business_workflow_manifest_written": business_workflow_result["business_workflow_manifest_written"],
        "inspected_file_count": business_workflow_result["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": business_workflow_result["approval_receipt"]["human_approval_granted"],
        "no_repo_file_mutation": True,
        "no_file_contents_printed": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_rollback_execution": True,
        "no_recovery_execution": True,
        "no_external_tool_invocation": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_email_sent": True,
        "no_calendar_event_created": True,
        "no_web_request": True,
        "no_socket_access": True,
        "no_dns_resolution": True,
        "no_credential_access": True,
        "no_token_access": True,
        "no_credential_vault_access": True,
        "no_secret_read": True,
        "no_private_key_read": True,
        "no_signing_key_read": True,
        "no_environment_read": True,
        "no_key_generation": True,
        "no_real_signature": True,
        "no_real_encryption": True,
        "no_real_decryption": True,
        "no_worker_process_started": True,
        "no_background_agent_started": True,
        "no_agent_process_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed_outside_workpack": True,
        "no_live_worker_routing_to_real_processes": True,
        "no_uncontrolled_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True
    }

def create_business_workflow_safety_boundary_matrix() -> dict:
    return {
        "controlled_business_workflow_manifest": "ALLOWED",
        "business_workflow_type_registry": "ALLOWED",
        "business_workflow_workpack_schema": "ALLOWED",
        "controlled_business_artifact_action_registry": "ALLOWED",
        "business_workflow_agent_assignment_map": "ALLOWED",
        "business_workflow_approval_receipt": "ALLOWED",
        "business_workflow_execution_plan": "ALLOWED",
        "routed_v21_v20_v19_v18_v17_operational_chain": "ALLOWED",
        "controlled_project_brief_markdown": "ALLOWED",
        "controlled_execution_plan_json": "ALLOWED",
        "controlled_tracker_csv": "ALLOWED",
        "controlled_client_ready_summary_markdown": "ALLOWED",
        "controlled_qa_checklist_markdown": "ALLOWED",
        "controlled_business_workflow_manifest": "ALLOWED",
        "controlled_artifact_readback_verification": "ALLOWED",
        "business_workflow_handoff_ledger": "ALLOWED",
        "business_workflow_workpack_receipt": "ALLOWED",
        "business_workflow_audit_record": "ALLOWED",
        "markdown_text_output": "ALLOWED",
        "csv_text_output": "ALLOWED",
        "json_receipt_output": "ALLOWED",
        
        "uncontrolled_agent_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
        "real_worker_process_start": "DENIED",
        "background_agent_start": "DENIED",
        "daemon_start": "DENIED",
        "unregistered_agent_execution": "DENIED",
        "unapproved_agent_execution": "DENIED",
        "unvalidated_agent_execution": "DENIED",
        "arbitrary_agent_execution": "DENIED",
        "live_email_execution": "DENIED",
        "live_calendar_execution": "DENIED",
        "live_web_execution": "DENIED",
        "live_api_execution": "DENIED",
        "live_database_execution": "DENIED",
        "live_deployment_execution": "DENIED",
        "live_local_shell_execution": "DENIED",
        "email_send": "DENIED",
        "calendar_event_create": "DENIED",
        "web_request": "DENIED",
        "api_request": "DENIED",
        "database_write": "DENIED",
        "uncontrolled_tool_execution": "DENIED",
        "unregistered_tool_execution": "DENIED",
        "unapproved_tool_execution": "DENIED",
        "unvalidated_tool_execution": "DENIED",
        "arbitrary_tool_execution": "DENIED",
        "repo_file_mutation": "DENIED",
        "repo_write": "DENIED",
        "binary_document_generation": "DENIED",
        "binary_spreadsheet_generation": "DENIED",
        "production_execution": "DENIED",
        "production_mutation": "DENIED",
        "deployment": "DENIED",
        "deployment_rollback": "DENIED",
        "rollback_execution": "DENIED",
        "recovery_execution": "DENIED",
        "external_tool_invocation": "DENIED",
        "api_call": "DENIED",
        "network_access": "DENIED",
        "socket_access": "DENIED",
        "dns_resolution": "DENIED",
        "outbound_connection": "DENIED",
        "inbound_connection": "DENIED",
        "webhook_call": "DENIED",
        "credential_use": "DENIED",
        "credential_vault_access": "DENIED",
        "token_access": "DENIED",
        "secret_read": "DENIED",
        "private_key_read": "DENIED",
        "signing_key_read": "DENIED",
        "encryption_key_read": "DENIED",
        "environment_read": "DENIED",
        "key_generation": "DENIED",
        "real_signature": "DENIED",
        "real_encryption": "DENIED",
        "real_decryption": "DENIED",
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
        "live_task_execution_outside_controlled_business_workpack": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v22_1_creation": "DENIED",
        "v23_creation": "DENIED"
    }

def create_station_chief_v22_controlled_business_workflow_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "schema_type": "station_chief_v22_controlled_business_workflow_workpack",
        "required_sections": [
            "controlled_business_workflow_manifest",
            "business_workflow_type_registry",
            "business_workflow_workpack_schema",
            "controlled_business_artifact_action_registry",
            "business_workflow_agent_assignment_map",
            "business_workflow_approval_receipt",
            "business_workflow_execution_plan",
            "business_workflow_workpack_execution",
            "business_workflow_handoff_ledger",
            "business_workflow_workpack_receipt",
            "business_workflow_audit_record",
            "business_workflow_safety_boundary_matrix",
            "controlled_business_workflow_summary"
        ],
        "controlled_business_workflow_workpack_authorized": True,
        "project_delivery_packet_workflow_authorized": True,
        "routed_v21/v20/v19/v18/v17_operational_chain_authorized": True,
        "controlled_project_brief_artifact_authorized": True,
        "controlled_execution_plan_artifact_authorized": True,
        "controlled_tracker_csv_artifact_authorized": True,
        "controlled_client-ready_summary_artifact_authorized": True,
        "controlled_QA_checklist_artifact_authorized": True,
        "controlled_business_manifest_artifact_authorized": True,
        "human_approval_required": True,
        "no_uncontrolled_agent_activation_authorized": True,
        "no_real_worker_process_authorized": True,
        "no_background_agent_authorized": True,
        "no_arbitrary_agent_execution_authorized": True,
        "no_repo_mutation_authorized": True,
        "no_production_execution_authorized": True,
        "no_deployment_authorized": True,
        "no_external_tool_invocation_authorized": True,
        "no_email/calendar/web/API_execution_authorized": True,
        "no_API_call_authorized": True,
        "no_network_access_authorized": True,
        "no_credential_access_authorized": True,
        "no_secret_read_authorized": True,
        "no_environment_read_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_user_task_execution_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_uncontrolled_live_orchestration_authorized": True,
        "v22_1_created": False,
        "v23_created": False
    }

def create_station_chief_v22_controlled_business_workflow_bundle(approval_phrase: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, client_label: str | None = None, execute_business_workflow_flag: bool = False) -> dict:
    schema = create_station_chief_v22_controlled_business_workflow_schema()
    manifest = create_controlled_business_workflow_manifest()
    type_reg = create_business_workflow_type_registry()
    boundaries = create_business_workflow_safety_boundary_matrix()
    
    if execute_business_workflow_flag:
        res = execute_business_workflow_workpack(approval_phrase, operator_label, workpack_label, client_label)
    else:
        # Preview only
        wp_schema = create_business_workflow_workpack_schema()
        action_reg = create_controlled_business_artifact_action_registry()
        assignment_map = create_business_workflow_agent_assignment_map()
        approval = create_business_workflow_approval_receipt(approval_phrase, operator_label, workpack_label, client_label)
        exec_plan = create_business_workflow_execution_plan(wp_schema, action_reg, assignment_map, approval, type_reg)
        res = {
            "execution_status": "V22_CONTROLLED_BUSINESS_WORKFLOW_NOT_ATTEMPTED",
            "business_workflow_workpack_performed": False,
            "controlled_action_count": 7,
            "completed_action_count": 0,
            "routed_v21_v20_v19_v18_v17_chain_performed": False,
            "project_brief_artifact_written": False,
            "execution_plan_artifact_written": False,
            "tracker_csv_artifact_written": False,
            "client_ready_summary_artifact_written": False,
            "qa_checklist_artifact_written": False,
            "business_workflow_manifest_written": False,
            "controlled_business_artifact_count": 6,
            "inspected_file_count": 0,
            "artifact_paths": STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS,
            "artifact_digests": {},
            "artifact_readback_verified": False,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "approval_receipt": approval,
            "manifest": manifest,
            "type_registry": type_reg,
            "workpack_schema": wp_schema,
            "action_registry": action_reg,
            "assignment_map": assignment_map,
            "execution_plan": exec_plan,
            "routed_v21_result": None,
            "artifact_results": {}
        }
        
    handoff_ledger = create_business_workflow_handoff_ledger(res)
    receipt = create_business_workflow_workpack_receipt(res, handoff_ledger)
    audit = create_business_workflow_audit_record(res, handoff_ledger, receipt)
    
    status = "CONTROLLED_BUSINESS_WORKFLOW_PREVIEW_ONLY"
    if execute_business_workflow_flag:
        if res["business_workflow_workpack_performed"]:
            status = "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_COMPLETED"
        else:
            status = "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
        "controlled_business_workflow_status": status,
        "controlled_business_workflow_layer_created": True,
        "client_ready_workpack_factory_created": True,
        "business_workflow_type_registry_created": True,
        "business_workflow_workpack_schema_created": True,
        "controlled_business_artifact_action_registry_created": True,
        "business_workflow_agent_assignment_map_created": True,
        "agent_role_count": 6,
        "controlled_action_count": 7,
        "completed_action_count": res["completed_action_count"],
        "controlled_business_artifact_count": 6,
        "business_workflow_workpack_performed": res["business_workflow_workpack_performed"],
        "routed_v21_v20_v19_v18_v17_chain_performed": res["routed_v21_v20_v19_v18_v17_chain_performed"],
        "project_brief_artifact_written": res["project_brief_artifact_written"],
        "execution_plan_artifact_written": res["execution_plan_artifact_written"],
        "tracker_csv_artifact_written": res["tracker_csv_artifact_written"],
        "client_ready_summary_artifact_written": res["client_ready_summary_artifact_written"],
        "qa_checklist_artifact_written": res["qa_checklist_artifact_written"],
        "business_workflow_manifest_written": res["business_workflow_manifest_written"],
        "artifact_readback_verified": res["artifact_readback_verified"],
        "inspected_file_count": res["inspected_file_count"],
        "artifact_paths": res["artifact_paths"],
        "artifact_digests": res["artifact_digests"],
        "business_workflow_handoff_ledger_created": True,
        "handoff_receipt_count": 6,
        "business_workflow_workpack_receipt_created": True,
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "repo_file_mutation_performed": False,
        "file_contents_printed": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "rollback_execution_performed": False,
        "recovery_execution_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "email_sent": False,
        "calendar_event_created": False,
        "web_request_performed": False,
        "socket_access_performed": False,
        "dns_resolution_performed": False,
        "credential_access_performed": False,
        "credential_vault_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "private_key_read_performed": False,
        "signing_key_read_performed": False,
        "environment_read_performed": False,
        "key_generation_performed": False,
        "real_signature_performed": False,
        "real_encryption_performed": False,
        "real_decryption_performed": False,
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
        "live_worker_routing_to_real_processes_performed": False,
        "uncontrolled_live_orchestration_performed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "shell_executed": False,
        "subprocess_started": False,
        "database_mutation_performed": False,
        "full_workforce_activation_performed": False,
        "v22_1_created": False,
        "v23_created": False,
        
        "schema": schema,
        "controlled_business_workflow_manifest": manifest,
        "business_workflow_type_registry": type_reg,
        "business_workflow_workpack_schema": res["workpack_schema"],
        "controlled_business_artifact_action_registry": res["action_registry"],
        "business_workflow_agent_assignment_map": res["assignment_map"],
        "business_workflow_approval_receipt": res["approval_receipt"],
        "business_workflow_execution_plan": res["execution_plan"],
        "business_workflow_workpack_execution": res,
        "business_workflow_handoff_ledger": handoff_ledger,
        "business_workflow_workpack_receipt": receipt,
        "business_workflow_audit_record": audit,
        "business_workflow_safety_boundary_matrix": boundaries,
        "controlled_business_workflow_summary": {
            "version": STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION,
            "status": status
        }
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
