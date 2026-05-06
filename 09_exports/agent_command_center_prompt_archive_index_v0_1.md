# Agent Command Center Prompt Archive Index v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime prompt archive indexing only.

This document does not create, modify, run, or authorize Station Chief runtime behavior.

## Purpose

This document defines how prompts should be categorized, named, archived, and referenced so the operator can track prompt families without builder agents choosing roadmap direction.

- this is an index structure only
- this document does not create executable prompts
- this document does not run prompts
- this document does not authorize runtime behavior
- this document does not grant permissions
- this document does not activate workers
- this document does not authorize v4.8

## Prompt Archive Principle

- prompt archive entries are references only
- archived prompt names do not imply approval
- archived prompt names do not imply execution
- prompt categories do not grant permissions
- prompt categories do not create workers
- prompt categories do not create tasks
- prompt categories do not create queues
- prompt categories do not create routes
- prompt categories do not create validators
- prompt categories do not create runtime layers

## Prompt Category Families

- **Station Chief Runtime Prompts**
  - definition: Prompts for building/validating Station Chief runtime.
  - purpose: Runtime ladder progression.
  - example prompt label: `station-chief-v4-8-runtime-build-prompt`
  - current allowed status: Parked
  - runtime effect: Runtime modification
  - denied behavior: Execution, tool use
  - approval requirement: Runtime build token

- **Station Chief Fix Prompts**
  - definition: Prompts for fixing runtime issues.
  - purpose: Runtime stability.
  - example prompt label: `station-chief-v4-7-fix-prompt`
  - current allowed status: Parked
  - runtime effect: Runtime modification
  - denied behavior: Unauthorized modification
  - approval requirement: Fix token

- **Station Chief Check Prompts**
  - definition: Prompts for validating runtime state.
  - purpose: Runtime verification.
  - example prompt label: `station-chief-v4-7-check-prompt`
  - current allowed status: Allowed (smoke tests)
  - runtime effect: None
  - denied behavior: Execution
  - approval requirement: None

- **Non-Runtime Planning Prompts**
  - definition: General planning and architectural prompts.
  - purpose: Strategic alignment.
  - example prompt label: `non-runtime-architecture-plan-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: System activation
  - approval requirement: None

- **Governance Documentation Prompts**
  - definition: Prompts for drafting governance/authority docs.
  - purpose: Operator control.
  - example prompt label: `operator-authority-protocol-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Runtime policy modification
  - approval requirement: None

- **Worker Architecture Prompts**
  - definition: Prompts for mapping workforce structure.
  - purpose: Worker family design.
  - example prompt label: `non-runtime-worker-architecture-map-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Worker activation
  - approval requirement: None

- **Permission Matrix Prompts**
  - definition: Prompts for designing access levels.
  - purpose: Permission mapping.
  - example prompt label: `permission-matrix-documentation-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Permission grant
  - approval requirement: None

- **Safety Boundary Prompts**
  - definition: Prompts for mapping safety boundaries.
  - purpose: Risk mitigation.
  - example prompt label: `safety-boundary-matrix-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Runtime boundary override
  - approval requirement: None

- **Operator Authority Prompts**
  - definition: Prompts for defining operator/builder roles.
  - purpose: Governance.
  - example prompt label: `operator-authority-protocol-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Runtime authorization
  - approval requirement: None

- **Task Taxonomy Prompts**
  - definition: Prompts for categorizing task work.
  - purpose: Organizational clarity.
  - example prompt label: `task-taxonomy-documentation-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Task assignment
  - approval requirement: None

- **Worker Glossary Prompts**
  - definition: Prompts for defining worker family terms.
  - purpose: Vocabulary standardization.
  - example prompt label: `worker-family-glossary-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Worker start
  - approval requirement: None

- **Documentation Index Prompts**
  - definition: Prompts for maintaining doc indices.
  - purpose: Tracking document state.
  - example prompt label: `documentation-index-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Runtime modification
  - approval requirement: None

- **Prompt Archive Prompts**
  - definition: Prompts for managing the archive itself.
  - purpose: Indexing organization.
  - example prompt label: `prompt-archive-index-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Runtime activation
  - approval requirement: None

