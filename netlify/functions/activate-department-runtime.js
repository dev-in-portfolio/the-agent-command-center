const base = require("./_shared/runtime_department_helpers");
const gate = require("./_shared/runtime_department_gate_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable("Department-gated runtime backend is not configured.");
  }

  try {
    const payload = base.parseBody(event);
    const departmentId = base.text(payload.department_id, 80);
    const requestedAgentCount = Number(payload.requested_agent_count);
    const actor = base.text(payload.actor, 120);
    const reason = base.text(payload.reason, 4000);

    if (gate.hasActivateAllFlag(payload) || gate.hasForbiddenExecutionFlags(payload)) {
      return base.jsonResponse(400, {
        ok: false,
        error: "DEPARTMENT_GATED_EXECUTION_DISABLED",
      });
    }

    if (!departmentId) {
      return base.jsonResponse(400, {
        ok: false,
        error: "department_id is required.",
      });
    }

    if (!Number.isInteger(requestedAgentCount) || requestedAgentCount < 1 || requestedAgentCount > gate.MAX_DEPARTMENT_ACTIVATION_CAP) {
      return base.jsonResponse(400, {
        ok: false,
        error: "requested_agent_count must be between 1 and 250.",
      });
    }

    if (!reason) {
      return base.jsonResponse(400, {
        ok: false,
        error: "reason is required.",
      });
    }

    const result = await gate.supabaseRpc("activate_department_runtime", {
      p_department_id: departmentId,
      p_requested_agent_count: requestedAgentCount,
      p_actor: actor || "operator",
      p_reason: reason,
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, {
        ok: false,
        operation: "activate-department-runtime",
        ...result,
      });
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "activate-department-runtime",
      blocked: false,
      gate: result.gate || null,
      activation: result.activation || null,
      event: result.event || null,
      live_runtime_agents_enabled: result.live_runtime_agents_enabled || 0,
      global_live_agent_cap: result.global_live_agent_cap || 2500,
      max_department_activation_cap: result.max_department_activation_cap || 250,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      });
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Department runtime activation failed.",
    });
  }
};
