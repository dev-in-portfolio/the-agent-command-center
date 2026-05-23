# MVP-60 Department-Gated Runtime Expansion Report

MVP60_DEPARTMENT_GATED_RUNTIME_EXPANSION_COMPLETE
MVP59_PREREQUISITE_PASSED
DEPARTMENT_RUNTIME_GATES_ADDED
DEPARTMENT_RUNTIME_ACTIVATIONS_ADDED
DEPARTMENT_RUNTIME_GATE_EVENTS_ADDED
GLOBAL_RUNTIME_LIMITS_ADDED
GLOBAL_LIVE_AGENT_CAP_2500
PER_DEPARTMENT_CAP_250
DEPARTMENT_GATE_APPROVAL_ADDED
DEPARTMENT_GATE_BLOCKING_ADDED
DEPARTMENT_RUNTIME_ACTIVATION_ADDED
DEPARTMENT_RUNTIME_DEACTIVATION_ADDED
DEPARTMENT_GATED_RUNTIME_UI_ADDED
DEMO_HUB_LINK_ADDED
DEPARTMENT_APPROVAL_IS_NOT_COMMAND_EXECUTION_COPY_ADDED
SUPERVISED_RUNTIME_CAPACITY_ONLY_COPY_ADDED
FULL_47979_ACTIVATION_BLOCKED
COMMAND_EXECUTION_DISABLED
DEPLOY_EXECUTION_DISABLED
ROLLBACK_EXECUTION_DISABLED
ALERT_SENDING_DISABLED
SERVICE_ROLE_SERVER_SIDE_ONLY
NO_SERVICE_ROLE_IN_BROWSER
NO_ARBITRARY_SQL_ENDPOINT_ADDED
NO_ARBITRARY_COMMAND_ENDPOINT_ADDED

## What Was Built
- A department-gated runtime migration with approval, activation, blocking, and deactivation RPCs.
- A live Department-Gated Runtime expansion UI in the demo package.
- Netlify functions for listing gates, approving gates, blocking gates, activating runtime, deactivating runtime, and rollup reporting.
- Demo Hub and launchpad links for the new runtime gate surface.

## What Is Real Now
- Approved departments can open supervised runtime capacity within a global cap of 2,500.
- Gate events, activation records, and global limits are persisted server-side.
- Department approval is not command execution.
- Activation means supervised runtime capacity only.

## What Is Still Disabled
- Full 47,979-agent activation.
- Command execution.
- Deploy execution.
- Rollback execution.
- Alert sending.
- Service-role exposure in browser JS.

## Manual Setup Required
- Apply the `supabase/migrations/20260522_mvp60_department_gated_runtime_expansion.sql` migration to the live Supabase project.
- Redeploy the Netlify site after the migration is applied.

## URLs To Check
- https://the-agent-command-center.netlify.app/demo/department-gated-runtime.html
- https://the-agent-command-center.netlify.app/.netlify/functions/list-department-runtime-gates
