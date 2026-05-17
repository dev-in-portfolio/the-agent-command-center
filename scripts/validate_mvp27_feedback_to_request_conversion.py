#!/usr/bin/env python3
import json
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
        "feedback_to_request_conversion_workspace_ready",
        "request_draft_from_feedback_ready",
        "decision_to_request_payload_preview_ready",
        "controlled_request_create_optional",
        "token_in_memory_only",
        "request_writes_server_gated",
        "manual_click_required_for_create",
    ]
    for key in expected_true:
        if key in data and data[key] is not True:
            fail(f"{path.name} gate not true: {key}")

    expected_false = [
        "automatic_request_creation",
        "service_role_used",
        "browser_direct_supabase_calls",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "automation_enabled",
    ]
    for key in expected_false:
        if key in data and data[key] is not False:
            fail(f"{path.name} forbidden flag not false: {key}")


def main():
    required_files = [
        UI_MODEL_DIR / "feedback_to_request_conversion_workspace_model.json",
        UI_MODEL_DIR / "request_draft_from_feedback_model.json",
        UI_MODEL_DIR / "feedback_decision_to_request_payload_model.json",
        UI_MODEL_DIR / "controlled_request_creation_from_feedback_model.json",
        DIST_DIR / "mvp27_feedback_to_request_conversion_model.json",
        REPORT_DIR / "mvp27_feedback_to_request_workspace_report.md",
        REPORT_DIR / "mvp27_request_draft_report.md",
        REPORT_DIR / "mvp27_request_payload_preview_report.md",
        REPORT_DIR / "mvp27_controlled_request_creation_report.md",
        REPORT_DIR / "mvp27_security_boundary_report.md",
        REPORT_DIR / "mvp27_next_product_step_report.md",
        REPORT_DIR / "mvp27_validator_quality_report.md",
        REPORT_DIR / "mvp27_acceptance_report.md",
        REPORT_DIR / "mvp27_validator_wall_review.md",
    ]
    for path in required_files:
        ensure_exists(path)

    acceptance = read_text(REPORT_DIR / "mvp27_acceptance_report.md")
    for marker in [
        "FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE_READY",
        "PASS_WITH_OPTIONAL_SERVER_GATED_REQUEST_CREATE",
        "REQUEST_DRAFT_FROM_FEEDBACK_READY",
        "DECISION_TO_REQUEST_PAYLOAD_PREVIEW_READY",
        "CONTROLLED_REQUEST_CREATE_OPTIONAL",
        "TOKEN_IN_MEMORY_ONLY",
        "REQUEST_WRITES_SERVER_GATED",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_OPERATOR_ROADMAP_PRIORITIZATION_BOARD",
    ]:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    index = read_text(DIST_DIR / "index.html")
    for marker in [
        "MVP-27",
        "FEEDBACK TO REQUEST CONVERSION WORKSPACE",
        "REQUEST DRAFT FROM FEEDBACK",
        "DECISION TO REQUEST PAYLOAD PREVIEW",
        "CONTROLLED REQUEST CREATE OPTIONAL",
        "TOKEN IN MEMORY ONLY",
        "REQUEST WRITES SERVER GATED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_OPERATOR_ROADMAP_PRIORITIZATION_BOARD",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(index, marker, f"index marker {marker}")

    for path in [
        UI_MODEL_DIR / "feedback_to_request_conversion_workspace_model.json",
        UI_MODEL_DIR / "request_draft_from_feedback_model.json",
        UI_MODEL_DIR / "feedback_decision_to_request_payload_model.json",
        UI_MODEL_DIR / "controlled_request_creation_from_feedback_model.json",
        DIST_DIR / "mvp27_feedback_to_request_conversion_model.json",
    ]:
        walk_json_flags(path)

    renderer = read_text(ROOT / "13_web_dashboard" / "dashboard_renderer.py")
    for marker in [
        "MVP-27",
        "FEEDBACK TO REQUEST CONVERSION WORKSPACE",
        "REQUEST DRAFT FROM FEEDBACK",
        "DECISION TO REQUEST PAYLOAD PREVIEW",
        "CONTROLLED REQUEST CREATE OPTIONAL",
        "TOKEN IN MEMORY ONLY",
        "REQUEST WRITES SERVER GATED",
        "NEXT_STEP_BUILD_OPERATOR_ROADMAP_PRIORITIZATION_BOARD",
    ]:
        assert_contains(renderer, marker, f"renderer marker {marker}")

    for path in [
        UI_MODEL_DIR / "feedback_to_request_conversion_workspace_model.json",
        UI_MODEL_DIR / "feedback_decision_to_request_payload_model.json",
        UI_MODEL_DIR / "controlled_request_creation_from_feedback_model.json",
        DIST_DIR / "mvp27_feedback_to_request_conversion_model.json",
        REPORT_DIR / "mvp27_request_payload_preview_report.md",
    ]:
        content = read_text(path)
        assert_contains(content, "POST /api/requests?action=create", f"manual create endpoint in {path.name}")
        if "manual" not in content.lower():
            fail(f"Manual request-create posture missing in {path}")

    runtime_files = [
        ROOT / "13_web_dashboard" / "static" / "dashboard.js",
        DIST_DIR / "static" / "dashboard.js",
        DIST_DIR / "index.html",
        DIST_DIR / "print.html",
    ]
    forbidden_runtime_tokens = [
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
        "fetch('/api/requests?action=create'",
        'fetch("/api/requests?action=create"',
        "axios.post('/api/requests?action=create'",
        'axios.post("/api/requests?action=create"',
        "window.addEventListener('load'",
        'window.addEventListener("load"',
    ]
    for path in runtime_files:
        content = read_text(path)
        for token in forbidden_runtime_tokens:
            if token in content:
                fail(f"Forbidden runtime token in {path}: {token}")

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

    print("MVP27_FEEDBACK_TO_REQUEST_CONVERSION_VALIDATION_PASS")


if __name__ == "__main__":
    main()
