# Phase 4D Action Request Queue Schema

## Goal
Define the request-only payload shape for future queue intake while keeping execution fully disabled in this build.

## Required Fields
- `request_id`
- `action_id`
- `requested_by`
- `requested_role`
- `risk_level`
- `justification`
- `requested_at_utc`
- `target_scope`
- `requested_effect`
- `queue_state`

## Queue State Rules
- Initial state: `draft` or `requested`
- Allowed future review states: `approved`, `denied`, `expired`, `cancelled`
- Forbidden in this phase: `executed`

## Safety Invariants
- Requests are declarative only.
- Requests do not execute actions.
- Requests do not mutate GitHub, Netlify, deployment, merge, or push state.
- Requests do not require live credentials in this build.

## Build Status
- Real queue storage implemented: false
- Action execution implemented: false
- Command execution added: false
- External API calls added: false
- Browser external fetches added: false

---
*Schema planning only. No queue storage or execution path is included in this build.*
