# Agent Command Center Document Crosswalk v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime document relationship map.
- This document does not modify referenced documents.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
This document maps how the non-runtime planning documents relate to each other so the operator can understand coverage without allowing builder agents to choose future work.

- this is a crosswalk only
- it does not modify referenced documents
- it does not create runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Crosswalk Principle
- document relationships are descriptive only
- related documents do not imply dependencies unless explicitly stated
- crosswalk links do not create permissions
- crosswalk links do not authorize runtime behavior
- crosswalk links do not select next tasks
- crosswalk links do not create workers, tasks, queues, routes, validators, or runtime layers

## Document Relationship Table

| Document | Primary Role | Supports | Supported By | Runtime Effect | Operator Use |
|---|---|---|---|---|---|
| Worker Architecture Map | Planning | All | None | None | Tracking |
| Permission Matrix | Governance | All | Architecture | None | Auditing |
| Safety Boundary Matrix | Governance | All | Permissions | None | Auditing |
| Operator Authority Protocol | Governance | All | None | None | Oversight |
| Task Taxonomy | Planning | All | Architecture | None | Tracking |
| Worker Family Glossary | Glossary | Taxonomy | Architecture | None | Reference |
| Documentation Index | Indexing | All | None | None | Tracking |
| Prompt Archive Index | Indexing | All | None | None | Reference |
| Status Dashboard Plan | Planning | All | All | None | Tracking |
| Handoff Status Template | Governance | All | None | None | Reporting |
| Document Crosswalk | Mapping | All | All | None | Tracking |

## Concept Coverage Matrix

| Concept | Covered By | Related Documents | Runtime Authorization | Notes |
|---|---|---|---|---|
| worker families | Worker Architecture Map | Worker Glossary | None | Design |
| worker labels | Worker Family Glossary | Worker Architecture | None | Design |
| task categories | Task Taxonomy | All | None | Design |
| task labels | Task Taxonomy | Worker Glossary | None | Design |
| permission levels | Permission Matrix | All | None | Design |
| safety boundaries | Safety Boundary Matrix | All | None | Design |
| operator authority | Operator Authority Protocol | All | None | Governance |
| builder no-freelancing | Operator Authority Protocol | All | None | Governance |
| documentation status | Documentation Index | Status Dashboard | None | Reporting |
| prompt categories | Prompt Archive Index | Documentation Index | None | Reporting |
| status dashboard fields | Status Dashboard Plan | Documentation Index | None | Tracking |
| handoff reporting | Handoff Status Template | All | None | Reporting |
| runtime parking | All | Release Lock | None | Governance |
| v4.8 denial while parked | All | Release Lock | None | Governance |

## Redundancy and Reinforcement Map

Repeated rules across documents are intentional reinforcement, not accidental duplication.

- Station Chief parked at v4.7.0
- v4.8 not created unless explicitly assigned
- no runtime modifications during non-runtime work
- no validator modifications during non-runtime work
- operator controls direction
- builder does not select next tasks
- documentation does not authorize runtime behavior

## Document Type Definitions

- **architecture map**: Describes worker structural families. No runtime effect.
- **permission matrix**: Describes access boundaries. No runtime effect.
- **safety boundary matrix**: Describes risk severity. No runtime effect.
- **authority protocol**: Describes governance roles. No runtime effect.
- **task taxonomy**: Describes task boundaries. No runtime effect.
- **worker glossary**: Describes worker terms. No runtime effect.
- **documentation index**: Describes file set. No runtime effect.
- **prompt archive index**: Describes prompt set. No runtime effect.
- **status dashboard plan**: Describes dashboard UI. No runtime effect.
- **handoff template**: Describes reporting format. No runtime effect.
- **document crosswalk**: Describes document relationships. No runtime effect.

## Operator Navigation Use

- locate the right document family
- understand coverage
- verify that runtime remains parked
- verify that no builder-selected next task exists
- verify that documentation is planning-only

## Runtime Parking Boundary

Station Chief runtime is parked at v4.7.0.

While parked:
- no v4.8
- no runtime file changes
- no validator changes
- no release lock changes
- no runtime ladder continuation

## Always-Denied Crosswalk Actions

- creating v4.8
- modifying runtime files
- modifying validators
- modifying release locks
- creating workers
- activating workers
- executing tasks
- enqueueing tasks
- creating queues
- routing live work
- calling APIs
- using network
- deploying
- production execution
- full 47,250-worker workforce activation
- selecting next task
- recommending next task

## Final Note

This document is planning-only and should not be treated as runtime authorization.
