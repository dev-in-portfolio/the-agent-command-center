#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def main():
    # 1. Run Snapshot validator
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4c_snapshot.py")])
    if res.returncode != 0:
        _fail(f"Snapshot validation failed: {res.stdout}")

    # 2. Run Gate Review validator
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4d_gate_review.py")])
    if res.returncode != 0:
        _fail(f"Gate Review validation failed: {res.stdout}")

    # 3. Check for dangerous implementation terms
    forbidden = [
        "workflow_dispatch", "merge_pull_request", "create_pull_request",
        "update_file", "delete_file", "netlify deploy"
    ]
    for path in ROOT.rglob("*.js"):
        if "_shared" in str(path) or "node_modules" in str(path):
            continue
        content = path.read_text(errors="ignore")
        for word in forbidden:
            if word in content:
                _fail(f"Forbidden term '{word}' found in JS source: {path}")

    # 4. Check acceptance report verdict
    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4c_snapshot_and_4d_gate_acceptance_report.md").read_text()
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Combined acceptance report missing required verdict")

    print("BACKEND_PHASE_4C_SNAPSHOT_AND_4D_GATE_E2E_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
