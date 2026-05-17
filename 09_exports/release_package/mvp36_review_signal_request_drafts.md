# MVP-36 Review Signal Request Drafts

## Request Candidates
| Draft ID | Source Signal | Draft Title | Draft Summary |
|---|---|---|---|
| REQ-001 | SIG-2026-001 | Growth Metrics Dashboard | Create a visible growth metrics section on the landing page for investor review. Include key indicators: active users, project count, engagement rate. |
| REQ-002 | SIG-2026-003 | CI/CD Validation Gate | Add an automated validation step to the build pipeline that runs linting, type checking, and integration tests before deploy. |
| REQ-003 | SIG-2026-005 | Metrics-First Project Display | Restructure project description layout to emphasize measurable outcomes and quantifiable results before narrative context. |
| REQ-004 | SIG-2026-006 | Accessibility Contrast Compliance | Perform a full WCAG AA contrast audit across all pages and adjust color tokens to meet minimum ratio requirements. |
| REQ-005 | SIG-2026-002 | Work History Timeline Redesign | Redesign the work history timeline view to improve chronological clarity and reduce cognitive load for recruiter scanning. |
| REQ-006 | SIG-2026-010 | Contact Flow Simplification | Reduce the number of steps in the contact flow from 4 to 2 based on recruiter feedback about friction. |

## Signal-to-Request Mapping
| Signal | Draft(s) | Mapping Confidence | Notes |
|---|---|---|---|
| Growth metrics not visible (SIG-2026-001) | REQ-001 | High | Direct 1:1 mapping from investor feedback to request |
| Build pipeline missing validation (SIG-2026-003) | REQ-002 | High | Direct technical concern with clear solution path |
| Project descriptions need metrics (SIG-2026-005) | REQ-003 | High | Clear signal from recruiter, specific ask |
| Accessibility contrast issues (SIG-2026-006) | REQ-004 | Medium | Signal is clear but scope needs operator refinement |
| Work history timeline confusing (SIG-2026-002) | REQ-005 | Medium | Signal is clear, solution needs UX exploration first |
| Contact flow unclear (SIG-2026-010) | REQ-006 | High | Direct feedback with actionable simplification path |

## Operator Review Notes
- **REQ-001**: Strong investor-facing value. Recommend prioritization. Note: needs analytics instrumentation (currently P2) to be completed first.
- **REQ-002**: Critical infra concern. No open questions. Ready for immediate approval if operator agrees with severity assessment.
- **REQ-003**: Requires UX mockup before implementation. Consider drafting a design spike as a precursor request.
- **REQ-004**: Well-defined scope. Low implementation risk. Recommended as a good candidate for quick win.
- **REQ-005**: Needs exploratory phase. Do not commit to full implementation until UX direction is validated.
- **REQ-006**: Simplification is clear but may break existing user flows. Recommend impact analysis before proceeding.

## Draft Status Overview
| Draft ID | Status | Operator Decision | Next Action |
|---|---|---|---|
| REQ-001 | Proposed | Pending | Awaiting operator approval |
| REQ-002 | Proposed | Pending | Awaiting operator approval |
| REQ-003 | Proposed | Pending | Awaiting operator approval |
| REQ-004 | Proposed | Pending | Awaiting operator approval |
| REQ-005 | Proposed | Pending | Awaiting UX exploration plan |
| REQ-006 | Proposed | Pending | Awaiting impact analysis |

## Rejected Draft Candidates
| Signal | Draft Idea | Rejection Rationale |
|---|---|---|
| Competitive differentiators unclear | Competitor comparison page | Signal confidence too low (3), scope too broad |
| Dependency update frequency | Automated dependency upgrade schedule | Not a roadmap concern, belongs in maintenance automation |
