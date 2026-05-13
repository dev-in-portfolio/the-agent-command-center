# Phase 4B: Audit Logging Plan

## Design
A persistent, immutable ledger of all meaningful backend interactions is required for security and transparency.

## Audit Event Schema
Every event should include:
- `timestamp_utc`: ISO 8601 timestamp.
- `event_id`: Unique identifier for the log entry.
- `actor_id`: Identifier for the authenticated user.
- `role`: The role assumed by the actor at the time of the event.
- `endpoint`: The API endpoint called.
- `request_id`: Cross-reference to the specific HTTP request.
- `action_type`: e.g., `READ_STATUS`, `REQUEST_ACTION`, `APPROVE_ACTION`.
- `result`: `SUCCESS`, `DENIED`, or `ERROR`.
- `metadata`: Non-sensitive context (e.g., action ID).

## Event Types
- **Security**: Failed auth attempts, unauthorized endpoint access.
- **Lifecycle**: Dashboard builds, backend mode changes.
- **Workflow**: Action requests, approvals, and (future) execution events.

## Invariants
- **No Secret Logging**: Secrets must never be written to the audit store.
- **Immutability**: Once written, audit events must be unchangeable.
- **Persistence**: Audit data must survive branch deletions and site redeploys.

## Storage
Initial prototyping may use a secure external database or Netlify-managed store (to be decided in Phase 4C/4D).

---
*Note: This is a planning document only. No functional implementation is included in this build.*
