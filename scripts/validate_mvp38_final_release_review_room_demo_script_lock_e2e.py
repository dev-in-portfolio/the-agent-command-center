#!/usr/bin/env python3
"""MVP-38 E2E validator — runs MVP-38 direct + MVP-37 E2E + MVP-36 E2E + master wall + safety self-check."""

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
    direct_path = ROOT / "scripts" / "validate_mvp38_final_release_review_room_demo_script_lock.py"
    if not direct_path.exists():
        return [f"MISSING_DIRECT_VALIDATOR: {direct_path}"]

    text = direct_path.read_text(encoding="utf-8", errors="replace")

    required_markers = [
        "MVP38_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT",
        "MVP38_NO_DEPLOYMENT_CHECK",
        "MVP38_NO_RELEASE_EXECUTION_CHECK",
        "MVP38_NO_AUTOMATIC_RELEASE_APPROVAL_CHECK",
        "MVP38_NO_LIVE_WRITES_CHECK",
        "MVP38_NO_PUBLIC_WRITES_CHECK",
        "MVP38_NO_TOKEN_INPUT_CHECK",
        "MVP38_NO_SECRETS_EXPOSED_CHECK",
        "MVP38_NO_SERVICE_ROLE_CHECK",
        "MVP38_NO_BROWSER_PERSISTENCE_CHECK",
        "MVP38_NO_DIRECT_SUPABASE_CHECK",
        "MVP38_NO_EMAIL_OR_OUTREACH_CHECK",
        "MVP38_NO_CONTACT_AUTOMATION_CHECK",
        "MVP38_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK",
        "MVP38_FINAL_RELEASE_REVIEW_ROOM_EXPORT_ARTIFACTS_CHECK",
        "MVP38_NO_WHOLE_FILE_SAFETY_LABEL_SKIP",
    ]

    issues = []
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Direct validator missing marker: {marker}")

    required_patterns = [
        "deployment_enabled",
        "release_execution_enabled",
        "automatic_release_approval_enabled",
        "live_write_enabled",
        "public_write_enabled",
        "token_input_enabled",
        "secrets_exposed",
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "email_sending_enabled",
        "automated_outreach_enabled",
        "contact_automation_enabled",
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
        "mvp38_final_release_review_room.md",
        "mvp38_demo_script_lock.md",
        "mvp38_reviewer_walkthrough_path.md",
        "mvp38_final_review_audience_paths.md",
        "mvp38_release_go_no_go_checklist.md",
        "mvp38_demo_timing_talking_points.md",
        "mvp38_final_release_review_copy_bank.md",
        "mvp38_final_release_review_room_manifest.json",
    ]

    for pattern in required_patterns:
        if pattern not in text:
            issues.append(f"Direct validator missing check for: {pattern}")

    return issues

all_pass = True

print("MVP-38 E2E Validation")
print()

# Phase 1 — MVP-38 Direct Validator
print("Phase 1 — MVP-38 Direct Validator")
if not run(
    "python3 scripts/validate_mvp38_final_release_review_room_demo_script_lock.py",
    "MVP-38 direct",
):
    print("  [TRIAGE] MVP-38 direct validator failure")
    all_pass = False

print()

# Phase 2 — MVP-37 E2E Validator (chain dependency)
print("Phase 2 — MVP-37 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp37_release_candidate_decision_log_handoff_e2e.py",
    "MVP-37 E2E",
):
    print("  [TRIAGE] MVP-37 E2E failure")
    all_pass = False

print()

# Phase 3 — MVP-36 E2E Validator (chain dependency)
print("Phase 3 — MVP-36 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp36_review_to_roadmap_decision_sync_e2e.py",
    "MVP-36 E2E",
):
    print("  [TRIAGE] MVP-36 E2E failure")
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
print("Phase 5 — Self-check: MVP-38 direct validator safety contract")
direct_issues = self_check_direct_validator()
if direct_issues:
    print("  [FAIL] MVP-38 direct validator safety contract gaps:")
    for issue in direct_issues:
        print(f"    {issue}")
    all_pass = False
else:
    print("  [PASS] MVP-38 direct validator full safety contract coverage verified")

print()

if all_pass:
    print("MVP38_FINAL_RELEASE_REVIEW_ROOM_DEMO_SCRIPT_LOCK_E2E_VALIDATION_PASS")
    sys.exit(0)
else:
    print("MVP38_E2E_VALIDATION_FAIL")
    print()
    print("Triage summary:")
    for label, passed, output in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")
    sys.exit(1)
