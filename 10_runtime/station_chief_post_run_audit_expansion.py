#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re

POST_RUN_AUDIT_EXPANSION_MODULE_VERSION = "3.1.0"
POST_RUN_AUDIT_EXPANSION_STATUS = "SINGLE_WORKER_POST_RUN_AUDIT_EXPANSION_ONLY"
POST_RUN_AUDIT_EXPANSION_PHASE = "Post-Run Audit Proof Expansion"
POST_RUN_AUDIT_EXPANSION_APPROVAL_TOKEN = "YES_I_APPROVE_POST_RUN_AUDIT_PROOF_EXPANSION"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_audit_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "post-run-audit-expansion"


def generate_post_run_audit_expansion_id(command: str, worker_id: str, runtime_version: str = "3.1.0") -> str:
    normalized_worker_id = normalize_audit_label(worker_id)
    hash_input = f"{runtime_version}:{command}:{worker_id}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"post-run-audit-v3-1-{normalized_worker_id}-{hash_chars}"


def create_post_run_audit_expansion_schema() -> dict:
    return {
        "post_run_audit_expansion_schema_version": "3.1.0",
        "schema_status": "SINGLE_WORKER_POST_RUN_AUDIT_EXPANSION_ONLY",
        "required_sections": [
            "expanded_audit_evidence_schema",
            "post_run_audit_approval_gate",
            "before_after_run_comparison_proof",
            "validator_backed_audit_artifact_index",
            "audit_replay_record",
            "failure_class_taxonomy",
            "human_review_packet",
            "audit_integrity_score",
            "audit_evidence_ledger",
            "audit_expansion_readiness_summary",
            "multi_worker_sandbox_coordination_readiness_bridge",
        ],
        "allowed_audit_modes": [
            "schema_only",
            "local_audit_preview",
            "approved_single_worker_audit_expansion_records",
            "comparison_proof_record",
            "replay_record_only",
            "human_review_packet_preview",
        ],
        "blocked_audit_modes": [
            "actual_replay_execution",
            "external_artifact_fetch",
            "shell_command_replay",
            "network_replay",
            "repo_mutating_replay",
            "deployment_replay",
            "broad_worker_replay",
            "live_orchestration_replay",
            "autonomous_retry",
            "background_audit_monitoring",
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_POST_RUN_AUDIT_PROOF_EXPANSION",
        ],
        "safety_invariants": [
            "single sandbox worker only",
            "local audit records only",
            "no actual replay execution",
            "no external artifact fetch",
            "no shell commands",
            "no network calls",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "no live orchestration",
            "audit replay records are descriptive records only",
            "audit proof expansion does not authorize broad execution",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "repo_files_modified": False,
        "external_artifact_fetch_performed": False,
        "broad_worker_activation_performed": False,
        "execution_authorized": False,
    }


def create_expanded_audit_evidence_schema() -> dict:
    return {
        "expanded_audit_evidence_schema_version": "3.1.0",
        "schema_status": "EVIDENCE_SCHEMA_ONLY",
        "required_evidence_fields": [
            "audit_id",
            "worker_id",
            "command",
            "runtime_version",
            "source_result_digest",
            "telemetry_digest",
            "permission_digest",
            "controlled_worker_digest",
            "before_after_comparison_digest",
            "validator_index_digest",
            "replay_record_digest",
            "failure_taxonomy_digest",
            "human_review_packet_digest",
            "audit_integrity_score",
            "external_actions_taken",
            "repo_files_modified",
            "execution_authorized",
        ],
        "recommended_evidence_groups": [
            "runtime identity",
            "command classification",
            "worker execution gate",
            "tool permission binding",
            "telemetry and abort controls",
            "post-abort audit proof",
            "artifact index",
            "validator evidence",
            "human review packet",
            "safety boundaries",
        ],
        "blocked_evidence_sources": [
            "live external API calls",
            "shell command output",
            "filesystem scans",
            "secret stores",
            "environment variables",
            "network responses",
            "deployment provider state",
            "GitHub API mutation state",
        ],
        "safety_checks": [
            "all required fields present",
            "evidence digests present",
            "no external actions",
            "no repo modifications",
            "no execution authorization",
            "no replay execution",
            "no broad worker activation",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_post_run_audit_approval_gate(worker_id: str, confirmation_token: str | None = None) -> dict:
    token_valid = confirmation_token == POST_RUN_AUDIT_EXPANSION_APPROVAL_TOKEN
    return {
        "post_run_audit_approval_gate_version": "3.1.0",
        "worker_id": worker_id,
        "gate_status": "APPROVED_FOR_SINGLE_WORKER_POST_RUN_AUDIT_EXPANSION_RECORDS" if token_valid else "BLOCKED_PENDING_POST_RUN_AUDIT_EXPANSION_APPROVAL",
        "confirmation_token_required": POST_RUN_AUDIT_EXPANSION_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_audit_expansion_records_authorized": token_valid,
        "actual_replay_authorized": False,
        "external_artifact_fetch_authorized": False,
        "shell_execution_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "broad_worker_activation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_before_after_run_comparison_proof(worker_id: str, audit_gate: dict, before_result: dict | None = None, after_result: dict | None = None) -> dict:
    before_result = before_result or {}
    after_result = after_result or {}
    approved = audit_gate.get("confirmation_token_valid") is True
    before_keys = set(before_result)
    after_keys = set(after_result)
    shared_keys = sorted(before_keys & after_keys)
    added_keys = sorted(after_keys - before_keys)
    removed_keys = sorted(before_keys - after_keys)
    changed_keys = [k for k in shared_keys if canonical_json(before_result.get(k)) != canonical_json(after_result.get(k))]
    before_digest = sha256_digest(before_result)
    after_digest = sha256_digest(after_result)
    return {
        "before_after_run_comparison_proof_version": "3.1.0",
        "worker_id": worker_id,
        "comparison_status": "CREATED" if approved else "BLOCKED",
        "before_key_count": len(before_keys),
        "after_key_count": len(after_keys),
        "added_top_level_keys": added_keys,
        "removed_top_level_keys": removed_keys,
        "shared_top_level_keys": shared_keys,
        "changed_top_level_keys": changed_keys,
        "before_digest": before_digest,
        "after_digest": after_digest,
        "comparison_digest": sha256_digest({"worker_id": worker_id, "approved": approved, "before": before_digest, "after": after_digest, "added": added_keys, "removed": removed_keys, "shared": shared_keys, "changed": changed_keys}),
        "filesystem_read": False,
        "git_diff_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_validator_backed_audit_artifact_index(worker_id: str, audit_gate: dict, artifact_names: list[str] | None = None, validator_names: list[str] | None = None) -> dict:
    artifact_names = artifact_names or ["full_result.json", "manifest.json", "controlled_worker_execution_result.json", "tool_permission_binding_bundle.json", "live_execution_telemetry_abort_bundle.json", "post_abort_audit_proof.json"]
    validator_names = validator_names or ["validate_station_chief_runtime_v2_5.py", "validate_station_chief_runtime_v2_3.py", "validate_station_chief_runtime_v2_2.py", "validate_station_chief_runtime_v2_1.py"]
    approved = audit_gate.get("confirmation_token_valid") is True
    artifact_index_entries = [{"artifact_name": name, "artifact_status": "EXPECTED_BY_CONTRACT", "artifact_verified_from_filesystem": False} for name in artifact_names]
    validator_index_entries = [{"validator_name": name, "validator_status": "EXPECTED_BY_CONTRACT", "validator_executed_by_module": False} for name in validator_names]
    return {
        "validator_backed_audit_artifact_index_version": "3.1.0",
        "worker_id": worker_id,
        "index_status": "INDEX_CREATED" if approved else "BLOCKED",
        "artifact_names": artifact_names,
        "validator_names": validator_names,
        "artifact_count": len(artifact_names),
        "validator_count": len(validator_names),
        "artifact_index_entries": artifact_index_entries,
        "validator_index_entries": validator_index_entries,
        "index_digest": sha256_digest({"worker_id": worker_id, "approved": approved, "artifact_index_entries": artifact_index_entries, "validator_index_entries": validator_index_entries}),
        "filesystem_checked": False,
        "validators_executed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_audit_replay_record(worker_id: str, audit_gate: dict, replay_source_digest: str | None = None) -> dict:
    replay_source_digest = replay_source_digest or sha256_digest({})
    approved = audit_gate.get("confirmation_token_valid") is True
    replay_steps = ["identify source result digest", "identify expected artifact contracts", "compare recorded digests", "classify failure if mismatch", "create human review packet", "do not execute replay automatically"]
    record = {
        "audit_replay_record_version": "3.1.0",
        "worker_id": worker_id,
        "replay_status": "REPLAY_RECORD_CREATED" if approved else "BLOCKED",
        "replay_source_digest": replay_source_digest,
        "replay_mode": "RECORD_ONLY_NO_EXECUTION",
        "replay_steps": replay_steps,
        "actual_replay_performed": False,
        "shell_commands_run": False,
        "filesystem_read": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    record["replay_record_digest"] = sha256_digest({"worker_id": worker_id, "approved": approved, "replay_source_digest": replay_source_digest, "replay_mode": record["replay_mode"], "replay_steps": replay_steps})
    return record


def create_failure_class_taxonomy(worker_id: str, audit_gate: dict, observed_failures: list[str] | None = None) -> dict:
    observed_failures = observed_failures or []
    approved = audit_gate.get("confirmation_token_valid") is True
    known_failure_classes = ["missing_required_artifact", "digest_mismatch", "validator_failure", "unsafe_output_detected", "token_missing", "token_invalid", "external_action_attempted", "repo_mutation_attempted", "broad_worker_activation_attempted", "unexpected_exception", "unknown_failure"]
    classified_failures = [failure if failure in known_failure_classes else "unknown_failure" for failure in observed_failures]
    return {
        "failure_class_taxonomy_version": "3.1.0",
        "worker_id": worker_id,
        "taxonomy_status": "TAXONOMY_CREATED" if approved else "BLOCKED",
        "known_failure_classes": known_failure_classes,
        "observed_failures": observed_failures,
        "classified_failures": classified_failures,
        "failure_count": len(classified_failures),
        "taxonomy_digest": sha256_digest({"worker_id": worker_id, "approved": approved, "observed_failures": observed_failures, "classified_failures": classified_failures}),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_human_review_packet(worker_id: str, audit_gate: dict, comparison_proof: dict, artifact_index: dict, audit_replay_record: dict, failure_taxonomy: dict) -> dict:
    approved = audit_gate.get("confirmation_token_valid") is True
    review_summary = "Post-run audit expansion is ready for human review when the audit gate is approved. This packet does not authorize broad execution."
    packet = {
        "human_review_packet_version": "3.1.0",
        "worker_id": worker_id,
        "packet_status": "READY_FOR_HUMAN_REVIEW" if approved else "BLOCKED",
        "review_summary": review_summary,
        "review_questions": [
            "Did the run preserve the locked baseline?",
            "Were any external actions attempted?",
            "Were any repo files modified?",
            "Were all expected audit artifacts accounted for by contract?",
            "Did the replay record remain record-only?",
            "Are any failure classes present?",
            "Should the system proceed to multi-worker sandbox coordination design?",
        ],
        "allowed_next_actions": ["review audit packet", "inspect artifact contracts", "compare recorded digests", "classify failures", "proceed to v2.4 design if safe"],
        "blocked_next_actions": ["broad worker activation", "live external API execution", "repo mutation", "deployment", "actual replay execution", "autonomous retry"],
        "comparison_digest": comparison_proof.get("comparison_digest"),
        "artifact_index_digest": artifact_index.get("index_digest"),
        "replay_record_digest": audit_replay_record.get("replay_record_digest"),
        "failure_taxonomy_digest": failure_taxonomy.get("taxonomy_digest"),
        "human_review_packet_digest": sha256_digest({"worker_id": worker_id, "approved": approved, "comparison_digest": comparison_proof.get("comparison_digest"), "artifact_index_digest": artifact_index.get("index_digest"), "replay_record_digest": audit_replay_record.get("replay_record_digest"), "failure_taxonomy_digest": failure_taxonomy.get("taxonomy_digest")}),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    return packet


def create_audit_integrity_score(worker_id: str, audit_gate: dict, comparison_proof: dict, artifact_index: dict, audit_replay_record: dict, failure_taxonomy: dict, human_review_packet: dict) -> dict:
    approved = audit_gate.get("confirmation_token_valid") is True
    score = 100
    factors: list[str] = []
    if not approved:
        score -= 40
        factors.append("audit gate invalid (-40)")
    if comparison_proof.get("comparison_status") != "CREATED":
        score -= 15
        factors.append("comparison proof not created (-15)")
    if artifact_index.get("index_status") != "INDEX_CREATED":
        score -= 15
        factors.append("artifact index not created (-15)")
    if audit_replay_record.get("replay_status") != "REPLAY_RECORD_CREATED":
        score -= 15
        factors.append("replay record not created (-15)")
    if human_review_packet.get("packet_status") != "READY_FOR_HUMAN_REVIEW":
        score -= 10
        factors.append("human review packet not ready (-10)")
    observed_failure_count = min(len(failure_taxonomy.get("classified_failures", [])), 5)
    if observed_failure_count:
        deduction = observed_failure_count * 5
        score -= deduction
        factors.append(f"observed failures ({observed_failure_count}) (-{deduction})")
    score = max(score, 0)
    integrity_status = "BLOCKED" if (not approved or score < 50) else ("REVIEW_REQUIRED" if score < 80 else "PASS")
    return {"audit_integrity_score_version": "3.1.0", "worker_id": worker_id, "integrity_score": score, "integrity_status": integrity_status, "score_factors": factors, "external_actions_taken": False, "repo_files_modified": False, "execution_authorized": False}


def create_audit_evidence_ledger(worker_id: str, audit_gate: dict, expanded_schema: dict, comparison_proof: dict, artifact_index: dict, audit_replay_record: dict, failure_taxonomy: dict, human_review_packet: dict, audit_integrity_score: dict) -> dict:
    entries = [
        {"entry_type": "audit approval gate", "entry_digest": sha256_digest(audit_gate)},
        {"entry_type": "expanded schema", "entry_digest": sha256_digest(expanded_schema)},
        {"entry_type": "before/after comparison proof", "entry_digest": sha256_digest(comparison_proof)},
        {"entry_type": "validator-backed artifact index", "entry_digest": sha256_digest(artifact_index)},
        {"entry_type": "audit replay record", "entry_digest": sha256_digest(audit_replay_record)},
        {"entry_type": "failure taxonomy", "entry_digest": sha256_digest(failure_taxonomy)},
        {"entry_type": "human review packet", "entry_digest": sha256_digest(human_review_packet)},
        {"entry_type": "audit integrity score", "entry_digest": sha256_digest(audit_integrity_score)},
    ]
    return {"audit_evidence_ledger_version": "3.1.0", "ledger_status": "SINGLE_WORKER_POST_RUN_AUDIT_LEDGER", "worker_id": worker_id, "entries": entries, "ledger_digest": sha256_digest(entries), "external_actions_taken": False, "actual_replay_performed": False, "repo_files_modified": False, "execution_authorized": False}


def create_audit_expansion_readiness_summary(worker_id: str, audit_gate: dict, audit_integrity_score: dict, audit_evidence_ledger: dict) -> dict:
    gate_approved = audit_gate.get("confirmation_token_valid") is True
    integrity_status = audit_integrity_score.get("integrity_status")
    ledger_status = audit_evidence_ledger.get("ledger_status")
    ready = gate_approved and integrity_status == "PASS" and ledger_status == "SINGLE_WORKER_POST_RUN_AUDIT_LEDGER"
    return {"audit_expansion_readiness_summary_version": "3.1.0", "worker_id": worker_id, "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED", "ready_for_multi_worker_sandbox_coordination": ready, "audit_gate_status": audit_gate.get("gate_status"), "integrity_status": integrity_status, "integrity_score": audit_integrity_score.get("integrity_score"), "ledger_status": ledger_status, "next_layer": "Multi-Worker Sandbox Coordination", "baseline_preserved": True, "external_actions_taken": False, "actual_replay_performed": False, "repo_files_modified": False, "execution_authorized": False}


def create_multi_worker_sandbox_coordination_readiness_bridge(result: dict, readiness_summary: dict) -> dict:
    ready = readiness_summary.get("ready_for_multi_worker_sandbox_coordination") is True
    return {"multi_worker_sandbox_coordination_readiness_bridge_version": "3.1.0", "current_layer": "Post-Run Audit Proof Expansion", "next_layer": "Multi-Worker Sandbox Coordination", "ready_for_multi_worker_sandbox_coordination": ready, "required_next_capabilities": ["multi-worker sandbox coordination schema", "worker coordination graph", "inter-worker handoff contract", "multi-worker dry-run ledger", "collision/conflict detector", "coordination abort contract", "coordination audit proof", "still no broad workforce animation"], "non_goals_for_next_layer": ["no full 47,250 worker activation", "no uncontrolled external API execution", "no baseline mutation", "no Devinization overlay mutation", "no unbounded tool access", "no autonomous deployment", "no live production orchestration"], "baseline_preserved": True, "external_actions_taken": False, "actual_replay_performed": False, "repo_files_modified": False, "execution_authorized": False}


def create_post_run_audit_expansion_bundle(result: dict, worker_id: str | None = None, command: str | None = None, confirmation_token: str | None = None, before_result: dict | None = None, after_result: dict | None = None, artifact_names: list[str] | None = None, validator_names: list[str] | None = None, observed_failures: list[str] | None = None) -> dict:
    worker_id = worker_id or "station-chief-sandbox-worker-001"
    command = command if command is not None else result.get("command", "")
    before_result = before_result or {}
    after_result = result if after_result is None else after_result
    expanded_schema = create_expanded_audit_evidence_schema()
    audit_gate = create_post_run_audit_approval_gate(worker_id, confirmation_token)
    comparison_proof = create_before_after_run_comparison_proof(worker_id, audit_gate, before_result, after_result)
    artifact_index = create_validator_backed_audit_artifact_index(worker_id, audit_gate, artifact_names, validator_names)
    replay_record = create_audit_replay_record(worker_id, audit_gate, sha256_digest(after_result))
    failure_taxonomy = create_failure_class_taxonomy(worker_id, audit_gate, observed_failures)
    human_review_packet = create_human_review_packet(worker_id, audit_gate, comparison_proof, artifact_index, replay_record, failure_taxonomy)
    audit_integrity_score = create_audit_integrity_score(worker_id, audit_gate, comparison_proof, artifact_index, replay_record, failure_taxonomy, human_review_packet)
    audit_evidence_ledger = create_audit_evidence_ledger(worker_id, audit_gate, expanded_schema, comparison_proof, artifact_index, replay_record, failure_taxonomy, human_review_packet, audit_integrity_score)
    readiness_summary = create_audit_expansion_readiness_summary(worker_id, audit_gate, audit_integrity_score, audit_evidence_ledger)
    bridge = create_multi_worker_sandbox_coordination_readiness_bridge(result, readiness_summary)
    bundle = {
        "post_run_audit_expansion_bundle_version": "3.1.0",
        "post_run_audit_expansion_status": POST_RUN_AUDIT_EXPANSION_STATUS,
        "worker_id": worker_id,
        "command": command,
        "post_run_audit_expansion_schema": create_post_run_audit_expansion_schema(),
        "expanded_audit_evidence_schema": expanded_schema,
        "post_run_audit_approval_gate": audit_gate,
        "before_after_run_comparison_proof": comparison_proof,
        "validator_backed_audit_artifact_index": artifact_index,
        "audit_replay_record": replay_record,
        "failure_class_taxonomy": failure_taxonomy,
        "human_review_packet": human_review_packet,
        "audit_integrity_score": audit_integrity_score,
        "audit_evidence_ledger": audit_evidence_ledger,
        "audit_expansion_readiness_summary": readiness_summary,
        "multi_worker_sandbox_coordination_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "external_artifact_fetch_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }
    bundle["post_run_audit_expansion_bundle_digest"] = sha256_digest(bundle)
    return bundle
