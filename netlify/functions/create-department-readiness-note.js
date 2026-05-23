const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseGet,
  supabasePost,
  text,
} = require("./_shared/runtime_department_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime department backend is not configured.");
  }

  try {
    const body = parseBody(event);
    const departmentId = text(body.department_id, 80);
    const noteBody = text(body.note_body, 5000);
    const noteType = text(body.note_type, 80) || "readiness_note";
    const actor = text(body.actor, 120);

    if (!departmentId) {
      return jsonResponse(400, { ok: false, error: "department_id is required." });
    }
    if (!noteBody) {
      return jsonResponse(400, { ok: false, error: "note_body is required." });
    }

    const departmentRows = await supabaseGet(`runtime_departments?select=*&department_id=eq.${encodeURIComponent(departmentId)}&limit=1`);
    const department = departmentRows && departmentRows[0];
    if (!department) {
      return jsonResponse(404, {
        ok: false,
        error: "Department not found.",
      });
    }

    const noteRow = {
      department_id: departmentId,
      note_type: noteType || "readiness_note",
      note_body: noteBody,
      actor: actor || null,
      source: "mvp59_department_runtime_mapping",
    };

    const noteRows = await supabasePost("runtime_department_readiness_notes", [noteRow]);
    const eventRow = {
      department_id: departmentId,
      actor: actor || null,
      event_type: "DEPARTMENT_READINESS_NOTE_CREATED",
      event_summary: `Readiness note created for department ${departmentId}.`,
      event_payload: {
        department_id: departmentId,
        note_type: noteType || "readiness_note",
        note_body: noteBody,
      },
      source: "mvp59_department_runtime_mapping",
    };

    await supabasePost("runtime_department_events", [eventRow]);

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      note: noteRows && noteRows[0] ? noteRows[0] : noteRow,
      event: eventRow,
      command_execution_enabled: false,
      deploy_execution_enabled: false,
      rollback_execution_enabled: false,
      alert_sending_enabled: false,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Department readiness note creation failed.",
    });
  }
};
