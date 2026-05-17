# MVP-36 Review-to-Roadmap Decision Sync

## Overview
This document defines how external review signals from MVP-36 operator sessions connect to roadmap priority decisions. All roadmap updates require explicit operator approval — no automatic promotion of feedback into the roadmap.

## External Review Signal Sources
- **Investor reviews**: Strategic alignment, market positioning, growth vector feedback received during investor demo sessions.
- **Recruiter reviews**: Talent signal, role clarity, portfolio presentation feedback from recruiter walkthroughs.
- **Technical reviewer signals**: Architecture feedback, code quality observations, dependency concerns from peer technical reviews.
- **Operator session logs**: Direct observations captured during operator-led review sessions, including pain points and friction areas.
- **User simulation signals**: Synthetic user testing outcomes that reveal usability gaps or missing capabilities.

## Priority Mapping Approach
- Each incoming signal is classified by source type, confidence level, and roadmap relevance.
- Signals are mapped to existing roadmap priority areas: Infrastructure, Feature Development, User Experience, Documentation, and Ecosystem.
- A signal must meet a minimum confidence threshold (3 out of 5) before it is eligible for roadmap consideration.
- Signals below threshold are logged to the signal backlog for future review but do not trigger recommendations.
- Mapping is performed by the operator during the sync review — no automated mapping is applied.

## Operator Review Workflow
1. **Signal ingestion**: All external signals are collected into the review signal inbox.
2. **Signal classification**: The operator classifies each signal by source, confidence, and relevance.
3. **Priority mapping**: Classified signals are mapped to roadmap priority areas manually.
4. **Recommendation generation**: The operator generates roadmap update recommendations based on mapped signals.
5. **Approval gate**: All recommendations require explicit operator approval before any roadmap changes are enacted.
6. **Sync recording**: Approved changes are recorded in the decision sync audit packet.
7. **Post-sync observation**: Changes are observed for one full review cycle before further adjustment.

## Safety Boundaries
- **No automatic updates**: Under no circumstances are review signals automatically promoted to roadmap changes.
- **Operator approval required**: Every single roadmap update derived from review signals requires explicit operator sign-off recorded in the audit packet.
- **Rollback readiness**: Any roadmap update based on review signals must have a documented rollback path before it is applied.
- **Signal freshness**: Signals older than 90 days are archived and must be re-validated before use in roadmap decisions.
- **Confidence floor**: No signal with a confidence rating below 3 may influence roadmap priority changes.
- **Audit trail**: Every decision must trace back to a specific signal, operator review session, and approval record.

## Signal Lifecycle
- New → Classified → Mapped → Recommended → Approved (or Rejected) → Applied (or Archived).
- Rejected signals are logged with the rejection rationale for future reference.
- Archived signals are retained for 12 months before deletion.

## Review Cadence
- Review-to-roadmap sync occurs every 14 days or after 5 new high-confidence signals, whichever comes first.
- Emergency signals (confidence 5, critical impact) may trigger an out-of-cycle review at operator discretion.
