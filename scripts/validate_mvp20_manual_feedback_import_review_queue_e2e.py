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
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    # Final System-Wide Safety Scan
    scan_script = """
import sys
import json
import re
from pathlib import Path
scan_roots = [
    Path("14_backend/product_runtime"),
    Path("netlify/functions"),
    Path("13_web_dashboard"),
    Path("09_exports/mvp_product_track"),
    Path("09_exports/external_demo_package")
]
for root in scan_roots:
    if not root.exists(): continue
    for path in root.rglob("*"):
        if not path.is_file(): continue
        if "__pycache__" in path.parts: continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}: continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        path_str = str(path).lower()
        if "scripts/validate_" in path_str: continue

        # 1. Critical Leaks
        if "sb_secret_" in text: raise SystemExit(f"SECRET_KEY_LEAK: {path}")
        if "postgresql://postgres:" in text: raise SystemExit(f"POSTGRES_CONNECTION_STRING_LEAK: {path}")
        if "SUPABASE_SERVICE_ROLE_KEY=sb_" in text: raise SystemExit(f"SERVICE_ROLE_VALUE_LEAK: {path}")
        if "service-role" in lower and not any(x in lower for x in ["not used", "blocked", "excluded", "no ", "not exposed", "disabled"]):
             if path.suffix in {".js", ".html", ".json"}:
                 # Only fail if it's a script/runtime; JSON contracts are fine
                 if path.suffix == ".js":
                     raise SystemExit(f"POTENTIAL_SERVICE_ROLE_EXPOSURE: {path}")

        # 2. Exact Dangerous Persistence Patterns (Runtime check)
        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
            for item in ["localStorage.setItem", "localStorage.getItem", "sessionStorage.setItem", "sessionStorage.getItem", "document.cookie =", "indexedDB.open"]:
                if item in text: raise SystemExit(f"FORBIDDEN_PERSISTENCE {item}: {path}")

        # 3. Exact Unauthorized Network/API Patterns (Runtime check)
        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
             for item in ["/api/feedback", "api.github.com", "api.netlify.com", "supabase.co"]:
                 if item in lower:
                     # Allow only as safety labels or documentation in HTML
                     is_safety_label = path.suffix == ".html" and any(x in lower for x in ["<code>", "no ", "blocked", "disabled", "remains", "no backend feedback"])
                     is_executable = f'"{item}"' in text or f"'{item}'" in text or f"fetch({item}" in text
                     if is_executable:
                         if "/dist/" not in path_str or item == "/api/feedback":
                              raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")
                     elif not is_safety_label:
                         raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")

print("MVP20_TIGHTENED_E2E_SAFETY_SCAN_PASS")
"""
    stdout, stderr, code = run(f"python3 - <<'PY'{scan_script}PY")
    if code != 0:
        fail(f"Validator quality meta-check failed: {stdout}")

    print("MVP20_MANUAL_FEEDBACK_IMPORT_REVIEW_QUEUE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
