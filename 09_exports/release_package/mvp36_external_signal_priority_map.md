# MVP-36 External Signal Priority Map

## Investor Signals
| Signal Theme | Source | Confidence | Mapped Priority Area | Impact |
|---|---|---|---|---|
| Portfolio lacks clear narrative flow | Investor demo Q2 | 4 | User Experience | Medium |
| Growth metrics not visible in landing | Investor demo Q2 | 5 | Feature Development | High |
| Competitive differentiators unclear | Investor sync | 3 | Documentation | Low |
| Request for integration roadmap | Investor follow-up | 4 | Ecosystem | Medium |

## Recruiter Signals
| Signal Theme | Source | Confidence | Mapped Priority Area | Impact |
|---|---|---|---|---|
| Work history timeline confusing | Recruiter walkthrough A | 4 | User Experience | Medium |
| Skills section lacks depth | Recruiter walkthrough B | 3 | Feature Development | Low |
| Project descriptions need metrics | Recruiter feedback session | 5 | Documentation | High |
| Contact flow is unclear | Recruiter walkthrough A | 4 | Infrastructure | Medium |

## Technical Reviewer Signals
| Signal Theme | Source | Confidence | Mapped Priority Area | Impact |
|---|---|---|---|---|
| Build pipeline missing validation step | Tech review session 12 | 5 | Infrastructure | High |
| Dependency update frequency too low | Code review Q2 | 4 | Infrastructure | Medium |
| Test coverage gaps in integration layer | Peer review notes | 4 | Feature Development | Medium |
| API response time degradation observed | Performance review | 3 | Infrastructure | Low |
| Accessibility audit reveals contrast issues | A11y review | 4 | User Experience | Medium |

## Priority Impact Assessment
- **High-impact signals** (rating 4-5): Eligible for immediate roadmap recommendation. Require operator review within current sync cycle.
- **Medium-impact signals** (rating 3): Queued for next sync cycle unless operator exercises discretion to expedite.
- **Low-impact signals** (rating 1-2): Logged to signal backlog. Re-evaluated at quarterly roadmap review.
- **Cross-cutting signals**: Any signal that maps to 3 or more priority areas is elevated to high impact regardless of individual ratings.

## Operator Decision Log
| Decision ID | Signal | Decision | Rationale | Operator | Date |
|---|---|---|---|---|---|
| SIG-2026-001 | Growth metrics visibility | Escalate to roadmap | High confidence, direct investor ask | TAC | 2026-05-10 |
| SIG-2026-002 | Work history timeline | Defer to next cycle | Medium confidence, needs UX exploration | TAC | 2026-05-10 |
| SIG-2026-003 | Build pipeline validation | Escalate to roadmap | High confidence, blocking concern | TAC | 2026-05-10 |
| SIG-2026-004 | Competitive differentiators | Archive | Low confidence, insufficient signal strength | TAC | 2026-05-10 |
| SIG-2026-005 | Project description metrics | Escalate to roadmap | High confidence, recruiter priority | TAC | 2026-05-10 |
| SIG-2026-006 | Accessibility contrast issues | Defer to next cycle | Medium confidence, non-critical | TAC | 2026-05-10 |

## Pending Signal Review Queue
- SIG-2026-007: Dependency update frequency — awaiting additional data points.
- SIG-2026-008: API response time degradation — awaiting second measurement.
- SIG-2026-009: Integration roadmap request — awaiting investor clarification.
