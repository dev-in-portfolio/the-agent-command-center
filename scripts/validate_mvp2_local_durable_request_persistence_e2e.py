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
        ["python3", "scripts/validate_mvp2_local_durable_request_persistence.py"],
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
        "scripts/validate_mvp2_local_durable_request_persistence.py",
        "scripts/validate_mvp2_local_durable_request_persistence_e2e.py",
        ".gitignore",
    ]
    forbidden_prefixes = [
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "11_interface/",
        "12_tui/",
        "10_runtime/",
        "netlify/functions/",
    ]

    for path in changed:
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                fail(f"Forbidden changed path: {path}")
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            fail(f"Unexpected changed path: {path}")

    print("MVP2_LOCAL_DURABLE_REQUEST_PERSISTENCE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()

