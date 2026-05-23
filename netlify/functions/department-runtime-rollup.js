const {
  backendUnavailable,
  buildRollupSnapshot,
  isConfigured,
  jsonResponse,
  supabaseGet,
  supabasePost,
  toConfigObject,
} = require("./_shared/runtime_department_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime department backend is not configured.");
  }

  try {
    const [configRows, departmentRows, noteRows, eventRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_departments?select=*&order=family_id.asc,department_id.asc&limit=5000"),
      supabaseGet("runtime_department_readiness_notes?select=*&order=created_at.desc&limit=5000"),
      supabaseGet("runtime_department_events?select=*&order=created_at.desc&limit=5000"),
    ]);

    const config = toConfigObject(configRows);
    const rollup = buildRollupSnapshot(departmentRows || [], config);

    await supabasePost("runtime_department_rollups", [{
      total_departments: rollup.total_departments,
      mapped_departments: rollup.mapped_departments,
      readiness_review_departments: rollup.readiness_review_departments,
      eligible_departments: rollup.eligible_departments,
      blocked_departments: rollup.blocked_departments,
      disabled_departments: rollup.disabled_departments,
      total_registered_agents: rollup.total_registered_agents,
      live_runtime_agents_enabled: rollup.live_runtime_agents_enabled,
      full_47979_activation_blocked: rollup.full_47979_activation_blocked,
      command_execution_enabled: rollup.command_execution_enabled,
      deploy_execution_enabled: rollup.deploy_execution_enabled,
      rollback_execution_enabled: rollup.rollback_execution_enabled,
      alert_sending_enabled: rollup.alert_sending_enabled,
      source: rollup.source,
    }]);

    const configUpdates = [
      { key: "total_departments", value: rollup.total_departments },
      { key: "total_units", value: Number(config.total_units || 5331) },
      { key: "total_families", value: Number(config.total_families || 175) },
      { key: "total_registered_agents", value: rollup.total_registered_agents },
      { key: "full_department_runtime_mapping_ready", value: true },
      { key: "full_47979_activation_blocked", value: true },
      { key: "department_command_execution_enabled", value: false },
      { key: "department_deploy_execution_enabled", value: false },
      { key: "department_rollback_execution_enabled", value: false },
      { key: "department_alert_sending_enabled", value: false },
    ];

    await supabasePost(
      "runtime_kernel_config?on_conflict=key",
      configUpdates.map((entry) => ({
        key: entry.key,
        value: entry.value,
      })),
      {
        Prefer: "resolution=merge-duplicates,return=representation",
      },
    );

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      rollup: {
        ...rollup,
        notes_count: (noteRows || []).length,
        audit_event_count: (eventRows || []).length,
      },
      config_updates: configUpdates,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Department runtime rollup failed.",
    });
  }
};
