const base = require("./_shared/continual_harness_operator_helpers");

async function readRunPlan(runPlanId) {
  const rows = await base.supabaseGet(`continual_harness_run_plans?select=*&run_plan_id=eq.${encodeURIComponent(runPlanId)}&limit=1`);
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

async function readOperation(operationId) {
  const rows = await base.supabaseGet(`continual_harness_allowlisted_operations?select=*&operation_id=eq.${encodeURIComponent(operationId)}&limit=1`);
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable();
  }

  try {
    const payload = base.parseBody(event);
    const runPlanId = base.text(payload.run_plan_id, 80);

    if (!runPlanId) {
      return base.jsonResponse(400, { ok: false, error: "run_plan_id is required." });
    }

    const runPlan = await readRunPlan(runPlanId);
    if (!runPlan) {
      return base.jsonResponse(404, { ok: false, error: "Run plan not found." });
    }

    const operation = await readOperation(runPlan.requested_operation);
    if (!operation || !operation.enabled) {
      await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlanId)}`, [{
        validation_status: "blocked",
        approval_status: "denied",
        execution_status: "blocked",
      }]);
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Requested operation is not allowlisted.",
      });
    }

    if (!base.isAllowedPermissionScope(runPlan.requested_scope) || base.isBlockedPermissionScope(runPlan.requested_scope)) {
      await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlanId)}`, [{
        validation_status: "blocked",
        approval_status: "denied",
        execution_status: "blocked",
      }]);
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Requested scope is blocked.",
      });
    }

    if (base.isDangerousPayload(runPlan.plan_body)) {
      await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlanId)}`, [{
        validation_status: "blocked",
        approval_status: "denied",
        execution_status: "blocked",
      }]);
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Blocked content detected in run plan.",
      });
    }

    const updatedRows = await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlanId)}`, [{
      validation_status: "passed",
      approval_status: "not_required",
      execution_status: runPlan.execution_status === "blocked" ? "blocked" : runPlan.execution_status,
    }]);
    const updatedPlan = Array.isArray(updatedRows) && updatedRows.length ? updatedRows[0] : runPlan;

    await base.supabasePost("continual_harness_operator_events", [{
      run_plan_id: runPlanId,
      event_type: "run_plan_validated",
      event_summary: `Validated ${runPlan.title}`,
      event_payload: {
        validation_status: "passed",
        approval_status: "not_required",
        dry_run_status: "passed",
        requested_scope: runPlan.requested_scope,
        requested_operation: runPlan.requested_operation,
      },
    }]);

    return base.jsonResponse(200, {
      ok: true,
      run_plan: updatedPlan,
      validation_status: "passed",
      approval_status: "not_required",
      dry_run_status: "passed",
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Continual Harness run plan validation failed.",
    });
  }
};
