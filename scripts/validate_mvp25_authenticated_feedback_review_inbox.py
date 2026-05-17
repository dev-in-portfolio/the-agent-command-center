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
        ROOT / "netlify" / "functions" / "_shared" / "supabase_feedback_read_client.js",
        UI_MODEL_DIR / "authenticated_feedback_review_inbox_model.json",
        UI_MODEL_DIR / "feedback_review_detail_model.json",
        UI_MODEL_DIR / "feedback_synthesis_queue_model.json",
        UI_MODEL_DIR / "feedback_read_api_contract_model.json",
        DIST_DIR / "mvp25_authenticated_feedback_review_inbox_model.json",
        REPORT_DIR / "mvp25_feedback_read_api_report.md",
        REPORT_DIR / "mvp25_feedback_review_inbox_report.md",
        REPORT_DIR / "mvp25_feedback_detail_report.md",
        REPORT_DIR / "mvp25_feedback_synthesis_queue_report.md",
        REPORT_DIR / "mvp25_security_boundary_report.md",
        REPORT_DIR / "mvp25_next_product_step_report.md",
        REPORT_DIR / "mvp25_validator_quality_report.md",
        REPORT_DIR / "mvp25_acceptance_report.md",
        REPORT_DIR / "mvp25_validator_wall_review.md"
    ]
    for path in required_files:
        ensure_exists(path)

    # Markers in acceptance
    acceptance = read_text(REPORT_DIR / "mvp25_acceptance_report.md")
    markers = [
        "AUTHENTICATED_FEEDBACK_REVIEW_INBOX_READY",
        "PASS_WITH_OWNER_SCOPED_READ_ONLY_FEEDBACK_REVIEW",
        "FEEDBACK_LIST_READ_API_READY",
        "FEEDBACK_DETAIL_READ_API_READY",
        "OWNER_SCOPED_RLS_READS",
        "READ_ONLY_REVIEW_WORKFLOW",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_FEEDBACK_SYNTHESIS_AND_PRODUCT_DECISION_WORKFLOW"
    ]
    for m in markers:
        assert_contains(acceptance, m, f"acceptance marker {m}")

    index = read_text(DIST_DIR / "index.html")
    for m in [
        "MVP-25",
        "AUTHENTICATED FEEDBACK REVIEW INBOX",
        "FEEDBACK LIST READ API",
        "FEEDBACK DETAIL READ API",
        "OWNER-SCOPED RLS READS",
        "FEEDBACK SYNTHESIS QUEUE",
        "READ ONLY REVIEW WORKFLOW",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_FEEDBACK_SYNTHESIS_AND_PRODUCT_DECISION_WORKFLOW",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]:
        assert_contains(index, m, f"index marker {m}")

    # Read Client
    client_code = read_text(ROOT / "netlify" / "functions" / "_shared" / "supabase_feedback_read_client.js")
    assert_contains(client_code, "getFeedbackReadClient", "read client init")
    assert_contains(client_code, "bearerToken", "bearer token usage")
    assert_contains(client_code, "SUPABASE_URL", "env URL")
    assert_contains(client_code, "SUPABASE_ANON_KEY", "env ANON KEY")
    assert_contains(client_code, "listFeedbackPackets", "list action")
    assert_contains(client_code, "getFeedbackPacket", "get action")
    
    if "SUPABASE_SERVICE_ROLE_KEY" in client_code:
        fail("Service role key found in read client")

    # Feedback Endpoint
    endpoint = read_text(ROOT / "netlify" / "functions" / "feedback.js")
    assert_contains(endpoint, "action === \"list\"", "list action handler")
    assert_contains(endpoint, "action === \"get\"", "get action handler")
    assert_contains(endpoint, "getAuthContext", "auth context")
    assert_contains(endpoint, "importFeedbackPacket", "previous import behavior preserved")

    # Deep Feedback Endpoint Checks
    assert_contains(endpoint, 'action === "list"', "list action string")
    assert_contains(endpoint, 'action === "get"', "get action string")
    assert_contains(endpoint, "listFeedbackPackets", "listFeedbackPackets function")
    assert_contains(endpoint, "getFeedbackPacket", "getFeedbackPacket function")
    assert_contains(endpoint, "importFeedbackPacket", "importFeedbackPacket function")
    assert_contains(endpoint, "METHOD_NOT_ALLOWED", "METHOD_NOT_ALLOWED string")
    assert_contains(endpoint, "INVALID_ACTION", "INVALID_ACTION string")
    assert_contains(endpoint, "WRITE_ACTION_NOT_ALLOWED", "WRITE_ACTION_NOT_ALLOWED string")
    assert_contains(endpoint, "FEEDBACK_PERSISTENCE_DISABLED", "FEEDBACK_PERSISTENCE_DISABLED string")

    # Deep Read Client Checks
    assert_contains(client_code, "getFeedbackReadClient", "getFeedbackReadClient function")
    assert_contains(client_code, "bearerToken", "bearerToken string")
    assert_contains(client_code, "SUPABASE_URL", "SUPABASE_URL string")
    assert_contains(client_code, "SUPABASE_ANON_KEY", "SUPABASE_ANON_KEY string")
    assert_contains(client_code, "listFeedbackPackets", "listFeedbackPackets function")
    assert_contains(client_code, "getFeedbackPacket", "getFeedbackPacket function")
    assert_contains(client_code, "external_feedback_packets", "external_feedback_packets table")
    assert_contains(client_code, "Authorization", "Authorization header")

    forbidden_client = ["SUPABASE_SERVICE_ROLE_KEY", "service_role", 'method: "PATCH"', 'method: "PUT"', 'method: "DELETE"', "/rpc/"]
    for f in forbidden_client:
        if f in client_code:
            fail(f"Forbidden string in read client: {f}")


    # EXACT_SUPABASE_EXECUTABLE_PATTERN_SCAN
    # DASHBOARD_DIRECT_SUPABASE_FETCH_BLOCKED
    # DASHBOARD_SUPABASE_CREATE_CLIENT_BLOCKED
    # SUPABASE_LABEL_TEXT_DOES_NOT_SUPPRESS_SCAN
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
        "child_process",
        "execSync",
        "spawn(",
        "os.system",
        "eval(",
        "Function(",
    ]
    supabase_fetch_prefixes = [
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
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
                            fail(f"Forbidden runtime pattern in dashboard: {pattern} in {path}")

                has_supabase_domain = "supabase.co" in content
                has_create_client = "createClient(" in content or "supabase.createClient" in content
                has_xhr = "XMLHttpRequest" in content
                has_supabase_executable_fetch = any(prefix in content for prefix in supabase_fetch_prefixes)

                if has_create_client:
                    fail(f"Forbidden dashboard Supabase executable pattern createClient in {path}")
                if has_supabase_domain and has_supabase_executable_fetch:
                    fail(f"Forbidden dashboard Supabase executable pattern {path}")
                if has_supabase_domain and has_xhr:
                    fail(f"Forbidden dashboard Supabase executable pattern XMLHttpRequest in {path}")

            if path.suffix == ".json" and ("mvp25" in path_str or "feedback" in path_str):
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

    print("MVP25_AUTHENTICATED_FEEDBACK_REVIEW_INBOX_VALIDATION_PASS")

if __name__ == "__main__":
    main()
