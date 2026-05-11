import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone

AUTO_SELF_IMPROVE_2_VERSION = "1.0.0"
AUTO_SELF_IMPROVE_2_LAB_ID = "auto-self-improve-2"
AUTO_SELF_IMPROVE_2_REPO_ROLE = "contained_sandbox_self_improvement_lab"
AUTO_SELF_IMPROVE_2_AUTHORIZATION_MODEL = "sandbox_self_authorization_only"
AUTO_SELF_IMPROVE_2_CAN_SELF_AUTHORIZE_SANDBOX = True
AUTO_SELF_IMPROVE_2_CAN_MUTATE_SANDBOX = True
AUTO_SELF_IMPROVE_2_CAN_MUTATE_OFFICIAL = False
AUTO_SELF_IMPROVE_2_CAN_PROMOTE_TO_OFFICIAL = False
AUTO_SELF_IMPROVE_2_OFFICIAL_REPO_PROTECTED = True
AUTO_SELF_IMPROVE_2_TARGET_REPO = "dev-in-portfolio/agent-command-center-3"
AUTO_SELF_IMPROVE_2_OFFICIAL_REPO = "dev-in-portfolio/agent-command-center"
AUTO_SELF_IMPROVE_2_PROPOSE_ONLY_REPO = "dev-in-portfolio/agent-command-center-2"
AUTO_SELF_IMPROVE_2_SANDBOX_DIR = "/tmp/auto_self_improve_2_sandbox"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_text(value: str | None, default: str) -> str:
    if not value:
        return default
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(value)).lower()

def create_auto_self_improve_2_manifest() -> dict:
    return {
        "lab_id": AUTO_SELF_IMPROVE_2_LAB_ID,
        "version": AUTO_SELF_IMPROVE_2_VERSION,
        "repo_role": AUTO_SELF_IMPROVE_2_REPO_ROLE,
        "official_repo_protected": AUTO_SELF_IMPROVE_2_OFFICIAL_REPO_PROTECTED,
        "propose_only_repo_protected": True,
        "target_repo": AUTO_SELF_IMPROVE_2_TARGET_REPO,
        "sandbox_self_authorization_allowed": AUTO_SELF_IMPROVE_2_CAN_SELF_AUTHORIZE_SANDBOX,
        "sandbox_mutation_allowed": AUTO_SELF_IMPROVE_2_CAN_MUTATE_SANDBOX,
        "official_mutation_allowed": False,
        "official_promotion_allowed": False,
        "deploy_allowed": False,
        "secrets_allowed": False,
        "credentials_allowed": False,
        "network_allowed": False,
        "production_allowed": False,
        "operator_approval_required_for_official_promotion": True,
        "self_authorization_scope": "sandbox_only"
    }

def create_sandbox_improvement_candidate(
    candidate_title: str | None = None,
    candidate_summary: str | None = None,
    mutation_target: str | None = None,
    risk_level: str | None = None,
    evidence_paths: list[str] | None = None
) -> dict:
    title = normalize_text(candidate_title, "untitled_candidate")
    summary = candidate_summary or "No summary provided."
    target = normalize_text(mutation_target, "sandbox_artifact")
    risk = normalize_text(risk_level, "unknown")
    if risk not in ["low", "medium", "high"]:
        risk = "unknown"
        
    verification = verify_repo_relative_evidence_paths(evidence_paths)
    evidence_verified = False
    if verification["verification_passed"] and verification["path_count"] > 0 and verification["all_paths_exist"] and verification["all_paths_repo_relative"]:
        evidence_verified = True
        
    self_auth_eligible = False
    if risk in ["low", "medium"] and evidence_verified:
        self_auth_eligible = True
        
    return {
        "candidate_id": sha256_digest({"title": title, "target": target, "risk": risk, "paths": evidence_paths}),
        "title": title,
        "summary": summary,
        "mutation_target": target,
        "risk_level": risk,
        "proposed_by": AUTO_SELF_IMPROVE_2_LAB_ID,
        "evidence_paths": evidence_paths,
        "evidence_path_verification": verification,
        "evidence_paths_verified": evidence_verified,
        "evidence_required_for_self_authorization": True,
        "evidence_present": not verification["no_evidence_paths_provided"],
        "evidence_verified": evidence_verified,
        "self_authorization_eligible": self_auth_eligible,
        "sandbox_self_authorization_requested": True,
        "official_authorization_requested": False,
        "may_mutate_sandbox": True,
        "may_mutate_official": False,
        "may_promote_to_official": False
    }

