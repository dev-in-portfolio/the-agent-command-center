const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const ALLOWED_PERMISSION_SCOPES = [
  "harness:read_status",
  "harness:create_run_plan",
  "harness:validate_run_plan",
  "harness:write_audit_event",
  "harness:create_readiness_note",
  "harness:update_harness_session",
  "harness:run_allowlisted_check",
  "harness:run_allowlisted_validator",
  "harness:request_department_gate_review",
  "harness:request_runtime_cohort_activation",
  "harness:request_runtime_cohort_deactivation",
  "harness:export_report",
];

const BLOCKED_PERMISSION_SCOPES = [
  "shell:execute",
  "sql:arbitrary",
  "deploy:execute",
  "rollback:execute",
  "alerts:send",
  "agents:activate_all",
  "agents:activate_47979",
  "external_api:mutate",
  "secrets:read",
  "env:read",
  "files:unrestricted_write",
];

const ALLOWLISTED_OPERATIONS = [
  { operation_id: "run_mvp_validators", display_name: "Run MVP Validators", scope: "harness:run_allowlisted_validator", enabled: true, risk_level: "medium", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "create_readiness_note", display_name: "Create Readiness Note", scope: "harness:create_readiness_note", enabled: true, risk_level: "low", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "create_audit_event", display_name: "Create Audit Event", scope: "harness:write_audit_event", enabled: true, risk_level: "low", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "export_status_report", display_name: "Export Status Report", scope: "harness:export_report", enabled: true, risk_level: "low", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "request_department_gate_review", display_name: "Request Department Gate Review", scope: "harness:request_department_gate_review", enabled: true, risk_level: "medium", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "request_runtime_rollup", display_name: "Request Runtime Rollup", scope: "harness:run_allowlisted_check", enabled: true, risk_level: "low", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
  { operation_id: "request_harness_stop", display_name: "Request Harness Stop", scope: "harness:update_harness_session", enabled: true, risk_level: "low", dry_run_required: true, approval_required: true, command_execution_enabled: false, deploy_execution_enabled: false, rollback_execution_enabled: false, alert_sending_enabled: false },
];

const DANGEROUS_KEYWORDS = [
  "shell:execute",
  "sql:arbitrary",
  "deploy:execute",
  "rollback:execute",
  "alerts:send",
  "agents:activate_all",
  "agents:activate_47979",
  "child_process",
  "exec(",
  "spawn(",
  "eval(",
  "new Function",
  "SUPABASE_SERVICE_ROLE_KEY",
  "localStorage",
  "sessionStorage",
  "document.cookie",
  "indexedDB",
];

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "continual-harness-operator-mode") {
  return {
    statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-agent-command-center-mode": mode,
    },
    body: JSON.stringify(data, null, 2),
  };
}

function backendUnavailable(message = "Continual Harness operator backend is not configured.") {
  return jsonResponse(503, {
    ok: false,
    error: message,
  });
}

function text(value, maxLength) {
  return String(value == null ? "" : value).trim().slice(0, maxLength);
}

function parseBody(event, maxLength = 48000) {
  const raw = event && typeof event.body === "string" ? event.body : "";
  if (raw.length > maxLength) {
    throw new Error("PAYLOAD_TOO_LARGE");
  }
  return raw ? JSON.parse(raw) : {};
}

function supabaseHeaders(extra = {}) {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
    ...extra,
  };
}

async function supabaseRequest(method, path, body, extraHeaders = {}) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers: supabaseHeaders(extraHeaders),
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const bodyText = await response.text();
  const parsed = bodyText ? JSON.parse(bodyText) : null;

  if (!response.ok) {
    const error = new Error(parsed && parsed.message ? parsed.message : response.statusText);
    error.payload = parsed;
    error.status = response.status;
    throw error;
  }

  return parsed;
}

function supabaseGet(path) {
  return supabaseRequest("GET", path);
}

function supabasePost(path, body, extraHeaders = {}) {
  return supabaseRequest("POST", path, body, extraHeaders);
}

function supabasePatch(path, body, extraHeaders = {}) {
  return supabaseRequest("PATCH", path, body, extraHeaders);
}

function supabaseRpc(functionName, payload, extraHeaders = {}) {
  return supabaseRequest("POST", `rpc/${functionName}`, payload, extraHeaders);
}

