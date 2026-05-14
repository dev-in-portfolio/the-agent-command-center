#!/usr/bin/env python3
"""Original Phase 5B — Request Packet Builder E2E Validator"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_validator(script_name):
    path = PROJECT_ROOT / "scripts" / script_name
    if not path.exists():
        print(f"  SKIP (not found): {script_name}")
        return None
    result = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    print(f"  {script_name}: exit={result.returncode}")
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            print(f"    {line}")
    if result.stderr.strip():
        for line in result.stderr.strip().split("\n"):
            if line.strip():
                print(f"    STDERR: {line}")
    return result.returncode == 0

def check_diff():
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

    forbidden_prefixes = [
        "netlify/functions/",
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "11_interface/",
        "12_tui/",
        "10_runtime/",
        "14_backend/",
    ]

    for path in changed:
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                print(f"  FAIL: Forbidden path changed: {path}")
                return False

    allowed_prefixes = [
        "13_web_dashboard/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "scripts/validate_original_phase_5b",
        "scripts/validate_original_phase_5a",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5d_handoff_composer_e2e.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5e_runbook_simulator_e2e.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_plus1_controlled_automation_readiness_e2e.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer_e2e.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for path in changed:
        allowed = any(path.startswith(p) for p in allowed_prefixes)
        if not allowed:
            print(f"  FAIL: Unexpected changed path: {path}")
            return False

    return True

def check_reports():
    reports_dir = PROJECT_ROOT / "09_exports" / "interface_phase_5"
    for report_name in [
        "original_phase_5b_client_side_request_packet_builder_report.md",
        "original_phase_5b_design_report.md",
        "original_phase_5b_safety_report.md",
        "original_phase_5b_validator_report.md",
        "original_phase_5b_acceptance_report.md",
    ]:
        path = reports_dir / report_name
        if not path.exists():
            print(f"  FAIL: Missing report: {report_name}")
            return False
        text = path.read_text(encoding="utf-8")
        if "PASS_WITH_HIGH_CONFIDENCE" not in text and "CLIENT_SIDE_ONLY" not in text:
            print(f"  FAIL: Report missing required markers: {report_name}")
            return False
    return True

print("Running Original Phase 5B Request Packet Builder E2E Validator...\n")

validators = [
    "validate_original_phase_5b_request_packet_builder.py",
    "validate_original_phase_5a_client_side_workflow_shell.py",
    "validate_original_phase_4_hosted_dashboard_polish.py",
    "validate_backend_phase_4d_schema_previews.py",
    "validate_backend_phase_4d_disabled_ui.py",
    "validate_backend_phase_4c_snapshot.py",
    "validate_backend_phase_4a_foundation.py",
]

all_pass = True
for v in validators:
    ok = run_validator(v)
    if not ok:
        all_pass = False
        print(f"  VALIDATOR_FAIL: {v}")

print()
print("Checking forbidden diff paths...")
diff_ok = check_diff()
if not diff_ok:
    all_pass = False

print("Checking reports...")
reports_ok = check_reports()
if not reports_ok:
    all_pass = False

print()
if all_pass:
    print("ORIGINAL_PHASE_5B_REQUEST_PACKET_BUILDER_E2E_VALIDATION_PASS")
else:
    print("ORIGINAL_PHASE_5B_REQUEST_PACKET_BUILDER_E2E_VALIDATION_FAIL")
    sys.exit(1)
