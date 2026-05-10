import json
import hashlib
import re
from pathlib import Path

# Import from v18 module as allowed
from station_chief_v18_universal_tool_permission_layer import (
    STATION_CHIEF_V18_APPROVAL_PHRASE,
    STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID,
    execute_v18_controlled_tool_adapter
)

STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION = "19.0.0"
STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_STATUS = "STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_SUPERVISED_DISPATCH"
STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_PHASE = "Station Chief v19.0 Multi-Agent Live Work Router / Supervised Dispatch Layer Candidate"

STATION_CHIEF_V19_APPROVAL_PHRASE = "I_APPROVE_V19_MULTI_AGENT_LIVE_ROUTED_WORK"

STATION_CHIEF_V19_ALLOWED_ROUTED_ACTION_ID = "station-chief-v19-routed-v18-controlled-repo-readonly-adapter-work-001"

STATION_CHIEF_V19_AGENT_ROLE_IDS = [
    "station-chief-v19-agent-role-intake-coordinator-001",
    "station-chief-v19-agent-role-permission-auditor-002",
    "station-chief-v19-agent-role-dispatch-controller-003",
    "station-chief-v19-agent-role-execution-observer-004",
    "station-chief-v19-agent-role-receipt-scribe-005",
    "station-chief-v19-agent-role-safety-officer-006"
]

STATION_CHIEF_V19_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v19.1 or broader multi-tool/multi-agent expansion requires explicit separate operator instruction"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()

def create_live_agent_squad_registry() -> dict:
    roles = [
        "intake_coordinator", "permission_auditor", "dispatch_controller",
        "execution_observer", "receipt_scribe", "safety_officer"
    ]
    
    registry = {}
    for idx, name in enumerate(roles):
        role_id = STATION_CHIEF_V19_AGENT_ROLE_IDS[idx]
        registry[role_id] = {
            "agent_role_id": role_id,
            "agent_role_name": name,
            "agent_role_type": "logical_supervised_live_work_agent",
            "role_registered": True,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "daemon_started": False,
            "subprocess_started": False,
            "shell_execution_allowed": False,
            "human_supervision_required": True,
            "can_receive_task_packet": True,
            "can_create_metadata_receipt": True,
            "can_execute_tools": False,
            "can_mutate_files": False,
            "can_access_credentials": False,
            "can_access_network": False,
            "can_touch_production": False
        }
    return registry

