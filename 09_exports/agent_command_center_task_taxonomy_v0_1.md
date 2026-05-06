# Agent Command Center Task Taxonomy v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime task taxonomy planning only.

This document does not create, modify, or authorize Station Chief runtime behavior.

## Purpose

This document defines task categories, task boundaries, risk levels, approval expectations, and worker/task relationships without activating anything.

- tasks are planning records only at this stage
- no tasks are executed
- no tasks are enqueued
- no workers are started
- no routing occurs
- no APIs are called
- no production behavior is authorized

## Core Task Principle

- a task definition is not task execution
- a task label is not task assignment
- a task assignment record is not task execution
- a queue preview is not a real queue
- a routing preview is not live routing
- documentation does not authorize runtime behavior
- approval for one task category does not imply approval for another category

## Task Category Overview

- **documentation task**
  - definition: Creation of markdown documentation, manuals, or plans.
  - examples: README.md, protocol drafts.
  - current status: Allowed
  - risk level: Risk 0
  - allowed behavior: Writing markdown files.
  - denied behavior: Execution, tool use.
  - future approval needed: None

- **planning task**
  - definition: Creation of structural, taxonomy, or roadmap planning files.
  - examples: Architecture maps, taxonomy drafts.
  - current status: Allowed
  - risk level: Risk 1
  - allowed behavior: Writing markdown planning.
  - denied behavior: Execution.
  - future approval needed: None

- **glossary task**
  - definition: Compiling term definitions and labels.
  - examples: Worker family glossary.
  - current status: Allowed
  - risk level: Risk 1
  - allowed behavior: Updating glossary documents.
  - denied behavior: None.
  - future approval needed: None

- **taxonomy task**
  - definition: Designing and structuring task/worker categories.
  - examples: Task hierarchy updates.
  - current status: Allowed
  - risk level: Risk 1
  - allowed behavior: Designing taxonomies.
  - denied behavior: None.
  - future approval needed: None

- **classification task**
  - definition: Tagging tasks with risk levels and capability needs.
  - examples: Risk tagging, permission level assignment.
  - current status: Allowed (design only)
  - risk level: Risk 2
  - allowed behavior: Designing classification schemas.
  - denied behavior: Assignment, execution.
  - future approval needed: Task assignment authorization

- **review task**
  - definition: Auditing designs or local metadata records.
  - examples: Permission matrix review, safety review.
  - current status: Allowed
  - risk level: Risk 2
  - allowed behavior: Examining records.
  - denied behavior: Code modification, system state changes.
  - future approval needed: Post-action audit approval

- **safety review task**
  - definition: Reviewing task safety boundaries and risk levels.
  - examples: Boundary matrix drafting.
  - current status: Allowed
  - risk level: Risk 2
  - allowed behavior: Designing safety schemas.
  - denied behavior: Execution.
  - future approval needed: Audit record creation approval

- **audit task**
  - definition: Post-execution examination of local metadata.
  - examples: Audit record creation.
  - current status: Allowed (design only)
  - risk level: Risk 2
  - allowed behavior: Defining audit criteria.
  - denied behavior: System access.
  - future approval needed: Audit record creation approval

- **closeout task**
  - definition: Finalizing task phase and persisting the audit record.
  - examples: Task closeout record creation.
  - current status: Allowed (with tokens)
  - risk level: Risk 2
  - allowed behavior: Writing closeout records.
  - denied behavior: Execution.
  - future approval needed: Task closeout approval

- **local record task**
  - definition: Creating deterministic local JSON metadata structures.
  - examples: Manifest creation.
  - current status: Allowed (with tokens)
  - risk level: Risk 1
  - allowed behavior: Memory-based JSON structure.
  - denied behavior: Disk write.
  - future approval needed: Specific approval token

- **local artifact task**
  - definition: Persisting JSON metadata to disk.
  - examples: Writing proof artifacts.
  - current status: Allowed (with tokens)
  - risk level: Risk 3
  - allowed behavior: Writing to approved directories.
  - denied behavior: Modifying codebase.
  - future approval needed: Local artifact write approval

- **cleanup task**
  - definition: Safely removing localized artifacts.
  - examples: Deleting artifact directory.
  - current status: Allowed (with tokens)
  - risk level: Risk 4
  - allowed behavior: Deleting target directories.
  - denied behavior: Broad repository deletions.
  - future approval needed: Local cleanup token

- **worker activation record task**
  - definition: Creating non-executing worker metadata records.
  - examples: Designating a worker template.
  - current status: Allowed
  - risk level: Risk 5
  - allowed behavior: Generating record metadata.
  - denied behavior: Starting processes.
  - future approval needed: Worker activation token

