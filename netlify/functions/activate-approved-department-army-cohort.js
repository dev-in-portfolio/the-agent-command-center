const base = require("./_shared/runtime_department_helpers");
const army = require("./_shared/runtime_army_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" }, "mvp62-20000-agent-department-gated-runtime-army");
  }

  if (!army.isConfigured()) {
    return army.backendUnavailable("Runtime army backend is not configured.");
  }

  try {
    const payload = army.parseBody(event);
    const departmentId = army.text(payload.department_id, 80);
    const requestedAgentCount = Number(payload.requested_agent_count);
    const actor = army.text(payload.actor, 120);
    const reason = army.text(payload.reason, 4000);

    if (army.hasActivateAllFlag(payload) || army.hasForbiddenExecutionFlags(payload)) {
      return base.jsonResponse(400, { ok: false, error: "RUNTIME_ARMY_EXECUTION_DISABLED" }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    if (!departmentId) {
      return base.jsonResponse(400, { ok: false, error: "department_id is required." }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    if (!Number.isInteger(requestedAgentCount) || requestedAgentCount < 1 || requestedAgentCount > army.MAX_COHORT_ACTIVATION_SIZE) {
      return base.jsonResponse(400, { ok: false, error: `requested_agent_count must be between 1 and ${army.MAX_COHORT_ACTIVATION_SIZE}.` }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    const result = await army.supabaseRpc("runtime_army_activate_department_cohort", {
      p_department_id: departmentId,
      p_requested_agent_count: requestedAgentCount,
      p_actor: actor || "operator",
      p_reason: reason || "",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "activate-approved-department-army-cohort", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "activate-approved-department-army-cohort",
      blocked: false,
      cohort: result.cohort || null,
      stage: result.stage || null,
      event: result.event || null,
      chunk_count: result.chunk_count || 0,
      live_runtime_agents_enabled: result.live_runtime_agents_enabled || 0,
      global_live_agent_cap: result.global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP,
      current_stage_cap: result.current_stage_cap || 5000,
      max_cohort_activation_size: result.max_cohort_activation_size || army.MAX_COHORT_ACTIVATION_SIZE,
      max_operation_chunk_size: result.max_operation_chunk_size || army.MAX_OPERATION_CHUNK_SIZE,
    }, "mvp62-20000-agent-department-gated-runtime-army");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" }, "mvp62-20000-agent-department-gated-runtime-army");
    }
    return base.jsonResponse(500, { ok: false, error: "Approved department army cohort activation failed." }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
