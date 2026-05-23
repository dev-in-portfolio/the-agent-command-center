const base = require("./runtime_department_helpers");

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const GLOBAL_LIVE_AGENT_CAP = 20000;
const MAX_DEPARTMENT_ACTIVATION_CAP = 500;
const MAX_COHORT_ACTIVATION_SIZE = 1000;
const MAX_OPERATION_CHUNK_SIZE = 500;

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data) {
  return base.jsonResponse(statusCode, data, "mvp62-20000-agent-department-gated-runtime-army");
}

function backendUnavailable(message = "Runtime army backend is not configured.") {
  return jsonResponse(503, { ok: false, error: message });
}

function text(value, maxLength) {
  return base.text(value, maxLength);
}

function parseBody(event, maxLength = 48000) {
  return base.parseBody(event, maxLength);
}

function supabaseRpc(functionName, payload, extraHeaders = {}) {
  return base.supabaseRpc(functionName, payload, extraHeaders);
}

function summarizeError(error) {
  return {
    message: error && error.message ? String(error.message) : "Unknown error",
    status: Number(error && error.status ? error.status : 0) || null,
    code: error && error.payload && error.payload.code ? String(error.payload.code) : null,
  };
}

async function safeSupabaseGet(path, fallback = null) {
  try {
    return {
      ok: true,
      data: await base.supabaseGet(path),
      error: null,
    };
  } catch (error) {
    console.error("[runtime-army] supabaseGet failed", path, summarizeError(error));
    return {
      ok: false,
      data: fallback,
      error: summarizeError(error),
    };
  }
}

async function safeSupabaseGetAll(path, fallback = []) {
  try {
    return {
      ok: true,
      data: await base.supabaseGetAll(path),
      error: null,
    };
  } catch (error) {
    console.error("[runtime-army] supabaseGetAll failed", path, summarizeError(error));
    return {
      ok: false,
      data: fallback,
      error: summarizeError(error),
    };
  }
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
  return payload.activate_all === true || payload.activate_all_departments === true || payload.activate_47979 === true;
}

function stageStatus(value) {
  return text(value, 80).toLowerCase();
}

function circuitBreakerStatus(value) {
  return text(value, 80).toLowerCase();
}

function countCohortsByStatus(cohorts) {
  const counts = {
    total_cohorts: 0,
    requested_cohorts: 0,
    approved_cohorts: 0,
    active_cohorts: 0,
    partially_active_cohorts: 0,
    deactivated_cohorts: 0,
    denied_cohorts: 0,
    blocked_cohorts: 0,
    circuit_breaker_paused_cohorts: 0,
    active_agents: 0,
  };

  for (const cohort of cohorts || []) {
    if (!cohort) continue;
    counts.total_cohorts += 1;
    counts.active_agents += Number(cohort.activated_agent_count || 0);
    const status = stageStatus(cohort.cohort_status);
    if (status === "requested") counts.requested_cohorts += 1;
    else if (status === "approved") counts.approved_cohorts += 1;
    else if (status === "active") counts.active_cohorts += 1;
    else if (status === "partially_active") counts.partially_active_cohorts += 1;
    else if (status === "deactivated") counts.deactivated_cohorts += 1;
    else if (status === "denied") counts.denied_cohorts += 1;
    else if (status === "blocked") counts.blocked_cohorts += 1;
    else if (status === "circuit_breaker_paused") counts.circuit_breaker_paused_cohorts += 1;
  }

  return counts;
}

function currentLiveRuntimeAgents(gates, cohorts) {
  const gateAgents = (gates || []).reduce((sum, item) => sum + Number(item.currently_active_agents || 0), 0);
  const cohortAgents = (cohorts || []).reduce((sum, item) => {
    const status = stageStatus(item.cohort_status);
    if (status !== "active" && status !== "partially_active") return sum;
    return sum + Number(item.activated_agent_count || 0);
  }, 0);
  return gateAgents + cohortAgents;
}

