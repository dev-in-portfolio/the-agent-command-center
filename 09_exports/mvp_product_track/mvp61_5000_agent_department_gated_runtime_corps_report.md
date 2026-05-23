# MVP61_5000_AGENT_DEPARTMENT_GATED_RUNTIME_CORPS_COMPLETE

- MVP60_PREREQUISITE_PASSED
- GLOBAL_LIVE_AGENT_CAP_5000
- MAX_COHORT_SIZE_500
- MAX_OPERATION_CHUNK_SIZE_250
- DEPARTMENT_GATED_ACTIVATION_REQUIRED
- RAW_5000_AGENT_ACTIVATION_BLOCKED
- FULL_47979_ACTIVATION_BLOCKED
- RUNTIME_CORPS_LIMITS_ADDED
- RUNTIME_CORPS_COHORTS_ADDED
- RUNTIME_CORPS_EVENTS_ADDED
- RUNTIME_CORPS_ROLLUPS_ADDED
- RUNTIME_CORPS_FUNCTIONS_ADDED
- RUNTIME_CORPS_UI_ADDED
- DEMO_HUB_LINK_ADDED
- FIVE_THOUSAND_IS_CAP_NOT_AUTOMATIC_COPY_ADDED
- DEPARTMENT_GATED_ACTIVATION_COPY_ADDED
- COMMAND_EXECUTION_DISABLED
- DEPLOY_EXECUTION_DISABLED
- ROLLBACK_EXECUTION_DISABLED
- ALERT_SENDING_DISABLED
- SERVICE_ROLE_SERVER_SIDE_ONLY
- NO_SERVICE_ROLE_IN_BROWSER
- NO_ARBITRARY_SQL_ENDPOINT_ADDED
- NO_ARBITRARY_COMMAND_ENDPOINT_ADDED

## What Was Built

- A department-gated runtime corps layer with a 5,000-agent cap.
- Supabase tables for limits, cohorts, chunk tracking, events, and rollups.
- Server-side Netlify functions for list, activate, deactivate, heartbeat, readiness notes, and rollups.
- A static corps UI and Demo Hub / launchpad links.

## What Is Real Now

- Department-gated activation is enforced server-side.
- Current live runtime agents are computed from the existing department gate state plus corps cohorts.
- The live page and functions stay inside the approved Netlify function surface.

## What Is Still Disabled

- Full 47,979-agent activation.
- Raw 5,000-agent activation without an approved department gate.
- Command execution.
- Deploy execution.
- Rollback execution.
- Alert sending.
- Service-role exposure in browser JS.

## Manual Setup Required

- None.

## URLs To Check

- https://the-agent-command-center.netlify.app/demo/runtime-corps.html
- https://the-agent-command-center.netlify.app/.netlify/functions/list-runtime-corps
