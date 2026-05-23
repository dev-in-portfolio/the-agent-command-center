const {
  backendUnavailable,
  isApprovedLane,
  isConfigured,
  jsonResponse,
  normalizeNumber,
  parseBody,
  supabaseGet,
  supabasePatch,
  supabasePost,
  text,
} = require("./_shared/runtime_department_helpers");

function assignmentStatusFromRuntimeStatus(runtimeStatus) {
  const normalized = text(runtimeStatus, 80).toLowerCase();
  if (normalized === "eligible_for_supervised_runtime") return "eligible";
  if (normalized === "readiness_review") return "readiness_review";
  if (normalized === "blocked") return "blocked";
  if (normalized === "disabled") return "disabled";
  return "mapped_readonly";
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable("Runtime department backend is not configured.");
  }

  try {
    const body = parseBody(event);
    const departmentId = text(body.department_id, 80);
    const runtimeLaneId = text(body.runtime_lane_id, 80);
    const runtimeSubdivisionId = text(body.runtime_subdivision_id, 80);
    const actor = text(body.actor, 120);
    const mappedAgentCapacity = normalizeNumber(body.mapped_agent_capacity, 0, 0, 1000000);

    if (!departmentId) {
      return jsonResponse(400, { ok: false, error: "department_id is required." });
    }
    if (!runtimeLaneId) {
      return jsonResponse(400, { ok: false, error: "runtime_lane_id is required." });
    }
    if (!isApprovedLane(runtimeLaneId, runtimeSubdivisionId || undefined)) {
      return jsonResponse(400, {
        ok: false,
        error: "runtime_lane_id must use the approved MVP-58 lane registry.",
      });
    }

    const departmentRows = await supabaseGet(`runtime_departments?select=*&department_id=eq.${encodeURIComponent(departmentId)}&limit=1`);
    const department = departmentRows && departmentRows[0];
    if (!department) {
      return jsonResponse(404, {
        ok: false,
        error: "Department not found.",
      });
    }

    const laneAssignment = {
      department_id: departmentId,
      runtime_lane_id: runtimeLaneId,
      runtime_subdivision_id: runtimeSubdivisionId || null,
      mapped_agent_capacity: mappedAgentCapacity || Number(department.registered_agent_count || 0),
      assignment_status: assignmentStatusFromRuntimeStatus(department.runtime_status),
      assigned_by: actor || null,
      source: "mvp59_department_runtime_mapping",
    };

    const assignmentRows = await supabasePost(
      "runtime_department_lane_assignments?on_conflict=department_id",
      [laneAssignment],
      {
        Prefer: "resolution=merge-duplicates,return=representation",
      },
    );

    if (text(department.runtime_status, 80).toLowerCase() === "unmapped") {
      await supabasePatch(`runtime_departments?department_id=eq.${encodeURIComponent(departmentId)}`, [{
        runtime_status: "mapped_readonly",
        activation_eligible: false,
        source: "mvp59_department_runtime_mapping",
      }]);
    }

    const eventRow = {
      department_id: departmentId,
      actor: actor || null,
      event_type: "DEPARTMENT_LANE_ASSIGNED",
      event_summary: `Department ${departmentId} assigned to runtime lane ${runtimeLaneId}.`,
      event_payload: {
        department_id: departmentId,
        runtime_lane_id: runtimeLaneId,
        runtime_subdivision_id: runtimeSubdivisionId || null,
        mapped_agent_capacity: laneAssignment.mapped_agent_capacity,
      },
      source: "mvp59_department_runtime_mapping",
    };

    await supabasePost("runtime_department_events", [eventRow]);

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      assignment: assignmentRows && assignmentRows[0] ? assignmentRows[0] : laneAssignment,
      event: eventRow,
      activation_enabled: false,
      command_execution_enabled: false,
      deploy_execution_enabled: false,
      rollback_execution_enabled: false,
      alert_sending_enabled: false,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Department lane assignment failed.",
    });
  }
};
