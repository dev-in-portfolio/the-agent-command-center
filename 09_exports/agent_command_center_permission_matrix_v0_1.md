# Agent Command Center Permission Matrix v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime permission planning only.

This document does not create, modify, or authorize Station Chief runtime behavior.

## Purpose

This document maps permission levels, denied actions, approval boundaries, worker-facing permissions, task-facing permissions, queue-facing permissions, routing-facing permissions, and production-facing permissions without activating anything.

## Core Permission Principle

- permissions are design records only at this stage
- no worker processes are started
- no tasks are executed
- no tasks are enqueued
- no queues are created
- no live routing occurs
- no APIs are called
- no network access occurs
- no credentials or secrets are used
- no production actions are authorized
- no full 47,250-worker workforce activation is authorized

## Permission Ladder

- **Level 0 — Documentation only**
  - description: Creation of planning, structural, and descriptive markdown documents.
  - what is allowed: Writing documentation.
  - what is denied: Any execution, local artifact generation, or system changes.
  - approval style: Implied by task prompt.
  - current status: Allowed

- **Level 1 — Local record creation**
  - description: Generating deterministic JSON metadata records without file writes.
  - what is allowed: Generating in-memory records.
  - what is denied: File writes, execution.
  - approval style: Specific token.
  - current status: Allowed via specific Station Chief candidate layers.

- **Level 2 — Local artifact write**
  - description: Writing local JSON proof artifacts to disk.
  - what is allowed: Writing localized, verified JSON to specific output directories.
  - what is denied: Modifying core files, execution.
  - approval style: Specific token + explicitly defined output directory.
  - current status: Allowed via specific Station Chief candidate layers.

- **Level 3 — Local artifact cleanup**
  - description: Safely deleting specific generated artifacts.
  - what is allowed: Deletion of specific artifact directories.
  - what is denied: Deleting codebase files, broad deletions.
  - approval style: Specific token.
  - current status: Allowed via supervised cleanup candidate.

- **Level 4 — Worker activation record**
  - description: Creating a non-executing local record of a worker design.
  - what is allowed: Generating/writing worker metadata records.
  - what is denied: Worker process creation, execution.
  - approval style: Specific token.
  - current status: Allowed via worker activation candidate.

- **Level 5 — Task assignment record**
  - description: Creating a non-executing local record assigning a task to a worker template.
  - what is allowed: Generating/writing task assignment metadata.
  - what is denied: Task execution, queue insertion.
  - approval style: Specific token.
  - current status: Allowed via task assignment candidate.

- **Level 6 — Queue preview record**
  - description: Creating a non-executing local record simulating queue placement.
  - what is allowed: Generating/writing queue preview metadata.
  - what is denied: Real queue creation, writing to schedulers.
  - approval style: Specific token.
  - current status: Allowed via queue preview candidate.

- **Level 7 — Routing preview record**
  - description: Simulating the assignment of a queued task to an active worker.
  - what is allowed: Generating/writing routing metadata.
  - what is denied: Live worker routing, orchestration.
  - approval style: Specific token.
  - current status: Not yet built (Future).

- **Level 8 — Limited tool-use simulation**
  - description: Simulating the invocation of a local or isolated tool.
  - what is allowed: Running safe local sandbox functions.
  - what is denied: External APIs, network access.
  - approval style: Specific token + sandbox review.
  - current status: Forbidden.

- **Level 9 — Supervised external tool candidate**
  - description: Safe execution of isolated external tools under strict supervision.
  - what is allowed: Supervised, sandboxed external tool invocations.
  - what is denied: Broad API access, unreviewed actions.
  - approval style: Specific token + operator intervention.
  - current status: Forbidden.

- **Level 10 — Production candidate**
  - description: Authorized execution of production-level changes or deployments.
  - what is allowed: Approved production state changes.
  - what is denied: Anything outside the explicitly approved payload.
  - approval style: Production gate token.
  - current status: Forbidden.

This document itself stays at Level 0 only.

## Permission Families

- **Documentation Permissions**
  - purpose: To allow safe creation of markdown files and plans.
  - examples: Write `README.md`, update architecture map.
  - current allowed status: Allowed
  - denied actions: Code execution, metadata generation.
  - future approval requirement: None (Implied)

- **Local Record Permissions**
  - purpose: Allow generating structural JSON metadata without saving to disk.
  - examples: Create a dry-run bundle.
  - current allowed status: Allowed
  - denied actions: Disk write, execution.
  - future approval requirement: Layer-specific token

- **Local Artifact Permissions**
  - purpose: Safely persist verified metadata.
  - examples: Write proof artifact to `/tmp/`.
  - current allowed status: Allowed
  - denied actions: Execution, repository state modification.
  - future approval requirement: Layer-specific token

