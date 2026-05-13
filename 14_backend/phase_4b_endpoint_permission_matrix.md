# Phase 4B: Endpoint Permission Matrix

This document defines the required authentication and role levels for current and future endpoint classes.

## Current Endpoints (Phase 4A)

| Endpoint | Method | Auth Required? | Role Required | Read-Only? | Mutates? | Secrets? | Phase |
|---|---|---|---|---|---|---|---|
| `/api/health` | GET | No | Public | Yes | No | No | 4A |
| `/api/status` | GET | No | Public | Yes | No | No | 4A |
| `/api/backend-manifest` | GET | No | Public | Yes | No | No | 4A |

## Future Possible Endpoints

| Endpoint Class | Method | Auth Required? | Role Required | Read-Only? | Mutates? | Secrets? | Phase |
|---|---|---|---|---|---|---|---|
| `/api/auth/session` | GET | Yes | Public | Yes | No | No | 4B+ |
| `/api/audit/events` | GET | Yes | Auditor | Yes | No | No | 4C+ |
| `/api/github/status` | GET | Yes | Operator | Yes | No | Yes | 4C+ |
| `/api/actions/request`| POST | Yes | Operator | No | No (Queue) | No | 4D+ |
| `/api/actions/approve`| POST | Yes | Admin | No | No (Gate) | No | 4E+ |
| `/api/actions/execute`| POST | Yes | Maintainer | No | Yes | Yes | 5+ |
| `/api/deploy/status` | GET | Yes | Operator | Yes | No | Yes | 4C+ |
| `/api/admin/config` | GET | Yes | Admin | Yes | No | Yes | 5+ |

## Safety Notes
- Mutating endpoints (`POST/PUT/DELETE`) are strictly forbidden until a robust authorization and audit system is verified.
- Endpoints requiring secrets must never be exposed to Public Viewers.
- All future endpoints must follow the same-origin restriction established in Phase 4A.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