function currentUnlockedStageCap(stages) {
  const unlocked = (stages || [])
    .filter((stage) => {
      const status = stageStatus(stage.stage_status);
      return status === "unlocked" || status === "active";
    })
    .map((stage) => Number(stage.stage_cap || 0))
    .filter((value) => Number.isFinite(value));
  if (!unlocked.length) return 5000;
  return Math.max(...unlocked);
}

function currentCircuitBreakerStatus(circuitBreakers) {
  const rows = circuitBreakers || [];
  if (rows.some((row) => circuitBreakerStatus(row.breaker_status) === "triggered")) return "triggered";
  if (rows.some((row) => circuitBreakerStatus(row.breaker_status) === "paused")) return "paused";
  if (rows.some((row) => circuitBreakerStatus(row.breaker_status) === "disabled")) return "disabled";
  if (rows.some((row) => circuitBreakerStatus(row.breaker_status) === "cleared")) return "cleared";
  return "clear";
}

function buildArmyRollup(departments, gates, cohorts, stages, circuitBreakers, config = {}, events = []) {
  const cohortCounts = countCohortsByStatus(cohorts);
  const stageCap = currentUnlockedStageCap(stages);
  const breakerStatus = currentCircuitBreakerStatus(circuitBreakers);
  const approvedDepartmentGates = (gates || []).filter((gateRow) => {
    const status = String(gateRow.gate_status || "").toLowerCase();
    return status === "approved" || status === "active";
  }).length;
  const activeDepartmentGates = (gates || []).filter((gateRow) => String(gateRow.gate_status || "").toLowerCase() === "active").length;
  const liveRuntimeAgents = Number(
    config.live_runtime_agents_enabled ||
      config.current_live_runtime_agents ||
      currentLiveRuntimeAgents(gates, cohorts),
  );
  const heartbeatCount = Number(
    config.heartbeat_count ||
      events.filter((event) => stageStatus(event.event_type) === "runtime_army_heartbeat").length,
  );
  const readinessNoteCount = Number(
    config.readiness_note_count ||
      events.filter((event) => stageStatus(event.event_type) === "runtime_army_readiness_note_created").length,
  );

  return {
    total_registered_agents: Number(config.total_registered_agents || 47979),
    total_departments: Number(config.total_departments || (departments || []).length || 1777),
    global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || GLOBAL_LIVE_AGENT_CAP),
    current_live_runtime_agents: liveRuntimeAgents,
    current_stage_cap: Number(config.current_stage_cap || stageCap),
    unlocked_stages: Number(config.unlocked_stages || (stages || []).filter((stage) => {
      const status = stageStatus(stage.stage_status);
      return status === "unlocked" || status === "active";
    }).length),
    approved_department_gates: approvedDepartmentGates,
    active_department_gates: activeDepartmentGates,
    active_cohorts: cohortCounts.active_cohorts + cohortCounts.partially_active_cohorts,
    heartbeat_count: heartbeatCount,
    readiness_note_count: readinessNoteCount,
    circuit_breaker_status: circuitBreakerStatus(config.circuit_breaker_status || breakerStatus),
    full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
    department_gated_activation_required: Boolean(config.department_gated_activation_required),
    staged_activation_required: Boolean(config.staged_activation_required),
    circuit_breaker_required: Boolean(config.circuit_breaker_required),
    max_cohort_activation_size: Number(config.max_cohort_activation_size || MAX_COHORT_ACTIVATION_SIZE),
    max_operation_chunk_size: Number(config.max_operation_chunk_size || MAX_OPERATION_CHUNK_SIZE),
    source: "mvp62_20000_agent_department_gated_runtime_army",
  };
}

