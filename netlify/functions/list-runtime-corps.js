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
    const [configRows, limitRows, departmentRows, assignmentRows, gateRows, gateEventRows, cohortRows, eventRows] = await Promise.all([
      base.supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      base.supabaseGet("runtime_corps_limits?select=key,value,updated_at&order=key.asc"),
      base.supabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc"),
      base.supabaseGet("runtime_department_lane_assignments?select=*&order=assigned_at.desc"),
      base.supabaseGetAll("department_runtime_gates?select=*&order=department_id.asc"),
      base.supabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc"),
      base.supabaseGetAll("runtime_corps_cohorts?select=*&order=created_at.desc"),
      base.supabaseGetAll("runtime_corps_events?select=*&order=created_at.desc"),
    ]);

    const config = base.toConfigObject(configRows);
    const limits = base.toConfigObject(limitRows);
    const enrichedDepartments = base.enrichDepartmentRecords(departmentRows || [], assignmentRows || [], [], []);
    const departments = corps.mergeCorpsGateRecords(enrichedDepartments, gateRows || [], gateEventRows || [], cohortRows || []);
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
    const activeCohorts = (cohortRows || []).filter((cohort) => {
      const status = String(cohort.cohort_status || "").toLowerCase();
      return status === "active" || status === "partially_active";
    });
    const rollup = corps.buildCorpsRollup(departments, gateRows || [], cohortRows || [], config);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        mvp61_department_gated_runtime_corps_ready: Boolean(config.mvp61_department_gated_runtime_corps_ready),
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        total_departments: Number(rollup.total_departments || 1777),
        full_47979_activation_blocked: Boolean(rollup.full_47979_activation_blocked),
        department_gated_activation_required: Boolean(rollup.department_gated_activation_required),
        command_execution_enabled: Boolean(rollup.command_execution_enabled),
        deploy_execution_enabled: Boolean(rollup.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(rollup.rollback_execution_enabled),
        alert_sending_enabled: Boolean(rollup.alert_sending_enabled),
        kill_switch_visible: true,
      },
      caps: {
        global_live_agent_cap: Number(config.mvp61_global_live_agent_cap || corps.GLOBAL_LIVE_AGENT_CAP),
        max_cohort_activation_size: Number(config.max_cohort_activation_size || corps.MAX_COHORT_ACTIVATION_SIZE),
        max_operation_chunk_size: Number(config.max_operation_chunk_size || corps.MAX_OPERATION_CHUNK_SIZE),
      },
      rollup: {
        ...rollup,
        gate_event_count: (gateEventRows || []).length,
        cohort_event_count: (eventRows || []).length,
        active_cohorts_count: activeCohorts.length,
      },
      counts: {
        total_departments: departments.length,
        filtered_departments: filteredDepartments.length,
        approved_department_gates: rollup.approved_department_gates,
        active_department_gates: rollup.active_department_gates,
        active_cohorts: activeCohorts.length,
        current_live_runtime_agents: Number(rollup.current_live_runtime_agents || 0),
        total_registered_agents: Number(rollup.total_registered_agents || 47979),
        gate_event_count: (gateEventRows || []).length,
        cohort_event_count: (eventRows || []).length,
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
      recent_events: (eventRows || []).slice(0, 100),
      gates: gateRows || [],
      cohorts: cohortRows || [],
      gate_events: gateEventRows || [],
      runtime_corps_events: eventRows || [],
      limits,
    });
  } catch (error) {
    return base.jsonResponse(500, {
      ok: false,
      error: "Runtime corps list failed.",
    });
  }
};
