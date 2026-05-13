import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "13_web_dashboard" / "dist"

def check():
    if not DIST_DIR.exists():
        print("FAIL: dist directory missing")
        sys.exit(1)
        
    required_files = [
        "index.html",
        "print.html",
        "static/dashboard.js",
        "static/dashboard.css"
    ]
    
    for req in required_files:
        if not (DIST_DIR / req).exists():
            print(f"FAIL: Missing {req}")
            sys.exit(1)

    index_html = (DIST_DIR / "index.html").read_text()
    
    # Title and Hero checks
    if "<title>The Agent Command Center" not in index_html:
        print("FAIL: Title missing 'The Agent Command Center'")
        sys.exit(1)
        
    if "Local Operations Dashboard" in index_html:
        print("FAIL: Contains forbidden wording 'Local Operations Dashboard'")
        sys.exit(1)
        
    if "Interface Phase 3" in index_html:
        print("FAIL: Contains forbidden wording 'Interface Phase 3'")
        sys.exit(1)

    # Required Dashboard Content
    required_strings = [
        "Production-hosted",
        "Read-Only",
        "Roadmap Re-Anchor",
        "Original Phase 4 — Hosted / Production Dashboard Polish",
        "Static/inert",
        "DISABLED — SCHEMA PREVIEW ONLY"
    ]
    for s in required_strings:
        if s not in index_html:
            print(f"FAIL: Missing required string '{s}'")
            sys.exit(1)

    # Forbidden external and active patterns
    forbidden_patterns = [
        r'href="https?://(?!fonts)', # Allow local fonts if any, but restrict general external links if strictly applied. We just check basic external assets below.
        r'src="https?://',
        r'fetch\([\'"]https?://',
    ]
    
    dashboard_js = (DIST_DIR / "static/dashboard.js").read_text()
    dashboard_css = (DIST_DIR / "static/dashboard.css").read_text()
    
    for pattern in forbidden_patterns:
        if re.search(pattern, index_html) or re.search(pattern, dashboard_js):
             print(f"FAIL: Forbidden pattern {pattern} detected.")
             sys.exit(1)
             
    if "@import" in dashboard_css:
         print("FAIL: CSS contains external @import")
         sys.exit(1)

    # Check that technical sections are collapsed by default (no 'open' attribute on details)
    # This is a basic structural check; actual implementation handles this via renderer.
    if 'id="validator-command-center" open' in index_html:
        print("FAIL: Validator Center is open by default")
        sys.exit(1)

    print("ORIGINAL_PHASE_4_HOSTED_DASHBOARD_POLISH_VALIDATION_PASS")

if __name__ == "__main__":
    check()
