# Phase 4C: Snapshot Schema

## Version
`phase_4c_snapshot_v1`

## Fields

### Metadata
- `snapshot_version`: String
- `project`: String
- `mode`: String (e.g., `static_read_only_snapshot`)
- `timestamp_utc`: String (ISO 8601)

### Safety Flags (Mandatory: ALL FALSE)
- `live_external_api_calls`: Boolean
- `github_api_calls`: Boolean
- `netlify_api_calls`: Boolean
- `browser_external_fetches`: Boolean
- `secrets_used`: Boolean
- `tokens_used`: Boolean
- `environment_variables_read`: Boolean
- `command_execution`: Boolean
- `github_mutation`: Boolean
- `netlify_mutation`: Boolean

### Status Data
- `production_site`: URL
- `phase_status`: Object mapping phase names to status strings.
- `endpoints`: List of endpoint objects (path, method, mode, danger).

---
*Note: This schema is for a static planning artifact only.*
