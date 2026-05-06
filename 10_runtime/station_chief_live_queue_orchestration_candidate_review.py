import hashlib
import json
import re
from pathlib import Path

LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION = "4.9.0"
LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_STATUS = "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_LOCAL_RECORD_ONLY"
LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_PHASE = "Live Queue Orchestration Candidate Review"
LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY"
DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL = "station-chief-v4-8-sandbox-routing-preview-reference"
DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME = "live_queue_orchestration_candidate_review_record.json"

_DANGEROUS_BOOLEAN_FIELDS = [
    "real_queue_created",
    "queue_write_performed",
    "scheduler_write_performed",
    "cron_write_performed",
    "task_enqueued",
    "task_executed",
    "live_task_assignment_performed",
    "live_worker_routing_performed",
    "live_orchestration_performed",
    "worker_process_started",
    "full_workforce_activation_performed",
    "external_actions_taken",
    "live_api_call_performed",
    "network_access_performed",
    "socket_opened",
    "dns_resolution_performed",
    "credential_vault_access_performed",
    "credentials_used",
    "secrets_read",
    "environment_read",
    "deployment_performed",
    "deployment_rollback_performed",
    "production_execution_performed",
    "production_activation_performed",
    "real_external_tool_invocation_performed",
    "real_task_execution_performed",
    "queue_created",
    "queue_item_created",
    "queue_item_queued",
    "queue_dispatch_write_performed",
    "worker_processes_started",
    "production_state_changed",
    "repo_files_modified",
    "execution_authorized",
]


def _false_booleans() -> dict[str, bool]:
    return {name: False for name in _DANGEROUS_BOOLEAN_FIELDS}


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def normalize_label(label: str, default_label: str) -> str:
    if not isinstance(label, str):
        return default_label
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or default_label


def safe_review_record_name(record_name: str | None) -> str:
    if not isinstance(record_name, str) or not record_name:
        return DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME
    return record_name


def generate_orchestration_candidate_review_id(
    command: str,
    v4_8_routing_preview_reference_label: str,
    runtime_version: str = LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
) -> str:
    reference_norm = normalize_label(
        v4_8_routing_preview_reference_label,
        DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL,
    )
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "v4_8_routing_preview_reference_label": reference_norm,
        }
    )
    return f"live-queue-orchestration-candidate-review-v4-9-{reference_norm}-{digest[:12]}"


def create_live_queue_orchestration_candidate_review_schema() -> dict:
    return {
        "schema_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "status": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_STATUS,
        "review_type": "live_queue_orchestration_candidate_review",
        "required_sections": [
            "orchestration_review_approval_gate",
            "v4_8_queue_routing_preview_reference_contract",
            "orchestration_review_scope_contract",
            "non_execution_orchestration_boundary",
            "orchestration_permission_denial_record",
            "orchestration_candidate_review_record",
            "orchestration_review_audit_record",
            "orchestration_readiness_summary",
            "first_live_queue_execution_candidate_bridge",
        ],
        "required_token": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_orchestration_review_record_written": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        **_false_booleans(),
    }


