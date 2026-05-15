#!/usr/bin/env python3
"""Original Phase 5E runbook simulator validator."""

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
        "./original_plus2c_audit_log_model.json",
        "./original_plus2b_request_storage_model.json",
        "./original_plus2a_auth_foundation_model.json",
        "./original_plus1e_backend_build_tickets.json",
        "./original_plus1d_backend_boundary_model.json",
        "./original_plus1c_readiness_qa_model.json",
        "./original_plus1b_contract_schemas.json",
        "/api/audit-log-status",
        "/api/request-storage-status",
        "/api/role-matrix",
        "/api/auth-status",
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
    "Original Phase 5E",
    "Client-Side End-to-End Operator Runbook & Scenario Simulator",
    "CLIENT-SIDE RUNBOOK SIMULATOR",
    "END-TO-END OPERATOR FLOW",
    "SCENARIO PREVIEW ONLY",
    "GENERATED LOCALLY",
    "TEMPORARY IN-BROWSER STATE ONLY",
    "NO PERSISTENCE",
    "NO BACKEND WRITES",
    "NO EXECUTION",
    "NO MUTATION",
    "Scenario Selector Panel",
    "Runbook Step Tracker Panel",
    "Scenario Transcript Panel",
    "Safety Gate Panel",
    "Full Runbook Markdown Preview",
    "Safe Status Review",
    "Validator Review",
    "Dashboard Polish Request",
    "Safety Review Request",
    "Forbidden Mutation Attempt",
    "Copy full runbook Markdown",
    "Copy scenario transcript",
    "Copy safety gate summary",
    "Copy next-action recommendation",
    "Safety Summary Panel",
]
for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

forbidden_action_words = ["execute", "deploy", "merge", "push", "create pr", "submit", "queue", "save"]
allowed_buttons = {
    "copy full runbook markdown",
    "copy scenario transcript",
    "copy safety gate summary",
    "copy next-action recommendation",
    "copy merge-readiness summary",
    "copy queue lifecycle model",
}
for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    if any(word in clean for word in forbidden_action_words):
        if "disabled" in tag.lower() or "aria-disabled=\"true\"" in tag.lower():
            continue
        if clean in allowed_buttons:
            continue
        check(False, f"index.html has forbidden enabled button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

report_files = [
    "original_phase_5e_client_side_runbook_simulator_report.md",
    "original_phase_5e_design_report.md",
    "original_phase_5e_safety_report.md",
    "original_phase_5e_validator_report.md",
    "original_phase_5e_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Phase 5E report missing: {report}")

acceptance = REPORTS / "original_phase_5e_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PHASE_5E_RUNBOOK_SIMULATOR_VALIDATION_PASS")
