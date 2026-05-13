# Phase 4C: Dashboard Status UI Plan

## Overview
A planning-only definition of future UI components for displaying integrated status.

## Future Components

### 1. Integration Health Panel
A dashboard section showing the reachability and status of all external sources (GitHub, Netlify, Prod API).

### 2. Live Branch View
A read-only table of active repository branches with sync status and commit age.

### 3. Pull Request Tracker
A visual summary of open PRs, their merge readiness states, and CI status checks.

### 4. Deployment Card
A status card showing the current production deployment ID, branch, and health.

## UX Rules
- **No Mutation Buttons**: Direct GitHub/Netlify controls (Merge, Deploy, Delete) are forbidden in this phase.
- **Sync Labels**: Every integrated card must show a "Last synced" timestamp.
- **Click-to-Refresh**: Prefer explicit operator triggers for syncing rather than automated polling.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
