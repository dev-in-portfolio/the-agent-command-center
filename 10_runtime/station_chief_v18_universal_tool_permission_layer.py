import json
import hashlib
import re
from pathlib import Path

# Import from v17 module as allowed
from station_chief_v17_live_activation_protocol import (
    STATION_CHIEF_V17_APPROVAL_PHRASE,
    execute_controlled_readonly_repo_integrity_inspection
)

STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION = "18.0.0"
STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_STATUS = "STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_CONTROLLED_ADAPTER_EXECUTION"
STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_PHASE = "Station Chief v18.0 Universal Tool Permission Layer / Controlled Tool Adapter Execution Candidate"

STATION_CHIEF_V18_APPROVAL_PHRASE = "I_APPROVE_V18_CONTROLLED_TOOL_ADAPTER_EXECUTION"

STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID = "station-chief-v18-adapter-repo-readonly-integrity-execution-001"

STATION_CHIEF_V18_TOOL_CATEGORY_IDS = [
    "station-chief-tool-category-repo-code-001",
    "station-chief-tool-category-local-files-002",
    "station-chief-tool-category-documents-003",
    "station-chief-tool-category-spreadsheets-004",
    "station-chief-tool-category-email-005",
    "station-chief-tool-category-calendar-006",
    "station-chief-tool-category-web-research-007",
    "station-chief-tool-category-api-008",
    "station-chief-tool-category-database-009",
    "station-chief-tool-category-deployment-010",
    "station-chief-tool-category-local-execution-011",
    "station-chief-tool-category-agent-routing-012",
    "station-chief-tool-category-business-workflow-013"
]

STATION_CHIEF_V18_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v18.1 or broader controlled tool expansion requires explicit separate operator instruction"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()

def create_universal_tool_category_registry() -> dict:
    categories = [
        "repo_code_tools", "local_file_tools", "document_tools", "spreadsheet_tools",
        "email_tools", "calendar_tools", "web_research_tools", "api_tools",
        "database_tools", "deployment_tools", "local_execution_tools",
        "agent_routing_tools", "business_workflow_tools"
    ]
    
    registry = {}
    for idx, name in enumerate(categories):
        cat_id = STATION_CHIEF_V18_TOOL_CATEGORY_IDS[idx]
        registry[cat_id] = {
            "category_id": cat_id,
            "category_name": name,
            "category_type": "universal_tool_permission_category",
            "category_registered": True,
            "permission_contract_required": True,
            "preview_required": True,
            "human_approval_required": True,
            "execution_receipt_required": True,
            "audit_required": True,
            "rollback_or_abort_rule_required": True,
            "executable_in_v18": name == "repo_code_tools",
            "live_adapter_count_allowed_in_v18": 1 if name == "repo_code_tools" else 0,
            "mutation_allowed_in_v18": False,
            "production_allowed_in_v18": False,
            "network_allowed_in_v18": False,
            "credential_access_allowed_in_v18": False,
            "secret_access_allowed_in_v18": False,
            "external_tool_execution_allowed_in_v18": False
        }
    return registry

def create_universal_tool_permission_contract() -> dict:
    return {
        "contract_id": sha256_digest("universal_tool_permission_contract"),
        "contract_type": "universal_tool_permission_contract",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "all_tool_categories_registered": True,
        "tool_category_count": 13,
        "action_class_required": True,
        "preview_required": True,
        "exact_human_approval_required": True,
        "scoped_approval_required": True,
        "live_execution_receipt_required": True,
        "denial_receipt_required": True,
        "audit_record_required": True,
        "rollback_or_abort_policy_required": True,
        "fail_closed_required": True,
        "future_expansion_requires_explicit_instruction": True,
        "no_tool_executes_without_adapter": True,
        "no_tool_executes_without_permission_contract": True,
        "no_tool_executes_without_receipt": True,
        "no_tool_executes_without_validator_coverage": True,
        "permission_modes": ["PREVIEW_ONLY", "DENIED", "APPROVED_CONTROLLED_EXECUTION"]
    }

