const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const ALLOWED_COMPANY_LANES = [
  { lane_key: "intake_lane_01", lane_name: "Intake Lane 01", lane_order: 1, lane_description: "Initial controlled intake and queue triage lane." },
  { lane_key: "intake_lane_02", lane_name: "Intake Lane 02", lane_order: 2, lane_description: "Second intake and intake review lane." },
  { lane_key: "validation_lane_01", lane_name: "Validation Lane 01", lane_order: 3, lane_description: "Controlled validation and readiness lane." },
  { lane_key: "validation_lane_02", lane_name: "Validation Lane 02", lane_order: 4, lane_description: "Second validation and acceptance lane." },
  { lane_key: "audit_lane_01", lane_name: "Audit Lane 01", lane_order: 5, lane_description: "Audit visibility and recordkeeping lane." },
  { lane_key: "audit_lane_02", lane_name: "Audit Lane 02", lane_order: 6, lane_description: "Second audit and traceability lane." },
  { lane_key: "approval_lane_01", lane_name: "Approval Lane 01", lane_order: 7, lane_description: "Approval review and decision lane." },
  { lane_key: "approval_lane_02", lane_name: "Approval Lane 02", lane_order: 8, lane_description: "Second approval and decision lane." },
  { lane_key: "dry_run_lane_01", lane_name: "Dry Run Lane 01", lane_order: 9, lane_description: "Dry-run and preview lane." },
  { lane_key: "dry_run_lane_02", lane_name: "Dry Run Lane 02", lane_order: 10, lane_description: "Second dry-run and preview lane." },
  { lane_key: "monitoring_lane_01", lane_name: "Monitoring Lane 01", lane_order: 11, lane_description: "Monitoring and readiness tracking lane." },
  { lane_key: "monitoring_lane_02", lane_name: "Monitoring Lane 02", lane_order: 12, lane_description: "Second monitoring and readiness lane." },
  { lane_key: "safety_lane_01", lane_name: "Safety Lane 01", lane_order: 13, lane_description: "Safety boundary and kill-switch lane." },
  { lane_key: "safety_lane_02", lane_name: "Safety Lane 02", lane_order: 14, lane_description: "Second safety boundary lane." },
  { lane_key: "registry_lane_01", lane_name: "Registry Lane 01", lane_order: 15, lane_description: "Registry and roster verification lane." },
  { lane_key: "registry_lane_02", lane_name: "Registry Lane 02", lane_order: 16, lane_description: "Second registry and roster lane." },
  { lane_key: "review_lane_01", lane_name: "Review Lane 01", lane_order: 17, lane_description: "Human review and QA lane." },
  { lane_key: "review_lane_02", lane_name: "Review Lane 02", lane_order: 18, lane_description: "Second human review lane." },
  { lane_key: "reporting_lane_01", lane_name: "Reporting Lane 01", lane_order: 19, lane_description: "Reporting and summary lane." },
  { lane_key: "reporting_lane_02", lane_name: "Reporting Lane 02", lane_order: 20, lane_description: "Second reporting and summary lane." },
  { lane_key: "compliance_lane_01", lane_name: "Compliance Lane 01", lane_order: 21, lane_description: "Compliance and controls lane." },
  { lane_key: "compliance_lane_02", lane_name: "Compliance Lane 02", lane_order: 22, lane_description: "Second compliance and controls lane." },
  { lane_key: "incident_lane_01", lane_name: "Incident Lane 01", lane_order: 23, lane_description: "Incident triage and escalation lane." },
  { lane_key: "readiness_lane_01", lane_name: "Readiness Lane 01", lane_order: 24, lane_description: "Readiness and signoff lane." },
  { lane_key: "command_center_lane_01", lane_name: "Command Center Lane 01", lane_order: 25, lane_description: "Command center coordination lane." },
];

const ALLOWED_COMPANY_AGENTS = Array.from({ length: 250 }, (_, index) => `mvp56_company_agent_${String(index + 1).padStart(3, "0")}`);

const LANE_AGENT_IDS = Object.fromEntries(
  ALLOWED_COMPANY_LANES.map((lane, laneIndex) => {
    const start = laneIndex * 10;
    return [lane.lane_key, ALLOWED_COMPANY_AGENTS.slice(start, start + 10)];
  }),
);

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp56-250-agent-runtime-company") {
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

function backendUnavailable(message = "Runtime company backend is not configured.") {
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

function companyHealthLabel(activeAgents, totalAgents, activeLaneCount, totalLanes) {
  if (activeAgents === 0) return "inactive";
  if (activeAgents >= totalAgents && activeLaneCount >= totalLanes) return "healthy";
  return "partial";
}

function buildBackendStatus(config = {}, activeCount = 0, activeLaneCount = 0) {
  const totalLanes = ALLOWED_COMPANY_LANES.length;
  const totalAgents = ALLOWED_COMPANY_AGENTS.length;
  const health = companyHealthLabel(activeCount, totalAgents, activeLaneCount, totalLanes);
  return {
    runtime_activation_started: Boolean(config.runtime_activation_started),
    runtime_company_size: Number(config.runtime_company_size || totalAgents),
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
    activation_mode: String(config.activation_mode || "supervised_two_hundred_fifty_agent_company"),
    company_health_rollup: config.company_health_rollup || {
      company_health: health,
      active_agents: activeCount,
      inactive_agents: Math.max(totalAgents - activeCount, 0),
      active_lanes: activeLaneCount,
      inactive_lanes: Math.max(totalLanes - activeLaneCount, 0),
      heartbeat_event_count: Number(config.heartbeat_event_count || 0),
      readiness_note_count: Number(config.readiness_note_count || 0),
      activation_event_count: Number(config.activation_event_count || 0),
      audit_event_count: Number(config.audit_event_count || 0),
      runtime_company_size: totalAgents,
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
  return ALLOWED_COMPANY_LANES.some((lane) => lane.lane_key === key) ? key : "";
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

  for (const lane of ALLOWED_COMPANY_LANES) {
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

  return ALLOWED_COMPANY_LANES.map((lane) => {
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
  ALLOWED_COMPANY_AGENTS,
  ALLOWED_COMPANY_LANES,
  LANE_AGENT_IDS,
  activeCount,
  backendUnavailable,
  buildBackendStatus,
  blockedResponse,
  companyHealthLabel,
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
