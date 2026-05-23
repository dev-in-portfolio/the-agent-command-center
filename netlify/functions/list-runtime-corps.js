const base = require("./_shared/runtime_department_helpers");
const gate = require("./_shared/runtime_department_gate_helpers");
const corps = require("./_shared/runtime_corps_helpers");
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are only read server-side through the shared helper.

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
    row.gate_id,
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
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" }, "mvp61-5000-agent-department-gated-runtime-corps");
  }

  if (!corps.isConfigured()) {
    return corps.backendUnavailable("Runtime corps backend is not configured.");
  }

  try {
    const [
      configResult,
      limitResult,
      departmentResult,
      assignmentResult,
      gateResult,
      gateEventResult,
      cohortResult,
      eventResult,
    ] = await Promise.all([
      corps.safeSupabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc", []),
      corps.safeSupabaseGet("runtime_corps_limits?select=key,value,updated_at&order=key.asc", []),
      corps.safeSupabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc", []),
      corps.safeSupabaseGet("runtime_department_lane_assignments?select=*&order=assigned_at.desc", []),
      corps.safeSupabaseGetAll("department_runtime_gates?select=*&order=department_id.asc", []),
      corps.safeSupabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc", []),
      corps.safeSupabaseGetAll("runtime_corps_cohorts?select=*&order=created_at.desc", []),
      corps.safeSupabaseGetAll("runtime_corps_events?select=*&order=created_at.desc", []),
    ]);

    const tableHealth = {
      runtime_kernel_config: configResult,
      runtime_corps_limits: limitResult,
      runtime_departments: departmentResult,
      runtime_department_lane_assignments: assignmentResult,
      department_runtime_gates: gateResult,
      department_runtime_gate_events: gateEventResult,
      runtime_corps_cohorts: cohortResult,
      runtime_corps_events: eventResult,
    };

    const config = base.toConfigObject(configResult.data || []);
    const limits = base.toConfigObject(limitResult.data || []);
    const enrichedDepartments = base.enrichDepartmentRecords(departmentResult.data || [], assignmentResult.data || [], [], []);
    const departments = corps.mergeCorpsGateRecords(enrichedDepartments, gateResult.data || [], gateEventResult.data || [], cohortResult.data || []);
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
      if (statusFilter && String(department.gate_status || "").toLowerCase() !== statusFilter) {
        return false;
      }
      if (familyFilter && !matchesFilter(department.family_id, familyFilter) && !matchesFilter(department.family_name, familyFilter)) {
        return false;
      }
      if (unitFilter && !matchesFilter(department.unit_id, unitFilter) && !matchesFilter(department.unit_name, unitFilter)) {
        return false;
      }
      if (
        laneFilter &&
        !matchesFilter(department.mapped_runtime_lane_id, laneFilter) &&
        !matchesFilter(department.mapped_runtime_lane_name, laneFilter) &&
        !matchesFilter(department.mapped_runtime_subdivision_id, laneFilter) &&
        !matchesFilter(department.mapped_runtime_subdivision_name, laneFilter)
      ) {
        return false;
      }
      if (search && !buildSearchText(department).includes(search)) {
        return false;
      }
      return true;
    });

    const limit = base.normalizeNumber((event.queryStringParameters && event.queryStringParameters.limit) || 100, 100, 1, 250);
    const offset = base.normalizeNumber((event.queryStringParameters && event.queryStringParameters.offset) || 0, 0, 0, 100000);
    const pageDepartments = filteredDepartments.slice(offset, offset + limit);
    const activeCohorts = (cohortResult.data || []).filter((cohort) => {
      const status = String(cohort.cohort_status || "").toLowerCase();
      return status === "active" || status === "partially_active";
    });
    const rollup = corps.buildCorpsRollup(departments, gateResult.data || [], cohortResult.data || [], config);
    const partialBackend = Object.values(tableHealth).some((entry) => !entry.ok);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_partial: partialBackend,
      backend_status: {
        mvp61_department_gated_runtime_corps_ready: true,
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        total_departments: Number(rollup.total_departments || 1777),
        full_47979_activation_blocked: Boolean(rollup.full_47979_activation_blocked),
        department_gated_activation_required: true,
        command_execution_enabled: Boolean(rollup.command_execution_enabled),
        deploy_execution_enabled: Boolean(rollup.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(rollup.rollback_execution_enabled),
        alert_sending_enabled: Boolean(rollup.alert_sending_enabled),
        kill_switch_visible: true,
        backend_partial: partialBackend,
      },
      caps: {
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
      },
      rollup: {
        ...rollup,
        gate_event_count: (gateEventResult.data || []).length,
        cohort_event_count: (eventResult.data || []).length,
        active_cohorts_count: activeCohorts.length,
        department_gated_activation_required: true,
      },
      counts: {
        total_departments: departments.length,
        filtered_departments: filteredDepartments.length,
        approved_department_gates: rollup.approved_department_gates,
        active_department_gates: rollup.active_department_gates,
        active_cohorts: activeCohorts.length,
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        gate_event_count: (gateEventResult.data || []).length,
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
      active_cohorts: activeCohorts,
      recent_events: (eventResult.data || []).slice(0, 100),
      gates: gateResult.data || [],
      cohorts: cohortResult.data || [],
      gate_events: gateEventResult.data || [],
      runtime_corps_events: eventResult.data || [],
      limits,
      table_health: tableHealth,
    });
  } catch (error) {
    console.error("[runtime-corps] list failed", error && error.message ? error.message : error);
    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime corps list failed.",
      details: corps.summarizeError(error),
    });
  }
};
