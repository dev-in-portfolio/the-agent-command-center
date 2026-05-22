const {
  ALLOWED_BATTALION_AGENTS,
  backendUnavailable,
  isConfigured,
  jsonResponse,
  normalizeRequestedAgents,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_battalion_helpers");

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
    const agentIds = normalizeRequestedAgents(payload.agent_ids || payload.agent_id ? [].concat(payload.agent_ids || payload.agent_id) : []);
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);
    const batchSize = Number(payload.batch_size || agentIds.length || 0);

    if (payload.command_execution_enabled === true || payload.deploy_execution_enabled === true || payload.rollback_execution_enabled === true || payload.alert_sending_enabled === true) {
      return jsonResponse(400, {
        ok: false,
        error: "BATTALION_EXECUTION_DISABLED",
      });
    }

    if (payload.activate_all === true) {
      return jsonResponse(400, {
        ok: false,
        error: "BATTALION_ACTIVATION_BLOCKED",
        message: "Full 47,979 activation is blocked. Use only the approved 100-agent battalion.",
      });
    }

    if (batchSize > 100) {
      return jsonResponse(400, {
        ok: false,
        error: "BATTALION_ACTIVATION_BLOCKED",
        message: "batch_size exceeds 100. Activation beyond 100 is blocked.",
      });
    }

    if (!agentIds.length) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "agent_id or agent_ids is required.",
      });
    }

    const requestedIds = agentIds.filter((id) => ALLOWED_BATTALION_AGENTS.includes(id));
    if (requestedIds.length !== agentIds.length) {
      const blocked = await supabaseRpc("runtime_battalion_activate_agents", {
        p_agent_ids: agentIds,
        p_actor: actor || "operator",
        p_reason: reason,
        p_batch_size: batchSize,
        p_activate_all: Boolean(payload.activate_all),
      });
      return jsonResponse(409, {
        ok: false,
        blocked: true,
        error: blocked.error || "UNKNOWN_AGENT_BLOCKED",
        reason: blocked.reason || "Only the approved 100-agent battalion may be activated.",
        unknown_agent_ids: blocked.unknown_agent_ids || null,
        audit_event: blocked.audit_event || null,
      });
    }

    const result = await supabaseRpc("runtime_battalion_activate_agents", {
      p_agent_ids: requestedIds,
      p_actor: actor || "operator",
      p_reason: reason,
      p_batch_size: batchSize,
      p_activate_all: Boolean(payload.activate_all),
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "activate-runtime-battalion",
      blocked: Boolean(result.blocked),
      agents: result.agents || [],
      audit_events: result.audit_events || [],
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
      error: "Runtime battalion activation failed.",
    });
  }
};
