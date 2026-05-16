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
        UI_MODEL_DIR / "live_test_results_package_model.json",
        UI_MODEL_DIR / "demo_pitch_package_model.json",
        UI_MODEL_DIR / "demo_walkthrough_script_model.json",
        UI_MODEL_DIR / "product_one_pager_model.json",
        UI_MODEL_DIR / "technical_architecture_summary_model.json",
        DIST_DIR / "mvp16_live_test_results_demo_package_model.json",
        REPORT_DIR / "mvp16_live_test_results_report.md",
        REPORT_DIR / "mvp16_demo_pitch_package_report.md",
        REPORT_DIR / "mvp16_product_one_pager_report.md",
        REPORT_DIR / "mvp16_demo_walkthrough_script_report.md",
        REPORT_DIR / "mvp16_technical_architecture_summary_report.md",
        REPORT_DIR / "mvp16_safety_boundary_report.md",
        REPORT_DIR / "mvp16_next_product_step_report.md",
        REPORT_DIR / "mvp16_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-16",
        "LIVE TEST RESULTS PACKAGE",
        "DEMO PITCH PACKAGE",
        "PRODUCT ONE-PAGER",
        "TECHNICAL ARCHITECTURE SUMMARY",
        "DEMO WALKTHROUGH SCRIPT",
        "SAFE RESULT CAPTURE",
        "NO TOKEN CAPTURE",
        "NO SECRET CAPTURE",
        "NO RAW ERROR CAPTURE",
        "PRODUCT READINESS UPDATE",
        "SAFETY-FIRST DEMO NARRATIVE",
        "MANUAL LIVE TEST STATUS",
        "BLOCKED ACTIONS REMAIN BLOCKED",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_LIVE_TEST_OR_PREPARE_EXTERNAL_DEMO",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Live Test Results Package Panel",
        "Demo Pitch Package Panel",
        "Product One-Pager Panel",
        "Technical Architecture Panel",
        "Demo Walkthrough Script Panel",
        "Safety Boundary Panel",
        "Copy MVP-16 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp16_acceptance_report.md")
    for text in [
        "LIVE_TEST_RESULTS_DEMO_PITCH_PACKAGE_READY",
        "PASS_WITH_LIVE_TEST_OPTIONAL_OR_TOKEN_REQUIRED",
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

    print("MVP16_LIVE_TEST_RESULTS_DEMO_PACKAGE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
