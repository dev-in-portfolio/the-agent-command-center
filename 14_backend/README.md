# 14_backend

This directory contains documentation and planning for The Agent Command Center backend layer.

## Phase 4A: Read-Only API Foundation

Phase 4A establishes a safe, read-only backend foundation using Netlify Functions on the existing same-origin site.

### Purpose
- Provide a skeleton for backend integration.
- Confirm same-origin API reachability from the hosted dashboard.
- Establish strict safety boundaries for backend code.

### Workflow
1. Develop on `backend/phase-4-read-only-api-foundation`.
2. Push to GitHub.
3. Test on Netlify Branch Deploy / Deploy Preview.
4. Merge to `master` after verification.

### Endpoints
- `/api/health`: Basic service health and mode status.
- `/api/status`: Detailed configuration and safety status.
- `/api/backend-manifest`: List of available endpoints and capabilities.

### Safety Model
- No secrets or credentials used.
- No command execution or GitHub mutation.
- No database writes.
- No outbound API calls.
- Purely read-only responses.

## Future Phases
- **Phase 4B**: Auth/permissions planning.
- **Phase 4C**: Read-only GitHub integration.
- **Phase 4D**: Controlled action request queue.
- **Phase 5+**: Mutation layer (if approved).
