# Read-Only Operations Dashboard Static Build Report

- Dashboard ID: PH3-20260512-230007
- Created at UTC: 2026-05-12T23:00:07Z
- Repo: dev-in-portfolio/the-agent-command-center
- Source lineage: dev-in-portfolio/agent-command-center-3
- Mode: static_local_dashboard
- Validation status: PASS
- Validation errors: 0
- Safety scan status: WARNING
- Output path: 13_web_dashboard/dist/index.html
- Print path: 13_web_dashboard/dist/print.html
- Dashboard data export: 13_web_dashboard/dist/dashboard_data.json
- Dist CSS path: 13_web_dashboard/dist/static/dashboard.css
- Dist JS path: 13_web_dashboard/dist/static/dashboard.js
- Snapshot schema contract: 09_exports/interface_phase_3/snapshot_schema_contract.md

## Build Inputs
- Phase 1 backend modules were read only.
- Phase 2 reference docs were read only.
- No application/API backend server is included in Phase 3.
- No outbound API calls, remote data fetching, analytics, tracking, or live backend connections are included in Phase 3.
- No secrets or credentials were accessed.
- No command packets were executed.
- Built HTML references only relative dist/static assets.

## Generated Artifact Policy
- Intentionally tracked: 13_web_dashboard/dist/index.html
- Intentionally tracked: 13_web_dashboard/dist/print.html
- Intentionally tracked: 13_web_dashboard/dist/dashboard_data.json
- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.css
- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.js
- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.json
- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.md
- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.txt
- Ignored going forward: 09_exports/interface_phase_3/test_runs/

## Snapshot / Export Modes
- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json`
- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown`
- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary`
- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full`
- `python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot` defaults to JSON when no snapshot mode is given.