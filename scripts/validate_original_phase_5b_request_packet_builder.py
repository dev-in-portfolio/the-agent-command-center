#!/usr/bin/env python3
"""Original Phase 5B — Request Packet Builder Validator"""

from pathlib import Path
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST = PROJECT_ROOT / "13_web_dashboard" / "dist"
STATIC = PROJECT_ROOT / "13_web_dashboard" / "static"
REPORTS = PROJECT_ROOT / "09_exports" / "interface_phase_5"

errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def file_contains(path, substring):
    if not path.exists():
        return False
    return substring in path.read_text(encoding="utf-8", errors="replace")

# -- Phase 1: dist files exist
check(DIST.exists(), f"dist dir missing: {DIST}")
check((DIST / "index.html").exists(), "index.html missing")
check((DIST / "static" / "dashboard.js").exists(), "dist dashboard.js missing")
check((DIST / "static" / "dashboard.css").exists(), "dist dashboard.css missing")
check((STATIC / "dashboard.js").exists(), "source dashboard.js missing")
check((STATIC / "dashboard.css").exists(), "source dashboard.css missing")

index_html = DIST / "index.html"
js_file = STATIC / "dashboard.js"
dist_js = DIST / "static" / "dashboard.js"

# -- Phase 2: dashboard markers
check(file_contains(index_html, "Original Phase 5B"), "index.html missing Original Phase 5B")
check(file_contains(index_html, "Client-Side Operator Request Packet Builder"), "index.html missing Client-Side Operator Request Packet Builder")
check(file_contains(index_html, "CLIENT-SIDE REQUEST PACKET BUILDER"), "index.html missing safety label")
check(file_contains(index_html, "GENERATED LOCALLY"), "index.html missing GENERATED LOCALLY")
check(file_contains(index_html, "COPY ONLY"), "index.html missing COPY ONLY")
check(file_contains(index_html, "NO PERSISTENCE"), "index.html missing NO PERSISTENCE")
check(file_contains(index_html, "NO BACKEND WRITES"), "index.html missing NO BACKEND WRITES")
check(file_contains(index_html, "NO EXECUTION"), "index.html missing NO EXECUTION")
check(file_contains(index_html, "NO MUTATION"), "index.html missing NO MUTATION")

# -- Phase 3: panel markers
check(file_contains(index_html, "Operator Request Packet Panel"), "index.html missing Operator Request Packet Panel")
check(file_contains(index_html, "Packet Validation Panel"), "index.html missing Packet Validation Panel")
check(file_contains(index_html, "Packet JSON Preview"), "index.html missing Packet JSON Preview")
check(file_contains(index_html, "Packet Markdown Preview"), "index.html missing Packet Markdown Preview")
check(file_contains(index_html, "Safety Summary Panel"), "index.html missing Safety Summary Panel")

# -- Phase 4: copy buttons
check(file_contains(index_html, "Copy packet JSON"), "index.html missing Copy packet JSON")
check(file_contains(index_html, "Copy packet Markdown"), "index.html missing Copy packet Markdown")
check(file_contains(index_html, "Copy safety summary"), "index.html missing Copy safety summary")

# -- Phase 5: no enabled execute/submit/queue/deploy/merge/push/create PR controls
# (disabled buttons are allowed, enabled ones are not)
for pattern in ["Submit", "Queue packet", "Execute packet", "Deploy packet", "Merge packet", "Push packet", "Create PR"]:
    if file_contains(index_html, pattern):
        idx = index_html.read_text(encoding="utf-8", errors="replace").find(pattern)
        before = index_html.read_text(encoding="utf-8", errors="replace")[max(0, idx-200):idx+len(pattern)+50]
        if "disabled" not in before.lower() and "DISABLED" not in before:
            check(False, f"Found non-disabled {pattern} in HTML")

# -- Phase 6: JS safety scan on source
def js_safety_check(path):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")

    forbidden_js = [
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "IndexedDB",
        "caches.",
        "serviceWorker",
        "WebSocket",
        "EventSource",
        "sendBeacon",
        "eval(",
        "Function(",
        "import(",
    ]
    for item in forbidden_js:
        if item in text:
            check(False, f"{path.name} contains forbidden: {item}")

    fetch_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', text)
    for target in fetch_calls:
        check(target.startswith("./") or target.startswith("/api/"), f"{path.name} unauthorized fetch: {target}")

    forbidden_fetch = [
        "method: \"POST\"",
        "method:'POST'",
        "method: \"PUT\"",
        "method:'PUT'",
        "method: \"PATCH\"",
        "method:'PATCH'",
        "method: \"DELETE\"",
        "method:'DELETE'",
    ]
    for item in forbidden_fetch:
        if item in text:
            check(False, f"{path.name} contains {item}")

    for item in ["Blob", "URL.createObjectURL", "createObjectURL"]:
        if item in text:
            parts = re.split(r'["\']', text)
            for p in parts:
                if item in p and "'" not in p and '"' not in p:
                    check(False, f"{path.name} contains {item}")

    file_related = [
        '<input type="file"',
        '<input type="file"',
        ".accept =",
        "FileReader",
        "FileList",
    ]
    for item in file_related:
        if item in text:
            check(False, f"{path.name} contains file input/import: {item}")

js_safety_check(js_file)
js_safety_check(dist_js)

# -- Phase 7: reports exist
for report_name in [
    "original_phase_5b_client_side_request_packet_builder_report.md",
    "original_phase_5b_design_report.md",
    "original_phase_5b_safety_report.md",
    "original_phase_5b_validator_report.md",
    "original_phase_5b_acceptance_report.md",
]:
    check((REPORTS / report_name).exists(), f"Report missing: {report_name}")

# -- Phase 8: acceptance report verdict
acceptance = REPORTS / "original_phase_5b_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "Acceptance report missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    print("ORIGINAL_PHASE_5B_REQUEST_PACKET_BUILDER_VALIDATION_FAIL")
    for e in errors:
        print(f"  FAIL: {e}")
    sys.exit(1)
else:
    print("ORIGINAL_PHASE_5B_REQUEST_PACKET_BUILDER_VALIDATION_PASS")
