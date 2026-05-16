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
        UI_MODEL_DIR / "request_list_ui_model.json",
        UI_MODEL_DIR / "request_detail_ui_model.json",
        UI_MODEL_DIR / "lifecycle_timeline_ui_model.json",
        UI_MODEL_DIR / "create_verification_harness_model.json",
        DIST_DIR / "mvp9_request_detail_lifecycle_model.json",
        REPORT_DIR / "mvp9_request_list_ui_report.md",
        REPORT_DIR / "mvp9_request_detail_ui_report.md",
        REPORT_DIR / "mvp9_lifecycle_timeline_report.md",
        REPORT_DIR / "mvp9_create_verification_harness_report.md",
        REPORT_DIR / "mvp9_security_boundary_report.md",
        REPORT_DIR / "mvp9_next_product_step_report.md",
        REPORT_DIR / "mvp9_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-9",
        "REQUEST LIST UI MODEL",
        "REQUEST DETAIL UI MODEL",
        "LIFECYCLE TIMELINE",
        "USER-OWNED REQUESTS ONLY",
        "RLS-ENFORCED READS",
        "CREATE VERIFICATION HARNESS",
        "UPDATE DELETE EXECUTE BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_OPERATOR_REQUEST_WORKSPACE_UI",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Request List UI Panel",
        "Request Detail UI Panel",
        "Lifecycle Timeline Panel",
        "Dry Run Results Panel",
        "Create Verification Harness Panel",
        "Security Boundary Panel",
        "Next Product Decision Panel",
        "Copy request list UI spec",
        "Copy request detail UI spec",
        "Copy lifecycle timeline spec",
        "Copy create verification harness spec",
        "Copy MVP-9 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp9_acceptance_report.md")
    for text in [
        "REQUEST_DETAIL_LIFECYCLE_TIMELINE_READY",
        "PASS_WITH_CREATE_VERIFICATION_OPTIONAL",
        "NEXT_STEP_BUILD_OPERATOR_REQUEST_WORKSPACE_UI",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks
    scan_roots = [UI_MODEL_DIR, REPORT_DIR]
    forbidden = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
    ]

    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            text = read_text(path).lower()
            for pattern in forbidden:
                if pattern.lower() in text:
                    fail(f"Forbidden pattern in {path.name}: {pattern}")

    print("MVP9_REQUEST_DETAIL_LIFECYCLE_TIMELINE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
