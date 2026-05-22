const {
  backendUnavailable,
  buildBackendStatus,
  isConfigured,
  jsonResponse,
  supabaseGet,
  toConfigObject,
  activeCount,
} = require("./_shared/runtime_squad_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime squad backend is not configured.");
  }

  try {
    const [configRows, agentRows, heartbeatRows, noteRows, auditRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_squad_agents?select=*&order=squad_position.asc"),
      supabaseGet("agent_heartbeat_events?select=*&order=created_at.desc&limit=50"),
      supabaseGet("agent_readiness_notes?select=*&order=created_at.desc&limit=50"),
      supabaseGet("runtime_squad_audit_events?select=*&order=created_at.desc&limit=50"),
    ]);

    const config = toConfigObject(configRows);
    const heartbeatsByAgent = new Map();
    for (const heartbeat of heartbeatRows || []) {
      if (!heartbeatsByAgent.has(heartbeat.agent_id)) {
        heartbeatsByAgent.set(heartbeat.agent_id, heartbeat);
      }
    }

    const notesByAgent = new Map();
    for (const note of noteRows || []) {
      if (!notesByAgent.has(note.agent_id)) {
        notesByAgent.set(note.agent_id, note);
      }
    }

    const agents = (agentRows || []).map((agent) => {
      return {
        ...agent,
        latest_heartbeat: heartbeatsByAgent.get(agent.agent_id) || null,
        latest_readiness_note: notesByAgent.get(agent.agent_id) || null,
      };
    });

    const liveCount = activeCount(agents);

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        ...buildBackendStatus(config, liveCount),
        live_runtime_agents_enabled: liveCount,
        approved_squad_size: 10,
      },
      config,
      agents,
      heartbeat_events: heartbeatRows || [],
      readiness_notes: noteRows || [],
      audit_events: auditRows || [],
      counts: {
        registered_agents: Number(config.total_registered_agents || 47979),
        squad_size: 10,
        active_agents: liveCount,
        inactive_agents: Math.max((agents || []).length - liveCount, 0),
        heartbeat_event_count: (heartbeatRows || []).length,
        readiness_note_count: (noteRows || []).length,
        audit_event_count: (auditRows || []).length,
      },
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime squad list failed.",
    });
  }
};
