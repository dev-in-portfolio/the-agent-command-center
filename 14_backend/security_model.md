# Phase 4A Security Model

## Boundary
The Phase 4A backend is a read-only shell that does not interact with the filesystem, external APIs, or system processes.

## Controls
- **No Secrets**: No environment variables containing secrets are read.
- **No Credentials**: No authentication tokens or credentials are used.
- **No Command Execution**: `child_process` and similar modules are strictly forbidden.
- **No GitHub Mutation**: Git and GitHub CLI operations are forbidden.
- **No Database Writes**: No database integration is included in this phase.
- **No External Calls**: Outbound network requests are forbidden.
- **Same-Origin Only**: API is only accessible via the dashboard's same origin.

## Future Auth
Any future sensitive capability will require a robust authentication and permissions layer (planned for Phase 4B).
