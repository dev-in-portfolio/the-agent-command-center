const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

// Explicit blocked markers used by the runtime division surface:
// UNKNOWN_AGENT_BLOCKED, NON_DIVISION_AGENT_BLOCKED, DIVISION_HEARTBEAT, DIVISION_READINESS_NOTE_CREATED.

const SUBDIVISION_GROUPS = [
  { prefix: "intake", label: "Intake", description: "Controlled intake and triage subdivision." },
  { prefix: "validation", label: "Validation", description: "Controlled validation and readiness subdivision." },
  { prefix: "audit", label: "Audit", description: "Audit visibility and recordkeeping subdivision." },
  { prefix: "approval", label: "Approval", description: "Approval review and decision subdivision." },
  { prefix: "dry_run", label: "Dry Run", description: "Dry-run and preview subdivision." },
  { prefix: "monitoring", label: "Monitoring", description: "Monitoring and readiness tracking subdivision." },
  { prefix: "safety", label: "Safety", description: "Safety boundary and kill-switch subdivision." },
  { prefix: "registry", label: "Registry", description: "Registry and roster verification subdivision." },
  { prefix: "review", label: "Review", description: "Human review and QA subdivision." },
  { prefix: "reporting", label: "Reporting", description: "Reporting and summary subdivision." },
];

const ALLOWED_DIVISION_SUBDIVISIONS = SUBDIVISION_GROUPS.map((group, index) => ({
  subdivision_key: `${group.prefix}_subdivision`,
  subdivision_name: `${group.label} Subdivision`,
  subdivision_order: index + 1,
  subdivision_description: group.description,
}));

const ALLOWED_DIVISION_LANES = (() => {
  const lanes = [];
  let laneOrder = 1;
  for (const subdivision of ALLOWED_DIVISION_SUBDIVISIONS) {
    const prefix = subdivision.subdivision_key.replace("_subdivision", "");
    const label = subdivision.subdivision_name.replace(" Subdivision", "");
    for (let laneIndex = 1; laneIndex <= 10; laneIndex += 1) {
      const suffix = String(laneIndex).padStart(3, "0");
      lanes.push({
        lane_key: `${prefix}_lane_${suffix}`,
        lane_name: `${label} Lane ${suffix}`,
        lane_order: laneOrder++,
        lane_index: laneIndex,
        subdivision_key: subdivision.subdivision_key,
        lane_description: subdivision.subdivision_description,
      });
    }
  }
  return lanes;
})();

const ALLOWED_DIVISION_AGENTS = Array.from(
  { length: 1000 },
  (_, index) => `mvp58_division_agent_${String(index + 1).padStart(4, "0")}`,
);

const SUBDIVISION_LANE_KEYS = Object.fromEntries(
  ALLOWED_DIVISION_SUBDIVISIONS.map((subdivision) => [
    subdivision.subdivision_key,
    ALLOWED_DIVISION_LANES.filter((lane) => lane.subdivision_key === subdivision.subdivision_key).map((lane) => lane.lane_key),
  ]),
);

const LANE_AGENT_IDS = Object.fromEntries(
  ALLOWED_DIVISION_LANES.map((lane, laneIndex) => {
    const start = laneIndex * 10;
    return [lane.lane_key, ALLOWED_DIVISION_AGENTS.slice(start, start + 10)];
  }),
);

const SUBDIVISION_AGENT_IDS = Object.fromEntries(
  ALLOWED_DIVISION_SUBDIVISIONS.map((subdivision) => {
    const laneKeys = SUBDIVISION_LANE_KEYS[subdivision.subdivision_key] || [];
    const agentIds = laneKeys.flatMap((laneKey) => LANE_AGENT_IDS[laneKey] || []);
    return [subdivision.subdivision_key, agentIds];
  }),
);

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp58-1000-agent-runtime-division") {
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

function backendUnavailable(message = "Runtime division backend is not configured.") {
  return jsonResponse(503, {
    ok: false,
    error: message,
  });
}

function text(value, maxLength) {
  return String(value == null ? "" : value).trim().slice(0, maxLength);
}

