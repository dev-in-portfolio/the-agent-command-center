# MVP-36 Roadmap Update Recommendations

## Priority Shift Recommendations

### Upgrade Recommendations
| Current Priority | Signal Source | Recommended Priority | Rationale |
|---|---|---|---|
| Growth metrics display | Investor | P3 → P1 | Direct investor feedback, blocking funding signal |
| Build pipeline validation | Technical | P3 → P1 | Infrastructure stability risk, blocking deploys |
| Project description with metrics | Recruiter | P3 → P2 | Repeated recruiter feedback, talent acquisition friction |

### Downgrade Recommendations
| Current Priority | Signal Source | Recommended Priority | Rationale |
|---|---|---|---|
| Theme color customization | User simulation | P2 → P4 | Low engagement in testing, no signal support |
| Animation library integration | Operator observation | P2 → P4 | No external signal mentions, internal-only concern |

### No-Change Recommendations
| Roadmap Item | Signal Check | Current Priority | Status |
|---|---|---|---|
| Contact form reliability | No conflicting signals | P2 | Hold steady |
| SEO metadata optimization | Mixed signals (1 low, 1 medium) | P3 | Hold steady |
| Mobile responsive layout | No conflicting signals | P1 | Hold steady |

## New Roadmap Candidates
| Candidate | Signal Source | Proposed Priority | Description |
|---|---|---|---|
| Growth metrics dashboard | Investor signal SIG-2026-001 | P1 | Visible growth metrics on landing page for investor review |
| CI/CD validation gate | Technical signal SIG-2026-003 | P1 | Automated validation step in build pipeline |
| Metrics-first project display | Recruiter signal SIG-2026-005 | P2 | Restructure project descriptions around measurable outcomes |
| Accessibility contrast pass | Technical signal SIG-2026-006 | P3 | WCAG contrast compliance audit and fix pass |

## Outdated Item Flags
| Roadmap Item | Current Priority | Flag Reason | Recommended Action |
|---|---|---|---|
| Dark mode toggle | P3 | No external signal support in 3 cycles | Consider removing from active roadmap |
| Blog engine integration | P4 | No signal mentions ever | Move to icebox |
| Social feed widget | P3 | Negative signal from operator observation | Deprioritize or remove |

## Operator Review Checklist
- [ ] Review all upgrade recommendations and confirm signal confidence ratings.
- [ ] Review all downgrade recommendations and check for counter-signals.
- [ ] Evaluate new roadmap candidates for feasibility and resource availability.
- [ ] Confirm outdated item flags against current roadmap state.
- [ ] Verify no recommendation contradicts an existing committed deliverable.
- [ ] Check for dependent items that may be affected by priority shifts.
- [ ] Record approval or rejection for each recommendation in the decision log.
- [ ] Sign and date the final recommendation set before any changes are applied.

## Dependency Impact Notes
- Growth metrics dashboard (proposed P1) depends on the analytics instrumentation item currently at P2. Consider co-scheduling.
- CI/CD validation gate (proposed P1) depends on the build pipeline refactor already underway. No conflict detected.
- Metrics-first project display (proposed P2) is independent of other active items. No dependency conflicts.
