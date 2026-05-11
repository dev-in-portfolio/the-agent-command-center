# Interface Phase 1: CLI Operator Console

## What This Is

Phase 1 of the Station Chief v25 operator interface for **The Agent Command Center**. A safe, boring, terminal command menu that lets a human operator interact with the product/interface workspace.

## Why This Repo

This interface lives in `dev-in-portfolio/the-agent-command-center`, the dedicated product repo cloned from the validated `agent-command-center-3` sandbox line. It separates product/interface work from sandbox validation.

## What It Can Do

- Show system status (product repo, source lineage, runtime version, locked/unlocked capabilities)
- Run validator wall (all three validators: auto-self-improve-2, v25, v24)
- List artifact packages (trial v3, gauntlet #1, repo migration, interface phase 1)
- Show latest trial / gauntlet / migration summaries
- Generate operator session report
- Show locked actions
- Prepare command packets (pre-written, non-executing review packets)

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

```bash
python3 11_interface/station_chief_cli.py
```

## Safety Boundaries

- All dangerous capabilities are locked at the policy layer
- The CLI never reads env, secrets, credentials, or config files
- The CLI never writes outside 09_exports/interface_phase_1/
- Command packets use status `prepared_not_executed` — they do not run commands
- Validator wall captures stdout/returncode but does not modify validators
- Session reports are deterministic and auditable

## Future Phases

| Phase | Description |
|-------|-------------|
| Phase 2 | TUI (terminal user interface with curses/textual) |
| Phase 3 | Local web dashboard (read-only status page) |
| Phase 4 | GitHub Actions buttons (trigger workflows from interface) |
| Phase 5 | API layer (REST endpoints for remote status checks) |
| Phase 6 | ChatOps (Slack/Discord command integration) |
