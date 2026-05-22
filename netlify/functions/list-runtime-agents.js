const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data) {
  return {
    statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-agent-command-center-mode": "mvp53-runtime-agent-activation-controller",
    },
    body: JSON.stringify(data, null, 2),
  };
}

function backendUnavailable() {
  return jsonResponse(503, {
    ok: false,
    error: "Runtime agent controller backend is not configured.",
  });
}

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
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

function buildConfig(configRows) {
  return Object.fromEntries((configRows || []).map((row) => [row.key, row.value]));
}

function buildBackendStatus(config) {
  return {
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
    total_registered_agents: Number(config.total_registered_agents || 47979),
    mass_activation_blocked: Boolean(config.mass_activation_blocked),
    max_activation_batch_size: Number(config.max_activation_batch_size || 1),
    activation_mode: String(config.activation_mode || "supervised_single_agent_test"),
    kill_switch_visible: Boolean(config.kill_switch_visible),
    supervised_test_agent_id: String(config.supervised_test_agent_id || "mvp53_supervised_test_agent_001"),
  };
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable();
  }

  try {
    const [configRows, agentRows, eventRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_agents?select=*&order=created_at.asc"),
      supabaseGet("agent_activation_events?select=*&order=created_at.desc&limit=50"),
    ]);

    const config = buildConfig(configRows);
    const backendStatus = buildBackendStatus(config);
    const activeAgentCount = (agentRows || []).filter((agent) => agent.status === "active").length;
    const currentAgent = (agentRows || []).find((agent) => agent.agent_id === backendStatus.supervised_test_agent_id) || (agentRows || [])[0] || null;

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        ...backendStatus,
        live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || activeAgentCount || 0),
      },
      config,
      agents: agentRows || [],
      current_agent: currentAgent,
      activation_events: eventRows || [],
      counts: {
        registered_agents: backendStatus.total_registered_agents,
        active_agents: activeAgentCount,
        inactive_agents: Math.max((agentRows || []).length - activeAgentCount, 0),
        activation_event_count: (eventRows || []).length,
      },
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime agent list failed.",
    });
  }
};
