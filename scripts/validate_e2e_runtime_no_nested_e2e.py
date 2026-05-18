#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

FAILURES = []

def main():
    e2e_scripts = list(SCRIPTS.glob("validate_*_e2e.py"))
    # Exclude this guard itself
    e2e_scripts = [s for s in e2e_scripts if s.name != "validate_e2e_runtime_no_nested_e2e.py"]
    for script in e2e_scripts:
        text = script.read_text(encoding="utf-8")
        # Find all references to other _e2e.py files
        matches = re.findall(r'validate_.*_e2e\.py', text)
        for m in matches:
            if m != script.name:
                FAILURES.append(f"{script.name} invokes or references nested E2E: {m}")

    if FAILURES:
        print("E2E_RUNTIME_NO_NESTED_E2E_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
        
    print("E2E_RUNTIME_NO_NESTED_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
