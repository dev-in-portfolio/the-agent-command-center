const base = require("./_shared/continual_harness_operator_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable();
  }

  try {
    const payload = base.parseBody(event);
    const reason = base.text(payload.reason, 4000) || "Operator stop requested.";
    const actor = base.text(payload.actor, 120) || "operator";

    const sessionRows = await base.supabaseGet("continual_harness_sessions?select=*&order=updated_at.desc,started_at.desc&limit=1");
    const session = Array.isArray(sessionRows) && sessionRows.length ? sessionRows[0] : null;

    if (session) {
      await base.supabasePatch(`continual_harness_sessions?session_id=eq.${encodeURIComponent(session.session_id)}`, [{
        status: "paused",
        stopped_at: new Date().toISOString(),
        stopped_reason: reason,
        current_scope: "harness:update_harness_session",
        current_operation: "request_harness_stop",
      }]);
    }

    await base.supabasePost("continual_harness_operator_events", [{
      run_plan_id: null,
      event_type: "harness_stopped",
      event_summary: `Harness paused by ${actor}`,
      event_payload: {
        actor,
        reason,
        session_id: session ? session.session_id : null,
      },
    }]);

    return base.jsonResponse(200, {
      ok: true,
      session_status: "paused",
      reason,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Continual Harness stop failed.",
    });
  }
};
