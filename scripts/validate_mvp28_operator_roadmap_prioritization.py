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
        "operator_roadmap_prioritization_board_ready",
        "feedback_signals_to_roadmap_ready",
        "product_decision_lanes_ready",
        "priority_scoring_ready",
        "impact_effort_confidence_matrix_ready",
        "read_only_roadmap_workflow",
    ]
    for key in expected_true:
        if key in data and data[key] is not True:
            fail(f"{path.name} gate not true: {key}")

    expected_false = [
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
        UI_MODEL_DIR / "operator_roadmap_board_model.json",
        UI_MODEL_DIR / "roadmap_priority_scoring_model.json",
        UI_MODEL_DIR / "roadmap_lane_model.json",
        UI_MODEL_DIR / "feedback_request_roadmap_link_model.json",
        DIST_DIR / "mvp28_operator_roadmap_prioritization_model.json",
        REPORT_DIR / "mvp28_operator_roadmap_report.md",
        REPORT_DIR / "mvp28_priority_scoring_report.md",
        REPORT_DIR / "mvp28_roadmap_lanes_report.md",
        REPORT_DIR / "mvp28_feedback_request_link_report.md",
        REPORT_DIR / "mvp28_security_boundary_report.md",
        REPORT_DIR / "mvp28_next_product_step_report.md",
        REPORT_DIR / "mvp28_validator_quality_report.md",
        REPORT_DIR / "mvp28_acceptance_report.md",
        REPORT_DIR / "mvp28_validator_wall_review.md",
    ]
    for path in required_files:
        ensure_exists(path)

    acceptance = read_text(REPORT_DIR / "mvp28_acceptance_report.md")
    for marker in [
        "OPERATOR_ROADMAP_PRIORITIZATION_BOARD_READY",
        "PASS_WITH_READ_ONLY_ROADMAP_WORKFLOW",
        "FEEDBACK_SIGNALS_TO_ROADMAP_READY",
        "PRODUCT_DECISION_LANES_READY",
        "PRIORITY_SCORING_READY",
        "IMPACT_EFFORT_CONFIDENCE_MATRIX_READY",
        "READ_ONLY_ROADMAP_WORKFLOW",
        "SERVICE ROLE NOT USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_GUIDED_PRODUCT_DEMO_CONTROL_ROOM",
    ]:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    index = read_text(DIST_DIR / "index.html")
    for marker in [
        "MVP-28",
        "OPERATOR ROADMAP PRIORITIZATION BOARD",
        "FEEDBACK SIGNALS TO ROADMAP",
        "PRODUCT DECISION LANES",
        "PRIORITY SCORING",
        "IMPACT EFFORT CONFIDENCE MATRIX",
        "READ ONLY ROADMAP WORKFLOW",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_GUIDED_PRODUCT_DEMO_CONTROL_ROOM",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(index, marker, f"index marker {marker}")

    for path in [
        UI_MODEL_DIR / "operator_roadmap_board_model.json",
        UI_MODEL_DIR / "roadmap_priority_scoring_model.json",
        UI_MODEL_DIR / "roadmap_lane_model.json",
        UI_MODEL_DIR / "feedback_request_roadmap_link_model.json",
        DIST_DIR / "mvp28_operator_roadmap_prioritization_model.json",
    ]:
        walk_json_flags(path)

    renderer = read_text(ROOT / "13_web_dashboard" / "dashboard_renderer.py")
    for marker in [
        "MVP-28",
        "OPERATOR ROADMAP PRIORITIZATION BOARD",
        "FEEDBACK SIGNALS TO ROADMAP",
        "PRODUCT DECISION LANES",
        "PRIORITY SCORING",
        "IMPACT EFFORT CONFIDENCE MATRIX",
        "READ ONLY ROADMAP WORKFLOW",
        "NEXT_STEP_BUILD_GUIDED_PRODUCT_DEMO_CONTROL_ROOM",
    ]:
        assert_contains(renderer, marker, f"renderer marker {marker}")

    for path in [
        UI_MODEL_DIR / "operator_roadmap_board_model.json",
        UI_MODEL_DIR / "roadmap_priority_scoring_model.json",
        UI_MODEL_DIR / "roadmap_lane_model.json",
        UI_MODEL_DIR / "feedback_request_roadmap_link_model.json",
        DIST_DIR / "mvp28_operator_roadmap_prioritization_model.json",
    ]:
        content = read_text(path)
        if "manual" not in content.lower():
            fail(f"Manual roadmap posture missing in {path}")

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

    print("MVP28_OPERATOR_ROADMAP_PRIORITIZATION_VALIDATION_PASS")


if __name__ == "__main__":
    main()
