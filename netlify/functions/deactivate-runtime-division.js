const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  normalizeRequestedAgents,
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
    const agentIds = normalizeRequestedAgents(payload.agent_ids || (payload.agent_id ? [].concat(payload.agent_id) : []));
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);
    const batchSize = Number(payload.batch_size || (agentIds.length ? agentIds.length : 0));
    const chunkSize = Number(payload.chunk_size || 100);

    if (payload.command_execution_enabled === true || payload.deploy_execution_enabled === true || payload.rollback_execution_enabled === true || payload.alert_sending_enabled === true) {
      return jsonResponse(400, { ok: false, error: "DIVISION_EXECUTION_DISABLED" });
    }

    if (payload.activate_all === true) {
      return jsonResponse(400, {
        ok: false,
        error: "DIVISION_DEACTIVATION_BLOCKED",
        message: "activate_all is blocked. Use the approved 1,000-agent division only.",
      });
    }

    if (batchSize > 1000) {
      return jsonResponse(400, {
        ok: false,
        error: "DIVISION_DEACTIVATION_BLOCKED",
        message: "batch_size exceeds 1000. Activation beyond 1,000 is blocked.",
      });
    }

    if (chunkSize > 100) {
      return jsonResponse(400, {
        ok: false,
        error: "DIVISION_DEACTIVATION_BLOCKED",
        message: "chunk_size exceeds 100. Full division deactivation must process in 10 chunks of 100.",
      });
    }

    const result = await supabaseRpc("runtime_division_deactivate_agents", {
      p_agent_ids: agentIds.length ? agentIds : null,
      p_actor: actor || "operator",
      p_reason: reason,
      p_batch_size: batchSize,
      p_chunk_size: chunkSize,
      p_activate_all: false,
      p_scope: payload.scope || "division",
      p_scope_key: text(payload.scope_key || payload.subdivision_key || payload.lane_key, 80) || null,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "deactivate-runtime-division",
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

    return jsonResponse(500, { ok: false, error: "Runtime division deactivation failed." });
  }
};
