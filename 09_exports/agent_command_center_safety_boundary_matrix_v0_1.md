# Agent Command Center Safety Boundary Matrix v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime safety planning only.

This document does not create, modify, or authorize Station Chief runtime behavior.

## Purpose

This document maps safety boundaries, denied actions, escalation gates, runtime-adjacent risks, worker-facing risks, task-facing risks, queue-facing risks, routing-facing risks, and production-facing risks without activating anything.

## Core Safety Principle

- safety boundaries are planning records only at this stage
- no worker processes are started
- no tasks are executed
- no tasks are enqueued
- no queues are created
- no routing occurs
- no APIs are called
- no network access occurs
- no credentials or secrets are used
- no production actions are authorized
- no full 47,250-worker workforce activation is authorized

## Always-Denied Boundary List

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
- deployment
- deployment rollback
- production execution
- production activation
- GitHub push by workers
- GitHub API actions by workers
- database mutation
- external tool invocation
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
- task enqueueing
- task execution
- full 47,250-worker workforce activation

## Safety Boundary Families

- **Documentation Boundary**
  - purpose: Safe creation of markdown planning and structural files.
  - allowed planning-only behavior: Markdown edits.
  - denied behavior: Code execution, metadata generation.
  - risk level: Risk 0
  - future approval requirement: Implied by task prompt
  - current status: Allowed

- **Local Record Boundary**
  - purpose: Safe generation of deterministic JSON metadata structures in memory.
  - allowed planning-only behavior: JSON validation logic design.
  - denied behavior: File writes, execution.
  - risk level: Risk 1
  - future approval requirement: Layer-specific token
  - current status: Allowed via specific Station Chief candidate layers

- **Local Artifact Boundary**
  - purpose: Persisting verified metadata safely.
  - allowed planning-only behavior: Artifact path generation logic.
  - denied behavior: Execution, codebase modification.
  - risk level: Risk 2
  - future approval requirement: Layer-specific token
  - current status: Allowed via specific Station Chief candidate layers

- **Cleanup Boundary**
  - purpose: Safely deleting specific generated artifacts.
  - allowed planning-only behavior: Defining cleanup paths.
  - denied behavior: Broad deletion, codebase modification.
  - risk level: Risk 3
  - future approval requirement: Layer-specific cleanup token
  - current status: Allowed via supervised cleanup candidate

- **Worker Activation Boundary**
  - purpose: Define worker templates safely.
  - allowed planning-only behavior: Designing worker schemas.
  - denied behavior: Starting worker processes.
  - risk level: Risk 4
  - future approval requirement: Worker activation token
  - current status: Allowed via worker activation candidate

- **Task Assignment Boundary**
  - purpose: Link task limits to worker templates safely.
  - allowed planning-only behavior: Designing task assignment schemas.
  - denied behavior: Task execution.
  - risk level: Risk 5
  - future approval requirement: Task assignment token
  - current status: Allowed via task assignment candidate

- **Queue Preview Boundary**
  - purpose: Logical mapping of tasks to a queue order safely.
  - allowed planning-only behavior: Generating preview records.
  - denied behavior: Writing to real queues or schedulers.
  - risk level: Risk 6
  - future approval requirement: Queue preview token
  - current status: Allowed via queue preview candidate

- **Routing Preview Boundary**
  - purpose: Simulating assignment of queue items safely.
  - allowed planning-only behavior: Designing routing logic.
  - denied behavior: Live routing, orchestration.
  - risk level: Risk 7
  - future approval requirement: Routing preview token
  - current status: Not yet built (Future)

- **Tool Simulation Boundary**
  - purpose: Safe programmatic sandbox logic execution.
  - allowed planning-only behavior: Designing sandbox protocols.
  - denied behavior: External APIs, network access.
  - risk level: Risk 8
  - future approval requirement: Tool simulation token
  - current status: Forbidden

- **External Tool Boundary**
  - purpose: Authorized network and API operations.
  - allowed planning-only behavior: Designing API schemas.
  - denied behavior: Unapproved tool invocation.
  - risk level: Risk 9
  - future approval requirement: External tool token
  - current status: Forbidden

- **Deployment Boundary**
  - purpose: Moving code to staging/production environments.
  - allowed planning-only behavior: Designing deployment manifests.
  - denied behavior: Executing deployments.
  - risk level: Risk 10
  - future approval requirement: Deployment token
  - current status: Forbidden

