#!/usr/bin/env python3
from __future__ import annotations

EXECUTION_PROFILE_MODULE_VERSION = "3.1.0"

EXECUTION_PROFILES = {
    "audit_only": {
        "name": "Audit Only",
        "allows_repo_patch": False,
        "allows_sandbox_write": False,
        "requires_confirmation": False,
        "risk_level": "low",
        "description": "Verification, inspection, and proof-only runtime behavior.",
    },
    "dry_run_patch": {
        "name": "Dry-Run Patch",
        "allows_repo_patch": False,
        "allows_sandbox_write": False,
        "requires_confirmation": False,
        "risk_level": "low",
        "description": "Prepare patch previews, scope proof, and approval checklist without writing patch files.",
    },
    "sandbox_write": {
        "name": "Sandbox Write",
        "allows_repo_patch": False,
        "allows_sandbox_write": True,
        "requires_confirmation": True,
        "risk_level": "medium",
        "description": "Allows confirmed writes only inside a provided sandbox execution directory.",
    },
    "scoped_repo_patch": {
        "name": "Scoped Repo Patch",
        "allows_repo_patch": True,
        "allows_sandbox_write": False,
        "requires_confirmation": True,
        "risk_level": "high",
        "description": "Allows confirmed patch-root-only writes to explicitly allowlisted relative files.",
    },
}


def list_execution_profiles() -> dict:
    return {
        "execution_profile_module_version": EXECUTION_PROFILE_MODULE_VERSION,
        "execution_profiles": EXECUTION_PROFILES,
    }


def select_execution_profile(command_type: str, selected_overlays: list[str], requested_profile: str | None = None) -> dict:
    if requested_profile is not None:
        if requested_profile in EXECUTION_PROFILES:
            profile_id = requested_profile
            selection_reason = "Requested profile accepted."
        else:
            profile_id = "audit_only"
            selection_reason = "Requested profile unavailable; defaulted to audit_only."
    else:
        profile_map = {
            "verification": "audit_only",
            "remember_only": "audit_only",
            "strict_execution": "dry_run_patch",
            "speed_racer": "dry_run_patch",
            "build": "dry_run_patch",
            "route": "audit_only",
            "repair": "dry_run_patch",
            "governance": "audit_only",
            "final_output": "audit_only",
            "unknown": "audit_only",
        }
        profile_id = profile_map.get(command_type, "audit_only")
        selection_reason = "Selected from command type defaults."
    return {
        "selected_profile_id": profile_id,
        "selected_profile": EXECUTION_PROFILES[profile_id],
        "requested_profile": requested_profile,
        "selection_reason": selection_reason,
        "command_type": command_type,
        "selected_overlays": selected_overlays,
    }


def create_preflight_gate_record(command_brief: dict, execution_profile: dict, repo_patch_plan: dict | None = None) -> dict:
    repo_patch_requested = repo_patch_plan is not None
    repo_patch_safety_status = repo_patch_plan.get("path_safety", {}).get("safety_status") if repo_patch_plan else None
    preflight_pass = repo_patch_plan is None or repo_patch_safety_status == "SAFE_REPO_PATCH_PATH"
    approval_required = execution_profile["selected_profile"]["requires_confirmation"] or repo_patch_requested
    return {
        "preflight_status": "PASS" if preflight_pass else "BLOCKED",
        "command_type": command_brief["command_type"],
        "selected_profile_id": execution_profile["selected_profile_id"],
        "risk_level": execution_profile["selected_profile"]["risk_level"],
        "baseline_preserved": True,
        "external_actions_allowed": False,
        "worker_animation_allowed": False,
        "repo_patch_requested": repo_patch_requested,
        "repo_patch_safety_status": repo_patch_safety_status,
        "requires_confirmation": execution_profile["selected_profile"]["requires_confirmation"],
        "approval_required_before_execution": approval_required,
        "reason": "Preflight gate passed." if preflight_pass else "Preflight gate blocked by repo patch safety.",
    }


