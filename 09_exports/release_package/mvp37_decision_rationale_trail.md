# MVP-37 Decision Rationale Trail

## Decision Rationale Entries

### D-001 — Approve RC-1 for Staging Validation
- **Driver:** Staging pipeline readiness, signal corridor mid-band at 94th percentile (threshold: 90th)
- **Alternatives considered:** Hold for RC-2 bundling; rejected because RC-1 is time-independent
- **Tradeoffs accepted:** Isolated RC-1 validation adds one pipeline cycle but reduces batch risk
- **Evidence:** Smoke test report `staging/smoke/rc1-20260514`, signal corridor snapshot `corridor/20260514-midband`

### D-002 — Defer RC-2 Signal Threshold Adjustment
- **Driver:** Corridor low-band variance at 18% (threshold max: 12%). Recalibration pipeline has a projected fix window of 6 hours.
- **Alternatives considered:** Force-adjust threshold to mask variance; rejected as it would hide a real degradation pattern.
- **Tradeoffs accepted:** Deferral adds one calibration cycle. No downstream dependency is blocked.
- **Evidence:** Variance report `corridor/lowband-variance-20260514`, calibration ETA from pipeline ops.

### D-003 — Merge Signal Corridor Patch
- **Driver:** Artifact drift of 2.3% in corridor mid-band alignment. Root cause identified as a stale normalization factor.
- **Alternatives considered:** Hotfix override in config; rejected because the normalization factor is computed, not static.
- **Tradeoffs accepted:** Patch introduces a 45-minute rebuild window. Regression suite confirmed no regressions.
- **Evidence:** Drift diff report `corridor/drift-diff-20260515`, regression run `regression/20260515-r1`.

### D-004 — Escalate Corridor Volatility to Release Board
- **Driver:** Volatility index spiked to 0.37 (alert threshold: 0.30) during final corridor pass. Not release-blocking but novel.
- **Alternatives considered:** Suppress and monitor; rejected because the spike pattern does not match known noise profiles.
- **Tradeoffs accepted:** Board visibility may trigger a post-release review. Release timeline unaffected.
- **Evidence:** Volatility alert `corridor/volatility-alert-20260515`, pattern analysis attachment.

### D-005 — Approve Handoff Copy
- **Driver:** Stakeholder distribution deadline. Copy reviewed through two-pass edit cycle.
- **Alternatives considered:** Delay for third pass; rejected due to diminishing returns.
- **Tradeoffs accepted:** Minor stylistic inconsistencies deferred to post-release doc cleanup.
- **Evidence:** Reviewed copy `exports/handoff-copy-v2.md`, edit log `logs/handoff-copy-edit-cycle.md`.

### D-006 — Tag Release Candidate
- **Driver:** All checks green. Artifact build verified. Handoff package assembled.
- **Alternatives considered:** Wait for board escalation resolution; rejected because escalation is asynchronous and non-blocking.
- **Tradeoffs accepted:** None — standard tagging procedure.
- **Evidence:** Commit `a1b2c3d4`, build manifest `builds/mvp37-rc-final-manifest.json`.

## Review-to-Roadmap-to-Handoff Trace

1. Roadmap item MVP-37-42 (signal corridor stabilization) → decision D-003 → patch merged → included in RC payload
2. Roadmap item MVP-37-19 (release candidate pipeline) → decisions D-001, D-002, D-006 → RC staged, deferred item tracked
3. Roadmap item MVP-37-08 (operator handoff automation) → decisions D-004, D-005 → escalation surfaced, copy approved

## Audit Notes

- All rationale entries are based on operator review logs and pipeline telemetry.
- No rationale was retroactively modified.
- Deferred items are tracked in the MVP-37 deferred-log bucket.
- Board escalation (D-004) has a follow-up action assigned: alice to present volatility analysis at next board sync.
- This trail is append-only. Any amendments require a new entry with cross-reference to the original.
