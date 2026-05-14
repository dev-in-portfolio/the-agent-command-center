#!/usr/bin/env python3
"""Original +1B operator console contract layer validator."""

from pathlib import Path
import json
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
check(file_exists(DIST / "print.html"), "dist/print.html missing")
check(file_exists(DIST / "static" / "dashboard.js"), "dist/static/dashboard.js missing")
check(file_exists(DIST / "static" / "dashboard.css"), "dist/static/dashboard.css missing")
check(file_exists(STATIC / "dashboard.js"), "static/dashboard.js missing")
check(file_exists(STATIC / "dashboard.css"), "static/dashboard.css missing")
check(file_exists(DIST / "original_plus1b_contract_schemas.json"), "dist/original_plus1b_contract_schemas.json missing")

index = (DIST / "index.html").read_text(encoding="utf-8", errors="replace")

required_markers = [
    "Original +1B",
    "Operator Console Consolidation",
    "Automation Contract Layer",
    "OPERATOR CONSOLE CONSOLIDATION",
    "CONTRACTS ONLY",
    "COPY/PASTE ONLY",
    "READINESS ONLY",
    "NO LIVE AUTOMATION",
    "NO EXECUTION",
    "NO MUTATION",
    "NO BACKEND WRITES",
    "NO DEPLOY / MERGE / PUSH / PR CONTROLS",
    "Unified Operator Flow Rail Panel",
    "Master Cockpit Summary Panel",
    "Formal Automation Contract Schema Panel",
    "Automation Contract Builder Panel",
    "Copy Output Hub Panel",
    "Master Safety Boundary Panel",
    "Master Validator Wall Panel",
    "Mode Emphasis Panel",
    "Request Packet Schema",
    "Review Decision Schema",
    "Decision Ledger Schema",
    "Handoff Contract Schema",
    "Runbook Scenario Schema",
    "Automation Readiness Contract Schema",
    "Approval Gate Contract Schema",
    "Dry-Run Plan Schema",
    "Preflight Checklist Schema",
    "No-Go / Rollback Policy Schema",
    "Copy implementation prompt",
    "Copy full runbook",
    "Copy automation readiness contract",
    "Copy dry-run plan",
    "Copy preflight checklist",
    "Copy no-go report",
    "Copy validator checklist",
    "Copy merge-readiness summary",
]
for marker in required_markers:
    check(marker in index, f"index.html missing required marker: {marker}")

forbidden_words = ["submit", "save", "queue", "execute", "deploy", "merge", "push", "create pr"]
for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
    tag, button_label, _ = match.groups()
    clean = button_label.strip().lower()
    if clean.startswith("copy ") or clean.startswith("load ") or clean.startswith("phase ") or clean.startswith("original +"):
        continue
    if any(word in clean for word in forbidden_words):
        check(False, f"index.html has forbidden enabled button label: {button_label.strip()}")

js_safety_check(STATIC / "dashboard.js")
js_safety_check(DIST / "static" / "dashboard.js")

schema_pack = json.loads((DIST / "original_plus1b_contract_schemas.json").read_text(encoding="utf-8"))
check(schema_pack.get("schema_pack_id") == "original-plus1b-operator-console-contract-pack", "schema pack id mismatch")
schemas = schema_pack.get("schemas", [])
check(len(schemas) >= 10, "schema pack missing expected schema entries")
schema_ids = {item.get("schema_id") for item in schemas}
for schema_id in [
    "request_packet_schema",
    "review_decision_schema",
    "decision_ledger_schema",
    "handoff_contract_schema",
    "runbook_scenario_schema",
    "automation_readiness_contract_schema",
    "approval_gate_contract_schema",
    "dry_run_plan_schema",
    "preflight_checklist_schema",
    "no_go_rollback_policy_schema",
]:
    check(schema_id in schema_ids, f"missing schema id: {schema_id}")

report_files = [
    "original_plus1b_operator_console_consolidation_report.md",
    "original_plus1b_automation_contract_layer_report.md",
    "original_plus1b_contract_schema_report.md",
    "original_plus1b_master_validator_wall_report.md",
    "original_plus1b_design_report.md",
    "original_plus1b_safety_report.md",
    "original_plus1b_acceptance_report.md",
]
for report in report_files:
    check(file_exists(REPORTS / report), f"Original +1B report missing: {report}")

acceptance = REPORTS / "original_plus1b_acceptance_report.md"
check(file_contains(acceptance, "PASS_WITH_HIGH_CONFIDENCE"), "acceptance report missing PASS_WITH_HIGH_CONFIDENCE")
check(file_contains(acceptance, "READINESS_ONLY"), "acceptance report missing READINESS_ONLY")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("ORIGINAL_PLUS1B_OPERATOR_CONSOLE_CONTRACT_LAYER_VALIDATION_PASS")
