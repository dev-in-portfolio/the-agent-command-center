#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FAILURES = []

def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"  [FAIL] {message}")

def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def main():
    report_dir = ROOT / "09_exports" / "mvp_product_track"
    reports = list(report_dir.glob("mvp*_production_verification_report.md"))
    
    max_mvp = 0
    for r in reports:
        filename = r.name
        match = re.search(r'mvp(\d+)', filename)
        if match:
            num = int(match.group(1))
            if num > max_mvp:
                max_mvp = num
    
    check(max_mvp > 0, "found production verification reports")
    latest_label = f"MVP-{max_mvp}"
    
    index_path = ROOT / "13_web_dashboard" / "dist" / "index.html"
    check(index_path.exists(), "index.html exists")
    
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        
        # Confirm Welcome page shows latest verified MVP dynamically
        # Using a simpler check to avoid f-string escaping hell
        welcome_marker = f'Latest production verified MVP</h3><span class="badge pass">{latest_label}'
        check(welcome_marker in text, f"Welcome page shows {latest_label}")
        
        # Confirm Current Status shows latest verified milestone dynamically
        status_marker = f"Latest verified milestone: {latest_label}"
        check(status_marker in text, f"Current Status shows {latest_label}")
        
        # Confirm Roadmap shows completed through latest verified MVP dynamically
        roadmap_marker = f"Completed through {latest_label}"
        check(roadmap_marker in text, f"Roadmap shows {latest_label}")
        
        # Confirm Latest MVP tab does not hardcode MVP-41 (if latest is higher)
        if max_mvp > 41:
            check("Latest Verified MVP</h2>\n      <summary>MVP-41" not in text, "Latest MVP tab does not hardcode MVP-41")
            
        # Confirm no runtime/backend behavior added
        check(not (ROOT / "netlify/functions/live_endpoint.js").exists(), "no endpoints added")
        
    renderer_path = ROOT / "13_web_dashboard" / "dashboard_renderer.py"
    if renderer_path.exists():
        renderer_text = renderer_path.read_text(encoding="utf-8")
        check("_get_latest_production_verified_mvp" in renderer_text, "dynamic logic helper exists")
        check("latest_mvp['label']" in renderer_text or 'latest_mvp["label"]' in renderer_text, "builders use dynamic label")

    if FAILURES:
        print("LIVE_DASHBOARD_DYNAMIC_LATEST_STATUS_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
        
    print("LIVE_DASHBOARD_DYNAMIC_LATEST_STATUS_VALIDATION_PASS")

if __name__ == "__main__":
    main()
