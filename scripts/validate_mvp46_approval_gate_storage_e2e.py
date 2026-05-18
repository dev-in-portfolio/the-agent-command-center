#!/usr/bin/env python3
"""E2E Validation for MVP-46 Approval Gate Storage"""

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
    print("MVP-46 E2E Validation")
    run_step("MVP-46 Direct Validator", "validate_mvp46_approval_gate_storage.py")
    run_step("MVP-45 E2E Validator (chain dependency)", "validate_mvp45_immutable_audit_event_ledger_e2e.py")
    run_step("MVP-44 E2E Validator (chain dependency)", "validate_mvp44_persistent_request_storage_foundation_e2e.py")
    run_step("Live Dashboard Usability Validator", "validate_live_dashboard_usability_after_mvp41.py")
    run_step("Live-Page Context-Aware Scan", "validate_live_page_context_aware_control_scan.py")
    run_step("Validation Helper Test", "test_validation_helpers_control_scan.py")
    run_step("Master Validator Wall", "validate_phase5_plus1_master_validator_wall.py")

    print("MVP46_APPROVAL_GATE_STORAGE_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
