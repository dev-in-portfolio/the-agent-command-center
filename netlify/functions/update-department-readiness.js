const {
  ALLOWED_RUNTIME_STATUS,
  backendUnavailable,
  isConfigured,
  jsonResponse,
  parseBody,
  supabaseGet,
  supabasePatch,
  supabasePost,
  text,
} = require("./_shared/runtime_department_helpers");

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
    const runtimeStatus = text(body.runtime_status, 80).toLowerCase();
    const actor = text(body.actor, 120);
    const reason = text(body.reason, 500);
    const activationEligible = Boolean(body.activation_eligible);

    if (!departmentId) {
      return jsonResponse(400, { ok: false, error: "department_id is required." });
    }
    if (!runtimeStatus || !ALLOWED_RUNTIME_STATUS.has(runtimeStatus)) {
      return jsonResponse(400, {
        ok: false,
        error: "runtime_status must be one of the controlled department runtime states.",
      });
    }
    if (activationEligible && runtimeStatus !== "eligible_for_supervised_runtime") {
      return jsonResponse(400, {
        ok: false,
        error: "activation_eligible can only be true when runtime_status is eligible_for_supervised_runtime.",
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

    const updatedDepartment = {
      runtime_status: runtimeStatus,
      activation_eligible: runtimeStatus === "eligible_for_supervised_runtime" ? activationEligible : false,
      source: "mvp59_department_runtime_mapping",
    };

    const departmentUpdateRows = await supabasePatch(`runtime_departments?department_id=eq.${encodeURIComponent(departmentId)}`, [updatedDepartment]);
    const eventRow = {
      department_id: departmentId,
      actor: actor || null,
      event_type: "DEPARTMENT_READINESS_UPDATED",
      event_summary: `Department ${departmentId} readiness updated to ${runtimeStatus}.`,
      event_payload: {
        department_id: departmentId,
        runtime_status: runtimeStatus,
        activation_eligible: updatedDepartment.activation_eligible,
        reason: reason || null,
      },
      source: "mvp59_department_runtime_mapping",
    };

    await supabasePost("runtime_department_events", [eventRow]);

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      department: departmentUpdateRows && departmentUpdateRows[0] ? departmentUpdateRows[0] : { ...department, ...updatedDepartment },
      event: eventRow,
      command_execution_enabled: false,
      deploy_execution_enabled: false,
      rollback_execution_enabled: false,
      alert_sending_enabled: false,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Department readiness update failed.",
    });
  }
};
