# Phase 4D: Audit Requirements

## Mandatory Audit Fields
- `event_type`: Security, Workflow, or Admin.
- `intent`: What was requested.
- `actor`: Authenticated user ID.
- `role`: Role assumed.
- `timestamp`: UTC.
- `result`: Success, Denied, or Failure.

## Prohibition
- **No Secret Logging**: Secrets, tokens, and PII must never be stored in the audit log.

---
*Note: Storage implementation is deferred to a future phase.*
