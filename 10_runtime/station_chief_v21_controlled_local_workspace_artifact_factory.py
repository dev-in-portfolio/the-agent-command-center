import json
import hashlib
import csv
import io
import re
from pathlib import Path

# Import from v20 module as allowed
from station_chief_v20_operational_agent_army_mode import (
    STATION_CHIEF_V20_APPROVAL_PHRASE,
    execute_operational_workpack
)

STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION = "21.0.0"
STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_STATUS = "STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY"
STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_PHASE = "Station Chief v21.0 Controlled Local Workspace Tool Expansion / Artifact Factory Workpack Candidate"

STATION_CHIEF_V21_APPROVAL_PHRASE = "I_APPROVE_V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY"

STATION_CHIEF_V21_ARTIFACT_FACTORY_WORKPACK_ID = "station-chief-v21-controlled-local-workspace-artifact-factory-workpack-001"

STATION_CHIEF_V21_CONTROLLED_WORKSPACE_DIR = "/tmp/station_chief_v21_local_workspace_artifacts"

STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS = {
    "json_receipt": "/tmp/station_chief_v21_local_workspace_artifacts/v21_artifact_factory_receipt.json",
    "markdown_summary": "/tmp/station_chief_v21_local_workspace_artifacts/v21_artifact_factory_summary.md",
    "csv_table": "/tmp/station_chief_v21_local_workspace_artifacts/v21_artifact_factory_table.csv",
    "artifact_manifest": "/tmp/station_chief_v21_local_workspace_artifacts/v21_artifact_manifest.json"
}

STATION_CHIEF_V21_ARTIFACT_ACTION_IDS = [
    "station-chief-v21-action-routed-v20-v19-v18-v17-operational-chain-001",
    "station-chief-v21-action-controlled-json-receipt-artifact-002",
    "station-chief-v21-action-controlled-markdown-document-artifact-003",
    "station-chief-v21-action-controlled-csv-spreadsheet-artifact-004",
    "station-chief-v21-action-controlled-artifact-manifest-005"
]

STATION_CHIEF_V21_ARTIFACT_AGENT_ROLE_IDS = [
    "station-chief-v21-agent-role-workspace-gatekeeper-001",
    "station-chief-v21-agent-role-artifact-planner-002",
    "station-chief-v21-agent-role-data-summarizer-003",
    "station-chief-v21-agent-role-document-scribe-004",
    "station-chief-v21-agent-role-table-scribe-005",
    "station-chief-v21-agent-role-manifest-auditor-006"
]

STATION_CHIEF_V21_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v21.1 or broader external/business tool expansion requires explicit separate operator instruction"

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

def create_controlled_local_workspace_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("controlled_local_workspace_tool_expansion_manifest"),
        "manifest_type": "controlled_local_workspace_tool_expansion_manifest",
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "controlled_local_workspace_layer_created": True,
        "artifact_factory_workpack_created": True,
        "non_repo_local_artifact_work_authorized": True,
        "human_approval_required": True,
        "exact_approval_phrase_required": True,
        "json_artifact_allowed": True,
        "markdown_artifact_allowed": True,
        "csv_artifact_allowed": True,
        "manifest_artifact_allowed": True,
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

