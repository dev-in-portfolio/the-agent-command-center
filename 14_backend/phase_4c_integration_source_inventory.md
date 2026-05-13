# Phase 4C: Integration Source Inventory

This document identifies potential future read-only data sources for The Agent Command Center.

## Candidate Sources

| Source | Purpose | Data Category | Secrets Required? | Mutation Risk |
|---|---|---|---|---|
| GitHub Repo | Basic metadata | Public | No | None |
| GitHub Branches | List active work | Public/Private | Yes (for private) | None |
| GitHub PRs | Track merge readiness | Public/Private | Yes (for private) | None |
| GitHub Actions | Workflow run status | Workflow status | Yes | None |
| GitHub Checks | Commit status | Status results | Yes | None |
| Netlify Deploys | Track hosting status | Deploy logs | Yes | None |
| Netlify Site | Hosting config | Site metadata | Yes | None |
| Production API | Live health check | Endpoint health | No | None |
| Validator Snapshots| local test results | Snapshots | No | None |
| Audit Events | interaction history | Events | No | None |

## Safe Fallback Strategy
If any external source is unavailable (e.g., rate limited or network failure), the dashboard should display the last known-good state with a prominent "Stale" or "Offline" warning.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
