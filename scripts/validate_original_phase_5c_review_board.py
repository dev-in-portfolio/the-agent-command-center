#!/usr/bin/env python3
"""Original Phase 5C Review Board Validator."""
import json
import re
import sys
from pathlib import Path

DIST = Path("13_web_dashboard/dist")
STATIC = Path("13_web_dashboard/static")
REPORTS = Path("09_exports/interface_phase_5")

errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def file_exists(path):
    return path.exists() and path.is_file()

def file_contains(path, text):
    return text in path.read_text(encoding="utf-8", errors="replace")

check(file_exists(DIST / "index.html"), "dist/index.html missing")
check(file_exists(DIST / "static" / "dashboard.js"), "dist/static/dashboard.js missing")
check(file_exists(DIST / "static" / "dashboard.css"), "dist/static/dashboard.css missing")
check(file_exists(STATIC / "dashboard.js"), "static/dashboard.js missing")
check(file_exists(STATIC / "dashboard.css"), "static/dashboard.css missing")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")

required_markers = [
    "Original Phase 5C",
    "Client-Side Operator Review Board",
    "Decision Ledger",
    "CLIENT-SIDE REVIEW BOARD",
    "DECISION LEDGER PREVIEW",
    "TEMPORARY IN-BROWSER STATE ONLY",
    "NO PERSISTENCE",
    "NO BACKEND WRITES",
    "NO EXECUTION",
    "NO MUTATION",
    "Review Board Intake Panel",
    "Review Board List Panel",
    "Decision Panel",
    "Decision Ledger Panel",
    "Ledger JSON Preview",
    "Ledger Markdown Preview",
    "Safety Summary Panel",
    "Copy review ledger JSON",
    "Copy review ledger Markdown",
    "Copy decision summary",
    "DISPLAY-ONLY REVIEW LIST",
    "NOT A QUEUE",
]

for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

# Verify no enabled buttons with forbidden action labels exist
import re as _re
forbidden_action_words = ["execute", "deploy", "merge", "push", "create pr", "submit review", "queue review", "save review"]

# Check section-button buttons
button_labels = _re.findall(r'<button[^>]*class="[^"]*section-button[^"]*"[^>]*>([^<]+)</button>', index)
for label in button_labels:
    clean = label.strip().lower()
    check(not any(w in clean for w in forbidden_action_words),
          f"index.html has enabled section-button with forbidden action: {label.strip()}")

# Check toggle-button buttons
toggle_labels = _re.findall(r'<button[^>]*class="[^"]*toggle-button[^"]*"[^>]*>([^<]+)</button>', index)
for label in toggle_labels:
    clean = label.strip().lower()
    check(not any(w in clean for w in forbidden_action_words),
          f"index.html has enabled toggle-button with forbidden action: {label.strip()}")

# Check copy-button buttons
copy_labels = _re.findall(r'<button[^>]*class="[^"]*copy-button[^"]*"[^>]*>([^<]+)</button>', index)
for label in copy_labels:
    clean = label.strip().lower()
    check(not any(w in clean for w in forbidden_action_words),
          f"index.html has enabled copy-button with forbidden action: {label.strip()}")

js_content = (STATIC / "dashboard.js").read_text(encoding="utf-8", errors="replace")

storage_apis = ["localStorage", "sessionStorage", "document.cookie", "indexedDB", "IndexedDB", "caches.", "serviceWorker"]
for api in storage_apis:
    check(api not in js_content, f"dashboard.js uses forbidden storage API: {api}")

forbidden_http = ['method: "POST"', "method:'POST'", 'method: "PUT"', "method:'PUT'", 'method: "PATCH"', "method:'PATCH'", 'method: "DELETE"', "method:'DELETE'"]
for method in forbidden_http:
    check(method not in js_content, f"dashboard.js contains forbidden HTTP method: {method}")

allowed_fetch_targets = {
    "/api/health", "/api/status", "/api/backend-manifest",
    "./status_snapshot.json",
    "./phase4d_identity_schema.json", "./phase4d_action_schema.json",
    "./phase4d_audit_schema.json", "./phase4d_approval_schema.json",
    "./phase4d_risk_model.json",
}
fetches = re.findall(r'fetch\(["\']([^"\']+)["\']', js_content)
for target in fetches:
    check(target in allowed_fetch_targets, f"dashboard.js unauthorized fetch: {target}")

forbidden_patterns = [
    "WebSocket", "EventSource", "sendBeacon", "eval(", "Function(", "import(",
    "Blob", "URL.createObjectURL", "FileReader", "api.github.com", "api.netlify.com",
    "github.com/repos", "workflow_dispatch", "merge_pull_request",
    "create_pull_request", "update_file", "delete_file",
]
for pattern in forbidden_patterns:
    check(pattern not in js_content, f"dashboard.js contains forbidden pattern: {pattern}")

# Check reports exist
report_files = [
    "original_phase_5c_client_side_review_board_report.md",
    "original_phase_5c_design_report.md",
    "original_phase_5c_safety_report.md",
    "original_phase_5c_validator_report.md",
    "original_phase_5c_acceptance_report.md",
]
for rfile in report_files:
    check(file_exists(REPORTS / rfile), f"Phase 5C report missing: {rfile}")

acceptance = (REPORTS / "original_phase_5c_acceptance_report.md").read_text(encoding="utf-8")
check("PASS_WITH_HIGH_CONFIDENCE" in acceptance, "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    print("VALIDATION_FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("ORIGINAL_PHASE_5C_REVIEW_BOARD_VALIDATION_PASS")
