import json
import hashlib
import re
from pathlib import Path

# Import from v19 module as allowed
from station_chief_v19_multi_agent_live_work_router import (
    STATION_CHIEF_V19_APPROVAL_PHRASE,
    execute_routed_controlled_adapter_work
)

STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION = "20.0.0"
STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_STATUS = "STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_CONTROLLED_WORKPACK_EXECUTION"
STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_PHASE = "Station Chief v20.0 Operational Agent Army Mode / Controlled Workpack Execution Layer Candidate"

STATION_CHIEF_V20_APPROVAL_PHRASE = "I_APPROVE_V20_OPERATIONAL_AGENT_ARMY_WORKPACK"

STATION_CHIEF_V20_OPERATIONAL_WORKPACK_ID = "station-chief-v20-operational-agent-army-workpack-001"

STATION_CHIEF_V20_CONTROLLED_SANDBOX_DIR = "/tmp/station_chief_v20_operational_sandbox"
STATION_CHIEF_V20_CONTROLLED_SANDBOX_ARTIFACT = "/tmp/station_chief_v20_operational_sandbox/v20_operational_workpack_receipt.json"

STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS = [
    "station-chief-v20-action-routed-v19-v18-v17-readonly-inspection-001",
    "station-chief-v20-action-controlled-local-sandbox-artifact-write-002"
]

STATION_CHIEF_V20_OPERATIONAL_AGENT_ROLE_IDS = [
    "station-chief-v20-agent-role-operator-gatekeeper-001",
    "station-chief-v20-agent-role-workpack-planner-002",
    "station-chief-v20-agent-role-tool-router-003",
    "station-chief-v20-agent-role-execution-supervisor-004",
    "station-chief-v20-agent-role-artifact-scribe-005",
    "station-chief-v20-agent-role-audit-safety-officer-006"
]

STATION_CHIEF_V20_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v20.1 or broader operational tool expansion requires explicit separate operator instruction"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()

def create_operational_agent_army_mode_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("operational_agent_army_mode_manifest"),
        "manifest_type": "operational_agent_army_mode_manifest",
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "operational_agent_army_mode_created": True,
        "controlled_workpack_execution_layer_created": True,
        "human_approval_required": True,
        "exact_approval_phrase_required": True,
        "logical_agent_roles_required": True,
        "supervised_routing_required": True,
        "workpack_receipt_required": True,
        "operational_audit_required": True,
        "uncontrolled_autonomy_allowed": False,
        "autonomous_self_activation_allowed": False,
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

