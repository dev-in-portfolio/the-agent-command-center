import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION = "17.0.0"
STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_STATUS = "STATION_CHIEF_V17_HUMAN_GATED_CONTROLLED_LIVE_ACTION_LAYER"
STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_PHASE = "Station Chief v17.0 Human-Gated Live Activation Protocol / Controlled First Real Action Layer"

STATION_CHIEF_V17_APPROVAL_PHRASE = "I_APPROVE_V17_READ_ONLY_REPO_INTEGRITY_INSPECTION"

STATION_CHIEF_V17_CONTROLLED_ACTION_ID = "station-chief-v17-controlled-local-repo-readonly-integrity-inspection-001"

STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS = [
    ".github/workflows/station-chief-validation.yml",
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_release_lock.py",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_v17_live_activation_protocol.py",
    "scripts/validate_station_chief_runtime_v17_0.py",
    "09_exports/station_chief_runtime_v17_0_report.md"
]

STATION_CHIEF_V17_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v17.1 or broader live action expansion requires explicit separate operator instruction"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()

def create_live_activation_protocol_schema() -> dict:
    return {
        "protocol_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "protocol_type": "human_gated_live_activation_protocol",
        "live_working_bridge_created": True,
        "controlled_live_action_layer_created": True,
        "human_approval_required": True,
        "explicit_approval_phrase_required": True,
        "uncontrolled_activation_allowed": False,
        "autonomous_self_activation_allowed": False,
        "broader_live_action_expansion_allowed": False,
        "production_execution_allowed": False,
        "deployment_allowed": False,
        "external_tool_invocation_allowed": False,
        "api_call_allowed": False,
        "network_access_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False
    }

def create_controlled_live_action_taxonomy() -> dict:
    return {
        "taxonomy_id": "station-chief-v17-controlled-live-action-taxonomy",
        "action_classes": {
            "metadata_only_action": {
                "action_class": "metadata_only_action",
                "action_status": "LOCKED",
                "executable_in_v17": False,
                "human_approval_required": True,
                "preview_required": True,
                "receipt_required": True,
                "rollback_required": False,
                "mutation_allowed": False,
                "production_allowed": False,
                "network_allowed": False,
                "credentials_allowed": False
            },
            "controlled_readonly_repo_inspection": {
                "action_class": "controlled_readonly_repo_inspection",
                "action_status": "ACTIVE_V17",
                "executable_in_v17": True,
                "human_approval_required": True,
                "preview_required": True,
                "receipt_required": True,
                "rollback_required": False,
                "mutation_allowed": False,
                "production_allowed": False,
                "network_allowed": False,
                "credentials_allowed": False
            },
            "future_controlled_tool_action": {
                "action_class": "future_controlled_tool_action",
                "action_status": "LOCKED",
                "executable_in_v17": False,
                "human_approval_required": True,
                "preview_required": True,
                "receipt_required": True,
                "rollback_required": True,
                "mutation_allowed": True,
                "production_allowed": False,
                "network_allowed": False,
                "credentials_allowed": False
            },
            "future_controlled_mutation_action": {
                "action_class": "future_controlled_mutation_action",
                "action_status": "LOCKED",
                "executable_in_v17": False,
                "human_approval_required": True,
                "preview_required": True,
                "receipt_required": True,
                "rollback_required": True,
                "mutation_allowed": True,
                "production_allowed": True,
                "network_allowed": True,
                "credentials_allowed": True
            }
        }
    }

def create_first_live_action_allowlist() -> dict:
    return {
        "allowlist_id": sha256_digest(STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS),
        "allowlist_type": "controlled_local_repo_readonly_integrity_inspection_allowlist",
        "allowed_action_id": STATION_CHIEF_V17_CONTROLLED_ACTION_ID,
        "allowed_action_name": "controlled_local_repo_readonly_integrity_inspection",
        "allowed_repo_paths": STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS,
        "allowed_path_count": len(STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS),
        "read_only_file_access_allowed": True,
        "file_content_hashing_allowed": True,
        "file_byte_count_allowed": True,
        "file_line_count_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "directory_scan_allowed": False,
        "glob_allowed": False,
        "rglob_allowed": False,
        "path_escape_allowed": False,
        "credential_path_access_allowed": False,
        "secret_path_access_allowed": False,
        "production_path_access_allowed": False
    }

