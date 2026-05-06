# Agent Command Center Builder Do / Do Not Card v0.1

## Current State
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is planning/governance documentation only.

## Builder Must Do
- execute assigned task only
- create only listed files
- validate allowed file list
- stop on unexpected files
- report only requested confirmations

## Builder Must Not Do
- select next task
- recommend roadmap direction
- create optional files
- modify runtime during documentation work
- modify validators during documentation work
- create v4.8 while parked

## Stop Conditions
- dirty working tree before start
- unexpected file changes
- forbidden path touched
- runtime file changes
- validator changes
- secrets encountered
- API/network requirements
- deployment requirements
- production requirements

## Report-Back Rules
- Files created/modified.
- Commit hash.
- Confirmation: no runtime files changed.
- Confirmation: no validators changed.
- Confirmation: v4.8 was not created.
- Confirmation: planning-only.
- Confirmation: no next task was selected or suggested.

## What This Card Does Not Authorize
- This card is a reference, not an execution trigger.
- Does not authorize any API, network, execution, or production changes.

## Runtime Authorization Boundary
- This card is not runtime authorization.
- Future runtime approval requires explicit operator instruction.

## Final Note
This document is planning-only and should not be treated as runtime authorization.
