# Agent Command Center Operator-Assigned Prompt Queue Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime operator-assigned prompt queue register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register defines how operator-assigned prompts may be tracked as text-only planning records.

- this is a register only
- it does not create runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Prompt Queue Principle
- a prompt queue is a text-only record
- queue entries are design records only
- queue entries do not imply execution
- queue entries do not select next tasks
- queue entries do not create runtime behavior
- queue entries do not create v4.8

## Queue Entry Fields
- prompt_id: Deterministic string. Ex: `prompt-001`.
- prompt_title: Descriptive title. Ex: `permission-matrix-draft`.
- operator_assigned: Authoritative flag. Ex: True.
- assigned_by_operator: Operator name. Ex: Devin O’Rourke.
- prompt_family: Category family. Ex: Governance.
- risk_level: Numeric severity. Ex: Risk 0.
- mode: Session mode. Ex: Low-Model.
- expected_file_count: Integer. Ex: 1.
- expected_files: List of file paths. Ex: `09_exports/prompt.md`.
- denied_paths: List of file paths. Ex: `10_runtime/*`.
- runtime_effect: Explanation. Ex: None.
- status: Enumerated state. Ex: Drafted.
- landing_commit: Hash. Ex: [HASH].
- operator_review_required: Boolean. Ex: False.
- notes: Tracking notes. Ex: -

## Prompt Queue Status Values
- Drafted: Planning state.
- Operator Assigned: Awaiting builder work.
- Waiting: Queued for session.
- In Progress: Active drafting.
- Landed: Integrated.
- Blocked: Safety/Security stop.
- Superseded: Replaced.
- Parked: Version locked.
- Reserved: Future capability.
- Retired: Archived.

## Prompt Queue Table Template

| Prompt ID | Prompt Title | Prompt Family | Risk Level | Mode | Expected Files | Status | Landing Commit | Runtime Effect | Operator Review |
|---|---|---|---|---|---|---|---|---|---|
| [ID] | [TITLE] | [FAMILY] | [LEVEL] | [MODE] | [FILES] | [STATUS] | [HASH] | None | [YES/NO] |

## Operator Assignment Rules
- operator assigns task
- operator specifies prompt family
- operator specifies risk level
- operator specifies expected files
- builder executes only the assigned prompt
- builder reports queue status
- builder does not create queue entries for unassigned tasks

## Prompt Queue Denials
- no automatic execution
- no task selection
- no roadmap priority
- no runtime modification
- no validator modification
- no v4.8 creation
- no APIs/network
- no deployment
- no production execution

## Runtime Authorization Boundary
- this register is not runtime authorization
- queue entries do not create runtime behavior
- queue entries do not create validators
- queue entries do not create workers
- queue entries do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
