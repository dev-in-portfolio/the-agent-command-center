# Original Phase 5 — Operator Workflow Map

## Status
PLANNING_ONLY

## High-Level Workflow

```
Operator opens dashboard
  → views read-only status and safety posture
  → chooses workflow type (request, review, audit, explore)
  → drafts request with intent and scope
  → sees automated risk classification
  → reviews generated request summary
  → marks request as draft / review-ready
  → approval gate displayed (conceptual — no execution)
  → state transition recorded in audit display model
  → no execution, mutation, deploy, merge, push, or PR occurs
  → future phase may connect storage/auth/execution only after separate human approval gate
```

## Operator Entry Points
- Dashboard homepage (existing Phase 4 polished dashboard)
- Status panel showing system readiness
- Schema preview panel showing concept definitions
- Audit trail display (future display-only)
- Disabled action controls with planning-only labels

## Intended Dashboard Interaction Path
1. Operator views the existing dashboard with Phase 4D schema previews
2. Dashboard displays a conceptual request panel (mock/disabled in Phase 5)
3. Operator can view but not execute any workflow action
4. All action-like controls display disabled state with PLANNING_ONLY labels
5. Dashboard remains static and read-only

## Request Drafting Path (Conceptual)
1. Operator opens request drafting panel
2. Operator fills plain-language intent and target scope
3. System generates risk classification based on static rules
4. System generates request summary for review
5. Operator saves as draft or marks review-ready
6. No request is sent to any external system
7. No request is persisted without future storage dependency

## Review Path (Conceptual)
1. Operator marks request as review-ready
2. Display transitions request state to review_ready
3. Display shows risk classification and safety warnings
4. Display shows required approval level
5. No external review mechanism — display-only
6. No notification, no email, no external dispatch

## Approval Path (Conceptual)
1. Request in review_ready state displays approval requirement
2. Approval in Phase 5 is display-only — no action is authorized
3. Approval transitions conceptual state to approved_for_future_phase
4. No mutation, no execution, no deployment occurs
5. Approval state is recorded in the display model only

## Rejection/Cancel Path (Conceptual)
1. Operator can mark request as cancelled at any state
2. Operator can mark request as rejected during review
3. Cancelled/rejected state is display-only
4. No external rollback, no mutation undo, no system impact

## Audit Trail Path (Conceptual)
1. Each state transition generates an audit event in the display model
2. Audit trail is visible in the dashboard
3. Audit trail is display-only — no persistent storage
4. Future implementation would require audit persistence dependency

## Dry-Run Preview Concept
- Dry-run preview is a display of what would happen if the request were executed
- In Phase 5, dry-run is conceptual only — no execution occurs
- Dry-run preview shows risk classification, affected scope, and safety warnings
- Dry-run does not call any external API
- Dry-run does not mutate any system

## Disabled-Action Boundary
- New Request: DISABLED — PLANNING ONLY
- Submit Request: DISABLED — REVIEW ONLY
- Execute Action: DISABLED — NO EXECUTION IN PHASE 5
- Deploy: DISABLED — FUTURE AUTH/STORAGE REQUIRED
- Merge: DISABLED — FUTURE CONTROLLED AUTOMATION GATE
- Push: DISABLED — FUTURE CONTROLLED AUTOMATION GATE
- Create PR: DISABLED — FUTURE CONTROLLED AUTOMATION GATE
- Approve: DISABLED — DISPLAY ONLY, NO AUTHORITY
- Save Draft: DISABLED — PLANNING ONLY (no persistence)
- Audit Export: DISABLED — FUTURE STORAGE REQUIRED

## Future Implementation Boundary
- Auth dependency required before any real user identity
- Storage dependency required before any persistence
- Queue dependency required before any action dispatch
- Execution dependency required before any mutation
- Each future dependency requires its own planning review
- Original +1 remains future-only and not planned here
