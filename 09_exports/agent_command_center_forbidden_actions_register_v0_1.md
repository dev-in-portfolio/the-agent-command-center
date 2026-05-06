# Agent Command Center Forbidden Actions Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime forbidden-actions register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register consolidates forbidden actions across non-runtime planning, runtime parking, builder execution, permission boundaries, safety boundaries, and operator governance.

- this is a register only
- it does not enforce runtime behavior
- it does not modify validators
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Forbidden Action Principle
- forbidden means denied unless explicitly approved by the operator in a separate task
- forbidden in documentation means not authorized by the document
- forbidden action labels do not create validators
- forbidden action registers do not modify runtime enforcement
- approval for one action does not imply approval for another action
- approval for documentation does not imply approval for execution

## Master Forbidden Action List

- Station Chief v4.8 creation unless explicitly assigned
- Station Chief runtime modification unless explicitly assigned
- validator modification unless explicitly assigned
- release lock modification unless explicitly assigned
- runtime report creation unless explicitly assigned
- worker process start
- worker activation
- worker process spawning
- daemon start
- scheduler start
- subprocess start
- task execution
- task enqueueing
- queued job execution
- live task assignment
- live worker routing
- live orchestration
- real queue creation
- queue writes
- scheduler writes
- cron writes
- API calls
- network access
- socket access
- DNS resolution
- outbound connections
- inbound connections
- webhook calls
- credential use
- credential vault access
- secret reads
- environment variable reads
- token reads
- API key reads
- OAuth use
- service account use
- deployment
- deployment rollback
- production execution
- production activation
- database mutation
- external tool invocation
- GitHub push by workers
- GitHub API actions by workers
- full 47,250-worker workforce activation

## Forbidden Action Categories

- **Runtime Forbidden Actions**
  - definition: Any action creating, modifying, or activating Station Chief runtime.
  - examples: Creating v4.8, editing release locks.
  - why forbidden: Violates parking rules.
  - current status: Forbidden
  - required future authorization: Explicit runtime task assignment.

- **Validator Forbidden Actions**
  - definition: Any modification of existing runtime validators.
  - examples: Editing scripts/validate_*.py.
  - why forbidden: System integrity.
  - current status: Forbidden
  - required future authorization: Validator redesign token.

- **Release Lock Forbidden Actions**
  - definition: Any modification to runtime version locks.
  - examples: Modifying station_chief_release_lock.py.
  - why forbidden: Version stability.
  - current status: Forbidden
  - required future authorization: Version release token.

- **Worker Forbidden Actions**
  - definition: Starting, spawning, or activating worker processes.
  - examples: worker.start, daemon start.
  - why forbidden: Runtime safety.
  - current status: Forbidden
  - required future authorization: Worker activation token.

- **Task Forbidden Actions**
  - definition: Executing or enqueueing system tasks.
  - examples: task execution, task enqueueing.
  - why forbidden: Runtime control.
  - current status: Forbidden
  - required future authorization: Task execution token.

- **Queue Forbidden Actions**
  - definition: Writing to or creating real system queues.
  - examples: real queue creation, queue writes.
  - why forbidden: Execution integrity.
  - current status: Forbidden
  - required future authorization: Queue creation token.

- **Routing Forbidden Actions**
  - definition: Live orchestration of worker tasks.
  - examples: live task assignment, live worker routing.
  - why forbidden: System stability.
  - current status: Forbidden
  - required future authorization: Routing token.

- **Tool / API Forbidden Actions**
  - definition: Interacting with external systems/services.
  - examples: API calls, network access, external tool invocation.
  - why forbidden: Security boundaries.
  - current status: Forbidden
  - required future authorization: External tool token.

- **Credential / Secret Forbidden Actions**
  - definition: Handling sensitive access information.
  - examples: credential use, secret reads.
  - why forbidden: Security risk.
  - current status: Forbidden
  - required future authorization: Credential token.

- **Deployment Forbidden Actions**
  - definition: Moving artifacts or running deployment scripts.
  - examples: deployment, deployment rollback.
  - why forbidden: Operational control.
  - current status: Forbidden
  - required future authorization: Deployment token.

- **Production Forbidden Actions**
  - definition: Direct manipulation of production environments.
  - examples: production execution, database mutation.
  - why forbidden: Production integrity.
  - current status: Forbidden
  - required future authorization: Production token.

- **Builder Governance Forbidden Actions**
  - definition: Builder-initiated roadmap changes.
  - examples: builder-selected next task, recommending roadmap direction.
  - why forbidden: Operator authority.
  - current status: Forbidden
  - required future authorization: Operator instruction.

