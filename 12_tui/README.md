# Station Chief TUI Operator Dashboard

Interface Phase 2: Terminal UI operator dashboard for The Agent Command Center.

## Files

| File | Purpose |
|------|---------|
| `station_chief_tui.py` | Entrypoint: `--snapshot`, `--no-curses`, `--help` |
| `tui_app.py` | Application controller: curses wrapper + plain-text loop |
| `tui_state.py` | Session state, Phase 1 module loading, session logs |
| `tui_keymap.py` | Key bindings, forbidden screen names |
| `tui_renderer.py` | Screen rendering for all 8 screens + snapshot |
| `tui_screens.py` | Input handlers per screen |
| `tui_safe_actions.py` | Safe wrappers for validator wall, packet prep, branch review, ledger |

## Usage

```bash
python3 12_tui/station_chief_tui.py                 # curses mode
python3 12_tui/station_chief_tui.py --no-curses         # plain text
python3 12_tui/station_chief_tui.py --snapshot           # non-interactive
python3 12_tui/station_chief_tui.py --help               # help
python3 12_tui/station_chief_tui.py --invalid-flag       # ERROR, exit 2
```

Supported flags: `--snapshot`, `--no-curses`, `--help`, `-h`.
Any other flag or positional argument is rejected with exit code 2.
No TUI mode is entered on invalid flags.

## Architecture

TUI modules import Phase 1 backend modules from `11_interface/` via `importlib`.
No Phase 1 modules are modified. No logic is duplicated.

## Safety

- No network access
- No shell injection
- No command execution from packets
- No deploy, merge, push, secrets
- All ledger writes set `execution_performed: false`
