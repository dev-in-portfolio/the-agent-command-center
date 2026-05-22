const {
  ALLOWED_GROUP_AGENTS,
  backendUnavailable,
  isConfigured,
  jsonResponse,
  normalizeRequestedAgents,
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
    const agentIds = normalizeRequestedAgents(payload.agent_ids || payload.agent_id ? [].concat(payload.agent_ids || payload.agent_id) : []);
    const actor = text(payload.actor_name, 120);
    const reason = text(payload.reason, 2000);
    const batchSize = Number(payload.batch_size || (agentIds.length ? agentIds.length : ALLOWED_GROUP_AGENTS.length));

    if (payload.command_execution_enabled === true || payload.deploy_execution_enabled === true || payload.rollback_execution_enabled === true || payload.alert_sending_enabled === true) {
      return jsonResponse(400, {
        ok: false,
        error: "GROUP_EXECUTION_DISABLED",
      });
    }

    if (payload.activate_all === true) {
      return jsonResponse(400, {
        ok: false,
        error: "GROUP_DEACTIVATION_BLOCKED",
        message: "Full 47,979 deactivation is blocked. Use only the approved 500-agent group.",
      });
    }

    if (batchSize > 500) {
      return jsonResponse(400, {
        ok: false,
        error: "GROUP_DEACTIVATION_BLOCKED",
        message: "batch_size exceeds 500. Deactivation beyond 500 is blocked.",
      });
    }

    if (agentIds.some((id) => !ALLOWED_GROUP_AGENTS.includes(id))) {
      return jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "NON_GROUP_AGENT_BLOCKED",
        reason: "Only the approved 500-agent group may be managed.",
      });
    }

        const requestedIds = agentIds.length ? agentIds.filter((id) => ALLOWED_GROUP_AGENTS.includes(id)) : [...ALLOWED_GROUP_AGENTS];
    if (requestedIds.length !== agentIds.length) {
      const blocked = await supabaseRpc("runtime_group_deactivate_agents", {
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
        reason: blocked.reason || "Only the approved 500-agent group may be managed.",
        unknown_agent_ids: blocked.unknown_agent_ids || null,
        audit_event: blocked.audit_event || null,
      });
    }

    const result = await supabaseRpc("runtime_group_deactivate_agents", {
      p_agent_ids: requestedIds,
      p_actor: actor || "operator",
      p_reason: reason,
      p_batch_size: batchSize,
      p_activate_all: Boolean(payload.activate_all),
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "deactivate-runtime-group",
      blocked: Boolean(result.blocked),
      agents: result.agents || [],
      audit_events: result.audit_events || [],
      backend_status: result.backend_status || null,
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
      error: "Runtime group deactivation failed.",
    });
  }
};
