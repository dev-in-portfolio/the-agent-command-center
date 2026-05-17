#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def fail(message):
    raise SystemExit(f"FAIL: {message}")

def run(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
        return res.stdout, res.stderr, res.returncode
    except Exception as exc:
        fail(f"Execution error for {cmd}: {exc}")

def main():
    validators = [
        "python3 scripts/validate_mvp25_authenticated_feedback_review_inbox.py",
        "python3 scripts/validate_mvp24_beta_feedback_import_workspace_e2e.py",
        "python3 scripts/validate_mvp23_feedback_import_smoke_test_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    print("MVP25_AUTHENTICATED_FEEDBACK_REVIEW_INBOX_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()