- **File Scope Forbidden Actions**
  - definition: Creating files outside the allowed list.
  - examples: optional files, extra planning docs.
  - why forbidden: Scope expansion.
  - current status: Forbidden
  - required future authorization: Operator instruction.

## Forbidden Action Severity Scale

- **Severity 0 — Documentation scope issue**
  - description: Minor planning scope overreach.
  - example: Creating an optional planning file.
  - builder response: stop
  - commit allowed: no

- **Severity 1 — Extra file issue**
  - description: Unauthorized file generation.
  - example: Adding a file not in task.
  - builder response: stop
  - commit allowed: no

- **Severity 2 — Existing planning doc modification issue**
  - description: Editing unapproved documents.
  - example: Changing an existing planning file.
  - builder response: stop
  - commit allowed: no

- **Severity 3 — Runtime-adjacent issue**
  - description: Touching runtime periphery.
  - example: Changing registry versions.
  - builder response: stop
  - commit allowed: no

- **Severity 4 — Validator issue**
  - description: Modifying validation logic.
  - example: Editing script/validate_v4_7.py.
  - builder response: stop
  - commit allowed: no

- **Severity 5 — Release lock issue**
  - description: Modifying stability locks.
  - example: Editing release_lock.py.
  - builder response: stop
  - commit allowed: no

- **Severity 6 — Worker/task execution issue**
  - description: Unauthorized execution.
  - example: starting worker processes.
  - builder response: stop
  - commit allowed: no

- **Severity 7 — Queue/routing issue**
  - description: Manipulating queues or routing.
  - example: writing to a queue.
  - builder response: stop
  - commit allowed: no

- **Severity 8 — API/network issue**
  - description: External system interaction.
  - example: API call.
  - builder response: stop
  - commit allowed: no

- **Severity 9 — Credential/secret/deployment issue**
  - description: Sensitive/deployment actions.
  - example: reading environment variables.
  - builder response: stop
  - commit allowed: no

- **Severity 10 — Production/workforce activation issue**
  - description: Production mutation or workforce activation.
  - example: full 47,250-worker activation.
  - builder response: stop
  - commit allowed: no

## Forbidden Action Response Table

| Forbidden Action | Severity | Expected Builder Response | Commit Allowed | Push Allowed | Operator Review Required |
|---|---|---|---|---|---|
| Station Chief v4.8 creation | Severity 10 | STOP | No | No | Yes |
| Station Chief runtime modification | Severity 10 | STOP | No | No | Yes |
| validator modification | Severity 4 | STOP | No | No | Yes |
| release lock modification | Severity 5 | STOP | No | No | Yes |
| runtime report creation | Severity 3 | STOP | No | No | Yes |
| worker process start | Severity 6 | STOP | No | No | Yes |
| worker activation | Severity 6 | STOP | No | No | Yes |
| task execution | Severity 6 | STOP | No | No | Yes |
| task enqueueing | Severity 6 | STOP | No | No | Yes |
| real queue creation | Severity 7 | STOP | No | No | Yes |
| queue writes | Severity 7 | STOP | No | No | Yes |
| scheduler writes | Severity 7 | STOP | No | No | Yes |
| API calls | Severity 8 | STOP | No | No | Yes |
| network access | Severity 8 | STOP | No | No | Yes |
| credential use | Severity 9 | STOP | No | No | Yes |
| secret reads | Severity 9 | STOP | No | No | Yes |
| environment variable reads | Severity 9 | STOP | No | No | Yes |
| deployment | Severity 9 | STOP | No | No | Yes |
| production execution | Severity 10 | STOP | No | No | Yes |
| database mutation | Severity 10 | STOP | No | No | Yes |

## Builder Stop Requirement
- builder must stop when forbidden paths change
- builder must stop when unexpected files appear
- builder must stop when v4.8 files appear
- builder must stop when runtime files change during documentation work
- builder must stop when validators change during documentation work
- builder must stop when task requires APIs/network/credentials/secrets/deployment/production
- builder must stop when prompt ambiguity could cause unauthorized scope expansion

## Operator Authority Boundary
- operator may explicitly override a forbidden action in a separate task
- override must be specific
- override must identify file targets
- override must identify allowed behavior
- override for one action does not authorize other actions
- builder may not infer override from context

## Documentation Boundary
- this register documents forbidden actions
- this register does not enforce them in code
- this register does not create validators
- this register does not modify runtime
- this register does not grant or deny runtime permissions by itself
- future enforcement requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
