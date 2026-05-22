const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_squad_helpers");

const READINESS_NOTE_EVENT_TYPE = "READINESS_NOTE_CREATED";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime squad backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const noteTitle = text(payload.note_title, 180);
    const noteBody = text(payload.note_body, 8000);
    const readinessLevel = text(payload.readiness_level, 32) || "green";

    if (!agentId || !noteTitle || !noteBody) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "agent_id, note_title, and note_body are required.",
      });
    }

    const result = await supabaseRpc("runtime_squad_create_readiness_note", {
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_note_title: noteTitle,
      p_note_body: noteBody,
      p_readiness_level: readinessLevel,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "create-readiness-note",
      blocked: Boolean(result.blocked),
      agent: result.agent || null,
      readiness_note: result.readiness_note || null,
      audit_event: result.audit_event || null,
      backend_status: result.backend_status || null,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      });
    }

    return jsonResponse(500, {
      ok: false,
      error: "Readiness note creation failed.",
    });
  }
};
