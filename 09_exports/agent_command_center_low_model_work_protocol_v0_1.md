# Agent Command Center Low-Model Work Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This protocol defines what lower-model sessions may safely do.
- This document does not modify runtime behavior.
- This document does not authorize v4.8.

## Purpose
This document separates lower-model-safe documentation work from high-model-reserved runtime work.

- low-model work is documentation-only unless explicitly assigned otherwise
- low-model work does not choose project direction
- low-model work does not modify runtime
- low-model work does not modify validators
- low-model work does not create v4.8

## Low-Model Principle
- lower-model sessions may organize text
- lower-model sessions may draft bounded documentation
- lower-model sessions may format tables
- lower-model sessions may maintain glossaries
- lower-model sessions may create planning docs when explicitly assigned
- lower-model sessions may not perform runtime architecture changes
- lower-model sessions may not perform validator changes
- lower-model sessions may not make roadmap decisions

## Allowed Low-Model Work Categories

- **documentation drafting**
  - allowed behavior: Writing markdown files.
  - denied behavior: Execution, tool use.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **glossary drafting**
  - allowed behavior: Drafting terms/definitions.
  - denied behavior: Modifying runtime code.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **taxonomy drafting**
  - allowed behavior: Designing taxonomies.
  - denied behavior: Assignment/runtime linkage.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **index drafting**
  - allowed behavior: Maintaining document lists.
  - denied behavior: Modification of indexed docs.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **matrix formatting**
  - allowed behavior: Creating/formatting markdown tables.
  - denied behavior: Modifying matrix logic.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **operator handbook drafting**
  - allowed behavior: Writing governance text.
  - denied behavior: Modifying protocols.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **handoff template drafting**
  - allowed behavior: Writing reporting templates.
  - denied behavior: Executing handoff.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **status table drafting**
  - allowed behavior: Updating non-runtime status rows.
  - denied behavior: Modifying runtime status.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **denied-action list formatting**
  - allowed behavior: Drafting/formatting forbidden lists.
  - denied behavior: Bypassing denials.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **crosswalk drafting**
  - allowed behavior: Mapping document relationships.
  - denied behavior: Modifying runtime links.
  - runtime effect: None
  - report requirement: Standard documentation report.

- **prompt archive organization**
  - allowed behavior: Indexing prompt names.
  - denied behavior: Executing prompts.
  - runtime effect: None
  - report requirement: Standard documentation report.

## Denied Low-Model Work Categories

- Station Chief v4.8+
- runtime architecture
- validator redesign
- release lock modification
- worker routing logic
- external tool integration
- production execution candidates
- architecture refactors

For each:
- why denied in low-model mode: Requires runtime safety reasoning.
- required mode: high-model
- runtime effect if mishandled: Potential system instability or unauthorized behavior.
- operator approval required: Mandatory.

## Low-Model File Boundary
- low-model prompts must list exact files to create
- low-model prompts must not modify existing docs unless explicitly instructed
- low-model prompts must not touch runtime files
- low-model prompts must not touch validators
- low-model prompts must not touch release locks
- low-model prompts must not create runtime reports
- low-model prompts must not create v4.8 files

## Low-Model Validation Boundary
- low-model validation may run git status and git diff checks
- low-model validation may verify file presence
- low-model validation may not run runtime build prompts
- low-model validation may not alter validator logic
- low-model validation may not weaken safety tests
- low-model validation may not create generated cache commits

## Low-Model Report Boundary
Default report must include:
1. Files created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation v4.8 was not created
6. Confirmation this is planning-only
7. Confirmation no next task was selected or suggested

## Low-Model Stop Conditions
Stop if:
- runtime files change
- validators change
- release locks change
- v4.8 files appear
- unexpected files appear
- prompt asks for APIs/network
- prompt asks for deployment
- prompt asks for execution
- prompt asks for secrets/credentials
- prompt asks builder to choose next task

## Low-Model Parking Reminder

Station Chief remains parked at v4.7.0 during low-model work.

Low-model work cannot resume Station Chief.
Low-model work cannot create v4.8.
Low-model work cannot continue runtime ladder work.

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- low-model documentation does not create runtime behavior
- low-model status does not grant permissions
- future approval still requires explicit operator instruction

## Final Note

This document is planning/governance-only and should not be treated as runtime authorization.
