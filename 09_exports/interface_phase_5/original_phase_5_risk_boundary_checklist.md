# Original Phase 5 — Risk Boundary Checklist

## Status
PLANNING_ONLY

## Purpose
Define the safety categories and red-line forbidden items for the Phase 5 planning context. This checklist ensures that Phase 5 remains planning-only and does not accidentally enable any execution, mutation, or unauthorized behavior.

## Display-Only Safe
- Dashboard content display
- Status display from existing /api/health, /api/status, /api/backend-manifest
- Schema preview display from Phase 4D static JSON files
- Request concept display (mock data)
- State machine display (mock data)
- Approval badge display (mock data)
- Audit trail display (mock data)
- Disabled control labels
- Planning document display

## Request Drafting Safe
- Plain-language intent text display
- Target scope display
- Risk classification display (static)
- Generated summary display (static)
- Safety warnings display (static)
- Disabled reason display
- All request drafting is display-only — no persistence, no submission

## Review Workflow Safe
- Review-ready state display
- Changes-requested state display
- Rejected state display
- Cancelled state display
- Review workflow is display-only — no notification, no dispatch

## Approval Display Safe
- Approval required badge display
- Pending review display
- Approved for planning display
- Blocked by safety boundary display
- Approval display is display-only — no auth, no authorization

## Dry-Run Concept Safe
- Dry-run preview placeholder display
- Example dry-run output display
- Risk classification example display
- Dry-run concept is display-only — no execution, no external call

## Storage Required Later
- Request persistence
- Draft persistence
- Audit trail persistence
- Approval record persistence
- State machine persistence
- These require future storage dependency — not implemented in Phase 5

## Auth Required Later
- User identity verification
- Role-based access control
- Session management
- Token management
- Approval authority verification
- These require future auth dependency — not implemented in Phase 5

## Forbidden Until Future Controlled Automation
- Action execution
- Command execution
- External API writes
- GitHub writes
- Netlify writes
- These require future execution dependency and separate human approval gate

## Never Allowed Without Explicit Human Gate
- Deploy to production
- Merge to master
- Push with force
- PR creation with auto-merge
- Database schema mutation
- Secret/token rotation
- Production configuration changes
- These must always require explicit human approval outside the automation system

## Red-Line Forbidden Items
These items must never appear in any Phase 5 implementation, prototype, or experiment:

- command execution strings
- deploy commands
- merge commands
- push commands
- PR creation commands
- GitHub mutation API calls
- Netlify mutation API calls
- external API write calls
- secrets or tokens in client-side code
- environment-variable exposure in client-side code
- database write operations
- queue dispatch operations
- browser external fetches to unauthorized endpoints
- localStorage, sessionStorage, or cookie-based secrets
- WebSocket, EventSource, or sendBeacon for data exfiltration
- eval() or Function() for dynamic code execution
- import() for unauthorized module loading
- workflow_dispatch API calls
- any form of remote code execution

## Checklist Usage
- Before any Phase 5 implementation merges, this checklist must be reviewed
- Any item in the red-line section automatically fails review
- Any item in the forbidden section requires explicit safety review
- Any item in the storage-required or auth-required sections must have its dependency implemented before being enabled
