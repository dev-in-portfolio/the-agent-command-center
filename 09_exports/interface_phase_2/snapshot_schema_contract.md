# Interface Phase 2 Snapshot Schema Contract

## Version 1.0

This contract defines the stable JSON schema for `--snapshot --format json` output.
Validators and downstream consumers MUST NOT assume any field beyond this contract exists. The prompt-required fields below are primary and mandatory. Legacy/internal fields may exist as optional backward-compatible extras.

## Root Object

```json
{
  "snapshot_id": "SNAP-20260101-000000-000000",
  "created_at_utc": "2026-01-01T00:00:00",
  "session_id": "TUI-20260101-000000-000000",
  "phase": "Interface Phase 2",
  "repo": "dev-in-portfolio/the-agent-command-center",
  "source_lineage": "dev-in-portfolio/agent-command-center-3",
  "format": "json",
  "safety_status": { /* see Safety Status */ },
  "artifact_summary": { /* see Artifact Summary */ },
  "approval_ledger_summary": { /* see Approval Ledger Summary */ },
  "validator_status": { /* see Validator Status */ },
  "boundary_status": { /* see Boundary Status */ },
  "recommended_next_action": "Check the approval ledger"
}
```

## Required Root Fields

| Field | Type | Always Present |
|-------|------|----------------|
| `snapshot_id` | string | yes |
| `created_at_utc` | string | yes |
| `session_id` | string | yes |
| `phase` | string | yes |
| `repo` | string | yes |
| `source_lineage` | string | yes |
| `format` | string | yes |
| `safety_status` | object | yes |
| `artifact_summary` | object | yes |
| `approval_ledger_summary` | object | yes |
| `validator_status` | object | yes |
| `boundary_status` | object | yes |
| `recommended_next_action` | string | yes |

## Exact Field Values

| Field | Required Value |
|-------|----------------|
| `phase` | `"Interface Phase 2"` |
| `repo` | `"dev-in-portfolio/the-agent-command-center"` |
| `source_lineage` | `"dev-in-portfolio/agent-command-center-3"` |
| `format` | `"json"` |

## Safety Status

Each field value MUST be one of: `"LOCKED"`, `"DISABLED"`.

```json
"safety_status": {
  "official_repo": "LOCKED",
  "repo_2": "LOCKED",
  "repo_3": "LOCKED",
  "deployment": "DISABLED",
  "secrets": "DISABLED",
  "credentials": "DISABLED",
  "command_packet_execution": "DISABLED",
  "free_form_shell": "DISABLED",
  "merge": "DISABLED",
  "push": "DISABLED",
  "pr_creation": "DISABLED",
  "network_behavior": "DISABLED"
}
```

## Artifact Summary

```json
"artifact_summary": {
  "package_count": 0,
  "packages": []
}
```

- `package_count` MUST be a non-negative integer.
- `packages` MUST be a list.
- Each package entry SHOULD contain `id` and `name`.

## Approval Ledger Summary

```json
"approval_ledger_summary": {
  "record_count": 0,
  "bad_execution_records": 0,
  "empty_ledger_allowed": true
}
```

- `record_count` MUST be a non-negative integer.
- `bad_execution_records` MUST be a non-negative integer.
- `empty_ledger_allowed` MUST be boolean `true`.

## Validator Status

```json
"validator_status": {
  "phase_2_tui": "unknown",
  "phase_2_e2e": "unknown",
  "phase_1": "unknown",
  "runtime": "unknown"
}
```

Status values are strings. Common values: `"PASS"`, `"FAIL"`, `"unknown"`.

## Boundary Status

Each field value MUST be a boolean (`true` or `false`).
Any value of `true` indicates a safety violation.

```json
"boundary_status": {
  "official_repo_touched": false,
  "repo_2_touched": false,
  "repo_3_touched": false,
  "deployment_performed": false,
  "secrets_credentials_used": false,
  "command_packets_executed": false,
  "merge_performed": false
}
```

Allowed values per field: `false`. (`true` would indicate a safety breach.)

## Schema Validation Rules

1. All required root fields MUST be present.
2. Safety status values MUST be one of `"LOCKED"` or `"DISABLED"`.
3. Boundary status values MUST be boolean. All MUST be `false` in normal operation.
4. `phase`, `repo`, `source_lineage`, `format` MUST match their exact required values.
5. `artifact_summary.package_count` MUST be a non-negative integer.
6. `artifact_summary.packages` MUST be a list.
7. `approval_ledger_summary.record_count` MUST be a non-negative integer.
8. `approval_ledger_summary.bad_execution_records` MUST be a non-negative integer.
9. `approval_ledger_summary.empty_ledger_allowed` MUST be boolean `true`.
10. `validator_status` MUST contain `phase_2_tui`, `phase_2_e2e`, `phase_1`, and `runtime`.
11. `recommended_next_action` MUST be a string.
12. No additional fields are forbidden at the root, but downstream consumers MUST only depend on fields listed in this contract.
13. JSON must be valid per RFC 8259.

## Change Process

- Schema version `1.0` is the initial release for Phase 2.
- Minor bumps (e.g. `1.1`) indicate additive fields or widened allowed values.
- Major bumps (e.g. `2.0`) indicate breaking changes or removed fields.