def create_supervised_live_task_packet(task_label: str | None = None, operator_label: str | None = None) -> dict:
    t_label = normalize_label(task_label, "v19_supervised_task")
    o_label = normalize_label(operator_label, "unknown_operator")
    
    return {
        "task_packet_id": sha256_digest({"label": t_label, "op": o_label, "version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION}),
        "packet_type": "supervised_live_work_task_packet",
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "task_label": t_label,
        "operator_label": o_label,
        "requested_action_id": STATION_CHIEF_V19_ALLOWED_ROUTED_ACTION_ID,
        "requested_adapter_id": STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID,
        "requested_tool_category": "repo_code_tools",
        "requested_work_class": "controlled_repo_readonly_integrity_adapter_execution",
        "live_work_requested": True,
        "human_approval_required": True,
        "supervised_dispatch_required": True,
        "agent_handoff_receipts_required": True,
        "final_work_receipt_required": True,
        "mutation_requested": False,
        "production_requested": False,
        "deployment_requested": False,
        "network_requested": False,
        "credential_access_requested": False,
        "external_tool_call_requested": False,
        "api_call_requested": False,
        "shell_requested": False,
        "subprocess_requested": False,
        "queue_requested": False,
        "arbitrary_task_requested": False
    }

def create_agent_assignment_matrix(agent_squad_registry: dict, task_packet: dict) -> dict:
    assignments = {}
    mapping = {
        STATION_CHIEF_V19_AGENT_ROLE_IDS[0]: "task_packet_review",
        STATION_CHIEF_V19_AGENT_ROLE_IDS[1]: "permission_scope_review",
        STATION_CHIEF_V19_AGENT_ROLE_IDS[2]: "adapter_dispatch_plan",
        STATION_CHIEF_V19_AGENT_ROLE_IDS[3]: "controlled_execution_observation",
        STATION_CHIEF_V19_AGENT_ROLE_IDS[4]: "receipt_ledger_creation",
        STATION_CHIEF_V19_AGENT_ROLE_IDS[5]: "final_safety_review"
    }
    
    for role_id, role in agent_squad_registry.items():
        stage = mapping.get(role_id)
        assignments[role_id] = {
            "agent_role_id": role_id,
            "agent_role_name": role["agent_role_name"],
            "workflow_stage": stage
        }
        
    return {
        "assignment_matrix_id": sha256_digest(assignments),
        "matrix_type": "multi_agent_live_work_assignment_matrix",
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "agent_role_count": len(agent_squad_registry),
        "assignment_count": len(assignments),
        "all_roles_assigned": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "logical_agent_routing_only": True,
        "assignments": assignments
    }

def create_live_work_routing_decision(task_packet: dict, assignment_matrix: dict, approval_phrase: str | None, operator_label: str | None = None) -> dict:
    phrase_matches = approval_phrase == STATION_CHIEF_V19_APPROVAL_PHRASE
    op = normalize_label(operator_label, task_packet["operator_label"])
    
    return {
        "routing_decision_id": sha256_digest({"packet": task_packet["task_packet_id"], "approved": phrase_matches}),
        "decision_type": "multi_agent_live_work_routing_decision",
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "requested_action_id": task_packet["requested_action_id"],
        "requested_adapter_id": task_packet["requested_adapter_id"],
        "operator_label": op,
        "approval_phrase_received": approval_phrase is not None,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V19_APPROVAL_PHRASE,
        "human_approval_granted": phrase_matches,
        "route_status": "APPROVED_FOR_SUPERVISED_DISPATCH" if phrase_matches else "DENIED_OR_PREVIEW_ONLY",
        "supervised_dispatch_allowed": phrase_matches,
        "controlled_v18_adapter_execution_allowed": phrase_matches,
        "mutation_allowed": False,
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

def create_supervised_dispatch_plan(task_packet: dict, assignment_matrix: dict, routing_decision: dict) -> dict:
    approved = routing_decision["human_approval_granted"]
    
    return {
        "dispatch_plan_id": sha256_digest({"decision": routing_decision["routing_decision_id"]}),
        "plan_type": "supervised_multi_agent_live_work_dispatch_plan",
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "dispatch_status": "READY_FOR_CONTROLLED_ADAPTER_EXECUTION" if approved else "DISPATCH_DENIED_OR_PREVIEW_ONLY",
        "requested_action_id": task_packet["requested_action_id"],
        "requested_adapter_id": task_packet["requested_adapter_id"],
        "agent_role_count": 6,
        "dispatch_stage_count": 6,
        "supervised_dispatch_allowed": approved,
        "execute_controlled_adapter": approved,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "no_queue_created": True,
        "no_shell_or_subprocess": True,
        "no_network_access": True,
        "no_credential_access": True,
        "no_mutation": True,
        "no_production": True
    }

def create_routed_work_human_approval_receipt(routing_decision: dict, task_packet: dict) -> dict:
    return {
        "approval_receipt_id": sha256_digest({"decision": routing_decision["routing_decision_id"]}),
        "receipt_type": "v19_routed_work_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "operator_label": routing_decision["operator_label"],
        "requested_action_id": task_packet["requested_action_id"],
        "requested_adapter_id": task_packet["requested_adapter_id"],
        "approval_phrase_received": routing_decision["approval_phrase_received"],
        "approval_phrase_matches": routing_decision["approval_phrase_matches"],
        "expected_approval_phrase": STATION_CHIEF_V19_APPROVAL_PHRASE,
        "human_approval_granted": routing_decision["human_approval_granted"],
        "autonomous_self_approval": False,
        "approval_scope": "v19_supervised_multi_agent_routed_controlled_adapter_work_only",
        "approval_does_not_authorize_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_broader_tool_use": True,
        "approval_does_not_authorize_future_adapters": True,
        "approval_does_not_authorize_real_worker_processes": True
    }

def execute_routed_controlled_adapter_work(approval_phrase: str | None, operator_label: str | None = None, task_label: str | None = None) -> dict:
    squad_registry = create_live_agent_squad_registry()
    task_packet = create_supervised_live_task_packet(task_label, operator_label)
    assignment_matrix = create_agent_assignment_matrix(squad_registry, task_packet)
    routing_decision = create_live_work_routing_decision(task_packet, assignment_matrix, approval_phrase, operator_label)
    dispatch_plan = create_supervised_dispatch_plan(task_packet, assignment_matrix, routing_decision)
    approval_receipt = create_routed_work_human_approval_receipt(routing_decision, task_packet)
    
    v18_result = None
    routed_live_work_performed = False
    
    if routing_decision["human_approval_granted"]:
        # Execute v18 controlled tool adapter using internally provided v18 phrase
        v18_result = execute_v18_controlled_tool_adapter(
            STATION_CHIEF_V18_APPROVAL_PHRASE,
            operator_label=operator_label,
            adapter_id=STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID,
            requested_mode="APPROVED_CONTROLLED_EXECUTION"
        )
        routed_live_work_performed = v18_result.get("live_tool_adapter_execution_performed", False)
        
    return {
        "execution_status": "V19_SUPERVISED_MULTI_AGENT_ROUTED_WORK_COMPLETED" if routed_live_work_performed else "V19_SUPERVISED_MULTI_AGENT_ROUTED_WORK_DENIED",
        "routed_live_work_performed": routed_live_work_performed,
        "supervised_dispatch_performed": routed_live_work_performed,
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "wrapped_v18_controlled_adapter_execution_performed": routed_live_work_performed,
        "wrapped_v17_readonly_inspection_performed": v18_result.get("wrapped_v17_readonly_inspection_performed", False) if v18_result else False,
        "inspected_file_count": v18_result.get("inspected_file_count", 0) if v18_result else 0,
        "inspected_file_records_present": routed_live_work_performed,
        "inspected_files": v18_result.get("inspected_files", []) if v18_result else [],
        "squad_registry": squad_registry,
        "task_packet": task_packet,
        "assignment_matrix": assignment_matrix,
        "routing_decision": routing_decision,
        "dispatch_plan": dispatch_plan,
        "approval_receipt": approval_receipt,
        "controlled_adapter_result": v18_result,
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

def create_agent_handoff_receipt_ledger(routed_work_result: dict) -> dict:
    assignments = routed_work_result["assignment_matrix"]["assignments"]
    performed = routed_work_result["routed_live_work_performed"]
    
    receipts = {}
    for role_id, assignment in assignments.items():
        h_id = sha256_digest({"role": role_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": role_id,
            "agent_role_name": assignment["agent_role_name"],
            "workflow_stage": assignment["workflow_stage"],
            "receipt_type": "logical_agent_handoff_receipt",
            "runtime_version": "19.0.0",
            "task_packet_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False, # Logical routing only
            "mutation_performed": False,
            "credential_access_performed": False,
            "network_access_performed": False,
            "shell_executed": False,
            "subprocess_started": False
        }
        
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v19_agent_handoff_receipt_ledger",
        "runtime_version": "19.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }

def create_final_routed_work_receipt(routed_work_result: dict, handoff_ledger: dict) -> dict:
    performed = routed_work_result["routed_live_work_performed"]
    
    return {
        "final_routed_work_receipt_id": sha256_digest({"res": routed_work_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v19_final_routed_work_receipt",
        "runtime_version": "19.0.0",
        "routed_live_work_performed": performed,
        "supervised_dispatch_performed": routed_work_result["supervised_dispatch_performed"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "wrapped_v18_controlled_adapter_execution_performed": routed_work_result["wrapped_v18_controlled_adapter_execution_performed"],
        "wrapped_v17_readonly_inspection_performed": routed_work_result["wrapped_v17_readonly_inspection_performed"],
        "inspected_file_count": routed_work_result["inspected_file_count"],
        "receipt_status": "SUPERVISED_MULTI_AGENT_ROUTED_WORK_COMPLETED" if performed else "SUPERVISED_MULTI_AGENT_ROUTED_WORK_DENIED",
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
        "no_real_worker_process": True,
        "no_background_agent": True,
        "no_subprocess": True,
        "no_shell": True,
        "no_queue": True,
        "no_live_task_execution": True
    }

def create_multi_agent_live_work_audit_record(routed_work_result: dict, handoff_ledger: dict, final_receipt: dict) -> dict:
    performed = routed_work_result["routed_live_work_performed"]
    
    return {
        "audit_id": sha256_digest({"final": final_receipt["final_routed_work_receipt_id"]}),
        "audit_type": "v19_multi_agent_live_work_router_audit",
        "runtime_version": "19.0.0",
        "multi_agent_live_work_router_created": True,
        "live_agent_squad_registry_created": True,
        "supervised_live_task_packet_created": True,
        "agent_assignment_matrix_created": True,
        "live_work_routing_decision_created": True,
        "supervised_dispatch_plan_created": True,
        "agent_handoff_receipt_ledger_created": True,
        "final_routed_work_receipt_created": True,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "routed_live_work_performed": performed,
        "supervised_dispatch_performed": routed_work_result["supervised_dispatch_performed"],
        "wrapped_v18_controlled_adapter_execution_performed": routed_work_result["wrapped_v18_controlled_adapter_execution_performed"],
        "wrapped_v17_readonly_inspection_performed": routed_work_result["wrapped_v17_readonly_inspection_performed"],
        "inspected_file_count": routed_work_result["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": routed_work_result["routing_decision"]["human_approval_granted"],
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
        "no_background_agent_started": True,
        "no_agent_process_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed": True,
        "no_live_worker_routing_to_real_processes": True,
        "no_uncontrolled_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True
    }

def create_multi_agent_live_work_safety_boundary_matrix() -> dict:
    return {
        "live_agent_squad_registry": "ALLOWED",
        "supervised_live_task_packet": "ALLOWED",
        "agent_assignment_matrix": "ALLOWED",
        "live_work_routing_decision": "ALLOWED",
        "supervised_dispatch_plan": "ALLOWED",
        "logical_agent_handoff_receipts": "ALLOWED",
        "routed_controlled_v18_adapter_execution": "ALLOWED",
        "wrapped_v18_controlled_tool_adapter_execution": "ALLOWED",
        "wrapped_v17_readonly_repo_inspection": "ALLOWED",
        "allowlisted_file_read": "ALLOWED",
        "allowlisted_file_sha256": "ALLOWED",
        "allowlisted_file_byte_count": "ALLOWED",
        "allowlisted_file_line_count": "ALLOWED",
        "final_routed_work_receipt": "ALLOWED",
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
        "live_task_execution_outside_controlled_adapter": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "filesystem_mutation": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v19_1_creation": "DENIED",
        "v20_creation": "DENIED"
    }

def create_station_chief_v19_multi_agent_live_work_router_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "schema_type": "station_chief_v19_multi_agent_live_work_router",
        "required_sections": [
            "live_agent_squad_registry",
            "supervised_live_task_packet",
            "agent_assignment_matrix",
            "live_work_routing_decision",
            "supervised_dispatch_plan",
            "routed_work_human_approval_receipt",
            "routed_controlled_adapter_work",
            "agent_handoff_receipt_ledger",
            "final_routed_work_receipt",
            "multi_agent_live_work_audit_record",
            "multi_agent_live_work_safety_boundary_matrix",
            "multi_agent_live_work_summary"
        ],
        "multi_agent_live_work_router_authorized": True,
        "supervised_routed_controlled_adapter_work_authorized": True,
        "logical_agent_routing_authorized": True,
        "human_approval_required": True,
        "no_uncontrolled_agent_activation_authorized": True,
        "no_real_worker_process_authorized": True,
        "no_background_agent_authorized": True,
        "no_arbitrary_agent_execution_authorized": True,
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
        "v19_1_created": False,
        "v20_created": False
    }

def create_station_chief_v19_multi_agent_live_work_router_bundle(approval_phrase: str | None = None, operator_label: str | None = None, task_label: str | None = None, execute_routed_work: bool = False) -> dict:
    schema = create_station_chief_v19_multi_agent_live_work_router_schema()
    squad_registry = create_live_agent_squad_registry()
    boundaries = create_multi_agent_live_work_safety_boundary_matrix()
    
    if execute_routed_work:
        res = execute_routed_controlled_adapter_work(approval_phrase, operator_label, task_label)
    else:
        # Denied/Preview only metadata
        task_packet = create_supervised_live_task_packet(task_label, operator_label)
        assignment_matrix = create_agent_assignment_matrix(squad_registry, task_packet)
        routing_decision = create_live_work_routing_decision(task_packet, assignment_matrix, approval_phrase, operator_label)
        dispatch_plan = create_supervised_dispatch_plan(task_packet, assignment_matrix, routing_decision)
        approval_receipt = create_routed_work_human_approval_receipt(routing_decision, task_packet)
        res = {
            "execution_status": "V19_SUPERVISED_MULTI_AGENT_ROUTED_WORK_NOT_ATTEMPTED",
            "routed_live_work_performed": False,
            "supervised_dispatch_performed": False,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "wrapped_v18_controlled_adapter_execution_performed": False,
            "wrapped_v17_readonly_inspection_performed": False,
            "inspected_file_count": 0,
            "inspected_file_records_present": False,
            "inspected_files": [],
            "squad_registry": squad_registry,
            "task_packet": task_packet,
            "assignment_matrix": assignment_matrix,
            "routing_decision": routing_decision,
            "dispatch_plan": dispatch_plan,
            "approval_receipt": approval_receipt,
            "human_approval_granted": approval_receipt["human_approval_granted"],
            "controlled_adapter_result": None
        }
        
    handoff_ledger = create_agent_handoff_receipt_ledger(res)
    final_receipt = create_final_routed_work_receipt(res, handoff_ledger)
    audit = create_multi_agent_live_work_audit_record(res, handoff_ledger, final_receipt)
    
    status = "MULTI_AGENT_LIVE_WORK_ROUTER_PREVIEW_ONLY"
    if execute_routed_work:
        if res["routed_live_work_performed"]:
            status = "SUPERVISED_MULTI_AGENT_ROUTED_WORK_COMPLETED"
        else:
            status = "SUPERVISED_MULTI_AGENT_ROUTED_WORK_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
        "multi_agent_live_work_status": status,
        "multi_agent_live_work_router_created": True,
        "live_agent_squad_registry_created": True,
        "agent_role_count": 6,
        "supervised_live_task_packet_created": True,
        "agent_assignment_matrix_created": True,
        "live_work_routing_decision_created": True,
        "supervised_dispatch_plan_created": True,
        "agent_handoff_receipt_ledger_created": True,
        "handoff_receipt_count": 6,
        "final_routed_work_receipt_created": True,
        "routed_live_work_performed": res["routed_live_work_performed"],
        "supervised_dispatch_performed": res["supervised_dispatch_performed"],
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "wrapped_v18_controlled_adapter_execution_performed": res["wrapped_v18_controlled_adapter_execution_performed"],
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
        "v19_1_created": False,
        "v20_created": False,
        
        "schema": schema,
        "live_agent_squad_registry": squad_registry,
        "supervised_live_task_packet": res["task_packet"],
        "agent_assignment_matrix": res["assignment_matrix"],
        "live_work_routing_decision": res["routing_decision"],
        "supervised_dispatch_plan": res["dispatch_plan"],
        "routed_work_human_approval_receipt": res["approval_receipt"],
        "routed_controlled_adapter_work": res,
        "agent_handoff_receipt_ledger": handoff_ledger,
        "final_routed_work_receipt": final_receipt,
        "multi_agent_live_work_audit_record": audit,
        "multi_agent_live_work_safety_boundary_matrix": boundaries,
        "multi_agent_live_work_summary": {
            "version": STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION,
            "status": status
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
