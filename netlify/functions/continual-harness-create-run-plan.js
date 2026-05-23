const base = require("./_shared/continual_harness_operator_helpers");

async function getSession() {
  const rows = await base.supabaseGet("continual_harness_sessions?select=*&order=updated_at.desc,started_at.desc&limit=1");
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
    const title = base.text(payload.title, 160);
    const requestedScope = base.text(payload.requested_scope, 120);
    const requestedOperation = base.text(payload.requested_operation, 120);
    const planBody = payload.plan_body && typeof payload.plan_body === "object" ? payload.plan_body : {};

    if (!title) {
      return base.jsonResponse(400, { ok: false, error: "title is required." });
    }

    if (!base.isAllowedPermissionScope(requestedScope) || base.isBlockedPermissionScope(requestedScope)) {
      return base.jsonResponse(400, { ok: false, error: "Requested scope is not available." });
    }

    const operationRows = await base.supabaseGet(`continual_harness_allowlisted_operations?select=*&operation_id=eq.${encodeURIComponent(requestedOperation)}&limit=1`);
    const operation = Array.isArray(operationRows) && operationRows.length ? operationRows[0] : null;

    if (!operation || !operation.enabled) {
      return base.jsonResponse(400, { ok: false, error: "Requested operation is not allowlisted." });
    }

    if (base.isDangerousPayload(planBody)) {
      return base.jsonResponse(400, { ok: false, error: "Blocked content detected in run plan." });
    }

    const session = await getSession();
    const runPlanRows = await base.supabasePost("continual_harness_run_plans", [{
      title,
      requested_scope: requestedScope,
      requested_operation: requestedOperation,
      plan_body: planBody,
      validation_status: "pending",
      approval_status: "pending",
      execution_status: "not_started",
    }]);
    const runPlan = Array.isArray(runPlanRows) && runPlanRows.length ? runPlanRows[0] : null;

    await base.supabasePost("continual_harness_operator_events", [{
      run_plan_id: runPlan ? runPlan.run_plan_id : null,
      event_type: "run_plan_created",
      event_summary: base.eventSummaryFromPlan(runPlan || { title, requested_operation: requestedOperation }),
      event_payload: {
        requested_scope: requestedScope,
        requested_operation: requestedOperation,
        session_status: session ? session.status : "active",
      },
    }]);

    return base.jsonResponse(200, {
      ok: true,
      run_plan: runPlan,
      session,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Continual Harness run plan creation failed.",
    });
  }
};
