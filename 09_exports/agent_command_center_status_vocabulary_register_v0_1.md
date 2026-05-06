# Agent Command Center Status Vocabulary Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime status vocabulary register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register defines status words used across reports, checks, handoffs, dashboards, parking state, and landing audits.

- this is vocabulary only
- it does not create runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Status Vocabulary Principle
- status labels are descriptive only
- status labels do not authorize execution
- status labels do not grant permissions
- status labels do not select next tasks
- status labels do not create runtime behavior
- status labels do not create v4.8

## Core Status Terms

- **landed**: Version or file successfully integrated into master.
- **not landed**: Version or file pending integration.
- **parked**: Station Chief runtime version locked.
- **in progress**: Active planning session.
- **blocked**: Security/safety condition prevents further action.
- **clean landing**: Commit check passed.
- **dirty state**: Uncommitted changes detected.
- **scope drift**: Unrequested file changes detected.
- **runtime drift**: Unrequested runtime file changes.
- **validator drift**: Unrequested validator file changes.
- **release lock drift**: Unrequested release lock changes.
- **forbidden path touched**: Attempted access to forbidden path.
- **planning-only**: Documentation context.
- **runtime authorization**: Permission to change system state.
- **future gated**: Feature locked behind future token.
- **reserved**: Future capability.
- **denied**: Explicit prohibition.
- **allowed**: Explicit permission.
- **operator-controlled**: Requires manual authorization.
- **builder freelancing**: Unauthorized task modification/selection.

## Status Table

| Status Term | Meaning | Runtime Effect | Authorizes Future Work | Operator Review Needed |
|---|---|---|---|---|
| landed | Integrated into master | None | No | No |
| not landed | Pending integration | None | No | No |
| parked | Version locked | None | No | Yes |
| in progress | Active planning | None | No | No |
| blocked | Security condition | None | No | Yes |
| clean landing | Commit check passed | None | No | No |
| dirty state | Uncommitted changes | None | No | Yes |
| scope drift | Unrequested changes | None | No | Yes |
| runtime drift | Unrequested runtime changes | None | No | Yes |
| validator drift | Unrequested validator changes | None | No | Yes |
| release lock drift | Unrequested lock changes | None | No | Yes |
| forbidden path touched | Forbidden access | None | No | Yes |
| planning-only | Documentation context | None | No | No |
| runtime authorization | System state access | Varies | Yes | Yes |
| future gated | Feature pending | None | No | No |
| reserved | Future capability | None | No | No |
| denied | Explicit prohibition | None | No | Yes |
| allowed | Explicit permission | None | No | No |
| operator-controlled | Requires authorization | None | No | Yes |
| builder freelancing | Freelancing detected | None | No | Yes |

## Progress Vocabulary

- **overall project progress**: Tracks movement toward goal.
- **runtime safety spine**: Tracks status of runtime validation chain.
- **governance / operating doctrine**: Tracks status of planning documents.
- **worker architecture design**: Tracks status of worker family maps.
- **controlled local execution capability**: Tracks status of local artifact/preview capabilities.
- **actual live worker/tool automation**: Tracks status of live runtime enablement.
- **full command center vision**: Tracks aggregate project completion.

## Parking Vocabulary

- **parked**: Version locked. Denial: No. Authority: Operator.
- **reserved**: Future work designation. Denial: No. Authority: Operator.
- **not created**: File/layer status. Denial: Yes. Authority: Operator.
- **explicitly assigned**: Required authorization. Denial: No. Authority: Operator.
- **resume**: Re-enabling ladder progression. Denial: Yes. Authority: Operator.
- **runtime ladder**: Multi-stage rollout. Denial: Yes. Authority: Operator.
- **runtime layer**: Versioned unit. Denial: Yes. Authority: Operator.
- **v4.8**: Next version. Denial: Yes. Authority: Operator.

## Landing Vocabulary

- **landed**: Integrated. Audit use: Yes. Effect: None.
- **clean landing**: Checked successfully. Audit use: Yes. Effect: None.
- **visible commit**: Commit in history. Audit use: Yes. Effect: None.
- **latest master**: HEAD state. Audit use: Yes. Effect: None.
- **created file**: New artifact. Audit use: Yes. Effect: None.
- **modified file**: Artifact change. Audit use: Yes. Effect: None.
- **runtime untouched**: Status pass. Audit use: Yes. Effect: None.
- **validators untouched**: Status pass. Audit use: Yes. Effect: None.
- **release locks untouched**: Status pass. Audit use: Yes. Effect: None.
- **no builder freelancing**: Behavior confirmation. Audit use: Yes. Effect: None.

## Dangerous Misread Terms

- **next**: Safe: Referring to next sequence. Unsafe: Selecting next roadmap item. Action: Stop.
- **continue**: Safe: Resuming non-runtime work. Unsafe: Resuming runtime ladder. Action: Stop.
- **check**: Safe: Verification. Unsafe: Verification implying fix authorization. Action: Stop.
- **prompt**: Safe: Labeling a plan. Unsafe: Executing a prompt. Action: Stop.
- **fix**: Safe: Targeted repair. Unsafe: Broad refactor. Action: Stop.
- **wait**: Safe: Parking confirmation. Unsafe: Inferred permission. Action: Stop.
- **easier tasks**: Safe: Glossary formatting. Unsafe: Roadmap selection. Action: Stop.
- **high-model**: Safe: Capability note. Unsafe: Runtime authorization. Action: Stop.
- **low-model**: Safe: Governance mode. Unsafe: Roadmap planning. Action: Stop.
- **runtime**: Safe: Reference only. Unsafe: Modification. Action: Stop.
- **worker**: Safe: Design category. Unsafe: Process starting. Action: Stop.
- **queue**: Safe: Simulation record. Unsafe: Live system queue. Action: Stop.
- **routing**: Safe: Routing preview. Unsafe: Live task assignment. Action: Stop.
- **activation**: Safe: Record labeling. Unsafe: Live execution. Action: Stop.

## Runtime Authorization Boundary
- this register is not runtime authorization
- vocabulary labels do not create runtime behavior
- vocabulary labels do not create validators
- vocabulary labels do not create workers
- vocabulary labels do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
