#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION = "4.6.0"
NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_STATUS = "NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_LOCAL_RECORD_ONLY"
NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_PHASE = "Non-Executing Task Queue Preview Candidate"
NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE"
DEFAULT_QUEUE_PREVIEW_LABEL = "non-executing-task-queue-preview-candidate"
DEFAULT_QUEUE_PREVIEW_RECORD_NAME = "non_executing_task_queue_preview_candidate_record.json"
EXPECTED_V4_4_ASSIGNMENT_RECORD_NAME = "permissioned_worker_task_assignment_candidate_record.json"
EXPECTED_V4_5_CLOSEOUT_RECORD_NAME = "task_assignment_audit_closeout_candidate_record.json"

DANGEROUS_BOOLEAN_FIELDS = [
    "external_actions_taken",
    "live_external_action_performed",
    "live_api_call_performed",
    "network_access_performed",
    "socket_opened",
    "dns_resolution_performed",
    "outbound_connection_performed",
    "inbound_connection_performed",
    "webhook_call_performed",
    "credential_vault_access_performed",
    "credentials_used",
    "secrets_read",
    "environment_read",
    "tokens_read",
    "api_keys_read",
    "oauth_used",
    "service_account_used",
    "deployment_performed",
    "deployment_rollback_performed",
    "production_execution_performed",
    "production_activation_performed",
    "real_external_tool_invocation_performed",
    "real_task_execution_performed",
    "queue_created",
    "queue_write_performed",
    "scheduler_write_performed",
    "cron_write_performed",
    "queue_item_created",
    "queue_item_queued",
    "task_executed",
    "task_enqueued",
    "live_task_assignment_performed",
    "live_worker_routing_performed",
    "live_orchestration_performed",
    "worker_process_started",
    "worker_processes_started",
    "real_rollback_performed",
    "real_recovery_performed",
    "processes_terminated",
    "workers_terminated",
    "production_state_changed",
    "repo_files_modified",
    "execution_authorized",
    "full_workforce_activation_performed",
    "referenced_task_assignment_record_mutated",
    "referenced_closeout_record_mutated",
]


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _false_booleans() -> dict:
    return {name: False for name in DANGEROUS_BOOLEAN_FIELDS}


def _iter_nested_values(data):
    if isinstance(data, dict):
        for key, value in data.items():
            yield key, value
            yield from _iter_nested_values(value)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_nested_values(item)
    elif isinstance(data, tuple):
        for item in data:
            yield from _iter_nested_values(item)


