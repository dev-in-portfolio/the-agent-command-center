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

    # 2. Run Planning validator (Phase 4B)
    res = _run([sys.executable, str(ROOT / "scripts/validate_backend_phase_4b_planning.py")])
    if res.returncode != 0:
        _fail(f"Phase 4B Planning validation failed: {res.stdout}")

    # 3. Check for dangerous implementation terms
    forbidden = ["child_process", "exec(", "spawn(", "GitHub token", "Netlify token"]
    for path in ROOT.rglob("*.md"):
        if "14_backend" in str(path) or "09_exports" in str(path):
            continue
        content = path.read_text(errors="ignore")
        for word in forbidden:
            if word in content:
                _fail(f"Forbidden term '{word}' found in {path}")

    # 4. Check acceptance report verdict
    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4b_acceptance_report.md").read_text()
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Phase 4B acceptance report missing required verdict")

    print("BACKEND_PHASE_4B_E2E_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
