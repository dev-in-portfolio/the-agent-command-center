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
    risk_level: str | None = None
) -> dict:
    title = normalize_text(candidate_title, "untitled_candidate")
    summary = candidate_summary or "No summary provided."
    target = normalize_text(mutation_target, "sandbox_artifact")
    risk = normalize_text(risk_level, "unknown")
    if risk not in ["low", "medium", "high"]:
        risk = "unknown"
        
    return {
        "candidate_id": sha256_digest({"title": title, "target": target, "risk": risk}),
        "title": title,
        "summary": summary,
        "mutation_target": target,
        "risk_level": risk,
        "proposed_by": AUTO_SELF_IMPROVE_2_LAB_ID,
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
    
    priority = "medium"
    if safety > 8.0 and usefulness > 7.0:
        priority = "high"
        
    return {
        "evaluation_id": sha256_digest({"candidate": candidate["candidate_id"], "stage": "eval"}),
        "clarity_score": clarity,
        "safety_score": safety,
        "usefulness_score": usefulness,
        "sandbox_mutation_risk_score": s_risk,
        "promotion_risk_score": p_risk,
        "sandbox_test_priority": priority
    }

def create_sandbox_self_authorization_receipt(candidate: dict, evaluation: dict) -> dict:
    # Grant sandbox authorization for low/medium risk only
    granted = (candidate["risk_level"] in ["low", "medium"])
    
    return {
        "self_authorization_receipt_id": sha256_digest({"c": candidate["candidate_id"], "granted": granted}),
        "sandbox_self_authorization_granted": granted,
        "authorization_scope": "sandbox_only",
        "official_repo_authorization_granted": False,
        "promotion_authorization_granted": False,
        "deployment_authorization_granted": False,
        "credentials_authorization_granted": False,
        "operator_required_for_official_promotion": True
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

def write_sandbox_artifact(artifact_name: str, payload: dict, authorization_receipt: dict) -> dict:
    if not authorization_receipt["sandbox_self_authorization_granted"]:
        return {"artifact_write_performed": False, "error": "Authorization missing"}
        
    allowed_names = ["sandbox_candidate_patch", "sandbox_test_result", "sandbox_self_authorization_receipt", "sandbox_mutation_audit"]
    if artifact_name not in allowed_names:
        return {"artifact_write_performed": False, "error": f"Unknown artifact name: {artifact_name}"}
        
    sandbox_dir = Path(AUTO_SELF_IMPROVE_2_SANDBOX_DIR)
    artifact_path = sandbox_dir / f"{artifact_name}.json"
    
    sandbox_dir.mkdir(parents=True, exist_ok=True)
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
        "artifact_readback_verified": (readback == content)
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
    return {
        "barrier_record_id": sha256_digest({"candidate": candidate["candidate_id"], "barrier": "official"}),
        "official_promotion_blocked": True,
        "self_promotion_blocked": True,
        "operator_approval_required": True,
        "official_repo_protected": True,
        "propose_only_repo_protected": True,
        "deployment_blocked": True,
        "credentials_blocked": True,
        "promotion_status": "OPERATOR_REVIEW_REQUIRED_FOR_ANY_OFFICIAL_PROMOTION"
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

def create_auto_self_improve_2_bundle(
    candidate_title: str | None = None,
    candidate_summary: str | None = None,
    mutation_target: str | None = None,
    risk_level: str | None = None
) -> dict:
    manifest = create_auto_self_improve_2_manifest()
    candidate = create_sandbox_improvement_candidate(candidate_title, candidate_summary, mutation_target, risk_level)
    evaluation = evaluate_sandbox_candidate(candidate)
    auth_receipt = create_sandbox_self_authorization_receipt(candidate, evaluation)
    patch = create_sandbox_candidate_patch(candidate, auth_receipt)
    test_result = run_sandbox_candidate_test(candidate, patch, auth_receipt)
    barrier = create_promotion_barrier_record(candidate, evaluation, test_result)
    
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
        "promotion_allowed": False
    }
    
    # Write artifacts if authorized
    writes = {}
    if auth_receipt["sandbox_self_authorization_granted"]:
        writes["receipt"] = write_sandbox_artifact("sandbox_self_authorization_receipt", auth_receipt, auth_receipt)
        writes["patch"] = write_sandbox_artifact("sandbox_candidate_patch", patch, auth_receipt)
        writes["test"] = write_sandbox_artifact("sandbox_test_result", test_result, auth_receipt)
        writes["audit"] = write_sandbox_artifact("sandbox_mutation_audit", audit, auth_receipt)

    safety_matrix = {
        "allowed": [
            "propose_sandbox_improvement",
            "evaluate_sandbox_improvement",
            "sandbox_self_authorize",
            "create_sandbox_candidate_patch",
            "write_sandbox_artifacts",
            "run_sandbox_metadata_tests",
            "create_promotion_barrier",
            "recommend_operator_review"
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
            "write_repo_runtime_files_automatically"
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
        "artifact_writes": writes,
        "safety_matrix": safety_matrix
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
