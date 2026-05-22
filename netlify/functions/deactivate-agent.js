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

function text(value, maxLength) {
  return String(value == null ? "" : value).trim().slice(0, maxLength);
}

function parseBody(event) {
  const raw = event && typeof event.body === "string" ? event.body : "";
  if (raw.length > 12000) {
    throw new Error("PAYLOAD_TOO_LARGE");
  }
  return raw ? JSON.parse(raw) : {};
}

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
  };
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

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable();
  }

  try {
    const payload = parseBody(event);
    if (payload.activate_all === true || payload.batch_size > 1 || Array.isArray(payload.agent_ids)) {
      return jsonResponse(400, {
        ok: false,
        error: "DEACTIVATE_ALL_BLOCKED",
        message: "Mass deactivation is blocked. Only one supervised test agent may be deactivated at a time.",
      });
    }

    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);

    if (agentId !== "mvp53_supervised_test_agent_001") {
      const blocked = await supabaseRpc("runtime_agent_activation_deactivate", {
        p_agent_id: agentId,
        p_actor: actor || "operator",
        p_reason: reason,
      });
      return jsonResponse(409, {
        ok: false,
        blocked: true,
        error: blocked.error || "DEACTIVATION_BLOCKED",
        reason: blocked.reason || "Only the supervised test agent may be managed.",
        event: blocked.event || null,
      });
    }

    const result = await supabaseRpc("runtime_agent_activation_deactivate", {
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_reason: reason,
    });

    return jsonResponse(200, {
      ok: true,
      operation: "deactivate-agent",
      agent: result.agent,
      event: result.event,
      backend_status: result.backend_status,
      blocked: false,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      });
    }

    return jsonResponse(500, {
      ok: false,
      error: "Agent deactivation failed.",
    });
  }
};