- **task assignment record task**
  - definition: Linking tasks to worker templates.
  - examples: Assignment candidate creation.
  - current status: Allowed
  - risk level: Risk 6
  - allowed behavior: Generating task assignment metadata.
  - denied behavior: Task assignment execution.
  - future approval needed: Task assignment token

- **queue preview task**
  - definition: Simulating queue order.
  - examples: Generating queue placement metadata.
  - current status: Allowed
  - risk level: Risk 7
  - allowed behavior: Generating queue records.
  - denied behavior: Real queueing/scheduling.
  - future approval needed: Queue preview token

- **routing preview task**
  - definition: Simulating worker routing.
  - examples: Routing simulation record creation.
  - current status: Not allowed
  - risk level: Risk 8
  - allowed behavior: Planning routing logic.
  - denied behavior: Live routing.
  - future approval needed: Routing preview token

- **tool simulation task**
  - definition: Local safe tool-use logic simulation.
  - examples: Hash calculation sandbox simulation.
  - current status: Forbidden
  - risk level: Risk 9
  - allowed behavior: Planning sandbox protocols.
  - denied behavior: External tool invocation.
  - future approval needed: Tool simulation token

- **external tool candidate task**
  - definition: Defining an external tool invocation flow.
  - examples: API call dry-run plan.
  - current status: Forbidden
  - risk level: Risk 9
  - allowed behavior: Planning API schemas.
  - denied behavior: Real API calls.
  - future approval needed: External tool token

- **deployment readiness task**
  - definition: Validating deployment state.
  - examples: Deployment check drafting.
  - current status: Forbidden
  - risk level: Risk 10
  - allowed behavior: Drafting checklists.
  - denied behavior: Deploying.
  - future approval needed: Deployment token

- **production candidate task**
  - definition: Defining a production state modification.
  - examples: Production dry-run manifest.
  - current status: Forbidden
  - risk level: Risk 10
  - allowed behavior: Designing production schemas.
  - denied behavior: Mutating production.
  - future approval needed: Production token

## Task Risk Levels

- Risk 0 — Documentation-only task
  - description: Creation of planning, structural, and descriptive markdown documents.
  - labels: `docs-plan-task`, `readme-task`
  - current status: Allowed
  - approval: Implied
  - denied: Execution

- Risk 1 — Planning / taxonomy task
  - description: Creation of architecture designs and hierarchies.
  - labels: `taxonomy-planning-task`, `architecture-map-task`
  - current status: Allowed
  - approval: Implied
  - denied: Execution

- Risk 2 — Local metadata task
  - description: Generating deterministic JSON metadata records.
  - labels: `manifest-draft-task`, `metadata-plan-task`
  - current status: Allowed
  - approval: Token
  - denied: Execution, write

- Risk 3 — Local file artifact task
  - description: Writing JSON artifacts to disk.
  - labels: `proof-artifact-task`, `write-record-task`
  - current status: Allowed
  - approval: Token
  - denied: Execution

- Risk 4 — Local cleanup task
  - description: Deleting localized artifact artifacts.
  - labels: `local-cleanup-task`, `artifact-remove-task`
  - current status: Allowed
  - approval: Token
  - denied: Codebase deletion

- Risk 5 — Worker record task
  - description: Creating worker templates.
  - labels: `worker-activate-task`, `worker-define-task`
  - current status: Allowed
  - approval: Token
  - denied: Execution

- Risk 6 — Task assignment record task
  - description: Creating task assignment metadata.
  - labels: `task-assign-task`, `task-assignment-record-task`
  - current status: Allowed
  - approval: Token
  - denied: Execution

- Risk 7 — Queue preview task
  - description: Simulating queue order.
  - labels: `queue-preview-task`, `queue-simulation-task`
  - current status: Allowed
  - approval: Token
  - denied: Queueing

- Risk 8 — Routing preview task
  - description: Simulating routing logic.
  - labels: `routing-preview-task`, `routing-simulation-task`
  - current status: Not allowed
  - approval: Token
  - denied: Routing

- Risk 9 — Tool simulation / external tool candidate task
  - description: Simulating tool logic.
  - labels: `tool-simulate-task`, `external-api-preview-task`
  - current status: Forbidden
  - approval: Token
  - denied: API access

- Risk 10 — Production candidate task
  - description: Defining production changes.
  - labels: `production-candidate-task`, `deploy-plan-task`
  - current status: Forbidden
  - approval: Token
  - denied: Production execution

