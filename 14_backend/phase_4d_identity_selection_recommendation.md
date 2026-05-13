# Phase 4D Identity Selection Recommendation

## Recommendation
Select **Netlify Identity** as the future primary operator identity provider for The Agent Command Center.

## Why This Is The Best Fit
- Aligns with the existing Netlify deployment surface already used by the project.
- Minimizes future integration sprawl across hosting, dashboard access, and operator-facing workflows.
- Supports role tagging and human operator identity without requiring custom command execution or external queue services in this phase.

## Why This Build Does Not Implement Identity
This build is a strategic contract only.

- Live auth implemented: false
- Database implemented: false
- Real queue storage implemented: false
- Action execution implemented: false
- Command execution added: false
- GitHub API calls added: false
- Netlify API calls added: false
- External API calls added: false
- Browser external fetches added: false
- Secrets added: false
- Tokens added: false
- Environment variables read: false

## Identity Model Intent
- `public_viewer`: can inspect static dashboard artifacts only.
- `operator_requester`: can prepare request-only actions in a future phase.
- `operator_approver`: can review and approve requests in a future phase.
- `security_auditor`: can inspect immutable audit trails in a future phase.
- `platform_admin`: can manage policy and disable surfaces in a future phase.

## Selection Conditions Before Any Future Implementation
1. The no-mutation boundary remains enforceable when auth is absent or degraded.
2. Role claims must be independently auditable.
3. Self-approval must be prohibited at the policy layer.
4. Any future secret lifecycle must remain server-side only.

## Decision
Proceed with Netlify Identity as the recommended future provider, but keep this phase limited to schema and contract preparation only.

---
*Planning only. No live identity integration is included in this build.*
