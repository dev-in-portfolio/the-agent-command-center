# Station Chief TUI Operator Dashboard

Interface Phase 2: Terminal UI operator dashboard for The Agent Command Center.

Phase 2.1–2.11 Upgrade: Visual polish, navigation upgrades, artifact deep view, validator wall UX, branch review cockpit, approval ledger viewer, session timeline, safety monitor, snapshot exports, test hardening, Phase 3 handoff contract.

## Files

| File | Purpose |
|------|---------|
| `station_chief_tui.py` | Entrypoint: `--snapshot`, `--no-curses`, `--help`, `--format`, `--save` |
| `tui_app.py` | Application controller: curses wrapper + plain-text loop + snapshot mode |
| `tui_state.py` | Session state, Phase 1 module loading, navigation/breadcrumbs, session logs |
| `tui_keymap.py` | Key bindings (1-9, q, r, h, b, d, ?), forbidden screen names |
| `tui_renderer.py` | Screen rendering for all 9 screens + 5 snapshot formats + status badges; produces JSON per Interface Phase 2 Snapshot Schema Contract |
| `tui_screens.py` | Input handlers per screen (9 screens: dashboard, actions, artifacts, validator, packet, branch, ledger, help, safety) |
| `tui_safe_actions.py` | Safe wrappers for validator wall, packet prep, branch review, ledger |

## Usage

```bash
python3 12_tui/station_chief_tui.py                         # curses mode
python3 12_tui/station_chief_tui.py --no-curses              # plain text
python3 12_tui/station_chief_tui.py --snapshot               # text snapshot
python3 12_tui/station_chief_tui.py --snapshot --format json # JSON snapshot
python3 12_tui/station_chief_tui.py --snapshot --save        # save snapshot to file
python3 12_tui/station_chief_tui.py --help                   # help
```

Supported flags: `--snapshot`, `--no-curses`, `--help`, `-h`, `--format`, `--save`.
Snapshot formats: `text`, `markdown`, `json`, `compact`, `full`.
`--format` and `--save` only work with `--snapshot`.
Any other flag or positional argument is rejected with exit code 2.

## Architecture

TUI modules import Phase 1 backend modules from `11_interface/` via `importlib`.
No Phase 1 modules are modified. No logic is duplicated.

## Navigation

| Key | Screen |
|-----|--------|
| 1 | Dashboard |
| 2 | Action Registry |
| 3 | Artifact Inspector |
| 4 | Validator Wall |
| 5 | Command Packet Prep |
| 6 | Branch Review Cockpit |
| 7 | Approval Ledger |
| 8 | Help |
| 9 | Safety Monitor |
| b | Back |
| d | Dashboard / Home |
| ? | Screen help |
| r | Refresh |
| h | Help |
| q | Quit |

## Safety

- No network access
- No shell injection
- No command execution from packets
- No deploy, merge, push, secrets, credentials
- All ledger writes set `execution_performed: false`
- Safety boundary monitor with self-checks (screen 9)
