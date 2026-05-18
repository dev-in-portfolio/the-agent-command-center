#!/usr/bin/env python3
"""E2E Validation for MVP-44 Persistent Request Storage Foundation"""

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
    print("MVP-44 E2E Validation")
    
    # Direct validators (Flat model)
    run_step("MVP-44 Direct Validator", "validate_mvp44_persistent_request_storage_foundation.py")
    run_step("MVP-43 Direct Validator", "validate_mvp43_operational_auth_foundation.py")
    run_step("MVP-42 Direct Validator", "validate_mvp42_operator_controlled_response_import_dry_run.py")
    run_step("MVP-41 Direct Validator", "validate_mvp41_controlled_reviewer_response_intake_blueprint.py")
    
    # Core system checks
    run_step("Live Dashboard Usability Validator", "validate_live_dashboard_usability_after_mvp41.py")
    run_step("Live-Page Context-Aware Scan", "validate_live_page_context_aware_control_scan.py")
    run_step("Validation Helper Test", "test_validation_helpers_control_scan.py")
    run_step("Master Validator Wall", "validate_phase5_plus1_master_validator_wall.py")

    print("MVP44_PERSISTENT_REQUEST_STORAGE_FOUNDATION_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