function mergeArmyGateRecords(departments, gates, gateEvents, cohorts, stages, circuitBreakers) {
  const gateMap = new Map((gates || []).map((gateRow) => [gateRow.department_id, gateRow]));
  const eventBuckets = new Map();
  const cohortBuckets = new Map();
  const stageMap = new Map((stages || []).map((stage) => [stage.stage_id, stage]));
  const breakerRows = circuitBreakers || [];

  for (const event of gateEvents || []) {
    if (!event || !event.department_id) continue;
    const bucket = eventBuckets.get(event.department_id) || { count: 0, latest: null };
    bucket.count += 1;
    if (!bucket.latest || new Date(event.created_at || 0) > new Date(bucket.latest.created_at || 0)) {
      bucket.latest = event;
    }
    eventBuckets.set(event.department_id, bucket);
  }

  for (const cohort of cohorts || []) {
    if (!cohort || !cohort.department_id) continue;
    const bucket = cohortBuckets.get(cohort.department_id) || { count: 0, active_agents: 0, latest: null };
    bucket.count += 1;
    bucket.active_agents += Number(cohort.activated_agent_count || 0);
    if (!bucket.latest || new Date(cohort.created_at || 0) > new Date(bucket.latest.created_at || 0)) {
      bucket.latest = cohort;
    }
    cohortBuckets.set(cohort.department_id, bucket);
  }

  return (departments || []).map((department) => {
    const gateRow = gateMap.get(department.department_id) || null;
    const eventBucket = eventBuckets.get(department.department_id) || { count: 0, latest: null };
    const cohortBucket = cohortBuckets.get(department.department_id) || { count: 0, active_agents: 0, latest: null };
    const stage = cohortBucket.latest && cohortBucket.latest.stage_id ? stageMap.get(cohortBucket.latest.stage_id) || null : null;

    return {
      ...department,
      gate_id: gateRow ? gateRow.gate_id : null,
      gate_status: gateRow ? gateRow.gate_status : "closed",
      activation_cap: gateRow ? Number(gateRow.activation_cap || 0) : 0,
      currently_active_agents: gateRow ? Number(gateRow.currently_active_agents || 0) : 0,
      approval_required: gateRow ? Boolean(gateRow.approval_required) : true,
      approved_by: gateRow ? gateRow.approved_by : null,
      approved_at: gateRow ? gateRow.approved_at : null,
      blocked_reason: gateRow ? gateRow.blocked_reason : null,
      command_execution_enabled: gateRow ? Boolean(gateRow.command_execution_enabled) : false,
      deploy_execution_enabled: gateRow ? Boolean(gateRow.deploy_execution_enabled) : false,
      rollback_execution_enabled: gateRow ? Boolean(gateRow.rollback_execution_enabled) : false,
      alert_sending_enabled: gateRow ? Boolean(gateRow.alert_sending_enabled) : false,
      gate_event_count: eventBucket.count,
      last_gate_event_at: eventBucket.latest ? eventBucket.latest.created_at : null,
      last_gate_event_type: eventBucket.latest ? eventBucket.latest.event_type : null,
      last_gate_event_summary: eventBucket.latest ? eventBucket.latest.event_summary : null,
      last_gate_event_payload: eventBucket.latest ? eventBucket.latest.event_payload : null,
      cohort_count: cohortBucket.count,
      cohort_active_agents: cohortBucket.active_agents,
      last_cohort_at: cohortBucket.latest ? cohortBucket.latest.created_at : null,
      last_cohort_status: cohortBucket.latest ? cohortBucket.latest.cohort_status : null,
      current_stage_id: stage ? stage.stage_id : null,
      current_stage_name: stage ? stage.stage_name : null,
      current_stage_cap: stage ? Number(stage.stage_cap || 0) : null,
    };
  });
}

module.exports = {
  GLOBAL_LIVE_AGENT_CAP,
  MAX_COHORT_ACTIVATION_SIZE,
  MAX_DEPARTMENT_ACTIVATION_CAP,
  MAX_OPERATION_CHUNK_SIZE,
  backendUnavailable,
  buildArmyRollup,
  circuitBreakerStatus,
  currentCircuitBreakerStatus,
  currentLiveRuntimeAgents,
  currentUnlockedStageCap,
  hasActivateAllFlag,
  hasForbiddenExecutionFlags,
  isConfigured,
  jsonResponse,
  mergeArmyGateRecords,
  parseBody,
  safeSupabaseGet,
  safeSupabaseGetAll,
  stageStatus,
  summarizeError,
  supabaseRpc,
  text,
};
