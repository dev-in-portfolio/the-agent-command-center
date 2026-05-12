# Interface Phase 2 Demo Notes

## How to Run the Demo

```bash
bash scripts/demo_interface_phase_2_tui.sh
```

## What It Demonstrates

- `--help` flag with all supported options
- `--snapshot` output (text format, default)
- `--snapshot --format markdown`
- `--snapshot --format json`
- `--snapshot --format compact`
- `--snapshot --format full`
- `--snapshot --format json --save` (writes to snapshots directory)
- `--no-curses` mode: starts and quits cleanly via `q`

## What It Does NOT Demonstrate

- Curses interactive mode (requires real terminal)
- Screen navigation (keys 1-9, b, d, ?, r, h)
- Validator wall execution (controlled action, requires manual confirmation)
- Branch review packet preparation
- Command packet preparation
- Approval ledger review/approve/reject lifecycle

## Safe Side Effects

- Session report written to `09_exports/interface_phase_2/sessions/` in no-curses mode
- Snapshot file written to `09_exports/interface_phase_2/snapshots/` when --save is used
- No network calls
- No file mutations outside `09_exports/interface_phase_2/`
- No Phase 1 backend module modifications

## Safety Invariants Preserved

- No deploy, merge, push, PR creation
- No secrets or credentials accessed
- No command packet execution
- No validator wall execution
- No official repo, repo 2, or repo 3 mutation
- No free-form shell execution
