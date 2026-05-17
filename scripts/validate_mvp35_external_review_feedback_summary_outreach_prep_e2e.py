#!/usr/bin/env python3
"""MVP-35 E2E validator — runs MVP-35 direct + MVP-34 E2E + MVP-33 E2E + master wall + safety self-check."""

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
    direct_path = ROOT / "scripts" / "validate_mvp35_external_review_feedback_summary_outreach_prep.py"
    if not direct_path.exists():
        return [f"MISSING_DIRECT_VALIDATOR: {direct_path}"]

    text = direct_path.read_text(encoding="utf-8", errors="replace")

    required_markers = [
        "MVP35_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT",
        "MVP35_NO_EMAIL_SENDING_CHECK",
        "MVP35_NO_AUTOMATED_OUTREACH_CHECK",
        "MVP35_NO_CONTACT_AUTOMATION_CHECK",
        "MVP35_NO_BROWSER_PERSISTENCE_CHECK",
        "MVP35_NO_DIRECT_SUPABASE_CHECK",
        "MVP35_EXTERNAL_REVIEW_EXPORT_ARTIFACTS_CHECK",
    ]

    issues = []
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Direct validator missing marker: {marker}")

    required_patterns = [
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "Send Email",
        "Start Outreach",
        "Automate Outreach",
        "Automate Review",
        "Contact Reviewer",
        "Connect Supabase",
        "mvp35_external_review_feedback_summary.md",
        "mvp35_reviewer_response_matrix.md",
        "mvp35_feedback_themes_questions_objections.md",
        "mvp35_outreach_prep_draft_workspace.md",
        "mvp35_follow_up_response_packet.md",
        "mvp35_external_reviewer_reply_guide.md",
        "mvp35_operator_follow_up_decision_packet.md",
        "mvp35_outreach_prep_copy_bank.md",
        "mvp35_external_review_feedback_manifest.json",
    ]

    for pattern in required_patterns:
        if pattern not in text:
            issues.append(f"Direct validator missing check for: {pattern}")

    return issues

all_pass = True

print("MVP-35 E2E Validation")
print()

# Phase 1 — MVP-35 Direct Validator
print("Phase 1 — MVP-35 Direct Validator")
if not run(
    "python3 scripts/validate_mvp35_external_review_feedback_summary_outreach_prep.py",
    "MVP-35 direct",
):
    print("  [TRIAGE] MVP-35 direct validator failure")
    all_pass = False

print()

# Phase 2 — MVP-34 E2E Validator (chain dependency)
print("Phase 2 — MVP-34 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp34_public_release_candidate_review_portal_e2e.py",
    "MVP-34 E2E",
):
    print("  [TRIAGE] MVP-34 E2E failure")
    all_pass = False

print()

# Phase 3 — MVP-33 E2E Validator (chain dependency)
print("Phase 3 — MVP-33 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp33_product_launch_readiness_final_pitch_packet_e2e.py",
    "MVP-33 E2E",
):
    print("  [TRIAGE] MVP-33 E2E failure")
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
print("Phase 5 — Self-check: MVP-35 direct validator safety contract")
direct_issues = self_check_direct_validator()
if direct_issues:
    print("  [FAIL] MVP-35 direct validator safety contract gaps:")
    for issue in direct_issues:
        print(f"    {issue}")
    all_pass = False
else:
    print("  [PASS] MVP-35 direct validator full safety contract coverage verified")

print()

if all_pass:
    print("MVP35_EXTERNAL_REVIEW_FEEDBACK_SUMMARY_OUTREACH_PREP_E2E_VALIDATION_PASS")
    sys.exit(0)
else:
    print("MVP35_E2E_VALIDATION_FAIL")
    print()
    print("Triage summary:")
    for label, passed, output in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")
    sys.exit(1)
