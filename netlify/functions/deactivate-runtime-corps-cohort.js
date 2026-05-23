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
    const cohortId = corps.text(payload.cohort_id, 80);
    const actor = corps.text(payload.actor, 120);
    const reason = corps.text(payload.reason, 4000);

    if (!cohortId) {
      return base.jsonResponse(400, {
        ok: false,
        error: "cohort_id is required.",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    const result = await corps.supabaseRpc("deactivate_runtime_corps_cohort", {
      p_cohort_id: cohortId,
      p_actor: actor || "operator",
      p_reason: reason || "",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, {
        ok: false,
        operation: "deactivate-runtime-corps-cohort",
        ...result,
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "deactivate-runtime-corps-cohort",
      blocked: false,
      cohort: result.cohort || null,
      event: result.event || null,
      live_runtime_agents_enabled: result.live_runtime_agents_enabled || 0,
      global_live_agent_cap: result.global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP,
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
      error: "Runtime corps cohort deactivation failed.",
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  }
};
