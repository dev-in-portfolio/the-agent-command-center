const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_battalion_helpers");

const BATTALION_HEARTBEAT = "BATTALION_HEARTBEAT";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime battalion backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const scope = text(payload.scope, 32) || "battalion";
    const laneKey = text(payload.lane_key, 80);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const heartbeatStatus = text(payload.heartbeat_status, 40) || "healthy";
    const heartbeatNote = text(payload.heartbeat_note, 2000);

    const result = await supabaseRpc("runtime_battalion_record_heartbeat", {
      p_scope: scope,
      p_lane_key: laneKey,
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_heartbeat_status: heartbeatStatus,
      p_heartbeat_note: heartbeatNote,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "battalion-heartbeat",
      blocked: Boolean(result.blocked),
      heartbeat_events: result.heartbeat_events || [],
      audit_event: result.audit_event || null,
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
      error: "Battalion heartbeat failed.",
    });
  }
};
