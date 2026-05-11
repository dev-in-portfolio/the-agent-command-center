# Interface Phase 1: CLI Operator Console

## What This Is

Phase 1 of the Station Chief v25 operator interface for **The Agent Command Center** (now at Phase 1.1–1.5 upgrade). A safe, boring, terminal command menu that lets a human operator interact with the product/interface workspace.

## Why This Repo

This interface lives in `dev-in-portfolio/the-agent-command-center`, the dedicated product repo cloned from the validated `agent-command-center-3` sandbox line. It separates product/interface work from sandbox validation.

## Phase 1.1–1.5 Upgrade Summary

The base Phase 1 CLI has been upgraded with:

| Area | Upgrade |
|------|---------|
| Accuracy | Fixed scoreboard path, file counting uses .is_file(), session report ordering |
| UX | Result banners [PASS/FAIL/WARNING/INFO], last action tracking, action recommendations, pause-after-action, session state |
| Packets | 12 packet types with full schema: packet_id, risk_level, approval_phrase, preflight checklist, rollback notes, do_not_run_if conditions |
| Session logging | session_id, git branch/commit tracking, session folders with JSON/stdout/packets, SHA256 packet hashes |
| Artifact viewer | Detailed package status: expected files, missing files, zero-byte files, detected verdicts, manifest status |
| Non-interactive | CLI flags for all actions: --status, --validator-wall, --list-artifacts, --show-summaries, --show-locked, --session-state, --prepare-packet, --generate-session-report |
| Config | interface_config.json for product identity and locked repos |
| Validator | 18 checks including smoke tests, forbidden import scan, non-interactive flag tests, invalid packet type test |

## What It Can Do (Upgraded)

- Show system status (product repo, source lineage, runtime version, locked/unlocked capabilities)
- Run validator wall (all three validators with PASS/FAIL/summary)
- List artifact packages with detailed health (expected files, missing files, zero-byte detection, verdicts)
- Show latest trial / gauntlet / migration summaries
- Generate operator session report with full audit trail (session folders, JSON, SHA256 hashes)
- Show locked actions
- Prepare hardened command packets (12 types, full preflight + rollback schema)
- Show current session state (ID, branch, commit, action count, errors)
- Non-interactive mode via CLI flags

## What It Cannot Do

- Mutate official repo (agent-command-center)
- Mutate agent-command-center-2
- Mutate agent-command-center-3
- Deploy to any environment
- Use secrets or credentials
- Read environment variables
- Inspect credential stores (~/.ssh, ~/.config, etc.)
- Promote lab work to official status
- Open PRs or merge into official repos
- Mutate production systems
- Operate autonomously
- Execute free-form shell commands from user input
- Run without human operator

All locked actions are enforced by interface policy. No bypass exists.

## How to Run

### Interactive Mode

```bash
python3 11_interface/station_chief_cli.py
```

### Non-Interactive Mode

```bash
python3 11_interface/station_chief_cli.py --status
python3 11_interface/station_chief_cli.py --validator-wall
python3 11_interface/station_chief_cli.py --list-artifacts
python3 11_interface/station_chief_cli.py --show-summaries
python3 11_interface/station_chief_cli.py --show-locked
python3 11_interface/station_chief_cli.py --session-state
python3 11_interface/station_chief_cli.py --prepare-packet validator_wall
python3 11_interface/station_chief_cli.py --generate-session-report
```

## Safety Boundaries

- All dangerous capabilities are locked at the policy layer
- The CLI never reads env, secrets, credentials, or config files
- The CLI never writes outside 09_exports/interface_phase_1/
- Command packets use status `prepared_not_executed` — they do not run commands
- Validator wall captures stdout/returncode but does not modify validators
- Session reports are deterministic and auditable with SHA256 packet hashes
- No shell=True anywhere in interface code
- No os.environ access anywhere in interface code
- No network imports (requests, urllib, http.client, socket)

## Future Phases

| Phase | Description |
|-------|-------------|
| Phase 2 | TUI (terminal user interface with curses/textual) |
| Phase 3 | Local web dashboard (read-only status page) |
| Phase 4 | GitHub Actions buttons (trigger workflows from interface) |
| Phase 5 | API layer (REST endpoints for remote status checks) |
| Phase 6 | ChatOps (Slack/Discord command integration) |
