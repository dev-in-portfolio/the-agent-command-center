const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_group_helpers");

const GROUP_HEARTBEAT = "GROUP_HEARTBEAT";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime group backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const scope = text(payload.scope, 32) || "group";
    const laneKey = text(payload.lane_key, 80);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const heartbeatStatus = text(payload.heartbeat_status, 40) || "healthy";
    const heartbeatNote = text(payload.heartbeat_note, 2000);

    const result = await supabaseRpc("runtime_group_record_heartbeat", {
      p_scope: scope,
      p_lane_key: laneKey,
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_heartbeat_status: heartbeatStatus,
      p_heartbeat_note: heartbeatNote,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "group-heartbeat",
      blocked: Boolean(result.blocked),
      event_type: GROUP_HEARTBEAT,
      heartbeat_events: result.heartbeat_events || [],
      audit_event: result.audit_event || null,
      group_rollup: result.group_rollup || null,
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
      error: "Group heartbeat failed.",
    });
  }
};
