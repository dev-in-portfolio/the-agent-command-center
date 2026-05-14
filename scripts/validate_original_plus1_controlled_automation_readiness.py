#!/usr/bin/env python3
"""Original +1 controlled automation readiness validator."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
STATIC = ROOT / "13_web_dashboard" / "static"
REPORTS = ROOT / "09_exports" / "original_plus1"

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
    "Original +1",
    "Controlled Automation Readiness Layer",
    "CONTROLLED AUTOMATION READINESS",
    "READINESS ONLY",
    "NO LIVE AUTOMATION",
    "NO EXECUTION",
    "NO MUTATION",
    "NO BACKEND WRITES",
    "FUTURE AUTH / STORAGE / APPROVAL REQUIRED",
    "Automation Readiness Overview Panel",
    "Action Classification Matrix Panel",
    "Role / Permission Readiness Panel",
    "Human Approval Gate Simulator Panel",
    "Dry-Run Plan Builder Panel",
    "Preflight Checklist Panel",
    "Execution Boundary Panel",
    "Automation Handoff Contract Builder Panel",
    "Original +1 Safety Summary Panel",
    "Copy automation readiness summary",
    "Copy dry-run plan",
    "Copy preflight checklist",
    "Copy automation handoff contract",
    "Copy Original +1 safety summary",
]
for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    first_word = clean.split()[0] if clean.split() else ""
    if clean.startswith("copy "):
        continue
    if clean.startswith("phase ") or clean.startswith("original +") or clean.startswith("roadmap ") or clean.startswith("jump "):
        continue
    if first_word in {"start", "run", "execute", "deploy", "merge", "push", "submit", "save", "queue"} or clean.startswith("create pr") or clean.startswith("live action") or clean.startswith("store"):
        check(False, f"index.html has forbidden enabled button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

report_files = [
    "original_plus1_controlled_automation_readiness_report.md",
    "original_plus1_design_report.md",
    "original_plus1_safety_report.md",
    "original_plus1_dependency_report.md",
    "original_plus1_validator_report.md",
    "original_plus1_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Original +1 report missing: {report}")

acceptance = REPORTS / "original_plus1_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")
check(file_contains(acceptance, "READINESS_ONLY"), "acceptance report missing READINESS_ONLY")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PLUS1_CONTROLLED_AUTOMATION_READINESS_VALIDATION_PASS")
