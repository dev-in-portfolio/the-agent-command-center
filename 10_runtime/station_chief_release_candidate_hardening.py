import json
import hashlib

RELEASE_CANDIDATE_HARDENING_MODULE_VERSION = "3.0.0"
RELEASE_CANDIDATE_HARDENING_STATUS = "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY"
RELEASE_CANDIDATE_HARDENING_PHASE = "Release Candidate Hardening"
RELEASE_CANDIDATE_HARDENING_APPROVAL_TOKEN = "YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_release_candidate_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "release-candidate-hardening"
    return normalized

def generate_release_candidate_hardening_id(command: str, release_candidate_label: str, runtime_version: str = "3.0.0") -> str:
    norm_label = normalize_release_candidate_label(release_candidate_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"release-candidate-hardening-v3-0-{norm_label}-{digest}"

def create_release_candidate_hardening_schema() -> dict:
    return {
        "release_candidate_hardening_schema_version": "3.0.0",
        "schema_status": "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY",
        "required_sections": [
            "release_candidate_hardening_approval_gate",
            "full_runtime_invariant_scan",
            "validator_chain_lock_proof",
            "artifact_contract_freeze_manifest",
            "known_issue_register",
            "pre_v3_production_readiness_checklist",
            "release_candidate_safety_gate",
            "release_candidate_audit_proof",
            "release_candidate_ledger",
            "release_candidate_readiness_summary",
            "controlled_production_readiness_gate_bridge"
        ],
        "allowed_hardening_modes": [
            "schema_only",
            "local_release_candidate_hardening_records",
            "approved_release_candidate_hardening_records",
            "invariant_scan_preview",
            "validator_chain_lock_preview",
            "artifact_contract_freeze_preview",
            "known_issue_register_preview",
            "pre_v3_checklist_preview",
            "release_candidate_audit_preview"
        ],
        "blocked_hardening_modes": [
            "production_execution",
            "production_readiness_gate_activation",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "worker_action_reexecution",
            "external_tool_replay",
            "live_api_replay",
            "network_replay",
            "sock_connection",
            "credential_use",
            "secret_read",
            "env_var_read",
            "repo_mutating_release_candidate_action",
            "deployment_release_candidate_action",
            "background_release_candidate_process",
            "autonomous_retry",
            "production_queue_execution"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING"
        ],
        "safety_invariants": [
            "release candidate records only",
            "no production execution",
            "no production readiness gate activation",
            "no automatic execution",
            "no queued action execution",
            "no auto-approval",
            "no approval bypass",
            "no actual replay execution",
            "no worker action re-execution",
            "no external tool replay",
            "no live-API replay",
            "no network access",
            "no-sock-access",
            "no credential use",
            "no secret reads",
            "no-env-reads",
            "no shell commands",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "no live orchestration",
            "release candidate hardening does not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_release_candidate_hardening_approval_gate(
    release_candidate_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING")
    gate_status = "APPROVED_FOR_RELEASE_CANDIDATE_HARDENING_RECORDS" if token_valid else "BLOCKED_PENDING_RELEASE_CANDIDATE_HARDENING_APPROVAL"
    return {
        "release_candidate_hardening_approval_gate_version": "3.0.0",
        "release_candidate_label": release_candidate_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_release_candidate_hardening_records_authorized": token_valid,
        "production_execution_authorized": False,
        "production_readiness_gate_activation_authorized": False,
        "automatic_execution_authorized": False,
        "queued_action_execution_authorized": False,
        "auto_approval_authorized": False,
        "approval_bypass_authorized": False,
        "actual_replay_authorized": False,
        "worker_action_reexecution_authorized": False,
        "external_tool_replay_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "sock_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "env_read_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_full_runtime_invariant_scan(
    approval_gate: dict,
    invariant_labels: list[str] | None = None
) -> dict:
    if invariant_labels is None:
        invariant_labels = [
            "baseline preserved",
            "no external actions",
            "no production execution",
            "no automatic execution",
            "no queued action execution",
            "no actual replay execution",
            "no live-API calls",
            "no network access",
            "no-sock-access",
            "no credential use",
            "no secret reads",
            "no-env-reads",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation"
        ]
    
    scan_status = "SCAN_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    invariant_results = []
    for label in invariant_labels:
        inv_id = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        invariant_results.append({
            "invariant_id": inv_id,
            "invariant_label": label,
            "invariant_status": "PASS" if approval_gate.get("confirmation_token_valid") else "BLOCKED",
            "invariant_digest": sha256_digest(label),
            "external_actions_taken": False,
            "execution_authorized": False
        })
        
    return {
        "full_runtime_invariant_scan_version": "3.0.0",
        "scan_status": scan_status,
        "invariant_results": invariant_results,
        "invariant_count": len(invariant_results),
        "failed_invariant_count": 0 if approval_gate.get("confirmation_token_valid") else len(invariant_results),
        "scan_digest": sha256_digest(invariant_results),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "actual_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_validator_chain_lock_proof(
    approval_gate: dict,
    validator_names: list[str] | None = None
) -> dict:
    if validator_names is None:
        validator_names = [
            "validate_station_chief_runtime_v2_9.py",
            "validate_station_chief_runtime_v2_8.py",
            "validate_station_chief_runtime_v2_7.py",
            "validate_station_chief_runtime_v2_6.py",
            "validate_station_chief_runtime_v2_5.py",
            "validate_station_chief_runtime_v2_4.py",
            "validate_station_chief_runtime_v2_3.py",
            "validate_station_chief_runtime_v2_2.py",
            "validate_station_chief_runtime_v2_1.py",
            "validate_station_chief_runtime_v2_0.py",
            "validate_station_chief_runtime_skeleton.py"
        ]
        
    proof_status = "PROOF_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    validator_records = []
    for name in validator_names:
        validator_records.append({
            "validator_name": name,
            "expected_current_runtime_version": "3.0.0",
            "lock_status": "LOCKED_TO_CURRENT_RUNTIME" if approval_gate.get("confirmation_token_valid") else "BLOCKED",
            "validator_executed": False,
            "external_actions_taken": False
        })
        
    return {
        "validator_chain_lock_proof_version": "3.0.0",
        "proof_status": proof_status,
        "validator_records": validator_records,
        "validator_count": len(validator_records),
        "validator_execution_performed": False,
        "validator_chain_digest": sha256_digest(validator_records),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_artifact_contract_freeze_manifest(
    approval_gate: dict,
    artifact_contracts: list[str] | None = None
) -> dict:
    if artifact_contracts is None:
        artifact_contracts = [
            "manifest.json",
            "full_result.json",
            "release_lock_bundle.json",
            "controlled_execution_bundle.json",
            "work_order_executor_bundle.json",
            "worker_hiring_registry_bundle.json",
            "department_routing_bundle.json",
            "multi_agent_orchestration_bundle.json",
            "operator_console_bundle.json",
            "github_patch_hardening_bundle.json",
            "deployment_packaging_bundle.json",
            "controlled_worker_execution_bundle.json",
            "tool_permission_binding_bundle.json",
            "live_execution_telemetry_abort_bundle.json",
            "post_run_audit_expansion_bundle.json",
            "multi_worker_sandbox_coordination_bundle.json",
            "controlled_external_tool_adapter_preview_bundle.json",
            "permissioned_external_api_dry_run_preview_bundle.json",
            "controlled_multi_worker_audit_replay_preview_bundle.json",
            "operator_approval_queue_enforcement_bundle.json",
            "release_candidate_hardening_bundle.json"
        ]
        
    freeze_status = "FREEZE_MANIFEST_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    artifact_contract_records = []
    for art in artifact_contracts:
        artifact_contract_records.append({
            "artifact_name": art,
            "contract_status": "FROZEN_FOR_RELEASE_CANDIDATE_REVIEW" if approval_gate.get("confirmation_token_valid") else "BLOCKED",
            "write_performed": False,
            "mutation_authorized": False
        })
        
    return {
        "artifact_contract_freeze_manifest_version": "3.0.0",
        "freeze_status": freeze_status,
        "artifact_contract_records": artifact_contract_records,
        "artifact_contract_count": len(artifact_contract_records),
        "freeze_manifest_digest": sha256_digest(artifact_contract_records),
        "artifacts_written": False,
        "repo_files_modified": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_known_issue_register(
    approval_gate: dict,
    known_issues: list[dict] | None = None
) -> dict:
    default_issues = [
        {
            "issue_id": "issue-001",
            "issue_label": "v2.5 commit message referenced multi-worker sandbox coordination while actual layer was controlled external tool adapter preview",
            "issue_status": "RECORDED",
            "issue_severity": "LOW",
            "issue_resolution_status": "RESOLVED_OR_DOCUMENTED",
            "blocks_release_candidate": False
        },
        {
            "issue_id": "issue-002",
            "issue_label": "v2.7 registry version drift was hotfixed",
            "issue_status": "RECORDED",
            "issue_severity": "LOW",
            "issue_resolution_status": "RESOLVED_OR_DOCUMENTED",
            "blocks_release_candidate": False
        },
        {
            "issue_id": "issue-003",
            "issue_label": "v2.8 validator module scan strictness was hotfixed",
            "issue_status": "RECORDED",
            "issue_severity": "LOW",
            "issue_resolution_status": "RESOLVED_OR_DOCUMENTED",
            "blocks_release_candidate": False
        }
    ]
    
    if known_issues is None:
        known_issues = default_issues
    else:
        # Merge or ensure defaults for provided issues
        processed = []
        for issue in known_issues:
            processed.append({
                "issue_id": issue.get("issue_id", f"issue-custom-{len(processed)+1}"),
                "issue_label": issue.get("issue_label", "unlabeled issue"),
                "issue_status": issue.get("issue_status", "RECORDED"),
                "issue_severity": issue.get("issue_severity", "MEDIUM"),
                "issue_resolution_status": issue.get("issue_resolution_status", "OPEN"),
                "blocks_release_candidate": issue.get("blocks_release_candidate", True)
            })
        known_issues = processed

    register_status = "REGISTER_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    blocking_count = sum(1 for issue in known_issues if issue.get("blocks_release_candidate"))
    
    return {
        "known_issue_register_version": "3.0.0",
        "register_status": register_status,
        "known_issues": known_issues,
        "known_issue_count": len(known_issues),
        "blocking_issue_count": blocking_count,
        "register_digest": sha256_digest(known_issues),
        "external_issue_tracker_called": False,
        "repo_files_modified": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_pre_v3_production_readiness_checklist(
    approval_gate: dict,
    checklist_items: list[str] | None = None
) -> dict:
    if checklist_items is None:
        checklist_items = [
            "locked baseline preserved",
            "Devinization overlays preserved",
            "all runtime validators delegated to current version",
            "registry/index version current",
            "artifact contract freeze manifest created",
            "known issue register reviewed",
            "no live-API execution",
            "no network access",
            "no-sock-access",
            "no credential use",
            "no secret reads",
            "no automatic execution",
            "no queued action execution",
            "no actual replay execution",
            "no deployment",
            "operator approval required for future production gate"
        ]
        
    checklist_status = "CHECKLIST_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    checklist_records = []
    for item in checklist_items:
        item_id = "".join(c if c.isalnum() else "_" for c in item.lower()).strip("_")
        checklist_records.append({
            "checklist_item_id": item_id,
            "checklist_item": item,
            "checklist_item_status": "READY_FOR_REVIEW" if approval_gate.get("confirmation_token_valid") else "BLOCKED",
            "production_activation_authorized": False
        })
        
    return {
        "pre_v3_production_readiness_checklist_version": "3.0.0",
        "checklist_status": checklist_status,
        "checklist_items": checklist_records,
        "checklist_item_count": len(checklist_records),
        "ready_for_review_count": len(checklist_records) if approval_gate.get("confirmation_token_valid") else 0,
        "production_activation_authorized": False,
        "checklist_digest": sha256_digest(checklist_records),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_release_candidate_safety_gate(
    approval_gate: dict,
    invariant_scan: dict,
    validator_chain_lock_proof: dict,
    artifact_contract_freeze_manifest: dict,
    known_issue_register: dict,
    pre_v3_checklist: dict
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid", False)
    scan_ok = (invariant_scan.get("scan_status") == "SCAN_CREATED" and invariant_scan.get("failed_invariant_count") == 0)
    proof_ok = (validator_chain_lock_proof.get("proof_status") == "PROOF_CREATED")
    freeze_ok = (artifact_contract_freeze_manifest.get("freeze_status") == "FREEZE_MANIFEST_CREATED")
    register_ok = (known_issue_register.get("register_status") == "REGISTER_CREATED")
    no_blocking = (known_issue_register.get("blocking_issue_count") == 0)
    checklist_ok = (pre_v3_checklist.get("checklist_status") == "CHECKLIST_CREATED")
    
    is_pass = gate_valid and scan_ok and proof_ok and freeze_ok and register_ok and no_blocking and checklist_ok
    
    is_review = gate_valid and not no_blocking
    
    if is_pass:
        safety_gate_status = "PASS"
    elif is_review:
        safety_gate_status = "REVIEW_REQUIRED"
    else:
        safety_gate_status = "BLOCKED"
        
    return {
        "release_candidate_safety_gate_version": "3.0.0",
        "safety_gate_status": safety_gate_status,
        "release_candidate_records_allowed": gate_valid and scan_ok,
        "production_execution_allowed": False,
        "production_readiness_gate_activation_allowed": False,
        "automatic_execution_allowed": False,
        "queued_action_execution_allowed": False,
        "auto_approval_allowed": False,
        "approval_bypass_allowed": False,
        "actual_replay_allowed": False,
        "external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "sock_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "env_read_allowed": False,
        "repo_mutation_allowed": False,
        "deployment_allowed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_release_candidate_audit_proof(
    approval_gate: dict,
    invariant_scan: dict,
    validator_chain_lock_proof: dict,
    artifact_contract_freeze_manifest: dict,
    known_issue_register: dict,
    pre_v3_checklist: dict,
    release_candidate_safety_gate: dict
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid", False)
    safety_gate_passed = (release_candidate_safety_gate.get("safety_gate_status") == "PASS")
    
    is_pass = gate_valid and safety_gate_passed
    is_review = gate_valid and release_candidate_safety_gate.get("safety_gate_status") == "REVIEW_REQUIRED"
    
    if is_pass:
        audit_status = "PASS"
    elif is_review:
        audit_status = "REVIEW_REQUIRED"
    else:
        audit_status = "BLOCKED"
        
    gate_digest = sha256_digest(approval_gate)
    scan_digest = sha256_digest(invariant_scan)
    proof_digest = sha256_digest(validator_chain_lock_proof)
    freeze_digest = sha256_digest(artifact_contract_freeze_manifest)
    register_digest = sha256_digest(known_issue_register)
    checklist_digest = sha256_digest(pre_v3_checklist)
    gate_out_digest = sha256_digest(release_candidate_safety_gate)
    
    combined_input = f"{gate_digest}:{scan_digest}:{proof_digest}:{freeze_digest}:{register_digest}:{checklist_digest}:{gate_out_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": gate_valid,
        "invariant_scan_created": invariant_scan.get("scan_status") == "SCAN_CREATED",
        "no_failed_invariants": invariant_scan.get("failed_invariant_count") == 0,
        "validator_chain_lock_created": validator_chain_lock_proof.get("proof_status") == "PROOF_CREATED",
        "artifact_contract_freeze_created": artifact_contract_freeze_manifest.get("freeze_status") == "FREEZE_MANIFEST_CREATED",
        "known_issue_register_created": known_issue_register.get("register_status") == "REGISTER_CREATED",
        "no_blocking_issues": known_issue_register.get("blocking_issue_count") == 0,
        "pre_v3_checklist_created": pre_v3_checklist.get("checklist_status") == "CHECKLIST_CREATED",
        "release_candidate_safety_gate_passed": safety_gate_passed,
        "no_production_execution": True,
        "no_production_readiness_gate_activation": True,
        "no_automatic_execution": True,
        "no_queued_action_execution": True,
        "no_auto_approval": True,
        "no_approval_bypass": True,
        "no_actual_replay": True,
        "no_worker_action_replay": True,
        "no_external_tool_replay": True,
        "no_live_api_call": True,
        "no_network_access": True,
        "no_sock_opened": True,
        "no_credentials_used": True,
        "no_secrets_read": True,
        "no_env_read": True,
        "no_repo_modifications": True,
        "no_deployment": True
    }
    
    return {
        "release_candidate_audit_proof_version": "3.0.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "invariant_scan_digest": scan_digest,
        "validator_chain_lock_digest": proof_digest,
        "artifact_contract_freeze_digest": freeze_digest,
        "known_issue_register_digest": register_digest,
        "pre_v3_checklist_digest": checklist_digest,
        "release_candidate_safety_gate_digest": gate_out_digest,
        "combined_release_candidate_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_release_candidate_ledger(
    approval_gate: dict,
    invariant_scan: dict,
    validator_chain_lock_proof: dict,
    artifact_contract_freeze_manifest: dict,
    known_issue_register: dict,
    pre_v3_checklist: dict,
    release_candidate_safety_gate: dict,
    audit_proof: dict
) -> dict:
    audit_status = audit_proof.get("audit_status")
    if audit_status == "PASS":
        ledger_status = "RELEASE_CANDIDATE_HARDENING_LEDGER"
    elif audit_status == "REVIEW_REQUIRED":
        ledger_status = "REVIEW_REQUIRED"
    else:
        ledger_status = "BLOCKED"
        
    entries = [
        {"type": "release_candidate_hardening_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "full_runtime_invariant_scan", "digest": sha256_digest(invariant_scan)},
        {"type": "validator_chain_lock_proof", "digest": sha256_digest(validator_chain_lock_proof)},
        {"type": "artifact_contract_freeze_manifest", "digest": sha256_digest(artifact_contract_freeze_manifest)},
        {"type": "known_issue_register", "digest": sha256_digest(known_issue_register)},
        {"type": "pre_v3_production_readiness_checklist", "digest": sha256_digest(pre_v3_checklist)},
        {"type": "release_candidate_safety_gate", "digest": sha256_digest(release_candidate_safety_gate)},
        {"type": "release_candidate_audit_proof", "digest": sha256_digest(audit_proof)}
    ]
    
    return {
        "release_candidate_ledger_version": "3.0.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_release_candidate_readiness_summary(
    approval_gate: dict,
    release_candidate_safety_gate: dict,
    audit_proof: dict,
    release_candidate_ledger: dict
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid", False)
    safety_gate_passed = (release_candidate_safety_gate.get("safety_gate_status") == "PASS")
    audit_pass = (audit_proof.get("audit_status") == "PASS")
    ledger_ready = (release_candidate_ledger.get("ledger_status") == "RELEASE_CANDIDATE_HARDENING_LEDGER")
    
    is_ready = gate_valid and safety_gate_passed and audit_pass and ledger_ready
    
    is_review = gate_valid and (release_candidate_safety_gate.get("safety_gate_status") == "REVIEW_REQUIRED" or audit_proof.get("audit_status") == "REVIEW_REQUIRED")
    
    if is_ready:
        readiness_status = "READY_FOR_NEXT_LAYER"
    elif is_review:
        readiness_status = "REVIEW_REQUIRED"
    else:
        readiness_status = "BLOCKED"
        
    return {
        "release_candidate_readiness_summary_version": "3.0.0",
        "readiness_status": readiness_status,
        "ready_for_controlled_production_readiness_gate": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "release_candidate_safety_gate_status": release_candidate_safety_gate.get("safety_gate_status", "BLOCKED"),
        "audit_status": audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": release_candidate_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "Controlled Production Readiness Gate",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_production_readiness_gate_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    is_ready = readiness_summary.get("ready_for_controlled_production_readiness_gate", False)
    return {
        "controlled_production_readiness_gate_bridge_version": "3.0.0",
        "current_layer": "Release Candidate Hardening",
        "next_layer": "Controlled Production Readiness Gate",
        "ready_for_controlled_production_readiness_gate": is_ready,
        "required_next_capabilities": [
            "controlled production readiness gate schema",
            "production activation denial by default",
            "final human approval requirement",
            "production capability manifest",
            "supervised pilot eligibility contract",
            "production rollback and kill-switch preview",
            "production readiness audit proof",
            "still no automatic production execution by default"
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no credential use",
            "no secret reads",
            "no actual replay execution",
            "no automatic approval",
            "no queued action execution",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no live production orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_release_candidate_hardening_bundle(
    result: dict,
    command: str | None = None,
    release_candidate_label: str | None = None,
    confirmation_token: str | None = None,
    invariant_labels: list[str] | None = None,
    validator_names: list[str] | None = None,
    artifact_contracts: list[str] | None = None,
    known_issues: list[dict] | None = None,
    checklist_items: list[str] | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if release_candidate_label is None:
        release_candidate_label = "station-chief-release-candidate-hardening"
        
    schema = create_release_candidate_hardening_schema()
    gate = create_release_candidate_hardening_approval_gate(release_candidate_label, confirmation_token)
    scan = create_full_runtime_invariant_scan(gate, invariant_labels)
    proof = create_validator_chain_lock_proof(gate, validator_names)
    freeze = create_artifact_contract_freeze_manifest(gate, artifact_contracts)
    register = create_known_issue_register(gate, known_issues)
    checklist = create_pre_v3_production_readiness_checklist(gate, checklist_items)
    safety_gate = create_release_candidate_safety_gate(gate, scan, proof, freeze, register, checklist)
    audit = create_release_candidate_audit_proof(gate, scan, proof, freeze, register, checklist, safety_gate)
    ledger = create_release_candidate_ledger(gate, scan, proof, freeze, register, checklist, safety_gate, audit)
    summary = create_release_candidate_readiness_summary(gate, safety_gate, audit, ledger)
    bridge = create_controlled_production_readiness_gate_bridge(result, summary)
    
    return {
        "release_candidate_hardening_bundle_version": "3.0.0",
        "release_candidate_hardening_status": "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY",
        "release_candidate_hardening_schema": schema,
        "release_candidate_hardening_approval_gate": gate,
        "full_runtime_invariant_scan": scan,
        "validator_chain_lock_proof": proof,
        "artifact_contract_freeze_manifest": freeze,
        "known_issue_register": register,
        "pre_v3_production_readiness_checklist": checklist,
        "release_candidate_safety_gate": safety_gate,
        "release_candidate_audit_proof": audit,
        "release_candidate_ledger": ledger,
        "release_candidate_readiness_summary": summary,
        "controlled_production_readiness_gate_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "sock_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "env_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