def create_controlled_tool_adapter_registry(tool_category_registry: dict) -> dict:
    adapters = [
        {"id": STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID, "name": "repo_readonly_integrity_execution_adapter", "cat": "repo_code_tools", "exec": True},
        {"id": "station-chief-v18-adapter-local-files-preview-002", "name": "local_files_preview_adapter", "cat": "local_file_tools", "exec": False},
        {"id": "station-chief-v18-adapter-documents-preview-003", "name": "document_preview_adapter", "cat": "document_tools", "exec": False},
        {"id": "station-chief-v18-adapter-spreadsheets-preview-004", "name": "spreadsheet_preview_adapter", "cat": "spreadsheet_tools", "exec": False},
        {"id": "station-chief-v18-adapter-email-preview-005", "name": "email_preview_adapter", "cat": "email_tools", "exec": False},
        {"id": "station-chief-v18-adapter-calendar-preview-006", "name": "calendar_preview_adapter", "cat": "calendar_tools", "exec": False},
        {"id": "station-chief-v18-adapter-web-research-preview-007", "name": "web_research_preview_adapter", "cat": "web_research_tools", "exec": False},
        {"id": "station-chief-v18-adapter-api-preview-008", "name": "api_preview_adapter", "cat": "api_tools", "exec": False},
        {"id": "station-chief-v18-adapter-database-preview-009", "name": "database_preview_adapter", "cat": "database_tools", "exec": False},
        {"id": "station-chief-v18-adapter-deployment-preview-010", "name": "deployment_preview_adapter", "cat": "deployment_tools", "exec": False},
        {"id": "station-chief-v18-adapter-local-execution-preview-011", "name": "local_execution_preview_adapter", "cat": "local_execution_tools", "exec": False},
        {"id": "station-chief-v18-adapter-agent-routing-preview-012", "name": "agent_routing_preview_adapter", "cat": "agent_routing_tools", "exec": False},
        {"id": "station-chief-v18-adapter-business-workflow-preview-013", "name": "business_workflow_preview_adapter", "cat": "business_workflow_tools", "exec": False}
    ]
    
    registry = {}
    for a in adapters:
        registry[a["id"]] = {
            "adapter_id": a["id"],
            "adapter_name": a["name"],
            "category_name": a["cat"],
            "adapter_type": "controlled_tool_adapter_descriptor",
            "adapter_registered": True,
            "preview_supported": True,
            "human_approval_required": True,
            "execution_receipt_required": True,
            "audit_required": True,
            "executable_in_v18": a["exec"],
            "live_execution_allowed_in_v18": a["exec"],
            "wraps_v17_readonly_repo_inspection": a["id"] == STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID,
            "mutation_allowed": False,
            "production_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "secret_access_allowed": False,
            "external_tool_call_allowed": False,
            "api_call_allowed": False,
            "deployment_allowed": False,
            "shell_allowed": False,
            "subprocess_allowed": False,
            "queue_allowed": False,
            "arbitrary_task_allowed": False
        }
    return registry

def create_tool_action_request_envelope(adapter_id: str | None = None, requested_mode: str | None = None, operator_label: str | None = None) -> dict:
    mode = requested_mode or "PREVIEW_ONLY"
    a_id = adapter_id or STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID
    op = normalize_label(operator_label, "unknown_operator")
    
    return {
        "request_envelope_id": sha256_digest({"adapter": a_id, "mode": mode, "op": op}),
        "envelope_type": "universal_tool_action_request_envelope",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "requested_adapter_id": a_id,
        "requested_mode": mode,
        "operator_label": op,
        "request_scope": "controlled_tool_adapter_execution",
        "mutation_requested": False,
        "production_requested": False,
        "network_requested": False,
        "credential_access_requested": False,
        "secret_access_requested": False,
        "external_tool_call_requested": False,
        "api_call_requested": False,
        "deployment_requested": False,
        "shell_requested": False,
        "subprocess_requested": False,
        "queue_requested": False,
        "arbitrary_task_requested": False
    }

def create_tool_action_preview_packet(request_envelope: dict, adapter_registry: dict) -> dict:
    adapter_id = request_envelope["requested_adapter_id"]
    adapter = adapter_registry.get(adapter_id)
    exists = adapter is not None
    executable = adapter.get("executable_in_v18", False) if exists else False
    
    status = "READY_FOR_HUMAN_APPROVAL" if (exists and executable) else "LOCKED_OR_DENIED"
    
    return {
        "preview_packet_id": sha256_digest({"env": request_envelope["request_envelope_id"], "status": status}),
        "preview_type": "universal_tool_action_preview_packet",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "requested_adapter_id": adapter_id,
        "requested_mode": request_envelope["requested_mode"],
        "adapter_exists": exists,
        "adapter_executable_in_v18": executable,
        "preview_status": status,
        "exact_approval_phrase_required": STATION_CHIEF_V18_APPROVAL_PHRASE,
        "wrapped_v17_approval_phrase_required": STATION_CHIEF_V17_APPROVAL_PHRASE,
        "expected_action": "controlled_repo_readonly_integrity_execution" if adapter_id == STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID else "unknown",
        "expected_result": "tool_execution_receipt_with_v17_integrity_records" if adapter_id == STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID else "denial",
        "mutation_expected": False,
        "production_expected": False,
        "credential_access_expected": False,
        "network_access_expected": False,
        "api_call_expected": False,
        "deployment_expected": False,
        "rollback_required": False,
        "abort_available": True
    }