def create_orchestration_review_approval_gate(
    v4_8_routing_preview_reference_label: str,
    review_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN
    reference_present = bool(v4_8_routing_preview_reference_label and str(v4_8_routing_preview_reference_label).strip())
    human_present = bool(human_operator and str(human_operator).strip())
    review_output_directory_present = bool(review_output_directory and str(review_output_directory).strip())
    local_records_authorized = token_valid and human_present and reference_present
    local_record_write_authorized = (
        local_records_authorized
        and review_output_directory_present
        and review_requested
    )
    return {
        "orchestration_review_approval_gate_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "gate_status": (
            "APPROVED_FOR_ONE_LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD"
            if local_records_authorized
            else "BLOCKED_PENDING_V4_9_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL"
        ),
        "v4_8_routing_preview_reference_label": v4_8_routing_preview_reference_label,
        "review_output_directory": review_output_directory,
        "confirmation_token_required": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "v4_8_routing_preview_reference_label_present": reference_present,
        "human_operator": human_operator,
        "human_operator_present": human_present,
        "review_requested": bool(review_requested),
        "review_output_directory_present": review_output_directory_present,
        "local_orchestration_review_records_authorized": local_records_authorized,
        "local_orchestration_review_record_write_authorized": local_record_write_authorized,
        "real_queue_creation_authorized": False,
        "queue_write_authorized": False,
        "scheduler_write_authorized": False,
        "cron_write_authorized": False,
        "task_enqueue_authorized": False,
        "task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "worker_process_start_authorized": False,
        "full_workforce_activation_authorized": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_v4_8_queue_routing_preview_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_orchestration_review_records_authorized", False)
    return {
        "v4_8_queue_routing_preview_reference_contract_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "contract_status": "CREATED" if authorized else "BLOCKED",
        "reference_count": 1 if authorized else 0,
        "v4_8_routing_preview_reference_label": approval_gate.get("v4_8_routing_preview_reference_label"),
        "v4_8_routing_preview_reference_label_normalized": normalize_label(
            approval_gate.get("v4_8_routing_preview_reference_label", ""),
            DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL,
        ),
        "reference_is_metadata_only": True,
        "reference_is_not_mutated": True,
        "reference_is_not_executed": True,
        "reference_is_not_enqueued": True,
        "reference_is_not_routed": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_orchestration_review_scope_contract(
    approval_gate: dict,
    v4_8_reference_contract: dict,
) -> dict:
    passed = (
        approval_gate.get("local_orchestration_review_records_authorized", False)
        and v4_8_reference_contract.get("contract_status") == "CREATED"
    )
    return {
        "orchestration_review_scope_contract_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "scope_status": "PASS" if passed else "BLOCKED",
        "exactly_one_v4_8_routing_preview_reference": True,
        "candidate_review_only": True,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_execution_orchestration_boundary(
    approval_gate: dict,
    orchestration_review_scope_contract: dict,
) -> dict:
    passed = (
        approval_gate.get("local_orchestration_review_records_authorized", False)
        and orchestration_review_scope_contract.get("scope_status") == "PASS"
    )
    return {
        "non_execution_orchestration_boundary_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "boundary_status": "PASS" if passed else "BLOCKED",
        "review_record_is_local_metadata_only": True,
        "no_real_queue": True,
        "no_queue_writes": True,
        "no_scheduler_writes": True,
        "no_cron_writes": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_live_routing": True,
        "no_live_orchestration": True,
        "no_worker_start": True,
        "no_tool_calls": True,
        "no_api_access": True,
        "no_network": True,
        "no_sockets": True,
        "no_dns": True,
        "no_credentials": True,
        "no_secrets": True,
        "no_environment": True,
        "no_deployment": True,
        "no_production_execution": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_orchestration_permission_denial_record(
    v4_8_routing_preview_reference_label: str,
) -> dict:
    return {
        "orchestration_permission_denial_record_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "v4_8_routing_preview_reference_label": v4_8_routing_preview_reference_label,
        "real_queue_creation_denied": True,
        "queue_writes_denied": True,
        "scheduler_writes_denied": True,
        "cron_writes_denied": True,
        "task_enqueue_denied": True,
        "task_execution_denied": True,
        "live_task_assignment_denied": True,
        "live_worker_routing_denied": True,
        "live_orchestration_denied": True,
        "worker_process_start_denied": True,
        "agent_start_denied": True,
        "external_tool_invocation_denied": True,
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
        "github_push_by_worker_denied": True,
        "full_workforce_activation_denied": True,
        "baseline_mutation_denied": True,
        "devinization_overlay_mutation_denied": True,
        "dashboard_org_master_export_mutation_denied": True,
        "ownership_metadata_mutation_denied": True,
        "referenced_v4_8_routing_preview_record_mutation_denied": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_orchestration_candidate_review_record(
    command: str,
    approval_gate: dict,
    v4_8_reference_contract: dict,
    orchestration_review_scope_contract: dict,
    non_execution_orchestration_boundary: dict,
    orchestration_permission_denial_record: dict,
) -> dict:
    candidate_ok = (
        approval_gate.get("local_orchestration_review_records_authorized", False)
        and v4_8_reference_contract.get("contract_status") == "CREATED"
        and orchestration_review_scope_contract.get("scope_status") == "PASS"
        and non_execution_orchestration_boundary.get("boundary_status") == "PASS"
    )
    candidate_id = generate_orchestration_candidate_review_id(
        command,
        v4_8_reference_contract.get("v4_8_routing_preview_reference_label", DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL),
    )
    candidate_record = {
        "orchestration_candidate_review_record_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "orchestration_candidate_review_id": candidate_id,
        "candidate_status": (
            "LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD_CREATED"
            if candidate_ok
            else "BLOCKED"
        ),
        "command": command,
        "v4_8_routing_preview_reference_label": v4_8_reference_contract.get("v4_8_routing_preview_reference_label"),
        "v4_8_routing_preview_reference_label_normalized": v4_8_reference_contract.get(
            "v4_8_routing_preview_reference_label_normalized"
        ),
        "human_operator": approval_gate.get("human_operator"),
        "review_mode": "local_metadata_only",
        "queue_runtime_state": "not_created",
        "task_runtime_state": "not_enqueued_not_executed",
        "worker_runtime_state": "not_started",
        "orchestration_runtime_state": "not_started",
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "orchestration_permission_denial_record": orchestration_permission_denial_record,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    candidate_record["orchestration_candidate_review_digest"] = sha256_digest(
        {k: v for k, v in candidate_record.items() if k != "orchestration_candidate_review_digest"}
    )
    return candidate_record


def create_orchestration_review_audit_record(
    approval_gate: dict,
    v4_8_reference_contract: dict,
    orchestration_review_scope_contract: dict,
    non_execution_orchestration_boundary: dict,
    orchestration_permission_denial_record: dict,
    orchestration_candidate_review_record: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "v4_8_queue_routing_preview_reference_contract": sha256_digest(v4_8_reference_contract),
        "orchestration_review_scope_contract": sha256_digest(orchestration_review_scope_contract),
        "non_execution_orchestration_boundary": sha256_digest(non_execution_orchestration_boundary),
        "orchestration_permission_denial_record": sha256_digest(orchestration_permission_denial_record),
        "orchestration_candidate_review_record": sha256_digest(orchestration_candidate_review_record),
    }
    audit_ok = (
        orchestration_candidate_review_record.get("candidate_status")
        == "LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD_CREATED"
        and not any(orchestration_candidate_review_record.get(name, False) for name in _DANGEROUS_BOOLEAN_FIELDS)
    )
    audit_record = {
        "orchestration_review_audit_record_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "section_digests": section_digests,
        "all_dangerous_booleans_false": True,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    audit_record["orchestration_review_audit_digest"] = sha256_digest(
        {k: v for k, v in audit_record.items() if k != "orchestration_review_audit_digest"}
    )
    return audit_record


def create_orchestration_readiness_summary(orchestration_review_audit_record: dict) -> dict:
    ready = orchestration_review_audit_record.get("audit_status") == "PASS"
    return {
        "orchestration_readiness_summary_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "readiness_status": (
            "READY_FOR_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "next_layer": "First Live Queue Execution Candidate Review",
        "v5_0_not_built": True,
        "no_real_queue_created_yet": True,
        "no_queue_write_yet": True,
        "no_task_enqueue_yet": True,
        "no_task_execution_yet": True,
        "no_live_routing_yet": True,
        "no_live_orchestration_yet": True,
        "no_worker_start_yet": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_first_live_queue_execution_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY"
    return {
        "first_live_queue_execution_candidate_bridge_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "bridge_status": (
            "READY_FOR_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "bridge_target": "First Live Queue Execution Candidate Review",
        "no_first_live_queue_execution_in_v4_9": True,
        "no_queue_creation_in_v4_9": True,
        "no_task_enqueue_in_v4_9": True,
        "no_task_execution_in_v4_9": True,
        "no_worker_routing_in_v4_9": True,
        "no_worker_process_start_in_v4_9": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def build_orchestration_candidate_review_record_payload(
    command: str,
    v4_8_routing_preview_reference_label: str,
    human_operator: str | None,
    approval_token_valid: bool,
    orchestration_candidate_review_id: str,
    orchestration_permission_denial_record: dict,
    orchestration_review_audit_digest: str,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "review_type": "live_queue_orchestration_candidate_review",
        "command": command,
        "v4_8_routing_preview_reference_label": v4_8_routing_preview_reference_label,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "orchestration_candidate_review_id": orchestration_candidate_review_id,
        "orchestration_permission_denial_record": orchestration_permission_denial_record,
        "orchestration_review_audit_digest": orchestration_review_audit_digest,
        "safety_booleans": _false_booleans(),
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_live_queue_orchestration_candidate_review_record(
    review_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    safe_name = safe_review_record_name(record_name)
    out_dir = Path(review_output_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = (out_dir / safe_name).resolve()
    try:
        out_path.relative_to(out_dir)
    except ValueError:
        return create_blocked_orchestration_candidate_review_write_record("path traversal denied")
    out_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "orchestration_candidate_review_write_record_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "write_status": "LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD_WRITTEN",
        "local_orchestration_review_record_written": True,
        "files_written_count": 1,
        "review_output_directory": str(out_dir),
        "record_name": safe_name,
        "record_path": str(out_path),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_orchestration_candidate_review_write_record(reason: str) -> dict:
    return {
        "orchestration_candidate_review_write_record_version": LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION,
        "write_status": "BLOCKED",
        "block_reason": reason,
        "local_orchestration_review_record_written": False,
        "files_written_count": 0,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_live_queue_orchestration_candidate_review_bundle(
    result: dict | None,
    command: str | None = None,
    v4_8_routing_preview_reference_label: str | None = None,
    review_output_directory: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
    write_review_record: bool = False,
) -> dict:
    base_result = result or {}
    command_text = command or base_result.get("command", "check please")
    reference_label = v4_8_routing_preview_reference_label or DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL
    approval_gate = create_orchestration_review_approval_gate(
        reference_label,
        review_output_directory=review_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=review_requested,
    )
    v4_8_reference_contract = create_v4_8_queue_routing_preview_reference_contract(approval_gate)
    orchestration_review_scope_contract = create_orchestration_review_scope_contract(
        approval_gate,
        v4_8_reference_contract,
    )
    non_execution_orchestration_boundary = create_non_execution_orchestration_boundary(
        approval_gate,
        orchestration_review_scope_contract,
    )
    orchestration_permission_denial_record = create_orchestration_permission_denial_record(
        reference_label,
    )
    orchestration_candidate_review_record = create_orchestration_candidate_review_record(
        command_text,
        approval_gate,
        v4_8_reference_contract,
        orchestration_review_scope_contract,
        non_execution_orchestration_boundary,
        orchestration_permission_denial_record,
    )
    orchestration_review_audit_record = create_orchestration_review_audit_record(
        approval_gate,
        v4_8_reference_contract,
        orchestration_review_scope_contract,
        non_execution_orchestration_boundary,
        orchestration_permission_denial_record,
        orchestration_candidate_review_record,
    )
    orchestration_readiness_summary = create_orchestration_readiness_summary(
        orchestration_review_audit_record
    )
    first_live_queue_execution_candidate_bridge = create_first_live_queue_execution_candidate_bridge(
        orchestration_readiness_summary
    )
    orchestration_candidate_review_id = orchestration_candidate_review_record["orchestration_candidate_review_id"]
    orchestration_candidate_review_record_payload = build_orchestration_candidate_review_record_payload(
        command_text,
        reference_label,
        human_operator,
        approval_gate.get("confirmation_token_valid", False),
        orchestration_candidate_review_id,
        orchestration_permission_denial_record,
        orchestration_review_audit_record["orchestration_review_audit_digest"],
    )

    if write_review_record:
        if approval_gate.get("local_orchestration_review_record_write_authorized", False):
            orchestration_candidate_review_write_record = write_live_queue_orchestration_candidate_review_record(
                review_output_directory or "",
                review_record_name or DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME,
                orchestration_candidate_review_record_payload,
            )
        else:
            orchestration_candidate_review_write_record = create_blocked_orchestration_candidate_review_write_record(
                "orchestration candidate review record write not authorized"
            )
    else:
        orchestration_candidate_review_write_record = create_blocked_orchestration_candidate_review_write_record(
            "orchestration candidate review record write not requested"
        )

    local_orchestration_review_record_written = orchestration_candidate_review_write_record.get(
        "local_orchestration_review_record_written", False
    )

    return {
        "schema": create_live_queue_orchestration_candidate_review_schema(),
        "orchestration_review_approval_gate": approval_gate,
        "v4_8_queue_routing_preview_reference_contract": v4_8_reference_contract,
        "orchestration_review_scope_contract": orchestration_review_scope_contract,
        "non_execution_orchestration_boundary": non_execution_orchestration_boundary,
        "orchestration_permission_denial_record": orchestration_permission_denial_record,
        "orchestration_candidate_review_record": orchestration_candidate_review_record,
        "orchestration_review_audit_record": orchestration_review_audit_record,
        "orchestration_readiness_summary": orchestration_readiness_summary,
        "first_live_queue_execution_candidate_bridge": first_live_queue_execution_candidate_bridge,
        "orchestration_candidate_review_record_payload": orchestration_candidate_review_record_payload,
        "orchestration_candidate_review_write_record": orchestration_candidate_review_write_record,
        "local_orchestration_review_record_written": local_orchestration_review_record_written,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
