# Agent Command Center Session Continuity Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime session continuity protocol.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define how continuity is preserved across sessions, model changes, prompt handoffs, parked runtime state, and operator-controlled work shifts.

- this is a protocol only
- it does not create command execution logic
- it does not create runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Continuity Principle
- switching models does not change project authority
- lower-model sessions remain documentation-only unless explicitly assigned otherwise
- high-model availability does not authorize runtime work
- model exhaustion does not authorize shortcuts
- prompt drafting does not execute prompts
- prompt queues do not select task priority
- Station Chief parking persists across sessions
- Station Chief resumes only by explicit operator assignment

## Session State Fields

- **current_repo**: Repository name. Ex: dev-in-portfolio/agent-command-center. Runtime effect: None. Authorizes: No.
- **current_branch**: Branch name. Ex: master. Runtime effect: None. Authorizes: No.
- **current_master_commit**: Latest hash. Ex: [HASH]. Runtime effect: None. Authorizes: No.
- **station_chief_current_version**: Version (4.7.0). Ex: 4.7.0. Runtime effect: None. Authorizes: No.
- **station_chief_parking_status**: State (Parked). Ex: Parked. Runtime effect: None. Authorizes: No.
- **v4_8_created**: Init status. Ex: False. Runtime effect: None. Authorizes: No.
- **latest_landed_bundle**: Most recent bundle. Ex: Control Registers Bundle. Runtime effect: None. Authorizes: No.
- **pending_operator_assigned_prompt**: Task queue item. Ex: None. Runtime effect: None. Authorizes: No.
- **current_mode**: Session mode. Ex: Low-Model Documentation Mode. Runtime effect: None. Authorizes: No.
- **low_model_mode_active**: Mode check. Ex: True. Runtime effect: None. Authorizes: No.
- **high_model_reserved_mode_active**: Mode check. Ex: False. Runtime effect: None. Authorizes: No.
- **runtime_files_changed**: Status. Ex: False. Runtime effect: None. Authorizes: No.
- **validators_changed**: Status. Ex: False. Runtime effect: None. Authorizes: No.
- **release_locks_changed**: Status. Ex: False. Runtime effect: None. Authorizes: No.
- **builder_freelancing_detected**: Behavior tracking. Ex: False. Runtime effect: None. Authorizes: No.
- **operator_review_required**: Decision status. Ex: False. Runtime effect: None. Authorizes: No.

## Session Handoff Template

Repo:
Branch:
Latest visible commit:
Latest landed bundle:
Station Chief version:
Parking status:
v4.8 created:
Runtime files changed:
Validators changed:
Release locks changed:
Current mode:
Pending operator-assigned prompt:
Builder-selected next task:
Planning-only confirmation:
Operator review required:
Notes:

## Model Switch Continuity Rules
- switching models does not change project authority
- lower-model sessions remain documentation-only unless explicitly assigned otherwise
- high-model availability does not authorize runtime work
- model exhaustion does not authorize shortcuts
- prompt drafting does not execute prompts
- prompt queues do not select task priority

## Prompt Continuity Rules
- Station Chief parking persists across sessions
- Station Chief resumes only by explicit operator assignment
- Runtime prompts are parked
- Documentation-only planning is allowed
- No runtime execution in continuity

## Parking Continuity Rules
- Station Chief runtime is parked at v4.7.0.
- While parked: no v4.8, no runtime edits, no ladder continuation.
- Parking persists across session handoffs.

## Continuity Failure Examples
- forgetting Station Chief is parked
- treating prior prompt as authorization
- treating “next” as task selection
- assuming v4.8 is approved
- modifying runtime during documentation work
- modifying validators during documentation work
- recommending roadmap direction

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- continuity fields do not create runtime behavior
- continuity fields do not create validators
- continuity fields do not create workers
- continuity fields do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