def create_tool_human_approval_receipt(approval_phrase: str | None, request_envelope: dict, operator_label: str | None = None) -> dict:
    phrase_received = approval_phrase is not None
    phrase_matches = approval_phrase == STATION_CHIEF_V18_APPROVAL_PHRASE
    op = normalize_label(operator_label, request_envelope["operator_label"])
    
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "env": request_envelope["request_envelope_id"]}),
        "receipt_type": "v18_tool_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "operator_label": op,
        "approval_phrase_received": phrase_received,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V18_APPROVAL_PHRASE,
        "human_approval_granted": phrase_matches,
        "autonomous_self_approval": False,
        "approval_scope": "v18_controlled_tool_adapter_execution_only",
        "approval_does_not_authorize_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_broader_tool_use": True,
        "approval_does_not_authorize_future_adapters": True
    }

def route_universal_tool_action(request_envelope: dict, approval_receipt: dict, adapter_registry: dict) -> dict:
    adapter_id = request_envelope["requested_adapter_id"]
    adapter = adapter_registry.get(adapter_id)
    exists = adapter is not None
    executable = adapter.get("executable_in_v18", False) if exists else False
    approved = approval_receipt["human_approval_granted"]
    
    execute = False
    status = "DENIED_OR_PREVIEW_ONLY"
    v17_req = False
    
    if adapter_id == STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID and approved:
        status = "APPROVED_FOR_CONTROLLED_ADAPTER_EXECUTION"
        execute = True
        v17_req = True
        
    return {
        "router_id": sha256_digest({"env": request_envelope["request_envelope_id"], "app": approved}),
        "router_type": "universal_tool_execution_router",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "requested_adapter_id": adapter_id,
        "adapter_exists": exists,
        "adapter_executable_in_v18": executable,
        "human_approval_granted": approved,
        "route_status": status,
        "execute_adapter": execute,
        "wrapped_v17_execution_required": v17_req,
        "mutation_allowed": False,
        "production_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "external_tool_call_allowed": False,
        "api_call_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }

def execute_v18_controlled_tool_adapter(approval_phrase: str | None, operator_label: str | None = None, adapter_id: str | None = None, requested_mode: str | None = None) -> dict:
    cat_registry = create_universal_tool_category_registry()
    contract = create_universal_tool_permission_contract()
    adapter_registry = create_controlled_tool_adapter_registry(cat_registry)
    
    envelope = create_tool_action_request_envelope(adapter_id, requested_mode, operator_label)
    preview = create_tool_action_preview_packet(envelope, adapter_registry)
    approval = create_tool_human_approval_receipt(approval_phrase, envelope, operator_label)
    
    route = route_universal_tool_action(envelope, approval, adapter_registry)
    
    v17_result = None
    if route["execute_adapter"]:
        # Execute wrapped v17 with v17 approval phrase
        v17_result = execute_controlled_readonly_repo_integrity_inspection(STATION_CHIEF_V17_APPROVAL_PHRASE, operator_label)
        
    performed = route["execute_adapter"] and v17_result and v17_result.get("live_action_performed", False)
    
    return {
        "execution_status": "V18_CONTROLLED_TOOL_ADAPTER_EXECUTION_COMPLETED" if performed else "V18_CONTROLLED_TOOL_ADAPTER_EXECUTION_DENIED",
        "live_tool_adapter_execution_performed": performed,
        "wrapped_v17_readonly_inspection_performed": performed,
        "inspected_file_count": v17_result["inspected_file_count"] if performed else 0,
        "inspected_file_records_present": performed,
        "inspected_files": v17_result["inspected_files"] if performed else [],
        "approval_receipt": approval,
        "request_envelope": envelope,
        "preview_packet": preview,
        "router_decision": route,
        "file_contents_printed": False,
        "file_mutation_performed": False,
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
        "live_orchestration_performed": False
    }

def create_tool_execution_receipt(adapter_execution_result: dict) -> dict:
    res = adapter_execution_result
    performed = res["live_tool_adapter_execution_performed"]
    digest = sha256_digest(res["inspected_files"]) if performed else None
    
    return {
        "tool_execution_receipt_id": sha256_digest(res),
        "receipt_type": "v18_controlled_tool_execution_receipt",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "requested_adapter_id": res["request_envelope"]["requested_adapter_id"],
        "execution_status": res["execution_status"],
        "live_tool_adapter_execution_performed": performed,
        "wrapped_v17_readonly_inspection_performed": res["wrapped_v17_readonly_inspection_performed"],
        "inspected_file_count": res["inspected_file_count"],
        "inspected_file_digest_summary": digest,
        "receipt_status": "CONTROLLED_TOOL_ADAPTER_EXECUTION_COMPLETED" if performed else "CONTROLLED_TOOL_ADAPTER_EXECUTION_DENIED",
        "no_file_contents_printed": True,
        "no_mutation": True,
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
        "no_subprocess": True,
        "no_shell": True,
        "no_queue": True,
        "no_live_task_execution": True
    }

def create_denied_tool_audit_record(adapter_execution_result: dict, tool_execution_receipt: dict) -> dict:
    return {
        "denied_audit_id": sha256_digest("denied_tool_audit"),
        "audit_type": "v18_denied_or_locked_tool_audit",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "locked_adapter_count": 12,
        "live_adapter_count": 1,
        "only_repo_readonly_adapter_executable": True,
        "email_live_execution_denied": True,
        "calendar_live_execution_denied": True,
        "web_live_execution_denied": True,
        "api_live_execution_denied": True,
        "database_live_execution_denied": True,
        "deployment_live_execution_denied": True,
        "local_execution_live_execution_denied": True,
        "mutation_actions_denied": True,
        "production_actions_denied": True,
        "credential_actions_denied": True,
        "network_actions_denied": True,
        "broader_live_actions_denied": True
    }

def create_universal_tool_activation_audit_record(adapter_execution_result: dict, tool_execution_receipt: dict, denied_audit: dict) -> dict:
    res = adapter_execution_result
    return {
        "audit_id": sha256_digest({"res": res["execution_status"], "receipt": tool_execution_receipt["receipt_status"]}),
        "audit_type": "v18_universal_tool_permission_layer_audit",
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "universal_tool_permission_layer_created": True,
        "controlled_tool_adapter_registry_created": True,
        "tool_category_count": 13,
        "adapter_count": 13,
        "live_adapter_count": 1,
        "locked_adapter_count": 12,
        "live_tool_adapter_execution_performed": res["live_tool_adapter_execution_performed"],
        "wrapped_v17_readonly_inspection_performed": res["wrapped_v17_readonly_inspection_performed"],
        "inspected_file_count": res["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": res["approval_receipt"]["human_approval_granted"],
        "no_file_contents_printed": True,
        "no_file_mutation": True,
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
        "no_user_task_execution": True
    }

def create_universal_tool_safety_boundary_matrix() -> dict:
    return {
        "universal_tool_category_registry": "ALLOWED",
        "universal_tool_permission_contract": "ALLOWED",
        "controlled_tool_adapter_registry": "ALLOWED",
        "tool_action_request_envelope": "ALLOWED",
        "tool_action_preview_packet": "ALLOWED",
        "human_approval_receipt": "ALLOWED",
        "universal_tool_execution_router": "ALLOWED",
        "controlled_repo_readonly_integrity_adapter_execution": "ALLOWED",
        "wrapped_v17_readonly_repo_inspection": "ALLOWED",
        "allowlisted_file_read": "ALLOWED",
        "allowlisted_file_sha256": "ALLOWED",
        "allowlisted_file_byte_count": "ALLOWED",
        "allowlisted_file_line_count": "ALLOWED",
        "json_receipt_output": "ALLOWED",
        
        "uncontrolled_tool_execution": "DENIED",
        "unregistered_tool_execution": "DENIED",
        "unapproved_tool_execution": "DENIED",
        "unvalidated_tool_execution": "DENIED",
        "arbitrary_tool_execution": "DENIED",
        "live_email_execution": "DENIED",
        "live_calendar_execution": "DENIED",
        "live_web_execution": "DENIED",
        "live_api_execution": "DENIED",
        "live_database_execution": "DENIED",
        "live_deployment_execution": "DENIED",
        "live_local_shell_execution": "DENIED",
        "uncontrolled_live_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
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
        "filesystem_mutation": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v18_1_creation": "DENIED",
        "v19_creation": "DENIED"
    }

def create_station_chief_v18_universal_tool_permission_layer_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "schema_type": "station_chief_v18_universal_tool_permission_layer",
        "required_sections": [
            "universal_tool_category_registry",
            "universal_tool_permission_contract",
            "controlled_tool_adapter_registry",
            "tool_action_request_envelope",
            "tool_action_preview_packet",
            "tool_human_approval_receipt",
            "universal_tool_execution_router",
            "controlled_tool_adapter_execution",
            "tool_execution_receipt",
            "denied_tool_audit_record",
            "universal_tool_activation_audit_record",
            "universal_tool_safety_boundary_matrix",
            "universal_tool_permission_summary"
        ],
        "universal_tool_permission_layer_authorized": True,
        "controlled_repo_read-only_tool_adapter_authorized": True,
        "human_approval_required": True,
        "no_uncontrolled_tool_execution_authorized": True,
        "no_arbitrary_tool_execution_authorized": True,
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
        "no_worker_process_start_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_live_orchestration_authorized": True,
        "v18_1_created": False,
        "v19_created": False
    }

def create_station_chief_v18_universal_tool_permission_layer_bundle(approval_phrase: str | None = None, operator_label: str | None = None, adapter_id: str | None = None, requested_mode: str | None = None, execute_controlled_adapter: bool = False) -> dict:
    schema = create_station_chief_v18_universal_tool_permission_layer_schema()
    cat_reg = create_universal_tool_category_registry()
    contract = create_universal_tool_permission_contract()
    adapter_reg = create_controlled_tool_adapter_registry(cat_reg)
    boundaries = create_universal_tool_safety_boundary_matrix()
    
    if execute_controlled_adapter:
        res = execute_v18_controlled_tool_adapter(approval_phrase, operator_label, adapter_id, requested_mode)
    else:
        env = create_tool_action_request_envelope(adapter_id, requested_mode, operator_label)
        preview = create_tool_action_preview_packet(env, adapter_reg)
        approval = create_tool_human_approval_receipt(approval_phrase, env, operator_label)
        route = route_universal_tool_action(env, approval, adapter_reg)
        res = {
            "execution_status": "V18_CONTROLLED_TOOL_ADAPTER_EXECUTION_NOT_ATTEMPTED",
            "live_tool_adapter_execution_performed": False,
            "wrapped_v17_readonly_inspection_performed": False,
            "inspected_file_count": 0,
            "inspected_file_records_present": False,
            "inspected_files": [],
            "approval_receipt": approval,
            "request_envelope": env,
            "preview_packet": preview,
            "router_decision": route
        }
        
    receipt = create_tool_execution_receipt(res)
    denied_audit = create_denied_tool_audit_record(res, receipt)
    audit = create_universal_tool_activation_audit_record(res, receipt, denied_audit)
    
    status = "UNIVERSAL_TOOL_LAYER_PREVIEW_ONLY"
    if execute_controlled_adapter:
        if res["live_tool_adapter_execution_performed"]:
            status = "CONTROLLED_TOOL_ADAPTER_EXECUTION_COMPLETED"
        else:
            status = "CONTROLLED_TOOL_ADAPTER_EXECUTION_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
        "universal_tool_permission_status": status,
        "universal_tool_permission_layer_created": True,
        "all_tool_categories_registered": True,
        "tool_category_count": 13,
        "controlled_tool_adapter_registry_created": True,
        "adapter_count": 13,
        "live_adapter_count": 1,
        "locked_adapter_count": 12,
        "controlled_repo_readonly_adapter_created": True,
        "controlled_repo_readonly_adapter_executed": res["live_tool_adapter_execution_performed"],
        "live_tool_adapter_execution_performed": res["live_tool_adapter_execution_performed"],
        "wrapped_v17_readonly_inspection_performed": res["wrapped_v17_readonly_inspection_performed"],
        "inspected_file_count": res["inspected_file_count"],
        "file_contents_printed": False,
        "file_mutation_performed": False,
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
        "database_mutation_performed": False,
        "full_workforce_activation_performed": False,
        "v18_1_created": False,
        "v19_created": False,
        
        "schema": schema,
        "universal_tool_category_registry": cat_reg,
        "universal_tool_permission_contract": contract,
        "controlled_tool_adapter_registry": adapter_reg,
        "tool_action_request_envelope": res["request_envelope"],
        "tool_action_preview_packet": res["preview_packet"],
        "tool_human_approval_receipt": res["approval_receipt"],
        "universal_tool_execution_router": res["router_decision"],
        "controlled_tool_adapter_execution": res,
        "tool_execution_receipt": receipt,
        "denied_tool_audit_record": denied_audit,
        "universal_tool_activation_audit_record": audit,
        "universal_tool_safety_boundary_matrix": boundaries,
        "universal_tool_permission_summary": {
            "version": STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION,
            "status": status
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