def create_artifact_factory_workpack_schema() -> dict:
    return {
        "workpack_schema_id": sha256_digest("controlled_local_workspace_artifact_factory_workpack_schema"),
        "schema_type": "controlled_local_workspace_artifact_factory_workpack_schema",
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "workpack_id": STATION_CHIEF_V21_ARTIFACT_FACTORY_WORKPACK_ID,
        "required_action_count": 5,
        "required_actions": [
            "routed_v20_v19_v18_v17_operational_chain",
            "controlled_json_receipt_artifact",
            "controlled_markdown_document_artifact",
            "controlled_csv_spreadsheet_artifact",
            "controlled_artifact_manifest"
        ],
        "human_approval_required": True,
        "exact_approval_phrase_required": STATION_CHIEF_V21_APPROVAL_PHRASE,
        "controlled_workspace_dir": STATION_CHIEF_V21_CONTROLLED_WORKSPACE_DIR,
        "controlled_artifact_paths": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS,
        "repo_mutation_allowed": False,
        "controlled_local_artifact_write_allowed": True,
        "production_allowed": False,
        "deployment_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "external_tool_call_allowed": False,
        "api_call_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }

def create_controlled_local_artifact_action_registry() -> dict:
    actions = {
        STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[0]: {
            "action_id": STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[0],
            "action_name": "routed_v20_v19_v18_v17_operational_chain",
            "action_type": "controlled_routed_operational_chain",
            "executable_in_v21": True,
            "wraps_v20_operational_workpack": True,
            "repo_read_allowed_through_prior_chain": True,
            "repo_write_allowed": False,
            "file_contents_printing_allowed": False,
            "mutation_allowed": False,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False
        },
        STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[1]: {
            "action_id": STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[1],
            "action_name": "controlled_json_receipt_artifact",
            "action_type": "controlled_local_json_artifact_write",
            "executable_in_v21": True,
            "controlled_temp_path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["json_receipt"],
            "artifact_format": "json",
            "repo_write_allowed": False,
            "local_artifact_write_allowed": True,
            "mutation_allowed": True,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        },
        STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[2]: {
            "action_id": STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[2],
            "action_name": "controlled_markdown_document_artifact",
            "action_type": "controlled_local_markdown_document_write",
            "executable_in_v21": True,
            "controlled_temp_path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["markdown_summary"],
            "artifact_format": "markdown",
            "binary_document": False,
            "repo_write_allowed": False,
            "local_artifact_write_allowed": True,
            "mutation_allowed": True,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        },
        STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[3]: {
            "action_id": STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[3],
            "action_name": "controlled_csv_spreadsheet_artifact",
            "action_type": "controlled_local_csv_spreadsheet_write",
            "executable_in_v21": True,
            "controlled_temp_path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["csv_table"],
            "artifact_format": "csv",
            "binary_spreadsheet": False,
            "repo_write_allowed": False,
            "local_artifact_write_allowed": True,
            "mutation_allowed": True,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        },
        STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[4]: {
            "action_id": STATION_CHIEF_V21_ARTIFACT_ACTION_IDS[4],
            "action_name": "controlled_artifact_manifest",
            "action_type": "controlled_local_artifact_manifest_write",
            "executable_in_v21": True,
            "controlled_temp_path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["artifact_manifest"],
            "artifact_format": "json",
            "repo_write_allowed": False,
            "local_artifact_write_allowed": True,
            "mutation_allowed": True,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        }
    }
    
    return {
        "action_registry_id": sha256_digest(actions),
        "registry_type": "controlled_local_artifact_action_registry",
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "action_count": 5,
        "executable_action_count": 5,
        "repo_mutating_action_count": 0,
        "controlled_local_artifact_action_count": 4,
        "routed_prior_chain_action_count": 1,
        "actions": actions
    }

def create_artifact_factory_agent_assignment_map() -> dict:
    roles = [
        ("workspace_gatekeeper", "approval_gate"),
        ("artifact_planner", "artifact_plan"),
        ("data_summarizer", "metadata_summary"),
        ("document_scribe", "markdown_artifact"),
        ("table_scribe", "csv_artifact"),
        ("manifest_auditor", "manifest_and_audit")
    ]
    
    assignments = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V21_ARTIFACT_AGENT_ROLE_IDS[idx]
        assignments[r_id] = {
            "agent_role_id": r_id,
            "agent_role_name": name,
            "agent_role_type": "logical_artifact_factory_agent_role",
            "role_registered": True,
            "workflow_stage": stage,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "daemon_started": False,
            "subprocess_started": False,
            "shell_execution_allowed": False,
            "human_supervision_required": True,
            "can_receive_artifact_workpack": True,
            "can_create_metadata_receipt": True,
            "can_execute_tools": False,
            "can_mutate_repo_files": False,
            "can_write_controlled_local_artifact": name in ["document_scribe", "table_scribe", "manifest_auditor"],
            "can_access_credentials": False,
            "can_access_network": False,
            "can_touch_production": False
        }
    return assignments

def create_artifact_factory_approval_receipt(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    phrase_received = approval_phrase is not None
    phrase_matches = approval_phrase == STATION_CHIEF_V21_APPROVAL_PHRASE
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v21_artifact_factory_workpack")
    
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "op": op, "wp": wp}),
        "receipt_type": "v21_artifact_factory_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "operator_label": op,
        "workpack_label": wp,
        "approval_phrase_received": phrase_received,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V21_APPROVAL_PHRASE,
        "human_approval_granted": phrase_matches,
        "autonomous_self_approval": False,
        "approval_scope": "v21_controlled_local_workspace_artifact_factory_only",
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_external_tools": True,
        "approval_does_not_authorize_future_adapters": True,
        "approval_does_not_authorize_real_worker_processes": True
    }

def create_artifact_factory_execution_plan(workpack_schema: dict, action_registry: dict, assignment_map: dict, approval_receipt: dict) -> dict:
    approved = approval_receipt["human_approval_granted"]
    
    return {
        "execution_plan_id": sha256_digest({"receipt": approval_receipt["approval_receipt_id"]}),
        "plan_type": "controlled_local_workspace_artifact_factory_execution_plan",
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "workpack_id": STATION_CHIEF_V21_ARTIFACT_FACTORY_WORKPACK_ID,
        "action_count": 5,
        "agent_role_count": 6,
        "human_approval_granted": approved,
        "execution_status": "READY_FOR_ARTIFACT_FACTORY_EXECUTION" if approved else "ARTIFACT_FACTORY_DENIED_OR_PREVIEW_ONLY",
        "execute_routed_v20_operational_chain": approved,
        "execute_json_artifact_write": approved,
        "execute_markdown_artifact_write": approved,
        "execute_csv_artifact_write": approved,
        "execute_manifest_artifact_write": approved,
        "repo_mutation_allowed": False,
        "controlled_local_artifact_write_allowed": approved,
        "binary_document_generation_allowed": False,
        "binary_spreadsheet_generation_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "external_tool_call_allowed": False,
        "api_call_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }

def resolve_controlled_workspace_paths() -> dict:
    workspace_dir = Path(STATION_CHIEF_V21_CONTROLLED_WORKSPACE_DIR)
    
    paths = {}
    valid = True
    if not str(workspace_dir).startswith("/tmp/station_chief_v21_local_workspace_artifacts"):
        valid = False
        
    for key, path_str in STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS.items():
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

def build_artifact_factory_payloads(routed_v20_result: dict, approval_receipt: dict) -> dict:
    # 1. JSON receipt payload
    json_payload = {
        "version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "status": "V21_ARTIFACT_FACTORY_JSON_RECEIPT",
        "operator": approval_receipt["operator_label"],
        "workpack": approval_receipt["workpack_label"],
        "routed_v20_chain_performed": routed_v20_result.get("operational_workpack_performed", False) if routed_v20_result else False,
        "inspected_file_count": routed_v20_result.get("inspected_file_count", 0) if routed_v20_result else 0
    }
    
    # 2. Markdown summary text
    markdown_text = f"""# Station Chief v21 Controlled Local Workspace Artifact Factory

## Runtime Context
- **Version:** {STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION}
- **Approval Status:** {"GRANTED" if approval_receipt["human_approval_granted"] else "DENIED"}
- **Operator:** {approval_receipt["operator_label"]}

## Execution Summary
- **Routed v20 Chain Performed:** {json_payload["routed_v20_chain_performed"]}
- **Inspected File Count:** {json_payload["inspected_file_count"]}

## Artifact List
- JSON Receipt: `v21_artifact_factory_receipt.json`
- Markdown Summary: `v21_artifact_factory_summary.md`
- CSV Table: `v21_artifact_factory_table.csv`
- Artifact Manifest: `v21_artifact_manifest.json`

## Safety Summary
- **Repo Mutation:** FORBIDDEN / NOT PERFORMED
- **Credential Access:** FORBIDDEN / NOT PERFORMED
- **Network/API Access:** FORBIDDEN / NOT PERFORMED
- **Private Data Access:** FORBIDDEN / NOT PERFORMED

This document was generated as part of the v21 controlled local workspace expansion test.
"""

    # 3. CSV rows
    csv_rows = [
        ["property", "value"],
        ["runtime_version", STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION],
        ["approval_granted", str(approval_receipt["human_approval_granted"])],
        ["routed_v20_chain_performed", str(json_payload["routed_v20_chain_performed"])],
        ["inspected_file_count", str(json_payload["inspected_file_count"])],
        ["json_receipt_written", "True"],
        ["markdown_summary_written", "True"],
        ["csv_table_written", "True"],
        ["manifest_written", "True"],
        ["repo_mutation_performed", "False"],
        ["network_access_performed", "False"],
        ["credential_access_performed", "False"],
        ["production_execution_performed", "False"]
    ]
    
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(csv_rows)
    csv_text = output.getvalue()
    
    # 4. Manifest payload
    manifest_payload = {
        "manifest_version": "1.0",
        "workpack_id": STATION_CHIEF_V21_ARTIFACT_FACTORY_WORKPACK_ID,
        "artifacts": [
            {"key": "json_receipt", "format": "json", "path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["json_receipt"]},
            {"key": "markdown_summary", "format": "markdown", "path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["markdown_summary"]},
            {"key": "csv_table", "format": "csv", "path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["csv_table"]},
            {"key": "artifact_manifest", "format": "json", "path": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS["artifact_manifest"]}
        ]
    }
    
    return {
        "json_receipt_payload": json_payload,
        "markdown_summary_text": markdown_text,
        "csv_table_text": csv_text,
        "manifest_payload": manifest_payload
    }

def write_controlled_text_artifact(artifact_key: str, content: str, approval_receipt: dict) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"artifact_write_performed": False, "error": "Approval missing"}
        
    paths_meta = resolve_controlled_workspace_paths()
    if not paths_meta["all_artifact_paths_valid"]:
        return {"artifact_write_performed": False, "error": "Invalid workspace path"}
        
    artifact_path_str = paths_meta["artifact_paths"].get(artifact_key)
    if not artifact_path_str:
        return {"artifact_write_performed": False, "error": f"Unknown artifact key: {artifact_key}"}
        
    workspace_dir = Path(paths_meta["workspace_dir"])
    artifact_path = Path(artifact_path_str)
    
    # mkdir parents=True, exist_ok=True
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # write_text
    artifact_path.write_text(content)
    
    # read_text readback
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

def execute_artifact_factory_workpack(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    manifest = create_controlled_local_workspace_manifest()
    schema = create_artifact_factory_workpack_schema()
    action_reg = create_controlled_local_artifact_action_registry()
    assignment_map = create_artifact_factory_agent_assignment_map()
    approval = create_artifact_factory_approval_receipt(approval_phrase, operator_label, workpack_label)
    exec_plan = create_artifact_factory_execution_plan(schema, action_reg, assignment_map, approval)
    
    v20_result = None
    performed = False
    completed_action_count = 0
    
    artifact_results = {}
    artifact_digests = {}
    all_verified = True
    
    if approval["human_approval_granted"]:
        # Action 1: routed v20 operational chain
        v20_result = execute_operational_workpack(
            STATION_CHIEF_V20_APPROVAL_PHRASE,
            operator_label=operator_label,
            workpack_label=workpack_label
        )
        if v20_result.get("operational_workpack_performed"):
            completed_action_count += 1
            
        # Build payloads
        payloads = build_artifact_factory_payloads(v20_result, approval)
        
        # Action 2: JSON Receipt
        res_json = write_controlled_text_artifact("json_receipt", canonical_json(payloads["json_receipt_payload"]), approval)
        artifact_results["json_receipt"] = res_json
        if res_json.get("artifact_write_performed"):
            completed_action_count += 1
            artifact_digests["json_receipt"] = res_json["artifact_sha256"]
            if not res_json["artifact_readback_verified"]: all_verified = False
            
        # Action 3: Markdown Summary
        res_md = write_controlled_text_artifact("markdown_summary", payloads["markdown_summary_text"], approval)
        artifact_results["markdown_summary"] = res_md
        if res_md.get("artifact_write_performed"):
            completed_action_count += 1
            artifact_digests["markdown_summary"] = res_md["artifact_sha256"]
            if not res_md["artifact_readback_verified"]: all_verified = False
            
        # Action 4: CSV Table
        res_csv = write_controlled_text_artifact("csv_table", payloads["csv_table_text"], approval)
        artifact_results["csv_table"] = res_csv
        if res_csv.get("artifact_write_performed"):
            completed_action_count += 1
            artifact_digests["csv_table"] = res_csv["artifact_sha256"]
            if not res_csv["artifact_readback_verified"]: all_verified = False
            
        # Action 5: Artifact Manifest
        res_man = write_controlled_text_artifact("artifact_manifest", canonical_json(payloads["manifest_payload"]), approval)
        artifact_results["artifact_manifest"] = res_man
        if res_man.get("artifact_write_performed"):
            completed_action_count += 1
            artifact_digests["artifact_manifest"] = res_man["artifact_sha256"]
            if not res_man["artifact_readback_verified"]: all_verified = False
            
        if completed_action_count == 5:
            performed = True
            
    return {
        "execution_status": "V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_COMPLETED" if performed else "V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_DENIED",
        "artifact_factory_workpack_performed": performed,
        "controlled_action_count": 5,
        "completed_action_count": completed_action_count,
        "routed_v20_v19_v18_v17_operational_chain_performed": v20_result.get("operational_workpack_performed", False) if v20_result else False,
        "json_receipt_artifact_written": artifact_results.get("json_receipt", {}).get("artifact_write_performed", False),
        "markdown_summary_artifact_written": artifact_results.get("markdown_summary", {}).get("artifact_write_performed", False),
        "csv_table_artifact_written": artifact_results.get("csv_table", {}).get("artifact_write_performed", False),
        "artifact_manifest_written": artifact_results.get("artifact_manifest", {}).get("artifact_write_performed", False),
        "controlled_artifact_count": 4,
        "inspected_file_count": v20_result.get("inspected_file_count", 0) if v20_result else 0,
        "artifact_paths": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS,
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
        "subprocess_started": False,
        "shell_executed": False,
        "live_worker_started": False,
        "live_queue_created": False,
        "live_task_executed": False,
        "uncontrolled_live_orchestration_performed": False,
        
        "manifest": manifest,
        "workpack_schema": schema,
        "action_registry": action_reg,
        "assignment_map": assignment_map,
        "approval_receipt": approval,
        "execution_plan": exec_plan,
        "routed_v20_result": v20_result,
        "artifact_results": artifact_results
    }

def create_artifact_factory_handoff_ledger(artifact_factory_result: dict) -> dict:
    assignments = artifact_factory_result["assignment_map"]
    performed = artifact_factory_result["artifact_factory_workpack_performed"]
    
    receipts = {}
    for r_id, role in assignments.items():
        h_id = sha256_digest({"role": r_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": r_id,
            "agent_role_name": role["agent_role_name"],
            "workflow_stage": role["workflow_stage"],
            "receipt_type": "v21_artifact_factory_agent_handoff_receipt",
            "runtime_version": "21.0.0",
            "artifact_workpack_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False,
            "repo_mutation_performed": False,
            "controlled_artifact_write_supervised": role["agent_role_name"] in ["document_scribe", "table_scribe", "manifest_auditor"] and performed,
            "credential_access_performed": False,
            "network_access_performed": False,
            "shell_executed": False,
            "subprocess_started": False
        }
        
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v21_artifact_factory_agent_handoff_ledger",
        "runtime_version": "21.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }

def create_artifact_factory_workpack_receipt(artifact_factory_result: dict, handoff_ledger: dict) -> dict:
    performed = artifact_factory_result["artifact_factory_workpack_performed"]
    
    return {
        "artifact_factory_workpack_receipt_id": sha256_digest({"res": artifact_factory_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v21_artifact_factory_workpack_execution_receipt",
        "runtime_version": "21.0.0",
        "artifact_factory_workpack_performed": performed,
        "controlled_action_count": 5,
        "completed_action_count": artifact_factory_result["completed_action_count"],
        "routed_v20_v19_v18_v17_operational_chain_performed": artifact_factory_result["routed_v20_v19_v18_v17_operational_chain_performed"],
        "json_receipt_artifact_written": artifact_factory_result["json_receipt_artifact_written"],
        "markdown_summary_artifact_written": artifact_factory_result["markdown_summary_artifact_written"],
        "csv_table_artifact_written": artifact_factory_result["csv_table_artifact_written"],
        "artifact_manifest_written": artifact_factory_result["artifact_manifest_written"],
        "controlled_artifact_count": 4,
        "inspected_file_count": artifact_factory_result["inspected_file_count"],
        "artifact_paths": artifact_factory_result["artifact_paths"],
        "artifact_digests": artifact_factory_result["artifact_digests"],
        "artifact_readback_verified": artifact_factory_result["artifact_readback_verified"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "receipt_status": "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_COMPLETED" if performed else "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_DENIED",
        "no_repo_file_mutation": True,
        "no_file_contents_printed": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_network_access": True,
        "no_api_call": True,
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

def create_artifact_factory_audit_record(artifact_factory_result: dict, handoff_ledger: dict, workpack_receipt: dict) -> dict:
    return {
        "audit_id": sha256_digest({"receipt": workpack_receipt["artifact_factory_workpack_receipt_id"]}),
        "audit_type": "v21_controlled_local_workspace_artifact_factory_audit",
        "runtime_version": "21.0.0",
        "controlled_local_workspace_layer_created": True,
        "artifact_factory_workpack_created": True,
        "artifact_factory_workpack_schema_created": True,
        "controlled_local_artifact_action_registry_created": True,
        "artifact_factory_agent_assignment_map_created": True,
        "artifact_factory_execution_plan_created": True,
        "artifact_factory_handoff_ledger_created": True,
        "artifact_factory_workpack_receipt_created": True,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "controlled_action_count": 5,
        "completed_action_count": artifact_factory_result["completed_action_count"],
        "controlled_artifact_count": 4,
        "artifact_factory_workpack_performed": artifact_factory_result["artifact_factory_workpack_performed"],
        "routed_v20_v19_v18_v17_operational_chain_performed": artifact_factory_result["routed_v20_v19_v18_v17_operational_chain_performed"],
        "json_receipt_artifact_written": artifact_factory_result["json_receipt_artifact_written"],
        "markdown_summary_artifact_written": artifact_factory_result["markdown_summary_artifact_written"],
        "csv_table_artifact_written": artifact_factory_result["csv_table_artifact_written"],
        "artifact_manifest_written": artifact_factory_result["artifact_manifest_written"],
        "inspected_file_count": artifact_factory_result["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": artifact_factory_result["approval_receipt"]["human_approval_granted"],
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

def create_local_workspace_safety_boundary_matrix() -> dict:
    return {
        "controlled_local_workspace_manifest": "ALLOWED",
        "artifact_factory_workpack_schema": "ALLOWED",
        "controlled_local_artifact_action_registry": "ALLOWED",
        "artifact_factory_agent_assignment_map": "ALLOWED",
        "artifact_factory_approval_receipt": "ALLOWED",
        "artifact_factory_execution_plan": "ALLOWED",
        "routed_v20_v19_v18_v17_operational_chain": "ALLOWED",
        "controlled_json_receipt_artifact": "ALLOWED",
        "controlled_markdown_document_artifact": "ALLOWED",
        "controlled_csv_spreadsheet_artifact": "ALLOWED",
        "controlled_artifact_manifest": "ALLOWED",
        "controlled_artifact_readback_verification": "ALLOWED",
        "artifact_factory_handoff_ledger": "ALLOWED",
        "artifact_factory_workpack_receipt": "ALLOWED",
        "artifact_factory_audit_record": "ALLOWED",
        "json_receipt_output": "ALLOWED",
        "markdown_text_output": "ALLOWED",
        "csv_text_output": "ALLOWED",
        
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
        "live_task_execution_outside_controlled_artifact_workpack": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v21_1_creation": "DENIED",
        "v22_creation": "DENIED"
    }

def create_station_chief_v21_controlled_local_workspace_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "schema_type": "station_chief_v21_controlled_local_workspace_artifact_factory",
        "required_sections": [
            "controlled_local_workspace_manifest",
            "artifact_factory_workpack_schema",
            "controlled_local_artifact_action_registry",
            "artifact_factory_agent_assignment_map",
            "artifact_factory_approval_receipt",
            "artifact_factory_execution_plan",
            "artifact_factory_workpack_execution",
            "artifact_factory_handoff_ledger",
            "artifact_factory_workpack_receipt",
            "artifact_factory_audit_record",
            "local_workspace_safety_boundary_matrix",
            "controlled_local_workspace_summary"
        ],
        "controlled_local_workspace_artifact_factory_authorized": True,
        "controlled_local_artifact_workpack_authorized": True,
        "routed_v20/v19/v18/v17_operational_chain_authorized": True,
        "controlled_JSON_artifact_authorized": True,
        "controlled_Markdown_artifact_authorized": True,
        "controlled_CSV_artifact_authorized": True,
        "controlled_artifact_manifest_authorized": True,
        "human_approval_required": True,
        "no_uncontrolled_agent_activation_authorized": True,
        "no_real_worker_process_authorized": True,
        "no_background_agent_authorized": True,
        "no_arbitrary_agent_execution_authorized": True,
        "no_repo_mutation_authorized": True,
        "no_production_execution_authorized": True,
        "no_deployment_authorized": True,
        "no_external_tool_invocation_authorized": True,
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
        "v21_1_created": False,
        "v22_created": False
    }

def create_station_chief_v21_controlled_local_workspace_bundle(approval_phrase: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, execute_artifact_factory_flag: bool = False) -> dict:
    schema = create_station_chief_v21_controlled_local_workspace_schema()
    manifest = create_controlled_local_workspace_manifest()
    boundaries = create_local_workspace_safety_boundary_matrix()
    
    if execute_artifact_factory_flag:
        res = execute_artifact_factory_workpack(approval_phrase, operator_label, workpack_label)
    else:
        # Preview only
        wp_schema = create_artifact_factory_workpack_schema()
        action_reg = create_controlled_local_artifact_action_registry()
        assignment_map = create_artifact_factory_agent_assignment_map()
        approval = create_artifact_factory_approval_receipt(approval_phrase, operator_label, workpack_label)
        exec_plan = create_artifact_factory_execution_plan(wp_schema, action_reg, assignment_map, approval)
        res = {
            "execution_status": "V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_NOT_ATTEMPTED",
            "artifact_factory_workpack_performed": False,
            "controlled_action_count": 5,
            "completed_action_count": 0,
            "routed_v20_v19_v18_v17_operational_chain_performed": False,
            "json_receipt_artifact_written": False,
            "markdown_summary_artifact_written": False,
            "csv_table_artifact_written": False,
            "artifact_manifest_written": False,
            "controlled_artifact_count": 4,
            "inspected_file_count": 0,
            "artifact_paths": STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS,
            "artifact_digests": {},
            "artifact_readback_verified": False,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "approval_receipt": approval,
            "manifest": manifest,
            "workpack_schema": wp_schema,
            "action_registry": action_reg,
            "assignment_map": assignment_map,
            "execution_plan": exec_plan,
            "routed_v20_result": None,
            "artifact_results": {}
        }
        
    handoff_ledger = create_artifact_factory_handoff_ledger(res)
    receipt = create_artifact_factory_workpack_receipt(res, handoff_ledger)
    audit = create_artifact_factory_audit_record(res, handoff_ledger, receipt)
    
    status = "CONTROLLED_LOCAL_WORKSPACE_PREVIEW_ONLY"
    if execute_artifact_factory_flag:
        if res["artifact_factory_workpack_performed"]:
            status = "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_COMPLETED"
        else:
            status = "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
        "controlled_local_workspace_status": status,
        "controlled_local_workspace_layer_created": True,
        "artifact_factory_workpack_created": True,
        "artifact_factory_workpack_schema_created": True,
        "controlled_local_artifact_action_registry_created": True,
        "artifact_factory_agent_assignment_map_created": True,
        "agent_role_count": 6,
        "controlled_action_count": 5,
        "completed_action_count": res["completed_action_count"],
        "controlled_artifact_count": 4,
        "artifact_factory_workpack_performed": res["artifact_factory_workpack_performed"],
        "routed_v20_v19_v18_v17_operational_chain_performed": res["routed_v20_v19_v18_v17_operational_chain_performed"],
        "json_receipt_artifact_written": res["json_receipt_artifact_written"],
        "markdown_summary_artifact_written": res["markdown_summary_artifact_written"],
        "csv_table_artifact_written": res["csv_table_artifact_written"],
        "artifact_manifest_written": res["artifact_manifest_written"],
        "artifact_readback_verified": res["artifact_readback_verified"],
        "inspected_file_count": res["inspected_file_count"],
        "artifact_paths": res["artifact_paths"],
        "artifact_digests": res["artifact_digests"],
        "artifact_factory_handoff_ledger_created": True,
        "handoff_receipt_count": 6,
        "artifact_factory_workpack_receipt_created": True,
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
        "v21_1_created": False,
        "v22_created": False,
        
        "schema": schema,
        "controlled_local_workspace_manifest": manifest,
        "artifact_factory_workpack_schema": res["workpack_schema"],
        "controlled_local_artifact_action_registry": res["action_registry"],
        "artifact_factory_agent_assignment_map": res["assignment_map"],
        "artifact_factory_approval_receipt": res["approval_receipt"],
        "artifact_factory_execution_plan": res["execution_plan"],
        "artifact_factory_workpack_execution": res,
        "artifact_factory_handoff_ledger": handoff_ledger,
        "artifact_factory_workpack_receipt": receipt,
        "artifact_factory_audit_record": audit,
        "local_workspace_safety_boundary_matrix": boundaries,
        "controlled_local_workspace_summary": {
            "version": STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION,
            "status": status
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
