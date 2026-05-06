# Agent Command Center Runtime Parking Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime parking register.
- This document does not modify runtime behavior.
- This document does not modify release locks.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register documents the parked runtime state so the operator and builder agents can distinguish parked runtime work from allowed non-runtime documentation work.

- this is a register only
- it does not resume Station Chief
- it does not authorize v4.8
- it does not modify runtime files
- it does not modify validators
- it does not modify release locks
- it does not grant permissions
- it does not activate workers

## Parking Principle
- parked means no runtime ladder continuation
- parked means no v4.8 creation
- parked means no runtime file edits
- parked means no validator edits
- parked means no release lock edits
- parked means no runtime-adjacent report creation
- parked means no execution-layer changes
- parked remains active until the operator explicitly resumes Station Chief runtime work

## Current Parking State

| Item | Current Value | Runtime Effect | Operator-Controlled | Notes |
|---|---|---|---|---|
| Station Chief runtime version | v4.7.0 | None | Yes | Locked |
| Parking status | Parked | None | Yes | Active |
| Next reserved runtime layer | v4.8.0 | None | Yes | Reserved |
| v4.8 creation status | Not created | None | Yes | Parked |
| Runtime file modification status | Denied | None | Yes | Parked |
| Validator modification status | Denied | None | Yes | Parked |
| Release lock modification status | Denied | None | Yes | Parked |
| Runtime ladder continuation status | Denied | None | Yes | Parked |
| Current non-runtime work mode | Low-model/Planning | None | Yes | Active |

## Parking Boundary Rules
- do not create v4.8
- do not modify 10_runtime/*
- do not modify scripts/validate_station_chief_runtime_*
- do not modify release locks
- do not modify runtime reports
- do not run runtime layer build prompts
- do not run runtime continuation prompts
- do not create runtime-adjacent files
- do not alter validator delegation
- do not weaken runtime safety boundaries

## Resume Conditions
Station Chief may resume only when the operator explicitly assigns a Station Chief runtime task.

Valid explicit resume examples:
- build Station Chief Runtime v4.8
- fix Station Chief runtime
- modify Station Chief validator
- resume Station Chief ladder
- create non-executing worker routing preview candidate

Invalid resume triggers:
- general discussion
- documentation work
- status checking
- prompt archive work
- dashboard planning
- glossary work
- low-model work
- “what should we do next” style questions
- builder suggestions

## Parking Violation Examples

- **creating any v4.8 file**: Violates parked state. Expected: stop.
- **editing runtime files during documentation work**: Violates parked state. Expected: stop.
- **editing validators during documentation work**: Violates parked state. Expected: stop.
- **changing release locks**: Violates parked state. Expected: stop.
- **creating runtime reports**: Violates parked state. Expected: stop.
- **running runtime layer prompts**: Violates parked state. Expected: stop.
- **adding runtime flags**: Violates parked state. Expected: stop.
- **adding runtime schema**: Violates parked state. Expected: stop.
- **adding worker routing logic**: Violates parked state. Expected: stop.
- **modifying protected exports**: Violates parked state. Expected: stop.

## Allowed While Parked

| Work Type | Allowed While Parked | Runtime Effect | Conditions |
|---|---|---|---|
| documentation-only planning | Allowed | None | Explicit assignment |
| glossary drafting | Allowed | None | Explicit assignment |
| taxonomy drafting | Allowed | None | Explicit assignment |
| status dashboard planning | Allowed | None | Explicit assignment |
| handoff template drafting | Allowed | None | Explicit assignment |
| crosswalk drafting | Allowed | None | Explicit assignment |
| register drafting | Allowed | None | Explicit assignment |
| non-runtime index drafting | Allowed | None | Explicit assignment |

## Denied While Parked

| Work Type | Denied While Parked | Reason | Required Future Authorization |
|---|---|---|---|
| v4.8 runtime build | Denied | Parking active | Runtime build token |
| runtime file modification | Denied | Parking active | Runtime fix token |
| validator modification | Denied | Parking active | Validator redesign token |
| release lock modification | Denied | Parking active | Release lock token |
| worker routing runtime logic | Denied | Parking active | Routing logic token |
| external tool integration | Denied | Parking active | External tool token |
| API/network behavior | Denied | Parking active | External tool token |
| deployment behavior | Denied | Parking active | Deployment token |
| production execution | Denied | Parking active | Production gate token |

## Operator Parking Control
- operator controls when Station Chief parks
- operator controls when Station Chief resumes
- builder does not resume runtime work
- builder does not infer resume authorization
- builder does not recommend resume timing
- builder does not select v4.8 as next task

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
