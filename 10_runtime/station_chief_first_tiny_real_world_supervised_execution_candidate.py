#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION = "4.0.0"
FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_STATUS = "FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_LOCAL_ONLY"
FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_PHASE = "First Tiny Real-World Supervised Execution Candidate"
FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE"
DEFAULT_ARTIFACT_NAME = "first_tiny_supervised_execution_candidate_proof.json"
DEFAULT_CANDIDATE_LABEL = "first-tiny-real-world-supervised-execution-candidate"
DEFAULT_FORBIDDEN_PATHS = [
    "02_departments/*",
    "04_workflow_templates/*",
    "09_exports/dashboard_seed.json",
    "09_exports/org_chart_export.json",
    "09_exports/master_department_list.md",
    "any Devinization overlay file",
    "any ownership metadata file",
    "any credential/secret/env file",
    "any production/deployment file",
]
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
    "live_task_assignment_performed",
    "live_worker_routing_performed",
    "live_orchestration_performed",
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


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_v4_candidate_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.strip().lower()).strip("-")
    return normalized or DEFAULT_CANDIDATE_LABEL


def safe_artifact_name(artifact_name: str | None) -> str:
    if not artifact_name:
        return DEFAULT_ARTIFACT_NAME
    candidate = str(artifact_name).strip()
    if candidate in {".", "..", ""}:
        return DEFAULT_ARTIFACT_NAME
    if candidate.endswith(".json") and "/" not in candidate and "\\" not in candidate:
        return candidate
    return DEFAULT_ARTIFACT_NAME


