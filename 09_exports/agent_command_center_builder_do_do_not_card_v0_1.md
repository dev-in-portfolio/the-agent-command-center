# Agent Command Center Builder Do / Do Not Card v0.1

## Current State
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is non-runtime planning/governance documentation only.

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
- Files created/modified list.
- Latest commit hash.
- Confirmation: no runtime files changed.
- Confirmation: no validators changed.
- Confirmation: v4.8 not created.
- Confirmation: planning-only.
- Confirmation: no next task selected or suggested.

## What This Card Does Not Authorize
- This card is a reference only.
- Does not authorize any API, network, execution, deployment, or production changes.

## Runtime Authorization Boundary
- This card is not runtime authorization.
- Future approval still requires explicit operator instruction.

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
