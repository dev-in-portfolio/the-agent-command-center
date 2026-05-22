const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const ALLOWED_BATTALION_LANES = [
  { lane_key: "intake_lane", lane_name: "Intake Lane", lane_order: 1 },
  { lane_key: "validation_lane", lane_name: "Validation Lane", lane_order: 2 },
  { lane_key: "audit_lane", lane_name: "Audit Lane", lane_order: 3 },
  { lane_key: "approval_lane", lane_name: "Approval Lane", lane_order: 4 },
  { lane_key: "dry_run_lane", lane_name: "Dry Run Lane", lane_order: 5 },
  { lane_key: "monitoring_lane", lane_name: "Monitoring Lane", lane_order: 6 },
  { lane_key: "safety_lane", lane_name: "Safety Lane", lane_order: 7 },
  { lane_key: "registry_lane", lane_name: "Registry Lane", lane_order: 8 },
  { lane_key: "review_lane", lane_name: "Review Lane", lane_order: 9 },
  { lane_key: "reporting_lane", lane_name: "Reporting Lane", lane_order: 10 },
];

const ALLOWED_BATTALION_AGENTS = Array.from({ length: 100 }, (_, index) => `mvp55_battalion_agent_${String(index + 1).padStart(3, "0")}`);

const LANE_AGENT_IDS = Object.fromEntries(
  ALLOWED_BATTALION_LANES.map((lane, laneIndex) => {
    const start = laneIndex * 10;
    return [
      lane.lane_key,
      ALLOWED_BATTALION_AGENTS.slice(start, start + 10),
    ];
  }),
);

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp55-100-agent-runtime-battalion") {
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

function backendUnavailable(message = "Runtime battalion backend is not configured.") {
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
  if (raw.length > 24000) {
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

function buildBackendStatus(config = {}, activeCount = 0, activeLaneCount = 0) {
  return {
    runtime_activation_started: Boolean(config.runtime_activation_started),
    runtime_battalion_size: Number(config.runtime_battalion_size || 100),
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || activeCount || 0),
    max_activation_batch_size: Number(config.max_activation_batch_size || 100),
    full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
    total_registered_agents: Number(config.total_registered_agents || 47979),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
    kill_switch_visible: Boolean(config.kill_switch_visible),
    active_lanes_count: Number(config.active_lanes_count || activeLaneCount || 0),
    inactive_lanes_count: Number(config.inactive_lanes_count || Math.max(10 - (activeLaneCount || 0), 0)),
    activation_mode: String(config.activation_mode || "supervised_hundred_agent_battalion"),
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
  return ALLOWED_BATTALION_LANES.some((lane) => lane.lane_key === key) ? key : "";
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

  for (const lane of ALLOWED_BATTALION_LANES) {
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

  return ALLOWED_BATTALION_LANES.map((lane) => {
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
  ALLOWED_BATTALION_AGENTS,
  ALLOWED_BATTALION_LANES,
  LANE_AGENT_IDS,
  backendUnavailable,
  buildBackendStatus,
  blockedResponse,
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
  activeCount,
};
