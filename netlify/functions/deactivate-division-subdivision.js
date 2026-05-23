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
    const subdivisionKey = text(payload.subdivision_key || payload.scope_key, 80);
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);

    if (payload.activate_all === true) {
      return jsonResponse(400, {
        ok: false,
        error: "DIVISION_DEACTIVATION_BLOCKED",
        message: "activate_all is blocked. Use only approved subdivisions.",
      });
    }

    const result = await supabaseRpc("runtime_division_deactivate_agents", {
      p_agent_ids: null,
      p_actor: actor || "operator",
      p_reason: reason,
      p_batch_size: Number(payload.batch_size || 100),
      p_chunk_size: Number(payload.chunk_size || 100),
      p_activate_all: false,
      p_scope: "subdivision",
      p_scope_key: subdivisionKey || null,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "deactivate-division-subdivision",
      blocked: Boolean(result.blocked),
      agents: result.agents || [],
      activation_events: result.activation_events || [],
      audit_events: result.audit_events || [],
      backend_status: result.backend_status || null,
      division_rollup: result.division_rollup || null,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return jsonResponse(500, { ok: false, error: "Runtime division subdivision deactivation failed." });
  }
};
