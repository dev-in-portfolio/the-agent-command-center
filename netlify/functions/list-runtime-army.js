const base = require("./_shared/runtime_department_helpers");
const army = require("./_shared/runtime_army_helpers");
const corps = require("./_shared/runtime_corps_helpers");

function matchesFilter(value, filter) {
  if (!filter) return true;
  return String(value == null ? "" : value).toLowerCase().includes(filter);
}

function buildSearchText(row) {
  return [
    row.department_id,
    row.department_name,
    row.family_id,
    row.family_name,
    row.unit_id,
    row.unit_name,
    row.mapped_runtime_lane_id,
    row.mapped_runtime_lane_name,
    row.mapped_runtime_subdivision_id,
    row.mapped_runtime_subdivision_name,
    row.stage_id,
    row.stage_name,
    row.circuit_breaker_status,
    row.gate_status,
    row.cohort_status,
    row.blocked_reason,
    row.last_gate_event_summary,
    row.last_gate_event_type,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

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
      assignmentResult,
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
      army.safeSupabaseGet("runtime_department_lane_assignments?select=*&order=assigned_at.desc", []),
      army.safeSupabaseGetAll("department_runtime_gates?select=*&order=department_id.asc", []),
      army.safeSupabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_stages?select=*&order=stage_cap.asc", []),
      army.safeSupabaseGetAll("runtime_army_circuit_breakers?select=*&order=updated_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_cohorts?select=*&order=created_at.desc", []),
      army.safeSupabaseGetAll("runtime_army_events?select=*&order=created_at.desc", []),
      army.safeSupabaseGet("runtime_army_health_rollups?select=*&order=created_at.desc&limit=1", []),
    ]);

    const tableHealth = {
      runtime_kernel_config: configResult,
      runtime_army_limits: limitResult,
      runtime_departments: departmentResult,
      runtime_department_lane_assignments: assignmentResult,
      department_runtime_gates: gateResult,
      department_runtime_gate_events: gateEventResult,
      runtime_army_stages: stageResult,
      runtime_army_circuit_breakers: breakerResult,
      runtime_army_cohorts: cohortResult,
      runtime_army_events: eventResult,
      runtime_army_health_rollups: rollupResult,
    };

    const config = base.toConfigObject(configResult.data || []);
    const limits = base.toConfigObject(limitResult.data || []);
    const enrichedDepartments = base.enrichDepartmentRecords(departmentResult.data || [], assignmentResult.data || [], [], []);
    const departments = army.mergeArmyGateRecords(enrichedDepartments, gateResult.data || [], gateEventResult.data || [], cohortResult.data || [], stageResult.data || [], breakerResult.data || []);
    const approvedDepartments = departments.filter((department) => {
      const status = String(department.gate_status || "").toLowerCase();
      return (status === "approved" || status === "active") && Boolean(department.activation_eligible);
    });

    const search = base.text((event.queryStringParameters && event.queryStringParameters.search) || "", 120).toLowerCase();
    const statusFilter = base.text((event.queryStringParameters && event.queryStringParameters.status) || "", 80).toLowerCase();
    const familyFilter = base.text((event.queryStringParameters && event.queryStringParameters.family) || "", 120).toLowerCase();
    const unitFilter = base.text((event.queryStringParameters && event.queryStringParameters.unit) || "", 120).toLowerCase();
    const laneFilter = base.text((event.queryStringParameters && event.queryStringParameters.lane) || "", 120).toLowerCase();

    const filteredDepartments = approvedDepartments.filter((department) => {
      if (statusFilter && String(department.gate_status || "").toLowerCase() !== statusFilter) return false;
      if (familyFilter && !matchesFilter(department.family_id, familyFilter) && !matchesFilter(department.family_name, familyFilter)) return false;
      if (unitFilter && !matchesFilter(department.unit_id, unitFilter) && !matchesFilter(department.unit_name, unitFilter)) return false;
      if (
        laneFilter &&
        !matchesFilter(department.mapped_runtime_lane_id, laneFilter) &&
        !matchesFilter(department.mapped_runtime_lane_name, laneFilter) &&
        !matchesFilter(department.mapped_runtime_subdivision_id, laneFilter) &&
        !matchesFilter(department.mapped_runtime_subdivision_name, laneFilter)
      ) {
        return false;
      }
      if (search && !buildSearchText(department).includes(search)) return false;
      return true;
    });

    const limit = base.normalizeNumber((event.queryStringParameters && event.queryStringParameters.limit) || 100, 100, 1, 250);
    const offset = base.normalizeNumber((event.queryStringParameters && event.queryStringParameters.offset) || 0, 0, 0, 100000);
    const pageDepartments = filteredDepartments.slice(offset, offset + limit);

    const latestRollup = Array.isArray(rollupResult.data) && rollupResult.data.length ? rollupResult.data[0] : null;
    const rollup = latestRollup || army.buildArmyRollup(departments, gateResult.data || [], cohortResult.data || [], stageResult.data || [], breakerResult.data || [], config, eventResult.data || []);
    const partialBackend = Object.values(tableHealth).some((entry) => !entry.ok);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_partial: partialBackend,
      backend_status: {
        mvp62_department_gated_runtime_army_ready: true,
        global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || army.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || army.MAX_OPERATION_CHUNK_SIZE),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        current_stage_cap: Number(rollup.current_stage_cap || 5000),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        total_departments: Number(rollup.total_departments || 1777),
        full_47979_activation_blocked: Boolean(rollup.full_47979_activation_blocked),
        department_gated_activation_required: true,
        staged_activation_required: true,
        circuit_breaker_required: true,
        command_execution_enabled: Boolean(rollup.command_execution_enabled),
        deploy_execution_enabled: Boolean(rollup.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(rollup.rollback_execution_enabled),
        alert_sending_enabled: Boolean(rollup.alert_sending_enabled),
        kill_switch_visible: true,
        backend_partial: partialBackend,
      },
      caps: {
        global_live_agent_cap: Number(config.mvp62_global_live_agent_cap || army.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || army.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || army.MAX_OPERATION_CHUNK_SIZE),
      },
      rollup: {
        ...rollup,
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
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        total_departments: Number(rollup.total_departments || 1777),
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
      page_info: {
        limit,
        offset,
        returned: pageDepartments.length,
        total_filtered_departments: filteredDepartments.length,
        total_departments: departments.length,
      },
      filters: {
        search: search || "",
        status: statusFilter || "",
        family: familyFilter || "",
        unit: unitFilter || "",
        lane: laneFilter || "",
      },
      departments: pageDepartments,
      approved_department_gates: filteredDepartments,
      active_cohorts: (cohortResult.data || []).filter((cohort) => {
        const status = String(cohort.cohort_status || "").toLowerCase();
        return status === "active" || status === "partially_active";
      }),
      stages: stageResult.data || [],
      circuit_breakers: breakerResult.data || [],
      recent_events: (eventResult.data || []).slice(0, 100),
      gates: gateResult.data || [],
      cohorts: cohortResult.data || [],
      gate_events: gateEventResult.data || [],
      runtime_army_events: eventResult.data || [],
      limits,
      table_health: tableHealth,
    });
  } catch (error) {
    console.error("[runtime-army] list failed", error && error.message ? error.message : error);
    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime army list failed.",
      details: army.summarizeError(error),
    }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
