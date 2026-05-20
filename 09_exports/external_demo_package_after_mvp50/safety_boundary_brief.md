# Safety Boundary Brief — Disabled Capabilities

## Disabled Capabilities

The following capabilities are explicitly disabled in the current system:

| Capability | Disabled Since | Verification |
|---|---|---|
| Public database writes | Architecture start | No write endpoints exist |
| Command execution | Architecture start | No exec endpoints exist |
| Action execution | Architecture start | No action endpoints exist |
| Automation / queue processing | Architecture start | No queue workers exist |
| Alert sending | Architecture start | No alert endpoints exist |
| Rollback execution | Architecture start | No rollback endpoints exist |
| Incident mutation | Architecture start | No incident endpoints exist |
| Deploy/merge/push from app | Architecture start | No deploy controls in app |
| API endpoints | Architecture start | No Netlify functions deployed |
| Serverless functions | Architecture start | No functions in netlify/functions/ |
| Runtime activation | Architecture start | Not started |

## Why Disabled Matters
The entire purpose of the readiness roadmap is to prove the architecture BEFORE enabling runtime. Every layer proves its schema, its contract, and its validation logic — without exposing any runtime capability. This prevents accidental execution, unauthorized actions, data corruption, and safety incidents during the review phase.

## How the System Proves Disabled Status
- `NOT_READY_FOR_REAL_AUTOMATION` marker visible on the dashboard
- `READINESS_ROADMAP_COMPLETE_PENDING_REVIEW` marker on the dashboard
- Validators check these markers and fail if removed or altered
- No Netlify functions exist in netlify/functions/
- No API routes exist
- No endpoints are defined
- No package dependencies that would enable runtime

## What Would Be Needed Before Enabling Runtime
1. A separate runtime activation plan
2. Feature flags or environment separation
3. Human approval gates for each enabled capability
4. Monitoring and alert integration
5. Rollback procedures
6. Security review
7. Stakeholder approval

## Explicit Warning
Do not enable runtime activation without a separate planning phase. This readiness architecture prevents accidents by construction. Bypassing it would remove the primary safety mechanism.