function parseBody(event) {
  const raw = event && typeof event.body === "string" ? event.body : "";
  if (raw.length > 48000) {
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

async function supabaseGet(path) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method: "GET",
    headers: supabaseHeaders(),
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

async function supabaseRpc(functionName, payload) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${functionName}`, {
    method: "POST",
    headers: supabaseHeaders(),
    body: JSON.stringify(payload),
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

function toConfigObject(configRows) {
  return Object.fromEntries((configRows || []).map((row) => [row.key, row.value]));
}

function activeCount(items) {
  return (items || []).filter((item) => item.status === "active").length;
}

function laneHealthLabel(activeAgents, totalAgents) {
  if (activeAgents === 0) return "inactive";
  if (activeAgents >= totalAgents) return "healthy";
  return "partial";
}

function subdivisionHealthLabel(activeAgents, totalAgents, activeLaneCount, totalLaneCount) {
  if (activeAgents === 0) return "inactive";
  if (activeAgents >= totalAgents && activeLaneCount >= totalLaneCount) return "healthy";
  return "partial";
}

function divisionHealthLabel(activeAgents, totalAgents, activeSubdivisionCount, totalSubdivisionCount, activeLaneCount, totalLaneCount) {
  if (activeAgents === 0) return "inactive";
  if (activeAgents >= totalAgents && activeSubdivisionCount >= totalSubdivisionCount && activeLaneCount >= totalLaneCount) return "healthy";
  return "partial";
}

function laneStats(lanes, agents, heartbeatEvents = [], readinessNotes = []) {
  const laneMap = new Map((lanes || []).map((lane) => [lane.lane_key, lane]));
  const heartbeatByLane = new Map();
  const noteByLane = new Map();

  for (const lane of ALLOWED_DIVISION_LANES) {
    heartbeatByLane.set(lane.lane_key, 0);
    noteByLane.set(lane.lane_key, 0);
  }

  for (const event of heartbeatEvents || []) {
    if (event && event.lane_key) {
      heartbeatByLane.set(event.lane_key, (heartbeatByLane.get(event.lane_key) || 0) + 1);
    }
  }

  for (const note of readinessNotes || []) {
    if (note && note.lane_key) {
      noteByLane.set(note.lane_key, (noteByLane.get(note.lane_key) || 0) + 1);
    }
  }

  return ALLOWED_DIVISION_LANES.map((lane) => {
    const laneAgents = (agents || []).filter((agent) => agent.lane_key === lane.lane_key);
    const activeAgents = laneAgents.filter((agent) => agent.status === "active").length;
    const inactiveAgents = laneAgents.length - activeAgents;
    const heartbeatCount = heartbeatByLane.get(lane.lane_key) || 0;
    const readinessNoteCount = noteByLane.get(lane.lane_key) || 0;
    const laneRecord = laneMap.get(lane.lane_key) || {};

    return {
      ...lane,
      lane_name: laneRecord.lane_name || lane.lane_name,
      lane_description: laneRecord.lane_description || lane.lane_description,
      active_agents: activeAgents,
      inactive_agents: inactiveAgents,
      lane_health: laneHealthLabel(activeAgents, laneAgents.length || 10),
      heartbeat_count: heartbeatCount,
      readiness_note_count: readinessNoteCount,
    };
  });
}

function subdivisionStats(subdivisions, lanes, agents, heartbeatEvents = [], readinessNotes = []) {
  const subdivisionMap = new Map((subdivisions || []).map((subdivision) => [subdivision.subdivision_key, subdivision]));
  const laneRollups = laneStats(lanes, agents, heartbeatEvents, readinessNotes);
  const laneMap = new Map(laneRollups.map((lane) => [lane.lane_key, lane]));

  return ALLOWED_DIVISION_SUBDIVISIONS.map((subdivision) => {
    const subdivisionLanes = ALLOWED_DIVISION_LANES.filter((lane) => lane.subdivision_key === subdivision.subdivision_key);
    const laneRollupRows = subdivisionLanes.map((lane) => laneMap.get(lane.lane_key)).filter(Boolean);
    const activeLaneCount = laneRollupRows.filter((lane) => lane.active_agents > 0).length;
    const activeAgents = (agents || []).filter((agent) => agent.subdivision_key === subdivision.subdivision_key && agent.status === "active").length;
    const totalAgents = (agents || []).filter((agent) => agent.subdivision_key === subdivision.subdivision_key).length;
    const heartbeatCount = laneRollupRows.reduce((sum, lane) => sum + Number(lane.heartbeat_count || 0), 0);
    const readinessNoteCount = laneRollupRows.reduce((sum, lane) => sum + Number(lane.readiness_note_count || 0), 0);
    const subdivisionRecord = subdivisionMap.get(subdivision.subdivision_key) || {};

    return {
      ...subdivision,
      subdivision_name: subdivisionRecord.subdivision_name || subdivision.subdivision_name,
      subdivision_description: subdivisionRecord.subdivision_description || subdivision.subdivision_description,
      active_agents: activeAgents,
      inactive_agents: Math.max(totalAgents - activeAgents, 0),
      active_lanes: activeLaneCount,
      inactive_lanes: Math.max(subdivisionLanes.length - activeLaneCount, 0),
      subdivision_health: subdivisionHealthLabel(activeAgents, totalAgents || 100, activeLaneCount, subdivisionLanes.length || 10),
      heartbeat_count: heartbeatCount,
      readiness_note_count: readinessNoteCount,
    };
  });
}

function divisionStats(subdivisionRollups, laneRollups, agents, heartbeatEvents = [], readinessNotes = [], activationEvents = [], auditEvents = []) {
  const activeAgents = activeCount(agents);
  const activeLaneCount = laneRollups.filter((lane) => lane.active_agents > 0).length;
  const activeSubdivisionCount = subdivisionRollups.filter((subdivision) => subdivision.active_agents > 0).length;

  return {
    division_health: divisionHealthLabel(activeAgents, ALLOWED_DIVISION_AGENTS.length, activeSubdivisionCount, ALLOWED_DIVISION_SUBDIVISIONS.length, activeLaneCount, ALLOWED_DIVISION_LANES.length),
    active_agents: activeAgents,
    inactive_agents: Math.max(ALLOWED_DIVISION_AGENTS.length - activeAgents, 0),
    active_subdivisions: activeSubdivisionCount,
    inactive_subdivisions: Math.max(ALLOWED_DIVISION_SUBDIVISIONS.length - activeSubdivisionCount, 0),
    active_lanes: activeLaneCount,
    inactive_lanes: Math.max(ALLOWED_DIVISION_LANES.length - activeLaneCount, 0),
    heartbeat_event_count: (heartbeatEvents || []).length,
    readiness_note_count: (readinessNotes || []).length,
    activation_event_count: (activationEvents || []).length,
    audit_event_count: (auditEvents || []).length,
    runtime_division_size: ALLOWED_DIVISION_AGENTS.length,
    total_registered_agents: 47979,
  };
}

function normalizeRequestedAgents(agentIds) {
  const unique = [];
  for (const rawId of Array.isArray(agentIds) ? agentIds : []) {
    const agentId = text(rawId, 80);
    if (!agentId || unique.includes(agentId)) {
      continue;
    }
    unique.push(agentId);
  }
  return unique;
}

function normalizeLaneKey(laneKey) {
  const key = text(laneKey, 80);
  return ALLOWED_DIVISION_LANES.some((lane) => lane.lane_key === key) ? key : "";
}

function normalizeSubdivisionKey(subdivisionKey) {
  const key = text(subdivisionKey, 80);
  return ALLOWED_DIVISION_SUBDIVISIONS.some((subdivision) => subdivision.subdivision_key === key) ? key : "";
}

function laneAgentIds(laneKey) {
  const key = normalizeLaneKey(laneKey);
  return key ? [...(LANE_AGENT_IDS[key] || [])] : [];
}

function subdivisionLaneKeys(subdivisionKey) {
  const key = normalizeSubdivisionKey(subdivisionKey);
  return key ? [...(SUBDIVISION_LANE_KEYS[key] || [])] : [];
}

function subdivisionAgentIds(subdivisionKey) {
  const key = normalizeSubdivisionKey(subdivisionKey);
  return key ? [...(SUBDIVISION_AGENT_IDS[key] || [])] : [];
}

function divisionAgentIds() {
  return [...ALLOWED_DIVISION_AGENTS];
}

function blockedResponse(error, reason, extra = {}) {
  return {
    ok: false,
    blocked: true,
    error,
    reason,
    ...extra,
  };
}

function buildBackendStatus(config = {}, rollup = {}) {
  return {
    runtime_activation_started: Boolean(config.division_runtime_activation_started),
    runtime_division_size: Number(config.division_runtime_size || ALLOWED_DIVISION_AGENTS.length),
    live_runtime_agents_enabled: Number(config.division_live_runtime_agents_enabled || rollup.active_agents || 0),
    max_activation_batch_size: Number(config.division_max_activation_batch_size || ALLOWED_DIVISION_AGENTS.length),
    max_operation_chunk_size: Number(config.division_max_operation_chunk_size || 100),
    full_47979_activation_blocked: Boolean(config.division_full_47979_activation_blocked),
    total_registered_agents: Number(config.division_total_registered_agents || 47979),
    command_execution_enabled: Boolean(config.division_command_execution_enabled),
    deploy_execution_enabled: Boolean(config.division_deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.division_rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.division_alert_sending_enabled),
    kill_switch_visible: Boolean(config.division_kill_switch_visible),
    active_subdivisions_count: Number(config.division_active_subdivisions_count || rollup.active_subdivisions || 0),
    inactive_subdivisions_count: Number(config.division_inactive_subdivisions_count || rollup.inactive_subdivisions || 0),
    active_lanes_count: Number(config.division_active_lanes_count || rollup.active_lanes || 0),
    inactive_lanes_count: Number(config.division_inactive_lanes_count || rollup.inactive_lanes || 0),
    activation_mode: String(config.division_activation_mode || "supervised_thousand_agent_division"),
    division_health_rollup: config.division_health_rollup || rollup,
  };
}

module.exports = {
  ALLOWED_DIVISION_AGENTS,
  ALLOWED_DIVISION_LANES,
  ALLOWED_DIVISION_SUBDIVISIONS,
  LANE_AGENT_IDS,
  SUBDIVISION_AGENT_IDS,
  SUBDIVISION_LANE_KEYS,
  activeCount,
  backendUnavailable,
  blockedResponse,
  buildBackendStatus,
  divisionAgentIds,
  divisionStats,
  divisionHealthLabel,
  isConfigured,
  jsonResponse,
  laneAgentIds,
  laneStats,
  normalizeLaneKey,
  normalizeRequestedAgents,
  normalizeSubdivisionKey,
  parseBody,
  subdivisionAgentIds,
  subdivisionLaneKeys,
  subdivisionStats,
  supabaseGet,
  supabaseRpc,
  text,
  toConfigObject,
};
