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
        "schema-only",
        "All controls remain disabled in Phase 4D.",
        "disabled"
    ]:
        if needle not in html:
            _fail(f"Dashboard HTML missing {needle}")

    for forbidden in [
        "Deploy now",
        "Merge branch",
        "Push branch",
        "Create PR",
        "workflow_dispatch",
        "merge_pull_request",
        "create_pull_request"
    ]:
        if forbidden in html:
            _fail(f"Forbidden live control found in HTML: {forbidden}")

    js = (ROOT / "13_web_dashboard/dist/static/dashboard.js").read_text(encoding="utf-8")
    allowed_fetches = ["/api/health", "/api/status", "/api/backend-manifest", "./status_snapshot.json"]
    for line in js.splitlines():
        if "fetch(" in line and not any(token in line for token in allowed_fetches):
            _fail(f"dashboard.js contains unauthorized fetch: {line.strip()}")

    print("BACKEND_PHASE_4D_DISABLED_UI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
