const base = require("./_shared/runtime_department_helpers");
const army = require("./_shared/runtime_army_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" }, "mvp62-20000-agent-department-gated-runtime-army");
  }

  if (!army.isConfigured()) {
    return army.backendUnavailable("Runtime army backend is not configured.");
  }

  try {
    const [
      configResult,
      limitResult,
      departmentResult,
      gateResult,
      gateEventResult,
      stageResult,
      breakerResult,
      cohortResult,
      eventResult,
      rollupResult,
    ] = await Promise.all([
      army.safeSupabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc", []),
      army.safeSupabaseGet("runtime_army_limits?select=key,value,updated_at&order=key.asc", []),
      army.safeSupabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc", []),
      army.safeSupabaseGetAll("department_runtime_gates?select=*&order=department_id.asc", []),
      army.safeSupabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_stages?select=*&order=stage_cap.asc", []),
      army.safeSupabaseGetAll("runtime_army_circuit_breakers?select=*&order=updated_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_cohorts?select=*&order=created_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_events?select=*&order=created_at.desc", []),
      army.safeSupabaseGet("runtime_army_health_rollups?select=*&order=created_at.desc&limit=1", []),
    ]);

    const config = base.toConfigObject(configResult.data || []);
    const limits = base.toConfigObject(limitResult.data || []);
    const latestRollup = Array.isArray(rollupResult.data) && rollupResult.data.length ? rollupResult.data[0] : null;
    const rollup = latestRollup || army.buildArmyRollup(departmentResult.data || [], gateResult.data || [], cohortResult.data || [], stageResult.data || [], breakerResult.data || [], config, eventResult.data || []);
    const partialBackend = [configResult, limitResult, departmentResult, gateResult, gateEventResult, stageResult, breakerResult, cohortResult, eventResult, rollupResult].some((entry) => !entry.ok);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_partial: partialBackend,
      caps: {
        global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || army.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || army.MAX_OPERATION_CHUNK_SIZE),
      },
      backend_status: {
        mvp62_department_gated_runtime_army_ready: true,
        global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || army.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || army.MAX_OPERATION_CHUNK_SIZE),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || army.currentLiveRuntimeAgents(gateResult.data || [], cohortResult.data || [])),
        current_stage_cap: Number(rollup.current_stage_cap || army.currentUnlockedStageCap(stageResult.data || [])),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
        department_gated_activation_required: true,
        staged_activation_required: true,
        circuit_breaker_required: true,
        command_execution_enabled: Boolean(config.command_execution_enabled),
        deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.alert_sending_enabled),
        kill_switch_visible: true,
        backend_partial: partialBackend,
      },
      rollup: {
        ...rollup,
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || army.currentLiveRuntimeAgents(gateResult.data || [], cohortResult.data || [])),
        current_stage_cap: Number(rollup.current_stage_cap || army.currentUnlockedStageCap(stageResult.data || [])),
        gate_event_count: (gateEventResult.data || []).length,
        stage_count: (stageResult.data || []).length,
        breaker_count: (breakerResult.data || []).length,
        cohort_event_count: (eventResult.data || []).length,
        department_gated_activation_required: true,
        staged_activation_required: true,
        circuit_breaker_required: true,
        backend_partial: partialBackend,
      },
      counts: {
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        current_stage_cap: Number(rollup.current_stage_cap || 5000),
        approved_department_gates: rollup.approved_department_gates || 0,
        active_department_gates: rollup.active_department_gates || 0,
        active_cohorts: rollup.active_cohorts || 0,
        heartbeat_count: rollup.heartbeat_count || 0,
        readiness_note_count: rollup.readiness_note_count || 0,
        gate_event_count: (gateEventResult.data || []).length,
        stage_count: (stageResult.data || []).length,
        breaker_count: (breakerResult.data || []).length,
        cohort_event_count: (eventResult.data || []).length,
      },
      limits,
      stages: stageResult.data || [],
      circuit_breakers: breakerResult.data || [],
      recent_events: (eventResult.data || []).slice(0, 100),
      table_health: {
        runtime_kernel_config: configResult,
        runtime_army_limits: limitResult,
        runtime_departments: departmentResult,
        department_runtime_gates: gateResult,
        department_runtime_gate_events: gateEventResult,
        runtime_army_stages: stageResult,
        runtime_army_circuit_breakers: breakerResult,
        runtime_army_cohorts: cohortResult,
        runtime_army_events: eventResult,
        runtime_army_health_rollups: rollupResult,
      },
    });
  } catch (error) {
    console.error("[runtime-army] rollup failed", error && error.message ? error.message : error);
    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime army rollup failed.",
      details: army.summarizeError(error),
    }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
