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

    const result = await gate.supabaseRpc("block_department_runtime_gate", {
      p_department_id: departmentId,
      p_actor: actor || "operator",
      p_reason: reason || "operator block",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, {
        ok: false,
        operation: "block-department-runtime-gate",
        ...result,
      });
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "block-department-runtime-gate",
      blocked: false,
      gate: result.gate || null,
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
      error: "Department gate blocking failed.",
    });
  }
};
