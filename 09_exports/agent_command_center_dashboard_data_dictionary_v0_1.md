# Agent Command Center Status Dashboard Plan v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime dashboard data dictionary.
- This document does not create a dashboard app.
- This document does not modify dashboard exports.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This data dictionary defines dashboard field names, meanings, example values, source concepts, and runtime boundaries for future operator-facing status views.

- this is a dictionary only
- it does not create live dashboard data
- it does not connect to APIs
- it does not read repo state automatically
- it does not modify runtime
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Dashboard Data Principle
- dashboard fields are descriptive only
- dashboard fields do not authorize runtime behavior
- dashboard fields do not create workers
- dashboard fields do not execute tasks
- dashboard fields do not create queues
- dashboard fields do not create routes
- dashboard fields do not modify validators
- dashboard fields do not create v4.8
- dashboard fields do not select next tasks

## Core Dashboard Fields

- **station_chief_current_version**: Current runtime version (v4.7.0).
- **station_chief_parking_status**: Parking state (Parked).
- **station_chief_next_reserved_layer**: Next reserved layer (v4.8.0).
- **v4_8_created**: Initialization status (False).
- **runtime_files_changed**: Modification status (False).
- **validators_changed**: Validator edit status (False).
- **release_locks_changed**: Lock edit status (False).
- **runtime_ladder_continued**: Progress status (False).
- **non_runtime_mode_active**: Mode check (True).
- **low_model_mode_active**: Mode check (True).
- **high_model_reserved_mode_active**: Mode check (False).
- **builder_freelancing_detected**: Behavior tracking (False).
- **next_task_selected_by_builder**: Roadmap tracking (False).
- **optional_files_created**: Scope check (False).
- **unexpected_files_changed**: Scope check (False).
- **forbidden_paths_touched**: Safety boundary check (False).
- **current_master_commit**: Latest git head.
- **latest_landing_commit**: Most recent landing.
- **latest_bundle_name**: Bundle identifier.
- **planning_only_confirmation**: Governance confirmation (True).

## Documentation Coverage Fields

- **worker_architecture_map_status**: Architecture map present.
- **permission_matrix_status**: Permission matrix present.
- **safety_boundary_matrix_status**: Safety boundary matrix present.
- **operator_authority_protocol_status**: Authority protocol present.
- **task_taxonomy_status**: Task taxonomy present.
- **worker_family_glossary_status**: Worker family glossary present.
- **documentation_index_status**: Documentation index present.
- **prompt_archive_index_status**: Prompt archive index present.
- **status_dashboard_plan_status**: Dashboard plan present.
- **handoff_status_template_status**: Handoff template present.
- **document_crosswalk_status**: Document crosswalk present.
- **operator_handbook_status**: Operator handbook present.
- **builder_execution_contract_status**: Builder contract present.
- **low_model_work_protocol_status**: Low-model protocol present.
- **high_model_reservation_protocol_status**: High-model protocol present.
- **runtime_parking_register_status**: Parking register present.
- **forbidden_actions_register_status**: Forbidden actions register present.
- **landing_audit_checklist_status**: Audit checklist present.
- **operator_control_register_status**: Control register present.
- **command_language_glossary_status**: Command language glossary present.
- **mode_switching_protocol_status**: Mode switching protocol present.
- **status_vocabulary_register_status**: Status vocabulary register present.
- **approval_phrase_register_status**: Approval phrase register present.
- **scope_boundary_templates_status**: Scope boundary templates present.

## Dashboard Data Table

| Field Name | Meaning | Example Value | Allowed Values | Runtime Effect | Authorizes Future Work |
|---|---|---|---|---|---|
| station_chief_current_version | Runtime version | 4.7.0 | v4.7.0 | None | No |
| station_chief_parking_status | Parking state | Parked | Parked | None | No |
| station_chief_next_reserved_layer | Next layer | v4.8.0 | v4.8.0 | None | No |
| v4_8_created | Init status | False | True/False | None | No |
| runtime_files_changed | Modification status | False | True/False | None | No |
| validators_changed | Validator status | False | True/False | None | No |
| release_locks_changed | Lock status | False | True/False | None | No |
| runtime_ladder_continued | Progress status | False | True/False | None | No |
| non_runtime_mode_active | Mode check | True | True/False | None | No |
| low_model_mode_active | Mode check | True | True/False | None | No |
| high_model_reserved_mode_active | Mode check | False | True/False | None | No |
| builder_freelancing_detected | Behavior status | False | True/False | None | No |
| next_task_selected_by_builder | Roadmap status | False | True/False | None | No |
| optional_files_created | Scope status | False | True/False | None | No |
| unexpected_files_changed | Scope status | False | True/False | None | No |
| forbidden_paths_touched | Safety status | False | True/False | None | No |
| current_master_commit | Git hash | [HASH] | String | None | No |
| latest_landing_commit | Git hash | [HASH] | String | None | No |
| latest_bundle_name | Bundle ID | [NAME] | String | None | No |
| planning_only_confirmation | Governance | True | True/False | None | No |

## Documentation Field Table

| Field Name | Document Family | Expected Status Values | Runtime Effect | Notes |
|---|---|---|---|---|
| worker_architecture_map_status | Architecture Planning | Present | None | File exists |
| permission_matrix_status | Permission Planning | Present | None | File exists |
| safety_boundary_matrix_status | Safety Planning | Present | None | File exists |
| operator_authority_protocol_status | Operator Governance | Present | None | File exists |
| task_taxonomy_status | Task Taxonomy | Present | None | File exists |
| worker_family_glossary_status | Worker Glossary | Present | None | File exists |
| documentation_index_status | Documentation Index | Present | None | File exists |
| prompt_archive_index_status | Prompt Archive | Present | None | File exists |
| status_dashboard_plan_status | Dashboard Planning | Created | None | Template |
| handoff_status_template_status | Handoff Reporting | Created | None | Template |
| document_crosswalk_status | Indexing | Created | None | Template |

## Status Value Definitions

- Present: File exists. Effect: None. Auth: No.
- Not Present: File missing. Effect: None. Auth: No.
- Landed: Implemented. Effect: None. Auth: No.
- Not Landed: Pending implementation. Effect: None. Auth: No.
- Parked: Version locked. Effect: None. Auth: No.
- Clean: Checks passed. Effect: None. Auth: No.
- Needs Review: Discrepancy. Effect: None. Auth: No.
- Blocked: Failed safety/security. Effect: None. Auth: No.
- Failed: System failure. Effect: None. Auth: No.
- Planning Only: Documentation context. Effect: None. Auth: No.
- Runtime Work: Authorized activity. Effect: Varies. Auth: Yes.
- Future Gated: Pending. Effect: None. Auth: No.

## Data Boundary Rules
- data dictionary fields do not read files
- data dictionary fields do not query GitHub
- data dictionary fields do not run validators
- data dictionary fields do not change repo state
- data dictionary fields do not modify dashboard exports
- data dictionary fields do not create runtime behavior
- data dictionary fields do not create v4.8

## Runtime Authorization Boundary
- this data dictionary is not runtime authorization
- field names do not grant permissions
- field names do not create validators
- field names do not create workers
- field names do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
