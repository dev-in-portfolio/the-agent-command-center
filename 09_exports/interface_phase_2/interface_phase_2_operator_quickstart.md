# Interface Phase 2 Operator Quickstart

## Prerequisites

- Python 3.8+
- Repository: `dev-in-portfolio/the-agent-command-center`
- Phase 1 backend modules in `11_interface/`

## Running the TUI

```bash
# Preferred: curses-based interactive mode
python3 12_tui/station_chief_tui.py

# Fallback: plain-text interactive mode
python3 12_tui/station_chief_tui.py --no-curses

# Snapshot: print dashboard and exit (no curses needed)
python3 12_tui/station_chief_tui.py --snapshot

# Snapshot with format
python3 12_tui/station_chief_tui.py --snapshot --format json

# Snapshot save to file
python3 12_tui/station_chief_tui.py --snapshot --format markdown --save

# Help
python3 12_tui/station_chief_tui.py --help
```

Supported flags: `--snapshot`, `--no-curses`, `--help`, `-h`, `--format`, `--save`.
Snapshot formats: `text` (default), `markdown`, `json`, `compact`, `full`.
`--format` and `--save` only work with `--snapshot`.
Any other flag or positional argument is rejected with exit code 2.

## Navigation

| Key | Screen |
|-----|--------|
| 1 | Main Dashboard |
| 2 | Action Registry |
| 3 | Artifact Inspector |
| 4 | Validator Wall |
| 5 | Command Packet Prep |
| 6 | Branch Review Prep |
| 7 | Approval Ledger |
| 8 | Help |
| 9 | Safety Monitor |
| b | Back |
| d | Dashboard / Home |
| ? | Screen help |
| r | Refresh screen |
| h | Help screen |
| q | Quit |

## Controlled Actions (require input)

- **Validator Wall** (key 4): Type `RUN_VALIDATOR_WALL` to run all Phase 1 validators
- **Command Packet** (key 5): Enter number to select packet type
- **Branch Review** (key 6): Enter `<branch> [base_branch]`
- **Approval Ledger** (key 7): Choose review/approve/reject

## Safety Rules

- No deploy, merge, push, secrets, credentials, free shell
- No command execution from packets
- All ledger records set `execution_performed: false`
- Session logs written to `09_exports/interface_phase_2/sessions/`
- Safety monitor (screen 9) scans for boundary violations

## Snapshot Schema Contract

The TUI adheres to the **Interface Phase 2 Snapshot Schema Contract** (`09_exports/interface_phase_2/snapshot_schema_contract.md`).
JSON snapshots (`--snapshot --format json`) include these required root fields: `snapshot_id`, `created_at_utc`, `safety_status`, `artifact_summary`, `approval_ledger_summary`, `validator_status`, `boundary_status`, `recommended_next_action`. The `phase` field is always `"Interface Phase 2"` and `format` is always `"json"`.

## What's New in Phase 2.1–2.11

- Visual polish: status badges, action banners, breadcrumbs, consistent borders
- Navigation: b=back, d=home, ?=screen help, 9=safety monitor
- Artifact deep view: package detail, expected files, missing files, verdict
- Validator wall UX: progress per validator, stdout capture, session logs
- Branch review cockpit: input validation, risk preview, safety status
- Approval ledger viewer: state filters, execution_performed invariant check
- Session timeline: screen visited, actions requested/completed/refused
- Safety monitor: keymap scan, source scan, ledger scan (screen 9)
- Snapshot exports: 5 formats, --save to file, never overwrites
- Phase 3 handoff contract: prevents web dashboard from weakening safety