## Task State Model

- proposed: Planning state. Allowed. Denied: Execution.
- drafted: Ready for review. Allowed. Denied: Recording.
- classified: Tagged for risk. Allowed. Denied: Recording.
- permission-reviewed: Security approved. Allowed. Denied: Writing.
- safety-reviewed: Boundary reviewed. Allowed. Denied: Writing.
- locally recorded: Metadata finalized. Allowed. Denied: Execution.
- locally written: Artifact persisted. Allowed. Denied: Execution.
- previewed: Simulated state. Allowed. Denied: Execution.
- assigned as record: Metadata linked to worker. Allowed. Denied: Execution.
- queued as preview: Simulated queue entry. Allowed. Denied: Enqueue.
- routed as preview: Simulated routing. Not allowed. Denied: Execution.
- execution-candidate: Candidate for execution. Forbidden. Denied: Execution.
- audited: Audited closeout. Forbidden. Denied: Execution.
- closed out: Phase archived. Forbidden. Denied: Execution.
- retired: Phase finished. Forbidden. Denied: Execution.

## Task Label Rules

- labels must be descriptive
- labels must be lowercase-friendly
- labels must avoid secrets
- labels must avoid credentials
- labels must avoid production identifiers
- labels must not imply execution
- labels must not imply routing
- labels must not imply deployment
- labels must not imply approval

Examples:
- documentation-cleanup-task
- permission-matrix-review-task
- safety-boundary-taxonomy-task
- worker-family-glossary-task
- queue-preview-record-task
- routing-preview-record-task

## Task-to-Worker Relationship

- workers are design records only at this stage
- assigning a task to a worker record does not start the worker
- assigning a task to a worker record does not execute the task
- queue preview does not enqueue the task
- routing preview does not route live work
- worker/task links are metadata only unless separately escalated

## Task Permission Mapping Table

| Task Category | Risk Level | Documentation Allowed | Local Record Allowed | Local File Write Allowed | Cleanup Allowed | Worker Start Allowed | Queue Write Allowed | Routing Allowed | Execution Allowed | Production Allowed | Current Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| documentation task | Risk 0 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| planning task | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| glossary task | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| taxonomy task | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| classification task | Risk 2 | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| review task | Risk 2 | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| safety review task | Risk 2 | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| audit task | Risk 2 | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| closeout task | Risk 2 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| local record task | Risk 2 | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| local artifact task | Risk 3 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| cleanup task | Risk 4 | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Allowed |
| worker activation record task | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| task assignment record task | Risk 6 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| queue preview task | Risk 7 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| routing preview task | Risk 8 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Future gated |
| tool simulation task | Risk 9 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Forbidden |
| external tool candidate task | Risk 9 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Forbidden |
| deployment readiness task | Risk 10 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Forbidden |
| production candidate task | Risk 10 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Forbidden |

## Always-Denied Task Actions

- task execution
- task enqueueing
- queued job execution
- live task assignment
- live worker routing
- live orchestration
- worker process start
- daemon start
- scheduler start
- subprocess start
- real queue creation
- queue writes
- scheduler writes
- cron writes
- API calls
- network access
- socket access
- DNS resolution
- credential use
- credential vault access
- secret reads
- environment variable reads
- deployment
- deployment rollback
- production execution
- production activation
- database mutation
- external tool invocation
- full 47,250-worker workforce activation

## Task Escalation Rules

- documentation tasks do not escalate automatically
- planning tasks do not become runtime tasks automatically
- local record tasks do not authorize local file writes automatically
- local file writes do not authorize cleanup automatically
- task assignment records do not authorize task execution
- queue preview records do not authorize real queues
- routing preview records do not authorize live routing
- tool simulation does not authorize external tools
- external tool candidates do not authorize production
- production candidates require separate explicit operator approval

## Low-Model-Safe Task Work Categories

- documentation task drafting
- glossary task drafting
- taxonomy task drafting
- task label cleanup
- task category formatting
- risk wording cleanup
- matrix formatting
- documentation consistency review

## High-Model Reserved Task Work Categories

- Station Chief v4.8+
- runtime task classification logic
- validator redesign
- worker routing logic
- external tool task logic
- production task candidates
- architecture refactors

## Runtime Authorization Boundary

This document is not runtime authorization.

- task taxonomy does not create tasks
- task labels do not execute tasks
- task categories do not grant permissions
- task maps do not start workers
- task planning does not create queues
- task planning does not authorize routing
- future approval still requires explicit operator instruction

## Final Note

This document is planning-only and should not be treated as runtime authorization.
