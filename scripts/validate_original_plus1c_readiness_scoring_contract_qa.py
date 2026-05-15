#!/usr/bin/env python3
"""Original +1C readiness scoring, contract QA, and no-go decision validator."""

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
        "./original_plus2c_audit_log_model.json",
        "./original_plus2b_request_storage_model.json",
        "./original_plus2a_auth_foundation_model.json",
        "./original_plus1e_backend_build_tickets.json",
        "./original_plus1d_backend_boundary_model.json",
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
    optional_model = DIST / "original_plus1c_readiness_qa_model.json"
    if optional_model.exists():
        allowed_fetches.add("./original_plus1c_readiness_qa_model.json")

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
check(file_exists(DIST / "original_plus1c_readiness_qa_model.json"), "dist/original_plus1c_readiness_qa_model.json missing")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")

required_markers = [
    "Original +1C",
    "Readiness Scoring",
    "Contract QA",
    "No-Go Decision Layer",
    "READINESS SCORING",
    "CONTRACT QA",
    "NO-GO DECISION LAYER",
    "LOCAL ANALYSIS ONLY",
    "COPY/PASTE ONLY",
    "READINESS ONLY",
    "NO LIVE AUTOMATION",
    "NO EXECUTION",
    "NO MUTATION",
    "NO BACKEND WRITES",
    "NO DEPLOY / MERGE / PUSH / PR CONTROLS",
    "Readiness Scorecard Panel",
    "Contract QA Matrix Panel",
    "Safety Assertion Panel",
    "No-Go Decision Panel",
    "Dependency Gap Map Panel",
    "Validator Confidence Panel",
    "Go / No-Go Packet Panel",
    "Copy readiness scorecard",
    "Copy contract QA report",
    "Copy safety assertion summary",
    "Copy no-go decision report",
    "Copy dependency gap map",
    "Copy validator confidence report",
    "Copy go/no-go packet",
    "READY_FOR_READINESS_REVIEW_ONLY",
    "NOT_READY_FOR_REAL_AUTOMATION",
]

for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

    forbidden_action_words = ["submit", "save", "queue", "execute", "deploy", "merge", "push", "create pr", "start automation", "approve live action"]
    for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
        tag, button_label, _ = match.groups()
        clean = button_label.strip().lower()
        if clean.startswith("copy ") or clean.startswith("load ") or clean.startswith("phase ") or clean.startswith("original +"):
            continue
        if any(word in clean for word in forbidden_action_words):
            check("disabled" in tag.lower() or "aria-disabled=\"true\"" in tag.lower(), f"index.html has enabled forbidden button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

optional_model_path = DIST / "original_plus1c_readiness_qa_model.json"
if optional_model_path.exists():
    model_text = optional_model_path.read_text(encoding="utf-8", errors="replace")
    for forbidden in [
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "WebSocket",
        "EventSource",
        "sendBeacon",
        "eval(",
        "Function(",
        "import(",
        "api.github.com",
        "api.netlify.com",
        "workflow_dispatch",
        "merge_pull_request",
        "create_pull_request",
        "update_file",
        "delete_file",
        "Blob",
        "URL.createObjectURL",
        "FileReader",
    ]:
        check(forbidden not in model_text, f"readiness QA JSON contains forbidden token: {forbidden}")

report_files = [
    "original_plus1c_readiness_scoring_report.md",
    "original_plus1c_contract_qa_report.md",
    "original_plus1c_no_go_decision_report.md",
    "original_plus1c_dependency_gap_report.md",
    "original_plus1c_validator_confidence_report.md",
    "original_plus1c_design_report.md",
    "original_plus1c_safety_report.md",
    "original_plus1c_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Original +1C report missing: {report}")

acceptance = REPORTS / "original_plus1c_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")
check(file_contains(acceptance, "READINESS_ONLY"), "acceptance report missing READINESS_ONLY")
check(file_contains(acceptance, "NOT_READY_FOR_REAL_AUTOMATION"), "acceptance report missing NOT_READY_FOR_REAL_AUTOMATION")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PLUS1C_READINESS_SCORING_CONTRACT_QA_VALIDATION_PASS")
