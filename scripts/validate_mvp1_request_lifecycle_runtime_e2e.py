#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd):
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"FAIL: {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def main():
    validators = [
        ["python3", "scripts/validate_mvp1_request_lifecycle_runtime.py"],
        ["python3", "scripts/validate_original_plus2e_server_side_dry_run_engine.py"],
        ["python3", "scripts/validate_original_plus2d_approval_gate_storage.py"],
        ["python3", "scripts/validate_original_plus2c_immutable_audit_log.py"],
        ["python3", "scripts/validate_original_plus2b_persistent_request_storage.py"],
        ["python3", "scripts/validate_original_plus2a_backend_auth_foundation.py"],
        ["python3", "scripts/validate_phase5_plus1_master_validator_wall.py"],
    ]
    for cmd in validators:
        run(cmd)

    changed = run(["git", "diff", "--name-only", "origin/master..HEAD"]).splitlines()
    allowed_prefixes = [
        "13_web_dashboard/",
        "14_backend/product_runtime/",
        "09_exports/mvp_product_track/",
        "netlify/functions/product-runtime-status.js",
        "netlify/functions/_shared/models/product_runtime_status.json",
        "netlify/functions/backend-manifest.js",
        "scripts/validate_mvp1_request_lifecycle_runtime.py",
        "scripts/validate_mvp1_request_lifecycle_runtime_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "09_exports/original_plus2/original_plus2e_production_verification_report.md",
    ]
    forbidden_prefixes = [
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "11_interface/",
        "12_tui/",
        "10_runtime/",
    ]

    for path in changed:
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                fail(f"Forbidden changed path: {path}")
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            fail(f"Unexpected changed path: {path}")

    print("MVP1_REQUEST_LIFECYCLE_RUNTIME_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