def _path_contains(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def normalize_label(label: str, default: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", str(label).strip().lower()).strip("-")
    return normalized or default


def safe_queue_preview_record_name(record_name: str | None) -> str:
    if not record_name:
        return DEFAULT_QUEUE_PREVIEW_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_QUEUE_PREVIEW_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_QUEUE_PREVIEW_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_QUEUE_PREVIEW_RECORD_NAME
    return record_name


def generate_non_executing_task_queue_preview_candidate_id(
    command: str,
    queue_preview_label: str,
    runtime_version: str = NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_queue_preview = normalize_label(queue_preview_label, DEFAULT_QUEUE_PREVIEW_LABEL)
    digest = sha256_digest(f"{runtime_version}:{command}:{queue_preview_label}")
    return f"non-executing-task-queue-preview-candidate-v4-6-{normalized_queue_preview}-{digest[:12]}"


def create_non_executing_task_queue_preview_candidate_schema() -> dict:
    return {
        "non_executing_task_queue_preview_candidate_schema_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "schema_status": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_STATUS,
        "queue_preview_type": "local_non_executing_task_queue_preview_record",
        "required_sections": [
            "non_executing_task_queue_preview_candidate_approval_gate",
            "v4_4_task_assignment_record_reference_contract",
            "optional_v4_5_closeout_record_reference_contract",
            "task_assignment_record_integrity_verification",
            "closeout_record_integrity_verification",
            "task_assignment_record_path_containment_review",
            "queue_preview_scope_contract",
            "non_execution_queue_boundary",
            "queue_permission_denial_record",
            "local_queue_preview_candidate_record",
            "queue_preview_audit_record",
            "queue_preview_ledger",
            "queue_preview_readiness_summary",
            "task_queue_preview_audit_closeout_candidate_bridge",
        ],
        "required_confirmation_token": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_queue_preview_record_written": False,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "worker_process_started": False,
        "live_worker_routing_performed": False,
        "live_task_assignment_performed": False,
        **_false_booleans(),
    }


def create_non_executing_task_queue_preview_candidate_approval_gate(
    queue_preview_label: str,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_record_path: str | None = None,
    queue_preview_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_preview_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_APPROVAL_TOKEN
    queue_preview_label_present = bool(queue_preview_label and str(queue_preview_label).strip())
    task_assignment_present = bool(task_assignment_record_path and str(task_assignment_record_path).strip())
    expected_output_present = bool(expected_task_assignment_output_directory and str(expected_task_assignment_output_directory).strip())
    closeout_record_present = bool(closeout_record_path and str(closeout_record_path).strip())
    queue_preview_output_present = bool(queue_preview_output_directory and str(queue_preview_output_directory).strip())
    human_present = bool(human_operator and str(human_operator).strip())
    local_queue_preview_records_authorized = token_valid and human_present and task_assignment_present
    local_queue_preview_record_write_authorized = (
        token_valid
        and human_present
        and task_assignment_present
        and queue_preview_output_present
        and bool(queue_preview_requested)
    )
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_NON_EXECUTING_QUEUE_PREVIEW_RECORD"
        if local_queue_preview_records_authorized
        else "BLOCKED_PENDING_V4_6_QUEUE_PREVIEW_APPROVAL"
    )
    return {
        "non_executing_task_queue_preview_candidate_approval_gate_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "queue_preview_label": queue_preview_label,
        "queue_preview_label_normalized": normalize_label(queue_preview_label, DEFAULT_QUEUE_PREVIEW_LABEL),
        "task_assignment_record_path": task_assignment_record_path,
        "task_assignment_record_path_present": task_assignment_present,
        "expected_task_assignment_output_directory": expected_task_assignment_output_directory,
        "expected_task_assignment_output_directory_present": expected_output_present,
        "closeout_record_path": closeout_record_path,
        "closeout_record_path_present": closeout_record_present,
        "queue_preview_output_directory": queue_preview_output_directory,
        "human_operator": human_operator,
        "queue_preview_requested": bool(queue_preview_requested),
        "gate_status": gate_status,
        "confirmation_token_required": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "queue_preview_label_present": queue_preview_label_present,
        "human_operator_present": human_present,
        "local_queue_preview_records_authorized": local_queue_preview_records_authorized,
        "local_queue_preview_record_write_authorized": local_queue_preview_record_write_authorized,
        "queue_creation_authorized": False,
        "queue_write_authorized": False,
        "scheduler_write_authorized": False,
        "cron_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "full_workforce_activation_authorized": False,
        "baseline_preserved": True,
        "local_queue_preview_record_written": False,
        **_false_booleans(),
    }


def create_v4_4_task_assignment_record_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_queue_preview_records_authorized", False)
    record_path = approval_gate.get("task_assignment_record_path")
    return {
        "v4_4_task_assignment_record_reference_contract_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "contract_status": "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "task_assignment_record_path": record_path,
        "task_assignment_record_name": Path(record_path).name if record_path else None,
        "referenced_task_assignment_record_name": EXPECTED_V4_4_ASSIGNMENT_RECORD_NAME,
        "referenced_task_assignment_record_is_v4_4_local_record_only": True,
        "does_not_mutate_referenced_record": True,
        "does_not_execute_task": True,
        "does_not_enqueue_task": True,
        "does_not_create_queue": True,
        "does_not_route_worker": True,
        "worker_process_started": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_optional_v4_5_closeout_record_reference_contract(approval_gate: dict) -> dict:
    closeout_path = approval_gate.get("closeout_record_path")
    closeout_present = bool(closeout_path and str(closeout_path).strip())
    if not closeout_present:
        return {
            "optional_v4_5_closeout_record_reference_contract_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
            "contract_status": "OPTIONAL_CLOSEOUT_RECORD_NOT_PROVIDED",
            "closeout_record_required": False,
            "closeout_record_present": False,
            "closeout_record_path": None,
            "referenced_closeout_record_name": EXPECTED_V4_5_CLOSEOUT_RECORD_NAME,
            "does_not_mutate_referenced_record": True,
            "execution_authorized": False,
            "baseline_preserved": True,
            **_false_booleans(),
        }
    authorized = approval_gate.get("local_queue_preview_records_authorized", False)
    return {
        "optional_v4_5_closeout_record_reference_contract_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "contract_status": "CLOSEOUT_RECORD_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "closeout_record_required": True,
        "closeout_record_present": True,
        "closeout_record_path": closeout_path,
        "closeout_record_name": Path(closeout_path).name,
        "referenced_closeout_record_name": EXPECTED_V4_5_CLOSEOUT_RECORD_NAME,
        "does_not_mutate_referenced_record": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_assignment_record_integrity_verification(task_assignment_record_path: str | None) -> dict:
    if not task_assignment_record_path:
        return {
            "task_assignment_record_integrity_verification_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
            "verification_status": "BLOCKED",
            "task_assignment_record_path_present": False,
            "record_exists": False,
            "record_is_file": False,
            "record_name_valid": False,
            "json_parse_valid": False,
            "runtime_version_valid": False,
            "assignment_type_valid": False,
            "payload_digest_present": False,
            "payload_digest_valid": False,
            "parsed_record_digest": None,
            "parsed_record_data": None,
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }
    record_path = Path(task_assignment_record_path).expanduser().resolve()
    record_exists = record_path.exists()
    record_is_file = record_path.is_file()
    record_name_valid = record_path.name == EXPECTED_V4_4_ASSIGNMENT_RECORD_NAME and record_path.suffix == ".json"
    json_parse_valid = False
    runtime_version_valid = False
    assignment_type_valid = False
    payload_digest_present = False
    payload_digest_valid = False
    parsed_record = None
    if record_exists and record_is_file and record_name_valid:
        try:
            parsed_record = json.loads(record_path.read_text(encoding="utf-8"))
            json_parse_valid = True
        except Exception:
            parsed_record = None
    parsed_record_digest = sha256_digest(parsed_record) if isinstance(parsed_record, dict) else None
    if isinstance(parsed_record, dict):
        runtime_version_valid = parsed_record.get("runtime_version") in (None, "4.4.0")
        assignment_type_valid = parsed_record.get("assignment_type") in (None, "permissioned_local_worker_task_assignment_record")
        if "payload_digest" in parsed_record:
            payload_digest_present = True
            payload_copy = dict(parsed_record)
            recorded_digest = payload_copy.pop("payload_digest")
            payload_digest_valid = recorded_digest == sha256_digest(payload_copy)
    verification_status = (
        "PASS"
        if record_exists
        and record_is_file
        and record_name_valid
        and json_parse_valid
        and runtime_version_valid
        and assignment_type_valid
        and (not payload_digest_present or payload_digest_valid)
        else "BLOCKED"
    )
    return {
        "task_assignment_record_integrity_verification_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "verification_status": verification_status,
        "task_assignment_record_path_present": True,
        "record_path_resolved": str(record_path),
        "record_exists": record_exists,
        "record_is_file": record_is_file,
        "record_name_valid": record_name_valid,
        "json_parse_valid": json_parse_valid,
        "runtime_version_valid": runtime_version_valid,
        "assignment_type_valid": assignment_type_valid,
        "payload_digest_present": payload_digest_present,
        "payload_digest_valid": payload_digest_valid,
        "parsed_record_digest": parsed_record_digest,
        "parsed_record_data": parsed_record,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_closeout_record_integrity_verification(closeout_record_path: str | None) -> dict:
    if not closeout_record_path:
        return {
            "closeout_record_integrity_verification_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
            "verification_status": "OPTIONAL_CLOSEOUT_RECORD_NOT_PROVIDED",
            "closeout_record_required": False,
            "closeout_record_path_present": False,
            "record_exists": False,
            "record_is_file": False,
            "record_name_valid": False,
            "json_parse_valid": False,
            "runtime_version_valid": False,
            "closeout_type_valid": False,
            "payload_digest_present": False,
            "payload_digest_valid": False,
            "parsed_closeout_record_digest": None,
            "parsed_closeout_record_data": None,
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }
    record_path = Path(closeout_record_path).expanduser().resolve()
    record_exists = record_path.exists()
    record_is_file = record_path.is_file()
    record_name_valid = record_path.name == EXPECTED_V4_5_CLOSEOUT_RECORD_NAME and record_path.suffix == ".json"
    json_parse_valid = False
    runtime_version_valid = False
    closeout_type_valid = False
    payload_digest_present = False
    payload_digest_valid = False
    parsed_closeout_record = None
    if record_exists and record_is_file and record_name_valid:
        try:
            parsed_closeout_record = json.loads(record_path.read_text(encoding="utf-8"))
            json_parse_valid = True
        except Exception:
            parsed_closeout_record = None
    parsed_closeout_record_digest = sha256_digest(parsed_closeout_record) if isinstance(parsed_closeout_record, dict) else None
    if isinstance(parsed_closeout_record, dict):
        runtime_version_valid = parsed_closeout_record.get("runtime_version") in (None, "4.5.0")
        closeout_type_valid = parsed_closeout_record.get("closeout_type") in (None, "local_task_assignment_audit_closeout_record")
        if "payload_digest" in parsed_closeout_record:
            payload_digest_present = True
            payload_copy = dict(parsed_closeout_record)
            recorded_digest = payload_copy.pop("payload_digest")
            payload_digest_valid = recorded_digest == sha256_digest(payload_copy)
    verification_status = (
        "PASS"
        if record_exists
        and record_is_file
        and record_name_valid
        and json_parse_valid
        and runtime_version_valid
        and closeout_type_valid
        and (not payload_digest_present or payload_digest_valid)
        else "BLOCKED"
    )
    return {
        "closeout_record_integrity_verification_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "verification_status": verification_status,
        "closeout_record_required": True,
        "closeout_record_path_present": True,
        "record_path_resolved": str(record_path),
        "record_exists": record_exists,
        "record_is_file": record_is_file,
        "record_name_valid": record_name_valid,
        "json_parse_valid": json_parse_valid,
        "runtime_version_valid": runtime_version_valid,
        "closeout_type_valid": closeout_type_valid,
        "payload_digest_present": payload_digest_present,
        "payload_digest_valid": payload_digest_valid,
        "parsed_closeout_record_digest": parsed_closeout_record_digest,
        "parsed_closeout_record_data": parsed_closeout_record,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_task_assignment_record_path_containment_review(
    task_assignment_record_path: str | None,
    expected_task_assignment_output_directory: str | None = None,
) -> dict:
    if not task_assignment_record_path:
        return {
            "task_assignment_record_path_containment_review_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
            "containment_status": "BLOCKED",
            "containment_passed": False,
            "task_assignment_record_path_present": False,
            "expected_task_assignment_output_directory_present": bool(expected_task_assignment_output_directory),
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }
    record_path = Path(task_assignment_record_path).expanduser().resolve()
    expected_dir_present = bool(expected_task_assignment_output_directory and str(expected_task_assignment_output_directory).strip())
    if not expected_dir_present:
        return {
            "task_assignment_record_path_containment_review_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
            "containment_status": "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY",
            "containment_passed": False,
            "task_assignment_record_path_present": True,
            "record_path_resolved": str(record_path),
            "expected_task_assignment_output_directory_present": False,
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }
    expected_dir = Path(expected_task_assignment_output_directory).expanduser().resolve()
    contained = _path_contains(record_path, expected_dir)
    return {
        "task_assignment_record_path_containment_review_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "containment_status": "PASS" if contained else "BLOCKED",
        "containment_passed": contained,
        "task_assignment_record_path_present": True,
        "record_path_resolved": str(record_path),
        "expected_task_assignment_output_directory": str(expected_dir),
        "expected_task_assignment_output_directory_present": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_queue_preview_scope_contract(
    approval_gate: dict,
    task_assignment_reference_contract: dict,
    task_assignment_integrity_verification: dict,
    task_assignment_path_containment_review: dict,
) -> dict:
    containment_status = task_assignment_path_containment_review.get("containment_status")
    scope_pass = (
        approval_gate.get("local_queue_preview_records_authorized", False)
        and task_assignment_reference_contract.get("contract_status") == "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED"
        and task_assignment_integrity_verification.get("verification_status") == "PASS"
        and containment_status == "PASS"
    )
    scope_status = "PASS" if scope_pass else (
        "BLOCKED_PENDING_EXPECTED_OUTPUT_DIRECTORY" if containment_status == "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY" else "BLOCKED"
    )
    return {
        "queue_preview_scope_contract_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "scope_status": scope_status,
        "exactly_one_task_assignment_record": True,
        "queue_preview_only": True,
        "optional_closeout_record_supported": True,
        "containment_requires_expected_output_directory": containment_status == "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY",
        "no_real_queue_creation": True,
        "no_queue_write": True,
        "no_scheduler_write": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_worker_process_start": True,
        "no_live_worker_routing": True,
        "no_full_workforce_activation": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_execution_queue_boundary(
    approval_gate: dict,
    queue_preview_scope_contract: dict,
) -> dict:
    pass_ok = (
        approval_gate.get("local_queue_preview_records_authorized", False)
        and queue_preview_scope_contract.get("scope_status") == "PASS"
    )
    return {
        "non_execution_queue_boundary_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "boundary_status": "PASS" if pass_ok else "BLOCKED",
        "queue_preview_record_is_local_metadata_only": True,
        "queue_preview_is_not_executable": True,
        "queue_preview_is_not_queued": True,
        "queue_preview_is_not_real_queue": True,
        "queue_item_is_not_created": True,
        "task_is_not_enqueued": True,
        "task_is_not_executed": True,
        "worker_is_not_running": True,
        "worker_cannot_call_tools": True,
        "worker_cannot_route_tasks": True,
        "worker_cannot_access_apis": True,
        "worker_cannot_access_network": True,
        "worker_cannot_access_credentials_secrets_environment": True,
        "worker_cannot_deploy": True,
        "worker_cannot_execute_production": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_queue_permission_denial_record(queue_preview_label: str) -> dict:
    return {
        "queue_permission_denial_record_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "queue_preview_label": queue_preview_label,
        "queue_creation_denied": True,
        "queue_write_denied": True,
        "queue_item_creation_denied": True,
        "scheduler_write_denied": True,
        "cron_write_denied": True,
        "task_enqueue_denied": True,
        "task_execution_denied": True,
        "live_task_assignment_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "worker_process_start_denied": True,
        "api_access_denied": True,
        "network_access_denied": True,
        "socket_access_denied": True,
        "dns_resolution_denied": True,
        "credential_use_denied": True,
        "credential_vault_access_denied": True,
        "secret_reads_denied": True,
        "environment_reads_denied": True,
        "deployment_denied": True,
        "production_execution_denied": True,
        "production_activation_denied": True,
        "github_push_denied": True,
        "external_tool_invocation_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_local_queue_preview_candidate_record(
    command: str,
    approval_gate: dict,
    task_assignment_reference_contract: dict,
    optional_closeout_reference_contract: dict,
    task_assignment_integrity_verification: dict,
    closeout_integrity_verification: dict,
    queue_preview_scope_contract: dict,
    non_execution_queue_boundary: dict,
    queue_permission_denial_record: dict,
) -> dict:
    queue_preview_label = approval_gate.get("queue_preview_label") or DEFAULT_QUEUE_PREVIEW_LABEL
    queue_preview_candidate_id = generate_non_executing_task_queue_preview_candidate_id(command, queue_preview_label)
    candidate_ok = (
        approval_gate.get("local_queue_preview_records_authorized", False)
        and task_assignment_reference_contract.get("contract_status") == "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED"
        and task_assignment_integrity_verification.get("verification_status") == "PASS"
        and queue_preview_scope_contract.get("scope_status") == "PASS"
        and non_execution_queue_boundary.get("boundary_status") == "PASS"
    )
    record = {
        "queue_preview_candidate_id": queue_preview_candidate_id,
        "candidate_status": "LOCAL_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_RECORD_CREATED" if candidate_ok else "BLOCKED",
        "queue_preview_label": queue_preview_label,
        "queue_preview_label_normalized": normalize_label(queue_preview_label, DEFAULT_QUEUE_PREVIEW_LABEL),
        "referenced_task_assignment_record_path": approval_gate.get("task_assignment_record_path"),
        "optional_closeout_record_path": approval_gate.get("closeout_record_path"),
        "human_operator": approval_gate.get("human_operator"),
        "queue_preview_mode": "local_record_only",
        "queue_runtime_state": "not_created",
        "queue_item_state": "not_created",
        "task_runtime_state": "not_started",
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "queue_permission_denial_record": queue_permission_denial_record,
        "queue_preview_scope_contract": queue_preview_scope_contract,
        "non_execution_queue_boundary": non_execution_queue_boundary,
        "task_assignment_record_integrity_verification": task_assignment_integrity_verification,
        "closeout_record_integrity_verification": closeout_integrity_verification,
        "task_assignment_reference_contract": task_assignment_reference_contract,
        "optional_v4_5_closeout_record_reference_contract": optional_closeout_reference_contract,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    record["queue_preview_candidate_digest"] = sha256_digest({k: v for k, v in record.items() if k != "queue_preview_candidate_digest"})
    return record


def create_queue_preview_audit_record(
    approval_gate: dict,
    task_assignment_reference_contract: dict,
    optional_closeout_reference_contract: dict,
    task_assignment_integrity_verification: dict,
    closeout_integrity_verification: dict,
    task_assignment_path_containment_review: dict,
    queue_preview_scope_contract: dict,
    non_execution_queue_boundary: dict,
    queue_permission_denial_record: dict,
    local_queue_preview_candidate_record: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "task_assignment_reference_contract": sha256_digest(task_assignment_reference_contract),
        "optional_closeout_reference_contract": sha256_digest(optional_closeout_reference_contract),
        "task_assignment_integrity_verification": sha256_digest(task_assignment_integrity_verification),
        "closeout_integrity_verification": sha256_digest(closeout_integrity_verification),
        "task_assignment_path_containment_review": sha256_digest(task_assignment_path_containment_review),
        "queue_preview_scope_contract": sha256_digest(queue_preview_scope_contract),
        "non_execution_queue_boundary": sha256_digest(non_execution_queue_boundary),
        "queue_permission_denial_record": sha256_digest(queue_permission_denial_record),
        "local_queue_preview_candidate_record": sha256_digest(local_queue_preview_candidate_record),
    }
    audit_ok = (
        local_queue_preview_candidate_record.get("candidate_status") == "LOCAL_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_RECORD_CREATED"
        and queue_preview_scope_contract.get("scope_status") == "PASS"
        and non_execution_queue_boundary.get("boundary_status") == "PASS"
        and not any(local_queue_preview_candidate_record.get(name, False) for name in DANGEROUS_BOOLEAN_FIELDS)
    )
    audit_record = {
        "queue_preview_audit_record_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "section_digests": section_digests,
        "queue_preview_candidate_created": local_queue_preview_candidate_record.get("candidate_status") == "LOCAL_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_RECORD_CREATED",
        "all_dangerous_booleans_false": True,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    audit_record["audit_digest"] = sha256_digest({k: v for k, v in audit_record.items() if k != "audit_digest"})
    return audit_record


def create_queue_preview_ledger(queue_preview_audit_record: dict) -> dict:
    ledger_ok = queue_preview_audit_record.get("audit_status") == "PASS"
    ledger_record = {
        "queue_preview_ledger_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "ledger_status": "PASS" if ledger_ok else "BLOCKED",
        "audit_record_digest": sha256_digest(queue_preview_audit_record),
        "all_dangerous_booleans_false": True,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    ledger_record["ledger_digest"] = sha256_digest({k: v for k, v in ledger_record.items() if k != "ledger_digest"})
    return ledger_record


def create_queue_preview_readiness_summary(queue_preview_ledger: dict) -> dict:
    ready = queue_preview_ledger.get("ledger_status") == "PASS"
    return {
        "queue_preview_readiness_summary_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Task Queue Preview Audit Closeout Candidate",
        "v4_7_built": False,
        "no_real_queue_created": True,
        "no_queue_write_yet": True,
        "no_task_enqueue_yet": True,
        "no_task_execution_yet": True,
        "no_live_task_assignment_yet": True,
        "no_worker_routing_yet": True,
        "no_process_start": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_queue_preview_audit_closeout_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE"
    return {
        "task_queue_preview_audit_closeout_candidate_bridge_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_7_TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE" if ready else "BLOCKED",
        "ready_for_v4_7": ready,
        "no_queue_audit_closeout_in_v4_6": True,
        "no_task_queue_creation_in_v4_6": True,
        "no_task_enqueue_in_v4_6": True,
        "no_task_execution_in_v4_6": True,
        "no_worker_routing_in_v4_6": True,
        "no_worker_process_start_in_v4_6": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def build_non_executing_task_queue_preview_record_payload(
    command: str,
    queue_preview_label: str,
    human_operator: str | None,
    referenced_task_assignment_record_path: str,
    optional_closeout_record_path: str | None,
    approval_gate: dict,
    task_assignment_integrity_verification: dict,
    closeout_integrity_verification: dict,
    queue_permission_denial_record: dict,
    queue_preview_audit_record: dict,
    local_queue_preview_candidate_record: dict,
    queue_preview_scope_contract: dict,
    non_execution_queue_boundary: dict,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "queue_preview_type": "local_non_executing_task_queue_preview_record",
        "queue_preview_label": queue_preview_label,
        "queue_preview_label_normalized": normalize_label(queue_preview_label, DEFAULT_QUEUE_PREVIEW_LABEL),
        "human_operator": human_operator,
        "referenced_task_assignment_record_path": referenced_task_assignment_record_path,
        "optional_closeout_record_path": optional_closeout_record_path,
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "queue_preview_candidate_id": local_queue_preview_candidate_record.get("queue_preview_candidate_id") or generate_non_executing_task_queue_preview_candidate_id(command, queue_preview_label),
        "referenced_task_assignment_record_digest": task_assignment_integrity_verification.get("parsed_record_digest"),
        "optional_closeout_record_digest": closeout_integrity_verification.get("parsed_closeout_record_digest"),
        "queue_permission_denial_record": queue_permission_denial_record,
        "queue_preview_audit_digest": queue_preview_audit_record.get("audit_digest"),
        "queue_preview_scope_contract": queue_preview_scope_contract,
        "non_execution_queue_boundary": non_execution_queue_boundary,
        "task_assignment_record_integrity_verification": task_assignment_integrity_verification,
        "closeout_record_integrity_verification": closeout_integrity_verification,
        "local_queue_preview_candidate_record": local_queue_preview_candidate_record,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "safety_booleans": {
            "queue_created": False,
            "queue_write_performed": False,
            "scheduler_write_performed": False,
            "task_executed": False,
            "task_enqueued": False,
            "worker_process_started": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "full_workforce_activation_performed": False,
            "referenced_task_assignment_record_mutated": False,
            "referenced_closeout_record_mutated": False,
            **_false_booleans(),
        },
        "baseline_preserved": True,
    }
    payload["payload_digest"] = sha256_digest({k: v for k, v in payload.items() if k != "payload_digest"})
    return payload


def write_non_executing_task_queue_preview_record(
    queue_preview_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(queue_preview_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_queue_preview_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    if not _path_contains(record_path, output_dir):
        return create_blocked_queue_preview_write_record("queue preview record path escaped approved output directory")
    record_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "queue_preview_write_record_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "write_status": "LOCAL_NON_EXECUTING_TASK_QUEUE_PREVIEW_RECORD_WRITTEN",
        "local_queue_preview_record_written": True,
        "files_written_count": 1,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "record_name": safe_name,
        "record_path": str(record_path),
        "queue_preview_output_directory": str(output_dir),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_queue_preview_write_record(reason: str) -> dict:
    return {
        "queue_preview_write_record_version": NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "reason": reason,
        "local_queue_preview_record_written": False,
        "files_written_count": 0,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_executing_task_queue_preview_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    queue_preview_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_record_path: str | None = None,
    queue_preview_output_directory: str | None = None,
    queue_preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_preview_requested: bool = False,
    write_queue_preview_record: bool = False,
) -> dict:
    command = command or "check please"
    queue_preview_label = queue_preview_label or DEFAULT_QUEUE_PREVIEW_LABEL
    approval_gate = create_non_executing_task_queue_preview_candidate_approval_gate(
        queue_preview_label=queue_preview_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_record_path=closeout_record_path,
        queue_preview_output_directory=queue_preview_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        queue_preview_requested=queue_preview_requested,
    )
    task_assignment_reference_contract = create_v4_4_task_assignment_record_reference_contract(approval_gate)
    optional_closeout_reference_contract = create_optional_v4_5_closeout_record_reference_contract(approval_gate)
    task_assignment_integrity_verification = create_task_assignment_record_integrity_verification(task_assignment_record_path)
    closeout_integrity_verification = create_closeout_record_integrity_verification(closeout_record_path)
    task_assignment_path_containment_review = create_task_assignment_record_path_containment_review(
        task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
    )
    queue_preview_scope_contract = create_queue_preview_scope_contract(
        approval_gate,
        task_assignment_reference_contract,
        task_assignment_integrity_verification,
        task_assignment_path_containment_review,
    )
    non_execution_queue_boundary = create_non_execution_queue_boundary(
        approval_gate,
        queue_preview_scope_contract,
    )
    queue_permission_denial_record = create_queue_permission_denial_record(queue_preview_label)
    local_queue_preview_candidate_record = create_local_queue_preview_candidate_record(
        command,
        approval_gate,
        task_assignment_reference_contract,
        optional_closeout_reference_contract,
        task_assignment_integrity_verification,
        closeout_integrity_verification,
        queue_preview_scope_contract,
        non_execution_queue_boundary,
        queue_permission_denial_record,
    )
    queue_preview_audit_record = create_queue_preview_audit_record(
        approval_gate,
        task_assignment_reference_contract,
        optional_closeout_reference_contract,
        task_assignment_integrity_verification,
        closeout_integrity_verification,
        task_assignment_path_containment_review,
        queue_preview_scope_contract,
        non_execution_queue_boundary,
        queue_permission_denial_record,
        local_queue_preview_candidate_record,
    )
    queue_preview_ledger = create_queue_preview_ledger(queue_preview_audit_record)
    queue_preview_readiness_summary = create_queue_preview_readiness_summary(queue_preview_ledger)
    task_queue_preview_audit_closeout_candidate_bridge = create_task_queue_preview_audit_closeout_candidate_bridge(queue_preview_readiness_summary)
    queue_preview_record_payload = build_non_executing_task_queue_preview_record_payload(
        command=command,
        queue_preview_label=queue_preview_label,
        human_operator=human_operator,
        referenced_task_assignment_record_path=task_assignment_record_path or "",
        optional_closeout_record_path=closeout_record_path,
        approval_gate=approval_gate,
        task_assignment_integrity_verification=task_assignment_integrity_verification,
        closeout_integrity_verification=closeout_integrity_verification,
        queue_permission_denial_record=queue_permission_denial_record,
        queue_preview_audit_record=queue_preview_audit_record,
        local_queue_preview_candidate_record=local_queue_preview_candidate_record,
        queue_preview_scope_contract=queue_preview_scope_contract,
        non_execution_queue_boundary=non_execution_queue_boundary,
    )
    if write_queue_preview_record and approval_gate.get("local_queue_preview_record_write_authorized", False):
        if not queue_preview_output_directory:
            queue_preview_write_record = create_blocked_queue_preview_write_record("queue preview output directory missing")
        else:
            queue_preview_write_record = write_non_executing_task_queue_preview_record(
                queue_preview_output_directory,
                queue_preview_record_name or DEFAULT_QUEUE_PREVIEW_RECORD_NAME,
                queue_preview_record_payload,
            )
    elif write_queue_preview_record:
        queue_preview_write_record = create_blocked_queue_preview_write_record("queue preview write not authorized")
    else:
        queue_preview_write_record = create_blocked_queue_preview_write_record("queue preview record write not requested")
    local_queue_preview_record_written = queue_preview_write_record.get("local_queue_preview_record_written", False)
    bundle = {
        "schema": create_non_executing_task_queue_preview_candidate_schema(),
        "non_executing_task_queue_preview_candidate_approval_gate": approval_gate,
        "v4_4_task_assignment_record_reference_contract": task_assignment_reference_contract,
        "optional_v4_5_closeout_record_reference_contract": optional_closeout_reference_contract,
        "task_assignment_record_integrity_verification": task_assignment_integrity_verification,
        "closeout_record_integrity_verification": closeout_integrity_verification,
        "task_assignment_record_path_containment_review": task_assignment_path_containment_review,
        "queue_preview_scope_contract": queue_preview_scope_contract,
        "non_execution_queue_boundary": non_execution_queue_boundary,
        "queue_permission_denial_record": queue_permission_denial_record,
        "local_queue_preview_candidate_record": local_queue_preview_candidate_record,
        "non_executing_task_queue_preview_candidate_record": local_queue_preview_candidate_record,
        "queue_preview_audit_record": queue_preview_audit_record,
        "queue_preview_ledger": queue_preview_ledger,
        "queue_preview_readiness_summary": queue_preview_readiness_summary,
        "task_queue_preview_audit_closeout_candidate_bridge": task_queue_preview_audit_closeout_candidate_bridge,
        "queue_preview_record_payload": queue_preview_record_payload,
        "queue_preview_write_record": queue_preview_write_record,
        "local_queue_preview_record_written": local_queue_preview_record_written,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "referenced_closeout_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest({k: v for k, v in bundle.items() if k != "bundle_digest"})
    return bundle
