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


def walk_json_flags(path):
    data = json.loads(read_text(path))
    expected_true = [
        "demo_session_capture_ready",
        "external_review_loop_ready",
        "reviewer_persona_selection_ready",
        "feedback_packet_draft_ready",
        "optional_feedback_import_supported",
        "requires_explicit_operator_action",
        "token_in_memory_only",
        "safe_demo_mode",
        "no_fake_reviewer_results",
        "manual_review_required",
    ]
    for key in expected_true:
        if key in data and data[key] is not True:
            fail(f"{path.name} gate not true: {key}")

    expected_false = [
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "email_sending_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "automation_enabled",
        "deploy_merge_push_controls_enabled",
    ]
    for key in expected_false:
        if key in data and data[key] is not False:
            fail(f"{path.name} forbidden flag not false: {key}")


def main():
    required_models = [
        UI_MODEL_DIR / "demo_session_capture_workspace_model.json",
        UI_MODEL_DIR / "external_reviewer_persona_session_model.json",
        UI_MODEL_DIR / "demo_session_notes_model.json",
        UI_MODEL_DIR / "review_feedback_packet_draft_model.json",
        UI_MODEL_DIR / "demo_follow_up_decision_model.json",
        DIST_DIR / "mvp31_demo_session_capture_review_loop_model.json",
    ]
    required_reports = [
        REPORT_DIR / "mvp31_demo_session_capture_report.md",
        REPORT_DIR / "mvp31_external_review_loop_report.md",
        REPORT_DIR / "mvp31_reviewer_persona_session_report.md",
        REPORT_DIR / "mvp31_feedback_packet_draft_report.md",
        REPORT_DIR / "mvp31_optional_feedback_import_report.md",
        REPORT_DIR / "mvp31_follow_up_decision_report.md",
        REPORT_DIR / "mvp31_security_boundary_report.md",
        REPORT_DIR / "mvp31_next_product_step_report.md",
        REPORT_DIR / "mvp31_validator_quality_report.md",
        REPORT_DIR / "mvp31_acceptance_report.md",
        REPORT_DIR / "mvp31_validator_wall_review.md",
    ]
    for path in required_models + required_reports:
        ensure_exists(path)

    acceptance = read_text(REPORT_DIR / "mvp31_acceptance_report.md")
    for marker in [
        "DEMO_SESSION_CAPTURE_REVIEW_LOOP_READY",
        "PASS_WITH_MANUAL_SESSION_CAPTURE_AND_OPTIONAL_GATED_IMPORT",
        "DEMO_SESSION_CAPTURE_WORKSPACE_READY",
        "EXTERNAL_REVIEW_FEEDBACK_LOOP_READY",
        "REVIEWER_PERSONA_SESSION_READY",
        "FEEDBACK_PACKET_DRAFT_READY",
        "OPTIONAL_FEEDBACK_IMPORT_GATED",
        "TOKEN_IN_MEMORY_ONLY",
        "NO_AUTOMATED_OUTREACH",
        "NO_FAKE_REVIEWER_RESULTS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_RELEASE_REVIEW_METRICS_AND_SIGNAL_DASHBOARD",
    ]:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    index = read_text(DIST_DIR / "index.html")
    section_match = re.search(
        r'<details[^>]*id="mvp31-demo-session-capture-review-loop".*?</details>',
        index,
        re.S,
    )
    if not section_match:
        fail("Missing MVP-31 demo session capture section block in index.html")
    section_html = section_match.group(0)
    for marker in [
        "MVP-31",
        "DEMO SESSION CAPTURE WORKSPACE",
        "EXTERNAL REVIEW FEEDBACK LOOP",
        "REVIEWER PERSONA SESSION",
        "DEMO SESSION NOTES",
        "FEEDBACK PACKET DRAFT",
        "OPTIONAL FEEDBACK IMPORT GATED",
        "TOKEN IN MEMORY ONLY",
        "NO AUTOMATED OUTREACH",
        "NO FAKE REVIEWER RESULTS",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_RELEASE_REVIEW_METRICS_AND_SIGNAL_DASHBOARD",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(section_html, marker, f"section marker {marker}")

    for label in [
        "Deploy",
        "Merge",
        "Push",
        "Create PR",
        "Execute",
        "Approve",
        "Start Automation",
        "Apply Migration",
        "Enable Writes",
        "Enable Feedback Persistence",
        "Submit to Supabase",
        "Save to Database",
        "Send Email",
        "Email Reviewer",
        "Auto" " Follow-Up",
        "Start" " Outreach",
        "Automate" " Review",
    ]:
        if label in section_html:
            fail(f"Forbidden enabled button label in MVP-31 section: {label}")

    for label in [
        "Copy Session Summary",
        "Copy Feedback Packet",
        "Copy Follow-Up Plan",
        "Copy Follow-Up Summary",
        "Use Token In Memory",
        "Clear Token",
        "Check Feedback Endpoint Status",
        "Submit Feedback Packet Manually",
    ]:
        assert_contains(section_html, label, f"allowed button label {label}")

    for path in required_models:
        walk_json_flags(path)

    model = json.loads(read_text(DIST_DIR / "mvp31_demo_session_capture_review_loop_model.json"))
    for key in [
        "demo_session_capture_ready",
        "external_review_loop_ready",
        "reviewer_persona_selection_ready",
        "feedback_packet_draft_ready",
        "optional_feedback_import_supported",
        "optional_feedback_import_default",
        "requires_explicit_operator_action",
        "token_in_memory_only",
        "safe_demo_mode",
        "no_fake_reviewer_results",
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "email_sending_enabled",
        "automation_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "deploy_merge_push_controls_enabled",
    ]:
        if key not in model:
            fail(f"Missing model field: {key}")
    if model["demo_session_capture_ready"] is not True or model["external_review_loop_ready"] is not True:
        fail("MVP-31 model readiness flags are not true")
    for key in [
        "requires_explicit_operator_action",
        "token_in_memory_only",
        "safe_demo_mode",
        "no_fake_reviewer_results",
    ]:
        if model[key] is not True:
            fail(f"MVP-31 model safety/readiness flag not true: {key}")
    if model["optional_feedback_import_default"] is not False:
        fail("MVP-31 model optional_feedback_import_default is not false")
    for key in [
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "email_sending_enabled",
        "automation_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "deploy_merge_push_controls_enabled",
    ]:
        if model[key] is not False:
            fail(f"MVP-31 model forbidden flag not false: {key}")

    renderer = read_text(ROOT / "13_web_dashboard" / "dashboard_renderer.py")
    for marker in [
        "MVP-31",
        "DEMO SESSION CAPTURE WORKSPACE",
        "EXTERNAL REVIEW FEEDBACK LOOP",
        "REVIEWER PERSONA SESSION",
        "DEMO SESSION NOTES",
        "FEEDBACK PACKET DRAFT",
        "OPTIONAL FEEDBACK IMPORT GATED",
        "TOKEN IN MEMORY ONLY",
        "NO AUTOMATED OUTREACH",
        "NO FAKE REVIEWER RESULTS",
        "NEXT_STEP_BUILD_RELEASE_REVIEW_METRICS_AND_SIGNAL_DASHBOARD",
    ]:
        assert_contains(renderer, marker, f"renderer marker {marker}")

    runtime_files = [
        ROOT / "13_web_dashboard" / "static" / "dashboard.js",
        DIST_DIR / "static" / "dashboard.js",
        DIST_DIR / "index.html",
        DIST_DIR / "print.html",
    ]
    forbidden_runtime_tokens = [
        "local" "Storage.setItem",
        "session" "Storage.setItem",
        "document" ".cookie =",
        "indexed" "DB.open",
        "create" "Client(",
        "supabase" ".createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
        "sendE" "mail(",
        "mail" "to:",
        "email" "js",
    ]
    for path in runtime_files:
        content = read_text(path)
        for token in forbidden_runtime_tokens:
            if token in content:
                fail(f"Forbidden runtime token in {path}: {token}")

    dashboard_js = read_text(ROOT / "13_web_dashboard" / "static" / "dashboard.js")
    for token in [
        '"/api/feedback?action=import"',
        'fetch("/api/feedback")',
        'mvp31-submit-feedback-packet',
        'mvp31-use-token-memory',
        'mvp31-clear-token',
        'mvp31-check-feedback-endpoint',
        'mvp31-feedback-token',
        'tokenMemory',
        'location.hostname === "127.0.0.1"',
    ]:
        assert_contains(dashboard_js, token, f"dashboard.js token {token}")
    for token in [
        'create' 'Client("',
        "supabase" ".createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
    ]:
        if token in dashboard_js:
            fail(f"Forbidden runtime token in dashboard.js: {token}")

    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, SCRIPT_DIR, ROOT / "netlify" / "functions"]
    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
                continue
            content = read_text(path)
            if "scripts/validate_" in str(path):
                continue
            if "sb_secret_" in content or "postgresql://postgres:" in content or "SUPABASE_SERVICE_ROLE_KEY=sb_" in content:
                fail(f"Forbidden secret pattern in {path}")

    print("MVP31_DEMO_SESSION_CAPTURE_REVIEW_LOOP_VALIDATION_PASS")


if __name__ == "__main__":
    main()