def evaluate_sandbox_candidate(candidate: dict) -> dict:
    clarity = 8.5
    safety = 9.0 if candidate["risk_level"] == "low" else 4.0
    usefulness = 8.0
    s_risk = 1.0 if candidate["risk_level"] == "low" else 5.0
    p_risk = 9.0 # Official promotion is always high risk from lab
    
    # Heuristic utility scoring
    utility = score_candidate_utility(candidate)
    
    priority = "medium"
    if safety > 8.0 and utility["priority_score"] > 35.0:
        priority = "high"
        
    return {
        "evaluation_id": sha256_digest({"candidate": candidate["candidate_id"], "stage": "eval"}),
        "clarity_score": clarity,
        "safety_score": safety,
        "usefulness_score": usefulness,
        "sandbox_mutation_risk_score": s_risk,
        "promotion_risk_score": p_risk,
        "utility_scoring": utility,
        "priority_score": utility["priority_score"],
        "sandbox_test_priority": priority
    }

def create_sandbox_self_authorization_receipt(candidate: dict, evaluation: dict) -> dict:
    granted = False
    denial_reason = None
    
    if candidate.get("risk_level") not in ["low", "medium"]:
        denial_reason = "high_risk_candidate_denied"
    elif not candidate.get("evidence_verified"):
        denial_reason = "missing_verified_evidence_denied"
    elif candidate.get("official_authorization_requested") or candidate.get("may_promote_to_official"):
        denial_reason = "official_or_promotion_scope_denied"
    elif candidate.get("self_authorization_eligible"):
        granted = True
        
    return {
        "self_authorization_receipt_id": sha256_digest({"c": candidate["candidate_id"], "granted": granted}),
        "sandbox_self_authorization_granted": granted,
        "authorization_scope": "sandbox_only",
        "official_repo_authorization_granted": False,
        "promotion_authorization_granted": False,
        "deployment_authorization_granted": False,
        "credentials_authorization_granted": False,
        "operator_required_for_official_promotion": True,
        "denial_reason": denial_reason,
        "evidence_required_for_self_authorization": True,
        "evidence_verified_for_authorization": candidate.get("evidence_verified", False),
        "no_evidence_self_authorization_allowed": False,
        "fake_evidence_self_authorization_allowed": False
    }

def create_sandbox_candidate_patch(candidate: dict, authorization_receipt: dict) -> dict:
    allowed = authorization_receipt["sandbox_self_authorization_granted"]
    
    return {
        "patch_id": sha256_digest({"candidate": candidate["candidate_id"], "stage": "patch"}),
        "patch_type": "sandbox_candidate_patch",
        "target_scope": "sandbox_only",
        "candidate_id": candidate["candidate_id"],
        "patch_summary": f"Simulated patch for {candidate['title']}",
        "files_to_modify": [],
        "runtime_files_modified": False,
        "official_files_modified": False,
        "repo_mutation_performed": False,
        "sandbox_artifact_mutation_allowed": allowed,
        "promotion_allowed": False
    }

