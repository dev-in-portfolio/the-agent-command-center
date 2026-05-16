# MVP-15 — Known Limitations / Safety Boundary Report

## Status
DEFINED

## Verdict
PASS

## Intentional Limitations
- **Manual Auth:** Tokens must be manually pasted (memory-only).
- **Narrow Writes:** Only request/event creation allowed.
- **No Persistence:** Tokens are never stored in the browser.

## Safety Boundary
- **Blocked:** Update, Delete, Approve, Execute.
- **RLS:** Strictly enforced at the database level.
- **Service Role:** Never used in the frontend.

## Result
Product limitations are documented honestly as part of the safety posture.
