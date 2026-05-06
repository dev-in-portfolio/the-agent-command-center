# Agent Command Center Assumption Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime assumption register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define a planning-only register for tracking assumptions so builder agents do not silently convert assumptions into authority, scope, or roadmap direction.

- this is a register only
- it does not convert assumptions to authority
- it does not modify runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Assumption Register Principle
- assumptions are planning records only
- assumption entries do not authorize runtime behavior
- assumption entries do not grant permission
- assumption entries do not imply execution
- assumption entries do not select next tasks
- assumption planning does not authorize workers, tasks, queues, routing, APIs, deployment, or production

## Assumption Entry Fields
- assumption_id: Identifier.
- assumption_statement: The assumption.
- assumption_category: Category.
- source: Contextual source.
- confidence: Estimate (Low/Medium/High).
- affected_scope: Task/file impact.
- runtime_effect: Explanation.
- v4_8_effect: Explanation.
- validation_needed: Boolean.
- operator_confirmation_required: Boolean.
- status: Enumerated state.
- notes: Tracking notes.

## Assumption Categories
- repo state assumption
- landed commit assumption
- file existence assumption
- mode assumption
- parking assumption
- operator intent assumption
- runtime authorization assumption
- validator scope assumption
- release lock assumption
- v4.8 assumption
- API/network assumption
- deployment assumption
- production assumption

## Assumption Status Values
- Unverified
- Verified
- Operator Confirmed
- Rejected
- Needs Review
- Parked
- Superseded

## Assumption Register Table Template

| Assumption ID | Assumption | Category | Confidence | Runtime Effect | v4.8 Effect | Operator Confirmation Required | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| [ID] | [TEXT] | [CAT] | [CONF] | None | None | [YES/NO] | [STATUS] | - |

## Unsafe Assumption Examples

- assuming “next” means select the next task
- assuming prompt drafting means prompt execution
- assuming high-model availability means runtime authorization
- assuming documentation completion means Station Chief resumes
- assuming v4.8 can start because v4.7 is parked
- assuming check means fix
- assuming builder can add optional files
- assuming prior similar approval applies to new task
- assuming API/network is allowed because dashboard fields mention data
- assuming production readiness means production approval

## Assumption Handling Rules
- if assumption affects scope, stop
- if assumption affects runtime, stop
- if assumption affects validators, stop
- if assumption affects release locks, stop
- if assumption affects v4.8, stop
- if assumption affects APIs/network/deployment/production, stop
- report assumption instead of acting on it

## Runtime Authorization Boundary
- this register is not runtime authorization
- assumption entries do not create runtime behavior
- assumption entries do not create validators
- assumption entries do not create workers
- assumption entries do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
