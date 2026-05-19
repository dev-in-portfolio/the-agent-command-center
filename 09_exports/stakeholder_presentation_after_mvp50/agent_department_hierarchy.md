# Agent / Department Hierarchy

## Known Declared Agents and Components
The repo does not contain a canonical agent registry. The closest explicit component registry in the live dashboard is the action registry, which contains 12 documented actions.

## Known Departments / Operating Areas
Departments are currently represented as operational domains, not formal named departments.

Operational domains:
1. Authentication / identity readiness
2. Request storage readiness
3. Audit ledger readiness
4. Approval gate readiness
5. Dry-run readiness
6. Controlled action queue readiness
7. Human-approved execution readiness
8. Monitoring / rollback / incident readiness
9. Demo / stakeholder review readiness
10. Validator / quality gate readiness
11. Safety boundary readiness

## Command Hierarchy
1. Product / Command Center Layer
2. Readiness Layer Roadmap
3. Operational Domains
4. Model / Artifact Layer
5. Validator Gate Layer
6. Human Review Layer
7. Future Runtime Activation Layer

## Validator Hierarchy
- The dashboard and exported docs are checked by targeted validators
- Validators are grouped by milestone and by wall-level policy checks
- The flat E2E pattern keeps each validator independent
- The master validator wall blocks unsafe or out-of-scope changes

## Human Review Hierarchy
- Stakeholders review the browser demo hub
- Technical reviewers inspect the appendix and validator map
- Executives review the opening statement, outline, and scorecard
- Runtime activation remains a separate approval decision

## Runtime Activation Hierarchy
Runtime activation is intentionally absent from the current build. A future activation phase would need:
- explicit approval
- runtime design
- security review
- monitoring and alert plan
- rollback plan
- change-management sign-off

## What Is Verified
- 8 readiness layers are production-verified through MVP-50
- 12 dashboard action registry items are documented in the live dashboard snapshot
- 13 disabled capability categories are captured in the presentation manifest

## What Is Not Yet Canonically Declared
- Exact agent count: UNKNOWN_NOT_CURRENTLY_DECLARED
- Exact department count: UNKNOWN_NOT_CURRENTLY_DECLARED

## Recommended Registry Structure
- `agent_registry.json`
- `department_registry.json`
- `system_hierarchy.json`

That registry set would let future demos state exact operating-unit counts without prose-based inference.