- **Dashboard Planning Prompts**
  - definition: Prompts for status dashboard UI/UX plans.
  - purpose: Visibility planning.
  - example prompt label: `dashboard-planning-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Real metric mutation
  - approval requirement: None

- **Handoff / Status Prompts**
  - definition: Prompts for status report generation.
  - purpose: Operator visibility.
  - example prompt label: `handoff-report-prompt`
  - current allowed status: Allowed
  - runtime effect: None
  - denied behavior: Live state mutation
  - approval requirement: None

## Prompt Label Rules

- labels must be descriptive
- labels must be lowercase-friendly
- labels should use hyphen-separated words
- labels must avoid secrets
- labels must avoid credentials
- labels must avoid production identifiers unless explicitly approved
- labels must not imply execution unless explicitly marked as execution-candidate
- labels must not imply approval
- labels must not imply deployment
- labels must distinguish runtime, non-runtime, fix, check, audit, closeout, planning, and archive prompts

Examples:
- station-chief-v4-7-check-prompt
- station-chief-v4-8-runtime-build-prompt
- non-runtime-worker-architecture-map-prompt
- permission-matrix-documentation-prompt
- safety-boundary-matrix-prompt
- operator-authority-protocol-prompt
- task-taxonomy-documentation-prompt
- worker-family-glossary-prompt
- documentation-index-prompt
- prompt-archive-index-prompt

## Prompt Risk Levels

- **Risk 0 — Documentation prompt**
  - description: Markdown documentation planning.
  - labels: `docs-plan-prompt`
  - current status: Allowed
  - approval style: Implied
  - denied actions: Execution

- **Risk 1 — Planning prompt**
  - description: Architecture designs and hierarchies.
  - labels: `architecture-map-prompt`
  - current status: Allowed
  - approval style: Implied
  - denied actions: Execution

- **Risk 2 — Index / glossary prompt**
  - description: Maintaining term lists and document indexes.
  - labels: `glossary-draft-prompt`
  - current status: Allowed
  - approval style: Implied
  - denied actions: None

- **Risk 3 — Check-only prompt**
  - description: Validating existing state without modification.
  - labels: `smoke-test-prompt`
  - current status: Allowed
  - approval style: Implied
  - denied actions: Modification

- **Risk 4 — Fix prompt**
  - description: Defining logic to repair issues.
  - labels: `runtime-fix-prompt`
  - current status: Parked
  - approval style: Fix token
  - denied actions: Unauthorized modification

- **Risk 5 — Local artifact prompt**
  - description: Generating local JSON proof artifacts.
  - labels: `artifact-write-prompt`
  - current status: Allowed
  - approval style: Token
  - denied actions: Execution

- **Risk 6 — Worker record prompt**
  - description: Defining worker templates.
  - labels: `worker-activate-prompt`
  - current status: Allowed
  - approval style: Token
  - denied actions: Execution

- **Risk 7 — Queue / routing preview prompt**
  - description: Simulating queue or routing logic.
  - labels: `queue-preview-prompt`
  - current status: Allowed
  - approval style: Token
  - denied actions: Queueing/routing

- **Risk 8 — Runtime build prompt**
  - description: Defining new runtime layers.
  - labels: `station-chief-v4-8-build-prompt`
  - current status: Parked
  - approval style: Build token
  - denied actions: Unauthorized execution

- **Risk 9 — External tool candidate prompt**
  - description: Simulating tool logic or external tool plans.
  - labels: `tool-simulate-prompt`
  - current status: Forbidden
  - approval style: Token
  - denied actions: API access

- **Risk 10 — Production candidate prompt**
  - description: Defining production state changes.
  - labels: `production-candidate-prompt`
  - current status: Forbidden
  - approval style: Production gate token
  - denied actions: Production mutation

This document itself stays at Risk 0 / documentation only.

## Prompt Archive Table

| Prompt Family | Risk Level | Documentation Allowed | Runtime Modification Allowed | Validator Modification Allowed | Worker Activation Allowed | Task Execution Allowed | Queue/Routing Allowed | API/Network Allowed | Production Allowed | Current Status |
|---|---|---|---|---|---|---|---|---|---|---|
| Station Chief Runtime Prompts | Risk 8 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Parked |
| Station Chief Fix Prompts | Risk 4 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Parked |
| Station Chief Check Prompts | Risk 3 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Non-Runtime Planning Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Governance Documentation Prompts | Risk 0 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Worker Architecture Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Permission Matrix Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Safety Boundary Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Operator Authority Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Task Taxonomy Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Worker Glossary Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Documentation Index Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Prompt Archive Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Dashboard Planning Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Handoff / Status Prompts | Risk 1 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |

## Prompt Lifecycle Terms

- drafted: Planning state. Not active. Auth: No. Modifies Runtime: No.
- reviewed: Specification finished. Not active. Auth: No. Modifies Runtime: No.
- used: Applied in planning. Not active. Auth: No. Modifies Runtime: No.
- checked: Validated against planning. Not active. Auth: No. Modifies Runtime: No.
- fixed: Logic updated. Not active. Auth: No. Modifies Runtime: No.
- superseded: Replaced version. Not active. Auth: No. Modifies Runtime: No.
- archived: Retired version. Not active. Auth: No. Modifies Runtime: No.
- parked: Runtime version locked. Not active. Auth: No. Modifies Runtime: No.
- reserved for high-model use: Pending top-tier model. Not active. Auth: No. Modifies Runtime: No.
- retired: Phase finished. Not active. Auth: No. Modifies Runtime: No.

## Station Chief Prompt Parking Rule

Station Chief runtime prompts are currently parked after v4.7.0.

While parked:
- do not create v4.8
- do not run v4.8 prompts
- do not modify runtime files
- do not modify validators
- do not modify release locks
- do not run runtime layer build prompts
- do not continue Station Chief ladder work

Station Chief prompts resume only when the operator explicitly assigns a Station Chief runtime task.

## Non-Runtime Prompt Boundary

Non-runtime prompts may create documentation-only files when explicitly assigned.

Non-runtime prompts may not:
- create runtime behavior
- modify runtime files
- modify validators
- create release locks
- create workers
- activate workers
- execute tasks
- enqueue tasks
- create queues
- route live work
- call APIs
- use network
- deploy
- create v4.8

## Prompt Archive Status Categories

- Present: File exists. Auth: No.
- Not present: File does not exist. Auth: No.
- In progress: Active planning. Auth: No.
- Parked: Version locked. Auth: No.
- Reserved for high-model use: Pending. Auth: No.
- Superseded: Replaced. Auth: No.
- Retired: Archived. Auth: No.

## Always-Denied Prompt Actions

- Station Chief v4.8 creation unless explicitly assigned
- Station Chief runtime modification unless explicitly assigned
- validator modification unless explicitly assigned
- release lock modification unless explicitly assigned
- worker process start
- worker activation
- task execution
- task enqueueing
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

## Operator Authority Boundary

- the operator controls project direction
- builders execute only assigned prompts
- builders do not select prompts
- builders do not recommend prompt order
- builders do not decide which prompt runs next
- builders do not create optional prompt archives
- builders do not add recommended next steps
- builders do not turn archive entries into runtime work

## Low-Model-Safe Prompt Archive Work Categories

- prompt label cleanup
- prompt category formatting
- archive table formatting
- glossary wording cleanup
- denied-action wording cleanup
- documentation consistency review
- status table maintenance

## High-Model Reserved Prompt Work Categories

- Station Chief v4.8+
- runtime build prompts
- validator redesign prompts
- worker routing logic prompts
- external tool integration prompts
- production execution candidate prompts
- architecture refactor prompts

## Runtime Authorization Boundary

This document is not runtime authorization.

- prompt archives do not run prompts
- prompt labels do not grant permissions
- prompt categories do not create runtime behavior
- prompt status does not authorize execution
- prompt indexes do not select next tasks
- prompt references do not create v4.8
- future approval still requires explicit operator instruction

## Final Note

This document is planning-only and should not be treated as runtime authorization.
