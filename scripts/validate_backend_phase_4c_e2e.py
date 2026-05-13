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
    # 1. Run Foundation validator (Phase 4A)
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4a_foundation.py")])
    if res.returncode != 0:
        _fail(f"Phase 4A Foundation validation failed: {res.stdout}")

    # 2. Run Phase 4B Planning validator
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4b_planning.py")])
    if res.returncode != 0:
        _fail(f"Phase 4B Planning validation failed: {res.stdout}")

    # 3. Run Phase 4C Planning validator
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4c_planning.py")])
    if res.returncode != 0:
        _fail(f"Phase 4C Planning validation failed: {res.stdout}")

    # 4. Check for dangerous implementation terms
    forbidden = [
        "workflow_dispatch",
        "merge_pull_request",
        "create_pull_request",
        "update_file",
        "delete_file",
        "netlify deploy",
    ]
    # Scrutinize source code for functional integration leaks
    for path in ROOT.rglob("*.js"):
        if "_shared" in str(path) or "node_modules" in str(path):
            continue
        content = path.read_text(errors="ignore")
        for word in forbidden:
            if word in content:
                _fail(f"Forbidden implementation term '{word}' found in JS source: {path}")

    # 5. Check acceptance report verdict
    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4c_acceptance_report.md").read_text()
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Phase 4C acceptance report missing required verdict")

    print("BACKEND_PHASE_4C_E2E_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
