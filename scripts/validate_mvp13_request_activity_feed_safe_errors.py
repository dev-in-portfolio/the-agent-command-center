#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
FUNCTIONS_DIR = ROOT / "netlify" / "functions"

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
        UI_MODEL_DIR / "safe_api_error_model.json",
        UI_MODEL_DIR / "request_activity_feed_model.json",
        UI_MODEL_DIR / "activity_feed_filter_model.json",
        UI_MODEL_DIR / "timeline_empty_error_state_model.json",
        DIST_DIR / "mvp13_request_activity_safe_errors_model.json",
        FUNCTIONS_DIR / "_shared" / "safe_error.js",
        REPORT_DIR / "mvp13_safe_api_error_report.md",
        REPORT_DIR / "mvp13_request_activity_feed_report.md",
        REPORT_DIR / "mvp13_activity_filtering_report.md",
        REPORT_DIR / "mvp13_timeline_empty_error_states_report.md",
        REPORT_DIR / "mvp13_timeline_refresh_ux_report.md",
        REPORT_DIR / "mvp13_security_boundary_report.md",
        REPORT_DIR / "mvp13_next_product_step_report.md",
        REPORT_DIR / "mvp13_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-13",
        "REQUEST ACTIVITY FEED",
        "SAFE API ERROR UX",
        "RAW ERROR EXPOSURE BLOCKED",
        "TIMELINE FILTERING",
        "GROUPED ACTIVITY FEED",
        "EMPTY AND ERROR STATES",
        "COPY SAFE ERROR CODE",
        "USER-OWNED ACTIVITY ONLY",
        "RLS-ENFORCED EVENT READS",
        "REQUEST ROW UPDATE BLOCKED",
        "UPDATE DELETE APPROVE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_MANUAL_LIFECYCLE_EVENT_TEST_THEN_ACTIVITY_FEED_REFINEMENT",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Safe Error UX Panel",
        "Request Activity Feed Panel",
        "Activity Filtering Panel",
        "Empty/Error States Panel",
        "Timeline Refresh UX Panel",
        "Security Boundary Panel",
        "Copy MVP-13 validation checklist"
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp13_acceptance_report.md")
    for text in [
        "REQUEST_ACTIVITY_FEED_SAFE_ERRORS_READY",
        "PASS_WITH_MANUAL_LIFECYCLE_TEST_RECOMMENDED",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    requests_js = read_text(FUNCTIONS_DIR / "requests.js")
    assert_contains(requests_js, "safeErrorResponse", "requests.js safe error import")
    if "err.message" in requests_js:
        fail("Raw err.message is still present in requests.js")

    # Safety checks
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR]
    forbidden = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
    ]

    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
                continue
            text = read_text(path).lower()
            for pattern in forbidden:
                if pattern.lower() in text:
                    fail(f"Forbidden pattern in {path.name}: {pattern}")

    print("MVP13_REQUEST_ACTIVITY_FEED_SAFE_ERRORS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
