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
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp18_share_ready_external_review_portal.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    # Final safety scan
    stdout, stderr, code = run("python3 - <<'PY'\nfrom pathlib import Path\nscan_roots = [Path('14_backend/product_runtime'), Path('netlify/functions'), Path('13_web_dashboard'), Path('09_exports/mvp_product_track'), Path('09_exports/external_demo_package')]\nfor root in scan_roots:\n if not root.exists(): continue\n for path in root.rglob('*'):\n  if not path.is_file(): continue\n  if '__pycache__' in path.parts: continue\n  if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico'}: continue\n  text = path.read_text(encoding='utf-8', errors='replace')\n  lower = text.lower()\n  if 'sb-secret-' in lower and not any(x in str(path) for x in ['scripts/validate_', '09_exports/']): raise SystemExit(f'SECRET_KEY_LEAK: {path}')\n  if not any(x in str(path) for x in ['scripts/validate_', '09_exports/', 'dashboard_renderer.py', '13_web_dashboard/dist/']):\n   for item in ['localstorage', 'sessionstorage', 'document.cookie', 'indexeddb']:\n    if item in lower: raise SystemExit(f'FORBIDDEN_PATTERN {item}: {path}')\nprint('MVP19_SAFETY_SCAN_PASS')\nPY")
    if code != 0:
        fail(f"Safety scan failed: {stdout}")

    print("MVP19_EXTERNAL_FEEDBACK_INTAKE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
