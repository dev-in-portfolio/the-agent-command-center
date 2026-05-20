#!/usr/bin/env python3
# MVP42_E2E_VALIDATOR_FLAT_DEPENDENCY_CONTRACT

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_script(script_name: str) -> bool:
    print(f"Running {script_name}...")
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / script_name)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] {script_name}")
        print(res.stdout)
        print(res.stderr)
        return False
    print(f"[PASS] {script_name}")
    return True

def main():
    print("MVP-42 E2E Validation")
    
    # Flat model: call direct validators, not E2E validators
    steps = [
        ("MVP-42 direct validator", "validate_mvp42_operator_controlled_response_import_dry_run.py"),
        ("MVP-41 direct validator", "validate_mvp41_controlled_reviewer_response_intake_blueprint.py"),
        ("MVP-40 direct validator", "validate_mvp40_reviewer_response_capture_readiness_lock.py"),
        ("Live-page context scan", "validate_live_page_context_aware_control_scan.py"),
        ("Validation helper test", "test_validation_helpers_control_scan.py"),
        ("Master validator wall", "validate_phase5_plus1_master_validator_wall.py"),
    ]
    
    for label, script in steps:
        if not run_script(script):
            print(f"MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_E2E_VALIDATION_FAIL: {label}")
            sys.exit(1)
            
    print("MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
