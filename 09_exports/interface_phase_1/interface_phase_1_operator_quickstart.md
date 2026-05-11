# Interface Phase 1 — CLI Operator Console Quickstart

## Run the Interface

```bash
python3 11_interface/station_chief_cli.py
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
  8. Exit
```

## Safe First Actions

Start with these read-only actions to learn the environment:

1. **Option 1 — Show system status** — confirms the product repo, source lineage, runtime version, and locked capabilities.
2. **Option 6 — Show locked actions** — lists everything the interface refuses to do.
3. **Option 3 — List artifact packages** — shows available export packages.

## How to Run Validator Wall

Select **option 2**. The CLI will run all three validators sequentially and display PASS/FAIL for each. Output includes stdout from each validator.

## How to Generate Session Report

Select **option 5** after running some actions. A session report is written to:

```
09_exports/interface_phase_1/operator_session_report.md
```

The report includes timestamps, repo name, actions run, validator results, and safety state.

The CLI will also prompt you to generate a session report before exit if one has not been written.

## How to Prepare Command Packet

Select **option 7**. Choose a packet type from:

1. validator_wall
2. artifact_audit
3. non_repo_gauntlet_review
4. trial_v3_review
5. migration_review
6. merge_review_packet

The packet is written to:

```
09_exports/interface_phase_1/command_packets/<type>_packet.md
```

All packets have status `prepared_not_executed`. They contain allowed actions, forbidden actions, and exact commands for an operator to review and approve before executing.
