#!/usr/bin/env python3
"""MVP-33 E2E validator — runs MVP-33 direct + MVP-32 E2E + MVP-31 E2E + master wall + safety-contract self-check.

Proactive validator triage classification:
- product regression:       downstream product code broke a previously passing check
- stale historical assumption:  validator assumption no longer matches current architecture
- validator overbreadth:        validator flags legitimate patterns as dangerous
- missing narrow allowlist:     validator needs targeted exemption for a safe pattern
- real safety violation:        actual vulnerability or policy breach
"""

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
    """Self-check the MVP-33 direct validator for full safety contract coverage."""
    direct_path = ROOT / "scripts" / "validate_mvp33_product_launch_readiness_final_pitch_packet.py"
    if not direct_path.exists():
        return [f"MISSING_DIRECT_VALIDATOR: {direct_path}"]

    text = direct_path.read_text(encoding="utf-8", errors="replace")

    required_markers = [
        "MVP33_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT",
        "MVP33_NO_FAKE_LAUNCH_STATUS_CHECK",
        "MVP33_NO_DEPLOY_CONTROLS_CHECK",
        "MVP33_NO_LAUNCH_AUTOMATION_CHECK",
        "MVP33_NO_EMAIL_OR_OUTREACH_CHECK",
        "MVP33_NO_BROWSER_PERSISTENCE_CHECK",
        "MVP33_NO_DIRECT_SUPABASE_CHECK",
        "MVP33_FINAL_PITCH_EXPORT_ARTIFACTS_CHECK",
        "MVP33_NO_WHOLE_FILE_SAFETY_LABEL_SKIP",
    ]

    issues = []
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Direct validator missing marker: {marker}")

    # Verify the direct validator actually checks dangerous runtime patterns
    required_patterns = [
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "supabase.co",
        "api.github.com",
        "api.netlify.com",
        "Send Email",
        "Email Reviewer",
        "Start Outreach",
        "Automate Launch",
        "Mark Launch Ready Automatically",
        "Deploy",
        "Merge",
        "Push",
        "Create PR",
        "Launch",
        "Publish",
        "final_pitch_manifest.json",
        "mvp33_final_pitch_packet.md",
        "mvp33_safety_readiness_one_pager.md",
    ]

    for pattern in required_patterns:
        if pattern not in text:
            issues.append(f"Direct validator missing check for: {pattern}")

    return issues

all_pass = True

print("MVP-33 E2E Validation")
print()

# Phase 1 — MVP-33 Direct Validator
print("Phase 1 — MVP-33 Direct Validator")
if not run(
    "python3 scripts/validate_mvp33_product_launch_readiness_final_pitch_packet.py",
    "MVP-33 direct",
):
    # Classification: could be product regression or real safety violation
    print("  [TRIAGE] MVP-33 direct validator failure — likely product regression or real safety violation")
    all_pass = False

print()

# Phase 2 — MVP-32 E2E Validator (chain dependency)
print("Phase 2 — MVP-32 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp32_release_review_metrics_signal_dashboard.py",
    "MVP-32 E2E",
):
    print("  [TRIAGE] MVP-32 E2E failure — may be stale historical assumption or product regression")
    all_pass = False

print()

# Phase 3 — MVP-31 E2E Validator (chain dependency)
print("Phase 3 — MVP-31 E2E Validator (chain dependency)")
if not run(
    "python3 scripts/validate_mvp31_demo_session_capture_review_loop.py",
    "MVP-31 E2E",
):
    print("  [TRIAGE] MVP-31 E2E failure — may be stale historical assumption or product regression")
    all_pass = False

print()

# Phase 4 — Master Validator Wall
print("Phase 4 — Master Validator Wall")
if not run(
    "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    "Master wall",
):
    print("  [TRIAGE] Master wall failure — may be missing narrow allowlist or stale historical assumption")
    all_pass = False

print()

# Phase 5 — Self-check: MVP-33 direct validator safety contract coverage
print("Phase 5 — Self-check: MVP-33 direct validator safety contract")
direct_issues = self_check_direct_validator()
if direct_issues:
    print("  [FAIL] MVP-33 direct validator safety contract gaps:")
    for issue in direct_issues:
        print(f"    {issue}")
    all_pass = False
else:
    print("  [PASS] MVP-33 direct validator full safety contract coverage verified")

print()

if all_pass:
    print("MVP33_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_E2E_VALIDATION_PASS")
    sys.exit(0)
else:
    print("MVP33_E2E_VALIDATION_FAIL")
    print()
    print("Triage summary:")
    for label, passed, output in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")
    sys.exit(1)
