# Interface Phase 2 Operator Command Card

Quick reference for the Phase 2 TUI Operator Dashboard.

## TUI Commands

| Command | Description |
|---------|-------------|
| `python3 12_tui/station_chief_tui.py` | Launch TUI with curses (requires 80x24 terminal) |
| `python3 12_tui/station_chief_tui.py --no-curses` | Launch TUI in plain-text readline mode |
| `python3 12_tui/station_chief_tui.py --help` | Display help message and exit |

## Snapshot Commands

| Command | Description |
|---------|-------------|
| `--snapshot` | Take text snapshot (default format) |
| `--snapshot --format text` | Text snapshot |
| `--snapshot --format markdown` | Markdown snapshot |
| `--snapshot --format json` | JSON snapshot |
| `--snapshot --format compact` | Compact single-line snapshot |
| `--snapshot --format full` | Full verbose snapshot |
| `--snapshot --format json --save` | Save JSON snapshot to file |
| `--snapshot --save` | Save text snapshot to file |

Error handling: `--format` and `--save` only valid with `--snapshot`. Invalid format or extra positional args exit 2.

## In-TUI Key Bindings

| Key | Action |
|-----|--------|
| `1` | Dashboard |
| `2` | Artifact Inspector |
| `3` | Validator Wall |
| `4` | Branch Review Cockpit |
| `5` | Approval Ledger View |
| `6` | Session Timeline |
| `7` | Command Packet Terminal |
| `8` | Help / Quick Reference |
| `9` | Safety Boundary Monitor |
| `q` | Quit / Exit |
| `r` | Refresh current screen |
| `h` | Home / Dashboard |
| `b` | Back (previous screen) |
| `d` | Dashboard (clear history) |
| `?` | Screen-specific help |

## Validation

| Command | Description |
|---------|-------------|
| `python3 scripts/validate_interface_phase_2_tui.py` | TUI validator (32 tests) |
| `python3 scripts/validate_interface_phase_2_e2e.py` | E2E validator (32 tests) |

## Demo

```bash
bash scripts/demo_interface_phase_2_tui.sh
```

Safe operations: `--help`, `--snapshot` (all 5 formats), `--no-curses` with `q` to quit. Does not run validator wall.

## Session and Snapshot Output

| Artifact | Location |
|----------|----------|
| Session reports | `09_exports/interface_phase_2/sessions/` |
| Saved snapshots | `09_exports/interface_phase_2/snapshots/` |
| Validator test artifacts | `09_exports/interface_phase_2/test_runs/` |

## Safety Boundaries

| Constraint | Value |
|------------|-------|
| Shell commands in TUI | None — no `shell=True`, `os.system`, `subprocess` |
| Network access | None — no `requests`, `urllib`, `http.client`, `socket` |
| Deploy/merge/push | None — keymap has no deploy/merge/push bindings |
| Secrets/credentials | None — no access in TUI code |
| Phase 1 mutation | None — Phase 1 backend imported read-only |
| Command packet execution | None — only viewed, never executed |
| Execution performed | All ledger records: `execution_performed: false` |

## Related Documents

| Document | Location |
|----------|----------|
| Merge readiness packet | `09_exports/interface_phase_2/merge_readiness/interface_phase_2_merge_readiness_packet.md` |
| Final diff audit | `09_exports/interface_phase_2/interface_phase_2_final_diff_audit.md` |
| Clean checkout checklist | `09_exports/interface_phase_2/interface_phase_2_clean_checkout_checklist.md` |
| Snapshot schema contract | `09_exports/interface_phase_2/snapshot_schema_contract.md` |
| Phase 3 handoff contract | `09_exports/interface_phase_2/phase_3_handoff_contract.md` |
