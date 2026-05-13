# Phase 4C: Snapshot Prototype Plan

## Overview
This document outlines the plan for the Phase 4C Static Status Snapshot. This prototype provides a safest-first implementation of external system visibility by using a generated JSON artifact instead of live API calls.

## Objectives
- Demonstrate a read-only integration path that requires zero runtime secrets.
- Integrate repository and deployment status into the dashboard.
- Establish a pattern for same-origin data fetching.

## Architecture
1. **Generator**: A local Python script (`build_phase4c_status_snapshot.py`) that reads existing project reports and metadata.
2. **Artifact**: A static `status_snapshot.json` file served from the dashboard's `dist/` directory.
3. **Frontend**: A dashboard panel that fetches and displays the JSON data.

## Data Sources (Static)
- Backend Phase 4 reports (Acceptance, Production Verification).
- Dashboard metadata (Version, Mode).
- Known project milestones.

## Safety Boundary
- No network requests during generation.
- No network requests from the dashboard (Same-origin only).
- No tokens or secrets in the generated JSON.

---
*Note: This is a prototype plan. The implementation is restricted to static data generated from local reports.*
