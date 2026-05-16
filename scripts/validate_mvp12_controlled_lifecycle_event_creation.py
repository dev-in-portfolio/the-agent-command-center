#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase"
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
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
        SUPABASE_DIR / "controlled_lifecycle_event_model.json",
        SUPABASE_DIR / "lifecycle_event_payload_schema.json",
        ROOT / "netlify/functions/_shared/lifecycle_event_payload_validator.js",
        ROOT / "netlify/functions/_shared/supabase_lifecycle_write_client.js",
        ROOT / "netlify/functions/lifecycle-event-smoke-status.js",
        UI_MODEL_DIR / "lifecycle_event_creation_ui_model.json",
        DIST_DIR / "mvp12_controlled_lifecycle_event_model.json",
        REPORT_DIR / "mvp12_controlled_lifecycle_event_report.md",
        REPORT_DIR / "mvp12_event_payload_schema_report.md",
        REPORT_DIR / "mvp12_event_write_gate_report.md",
        REPORT_DIR / "mvp12_timeline_refresh_report.md",
        REPORT_DIR / "mvp12_blocked_actions_report.md",
        REPORT_DIR / "mvp12_lifecycle_event_smoke_test_report.md",
        REPORT_DIR / "mvp12_security_boundary_report.md",
        REPORT_DIR / "mvp12_next_product_step_report.md",
        REPORT_DIR / "mvp12_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-12",
        "CONTROLLED LIFECYCLE EVENT CREATION",
        "OPERATOR NOTE CREATION",
        "AUTHENTICATED EVENT POST REQUIRED",
        "STRICT EVENT PAYLOAD VALIDATION",
        "ANON KEY + USER BEARER TOKEN",
        "RLS-ENFORCED EVENT INSERT",
        "TIMELINE REFRESH AFTER EVENT",
        "REQUEST ROW UPDATE BLOCKED",
        "UPDATE DELETE APPROVE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_VERIFY_LIFECYCLE_EVENT_CREATION_WITH_REAL_USER_TOKEN",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Lifecycle Event Creation Panel",
        "Event Payload Schema Panel",
        "Event Write Gate Panel",
        "Timeline Refresh Panel",
        "Blocked Actions Panel",
        "Smoke Status Panel",
        "Security Boundary Panel",
        "Copy event payload schema",
        "Copy MVP-12 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp12_acceptance_report.md")
    for text in [
        "CONTROLLED_LIFECYCLE_EVENT_CREATION_READY",
        "PASS_WITH_LIFECYCLE_EVENT_SMOKE_TEST_OPTIONAL",
        "NEXT_STEP_VERIFY_LIFECYCLE_EVENT_CREATION_WITH_REAL_USER_TOKEN",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    requests_js = read_text(ROOT / "netlify/functions/requests.js")
    assert_contains(requests_js, "action === \"add_event\"", "requests.js action gate")
    assert_contains(requests_js, "validateLifecycleEventPayload", "requests.js payload validation call")
    assert_contains(requests_js, "createLifecycleEvent(", "requests.js write client call")

    file_map = {
        "supabase_lifecycle_write_client.js": read_text(ROOT / "netlify/functions/_shared/supabase_lifecycle_write_client.js"),
        "lifecycle_event_payload_validator.js": read_text(ROOT / "netlify/functions/_shared/lifecycle_event_payload_validator.js"),
        "lifecycle-event-smoke-status.js": read_text(ROOT / "netlify/functions/lifecycle-event-smoke-status.js"),
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
    write_client = file_map["supabase_lifecycle_write_client.js"].lower()
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
            fail(f"Forbidden pattern in supabase_lifecycle_write_client.js: {forbidden}")

    print("MVP12_CONTROLLED_LIFECYCLE_EVENT_CREATION_VALIDATION_PASS")


if __name__ == "__main__":
    main()
