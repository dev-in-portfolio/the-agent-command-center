#!/usr/bin/env python3
"""MVP-36 E2E validator — runs MVP-36 direct + MVP-35 E2E + MVP-34 E2E + master wall + safety self-check."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 120

results = []

def run(cmd, label):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=TIMEOUT,
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            print(f"  [FAIL] {label}")
            for line in result.stderr.splitlines()[-8:]:
                print(f"    {line}")
            results.append((label, False, result.stdout.strip()))
            return False
        print(f"  [PASS] {label}")
        results.append((label, True, result.stdout.strip()))
        return True
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] {label} (timeout {TIMEOUT}s)")
        results.append((label, False, "TIMEOUT"))
        return False

def self_check_direct_validator():
    direct_path = ROOT / "scripts" / "validate_mvp36_review_to_roadmap_decision_sync.py"
    if not direct_path.exists():
        return [f"MISSING_DIRECT_VALIDATOR: {direct_path}"]

    text = direct_path.read_text(encoding="utf-8", errors="replace")

    required_markers = [
        "MVP36_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT",
        "MVP36_NO_AUTOMATIC_ROADMAP_UPDATES_CHECK",
        "MVP36_NO_AUTOMATIC_REQUEST_CREATION_CHECK",
        "MVP36_NO_LIVE_WRITES_CHECK",
        "MVP36_NO_PUBLIC_WRITES_CHECK",
        "MVP36_NO_TOKEN_INPUT_CHECK",
        "MVP36_NO_SECRETS_EXPOSED_CHECK",
        "MVP36_NO_SERVICE_ROLE_CHECK",
        "MVP36_NO_BROWSER_PERSISTENCE_CHECK",
        "MVP36_NO_DIRECT_SUPABASE_CHECK",
        "MVP36_NO_EMAIL_OR_OUTREACH_CHECK",
        "MVP36_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK",
        "MVP36_REVIEW_TO_ROADMAP_EXPORT_ARTIFACTS_CHECK",
        "MVP36_NO_WHOLE_FILE_SAFETY_LABEL_SKIP",
    ]

    issues = []
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Direct validator missing marker: {marker}")

    required_patterns = [
        "automatic_roadmap_updates_enabled",
        "automatic_request_creation_enabled",
        "live_write_enabled",
        "public_write_enabled",
        "token_input_enabled",
        "secrets_exposed",
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "email_sending_enabled",
        "automated_outreach_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "deploy_merge_push_controls_enabled",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "Update Roadmap",
        "Create Request",
        "Create Live Request",
        "Apply Recommendation",
        "Send Email",
        "Start Outreach",
        "Automate Outreach",
        "Contact Reviewer",
        "Connect Supabase",
        "mvp36_review_to_roadmap_decision_sync.md",
        "mvp36_external_signal_priority_map.md",
        "mvp36_roadmap_update_recommendations.md",
        "mvp36_review_signal_request_drafts.md",
        "mvp36_decision_sync_audit_packet.md",
        "mvp36_operator_roadmap_sync_review_packet.md",
        "mvp36_review_to_roadmap_copy_bank.md",
        "mvp36_review_to_roadmap_decision_manifest.json",
    ]

    for pattern in required_patterns:
        if pattern not in text:
            issues.append(f"Direct validator missing check for: {pattern}")

    return issues

all_pass = True

print("MVP-36 E2E Validation")
print()

# Phase 1 — MVP-36 Direct Validator
print("Phase 1 — MVP-36 Direct Validator")
if not run(
    "python3 scripts/validate_mvp36_review_to_roadmap_decision_sync.py",
    "MVP-36 direct",
):
    print("  [TRIAGE] MVP-36 direct validator failure")
    all_pass = False

print()

# Phase 2 — MVP-35 E2E Validator (chain dependency)
print("Phase 2 — MVP-35 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp35_external_review_feedback_summary_outreach_prep.py",
    "MVP-35 E2E",
):
    print("  [TRIAGE] MVP-35 E2E failure")
    all_pass = False

print()

# Phase 3 — MVP-34 E2E Validator (chain dependency)
print("Phase 3 — MVP-34 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp34_public_release_candidate_review_portal.py",
    "MVP-34 E2E",
):
    print("  [TRIAGE] MVP-34 E2E failure")
    all_pass = False

print()

# Phase 4 — Master Validator Wall
print("Phase 4 — Master Validator Wall")
if not run(
    "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    "Master wall",
):
    print("  [TRIAGE] Master wall failure")
    all_pass = False

print()

# Phase 5 — Self-check
print("Phase 5 — Self-check: MVP-36 direct validator safety contract")
direct_issues = self_check_direct_validator()
if direct_issues:
    print("  [FAIL] MVP-36 direct validator safety contract gaps:")
    for issue in direct_issues:
        print(f"    {issue}")
    all_pass = False
else:
    print("  [PASS] MVP-36 direct validator full safety contract coverage verified")

print()

if all_pass:
    print("MVP36_REVIEW_TO_ROADMAP_DECISION_SYNC_E2E_VALIDATION_PASS")
    sys.exit(0)
else:
    print("MVP36_E2E_VALIDATION_FAIL")
    print()
    print("Triage summary:")
    for label, passed, output in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")
    sys.exit(1)