- **Production Boundary**
  - purpose: Modifying live data or systems.
  - allowed planning-only behavior: Documenting production schemas.
  - denied behavior: Execution, production mutation.
  - risk level: Risk 10
  - future approval requirement: Production gate token
  - current status: Forbidden

## Boundary Matrix Table

| Boundary Family | Current Planning Allowed | Local Record Allowed | Local File Write Allowed | Worker Start Allowed | Task Execution Allowed | Queue Write Allowed | Routing Allowed | API/Network Allowed | Production Allowed | Current Status |
|---|---|---|---|---|---|---|---|---|---|---|
| Documentation Boundary | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Local Record Boundary | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Local Artifact Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Cleanup Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Worker Activation Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Task Assignment Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Queue Preview Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Routing Preview Boundary | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Future gated |
| Tool Simulation Boundary | Allowed | Allowed | Allowed | Denied | Future gated | Denied | Denied | Denied | Denied | Future gated |
| External Tool Boundary | Allowed | Allowed | Allowed | Future gated | Future gated | Future gated | Future gated | Future gated | Denied | Future gated |
| Deployment Boundary | Allowed | Allowed | Allowed | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated |
| Production Boundary | Allowed | Allowed | Allowed | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated |

## Risk Severity Scale

- **Risk 0 — Documentation-only**
  - description: Creation of planning, structural, and descriptive markdown documents.
  - examples: Write `README.md`, update architecture map.
  - current allowed status: Allowed
  - required approval style: Implied by task prompt.

- **Risk 1 — Local metadata only**
  - description: Generating deterministic JSON metadata records without file writes.
  - examples: Create a dry-run bundle.
  - current allowed status: Allowed via specific Station Chief candidate layers.
  - required approval style: Specific token.

- **Risk 2 — Local file write**
  - description: Writing local JSON proof artifacts to disk.
  - examples: Write proof artifact to `/tmp/`.
  - current allowed status: Allowed via specific Station Chief candidate layers.
  - required approval style: Specific token + explicitly defined output directory.

- **Risk 3 — Local cleanup**
  - description: Safely deleting specific generated artifacts.
  - examples: Delete a specific `/tmp/` artifact directory.
  - current allowed status: Allowed via supervised cleanup candidate.
  - required approval style: Specific token.

- **Risk 4 — Worker record**
  - description: Creating a non-executing local record of a worker design.
  - examples: Write worker activation record.
  - current allowed status: Allowed via worker activation candidate.
  - required approval style: Specific token.

- **Risk 5 — Task record**
  - description: Creating a non-executing local record assigning a task to a worker template.
  - examples: Write task assignment record.
  - current allowed status: Allowed via task assignment candidate.
  - required approval style: Specific token.

- **Risk 6 — Queue preview**
  - description: Creating a non-executing local record simulating queue placement.
  - examples: Write queue preview record.
  - current allowed status: Allowed via queue preview candidate.
  - required approval style: Specific token.

- **Risk 7 — Routing preview**
  - description: Simulating the assignment of a queued task to an active worker.
  - examples: Write routing preview record.
  - current allowed status: Not yet built (Future).
  - required approval style: Specific token.

- **Risk 8 — Tool simulation**
  - description: Simulating the invocation of a local or isolated tool.
  - examples: Calculate a hash, parse a file locally.
  - current allowed status: Forbidden.
  - required approval style: Specific token + sandbox review.

- **Risk 9 — External tool candidate**
  - description: Safe execution of isolated external tools under strict supervision.
  - examples: Fetch from GitHub API.
  - current allowed status: Forbidden.
  - required approval style: Specific token + operator intervention.

- **Risk 10 — Production candidate**
  - description: Authorized execution of production-level changes or deployments.
  - examples: Migrate database, push to main.
  - current allowed status: Forbidden.
  - required approval style: Production gate token.

This document itself stays at Risk 0 only.

## Worker-Facing Safety Boundaries

- **Intake Workers**
  - current status: design-only
  - primary risk: Injecting unsafe commands.
  - denied actions: Network access, production mutation.
  - safety boundary: Input sanitization, sandbox isolation.
  - future approval required before escalation: Intake validation token.

- **Classification Workers**
  - current status: design-only
  - primary risk: Mislabeling high-risk tasks.
  - denied actions: Modifying queue structure, network.
  - safety boundary: Read-only context processing.
  - future approval required before escalation: Classification mapping token.