def create_live_action_preview_packet(action_id: str | None = None) -> dict:
    return {
        "preview_packet_id": sha256_digest({"action_id": action_id or STATION_CHIEF_V17_CONTROLLED_ACTION_ID, "version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION}),
        "preview_type": "controlled_live_action_preview_packet",
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "action_id": action_id or STATION_CHIEF_V17_CONTROLLED_ACTION_ID,
        "action_name": "controlled_local_repo_readonly_integrity_inspection",
        "action_class": "controlled_readonly_repo_inspection",
        "action_summary": "Read explicitly allowlisted repository files, compute hashes and counts, and return a JSON receipt without mutation.",
        "human_approval_required": True,
        "exact_approval_phrase_required": STATION_CHIEF_V17_APPROVAL_PHRASE,
        "mutation_expected": False,
        "production_expected": False,
        "credential_access_expected": False,
        "network_access_expected": False,
        "api_call_expected": False,
        "deployment_expected": False,
        "rollback_required": False,
        "abort_available": True,
        "preview_status": "READY_FOR_HUMAN_APPROVAL"
    }

def create_human_approval_receipt(approval_phrase: str | None, operator_label: str | None = None) -> dict:
    phrase_received = approval_phrase is not None
    phrase_matches = approval_phrase == STATION_CHIEF_V17_APPROVAL_PHRASE
    approval_granted = phrase_matches
    
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "op": operator_label}),
        "receipt_type": "human_approval_receipt",
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "operator_label": normalize_label(operator_label, "unknown_operator"),
        "approval_phrase_received": phrase_received,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V17_APPROVAL_PHRASE,
        "human_approval_granted": approval_granted,
        "autonomous_self_approval": False,
        "approval_phrase_used": approval_phrase if phrase_matches else None,
        "approval_scope": "controlled_local_repo_readonly_integrity_inspection_only",
        "approval_does_not_authorize_mutation": True,
        "approval_does_not_authorize_network": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_production": True,
        "approval_does_not_authorize_broader_live_work": True
    }

def resolve_repo_root(anchor_path: Path | None = None) -> Path:
    anchor = anchor_path or Path(__file__)
    # anchor is in 10_runtime/
    return anchor.resolve().parent.parent

def validate_allowlisted_repo_path(relative_path: str, repo_root: Path, allowlist: dict) -> dict:
    is_valid = True
    reason = "Valid allowlisted path"
    
    if relative_path not in allowlist["allowed_repo_paths"]:
        is_valid = False
        reason = "Path not in allowlist"
    
    if ".." in relative_path or relative_path.startswith("/"):
        is_valid = False
        reason = "Path traversal or absolute path detected"
        
    resolved_path = (repo_root / relative_path).resolve()
    if not str(resolved_path).startswith(str(repo_root.resolve())):
        is_valid = False
        reason = "Path escaped repository root"
        
    if not resolved_path.exists():
        is_valid = False
        reason = "File does not exist"
        
    if not resolved_path.is_file():
        is_valid = False
        reason = "Path is not a file"
        
    return {
        "relative_path": relative_path,
        "is_valid": is_valid,
        "reason": reason,
        "resolved_path": str(resolved_path) if is_valid else None
    }

