# Interface Phase 3 Operator Quickstart

## Build

```bash
python3 13_web_dashboard/build_phase3_dashboard.py
```

## Output Path

`13_web_dashboard/dist/index.html`

## Open Locally

Open `13_web_dashboard/dist/index.html` directly in a browser. No server is required.

## Temporary Local Preview

For operator review only:

```bash
cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1
```

Preview URL: `http://127.0.0.1:8080`

This preview is local-only, temporary, and not product behavior.
The built `dist/` output is self-contained and loads `./static/dashboard.css` and `./static/dashboard.js` from inside the served root.

## Snapshot Modes

```bash
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full
python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot
```

`--save-snapshot` defaults to JSON when no snapshot mode is supplied.

Snapshot exports are timestamped review artifacts and are ignored by Git going forward.

Hygiene report: `09_exports/interface_phase_3/interface_phase_3_generated_artifact_hygiene_report.md`
Visual QA report: `09_exports/interface_phase_3/interface_phase_3_visual_qa_report.md`

## Validate

```bash
python3 scripts/validate_interface_phase_3_dashboard.py
python3 scripts/validate_interface_phase_3_e2e.py
```

## Safety Limitations

- No server
- No deployment
- No merge
- No push
- No PR creation
- No secrets or credentials
- No command packet execution
- No network access

## Notes

The dashboard is local-only and read-only. It reuses Phase 1 and Phase 2 source modules as the operating boundary.


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
