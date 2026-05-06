# Agent Command Center Documentation Index v0.1

## Current Context

Station Chief runtime is parked at v4.7.0 and that this document covers non-runtime documentation indexing only.

This document does not create, modify, or authorize Station Chief runtime behavior.

## Purpose

This document indexes planning, governance, taxonomy, glossary, permission, and safety documents so the operator can track what exists without asking builder agents to choose the roadmap.

- this is an index only
- this document does not select future work
- this document does not create runtime behavior
- this document does not grant permissions
- this document does not activate workers
- this document does not authorize v4.8

## Documentation Index Principle

- documentation index entries are references only
- index entries do not modify the referenced documents
- index entries do not imply runtime authorization
- index entries do not imply task selection
- index entries do not imply roadmap priority
- index entries do not create workers, tasks, queues, routes, validators, or runtime layers

## Known Documentation Set

| Document | Expected Path | Category | Purpose | Runtime Authorization | Current Status |
|---|---|---|---|---|---|
| Worker Architecture Map | 09_exports/agent_command_center_worker_architecture_map_v0_1.md | architecture planning | Map worker families, families, and future concepts | None | Present |
| Permission Matrix | 09_exports/agent_command_center_permission_matrix_v0_1.md | permission planning | Map permission levels and approval boundaries | None | Present |
| Safety Boundary Matrix | 09_exports/agent_command_center_safety_boundary_matrix_v0_1.md | safety boundary planning | Map safety boundaries and risk severity | None | Present |
| Operator Authority Protocol | 09_exports/agent_command_center_operator_authority_protocol_v0_1.md | operator governance | Define operator and builder authority | None | Present |
| Task Taxonomy | 09_exports/agent_command_center_task_taxonomy_v0_1.md | task taxonomy | Map task categories and task boundaries | None | Present |
| Worker Family Glossary | 09_exports/agent_command_center_worker_family_glossary_v0_1.md | worker glossary | Map worker families and terminology | None | Present |

## Documentation Categories

- **architecture planning**
  - purpose: High-level organizational and structural planning.
  - what it may describe: Worker families, system concepts, future possibilities.
  - what it may not authorize: Runtime behavior, execution.
  - current runtime effect: None

- **permission planning**
  - purpose: Governance and security design.
  - what it may describe: Permissions, approval boundaries, levels.
  - what it may not authorize: Runtime permissions, live system changes.
  - current runtime effect: None

- **safety boundary planning**
  - purpose: Ensuring system stability and risk mitigation.
  - what it may describe: Safety boundaries, risk levels, denied actions.
  - what it may not authorize: Runtime execution, runtime safety gates.
  - current runtime effect: None

- **operator governance**
  - purpose: Establishing authority and protocol relationship.
  - what it may describe: Operator authority, builder prohibitions, stop conditions.
  - what it may not authorize: Runtime changes.
  - current runtime effect: None

- **task taxonomy**
  - definition: Categorizing work types.
  - what it may describe: Task categories, boundaries, worker/task relationships.
  - what it may not authorize: Execution, task enqueueing.
  - current runtime effect: None

- **worker glossary**
  - definition: Terminology and naming conventions.
  - what it may describe: Worker family labels, lifecycle states.
  - what it may not authorize: Starting processes.
  - current runtime effect: None

- **documentation index**
  - purpose: References and tracking.
  - what it may describe: Document set status.
  - what it may not authorize: Roadmap selection, runtime activity.
  - current runtime effect: None

## Runtime Parking Summary

Station Chief runtime is parked at v4.7.0.

While parked:
- do not create v4.8
- do not modify runtime files
- do not modify validators
- do not modify release locks
- do not run runtime layer build prompts
- do not continue Station Chief ladder work

Station Chief resumes only when the operator explicitly assigns a Station Chief runtime task.

## Operator Authority Summary

- the operator controls project direction
- builder agents execute only assigned tasks
- builder agents do not select next tasks
- builder agents do not recommend roadmap direction
- builder agents do not expand scope
- builder agents do not create optional files
- builder agents report only the requested confirmations

## Non-Runtime Documentation Boundary

Documentation may describe:
- concepts
- categories
- terms
- permissions
- safety boundaries
- operator authority
- future possibilities

Documentation may not:
- authorize runtime behavior
- create workers
- start processes
- execute tasks
- enqueue tasks
- create queues
- route live work
- call APIs
- use network
- deploy
- modify production
- create v4.8

## File Creation and Modification Rules

- this document may create only its own index file
- this document may not modify referenced documents
- this document may not modify runtime files
- this document may not modify validators
- this document may not modify release locks
- this document may not create generated caches
- this document may not create optional companion files

## Documentation Status Table

| Area | Current Non-Runtime Coverage | Runtime Effect | Notes |
|---|---|---|---|
| Worker architecture | Present | None | File exists |
| Permissions | Present | None | File exists |
| Safety boundaries | Present | None | File exists |
| Operator authority | Present | None | File exists |
| Task taxonomy | Present | None | File exists |
| Worker glossary | Present | None | File exists |
| Documentation indexing | Present | None | File exists |

## Always-Denied Actions

- Station Chief v4.8 creation
- Station Chief runtime modification
- validator modification
- release lock modification
- worker process start
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

## Low-Model-Safe Documentation Work Categories

- index formatting
- glossary formatting
- taxonomy formatting
- table cleanup
- denied-action wording cleanup
- documentation consistency review
- status table maintenance

## High-Model Reserved Work Categories

- Station Chief v4.8+
- runtime architecture
- validator redesign
- worker routing logic
- external tool integration
- production execution candidates
- architecture refactors

## Runtime Authorization Boundary

This document is not runtime authorization.

- documentation indexes do not create runtime behavior
- documentation status does not grant permissions
- documentation references do not activate workers
- documentation references do not select next tasks
- documentation references do not create v4.8
- future approval still requires explicit operator instruction

## Final Note

This document is planning-only and should not be treated as runtime authorization.
