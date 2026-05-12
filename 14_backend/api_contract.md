# Phase 4A API Contract

## Endpoints

### GET `/api/health`
Basic health check.
- **Response**: JSON object with `ok: true`, `service`, `phase`, `mode`, and safety flags.

### GET `/api/status`
Configuration and safety status.
- **Response**: JSON object with `dashboard`, `backend`, `safety`, and `next_phase` information.

### GET `/api/backend-manifest`
List of available endpoints and planned future phases.
- **Response**: JSON object with `endpoints` list and capability flags.

## Safety Invariants
- All responses must be `application/json`.
- Same-origin only (no `Access-Control-Allow-Origin: *`).
- `command_execution` must be `false`.
- `github_mutation` must be `false`.
- `secret_access` must be `false`.
- `credential_access` must be `false`.
- No outbound API calls are allowed.
