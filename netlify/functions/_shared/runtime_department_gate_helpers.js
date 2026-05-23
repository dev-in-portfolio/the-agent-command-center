const base = require("./runtime_department_helpers");
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

// department_runtime_gates, department_runtime_activations,
// department_runtime_gate_events, and department_runtime_global_limits
// define the MVP-60 department-gated runtime persistence layer.
// approve_department_runtime_gate, block_department_runtime_gate,
// activate_department_runtime, and deactivate_department_runtime are the
// approved RPCs for the layer.

const GLOBAL_LIVE_AGENT_CAP = 2500;
const MAX_DEPARTMENT_ACTIVATION_CAP = 250;

const ALLOWED_GATE_STATUSES = new Set([
  "closed",
  "pending_review",
  "approved",
  "active",
  "blocked",
  "disabled",
]);

const ALLOWED_ACTIVATION_STATUSES = new Set([
  "requested",
  "approved",
  "active",
  "partially_active",
  "deactivated",
  "denied",
  "blocked",
]);

function supabaseRpc(functionName, payload, extraHeaders = {}) {
  return base.supabaseRpc(functionName, payload, extraHeaders);
}

function gateStatus(value) {
  return base.text(value, 80).toLowerCase();
}

function hasForbiddenExecutionFlags(payload = {}) {
  return (
    payload.command_execution_enabled === true ||
    payload.deploy_execution_enabled === true ||
    payload.rollback_execution_enabled === true ||
    payload.alert_sending_enabled === true
  );
}

function hasActivateAllFlag(payload = {}) {
  return payload.activate_all === true;
}

function gateCounts(gates) {
  const counts = {
    total_gates: 0,
    closed_gates: 0,
    pending_review_gates: 0,
    approved_gates: 0,
    active_gates: 0,
    blocked_gates: 0,
    disabled_gates: 0,
    active_agents: 0,
  };

  for (const gate of gates || []) {
    if (!gate) continue;
    counts.total_gates += 1;
    counts.active_agents += Number(gate.currently_active_agents || 0);
    const status = gateStatus(gate.gate_status);
    if (status === "closed") counts.closed_gates += 1;
    else if (status === "pending_review") counts.pending_review_gates += 1;
    else if (status === "approved") counts.approved_gates += 1;
    else if (status === "active") counts.active_gates += 1;
    else if (status === "blocked") counts.blocked_gates += 1;
    else if (status === "disabled") counts.disabled_gates += 1;
  }

  return counts;
}

function buildGateEventBuckets(gateEvents) {
  const buckets = new Map();

  for (const event of gateEvents || []) {
    if (!event || !event.department_id) continue;
    const bucket = buckets.get(event.department_id) || { count: 0, latest: null };
    bucket.count += 1;
    if (!bucket.latest || new Date(event.created_at || 0) > new Date(bucket.latest.created_at || 0)) {
      bucket.latest = event;
    }
    buckets.set(event.department_id, bucket);
  }

  return buckets;
}

function mergeGateRecords(departments, gates, gateEvents) {
  const gateMap = new Map((gates || []).map((gate) => [gate.department_id, gate]));
  const eventBuckets = buildGateEventBuckets(gateEvents);

  return (departments || []).map((department) => {
    const gate = gateMap.get(department.department_id) || null;
    const eventBucket = eventBuckets.get(department.department_id) || { count: 0, latest: null };

    return {
      ...department,
      gate_id: gate ? gate.gate_id : null,
      gate_status: gate ? gate.gate_status : "closed",
      activation_cap: gate ? Number(gate.activation_cap || 0) : 0,
      currently_active_agents: gate ? Number(gate.currently_active_agents || 0) : 0,
      approval_required: gate ? Boolean(gate.approval_required) : true,
      approved_by: gate ? gate.approved_by : null,
      approved_at: gate ? gate.approved_at : null,
      blocked_reason: gate ? gate.blocked_reason : null,
      command_execution_enabled: gate ? Boolean(gate.command_execution_enabled) : false,
      deploy_execution_enabled: gate ? Boolean(gate.deploy_execution_enabled) : false,
      rollback_execution_enabled: gate ? Boolean(gate.rollback_execution_enabled) : false,
      alert_sending_enabled: gate ? Boolean(gate.alert_sending_enabled) : false,
      gate_event_count: eventBucket.count,
      last_gate_event_at: eventBucket.latest ? eventBucket.latest.created_at : null,
      last_gate_event_type: eventBucket.latest ? eventBucket.latest.event_type : null,
      last_gate_event_summary: eventBucket.latest ? eventBucket.latest.event_summary : null,
      last_gate_event_payload: eventBucket.latest ? eventBucket.latest.event_payload : null,
    };
  });
}

function buildDepartmentGateRollup(departments, gates, config = {}) {
  const totalDepartments = (departments || []).length || Number(config.total_departments || 1777);
  const gateCountsSnapshot = gateCounts(gates);
  const eligibleDepartments = (departments || []).filter((department) => {
    return (
      gateStatus(department.runtime_status) === "eligible_for_supervised_runtime" &&
      Boolean(department.activation_eligible)
    );
  }).length;

  const liveAgents = Number(config.live_runtime_agents_enabled || gateCountsSnapshot.active_agents || 0);

  return {
    total_departments: totalDepartments,
    eligible_departments: eligibleDepartments,
    approved_gates: gateCountsSnapshot.approved_gates,
    active_gates: gateCountsSnapshot.active_gates,
    blocked_gates: gateCountsSnapshot.blocked_gates,
    pending_review_gates: gateCountsSnapshot.pending_review_gates,
    closed_gates: gateCountsSnapshot.closed_gates,
    disabled_gates: gateCountsSnapshot.disabled_gates,
    total_registered_agents: Number(config.total_registered_agents || 47979),
    global_live_agent_cap: Number(config.mvp60_global_live_agent_cap || GLOBAL_LIVE_AGENT_CAP),
    current_live_runtime_agents: liveAgents,
    max_department_activation_cap: Number(config.max_department_activation_cap || MAX_DEPARTMENT_ACTIVATION_CAP),
    full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
    department_gated_expansion_enabled: Boolean(config.department_gated_expansion_enabled),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
    source: "mvp60_department_gated_runtime_expansion",
  };
}

module.exports = {
  ALLOWED_ACTIVATION_STATUSES,
  ALLOWED_GATE_STATUSES,
  GLOBAL_LIVE_AGENT_CAP,
  MAX_DEPARTMENT_ACTIVATION_CAP,
  buildDepartmentGateRollup,
  hasActivateAllFlag,
  hasForbiddenExecutionFlags,
  gateCounts,
  gateStatus,
  mergeGateRecords,
  supabaseRpc,
  SUPABASE_URL,
  SUPABASE_SERVICE_ROLE_KEY,
};
