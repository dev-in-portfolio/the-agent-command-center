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
    const noteBody = corps.text(payload.note_body, 4000);
    const noteType = corps.text(payload.note_type || "readiness_note", 80) || "readiness_note";
    const actor = corps.text(payload.actor, 120) || "operator";

    if (!departmentId) {
      return base.jsonResponse(400, {
        ok: false,
        error: "department_id is required.",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    if (!noteBody) {
      return base.jsonResponse(400, {
        ok: false,
        error: "note_body is required.",
      }, "mvp61-5000-agent-department-gated-runtime-corps");
    }

    const [noteRow, eventRow] = await Promise.all([
      base.supabasePost("runtime_department_readiness_notes", {
        department_id: departmentId,
        note_type: noteType,
        note_body: noteBody,
        actor,
        source: "mvp61_5000_agent_department_gated_runtime_corps",
      }),
      base.supabasePost("runtime_corps_events", {
        department_id: departmentId,
        cohort_id: null,
        actor,
        event_type: "RUNTIME_CORPS_READINESS_NOTE_CREATED",
        event_summary: `Readiness note created for department ${departmentId}.`,
        event_payload: {
          department_id: departmentId,
          note_type: noteType,
          note_body: noteBody,
        },
        source: "mvp61_5000_agent_department_gated_runtime_corps",
      }),
    ]);

    return base.jsonResponse(200, {
      ok: true,
      operation: "create-runtime-corps-readiness-note",
      note: Array.isArray(noteRow) ? noteRow[0] || null : noteRow || null,
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
      error: "Runtime corps readiness note failed.",
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  }
};