- **Cleanup Permissions**
  - purpose: Rollback and delete localized artifacts safely.
  - examples: Delete a specific `/tmp/` artifact directory.
  - current allowed status: Allowed
  - denied actions: Broad deletion, repository state modification.
  - future approval requirement: Layer-specific cleanup token

- **Worker Activation Permissions**
  - purpose: Define and persist worker templates.
  - examples: Write worker activation record.
  - current allowed status: Allowed
  - denied actions: Starting a worker process.
  - future approval requirement: Worker activation token

- **Task Assignment Permissions**
  - purpose: Define and persist task boundaries linked to a worker.
  - examples: Write task assignment record.
  - current allowed status: Allowed
  - denied actions: Task execution.
  - future approval requirement: Task assignment token

- **Queue Preview Permissions**
  - purpose: Map tasks into a logical queue order without real scheduling.
  - examples: Write queue preview record.
  - current allowed status: Allowed
  - denied actions: Writing to a real queue, cron, or scheduler.
  - future approval requirement: Queue preview token

- **Routing Preview Permissions**
  - purpose: Define logic for routing a queue item to a worker.
  - examples: Write routing preview record.
  - current allowed status: Forbidden (pending build)
  - denied actions: Live routing.
  - future approval requirement: Routing preview token

- **Tool Simulation Permissions**
  - purpose: Execute safe, local programmatic logic.
  - examples: Calculate a hash, parse a file locally.
  - current allowed status: Forbidden
  - denied actions: Unsafe local execution, network.
  - future approval requirement: Tool simulation token

- **External Tool Permissions**
  - purpose: Authorized network and API calls.
  - examples: Fetch from GitHub API.
  - current allowed status: Forbidden
  - denied actions: Unauthorized external actions, credential exfiltration.
  - future approval requirement: External tool token

- **Deployment Permissions**
  - purpose: Packaging and moving code to an environment.
  - examples: Run deployment script.
  - current allowed status: Forbidden
  - denied actions: Unapproved deployments.
  - future approval requirement: Deployment token

- **Production Permissions**
  - purpose: Modifying live data or environments.
  - examples: Migrate database, push to main.
  - current allowed status: Forbidden
  - denied actions: Anything unapproved by operator.
  - future approval requirement: Production token

## Always-Denied Actions Unless Separately Approved

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

## Permission Matrix Table

| Permission Level | Name | Documentation Allowed | Local Record Allowed | Local File Write Allowed | Cleanup Allowed | Worker Start Allowed | Task Execution Allowed | Queue Write Allowed | Routing Allowed | API/Network Allowed | Production Allowed | Current Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Level 0 | Documentation only | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 1 | Local record creation | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 2 | Local artifact write | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 3 | Local artifact cleanup | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 4 | Worker activation record | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 5 | Task assignment record | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 6 | Queue preview record | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Allowed |
| Level 7 | Routing preview record | Allowed | Allowed | Allowed | Allowed | Denied | Denied | Denied | Denied | Denied | Denied | Future gated |
| Level 8 | Limited tool-use simulation | Allowed | Allowed | Allowed | Allowed | Denied | Future gated | Denied | Denied | Denied | Denied | Future gated |
| Level 9 | Supervised external tool candidate | Allowed | Allowed | Allowed | Allowed | Future gated | Future gated | Future gated | Future gated | Future gated | Denied | Future gated |
| Level 10 | Production candidate | Allowed | Allowed | Allowed | Allowed | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated | Future gated |

## Worker Permission Boundaries

- **Intake Workers**
  - likely future permission ceiling: Level 8 (safe local parsing tools)
  - current status: design-only
  - denied actions: Network, Production, Queue writes
  - approval needed later: Token for specific intake tools

- **Classification Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Modification of queues, network
  - approval needed later: Task assignment parsing token

- **Research Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Modifying code, execution
  - approval needed later: Read-only codebase access token

- **Document Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Modifying functional code, network
  - approval needed later: Doc-writing token

- **Code Workers**
  - likely future permission ceiling: Level 9
  - current status: design-only
  - denied actions: Production deploy, broad tool use
  - approval needed later: Supervised code generation token

- **QA / Validator Workers**
  - likely future permission ceiling: Level 9
  - current status: design-only
  - denied actions: Code generation, production data access
  - approval needed later: Supervised test runner token

- **Safety Review Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Unsupervised execution, network
  - approval needed later: Read-only sandbox token

- **Audit Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Modification of records, execution
  - approval needed later: Audit record token

- **Routing Preview Workers**
  - likely future permission ceiling: Level 7
  - current status: design-only
  - denied actions: Live routing
  - approval needed later: Routing preview token

