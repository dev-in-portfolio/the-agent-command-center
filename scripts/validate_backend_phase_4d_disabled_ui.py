#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def main():
    required_files = [
        "14_backend/phase_4d_disabled_dashboard_ui_contract.md",
        "09_exports/backend_phase_4/backend_phase_4d_disabled_ui_report.md",
        "13_web_dashboard/dist/index.html",
        "13_web_dashboard/dist/static/dashboard.js",
    ]
    for rel in required_files:
        if not (ROOT / rel).exists():
            _fail(f"Required file missing: {rel}")

    html = (ROOT / "13_web_dashboard/dist/index.html").read_text(encoding="utf-8")
    for needle in [
        "Phase 4D Control Room Preview",
        "Identity & Permissions Preview",
        "Action Request Queue Preview",
        "Audit Event Schema Preview",
        "Risk Model Preview",
        "DISABLED MOCK",
        "SCHEMA PREVIEW ONLY",
        "NO EXECUTION",
        "NO MUTATION",
        "NO DEPLOY",
        "NO MERGE",
        "NO PUSH",
        "NO SECRET ACCESS",
        "DISABLED — SCHEMA PREVIEW ONLY",
        "Load identity schema",
        "Load action schema",
        "Load audit schema",
        "Load risk model",
    ]:
        if needle not in html:
            _fail(f"Dashboard HTML missing {needle}")

    js = (ROOT / "13_web_dashboard/dist/static/dashboard.js").read_text(encoding="utf-8")
    allowed_fetches = [
        "/api/health",
        "/api/status",
        "/api/backend-manifest",
        "./status_snapshot.json",
        "./phase4d_identity_schema.json",
        "./phase4d_action_schema.json",
        "./phase4d_audit_schema.json",
        "./phase4d_risk_model.json",
        "./phase4d_approval_schema.json",
    ]
    for line in js.splitlines():
        if "fetch(" in line and not any(token in line for token in allowed_fetches):
            _fail(f"dashboard.js contains unauthorized fetch: {line.strip()}")
    for forbidden in [
        "http://",
        "https://",
        "api.github.com",
        "api.netlify.com",
        "github.com",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "WebSocket",
        "EventSource",
        "sendBeacon",
        "eval(",
        "Function(",
        "import(",
        'fetch("//',
        "fetch('//",
        'src="//',
        'href="//',
    ]:
        if forbidden in js or forbidden in html:
            _fail(f"Forbidden token found in disabled UI assets: {forbidden}")

    print("BACKEND_PHASE_4D_DISABLED_UI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
