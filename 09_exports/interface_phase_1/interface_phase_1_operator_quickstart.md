# Interface Phase 1 — CLI Operator Console Quickstart

## Interactive Run

```bash
python3 11_interface/station_chief_cli.py
```

## Non-Interactive Examples

```bash
# View system status
python3 11_interface/station_chief_cli.py --status

# Run validator wall
python3 11_interface/station_chief_cli.py --validator-wall

# List artifact packages
python3 11_interface/station_chief_cli.py --list-artifacts

# Show latest summaries
python3 11_interface/station_chief_cli.py --show-summaries

# Show locked actions
python3 11_interface/station_chief_cli.py --show-locked

# Show current session state
python3 11_interface/station_chief_cli.py --session-state

# Prepare a command packet (non-interactive)
python3 11_interface/station_chief_cli.py --prepare-packet validator_wall

# Generate session report
python3 11_interface/station_chief_cli.py --generate-session-report
```

## Example Menu

```
============================================================
  AGENT COMMAND CENTER -- STATION CHIEF v25
  The Agent Command Center
  Interface Phase 1: CLI Operator Console
============================================================

  1. Show system status [safe]
  2. Run validator wall [controlled]
  3. List artifact packages [safe]
  4. Show latest trial / gauntlet summaries [safe]
  5. Generate operator session report [controlled]
  6. Show locked actions [safe]
  7. Prepare command packet [controlled]
  8. Show current session state [safe]
  9. Exit
```

## Safe First Actions

Start with these read-only actions:

1. **Option 1 — Show system status** — confirms product repo, source lineage, runtime, capabilities.
2. **Option 6 — Show locked actions** — lists everything the interface refuses to do.
3. **Option 8 — Show current session state** — see session ID, branch, commit, actions.

## How to Run Validator Wall

Select **option 2** or run `--validator-wall`. All three validators run sequentially with PASS/FAIL output, durations, and recommendations.

## How to Generate Session Report

Select **option 5** or run `--generate-session-report`. Written to:

```
09_exports/interface_phase_1/sessions/session_YYYYMMDD_HHMMSS/session_report.md
09_exports/interface_phase_1/sessions/session_YYYYMMDD_HHMMSS/session_result.json
09_exports/interface_phase_1/operator_session_report.md (latest)
```

If validator wall ran, additional logs are saved:
```
.../validator_wall_stdout.txt
.../validator_wall_result.json
```

If command packets were prepared, copies are saved under:
```
.../prepared_packets/
```

## How to Prepare Command Packet

Select **option 7** or run `--prepare-packet <type>`. Available types:

- validator_wall
- artifact_audit
- non_repo_gauntlet_review
- trial_v3_review
- migration_review
- merge_review_packet
- interface_phase_1_merge_review
- interface_phase_2_planning
- artifact_integrity_audit
- release_readiness_review
- cleanup_branch_review
- branch_delete_review

Written to:

```
09_exports/interface_phase_1/command_packets/<type>_packet.md
```

All packets have status `prepared_not_executed`. Each includes packet_id, risk_level, allowed/forbidden actions, preflight checklist, rollback notes, do_not_run_if conditions, and a required approval phrase.
