const base = require("./_shared/runtime_department_helpers");
const corps = require("./_shared/runtime_corps_helpers");
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are only read server-side through the shared helper.

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return base.jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    }, "mvp61-5000-agent-department-gated-runtime-corps");
  }

  if (!corps.isConfigured()) {
    return corps.backendUnavailable("Runtime corps backend is not configured.");
  }

  try {
    const [
      configResult,
      limitResult,
      departmentResult,
      gateResult,
      cohortResult,
      eventResult,
      rollupResult,
    ] = await Promise.all([
      corps.safeSupabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc", []),
      corps.safeSupabaseGet("runtime_corps_limits?select=key,value,updated_at&order=key.asc", []),
      corps.safeSupabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc", []),
      corps.safeSupabaseGetAll("department_runtime_gates?select=*&order=department_id.asc", []),
      corps.safeSupabaseGetAll("runtime_corps_cohorts?select=*&order=created_at.desc", []),
      corps.safeSupabaseGetAll("runtime_corps_events?select=*&order=created_at.desc", []),
      corps.safeSupabaseGet("runtime_corps_rollups?select=*&order=created_at.desc&limit=1", []),
    ]);

    const config = base.toConfigObject(configResult.data || []);
    const limits = base.toConfigObject(limitResult.data || []);
    const latestRollup = Array.isArray(rollupResult.data) && rollupResult.data.length ? rollupResult.data[0] : null;
    const rollup = latestRollup || corps.buildCorpsRollup(departmentResult.data || [], gateResult.data || [], cohortResult.data || [], config);
    const partialBackend = [configResult, limitResult, departmentResult, gateResult, cohortResult, eventResult, rollupResult].some((entry) => !entry.ok);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_partial: partialBackend,
      caps: {
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
      },
      backend_status: {
        mvp61_department_gated_runtime_corps_ready: true,
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || corps.currentLiveRuntimeAgents(gateResult.data || [], cohortResult.data || [])),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
        department_gated_activation_required: true,
        command_execution_enabled: Boolean(config.command_execution_enabled),
        deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.alert_sending_enabled),
        kill_switch_visible: true,
        backend_partial: partialBackend,
      },
      rollup: {
        ...rollup,
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || corps.currentLiveRuntimeAgents(gateResult.data || [], cohortResult.data || [])),
        gate_event_count: (eventResult.data || []).length,
        department_gated_activation_required: true,
        backend_partial: partialBackend,
      },
      counts: {
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || corps.currentLiveRuntimeAgents(gateResult.data || [], cohortResult.data || [])),
        approved_department_gates: rollup.approved_department_gates || 0,
        active_department_gates: rollup.active_department_gates || 0,
        active_cohorts: rollup.active_cohorts || 0,
        gate_event_count: (eventResult.data || []).length,
      },
      limits,
      recent_events: (eventResult.data || []).slice(0, 100),
      table_health: {
        runtime_kernel_config: configResult,
        runtime_corps_limits: limitResult,
        runtime_departments: departmentResult,
        department_runtime_gates: gateResult,
        runtime_corps_cohorts: cohortResult,
        runtime_corps_events: eventResult,
        runtime_corps_rollups: rollupResult,
      },
    });
  } catch (error) {
    console.error("[runtime-corps] rollup failed", error && error.message ? error.message : error);
    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime corps rollup failed.",
      details: corps.summarizeError(error),
    });
  }
};
