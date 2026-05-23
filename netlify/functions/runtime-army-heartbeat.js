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
    const actor = army.text(payload.actor, 120);
    const reason = army.text(payload.reason, 4000);

    if (army.hasActivateAllFlag(payload) || army.hasForbiddenExecutionFlags(payload)) {
      return base.jsonResponse(400, { ok: false, error: "RUNTIME_ARMY_EXECUTION_DISABLED" }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    const result = await army.supabaseRpc("runtime_army_record_heartbeat", {
      p_actor: actor || "operator",
      p_reason: reason || "",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "runtime-army-heartbeat", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "runtime-army-heartbeat",
      blocked: false,
      event: result.event || null,
      heartbeat_count: result.heartbeat_count || 0,
      readiness_note_count: result.readiness_note_count || 0,
    }, "mvp62-20000-agent-department-gated-runtime-army");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" }, "mvp62-20000-agent-department-gated-runtime-army");
    }
    return base.jsonResponse(500, { ok: false, error: "Runtime army heartbeat failed." }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
