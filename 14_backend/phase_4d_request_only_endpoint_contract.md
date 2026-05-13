# Phase 4D Request-Only Endpoint Contract

## Purpose
Define the safest future API shape for action requests while prohibiting execution and mutation in this phase.

## Future Request-Only Endpoints
- `POST /api/action-requests`
- `GET /api/action-requests/:request_id`
- `GET /api/action-requests`
- `POST /api/action-requests/:request_id/approve`
- `POST /api/action-requests/:request_id/deny`

## Required Rules
- Every `POST` endpoint is request-only or decision-only.
- No endpoint may execute a command in Phase 4D.
- No endpoint may mutate GitHub, Netlify, deploy, merge, or push state in Phase 4D.
- No endpoint may rely on browser-provided secrets.

## Build Status
- Action execution implemented: false
- Command execution added: false
- GitHub mutation added: false
- Netlify mutation added: false
- External API calls added: false

---
*Planning only. This contract does not add live endpoints or backend mutation logic.*
