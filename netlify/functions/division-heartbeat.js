const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_division_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, { ok: false, error: "Method Not Allowed" });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime division backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const result = await supabaseRpc("runtime_division_record_heartbeat", {
      p_scope: text(payload.scope || "division", 40) || "division",
      p_subdivision_key: text(payload.subdivision_key || payload.scope_key, 80) || null,
      p_lane_key: text(payload.lane_key, 80) || null,
      p_agent_id: text(payload.agent_id, 80) || null,
      p_actor: text(payload.actor_name, 120) || null,
      p_heartbeat_status: text(payload.heartbeat_status || "healthy", 40) || "healthy",
      p_heartbeat_note: text(payload.heartbeat_note, 2000) || null,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "division-heartbeat",
      blocked: Boolean(result.blocked),
      heartbeat_events: result.heartbeat_events || [],
      audit_event: result.audit_event || null,
      division_rollup: result.division_rollup || null,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return jsonResponse(500, { ok: false, error: "Runtime division heartbeat failed." });
  }
};