- **Research Workers**
  - current status: design-only
  - primary risk: Over-exposing sensitive information.
  - denied actions: Execution, modifications.
  - safety boundary: Read-only access to repositories.
  - future approval required before escalation: Research context token.

- **Document Workers**
  - current status: design-only
  - primary risk: Corrupting essential documentation.
  - denied actions: Code execution, network.
  - safety boundary: Restrict to `/docs` and `.md` formats.
  - future approval required before escalation: Documentation write token.

- **Code Workers**
  - current status: design-only
  - primary risk: Injecting unsafe codebase modifications.
  - denied actions: Production deployment, execution outside test suite.
  - safety boundary: AST verification, sandbox environments.
  - future approval required before escalation: Supervised coding token.

- **QA / Validator Workers**
  - current status: design-only
  - primary risk: False positives or ignoring critical errors.
  - denied actions: Code generation, external data fetching.
  - safety boundary: Read-only execution of existing tests.
  - future approval required before escalation: Supervised test token.

- **Safety Review Workers**
  - current status: design-only
  - primary risk: Overlooking security vulnerabilities.
  - denied actions: Changing code, network.
  - safety boundary: Audit-only mode.
  - future approval required before escalation: Safety audit token.

- **Audit Workers**
  - current status: design-only
  - primary risk: Losing execution logs.
  - denied actions: execution, modification.
  - safety boundary: Write-only append log access.
  - future approval required before escalation: Audit log token.

- **Routing Preview Workers**
  - current status: design-only
  - primary risk: Incorrectly simulating routing behavior.
  - denied actions: Live routing.
  - safety boundary: Generation of preview records only.
  - future approval required before escalation: Routing preview token.

- **Operator Support Workers**
  - current status: design-only
  - primary risk: Providing incorrect systemic instructions.
  - denied actions: Unsupervised execution.
  - safety boundary: Interactive operator gates.
  - future approval required before escalation: Support query token.

- **Dashboard Workers**
  - current status: design-only
  - primary risk: Corrupting exported metric systems.
  - denied actions: Core system modifications.
  - safety boundary: Strict schema enforcement for exports.
  - future approval required before escalation: Dashboard update token.

- **Memory / Archive Workers**
  - current status: design-only
  - primary risk: Permanent deletion of context.
  - denied actions: Execution, network.
  - safety boundary: Append-only archive constraints.
  - future approval required before escalation: Archive token.

- **Prompt Library Workers**
  - current status: design-only
  - primary risk: Corrupting system templates.
  - denied actions: Execution, network.
  - safety boundary: Version control locking.
  - future approval required before escalation: Library manager token.

- **Report Generation Workers**
  - current status: design-only
  - primary risk: Halting the reporting process with bad data.
  - denied actions: Execution, network.
  - safety boundary: Restricted to schema templates.
  - future approval required before escalation: Reporting token.

- **Deployment Readiness Workers**
  - current status: design-only
  - primary risk: Missing critical deployment steps.
  - denied actions: Direct deployment.
  - safety boundary: Read-only checklist enforcement.
  - future approval required before escalation: Readiness check token.

- **Recovery / Rollback Planning Workers**
  - current status: design-only
  - primary risk: Implementing unsafe rollback paths.
  - denied actions: Unsupervised rollback.
  - safety boundary: Step-by-step operator verification.
  - future approval required before escalation: Rollback planning token.

## Task-Facing Safety Boundaries

- **documentation task**
  - current status: Allowed
  - primary risk: None
  - denied actions: Script execution
  - safety boundary: Markdown formatting rules
  - future approval required before escalation: None (Risk 0 safe)

- **planning task**
  - current status: Allowed
  - primary risk: None
  - denied actions: Execution, external tool use
  - safety boundary: Planning schemas only
  - future approval required before escalation: None (Risk 0 safe)

- **classification task**
  - current status: Allowed (design only)
  - primary risk: Misclassification
  - denied actions: Enqueueing, execution
  - safety boundary: Design metadata restrictions
  - future approval required before escalation: Task assignment token

- **review task**
  - current status: Allowed (for local records)
  - primary risk: Skipping validations
  - denied actions: Modifying target files
  - safety boundary: Local artifact review scopes
  - future approval required before escalation: Post-action audit token

- **local artifact task**
  - current status: Allowed (with specific tokens)
  - primary risk: Overwriting existing data
  - denied actions: Creating processes, running live tasks
  - safety boundary: Output directory containment
  - future approval required before escalation: Local artifact write token

