const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const ALLOWED_SQUAD_AGENTS = [
  "mvp54_runtime_squad_agent_001",
  "mvp54_runtime_squad_agent_002",
  "mvp54_runtime_squad_agent_003",
  "mvp54_runtime_squad_agent_004",
  "mvp54_runtime_squad_agent_005",
  "mvp54_runtime_squad_agent_006",
  "mvp54_runtime_squad_agent_007",
  "mvp54_runtime_squad_agent_008",
  "mvp54_runtime_squad_agent_009",
  "mvp54_runtime_squad_agent_010",
];

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp54-ten-agent-runtime-squad") {
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

function backendUnavailable(message = "Runtime squad backend is not configured.") {
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
  if (raw.length > 16000) {
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

function buildBackendStatus(config = {}, activeCount = 0) {
  return {
    runtime_activation_started: Boolean(config.runtime_activation_started),
    runtime_squad_size: Number(config.runtime_squad_size || 10),
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || activeCount || 0),
    max_activation_batch_size: Number(config.max_activation_batch_size || 10),
    mass_activation_blocked: Boolean(config.mass_activation_blocked),
    full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
    total_registered_agents: Number(config.total_registered_agents || 47979),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
    kill_switch_visible: Boolean(config.kill_switch_visible),
    activation_mode: String(config.activation_mode || "supervised_ten_agent_squad"),
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

function blockedResponse(error, reason, extra = {}) {
  return {
    ok: false,
    blocked: true,
    error,
    reason,
    ...extra,
  };
}

function activeCount(agents) {
  return (agents || []).filter((agent) => agent.status === "active").length;
}

module.exports = {
  ALLOWED_SQUAD_AGENTS,
  backendUnavailable,
  buildBackendStatus,
  isConfigured,
  jsonResponse,
  normalizeRequestedAgents,
  parseBody,
  supabaseGet,
  supabaseRpc,
  text,
  toConfigObject,
  blockedResponse,
  activeCount,
};
