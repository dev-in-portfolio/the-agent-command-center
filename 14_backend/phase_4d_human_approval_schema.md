# Phase 4D Human Approval Schema

## Goal
Define the future approval record required for a human-in-the-loop queue.

## Required Fields
- `approval_id`
- `request_id`
- `approver_id`
- `approver_role`
- `decision`
- `decision_reason`
- `decision_at_utc`
- `confirmation_phrase_required`
- `confirmation_phrase_provided`
- `dual_control_required`

## Approval Invariants
- Approval must be explicit.
- Approval cannot be inferred from navigation or page view.
- Approval cannot be performed by the same actor who requested the action.
- High-risk requests must require dual control.
- Missing confirmation must block approval completion.

## Build Status
- Live auth implemented: false
- Database implemented: false
- Real queue storage implemented: false
- Action execution implemented: false
- GitHub mutation added: false
- Netlify mutation added: false

---
*Planning only. This schema defines a future approval artifact and does not create a live approval flow.*