def execute_controlled_readonly_repo_integrity_inspection(approval_phrase: str | None, operator_label: str | None = None) -> dict:
    approval_receipt = create_human_approval_receipt(approval_phrase, operator_label)
    allowlist = create_first_live_action_allowlist()
    preview = create_live_action_preview_packet()
    repo_root = resolve_repo_root()
    
    inspected_files = []
    live_action_performed = False
    real_file_read_performed = False
    
    if approval_receipt["human_approval_granted"]:
        live_action_performed = True
        real_file_read_performed = True
        for rel_path in STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS:
            validation = validate_allowlisted_repo_path(rel_path, repo_root, allowlist)
            if validation["is_valid"]:
                file_path = repo_root / rel_path
                content_bytes = file_path.read_bytes()
                inspected_files.append({
                    "relative_path": rel_path,
                    "exists": True,
                    "read_performed": True,
                    "sha256": hashlib.sha256(content_bytes).hexdigest(),
                    "byte_count": len(content_bytes),
                    "line_count": len(content_bytes.splitlines()),
                    "content_printed": False,
                    "mutation_performed": False,
                    "credential_access_performed": False,
                    "secret_access_performed": False,
                    "environment_read_performed": False,
                    "network_access_performed": False,
                    "api_call_performed": False
                })
            else:
                inspected_files.append({
                    "relative_path": rel_path,
                    "exists": False,
                    "read_performed": False,
                    "error": validation["reason"]
                })
                
    return {
        "execution_status": "LIVE_READONLY_INSPECTION_COMPLETED" if live_action_performed else "LIVE_READONLY_INSPECTION_DENIED",
        "live_action_performed": live_action_performed,
        "real_file_read_performed": real_file_read_performed,
        "human_approval_granted": approval_receipt["human_approval_granted"],
        "approval_receipt": approval_receipt,
        "allowlist": allowlist,
        "preview": preview,
        "allowed_file_count": len(STATION_CHIEF_V17_ALLOWED_READONLY_REPO_PATHS),
        "inspected_file_count": len(inspected_files),
        "inspected_files": inspected_files,
        "mutation_performed": False,
        "production_execution_performed": False,
        "deployment_performed": False,
        "credential_access_performed": False,
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

def create_live_action_receipt(inspection_result: dict) -> dict:
    files_digest = sha256_digest(inspection_result["inspected_files"]) if inspection_result["live_action_performed"] else None
    
    return {
        "live_action_receipt_id": sha256_digest(inspection_result),
        "receipt_type": "controlled_live_action_receipt",
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "action_id": STATION_CHIEF_V17_CONTROLLED_ACTION_ID,
        "action_name": "controlled_local_repo_readonly_integrity_inspection",
        "live_action_performed": inspection_result["live_action_performed"],
        "approval_granted": inspection_result["human_approval_granted"],
        "inspected_file_count": inspection_result["inspected_file_count"],
        "inspected_file_digest_summary": files_digest,
        "receipt_status": "CONTROLLED_LIVE_READONLY_ACTION_COMPLETED" if inspection_result["live_action_performed"] else "CONTROLLED_LIVE_READONLY_ACTION_DENIED",
        "no_mutation": True,
        "no_production_execution": True,
        "no_deployment": True,
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

def create_emergency_abort_denial_gate() -> dict:
    return {
        "abort_gate_id": sha256_digest("emergency_abort_denial_gate"),
        "gate_type": "v17_emergency_abort_denial_gate",
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "abort_available": True,
        "abort_required_for_future_mutation_actions": True,
        "current_action_readonly": True,
        "rollback_required_for_current_action": False,
        "mutation_actions_denied": True,
        "production_actions_denied": True,
        "external_actions_denied": True,
        "credential_actions_denied": True,
        "network_actions_denied": True,
        "broader_live_actions_denied": True
    }

def create_live_activation_audit_record(inspection_result: dict, live_action_receipt: dict, abort_gate: dict) -> dict:
    return {
        "audit_id": sha256_digest({"inspection": inspection_result, "receipt": live_action_receipt, "abort": abort_gate}),
        "audit_type": "v17_human_gated_live_activation_audit",
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "live_working_bridge_created": True,
        "controlled_live_action_layer_created": True,
        "first_real_action_class": "controlled_local_repo_readonly_integrity_inspection",
        "live_action_performed": live_action_receipt["live_action_performed"],
        "real_file_read_performed": inspection_result["real_file_read_performed"],
        "inspected_file_count": inspection_result["inspected_file_count"],
        "human_approval_required": True,
        "human_approval_granted": inspection_result["human_approval_granted"],
        "no_file_contents_printed": True,
        "no_file_mutation": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_rollback_execution": True,
        "no_recovery_execution": True,
        "no_real_tool_invocation": True,
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

def create_live_activation_safety_boundary_matrix() -> dict:
    return {
        "controlled_local_repo_readonly_integrity_inspection": "ALLOWED",
        "allowlisted_file_read": "ALLOWED",
        "allowlisted_file_sha256": "ALLOWED",
        "allowlisted_file_byte_count": "ALLOWED",
        "allowlisted_file_line_count": "ALLOWED",
        "json_receipt_output": "ALLOWED",
        
        "uncontrolled_live_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
        "production_execution": "DENIED",
        "production_mutation": "DENIED",
        "deployment": "DENIED",
        "deployment_rollback": "DENIED",
        "rollback_execution": "DENIED",
        "recovery_execution": "DENIED",
        "real_tool_invocation": "DENIED",
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
        "v17_1_creation": "DENIED",
        "v18_creation": "DENIED"
    }

def create_station_chief_v17_live_activation_protocol_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "schema_type": "station_chief_v17_human_gated_live_activation_protocol",
        "required_sections": [
            "live_activation_protocol_schema",
            "controlled_live_action_taxonomy",
            "first_live_action_allowlist",
            "live_action_preview_packet",
            "human_approval_receipt",
            "controlled_readonly_repo_integrity_inspection",
            "live_action_receipt",
            "emergency_abort_denial_gate",
            "live_activation_audit_record",
            "live_activation_safety_boundary_matrix",
            "live_activation_summary"
        ],
        "live_working_bridge_authorized": True,
        "controlled_read_only_repo_inspection_authorized": True,
        "human_approval_required": True,
        "no_uncontrolled_activation_authorized": True,
        "no_autonomous_self_activation_authorized": True,
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
        "v17_1_created": False,
        "v18_created": False
    }

def create_station_chief_v17_live_activation_protocol_bundle(approval_phrase: str | None = None, operator_label: str | None = None, execute_live_readonly_inspection: bool = False) -> dict:
    schema = create_station_chief_v17_live_activation_protocol_schema()
    protocol_schema = create_live_activation_protocol_schema()
    taxonomy = create_controlled_live_action_taxonomy()
    allowlist = create_first_live_action_allowlist()
    preview = create_live_action_preview_packet()
    abort_gate = create_emergency_abort_denial_gate()
    boundaries = create_live_activation_safety_boundary_matrix()
    
    if execute_live_readonly_inspection:
        inspection = execute_controlled_readonly_repo_integrity_inspection(approval_phrase, operator_label)
    else:
        # Denied/Preview only metadata
        approval_receipt = create_human_approval_receipt(approval_phrase, operator_label)
        inspection = {
            "execution_status": "LIVE_READONLY_INSPECTION_NOT_EXECUTED",
            "live_action_performed": False,
            "real_file_read_performed": False,
            "human_approval_granted": approval_receipt["human_approval_granted"],
            "approval_receipt": approval_receipt,
            "allowlist": allowlist,
            "preview": preview,
            "allowed_file_count": 7,
            "inspected_file_count": 0,
            "inspected_files": []
        }
        
    receipt = create_live_action_receipt(inspection)
    audit = create_live_activation_audit_record(inspection, receipt, abort_gate)
    
    status = "HUMAN_GATED_LIVE_ACTION_PREVIEW_ONLY"
    if execute_live_readonly_inspection:
        if inspection["live_action_performed"]:
            status = "HUMAN_GATED_LIVE_READONLY_ACTION_COMPLETED"
        else:
            status = "HUMAN_GATED_LIVE_ACTION_DENIED"

    bundle = {
        "runtime_version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
        "live_activation_status": status,
        "live_working_bridge_created": True,
        "controlled_live_action_layer_created": True,
        "first_real_action_class_created": True,
        "first_real_action_class": "controlled_local_repo_readonly_integrity_inspection",
        "human_approval_required": True,
        "approval_phrase_required": True,
        "live_action_performed": inspection["live_action_performed"],
        "real_file_read_performed": inspection["real_file_read_performed"],
        "allowed_file_count": 7,
        "inspected_file_count": inspection["inspected_file_count"],
        "file_contents_printed": False,
        "file_mutation_performed": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "rollback_execution_performed": False,
        "recovery_execution_performed": False,
        "real_tool_invocation_performed": False,
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
        "v17_1_created": False,
        "v18_created": False,
        
        "schema": schema,
        "live_activation_protocol_schema": protocol_schema,
        "controlled_live_action_taxonomy": taxonomy,
        "first_live_action_allowlist": allowlist,
        "live_action_preview_packet": preview,
        "human_approval_receipt": inspection["approval_receipt"],
        "controlled_readonly_repo_integrity_inspection": inspection,
        "live_action_receipt": receipt,
        "emergency_abort_denial_gate": abort_gate,
        "live_activation_audit_record": audit,
        "live_activation_safety_boundary_matrix": boundaries,
        "live_activation_summary": {
            "version": STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION,
            "status": status
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
