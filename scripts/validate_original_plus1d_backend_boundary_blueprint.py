#!/usr/bin/env python3
"""Original +1D backend boundary blueprint validator."""

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
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")


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
        "./original_plus1b_contract_schemas.json",
    }
    optional_model = DIST / "original_plus1d_backend_boundary_model.json"
    if optional_model.exists():
        allowed_fetches.add("./original_plus1d_backend_boundary_model.json")
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
check(file_exists(DIST / "original_plus1d_backend_boundary_model.json"), "dist/original_plus1d_backend_boundary_model.json missing")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")

required_markers = [
    "Original +1B",
    "Original +1C",
    "Original +1D",
    "Backend Boundary Blueprint",
    "Real Automation Dependency Map",
    "BACKEND BOUNDARY BLUEPRINT",
    "REAL AUTOMATION DEPENDENCY MAP",
    "BLUEPRINT ONLY",
    "FUTURE IMPLEMENTATION ONLY",
    "READINESS ONLY",
    "NO LIVE AUTOMATION",
    "NO EXECUTION",
    "NO MUTATION",
    "NO BACKEND WRITES",
    "NO DEPLOY / MERGE / PUSH / PR CONTROLS",
    "READY_FOR_BACKEND_ARCHITECTURE_REVIEW_ONLY",
    "NOT_READY_FOR_REAL_AUTOMATION",
    "Backend Boundary Overview Panel",
    "Future Backend Endpoint Contract Map Panel",
    "Auth / Role / Permission Architecture Panel",
    "Persistent Request Storage Model Panel",
    "Audit Log Storage Model Panel",
    "Approval Record Model Panel",
    "Queue / Job Lifecycle Model Panel",
    "Dry-Run Engine Boundary Panel",
    "Mutation Gateway Boundary Panel",
    "GitHub / Netlify Future Integration Boundary Panel",
    "Secrets Management Requirements Panel",
    "Rollback / No-Go Enforcement Model Panel",
    "Rate Limit / Abuse Control Plan Panel",
    "Future Implementation Sequence Panel",
    "Real Automation Prerequisite Checklist Panel",
    "Copy backend boundary blueprint",
    "Copy endpoint contract map",
    "Copy auth/permission architecture",
    "Copy storage model summary",
    "Copy audit model summary",
    "Copy queue lifecycle model",
    "Copy mutation gateway requirements",
    "Copy future implementation sequence",
    "Copy real automation prerequisite checklist",
]

for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

forbidden_action_words = ["submit", "save", "queue", "execute", "deploy", "merge", "push", "create pr", "start automation", "approve live action", "trigger workflow", "create endpoint"]
for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    if clean.startswith("copy ") or clean.startswith("load ") or clean.startswith("phase ") or clean.startswith("original +"):
        continue
    if any(word in clean for word in forbidden_action_words):
        check("disabled" in tag.lower() or "aria-disabled=\"true\"" in tag.lower(), f"index.html has enabled forbidden button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

optional_model_path = DIST / "original_plus1d_backend_boundary_model.json"
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
        check(forbidden not in model_text, f"backend boundary JSON contains forbidden token: {forbidden}")

report_files = [
    "original_plus1d_backend_boundary_blueprint_report.md",
    "original_plus1d_real_automation_dependency_map_report.md",
    "original_plus1d_endpoint_contract_map_report.md",
    "original_plus1d_auth_permission_architecture_report.md",
    "original_plus1d_storage_audit_approval_models_report.md",
    "original_plus1d_queue_job_lifecycle_report.md",
    "original_plus1d_mutation_gateway_boundary_report.md",
    "original_plus1d_future_integration_boundary_report.md",
    "original_plus1d_secrets_rollback_rate_limit_report.md",
    "original_plus1d_design_report.md",
    "original_plus1d_safety_report.md",
    "original_plus1d_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Original +1D report missing: {report}")

acceptance = REPORTS / "original_plus1d_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")
check(file_contains(acceptance, "BLUEPRINT_ONLY"), "acceptance report missing BLUEPRINT_ONLY")
check(file_contains(acceptance, "NOT_READY_FOR_REAL_AUTOMATION"), "acceptance report missing NOT_READY_FOR_REAL_AUTOMATION")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PLUS1D_BACKEND_BOUNDARY_BLUEPRINT_VALIDATION_PASS")
