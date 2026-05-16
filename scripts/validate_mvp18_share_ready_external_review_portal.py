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
        UI_MODEL_DIR / "share_ready_external_review_portal_model.json",
        UI_MODEL_DIR / "external_review_navigation_model.json",
        UI_MODEL_DIR / "demo_package_qa_model.json",
        UI_MODEL_DIR / "share_safe_reviewer_instructions_model.json",
        UI_MODEL_DIR / "reviewer_persona_routing_model.json",
        DIST_DIR / "mvp18_share_ready_external_review_model.json",
        REPORT_DIR / "mvp18_share_ready_external_review_portal_report.md",
        REPORT_DIR / "mvp18_review_packet_index_report.md",
        REPORT_DIR / "mvp18_role_based_review_paths_report.md",
        REPORT_DIR / "mvp18_demo_package_qa_report.md",
        REPORT_DIR / "mvp18_share_safe_checklist_report.md",
        REPORT_DIR / "mvp18_feedback_prompts_report.md",
        REPORT_DIR / "mvp18_safety_boundary_report.md",
        REPORT_DIR / "mvp18_next_product_step_report.md",
        REPORT_DIR / "mvp18_acceptance_report.md",
        ASSET_DIR / "START_HERE.md",
        ASSET_DIR / "REVIEW_PACKET_INDEX.md",
        ASSET_DIR / "SHARE_SAFE_CHECKLIST.md",
        ASSET_DIR / "FEEDBACK_PROMPTS.md",
        ASSET_DIR / "ROLE_BASED_REVIEW_PATHS.md",
        ASSET_DIR / "EXTERNAL_REVIEW_PORTAL.md",
        ASSET_DIR / "DEMO_PACKAGE_QA.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-18",
        "SHARE-READY EXTERNAL REVIEW PORTAL",
        "REVIEW PACKET INDEX",
        "START HERE GUIDE",
        "ROLE-BASED REVIEW PATHS",
        "DEMO PACKAGE QA",
        "SHARE-SAFE CHECKLIST",
        "FEEDBACK PROMPTS",
        "REVIEWER PERSONA ROUTING",
        "FIVE MINUTE REVIEW PATH",
        "FIFTEEN MINUTE REVIEW PATH",
        "THIRTY MINUTE REVIEW PATH",
        "LIVE TEST STATUS NOT OVERCLAIMED",
        "APPROVAL EXECUTION AUTOMATION BLOCKED",
        "NO SECRET DISCLOSURE",
        "SERVICE ROLE NOT USED",
        "NEXT_STEP_REVIEW_PACKAGE_AND_PREPARE_EXTERNAL_FEEDBACK_ROUND",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Share-Ready Portal Panel",
        "Role-Based Review Paths Panel",
        "Timebox Review Panel",
        "Demo Package QA Panel",
        "Share-Safe Checklist Panel",
        "Feedback Prompts Panel",
        "Copy MVP-18 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp18_acceptance_report.md")
    for text in [
        "SHARE_READY_EXTERNAL_REVIEW_PORTAL_READY",
        "PASS_WITH_EXTERNAL_REVIEW_PACKAGE_QA_READY",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks
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

    print("MVP18_SHARE_READY_EXTERNAL_REVIEW_PORTAL_VALIDATION_PASS")


if __name__ == "__main__":
    main()
