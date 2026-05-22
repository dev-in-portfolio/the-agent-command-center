const {
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseRpc,
  text,
} = require("./_shared/runtime_company_helpers");

const COMPANY_READINESS_NOTE_CREATED = "COMPANY_READINESS_NOTE_CREATED";

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime company backend is not configured.");
  }

  try {
    const payload = parseBody(event);
    const scope = text(payload.scope, 32) || "company";
    const laneKey = text(payload.lane_key, 80);
    const agentId = text(payload.agent_id, 80);
    const actor = text(payload.actor_name, 120);
    const noteTitle = text(payload.note_title, 180);
    const noteBody = text(payload.note_body, 8000);
    const readinessLevel = text(payload.readiness_level, 32) || "green";

    if (!noteTitle || !noteBody) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "note_title and note_body are required.",
      });
    }

    const result = await supabaseRpc("runtime_company_create_readiness_note", {
      p_scope: scope,
      p_lane_key: laneKey,
      p_agent_id: agentId,
      p_actor: actor || "operator",
      p_note_title: noteTitle,
      p_note_body: noteBody,
      p_readiness_level: readinessLevel,
    });

    return jsonResponse(result.blocked ? 409 : 200, {
      ok: Boolean(result.ok),
      operation: "create-company-readiness-note",
      blocked: Boolean(result.blocked),
      event_type: COMPANY_READINESS_NOTE_CREATED,
      readiness_notes: result.readiness_notes || [],
      audit_event: result.audit_event || null,
      company_rollup: result.company_rollup || null,
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
      error: "Company readiness note creation failed.",
    });
  }
};
