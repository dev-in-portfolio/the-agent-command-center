const {
  backendUnavailable,
  buildBackendStatus,
  divisionStats,
  isConfigured,
  jsonResponse,
  laneStats,
  subdivisionStats,
  supabaseGet,
  supabaseRpc,
  toConfigObject,
} = require("./_shared/runtime_division_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime division backend is not configured.");
  }

  try {
    await supabaseRpc("runtime_division_sync_rollups", {});

    const [configRows, subdivisionRows, laneRows, agentRows, heartbeatRows, noteRows, activationRows, auditRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_division_subdivisions?select=*&order=subdivision_order.asc"),
      supabaseGet("runtime_division_lanes?select=*&order=lane_order.asc"),
      supabaseGet("runtime_division_agents?select=*&order=subdivision_key.asc,lane_key.asc,lane_position.asc"),
      supabaseGet("division_heartbeat_events?select=*&order=created_at.desc&limit=500"),
      supabaseGet("division_readiness_notes?select=*&order=created_at.desc&limit=500"),
      supabaseGet("runtime_division_activation_events?select=*&order=created_at.desc&limit=500"),
      supabaseGet("runtime_division_audit_events?select=*&order=created_at.desc&limit=500"),
    ]);

    const config = toConfigObject(configRows);
    const laneRollups = laneStats(laneRows, agentRows, heartbeatRows, noteRows);
    const subdivisionRollups = subdivisionStats(subdivisionRows, laneRows, agentRows, heartbeatRows, noteRows);
    const divisionRollup = divisionStats(subdivisionRollups, laneRollups, agentRows, heartbeatRows, noteRows, activationRows, auditRows);
    const activeSubdivisionCount = subdivisionRollups.filter((subdivision) => subdivision.active_agents > 0).length;
    const activeLaneCount = laneRollups.filter((lane) => lane.active_agents > 0).length;

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        ...buildBackendStatus(config, divisionRollup),
        runtime_activation_started: false,
        runtime_division_size: Number(config.division_runtime_size || 1000),
        live_runtime_agents_enabled: Number(config.division_live_runtime_agents_enabled || divisionRollup.active_agents || 0),
        max_activation_batch_size: Number(config.division_max_activation_batch_size || 1000),
        max_operation_chunk_size: Number(config.division_max_operation_chunk_size || 100),
        full_47979_activation_blocked: Boolean(config.division_full_47979_activation_blocked),
        total_registered_agents: Number(config.division_total_registered_agents || 47979),
        command_execution_enabled: Boolean(config.division_command_execution_enabled),
        deploy_execution_enabled: Boolean(config.division_deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.division_rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.division_alert_sending_enabled),
        kill_switch_visible: Boolean(config.division_kill_switch_visible),
        active_subdivisions_count: activeSubdivisionCount,
        inactive_subdivisions_count: Math.max(subdivisionRollups.length - activeSubdivisionCount, 0),
        active_lanes_count: activeLaneCount,
        inactive_lanes_count: Math.max(laneRollups.length - activeLaneCount, 0),
      },
      config,
      division_rollup: divisionRollup,
      subdivision_rollups: subdivisionRollups,
      lane_rollups: laneRollups,
      subdivisions: subdivisionRows || [],
      lanes: laneRows || [],
      agents: agentRows || [],
      heartbeat_events: heartbeatRows || [],
      readiness_notes: noteRows || [],
      activation_events: activationRows || [],
      audit_events: auditRows || [],
      counts: {
        registered_agents: Number(config.division_total_registered_agents || 47979),
        division_size: 1000,
        active_agents: divisionRollup.active_agents || 0,
        inactive_agents: divisionRollup.inactive_agents || 0,
        active_subdivisions: activeSubdivisionCount,
        inactive_subdivisions: Math.max(subdivisionRollups.length - activeSubdivisionCount, 0),
        active_lanes: activeLaneCount,
        inactive_lanes: Math.max(laneRollups.length - activeLaneCount, 0),
        heartbeat_event_count: heartbeatRows ? heartbeatRows.length : 0,
        readiness_note_count: noteRows ? noteRows.length : 0,
        activation_event_count: activationRows ? activationRows.length : 0,
        audit_event_count: auditRows ? auditRows.length : 0,
      },
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime division list failed.",
    });
  }
};
