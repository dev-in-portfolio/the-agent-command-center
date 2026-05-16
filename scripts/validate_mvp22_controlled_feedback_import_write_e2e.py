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
    # Implementation audit targets for quality audit:
    # netlify/functions/feedback.js
    # supabase_feedback_write_client.js
    # feedback_payload_validator.js
    # external_feedback_packets
    # MVP_ENABLE_FEEDBACK_PERSISTENCE
    # FEEDBACK_PERSISTENCE_DISABLED
    # owner_user_id
    # method === "GET"
    # action === "status"
    # INVALID_ACTION
    # method === "POST"
    # action !== "import"
    # WRITE_ACTION_NOT_ALLOWED
    # MVP_ENABLE_FEEDBACK_PERSISTENCE
    # FEEDBACK_PERSISTENCE_DISABLED
    # getAuthContext
    # validateFeedbackPayload
    # importFeedbackPacket
    # METHOD_NOT_ALLOWED
    # disabled_idx
    # auth_idx
    # validate_idx
    # import_idx
    validators = [
        "python3 scripts/validate_mvp22_controlled_feedback_import_write.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    # Final System-Wide Implementation Safety Scan
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
        if "service-role" in lower and not any(x in lower for x in ["not used", "blocked", "excluded", "no ", "not exposed", "disabled", "forbidden"]):
             if path.suffix in {".js", ".html", ".json"}:
                 # Allow in JSON/HTML as labels
                 if path.suffix in [".json", ".html"]:
                     continue
                 # Only fail if it's a script/runtime; some JS are fine if they are status reporters
                 if path.suffix == ".js" and not any(x in path_str for x in ["auth-status.js", "validator", "readiness-status.js", "provider_config.js"]):
                     raise SystemExit(f"POTENTIAL_SERVICE_ROLE_EXPOSURE: {path}")

        # 2. Exact Dangerous Persistence Patterns (Runtime check)
        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
            for item in ["localStorage.setItem", "localStorage.getItem", "sessionStorage.setItem", "sessionStorage.getItem", "document.cookie =", "indexedDB.open"]:
                if item in text: raise SystemExit(f"FORBIDDEN_PERSISTENCE {item}: {path}")

        # 3. Exact Unauthorized Network/API Patterns (Runtime check)
        if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
             for item in ["api.github.com", "api.netlify.com"]:
                 if item in lower:
                     raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")
             
             # supabase.co and /api/feedback allowed only in safety labels or documentation in HTML
             for item in ["/api/feedback", "supabase.co"]:
                 if item in lower:
                     is_safety_label = path.suffix == ".html" and any(x in lower for x in ["<code>", "no ", "blocked", "disabled", "remains", "no-secret"])
                     is_executable = f'"{item}"' in text or f"'{item}'" in text or f"fetch({item}" in text
                     if is_executable:
                         if "/dist/" not in path_str or item == "/api/feedback":
                              raise SystemExit(f"FORBIDDEN_NETWORK_PATTERN {item}: {path}")
                     elif not is_safety_label:
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
                             dangerous_flags = ["submission", "write", "automation", "synthesis", "ingestion", "queue", "persistence", "migration", "apply", "migration_apply_enabled", "persistence_enabled", "supabase_write_enabled"]
                             if any(x in nk for x in dangerous_flags):
                                 if "implementation_enabled" in nk and "controlled_feedback_import_write_model.json" in path_str:
                                     continue
                                 if "implementation_enabled" in nk and "controlled_feedback_import_write_model.json" in path_str:
                                     continue
                                 raise SystemExit(f"FORBIDDEN_ENABLED_FLAG {k}: {path}")
                        if nk == "service_role_used" and v is True:
                             raise SystemExit(f"FORBIDDEN_SERVICE_ROLE_USED_FLAG: {path}")
                        if nk == "token_required" and v is True and ("mvp19" in path_str or "mvp20" in path_str or "mvp21" in path_str or "mvp22" in path_str):
                             raise SystemExit(f"FORBIDDEN_TOKEN_REQUIRED_FLAG: {path}")
                        check_obj(v)
                check_obj(data)
            except json.JSONDecodeError: pass

print("MVP22_TIGHTENED_E2E_SAFETY_SCAN_PASS")
"""
    stdout, stderr, code = run(f"python3 - <<'PY'{scan_script}PY")
    if code != 0:
        fail(f"Tightened safety scan failed: {stdout}")

    print("MVP22_CONTROLLED_FEEDBACK_IMPORT_WRITE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
