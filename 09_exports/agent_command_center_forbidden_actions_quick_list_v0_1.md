# Agent Command Center Forbidden Actions Quick List v0.1

## Current State
- Station Chief runtime is parked at v4.7.0.
- v4.8 was not created.
- This is planning/governance documentation only.

## Denied List
- Station Chief v4.8 creation
- runtime file modification
- validator modification
- release lock modification
- worker process start
- task execution
- live task assignment
- live worker routing
- real queue creation
- queue writes
- scheduler writes
- cron writes
- API calls
- network access
- socket access
- DNS resolution
- credential use
- secret reads
- deployment
- production execution

## Parking Reminder
- Station Chief is parked.
- No ladder progression.
- No version updates.

## Builder Must Not Do
- select next task
- recommend roadmap direction
- create optional files
- broaden scope

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
