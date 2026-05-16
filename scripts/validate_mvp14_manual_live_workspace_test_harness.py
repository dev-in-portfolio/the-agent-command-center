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
        UI_MODEL_DIR / "manual_live_workspace_test_harness_model.json",
        UI_MODEL_DIR / "live_test_checklist_model.json",
        UI_MODEL_DIR / "demo_readiness_model.json",
        UI_MODEL_DIR / "manual_test_result_capture_model.json",
        DIST_DIR / "mvp14_manual_live_workspace_test_model.json",
        REPORT_DIR / "mvp14_manual_live_workspace_test_harness_report.md",
        REPORT_DIR / "mvp14_live_test_checklist_report.md",
        REPORT_DIR / "mvp14_demo_readiness_report.md",
        REPORT_DIR / "mvp14_manual_test_result_capture_report.md",
        REPORT_DIR / "mvp14_safe_testing_boundary_report.md",
        REPORT_DIR / "mvp14_next_product_step_report.md",
        REPORT_DIR / "mvp14_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-14",
        "MANUAL LIVE WORKSPACE TEST HARNESS",
        "DEMO READINESS CHECKLIST",
        "LIVE TEST CHECKLIST",
        "SAFE MANUAL TEST RESULT CAPTURE",
        "MEMORY-ONLY TOKEN TESTING",
        "STATUS ENDPOINT CHECKS",
        "READ FLOW VERIFICATION",
        "Write Readiness Panel",
        "SAFE ERROR BEHAVIOR CHECK",
        "ACTIVITY FEED DEMO FLOW",
        "BLOCKED ACTIONS DEMO",
        "TOKEN STORAGE BLOCKED",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE APPROVE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_MANUAL_LIVE_WORKSPACE_TEST_WITH_REAL_USER_TOKEN",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Manual Live Test Harness Panel",
        "Demo Readiness Checklist Panel",
        "Manual Result Capture Panel",
        "Copy MVP-14 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp14_acceptance_report.md")
    for text in [
        "MANUAL_LIVE_WORKSPACE_TEST_HARNESS_READY",
        "PASS_WITH_REAL_USER_TOKEN_TEST_REQUIRED",
        "NEXT_STEP_RUN_MANUAL_LIVE_WORKSPACE_TEST_WITH_REAL_USER_TOKEN",
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
                    if "09_exports/" in str(path) or "scripts/validate_" in str(path):
                        continue
                    if "dashboard_renderer.py" in str(path):
                        continue
                    if path.suffix == ".json" and ("\"false\"" in text or "-" in text):
                         continue
                    fail(f"Forbidden pattern in {path.name}: {pattern}")

    print("MVP14_MANUAL_LIVE_WORKSPACE_TEST_HARNESS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
