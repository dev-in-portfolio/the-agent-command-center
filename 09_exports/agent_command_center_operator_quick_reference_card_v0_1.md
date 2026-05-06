# Agent Command Center Operator Quick Reference Card v0.1

## Current State
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is planning/governance documentation only.

## Operator Controls
- next task selection
- Station Chief resume (requires explicit assignment)
- v4.8 start (requires explicit assignment)
- runtime changes (requires runtime task assignment)
- validator changes (requires validator task assignment)
- release lock changes (requires explicit assignment)
- API/network/deployment/production approval (requires specific task/token)

## Safe Commands
- check please (verification only)
- write prompt (drafting only)
- report status (summary only)
- document/bundle creation (if assigned)

## Dangerous Commands Requiring Explicit Scope
- fix (requires target and file scope)
- runtime build (requires high-model)
- validator command (requires explicit validator task)
- scope correction (requires explicit instruction)

## Parking Reminder
- Station Chief is parked at v4.7.0.
- While parked: no v4.8, no runtime changes, no release lock changes.
- Resumes only via explicit operator assignment.

## Report-Back Expectations
- Files created/modified list.
- Commit hash.
- Confirmation: no runtime files changed.
- Confirmation: no validators changed.
- Confirmation: v4.8 not created.
- Confirmation: planning-only.
- Confirmation: no next task selected or suggested.

## What This Card Does Not Authorize
- This card is a reference, not an execution trigger.
- Does not authorize any API, network, execution, or production changes.

## Runtime Authorization Boundary
- This card is not runtime authorization.
- Future runtime approval requires explicit operator instruction.

## Final Note
This document is planning-only and should not be treated as runtime authorization.
