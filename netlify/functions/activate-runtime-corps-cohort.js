const base = require("./_shared/runtime_department_helpers");
const corps = require("./_shared/runtime_corps_helpers");
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are only read server-side through the shared helper.

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" }, "mvp61-5000-agent-department-gated-runtime-corps");
  }

  if (!corps.isConfigured()) {
    return corps.backendUnavailable("Runtime corps backend is not configured.");
  }

  try {
    const payload = corps.parseBody(event);
    const departmentId = corps.text(payload.department_id, 80);
    const requestedAgentCount = Number(payload.requested_agent_count);
    const actor = corps.text(payload.actor, 120);
    const reason = corps.text(payload.reason, 4000);

    if (corps.hasActivateAllFlag(payload) || corps.hasForbiddenExecutionFlags(payload)) {
      return base.jsonResponse(400, {
        ok: false,
        error: "DEPARTMENT_GATED_EXECUTION_DISABLED",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    if (!departmentId) {
      return base.jsonResponse(400, {
        ok: false,
        error: "department_id is required.",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    if (!Number.isInteger(requestedAgentCount) || requestedAgentCount < 1 || requestedAgentCount > corps.MAX_COHORT_ACTIVATION_SIZE) {
      return base.jsonResponse(400, {
        ok: false,
        error: "requested_agent_count must be between 1 and 500.",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    const result = await corps.supabaseRpc("activate_runtime_corps_cohort", {
      p_department_id: departmentId,
      p_requested_agent_count: requestedAgentCount,
      p_actor: actor || "operator",
      p_reason: reason || "",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, {
        ok: false,
        operation: "activate-runtime-corps-cohort",
        ...result,
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "activate-runtime-corps-cohort",
      blocked: false,
      cohort: result.cohort || null,
      gate: result.gate || null,
      event: result.event || null,
      live_runtime_agents_enabled: result.live_runtime_agents_enabled || 0,
      global_live_agent_cap: result.global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP,
      max_cohort_activation_size: result.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE,
      max_operation_chunk_size: result.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE,
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime corps cohort activation failed.",
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  }
};
