#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION = "4.1.0"
POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_STATUS = "POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_LOCAL_ONLY"
POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_PHASE = "Post-Action Verification and Audit Review"
POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW"
DEFAULT_REVIEW_LABEL = "post-action-verification-and-audit-review"
DEFAULT_REVIEW_RECORD_NAME = "post_action_verification_and_audit_review_record.json"
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


def _false_booleans() -> dict:
    return {name: False for name in DANGEROUS_BOOLEAN_FIELDS}


def _safe_path_digest(paths: list[str]) -> dict:
    return {"paths": list(paths), "digest": sha256_digest(paths)}


def normalize_review_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.strip().lower()).strip("-")
    return normalized or DEFAULT_REVIEW_LABEL


def generate_post_action_verification_and_audit_review_id(
    command: str,
    review_label: str,
    runtime_version: str = POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
) -> str:
    normalized_label = normalize_review_label(review_label)
    digest = sha256_digest(f"{runtime_version}:{command}:{review_label}")
    return f"post-action-verification-and-audit-review-v4-1-{normalized_label}-{digest[:12]}"


def create_post_action_verification_and_audit_review_schema() -> dict:
    return {
        "post_action_verification_and_audit_review_schema_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "schema_status": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_STATUS,
        "review_type": "post_action_verification_and_audit_review",
        "required_sections": [
            "post_action_verification_and_audit_review_approval_gate",
            "v4_candidate_artifact_reference_contract",
            "artifact_integrity_verification_record",
            "artifact_path_containment_review",
            "safety_boolean_review",
            "cleanup_instruction_review",
            "operator_review_acknowledgement",
            "post_action_closeout_ledger",
            "post_action_readiness_summary",
            "supervised_rollback_cleanup_candidate_bridge",
        ],
        "required_confirmation_token": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_APPROVAL_TOKEN,
        "baseline_preserved": True,
        "local_review_records_written": False,
        **_false_booleans(),
    }


