# Agent Command Center Operator Control Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime operator control register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register consolidates operator-control rules so builder agents remain execution units and do not become roadmap owners.

- this is a governance register only
- it does not select future work
- it does not recommend future work
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Operator Control Principle
- operator controls project direction
- operator selects tasks
- operator approves escalation
- operator decides when Station Chief resumes
- operator decides when v4.8 begins
- operator decides when low-model work is acceptable
- operator decides when high-model work is required
- builder agents execute assigned tasks only

## Operator-Controlled Decisions

- **next task selection**
  - what the operator controls: Choosing the next task.
  - what builder cannot infer: Builder may not assume next steps.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Varies.

- **Station Chief resume decision**
  - what the operator controls: Resuming from v4.7.0.
  - what builder cannot infer: Builder may not assume parking has ended.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Runtime Ladder continuation.

- **v4.8 start decision**
  - what the operator controls: v4.8 initialization.
  - what builder cannot infer: Builder may not create v4.8.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Runtime layer build.

- **runtime modification approval**
  - what the operator controls: Permission to edit runtime files.
  - what builder cannot infer: Builder may not modify 10_runtime/*.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Runtime changes.

- **validator modification approval**
  - what the operator controls: Permission to edit validators.
  - what builder cannot infer: Builder may not modify scripts/validate_*.py.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Safety/Logic changes.

- **release lock modification approval**
  - what the operator controls: Permission to edit release locks.
  - what builder cannot infer: Builder may not modify release locks.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Stability lock drift.

- **file-scope approval**
  - what the operator controls: Defining allowed changed files.
  - what builder cannot infer: Builder may not touch extra files.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Scope expansion.

- **commit/push approval**
  - what the operator controls: Staging, committing, and pushing.
  - what builder cannot infer: Builder may not push forbidden paths.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Remote repository state update.

- **low-model vs high-model mode**
  - what the operator controls: Deciding session model level.
  - what builder cannot infer: Builder may not switch modes on its own.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Enables complex runtime/safety work.

- **worker activation approval**
  - what the operator controls: Permission to activate workers.
  - what builder cannot infer: Builder may not start processes.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Worker execution.

- **task execution approval**
  - what the operator controls: Permission to run tasks.
  - what builder cannot infer: Builder may not execute tasks.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Live system state changes.

- **API/network approval**
  - what the operator controls: API/Network connectivity.
  - what builder cannot infer: Builder may not use APIs/network.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: External action.

- **deployment approval**
  - what the operator controls: Permission to deploy artifacts.
  - what builder cannot infer: Builder may not deploy.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: Env changes.

- **production approval**
  - what the operator controls: Permission to modify production.
  - what builder cannot infer: Builder may not mutate production.
  - required explicit instruction: Mandatory.
  - runtime effect if later authorized: State mutation.

## Builder Non-Authority Areas
- roadmap direction
- next task order
- v4.8 timing
- Station Chief resume timing
- runtime scope
- validator scope
- release lock scope
- production readiness
- deployment readiness
- worker activation
- task execution
- API/network use

## Control Boundary Table

| Decision Area | Controlled By Operator | Builder May Decide | Requires Explicit Instruction | Runtime Effect If Later Authorized |
|---|---|---|---|---|
| next task selection | Yes | No | Yes | Variable |
| Station Chief resume decision | Yes | No | Yes | Ladder continuation |
| v4.8 start decision | Yes | No | Yes | Build layer |
| runtime modification approval | Yes | No | Yes | Runtime changes |
| validator modification approval | Yes | No | Yes | Safety logic change |
| release lock modification approval | Yes | No | Yes | Version shift |
| file-scope approval | Yes | No | Yes | Scope expansion |
| commit/push approval | Yes | No | Yes | Repository update |
| low-model vs high-model mode | Yes | No | Yes | Execution access |
| worker activation approval | Yes | No | Yes | Worker execution |
| task execution approval | Yes | No | Yes | Execution enabled |
| API/network approval | Yes | No | Yes | External access |
| deployment approval | Yes | No | Yes | Environment update |
| production approval | Yes | No | Yes | Production state change |

## No-Freelancing Enforcement

- builder does not suggest next tasks
- builder does not select next tasks
- builder does not create optional deliverables
- builder does not add roadmap commentary
- builder does not merge tasks unless explicitly instructed
- builder does not infer intent beyond prompt scope
- builder stops when ambiguity could create unauthorized changes

## Operator Review Triggers

- unexpected file changes
- runtime file changes
- validator changes
- release lock changes
- v4.8 files appear
- builder suggests next task
- builder adds optional files
- builder broadens scope
- credentials/secrets appear
- APIs/network/deployment/production requested

## Parking Control Rule

Station Chief remains parked at v4.7.0 until the operator explicitly resumes it.

While parked:
- no v4.8
- no runtime edits
- no validator edits
- no release lock edits
- no runtime ladder continuation

## Future Approval Boundary

- approval must be explicit
- approval must name the task
- approval must name the files or layer
- approval must not be inferred from conversation context
- approval for documentation does not authorize runtime
- approval for planning does not authorize execution
- approval for preview does not authorize live behavior

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
