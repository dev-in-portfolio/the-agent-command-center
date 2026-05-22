const {
  ALLOWED_GROUP_LANES,
  backendUnavailable,
  isConfigured,
  jsonResponse,
  normalizeLaneKey,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_group_helpers");

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
    const laneKey = normalizeLaneKey(payload.lane_key);
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);

    if (!laneKey) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_LANE_KEY",
      });
    }

    if (!ALLOWED_GROUP_LANES.some((lane) => lane.lane_key === laneKey)) {
      return jsonResponse(400, {
        ok: false,
        error: "UNKNOWN_LANE_BLOCKED",
      });
    }

    const result = await supabaseRpc("runtime_group_deactivate_lane", {
      p_lane_key: laneKey,
      p_actor: actor || "operator",
      p_reason: reason,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "deactivate-group-lane",
      blocked: Boolean(result.blocked),
      agents: result.agents || [],
      audit_events: result.audit_events || [],
      backend_status: result.backend_status || null,
      group_rollup: result.group_rollup || null,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Group lane deactivation failed.",
    });
  }
};
