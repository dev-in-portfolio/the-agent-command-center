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
        SUPABASE_DIR / "controlled_request_create_model.json",
        SUPABASE_DIR / "request_create_payload_schema.json",
        ROOT / "netlify/functions/_shared/request_payload_validator.js",
        ROOT / "netlify/functions/_shared/supabase_write_client.js",
        ROOT / "netlify/functions/request-write-smoke-status.js",
        DIST_DIR / "mvp8_controlled_request_create_model.json",
        REPORT_DIR / "mvp8_controlled_request_create_report.md",
        REPORT_DIR / "mvp8_payload_schema_report.md",
        REPORT_DIR / "mvp8_write_gate_report.md",
        REPORT_DIR / "mvp8_blocked_actions_report.md",
        REPORT_DIR / "mvp8_create_smoke_test_report.md",
        REPORT_DIR / "mvp8_security_boundary_report.md",
        REPORT_DIR / "mvp8_next_product_step_report.md",
        REPORT_DIR / "mvp8_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-8",
        "CONTROLLED REQUEST CREATE WRITE",
        "CREATE ONLY",
        "AUTHENTICATED POST REQUIRED",
        "STRICT PAYLOAD VALIDATION",
        "ANON KEY + USER BEARER TOKEN",
        "RLS-ENFORCED INSERT",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "VERIFY CREATE WITH REAL USER TOKEN",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Create Write Status Panel",
        "Payload Schema Panel",
        "Write Gate Panel",
        "Blocked Actions Panel",
        "Smoke Test Panel",
        "Next Product Decision Panel",
        "Copy create-write checklist",
        "Copy payload schema",
        "Copy write-gate checklist",
        "Copy smoke-test checklist",
        "Copy MVP-8 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp8_acceptance_report.md")
    for text in [
        "CONTROLLED_AUTHENTICATED_REQUEST_CREATE_READY",
        "PASS_WITH_CREATE_SMOKE_TEST_OPTIONAL",
        "NEXT_STEP_VERIFY_CREATE_WRITE_THEN_ADD_REQUEST_DETAIL_UI",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    requests_js = read_text(ROOT / "netlify/functions/requests.js")
    if "action === \"create\"" not in requests_js and "action !== \"create\"" not in requests_js:
        fail("Missing requests.js action gate: action check for create")
    assert_contains(requests_js, "MVP_ENABLE_REQUEST_API_WRITES", "requests.js write flag check")
    assert_contains(requests_js, "validateCreateRequestPayload", "requests.js payload validation call")
    assert_contains(requests_js, "createRequest(", "requests.js write client call")

    file_map = {
        "supabase_write_client.js": read_text(ROOT / "netlify/functions/_shared/supabase_write_client.js"),
        "request_payload_validator.js": read_text(ROOT / "netlify/functions/_shared/request_payload_validator.js"),
        "request-write-smoke-status.js": read_text(ROOT / "netlify/functions/request-write-smoke-status.js"),
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
    ]
    for name, text in file_map.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    # Specific safety checks for write client
    write_client = file_map["supabase_write_client.js"].lower()
    for forbidden in [
        "supabase_service_role_key",
        "service_role",
        "method: \"patch\"",
        "method: 'patch'",
        "method: \"put\"",
        "method: 'put'",
        "method: \"delete\"",
        "method: 'delete'",
        "/rpc/",
    ]:
        if forbidden in write_client:
            fail(f"Forbidden pattern in supabase_write_client.js: {forbidden}")

    print("MVP8_CONTROLLED_AUTHENTICATED_REQUEST_CREATE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
