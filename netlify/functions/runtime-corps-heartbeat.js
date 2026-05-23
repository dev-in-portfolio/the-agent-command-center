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
    const actor = corps.text(payload.actor, 120) || "operator";
    const reason = corps.text(payload.reason, 4000);

    const eventRow = await base.supabasePost("runtime_corps_events", {
      department_id: null,
      cohort_id: null,
      actor,
      event_type: "RUNTIME_CORPS_HEARTBEAT",
      event_summary: "Runtime corps heartbeat recorded.",
      event_payload: {
        actor,
        reason,
      },
      source: "mvp61_5000_agent_department_gated_runtime_corps",
    });

    return base.jsonResponse(200, {
      ok: true,
      operation: "runtime-corps-heartbeat",
      event: Array.isArray(eventRow) ? eventRow[0] || null : eventRow || null,
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
      error: "Runtime corps heartbeat failed.",
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  }
};
