# Agent Command Center Risk Register Template v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime planning-only risk register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define a reusable planning-only risk register for tracking documentation, governance, runtime-adjacent, security, and operator-control risks.

- this is a register only
- it does not create live risk analysis
- it does not connect to APIs
- it does not read repo state automatically
- it does not modify runtime
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Risk Register Principle
- risks are planning records only at this stage
- risk entries do not authorize runtime behavior
- risk entries do not grant permission
- risk entries do not imply execution
- risk entries do not select next tasks
- risk planning does not authorize workers, tasks, queues, routing, APIs, deployment, or production

## Risk Entry Fields
- risk_id: Deterministic identifier. Ex: `risk-001`.
- risk_title: Descriptive title. Ex: `unauthorized-v4-8-creation`.
- risk_category: Category family. Ex: `v4.8 creation risk`.
- description: Explanation. Ex: `v4.8 created accidentally`.
- severity: Numeric severity. Ex: Risk 7.
- likelihood: Estimate. Ex: Low.
- impact: Estimate. Ex: High.
- trigger: Event marker. Ex: `v4.8 file detected`.
- affected_scope: Task/file impact.
- runtime_effect: Explanation. Ex: None.
- mitigation_note: Action. Ex: `validation scripts`.
- owner: Operator.
- status: Enumerated state.
- operator_review_required: Boolean.
- notes: Tracking notes. Ex: -

## Risk Categories
- documentation scope risk
- builder freelancing risk
- prompt ambiguity risk
- runtime drift risk
- validator drift risk
- release lock drift risk
- v4.8 accidental creation risk
- protected export drift risk
- credential/secret exposure risk
- API/network risk
- deployment risk
- production risk
- full workforce activation risk
- model capability mismatch risk
- continuity loss risk

## Risk Severity Scale
- Risk 0 — Documentation wording issue
- Risk 1 — Minor formatting issue
- Risk 2 — Extra documentation file risk
- Risk 3 — Existing planning doc modification risk
- Risk 4 — Protected non-runtime export risk
- Risk 5 — Runtime-adjacent drift risk
- Risk 6 — Validator/release lock drift risk
- Risk 7 — v4.8 creation risk
- Risk 8 — API/network/credential risk
- Risk 9 — Deployment/production risk
- Risk 10 — Live worker/task/workforce activation risk

## Risk Status Values
- Open
- Watching
- Mitigated
- Blocked
- Needs Operator Review
- Closed
- Parked
- Future Gated

## Risk Register Table Template

| Risk ID | Risk Title | Category | Severity | Likelihood | Impact | Status | Runtime Effect | Operator Review | Notes |
|---|---|---|---|---|---|---|---|---|---|
| [ID] | [TITLE] | [CAT] | [LEVEL] | [LIKE] | [IMP] | [STATUS] | None | [YES/NO] | - |

## Risk Response Rules
- risks do not authorize fixes
- risks do not authorize runtime changes
- risks do not authorize validator changes
- risks do not authorize v4.8
- risks do not authorize API/network/deployment/production
- builder must stop on high-severity active risk if it affects current scope

## Runtime Authorization Boundary
- this risk register template is not runtime authorization
- risk entries do not create runtime behavior
- risk entries do not create validators
- risk entries do not create workers
- risk entries do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
