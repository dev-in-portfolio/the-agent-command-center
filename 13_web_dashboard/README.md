# Interface Phase 3 - Read-Only Operations Dashboard

Phase 3 is a static, local, browser-friendly dashboard for The Agent Command Center.

It reuses the Phase 1 backend modules and Phase 2 contracts as read-only source of truth. It does not start a server, does not call any network service, does not use secrets or credentials, and does not execute command packets.

## Phase 3.1 to 3.10 Upgrade Summary

- Visual polish and dashboard UX
- Data quality and source transparency
- Interactive filtering and table tools
- Reports Library panel
- Artifact package deep-dive cards
- Validator Command Center
- Safety scanner hardening
- Snapshot/export upgrades
- Accessibility, print, and data export improvements
- Static dashboard release-candidate prep

## Build

```bash
python3 13_web_dashboard/build_phase3_dashboard.py
```

This writes:

- `13_web_dashboard/dist/index.html`
- `13_web_dashboard/dist/print.html`
- `13_web_dashboard/dist/dashboard_data.json`
- `13_web_dashboard/dist/static/dashboard.css`
- `13_web_dashboard/dist/static/dashboard.js`
- `09_exports/interface_phase_3/interface_phase_3_static_build_report.md`

Generated artifact hygiene:

- `13_web_dashboard/dist/index.html` is intentionally tracked.
- `13_web_dashboard/dist/print.html` is intentionally tracked.
- `13_web_dashboard/dist/dashboard_data.json` is intentionally tracked.
- `13_web_dashboard/dist/static/dashboard.css` is intentionally tracked.
- `13_web_dashboard/dist/static/dashboard.js` is intentionally tracked.
- Timestamped snapshot exports under `09_exports/interface_phase_3/snapshots/` are ignored going forward.
- `09_exports/interface_phase_3/test_runs/` is ignored going forward.
- Hygiene report: `09_exports/interface_phase_3/interface_phase_3_generated_artifact_hygiene_report.md`
- Visual QA report: `09_exports/interface_phase_3/interface_phase_3_visual_qa_report.md`

## Open Preview or Host Statically

Open `13_web_dashboard/dist/index.html` directly in a browser. No backend server is required.
The built `dist/` output is self-contained and loads its own `./static/dashboard.css` and `./static/dashboard.js` copies.

## Temporary Local Preview

For operator review only, you can serve the built dashboard locally from `13_web_dashboard/dist/`:

```bash
cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1
```

Preview URL: `http://127.0.0.1:8080`

This is not product behavior and is not committed as server code.

## Snapshot / Export Modes

```bash
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full
python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot
```

`--save-snapshot` defaults to JSON when no snapshot mode is supplied.

Saved snapshots live under:

- `09_exports/interface_phase_3/snapshots/`

Snapshot exports are timestamped review artifacts and are ignored by Git going forward.

## Validate

```bash
python3 scripts/validate_interface_phase_3_dashboard.py
python3 scripts/validate_interface_phase_3_e2e.py
```

## Safety Boundaries

- Official repo: locked
- Repo 2: locked
- Repo 3: locked
- Deployment: disabled
- Secrets: disabled
- Credentials: disabled
- Command packet execution: disabled
- Free-form shell: disabled
- Merge: disabled
- Push: disabled
- PR creation: disabled
- Network behavior: disabled
- API server: disabled
- Hosted app: disabled

## Backend Reuse

Phase 3 consumes read-only data from:

- `11_interface/interface_action_registry.py`
- `11_interface/interface_policy_enforcer.py`
- `11_interface/interface_artifact_inspector.py`
- `11_interface/interface_branch_review.py`
- `11_interface/interface_approval_ledger.py`
- `11_interface/interface_session_log.py`
- `12_tui/tui_safety_scanner.py`
- `12_tui/tui_state.py`
- `12_tui/tui_renderer.py`
- `12_tui/tui_screens.py`
- `12_tui/tui_keymap.py`

## What Phase 3 Cannot Do

- hosted deployment
- backend serving
- authentication
- network requests
- GitHub mutation
- command packet execution
- merge or push
- secrets or credential access

## What Still Waits for Phase 4

- Any hosted or server-based behavior
- Any deploy, merge, push, or PR creation behavior
- Any secrets or credential access
- Any command packet execution

## What Waits for Phase 4

Phase 4 may build on this dashboard with more static hosting ready review workflows, better static diff comparisons, and optional per-branch generated dashboards. It must keep the Phase 1 through Phase 3 safety boundaries intact.


## Visual Rebuild Confirmations

- Visual rebuild completed
- Capabilities Page dashboard used as visual reference
- Agent Command Center color theme applied
- dist is self-contained
- dist/static/dashboard.css exists
- dist/static/dashboard.js exists
- index.html references ./static/dashboard.css
- index.html references ./static/dashboard.js
- no ../static/ references
- local preview works from 13_web_dashboard/dist
- Visual QA report path: 09_exports/interface_phase_3/interface_phase_3_visual_qa_report.md
- No application/API backend server behavior
- No deploy/merge/push/secret/packet execution
