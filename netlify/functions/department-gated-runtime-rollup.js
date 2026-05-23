const base = require("./_shared/runtime_department_helpers");
const gate = require("./_shared/runtime_department_gate_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return base.jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable("Department-gated runtime backend is not configured.");
  }

  try {
    const [configRows, limitRows, departmentRows, gateRows, gateEventRows, activationRows] = await Promise.all([
      base.supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      base.supabaseGet("department_runtime_global_limits?select=key,value,updated_at&order=key.asc"),
      base.supabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc"),
      base.supabaseGetAll("department_runtime_gates?select=*&order=department_id.asc"),
      base.supabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc"),
      base.supabaseGetAll("department_runtime_activations?select=*&order=created_at.desc"),
    ]);

    const config = base.toConfigObject(configRows);
    const limits = base.toConfigObject(limitRows);
    const rollup = gate.buildDepartmentGateRollup(departmentRows || [], gateRows || [], config);
    const currentLiveRuntimeAgents = Number(rollup.current_live_runtime_agents || 0);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      rollup: {
        ...rollup,
        current_live_runtime_agents: currentLiveRuntimeAgents,
        gate_event_count: (gateEventRows || []).length,
        activation_event_count: (activationRows || []).length,
      },
      counts: {
        total_departments: Number(rollup.total_departments || 1777),
        eligible_departments: Number(rollup.eligible_departments || 0),
        approved_gates: Number(rollup.approved_gates || 0),
        active_gates: Number(rollup.active_gates || 0),
        blocked_gates: Number(rollup.blocked_gates || 0),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        current_live_runtime_agents: currentLiveRuntimeAgents,
        gate_event_count: (gateEventRows || []).length,
        activation_event_count: (activationRows || []).length,
      },
      global_limits: limits,
      backend_status: {
        global_live_agent_cap: Number(config.mvp60_global_live_agent_cap || gate.GLOBAL_LIVE_AGENT_CAP),
        max_department_activation_cap: Number(config.max_department_activation_cap || gate.MAX_DEPARTMENT_ACTIVATION_CAP),
        current_live_runtime_agents: currentLiveRuntimeAgents,
        total_departments: Number(config.total_departments || 1777),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
        department_gated_expansion_enabled: Boolean(config.department_gated_expansion_enabled),
        command_execution_enabled: Boolean(config.command_execution_enabled),
        deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.alert_sending_enabled),
        kill_switch_visible: true,
      },
      events: gateEventRows || [],
      activations: activationRows || [],
    });
  } catch (error) {
    return base.jsonResponse(500, {
      ok: false,
      error: "Department-gated runtime rollup failed.",
    });
  }
};
