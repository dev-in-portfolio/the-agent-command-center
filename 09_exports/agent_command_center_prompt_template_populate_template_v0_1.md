# Agent Command Center Prompt Template — Populate Existing Template Into New Current File v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime prompt-template documentation only.
- This document does not modify runtime behavior.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
Provide a reusable prompt template for creating populated current-state versions of existing templates without modifying the original template files.

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

## Reusable Populate-Template Prompt Template
```markdown
STRICT EXECUTION MODE.

AUTHORITY RULE:
The operator controls project direction. Do not recommend, select, or suggest next tasks. Do not include a “next steps” section unless explicitly requested. Do not act as roadmap owner. Do not expand scope. Do not create optional files. This task ends after creating the requested documents and reporting the required confirmations.

REPO: dev-in-portfolio/agent-command-center
Branch: master

TASK: Populate [INSERT_TEMPLATE_PATH] into [INSERT_OUTPUT_PATH] with current facts.

CURRENT CONTEXT:
- Station Chief runtime is parked at v4.7.0.
- v4.8 must not be created.

DO NOT MODIFY:
- 10_runtime/*
- scripts/validate_station_chief_runtime_*
- All core Station Chief and existing documentation files.
- [INSERT_TEMPLATE_PATH] (DO NOT MODIFY TEMPLATE)

CREATE ONLY:
[INSERT_OUTPUT_PATH]

CONTENT REQUIREMENTS:
- Populate using known facts for [INSERT_DATE].
- Include current master commit: [INSERT_HASH].
- Include current progress counters: [INSERT_PROGRESS_COUNTERS].

VALIDATION:
Run:
git status --short
git diff --name-only

Allowed changed file only:
[INSERT_OUTPUT_PATH]

COMMIT:
git add [INSERT_OUTPUT_PATH]
git commit -m "[INSERT_COMMIT_MSG]"
git push origin master

REPORT BACK ONLY:
1. File created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation this is planning-only
6. Confirmation no next task was selected or suggested
```

## Required Placeholder Fields
- [INSERT_TEMPLATE_PATH]
- [INSERT_OUTPUT_PATH]
- [INSERT_DATE]
- [INSERT_HASH]
- [INSERT_PROGRESS_COUNTERS]
- [INSERT_COMMIT_MSG]

## Source Template Rules
- do not modify original template file
- perform no runtime modifications
- no validator modifications
- no release lock modifications

## Output File Rules
- must match output path exactly
- must contain populated facts
- no runtime-adjacent work
- no optional files

## Denied Uses
- Any runtime modification.
- Selection of next tasks.
- Broadening scope.
- Suggesting roadmap direction.
- Creation of optional files.

## Runtime Authorization Boundary
- This template is not runtime authorization.
- Future approval still requires explicit operator instruction.

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
