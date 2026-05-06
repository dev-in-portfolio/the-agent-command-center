import hashlib
import json
import re
from pathlib import Path

NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION = "4.8.0"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_CANDIDATE_MODULE_VERSION = NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_STATUS = "NON_EXECUTING_QUEUE_ROUTING_PREVIEW_LOCAL_RECORD_ONLY"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_PHASE = "Non-Executing Queue Routing Preview Candidate"
NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_NON_EXECUTING_QUEUE_ROUTING_PREVIEW_CANDIDATE"
DEFAULT_TASK_CANDIDATE_LABEL = "station-chief-sandbox-observation-task-candidate"
DEFAULT_WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME = "non_executing_queue_routing_preview_candidate_record.json"

_DANGEROUS_BOOLEAN_FIELDS = [
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
    "real_queue_created",
    "queue_created",
    "queue_write_performed",
    "queue_dispatch_write_performed",
    "cron_write_performed",
    "queue_item_created",
    "queue_item_queued",
    "task_enqueued",
    "task_executed",
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


def safe_preview_record_name(record_name: str | None) -> str:
    if not isinstance(record_name, str) or not record_name:
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if record_name in {".", ".."}:
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if "/" in record_name or "\\" in record_name:
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    if not record_name.endswith(".json"):
        return DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME
    return record_name


def generate_queue_routing_preview_candidate_id(
    command: str,
    task_candidate_label: str,
    worker_template_label: str,
    runtime_version: str = NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
) -> str:
    task_norm = normalize_label(task_candidate_label, DEFAULT_TASK_CANDIDATE_LABEL)
    worker_norm = normalize_label(worker_template_label, DEFAULT_WORKER_TEMPLATE_LABEL)
    digest = sha256_digest(
        {
            "command": command,
            "runtime_version": runtime_version,
            "task_candidate_label": task_norm,
            "worker_template_label": worker_norm,
        }
    )
    return f"non-executing-queue-routing-preview-v4-8-{task_norm}-{worker_norm}-{digest[:12]}"


def create_non_executing_queue_routing_preview_schema() -> dict:
    return {
        "schema_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "status": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_STATUS,
        "preview_type": "non_executing_queue_routing_preview",
        "required_sections": [
            "queue_routing_preview_approval_gate",
            "hypothetical_task_candidate_reference",
            "worker_template_reference_contract",
            "queue_preview_scope_contract",
            "non_execution_routing_boundary",
            "routing_permission_denial_record",
            "routing_preview_candidate_record",
            "routing_preview_audit_record",
            "routing_preview_readiness_summary",
            "live_queue_orchestration_candidate_bridge",
        ],
        "required_token": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_queue_routing_preview_record_written": False,
        "real_queue_created": False,
        "queue_created": False,
        "queue_write_performed": False,
        "queue_dispatch_write_performed": False,
        "cron_write_performed": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_process_started": False,
        "worker_processes_started": False,
        "full_workforce_activation_performed": False,
        **_false_booleans(),
    }


def create_queue_routing_preview_approval_gate(
    task_candidate_label: str,
    worker_template_label: str,
    preview_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    preview_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN
    task_candidate_present = bool(task_candidate_label and str(task_candidate_label).strip())
    worker_template_present = bool(worker_template_label and str(worker_template_label).strip())
    human_operator_present = bool(human_operator and str(human_operator).strip())
    preview_output_directory_present = bool(preview_output_directory and str(preview_output_directory).strip())
    local_records_authorized = token_valid and human_operator_present and task_candidate_present and worker_template_present
    local_record_write_authorized = (
        local_records_authorized
        and preview_output_directory_present
        and preview_requested
    )
    return {
        "queue_routing_preview_approval_gate_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "gate_status": (
            "APPROVED_FOR_ONE_LOCAL_QUEUE_ROUTING_PREVIEW_RECORD"
            if local_records_authorized
            else "BLOCKED_PENDING_V4_8_QUEUE_ROUTING_PREVIEW_APPROVAL"
        ),
        "task_candidate_label": task_candidate_label,
        "worker_template_label": worker_template_label,
        "preview_output_directory": preview_output_directory,
        "confirmation_token_required": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "task_candidate_label_present": task_candidate_present,
        "worker_template_label_present": worker_template_present,
        "human_operator": human_operator,
        "human_operator_present": human_operator_present,
        "preview_requested": bool(preview_requested),
        "preview_output_directory_present": preview_output_directory_present,
        "local_queue_routing_preview_records_authorized": local_records_authorized,
        "local_queue_routing_preview_record_write_authorized": local_record_write_authorized,
        "real_queue_creation_authorized": False,
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


def create_hypothetical_task_candidate_reference(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_queue_routing_preview_records_authorized", False)
    return {
        "task_candidate_reference_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "reference_status": "CREATED" if authorized else "BLOCKED",
        "reference_count": 1 if authorized else 0,
        "task_candidate_label": approval_gate.get("task_candidate_label"),
        "task_candidate_label_normalized": normalize_label(
            approval_gate.get("task_candidate_label", ""),
            DEFAULT_TASK_CANDIDATE_LABEL,
        ),
        "task_candidate_is_metadata_only": True,
        "task_candidate_is_not_enqueued": True,
        "task_candidate_is_not_executed": True,
        "task_candidate_has_no_runtime_effect": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_worker_template_reference_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_queue_routing_preview_records_authorized", False)
    return {
        "worker_template_reference_contract_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "contract_status": "CREATED" if authorized else "BLOCKED",
        "reference_count": 1 if authorized else 0,
        "worker_template_label": approval_gate.get("worker_template_label"),
        "worker_template_label_normalized": normalize_label(
            approval_gate.get("worker_template_label", ""),
            DEFAULT_WORKER_TEMPLATE_LABEL,
        ),
        "worker_template_is_design_record": True,
        "worker_template_is_running_process": False,
        "worker_template_cannot_accept_live_task": True,
        "worker_process_start_authorized": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_queue_preview_scope_contract(
    approval_gate: dict,
    task_candidate_reference: dict,
    worker_template_reference_contract: dict,
) -> dict:
    passed = (
        approval_gate.get("local_queue_routing_preview_records_authorized", False)
        and task_candidate_reference.get("reference_status") == "CREATED"
        and worker_template_reference_contract.get("contract_status") == "CREATED"
    )
    return {
        "queue_preview_scope_contract_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "scope_status": "PASS" if passed else "BLOCKED",
        "exactly_one_task_candidate": True,
        "exactly_one_worker_template": True,
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_routing_performed": False,
        "no_batch_routing": True,
        "no_department_wide_routing": True,
        "no_live_task_activation": True,
        "no_process_activation": True,
        "workforce_size_target_reference": 47250,
        "full_workforce_activation_allowed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_execution_routing_boundary(
    approval_gate: dict,
    queue_preview_scope_contract: dict,
) -> dict:
    passed = (
        approval_gate.get("local_queue_routing_preview_records_authorized", False)
        and queue_preview_scope_contract.get("scope_status") == "PASS"
    )
    return {
        "non_execution_routing_boundary_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "boundary_status": "PASS" if passed else "BLOCKED",
        "routing_preview_record_is_local_metadata_only": True,
        "no_real_queue": True,
        "no_task_enqueue": True,
        "no_task_execution": True,
        "no_live_routing": True,
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


def create_routing_permission_denial_record(
    task_candidate_label: str,
    worker_template_label: str,
) -> dict:
    return {
        "routing_permission_denial_record_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "task_candidate_label": task_candidate_label,
        "worker_template_label": worker_template_label,
        "real_queue_creation_denied": True,
        "queue_writes_denied": True,
        "queue_dispatch_writes_denied": True,
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
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_routing_preview_candidate_record(
    command: str,
    approval_gate: dict,
    task_candidate_reference: dict,
    worker_template_reference_contract: dict,
    queue_preview_scope_contract: dict,
    non_execution_routing_boundary: dict,
    routing_permission_denial_record: dict,
) -> dict:
    candidate_ok = (
        approval_gate.get("local_queue_routing_preview_records_authorized", False)
        and task_candidate_reference.get("reference_status") == "CREATED"
        and worker_template_reference_contract.get("contract_status") == "CREATED"
        and queue_preview_scope_contract.get("scope_status") == "PASS"
        and non_execution_routing_boundary.get("boundary_status") == "PASS"
    )
    candidate_id = generate_queue_routing_preview_candidate_id(
        command,
        task_candidate_reference.get("task_candidate_label", DEFAULT_TASK_CANDIDATE_LABEL),
        worker_template_reference_contract.get("worker_template_label", DEFAULT_WORKER_TEMPLATE_LABEL),
    )
    candidate_record = {
        "routing_preview_candidate_record_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "routing_preview_candidate_id": candidate_id,
        "candidate_status": (
            "LOCAL_QUEUE_ROUTING_PREVIEW_CANDIDATE_RECORD_CREATED"
            if candidate_ok
            else "BLOCKED"
        ),
        "command": command,
        "task_candidate_label": task_candidate_reference.get("task_candidate_label"),
        "task_candidate_label_normalized": task_candidate_reference.get("task_candidate_label_normalized"),
        "worker_template_label": worker_template_reference_contract.get("worker_template_label"),
        "worker_template_label_normalized": worker_template_reference_contract.get("worker_template_label_normalized"),
        "human_operator": approval_gate.get("human_operator"),
        "preview_mode": "local_metadata_only",
        "queue_runtime_state": "not_created",
        "task_runtime_state": "not_enqueued_not_executed",
        "worker_runtime_state": "not_started",
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "routing_permission_denial_record": routing_permission_denial_record,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    candidate_record["routing_preview_candidate_digest"] = sha256_digest(
        {k: v for k, v in candidate_record.items() if k != "routing_preview_candidate_digest"}
    )
    return candidate_record


def create_routing_preview_audit_record(
    approval_gate: dict,
    hypothetical_task_candidate_reference: dict,
    worker_template_reference_contract: dict,
    queue_preview_scope_contract: dict,
    non_execution_routing_boundary: dict,
    routing_permission_denial_record: dict,
    routing_preview_candidate_record: dict,
) -> dict:
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "hypothetical_task_candidate_reference": sha256_digest(hypothetical_task_candidate_reference),
        "worker_template_reference_contract": sha256_digest(worker_template_reference_contract),
        "queue_preview_scope_contract": sha256_digest(queue_preview_scope_contract),
        "non_execution_routing_boundary": sha256_digest(non_execution_routing_boundary),
        "routing_permission_denial_record": sha256_digest(routing_permission_denial_record),
        "routing_preview_candidate_record": sha256_digest(routing_preview_candidate_record),
    }
    audit_ok = (
        routing_preview_candidate_record.get("candidate_status")
        == "LOCAL_QUEUE_ROUTING_PREVIEW_CANDIDATE_RECORD_CREATED"
        and not any(routing_preview_candidate_record.get(name, False) for name in _DANGEROUS_BOOLEAN_FIELDS)
    )
    audit_record = {
        "routing_preview_audit_record_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "section_digests": section_digests,
        "all_dangerous_booleans_false": True,
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }
    audit_record["routing_preview_audit_digest"] = sha256_digest(
        {k: v for k, v in audit_record.items() if k != "routing_preview_audit_digest"}
    )
    return audit_record


def create_routing_preview_readiness_summary(routing_preview_audit_record: dict) -> dict:
    ready = routing_preview_audit_record.get("audit_status") == "PASS"
    return {
        "routing_preview_readiness_summary_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "readiness_status": (
            "READY_FOR_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "next_layer": "Live Queue Orchestration Candidate Review",
        "v4_9_not_built": True,
        "no_queue_created_yet": True,
        "no_task_enqueue_yet": True,
        "no_task_execution_yet": True,
        "no_live_routing_yet": True,
        "no_worker_start": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_live_queue_orchestration_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("readiness_status") == "READY_FOR_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY"
    return {
        "live_queue_orchestration_candidate_bridge_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "bridge_status": (
            "READY_FOR_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY"
            if ready
            else "BLOCKED"
        ),
        "bridge_target": "Live Queue Orchestration Candidate Review",
        "no_live_queue_orchestration_in_v4_8": True,
        "no_task_assignment_in_v4_8": True,
        "no_worker_routing_in_v4_8": True,
        "no_worker_process_start_in_v4_8": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def build_queue_routing_preview_record_payload(
    command: str,
    task_candidate_label: str,
    worker_template_label: str,
    human_operator: str | None,
    approval_token_valid: bool,
    routing_preview_candidate_id: str,
    routing_permission_denial_record: dict,
    routing_preview_audit_digest: str,
) -> dict:
    payload = {
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "runtime_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "preview_type": "non_executing_queue_routing_preview",
        "command": command,
        "task_candidate_label": task_candidate_label,
        "worker_template_label": worker_template_label,
        "human_operator": human_operator,
        "approval_token_valid": approval_token_valid,
        "routing_preview_candidate_id": routing_preview_candidate_id,
        "routing_permission_denial_record": routing_permission_denial_record,
        "routing_preview_audit_digest": routing_preview_audit_digest,
        "safety_booleans": _false_booleans(),
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_non_executing_queue_routing_preview_record(
    preview_output_directory: str,
    record_name: str,
    payload: dict,
) -> dict:
    safe_name = safe_preview_record_name(record_name)
    out_dir = Path(preview_output_directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = (out_dir / safe_name).resolve()
    try:
        out_path.relative_to(out_dir)
    except ValueError:
        return create_blocked_queue_routing_preview_write_record("path traversal denied")
    out_path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "queue_routing_preview_write_record_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "write_status": "LOCAL_QUEUE_ROUTING_PREVIEW_RECORD_WRITTEN",
        "local_queue_routing_preview_record_written": True,
        "files_written_count": 1,
        "queue_routing_preview_output_directory": str(out_dir),
        "record_name": safe_name,
        "record_path": str(out_path),
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_queue_routing_preview_write_record(reason: str) -> dict:
    return {
        "queue_routing_preview_write_record_version": NON_EXECUTING_QUEUE_ROUTING_PREVIEW_MODULE_VERSION,
        "write_status": "BLOCKED",
        "block_reason": reason,
        "local_queue_routing_preview_record_written": False,
        "files_written_count": 0,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_non_executing_queue_routing_preview_bundle(
    result: dict | None,
    command: str | None = None,
    task_candidate_label: str | None = None,
    worker_template_label: str | None = None,
    preview_output_directory: str | None = None,
    preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    preview_requested: bool = False,
    write_preview_record: bool = False,
) -> dict:
    base_result = result or {}
    command_text = command or base_result.get("command", "check please")
    task_label = task_candidate_label or DEFAULT_TASK_CANDIDATE_LABEL
    worker_label = worker_template_label or DEFAULT_WORKER_TEMPLATE_LABEL
    approval_gate = create_queue_routing_preview_approval_gate(
        task_label,
        worker_label,
        preview_output_directory=preview_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        preview_requested=preview_requested,
    )
    hypothetical_task_candidate_reference = create_hypothetical_task_candidate_reference(approval_gate)
    worker_template_reference_contract = create_worker_template_reference_contract(approval_gate)
    queue_preview_scope_contract = create_queue_preview_scope_contract(
        approval_gate,
        hypothetical_task_candidate_reference,
        worker_template_reference_contract,
    )
    non_execution_routing_boundary = create_non_execution_routing_boundary(
        approval_gate,
        queue_preview_scope_contract,
    )
    routing_permission_denial_record = create_routing_permission_denial_record(
        task_label,
        worker_label,
    )
    routing_preview_candidate_record = create_routing_preview_candidate_record(
        command_text,
        approval_gate,
        hypothetical_task_candidate_reference,
        worker_template_reference_contract,
        queue_preview_scope_contract,
        non_execution_routing_boundary,
        routing_permission_denial_record,
    )
    routing_preview_audit_record = create_routing_preview_audit_record(
        approval_gate,
        hypothetical_task_candidate_reference,
        worker_template_reference_contract,
        queue_preview_scope_contract,
        non_execution_routing_boundary,
        routing_permission_denial_record,
        routing_preview_candidate_record,
    )
    routing_preview_readiness_summary = create_routing_preview_readiness_summary(routing_preview_audit_record)
    live_queue_orchestration_candidate_bridge = create_live_queue_orchestration_candidate_bridge(
        routing_preview_readiness_summary
    )
    routing_preview_candidate_id = routing_preview_candidate_record["routing_preview_candidate_id"]
    routing_preview_record_payload = build_queue_routing_preview_record_payload(
        command_text,
        task_label,
        worker_label,
        human_operator,
        approval_gate.get("confirmation_token_valid", False),
        routing_preview_candidate_id,
        routing_permission_denial_record,
        routing_preview_audit_record["routing_preview_audit_digest"],
    )

    if write_preview_record:
        if approval_gate.get("local_queue_routing_preview_record_write_authorized", False):
            queue_routing_preview_write_record = write_non_executing_queue_routing_preview_record(
                preview_output_directory or "",
                preview_record_name or DEFAULT_QUEUE_ROUTING_PREVIEW_RECORD_NAME,
                routing_preview_record_payload,
            )
        else:
            queue_routing_preview_write_record = create_blocked_queue_routing_preview_write_record(
                "queue routing preview record write not authorized"
            )
    else:
        queue_routing_preview_write_record = create_blocked_queue_routing_preview_write_record(
            "queue routing preview record write not requested"
        )

    local_queue_routing_preview_record_written = queue_routing_preview_write_record.get(
        "local_queue_routing_preview_record_written", False
    )
    execution_authorized = False
    return {
        "schema": create_non_executing_queue_routing_preview_schema(),
        "queue_routing_preview_approval_gate": approval_gate,
        "hypothetical_task_candidate_reference": hypothetical_task_candidate_reference,
        "worker_template_reference_contract": worker_template_reference_contract,
        "queue_preview_scope_contract": queue_preview_scope_contract,
        "non_execution_routing_boundary": non_execution_routing_boundary,
        "routing_permission_denial_record": routing_permission_denial_record,
        "routing_preview_candidate_record": routing_preview_candidate_record,
        "routing_preview_audit_record": routing_preview_audit_record,
        "routing_preview_readiness_summary": routing_preview_readiness_summary,
        "live_queue_orchestration_candidate_bridge": live_queue_orchestration_candidate_bridge,
        "routing_preview_record_payload": routing_preview_record_payload,
        "queue_routing_preview_write_record": queue_routing_preview_write_record,
        "local_queue_routing_preview_record_written": local_queue_routing_preview_record_written,
        "real_queue_created": False,
        "task_enqueued": False,
        "task_executed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "worker_process_started": False,
        "full_workforce_activation_performed": False,
        "execution_authorized": execution_authorized,
        "baseline_preserved": True,
        **_false_booleans(),
    }
