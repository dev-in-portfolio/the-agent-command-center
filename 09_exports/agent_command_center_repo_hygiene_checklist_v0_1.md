# Agent Command Center Repo Hygiene Checklist v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime repo hygiene checklist.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define clean-repo expectations for non-runtime documentation tasks and operator audits.

- this is a checklist only
- it does not enforce repo state
- it does not modify files
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Repo Hygiene Principle
- a clean repo means only allowed files changed
- a clean repo means no runtime drift
- a clean repo means no validator drift
- a clean repo means no release lock drift
- a clean repo means no orphaned temp files
- a clean repo means no uncommitted generated cache

## Pre-Work Hygiene Checklist
- verify branch is master
- verify working tree is clean
- verify target files do not already exist unless overwrite is approved
- verify allowed files are listed
- verify denied paths are listed
- verify Station Chief is parked
- verify v4.8 is not being created
- verify no runtime files are included
- verify no validators are included
- verify no release locks are included

## During-Work Hygiene Checklist
- create only listed files
- do not modify existing docs unless allowed
- do not touch runtime files
- do not touch validators
- do not touch release locks
- do not create caches
- do not create temp directories inside repo
- do not create optional files
- do not run unrequested commands
- do not use APIs/network

## Pre-Commit Hygiene Checklist
- run git status --short
- run git diff --name-only
- compare changed files to allowed list
- confirm exact expected file count
- confirm no runtime files changed
- confirm no validators changed
- confirm no release locks changed
- confirm no v4.8 files created
- confirm no generated caches committed
- confirm no protected exports modified
- confirm no overlays modified
- confirm no ownership metadata modified

## Protected Path Categories
- **runtime files**: `10_runtime/*`
- **validator files**: `scripts/validate_station_chief_runtime_*`
- **release locks**: `10_runtime/station_chief_release_lock.py`
- **v4.8 files**: Any `v4.8` references.
- **runtime reports**: `09_exports/*_report.md` (runtime-specific)
- **dashboard/org/master exports**: `09_exports/dashboard_seed.json`, `org_chart_export.json`, `master_department_list.md`
- **Devinization overlays**: Any Devinization file.
- **ownership metadata**: Any ownership file.
- **credentials/secrets/env files**: `.env`, `*.env`.
- **generated caches**: `__pycache__`, `*.pyc`.
- **temp directories**: Any temp directory inside repo.

## Repo Hygiene Audit Table

| Hygiene Check | Expected Result | Failure Meaning | Builder Response | Commit Allowed |
|---|---|---|---|---|
| branch master | master | Wrong branch | Stop | No |
| tree clean | Clean | Dirty state | Stop | No |
| target not exists | New file | File overwrite | Stop | No |
| allowed files listed | Match | Scope drift | Stop | No |
| denied paths listed | Avoided | Forbidden access | Stop | No |
| Station Chief parked | Parked | Parking violation | Stop | No |
| v4.8 avoided | No v4.8 | Version drift | Stop | No |
| no runtime files | None | Runtime modification | Stop | No |
| no validators | None | Validator modification | Stop | No |
| no release locks | None | Lock modification | Stop | No |
| create only listed files | Exact | Scope drift | Stop | No |
| do not modify existing docs | None | Unrequested edit | Stop | No |
| no caches | None | Cache pollution | Stop | No |
| no temp directories | None | Temp pollution | Stop | No |
| no optional files | None | Scope expansion | Stop | No |
| no unrequested commands | None | Forbidden action | Stop | No |
| no APIs/network | None | Boundary breach | Stop | No |
| git status --short | Matches | Unexpected files | Stop | No |
| git diff --name-only | Matches | Scope drift | Stop | No |
| no protected exports | None modified | Export mutation | Stop | No |

## Clean Repo Definition
- working tree is clean
- only requested files were created/modified
- protected paths are completely untouched
- no runtime-related files are present in the change set
- validators are identical to branch master

## Dirty Repo Response
- stop
- report dirty files
- do not stage
- do not commit
- do not push
- do not “fix” unless explicitly assigned
- do not delete unexpected files unless explicitly assigned
- request operator review if needed

## Runtime Authorization Boundary
- this checklist is not runtime authorization
- checklist compliance does not grant permissions
- checklist compliance does not create validators
- checklist compliance does not create workers
- checklist compliance does not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
