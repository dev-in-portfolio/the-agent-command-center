# Agent Command Center Worker Family Glossary v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime worker terminology only.

This document does not create, modify, activate, route, or authorize Station Chief runtime behavior.

## Purpose

This glossary defines worker family names, worker label conventions, non-executing roles, risk boundaries, and future permission expectations.

- worker family definitions are planning records only
- worker labels do not create workers
- worker descriptions do not start processes
- worker families do not authorize routing
- worker families do not authorize task execution
- worker families do not authorize API, network, credential, secret, deployment, or production behavior

## Core Worker Glossary Principle

- a worker family is a design category
- a worker label is a descriptive metadata label
- a worker record is not a running process
- a worker activation record is not worker execution
- a task assignment record is not task execution
- a routing preview is not live routing
- documentation does not authorize runtime behavior
- approval for one worker family does not imply approval for another worker family

## Worker Label Rules

- labels must be descriptive
- labels must be lowercase-friendly
- labels should use hyphen-separated words
- labels must avoid secrets
- labels must avoid credentials
- labels must avoid production identifiers unless explicitly approved
- labels must not imply execution
- labels must not imply routing
- labels must not imply deployment
- labels must not imply approval
- labels should distinguish design, preview, record, audit, and execution-candidate states

Examples:
- intake-command-parser
- classification-risk-tagger
- documentation-map-writer
- safety-boundary-reviewer
- audit-closeout-reviewer
- queue-preview-planner
- routing-preview-planner
- operator-report-formatter

## Worker Family Glossary

- **Intake Workers**
  - definition: Handle initial command reception and taxonomy parsing.
  - plain-English role: Receptionist
  - example worker labels: `intake-command-parser`
  - example planning-only tasks: Parse system command intent, taxonomy mapping.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Network, runtime execution, production access.
  - likely future permission ceiling: Level 8
  - escalation requirement: Intake token

- **Classification Workers**
  - definition: Categorize incoming tasks and assign risk metadata.
  - plain-English role: Categorizer
  - example worker labels: `classification-risk-tagger`
  - example planning-only tasks: Assign risk level, define classification schema.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Live routing, execution.
  - likely future permission ceiling: Level 8
  - escalation requirement: Classification token

- **Research Workers**
  - definition: Analyze codebase and retrieve system context.
  - plain-English role: Researcher
  - example worker labels: `research-context-gatherer`
  - example planning-only tasks: Dependency mapping, codebase summarization.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Source code modification, execution.
  - likely future permission ceiling: Level 8
  - escalation requirement: Research token

- **Document Workers**
  - definition: Maintain system documentation and structural maps.
  - plain-English role: Scribe
  - example worker labels: `documentation-map-writer`
  - example planning-only tasks: Maintain architecture map, draft glossary.
  - current status: design-only
  - risk level: Risk 0
  - denied actions: Runtime execution, network.
  - likely future permission ceiling: Level 8
  - escalation requirement: Documentation token

- **Code Workers**
  - definition: Design and propose codebase structural updates.
  - plain-English role: Architect
  - example worker labels: `code-refactor-planner`
  - example planning-only tasks: Design function skeletons, plan refactors.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Production deploy, task execution.
  - likely future permission ceiling: Level 9
  - escalation requirement: Supervised coding token

- **QA / Validator Workers**
  - definition: Design and maintain test/validation specifications.
  - plain-English role: Auditor
  - example worker labels: `qa-test-plan-generator`
  - example planning-only tasks: Draft test case specs, review validation requirements.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Real execution, production data access.
  - likely future permission ceiling: Level 9
  - escalation requirement: Supervised QA token

- **Safety Review Workers**
  - definition: Define and audit safety boundaries and compliance.
  - plain-English role: Auditor
  - example worker labels: `safety-boundary-reviewer`
  - example planning-only tasks: Audit planning records, verify boundary rules.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Modification of records, execution.
  - likely future permission ceiling: Level 8
  - escalation requirement: Safety audit token

