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
    const actor = army.text(payload.actor, 120);
    const reason = army.text(payload.reason, 4000);

    if (!departmentId) {
      return base.jsonResponse(400, { ok: false, error: "department_id is required." }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    const result = await army.supabaseRpc("deactivate_approved_department_army_cohorts", {
      p_department_id: departmentId,
      p_actor: actor || "operator",
      p_reason: reason || "",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "deactivate-approved-department-army-cohort", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "deactivate-approved-department-army-cohort",
      blocked: false,
      department_id: departmentId,
      deactivated_cohort_count: result.deactivated_cohort_count || 0,
      event: result.event || null,
      live_runtime_agents_enabled: result.live_runtime_agents_enabled || 0,
      global_live_agent_cap: result.global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP,
    }, "mvp62-20000-agent-department-gated-runtime-army");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" }, "mvp62-20000-agent-department-gated-runtime-army");
    }
    return base.jsonResponse(500, { ok: false, error: "Runtime army department cohort deactivation failed." }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