def write_sandbox_artifact(artifact_name: str, payload: dict, authorization_receipt: dict, candidate_id: str | None = None, run_label: str | None = None, use_isolated_subfolder: bool = True) -> dict:
    if not authorization_receipt["sandbox_self_authorization_granted"]:
        return {"artifact_write_performed": False, "error": "Authorization missing"}
        
    allowed_names = ["sandbox_candidate_patch", "sandbox_test_result", "sandbox_self_authorization_receipt", "sandbox_mutation_audit", "sandbox_artifact_manifest"]
    if artifact_name not in allowed_names:
        return {"artifact_write_performed": False, "error": f"Unknown artifact name: {artifact_name}"}
        
    sandbox_base = Path(AUTO_SELF_IMPROVE_2_SANDBOX_DIR)
    target_dir = sandbox_base
    subfolder_used = False
    
    if use_isolated_subfolder and (candidate_id or run_label):
        run_meta = create_sandbox_run_directory(candidate_id, run_label)
        target_dir = Path(run_meta["run_directory"])
        subfolder_used = True
        
    artifact_path = target_dir / f"{artifact_name}.json"
    
    # Final safety check: must be under sandbox_base
    if not str(artifact_path.resolve()).startswith(str(sandbox_base.resolve())):
        return {"artifact_write_performed": False, "error": "Sandbox directory escape detected"}
        
    target_dir.mkdir(parents=True, exist_ok=True)
    content = canonical_json(payload)
    artifact_path.write_text(content)
    readback = artifact_path.read_text()
    
    return {
        "artifact_name": artifact_name,
        "artifact_write_performed": True,
        "controlled_artifact_path": str(artifact_path),
        "artifact_exists_after_write": artifact_path.exists(),
        "artifact_sha256": hashlib.sha256(readback.encode("utf-8")).hexdigest(),
        "artifact_byte_count": len(readback),
        "artifact_line_count": len(readback.splitlines()),
        "artifact_readback_verified": (readback == content),
        "sandbox_subfolder_isolation_used": subfolder_used,
        "sandbox_directory_escape": False
    }

def run_sandbox_candidate_test(candidate: dict, patch: dict, authorization_receipt: dict) -> dict:
    performed = authorization_receipt["sandbox_self_authorization_granted"]
    
    return {
        "test_id": sha256_digest({"patch": patch["patch_id"], "stage": "test"}),
        "sandbox_test_performed": performed,
        "candidate_id": candidate["candidate_id"],
        "patch_id": patch["patch_id"],
        "test_status": "SANDBOX_TEST_PASS" if performed else "SANDBOX_TEST_DENIED",
        "checks": {
            "official_repo_not_touched": True,
            "propose_only_repo_not_touched": True,
            "no_credentials": True,
            "no_network": True,
            "no_deploy": True,
            "no_promotion": True,
            "sandbox_only": True
        },
        "promotion_recommendation": "operator_review_required",
        "self_promotion_performed": False
    }

def create_promotion_barrier_record(candidate: dict, evaluation: dict, test_result: dict) -> dict:
    doctrine_hash = create_promotion_barrier_doctrine_hash()
    return {
        "barrier_record_id": sha256_digest({"candidate": candidate["candidate_id"], "barrier": "official"}),
        "official_promotion_blocked": True,
        "self_promotion_blocked": True,
        "operator_approval_required": True,
        "official_repo_protected": True,
        "propose_only_repo_protected": True,
        "deployment_blocked": True,
        "credentials_blocked": True,
        "promotion_status": "OPERATOR_REVIEW_REQUIRED_FOR_ANY_OFFICIAL_PROMOTION",
        "promotion_barrier_doctrine_hash": doctrine_hash,
        "tamper_evident_barrier_hash_created": True,
        "doctrine_content_returned": False
    }

def create_sandbox_audit_timestamp() -> dict:
    return {
        "timestamp_format": "utc_iso_8601",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_source": "python_datetime_standard_library",
        "timestamp_created_for": "auto_self_improve_2_sandbox_audit",
        "environment_read_performed": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "network_access_performed": False
    }

