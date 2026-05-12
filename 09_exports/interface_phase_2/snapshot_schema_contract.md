# Snapshot JSON Schema Contract

## Version 1.0

This contract defines the stable JSON schema for `--snapshot --format json` output.
Validators and downstream consumers MUST NOT assume any field beyond this contract exists.

## Root Object

```json
{
  "timestamp": "2026-01-01 00:00:00 UTC",
  "repo": "dev-in-portfolio/the-agent-command-center",
  "source_lineage": "dev-in-portfolio/agent-command-center-3",
  "phase": "2",
  "mode": "TUI Operator Dashboard",
  "session_id": "TUI-20260101-000000-000000",
  "current_screen": "dashboard",
  "safety": { /* see Safety Status */ },
  "boundary": { /* see Boundary State */ },
  "actions_completed": 0,
  "actions_refused": 0,
  "validator_runs": 0,
  "packets_prepared": 0,
  "branch_reviews_prepared": 0,
  "ledger_records_created": 0,
  "action_registry": { /* see Action Registry */ },
  "last_validator_results": {},

  "_schema_version": "1.0",
  "_metadata": {
    "source": "phase_2_tui_operator_dashboard",
    "generated_by": "tui_renderer.render_snapshot_json"
  }
}
```

## Required Root Fields

| Field | Type | Always Present |
|-------|------|----------------|
| `timestamp` | string | yes |
| `repo` | string | yes |
| `source_lineage` | string | yes |
| `phase` | string | yes |
| `mode` | string | yes |
| `session_id` | string | yes |
| `current_screen` | string | yes |
| `safety` | object | yes |
| `boundary` | object | yes |
| `actions_completed` | integer | yes |
| `actions_refused` | integer | yes |
| `validator_runs` | integer | yes |
| `packets_prepared` | integer | yes |
| `branch_reviews_prepared` | integer | yes |
| `ledger_records_created` | integer | yes |
| `action_registry` | object | yes |
| `last_validator_results` | object | yes |
| `_schema_version` | string | yes |
| `_metadata` | object | yes |

## Safety Status (display strings)

Each safety field value MUST be one of: `"LOCKED"`, `"DISABLED"`.

```json
"safety": {
  "official_repo": "LOCKED",
  "repo2": "LOCKED",
  "repo3": "LOCKED",
  "deployment": "DISABLED",
  "secrets": "DISABLED",
  "credentials": "DISABLED",
  "command_packet_execution": "DISABLED",
  "merge": "DISABLED",
  "push": "DISABLED",
  "pr_creation": "DISABLED",
  "free_form_shell": "DISABLED",
  "network_behavior": "DISABLED"
}
```

Allowed values per field: `"LOCKED"`, `"DISABLED"`.

## Boundary State (boolean invariants)

Each boundary field value MUST be a boolean (`true` or `false`).
Any value of `true` indicates a safety violation.

```json
"boundary": {
  "official_repo_touched": false,
  "repo2_touched": false,
  "repo3_touched": false,
  "deployment_performed": false,
  "secrets_used": false,
  "credentials_used": false,
  "command_packets_executed": false
}
```

Allowed values per field: `false`. (`true` would indicate a safety breach.)

## Action Registry

```json
"action_registry": {
  "total": 0,
  "safe": 0,
  "controlled": 0,
  "locked": 0
}
```

All values are non-negative integers.

## Validator Results

```json
"last_validator_results": {
  "CLI": "PASS",
  "Command Packets": "PASS",
  "E2E": "PASS",
  "RC": "PASS"
}
```

Status values are strings. Common values: `"PASS"`, `"FAIL"`, `"TIMEOUT"`.

## Schema Validation Rules

1. All required root fields MUST be present.
2. Safety status values MUST be one of `"LOCKED"` or `"DISABLED"`.
3. Boundary values MUST be boolean. All MUST be `false` in normal operation.
4. `_schema_version` MUST be a valid semver string (e.g. `"1.0"`).
5. No additional fields are forbidden at the root, but downstream consumers MUST only depend on fields listed in this contract.
6. JSON must be valid per RFC 8259.

## Change Process

- Schema version `1.0` is the initial release for Phase 2.
- Minor bumps (e.g. `1.1`) indicate additive fields or widened allowed values.
- Major bumps (e.g. `2.0`) indicate breaking changes or removed fields.
- Schema version is recorded in `_schema_version` and `_metadata`.
