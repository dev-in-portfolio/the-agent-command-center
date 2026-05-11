# Interface Phase 1 — Command Map (Operationally Hardened)

## Legend

| Column | Description |
|--------|-------------|
| Menu | Menu option number |
| CLI Flag | Non-interactive CLI flag |
| Internal Action | Action function name (action_id) |
| Category | safe / controlled / locked / exit |
| Risk Level | none / low / medium / high / informational |
| Executes? | Whether the action runs commands on the system |
| Writes Files? | Whether the action creates or modifies files |
| Forbidden | Whether the action provides access to locked capabilities |

## Interactive Menu + CLI Flags

| Menu | CLI Flag | Action ID | Category | Risk Level | Executes? | Writes Files? | Forbidden |
|------|----------|-----------|----------|------------|-----------|---------------|-----------|
| 1 | `--status` | `show_status` | safe | none | No | No | No |
| 2 | `--validator-wall` | `run_validator_wall` | controlled | low | Yes (subprocess) | No | No |
| 3 | `--list-artifacts` | `list_artifacts` | safe | none | No | No | No |
| 4 | `--show-summaries` | `show_summaries` | safe | none | No | No | No |
| 5 | `--generate-session-report` | `generate_session_report` | controlled | low | No | Yes (session folder) | No |
| 6 | `--show-locked` | `show_locked_actions` | safe | none | No | No | No |
| 7 | `--prepare-packet <type>` | `prepare_command_packet` | controlled | low | No | Yes (command packet) | No |
| 8 | `--session-state` | `show_session_state` | safe | none | No | No | No |
| 9 | `--inspect-artifacts` | `inspect_artifact_package` | safe | none | No | No | No |
| 10 | `--show-approval-ledger` | `show_approval_ledger` | controlled | none | No | No | No |
| 11 | — | Exit | exit | — | No | No | No |

## CLI-Only Flags (No Menu Entry)

| CLI Flag | Action ID | Category | Risk Level | Executes? | Writes Files? |
|----------|-----------|----------|------------|-----------|---------------|
| `--prepare-branch-review <branch> [base]` | `prepare_branch_review` | controlled | low | Yes (git diff) | Yes (branch review packet) |
| `--review-packet <path>` | `review_packet_approval` | controlled | low | No | Yes (ledger record) |
| `--approve-packet <path> <phrase>` | `review_packet_approval` | controlled | low | No | Yes (ledger record) |
| `--reject-packet <path> [reason]` | `review_packet_approval` | controlled | low | No | Yes (ledger record) |

## Test Ledger

A separate test ledger at `09_exports/interface_phase_1/test_runs/e2e_ledger_test.jsonl` is used
by the E2E validator for tests 12-15. The production ledger (`approval_ledger.jsonl`) is never
modified during automated testing. All records in both ledgers have `execution_performed: false`.

## Command Packet Types

| Type | Risk Level | Preflight Checks | Rollback Defined | Approval Phrase |
|------|------------|-----------------|-----------------|-----------------|
| validator_wall | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_VALIDATOR_WALL |
| artifact_audit | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_ARTIFACT_AUDIT |
| non_repo_gauntlet_review | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_NON_REPO_GAUNTLET_REVIEW |
| trial_v3_review | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_TRIAL_V3_REVIEW |
| migration_review | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_MIGRATION_REVIEW |
| merge_review_packet | medium | Yes | Yes (git reset) | I_APPROVE_PREPARED_PACKET_MERGE_REVIEW_PACKET |
| interface_phase_1_merge_review | medium | Yes | Yes (git reset) | I_APPROVE_PREPARED_PACKET_INTERFACE_PHASE_1_MERGE_REVIEW |
| interface_phase_2_planning | informational | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_INTERFACE_PHASE_2_PLANNING |
| artifact_integrity_audit | low | Yes | Yes (none needed) | I_APPROVE_PREPARED_PACKET_ARTIFACT_INTEGRITY_AUDIT |
| release_readiness_review | medium | Yes | Yes (promotion is irreversible) | I_APPROVE_PREPARED_PACKET_RELEASE_READINESS_REVIEW |
| cleanup_branch_review | low | Yes | Yes (reflog) | I_APPROVE_PREPARED_PACKET_CLEANUP_BRANCH_REVIEW |
| branch_delete_review | high | Yes | Yes (reflog, may not recover remote) | I_APPROVE_PREPARED_PACKET_BRANCH_DELETE_REVIEW |

## Locked Action Map

| Action | Lock Reason |
|--------|-------------|
| `mutate_official_repo` | Official repo must remain untouched |
| `mutate_repo_2` | agent-command-center-2 must remain untouched |
| `mutate_repo_3` | agent-command-center-3 must remain untouched |
| `deploy` | Deployment is disabled in interface workspace |
| `use_secrets` | Secrets must never be accessed |
| `use_credentials` | Credentials must never be accessed |
| `read_environment` | Environment reads could leak configuration |
| `inspect_credential_stores` | Credential stores are off-limits |
| `promote_to_official` | Promotion requires human-only decision |
| `open_official_pr` | PRs against official repos require human operator |
| `merge_official` | Merges to official require human operator |
| `production_mutation` | Production mutation is disabled |
| `uncontrolled_autonomy` | Operator must always be in the loop |
| `free_form_shell` | Arbitrary shell execution is a safety risk |
