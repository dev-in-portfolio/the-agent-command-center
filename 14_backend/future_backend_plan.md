# Future Backend Plan

## Phase 4B: Auth & Permissions
- Design authentication flow (e.g., Netlify Identity).
- Implement role-based access control (RBAC).
- Define admin boundaries.
- Plan secret management strategy for sensitive backend operations.

## Phase 4C: GitHub Integration (Read-Only)
- Fetch repository status via GitHub API safely.
- List active branches.
- Show recent PRs and commit history for review.
- Guided by [Phase 4C Read-Only Integration Plan](./phase_4c_read_only_integration_plan.md).

## Phase 4D: Action Request Queue
- Allow operators to request specific actions via the dashboard.
- Store requests in a queue (e.g., database integration).
- Establish an approval workflow for queued actions.

## Phase 5+: Mutation Layer
- Carefully reviewed and approved mutation operations.
- GitHub mutation (merge, push, PR creation) via backend API.
- Full command packet lifecycle integration.
