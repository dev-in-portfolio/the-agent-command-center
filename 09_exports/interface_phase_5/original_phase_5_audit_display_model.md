# Original Phase 5 — Audit Display Model

## Status
PLANNING_ONLY

## Purpose
Define the conceptual audit display model for the interactive operator workflow system. Phase 5 only plans audit visibility — it does not implement persistent audit storage.

## Audit Event Fields

| Field | Type | Description |
|-------|------|-------------|
| audit_event_id | string | Unique identifier for the event |
| timestamp | timestamp | When the event occurred (conceptual) |
| actor_display | string | Display name of the operator |
| event_type | string | Type of event (state_transition, draft_created, review_submitted, approved, rejected, cancelled) |
| request_id | string | Related request identifier |
| previous_state | string | State before the transition |
| next_state | string | State after the transition |
| reason | string | Reason for the transition |
| safety_boundary_status | string | Safety boundary status at time of event |
| related_report | string | Reference to any related report |
| visible_in_dashboard | boolean | Whether the event is visible in the dashboard |
| immutable_in_future_design | boolean | Whether the event should be immutable in future implementation |

## Display Rules
- All audit events are display-only in Phase 5
- No audit event is persisted without future storage dependency
- No audit event triggers any external system call
- Audit display is visible in the dashboard only
- Future implementation would require audit persistence with immutability guarantees

## Event Types

| Event Type | Description | Phase 5 Behavior |
|------------|-------------|------------------|
| state_transition | Request state changed | Display only |
| draft_created | Request draft created | Display only |
| review_submitted | Request submitted for review | Display only |
| approved | Request approved (conceptual) | Display only |
| rejected | Request rejected | Display only |
| cancelled | Request cancelled | Display only |
| expired | Request expired | Display only |
| archived | Request archived | Display only |

## Audit Trail Display Concepts
- Timeline view showing events in chronological order
- Filter by event type, state, or request
- Expandable event detail panel
- Safety boundary status shown per event
- Display-only — no export, no download, no external sharing

## Future Implementation Requirements
Before audit persistence can be implemented:
1. Auth dependency — identity verification
2. Storage dependency — append-only audit log
3. Immutability guarantee — cryptographic chain or database enforcement
4. Access control — who can view which audit events
5. Retention policy — how long events are kept
6. Export mechanism — if export is needed

## Non-Implementation Notes
- Phase 5 does not implement any audit storage
- Phase 5 does not implement any audit export
- Phase 5 does not implement any audit notification
- Phase 5 does not implement any audit webhook
- Phase 5 does not implement any audit integration with external systems
