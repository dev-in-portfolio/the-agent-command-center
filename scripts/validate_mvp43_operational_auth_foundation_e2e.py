#!/usr/bin/env python3
"""E2E Validation for MVP-43 Operational Auth Foundation"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

FAILURES = []

def run_step(name, script_name):
    print(f"\nPhase {len(FAILURES) + 1} — {name}")
    result = subprocess.run(["python3", ROOT / "scripts" / script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name}")
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
        for line in result.stderr.strip().splitlines():
            print(f"    [ERR] {line}")
        FAILURES.append(name)
        sys.exit(1)

def main():
    print("MVP-43 E2E Validation")
    run_step("MVP-43 Direct Validator", "validate_mvp43_operational_auth_foundation.py")
    run_step("MVP-42 E2E Validator (chain dependency)", "validate_mvp42_operator_controlled_response_import_dry_run_e2e.py")
    run_step("MVP-41 E2E Validator (chain dependency)", "validate_mvp41_controlled_reviewer_response_intake_blueprint_e2e.py")
    run_step("Live Dashboard Usability Validator", "validate_live_dashboard_usability_after_mvp41.py")
    run_step("Live-Page Context-Aware Scan", "validate_live_page_context_aware_control_scan.py")
    run_step("Validation Helper Test", "test_validation_helpers_control_scan.py")
    run_step("Master Validator Wall", "validate_phase5_plus1_master_validator_wall.py")

    print("MVP43_OPERATIONAL_AUTH_FOUNDATION_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
