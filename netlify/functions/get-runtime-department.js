const {
  backendUnavailable,
  buildRollupSnapshot,
  enrichDepartmentRecords,
  isConfigured,
  jsonResponse,
  supabaseGet,
  text,
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

  const departmentId = text((event.queryStringParameters && event.queryStringParameters.department_id) || "", 80);
  if (!departmentId) {
    return jsonResponse(400, {
      ok: false,
      error: "department_id is required.",
    });
  }

  try {
    const [configRows, departmentRows, assignmentRows, noteRows, eventRows, rollupRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet(`runtime_departments?select=*&department_id=eq.${encodeURIComponent(departmentId)}&limit=1`),
      supabaseGet(`runtime_department_lane_assignments?select=*&department_id=eq.${encodeURIComponent(departmentId)}&limit=1`),
      supabaseGet(`runtime_department_readiness_notes?select=*&department_id=eq.${encodeURIComponent(departmentId)}&order=created_at.desc&limit=500`),
      supabaseGet(`runtime_department_events?select=*&department_id=eq.${encodeURIComponent(departmentId)}&order=created_at.desc&limit=500`),
      supabaseGet("runtime_department_rollups?select=*&order=created_at.desc&limit=1"),
    ]);

    const config = toConfigObject(configRows);
    const department = (enrichDepartmentRecords(departmentRows || [], assignmentRows || [], noteRows || [], eventRows || [])[0]) || null;
    if (!department) {
      return jsonResponse(404, {
        ok: false,
        error: "Department not found.",
      });
    }

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: {
        full_47979_activation_blocked: Boolean(config.full_47979_activation_blocked),
        total_registered_agents: Number(config.total_registered_agents || 47979),
        total_departments: Number(config.total_departments || 1777),
        total_units: Number(config.total_units || 5331),
        total_families: Number(config.total_families || 175),
        live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
      },
      rollup: rollupRows && rollupRows[0] ? rollupRows[0] : buildRollupSnapshot([department], config),
      department,
      lane_assignment: assignmentRows && assignmentRows[0] ? assignmentRows[0] : null,
      readiness_notes: noteRows || [],
      department_events: eventRows || [],
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime department lookup failed.",
    });
  }
};
