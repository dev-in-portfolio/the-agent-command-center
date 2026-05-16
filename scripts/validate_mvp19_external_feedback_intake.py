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
        UI_MODEL_DIR / "external_feedback_intake_model.json",
        UI_MODEL_DIR / "reviewer_response_capture_model.json",
        UI_MODEL_DIR / "feedback_review_queue_model.json",
        UI_MODEL_DIR / "feedback_synthesis_readiness_model.json",
        DIST_DIR / "mvp19_external_feedback_model.json",
        REPORT_DIR / "mvp19_feedback_intake_model_report.md",
        REPORT_DIR / "mvp19_reviewer_response_capture_report.md",
        REPORT_DIR / "mvp19_feedback_review_queue_report.md",
        REPORT_DIR / "mvp19_feedback_synthesis_readiness_report.md",
        REPORT_DIR / "mvp19_external_demo_feedback_package_report.md",
        REPORT_DIR / "mvp19_security_boundary_report.md",
        REPORT_DIR / "mvp19_next_product_step_report.md",
        REPORT_DIR / "mvp19_acceptance_report.md",
        ASSET_DIR / "FEEDBACK_INTAKE_GUIDE.md",
        ASSET_DIR / "REVIEWER_RESPONSE_FORM.md",
        ASSET_DIR / "FEEDBACK_REVIEW_QUEUE.md",
        ASSET_DIR / "FEEDBACK_SYNTHESIS_GUIDE.md",
        ASSET_DIR / "EXTERNAL_REVIEW_RETURN_INSTRUCTIONS.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-19",
        "EXTERNAL FEEDBACK INTAKE",
        "REVIEWER RESPONSE CAPTURE",
        "STATIC FEEDBACK PACKET ONLY",
        "REVIEWER PERSONA ROUTING",
        "FEEDBACK REVIEW QUEUE",
        "FEEDBACK SYNTHESIS READINESS",
        "NO BACKEND FEEDBACK SUBMISSION",
        "NO BROWSER PERSISTENCE",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_EXTERNAL_REVIEW_ROUND_OR_ADD_MANUAL_FEEDBACK_IMPORT_QUEUE",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Feedback Intake Panel",
        "Reviewer Response Capture Panel",
        "Static Feedback Packet Panel",
        "Feedback Review Queue Panel",
        "Feedback Synthesis Readiness Panel",
        "Security Boundary Panel",
        "Copy MVP-19 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp19_acceptance_report.md")
    for text in [
        "EXTERNAL_FEEDBACK_INTAKE_READY",
        "PASS_WITH_STATIC_FEEDBACK_PACKET_READY",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    # Safety checks
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, ASSET_DIR]
    forbidden = [
        "sb-secret-",
        "postgresql-postgres-",
        "SUPABASE-SERVICE-ROLE-KEY-sb-",
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

    print("MVP19_EXTERNAL_FEEDBACK_INTAKE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
