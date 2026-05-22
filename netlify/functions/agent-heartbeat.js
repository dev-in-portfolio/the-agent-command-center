const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_squad_helpers");

const HEARTBEAT_EVENT_TYPE = "AGENT_HEARTBEAT";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime squad backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const heartbeatStatus = text(payload.heartbeat_status, 40) || "healthy";
    const heartbeatNote = text(payload.heartbeat_note, 2000);

    if (!agentId) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "agent_id is required.",
      });
    }

    const result = await supabaseRpc("runtime_squad_record_heartbeat", {
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_heartbeat_status: heartbeatStatus,
      p_heartbeat_note: heartbeatNote,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "agent-heartbeat",
      blocked: Boolean(result.blocked),
      agent: result.agent || null,
      heartbeat: result.heartbeat || null,
      audit_event: result.audit_event || null,
      backend_status: result.backend_status || null,
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
      error: "Agent heartbeat failed.",
    });
  }
};
