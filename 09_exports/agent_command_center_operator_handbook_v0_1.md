# Agent Command Center Operator Handbook v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime operator handbook.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This handbook gives the operator a single plain-English control reference for directing builder agents, preserving Station Chief parking, and keeping documentation-only work separate from runtime work.

- this is operator guidance only
- this does not choose future work
- this does not recommend next tasks
- this does not grant permissions
- this does not activate workers
- this does not authorize APIs, network, deployment, production, or v4.8

## Operator Control Principle
- the operator controls project direction
- the operator selects tasks
- the operator approves escalation
- the operator decides when Station Chief runtime resumes
- the operator decides when high-model work starts
- the operator decides when lower-model work is acceptable
- builder agents execute assigned work only

## Station Chief Parking Rule

Station Chief runtime is parked at v4.7.0.

While parked:
- do not create v4.8
- do not modify runtime files
- do not modify validators
- do not modify release locks
- do not run runtime layer build prompts
- do not continue Station Chief ladder work
- do not create runtime-adjacent files
- do not create runtime reports

Station Chief resumes only when the operator explicitly assigns a Station Chief runtime task.

## Operator Command Types

- **check command**: Verification of system state.
- **write prompt command**: Creation of prompt records.
- **documentation creation command**: Drafting governance/planning docs.
- **fix command**: Repairing logic issues.
- **runtime build command**: Building a runtime layer (requires high-model).
- **handoff command**: Status reporting.
- **pause command**: Immediate work stop.
- **parking command**: Confirming parking state.

For each:
- allowed builder behavior: Execution of the explicit command.
- denied builder behavior: All other actions.
- runtime effect: Dependent on command type (none for docs).
- whether top-tier model is preferred: Yes for runtime build/fix/check; No for documentation/planning.

## Builder Response Expectations

Builder reports must be limited to requested confirmations.

Default report format for documentation tasks:
1. Files created
2. Commit hash
3. Confirmation no Station Chief runtime files changed
4. Confirmation no validators changed
5. Confirmation v4.8 was not created
6. Confirmation this is planning-only
7. Confirmation no next task was selected or suggested

## Operator Safety Checks

- Did the commit touch only allowed files?
- Did runtime remain parked?
- Was v4.8 avoided?
- Were validators untouched?
- Were release locks untouched?
- Did the builder avoid suggesting next tasks?
- Did the builder avoid optional files?
- Did the report include only requested confirmations?

## Low-Model Operating Mode
- low-model mode is for documentation-only work
- low-model mode may draft planning documents
- low-model mode may organize glossary/index/table content
- low-model mode may not modify runtime
- low-model mode may not touch validators
- low-model mode may not create v4.8
- low-model mode may not decide direction

## High-Model Operating Mode
- high-model mode is reserved for runtime layers, validators, architecture, execution gates, and complex code changes
- high-model mode is required before resuming Station Chief v4.8+
- high-model mode should handle deep validator reasoning and runtime safety logic
- high-model mode does not override operator authority

## Forbidden Builder Behaviors

- do not suggest next tasks
- do not select next tasks
- do not create “recommended next steps”
- do not create roadmaps unless explicitly assigned
- do not broaden scope
- do not create extra files
- do not edit unapproved files
- do not modify runtime files unless explicitly assigned
- do not modify validators unless explicitly assigned
- do not create Station Chief v4.8 unless explicitly assigned
- do not execute workers
- do not activate workers
- do not route tasks
- do not start worker processes
- do not call APIs
- do not use network
- do not deploy
- do not read credentials
- do not read secrets
- do not read environment variables

## Operator Handoff Language

- “Station Chief remains parked at v4.7.0.”
- “This task is non-runtime documentation only.”
- “Create only the listed files.”
- “Do not recommend or select the next task.”
- “Report only the requested confirmations.”
- “Stop if any unexpected file changes.”

## Always-Denied Actions

- Station Chief v4.8 creation unless explicitly assigned
- Station Chief runtime modification unless explicitly assigned
- validator modification unless explicitly assigned
- release lock modification unless explicitly assigned
- worker process start
- worker activation
- task execution
- task enqueueing
- live task assignment
- live worker routing
- live orchestration
- real queue creation
- queue writes
- scheduler writes
- cron writes
- API calls
- network access
- socket access
- DNS resolution
- credential use
- credential vault access
- secret reads
- environment variable reads
- deployment
- deployment rollback
- production execution
- production activation
- database mutation
- external tool invocation
- full 47,250-worker workforce activation

## Final Note

This handbook is planning/governance-only and should not be treated as runtime authorization.
