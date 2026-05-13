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

## Phase 4B: Auth & Permissions Planning

Phase 4B defines the security architecture and permission model required for future interactive capabilities.

### Planning Docs
- [Auth & Permissions Plan](./phase_4b_auth_permissions_plan.md)
- [Role Model](./phase_4b_role_model.md)
- [Endpoint Permission Matrix](./phase_4b_endpoint_permission_matrix.md)
- [Secret Handling Plan](./phase_4b_secret_handling_plan.md)
- [Audit Logging Plan](./phase_4b_audit_logging_plan.md)
- [Rate Limit & Abuse Plan](./phase_4b_rate_limit_and_abuse_plan.md)
- [Threat Model](./phase_4b_threat_model.md)
- [Action Queue Concept](./phase_4b_action_queue_concept.md)
- [Dashboard UI Implications](./phase_4b_dashboard_ui_implications.md)

## Future Phases
- **Phase 4B**: Auth/permissions planning.
- **Phase 4C**: Read-only GitHub integration.
- **Phase 4D**: Controlled action request queue.
- **Phase 5+**: Mutation layer (if approved).
