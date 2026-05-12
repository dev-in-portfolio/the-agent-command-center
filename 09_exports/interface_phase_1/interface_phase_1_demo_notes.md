# Interface Phase 1 — Demo Notes

## Demo Script

The demo script is at `scripts/demo_interface_phase_1.sh`.

## Safe Demo Scope

This demo is designed to be non-destructive and safe to run in any environment.

### Does
- Show system status
- Show locked actions
- List artifact packages
- Inspect artifact packages (all and single)
- Show session state
- Prepare a command packet (validator_wall)
- Show approval ledger
- Show summaries
- Generate a session report

### Does Not
- Deploy
- Merge
- Push
- Open PRs
- Call network
- Execute command packets
- Touch official/repo2/repo3
- Use secrets or credentials
- Run validator wall automatically

## Running the Demo

```bash
bash scripts/demo_interface_phase_1.sh
```

## Running Validator Wall Manually

The safe demo intentionally skips `--validator-wall` because it may run checks that
depend on local runtime/repo state or network connectivity. To run validators manually:

```bash
python3 11_interface/station_chief_cli.py --validator-wall
```

Or run individual validators:

```bash
python3 scripts/validate_interface_phase_1_cli.py
python3 scripts/validate_interface_phase_1_command_packets.py
python3 scripts/validate_interface_phase_1_e2e.py
python3 scripts/validate_interface_phase_1_release_candidate.py
```

## Final Acceptance Report

The final Phase 1 acceptance report is at:
`09_exports/interface_phase_1/interface_phase_1_final_acceptance_report.md`

## Release-Candidate Validator Pass String

`INTERFACE_PHASE_1_RELEASE_CANDIDATE_VALIDATION_PASS`

## Merge Readiness Packet

`09_exports/interface_phase_1/merge_readiness/interface_phase_1_merge_readiness_packet.md`
