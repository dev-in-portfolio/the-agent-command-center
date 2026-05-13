# Phase 4C: Read-Only Integration Plan

## Overview
Phase 4C outlines the strategy for integrating The Agent Command Center with external services (e.g., GitHub, Netlify) in a strictly read-only manner. This integration allows the dashboard to display real-time system status without introducing mutation risk.

## Purpose
- Define the scope of read-only integrations.
- Establish security boundaries for external API interactions.
- Provide a roadmap for implementing status proxies.
- Ensure that the dashboard remains safe and operational without secrets.

## Scope
- **Planning Only**: This phase does not implement live API calls.
- **No Secrets**: All plans must function without browser-side secrets or tokens.
- **Strictly Read-Only**: No mutation (write) operations are allowed.
- **Same-Origin Only**: All API requests from the frontend must be proxied through the same-origin backend foundation established in Phase 4A.

## Integration Candidates
- **GitHub**: Repository metadata, branch lists, PR status, workflow runs.
- **Netlify**: Deploy status, site configuration (read-only).
- **Production Endpoints**: Health checks for the live dashboard and API.
- **Snapshots**: Periodic captures of validator and audit data.

## Implementation Prerequisites
- Authentication (Phase 4B) must be selected and configured before any sensitive data categories are integrated.
- Audit logging (Phase 4B) must be functional for tracking all external proxy calls.
- Secret management (Phase 4B) must be active for storing any required API tokens server-side.

## Decision Gates
- The "Snapshot vs. Live" decision must be finalized before Phase 4C implementation.
- The external API allowlist must be approved by the Maintainer.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