def create_post_action_verification_and_audit_review_approval_gate(
    review_label: str,
    artifact_path: str | None = None,
    review_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    token_valid = confirmation_token == POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_APPROVAL_TOKEN
    artifact_path_present = bool(artifact_path and str(artifact_path).strip())
    human_operator_present = bool(human_operator and str(human_operator).strip())
    review_output_directory_present = bool(review_output_directory and str(review_output_directory).strip())
    local_review_records_authorized = token_valid and human_operator_present and artifact_path_present
    local_review_record_write_authorized = local_review_records_authorized and review_output_directory_present
    gate_status = (
        "APPROVED_FOR_LOCAL_POST_ACTION_REVIEW_RECORDS"
        if local_review_records_authorized
        else "BLOCKED_PENDING_V4_1_REVIEW_APPROVAL"
    )
    return {
        "post_action_verification_and_audit_review_approval_gate_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "review_label": review_label,
        "review_label_normalized": normalize_review_label(review_label),
        "artifact_path": artifact_path,
        "review_output_directory": review_output_directory,
        "human_operator": human_operator,
        "gate_status": gate_status,
        "confirmation_token_required": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "artifact_path_present": artifact_path_present,
        "local_review_records_authorized": local_review_records_authorized,
        "local_review_record_write_authorized": local_review_record_write_authorized,
        "local_review_records_written": False,
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


def create_v4_candidate_artifact_reference_contract(approval_gate: dict) -> dict:
    artifact_path = approval_gate.get("artifact_path")
    token_valid = approval_gate.get("local_review_records_authorized", False) and bool(artifact_path)
    contract_status = "V4_CANDIDATE_ARTIFACT_REFERENCE_CONTRACT_CREATED" if token_valid else "BLOCKED"
    return {
        "v4_candidate_artifact_reference_contract_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "contract_status": contract_status,
        "artifact_path": artifact_path,
        "reference_only": True,
        "no_artifact_mutation": True,
        "artifact_reference_digest": sha256_digest(str(artifact_path or "")),
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_artifact_integrity_verification_record(artifact_path: str | None) -> dict:
    if not artifact_path:
        return {
            "artifact_integrity_verification_record_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
            "verification_status": "BLOCKED",
            "artifact_path": None,
            "artifact_exists": False,
            "artifact_suffix_json": False,
            "artifact_json_parses": False,
            "payload_digest_present": False,
            "payload_digest_valid": False,
            "artifact_digest": None,
            "baseline_preserved": True,
            "execution_authorized": False,
            **_false_booleans(),
        }

    resolved_path = Path(artifact_path).expanduser().resolve()
    artifact_exists = resolved_path.exists()
    suffix_json = resolved_path.suffix == ".json"
    artifact_json_parses = False
    payload_digest_present = False
    payload_digest_valid = False
    artifact_digest = None
    parsed_artifact: dict | None = None
    if artifact_exists and suffix_json:
        try:
            parsed_artifact = json.loads(resolved_path.read_text(encoding="utf-8"))
            artifact_json_parses = isinstance(parsed_artifact, dict)
            if artifact_json_parses:
                artifact_digest = sha256_digest(parsed_artifact)
                payload_digest_present = "payload_digest" in parsed_artifact
                if payload_digest_present:
                    payload_without_digest = dict(parsed_artifact)
                    provided_payload_digest = payload_without_digest.pop("payload_digest")
                    payload_digest_valid = sha256_digest(payload_without_digest) == provided_payload_digest
                else:
                    payload_digest_valid = True
        except Exception:
            artifact_json_parses = False

    verification_status = (
        "PASS"
        if artifact_exists and suffix_json and artifact_json_parses and payload_digest_valid
        else "BLOCKED"
    )
    return {
        "artifact_integrity_verification_record_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "verification_status": verification_status,
        "artifact_path": str(resolved_path),
        "artifact_exists": artifact_exists,
        "artifact_suffix_json": suffix_json,
        "artifact_json_parses": artifact_json_parses,
        "payload_digest_present": payload_digest_present,
        "payload_digest_valid": payload_digest_valid,
        "artifact_digest": artifact_digest,
        "parsed_artifact_digest": artifact_digest,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_artifact_path_containment_review(artifact_path: str | None, expected_output_directory: str | None = None) -> dict:
    if not artifact_path:
        return {
            "artifact_path_containment_review_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
            "containment_status": "BLOCKED",
            "artifact_path": None,
            "expected_output_directory": expected_output_directory,
            "artifact_path_contained_within_expected_output_directory": False,
            "execution_authorized": False,
            "baseline_preserved": True,
            **_false_booleans(),
        }

    artifact_resolved = Path(artifact_path).expanduser().resolve()
    if not expected_output_directory:
        return {
            "artifact_path_containment_review_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
            "containment_status": "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY",
            "artifact_path": str(artifact_resolved),
            "expected_output_directory": None,
            "resolved_expected_output_directory": None,
            "artifact_path_contained_within_expected_output_directory": False,
            "execution_authorized": False,
            "baseline_preserved": True,
            **_false_booleans(),
        }

    expected_resolved = Path(expected_output_directory).expanduser().resolve()
    try:
        artifact_resolved.relative_to(expected_resolved)
        contained = True
    except ValueError:
        contained = False
    status = "PASS" if contained else "BLOCKED"
    return {
        "artifact_path_containment_review_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "containment_status": status,
        "artifact_path": str(artifact_resolved),
        "expected_output_directory": str(expected_resolved),
        "artifact_path_contained_within_expected_output_directory": contained,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_safety_boolean_review(artifact_data: dict | None) -> dict:
    hits = []
    if isinstance(artifact_data, dict):
        for key, value in artifact_data.items():
            if key in DANGEROUS_BOOLEAN_FIELDS and value is True:
                hits.append(key)
            if key == "safety_booleans" and isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if nested_key in DANGEROUS_BOOLEAN_FIELDS and nested_value is True:
                        hits.append(nested_key)
    status = "PASS" if not hits else "BLOCKED"
    return {
        "safety_boolean_review_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "safety_review_status": status,
        "dangerous_boolean_hits": hits,
        "local_proof_artifact_write_performed": bool(artifact_data.get("local_proof_artifact_write_performed")) if isinstance(artifact_data, dict) else False,
        "baseline_preserved": True if not isinstance(artifact_data, dict) else bool(artifact_data.get("baseline_preserved", True)),
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_cleanup_instruction_review(artifact_data: dict | None) -> dict:
    cleanup_instructions = []
    if isinstance(artifact_data, dict):
        cleanup_instructions = list(artifact_data.get("cleanup_instructions") or [])
    has_required_style = any(
        "approved output directory" in str(item).lower() or "output directory" in str(item).lower()
        for item in cleanup_instructions
    )
    status = "PASS" if cleanup_instructions and has_required_style else "BLOCKED"
    return {
        "cleanup_instruction_review_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "cleanup_instruction_review_status": status,
        "cleanup_instructions_present": bool(cleanup_instructions),
        "cleanup_instructions": cleanup_instructions,
        "cleanup_only_inside_approved_output_directory": has_required_style,
        "cleanup_not_performed_by_v4_1": True,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_operator_review_acknowledgement(
    approval_gate: dict,
    artifact_integrity_verification_record: dict,
    artifact_path_containment_review: dict,
    safety_boolean_review: dict,
    cleanup_instruction_review: dict,
) -> dict:
    token_valid = approval_gate.get("confirmation_token_valid", False)
    human_operator_present = bool(approval_gate.get("human_operator"))
    integrity_ok = artifact_integrity_verification_record.get("verification_status") == "PASS"
    safety_ok = safety_boolean_review.get("safety_review_status") == "PASS"
    cleanup_ok = cleanup_instruction_review.get("cleanup_instruction_review_status") == "PASS"
    containment_status = artifact_path_containment_review.get("containment_status")
    containment_ok = containment_status == "PASS"
    review_requires_directory = containment_status == "REVIEW_REQUIRES_EXPECTED_OUTPUT_DIRECTORY"
    if not token_valid or not human_operator_present:
        status = "BLOCKED_PENDING_V4_1_REVIEW_APPROVAL"
    elif not integrity_ok or not safety_ok or not cleanup_ok:
        status = "BLOCKED"
    elif review_requires_directory:
        status = "BLOCKED_PENDING_OUTPUT_DIRECTORY_CONFIRMATION"
    elif not containment_ok:
        status = "BLOCKED"
    else:
        status = "PASS"
    return {
        "operator_review_acknowledgement_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "acknowledgement_status": status,
        "token_valid": token_valid,
        "human_operator_present": human_operator_present,
        "artifact_integrity_pass": integrity_ok,
        "containment_status": containment_status,
        "safety_review_pass": safety_ok,
        "cleanup_review_pass": cleanup_ok,
        "execution_authorized": False,
        "baseline_preserved": True,
        **_false_booleans(),
    }


def create_post_action_closeout_ledger(
    approval_gate: dict,
    artifact_reference_contract: dict,
    artifact_integrity_verification_record: dict,
    artifact_path_containment_review: dict,
    safety_boolean_review: dict,
    cleanup_instruction_review: dict,
    operator_review_acknowledgement: dict,
) -> dict:
    ack_ok = operator_review_acknowledgement.get("acknowledgement_status") == "PASS"
    ledger = {
        "post_action_closeout_ledger_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "ledger_status": "PASS" if ack_ok else "BLOCKED",
        "approval_gate_digest": sha256_digest(approval_gate),
        "artifact_reference_contract_digest": sha256_digest(artifact_reference_contract),
        "artifact_integrity_verification_record_digest": sha256_digest(artifact_integrity_verification_record),
        "artifact_path_containment_review_digest": sha256_digest(artifact_path_containment_review),
        "safety_boolean_review_digest": sha256_digest(safety_boolean_review),
        "cleanup_instruction_review_digest": sha256_digest(cleanup_instruction_review),
        "operator_review_acknowledgement_digest": sha256_digest(operator_review_acknowledgement),
        "baseline_preserved": True,
        "local_review_records_written": False,
        "execution_authorized": False,
        **_false_booleans(),
    }
    ledger["ledger_digest"] = sha256_digest(ledger)
    return ledger


def create_post_action_readiness_summary(ledger: dict) -> dict:
    ready = ledger.get("ledger_status") == "PASS"
    return {
        "post_action_readiness_summary_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "readiness_status": "READY_FOR_SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "Supervised Rollback / Cleanup Candidate",
        "v4_2_built": False,
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        "local_review_records_written": bool(ledger.get("local_review_records_written", False)),
        **_false_booleans(),
    }


def create_supervised_rollback_cleanup_candidate_bridge(summary: dict) -> dict:
    ready = summary.get("ready_for_next_layer", False)
    return {
        "supervised_rollback_cleanup_candidate_bridge_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "bridge_status": "READY_FOR_V4_2_SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE" if ready else "BLOCKED",
        "next_layer": "v4.2 supervised rollback / cleanup candidate",
        "ready_for_next_layer": ready,
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }


def create_post_action_verification_and_audit_review_bundle(
    result: dict | None,
    command: str | None = None,
    review_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    review_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    write_review_records: bool = False,
) -> dict:
    result = dict(result or {})
    command = command or result.get("command", "check please")
    review_label = review_label or "post-action verification and audit review"
    artifact_path = artifact_path or result.get("artifact_path")
    approval_gate = create_post_action_verification_and_audit_review_approval_gate(
        review_label,
        artifact_path=artifact_path,
        review_output_directory=review_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
    )
    artifact_reference_contract = create_v4_candidate_artifact_reference_contract(approval_gate)
    artifact_integrity_verification_record = create_artifact_integrity_verification_record(artifact_path)
    artifact_path_containment_review = create_artifact_path_containment_review(artifact_path, expected_output_directory=expected_output_directory)
    artifact_data = None
    if artifact_integrity_verification_record.get("verification_status") == "PASS" and artifact_path:
        artifact_data = json.loads(Path(artifact_integrity_verification_record["artifact_path"]).read_text(encoding="utf-8"))
    safety_boolean_review = create_safety_boolean_review(artifact_data)
    cleanup_instruction_review = create_cleanup_instruction_review(artifact_data)
    operator_review_acknowledgement = create_operator_review_acknowledgement(
        approval_gate,
        artifact_integrity_verification_record,
        artifact_path_containment_review,
        safety_boolean_review,
        cleanup_instruction_review,
    )
    post_action_closeout_ledger = create_post_action_closeout_ledger(
        approval_gate,
        artifact_reference_contract,
        artifact_integrity_verification_record,
        artifact_path_containment_review,
        safety_boolean_review,
        cleanup_instruction_review,
        operator_review_acknowledgement,
    )
    post_action_readiness_summary = create_post_action_readiness_summary(post_action_closeout_ledger)
    supervised_rollback_cleanup_candidate_bridge = create_supervised_rollback_cleanup_candidate_bridge(post_action_readiness_summary)

    review_record = {
        "post_action_verification_and_audit_review_record_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "review_label": review_label,
        "review_label_normalized": normalize_review_label(review_label),
        "command": command,
        "artifact_path": artifact_path,
        "expected_output_directory": expected_output_directory,
        "review_output_directory": review_output_directory,
        "approval_gate_digest": sha256_digest(approval_gate),
        "artifact_reference_contract_digest": sha256_digest(artifact_reference_contract),
        "artifact_integrity_verification_record_digest": sha256_digest(artifact_integrity_verification_record),
        "artifact_path_containment_review_digest": sha256_digest(artifact_path_containment_review),
        "safety_boolean_review_digest": sha256_digest(safety_boolean_review),
        "cleanup_instruction_review_digest": sha256_digest(cleanup_instruction_review),
        "operator_review_acknowledgement_digest": sha256_digest(operator_review_acknowledgement),
        "post_action_closeout_ledger_digest": sha256_digest(post_action_closeout_ledger),
        "readiness_summary_digest": sha256_digest(post_action_readiness_summary),
        "bridge_digest": sha256_digest(supervised_rollback_cleanup_candidate_bridge),
        "baseline_preserved": True,
        "local_review_records_written": False,
        "execution_authorized": False,
        **_false_booleans(),
    }
    if write_review_records and operator_review_acknowledgement.get("acknowledgement_status") == "PASS":
        if review_output_directory:
            payload = {
                "runtime_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
                "review_label": review_label,
                "review_label_normalized": normalize_review_label(review_label),
                "command": command,
                "artifact_path": artifact_path,
                "expected_output_directory": expected_output_directory,
                "review_output_directory": review_output_directory,
                "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
                "human_operator": human_operator,
                "forbidden_paths": list(DEFAULT_FORBIDDEN_PATHS),
                "artifact_integrity_verification_record": artifact_integrity_verification_record,
                "artifact_path_containment_review": artifact_path_containment_review,
                "safety_boolean_review": safety_boolean_review,
                "cleanup_instruction_review": cleanup_instruction_review,
                "operator_review_acknowledgement": operator_review_acknowledgement,
                "post_action_closeout_ledger": post_action_closeout_ledger,
                "post_action_readiness_summary": post_action_readiness_summary,
                "supervised_rollback_cleanup_candidate_bridge": supervised_rollback_cleanup_candidate_bridge,
                "local_review_records_written": False,
                "baseline_preserved": True,
                "execution_authorized": False,
                "cleanup_instructions": cleanup_instruction_review.get("cleanup_instructions", []),
                "timestamp_mode": "deterministic_no_wall_clock_timestamp",
                "safety_booleans": _false_booleans(),
            }
            payload["payload_digest"] = sha256_digest(payload)
            review_write_summary = write_post_action_verification_and_audit_review_record(review_output_directory, payload)
            review_record = dict(review_write_summary)
            review_record["local_review_records_written"] = True
            review_record["review_record_payload_digest"] = payload["payload_digest"]
        else:
            review_record["block_reason"] = "review output directory not requested"
    else:
        review_record["block_reason"] = "review not authorized"
    review_record["review_record_status"] = (
        "WRITTEN" if review_record.get("local_review_records_written") else "BLOCKED"
    )

    bundle = {
        "post_action_verification_and_audit_review_bundle_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "schema": create_post_action_verification_and_audit_review_schema(),
        "post_action_verification_and_audit_review_approval_gate": approval_gate,
        "v4_candidate_artifact_reference_contract": artifact_reference_contract,
        "artifact_integrity_verification_record": artifact_integrity_verification_record,
        "artifact_path_containment_review": artifact_path_containment_review,
        "safety_boolean_review": safety_boolean_review,
        "cleanup_instruction_review": cleanup_instruction_review,
        "operator_review_acknowledgement": operator_review_acknowledgement,
        "post_action_closeout_ledger": post_action_closeout_ledger,
        "post_action_readiness_summary": post_action_readiness_summary,
        "supervised_rollback_cleanup_candidate_bridge": supervised_rollback_cleanup_candidate_bridge,
        "post_action_verification_and_audit_review_record": review_record,
        "local_review_records_written": bool(review_record.get("local_review_records_written")),
        "local_review_record_write_authorized": approval_gate.get("local_review_record_write_authorized", False),
        "approval_token_valid": approval_gate.get("confirmation_token_valid", False),
        "baseline_preserved": True,
        "execution_authorized": False,
        **_false_booleans(),
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle


def write_post_action_verification_and_audit_review_record(
    review_output_directory: str,
    payload: dict,
) -> dict:
    output_dir = Path(review_output_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    review_path = (output_dir / DEFAULT_REVIEW_RECORD_NAME).resolve()
    try:
        review_path.relative_to(output_dir)
    except ValueError as exc:
        raise ValueError("review record path escaped approved review output directory") from exc
    review_path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    return {
        "post_action_verification_and_audit_review_record_version": POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_MODULE_VERSION,
        "local_review_records_written": True,
        "review_record_path": str(review_path),
        "review_output_directory": str(output_dir),
        "review_record_name": DEFAULT_REVIEW_RECORD_NAME,
        "files_written": [DEFAULT_REVIEW_RECORD_NAME],
        "baseline_preserved": True,
        "repo_files_modified": False,
        "execution_authorized": False,
        **_false_booleans(),
    }
