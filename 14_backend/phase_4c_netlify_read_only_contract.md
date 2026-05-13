# Phase 4C: Netlify Read-Only Contract

## Goal
Define the strict boundary for future read-only interactions with the Netlify API.

## Allowed Data Categories
- Site configuration (read-only).
- Deploy list and individual deploy states (Ready/Building/Failed).
- Build environment status (non-secret metadata).
- Branch deploy settings (read-only).

## Forbidden Actions
- **No Manual Deploys**: Triggering new builds or deploys is forbidden.
- **No Mutation**: Updating site settings or redirects is forbidden.
- **No Secret Access**: Reading encrypted environment variables is forbidden.
- **No Token Exposure**: Netlify Personal Access Tokens must never leave the backend.
- **No Hook Management**: Creating or deleting build hooks is forbidden.

## Implementation Rules
- Auth requirement: Operator role or higher.
- Audit logging: Mandatory for all Netlify API interactions.
- Access model: Server-side proxy only.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
