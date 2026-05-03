#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json

APPROVAL_RECORD_MODULE_VERSION = "2.6.0"
APPROVAL_RECORD_CONFIRMATION_TOKEN = "YES_I_APPROVE_APPROVAL_HANDOFF_RECORD"

APPROVAL_DECISIONS = {
    "approve": {
        "label": "Approve",
        "requires_confirmation_token": True,
        "allows_future_scoped_patch_execution_review": True,
        "description": "Records human approval of the approval handoff packet, but does not execute any repo patch by itself.",
    },
    "reject": {
        "label": "Reject",
        "requires_confirmation_token": False,
        "allows_future_scoped_patch_execution_review": False,
        "description": "Records human rejection of the approval handoff packet.",
    },
    "needs_changes": {
        "label": "Needs Changes",
        "requires_confirmation_token": False,
        "allows_future_scoped_patch_execution_review": False,
        "description": "Records that the approval handoff packet needs revision before approval.",
    },
}


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = canonical_json(data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def create_approval_review_ui_schema() -> dict:
    fields = [
        {
            "field_id": "reviewer_name",
            "label": "Reviewer Name",
            "field_type": "text",
            "required": True,
            "description": "Human reviewer name or handle.",
        },
        {
            "field_id": "approval_decision",
            "label": "Approval Decision",
            "field_type": "select",
            "required": True,
            "allowed_values": ["approve", "reject", "needs_changes"],
            "description": "Decision for this approval handoff packet.",
        },
        {
            "field_id": "approval_note",
            "label": "Approval Note",
            "field_type": "textarea",
            "required": False,
            "description": "Optional reviewer note explaining the decision.",
        },
        {
            "field_id": "confirmation_token",
            "label": "Confirmation Token",
            "field_type": "text",
            "required_when": "approval_decision == approve",
            "expected_value": APPROVAL_RECORD_CONFIRMATION_TOKEN,
            "description": "Required only to create an approved signed approval record.",
        },
        {
            "field_id": "patch_preview_reviewed",
            "label": "Patch Preview Reviewed",
            "field_type": "checkbox",
            "required_when": "approval_decision == approve",
            "description": "Reviewer confirms the patch preview was reviewed.",
        },
        {
            "field_id": "changed_file_scope_reviewed",
            "label": "Changed-File Scope Reviewed",
            "field_type": "checkbox",
            "required_when": "approval_decision == approve",
            "description": "Reviewer confirms the changed-file scope was reviewed.",
        },
        {
            "field_id": "baseline_protection_reviewed",
            "label": "Baseline Protection Reviewed",
            "field_type": "checkbox",
            "required_when": "approval_decision == approve",
            "description": "Reviewer confirms baseline protection was reviewed.",
        },
        {
            "field_id": "risk_summary_reviewed",
            "label": "Risk Summary Reviewed",
            "field_type": "checkbox",
            "required_when": "approval_decision == approve",
            "description": "Reviewer confirms the risk summary was reviewed.",
        },
    ]
    return {
        "approval_review_ui_schema_version": "2.6.0",
        "title": "Station Chief Approval Handoff Review",
        "purpose": "Review an approval handoff packet before any human-confirmed scoped repo patch execution.",
        "fields": fields,
        "approval_decisions": APPROVAL_DECISIONS,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }


def validate_approval_inputs(
    approval_handoff_packet: dict,
    reviewer_name: str,
    approval_decision: str,
    approval_note: str | None = None,
    confirmation_token: str | None = None,
    patch_preview_reviewed: bool = False,
    changed_file_scope_reviewed: bool = False,
    baseline_protection_reviewed: bool = False,
    risk_summary_reviewed: bool = False,
) -> dict:
    errors: list[str] = []
    reviewer_name_present = bool(reviewer_name and reviewer_name.strip())
    if not reviewer_name_present:
        errors.append("reviewer_name must be non-empty.")
    if approval_decision not in APPROVAL_DECISIONS:
        errors.append("approval_decision must be one of approve, reject, needs_changes.")
    if not isinstance(approval_handoff_packet, dict) or "approval_handoff_version" not in approval_handoff_packet:
        errors.append("approval_handoff_packet must contain approval_handoff_version.")

    confirmation_token_required = approval_decision == "approve"
    confirmation_token_valid = True
    review_checkboxes_complete = True
    if confirmation_token_required:
        confirmation_token_valid = confirmation_token == APPROVAL_RECORD_CONFIRMATION_TOKEN
        if not confirmation_token_valid:
            errors.append("confirmation token is required for approve decisions.")
        review_checkboxes_complete = all(
            [patch_preview_reviewed, changed_file_scope_reviewed, baseline_protection_reviewed, risk_summary_reviewed]
        )
        if not review_checkboxes_complete:
            errors.append("all review attestations are required for approve decisions.")
        approval_required = bool((approval_handoff_packet.get("human_approval_summary") or {}).get("approval_required"))
        allowlist_ok = "approve scoped repo patch with confirmation token" in (
            (approval_handoff_packet.get("next_action_recommendation") or {}).get("allowed_next_actions") or []
        )
        if not approval_required and not allowlist_ok:
            errors.append("approval handoff packet is not ready for approve decision.")
    else:
        confirmation_token_valid = confirmation_token in {None, "", APPROVAL_RECORD_CONFIRMATION_TOKEN}

    status = "PASS" if not errors else "BLOCKED"
    return {
        "input_validation_status": status,
        "errors": errors,
        "reviewer_name_present": reviewer_name_present,
        "approval_decision": approval_decision,
        "confirmation_token_required": confirmation_token_required,
        "confirmation_token_valid": confirmation_token_valid,
        "review_checkboxes_complete": review_checkboxes_complete,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
    }


def create_signed_approval_record(
    approval_handoff_packet: dict,
    reviewer_name: str,
    approval_decision: str,
    approval_note: str | None = None,
    confirmation_token: str | None = None,
    patch_preview_reviewed: bool = False,
    changed_file_scope_reviewed: bool = False,
    baseline_protection_reviewed: bool = False,
    risk_summary_reviewed: bool = False,
) -> dict:
    validation_result = validate_approval_inputs(
        approval_handoff_packet,
        reviewer_name,
        approval_decision,
        approval_note=approval_note,
        confirmation_token=confirmation_token,
        patch_preview_reviewed=patch_preview_reviewed,
        changed_file_scope_reviewed=changed_file_scope_reviewed,
        baseline_protection_reviewed=baseline_protection_reviewed,
        risk_summary_reviewed=risk_summary_reviewed,
    )
    approval_packet_digest = sha256_digest(approval_handoff_packet)
    reviewer_name_clean = (reviewer_name or "").strip()
    approval_note_clean = approval_note or ""
    record_status = "SIGNED" if validation_result["input_validation_status"] == "PASS" else "BLOCKED"
    record = {
        "approval_record_version": "2.6.0",
        "approval_packet_digest": approval_packet_digest,
        "reviewer_name": reviewer_name_clean,
        "approval_decision": approval_decision,
        "approval_note": approval_note_clean,
        "input_validation": validation_result,
        "review_attestations": {
            "patch_preview_reviewed": patch_preview_reviewed,
            "changed_file_scope_reviewed": changed_file_scope_reviewed,
            "baseline_protection_reviewed": baseline_protection_reviewed,
            "risk_summary_reviewed": risk_summary_reviewed,
        },
        "approval_handoff_version": approval_handoff_packet.get("approval_handoff_version"),
        "approval_required": bool((approval_handoff_packet.get("human_approval_summary") or {}).get("approval_required", False)),
        "recommended_next_action": (approval_handoff_packet.get("next_action_recommendation") or {}).get("recommended_next_action"),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "record_status": record_status,
    }
    signature_payload = {
        "approval_record_version": "2.6.0",
        "approval_packet_digest": approval_packet_digest,
        "reviewer_name": reviewer_name_clean,
        "approval_decision": approval_decision,
        "approval_note": approval_note_clean,
        "record_status": record_status,
    }
    record["approval_signature"] = sha256_digest(signature_payload)
    return record


def verify_signed_approval_record(approval_handoff_packet: dict, approval_record: dict) -> dict:
    expected_packet_digest = sha256_digest(approval_handoff_packet)
    approval_packet_digest_matches = approval_record.get("approval_packet_digest") == expected_packet_digest
    signature_payload = {
        "approval_record_version": approval_record.get("approval_record_version"),
        "approval_packet_digest": approval_record.get("approval_packet_digest"),
        "reviewer_name": approval_record.get("reviewer_name"),
        "approval_decision": approval_record.get("approval_decision"),
        "approval_note": approval_record.get("approval_note", ""),
        "record_status": approval_record.get("record_status"),
    }
    expected_signature = sha256_digest(signature_payload)
    approval_signature_matches = approval_record.get("approval_signature") == expected_signature
    if approval_packet_digest_matches and approval_signature_matches and approval_record.get("record_status") == "SIGNED":
        status = "PASS"
        reason = "Approval record matches handoff packet and signature."
    else:
        status = "FAIL"
        reason = "Approval record digest or signature mismatch, or record status is not SIGNED."
    return {
        "verification_status": status,
        "approval_packet_digest_matches": approval_packet_digest_matches,
        "approval_signature_matches": approval_signature_matches,
        "record_status": approval_record.get("record_status"),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "reason": reason,
    }


def create_approval_record_audit_manifest(
    approval_handoff_packet: dict,
    approval_record: dict,
    verification_result: dict,
) -> dict:
    return {
        "approval_record_audit_manifest_version": "2.6.0",
        "approval_handoff_version": approval_handoff_packet.get("approval_handoff_version"),
        "approval_record_version": approval_record.get("approval_record_version"),
        "approval_packet_digest": approval_record.get("approval_packet_digest"),
        "approval_signature": approval_record.get("approval_signature"),
        "approval_decision": approval_record.get("approval_decision"),
        "record_status": approval_record.get("record_status"),
        "verification_status": verification_result.get("verification_status"),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False,
        "note": "This approval record documents human review. It does not execute repo patches by itself.",
    }