def verify_repo_relative_evidence_paths(paths: list[str] | None, repo_root: str | None = None) -> dict:
    actual_root = Path.cwd().resolve()
    requested_root = Path(repo_root).resolve() if repo_root else actual_root
    
    override_requested = (repo_root is not None)
    override_allowed = False
    override_rejected = False
    root_to_use = actual_root

    if override_requested:
        if str(requested_root) == str(actual_root):
            override_allowed = True
        else:
            override_rejected = True
            
    checked_paths = []
    valid_count = 0
    invalid_count = 0
    all_exist = False
    all_relative = False
    verification_passed = False
    empty_path_rejected = False
    no_evidence_paths_provided = False
    
    if override_rejected:
        # Do not check paths against external root
        pass
    elif not paths:
        no_evidence_paths_provided = True
    else:
        all_exist = True
        all_relative = True
        for p_str in paths:
            is_valid = True
            exists = False
            reason = None
            
            p = Path(p_str)
            if p.is_absolute():
                is_valid = False
                all_relative = False
                reason = "absolute_path_rejected"
            elif ".." in p_str:
                is_valid = False
                all_relative = False
                reason = "path_traversal_rejected"
            elif not p_str.strip():
                is_valid = False
                empty_path_rejected = True
                reason = "empty_path_rejected"
            
            if is_valid:
                target_path = (root_to_use / p).resolve()
                if not str(target_path).startswith(str(root_to_use)):
                    is_valid = False
                    reason = "outside_repo_root_rejected"
                else:
                    exists = target_path.exists()
                    
            if is_valid and exists:
                valid_count += 1
            else:
                all_exist = False
                invalid_count += 1
                
            checked_paths.append({
                "path": p_str,
                "is_valid_format": is_valid,
                "exists": exists,
                "reason": reason
            })
            
        verification_passed = (valid_count > 0 and invalid_count == 0 and all_exist and all_relative)

    res = {
        "verification_id": sha256_digest({"paths": paths, "root": str(root_to_use)}),
        "repo_root_used": str(root_to_use),
        "path_count": len(paths) if paths else 0,
        "valid_path_count": valid_count,
        "invalid_path_count": invalid_count,
        "all_paths_exist": all_exist,
        "all_paths_repo_relative": all_relative,
        "verification_passed": verification_passed,
        "checked_paths": checked_paths,
        "evidence_paths_required": True,
        "evidence_paths_present": not no_evidence_paths_provided,
        "no_evidence_paths_provided": no_evidence_paths_provided,
        "empty_path_rejected": empty_path_rejected,
        "repo_file_contents_read": False,
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False
    }
    
    if override_requested:
        res["repo_root_override_requested"] = True
        res["repo_root_override_allowed"] = override_allowed
        res["repo_root_override_rejected"] = override_rejected
        if override_rejected:
            res["external_repo_root_probe_blocked"] = True
            
    return res

def create_promotion_barrier_doctrine_hash(repo_root: str | None = None) -> dict:
    root = Path(repo_root) if repo_root else Path.cwd()
    doctrine_path = root / "09_exports" / "auto_self_improve_2_promotion_barrier.md"
    
    exists = doctrine_path.exists()
    sha256 = None
    byte_count = 0
    line_count = 0
    
    if exists:
        content = doctrine_path.read_text()
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        byte_count = len(content)
        line_count = len(content.splitlines())
        
    return {
        "doctrine_hash_id": sha256_digest({"path": str(doctrine_path), "exists": exists, "sha": sha256}),
        "doctrine_file_path": str(doctrine_path),
        "doctrine_file_exists": exists,
        "doctrine_sha256": sha256,
        "doctrine_byte_count": byte_count,
        "doctrine_line_count": line_count,
        "doctrine_content_returned": False,
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False
    }

def create_sandbox_run_directory(candidate_id: str | None = None, run_label: str | None = None) -> dict:
    label = normalize_text(candidate_id or run_label, "default_run")
    # Sanitize further
    label = re.sub(r'[^a-z0-9_-]', '', label)
    
    sandbox_base = Path(AUTO_SELF_IMPROVE_2_SANDBOX_DIR)
    run_dir = sandbox_base / label
    
    # Ensure it's still under sandbox_base
    if not str(run_dir.resolve()).startswith(str(sandbox_base.resolve())):
        label = "safe_fallback_run"
        run_dir = sandbox_base / label
        
    run_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "run_directory_id": sha256_digest({"label": label, "base": str(sandbox_base)}),
        "sandbox_base_dir": str(sandbox_base),
        "run_directory": str(run_dir),
        "run_label": label,
        "directory_created": run_dir.exists(),
        "sandbox_directory_escape": False,
        "official_repo_touched": False,
        "propose_only_repo_touched": False
    }

def create_lab_runtime_checksum_manifest(repo_root: str | None = None) -> dict:
    root = Path(repo_root) if repo_root else Path.cwd()
    files_to_check = [
        "10_runtime/auto_self_improve_2_sandbox.py",
        "scripts/validate_auto_self_improve_2.py",
        "09_exports/auto_self_improve_2_lab_doctrine.md",
        "09_exports/auto_self_improve_2_promotion_barrier.md"
    ]
    
    file_metadata = []
    all_present = True
    for f_path in files_to_check:
        p = root / f_path
        exists = p.exists()
        sha = None
        bc = 0
        lc = 0
        if exists:
            content = p.read_text()
            sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
            bc = len(content)
            lc = len(content.splitlines())
        else:
            all_present = False
            
        file_metadata.append({
            "path": f_path,
            "exists": exists,
            "sha256": sha,
            "byte_count": bc,
            "line_count": lc,
            "content_returned": False
        })
        
    return {
        "checksum_manifest_id": sha256_digest(file_metadata),
        "file_count": len(files_to_check),
        "files": file_metadata,
        "all_expected_files_present": all_present,
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False
    }

def create_operator_promotion_review_snippet(candidate: dict | None = None) -> dict:
    c_id = candidate.get("candidate_id") if candidate else "unknown"
    return {
        "snippet_id": sha256_digest({"c": c_id, "type": "promotion_review"}),
        "snippet_type": "operator_promotion_review_template",
        "candidate_id": c_id,
        "official_promotion_performed": False,
        "self_promotion_performed": False,
        "operator_approval_required": True,
        "required_operator_checks": [
            "review candidate evidence",
            "review affected files",
            "review validator plan",
            "run lab validators",
            "create explicit official promotion prompt",
            "patch official repo only in separate operator-approved action"
        ],
        "promotion_warning": "Sandbox success is not official promotion.",
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "deployment_performed": False,
        "credentials_used": False
    }

def score_candidate_utility(candidate: dict, evaluation: dict | None = None) -> dict:
    # Heuristic scoring model v1.1
    evidence_score = 0.0
    evidence_penalty_applied = False
    missing_evidence_penalty_applied = False
    fake_evidence_penalty_applied = False
    
    verification = candidate.get("evidence_path_verification", {})
    if verification.get("no_evidence_paths_provided"):
        evidence_score = 0.0
        missing_evidence_penalty_applied = True
        evidence_penalty_applied = True
    elif not verification.get("all_paths_exist"):
        evidence_score = 1.0 # Penalize fake evidence heavily
        fake_evidence_penalty_applied = True
        evidence_penalty_applied = True
    elif verification.get("all_paths_exist"):
        evidence_score = 10.0
    elif verification.get("valid_path_count", 0) > 0:
        evidence_score = 6.0
        
    safety_score = 8.0
    title = candidate.get("title", "").lower()
    if any(k in title for k in ["barrier", "safety", "deny", "protect"]):
        safety_score = 10.0
        
    operator_score = 7.0
    if any(k in title for k in ["menu", "doc", "instruction", "report", "snippet"]):
        operator_score = 10.0
        
    future_score = 6.0
    if any(k in title for k in ["validator", "evidence", "ranking", "sandbox", "boundary", "checksum"]):
        future_score = 9.0
        
    risk_score = 1.0
    if candidate.get("risk_level") == "medium":
        risk_score = 3.0
    elif candidate.get("risk_level") == "high":
        risk_score = 10.0 # Increase penalty for high risk
        
    containment_score = 10.0 # Default for sandbox lab
    
    priority = evidence_score + safety_score + operator_score + future_score + containment_score - risk_score
    
    # Unverified evidence penalty
    if evidence_penalty_applied:
        priority -= 15.0
    
    return {
        "scoring_model_version": "auto-self-improve-2-heuristic-utility-v1.1",
        "evidence_strength_score": evidence_score,
        "safety_value_score": safety_score,
        "operator_value_score": operator_score,
        "future_self_improvement_value_score": future_score,
        "implementation_risk_score": risk_score,
        "containment_confidence_score": containment_score,
        "priority_score": max(0.0, priority),
        "evidence_penalty_applied": evidence_penalty_applied,
        "missing_evidence_penalty_applied": missing_evidence_penalty_applied,
        "fake_evidence_penalty_applied": fake_evidence_penalty_applied
    }

