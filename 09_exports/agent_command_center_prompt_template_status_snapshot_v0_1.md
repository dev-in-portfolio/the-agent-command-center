# Agent Command Center Prompt Template — Status Snapshot v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime prompt-template documentation only.
- This document does not modify runtime behavior.
- This document does not authorize runtime behavior.
- This document does not authorize v4.8.

## Purpose
Provide a reusable prompt template for creating a current project status snapshot.

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

## Reusable Status Snapshot Prompt Template
```markdown
STRICT EXECUTION MODE.

AUTHORITY RULE:
The operator controls project direction. Do not recommend, select, or suggest next tasks. Do not include a “next steps” section unless explicitly requested. Do not act as roadmap owner. Do not expand scope. Do not create optional files. This task ends after creating the requested documents and reporting the required confirmations.

REPO: dev-in-portfolio/agent-command-center
Branch: master

TASK: Create current status snapshot.

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
- Include current status snapshot fields.
- Include progress counters.

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

## Required Snapshot Fields
- snapshot_title
- date
- repo
- branch
- current_master_commit
- current_visible_commit_message
- snapshot_source
- operator
- builder_role
- planning_only_confirmation

## Progress Counter Fields
- overall_project_progress
- runtime_safety_spine
- governance_doctrine
- worker_architecture
- local_execution_capability
- live_worker_automation
- full_vision
- doc_coverage
- authority_coverage
- builder_discipline
- parking_discipline
- dashboard_readiness

## Heavy-Model Reserved Fields
- v4_8_status
- runtime_file_changes
- validator_changes
- release_lock_changes
- execution_logic_status
- routing_logic_status
- queue_logic_status
- api_network_tool_logic
- production_candidate_status
- architecture_refactor_status

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
