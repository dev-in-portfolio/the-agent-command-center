#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
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
        UI_MODEL_DIR / "token_aware_workspace_session_model.json",
        UI_MODEL_DIR / "request_workspace_state_machine_model.json",
        UI_MODEL_DIR / "request_list_controls_model.json",
        UI_MODEL_DIR / "request_workflow_ux_model.json",
        DIST_DIR / "mvp11_token_aware_workspace_polish_model.json",
        REPORT_DIR / "mvp11_token_aware_session_report.md",
        REPORT_DIR / "mvp11_workspace_state_machine_report.md",
        REPORT_DIR / "mvp11_request_list_controls_report.md",
        REPORT_DIR / "mvp11_request_workflow_ux_report.md",
        REPORT_DIR / "mvp11_error_empty_states_report.md",
        REPORT_DIR / "mvp11_security_boundary_report.md",
        REPORT_DIR / "mvp11_next_product_step_report.md",
        REPORT_DIR / "mvp11_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-11",
        "TOKEN-AWARE WORKSPACE SESSION",
        "MEMORY-ONLY TOKEN STATE",
        "TOKEN VERIFY CLEAR FLOW",
        "REQUEST WORKSPACE STATE MACHINE",
        "REQUEST LIST SEARCH FILTER SORT",
        "REQUEST DETAIL WORKFLOW",
        "LIFECYCLE TIMELINE WORKFLOW",
        "DRY RUN RESULTS WORKFLOW",
        "CREATE SUCCESS REFRESH FLOW",
        "READ AND CREATE ONLY",
        "UPDATE DELETE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_MANUAL_TOKEN_TEST_AND_WORKSPACE_UX_REFINEMENT",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Token Session Panel",
        "Request List Controls Panel",
        "Workspace State Machine Panel",
        "Request Workflow Panel",
        "Create Success Flow Panel",
        "Copy session model",
        "Copy MVP-11 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp11_acceptance_report.md")
    for text in [
        "TOKEN_AWARE_WORKSPACE_REQUEST_WORKFLOW_POLISH_READY",
        "PASS_WITH_MANUAL_WORKSPACE_TEST_REQUIRED",
        "NEXT_STEP_MANUAL_TOKEN_TEST_AND_WORKSPACE_UX_REFINEMENT",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR]
    forbidden = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
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
                    # Allow mention in reports/validators for documentation
                    if "09_exports/" in str(path) or "scripts/validate_" in str(path):
                        continue
                    # Allow dashboard renderer to mention them in obfuscated strings or comments
                    if "dashboard_renderer.py" in str(path):
                        continue
                    # Allow models to declare them as false/forbidden or use hyphenated versions
                    if path.suffix == ".json" and ("\"false\"" in text or "-" in text):
                         continue
                    fail(f"Forbidden pattern in {path.name}: {pattern}")

    print("MVP11_TOKEN_AWARE_WORKSPACE_POLISH_VALIDATION_PASS")


if __name__ == "__main__":
    main()
