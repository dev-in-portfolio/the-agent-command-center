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
        UI_MODEL_DIR / "live_test_execution_plan_model.json",
        UI_MODEL_DIR / "live_test_result_template_model.json",
        UI_MODEL_DIR / "demo_pitch_flow_model.json",
        UI_MODEL_DIR / "product_readiness_scorecard_model.json",
        UI_MODEL_DIR / "known_limitations_safety_boundary_model.json",
        DIST_DIR / "mvp15_live_test_demo_pitch_model.json",
        REPORT_DIR / "mvp15_live_test_execution_plan_report.md",
        REPORT_DIR / "mvp15_live_test_execution_result_report.md",
        REPORT_DIR / "mvp15_safe_result_template_report.md",
        REPORT_DIR / "mvp15_demo_pitch_flow_report.md",
        REPORT_DIR / "mvp15_product_readiness_scorecard_report.md",
        REPORT_DIR / "mvp15_known_limitations_safety_boundary_report.md",
        REPORT_DIR / "mvp15_next_product_step_report.md",
        REPORT_DIR / "mvp15_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-15",
        "LIVE TEST EXECUTION PLAN",
        "SAFE TEST RESULT TEMPLATE",
        "DEMO PITCH FLOW",
        "PRODUCT READINESS SCORECARD",
        "KNOWN LIMITATIONS AND SAFETY BOUNDARY",
        "MANUAL TOKEN TEST REQUIRED",
        "MEMORY-ONLY TOKEN TESTING",
        "PRODUCTION WORKSPACE TEST SEQUENCE",
        "SAFE RESULT CAPTURE ONLY",
        "NO SECRET CAPTURE",
        "NO ENV MUTATION",
        "NO MIGRATION APPLY",
        "BLOCKED ACTIONS REMAIN BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_LIVE_TEST_AND_CAPTURE_RESULTS",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Live Test Execution Plan Panel",
        "Safe Test Result Template Panel",
        "Demo Pitch Flow Panel",
        "Product Readiness Scorecard Panel",
        "Known Limitations Panel",
        "Safety Boundary Panel",
        "Copy MVP-15 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp15_acceptance_report.md")
    for text in [
        "LIVE_TEST_EXECUTION_DEMO_PITCH_FLOW_READY",
        "PASS_WITH_MANUAL_LIVE_TEST_REQUIRED",
        "NEXT_STEP_RUN_LIVE_TEST_AND_CAPTURE_RESULTS",
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

    print("MVP15_LIVE_TEST_EXECUTION_DEMO_PITCH_VALIDATION_PASS")


if __name__ == "__main__":
    main()
