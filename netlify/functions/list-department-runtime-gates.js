const base = require("./_shared/runtime_department_helpers");
const gate = require("./_shared/runtime_department_gate_helpers");

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
    return base.jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable("Department-gated runtime backend is not configured.");
  }

  try {
    const [configRows, limitRows, departmentRows, assignmentRows, noteRows, departmentEventRows, gateRows, gateEventRows] = await Promise.all([
      base.supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      base.supabaseGet("department_runtime_global_limits?select=key,value,updated_at&order=key.asc"),
      base.supabaseGetAll("runtime_departments?select=*&order=family_id.asc,department_id.asc"),
      base.supabaseGet("runtime_department_lane_assignments?select=*&order=assigned_at.desc"),
      base.supabaseGetAll("runtime_department_readiness_notes?select=*&order=created_at.desc"),
      base.supabaseGetAll("runtime_department_events?select=*&order=created_at.desc"),
      base.supabaseGetAll("department_runtime_gates?select=*&order=department_id.asc"),
      base.supabaseGetAll("department_runtime_gate_events?select=*&order=created_at.desc"),
    ]);

    const config = base.toConfigObject(configRows);
    const limits = base.toConfigObject(limitRows);
    const enrichedDepartments = base.enrichDepartmentRecords(
      departmentRows || [],
      assignmentRows || [],
      noteRows || [],
      departmentEventRows || [],
    );
    const departments = gate.mergeGateRecords(enrichedDepartments, gateRows || [], gateEventRows || []);
    const search = base.text((event.queryStringParameters && event.queryStringParameters.search) || "", 120).toLowerCase();
    const statusFilter = base.text((event.queryStringParameters && event.queryStringParameters.status) || "", 80).toLowerCase();
    const familyFilter = base.text((event.queryStringParameters && event.queryStringParameters.family) || "", 120).toLowerCase();
    const unitFilter = base.text((event.queryStringParameters && event.queryStringParameters.unit) || "", 120).toLowerCase();
    const laneFilter = base.text((event.queryStringParameters && event.queryStringParameters.lane) || "", 120).toLowerCase();

    const filteredDepartments = departments.filter((department) => {
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
    const rollup = gate.buildDepartmentGateRollup(departments, gateRows || [], config);
    const activeAgents = Number(rollup.current_live_runtime_agents || 0);

    return base.jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        department_gated_runtime_ready: Boolean(config.mvp60_department_gated_runtime_ready),
        global_live_agent_cap: Number(config.mvp60_global_live_agent_cap || gate.GLOBAL_LIVE_AGENT_CAP),
        max_department_activation_cap: Number(config.max_department_activation_cap || gate.MAX_DEPARTMENT_ACTIVATION_CAP),
        live_runtime_agents_enabled: activeAgents,
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        total_units: Number(config.total_units || 5331),
        total_families: Number(config.total_families || 175),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked !== false),
        department_gated_expansion_enabled: Boolean(config.department_gated_expansion_enabled),
        command_execution_enabled: Boolean(config.command_execution_enabled),
        deploy_execution_enabled: Boolean(config.deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.alert_sending_enabled),
        kill_switch_visible: true,
      },
      config,
      global_limits: limits,
      rollup: {
        ...rollup,
        gate_event_count: (gateEventRows || []).length,
        readiness_note_count: (noteRows || []).length,
        audit_event_count: (departmentEventRows || []).length,
      },
      counts: {
        total_departments: departments.length,
        filtered_departments: filteredDepartments.length,
        approved_gates: rollup.approved_gates,
        active_gates: rollup.active_gates,
        blocked_gates: rollup.blocked_gates,
        current_live_runtime_agents: activeAgents,
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_units: Number(config.total_units || 5331),
        total_families: Number(config.total_families || 175),
        gate_event_count: (gateEventRows || []).length,
        readiness_note_count: (noteRows || []).length,
        audit_event_count: (departmentEventRows || []).length,
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
      gates: gateRows || [],
      gate_events: gateEventRows || [],
      readiness_notes: noteRows || [],
      department_events: departmentEventRows || [],
    });
  } catch (error) {
    return base.jsonResponse(500, {
      ok: false,
      error: "Department-gated runtime list failed.",
    });
  }
};
