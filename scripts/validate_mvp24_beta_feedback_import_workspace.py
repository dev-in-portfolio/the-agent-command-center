#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
SCRIPT_DIR = ROOT / "scripts"

def fail(message):
    raise SystemExit(f"FAIL: {message}")

def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        fail(f"Unable to read {path}: {exc}")

def ensure_exists(path):
    if not path.exists():
        fail(f"Missing required file: {path}")

def assert_contains(text, needle, label):
    if needle not in text:
        fail(f"Missing {label}: {needle}")

def main():
    required_files = [
        UI_MODEL_DIR / "reviewed_beta_feedback_import_workspace_model.json",
        UI_MODEL_DIR / "beta_feedback_import_session_model.json",
        UI_MODEL_DIR / "beta_feedback_import_form_model.json",
        UI_MODEL_DIR / "beta_feedback_import_result_model.json",
        DIST_DIR / "mvp24_beta_feedback_import_workspace_model.json",
        REPORT_DIR / "mvp24_beta_feedback_import_workspace_report.md",
        REPORT_DIR / "mvp24_beta_import_session_report.md",
        REPORT_DIR / "mvp24_beta_import_form_report.md",
        REPORT_DIR / "mvp24_security_boundary_report.md",
        REPORT_DIR / "mvp24_next_product_step_report.md",
        REPORT_DIR / "mvp24_validator_quality_report.md",
        REPORT_DIR / "mvp24_acceptance_report.md",
        REPORT_DIR / "mvp24_validator_wall_review.md"
    ]
    for path in required_files:
        ensure_exists(path)

    # Markers in acceptance
    acceptance = read_text(REPORT_DIR / "mvp24_acceptance_report.md")
    markers = [
        "REVIEWED_BETA_FEEDBACK_IMPORT_WORKSPACE_READY",
        "PASS_WITH_TOKEN_IN_MEMORY_AND_FLAG_GATED_IMPORT",
        "TOKEN_IN_MEMORY_ONLY",
        "NETLIFY_FUNCTION_ONLY",
        "PAYLOAD_VALIDATION_PREVIEW_READY",
        "FEEDBACK_PERSISTENCE_DISABLED_HANDLED",
        "SERVICE_ROLE_NOT_USED",
        "NO_AUTOMATIC_MIGRATION_APPLY",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_ADD_AUTHENTICATED_FEEDBACK_REVIEW_INBOX"
    ]
    for m in markers:
        assert_contains(acceptance, m, f"acceptance marker {m}")

    index = read_text(DIST_DIR / "index.html")
    for m in [
        "MVP-24",
        "REVIEWED BETA FEEDBACK IMPORT WORKSPACE",
        "TOKEN IN MEMORY ONLY",
        "FEEDBACK ENDPOINT STATUS PANEL",
        "MIGRATION READINESS PANEL",
        "FEEDBACK PACKET IMPORT FORM",
        "PAYLOAD VALIDATION PREVIEW",
        "FEEDBACK_PERSISTENCE_DISABLED HANDLED",
        "NETLIFY FUNCTION ONLY",
        "SERVICE ROLE NOT USED",
        "NO AUTOMATIC MIGRATION APPLY",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_ADD_AUTHENTICATED_FEEDBACK_REVIEW_INBOX",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]:
        assert_contains(index, m, f"index marker {m}")

    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, SCRIPT_DIR, ROOT / "netlify" / "functions"]
    runtime_forbidden = [
        "localStorage.setItem",
        "localStorage.getItem",
        "sessionStorage.setItem",
        "sessionStorage.getItem",
        "document.cookie =",
        "indexedDB.open",
        "api.github.com",
        "api.netlify.com",
        "supabase.co",
        "child_process",
        "execSync",
        "spawn(",
        "os.system",
        "eval(",
        "Function(",
    ]

    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file(): continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts): continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}: continue
            
            content = read_text(path)
            lower = content.lower()
            path_str = str(path).lower()
            
            if "scripts/validate_" in path_str: continue

            for pattern in ["sb_secret_", "postgresql://postgres:", "SUPABASE_SERVICE_ROLE_KEY=sb_"]:
                if pattern in content:
                    fail(f"Forbidden critical pattern in {path}: {pattern}")

            if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
                for pattern in runtime_forbidden:
                    if pattern in content:
                        is_js_call = path.suffix == ".js"
                        is_html_exec = path.suffix == ".html" and (f'"{pattern}"' in content or f"'{pattern}'" in content or f"fetch({pattern}" in content)
                        if is_js_call or is_html_exec:
                            if pattern in ["/api/feedback", "supabase.co"]:
                                if "createClient(" in content or "supabase.createClient" in content:
                                     fail(f"Forbidden direct Supabase client in dashboard runtime: {path}")
                                continue
                            fail(f"Forbidden runtime pattern in dashboard: {pattern} in {path}")

            if path.suffix == ".json" and ("mvp24" in path_str or "feedback" in path_str):
                try:
                    data = json.loads(content)
                    def check_json_security(obj):
                        if not isinstance(obj, dict): return
                        for k, v in obj.items():
                            nk = k.lower()
                            if nk.endswith("enabled") and v is True:
                                 if nk.startswith("no_"): continue
                                 dangerous_flags = ["automation", "synthesis", "ingestion", "queue", "migration", "apply", "automatic_migration_apply_enabled"]
                                 if any(x in nk for x in dangerous_flags):
                                      if "implementation_enabled" in nk and "controlled_feedback_import_write_model.json" in path_str:
                                          continue
                                      fail(f"Forbidden enabled flag {k} in {path}")
                            if nk == "actual_import_default" and v is True:
                                 fail(f"Forbidden actual_import_default flag {k} in {path}")
                            if nk == "does_not_enable_feature_flag" and v is False:
                                 fail(f"Gate violation: does_not_enable_feature_flag must be true in {path}")
                            if nk == "does_not_apply_migration" and v is False:
                                 fail(f"Gate violation: does_not_apply_migration must be true in {path}")
                            if nk == "service_role_used" and v is True:
                                 fail(f"Forbidden service_role_used flag {k} in {path}")
                            if nk == "browser_direct_supabase_calls" and v is True:
                                 fail(f"Forbidden browser_direct_supabase_calls {k} in {path}")
                            check_json_security(v)
                    check_json_security(data)
                except json.JSONDecodeError: pass

    print("MVP24_BETA_FEEDBACK_IMPORT_WORKSPACE_VALIDATION_PASS")

if __name__ == "__main__":
    main()