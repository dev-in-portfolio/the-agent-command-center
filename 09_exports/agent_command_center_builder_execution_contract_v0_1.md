# Agent Command Center Builder Execution Contract v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime builder execution contract.
- This document does not modify runtime behavior.
- This document does not authorize v4.8.

## Purpose
This contract defines the expected behavior of builder agents when executing operator-assigned tasks.

- builder agents execute only assigned tasks
- builder agents do not choose the next task
- builder agents do not act as roadmap owners
- builder agents do not create optional files
- builder agents do not modify runtime unless explicitly assigned

## Builder Contract Principle
- one prompt equals one bounded assignment
- allowed files define the work area
- denied paths define hard stops
- report-back instructions define the entire report
- optional “helpful” changes are forbidden
- builder discretion does not override operator direction

## Builder Must Do
- read the task boundary
- verify allowed files
- create only requested files
- modify only approved files
- run only requested validation
- stop on unexpected changes
- commit only approved files
- report only requested confirmations

## Builder Must Not Do
- recommend next task
- select next task
- add next-step section
- create roadmap
- broaden scope
- add optional files
- modify existing docs unless explicitly assigned
- touch runtime during documentation tasks
- touch validators during documentation tasks
- create v4.8 while parked
- use APIs
- use network
- deploy
- read secrets
- read credentials
- execute workers
- execute tasks

## Scope Boundary Contract
- CREATE ONLY means exactly those files and no others
- DO NOT MODIFY means no edits, formatting, metadata updates, or cleanup to those paths
- DO NOT means absolute denial unless later explicitly overridden
- allowed changed files must match the prompt exactly
- unexpected git diff requires stop
- dirty working tree before start requires stop

## Validation Contract
- validation must match the prompt
- validation must not run unrequested runtime build steps
- validation must not create generated caches that are committed
- validation must not silently fix unrelated issues
- validation must not weaken existing safety boundaries
- validation must not alter validators unless explicitly assigned

## Commit Contract
- stage only allowed files
- do not use broad git add unless allowed files are explicitly listed
- do not commit unexpected files
- do not commit generated cache
- do not commit runtime changes during documentation tasks
- do not push if forbidden paths changed

## Report Contract
Default documentation report must include only:
1. Files created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation v4.8 was not created
6. Confirmation this is planning-only
7. Confirmation no next task was selected or suggested

- no recommendations
- no next steps
- no roadmap suggestions
- no optional follow-ups
- no “you may want to”
- no extra analysis unless explicitly requested

## Stop Conditions
Builder must stop if:
- working tree is dirty before start
- requested file already exists without overwrite approval
- unexpected file appears in git diff
- forbidden file changes
- runtime file changes
- validator changes
- release lock changes
- v4.8 files appear
- secrets are encountered
- credentials are encountered
- task requires APIs/network
- task requires runtime execution
- task requires interpretation beyond explicit instructions

## Builder Freelancing Definition
Freelancing is defined as:
- suggesting work
- selecting work
- expanding work
- reordering work
- combining work
- creating extra artifacts
- deciding roadmap direction
- adding “helpful” changes not requested
- converting documentation tasks into runtime tasks

Freelancing is forbidden unless the operator explicitly requests recommendations.

## Runtime Authorization Boundary
- this contract is not runtime authorization
- builder contracts do not create runtime behavior
- builder contracts do not grant permissions
- builder contracts do not create validators
- builder contracts do not create workers
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
