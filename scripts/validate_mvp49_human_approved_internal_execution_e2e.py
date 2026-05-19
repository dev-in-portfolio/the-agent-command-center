#!/usr/bin/env python3
"""E2E Validation for MVP-49 Human-Approved Internal Execution (Optimized Flat Model)"""

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
    print("MVP-49 E2E Validation")

    # Direct validators (Flat model - no recursive E2E calls)
    run_step("MVP-49 Direct Validator", "validate_mvp49_human_approved_internal_execution.py")
    run_step("MVP-48 Direct Validator", "validate_mvp48_controlled_action_queue.py")
    run_step("MVP-47 Direct Validator", "validate_mvp47_server_side_dry_run_engine.py")
    run_step("MVP-46 Direct Validator", "validate_mvp46_approval_gate_storage.py")
    run_step("MVP-45 Direct Validator", "validate_mvp45_immutable_audit_event_ledger.py")
    run_step("MVP-44 Direct Validator", "validate_mvp44_persistent_request_storage_foundation.py")
    run_step("MVP-43 Direct Validator", "validate_mvp43_operational_auth_foundation.py")
    run_step("MVP-42 Direct Validator", "validate_mvp42_operator_controlled_response_import_dry_run.py")

    # Core system checks
    run_step("Live Dashboard Usability Validator", "validate_live_dashboard_usability_after_mvp41.py")
    run_step("Live-Page Context-Aware Scan", "validate_live_page_context_aware_control_scan.py")
    run_step("Validation Helper Test", "test_validation_helpers_control_scan.py")
    run_step("E2E Runtime No-Nested Guard", "validate_e2e_runtime_no_nested_e2e.py")
    run_step("Master Validator Wall", "validate_phase5_plus1_master_validator_wall.py")

    print("MVP49_HUMAN_APPROVED_INTERNAL_EXECUTION_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
