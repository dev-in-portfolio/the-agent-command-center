const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_company_helpers");

const COMPANY_HEARTBEAT = "COMPANY_HEARTBEAT";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime company backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const scope = text(payload.scope, 32) || "company";
    const laneKey = text(payload.lane_key, 80);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const heartbeatStatus = text(payload.heartbeat_status, 40) || "healthy";
    const heartbeatNote = text(payload.heartbeat_note, 2000);

    const result = await supabaseRpc("runtime_company_record_heartbeat", {
      p_scope: scope,
      p_lane_key: laneKey,
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_heartbeat_status: heartbeatStatus,
      p_heartbeat_note: heartbeatNote,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "company-heartbeat",
      blocked: Boolean(result.blocked),
      event_type: COMPANY_HEARTBEAT,
      heartbeat_events: result.heartbeat_events || [],
      audit_event: result.audit_event || null,
      company_rollup: result.company_rollup || null,
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
      error: "Company heartbeat failed.",
    });
  }
};
