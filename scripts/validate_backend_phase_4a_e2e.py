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
    # 1. Run Foundation validator
    res = _run([sys.executable, str(ROOT / "scripts" / "validate_backend_phase_4a_foundation.py")])
    if res.returncode != 0:
        _fail(f"Foundation validation failed: {res.stdout} {res.stderr}")
    
    # 2. Run Phase 3 validators (to ensure no regressions)
    res = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_3_dashboard.py")])
    if res.returncode != 0:
        _fail(f"Phase 3 Dashboard validation failed: {res.stdout} {res.stderr}")

    res = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_3_e2e.py")])
    if res.returncode != 0:
        _fail(f"Phase 3 E2E validation failed: {res.stdout} {res.stderr}")

    # 3. Check for specific panel in built index.html
    index_html = (ROOT / "13_web_dashboard" / "dist" / "index.html").read_text()
    if 'id="backend-status-panel"' not in index_html:
        _fail("Backend status panel missing from built index.html")

    print("BACKEND_PHASE_4A_E2E_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
