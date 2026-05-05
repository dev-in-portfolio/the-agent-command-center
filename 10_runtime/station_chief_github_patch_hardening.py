import json
import hashlib
import re
import difflib
from pathlib import Path

GITHUB_PATCH_HARDENING_MODULE_VERSION = "3.5.0"
GITHUB_PATCH_HARDENING_STATUS = "PATCH_HARDENING_CONTRACT_ONLY"
GITHUB_PATCH_HARDENING_PHASE = "GitHub Patch Application Hardening"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_patch_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "patch-hardening"

def generate_patch_hardening_id(command: str, label: str, runtime_version: str = "3.5.0") -> str:
    normalized_label = normalize_patch_label(label)
    hash_input = f"{runtime_version}:{command}:{label}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"patch-hardening-v3-4-{normalized_label}-{hash_chars}"

def create_patch_hardening_schema() -> dict:
    return {
        "patch_hardening_schema_version": "3.5.0",
        "schema_status": "PATCH_HARDENING_CONTRACT_ONLY",
        "required_sections": [
            "protected_path_policy",
            "patch_root_validation",
            "patch_preview_diff_contract",
            "patch_digest_manifest",
            "patch_rollback_preview",
            "changed_file_proof",
            "human_approval_chain_binding",
            "patch_execution_readiness_score",
            "patch_hardening_audit_bundle"
        ],
        "allowed_patch_modes": [
            "read_only_patch_review",
            "dry_run_patch_preview",
            "sandbox_patch_preview",
            "explicit_scoped_repo_patch_only"
        ],
        "blocked_patch_modes": [
            "uncontrolled_repo_edit",
            "baseline_file_patch",
            "Devinization_overlay_patch",
            "GitHub_API_patch",
            "direct_push",
            "unconfirmed_patch_application",
            "broad_directory_patch",
            "generated_artifact_patch",
            "external_action_patch"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_SCOPED_REPO_PATCH"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no GitHub API mutation",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no protected path writes",
            "no patch outside explicit patch root",
            "no patch outside explicit allowlist",
            "no shell command execution",
            "no package installation",
            "patch hardening contracts do not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_protected_path_policy() -> dict:
    return {
        "protected_path_policy_version": "3.5.0",
        "policy_status": "ACTIVE_CONTRACT",
        "protected_paths": [
            "09_exports/dashboard_seed.json",
            "09_exports/org_chart_export.json",
            "09_exports/master_department_list.md"
        ],
        "protected_path_prefixes": [
            "02_departments/",
            "04_workflow_templates/",
            "09_exports/devinization_pack_",
            "09_exports/final_devinization_stack",
            "09_exports/devin_ownership",
            "ownership",
            "metadata"
        ],
        "generated_artifact_prefixes": [
            "station_chief_runs/",
            "station_chief_registry/",
            "station_chief_execution/",
            "station_chief_dry_run/",
            "station_chief_approval/",
            "station_chief_release_lock/",
            "station_chief_controlled_execution/",
            "station_chief_work_orders/",
            "station_chief_worker_registry/",
            "station_chief_department_routing/",
            "station_chief_orchestration/",
            "station_chief_operator_console/",
            "station_chief_patch_hardening/"
        ],
        "allowed_patch_roots_policy": [
            "explicit user-provided patch root only",
            "patch root must resolve safely",
            "patch target must remain inside patch root",
            "patch target must match allowed relative file",
            "patch target must not match protected path policy",
            "patch application still requires YES_I_APPROVE_SCOPED_REPO_PATCH"
        ],
        "policy_reason": "Protected path policy prevents accidental mutation of locked baseline, Devinization overlays, ownership metadata, generated artifacts, and non-allowlisted repository areas.",
        "baseline_preserved": True,
        "repo_patch_applied": False,
        "execution_authorized": False
    }

def is_path_protected(path: str, protected_policy: dict | None = None) -> dict:
    if protected_policy is None:
        protected_policy = create_protected_path_policy()
        
    normalized = path.replace("\\", "/").lstrip("/")
    
    is_protected = False
    matched_rule = None
    reason = "Path allowed."
    
    if normalized in protected_policy["protected_paths"]:
        is_protected = True
        matched_rule = f"protected_path: {normalized}"
        reason = "Exact match in protected path list."
    elif any(normalized.startswith(p) for p in protected_policy["protected_path_prefixes"]):
        is_protected = True
        matched_rule = "protected_path_prefix"
        reason = "Path starts with protected prefix."
    elif any(normalized.startswith(p) for p in protected_policy["generated_artifact_prefixes"]):
        is_protected = True
        matched_rule = "generated_artifact_prefix"
        reason = "Path belongs to generated artifact directory."
    elif any(s in normalized for s in ["/../", ".git/", ".env", "secrets", "token", "credential", "key"]) or normalized.startswith("../"):
        is_protected = True
        matched_rule = "sensitive_pattern"
        reason = "Path contains sensitive keywords or traversal patterns."
        
    return {
        "path_protection_check_version": "3.5.0",
        "path": normalized,
        "is_protected": is_protected,
        "matched_rule": matched_rule,
        "protection_reason": reason if is_protected else "Path allowed.",
        "repo_patch_applied": False,
        "execution_authorized": False
    }

def create_patch_root_validation(
    patch_root: str | None,
    allowed_patch_file: str | None,
    protected_policy: dict | None = None
) -> dict:
    checks = {
        "patch_root_present": patch_root is not None,
        "allowed_patch_file_present": allowed_patch_file is not None,
        "allowed_patch_file_relative": False,
        "no_parent_path_escape": False,
        "not_protected_path": False,
        "target_not_directory_like": False
    }
    
    reasons = []
    if not checks["patch_root_present"]: reasons.append("Patch root DIR is missing.")
    if not checks["allowed_patch_file_present"]: reasons.append("Allowed patch file RELATIVE_PATH is missing.")
    
    protected_check = {}
    
    if checks["allowed_patch_file_present"]:
        f = allowed_patch_file
        checks["allowed_patch_file_relative"] = not Path(f).is_absolute()
        checks["no_parent_path_escape"] = ".." not in f
        checks["target_not_directory_like"] = not f.endswith("/")
        
        protected_check = is_path_protected(f, protected_policy)
        checks["not_protected_path"] = not protected_check["is_protected"]
        
        if not checks["allowed_patch_file_relative"]: reasons.append("Target file must be a relative path.")
        if not checks["no_parent_path_escape"]: reasons.append("Target file cannot contain parent directory escapes.")
        if not checks["target_not_directory_like"]: reasons.append("Target file cannot be a directory.")
        if not checks["not_protected_path"]: reasons.append(f"Target file is protected: {protected_check['protection_reason']}")

    status = "PASS" if all(checks.values()) else "BLOCKED"
    
    return {
        "patch_root_validation_version": "3.5.0",
        "patch_root": patch_root or "",
        "allowed_patch_file": allowed_patch_file or "",
        "validation_status": status,
        "checks": checks,
        "blocking_reasons": reasons,
        "protected_path_check": protected_check,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_patch_preview_diff_contract(
    command: str,
    allowed_patch_file: str | None,
    patch_content: str | None = None,
    original_content: str | None = None
) -> dict:
    original = original_content if original_content is not None else ""
    patch = patch_content if patch_content is not None else f"Station Chief scoped repo patch preview for command: {command}\n"
    
    target = allowed_patch_file or "unknown-file"
    
    orig_lines = original.splitlines(keepends=True)
    patch_lines = patch.splitlines(keepends=True)
    
    diff_lines = list(difflib.unified_diff(orig_lines, patch_lines, fromfile=f"a/{target}", tofile=f"b/{target}"))
    diff_text = "".join(diff_lines)
    
    return {
        "patch_preview_diff_contract_version": "3.5.0",
        "diff_status": "PREVIEW_ONLY",
        "target_file": target,
        "original_content_digest": hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "patch_content_digest": hashlib.sha256(patch.encode("utf-8")).hexdigest(),
        "preview_diff_digest": hashlib.sha256(diff_text.encode("utf-8")).hexdigest(),
        "preview_diff": diff_text,
        "original_line_count": len(orig_lines),
        "patch_line_count": len(patch_lines),
        "diff_line_count": len(diff_lines),
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_patch_digest_manifest(
    command: str,
    patch_root_validation: dict,
    patch_preview_diff_contract: dict,
    protected_path_policy: dict
) -> dict:
    comb_input = {
        "command": command,
        "validation": patch_root_validation,
        "diff": patch_preview_diff_contract,
        "policy": protected_path_policy
    }
    
    return {
        "patch_digest_manifest_version": "3.5.0",
        "manifest_status": "DIGESTED_PREVIEW_ONLY",
        "command_digest": hashlib.sha256(command.encode("utf-8")).hexdigest(),
        "patch_root_validation_digest": sha256_digest(patch_root_validation),
        "patch_preview_diff_digest": sha256_digest(patch_preview_diff_contract),
        "protected_path_policy_digest": sha256_digest(protected_path_policy),
        "combined_patch_hardening_digest": sha256_digest(comb_input),
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_patch_rollback_preview(
    allowed_patch_file: str | None,
    original_content: str | None = None,
    patch_content: str | None = None
) -> dict:
    orig = original_content if original_content is not None else ""
    patch = patch_content if patch_content is not None else ""
    
    return {
        "patch_rollback_preview_version": "3.5.0",
        "rollback_status": "PREVIEW_ONLY",
        "target_file": allowed_patch_file or "",
        "rollback_available": allowed_patch_file is not None,
        "rollback_strategy": "Restore original content digest and target path from preview record; requires separate explicit confirmation before any real patch application.",
        "rollback_steps": [
            "verify target path still matches allowlist",
            "verify target path is not protected",
            "verify original content digest",
            "restore original content only inside patch root",
            "record rollback proof",
            "require separate human confirmation before real rollback"
        ],
        "original_content_digest": hashlib.sha256(orig.encode("utf-8")).hexdigest(),
        "patch_content_digest": hashlib.sha256(patch.encode("utf-8")).hexdigest(),
        "repo_patch_applied": False,
        "rollback_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_changed_file_proof_hardening(
    allowed_files: list[str],
    changed_files: list[str] | None = None,
    protected_policy: dict | None = None
) -> dict:
    if changed_files is None: changed_files = []
    if protected_policy is None: protected_policy = create_protected_path_policy()
    
    file_checks = []
    blocked = []
    unapproved = []
    protected = []
    
    for f in changed_files:
        p_check = is_path_protected(f, protected_policy)
        is_allowed = f in allowed_files
        is_prot = p_check["is_protected"]
        
        status = "PASS" if (is_allowed and not is_prot) else "BLOCKED"
        
        file_checks.append({
            "file": f,
            "is_allowlisted": is_allowed,
            "is_protected": is_prot,
            "status": status,
            "reason": p_check["protection_reason"] if is_prot else ("Allowlisted." if is_allowed else "Not in allowlist.")
        })
        
        if status == "BLOCKED":
            blocked.append(f)
            if is_prot: protected.append(f)
            if not is_allowed: unapproved.append(f)
            
    status = "PASS" if not blocked else "BLOCKED"
    if not changed_files:
        status = "PASS"
        note = "No files were changed."
    else:
        note = f"{len(changed_files)} files checked."
        
    return {
        "changed_file_proof_hardening_version": "3.5.0",
        "proof_status": status,
        "note": note,
        "allowed_files": allowed_files,
        "changed_files": changed_files,
        "file_checks": file_checks,
        "blocked_files": blocked,
        "unapproved_files": unapproved,
        "protected_files": protected,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_human_approval_chain_binding(
    patch_digest_manifest: dict,
    approval_record: dict | None = None,
    approval_ledger: dict | None = None,
    required_token: str = "YES_I_APPROVE_SCOPED_REPO_PATCH"
) -> dict:
    binding_present = (approval_record is not None or approval_ledger is not None)
    
    return {
        "human_approval_chain_binding_version": "3.5.0",
        "binding_status": "BOUND_FOR_REVIEW" if binding_present else "MISSING_APPROVAL_CHAIN",
        "required_token": "YES_I_APPROVE_SCOPED_REPO_PATCH",
        "approval_record_present": approval_record is not None,
        "approval_ledger_present": approval_ledger is not None,
        "patch_digest_manifest_digest": sha256_digest(patch_digest_manifest),
        "approval_record_digest": sha256_digest(approval_record) if approval_record else None,
        "approval_ledger_digest": sha256_digest(approval_ledger) if approval_ledger else None,
        "approval_chain_digest": sha256_digest({"record": approval_record, "ledger": approval_ledger}),
        "note": "Approval chain binding is review metadata only and does not authorize execution.",
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_patch_execution_readiness_score(
    patch_root_validation: dict,
    changed_file_proof_hardening: dict,
    human_approval_chain_binding: dict,
    protected_path_policy: dict
) -> dict:
    score = 0
    breakdown = {}
    reasons = []
    
    if patch_root_validation["validation_status"] == "PASS":
        score += 30
        breakdown["patch_root_validation"] = 30
    else:
        reasons.extend(patch_root_validation["blocking_reasons"])
        
    if changed_file_proof_hardening["proof_status"] == "PASS":
        score += 30
        breakdown["changed_file_proof"] = 30
    else:
        reasons.append("Changed file proof validation failed.")
        
    if protected_path_policy:
        score += 20
        breakdown["protected_path_policy"] = 20
        
    if human_approval_chain_binding["binding_status"] == "BOUND_FOR_REVIEW":
        score += 10
        breakdown["approval_chain_binding"] = 10
    else:
        reasons.append("Human approval chain not bound.")
        
    # Standard 10 points for schema availability
    score += 10
    breakdown["schema_availability"] = 10
    
    status = "READY_FOR_CONFIRMED_SCOPED_PATCH_REVIEW" if score >= 80 and patch_root_validation["validation_status"] == "PASS" and changed_file_proof_hardening["proof_status"] == "PASS" else "BLOCKED"
    
    return {
        "patch_execution_readiness_score_version": "3.5.0",
        "readiness_status": status,
        "readiness_score": score,
        "score_breakdown": breakdown,
        "blocking_reasons": reasons,
        "execution_authorized": False,
        "repo_patch_applied": False,
        "github_api_called": False
    }

def create_patch_hardening_audit_bundle(
    command: str,
    patch_root: str | None = None,
    allowed_patch_file: str | None = None,
    patch_content: str | None = None,
    original_content: str | None = None,
    changed_files: list[str] | None = None,
    approval_record: dict | None = None,
    approval_ledger: dict | None = None
) -> dict:
    schema = create_patch_hardening_schema()
    policy = create_protected_path_policy()
    validation = create_patch_root_validation(patch_root, allowed_patch_file, policy)
    diff_contract = create_patch_preview_diff_contract(command, allowed_patch_file, patch_content, original_content)
    manifest = create_patch_digest_manifest(command, validation, diff_contract, policy)
    rollback = create_patch_rollback_preview(allowed_patch_file, original_content, patch_content)
    proof = create_changed_file_proof_hardening([allowed_patch_file] if allowed_patch_file else [], changed_files, policy)
    binding = create_human_approval_chain_binding(manifest, approval_record, approval_ledger)
    score = create_patch_execution_readiness_score(validation, proof, binding, policy)
    
    return {
        "patch_hardening_audit_bundle_version": "3.5.0",
        "patch_hardening_status": "PATCH_HARDENING_CONTRACT_ONLY",
        "patch_hardening_schema": schema,
        "protected_path_policy": policy,
        "patch_root_validation": validation,
        "patch_preview_diff_contract": diff_contract,
        "patch_digest_manifest": manifest,
        "patch_rollback_preview": rollback,
        "changed_file_proof_hardening": proof,
        "human_approval_chain_binding": binding,
        "patch_execution_readiness_score": score,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_deployment_packaging_readiness_bridge(result: dict, audit_bundle: dict) -> dict:
    ready = (
        audit_bundle["patch_hardening_status"] == "PATCH_HARDENING_CONTRACT_ONLY"
        and audit_bundle["protected_path_policy"] is not None
        and audit_bundle["patch_digest_manifest"] is not None
        and audit_bundle["patch_execution_readiness_score"] is not None
        and not audit_bundle["repo_patch_applied"]
        and not audit_bundle["github_api_called"]
        and not audit_bundle["execution_authorized"]
    )
    
    return {
        "deployment_packaging_readiness_bridge_version": "3.5.0",
        "current_layer": "GitHub Patch Application Hardening",
        "next_layer": "Deployment / Portfolio Packaging Bridge",
        "ready_for_deployment_packaging_bridge": ready,
        "required_next_capabilities": [
            "deployment artifact schema",
            "portfolio packaging manifest",
            "runtime export bundle",
            "release notes generator",
            "deployment readiness proof",
            "no live deployment without approval",
            "no external hosting mutation"
        ],
        "non_goals_for_next_layer": [
            "no external API execution",
            "no full workforce animation",
            "no real worker hiring",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no uncontrolled deployment"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }

def create_github_patch_hardening_bundle(
    result: dict,
    patch_root: str | None = None,
    allowed_patch_file: str | None = None,
    patch_content: str | None = None,
    original_content: str | None = None,
    changed_files: list[str] | None = None,
    approval_record: dict | None = None,
    approval_ledger: dict | None = None
) -> dict:
    command = result.get("command", "empty")
    audit_bundle = create_patch_hardening_audit_bundle(
        command, patch_root, allowed_patch_file, patch_content, original_content, changed_files, approval_record, approval_ledger
    )
    bridge = create_deployment_packaging_readiness_bridge(result, audit_bundle)
    
    return {
        "github_patch_hardening_bundle_version": "3.5.0",
        "patch_hardening_status": "PATCH_HARDENING_CONTRACT_ONLY",
        "patch_hardening_audit_bundle": audit_bundle,
        "patch_hardening_schema": audit_bundle["patch_hardening_schema"],
        "protected_path_policy": audit_bundle["protected_path_policy"],
        "patch_root_validation": audit_bundle["patch_root_validation"],
        "patch_preview_diff_contract": audit_bundle["patch_preview_diff_contract"],
        "patch_digest_manifest": audit_bundle["patch_digest_manifest"],
        "patch_rollback_preview": audit_bundle["patch_rollback_preview"],
        "changed_file_proof_hardening": audit_bundle["changed_file_proof_hardening"],
        "human_approval_chain_binding": audit_bundle["human_approval_chain_binding"],
        "patch_execution_readiness_score": audit_bundle["patch_execution_readiness_score"],
        "deployment_packaging_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False
    }
