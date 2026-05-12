# Interface Phase 3 Operator Command Card

## Build

```bash
python3 13_web_dashboard/build_phase3_dashboard.py
```

## Snapshot Views

```bash
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full
python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot
```

## Validate

```bash
python3 13_web_dashboard/build_phase3_dashboard.py --validate-only
python3 scripts/validate_interface_phase_3_dashboard.py
python3 scripts/validate_interface_phase_3_e2e.py
```

## Open

Open `13_web_dashboard/dist/index.html` directly in a browser.

## Temporary Local Preview

```bash
cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1
```

Preview URL: `http://127.0.0.1:8080`

This preview is operator-only and temporary.
The built `dist/` folder includes `./static/dashboard.css` and `./static/dashboard.js`, so the preview renders from `dist/` without reaching outside the served root.

## Safety

- Static local only
- No server
- No network
- No deploy
- No merge
- No push
- No PR creation
- No secrets
- No credentials
- No command packet execution

## Generated Artifact Hygiene

- `13_web_dashboard/dist/index.html` is intentionally tracked.
- `13_web_dashboard/dist/print.html` is intentionally tracked.
- `13_web_dashboard/dist/dashboard_data.json` is intentionally tracked.
- `13_web_dashboard/dist/static/dashboard.css` is intentionally tracked.
- `13_web_dashboard/dist/static/dashboard.js` is intentionally tracked.
- Timestamped snapshot exports under `09_exports/interface_phase_3/snapshots/` are ignored going forward.
- `09_exports/interface_phase_3/test_runs/` is ignored going forward.
- Hygiene report: `09_exports/interface_phase_3/interface_phase_3_generated_artifact_hygiene_report.md`
- Visual QA report: `09_exports/interface_phase_3/interface_phase_3_visual_qa_report.md`

## Review Targets

- Safety boundary panel
- Source transparency panel
- Reports Library panel
- Validator Command Center
- Artifact deep-dive cards
- Compare Phases panel


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
- No server product behavior
- No deploy/merge/push/secret/packet execution
