# Agent Command Center Prompt Template — Closeout Packet v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime prompt-template documentation only.
- This document does not modify runtime behavior.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
Provide a reusable prompt template for creating a final non-runtime closeout packet.

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

## Reusable Closeout Packet Prompt Template
```markdown
STRICT EXECUTION MODE.

AUTHORITY RULE:
The operator controls project direction. Do not recommend, select, or suggest next tasks. Do not include a “next steps” section unless explicitly requested. Do not act as roadmap owner. Do not expand scope. Do not create optional files. This task ends after creating the requested documents and reporting the required confirmations.

REPO: dev-in-portfolio/agent-command-center
Branch: master

TASK: Create closeout review packet.

CURRENT CONTEXT:
- Station Chief runtime is parked at v4.7.0.
- v4.8 must not be created.

DO NOT MODIFY:
- 10_runtime/*
- scripts/validate_station_chief_runtime_*
- All core Station Chief and existing documentation files.

CREATE ONLY:
[INSERT_OUTPUT_PATH]

CONTENT REQUIREMENTS:
- Populate using current master commit: [INSERT_HASH].
- Include landing summaries.
- Include parking compliance summary.
- Include governance coverage summary.
- Include risk/assumption/change summaries.

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

## Required Closeout Fields
- current_context
- landed_files_summary
- coverage_summary
- parking_summary
- progress_summary
- operator_decision_placeholder

## Required Parking Fields
- parking_status: Parked
- runtime_files_protected: True
- validators_protected: True
- v4_8_status: Not created

## Required Heavy-Model Reserved Fields
- reentry_gate_summary
- compliance_audit_summary
- overall_review_packet_status

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