def generate_first_tiny_real_world_supervised_execution_candidate_id(
    command: str,
    candidate_label: str,
    runtime_version: str = FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_label = normalize_v4_candidate_label(candidate_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{candidate_label}")
    return f"first-tiny-real-world-supervised-execution-candidate-v4-0-{normalized_label}-{digest[:12]}"


def _false_booleans() -> dict:
    return {name: False for name in DANGEROUS_BOOLEAN_FIELDS}


def _safe_path_digests(paths: list[str]) -> dict:
    return {"paths": list(paths), "digest": sha256_digest(paths)}


def create_first_tiny_real_world_supervised_execution_candidate_schema() -> dict:
    return {
        "first_tiny_real_world_supervised_execution_candidate_schema_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "schema_status": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_STATUS,
        "candidate_type": "local_deterministic_reversible_proof_artifact",
        "required_sections": [
            "first_tiny_real_world_supervised_execution_candidate_approval_gate",
            "local_proof_artifact_candidate_contract",
            "explicit_output_directory_boundary_contract",
            "forbidden_path_contract",
            "local_only_execution_envelope",
            "candidate_pre_action_audit_proof",
            "local_proof_artifact_execution_record",
            "post_action_verification_record",
            "cleanup_rollback_instruction_record",
            "first_tiny_candidate_ledger",
            "first_tiny_candidate_readiness_summary",
            "post_action_verification_and_audit_review_bridge",
        ],
        "required_confirmation_token": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_proof_artifact_write_performed": False,
        **_false_booleans(),
    }


def create_first_tiny_real_world_supervised_execution_candidate_approval_gate(
    candidate_label: str,
    output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    token_valid = confirmation_token == FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN
    output_directory_present = bool(output_directory and str(output_directory).strip())
    human_operator_present = bool(human_operator and str(human_operator).strip())
    local_candidate_records_authorized = token_valid
    local_proof_artifact_write_authorized = token_valid and output_directory_present and human_operator_present
    gate_status = (
        "APPROVED_FOR_LOCAL_PROOF_ARTIFACT_WRITE"
        if local_proof_artifact_write_authorized
        else "BLOCKED_PENDING_V4_LOCAL_CANDIDATE_APPROVAL"
    )
    return {
        "first_tiny_real_world_supervised_execution_candidate_approval_gate_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "candidate_label": candidate_label,
        "candidate_label_normalized": normalize_v4_candidate_label(candidate_label),
        "output_directory": output_directory,
        "human_operator": human_operator,
        "gate_status": gate_status,
        "confirmation_token_required": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_candidate_records_authorized": local_candidate_records_authorized,
        "local_proof_artifact_write_authorized": local_proof_artifact_write_authorized,
        "local_proof_artifact_write_performed": False,
        "baseline_preserved": True,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "dns_resolution_authorized": False,
        "outbound_connection_authorized": False,
        "inbound_connection_authorized": False,
        "webhook_call_authorized": False,
        "credential_use_authorized": False,
        "credential_vault_access_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "deployment_rollback_authorized": False,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "real_external_tool_invocation_authorized": False,
        "real_task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "worker_process_start_authorized": False,
        "repo_mutation_authorized": False,
        "full_workforce_activation_authorized": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_local_proof_artifact_candidate_contract(approval_gate: dict, artifact_name: str | None = None) -> dict:
    token_valid = approval_gate.get("local_candidate_records_authorized", False)
    candidate_status = "LOCAL_PROOF_ARTIFACT_CANDIDATE_CONTRACT_CREATED" if token_valid else "BLOCKED"
    safe_name = safe_artifact_name(artifact_name)
    candidate_label = approval_gate.get("candidate_label", DEFAULT_CANDIDATE_LABEL)
    candidate_id = generate_first_tiny_real_world_supervised_execution_candidate_id(
        "check please",
        candidate_label,
        runtime_version=FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
    )
    return {
        "local_proof_artifact_candidate_contract_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "contract_status": candidate_status,
        "candidate_type": "local_deterministic_reversible_proof_artifact",
        "candidate_id": candidate_id,
        "candidate_label": candidate_label,
        "candidate_label_normalized": normalize_v4_candidate_label(candidate_label),
        "artifact_name": safe_name,
        "local_only": True,
        "deterministic": True,
        "reversible": True,
        "single_file_only": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_explicit_output_directory_boundary_contract(approval_gate: dict) -> dict:
    token_valid = approval_gate.get("local_proof_artifact_write_authorized", False)
    output_directory = approval_gate.get("output_directory")
    boundary_status = "EXPLICIT_OUTPUT_DIRECTORY_BOUNDARY_CONTRACT_CREATED" if token_valid else "BLOCKED"
    resolved_output_directory = None
    if token_valid and output_directory:
        resolved_output_directory = str(Path(output_directory).expanduser().resolve())
    return {
        "explicit_output_directory_boundary_contract_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "contract_status": boundary_status,
        "output_directory": output_directory,
        "resolved_output_directory": resolved_output_directory,
        "writes_limited_to_output_directory_only": True,
        "no_protected_path_writes": True,
        "repo_root_write_allowed_only_if_output_directory_is_repo_root": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_forbidden_path_contract() -> dict:
    return {
        "forbidden_path_contract_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "forbidden_paths": list(DEFAULT_FORBIDDEN_PATHS),
        "forbidden_paths_digest": sha256_digest(DEFAULT_FORBIDDEN_PATHS),
        "protected_baseline_mutation": False,
        "devinization_overlay_mutation": False,
        "dashboard_export_mutation": False,
        "ownership_metadata_mutation": False,
        "repo_root_mutation": False,
        **_false_booleans(),
    }


def create_local_only_execution_envelope(
    approval_gate: dict,
    output_boundary_contract: dict,
    forbidden_path_contract: dict,
) -> dict:
    token_valid = approval_gate.get("local_proof_artifact_write_authorized", False)
    boundary_created = output_boundary_contract.get("contract_status") == "EXPLICIT_OUTPUT_DIRECTORY_BOUNDARY_CONTRACT_CREATED"
    envelope_status = "LOCAL_ONLY_EXECUTION_ENVELOPE_CREATED" if token_valid and boundary_created else "BLOCKED"
    return {
        "local_only_execution_envelope_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "envelope_status": envelope_status,
        "allowed_action": "write_one_local_deterministic_reversible_proof_artifact_to_explicit_output_directory",
        "local_only": True,
        "deterministic": True,
        "reversible": True,
        "single_file_only": True,
        "writes_only_inside_output_directory": True,
        "output_directory_boundary": output_boundary_contract.get("resolved_output_directory") or output_boundary_contract.get("output_directory"),
        "forbidden_paths": list(forbidden_path_contract.get("forbidden_paths", [])),
        "local_proof_artifact_write_allowed": bool(token_valid and boundary_created),
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_candidate_pre_action_audit_proof(
    approval_gate: dict,
    candidate_contract: dict,
    output_boundary_contract: dict,
    forbidden_path_contract: dict,
    local_only_execution_envelope: dict,
) -> dict:
    gate_ok = approval_gate.get("local_proof_artifact_write_authorized", False)
    contract_ok = candidate_contract.get("contract_status") == "LOCAL_PROOF_ARTIFACT_CANDIDATE_CONTRACT_CREATED"
    boundary_ok = output_boundary_contract.get("contract_status") == "EXPLICIT_OUTPUT_DIRECTORY_BOUNDARY_CONTRACT_CREATED"
    envelope_ok = local_only_execution_envelope.get("envelope_status") == "LOCAL_ONLY_EXECUTION_ENVELOPE_CREATED"
    proof_status = "PASS" if gate_ok and contract_ok and boundary_ok and envelope_ok else "BLOCKED"
    section_digests = {
        "approval_gate": sha256_digest(approval_gate),
        "candidate_contract": sha256_digest(candidate_contract),
        "output_boundary_contract": sha256_digest(output_boundary_contract),
        "forbidden_path_contract": sha256_digest(forbidden_path_contract),
        "local_only_execution_envelope": sha256_digest(local_only_execution_envelope),
    }
    return {
        "candidate_pre_action_audit_proof_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "candidate_pre_action_audit_proof_status": proof_status,
        "approval_gate_valid": gate_ok,
        "candidate_contract_valid": contract_ok,
        "output_boundary_contract_valid": boundary_ok,
        "forbidden_path_contract_valid": forbidden_path_contract.get("forbidden_paths") == list(DEFAULT_FORBIDDEN_PATHS),
        "local_only_execution_envelope_valid": envelope_ok,
        "section_digests": section_digests,
        "section_digests_digest": sha256_digest(section_digests),
        "local_proof_artifact_write_performed": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def build_local_proof_artifact_payload(
    command: str,
    candidate_label: str,
    human_operator: str,
    output_directory: str,
    artifact_name: str,
    approval_gate: dict,
    candidate_pre_action_audit_proof: dict,
) -> dict:
    safe_candidate_label = normalize_v4_candidate_label(candidate_label)
    payload = {
        "runtime_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "candidate_label": candidate_label,
        "candidate_label_normalized": safe_candidate_label,
        "candidate_id": generate_first_tiny_real_world_supervised_execution_candidate_id(command, candidate_label),
        "command": command,
        "human_operator": human_operator,
        "output_directory": str(output_directory),
        "artifact_name": artifact_name,
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "approval_token_required": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
        "forbidden_paths": list(DEFAULT_FORBIDDEN_PATHS),
        "cleanup_instructions": [
            "remove only the approved output artifact inside the approved output directory",
            "do not use git reset",
            "do not terminate processes",
            "do not terminate workers",
            "do not roll back production",
        ],
        "verification_requirements": [
            "artifact exists",
            "artifact name matches expectation",
            "artifact parses as JSON",
            "artifact path stays inside approved output directory",
        ],
        "timestamp_mode": "deterministic_no_wall_clock_timestamp",
        "baseline_preserved": True,
        "local_proof_artifact_write_performed": False,
        "safety_booleans": _false_booleans(),
        "candidate_pre_action_audit_proof_digest": sha256_digest(candidate_pre_action_audit_proof),
    }
    payload["payload_digest"] = sha256_digest(payload)
    return payload


def write_local_proof_artifact(output_directory: str | Path, artifact_name: str, payload: dict) -> dict:
    output_dir = Path(output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_artifact_name(artifact_name)
    artifact_path = (output_dir / safe_name).resolve()
    try:
        artifact_path.relative_to(output_dir)
    except ValueError as exc:
        raise ValueError("artifact path escaped approved output directory") from exc
    artifact_path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    return {
        "local_proof_artifact_write_performed": True,
        "artifact_name": safe_name,
        "artifact_path": str(artifact_path),
        "resolved_output_directory": str(output_dir),
        "local_only": True,
        "deterministic": True,
        "reversible": True,
        "baseline_preserved": True,
        "repo_files_modified": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_blocked_local_proof_artifact_execution_record(reason: str) -> dict:
    return {
        "local_proof_artifact_write_performed": False,
        "execution_status": "BLOCKED",
        "block_reason": reason,
        "artifact_name": DEFAULT_ARTIFACT_NAME,
        "artifact_path": None,
        "resolved_output_directory": None,
        "baseline_preserved": True,
        "repo_files_modified": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_post_action_verification_record(execution_record: dict, expected_artifact_name: str) -> dict:
    artifact_path = execution_record.get("artifact_path")
    artifact_name = execution_record.get("artifact_name")
    artifact_exists = bool(execution_record.get("local_proof_artifact_write_performed") and artifact_path and Path(artifact_path).exists())
    name_matches = artifact_name == safe_artifact_name(expected_artifact_name)
    json_parses = False
    if artifact_exists:
        try:
            json.loads(Path(artifact_path).read_text(encoding="utf-8"))
            json_parses = True
        except Exception:
            json_parses = False
    status = "PASS" if artifact_exists and name_matches and json_parses else "BLOCKED"
    return {
        "post_action_verification_record_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "post_action_verification_status": status,
        "artifact_exists": artifact_exists,
        "artifact_name_matches": name_matches,
        "artifact_json_parses": json_parses,
        "artifact_path": artifact_path,
        "expected_artifact_name": safe_artifact_name(expected_artifact_name),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_rollback_instruction_record(execution_record: dict) -> dict:
    return {
        "cleanup_rollback_instruction_record_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "cleanup_scope": "approved_output_directory_only",
        "cleanup_allowed_only_inside_output_directory": True,
        "cleanup_performed_by_runtime": False,
        "git_reset_allowed": False,
        "production_rollback_allowed": False,
        "process_termination_allowed": False,
        "worker_termination_allowed": False,
        "external_state_mutation_allowed": False,
        "execution_authorized": False,
        "artifact_path": execution_record.get("artifact_path"),
        **_false_booleans(),
    }


def create_first_tiny_candidate_ledger(
    pre_action_audit_proof: dict,
    execution_record: dict,
    post_action_verification_record: dict,
) -> dict:
    pre_ok = pre_action_audit_proof.get("candidate_pre_action_audit_proof_status") == "PASS"
    exec_ok = bool(execution_record.get("local_proof_artifact_write_performed"))
    verify_ok = post_action_verification_record.get("post_action_verification_status") == "PASS"
    ledger_status = "PASS" if pre_ok and exec_ok and verify_ok else "BLOCKED"
    ledger = {
        "first_tiny_candidate_ledger_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "ledger_status": ledger_status,
        "pre_action_audit_proof_digest": sha256_digest(pre_action_audit_proof),
        "execution_record_digest": sha256_digest(execution_record),
        "post_action_verification_record_digest": sha256_digest(post_action_verification_record),
        "baseline_preserved": True,
        "local_proof_artifact_write_performed": bool(execution_record.get("local_proof_artifact_write_performed")),
        "execution_authorized": False,
        **_false_booleans(),
    }
    ledger["ledger_digest"] = sha256_digest(ledger)
    return ledger


def create_first_tiny_candidate_readiness_summary(
    ledger: dict,
    post_action_verification_record: dict,
) -> dict:
    ready = ledger.get("ledger_status") == "PASS" and post_action_verification_record.get("post_action_verification_status") == "PASS"
    return {
        "first_tiny_candidate_readiness_summary_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW" if ready else "BLOCKED",
        "next_layer": "Post-Action Verification and Audit Review",
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        "local_proof_artifact_write_performed": bool(ledger.get("local_proof_artifact_write_performed")),
        **_false_booleans(),
    }


def create_post_action_verification_and_audit_review_bridge(summary: dict) -> dict:
    ready = summary.get("ready_for_next_layer", False)
    return {
        "post_action_verification_and_audit_review_bridge_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_1_POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW" if ready else "BLOCKED",
        "next_layer": "v4.1 post-action verification and audit review",
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_first_tiny_real_world_supervised_execution_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    candidate_label: str | None = None,
    output_directory: str | None = None,
    artifact_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execute_local_proof_artifact_write: bool = False,
) -> dict:
    result = dict(result or {})
    command = command or result.get("command", "check please")
    candidate_label = candidate_label or "first tiny real-world supervised execution candidate"
    safe_name = safe_artifact_name(artifact_name)
    schema = create_first_tiny_real_world_supervised_execution_candidate_schema()
    approval_gate = create_first_tiny_real_world_supervised_execution_candidate_approval_gate(
        candidate_label,
        output_directory=output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
    )
    candidate_contract = create_local_proof_artifact_candidate_contract(approval_gate, safe_name)
    output_boundary_contract = create_explicit_output_directory_boundary_contract(approval_gate)
    forbidden_path_contract = create_forbidden_path_contract()
    local_only_execution_envelope = create_local_only_execution_envelope(approval_gate, output_boundary_contract, forbidden_path_contract)
    candidate_pre_action_audit_proof = create_candidate_pre_action_audit_proof(
        approval_gate,
        candidate_contract,
        output_boundary_contract,
        forbidden_path_contract,
        local_only_execution_envelope,
    )

    if execute_local_proof_artifact_write and approval_gate.get("local_proof_artifact_write_authorized", False) and candidate_pre_action_audit_proof.get("candidate_pre_action_audit_proof_status") == "PASS":
        payload = build_local_proof_artifact_payload(
            command=command,
            candidate_label=candidate_label,
            human_operator=human_operator or "",
            output_directory=output_boundary_contract.get("resolved_output_directory") or output_directory or "",
            artifact_name=safe_name,
            approval_gate=approval_gate,
            candidate_pre_action_audit_proof=candidate_pre_action_audit_proof,
        )
        execution_record = write_local_proof_artifact(output_directory or output_boundary_contract.get("resolved_output_directory") or ".", safe_name, payload)
    elif execute_local_proof_artifact_write:
        execution_record = create_blocked_local_proof_artifact_execution_record("local proof artifact write not authorized")
        payload = None
    else:
        execution_record = create_blocked_local_proof_artifact_execution_record("local proof artifact write not requested")
        payload = None

    post_action_verification_record = create_post_action_verification_record(execution_record, safe_name)
    cleanup_rollback_instruction_record = create_cleanup_rollback_instruction_record(execution_record)
    first_tiny_candidate_ledger = create_first_tiny_candidate_ledger(
        candidate_pre_action_audit_proof,
        execution_record,
        post_action_verification_record,
    )
    first_tiny_candidate_readiness_summary = create_first_tiny_candidate_readiness_summary(
        first_tiny_candidate_ledger,
        post_action_verification_record,
    )
    post_action_verification_and_audit_review_bridge = create_post_action_verification_and_audit_review_bridge(first_tiny_candidate_readiness_summary)

    bundle = {
        "first_tiny_real_world_supervised_execution_candidate_bundle_version": FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_MODULE_VERSION,
        "schema": schema,
        "first_tiny_real_world_supervised_execution_candidate_approval_gate": approval_gate,
        "local_proof_artifact_candidate_contract": candidate_contract,
        "explicit_output_directory_boundary_contract": output_boundary_contract,
        "forbidden_path_contract": forbidden_path_contract,
        "local_only_execution_envelope": local_only_execution_envelope,
        "candidate_pre_action_audit_proof": candidate_pre_action_audit_proof,
        "local_proof_artifact_execution_record": execution_record,
        "post_action_verification_record": post_action_verification_record,
        "cleanup_rollback_instruction_record": cleanup_rollback_instruction_record,
        "first_tiny_candidate_ledger": first_tiny_candidate_ledger,
        "first_tiny_candidate_readiness_summary": first_tiny_candidate_readiness_summary,
        "post_action_verification_and_audit_review_bridge": post_action_verification_and_audit_review_bridge,
        "local_proof_artifact_write_performed": bool(execution_record.get("local_proof_artifact_write_performed")),
        "local_proof_artifact_write_authorized": approval_gate.get("local_proof_artifact_write_authorized", False),
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    if payload is not None:
        bundle["local_proof_artifact_payload"] = payload
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
