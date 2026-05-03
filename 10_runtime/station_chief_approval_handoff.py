#!/usr/bin/env python3
from __future__ import annotations

import difflib

APPROVAL_HANDOFF_MODULE_VERSION = "2.6.0"


def safe_get(dictionary: dict, dotted_path: str, default=None):
    current = dictionary
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def extract_bundle_summary(bundle: dict, label: str) -> dict:
    return {
        "label": label,
        "dry_run_bundle_version": bundle.get("dry_run_bundle_version"),
        "command": bundle.get("command"),
        "command_type": bundle.get("command_type"),
        "activation_tier": safe_get(bundle, "activation_tier.name"),
        "selected_profile_id": safe_get(bundle, "execution_profile.selected_profile_id"),
        "readiness_status": safe_get(bundle, "execution_readiness_score.readiness_status"),
        "readiness_score": safe_get(bundle, "execution_readiness_score.score"),
        "repo_patch_present": bundle.get("repo_patch_plan") is not None,
        "repo_patch_target": safe_get(bundle, "repo_patch_plan.normalized_relative_path"),
        "repo_patch_safety_status": safe_get(bundle, "repo_patch_plan.path_safety.safety_status"),
        "approval_checklist_status": safe_get(bundle, "approval_checklist.checklist_status"),
        "baseline_preserved": bundle.get("baseline_preserved", False),
        "external_actions_taken": bundle.get("external_actions_taken", False),
        "live_worker_agents_activated": bundle.get("live_worker_agents_activated", False),
    }


def compare_text_blocks(before_text: str | None, after_text: str | None) -> dict:
    before_lines = (before_text or "").splitlines()
    after_lines = (after_text or "").splitlines()
    diff_lines = list(difflib.unified_diff(before_lines, after_lines, fromfile="before", tofile="after", lineterm=""))
    return {
        "comparison_status": "UNCHANGED" if not diff_lines else "CHANGED",
        "before_line_count": len(before_lines),
        "after_line_count": len(after_lines),
        "diff_text": "\n".join(diff_lines),
    }


def compare_dry_run_bundles(before_bundle: dict, after_bundle: dict) -> dict:
    before_summary = extract_bundle_summary(before_bundle, "before")
    after_summary = extract_bundle_summary(after_bundle, "after")
    before_preview = safe_get(before_bundle, "repo_patch_preview")
    after_preview = safe_get(after_bundle, "repo_patch_preview")
    patch_preview_comparison = compare_text_blocks(before_preview, after_preview)
    readiness_before = safe_get(before_bundle, "execution_readiness_score.readiness_status")
    readiness_after = safe_get(after_bundle, "execution_readiness_score.readiness_status")
    score_before = safe_get(before_bundle, "execution_readiness_score.score")
    score_after = safe_get(after_bundle, "execution_readiness_score.score")
    tracked_before = {key: value for key, value in before_summary.items() if key != "label"}
    tracked_after = {key: value for key, value in after_summary.items() if key != "label"}
    comparison_status = "CHANGED"
    if (
        tracked_before == tracked_after
        and patch_preview_comparison["comparison_status"] == "UNCHANGED"
        and score_before == score_after
        and readiness_before == readiness_after
    ):
        comparison_status = "UNCHANGED"
    return {
        "comparison_version": "2.6.0",
        "comparison_status": comparison_status,
        "before_summary": before_summary,
        "after_summary": after_summary,
        "profile_changed": before_summary["selected_profile_id"] != after_summary["selected_profile_id"],
        "readiness_status_changed": readiness_before != readiness_after,
        "readiness_score_delta": None if score_before is None or score_after is None else score_after - score_before,
        "repo_patch_target_changed": before_summary["repo_patch_target"] != after_summary["repo_patch_target"],
        "repo_patch_safety_changed": before_summary["repo_patch_safety_status"] != after_summary["repo_patch_safety_status"],
        "approval_checklist_changed": before_summary["approval_checklist_status"] != after_summary["approval_checklist_status"],
        "patch_preview_comparison": patch_preview_comparison,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }


def create_risk_summary(dry_run_bundle: dict, comparison: dict | None = None) -> dict:
    selected_profile_id = safe_get(dry_run_bundle, "execution_profile.selected_profile_id")
    readiness_status = safe_get(dry_run_bundle, "execution_readiness_score.readiness_status")
    checklist_status = safe_get(dry_run_bundle, "patch_approval_checklist.checklist_status")
    safety_status = safe_get(dry_run_bundle, "repo_patch_plan.path_safety.safety_status")
    risk_factors = []
    blocking_reasons = []
    if comparison and comparison.get("comparison_status") == "CHANGED":
        risk_factors.append("Dry-run bundle changed from comparison baseline.")
    if safe_get(dry_run_bundle, "repo_patch_plan") is not None:
        risk_factors.append("Repo patch approval required before execution.")
    if selected_profile_id == "scoped_repo_patch":
        risk_level = "high"
    elif selected_profile_id == "sandbox_write":
        risk_level = "medium"
    elif selected_profile_id in {"dry_run_patch", "audit_only"}:
        risk_level = "low"
    else:
        risk_level = "low"
    if readiness_status == "BLOCKED":
        risk_level = "blocked"
        blocking_reasons.append("Execution readiness is blocked.")
    if checklist_status == "BLOCKED":
        blocking_reasons.append("Approval checklist is blocked.")
    if safe_get(dry_run_bundle, "repo_patch_plan") is not None and safety_status != "SAFE_REPO_PATCH_PATH":
        blocking_reasons.append("Repo patch path safety is not approved.")
    return {
        "risk_summary_version": "2.6.0",
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "blocking_reasons": blocking_reasons,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }


def create_human_approval_summary(dry_run_bundle: dict, risk_summary: dict) -> dict:
    approval_required = safe_get(dry_run_bundle, "repo_patch_plan") is not None or safe_get(dry_run_bundle, "execution_profile.selected_profile.requires_confirmation") is True
    checklist_status = safe_get(dry_run_bundle, "patch_approval_checklist.checklist_status")
    readiness_status = safe_get(dry_run_bundle, "execution_readiness_score.readiness_status")
    approval_token = "YES_I_APPROVE_SCOPED_REPO_PATCH" if approval_required else None
    if approval_required:
        plain_language_summary = "This bundle includes a scoped repo patch or confirmation-gated profile and needs human review before execution."
    else:
        plain_language_summary = "This bundle is audit-only and can be archived without execution approval."
    approval_questions = []
    if approval_required:
        approval_questions = [
            "Is the patch target file expected?",
            "Is the changed-file scope allowlisted?",
            "Is the repo patch preview acceptable?",
            "Is the baseline protected?",
            "Should this proceed to confirmed scoped repo patch execution?",
        ]
    return {
        "approval_summary_version": "2.6.0",
        "approval_required": approval_required,
        "approval_token": approval_token,
        "readiness_status": readiness_status,
        "checklist_status": checklist_status,
        "risk_level": risk_summary.get("risk_level"),
        "plain_language_summary": plain_language_summary,
        "approval_questions": approval_questions,
    }


def create_next_action_recommendation(dry_run_bundle: dict, risk_summary: dict, comparison: dict | None = None) -> dict:
    readiness_status = safe_get(dry_run_bundle, "execution_readiness_score.readiness_status")
    risk_level = risk_summary.get("risk_level")
    approval_required = safe_get(dry_run_bundle, "repo_patch_plan") is not None or safe_get(dry_run_bundle, "execution_profile.selected_profile.requires_confirmation") is True
    allowed_next_actions = []
    blocked_next_actions = [
        "modify locked 175-family baseline",
        "modify Devinization overlays without explicit scope",
        "execute live external API actions",
        "animate full worker-agent workforce",
    ]
    if comparison and comparison.get("comparison_status") == "CHANGED":
        allowed_next_actions.append("review dry-run comparison")
    if readiness_status == "BLOCKED" or risk_level == "blocked":
        recommended_next_action = "Revise dry-run inputs before approval."
        blocked_next_actions.append("execute scoped repo patch")
    elif approval_required and readiness_status == "READY_FOR_APPROVAL":
        recommended_next_action = "Review approval handoff, then provide confirmation token only if acceptable."
        allowed_next_actions.extend(["review patch preview", "approve scoped repo patch with confirmation token"])
    elif readiness_status == "READY_AUDIT_ONLY":
        recommended_next_action = "Archive audit-only dry-run bundle."
        allowed_next_actions.append("archive dry-run bundle")
    else:
        recommended_next_action = "Review dry-run bundle before deciding next action."
    return {
        "recommendation_version": "2.6.0",
        "recommended_next_action": recommended_next_action,
        "allowed_next_actions": allowed_next_actions,
        "blocked_next_actions": blocked_next_actions,
        "reason": "Recommendation derived from readiness, approval requirements, and comparison state.",
    }


def create_approval_handoff_packet(dry_run_bundle: dict, comparison: dict | None = None) -> dict:
    risk_summary = create_risk_summary(dry_run_bundle, comparison)
    human_approval_summary = create_human_approval_summary(dry_run_bundle, risk_summary)
    next_action_recommendation = create_next_action_recommendation(dry_run_bundle, risk_summary, comparison)
    return {
        "approval_handoff_version": "2.6.0",
        "dry_run_bundle": dry_run_bundle,
        "comparison": comparison,
        "risk_summary": risk_summary,
        "human_approval_summary": human_approval_summary,
        "next_action_recommendation": next_action_recommendation,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }
