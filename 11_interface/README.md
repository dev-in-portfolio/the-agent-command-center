# Interface Phase 1: CLI Operator Console

## What This Is

Phase 1 of the Station Chief v25 operator interface for **The Agent Command Center** (now at Phase 1.6–1.10 operational hardening). A safe, boring, terminal command menu that lets a human operator interact with the product/interface workspace.

## Why This Repo

This interface lives in `dev-in-portfolio/the-agent-command-center`, the dedicated product repo cloned from the validated `agent-command-center-3` sandbox line. It separates product/interface work from sandbox validation.

## Phase 1.6–1.10 Operational Hardening Summary

The Phase 1.1–1.5 upgrade has been hardened with:

| Area | Upgrade |
|------|---------|
| Action Registry | Centralised metadata for 12 actions with category, risk_level, cli_flags, menu_option, allowed_paths, forbidden_capabilities |
| Policy Enforcer | `enforce_allowed()` raises `PolicyRefusal` for locked/unknown actions; `validate_action_registry()` checks consistency |
| Artifact Inspector | Deep inspection engine: 5-package definitions, verdict extraction, stale claim detection, zero-byte/missing detection |
| Branch Review | Safe branch review packet generator using `git diff --name-only`; risk classification; human review checklist; never merges/pushes/deletes |
| Approval Ledger | JSONL-based lifecycle tracking (prepared, reviewed, approved/rejected_by_operator); all records `execution_performed: false` |
| CLI | Menu options 9-10 (artifact inspection, approval ledger); 6 new non-interactive flags |
| Policy | SAFE_ACTIONS and CONTROLLED_ACTIONS updated with new hardening actions; action registry auto-validated |
| Validator | 29 checks in CLI validator (+11); branch review packet check in command packet validator; new 15-test e2e validator |

## What It Can Do (Hardened)

- Show system status (product repo, source lineage, runtime version, locked/unlocked capabilities)
- Run validator wall (all three validators with PASS/FAIL/summary)
- List artifact packages with detailed health (expected files, missing files, zero-byte detection, verdicts)
- Show latest trial / gauntlet / migration summaries
- Generate operator session report with full audit trail (session folders, JSON, SHA256 hashes)
- Show locked actions
- Prepare hardened command packets (12 types, full preflight + rollback schema)
- Show current session state (ID, branch, commit, action count, errors)
- **Deep-inspect artifact packages** (9. Inspect artifact packages / `--inspect-artifacts`)
- **Prepare branch review packets** (`--prepare-branch-review <branch> [base]`)
- **Review, approve, reject command packets** (`--review-packet`, `--approve-packet`, `--reject-packet`)
- **Show approval ledger** (10. Show approval ledger / `--show-approval-ledger`)

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
python3 11_interface/station_chief_cli.py --inspect-artifacts
python3 11_interface/station_chief_cli.py --prepare-branch-review <branch>
python3 11_interface/station_chief_cli.py --review-packet <path>
python3 11_interface/station_chief_cli.py --approve-packet <path> <phrase>
python3 11_interface/station_chief_cli.py --reject-packet <path>
python3 11_interface/station_chief_cli.py --show-approval-ledger
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

## Approval Ledger

The approval ledger at `09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl`
tracks the lifecycle of every command packet review, approval, and rejection event.

- `approval_ledger.jsonl` is allowed to start empty. An empty ledger means no packet
  review/approval/rejection events have been recorded yet. It is not evidence of failure
  by itself.
- Every ledger record, once present, includes `execution_performed: false`.
- Records never represent actual execution. They only track the human operator's
  review decision.
- States: `prepared` → `reviewed` → `approved_by_operator` / `rejected_by_operator`
  / `expired` / `superseded`.

## Test Ledger

E2E validation uses a separate test ledger at
`09_exports/interface_phase_1/test_runs/e2e_ledger_test.jsonl` to avoid polluting the
production ledger. Tests 12-15 in the E2E validator call module functions directly with
`ledger_file=TEST_LEDGER`. The production ledger is never modified by automated tests.
CLI `--show-approval-ledger` always reads the production ledger.
All records in both ledgers have `execution_performed: false`.

## Future Phases

| Phase | Description |
|-------|-------------|
| Phase 2 | TUI (terminal user interface with curses/textual) |
| Phase 3 | Local web dashboard (read-only status page) |
| Phase 4 | GitHub Actions buttons (trigger workflows from interface) |
| Phase 5 | API layer (REST endpoints for remote status checks) |
| Phase 6 | ChatOps (Slack/Discord command integration) |
