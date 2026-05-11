# Interface Phase 1 — Command Map

## Legend

| Column | Description |
|--------|-------------|
| Menu | Menu option number |
| Internal Action | Action function name |
| Category | safe / controlled / locked / exit |
| Executes? | Whether the action runs commands on the system |
| Writes Files? | Whether the action creates or modifies files |
| Forbidden | Whether the action provides access to locked capabilities |

## Command Map

| Menu | Internal Action | Category | Executes? | Writes Files? | Forbidden |
|------|----------------|----------|-----------|---------------|-----------|
| 1 | `show_status` | safe | No | No | No |
| 2 | `run_validator_wall` | controlled | Yes (subprocess to validators) | No | No |
| 3 | `list_artifacts` | safe | No | No | No |
| 4 | `show_summaries` | safe | No | No | No |
| 5 | `generate_session_report` | controlled | No | Yes (session report) | No |
| 6 | `show_locked_actions` | safe | No | No | No |
| 7 | `prepare_command_packet` | controlled | No | Yes (command packet) | No |
| 8 | Exit | exit | No | No | No |

## Locked Action Map

These actions exist in the policy but are never exposed in the menu. The CLI refuses them at every layer.

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