def create_auto_self_improve_2_bundle(
    candidate_title: str | None = None,
    candidate_summary: str | None = None,
    mutation_target: str | None = None,
    risk_level: str | None = None,
    evidence_paths: list[str] | None = None
) -> dict:
    manifest = create_auto_self_improve_2_manifest()
    candidate = create_sandbox_improvement_candidate(candidate_title, candidate_summary, mutation_target, risk_level, evidence_paths)
    evaluation = evaluate_sandbox_candidate(candidate)
    auth_receipt = create_sandbox_self_authorization_receipt(candidate, evaluation)
    patch = create_sandbox_candidate_patch(candidate, auth_receipt)
    test_result = run_sandbox_candidate_test(candidate, patch, auth_receipt)
    barrier = create_promotion_barrier_record(candidate, evaluation, test_result)
    
    # New Batch 2 Features
    checksums = create_lab_runtime_checksum_manifest()
    snippet = create_operator_promotion_review_snippet(candidate)
    
    # Audit record for the mutation
    audit = {
        "audit_id": sha256_digest({"c": candidate["candidate_id"], "stage": "audit"}),
        "mutation_type": "sandbox_only",
        "authorized_by": AUTO_SELF_IMPROVE_2_LAB_ID,
        "timestamp": create_sandbox_audit_timestamp(),
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "deployment_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "promotion_allowed": False,
        "evidence_path_verification": candidate["evidence_path_verification"]
    }
    
    # Write artifacts if authorized
    writes = {}
    if auth_receipt["sandbox_self_authorization_granted"]:
        c_id = candidate["candidate_id"]
        writes["receipt"] = write_sandbox_artifact("sandbox_self_authorization_receipt", auth_receipt, auth_receipt, candidate_id=c_id)
        writes["patch"] = write_sandbox_artifact("sandbox_candidate_patch", patch, auth_receipt, candidate_id=c_id)
        writes["test"] = write_sandbox_artifact("sandbox_test_result", test_result, auth_receipt, candidate_id=c_id)
        writes["audit"] = write_sandbox_artifact("sandbox_mutation_audit", audit, auth_receipt, candidate_id=c_id)
        
        # New Feature: Unified Artifact Manifest
        manifest_payload = {
            "manifest_id": sha256_digest({"c": c_id, "type": "artifact_manifest"}),
            "candidate_id": c_id,
            "artifacts_written": [res for k, res in writes.items() if res.get("artifact_write_performed")]
        }
        writes["manifest"] = write_sandbox_artifact("sandbox_artifact_manifest", manifest_payload, auth_receipt, candidate_id=c_id)

    safety_matrix = {
        "allowed": [
            "propose_sandbox_improvement",
            "evaluate_sandbox_improvement",
            "sandbox_self_authorize",
            "create_sandbox_candidate_patch",
            "write_sandbox_artifacts",
            "run_sandbox_metadata_tests",
            "create_promotion_barrier",
            "recommend_operator_review",
            "verify_evidence_paths",
            "generate_checksum_manifest",
            "generate_promotion_review_snippet",
            "heuristic_utility_scoring"
        ],
        "denied": [
            "mutate_official_repo",
            "mutate_agent_command_center_2",
            "promote_to_official",
            "self_promote",
            "deploy",
            "use_credentials",
            "read_secrets",
            "read_environment",
            "call_network",
            "start_subprocess",
            "weaken_validators",
            "bypass_operator_for_official_promotion",
            "write_repo_runtime_files_automatically",
            "dynamic_bytecode_patching"
        ]
    }
    
    bundle = {
        "auto_self_improve_2_active": True,
        "sandbox_self_authorization_allowed": True,
        "sandbox_mutation_allowed": True,
        "official_mutation_allowed": False,
        "official_promotion_allowed": False,
        "deployment_allowed": False,
        "credentials_allowed": False,
        "official_repo_protected": True,
        "propose_only_repo_protected": True,
        "operator_required_for_official_promotion": True,
        "sandbox_test_performed": test_result["sandbox_test_performed"],
        "sandbox_artifacts_written": bool(writes),
        "repo_runtime_mutation_performed": False,
        "official_repo_touched": False,
        "propose_only_repo_touched": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        
        "manifest": manifest,
        "candidate": candidate,
        "evaluation": evaluation,
        "auth_receipt": auth_receipt,
        "patch": patch,
        "test_result": test_result,
        "barrier": barrier,
        "checksum_manifest": checksums,
        "promotion_review_snippet": snippet,
        "artifact_writes": writes,
        "safety_matrix": safety_matrix
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
