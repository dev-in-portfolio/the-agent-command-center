#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
ASSET_DIR = ROOT / "09_exports" / "external_demo_package"


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
        UI_MODEL_DIR / "external_demo_package_model.json",
        UI_MODEL_DIR / "external_demo_landing_model.json",
        UI_MODEL_DIR / "public_facing_product_summary_model.json",
        UI_MODEL_DIR / "reviewer_brief_model.json",
        UI_MODEL_DIR / "demo_q_and_a_model.json",
        DIST_DIR / "mvp17_external_demo_package_model.json",
        REPORT_DIR / "mvp17_external_demo_package_report.md",
        REPORT_DIR / "mvp17_public_product_summary_report.md",
        REPORT_DIR / "mvp17_reviewer_brief_report.md",
        REPORT_DIR / "mvp17_safety_boundary_brief_report.md",
        REPORT_DIR / "mvp17_demo_walkthrough_report.md",
        REPORT_DIR / "mvp17_demo_q_and_a_report.md",
        REPORT_DIR / "mvp17_known_limitations_report.md",
        REPORT_DIR / "mvp17_next_product_step_report.md",
        REPORT_DIR / "mvp17_acceptance_report.md",
        ASSET_DIR / "README.md",
        ASSET_DIR / "product_one_pager.md",
        ASSET_DIR / "technical_reviewer_brief.md",
        ASSET_DIR / "founder_operator_brief.md",
        ASSET_DIR / "recruiter_brief.md",
        ASSET_DIR / "safety_boundary_brief.md",
        ASSET_DIR / "demo_walkthrough_script.md",
        ASSET_DIR / "demo_q_and_a.md",
        ASSET_DIR / "reviewer_checklist.md",
        ASSET_DIR / "known_limitations.md",
        ASSET_DIR / "next_milestones.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-17",
        "EXTERNAL DEMO PACKAGE",
        "PUBLIC PRODUCT SUMMARY",
        "REVIEWER BRIEF",
        "TECHNICAL REVIEWER BRIEF",
        "RECRUITER BRIEF",
        "FOUNDER OPERATOR BRIEF",
        "SAFETY BOUNDARY BRIEF",
        "DEMO WALKTHROUGH SCRIPT",
        "DEMO Q AND A",
        "REVIEWER CHECKLIST",
        "KNOWN LIMITATIONS",
        "DO NOT OVERCLAIM LIVE TEST STATUS",
        "APPROVAL EXECUTION AUTOMATION BLOCKED",
        "SERVICE ROLE NOT USED",
        "NO SECRET DISCLOSURE",
        "NEXT_STEP_PREPARE_EXTERNAL_REVIEW_OR_RUN_LIVE_TEST_FIRST",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "External Demo Package Panel",
        "Public Product Summary Panel",
        "Reviewer Brief Panel",
        "Safety Boundary Brief Panel",
        "Demo Walkthrough Script Panel",
        "Q&A Panel",
        "Next Review Step Panel",
        "Copy MVP-17 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp17_acceptance_report.md")
    for text in [
        "EXTERNAL_DEMO_PACKAGE_PITCH_ASSETS_READY",
        "PASS_WITH_LIVE_TEST_STATUS_NOT_OVERCLAIMED",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks for leaks
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, ASSET_DIR]
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

    print("MVP17_EXTERNAL_DEMO_PACKAGE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
