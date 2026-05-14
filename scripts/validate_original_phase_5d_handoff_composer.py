#!/usr/bin/env python3
"""Original Phase 5D handoff composer validator."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
STATIC = ROOT / "13_web_dashboard" / "static"
REPORTS = ROOT / "09_exports" / "interface_phase_5"

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def file_exists(path):
    return path.exists() and path.is_file()


def file_contains(path, text):
    if not path.exists():
        return False
    return text in path.read_text(encoding="utf-8", errors="replace")


def js_safety_check(path):
    if not path.exists():
        errors.append(f"Missing JS file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in [
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
        "Blob",
        "URL.createObjectURL",
        "FileReader",
    ]:
        check(token not in text, f"dashboard.js contains forbidden token: {token}")

    for method in [
        'method: "POST"', "method:'POST'",
        'method: "PUT"', "method:'PUT'",
        'method: "PATCH"', "method:'PATCH'",
        'method: "DELETE"', "method:'DELETE'",
    ]:
        check(method not in text, f"dashboard.js contains forbidden HTTP method: {method}")

    allowed_fetches = {
        "/api/health",
        "/api/status",
        "/api/backend-manifest",
        "./status_snapshot.json",
        "./phase4d_identity_schema.json",
        "./phase4d_action_schema.json",
        "./phase4d_audit_schema.json",
        "./phase4d_approval_schema.json",
        "./phase4d_risk_model.json",
    }
    for target in re.findall(r'fetch\(["\']([^"\']+)["\']', text):
        check(target in allowed_fetches, f"dashboard.js unauthorized fetch: {target}")

    for url in re.findall(r'https?://[^"\']+', text):
        check("api.github.com" not in url, f"dashboard.js contains external URL: {url}")
        check("api.netlify.com" not in url, f"dashboard.js contains external URL: {url}")
        check("github.com/repos" not in url, f"dashboard.js contains external URL: {url}")


check(file_exists(DIST / "index.html"), "dist/index.html missing")
check(file_exists(DIST / "static" / "dashboard.js"), "dist/static/dashboard.js missing")
check(file_exists(DIST / "static" / "dashboard.css"), "dist/static/dashboard.css missing")
check(file_exists(STATIC / "dashboard.js"), "static/dashboard.js missing")
check(file_exists(STATIC / "dashboard.css"), "static/dashboard.css missing")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")

required_markers = [
    "Original Phase 5D",
    "Client-Side Operator Handoff Composer",
    "CLIENT-SIDE HANDOFF COMPOSER",
    "GENERATED LOCALLY",
    "COPY/PASTE HANDOFF ONLY",
    "TEMPORARY IN-BROWSER STATE ONLY",
    "NO PERSISTENCE",
    "NO BACKEND WRITES",
    "NO EXECUTION",
    "NO MUTATION",
    "Handoff Source Panel",
    "Handoff Notes Panel",
    "Implementation Prompt Preview",
    "Safety Summary Preview",
    "Acceptance Checklist Preview",
    "Rollback / No-Go Notes Preview",
    "Full Handoff Markdown Preview",
    "Copy implementation prompt",
    "Copy safety summary",
    "Copy acceptance checklist",
    "Copy rollback/no-go notes",
    "Copy full handoff Markdown",
    "Safety Summary Panel",
]
for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

forbidden_action_words = ["execute", "deploy", "merge", "push", "create pr", "submit", "queue", "save"]
for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    if any(word in clean for word in forbidden_action_words):
        if "disabled" in tag.lower() or "aria-disabled=\"true\"" in tag.lower():
            continue
        if clean in {
            "compose handoff from 5c decisions",
            "clear handoff",
            "parse pasted handoff",
            "copy implementation prompt",
            "copy safety summary",
            "copy acceptance checklist",
            "copy rollback/no-go notes",
            "copy full handoff markdown",
        }:
            continue
        check(False, f"index.html has forbidden enabled button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

report_files = [
    "original_phase_5d_client_side_handoff_composer_report.md",
    "original_phase_5d_design_report.md",
    "original_phase_5d_safety_report.md",
    "original_phase_5d_validator_report.md",
    "original_phase_5d_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Phase 5D report missing: {report}")

acceptance = REPORTS / "original_phase_5d_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PHASE_5D_HANDOFF_COMPOSER_VALIDATION_PASS")
