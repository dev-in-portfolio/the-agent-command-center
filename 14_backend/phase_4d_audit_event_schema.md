# Phase 4D Audit Event Schema

## Goal
Define the immutable audit event structure that future request, approval, and policy surfaces must emit.

## Required Fields
- `event_id`
- `event_type`
- `actor_id`
- `actor_role`
- `request_id`
- `action_id`
- `risk_level`
- `event_at_utc`
- `decision_state`
- `target_scope`
- `evidence_refs`

## Event Types
- `request_created`
- `request_updated`
- `request_cancelled`
- `approval_granted`
- `approval_denied`
- `approval_expired`
- `policy_override_recorded`
- `execution_blocked`

## Invariants
- Audit records must be append-only.
- Audit records must never rely on browser-only trust.
- Audit records must capture both actor identity and assumed role.
- Execution attempts must be logged even when blocked.

## Build Status
- Database implemented: false
- Real queue storage implemented: false
- Action execution implemented: false
- Secrets added: false
- Tokens added: false

---
*Planning only. This build introduces the schema contract but no audit storage implementation.*