- **Operator Support Workers**
  - likely future permission ceiling: Level 9
  - current status: design-only
  - denied actions: Unsupervised execution
  - approval needed later: Support tool token

- **Dashboard Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Core system modifications
  - approval needed later: Export modification token

- **Memory / Archive Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Execution, network
  - approval needed later: Safe archival token

- **Prompt Library Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Execution, network
  - approval needed later: Safe library management token

- **Report Generation Workers**
  - likely future permission ceiling: Level 8
  - current status: design-only
  - denied actions: Execution, network
  - approval needed later: Report generation token

- **Deployment Readiness Workers**
  - likely future permission ceiling: Level 9
  - current status: design-only
  - denied actions: Direct deployment
  - approval needed later: Safe deployment check token

- **Recovery / Rollback Planning Workers**
  - likely future permission ceiling: Level 10
  - current status: design-only
  - denied actions: Unsupervised rollback
  - approval needed later: Supervised rollback execution token

## Task Permission Boundaries

- **documentation task**
  - current allowed status: Allowed
  - required future permission level: Level 0
  - denied actions until approved: Any local artifact generation or script execution

- **planning task**
  - current allowed status: Allowed
  - required future permission level: Level 0
  - denied actions until approved: Execution, external tool use

- **classification task**
  - current allowed status: Allowed (design only)
  - required future permission level: Level 5
  - denied actions until approved: Task enqueueing, execution

- **review task**
  - current allowed status: Allowed (for local records)
  - required future permission level: Level 2
  - denied actions until approved: Modifying target files

- **local artifact task**
  - current allowed status: Allowed (with specific tokens)
  - required future permission level: Level 2
  - denied actions until approved: Creating worker processes, live tasks

- **audit task**
  - current allowed status: Allowed (for non-executing records)
  - required future permission level: Level 2
  - denied actions until approved: Execution

- **closeout task**
  - current allowed status: Allowed (with specific tokens)
  - required future permission level: Level 2
  - denied actions until approved: Execution

- **queue preview task**
  - current allowed status: Allowed (with specific tokens)
  - required future permission level: Level 6
  - denied actions until approved: Queue writing, execution

- **routing preview task**
  - current allowed status: Not yet allowed (pending v4.8)
  - required future permission level: Level 7
  - denied actions until approved: Live assignment, orchestration

- **live execution task**
  - current allowed status: Forbidden
  - required future permission level: Level 9
  - denied actions until approved: Tool access, network, API usage

- **production task**
  - current allowed status: Forbidden
  - required future permission level: Level 10
  - denied actions until approved: Data mutation, deployment

## Record Types and Permission Level Mapping

- **planning document**
  - permission level: Level 0
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: No

- **glossary document**
  - permission level: Level 0
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: No

- **taxonomy document**
  - permission level: Level 0
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: No

- **local proof artifact record**
  - permission level: Level 2
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **audit record**
  - permission level: Level 2
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **closeout record**
  - permission level: Level 2
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **worker activation record**
  - permission level: Level 4
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **task assignment record**
  - permission level: Level 5
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **queue preview record**
  - permission level: Level 6
  - current allowed status: Allowed
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Optional

- **routing preview record**
  - permission level: Level 7
  - current allowed status: Future gated
  - whether it can be created in low-model sessions: Yes
  - whether top-tier model review is required: Yes

- **supervised tool-use candidate record**
  - permission level: Level 9
  - current allowed status: Future gated
  - whether it can be created in low-model sessions: No
  - whether top-tier model review is required: Yes

- **production candidate record**
  - permission level: Level 10
  - current allowed status: Future gated
  - whether it can be created in low-model sessions: No
  - whether top-tier model review is required: Yes

## Approval Boundary Rules

- Each permission escalation requires explicit operator approval.
- Approval for one level does not imply approval for the next level.
- Approval for a record does not imply approval for execution.
- Approval for a preview does not imply approval for live routing.
- Approval for local artifacts does not imply approval for APIs, network, credentials, or production.
- Approval tokens, if used later, must be specific to the layer and action.
- Documentation does not authorize runtime behavior.

## Low-Model-Safe Permission Work Categories

- permission glossary cleanup
- matrix formatting
- denied-action list refinement
- documentation consistency checks
- operator handbook drafting
- role descriptions
- taxonomy expansion
- version timeline documentation

## High-Model Reserved Permission Work Categories

- Station Chief v4.8+
- runtime permission enforcement
- validator redesign
- live worker routing permission logic
- external tool permission logic
- production execution candidates
- architecture refactors

## Final Note

This document is planning-only and should not be treated as runtime authorization.
