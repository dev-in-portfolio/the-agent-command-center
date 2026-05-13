#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
SNAPSHOT_PATH = DIST_DIR / "status_snapshot.json"

def main():
    # Verify prerequisites
    required_reports = [
        ROOT / "09_exports/backend_phase_4/backend_phase_4a_production_verification_report.md",
        ROOT / "09_exports/backend_phase_4/backend_phase_4b_acceptance_report.md",
        ROOT / "09_exports/backend_phase_4/backend_phase_4c_acceptance_report.md"
    ]
    for r in required_reports:
        if not r.exists():
            print(f"ERROR: missing required report: {r.name}")
            return 1

    # Define snapshot structure
    snapshot = {
        "snapshot_version": "phase_4c_snapshot_v1",
        "project": "The Agent Command Center",
        "mode": "static_read_only_snapshot",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "generated_from": "local_repository_reports",
        "live_external_api_calls": False,
        "github_api_calls": False,
        "netlify_api_calls": False,
        "browser_external_fetches": False,
        "secrets_used": False,
        "tokens_used": False,
        "environment_variables_read": False,
        "command_execution": False,
        "github_mutation": False,
        "netlify_mutation": False,
        "deploy_controls": False,
        "merge_controls": False,
        "push_controls": False,
        "pr_controls": False,
        "production_site": "https://the-agent-command-center-dashboard.netlify.app/",
        "phase_status": {
            "phase_4a": "complete_live_verified",
            "phase_4b": "planning_merged",
            "phase_4c": "planning_merged_snapshot_prototype",
            "phase_4d": "gate_review_only"
        },
        "endpoints": [
            {
                "path": "/api/health",
                "method": "GET",
                "mode": "read_only",
                "dangerous_capabilities_enabled": False
            },
            {
                "path": "/api/status",
                "method": "GET",
                "mode": "read_only",
                "dangerous_capabilities_enabled": False
            },
            {
                "path": "/api/backend-manifest",
                "method": "GET",
                "mode": "read_only",
                "dangerous_capabilities_enabled": False
            }
        ],
        "snapshot_notes": [
            "This snapshot is generated from local repository reports.",
            "This snapshot does not call GitHub, Netlify, or external APIs.",
            "This snapshot does not contain secrets, tokens, or credentials."
        ],
        "source_reports": [
            "09_exports/backend_phase_4/backend_phase_4a_production_verification_report.md",
            "09_exports/backend_phase_4/backend_phase_4b_acceptance_report.md",
            "09_exports/backend_phase_4/backend_phase_4c_acceptance_report.md"
        ]
    }

    # Ensure dist exists
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Write snapshot
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, sort_keys=False)

    print("PHASE_4C_STATUS_SNAPSHOT_BUILD_PASS")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