def create_patch_approval_checklist(repo_patch_plan: dict | None, execution_profile: dict) -> dict:
    if repo_patch_plan is None:
        return {
            "checklist_status": "NOT_APPLICABLE",
            "selected_profile_id": execution_profile["selected_profile_id"],
            "approval_token_required": None,
            "items": [],
        }

    path_safety = repo_patch_plan.get("path_safety", {})
    normalized_relative_path = repo_patch_plan.get("normalized_relative_path", "")
    items = [
        {"item": "Patch root provided", "passed": bool(repo_patch_plan.get("patch_root"))},
        {"item": "Relative patch path normalized", "passed": bool(normalized_relative_path)},
        {"item": "Target file explicitly allowlisted", "passed": path_safety.get("is_allowlisted") is True},
        {"item": "Forbidden path check passed", "passed": path_safety.get("is_forbidden_repo_path") is False},
        {"item": "Target resolves inside patch root", "passed": path_safety.get("is_inside_patch_root") is True},
        {"item": "Human confirmation required before write", "passed": True},
        {"item": "Changed-file scope proof required", "passed": True},
    ]
    safety_pass = all(item["passed"] for item in items[:5])
    return {
        "checklist_status": "READY" if safety_pass else "BLOCKED",
        "selected_profile_id": execution_profile["selected_profile_id"],
        "approval_token_required": "YES_I_APPROVE_SCOPED_REPO_PATCH",
        "items": items,
    }


def create_execution_readiness_score(preflight_gate_record: dict, approval_checklist: dict, changed_file_scope_proof: dict | None = None) -> dict:
    score = 0
    components = {
        "baseline_preserved": False,
        "external_actions_allowed": False,
        "worker_animation_allowed": False,
        "preflight_pass": False,
        "approval_ready_or_not_applicable": False,
    }

    if preflight_gate_record.get("baseline_preserved") is True:
        score += 25
        components["baseline_preserved"] = True
    if preflight_gate_record.get("external_actions_allowed") is False:
        score += 20
        components["external_actions_allowed"] = True
    if preflight_gate_record.get("worker_animation_allowed") is False:
        score += 20
        components["worker_animation_allowed"] = True
    if preflight_gate_record.get("preflight_status") == "PASS":
        score += 20
        components["preflight_pass"] = True
    if approval_checklist.get("checklist_status") in {"READY", "NOT_APPLICABLE"}:
        score += 15
        components["approval_ready_or_not_applicable"] = True

    if preflight_gate_record.get("preflight_status") == "BLOCKED":
        readiness_status = "BLOCKED"
        reason = preflight_gate_record.get("reason", "Preflight gate blocked.")
    elif approval_checklist.get("checklist_status") == "BLOCKED":
        readiness_status = "BLOCKED"
        reason = "Approval checklist blocked."
    elif approval_checklist.get("checklist_status") == "READY":
        readiness_status = "READY_FOR_APPROVAL"
        reason = "Ready for human approval."
    else:
        readiness_status = "READY_AUDIT_ONLY"
        reason = "Ready for audit-only behavior."

    if changed_file_scope_proof and changed_file_scope_proof.get("scope_proof_status") == "PASS":
        components["changed_file_scope_proof_pass"] = True
    elif changed_file_scope_proof is not None:
        components["changed_file_scope_proof_pass"] = False

    return {
        "readiness_status": readiness_status,
        "score": score,
        "max_score": 100,
        "components": components,
        "reason": reason,
    }


def create_dry_run_bundle(
    result: dict,
    execution_profile: dict,
    preflight_gate_record: dict,
    approval_checklist: dict,
    execution_readiness_score: dict,
) -> dict:
    repo_patch_plan = result.get("repo_patch_plan")
    if repo_patch_plan is None:
        repo_patch_preview = None
    else:
        repo_patch_preview = repo_patch_plan.get("patch_preview")
    return {
        "dry_run_bundle_version": "3.1.0",
        "command": result["command"],
        "command_type": result["command_type"],
        "activation_tier": result["activation_tier"],
        "selected_overlays": result["selected_overlays"],
        "execution_profile": execution_profile,
        "preflight_gate_record": preflight_gate_record,
        "approval_checklist": approval_checklist,
        "execution_readiness_score": execution_readiness_score,
        "repo_patch_plan": repo_patch_plan,
        "repo_patch_preview": repo_patch_preview,
        "changed_file_scope_proof": result.get("changed_file_scope_proof"),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }
