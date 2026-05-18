#!/usr/bin/env python3
"""Context-aware live-page control scan for MVP-41 stabilization."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import scan_text_for_dangerous_controls


FILES = [
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "print.html",
    ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js",
    ROOT / "13_web_dashboard" / "static" / "dashboard.js",
    ROOT / "13_web_dashboard" / "dashboard_renderer.py",
    ROOT / "13_web_dashboard" / "dist" / "dashboard_data.json",
    ROOT / "13_web_dashboard" / "dist" / "status_snapshot.json",
    ROOT / "09_exports" / "mvp_product_track" / "mvp41_production_verification_report.md",
    ROOT / "09_exports" / "mvp_product_track" / "validation_stabilization_after_mvp41_report.md",
]

OPTIONAL_FILES = [
    ROOT / "09_exports" / "mvp_product_track" / "live_page_assessment_after_mvp41_report.md",
]

INDEX_MARKERS = [
    "The Agent Command Center",
    "MVP-41",
    "CONTROLLED REVIEWER RESPONSE INTAKE BLUEPRINT",
    "NO PUBLIC ENDPOINT",
    "NO LIVE INTAKE",
    "NO PUBLIC WRITES",
    "NO TOKEN INPUT",
    "SERVICE ROLE NOT USED",
    "NOT_READY_FOR_REAL_AUTOMATION",
]

STABILIZATION_MARKERS = [
    "VALIDATION_STABILIZATION_AFTER_MVP41_COMPLETE",
    "CONTEXT_AWARE_CONTROL_SCAN_ADDED",
    "WORD_ONLY_DEPLOY_SCAN_REMOVED",
    "SAFETY_DENIAL_LANGUAGE_ALLOWED",
    "DANGEROUS_RUNTIME_CONTROLS_STILL_BLOCKED",
    "LIVE_PAGE_CONTEXT_AWARE_CONTROL_SCAN_READY",
    "LATEST_PRODUCTION_VERIFIED_MVP_41",
    "NO_PUBLIC_ENDPOINT_ADDED",
    "NO_LIVE_INTAKE_ADDED",
    "NO_PUBLIC_WRITES_ADDED",
    "NO_TOKEN_INPUT_ADDED",
    "NO_EMAIL_OR_REVIEWER_CONTACT_ADDED",
    "NO_AUTOMATION_ADDED",
    "NO_DEPLOY_CONTROLS_ADDED",
    "NEXT_STEP_MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN",
]


def main() -> None:
    for path in FILES:
        if not path.exists():
            raise SystemExit(f"SCAN_FILE_MISSING: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8", errors="replace")
        findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
        if findings:
            raise SystemExit(f"DANGEROUS_CONTROL_FINDINGS: {findings}")

    for path in OPTIONAL_FILES:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
            if findings:
                raise SystemExit(f"DANGEROUS_CONTROL_FINDINGS: {findings}")

    index = (ROOT / "13_web_dashboard" / "dist" / "index.html").read_text(encoding="utf-8", errors="replace")
    for marker in INDEX_MARKERS:
        if marker not in index:
            raise SystemExit(f"INDEX_MARKER_MISSING: {marker}")

    stabilization_report = ROOT / "09_exports" / "mvp_product_track" / "validation_stabilization_after_mvp41_report.md"
    text = stabilization_report.read_text(encoding="utf-8", errors="replace")
    for marker in STABILIZATION_MARKERS:
        if marker not in text:
            raise SystemExit(f"STABILIZATION_REPORT_MARKER_MISSING: {marker}")

    print("LIVE_PAGE_CONTEXT_AWARE_CONTROL_SCAN_PASS")


if __name__ == "__main__":
    main()
