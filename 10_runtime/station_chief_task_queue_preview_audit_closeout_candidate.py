import json
import hashlib
import re
from pathlib import Path

TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION = "4.7.0"
TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_STATUS = "TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_LOCAL_RECORD_ONLY"
TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_PHASE = "Task Queue Preview Audit Closeout Candidate"
TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE"
DEFAULT_QUEUE_CLOSEOUT_LABEL = "task-queue-preview-audit-closeout-candidate"
DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME = "task_queue_preview_audit_closeout_candidate_record.json"
EXPECTED_V4_6_QUEUE_PREVIEW_RECORD_NAME = "non_executing_task_queue_preview_candidate_record.json"

def _false_booleans() -> dict:
    return {
        "external_actions_taken": False,
        "live_external_action_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "dns_resolution_performed": False,
        "outbound_connection_performed": False,
        "inbound_connection_performed": False,
        "webhook_call_performed": False,
        "credential_vault_access_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "tokens_read": False,
        "api_keys_read": False,
        "oauth_used": False,
        "service_account_used": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "task_executed": False,
        "task_enqueued": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "worker_processes_started": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "full_workforce_activation_performed": False,
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def normalize_label(label: str, default: str) -> str:
    if not label or not isinstance(label, str):
        return default
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", label.lower()).strip("-")
    if not normalized:
        return default
    return normalized


def safe_queue_closeout_record_name(record_name: str | None) -> str:
    if not record_name or not isinstance(record_name, str):
        return DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME
    if record_name in [".", ".."]:
        return DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME
    return record_name


def generate_task_queue_preview_audit_closeout_candidate_id(
    command: str,
    queue_closeout_label: str,
    runtime_version: str = "4.7.0"
) -> str:
    normalized = normalize_label(queue_closeout_label, DEFAULT_QUEUE_CLOSEOUT_LABEL)
    digest = sha256_digest({"command": command, "label": normalized, "version": runtime_version})
    return f"task-queue-preview-audit-closeout-candidate-v4-7-{normalized}-{digest[:12]}"


def create_task_queue_preview_audit_closeout_candidate_schema() -> dict:
    return {
        "task_queue_preview_audit_closeout_candidate_schema_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "schema_status": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_STATUS,
        "closeout_type": "local_task_queue_preview_audit_closeout_record",
        "required_sections": [
            "task_queue_preview_audit_closeout_candidate_approval_gate",
            "v4_6_queue_preview_record_reference_contract",
            "queue_preview_record_integrity_verification",
            "queue_preview_record_path_containment_review",
            "queue_preview_safety_boolean_review",
            "non_execution_queue_closeout_boundary",
            "operator_queue_closeout_acknowledgement",
            "queue_preview_closeout_audit_record",
            "queue_preview_closeout_ledger",
            "queue_preview_closeout_readiness_summary",
            "non_executing_worker_routing_preview_candidate_bridge",
        ],
        "required_confirmation_token": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_queue_closeout_record_written": False,
        **_false_booleans(),
    }


def create_task_queue_preview_audit_closeout_candidate_approval_gate(
    queue_closeout_label: str,
    queue_preview_record_path: str | None = None,
    expected_queue_preview_output_directory: str | None = None,
    queue_closeout_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_closeout_requested: bool = False
) -> dict:
    token_valid = confirmation_token == TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN
    human_operator_present = bool(human_operator and isinstance(human_operator, str) and human_operator.strip())
    queue_preview_record_path_present = bool(queue_preview_record_path and isinstance(queue_preview_record_path, str) and queue_preview_record_path.strip())
    queue_closeout_output_directory_present = bool(queue_closeout_output_directory and isinstance(queue_closeout_output_directory, str) and queue_closeout_output_directory.strip())
    
    local_queue_closeout_records_authorized = token_valid and human_operator_present and queue_preview_record_path_present
    local_queue_closeout_record_write_authorized = (
        local_queue_closeout_records_authorized and
        queue_closeout_output_directory_present and
        queue_closeout_requested
    )

    if local_queue_closeout_records_authorized:
        gate_status = "APPROVED_FOR_ONE_LOCAL_TASK_QUEUE_PREVIEW_CLOSEOUT_RECORD"
    else:
        gate_status = "BLOCKED_PENDING_V4_7_QUEUE_CLOSEOUT_APPROVAL"

    return {
        "approval_gate_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "queue_closeout_label": queue_closeout_label,
        "queue_preview_record_path": queue_preview_record_path,
        "expected_queue_preview_output_directory": expected_queue_preview_output_directory,
        "queue_closeout_output_directory": queue_closeout_output_directory,
        "human_operator": human_operator,
        "gate_status": gate_status,
        "confirmation_token_required": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": bool(confirmation_token),
        "confirmation_token_valid": token_valid,
        "human_operator_present": human_operator_present,
        "queue_preview_record_path_present": queue_preview_record_path_present,
        "local_queue_closeout_records_authorized": local_queue_closeout_records_authorized,
        "local_queue_closeout_record_write_authorized": local_queue_closeout_record_write_authorized,
        "baseline_preserved": True,
        "queue_creation_authorized": False,
        "queue_write_authorized": False,
        "scheduler_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "full_workforce_activation_authorized": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_v4_6_queue_preview_record_reference_contract(approval_gate: dict) -> dict:
    if approval_gate.get("local_queue_closeout_records_authorized"):
        contract_status = "V4_6_QUEUE_PREVIEW_RECORD_REFERENCE_CONTRACT_CREATED"
    else:
        contract_status = "BLOCKED_PENDING_QUEUE_CLOSEOUT_APPROVAL"
        
    return {
        "reference_contract_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "contract_status": contract_status,
        "queue_preview_record_path": approval_gate.get("queue_preview_record_path"),
        "references_exactly_one_v4_6_queue_preview_record": True,
        "reference_only": True,
        "does_not_mutate_referenced_record": True,
        "does_not_create_queue": True,
        "does_not_write_to_queue": True,
        "does_not_enqueue_task": True,
        "does_not_execute_task": True,
        "does_not_route_worker": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_queue_preview_record_integrity_verification(queue_preview_record_path: str | None) -> dict:
    res = {
        "integrity_verification_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "verification_status": "BLOCKED",
        "queue_preview_record_path": queue_preview_record_path,
        "record_exists": False,
        "record_is_file": False,
        "record_suffix_json": False,
        "record_filename_expected": False,
        "record_json_parses": False,
        "runtime_version_matches": False,
        "queue_preview_type_matches": False,
        "payload_digest_present": False,
        "payload_digest_valid": False,
        "parsed_record_digest": None,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }

    if not queue_preview_record_path:
        res["verification_status"] = "BLOCKED"
        return res

    path = Path(queue_preview_record_path)
    res["record_exists"] = path.exists()
    if not res["record_exists"]:
        return res

    res["record_is_file"] = path.is_file()
    if not res["record_is_file"]:
        return res

    res["record_filename_expected"] = path.name == EXPECTED_V4_6_QUEUE_PREVIEW_RECORD_NAME
    res["record_suffix_json"] = path.suffix == ".json"

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        res["record_json_parses"] = True
    except Exception:
        return res

    res["runtime_version_matches"] = data.get("runtime_version") == "4.6.0"
    res["queue_preview_type_matches"] = data.get("queue_preview_type") == "local_non_executing_task_queue_preview_record"

    payload_digest = data.get("payload_digest")
    res["payload_digest_present"] = bool(payload_digest)

    parsed_copy = dict(data)
    if "payload_digest" in parsed_copy:
        del parsed_copy["payload_digest"]
        
    recomputed = sha256_digest(parsed_copy)
    res["parsed_record_digest"] = recomputed
    
    if payload_digest:
        res["payload_digest_valid"] = payload_digest == recomputed

    res["parsed_record_data"] = {
        "queue_preview_label": data.get("queue_preview_label"),
        "human_operator": data.get("human_operator"),
        "queue_preview_candidate_id": data.get("queue_preview_candidate_id"),
        "local_queue_preview_record_written": data.get("local_queue_preview_record_written"),
        "queue_created": data.get("queue_created"),
        "queue_write_performed": data.get("queue_write_performed"),
        "scheduler_write_performed": data.get("scheduler_write_performed"),
        "task_executed": data.get("task_executed"),
        "task_enqueued": data.get("task_enqueued"),
        "worker_process_started": data.get("worker_process_started"),
        "live_task_assignment_performed": data.get("live_task_assignment_performed"),
        "live_worker_routing_performed": data.get("live_worker_routing_performed"),
        "full_workforce_activation_performed": data.get("full_workforce_activation_performed"),
    }

    if (res["record_exists"] and res["record_is_file"] and res["record_json_parses"] and
        res["record_filename_expected"] and res["queue_preview_type_matches"]):
        if not payload_digest or res["payload_digest_valid"]:
            res["verification_status"] = "PASS"

    return res


def create_queue_preview_record_path_containment_review(
    queue_preview_record_path: str | None,
    expected_queue_preview_output_directory: str | None = None
) -> dict:
    res = {
        "path_containment_review_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "containment_status": "BLOCKED",
        "queue_preview_record_path": queue_preview_record_path,
        "expected_queue_preview_output_directory": expected_queue_preview_output_directory,
        "record_path_contained_within_expected_output_directory": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }

    if not expected_queue_preview_output_directory:
        res["containment_status"] = "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY"
        return res

    if not queue_preview_record_path:
        return res

    try:
        record_path = Path(queue_preview_record_path).resolve()
        expected_dir = Path(expected_queue_preview_output_directory).resolve()
        if expected_dir in record_path.parents:
            res["record_path_contained_within_expected_output_directory"] = True
            res["containment_status"] = "PASS"
    except Exception:
        pass

    return res


def create_queue_preview_safety_boolean_review(queue_preview_record_data: dict | None) -> dict:
    res = {
        "safety_boolean_review_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "safety_review_status": "BLOCKED",
        "dangerous_boolean_hits": [],
        "local_queue_preview_record_written": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    if not queue_preview_record_data:
        return res

    dangerous_keys = [
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
    ]

    hits = []
    
    def check_dict(d: dict):
        for k, v in d.items():
            if k in dangerous_keys and v is True:
                hits.append(k)
            if isinstance(v, dict):
                check_dict(v)

    check_dict(queue_preview_record_data)

    res["dangerous_boolean_hits"] = hits
    if "local_queue_preview_record_written" in queue_preview_record_data:
        res["local_queue_preview_record_written"] = queue_preview_record_data["local_queue_preview_record_written"]
        
    if not hits:
        res["safety_review_status"] = "PASS"

    return res


def create_non_execution_queue_closeout_boundary(
    approval_gate: dict,
    reference_contract: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict
) -> dict:
    gate_ok = approval_gate.get("local_queue_closeout_records_authorized")
    ref_ok = reference_contract.get("contract_status") == "V4_6_QUEUE_PREVIEW_RECORD_REFERENCE_CONTRACT_CREATED"
    int_ok = integrity_verification.get("verification_status") == "PASS"
    safe_ok = safety_boolean_review.get("safety_review_status") == "PASS"
    cont_ok = path_containment_review.get("containment_status") in ["PASS", "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY"]

    if gate_ok and ref_ok and int_ok and safe_ok and cont_ok:
        boundary_status = "PASS"
    else:
        boundary_status = "BLOCKED"

    return {
        "non_execution_boundary_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "boundary_status": boundary_status,
        "closeout_record_is_local_metadata_only": True,
        "no_queue_creation": True,
        "no_queue_write": True,
        "no_scheduler_write": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_live_assignment": True,
        "no_worker_routing": True,
        "no_worker_process_start": True,
        "no_referenced_record_mutation": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_operator_queue_closeout_acknowledgement(
    approval_gate: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict,
    non_execution_queue_closeout_boundary: dict
) -> dict:
    token_valid = approval_gate.get("confirmation_token_valid")
    human_present = approval_gate.get("human_operator_present")
    int_ok = integrity_verification.get("verification_status") == "PASS"
    safe_ok = safety_boolean_review.get("safety_review_status") == "PASS"
    cont_status = path_containment_review.get("containment_status")
    boundary_ok = non_execution_queue_closeout_boundary.get("boundary_status") == "PASS"

    status = "BLOCKED"
    if token_valid and human_present and int_ok and safe_ok and boundary_ok:
        if cont_status == "PASS":
            status = "PASS"
        elif cont_status == "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY":
            status = "BLOCKED_PENDING_OUTPUT_DIRECTORY_CONFIRMATION"

    return {
        "acknowledgement_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "acknowledgement_status": status,
        "token_valid": token_valid,
        "human_operator_present": human_present,
        "integrity_verification_pass": int_ok,
        "safety_review_pass": safe_ok,
        "containment_review_status": cont_status,
        "boundary_review_pass": boundary_ok,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_queue_preview_closeout_audit_record(
    approval_gate: dict,
    reference_contract: dict,
    integrity_verification: dict,
    path_containment_review: dict,
    safety_boolean_review: dict,
    non_execution_queue_closeout_boundary: dict,
    operator_acknowledgement: dict
) -> dict:
    status = "PASS" if operator_acknowledgement.get("acknowledgement_status") == "PASS" else "BLOCKED"
    return {
        "audit_record_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "audit_status": status,
        "approval_gate_digest": sha256_digest(approval_gate),
        "reference_contract_digest": sha256_digest(reference_contract),
        "integrity_verification_digest": sha256_digest(integrity_verification),
        "path_containment_review_digest": sha256_digest(path_containment_review),
        "safety_boolean_review_digest": sha256_digest(safety_boolean_review),
        "non_execution_queue_closeout_boundary_digest": sha256_digest(non_execution_queue_closeout_boundary),
        "operator_acknowledgement_digest": sha256_digest(operator_acknowledgement),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_queue_preview_closeout_ledger(audit_record: dict) -> dict:
    status = "PASS" if audit_record.get("audit_status") == "PASS" else "BLOCKED"
    return {
        "ledger_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "ledger_status": status,
        "audit_record_digest": sha256_digest(audit_record),
        "ledger_digest": sha256_digest({"status": status, "audit": sha256_digest(audit_record)}),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_queue_preview_closeout_readiness_summary(ledger: dict) -> dict:
    status = "READY_FOR_NON_EXECUTING_WORKER_ROUTING_PREVIEW_CANDIDATE" if ledger.get("ledger_status") == "PASS" else "BLOCKED"
    return {
        "readiness_summary_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "readiness_status": status,
        "next_layer": "Non-Executing Worker Routing Preview Candidate",
        "v4_8_built": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_non_executing_worker_routing_preview_candidate_bridge(summary: dict) -> dict:
    status = "READY" if summary.get("readiness_status") == "READY_FOR_NON_EXECUTING_WORKER_ROUTING_PREVIEW_CANDIDATE" else "BLOCKED"
    return {
        "bridge_version": TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_MODULE_VERSION,
        "bridge_status": status,
        "no_worker_routing_in_v4_7": True,
        "no_live_routing_in_v4_7": True,
        "no_task_execution_in_v4_7": True,
        "no_task_enqueue_in_v4_7": True,
        "no_worker_process_start_in_v4_7": True,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def build_task_queue_preview_audit_closeout_record_payload(
    queue_closeout_label: str,
    human_operator: str | None,
    referenced_queue_preview_record_path: str | None,
    approval_token_valid: bool,
    queue_closeout_candidate_id: str,
    referenced_queue_preview_record_digest: str | None,
    safety_review_digest: str,
    closeout_audit_digest: str
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": "4.7.0",
        "closeout_type": "local_task_queue_preview_audit_closeout_record",
        "queue_closeout_label": queue_closeout_label,
        "human_operator": human_operator,
        "referenced_queue_preview_record_path": referenced_queue_preview_record_path,
        "approval_token_valid": approval_token_valid,
        "queue_closeout_candidate_id": queue_closeout_candidate_id,
        "referenced_queue_preview_record_digest": referenced_queue_preview_record_digest,
        "safety_review_digest": safety_review_digest,
        "closeout_audit_digest": closeout_audit_digest,
        **_false_booleans(),
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_task_queue_preview_audit_closeout_record(
    queue_closeout_output_directory: str,
    record_name: str,
    payload: dict
) -> dict:
    try:
        out_dir = Path(queue_closeout_output_directory).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = safe_queue_closeout_record_name(record_name)
        out_path = (out_dir / safe_name).resolve()
        
        if out_dir not in out_path.parents:
            return create_blocked_queue_closeout_write_record("path traversal denied")
            
        out_path.write_text(canonical_json(payload), encoding="utf-8")
        
        return {
            "queue_closeout_write_record_version": "4.7.0",
            "write_status": "LOCAL_TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_RECORD_WRITTEN",
            "local_queue_closeout_record_written": True,
            "files_written_count": 1,
            "queue_closeout_output_directory": str(out_dir),
            "record_name": safe_name,
            "record_path": str(out_path),
            "referenced_queue_preview_record_mutated": False,
            "execution_authorized": False,
            **_false_booleans(),
        }
    except Exception as e:
        return create_blocked_queue_closeout_write_record(f"write failed: {str(e)}")


def create_blocked_queue_closeout_write_record(reason: str) -> dict:
    return {
        "queue_closeout_write_record_version": "4.7.0",
        "write_status": "BLOCKED",
        "block_reason": reason,
        "local_queue_closeout_record_written": False,
        "files_written_count": 0,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_task_queue_preview_audit_closeout_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    queue_closeout_label: str | None = None,
    queue_preview_record_path: str | None = None,
    expected_queue_preview_output_directory: str | None = None,
    queue_closeout_output_directory: str | None = None,
    queue_closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_closeout_requested: bool = False,
    write_queue_closeout_record: bool = False
) -> dict:
    schema = create_task_queue_preview_audit_closeout_candidate_schema()
    command = command or "check please"
    queue_closeout_label = queue_closeout_label or DEFAULT_QUEUE_CLOSEOUT_LABEL
    
    approval_gate = create_task_queue_preview_audit_closeout_candidate_approval_gate(
        queue_closeout_label,
        queue_preview_record_path,
        expected_queue_preview_output_directory,
        queue_closeout_output_directory,
        confirmation_token,
        human_operator,
        queue_closeout_requested
    )
    
    reference_contract = create_v4_6_queue_preview_record_reference_contract(approval_gate)
    integrity_verification = create_queue_preview_record_integrity_verification(queue_preview_record_path)
    path_containment_review = create_queue_preview_record_path_containment_review(queue_preview_record_path, expected_queue_preview_output_directory)
    
    record_data = None
    if integrity_verification.get("verification_status") == "PASS":
        try:
            record_data = json.loads(Path(queue_preview_record_path).read_text(encoding="utf-8")) # type: ignore
        except Exception:
            pass

    safety_review = create_queue_preview_safety_boolean_review(record_data)
    boundary = create_non_execution_queue_closeout_boundary(approval_gate, reference_contract, integrity_verification, path_containment_review, safety_review)
    acknowledgement = create_operator_queue_closeout_acknowledgement(approval_gate, integrity_verification, path_containment_review, safety_review, boundary)
    audit = create_queue_preview_closeout_audit_record(approval_gate, reference_contract, integrity_verification, path_containment_review, safety_review, boundary, acknowledgement)
    ledger = create_queue_preview_closeout_ledger(audit)
    summary = create_queue_preview_closeout_readiness_summary(ledger)
    bridge = create_non_executing_worker_routing_preview_candidate_bridge(summary)

    cid = generate_task_queue_preview_audit_closeout_candidate_id(command, queue_closeout_label)

    payload = build_task_queue_preview_audit_closeout_record_payload(
        queue_closeout_label,
        human_operator,
        queue_preview_record_path,
        approval_gate.get("confirmation_token_valid", False),
        cid,
        integrity_verification.get("parsed_record_digest"),
        sha256_digest(safety_review),
        sha256_digest(audit)
    )

    write_record = create_blocked_queue_closeout_write_record("queue preview closeout record write not requested")
    
    if write_queue_closeout_record:
        if ledger.get("ledger_status") == "PASS" and acknowledgement.get("acknowledgement_status") == "PASS":
            write_record = write_task_queue_preview_audit_closeout_record(
                queue_closeout_output_directory, # type: ignore
                queue_closeout_record_name or DEFAULT_QUEUE_CLOSEOUT_RECORD_NAME,
                payload
            )
        else:
            write_record = create_blocked_queue_closeout_write_record("ledger or acknowledgement blocked")

    return {
        "schema": schema,
        "task_queue_preview_audit_closeout_candidate_approval_gate": approval_gate,
        "v4_6_queue_preview_record_reference_contract": reference_contract,
        "queue_preview_record_integrity_verification": integrity_verification,
        "queue_preview_record_path_containment_review": path_containment_review,
        "queue_preview_safety_boolean_review": safety_review,
        "non_execution_queue_closeout_boundary": boundary,
        "operator_queue_closeout_acknowledgement": acknowledgement,
        "queue_preview_closeout_audit_record": audit,
        "queue_preview_closeout_ledger": ledger,
        "queue_preview_closeout_readiness_summary": summary,
        "non_executing_worker_routing_preview_candidate_bridge": bridge,
        "queue_closeout_record_payload": payload,
        "queue_closeout_write_record": write_record,
        "local_queue_closeout_record_written": write_record.get("local_queue_closeout_record_written", False),
        "execution_authorized": False,
        **_false_booleans(),
    }
