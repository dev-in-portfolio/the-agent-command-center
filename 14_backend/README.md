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

## Phase 4C: Read-Only Integration Planning

Phase 4C establishes the framework for safe, read-only data synchronization with external services.

### Planning Docs
- [Read-Only Integration Plan](./phase_4c_read_only_integration_plan.md)
- [Integration Source Inventory](./phase_4c_integration_source_inventory.md)
- [GitHub Read-Only Contract](./phase_4c_github_read_only_contract.md)
- [Netlify Read-Only Contract](./phase_4c_netlify_read_only_contract.md)
- [Status Snapshot Contract](./phase_4c_status_snapshot_contract.md)
- [External API Safety Rules](./phase_4c_external_api_safety_rules.md)
- [Cache & Staleness Plan](./phase_4c_cache_and_staleness_plan.md)
- [Error Handling Plan](./phase_4c_error_handling_plan.md)
- [Observability Plan](./phase_4c_observability_plan.md)
- [Dashboard Status UI Plan](./phase_4c_dashboard_status_ui_plan.md)
- [Phase 4D Gate Review](./phase_4c_phase_4d_gate_review.md)

## Phase 4C: Snapshot Prototype

Phase 4C provides a zero-secret static status artifact for dashboard visibility.

### Docs
- [Prototype Plan](./phase_4c_snapshot_prototype_plan.md)
- [Schema](./phase_4c_snapshot_schema.md)
- [Generation Contract](./phase_4c_snapshot_generation_contract.md)
- [Dashboard Contract](./phase_4c_snapshot_dashboard_contract.md)
- [Safety Report](./phase_4c_snapshot_safety_report.md)

## Phase 4D: Gate Review

Phase 4D defines the mandatory security milestones required before interactive features.

### Docs
- [Gate Review Overview](./phase_4d_gate_review.md)
- [Decision Matrix](./phase_4d_gate_decision_matrix.md)
- [Readiness Checklist](./phase_4d_action_request_readiness_checklist.md)
- [Forbidden until Approved](./phase_4d_forbidden_until_approved.md)
- [Human Approval Contract](./phase_4d_human_approval_contract.md)
- [Audit Requirements](./phase_4d_audit_requirements.md)
- [Safe Next Steps](./phase_4d_safe_next_steps.md)

## Roadmap Re-Anchor

The inserted backend safety track is now complete enough to return to the original project roadmap.

- [Original Roadmap Re-Anchor After Backend Safety Track](./original_roadmap_reanchor_after_backend_safety_track.md)

## Future Phases
- **Phase 4B**: Auth/permissions planning.
- **Phase 4C**: Read-only GitHub integration.
- **Phase 4D**: Controlled action request queue.
- **Phase 5+**: Mutation layer (if approved).
