const {
  backendUnavailable,
  buildBackendStatus,
  isConfigured,
  jsonResponse,
  supabaseGet,
  toConfigObject,
  activeCount,
  laneStats,
} = require("./_shared/runtime_company_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime company backend is not configured.");
  }

  try {
    const [configRows, laneRows, agentRows, heartbeatRows, noteRows, activationRows, auditRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_company_lanes?select=*&order=lane_order.asc"),
      supabaseGet("runtime_company_agents?select=*&order=lane_key.asc,lane_position.asc"),
      supabaseGet("company_heartbeat_events?select=*&order=created_at.desc&limit=250"),
      supabaseGet("company_readiness_notes?select=*&order=created_at.desc&limit=250"),
      supabaseGet("runtime_company_activation_events?select=*&order=created_at.desc&limit=250"),
      supabaseGet("runtime_company_audit_events?select=*&order=created_at.desc&limit=250"),
    ]);

    const config = toConfigObject(configRows);
    const laneRollups = laneStats(laneRows, agentRows, heartbeatRows, noteRows);
    const activeAgents = activeCount(agentRows);
    const activeLaneCount = laneRollups.filter((lane) => lane.active_agents > 0).length;
    const inactiveLaneCount = Math.max(laneRollups.length - activeLaneCount, 0);
    const companyRollup = config.company_health_rollup || {
      company_health: activeAgents === 0 ? "inactive" : activeAgents >= 250 && activeLaneCount >= 25 ? "healthy" : "partial",
      active_agents: activeAgents,
      inactive_agents: Math.max(250 - activeAgents, 0),
      active_lanes: activeLaneCount,
      inactive_lanes: inactiveLaneCount,
      heartbeat_event_count: (heartbeatRows || []).length,
      readiness_note_count: (noteRows || []).length,
      activation_event_count: (activationRows || []).length,
      audit_event_count: (auditRows || []).length,
      runtime_company_size: 250,
      total_registered_agents: 47979,
    };

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        ...buildBackendStatus(config, activeAgents, activeLaneCount),
        runtime_activation_started: false,
        runtime_company_size: Number(config.runtime_company_size || 250),
        live_runtime_agents_enabled: activeAgents,
        max_activation_batch_size: Number(config.max_activation_batch_size || 250),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        command_execution_enabled: Boolean(config.command_execution_enabled),
        deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.alert_sending_enabled),
        kill_switch_visible: Boolean(config.kill_switch_visible),
        active_lanes_count: activeLaneCount,
        inactive_lanes_count: inactiveLaneCount,
        company_health_rollup: companyRollup,
      },
      config,
      company_rollup: companyRollup,
      lane_rollups: laneRollups,
      lanes: laneRows || [],
      agents: agentRows || [],
      heartbeat_events: heartbeatRows || [],
      readiness_notes: noteRows || [],
      activation_events: activationRows || [],
      audit_events: auditRows || [],
      counts: {
        registered_agents: Number(config.total_registered_agents || 47979),
        company_size: 250,
        active_agents: activeAgents,
        inactive_agents: Math.max((agentRows || []).length - activeAgents, 0),
        active_lanes: activeLaneCount,
        inactive_lanes: inactiveLaneCount,
        heartbeat_event_count: (heartbeatRows || []).length,
        readiness_note_count: (noteRows || []).length,
        activation_event_count: (activationRows || []).length,
        audit_event_count: (auditRows || []).length,
      },
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime company list failed.",
    });
  }
};
