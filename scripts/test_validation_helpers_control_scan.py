#!/usr/bin/env python3
"""File-based helper test for context-aware control scanning."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import (
    is_safety_denial_line,
    scan_text_for_dangerous_controls,
)


SAFE_LINES = [
    "NO_DEPLOY_CONTROLS_ADDED",
    "No deployment actions are enabled.",
    "Deploy controls are not exposed through app runtime.",
    "NO_PUBLIC_WRITES_ADDED",
    "NO_TOKEN_INPUT_ADDED",
    "NO_EMAIL_OR_REVIEWER_CONTACT_ADDED",
    "AUTOMATION STILL DISABLED",
    "This is operator review only.",
    "Deployment is not enabled.",
    "Response import remains blocked.",
    "service_role: NOT REQUIRED",
]

DANGEROUS_LINES = [
    "fetch('/api/deploy')",
    'fetch("/api/reviewer-response")',
    "fetch('/api/response-import')",
    "deployToNetlify()",
    "mergePullRequest()",
    "pushToGithub()",
    "sendEmail()",
    "contactReviewer()",
    "localStorage.setItem('token', token)",
    "sessionStorage.setItem('token', token)",
    "indexedDB.open('tokens')",
    "document.cookie = 'token=abc'",
    "createClient(url, key)",
    "approveRelease()",
    "executeRelease()",
    "runImport()",
    "commitImport()",
    "persistResponse()",
    "submitResponse()",
    "saveResponse()",
    "captureResponse()",
    '"public_endpoint_enabled": true',
    '"live_intake_enabled": true',
    '"public_response_submission_enabled": true',
    '"reviewer_response_write_enabled": true',
    '"response_capture_enabled": true',
    '"response_persistence_enabled": true',
    '"real_import_enabled": true',
    '"automatic_import_enabled": true',
    '"email_sending_enabled": true',
    '"reviewer_contact_enabled": true',
    '"automated_outreach_enabled": true',
    '"contact_automation_enabled": true',
    '"live_write_enabled": true',
    '"public_write_enabled": true',
    '"token_input_enabled": true',
    '"secrets_exposed": true',
    '"service_role_used": true',
    '"browser_persistence_enabled": true',
    '"browser_direct_supabase_calls": true',
    '"automation_enabled": true',
    '"deploy_controls_enabled": true',
    '"launch_automation_enabled": true',
    '"update_enabled": true',
    '"delete_enabled": true',
    '"approve_enabled": true',
    '"execute_enabled": true',
    '"deploy_merge_push_controls_enabled": true',
]


def main() -> None:
    for line in SAFE_LINES:
        if not is_safety_denial_line(line):
            raise SystemExit(f"SAFE_DENIAL_NOT_ALLOWED: {line}")

    danger_text = "\n".join(DANGEROUS_LINES)
    findings = scan_text_for_dangerous_controls("synthetic-danger-test", danger_text)
    if not findings:
        raise SystemExit("DANGEROUS_PATTERNS_NOT_DETECTED")

    safe_text = "\n".join(SAFE_LINES)
    safe_findings = scan_text_for_dangerous_controls("synthetic-safe-test", safe_text)
    if safe_findings:
        raise SystemExit(f"SAFE_DENIAL_FALSE_POSITIVE: {safe_findings}")

    mixed_text = "\n".join([
        "NO_DEPLOY_CONTROLS_ADDED",
        "No public writes are enabled.",
        "This button is disabled.",
        "No email sending or reviewer contact is enabled.",
    ])
    mixed_findings = scan_text_for_dangerous_controls("synthetic-mixed-test", mixed_text)
    if mixed_findings:
        raise SystemExit(f"SAFETY_DENIAL_FALSE_POSITIVE: {mixed_findings}")

    semantic_flags = "\n".join([
        '"public_endpoint_enabled": true',
        '"live_intake_enabled": true',
        '"public_response_submission_enabled": true',
        '"reviewer_response_write_enabled": true',
        '"response_capture_enabled": true',
        '"response_persistence_enabled": true',
        '"real_import_enabled": true',
        '"automatic_import_enabled": true',
        '"email_sending_enabled": true',
        '"reviewer_contact_enabled": true',
        '"automated_outreach_enabled": true',
        '"contact_automation_enabled": true',
        '"live_write_enabled": true',
        '"public_write_enabled": true',
        '"token_input_enabled": true',
        '"secrets_exposed": true',
        '"service_role_used": true',
        '"browser_persistence_enabled": true',
        '"browser_direct_supabase_calls": true',
        '"automation_enabled": true',
        '"deploy_controls_enabled": true',
        '"launch_automation_enabled": true',
        '"update_enabled": true',
        '"delete_enabled": true',
        '"approve_enabled": true',
        '"execute_enabled": true',
        '"deploy_merge_push_controls_enabled": true',
    ])
    semantic_findings = scan_text_for_dangerous_controls("synthetic-flags-test", semantic_flags)
    if len(semantic_findings) < 20:
        raise SystemExit(f"SEMANTIC_FLAGS_NOT_DETECTED: {semantic_findings}")

    print("VALIDATION_HELPERS_CONTROL_SCAN_TEST_PASS")


if __name__ == "__main__":
    main()