def create_operational_workpack_schema() -> dict:
    return {
        "workpack_schema_id": sha256_digest("controlled_operational_workpack_schema"),
        "schema_type": "controlled_operational_workpack_schema",
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "workpack_id": STATION_CHIEF_V20_OPERATIONAL_WORKPACK_ID,
        "required_action_count": 2,
        "required_actions": [
            "routed_v19_v18_v17_readonly_inspection",
            "controlled_local_sandbox_artifact_write"
        ],
        "human_approval_required": True,
        "exact_approval_phrase_required": STATION_CHIEF_V20_APPROVAL_PHRASE,
        "logical_agent_supervision_required": True,
        "repo_mutation_allowed": False,
        "controlled_temp_artifact_write_allowed": True,
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

def create_controlled_workpack_action_registry() -> dict:
    actions = {
        STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS[0]: {
            "action_id": STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS[0],
            "action_name": "routed_v19_v18_v17_readonly_inspection",
            "action_type": "controlled_routed_readonly_inspection",
            "executable_in_v20": True,
            "wraps_v19_router": True,
            "repo_read_allowed": True,
            "repo_write_allowed": False,
            "file_contents_printing_allowed": False,
            "mutation_allowed": False,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False
        },
        STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS[1]: {
            "action_id": STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS[1],
            "action_name": "controlled_local_sandbox_artifact_write",
            "action_type": "controlled_temp_artifact_write",
            "executable_in_v20": True,
            "controlled_temp_path": STATION_CHIEF_V20_CONTROLLED_SANDBOX_ARTIFACT,
            "repo_write_allowed": False,
            "temp_artifact_write_allowed": True,
            "overwrite_same_temp_artifact_allowed": True,
            "mutation_allowed": True, # only for controlled temp artifact
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "environment_read_allowed": False
        }
    }
    
    return {
        "action_registry_id": sha256_digest(actions),
        "registry_type": "controlled_workpack_action_registry",
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "action_count": 2,
        "executable_action_count": 2,
        "repo_mutating_action_count": 0,
        "controlled_temp_artifact_action_count": 1,
        "actions": actions
    }

def create_operational_agent_squad_assignment_map() -> dict:
    roles = [
        ("operator_gatekeeper", "approval_gate"),
        ("workpack_planner", "workpack_plan"),
        ("tool_router", "controlled_tool_route"),
        ("execution_supervisor", "supervised_execution"),
        ("artifact_scribe", "controlled_artifact_receipt"),
        ("audit_safety_officer", "final_audit_review")
    ]
    
    assignments = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V20_OPERATIONAL_AGENT_ROLE_IDS[idx]
        assignments[r_id] = {
            "agent_role_id": r_id,
            "agent_role_name": name,
            "agent_role_type": "logical_operational_agent_army_role",
            "role_registered": True,
            "workflow_stage": stage,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "daemon_started": False,
            "subprocess_started": False,
            "shell_execution_allowed": False,
            "human_supervision_required": True,
            "can_receive_workpack": True,
            "can_create_metadata_receipt": True,
            "can_execute_tools": False,
            "can_mutate_repo_files": False,
            "can_write_controlled_temp_artifact": name == "artifact_scribe",
            "can_access_credentials": False,
            "can_access_network": False,
            "can_touch_production": False
        }
    return assignments

def create_operational_approval_receipt(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    phrase_received = approval_phrase is not None
    phrase_matches = approval_phrase == STATION_CHIEF_V20_APPROVAL_PHRASE
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v20_operational_workpack")
    
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "op": op, "wp": wp}),
        "receipt_type": "v20_operational_workpack_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "operator_label": op,
        "workpack_label": wp,
        "approval_phrase_received": phrase_received,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V20_APPROVAL_PHRASE,
        "human_approval_granted": phrase_matches,
        "autonomous_self_approval": False,
        "approval_scope": "v20_operational_agent_army_controlled_workpack_only",
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_broader_tool_use": True,
        "approval_does_not_authorize_future_adapters": True,
        "approval_does_not_authorize_real_worker_processes": True
    }

