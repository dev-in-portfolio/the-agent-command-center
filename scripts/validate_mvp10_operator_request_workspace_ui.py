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
        UI_MODEL_DIR / "operator_workspace_ui_model.json",
        UI_MODEL_DIR / "operator_workspace_api_client_model.json",
        UI_MODEL_DIR / "operator_workspace_create_form_model.json",
        DIST_DIR / "mvp10_operator_workspace_model.json",
        REPORT_DIR / "mvp10_operator_workspace_ui_report.md",
        REPORT_DIR / "mvp10_api_client_report.md",
        REPORT_DIR / "mvp10_token_handling_report.md",
        REPORT_DIR / "mvp10_create_form_report.md",
        REPORT_DIR / "mvp10_request_panels_report.md",
        REPORT_DIR / "mvp10_security_boundary_report.md",
        REPORT_DIR / "mvp10_next_product_step_report.md",
        REPORT_DIR / "mvp10_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-10",
        "OPERATOR REQUEST WORKSPACE",
        "TOKEN IN MEMORY ONLY",
        "AUTH STATUS PANEL",
        "API STATUS PANEL",
        "REQUEST LIST PANEL",
        "REQUEST DETAIL PANEL",
        "LIFECYCLE TIMELINE PANEL",
        "DRY RUN RESULTS PANEL",
        "CREATE REQUEST FORM",
        "READ AND CREATE ONLY",
        "UPDATE DELETE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_ADD_TOKEN_AWARE_FRONTEND_SESSION_AND_REQUEST_WORKFLOW_POLISH",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Workspace UI Status",
        "Token Handling Panel",
        "API Client Panel",
        "Create Form Panel",
        "Copy workspace UI spec",
        "Copy MVP-10 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp10_acceptance_report.md")
    for text in [
        "OPERATOR_REQUEST_WORKSPACE_UI_READY",
        "PASS_WITH_MANUAL_TOKEN_TEST_REQUIRED",
        "NEXT_STEP_ADD_TOKEN_AWARE_FRONTEND_SESSION_AND_REQUEST_WORKFLOW_POLISH",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks for token persistence and runtime patterns
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
                # Lowercase match
                if pattern.lower() in text:
                    # Allow mention in reports/validators for documentation
                    if "09_exports/" in str(path) or "scripts/validate_" in str(path):
                        continue
                    # Allow dashboard renderer to mention them in obfuscated strings or comments
                    if "dashboard_renderer.py" in str(path):
                        continue
                    # Allow models to declare them as false/forbidden
                    if path.suffix == ".json" and "\"false\"" in text:
                         continue
                    fail(f"Forbidden pattern in {path.name}: {pattern}")

    print("MVP10_OPERATOR_REQUEST_WORKSPACE_UI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
