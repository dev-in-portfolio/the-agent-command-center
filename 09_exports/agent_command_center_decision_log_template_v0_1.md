# Agent Command Center Decision Log Template v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime decision log template.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define a reusable operator-controlled template for recording project decisions without allowing builder agents to choose direction.

- this is planning only
- no UI files are created
- no dashboard data files are modified
- no live metrics are connected
- no APIs are called
- no automation is activated

## Decision Log Principle
- decision sections are reference only
- decision fields do not create runtime behavior
- decision status does not grant permission
- decision visibility does not imply execution
- decision status does not select next tasks
- decision planning does not authorize workers, tasks, queues, routing, APIs, deployment, or production

## Decision Entry Fields
- decision_id: Deterministic identifier. Ex: `decision-001`.
- decision_title: Descriptive title. Ex: `v4.7.0-runtime-parking`.
- decision_type: Category. Ex: `Station Chief parking`.
- operator_statement: Explicit operator instruction.
- date_recorded: YYYY-MM-DD.
- related_files: List of relevant files.
- affected_scope: Task/file impact.
- runtime_effect: Explanation. Ex: None.
- v4_8_effect: Explanation. Ex: None.
- status: Enumerated state.
- supersedes: Reference to old decision.
- superseded_by: Reference to new decision.
- operator_review_required: Boolean.
- notes: Tracking notes.

## Decision Status Values
- Drafted
- Recorded
- Active
- Superseded
- Parked
- Rejected
- Needs Review
- Operator Confirmed

## Decision Log Table Template

| Decision ID | Decision Title | Decision Type | Status | Affected Scope | Runtime Effect | v4.8 Effect | Operator Review | Notes |
|---|---|---|---|---|---|---|---|---|
| [ID] | [TITLE] | [TYPE] | [STATUS] | [SCOPE] | None | None | [YES/NO] | - |

## Operator-Controlled Decision Types
- next task selection
- Station Chief parking
- Station Chief resume
- v4.8 start
- runtime modification
- validator modification
- release lock modification
- file-scope approval
- commit/push approval
- low-model mode
- high-model reserved mode
- documentation-only work
- API/network approval
- deployment approval
- production approval

## Builder Non-Decision Boundaries
- builder does not select next tasks
- builder does not set roadmap direction
- builder does not decide v4.8 timing
- builder does not decide Station Chief resume
- builder does not approve runtime changes
- builder does not approve validators
- builder does not approve release locks
- builder does not approve APIs/network/deployment/production

## Decision Review Template
Decision ID:
Date:
Subject:
Operator instruction:
Decision rationale:
Scope affected:
Runtime impact:
Operator confirmation:
Notes:

## Runtime Authorization Boundary
- this decision log template is not runtime authorization
- decision entries do not create runtime behavior
- decision entries do not create validators
- decision entries do not create workers
- decision entries do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
