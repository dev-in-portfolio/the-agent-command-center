#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION = "4.5.0"
TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_STATUS = "TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_LOCAL_RECORD_ONLY"
TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_PHASE = "Task Assignment Audit Closeout Candidate"
TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE"
DEFAULT_CLOSEOUT_LABEL = "task-assignment-audit-closeout-candidate"
DEFAULT_CLOSEOUT_RECORD_NAME = "task_assignment_audit_closeout_candidate_record.json"
EXPECTED_V4_4_ASSIGNMENT_RECORD_NAME = "permissioned_worker_task_assignment_candidate_record.json"

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


def safe_closeout_record_name(record_name: str | None) -> str:
    if not record_name:
        return DEFAULT_CLOSEOUT_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_CLOSEOUT_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_CLOSEOUT_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_CLOSEOUT_RECORD_NAME
    return record_name


def generate_task_assignment_audit_closeout_candidate_id(
    command: str,
    closeout_label: str,
    runtime_version: str = TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_closeout = normalize_label(closeout_label, DEFAULT_CLOSEOUT_LABEL)
    digest = sha256_digest(f"{runtime_version}:{command}:{closeout_label}")
    return f"task-assignment-audit-closeout-candidate-v4-5-{normalized_closeout}-{digest[:12]}"


def create_task_assignment_audit_closeout_candidate_schema() -> dict:
    return {
        "task_assignment_audit_closeout_candidate_schema_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "schema_status": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_STATUS,
        "closeout_type": "local_task_assignment_audit_closeout_record",
        "required_sections": [
            "task_assignment_audit_closeout_candidate_approval_gate",
            "v4_4_task_assignment_record_reference_contract",
            "task_assignment_record_integrity_verification",
            "task_assignment_record_path_containment_review",
            "task_assignment_safety_boolean_review",
            "non_execution_closeout_boundary",
            "operator_closeout_acknowledgement",
            "task_assignment_closeout_audit_record",
            "task_assignment_closeout_ledger",
            "task_assignment_closeout_readiness_summary",
            "non_executing_task_queue_preview_candidate_bridge",
        ],
        "required_confirmation_token": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_closeout_record_written": False,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_worker_routing_performed": False,
        "live_task_assignment_performed": False,
        **_false_booleans(),
    }


def create_task_assignment_audit_closeout_candidate_approval_gate(
    closeout_label: str,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    closeout_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN
    closeout_label_present = bool(closeout_label and str(closeout_label).strip())
    record_path_present = bool(task_assignment_record_path and str(task_assignment_record_path).strip())
    human_present = bool(human_operator and str(human_operator).strip())
    expected_output_present = bool(expected_task_assignment_output_directory and str(expected_task_assignment_output_directory).strip())
    closeout_output_present = bool(closeout_output_directory and str(closeout_output_directory).strip())
    local_closeout_records_authorized = token_valid and human_present and record_path_present
    local_closeout_record_write_authorized = (
        token_valid
        and human_present
        and record_path_present
        and closeout_output_present
        and bool(closeout_requested)
    )
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_TASK_ASSIGNMENT_CLOSEOUT_RECORD"
        if local_closeout_records_authorized
        else "BLOCKED_PENDING_V4_5_CLOSEOUT_APPROVAL"
    )
    return {
        "task_assignment_audit_closeout_candidate_approval_gate_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "closeout_label": closeout_label,
        "closeout_label_normalized": normalize_label(closeout_label, DEFAULT_CLOSEOUT_LABEL),
        "task_assignment_record_path": task_assignment_record_path,
        "task_assignment_record_path_present": record_path_present,
        "expected_task_assignment_output_directory": expected_task_assignment_output_directory,
        "expected_task_assignment_output_directory_present": expected_output_present,
        "closeout_output_directory": closeout_output_directory,
        "human_operator": human_operator,
        "closeout_requested": bool(closeout_requested),
        "gate_status": gate_status,
        "confirmation_token_required": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "closeout_label_present": closeout_label_present,
        "human_operator_present": human_present,
        "local_closeout_records_authorized": local_closeout_records_authorized,
        "local_closeout_record_write_authorized": local_closeout_record_write_authorized,
        "task_execution_authorized": False,
        "task_enqueue_authorized": False,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "full_workforce_activation_authorized": False,
        "baseline_preserved": True,
        "local_closeout_record_written": False,
        **_false_booleans(),
    }


def create_v4_4_task_assignment_record_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_closeout_records_authorized", False)
    record_path = approval_gate.get("task_assignment_record_path")
    return {
        "v4_4_task_assignment_record_reference_contract_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "contract_status": "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "task_assignment_record_path": record_path,
        "task_assignment_record_name": Path(record_path).name if record_path else None,
        "referenced_task_assignment_record_name": EXPECTED_V4_4_ASSIGNMENT_RECORD_NAME,
        "referenced_task_assignment_record_is_v4_4_local_record_only": True,
        "does_not_mutate_referenced_record": True,
        "does_not_execute_task": True,
        "does_not_enqueue_task": True,
        "does_not_route_worker": True,
        "does_not_start_worker_process": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_assignment_record_integrity_verification(task_assignment_record_path: str | None) -> dict:
    if not task_assignment_record_path:
        return {
            "task_assignment_record_integrity_verification_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
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
    parsed_record_digest = None
    if record_exists and record_is_file and record_name_valid:
        try:
            parsed_record = json.loads(record_path.read_text(encoding="utf-8"))
            json_parse_valid = True
        except Exception:
            parsed_record = None
    if isinstance(parsed_record, dict):
        parsed_record_digest = sha256_digest(parsed_record)
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
        "task_assignment_record_integrity_verification_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
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
            "task_assignment_record_path_containment_review_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
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
            "task_assignment_record_path_containment_review_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
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
        "task_assignment_record_path_containment_review_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
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


def create_task_assignment_safety_boolean_review(task_assignment_record_data: dict | None) -> dict:
    observed = {}
    if isinstance(task_assignment_record_data, dict):
        for key, value in _iter_nested_values(task_assignment_record_data):
            if key in DANGEROUS_BOOLEAN_FIELDS and key not in observed:
                observed[key] = value
    dangerous_false = all(value is False for value in observed.values())
    local_written = task_assignment_record_data.get("local_closeout_record_written") if isinstance(task_assignment_record_data, dict) else False
    return {
        "task_assignment_safety_boolean_review_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "safety_review_status": "PASS" if dangerous_false else "BLOCKED",
        "dangerous_boolean_values": observed,
        "local_closeout_record_written": bool(local_written),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_non_execution_closeout_boundary(
    approval_gate: dict,
    reference_contract: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict,
) -> dict:
    containment_status = path_containment_review.get("containment_status")
    pass_ok = (
        approval_gate.get("local_closeout_records_authorized", False)
        and reference_contract.get("contract_status") == "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED"
        and integrity_verification.get("verification_status") == "PASS"
        and safety_boolean_review.get("safety_review_status") == "PASS"
        and containment_status == "PASS"
    )
    return {
        "non_execution_closeout_boundary_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "boundary_status": "PASS" if pass_ok else "BLOCKED",
        "containment_blocker": containment_status == "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY",
        "closeout_record_is_local_metadata_only": True,
        "closeout_is_not_executable": True,
        "closeout_is_not_queued": True,
        "closeout_is_not_running": True,
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


def create_operator_closeout_acknowledgement(
    approval_gate: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict,
    non_execution_closeout_boundary: dict,
) -> dict:
    expected_dir_present = bool(approval_gate.get("expected_task_assignment_output_directory_present"))
    if not expected_dir_present:
        acknowledgement_status = "BLOCKED_PENDING_OUTPUT_DIRECTORY_CONFIRMATION"
    else:
        acknowledgement_status = (
            "PASS"
            if (
                approval_gate.get("confirmation_token_valid", False)
                and approval_gate.get("human_operator_present", False)
                and integrity_verification.get("verification_status") == "PASS"
                and path_containment_review.get("containment_status") == "PASS"
                and safety_boolean_review.get("safety_review_status") == "PASS"
                and non_execution_closeout_boundary.get("boundary_status") == "PASS"
            )
            else "BLOCKED"
        )
    return {
        "operator_closeout_acknowledgement_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "acknowledgement_status": acknowledgement_status,
        "token_valid": approval_gate.get("confirmation_token_valid", False),
        "human_operator_present": approval_gate.get("human_operator_present", False),
        "integrity_verification_status": integrity_verification.get("verification_status"),
        "containment_status": path_containment_review.get("containment_status"),
        "safety_review_status": safety_boolean_review.get("safety_review_status"),
        "boundary_status": non_execution_closeout_boundary.get("boundary_status"),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_assignment_closeout_audit_record(
    approval_gate: dict,
    reference_contract: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict,
    non_execution_closeout_boundary: dict,
    operator_closeout_acknowledgement: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "reference_contract": sha256_digest(reference_contract),
        "integrity_verification": sha256_digest(integrity_verification),
        "path_containment_review": sha256_digest(path_containment_review),
        "safety_boolean_review": sha256_digest(safety_boolean_review),
        "non_execution_closeout_boundary": sha256_digest(non_execution_closeout_boundary),
        "operator_closeout_acknowledgement": sha256_digest(operator_closeout_acknowledgement),
    }
    audit_ok = (
        operator_closeout_acknowledgement.get("acknowledgement_status") == "PASS"
        and safety_boolean_review.get("safety_review_status") == "PASS"
        and non_execution_closeout_boundary.get("boundary_status") == "PASS"
    )
    audit_record = {
        "task_assignment_closeout_audit_record_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "section_digests": section_digests,
        "closeout_candidate_created": reference_contract.get("contract_status") == "V4_4_TASK_ASSIGNMENT_RECORD_REFERENCE_CONTRACT_CREATED",
        "all_dangerous_booleans_false": True,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    audit_record["audit_digest"] = sha256_digest({k: v for k, v in audit_record.items() if k != "audit_digest"})
    return audit_record


def create_task_assignment_closeout_ledger(task_assignment_closeout_audit_record: dict) -> dict:
    ledger_ok = task_assignment_closeout_audit_record.get("audit_status") == "PASS"
    ledger_record = {
        "task_assignment_closeout_ledger_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "ledger_status": "PASS" if ledger_ok else "BLOCKED",
        "audit_record_digest": sha256_digest(task_assignment_closeout_audit_record),
        "all_dangerous_booleans_false": True,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    ledger_record["ledger_digest"] = sha256_digest({k: v for k, v in ledger_record.items() if k != "ledger_digest"})
    return ledger_record


def create_task_assignment_closeout_readiness_summary(task_assignment_closeout_ledger: dict) -> dict:
    ready = task_assignment_closeout_ledger.get("ledger_status") == "PASS"
    return {
        "task_assignment_closeout_readiness_summary_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Non-Executing Task Queue Preview Candidate",
        "v4_6_built": False,
        "no_task_execution_yet": True,
        "no_task_enqueue_yet": True,
        "no_live_task_assignment_yet": True,
        "no_worker_routing_yet": True,
        "no_process_start": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_executing_task_queue_preview_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE"
    return {
        "non_executing_task_queue_preview_candidate_bridge_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_6_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE" if ready else "BLOCKED",
        "ready_for_v4_6": ready,
        "no_task_queue_in_v4_5": True,
        "no_task_enqueue_in_v4_5": True,
        "no_task_execution_in_v4_5": True,
        "no_worker_routing_in_v4_5": True,
        "no_worker_process_start_in_v4_5": True,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def build_task_assignment_audit_closeout_record_payload(
    command: str,
    closeout_label: str,
    human_operator: str | None,
    task_assignment_record_path: str,
    approval_gate: dict,
    reference_contract: dict,
    integrity_verification: dict,
    safety_boolean_review: dict,
    closeout_audit_record: dict,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "closeout_type": "local_task_assignment_audit_closeout_record",
        "closeout_label": closeout_label,
        "human_operator": human_operator,
        "referenced_task_assignment_record_path": task_assignment_record_path,
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "closeout_candidate_id": generate_task_assignment_audit_closeout_candidate_id(command, closeout_label),
        "referenced_record_digest": integrity_verification.get("parsed_record_digest"),
        "safety_review_digest": sha256_digest(safety_boolean_review),
        "closeout_audit_digest": closeout_audit_record.get("audit_digest"),
        "task_assignment_record_integrity_verification": integrity_verification,
        "v4_4_task_assignment_record_reference_contract": reference_contract,
        "task_assignment_record_path_containment_review": approval_gate.get("task_assignment_record_path_containment_review"),
        "task_assignment_safety_boolean_review": safety_boolean_review,
        "non_execution_closeout_boundary": approval_gate.get("non_execution_closeout_boundary"),
        "operator_closeout_acknowledgement": approval_gate.get("operator_closeout_acknowledgement"),
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "safety_booleans": {
            "task_executed": False,
            "task_enqueued": False,
            "worker_process_started": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "full_workforce_activation_performed": False,
            "referenced_task_assignment_record_mutated": False,
            **_false_booleans(),
        },
        "baseline_preserved": True,
    }
    payload["payload_digest"] = sha256_digest({k: v for k, v in payload.items() if k != "payload_digest"})
    return payload


def write_task_assignment_audit_closeout_record(
    closeout_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    output_dir = Path(closeout_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_closeout_record_name(record_name)
    record_path = (output_dir / safe_name).resolve()
    if not _path_contains(record_path, output_dir):
        return create_blocked_closeout_write_record("record path escaped approved output directory")
    record_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "closeout_write_record_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "write_status": "LOCAL_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_RECORD_WRITTEN",
        "local_closeout_record_written": True,
        "files_written_count": 1,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "record_name": safe_name,
        "record_path": str(record_path),
        "closeout_output_directory": str(output_dir),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_closeout_write_record(reason: str) -> dict:
    return {
        "closeout_write_record_version": TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "write_status": "BLOCKED",
        "reason": reason,
        "local_closeout_record_written": False,
        "files_written_count": 0,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_task_assignment_audit_closeout_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    closeout_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_output_directory: str | None = None,
    closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    closeout_requested: bool = False,
    write_closeout_record: bool = False,
) -> dict:
    command = command or "check please"
    closeout_label = closeout_label or DEFAULT_CLOSEOUT_LABEL
    approval_gate = create_task_assignment_audit_closeout_candidate_approval_gate(
        closeout_label=closeout_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_output_directory=closeout_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        closeout_requested=closeout_requested,
    )
    reference_contract = create_v4_4_task_assignment_record_reference_contract(approval_gate)
    integrity_verification = create_task_assignment_record_integrity_verification(task_assignment_record_path)
    path_containment_review = create_task_assignment_record_path_containment_review(
        task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
    )
    safety_boolean_review = create_task_assignment_safety_boolean_review(result if isinstance(result, dict) else None)
    non_execution_closeout_boundary = create_non_execution_closeout_boundary(
        approval_gate,
        reference_contract,
        integrity_verification,
        path_containment_review,
        safety_boolean_review,
    )
    operator_closeout_acknowledgement = create_operator_closeout_acknowledgement(
        approval_gate,
        integrity_verification,
        path_containment_review,
        safety_boolean_review,
        non_execution_closeout_boundary,
    )
    task_assignment_closeout_audit_record = create_task_assignment_closeout_audit_record(
        approval_gate,
        reference_contract,
        integrity_verification,
        path_containment_review,
        safety_boolean_review,
        non_execution_closeout_boundary,
        operator_closeout_acknowledgement,
    )
    task_assignment_closeout_ledger = create_task_assignment_closeout_ledger(task_assignment_closeout_audit_record)
    task_assignment_closeout_readiness_summary = create_task_assignment_closeout_readiness_summary(task_assignment_closeout_ledger)
    non_executing_task_queue_preview_candidate_bridge = create_non_executing_task_queue_preview_candidate_bridge(
        task_assignment_closeout_readiness_summary
    )
    task_assignment_closeout_record_payload = build_task_assignment_audit_closeout_record_payload(
        command=command,
        closeout_label=closeout_label,
        human_operator=human_operator,
        task_assignment_record_path=task_assignment_record_path or "",
        approval_gate={
            **approval_gate,
            "task_assignment_record_path_containment_review": path_containment_review,
            "non_execution_closeout_boundary": non_execution_closeout_boundary,
            "operator_closeout_acknowledgement": operator_closeout_acknowledgement,
        },
        reference_contract=reference_contract,
        integrity_verification=integrity_verification,
        safety_boolean_review=safety_boolean_review,
        closeout_audit_record=task_assignment_closeout_audit_record,
    )
    if write_closeout_record and approval_gate.get("local_closeout_record_write_authorized", False):
        if not closeout_output_directory:
            task_assignment_closeout_write_record = create_blocked_closeout_write_record("closeout output directory missing")
        else:
            task_assignment_closeout_write_record = write_task_assignment_audit_closeout_record(
                closeout_output_directory,
                closeout_record_name or DEFAULT_CLOSEOUT_RECORD_NAME,
                task_assignment_closeout_record_payload,
            )
    elif write_closeout_record:
        task_assignment_closeout_write_record = create_blocked_closeout_write_record("closeout write not authorized")
    else:
        task_assignment_closeout_write_record = create_blocked_closeout_write_record("closeout record write not requested")
    local_closeout_record_written = task_assignment_closeout_write_record.get("local_closeout_record_written", False)
    bundle = {
        "schema": create_task_assignment_audit_closeout_candidate_schema(),
        "task_assignment_audit_closeout_candidate_approval_gate": approval_gate,
        "v4_4_task_assignment_record_reference_contract": reference_contract,
        "task_assignment_record_integrity_verification": integrity_verification,
        "task_assignment_record_path_containment_review": path_containment_review,
        "task_assignment_safety_boolean_review": safety_boolean_review,
        "non_execution_closeout_boundary": non_execution_closeout_boundary,
        "operator_closeout_acknowledgement": operator_closeout_acknowledgement,
        "task_assignment_closeout_audit_record": task_assignment_closeout_audit_record,
        "task_assignment_closeout_ledger": task_assignment_closeout_ledger,
        "task_assignment_closeout_readiness_summary": task_assignment_closeout_readiness_summary,
        "non_executing_task_queue_preview_candidate_bridge": non_executing_task_queue_preview_candidate_bridge,
        "task_assignment_audit_closeout_record_payload": task_assignment_closeout_record_payload,
        "task_assignment_closeout_write_record": task_assignment_closeout_write_record,
        "local_closeout_record_written": local_closeout_record_written,
        "task_executed": False,
        "task_enqueued": False,
        "worker_process_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "full_workforce_activation_performed": False,
        "referenced_task_assignment_record_mutated": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest({k: v for k, v in bundle.items() if k != "bundle_digest"})
    return bundle
