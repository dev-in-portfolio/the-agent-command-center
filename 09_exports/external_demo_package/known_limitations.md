# Known Limitations — The Agent Command Center

## Authentication
- **Manual Token Paste:** Currently requires manually pasting a Supabase user bearer token for authenticated views.
- **No Persistent Login:** Browser sessions are not yet persistent.

## Data Persistence
- **Narrow Writes:** Only request and lifecycle event creation are permitted.
- **No Deletion:** Orphaned test data must be handled at the database level.

## Product Surface
- **Blocked Actions:** Approval, Execution, and Automation are intentionally disabled.
- **Read-Only Dashboard:** The public dashboard is a read-only snapshot of system status.

## Verification
- **Manual Live Test:** End-to-end live verification with a real user token is an ongoing requirement before full external rollout.