async function supabaseGetAll(path, pageSize = 1000) {
  const rows = [];
  let offset = 0;

  while (true) {
    const pagePath = `${path}${path.includes("?") ? "&" : "?"}limit=${pageSize}&offset=${offset}`;
    const page = await supabaseGet(pagePath);
    if (Array.isArray(page) && page.length) {
      rows.push(...page);
    }
    if (!Array.isArray(page) || page.length < pageSize) {
      break;
    }
    offset += pageSize;
  }

  return rows;
}

function normalizeStatus(value) {
  return text(value, 80).toLowerCase();
}

function normalizeBoolean(value) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  const normalized = text(value, 12).toLowerCase();
  return normalized === "true" || normalized === "1" || normalized === "yes";
}

function normalizeNumber(value, fallback = 0, min = 0, max = Number.POSITIVE_INFINITY) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.min(Math.max(Math.trunc(parsed), min), max);
}

function getPermissionIndex(rows) {
  return new Map((rows || []).map((row) => [row.scope, row]));
}

function getOperationIndex(rows) {
  return new Map((rows || []).map((row) => [row.operation_id, row]));
}

function isAllowedPermissionScope(scope) {
  return ALLOWED_PERMISSION_SCOPES.includes(text(scope, 120));
}

function isBlockedPermissionScope(scope) {
  return BLOCKED_PERMISSION_SCOPES.includes(text(scope, 120));
}

function isDangerousPayload(value) {
  const haystack = JSON.stringify(value || {}).toLowerCase();
  return DANGEROUS_KEYWORDS.some((keyword) => haystack.includes(keyword.toLowerCase()));
}

function eventSummaryFromPlan(plan) {
  if (!plan) return "Operator run plan event";
  return `${text(plan.title, 60) || "Operator"} · ${text(plan.requested_operation, 60) || "operation"}`;
}

function buildOperatorStatus({
  session,
  permissions,
  operations,
  plans,
  events,
  notes,
  circuitBreaker,
}) {
  const permissionIndex = getPermissionIndex(permissions);
  const operationIndex = getOperationIndex(operations);
  const enabledScopes = [];
  const blockedScopes = [];

  for (const row of permissions || []) {
    if (normalizeStatus(row.status) === "enabled") {
      enabledScopes.push(row.scope);
    } else if (normalizeStatus(row.status) === "blocked") {
      blockedScopes.push(row.scope);
    }
  }

  const lastEvents = (events || []).slice(0, 20);
  const runPlans = (plans || []).slice(0, 25);

  return {
    ok: true,
    session: session || null,
    permission_scopes: {
      enabled: enabledScopes,
      blocked: blockedScopes,
      total_allowed: ALLOWED_PERMISSION_SCOPES.length,
      total_blocked: BLOCKED_PERMISSION_SCOPES.length,
    },
    allowlisted_operations: ALLOWLISTED_OPERATIONS.map((op) => ({
      ...op,
      current_status: operationIndex.get(op.operation_id) ? normalizeStatus(operationIndex.get(op.operation_id).enabled ? "enabled" : "disabled") : "enabled",
    })),
    run_plans: runPlans,
    operator_events: lastEvents,
    readiness_notes: (notes || []).slice(0, 25),
    blocked_permissions: BLOCKED_PERMISSION_SCOPES.map((scope) => ({
      scope,
      status: permissionIndex.get(scope) ? normalizeStatus(permissionIndex.get(scope).status) : "blocked",
    })),
    circuit_breaker: circuitBreaker || { breaker_status: "clear" },
  };
}

module.exports = {
  ALLOWLISTED_OPERATIONS,
  ALLOWED_PERMISSION_SCOPES,
  BLOCKED_PERMISSION_SCOPES,
  DANGEROUS_KEYWORDS,
  backendUnavailable,
  buildOperatorStatus,
  eventSummaryFromPlan,
  getOperationIndex,
  getPermissionIndex,
  isAllowedPermissionScope,
  isBlockedPermissionScope,
  isConfigured,
  isDangerousPayload,
  jsonResponse,
  normalizeBoolean,
  normalizeNumber,
  normalizeStatus,
  parseBody,
  supabaseGet,
  supabaseGetAll,
  supabasePatch,
  supabasePost,
  supabaseRequest,
  supabaseRpc,
  supabaseHeaders,
  text,
};
