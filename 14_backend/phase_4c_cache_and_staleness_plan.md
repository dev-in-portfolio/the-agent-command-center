# Phase 4C: Cache & Staleness Plan

## Strategy
Balance data freshness with performance and API safety.

## Cache Recommendations
- **Public Data**: 1 hour TTL.
- **Internal Status**: 5 minutes TTL.
- **Validator Results**: Persistent until next build.

## Staleness Indicators
The dashboard UI must clearly indicate the age of all integrated data:
- **Fresh**: < 5 minutes.
- **Stale**: > 10 minutes.
- **Expired**: > 1 hour (Display warning).

## Unavailable State
If a source is unreachable, the UI should show the last known-good value with a high-contrast "Offline" badge and the last successful sync timestamp.

## Refresh Control
- Manual refresh should only be available to authenticated Operators.
- Automated background syncing is not allowed in Phase 4C.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
