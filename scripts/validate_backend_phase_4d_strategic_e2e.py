#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _run(path):
    return subprocess.run([sys.executable, str(ROOT / path)], capture_output=True, text=True)


def main():
    validators = [
        "scripts/validate_backend_phase_4d_schema_previews.py",
        "scripts/validate_backend_phase_4d_disabled_ui.py",
        "scripts/validate_backend_phase_4d_strategic_build.py",
    ]
    for validator in validators:
        result = _run(validator)
        if result.returncode != 0:
            _fail(f"{validator} failed: {result.stdout}{result.stderr}")

    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4d_strategic_build_acceptance_report.md").read_text(encoding="utf-8")
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Strategic build acceptance report missing required verdict")

    html = (ROOT / "13_web_dashboard/dist/index.html").read_text(encoding="utf-8")
    for forbidden in ["http://", "https://", "fetch(\"https://", "fetch('https://"]:
        if forbidden in html:
            _fail(f"Forbidden external reference found in dashboard HTML: {forbidden}")

    print("BACKEND_PHASE_4D_STRATEGIC_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
