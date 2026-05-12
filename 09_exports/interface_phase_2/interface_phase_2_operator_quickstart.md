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

# Help
python3 12_tui/station_chief_tui.py --help
```

Supported flags: `--snapshot`, `--no-curses`, `--help`, `-h`.
Any other flag or positional argument is rejected with exit code 2 and an error message.
The TUI will not enter curses or plain-text mode on invalid flags.

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
