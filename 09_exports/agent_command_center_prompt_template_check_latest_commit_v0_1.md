# Agent Command Center Prompt Template — Check Latest Commit v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime prompt-template documentation only.
- This document does not modify runtime behavior.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
Provide a reusable check-only prompt template for inspecting latest visible master state.

- this is a template only
- it does not create executable prompts
- it does not run prompts
- it does not choose future work
- it does not grant permissions
- it does not authorize runtime behavior
- it does not authorize v4.8

## Template Boundary
- This template provides structure only.
- It does not authorize execution.
- It does not select future work.

## Reusable Check-Only Prompt Template
```markdown
STRICT EXECUTION MODE.

AUTHORITY RULE:
The operator controls project direction. Do not recommend, select, or suggest next tasks. Do not include a “next steps” section unless explicitly requested. Do not act as roadmap owner. Do not expand scope. Do not create optional files. This task ends after creating the requested documents and reporting the required confirmations.

REPO: dev-in-portfolio/agent-command-center
Branch: master

TASK: Inspect latest visible master state.

CURRENT CONTEXT:
- Station Chief runtime is parked at v4.7.0.
- v4.8 must not be created.

DO NOT MODIFY:
- 10_runtime/*
- scripts/validate_station_chief_runtime_*
- All core Station Chief and existing documentation files.

ALLOWED ACTIONS:
- Inspect visible state using git log and status.
- Confirm parking state.
- Report status findings.

VALIDATION:
- Report commit hash.
- Report status.

REPORT BACK ONLY:
1. Latest commit hash
2. Station Chief runtime parking state
3. Confirmation v4.8 was not created
4. Confirmation runtime files/validators not modified
5. Confirmation planning-only check
6. Confirmation no next task was selected or suggested
```

## Allowed Check Behavior
- git status
- git log
- git diff --name-only
- file presence validation

## Denied Check Behavior
- no fixes
- no commits
- no file edits
- no next task selection
- no roadmap commentary

## Standard Check Report Format
- Commit hash: [HASH]
- Commit message: [MSG]
- Station Chief version: 4.7.0
- Parking status: Parked
- v4.8 created: No
- Runtime changes: None
- Integrity confirmation: Yes

## Progress Counter Block
- Overall project progress: [PERCENT]
- Runtime safety spine: [PERCENT]
- Governance coverage: [PERCENT]

## Runtime Authorization Boundary
- This template is not runtime authorization.
- Future approval still requires explicit operator instruction.

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
