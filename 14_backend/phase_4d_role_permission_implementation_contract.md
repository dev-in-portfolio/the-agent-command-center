# Phase 4D Role Permission Implementation Contract

## Purpose
Define the future role and permission boundary for request-only backend actions without enabling any live mutation in this build.

## Roles
- `public_viewer`: read-only dashboard visibility.
- `operator_requester`: may submit request-only action intents in a future phase.
- `operator_approver`: may approve or deny requests in a future phase.
- `security_auditor`: may inspect audit evidence in a future phase.
- `platform_admin`: may manage policy and freeze the queue in a future phase.

## Permission Rules
- Request creation must never imply approval.
- Approval must never imply execution.
- Execution must remain separated from request and approval concerns.
- Self-approval is forbidden.
- High-risk actions require two-party review.
- Every permission decision must produce an audit event.

## Future Endpoint Contract Summary
- `GET` endpoints may remain read-only when safe.
- `POST /api/action-requests` must be request-only in a future phase.
- Approval endpoints must mutate queue state only after the auth, audit, and storage gates are accepted.
- Execution endpoints remain forbidden in Phase 4D.

## Safety Status In This Build
- Live auth implemented: false
- Database implemented: false
- Real queue storage implemented: false
- Action execution implemented: false
- GitHub mutation added: false
- Netlify mutation added: false
- Deploy controls added: false
- Merge controls added: false
- Push controls added: false
- PR controls added: false

## Implementation Boundary
This contract does not add auth middleware, database tables, queue state, secrets, command execution, or external API access.

---
*Planning only. This contract defines future role enforcement boundaries and includes no live implementation.*
