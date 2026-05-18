#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import scan_text_for_dangerous_controls

FAILURES = []

def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"  [FAIL] {message}")

def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def scan_text(path: Path, text: str) -> None:
    findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
    if findings:
        fail(f"{path.relative_to(ROOT)}: {findings}")

def main():
    index_path = ROOT / "13_web_dashboard" / "dist" / "index.html"
    js_path = ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js"
    report_path = ROOT / "09_exports" / "mvp_product_track" / "live_dashboard_usability_refactor_after_mvp41_report.md"

    check(index_path.exists(), "index.html exists")
    check(js_path.exists(), "dashboard JS exists")
    check(report_path.exists(), "usability report exists")

    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        check('id="view-welcome"' in text, "Welcome view exists")
        check('id="view-orientation"' in text, "“What the hell am I looking at?” view exists")
        check('id="view-status"' in text, "Current Status view exists")
        check('id="view-latest-mvp"' in text, "Latest Verified MVP view exists")
        check('id="view-demo"' in text, "External Review / Demo view exists")
        check('id="view-safety"' in text, "Safety Posture view exists")
        check('id="view-roadmap"' in text, "Roadmap / Next Step view exists")
        check('id="view-archive"' in text, "Archive / Full Audit Trail view exists")
        check('id="view-developer"' in text, "Developer / Validator View exists")
        
        check("MVP-41" in text, "MVP-41 still visible")
        
        if "MVP-42" in text:
            # ensure it's not claimed as verified
            check('Latest Verified MVP</h3><span class="badge pass">MVP-42' not in text, "MVP-42 is not claimed as production verified")
            
        check('id="view-archive" style="display: none;"' in text or 'id="view-archive" class="tab-pane"' in text, "Archive defaults collapsed or non-landing")
        
    if report_path.exists():
        text = report_path.read_text(encoding="utf-8")
        scan_text(report_path, text)

    # ensure no endpoint files added
    check(not (ROOT / "netlify" / "functions" / "live_endpoint.js").exists(), "no endpoint files added")
    
    if FAILURES:
        print("LIVE_DASHBOARD_USABILITY_AFTER_MVP41_VALIDATION_FAIL")
        sys.exit(1)
        
    print("LIVE_DASHBOARD_USABILITY_AFTER_MVP41_VALIDATION_PASS")

if __name__ == "__main__":
    main()