def create_controlled_workpack_execution_plan(workpack_schema: dict, action_registry: dict, assignment_map: dict, approval_receipt: dict) -> dict:
    approved = approval_receipt["human_approval_granted"]
    
    return {
        "execution_plan_id": sha256_digest({"receipt": approval_receipt["approval_receipt_id"]}),
        "plan_type": "controlled_operational_workpack_execution_plan",
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "workpack_id": STATION_CHIEF_V20_OPERATIONAL_WORKPACK_ID,
        "action_count": 2,
        "agent_role_count": 6,
        "human_approval_granted": approved,
        "execution_status": "READY_FOR_OPERATIONAL_WORKPACK_EXECUTION" if approved else "OPERATIONAL_WORKPACK_DENIED_OR_PREVIEW_ONLY",
        "execute_routed_readonly_inspection": approved,
        "execute_controlled_temp_artifact_write": approved,
        "repo_mutation_allowed": False,
        "controlled_temp_artifact_write_allowed": approved,
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

def resolve_controlled_sandbox_paths() -> dict:
    sandbox_dir = Path(STATION_CHIEF_V20_CONTROLLED_SANDBOX_DIR)
    sandbox_artifact = Path(STATION_CHIEF_V20_CONTROLLED_SANDBOX_ARTIFACT)
    
    valid = (
        sandbox_artifact.parent == sandbox_dir and 
        str(sandbox_dir).startswith("/tmp/station_chief_v20_operational_sandbox")
    )
    
    return {
        "sandbox_dir": str(sandbox_dir),
        "sandbox_artifact": str(sandbox_artifact),
        "sandbox_path_valid": valid,
        "repo_path": False,
        "production_path": False,
        "credential_path": False,
        "secret_path": False
    }

def write_controlled_sandbox_artifact(receipt_payload: dict, approval_receipt: dict) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"artifact_write_performed": False, "error": "Approval missing"}
        
    paths = resolve_controlled_sandbox_paths()
    if not paths["sandbox_path_valid"]:
        return {"artifact_write_performed": False, "error": "Invalid sandbox path"}
        
    sandbox_dir = Path(paths["sandbox_dir"])
    sandbox_artifact = Path(paths["sandbox_artifact"])
    
    # mkdir -parents=True, exist_ok=True
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    # write_text
    artifact_content = canonical_json(receipt_payload)
    sandbox_artifact.write_text(artifact_content)
    
    # read_text readback
    readback = sandbox_artifact.read_text()
    
    return {
        "artifact_action_id": STATION_CHIEF_V20_OPERATIONAL_ACTION_IDS[1],
        "artifact_write_performed": True,
        "controlled_temp_artifact_path": str(sandbox_artifact),
        "artifact_exists_after_write": sandbox_artifact.exists(),
        "artifact_sha256": hashlib.sha256(readback.encode("utf-8")).hexdigest(),
        "artifact_byte_count": len(readback),
        "artifact_readback_verified": readback == artifact_content,
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

def execute_operational_workpack(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None) -> dict:
    manifest = create_operational_agent_army_mode_manifest()
    schema = create_operational_workpack_schema()
    action_reg = create_controlled_workpack_action_registry()
    assignment_map = create_operational_agent_squad_assignment_map()
    approval = create_operational_approval_receipt(approval_phrase, operator_label, workpack_label)
    exec_plan = create_controlled_workpack_execution_plan(schema, action_reg, assignment_map, approval)
    
    routed_result = None
    artifact_result = None
    performed = False
    completed_action_count = 0
    
    if approval["human_approval_granted"]:
        # Action 1: routed v19 inspection
        routed_result = execute_routed_controlled_adapter_work(
            STATION_CHIEF_V19_APPROVAL_PHRASE,
            operator_label=operator_label,
            task_label=workpack_label
        )
        if routed_result.get("routed_live_work_performed"):
            completed_action_count += 1
            
        # Action 2: controlled artifact write
        receipt_payload = {
            "version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
            "status": "V20_OPERATIONAL_WORKPACK_EXECUTION_RECEIPT",
            "routed_inspection_performed": routed_result.get("routed_live_work_performed", False) if routed_result else False,
            "inspected_file_count": routed_result.get("inspected_file_count", 0) if routed_result else 0,
            "audit_id": sha256_digest(routed_result) if routed_result else None
        }
        artifact_result = write_controlled_sandbox_artifact(receipt_payload, approval)
        if artifact_result.get("artifact_write_performed"):
            completed_action_count += 1
            
        if completed_action_count == 2:
            performed = True
            
    return {
        "execution_status": "V20_OPERATIONAL_AGENT_ARMY_WORKPACK_COMPLETED" if performed else "V20_OPERATIONAL_AGENT_ARMY_WORKPACK_DENIED",
        "operational_workpack_performed": performed,
        "controlled_action_count": 2,
        "completed_action_count": completed_action_count,
        "routed_v19_v18_v17_readonly_inspection_performed": routed_result.get("routed_live_work_performed", False) if routed_result else False,
        "controlled_sandbox_artifact_write_performed": artifact_result.get("artifact_write_performed", False) if artifact_result else False,
        "inspected_file_count": routed_result.get("inspected_file_count", 0) if routed_result else 0,
        "inspected_file_records_present": routed_result.get("inspected_file_records_present", False) if routed_result else False,
        "inspected_files": routed_result.get("inspected_files", []) if routed_result else [],
        "controlled_temp_artifact_path": artifact_result.get("controlled_temp_artifact_path") if artifact_result else None,
        "controlled_temp_artifact_sha256": artifact_result.get("artifact_sha256") if artifact_result else None,
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
        "routed_inspection_result": routed_result,
        "artifact_write_result": artifact_result
    }

def create_operational_agent_handoff_ledger(operational_result: dict) -> dict:
    assignments = operational_result["assignment_map"]
    performed = operational_result["operational_workpack_performed"]
    
    receipts = {}
    for r_id, role in assignments.items():
        h_id = sha256_digest({"role": r_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": r_id,
            "agent_role_name": role["agent_role_name"],
            "workflow_stage": role["workflow_stage"],
            "receipt_type": "v20_operational_agent_handoff_receipt",
            "runtime_version": "20.0.0",
            "workpack_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False,
            "repo_mutation_performed": False,
            "controlled_temp_artifact_write_supervised": role["agent_role_name"] == "artifact_scribe" and performed,
            "credential_access_performed": False,
            "network_access_performed": False,
            "shell_executed": False,
            "subprocess_started": False
        }
        
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v20_operational_agent_handoff_ledger",
        "runtime_version": "20.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }

def create_operational_workpack_receipt(operational_result: dict, handoff_ledger: dict) -> dict:
    performed = operational_result["operational_workpack_performed"]
    
    return {
        "operational_workpack_receipt_id": sha256_digest({"res": operational_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v20_operational_workpack_execution_receipt",
        "runtime_version": "20.0.0",
        "operational_workpack_performed": performed,
        "controlled_action_count": 2,
        "completed_action_count": operational_result["completed_action_count"],
        "routed_v19_v18_v17_readonly_inspection_performed": operational_result["routed_v19_v18_v17_readonly_inspection_performed"],
        "controlled_sandbox_artifact_write_performed": operational_result["controlled_sandbox_artifact_write_performed"],
        "inspected_file_count": operational_result["inspected_file_count"],
        "controlled_temp_artifact_path": operational_result["controlled_temp_artifact_path"],
        "controlled_temp_artifact_sha256": operational_result["controlled_temp_artifact_sha256"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "receipt_status": "OPERATIONAL_AGENT_ARMY_WORKPACK_COMPLETED" if performed else "OPERATIONAL_AGENT_ARMY_WORKPACK_DENIED",
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

def create_operational_agent_army_audit_record(operational_result: dict, handoff_ledger: dict, workpack_receipt: dict) -> dict:
    return {
        "audit_id": sha256_digest({"receipt": workpack_receipt["operational_workpack_receipt_id"]}),
        "audit_type": "v20_operational_agent_army_mode_audit",
        "runtime_version": "20.0.0",
        "operational_agent_army_mode_created": True,
        "controlled_workpack_execution_layer_created": True,
        "operational_workpack_schema_created": True,
        "controlled_workpack_action_registry_created": True,
        "operational_agent_squad_assignment_map_created": True,
        "controlled_workpack_execution_plan_created": True,
        "operational_agent_handoff_ledger_created": True,
        "operational_workpack_receipt_created": True,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "controlled_action_count": 2,
        "completed_action_count": operational_result["completed_action_count"],
        "operational_workpack_performed": operational_result["operational_workpack_performed"],
        "routed_v19_v18_v17_readonly_inspection_performed": operational_result["routed_v19_v18_v17_readonly_inspection_performed"],
        "controlled_sandbox_artifact_write_performed": operational_result["controlled_sandbox_artifact_write_performed"],
        "inspected_file_count": operational_result["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": operational_result["approval_receipt"]["human_approval_granted"],
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

def create_operational_agent_army_safety_boundary_matrix() -> dict:
    return {
        "operational_agent_army_mode_manifest": "ALLOWED",
        "operational_workpack_schema": "ALLOWED",
        "controlled_workpack_action_registry": "ALLOWED",
        "operational_agent_squad_assignment_map": "ALLOWED",
        "operational_approval_receipt": "ALLOWED",
        "controlled_workpack_execution_plan": "ALLOWED",
        "routed_v19_v18_v17_readonly_inspection": "ALLOWED",
        "controlled_local_temp_sandbox_artifact_write": "ALLOWED",
        "controlled_temp_artifact_readback_verification": "ALLOWED",
        "operational_agent_handoff_ledger": "ALLOWED",
        "operational_workpack_receipt": "ALLOWED",
        "operational_audit_record": "ALLOWED",
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
        "uncontrolled_tool_execution": "DENIED",
        "unregistered_tool_execution": "DENIED",
        "unapproved_tool_execution": "DENIED",
        "unvalidated_tool_execution": "DENIED",
        "arbitrary_tool_execution": "DENIED",
        "repo_file_mutation": "DENIED",
        "repo_write": "DENIED",
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
        "live_task_execution_outside_controlled_workpack": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v20_1_creation": "DENIED",
        "v21_creation": "DENIED"
    }

def create_station_chief_v20_operational_agent_army_mode_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "schema_type": "station_chief_v20_operational_agent_army_mode",
        "required_sections": [
            "operational_agent_army_mode_manifest",
            "operational_workpack_schema",
            "controlled_workpack_action_registry",
            "operational_agent_squad_assignment_map",
            "operational_approval_receipt",
            "controlled_workpack_execution_plan",
            "operational_workpack_execution",
            "operational_agent_handoff_ledger",
            "operational_workpack_receipt",
            "operational_agent_army_audit_record",
            "operational_agent_army_safety_boundary_matrix",
            "operational_agent_army_summary"
        ],
        "operational_agent_army_mode_authorized": True,
        "controlled_operational_workpack_authorized": True,
        "routed_v19/v18/v17_readonly_inspection_authorized": True,
        "controlled_local_temp_sandbox_artifact_write_authorized": True,
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
        "v20_1_created": False,
        "v21_created": False
    }

def create_station_chief_v20_operational_agent_army_mode_bundle(approval_phrase: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, execute_operational_workpack_flag: bool = False) -> dict:
    schema = create_station_chief_v20_operational_agent_army_mode_schema()
    manifest = create_operational_agent_army_mode_manifest()
    boundaries = create_operational_agent_army_safety_boundary_matrix()
    
    if execute_operational_workpack_flag:
        res = execute_operational_workpack(approval_phrase, operator_label, workpack_label)
    else:
        # Preview only
        wp_schema = create_operational_workpack_schema()
        action_reg = create_controlled_workpack_action_registry()
        assignment_map = create_operational_agent_squad_assignment_map()
        approval = create_operational_approval_receipt(approval_phrase, operator_label, workpack_label)
        exec_plan = create_controlled_workpack_execution_plan(wp_schema, action_reg, assignment_map, approval)
        res = {
            "execution_status": "V20_OPERATIONAL_AGENT_ARMY_WORKPACK_NOT_ATTEMPTED",
            "operational_workpack_performed": False,
            "controlled_action_count": 2,
            "completed_action_count": 0,
            "routed_v19_v18_v17_readonly_inspection_performed": False,
            "controlled_sandbox_artifact_write_performed": False,
            "inspected_file_count": 0,
            "inspected_file_records_present": False,
            "inspected_files": [],
            "controlled_temp_artifact_path": None,
            "controlled_temp_artifact_sha256": None,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "approval_receipt": approval,
            "manifest": manifest,
            "workpack_schema": wp_schema,
            "action_registry": action_reg,
            "assignment_map": assignment_map,
            "execution_plan": exec_plan,
            "routed_inspection_result": None,
            "artifact_write_result": None
        }
        
    handoff_ledger = create_operational_agent_handoff_ledger(res)
    receipt = create_operational_workpack_receipt(res, handoff_ledger)
    audit = create_operational_agent_army_audit_record(res, handoff_ledger, receipt)
    
    status = "OPERATIONAL_AGENT_ARMY_PREVIEW_ONLY"
    if execute_operational_workpack_flag:
        if res["operational_workpack_performed"]:
            status = "OPERATIONAL_AGENT_ARMY_WORKPACK_COMPLETED"
        else:
            status = "OPERATIONAL_AGENT_ARMY_WORKPACK_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
        "operational_agent_army_status": status,
        "operational_agent_army_mode_created": True,
        "controlled_workpack_execution_layer_created": True,
        "operational_workpack_schema_created": True,
        "controlled_workpack_action_registry_created": True,
        "operational_agent_squad_assignment_map_created": True,
        "agent_role_count": 6,
        "controlled_action_count": 2,
        "completed_action_count": res["completed_action_count"],
        "operational_workpack_performed": res["operational_workpack_performed"],
        "routed_v19_v18_v17_readonly_inspection_performed": res["routed_v19_v18_v17_readonly_inspection_performed"],
        "controlled_sandbox_artifact_write_performed": res["controlled_sandbox_artifact_write_performed"],
        "inspected_file_count": res["inspected_file_count"],
        "controlled_temp_artifact_path": res["controlled_temp_artifact_path"],
        "controlled_temp_artifact_sha256": res["controlled_temp_artifact_sha256"],
        "operational_agent_handoff_ledger_created": True,
        "handoff_receipt_count": 6,
        "operational_workpack_receipt_created": True,
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
        "v20_1_created": False,
        "v21_created": False,
        
        "schema": schema,
        "operational_agent_army_mode_manifest": manifest,
        "operational_workpack_schema": res["workpack_schema"],
        "controlled_workpack_action_registry": res["action_registry"],
        "operational_agent_squad_assignment_map": res["assignment_map"],
        "operational_approval_receipt": res["approval_receipt"],
        "controlled_workpack_execution_plan": res["execution_plan"],
        "operational_workpack_execution": res,
        "operational_agent_handoff_ledger": handoff_ledger,
        "operational_workpack_receipt": receipt,
        "operational_agent_army_audit_record": audit,
        "operational_agent_army_safety_boundary_matrix": boundaries,
        "operational_agent_army_summary": {
            "version": STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION,
            "status": status
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
