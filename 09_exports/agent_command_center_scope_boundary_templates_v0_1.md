# Agent Command Center Scope Boundary Templates v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime scope boundary template document.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This document provides reusable prompt boundary templates for keeping builder tasks narrow, file-scoped, and operator-controlled.

- this is a template document only
- it does not create executable prompts
- it does not run prompts
- it does not select future work
- it does not grant permissions
- it does not authorize v4.8

## Scope Boundary Principle
- every task must define allowed files
- every task must define denied paths
- every task must define forbidden actions
- every task must define validation
- every task must define report-back format
- builder may not add optional files
- builder may not expand beyond the template

## Documentation Task Boundary Template

- **task name**: [TASK_NAME]
- **context**: Station Chief is parked at v4.7.0.
- **create only**: [FILE_LIST]
- **do not modify**: [FILES]
- **do not do**: [DENIED_ACTIONS]
- **content requirements**: [SPEC]
- **validation**: git status --short && git diff --name-only
- **commit instructions**: git add [FILES] && git commit -m "[MESSAGE]" && git push origin master
- **report back only**: [REPORT_ITEMS]

## Bundle Task Boundary Template

- **exact file count**: [COUNT]
- **exact file paths**: [FILE_LIST]
- **no optional files**: Mandatory
- **no existing doc modifications**: Mandatory
- **validation allowed files**: git status --short && git diff --name-only
- **commit only listed files**: Mandatory
- **report exactly listed confirmations**: Mandatory

## Check Task Boundary Template

- **check target**: [PATH]
- **allowed inspection**: [ACTIONS]
- **no file modifications**: Mandatory
- **no commits**: Mandatory
- **no fixes**: Mandatory
- **no recommendations**: Mandatory
- **report only visible findings**: Mandatory

## Fix Task Boundary Template

- **specific issue**: [ISSUE]
- **specific allowed files**: [FILES]
- **forbidden files**: [FILES]
- **validation commands**: [COMMANDS]
- **stop conditions**: [STOP_LIST]
- **commit instructions**: git add [FILES] && git commit -m "[MESSAGE]" && git push origin master
- **report confirmations**: [CONFIRMATIONS]

Note: Fix templates do not authorize v4.8 unless explicitly named.

## Runtime Build Boundary Template

- **runtime layer name**: [LAYER]
- **version target**: [VERSION]
- **allowed files**: [FILES]
- **forbidden paths**: [PATHS]
- **approval token**: [TOKEN]
- **validation chain**: [VALIDATORS]
- **safety boundaries**: [BOUNDARIES]
- **report confirmations**: [CONFIRMATIONS]

Note: This template is reserved and does not authorize runtime work.

## Stop Condition Template

- dirty working tree
- unexpected file changes
- forbidden path touched
- runtime touched during documentation task
- validators touched during documentation task
- release locks touched during documentation task
- v4.8 files appear while parked
- APIs/network required
- secrets/credentials encountered
- ambiguity causes scope risk

## Report-Back Template

1. Files created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation no release locks changed
6. Confirmation v4.8 was not created
7. Confirmation this is planning-only
8. Confirmation no next task was selected or suggested
9. Confirmation exactly [COUNT] files were created
10. Confirmation no existing planning docs were modified

## Runtime Authorization Boundary
- this template document is not runtime authorization
- templates do not create runtime behavior
- templates do not create validators
- templates do not create workers
- templates do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
