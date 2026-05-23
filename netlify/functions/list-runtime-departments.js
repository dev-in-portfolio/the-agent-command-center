const {
  ALLOWED_RUNTIME_LANES,
  ALLOWED_RUNTIME_SUBDIVISIONS,
  backendUnavailable,
  buildRollupSnapshot,
  enrichDepartmentRecords,
  isConfigured,
  jsonResponse,
  normalizeNumber,
  normalizeStatus,
  supabaseGet,
  text,
  toConfigObject,
} = require("./_shared/runtime_department_helpers");

function matchesFilter(value, filter) {
  if (!filter) return true;
  return String(value == null ? "" : value).toLowerCase().includes(filter);
}

function buildSearchText(department) {
  return [
    department.department_id,
    department.department_name,
    department.family_id,
    department.family_name,
    department.unit_id,
    department.unit_name,
    department.mapped_runtime_lane_id,
    department.mapped_runtime_lane_name,
    department.mapped_runtime_subdivision_id,
    department.mapped_runtime_subdivision_name,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

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
    const [configRows, departmentRows, assignmentRows, noteRows, eventRows, rollupRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_departments?select=*&order=family_id.asc,department_id.asc&limit=5000"),
      supabaseGet("runtime_department_lane_assignments?select=*&order=assigned_at.desc"),
      supabaseGet("runtime_department_readiness_notes?select=*&order=created_at.desc&limit=5000"),
      supabaseGet("runtime_department_events?select=*&order=created_at.desc&limit=5000"),
      supabaseGet("runtime_department_rollups?select=*&order=created_at.desc&limit=1"),
    ]);

    const config = toConfigObject(configRows);
    const enrichedDepartments = enrichDepartmentRecords(departmentRows || [], assignmentRows || [], noteRows || [], eventRows || []);
    const totalDepartments = enrichedDepartments.length;
    const latestRollup = rollupRows && rollupRows[0] ? rollupRows[0] : buildRollupSnapshot(enrichedDepartments, config);
    const notesCount = (noteRows || []).length;
    const auditEventCount = (eventRows || []).length;

    const search = text((event.queryStringParameters && event.queryStringParameters.search) || "", 120).toLowerCase();
    const statusFilter = normalizeStatus((event.queryStringParameters && event.queryStringParameters.status) || "");
    const familyFilter = text((event.queryStringParameters && event.queryStringParameters.family) || "", 120).toLowerCase();
    const unitFilter = text((event.queryStringParameters && event.queryStringParameters.unit) || "", 120).toLowerCase();
    const laneFilter = text((event.queryStringParameters && event.queryStringParameters.lane) || "", 120).toLowerCase();

    const filteredDepartments = enrichedDepartments.filter((department) => {
      if (statusFilter && normalizeStatus(department.runtime_status) !== statusFilter) {
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

    const limit = normalizeNumber((event.queryStringParameters && event.queryStringParameters.limit) || 100, 100, 1, 250);
    const offset = normalizeNumber((event.queryStringParameters && event.queryStringParameters.offset) || 0, 0, 0, 100000);
    const pageDepartments = filteredDepartments.slice(offset, offset + limit);
    const mappedCount = enrichedDepartments.filter((department) => normalizeStatus(department.runtime_status) !== "unmapped").length;
    const readinessReviewCount = enrichedDepartments.filter((department) => normalizeStatus(department.runtime_status) === "readiness_review").length;
    const eligibleCount = enrichedDepartments.filter((department) => normalizeStatus(department.runtime_status) === "eligible_for_supervised_runtime").length;
    const blockedCount = enrichedDepartments.filter((department) => normalizeStatus(department.runtime_status) === "blocked").length;
    const disabledCount = enrichedDepartments.filter((department) => normalizeStatus(department.runtime_status) === "disabled").length;

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        runtime_department_mapping_ready: Boolean(config.full_department_runtime_mapping_ready),
        full_department_runtime_mapping_ready: Boolean(config.full_department_runtime_mapping_ready),
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        total_units: Number(config.total_units || 5331),
        total_families: Number(config.total_families || 175),
        live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
        command_execution_enabled: Boolean(config.department_command_execution_enabled),
        deploy_execution_enabled: Boolean(config.department_deploy_execution_enabled),
        rollback_execution_enabled: Boolean(config.department_rollback_execution_enabled),
        alert_sending_enabled: Boolean(config.department_alert_sending_enabled),
        kill_switch_visible: true,
      },
      config,
      rollup: {
        ...latestRollup,
        notes_count: notesCount,
        audit_event_count: auditEventCount,
        heartbeat_count: Number(config.heartbeat_count || 0),
        readiness_note_count: notesCount,
      },
      counts: {
        total_departments: totalDepartments,
        mapped_departments: mappedCount,
        readiness_review_departments: readinessReviewCount,
        eligible_departments: eligibleCount,
        blocked_departments: blockedCount,
        disabled_departments: disabledCount,
        live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_units: Number(config.total_units || 5331),
        total_families: Number(config.total_families || 175),
        notes_count: notesCount,
        audit_event_count: auditEventCount,
      },
      page_info: {
        limit,
        offset,
        returned: pageDepartments.length,
        total_filtered_departments: filteredDepartments.length,
        total_departments: totalDepartments,
      },
      filters: {
        search: search || "",
        status: statusFilter || "",
        family: familyFilter || "",
        unit: unitFilter || "",
        lane: laneFilter || "",
      },
      departments: pageDepartments,
      lane_options: ALLOWED_RUNTIME_LANES,
      subdivision_options: ALLOWED_RUNTIME_SUBDIVISIONS,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime department list failed.",
    });
  }
};
