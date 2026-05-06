# Agent Command Center Change Control Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime change control protocol.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define how proposed changes are described, scoped, approved, blocked, recorded, and reported without allowing unauthorized runtime or roadmap changes.

- this is a protocol only
- it does not auto-approve changes
- it does not modify runtime files
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Change Control Principle
- every proposed change requires clear operator description
- every change requires explicit file-scope approval
- changes must not bypass Station Chief parking
- change requests do not modify runtime
- change requests do not grant permission
- change requests do not choose next tasks

## Change Request Fields
- change_id: Identifier.
- change_title: Descriptive name.
- change_type: Classification.
- requested_by: Operator.
- approved_by_operator: Boolean.
- allowed_files: List of authorized paths.
- denied_paths: List of protected paths.
- expected_file_count: Expected change count.
- runtime_effect: Explanation. Ex: None.
- validator_effect: Explanation. Ex: None.
- release_lock_effect: Explanation. Ex: None.
- v4_8_effect: Explanation. Ex: None.
- validation_required: List of checks.
- commit_allowed: Boolean.
- push_allowed: Boolean.
- status: Enumerated state.
- notes: Tracking notes.

## Change Types
- documentation creation
- documentation bundle creation
- existing documentation modification
- prompt drafting
- check-only verification
- targeted fix
- runtime change
- validator change
- release lock change
- v4.8 creation
- API/network change
- deployment change
- production change

## Change Status Values
- Drafted
- Operator Assigned
- Approved
- Blocked
- In Progress
- Landed
- Rejected
- Superseded
- Parked
- Needs Review

## Change Control Table Template

| Change ID | Change Type | Approved By Operator | Allowed Files | Runtime Effect | Validator Effect | Release Lock Effect | v4.8 Effect | Status | Operator Review |
|---|---|---|---|---|---|---|---|---|---|
| [ID] | [TYPE] | [YES/NO] | [FILES] | None | None | None | None | [STATUS] | [YES/NO] |

## Approval Requirements
- documentation changes require exact file list
- existing document modification requires explicit allowance
- runtime changes require explicit runtime scope
- validator changes require explicit validator scope
- release lock changes require explicit release lock scope
- v4.8 changes require explicit v4.8 assignment
- API/network/deployment/production require explicit separate approval

## Denied Change Patterns
- broad refactor without file scope
- runtime modification during documentation task
- validator modification during documentation task
- release lock modification during documentation task
- creating v4.8 while parked
- adding optional files
- modifying protected exports

## Change Failure Response
- stop
- report exact failure
- do not stage
- do not commit
- do not push
- do not broaden scope
- do not auto-fix unless explicitly assigned
- do not recommend next task

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- change control records do not create runtime behavior
- change control records do not grant permissions
- change control records do not create validators
- change control records do not create workers
- change control records do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
