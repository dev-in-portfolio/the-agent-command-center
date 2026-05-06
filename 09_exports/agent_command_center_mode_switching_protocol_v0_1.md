# Agent Command Center Mode Switching Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime mode switching protocol.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This protocol defines how the operator switches between low-model work, high-model reserved work, parked runtime state, documentation mode, check mode, and fix mode.

- this is a protocol only
- it does not switch modes automatically
- it does not resume Station Chief
- it does not create runtime behavior
- it does not grant permissions
- it does not authorize v4.8

## Mode Switching Principle
- only the operator switches modes
- builder agents do not switch modes for the operator
- builder agents do not infer mode changes from context
- builder agents do not treat model availability as authorization
- builder agents do not resume Station Chief unless explicitly assigned
- builder agents do not create v4.8 unless explicitly assigned

## Defined Modes

- **Station Chief Parked Mode**
  - definition: Runtime environment locked at v4.7.0.
  - allowed behavior: None related to runtime.
  - denied behavior: Modifying runtime, validators, release locks.
  - entry condition: Explicit operator parking.
  - exit condition: Explicit operator resume.
  - runtime effect: None.
  - operator authority requirement: High.

- **Low-Model Documentation Mode**
  - definition: Safe documentation-only work.
  - allowed behavior: Drafting governance/planning docs.
  - denied behavior: Runtime/validator modification.
  - entry condition: Operator assigns documentation task.
  - exit condition: Documentation task completion.
  - runtime effect: None.
  - operator authority requirement: Low.

- **High-Model Reserved Mode**
  - definition: Reserved for runtime, architecture, or validation redesigns.
  - allowed behavior: Complex runtime/safety reasoning.
  - denied behavior: Unauthorized modification.
  - entry condition: Operator assigns runtime-layer task.
  - exit condition: Task completion/parking.
  - runtime effect: None.
  - operator authority requirement: High.

- **Check Mode**
  - definition: Verifying current repository state.
  - allowed behavior: Running read-only checks.
  - denied behavior: Modifying state.
  - entry condition: Operator "check please".
  - exit condition: Status report.
  - runtime effect: None.
  - operator authority requirement: None.

- **Prompt Drafting Mode**
  - definition: Drafting operator commands.
  - allowed behavior: Markdown/plain text drafting.
  - denied behavior: Running/executing prompts.
  - entry condition: Operator assigns prompt-drafting task.
  - exit condition: Draft completion.
  - runtime effect: None.
  - operator authority requirement: Low.

- **Fix Mode**
  - definition: Repairing specific issues.
  - allowed behavior: Targeted file scope edits.
  - denied behavior: Broad refactoring.
  - entry condition: Operator assigns fix task.
  - exit condition: Fix landing.
  - runtime effect: State modification.
  - operator authority requirement: High.

- **Runtime Build Mode**
  - definition: Initiating new Station Chief layers.
  - allowed behavior: Building runtime layers.
  - denied behavior: Modifying locked layers.
  - entry condition: Operator assigns build task.
  - exit condition: Layer landing.
  - runtime effect: New runtime layer.
  - operator authority requirement: High.

- **Validation Mode**
  - definition: Running the validation chain.
  - allowed behavior: Executing existing validators.
  - denied behavior: Modifying validators.
  - entry condition: Operator validation request.
  - exit condition: Validator report.
  - runtime effect: None.
  - operator authority requirement: None.

- **Handoff Mode**
  - definition: Summarizing completed task work.
  - allowed behavior: Reporting confirmations.
  - denied behavior: Modifying codebase.
  - entry condition: Task phase completion.
  - exit condition: Report submission.
  - runtime effect: None.
  - operator authority requirement: Low.

- **Stop/Pause Mode**
  - definition: Immediate work cessation.
  - allowed behavior: None.
  - denied behavior: Any activity.
  - entry condition: Stop command or violation detection.
  - exit condition: Operator restart.
  - runtime effect: None.
  - operator authority requirement: Absolute.

## Mode Table

| Mode | Entry Trigger | Allowed Work | Denied Work | Runtime Effect | Can Builder Enter Automatically |
|---|---|---|---|---|---|
| Station Chief Parked | Operator Command | None | Runtime Ladder | None | No |
| Low-Model Doc | Operator Command | Planning Docs | Runtime Logic | None | No |
| High-Model Reserved | Operator Command | Runtime/Architecture | Unassigned Changes | None | No |
| Check Mode | Operator Command | Verification | State Modification | None | No |
| Prompt Drafting | Operator Command | Prompt Drafting | Prompt Execution | None | No |
| Fix Mode | Operator Command | Targeted Fix | Broad Refactor | State Change | No |
| Runtime Build Mode | Operator Command | Runtime Building | Locked Layer Modification | State Change | No |
| Validation Mode | Operator Command | Run Validators | Modify Validators | None | No |
| Handoff Mode | Completion | Reporting | Development | None | No |
| Stop/Pause Mode | Stop Command | None | All | None | No |

## Station Chief Parked Mode Rules
- current Station Chief mode is parked
- current parked version is v4.7.0
- v4.8 is reserved but not created
- no runtime files may be modified
- no validators may be modified
- no release locks may be modified
- no runtime reports may be created
- no runtime ladder continuation may occur

## Low-Model Documentation Mode Rules
- low-model mode may create bounded documentation
- low-model mode may create exact files listed by operator
- low-model mode may format markdown tables
- low-model mode may draft glossaries/registers/indexes/templates
- low-model mode may not modify runtime
- low-model mode may not modify validators
- low-model mode may not create v4.8
- low-model mode may not select roadmap direction

## High-Model Reserved Mode Rules
- high-model mode is for complex runtime, validator, architecture, and execution-layer work
- high-model availability does not authorize the work
- operator still must explicitly assign the work
- high-model mode does not override Station Chief parking
- high-model mode does not automatically create v4.8

## Mode Confusion Examples

- **documentation prompt accidentally modifies runtime**: Violates mode. Builder must stop.
- **check prompt becomes fix prompt**: Violates mode. Builder must stop.
- **prompt drafting becomes execution**: Violates mode. Builder must stop.
- **high-model discussion becomes runtime authorization**: Violates mode. Builder must stop.
- **parked mode accidentally creates v4.8**: Violates mode. Builder must stop.
- **low-model mode modifies validators**: Violates mode. Builder must stop.

## Mode Transition Rules
- mode changes must be explicit
- mode changes must name the new mode or task
- mode changes must not be inferred from urgency
- mode changes must not be inferred from previous tasks
- mode changes must not be inferred from “next”
- runtime mode changes must name the runtime layer or file scope
- Station Chief resume must be explicit

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- mode labels do not grant permissions
- mode labels do not create runtime behavior
- mode labels do not create validators
- mode labels do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
