#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
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
        SUPABASE_DIR / "real_authenticated_reads_model.json",
        ROOT / "netlify/functions/_shared/supabase_read_client.js",
        ROOT / "netlify/functions/_shared/auth_context.js",
        ROOT / "netlify/functions/requests.js",
        ROOT / "netlify/functions/request-read-smoke-status.js",
        DIST_DIR / "mvp7_real_authenticated_reads_model.json",
        REPORT_DIR / "mvp7_real_authenticated_reads_report.md",
        REPORT_DIR / "mvp7_auth_token_validation_report.md",
        REPORT_DIR / "mvp7_postgrest_read_adapter_report.md",
        REPORT_DIR / "mvp7_request_endpoint_actions_report.md",
        REPORT_DIR / "mvp7_read_smoke_test_report.md",
        REPORT_DIR / "mvp7_security_boundary_report.md",
        REPORT_DIR / "mvp7_next_product_step_report.md",
        REPORT_DIR / "mvp7_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-7",
        "REAL AUTHENTICATED SUPABASE READS",
        "SUPABASE AUTH TOKEN VALIDATION",
        "POSTGREST READS ENABLED",
        "ANON KEY + USER BEARER TOKEN",
        "RLS-ENFORCED REQUEST READS",
        "SERVICE ROLE NOT USED",
        "WRITES STILL DISABLED",
        "POST WRITES BLOCKED",
        "VERIFY WITH REAL USER TOKEN",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_CONTROLLED_REQUEST_CREATE_WRITES",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp7_acceptance_report.md")
    for text in [
        "REAL_AUTHENTICATED_SUPABASE_READS_READY",
        "PASS_WITH_TOKEN_TEST_OPTIONAL",
        "NEXT_STEP_BUILD_CONTROLLED_REQUEST_CREATE_WRITES",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    file_map = {
        "real_authenticated_reads_model.json": read_text(SUPABASE_DIR / "real_authenticated_reads_model.json"),
        "supabase_read_client.js": read_text(ROOT / "netlify/functions/_shared/supabase_read_client.js"),
        "auth_context.js": read_text(ROOT / "netlify/functions/_shared/auth_context.js"),
        "requests.js": read_text(ROOT / "netlify/functions/requests.js"),
        "request-read-smoke-status.js": read_text(ROOT / "netlify/functions/request-read-smoke-status.js"),
    }

    forbidden_patterns = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "api.github.com",
        "api.netlify.com",
        "os.system",
        "exec(",
        "spawn(",
        "execSync(",
        "child_process",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexeddb",
    ]
    for name, text in file_map.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    # Specific safety checks for read client
    read_client = file_map["supabase_read_client.js"].lower()
    for forbidden in [
        "supabase_service_role_key",
        "service_role",
        "method: \"post\"",
        "method: 'post'",
        "method: \"patch\"",
        "method: 'patch'",
        "method: \"put\"",
        "method: 'put'",
        "method: \"delete\"",
        "method: 'delete'",
    ]:
        if forbidden in read_client:
            fail(f"Forbidden pattern in supabase_read_client.js: {forbidden}")

    print("MVP7_REAL_AUTHENTICATED_SUPABASE_READS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
