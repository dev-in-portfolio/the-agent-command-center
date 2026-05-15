#!/usr/bin/env python3
"""E2E validation for Original Phase 5A client-side operator workflow shell."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errors = []

def run_validator(script_name):
    path = ROOT / "scripts" / script_name
    if not path.exists():
        errors.append(f"Missing validator: {script_name}")
        return None
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        errors.append(f"{script_name} exited with code {result.returncode}")
        if result.stderr:
            errors.append(f"  stderr: {result.stderr.strip()[:200]}")
    return result.stdout.strip()

# Run Phase 5A shell validator
shell_out = run_validator("validate_original_phase_5a_client_side_workflow_shell.py")
if shell_out and "ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_SHELL_VALIDATION_PASS" not in shell_out:
    errors.append("Phase 5A shell validator did not pass")

# Run Phase 4 validators
for validator in [
    "validate_original_phase_4_hosted_dashboard_polish.py",
    "validate_backend_phase_4d_schema_previews.py",
    "validate_backend_phase_4d_disabled_ui.py",
    "validate_backend_phase_4c_snapshot.py",
    "validate_backend_phase_4a_foundation.py",
]:
    out = run_validator(validator)
    if validator == "validate_original_phase_4_hosted_dashboard_polish.py" and out:
        if "ORIGINAL_PHASE_4_HOSTED_DASHBOARD_POLISH_VALIDATION_PASS" not in out:
            errors.append(f"{validator} did not pass")

# Check for forbidden changes
result = subprocess.run(
    ["git", "diff", "--name-only", "origin/master..HEAD"],
    capture_output=True, text=True, cwd=ROOT
)
changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

allowed_prefixes = [
    "13_web_dashboard/",
    "09_exports/interface_phase_5/",
    "09_exports/original_plus1/",
    "09_exports/original_plus2/",
    "14_backend/auth/",
    "14_backend/request_storage/",
    "netlify/functions/auth-status.js",
    "netlify/functions/role-matrix.js",
    "netlify/functions/request-storage-status.js",
    "netlify/functions/backend-manifest.js",
    "netlify/functions/_shared/models/",
    "scripts/validate_",
]

for path in changed:
    if any(path.startswith(p) for p in allowed_prefixes):
        continue
        
    if path.startswith("09_exports/interface_phase_1/"):
        errors.append(f"Phase 1 files changed: {path}")
    elif path.startswith("09_exports/interface_phase_2/"):
        errors.append(f"Phase 2 files changed: {path}")
    elif path.startswith("11_interface/"):
        errors.append(f"Interface files changed: {path}")
    elif path.startswith("12_tui/"):
        errors.append(f"TUI files changed: {path}")
    elif path.startswith("10_runtime/"):
        errors.append(f"Runtime files changed: {path}")
    elif path.startswith("netlify/functions/"):
        errors.append(f"netlify/functions changed: {path}")
    elif path.startswith("14_backend/"):
        errors.append(f"Backend files changed: {path}")
    else:
        errors.append(f"Unexpected file changed: {path}")

# Reports contain PASS_WITH_HIGH_CONFIDENCE
reports_dir = ROOT / "09_exports" / "interface_phase_5"
for report in ["original_phase_5a_safety_report.md", "original_phase_5a_acceptance_report.md"]:
    path = reports_dir / report
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "PASS_WITH_HIGH_CONFIDENCE" not in content:
            errors.append(f"{report} missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print("ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_E2E_VALIDATION_PASS")
