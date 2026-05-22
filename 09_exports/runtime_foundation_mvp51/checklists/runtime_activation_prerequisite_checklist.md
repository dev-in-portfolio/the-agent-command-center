# Runtime Activation Prerequisite Checklist

## Auth/RBAC
- Authenticated user exists.
- Role is assigned and validated.

## Tenant/workspace boundaries
- Tenant scope is defined.
- Workspace scope is defined.
- Data boundary is documented.

## Action registry
- Actions are registered.
- Each action has risk classification.

## Audit ledger
- Audit schema exists.
- Audit event logging is required for every request and decision.

## Approval gates
- Approval levels are defined.
- High-risk actions require human approval.

## Dry-run engine
- Dry-run is required before execution.
- Dry-run result must be complete before action can continue.

## Queue/human review
- Queue record exists when required.
- Human review exists when required.

## Monitoring/readiness
- Monitoring notes exist.
- Runtime readiness is explicitly blocked until gates pass.

## Incident/rollback planning
- Rollback readiness note exists.
- Incident readiness note exists.

## Security review
- Security reviewer approval exists for high-risk paths.

## Legal/ownership review
- Ownership and legal review are documented.

## Pilot scope
- Pilot scope is narrow.
- Fake data or sandbox boundaries are explicit.

## Explicit activation approval
- Activation approval is recorded.
- No runtime activation occurs before all gates pass.