- **Audit Workers**
  - definition: Define audit requirements and evidence records.
  - plain-English role: Compliance
  - example worker labels: `audit-closeout-reviewer`
  - example planning-only tasks: Draft audit criteria, define record schema.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Modification of evidence, system access.
  - likely future permission ceiling: Level 8
  - escalation requirement: Audit record token

- **Routing Preview Workers**
  - definition: Plan task assignment simulation logic.
  - plain-English role: Planner
  - example worker labels: `routing-preview-planner`
  - example planning-only tasks: Simulate routing logic, define routing schema.
  - current status: design-only
  - risk level: Risk 7
  - denied actions: Live routing.
  - likely future permission ceiling: Level 7
  - escalation requirement: Routing preview token

- **Operator Support Workers**
  - definition: Formulate support procedures and interface logs.
  - plain-English role: Assistant
  - example worker labels: `operator-report-formatter`
  - example planning-only tasks: Format reports, log analysis strategies.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Unsupervised execution.
  - likely future permission ceiling: Level 9
  - escalation requirement: Support token

- **Dashboard Workers**
  - definition: Design status dashboards and KPI metrics.
  - plain-English role: Monitor
  - example worker labels: `dashboard-metrics-planner`
  - example planning-only tasks: Design dashboard views, define KPIs.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: System control.
  - likely future permission ceiling: Level 8
  - escalation requirement: Dashboard token

- **Memory / Archive Workers**
  - definition: Define long-term storage and archival strategies.
  - plain-English role: Archivist
  - example worker labels: `memory-archive-manager`
  - example planning-only tasks: Design archive indices, history retention rules.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Execution, network.
  - likely future permission ceiling: Level 8
  - escalation requirement: Memory token

- **Prompt Library Workers**
  - definition: Manage and version system prompts.
  - plain-English role: Librarian
  - example worker labels: `prompt-library-manager`
  - example planning-only tasks: Organize workflow templates, categorize library entries.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Execution, network.
  - likely future permission ceiling: Level 8
  - escalation requirement: Prompt library token

- **Report Generation Workers**
  - definition: Plan status and progress reporting protocols.
  - plain-English role: Reporter
  - example worker labels: `report-generation-planner`
  - example planning-only tasks: Draft reporting templates, define reporting cadence.
  - current status: design-only
  - risk level: Risk 4
  - denied actions: Execution, network.
  - likely future permission ceiling: Level 8
  - escalation requirement: Report token

- **Deployment Readiness Workers**
  - definition: Define deployment prerequisites and readiness checks.
  - plain-English role: Gatekeeper
  - example worker labels: `deployment-readiness-planner`
  - example planning-only tasks: Draft pre-deploy checklists.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Deploying.
  - likely future permission ceiling: Level 9
  - escalation requirement: Readiness token

- **Recovery / Rollback Planning Workers**
  - definition: Design emergency rollback and recovery paths.
  - plain-English role: Recovery
  - example worker labels: `rollback-recovery-planner`
  - example planning-only tasks: Map recovery checkpoints, draft rollback steps.
  - current status: design-only
  - risk level: Risk 5
  - denied actions: Unsupervised rollback.
  - likely future permission ceiling: Level 10
  - escalation requirement: Rollback token

## Worker Family Risk Scale

- **Risk 0 — Documentation-only worker description**
  - examples: Documentation family
  - current status: Allowed
  - approval: Implied
  - denied: Execution

- **Risk 1 — Local metadata worker description**
  - examples: Intake, Classification families
  - current status: Allowed
  - approval: Token
  - denied: Write

- **Risk 2 — Local file artifact worker description**
  - examples: Research, Memory, Prompt, Report families
  - current status: Allowed
  - approval: Token
  - denied: Execution

- **Risk 3 — Cleanup planning worker description**
  - examples: Cleanup planning task workers
  - current status: Allowed
  - approval: Token
  - denied: Broad deletion

- **Risk 4 — Worker activation record description**
  - examples: All families in design
  - current status: Allowed
  - approval: Token
  - denied: Execution

- **Risk 5 — Task assignment record description**
  - examples: Code, QA, Deployment families
  - current status: Allowed
  - approval: Token
  - denied: Execution

