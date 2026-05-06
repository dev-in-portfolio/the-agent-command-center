#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION = "4.2.0"
SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_STATUS = "SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_LOCAL_ONLY"
SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_PHASE = "Supervised Rollback / Cleanup Candidate"
SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_APPROVAL_TOKEN = "YES_I_APPROVE_SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE"
APPROVED_V4_PROOF_ARTIFACT_NAME = "first_tiny_supervised_execution_candidate_proof.json"
DEFAULT_CLEANUP_LABEL = "supervised-rollback-cleanup-candidate"

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


def _false_booleans() -> dict:
    return {name: False for name in DANGEROUS_BOOLEAN_FIELDS}


def normalize_cleanup_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.strip().lower()).strip("-")
    return normalized or DEFAULT_CLEANUP_LABEL


def generate_supervised_rollback_cleanup_candidate_id(
    command: str,
    cleanup_label: str,
    runtime_version: str = SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
) -> str:
    normalized_label = normalize_cleanup_label(cleanup_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{cleanup_label}")
    return f"supervised-rollback-cleanup-candidate-v4-2-{normalized_label}-{digest[:12]}"


def create_supervised_rollback_cleanup_candidate_schema() -> dict:
    return {
        "supervised_rollback_cleanup_candidate_schema_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "schema_status": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_STATUS,
        "cleanup_type": "supervised_local_artifact_cleanup",
        "required_sections": [
            "supervised_rollback_cleanup_candidate_approval_gate",
            "cleanup_candidate_contract",
            "artifact_pre_cleanup_verification_record",
            "cleanup_path_containment_record",
            "cleanup_scope_envelope",
            "cleanup_execution_record",
            "post_cleanup_verification_record",
            "cleanup_audit_record",
            "cleanup_closeout_ledger",
            "cleanup_readiness_summary",
            "limited_live_worker_activation_candidate_bridge",
        ],
        "required_confirmation_token": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_cleanup_performed": False,
        **_false_booleans(),
    }


def create_supervised_rollback_cleanup_candidate_approval_gate(
    cleanup_label: str,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    cleanup_requested: bool = False,
) -> dict:
    token_valid = confirmation_token == SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_APPROVAL_TOKEN
    human_present = bool(human_operator and str(human_operator).strip())
    artifact_present = bool(artifact_path and str(artifact_path).strip())
    expected_output_present = bool(expected_output_directory and str(expected_output_directory).strip())
    local_cleanup_records_authorized = token_valid and human_present
    local_cleanup_execution_authorized = (
        token_valid and human_present and artifact_present and expected_output_present and bool(cleanup_requested)
    )
    gate_status = (
        "APPROVED_FOR_ONE_LOCAL_ARTIFACT_CLEANUP"
        if local_cleanup_records_authorized
        else "BLOCKED_PENDING_V4_2_CLEANUP_APPROVAL"
    )
    return {
        "supervised_rollback_cleanup_candidate_approval_gate_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "cleanup_label": cleanup_label,
        "cleanup_label_normalized": normalize_cleanup_label(cleanup_label),
        "artifact_path": artifact_path,
        "expected_output_directory": expected_output_directory,
        "human_operator": human_operator,
        "cleanup_requested": bool(cleanup_requested),
        "gate_status": gate_status,
        "confirmation_token_required": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "artifact_path_present": artifact_present,
        "expected_output_directory_present": expected_output_present,
        "local_cleanup_records_authorized": local_cleanup_records_authorized,
        "local_cleanup_execution_authorized": local_cleanup_execution_authorized,
        "baseline_preserved": True,
        "local_cleanup_performed": False,
        "directory_deletion_allowed": False,
        "repo_mutation_authorized": False,
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
        "full_workforce_activation_authorized": False,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_candidate_contract(approval_gate: dict) -> dict:
    authorized = approval_gate.get("local_cleanup_records_authorized", False)
    return {
        "cleanup_candidate_contract_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "contract_status": "CLEANUP_CANDIDATE_CONTRACT_CREATED" if authorized else "BLOCKED",
        "approved_action": "delete_exactly_one_v4_0_local_proof_artifact",
        "approved_artifact_name": APPROVED_V4_PROOF_ARTIFACT_NAME,
        "no_directory_deletion": True,
        "no_repo_mutation": True,
        "no_external_action": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_artifact_pre_cleanup_verification_record(artifact_path: str | None) -> dict:
    if not artifact_path:
        return {
            "artifact_pre_cleanup_verification_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
            "verification_status": "BLOCKED",
            "artifact_path": None,
            "artifact_exists": False,
            "artifact_is_file": False,
            "artifact_suffix_json": False,
            "artifact_name_matches": False,
            "artifact_json_parses": False,
            "runtime_version_is_4_0_0": False,
            "candidate_type_looks_correct": False,
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }

    resolved = Path(artifact_path).expanduser().resolve()
    artifact_exists = resolved.exists()
    artifact_is_file = resolved.is_file()
    artifact_suffix_json = resolved.suffix == ".json"
    artifact_name_matches = resolved.name == APPROVED_V4_PROOF_ARTIFACT_NAME
    artifact_json_parses = False
    runtime_version_ok = False
    candidate_type_ok = False
    if artifact_exists and artifact_is_file and artifact_suffix_json:
        try:
            parsed = json.loads(resolved.read_text(encoding="utf-8"))
            artifact_json_parses = isinstance(parsed, dict)
            if artifact_json_parses:
                runtime_version = parsed.get("runtime_version")
                runtime_version_ok = runtime_version in {None, "4.0.0"}
                candidate_type = parsed.get("candidate_type") or parsed.get("artifact_type") or parsed.get("proof_type")
                if candidate_type is None:
                    candidate_type_ok = True
                else:
                    candidate_type_ok = "proof" in str(candidate_type).lower() or "deterministic" in str(candidate_type).lower()
        except Exception:
            artifact_json_parses = False
    verification_status = "PASS" if (
        artifact_exists
        and artifact_is_file
        and artifact_suffix_json
        and artifact_name_matches
        and artifact_json_parses
        and runtime_version_ok
        and candidate_type_ok
    ) else "BLOCKED"
    return {
        "artifact_pre_cleanup_verification_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "verification_status": verification_status,
        "artifact_path": str(resolved),
        "artifact_exists": artifact_exists,
        "artifact_is_file": artifact_is_file,
        "artifact_suffix_json": artifact_suffix_json,
        "artifact_name_matches": artifact_name_matches,
        "artifact_json_parses": artifact_json_parses,
        "runtime_version_is_4_0_0": runtime_version_ok,
        "candidate_type_looks_correct": candidate_type_ok,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_path_containment_record(artifact_path: str | None, expected_output_directory: str | None) -> dict:
    if not artifact_path or not expected_output_directory:
        return {
            "cleanup_path_containment_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
            "containment_status": "BLOCKED",
            "artifact_path": artifact_path,
            "expected_output_directory": expected_output_directory,
            "artifact_path_contained_within_expected_output_directory": False,
            "expected_output_directory_exists": bool(expected_output_directory and Path(expected_output_directory).expanduser().exists()),
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }
    artifact_resolved = Path(artifact_path).expanduser().resolve()
    expected_resolved = Path(expected_output_directory).expanduser().resolve()
    expected_exists = expected_resolved.exists()
    contained = False
    if expected_exists and artifact_resolved.exists() and not artifact_resolved.is_dir():
        try:
            artifact_resolved.relative_to(expected_resolved)
            contained = True
        except ValueError:
            contained = False
    return {
        "cleanup_path_containment_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "containment_status": "PASS" if contained else "BLOCKED",
        "artifact_path": str(artifact_resolved),
        "expected_output_directory": str(expected_resolved),
        "artifact_path_contained_within_expected_output_directory": contained,
        "expected_output_directory_exists": expected_exists,
        "artifact_is_directory": artifact_resolved.is_dir(),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_scope_envelope(
    approval_gate: dict,
    cleanup_candidate_contract: dict,
    artifact_pre_cleanup_verification_record: dict,
    cleanup_path_containment_record: dict,
) -> dict:
    cleanup_requested = bool(approval_gate.get("cleanup_requested", False))
    execution_authorized = (
        approval_gate.get("local_cleanup_execution_authorized", False)
        and cleanup_candidate_contract.get("contract_status") == "CLEANUP_CANDIDATE_CONTRACT_CREATED"
        and artifact_pre_cleanup_verification_record.get("verification_status") == "PASS"
        and cleanup_path_containment_record.get("containment_status") == "PASS"
    )
    return {
        "cleanup_scope_envelope_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "envelope_status": "PASS" if execution_authorized else "BLOCKED_PENDING_CLEANUP_EXECUTION_REQUEST",
        "approved_cleanup_action": "delete_exactly_one_file_inside_expected_output_directory",
        "cleanup_requested": cleanup_requested,
        "cleanup_requested_explicitly": cleanup_requested,
        "cleanup_execution_authorized": execution_authorized,
        "directory_deletion_allowed": False,
        "repo_mutation_allowed": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_blocked_cleanup_execution_record(reason: str) -> dict:
    return {
        "cleanup_execution_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "cleanup_execution_status": "BLOCKED",
        "block_reason": reason,
        "local_cleanup_performed": False,
        "artifact_deleted": False,
        "deleted_artifact_path": None,
        "expected_output_directory": None,
        "deleted_file_count": 0,
        "directories_deleted": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def execute_supervised_local_artifact_cleanup(
    artifact_path: str,
    expected_output_directory: str,
    cleanup_scope_envelope: dict,
) -> dict:
    if cleanup_scope_envelope.get("cleanup_execution_authorized") is not True or cleanup_scope_envelope.get("envelope_status") != "PASS":
        return create_blocked_cleanup_execution_record("cleanup scope envelope blocked")
    artifact_resolved = Path(artifact_path).expanduser().resolve()
    expected_resolved = Path(expected_output_directory).expanduser().resolve()
    if not expected_resolved.exists():
        return create_blocked_cleanup_execution_record("expected output directory missing")
    if not artifact_resolved.exists():
        return create_blocked_cleanup_execution_record("artifact missing")
    if artifact_resolved.is_dir():
        return create_blocked_cleanup_execution_record("artifact is directory")
    if artifact_resolved.name != APPROVED_V4_PROOF_ARTIFACT_NAME:
        return create_blocked_cleanup_execution_record("artifact name mismatch")
    try:
        artifact_resolved.relative_to(expected_resolved)
    except ValueError:
        return create_blocked_cleanup_execution_record("artifact outside expected output directory")
    artifact_resolved.unlink()
    return {
        "cleanup_execution_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "cleanup_execution_status": "LOCAL_ARTIFACT_CLEANUP_PERFORMED",
        "local_cleanup_performed": True,
        "artifact_deleted": True,
        "deleted_artifact_path": str(artifact_resolved),
        "expected_output_directory": str(expected_resolved),
        "deleted_file_count": 1,
        "directories_deleted": False,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_post_cleanup_verification_record(cleanup_execution_record: dict, artifact_path: str | None) -> dict:
    artifact_resolved = Path(artifact_path).expanduser().resolve() if artifact_path else None
    exists_after = artifact_resolved.exists() if artifact_resolved else False
    status = "PASS" if cleanup_execution_record.get("cleanup_execution_status") == "LOCAL_ARTIFACT_CLEANUP_PERFORMED" and not exists_after else "BLOCKED"
    return {
        "post_cleanup_verification_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "verification_status": status,
        "artifact_path": str(artifact_resolved) if artifact_resolved else None,
        "artifact_exists_after_cleanup": exists_after,
        "cleanup_execution_status": cleanup_execution_record.get("cleanup_execution_status"),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_audit_record(
    approval_gate: dict,
    cleanup_candidate_contract: dict,
    artifact_pre_cleanup_verification_record: dict,
    cleanup_path_containment_record: dict,
    cleanup_scope_envelope: dict,
    cleanup_execution_record: dict,
    post_cleanup_verification_record: dict,
) -> dict:
    audit_ok = (
        cleanup_execution_record.get("cleanup_execution_status") == "LOCAL_ARTIFACT_CLEANUP_PERFORMED"
        and post_cleanup_verification_record.get("verification_status") == "PASS"
    )
    record = {
        "cleanup_audit_record_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "audit_status": "PASS" if audit_ok else "BLOCKED",
        "approval_gate_digest": sha256_digest(approval_gate),
        "cleanup_candidate_contract_digest": sha256_digest(cleanup_candidate_contract),
        "artifact_pre_cleanup_verification_record_digest": sha256_digest(artifact_pre_cleanup_verification_record),
        "cleanup_path_containment_record_digest": sha256_digest(cleanup_path_containment_record),
        "cleanup_scope_envelope_digest": sha256_digest(cleanup_scope_envelope),
        "cleanup_execution_record_digest": sha256_digest(cleanup_execution_record),
        "post_cleanup_verification_record_digest": sha256_digest(post_cleanup_verification_record),
        "local_cleanup_performed": bool(cleanup_execution_record.get("local_cleanup_performed")),
        "artifact_deleted": bool(cleanup_execution_record.get("artifact_deleted")),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    record["audit_digest"] = sha256_digest(record)
    return record


def create_cleanup_closeout_ledger(cleanup_audit_record: dict) -> dict:
    ledger = {
        "cleanup_closeout_ledger_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "ledger_status": "PASS" if cleanup_audit_record.get("audit_status") == "PASS" else "BLOCKED",
        "cleanup_audit_record_digest": sha256_digest(cleanup_audit_record),
        "local_cleanup_performed": bool(cleanup_audit_record.get("local_cleanup_performed")),
        "artifact_deleted": bool(cleanup_audit_record.get("artifact_deleted")),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    ledger["ledger_digest"] = sha256_digest(ledger)
    return ledger


def create_cleanup_readiness_summary(cleanup_closeout_ledger: dict) -> dict:
    ready = cleanup_closeout_ledger.get("ledger_status") == "PASS"
    return {
        "cleanup_readiness_summary_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "readiness_status": "READY_FOR_LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Limited Live Worker Activation Candidate",
        "v4_3_built": False,
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_limited_live_worker_activation_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("ready_for_next_layer", False)
    return {
        "limited_live_worker_activation_candidate_bridge_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_3_LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "v4.3 limited live worker activation candidate",
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_supervised_rollback_cleanup_candidate_bundle(
    result: dict | None,
    command: str | None = None,
    cleanup_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    cleanup_requested: bool = False,
    execute_cleanup: bool = False,
) -> dict:
    result = dict(result or {})
    command = command or result.get("command", "check please")
    cleanup_label = cleanup_label or "supervised rollback cleanup candidate"
    approval_gate = create_supervised_rollback_cleanup_candidate_approval_gate(
        cleanup_label,
        artifact_path=artifact_path,
        expected_output_directory=expected_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        cleanup_requested=cleanup_requested,
    )
    cleanup_candidate_contract = create_cleanup_candidate_contract(approval_gate)
    artifact_pre_cleanup_verification_record = create_artifact_pre_cleanup_verification_record(artifact_path)
    cleanup_path_containment_record = create_cleanup_path_containment_record(artifact_path, expected_output_directory)
    cleanup_scope_envelope = create_cleanup_scope_envelope(
        approval_gate,
        cleanup_candidate_contract,
        artifact_pre_cleanup_verification_record,
        cleanup_path_containment_record,
    )
    if execute_cleanup:
        if cleanup_scope_envelope.get("cleanup_execution_authorized"):
            cleanup_execution_record = execute_supervised_local_artifact_cleanup(
                artifact_path=str(artifact_path),
                expected_output_directory=str(expected_output_directory),
                cleanup_scope_envelope=cleanup_scope_envelope,
            )
        else:
            cleanup_execution_record = create_blocked_cleanup_execution_record("cleanup execution not authorized")
    else:
        cleanup_execution_record = create_blocked_cleanup_execution_record("cleanup execution not requested")
    post_cleanup_verification_record = create_post_cleanup_verification_record(cleanup_execution_record, artifact_path)
    cleanup_audit_record = create_cleanup_audit_record(
        approval_gate,
        cleanup_candidate_contract,
        artifact_pre_cleanup_verification_record,
        cleanup_path_containment_record,
        cleanup_scope_envelope,
        cleanup_execution_record,
        post_cleanup_verification_record,
    )
    cleanup_closeout_ledger = create_cleanup_closeout_ledger(cleanup_audit_record)
    cleanup_readiness_summary = create_cleanup_readiness_summary(cleanup_closeout_ledger)
    limited_live_worker_activation_candidate_bridge = create_limited_live_worker_activation_candidate_bridge(cleanup_readiness_summary)
    bundle = {
        "supervised_rollback_cleanup_candidate_bundle_version": SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_MODULE_VERSION,
        "schema": create_supervised_rollback_cleanup_candidate_schema(),
        "supervised_rollback_cleanup_candidate_approval_gate": approval_gate,
        "cleanup_candidate_contract": cleanup_candidate_contract,
        "artifact_pre_cleanup_verification_record": artifact_pre_cleanup_verification_record,
        "cleanup_path_containment_record": cleanup_path_containment_record,
        "cleanup_scope_envelope": cleanup_scope_envelope,
        "cleanup_execution_record": cleanup_execution_record,
        "post_cleanup_verification_record": post_cleanup_verification_record,
        "cleanup_audit_record": cleanup_audit_record,
        "cleanup_closeout_ledger": cleanup_closeout_ledger,
        "cleanup_readiness_summary": cleanup_readiness_summary,
        "limited_live_worker_activation_candidate_bridge": limited_live_worker_activation_candidate_bridge,
        "local_cleanup_performed": bool(cleanup_execution_record.get("local_cleanup_performed")),
        "artifact_deleted": bool(cleanup_execution_record.get("artifact_deleted")),
        "deleted_file_count": int(cleanup_execution_record.get("deleted_file_count", 0)),
        "cleanup_requested": bool(cleanup_requested),
        "execute_cleanup_requested": bool(execute_cleanup),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
