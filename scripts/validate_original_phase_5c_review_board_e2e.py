#!/usr/bin/env python3
"""Original Phase 5C Review Board E2E Validator."""
import subprocess
import sys
from pathlib import Path

REPORTS = Path("09_exports/interface_phase_5")
errors = []

def run_validator(script):
    result = subprocess.run(["python3", script], capture_output=True, text=True)
    print(f"  {script}: exit={result.returncode}")
    for line in result.stdout.strip().split("\n"):
        print(f"    {line}")
    if result.stderr.strip():
        for line in result.stderr.strip().split("\n"):
            print(f"    stderr: {line}")
    return result.returncode == 0 and result.stdout.strip().endswith("_VALIDATION_PASS") or result.stdout.strip().endswith("_PASS")

def check(condition, message):
    if not condition:
        errors.append(message)

print("Running Original Phase 5C Review Board E2E Validator...")
print()

# Run Phase 5C validator
print("  Validating Phase 5C review board...")
check(run_validator("scripts/validate_original_phase_5c_review_board.py"), "Phase 5C validator failed")

print("  Validating Phase 5B request packet builder...")
check(run_validator("scripts/validate_original_phase_5b_request_packet_builder.py"), "Phase 5B validator failed")

print("  Validating Phase 5A workflow shell...")
check(run_validator("scripts/validate_original_phase_5a_client_side_workflow_shell.py"), "Phase 5A validator failed")

print("  Validating Phase 4 hosted dashboard polish...")
check(run_validator("scripts/validate_original_phase_4_hosted_dashboard_polish.py"), "Phase 4 polish validator failed")

print("  Validating Phase 4D schema previews...")
check(run_validator("scripts/validate_backend_phase_4d_schema_previews.py"), "Phase 4D schema previews validator failed")

print("  Validating Phase 4D disabled UI...")
check(run_validator("scripts/validate_backend_phase_4d_disabled_ui.py"), "Phase 4D disabled UI validator failed")

print("  Validating Phase 4C snapshot...")
check(run_validator("scripts/validate_backend_phase_4c_snapshot.py"), "Phase 4C snapshot validator failed")

print("  Validating Phase 4A foundation...")
check(run_validator("scripts/validate_backend_phase_4a_foundation.py"), "Phase 4A foundation validator failed")

# Check forbidden diff paths
print()
print("  Checking forbidden diff paths...")
result = subprocess.run(
    ["git", "diff", "--name-only", "origin/master..HEAD"],
    capture_output=True, text=True
)
changed = result.stdout.strip().split("\n") if result.stdout.strip() else []
forbidden_patterns = [
    "09_exports/interface_phase_1/",
    "09_exports/interface_phase_2/",
    "09_exports/interface_phase_3/",
    "09_exports/interface_phase_4/",
    "11_interface/",
    "12_tui/",
    "10_runtime/",
]
allowed_patterns = [
    "13_web_dashboard/",
    "09_exports/interface_phase_5/",
    "09_exports/original_plus1/",
    "09_exports/original_plus2/",
    "14_backend/auth/",
    "14_backend/request_storage/",
    "14_backend/audit_log/",
    "14_backend/approval_gate/",
    "netlify/functions/auth-status.js",
    "netlify/functions/role-matrix.js",
    "netlify/functions/request-storage-status.js",
    "netlify/functions/audit-log-status.js",
    "netlify/functions/approval-gate-status.js",
    "netlify/functions/backend-manifest.js",
    "netlify/functions/_shared/models/",
    "scripts/validate_",
]

for path in changed:
    for fp in forbidden_patterns:
        if path.startswith(fp):
            check(False, f"Forbidden changed path: {path}")
            break

print("  Checking reports...")
report_files = [
    "original_phase_5c_client_side_review_board_report.md",
    "original_phase_5c_design_report.md",
    "original_phase_5c_safety_report.md",
    "original_phase_5c_validator_report.md",
    "original_phase_5c_acceptance_report.md",
]
for rfile in report_files:
    check((REPORTS / rfile).exists(), f"Phase 5C report missing: {rfile}")

acceptance = (REPORTS / "original_phase_5c_acceptance_report.md").read_text(encoding="utf-8")
check("PASS_WITH_HIGH_CONFIDENCE" in acceptance, "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")

print()
if errors:
    print("VALIDATION_FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("ORIGINAL_PHASE_5C_REVIEW_BOARD_E2E_VALIDATION_PASS")