- **Risk 6 — Queue preview worker description**
  - examples: Routing Preview workers
  - current status: Allowed
  - approval: Token
  - denied: Queueing

- **Risk 7 — Routing preview worker description**
  - examples: Routing Preview workers
  - current status: Not allowed
  - approval: Token
  - denied: Routing

- **Risk 8 — Tool simulation worker description**
  - examples: Tool simulation families
  - current status: Forbidden
  - approval: Token
  - denied: API access

- **Risk 9 — External tool candidate worker description**
  - examples: External Tool, QA, Code workers
  - current status: Forbidden
  - approval: Token
  - denied: Network

- **Risk 10 — Production candidate worker description**
  - examples: Deployment, Rollback families
  - current status: Forbidden
  - approval: Token
  - denied: Production execution

## Worker Family Permission Table

| Worker Family | Risk Level | Documentation Allowed | Local Record Allowed | Local File Write Allowed | Worker Start Allowed | Task Execution Allowed | Queue Write Allowed | Routing Allowed | API/Network Allowed | Production Allowed | Current Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Intake Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Classification Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Research Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Document Workers | Risk 0 | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Code Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| QA / Validator Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Safety Review Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Audit Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Routing Preview Workers | Risk 7 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Future gated |
| Operator Support Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Dashboard Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Memory / Archive Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Prompt Library Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Report Generation Workers | Risk 4 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Deployment Readiness Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Recovery / Rollback Planning Workers | Risk 5 | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |

## Worker-to-Task Relationship Rules

- workers are design records only at this stage
- worker labels do not create worker processes
- assigning a task to a worker record does not start the worker
- assigning a task to a worker record does not execute the task
- queue preview does not enqueue the task
- routing preview does not route live work
- worker/task links are metadata only unless separately escalated
- live work requires separate explicit operator approval

## Worker Lifecycle Terms

- proposed: Design state. Not active. Denied: Execution.
- designed: Specification finished. Not active. Denied: Execution.
- registered: Entered in system. Not active. Denied: Execution.
- locally activated as record: Metadata object created. Not active. Denied: Execution.
- assigned local task record: Metadata linked. Not active. Denied: Execution.
- queued preview record: Simulated queueing. Not active. Denied: Execution.
- routed preview record: Simulated routing. Not active. Denied: Execution.
- execution candidate: Pending operator. Not active. Denied: Execution.
- audited: Reviewed post-close. Not active. Denied: Execution.
- closed out: Phase complete. Not active. Denied: Execution.
- retired: Archive state. Not active. Denied: Execution.

## Always-Denied Worker Actions

- worker process start
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

## Worker Escalation Rules

- documentation worker descriptions do not escalate automatically
- worker family definitions do not create workers
- worker labels do not create worker records
- worker activation records do not start worker processes
- task assignment records do not execute tasks
- queue preview records do not authorize real queues
- routing preview records do not authorize live routing
- tool simulation does not authorize external APIs
- external tool candidates do not authorize production
- production candidates require separate explicit operator approval

## Operator Authority Boundary

- the operator controls project direction
- builders execute only assigned tasks
- builders do not select worker families for activation
- builders do not recommend worker activation
- builders do not create worker records unless explicitly assigned
- builders do not create runtime behavior from glossary entries
- builders do not add recommended next steps

## Low-Model-Safe Worker Glossary Work Categories

- worker definition drafting
- label cleanup
- glossary formatting
- denied-action wording cleanup
- worker family description cleanup
- matrix formatting
- documentation consistency review

## High-Model Reserved Worker Work Categories

- Station Chief v4.8+
- runtime worker routing logic
- validator redesign
- worker activation enforcement
- task assignment enforcement
- external tool worker logic
- production worker candidates
- architecture refactors

## Runtime Authorization Boundary

This document is not runtime authorization.

- worker glossary entries do not create workers
- worker labels do not start processes
- worker family categories do not grant permissions
- worker maps do not route tasks
- worker planning does not create queues
- worker planning does not authorize execution
- future approval still requires explicit operator instruction

## Final Note

This document is planning-only and should not be treated as runtime authorization.
