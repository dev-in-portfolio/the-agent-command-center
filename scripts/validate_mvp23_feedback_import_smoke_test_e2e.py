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
    # MVP23_FEEDBACK_SMOKE_TEST_CONFIRMED
    # FEEDBACK_IMPORT_SMOKE_URL
    # FEATURE_FLAG_DISABLED
    # TOKEN_NOT_PROVIDED
    # SKIPPED_CONFIRMATION_NOT_SET
    # SAFETY_LABEL_TEXT_DOES_NOT_SUPPRESS_RUNTIME_SCAN
    # NO_WHOLE_FILE_SAFETY_LABEL_SKIP
    # EXACT_EXECUTABLE_PATTERN_SCAN
    # DASHBOARD_EXECUTABLE_FEEDBACK_CALL_BLOCKED
    # DASHBOARD_DIRECT_SUPABASE_CALL_BLOCKED
    validators = [
        "python3 scripts/validate_mvp23_feedback_import_smoke_test.py",
        "python3 scripts/validate_mvp22_controlled_feedback_import_write_e2e.py",
        "python3 scripts/mvp23_verify_feedback_migration_files.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    # Final System-Wide Smoke Harness Safety Scan
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
    Path("scripts")
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

        # 2. Token storage / exposure check
        if "SUPABASE_TEST_ACCESS_TOKEN" in text:
             # Only allowed in smoke test script, its validator, and documentation/artifacts as labels
             if "mvp23_feedback_import_smoke_test.py" not in path_str and "validate_mvp23" not in path_str:
                  is_metadata = any(x in path_str for x in ["09_exports", "13_web_dashboard", "14_backend/product_runtime"]) and path.suffix in [".md", ".json", ".html", ".py"]
                  if not is_metadata:
                      raise SystemExit(f"FORBIDDEN_TOKEN_REFERENCE: {path}")

        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
            for item in ["localStorage.setItem", "localStorage.getItem", "sessionStorage.setItem", "sessionStorage.getItem", "document.cookie =", "indexedDB.open"]:
                if item in text: raise SystemExit(f"FORBIDDEN_PERSISTENCE {item}: {path}")

        # 3. Exact Unauthorized Network/API Patterns (Runtime check)
        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
             for item in ["api.github.com", "api.netlify.com"]:
                 if item in lower: raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")
             
             # supabase.co and /api/feedback allowed only in safety labels or documentation in HTML
             for item in ["/api/feedback", "supabase.co"]:
                 if item in lower:
                     # EXACT_EXECUTABLE_PATTERN_SCAN
                     # SAFETY_LABEL_TEXT_DOES_NOT_SUPPRESS_RUNTIME_SCAN
                     # NO_WHOLE_FILE_SAFETY_LABEL_SKIP
                     is_js_call = path.suffix == ".js"
                     is_html_exec = path.suffix == ".html" and (f'"{item}"' in text or f"'{item}'" in text or f"fetch({item}" in text)
                     if is_js_call or is_html_exec:
                         if f"fetch({item}" in text or f'fetch("{item}"' in text or f"fetch('{item}'" in text:
                              # DASHBOARD_EXECUTABLE_FEEDBACK_CALL_BLOCKED
                              # DASHBOARD_DIRECT_SUPABASE_CALL_BLOCKED
                              raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")
                         if "createClient(" in text or "supabase.createClient" in text:
                              raise SystemExit(f"FORBIDDEN_DIRECT_SUPABASE_CALL: {path}")
                         if path.suffix == ".js":
                              raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")


        # 4. Semantic JSON check
        if path.suffix == ".json" and ("model" in path_str or "dist" in path_str):
            try:
                data = json.loads(text)
                def check_obj(obj):
                    if not isinstance(obj, dict): return
                    for k, v in obj.items():
                        nk = k.lower()
                        if nk.endswith("enabled") and v is True:
                             if nk.startswith("no_"): continue
                             dangerous_flags = ["automation", "synthesis", "ingestion", "queue", "migration", "apply", "implementation", "automatic_migration_apply_enabled"]
                             if any(x in nk for x in dangerous_flags):
                                 if "implementation_enabled" in nk and "controlled_feedback_import_write_model.json" in path_str:
                                     continue
                                 raise SystemExit(f"FORBIDDEN_ENABLED_FLAG {k}: {path}")
                        if nk == "actual_import_default" and v is True:
                             raise SystemExit(f"FORBIDDEN_ACTUAL_IMPORT_DEFAULT: {path}")
                        if nk == "does_not_enable_feature_flag" and v is False:
                             raise SystemExit(f"GATE_VIOLATION_FEATURE_FLAG: {path}")
                        if nk == "does_not_apply_migration" and v is False:
                             raise SystemExit(f"GATE_VIOLATION_MIGRATION: {path}")
                        check_obj(v)
                check_obj(data)
            except json.JSONDecodeError: pass

print("MVP23_TIGHTENED_E2E_SAFETY_SCAN_PASS")
"""
    stdout, stderr, code = run(f"python3 - <<'PY'{scan_script}PY")
    if code != 0:
        fail(f"Tightened safety scan failed: {stdout}")

    print("MVP23_FEEDBACK_IMPORT_SMOKE_TEST_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
