# Phase 4C: Observability Plan

## Metrics
- **Success Rate**: % of successful external syncs.
- **Latency**: Time to fetch and shape upstream data.
- **Staleness**: Distribution of data age in the dashboard.

## Logs
- Backend interaction summaries (Actor, Endpoint, Result).
- Redaction of all secrets and PII (Personally Identifiable Information).
- Request-ID correlation for end-to-end tracing.

## Production Verification
- Post-merge verification must confirm that integration endpoints respond within 2 seconds.
- Safety scans must continue to verify that no forbidden mutation patterns exist in the integration logic.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
