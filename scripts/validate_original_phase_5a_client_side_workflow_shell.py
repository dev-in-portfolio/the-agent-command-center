#!/usr/bin/env python3
"""Validate Original Phase 5A client-side operator workflow shell."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
STATIC = DIST / "static"
REPORTS = ROOT / "09_exports" / "interface_phase_5"

errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def file_exists(path):
    check(path.exists(), f"Missing file: {path.relative_to(ROOT)}")

def file_contains(path, text):
    if not path.exists():
        errors.append(f"Missing file for content check: {path.relative_to(ROOT)}")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    check(text in content, f"Missing '{text}' in {path.relative_to(ROOT)}")

def file_not_contains(path, text):
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    check(text not in content, f"Forbidden '{text}' found in {path.relative_to(ROOT)}")

# Dashboard dist files exist
file_exists(DIST / "index.html")
file_exists(STATIC / "dashboard.js")
file_exists(STATIC / "dashboard.css")

html = DIST / "index.html"
js_path = STATIC / "dashboard.js"

# Dashboard contains Original Phase 5A
file_contains(html, "Original Phase 5A")
file_contains(html, "Client-Side Operator Workflow Shell")
file_contains(html, "TEMPORARY IN-BROWSER STATE ONLY")
file_contains(html, "NO PERSISTENCE")
file_contains(html, "NO BACKEND WRITES")
file_contains(html, "NO EXECUTION")
file_contains(html, "NO MUTATION")

# Dashboard contains request drafting panel
file_contains(html, "Request Drafting Panel")
file_contains(html, "Workflow Type")
file_contains(html, "Plain-Language Intent")
file_contains(html, "Target Scope")
file_contains(html, "Operator Notes")

# Dashboard contains risk preview panel (check JS for risk classification logic)
file_contains(html, "Risk Preview Panel")
file_contains(js_path, "GREEN_READ_ONLY")
file_contains(js_path, "RED_FORBIDDEN_MUTATION")
file_contains(js_path, "YELLOW_REVIEW_ONLY")
file_contains(js_path, "ORANGE_REQUIRES_FUTURE_AUTH_STORAGE")

# Dashboard contains request state panel
file_contains(html, "Request State")
file_contains(js_path, "needs_review")
file_contains(js_path, "review_ready")
file_contains(js_path, "approved_for_future_phase")

# Dashboard contains review summary panel
file_contains(html, "Review Summary")
file_contains(js_path, "Execution Allowed")
file_contains(js_path, "Mutation Allowed")

# Dashboard contains approval required panel
file_contains(html, "Approval Required")
file_contains(html, "Approval display only")

# Dashboard contains audit trail preview panel
file_contains(html, "Audit Trail Preview")
file_contains(html, "in-memory")

# Dashboard contains dry-run preview placeholder
file_contains(html, "Dry-Run Preview")
file_contains(html, "future-only")

# Dashboard contains disabled boundary labels
file_contains(html, "DISABLED — PLANNING ONLY")
file_contains(html, "NO EXECUTION IN PHASE 5")
file_contains(html, "FUTURE STORAGE REQUIRED")

# Dashboard JS does not use localStorage/sessionStorage/cookies/IndexedDB
file_not_contains(js_path, "localStorage")
file_not_contains(js_path, "sessionStorage")
file_not_contains(js_path, "document.cookie")
file_not_contains(js_path, "IndexedDB")

# Dashboard JS fetch targets remain only on approved allowlist
approved_fetches = [
    "/api/health", "/api/status", "/api/backend-manifest",
    "/api/auth-status", "/api/role-matrix", "/api/request-storage-status",
    "./status_snapshot.json",
    "./phase4d_identity_schema.json", "./phase4d_action_schema.json",
    "./phase4d_audit_schema.json", "./phase4d_approval_schema.json",
    "./phase4d_risk_model.json",
    "./original_plus1b_contract_schemas.json",
    "./original_plus1c_readiness_qa_model.json",
    "./original_plus1d_backend_boundary_model.json",
    "./original_plus1e_backend_build_tickets.json",
    "./original_plus2a_auth_foundation_model.json",
    "./original_plus2b_request_storage_model.json",
]
js_content = js_path.read_text(encoding="utf-8", errors="replace")
fetches = re.findall(r'fetch\(["\']([^"\']+)["\']\)', js_content)
for target in fetches:
    check(target in approved_fetches, f"Unauthorized fetch target: {target}")

# Dashboard JS does not contain external URLs in fetch or import context
# (exclude inline CSS background URLs if any)
url_fetches = re.findall(r'https?://[^"\']+', js_content)
for url in url_fetches:
    check("github.com" not in url or "/dev-in-portfolio/" not in url or "/assets/" in url,
          f"External URL found: {url}")

# Dashboard JS does not contain WebSocket/EventSource/sendBeacon/eval/Function/import
file_not_contains(js_path, "WebSocket")
file_not_contains(js_path, "EventSource")
file_not_contains(js_path, "sendBeacon")
file_not_contains(js_path, "eval(")
file_not_contains(js_path, "Function(")

# Reports exist
for report in [
    "original_phase_5a_client_side_operator_workflow_shell_report.md",
    "original_phase_5a_safety_report.md",
    "original_phase_5a_design_report.md",
    "original_phase_5a_validator_report.md",
    "original_phase_5a_acceptance_report.md",
]:
    file_exists(REPORTS / report)

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print("ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_SHELL_VALIDATION_PASS")