- **audit task**
  - current status: Allowed (for non-executing records)
  - primary risk: Invalidating evidence
  - denied actions: Execution
  - safety boundary: Pure structural validation
  - future approval required before escalation: Audit record token

- **closeout task**
  - current status: Allowed (with specific tokens)
  - primary risk: Closing a phase prematurely
  - denied actions: Execution
  - safety boundary: Closeout constraints
  - future approval required before escalation: Closeout token

- **queue preview task**
  - current status: Allowed (with specific tokens)
  - primary risk: Simulating incorrect scheduling
  - denied actions: Real queue write, execution
  - safety boundary: Preview schema compliance
  - future approval required before escalation: Queue preview token

- **routing preview task**
  - current status: Not yet allowed (pending v4.8)
  - primary risk: Incorrectly simulating routing rules
  - denied actions: Live assignment, orchestration
  - safety boundary: Preview schema compliance
  - future approval required before escalation: Routing preview token

- **live execution task**
  - current status: Forbidden
  - primary risk: System disruption
  - denied actions: Tool access, network, API usage
  - safety boundary: Sandbox container
  - future approval required before escalation: Telemetry/supervised token

- **production task**
  - current status: Forbidden
  - primary risk: Production outages
  - denied actions: Data mutation, deployment
  - safety boundary: Complete production lock
  - future approval required before escalation: Production gate token

## Queue and Routing Safety Boundaries

- **queue preview**
  - what it means: Creating a simulated record of a queue position.
  - whether it is currently allowed: Allowed
  - what is denied: Enqueueing, execution.
  - what approval would be needed later: Queue preview token

- **real queue creation**
  - what it means: Initializing a queue service or data structure.
  - whether it is currently allowed: Forbidden
  - what is denied: Creating the queue.
  - what approval would be needed later: Queue creation token

- **queue write**
  - what it means: Writing a live item to an active queue.
  - whether it is currently allowed: Forbidden
  - what is denied: Adding to a queue.
  - what approval would be needed later: Queue write token

- **scheduler write**
  - what it means: Scheduling a task to run automatically.
  - whether it is currently allowed: Forbidden
  - what is denied: Adding to scheduler/cron.
  - what approval would be needed later: Scheduler token

- **task enqueue**
  - what it means: Storing an active task.
  - whether it is currently allowed: Forbidden
  - what is denied: Task entry.
  - what approval would be needed later: Enqueue token

- **routing preview**
  - what it means: Simulating the assignment of a queued item to a worker.
  - whether it is currently allowed: Forbidden (pending v4.8)
  - what is denied: Live routing.
  - what approval would be needed later: Routing preview token

- **live worker routing**
  - what it means: Assigning tasks to active worker processes.
  - whether it is currently allowed: Forbidden
  - what is denied: Orchestration.
  - what approval would be needed later: Worker routing token

- **live orchestration**
  - what it means: Systemic coordination of multiple worker processes.
  - whether it is currently allowed: Forbidden
  - what is denied: Full execution orchestration.
  - what approval would be needed later: Orchestration token

## Runtime-Adjacent Boundary Rules

- Documentation does not authorize runtime behavior.
- Planning documents do not modify runtime behavior.
- Permission matrices do not grant runtime permissions.
- Safety boundary documents do not create validators.
- Worker maps do not create workers.
- Queue preview docs do not create queues.
- Routing concepts do not authorize routing.
- Approval for a record does not imply approval for execution.
- Approval for a preview does not imply approval for live behavior.
- Approval for one layer does not imply approval for the next layer.

## Operator Authority Rules

- The operator controls project direction.
- Builder agents execute only the assigned task.
- Builder agents do not select next tasks.
- Builder agents do not recommend roadmap direction.
- Builder agents do not expand scope.
- Builder agents do not create optional files.
- Builder agents report only the requested confirmations.

## Low-Model-Safe Safety Work Categories

- boundary wording cleanup
- denied-action list formatting
- safety glossary drafting
- matrix formatting
- documentation consistency checks
- operator handbook drafting
- risk scale documentation
- version timeline documentation

## High-Model Reserved Safety Work Categories

- Station Chief v4.8+
- runtime safety enforcement
- validator redesign
- live worker routing safety logic
- external tool safety logic
- production execution safety gates
- architecture refactors

## Final Note

This document is planning-only and should not be treated as runtime authorization.