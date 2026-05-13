#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    required_files = [
        "13_web_dashboard/build_phase4c_status_snapshot.py",
        "13_web_dashboard/dist/status_snapshot.json",
        "14_backend/phase_4c_snapshot_prototype_plan.md",
        "14_backend/phase_4c_snapshot_schema.md",
        "14_backend/phase_4c_snapshot_generation_contract.md",
        "14_backend/phase_4c_snapshot_dashboard_contract.md",
        "14_backend/phase_4c_snapshot_safety_report.md",
    ]
    for f in required_files:
        if not (ROOT / f).exists():
            _fail(f"Required file missing: {f}")

    # Snapshot content validation
    snapshot_data = json.loads((ROOT / "13_web_dashboard/dist/status_snapshot.json").read_text())
    if snapshot_data.get("snapshot_version") != "phase_4c_snapshot_v1":
        _fail("Snapshot version mismatch")
    if snapshot_data.get("mode") != "static_read_only_snapshot":
        _fail("Snapshot mode mismatch")
    
    # Safety flags check
    safety_keys = [
        "live_external_api_calls", "github_api_calls", "netlify_api_calls",
        "browser_external_fetches", "secrets_used", "tokens_used",
        "environment_variables_read", "command_execution", "github_mutation", "netlify_mutation",
        "deploy_controls", "merge_controls", "push_controls", "pr_controls"
    ]
    for key in safety_keys:
        if snapshot_data.get(key) is not False:
            _fail(f"Snapshot safety flag '{key}' must be false")

    # Dashboard JS allowed fetches
    js_content = (ROOT / "13_web_dashboard/static/dashboard.js").read_text()
    allowed = [
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
    for line in js_content.splitlines():
        if "fetch(" in line:
            if not any(a in line for a in allowed):
                _fail(f"dashboard.js contains unauthorized fetch: {line.strip()}")

    print("BACKEND_PHASE_4C_STATUS_SNAPSHOT_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
