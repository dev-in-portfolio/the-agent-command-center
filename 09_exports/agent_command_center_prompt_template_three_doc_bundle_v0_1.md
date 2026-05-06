# Agent Command Center Prompt Template — Three-Document Bundle v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime prompt-template documentation only.
- This document does not modify runtime behavior.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
Provide a reusable copy/paste template for creating exactly three non-runtime documentation files.

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

## Reusable Three-Document Bundle Prompt Template
```markdown
STRICT EXECUTION MODE.

AUTHORITY RULE:
The operator controls project direction. Do not recommend, select, or suggest next tasks. Do not include a “next steps” section unless explicitly requested. Do not act as roadmap owner. Do not expand scope. Do not create optional files. This task ends after creating the requested documents and reporting the required confirmations.

REPO: dev-in-portfolio/agent-command-center
Branch: master

TASK: [INSERT_TASK_DESCRIPTION]

CURRENT CONTEXT:
- Station Chief runtime is parked at v4.7.0.
- v4.8 must not be created.

DO NOT MODIFY:
- 10_runtime/*
- scripts/validate_station_chief_runtime_*
- All core Station Chief and existing documentation files.

CREATE EXACTLY THESE THREE FILES:
1. [PATH1]
2. [PATH2]
3. [PATH3]

CONTENT REQUIREMENTS:
[INSERT_CONTENT_SPEC]

VALIDATION:
Run:
git status --short
git diff --name-only

Allowed changed files only:
[PATH1]
[PATH2]
[PATH3]

COMMIT:
git add [PATH1] [PATH2] [PATH3]
git commit -m "[INSERT_COMMIT_MSG]"
git push origin master

REPORT BACK ONLY:
1. Files created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation this is planning-only
6. Confirmation no next task was selected or suggested
```

## Required Placeholder Fields
- [INSERT_TASK_DESCRIPTION]
- [PATH1], [PATH2], [PATH3]
- [INSERT_CONTENT_SPEC]
- [INSERT_COMMIT_MSG]

## Bundle Validation Rules
- exact file count: three
- exact file paths
- no optional files
- no existing doc modifications unless explicitly allowed
- global content rules
- per-document content placeholders
- validation allowed files only
- commit only listed files
- report back only

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
