# Runtime Activation Separation Memo

## Purpose
This memo documents the explicit separation between the readiness architecture (complete through MVP-50) and runtime activation (not started).

## Current State
- 8 readiness layers are verified and documented
- All are schema-backed with no runtime execution
- The system is a read-only dashboard
- No endpoints, functions, or execution paths exist

## Proposed Activation Gates
Before enabling any runtime capability, the following gates must be cleared:

| Gate | Requirement | Owner |
|---|---|---|
| G1 | Stakeholder approval to begin runtime planning | Product owner |
| G2 | Runtime activation plan document approved | Engineering lead |
| G3 | Feature flag infrastructure deployed | Engineering |
| G4 | Human approval gate for each enabled capability | Operations |
| G5 | Monitoring and alert integration | Operations |
| G6 | Rollback procedures documented and tested | Engineering |
| G7 | Security review passed | Security |
| G8 | Stakeholder sign-off for specific runtime level | Product owner |

## Minimum Required Controls Before Enabling Real Execution
1. Feature flag per capability (auth, storage, audit, etc.)
2. Human approval before any execution
3. Read-only mode by default for all new capabilities
4. Monitoring and logging for all enabled capabilities
5. Rollback procedure for each capability
6. Rate limiting and resource controls
7. Audit event recording for every action

## Feature Flag Plan (Not Implemented)
Each runtime capability should have a flag:
- `features.execution.enabled` (default: false)
- `features.automation.enabled` (default: false)
- `features.writes.enabled` (default: false)
- `features.alerts.enabled` (default: false)
- `features.rollback.enabled` (default: false)
- `features.incident-mutation.enabled` (default: false)

## Rollback Plan (Not Implemented)
Each capability must have:
- Database backup procedure before enabling writes
- Feature flag disable procedure
- Capability-specific rollback steps

## Monitoring Plan (Not Implemented)
Before enabling any runtime:
- Health check endpoint
- Error rate monitoring
- Execution audit trail
- Alert channel integration

## Human Approval Plan (Not Implemented)
- Every execution requires explicit human approval
- Approval requires authenticated operator session
- Approval expires after configurable timeout

## Do-Not-Enable List
The following must NEVER be enabled in the demo/dashboard environment:
- Direct database write access from the public internet
- Unauthenticated execution endpoints
- Automatic execution without human approval
- Deployment controls accessible from the dashboard UI
- Privileged action execution without audit
