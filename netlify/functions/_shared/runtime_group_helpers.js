
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const LANE_GROUPS = [
  { prefix: "intake", label: "Intake", description: "Initial controlled intake and queue triage lane." },
  { prefix: "validation", label: "Validation", description: "Controlled validation and readiness lane." },
  { prefix: "audit", label: "Audit", description: "Audit visibility and recordkeeping lane." },
  { prefix: "approval", label: "Approval", description: "Approval review and decision lane." },
  { prefix: "dry_run", label: "Dry Run", description: "Dry-run and preview lane." },
  { prefix: "monitoring", label: "Monitoring", description: "Monitoring and readiness tracking lane." },
  { prefix: "safety", label: "Safety", description: "Safety boundary and kill-switch lane." },
  { prefix: "registry", label: "Registry", description: "Registry and roster verification lane." },
  { prefix: "review", label: "Review", description: "Human review and QA lane." },
  { prefix: "reporting", label: "Reporting", description: "Reporting and summary lane." },
];

const ALLOWED_GROUP_LANES = (() => {
  const lanes = [];
  let laneOrder = 1;
  for (const group of LANE_GROUPS) {
    for (let index = 1; index <= 5; index += 1) {
      const suffix = String(index).padStart(2, "0");
      lanes.push({
        lane_key: `${group.prefix}_lane_${suffix}`,
        lane_name: `${group.label} Lane ${suffix}`,
        lane_order: laneOrder++,
        lane_description: group.description,
      });
    }
  }
  return lanes;
})();

const ALLOWED_GROUP_AGENTS = Array.from({ length: 500 }, (_, index) => `mvp57_group_agent_${String(index + 1).padStart(3, "0")}`);

const LANE_AGENT_IDS = Object.fromEntries(
  ALLOWED_GROUP_LANES.map((lane, laneIndex) => {
    const start = laneIndex * 10;
    return [lane.lane_key, ALLOWED_GROUP_AGENTS.slice(start, start + 10)];
  }),
);

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp57-500-agent-runtime-group") {
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

function backendUnavailable(message = "Runtime group backend is not configured.") {
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
  if (raw.length > 32000) {
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

function groupHealthLabel(activeAgents, totalAgents, activeLaneCount, totalLanes) {
  if (activeAgents === 0) return "inactive";
  if (activeAgents >= totalAgents && activeLaneCount >= totalLanes) return "healthy";
  return "partial";
}

function buildBackendStatus(config = {}, activeCount = 0, activeLaneCount = 0) {
  const totalLanes = ALLOWED_GROUP_LANES.length;
  const totalAgents = ALLOWED_GROUP_AGENTS.length;
  const health = groupHealthLabel(activeCount, totalAgents, activeLaneCount, totalLanes);
  return {
    runtime_activation_started: Boolean(config.runtime_activation_started),
    runtime_group_size: Number(config.runtime_group_size || totalAgents),
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || activeCount || 0),
    max_activation_batch_size: Number(config.max_activation_batch_size || totalAgents),
    full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
    total_registered_agents: Number(config.total_registered_agents || 47979),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
    kill_switch_visible: Boolean(config.kill_switch_visible),
    active_lanes_count: Number(config.active_lanes_count || activeLaneCount || 0),
    inactive_lanes_count: Number(config.inactive_lanes_count || Math.max(totalLanes - (activeLaneCount || 0), 0)),
    activation_mode: String(config.activation_mode || "supervised_five_hundred_agent_group"),
    group_health_rollup: config.group_health_rollup || {
      group_health: health,
      active_agents: activeCount,
      inactive_agents: Math.max(totalAgents - activeCount, 0),
      active_lanes: activeLaneCount,
      inactive_lanes: Math.max(totalLanes - activeLaneCount, 0),
      heartbeat_event_count: Number(config.heartbeat_event_count || 0),
      readiness_note_count: Number(config.readiness_note_count || 0),
      activation_event_count: Number(config.activation_event_count || 0),
      audit_event_count: Number(config.audit_event_count || 0),
      runtime_group_size: totalAgents,
      total_registered_agents: 47979,
    },
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
  return ALLOWED_GROUP_LANES.some((lane) => lane.lane_key === key) ? key : "";
}

function laneAgentIds(laneKey) {
  const key = normalizeLaneKey(laneKey);
  return key ? [...(LANE_AGENT_IDS[key] || [])] : [];
}

function activeCount(agents) {
  return (agents || []).filter((agent) => agent.status === "active").length;
}

function laneStats(lanes, agents, heartbeatEvents = [], readinessNotes = []) {
  const laneMap = new Map((lanes || []).map((lane) => [lane.lane_key, lane]));
  const heartbeatByLane = new Map();
  const noteByLane = new Map();

  for (const lane of ALLOWED_GROUP_LANES) {
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

  return ALLOWED_GROUP_LANES.map((lane) => {
    const laneAgents = (agents || []).filter((agent) => agent.lane_key === lane.lane_key);
    const activeAgents = laneAgents.filter((agent) => agent.status === "active").length;
    const inactiveAgents = laneAgents.length - activeAgents;
    const heartbeatCount = heartbeatByLane.get(lane.lane_key) || 0;
    const readinessNoteCount = noteByLane.get(lane.lane_key) || 0;
    const laneRecord = laneMap.get(lane.lane_key) || {};
    const health = activeAgents === 0
      ? "inactive"
      : activeAgents === laneAgents.length
        ? "healthy"
        : "partial";

    return {
      ...lane,
      lane_name: laneRecord.lane_name || lane.lane_name,
      lane_description: laneRecord.lane_description || lane.lane_description,
      active_agents: activeAgents,
      inactive_agents: inactiveAgents,
      lane_health: health,
      heartbeat_count: heartbeatCount,
      readiness_note_count: readinessNoteCount,
    };
  });
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

module.exports = {
  ALLOWED_GROUP_AGENTS,
  ALLOWED_GROUP_LANES,
  LANE_AGENT_IDS,
  activeCount,
  backendUnavailable,
  buildBackendStatus,
  blockedResponse,
  groupHealthLabel,
  isConfigured,
  jsonResponse,
  laneAgentIds,
  laneStats,
  normalizeLaneKey,
  normalizeRequestedAgents,
  parseBody,
  supabaseGet,
  supabaseRpc,
  text,
  toConfigObject,
};
