# Original Phase 5 — Request Intake Model

## Status
PLANNING_ONLY

## Purpose
Define the conceptual request intake fields for the interactive operator workflow system. This is a display model only — not a database schema implementation.

## Request Fields

| Field | Type | Description | Persistence |
|-------|------|-------------|-------------|
| request_id | string | Unique identifier for the request | Display only |
| created_at | timestamp | When the request was created (conceptual) | Display only |
| created_by_display | string | Display name of the creating operator | Display only |
| source_context | string | Dashboard, CLI, TUI, or API context | Display only |
| workflow_type | string | Type of workflow (request, review, audit) | Display only |
| requested_action_label | string | Human-readable action label | Display only |
| plain_language_intent | string | Operator's plain-language description of intent | Display only |
| target_scope | string | What the request targets (files, systems, configs) | Display only |
| affected_files_or_systems | string | Specific files or systems affected | Display only |
| risk_classification | string | Automated risk level (low, medium, high, critical) | Display only |
| required_review_level | string | Review level required (self, peer, senior, safety) | Display only |
| execution_allowed | boolean | Always false in Phase 5 | Display only |
| mutation_allowed | boolean | Always false in Phase 5 | Display only |
| approval_required | boolean | Whether human approval would be required | Display only |
| dry_run_required | boolean | Whether dry-run would be required before execution | Display only |
| operator_notes | string | Free-text operator notes | Display only |
| generated_summary | string | System-generated summary of the request | Display only |
| safety_warnings | list | List of safety warnings triggered by the request | Display only |
| disabled_reason | string | Why the action is disabled | Display only |
| current_state | string | Current state in the request state machine | Display only |

## Field Rules
- All fields are conceptual / display-only
- No field triggers any external system call
- No field is persisted without future storage dependency
- No field enables execution, mutation, deploy, merge, push, or PR creation
- execution_allowed and mutation_allowed are always false
- disabled_reason must contain one of the standard disabled labels

## Standard Disabled Labels
- DISABLED — PLANNING ONLY
- DISABLED — REVIEW ONLY
- DISABLED — FUTURE AUTH/STORAGE REQUIRED
- DISABLED — NO EXECUTION IN PHASE 5

## Non-Implementation Notes
- This model is not a database schema
- This model is not an API contract
- This model is not a form validation rule
- Future implementation will require separate schema design with auth, storage, and validation dependencies
