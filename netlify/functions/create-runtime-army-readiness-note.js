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
    const noteBody = army.text(payload.note_body, 4000);
    const actor = army.text(payload.actor, 120);

    if (!departmentId) {
      return base.jsonResponse(400, { ok: false, error: "department_id is required." }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    if (!noteBody) {
      return base.jsonResponse(400, { ok: false, error: "note_body is required." }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    const result = await army.supabaseRpc("runtime_army_create_readiness_note", {
      p_department_id: departmentId,
      p_note_body: noteBody,
      p_actor: actor || "operator",
    });

    if (!result.ok) {
      return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "create-runtime-army-readiness-note", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    return base.jsonResponse(200, {
      ok: true,
      operation: "create-runtime-army-readiness-note",
      blocked: false,
      department_id: departmentId,
      event: result.event || null,
      heartbeat_count: result.heartbeat_count || 0,
      readiness_note_count: result.readiness_note_count || 0,
    }, "mvp62-20000-agent-department-gated-runtime-army");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" }, "mvp62-20000-agent-department-gated-runtime-army");
    }
    return base.jsonResponse(500, { ok: false, error: "Runtime army readiness note failed." }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
