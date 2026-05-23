const base = require("./_shared/continual_harness_operator_helpers");

async function readRunPlan(runPlanId) {
  const rows = await base.supabaseGet(`continual_harness_run_plans?select=*&run_plan_id=eq.${encodeURIComponent(runPlanId)}&limit=1`);
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

async function readSession() {
  const rows = await base.supabaseGet("continual_harness_sessions?select=*&order=updated_at.desc,started_at.desc&limit=1");
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

async function readCircuitBreaker() {
  try {
    const rows = await base.supabaseGet("runtime_army_circuit_breakers?select=*&order=updated_at.desc&limit=1");
    return Array.isArray(rows) && rows.length ? rows[0] : { breaker_status: "clear" };
  } catch {
    return { breaker_status: "clear" };
  }
}

function ensureSafe(operationId) {
  return [
    "run_mvp_validators",
    "create_readiness_note",
    "create_audit_event",
    "export_status_report",
    "request_department_gate_review",
    "request_runtime_rollup",
    "request_harness_stop",
  ].includes(operationId);
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

    const circuitBreaker = await readCircuitBreaker();
    if (base.normalizeStatus(circuitBreaker.breaker_status) !== "clear") {
      await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlanId)}`, [{
        execution_status: "blocked",
      }]);
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Circuit breaker is not clear.",
      });
    }

    if (base.normalizeStatus(runPlan.validation_status) !== "passed") {
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Run plan has not passed validation.",
      });
    }

    if (!["approved", "not_required"].includes(base.normalizeStatus(runPlan.approval_status))) {
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Run plan approval is not recorded.",
      });
    }

    if (!ensureSafe(runPlan.requested_operation)) {
      return base.jsonResponse(409, {
        ok: false,
        blocked: true,
        error: "Requested operation is not allowlisted.",
      });
    }

    const session = await readSession();
    const planBody = runPlan.plan_body || {};
    let result = {
      operation: runPlan.requested_operation,
      status: "completed",
      message: "Allowlisted operator action recorded.",
    };

    if (runPlan.requested_operation === "create_readiness_note") {
      const noteBody = base.text(planBody.note_body || planBody.readiness_note || payload.note_body, 4000);
      const actor = base.text(planBody.actor || payload.actor, 120) || "operator";
      if (!noteBody) {
        return base.jsonResponse(400, { ok: false, error: "A readiness note body is required." });
      }

      const noteRows = await base.supabasePost("continual_harness_readiness_notes", [{
        run_plan_id: runPlan.run_plan_id,
        note_type: base.text(planBody.note_type || "readiness_note", 80),
        note_body: noteBody,
        actor,
      }]);

      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        readiness_note: Array.isArray(noteRows) && noteRows.length ? noteRows[0] : null,
      };
    } else if (runPlan.requested_operation === "create_audit_event") {
      const eventType = base.text(planBody.event_type || "operator_audit", 120);
      const eventSummary = base.text(planBody.event_summary || "Operator audit event recorded.", 400);
      await base.supabasePost("continual_harness_operator_events", [{
        run_plan_id: runPlan.run_plan_id,
        event_type: eventType,
        event_summary: eventSummary,
        event_payload: planBody.event_payload || {},
      }]);
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        event_type: eventType,
        event_summary: eventSummary,
      };
    } else if (runPlan.requested_operation === "export_status_report") {
      const permissions = await base.supabaseGet("continual_harness_permissions?select=*&order=scope.asc");
      const operations = await base.supabaseGet("continual_harness_allowlisted_operations?select=*&order=operation_id.asc");
      const status = base.buildOperatorStatus({
        session,
        permissions: Array.isArray(permissions) ? permissions : [],
        operations: Array.isArray(operations) ? operations : [],
        plans: [runPlan],
        events: [],
        notes: [],
        circuitBreaker,
      });
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        exported_report: status,
      };
    } else if (runPlan.requested_operation === "request_department_gate_review") {
      const departmentId = base.text(planBody.department_id, 80);
      if (!departmentId) {
        return base.jsonResponse(400, { ok: false, error: "department_id is required for a gate review request." });
      }
      const noteBody = base.text(planBody.note_body || "Continual Harness requested department gate review.", 4000);
      await base.supabasePost("runtime_department_readiness_notes", [{
        department_id: departmentId,
        note_type: base.text(planBody.note_type || "gate_review_request", 80),
        note_body: noteBody,
        actor: base.text(planBody.actor || payload.actor, 120) || "operator",
      }]);
      await base.supabasePost("continual_harness_operator_events", [{
        run_plan_id: runPlan.run_plan_id,
        event_type: "department_gate_review_requested",
        event_summary: `Requested gate review for ${departmentId}`,
        event_payload: {
          department_id: departmentId,
          note_body: noteBody,
        },
      }]);
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        department_id: departmentId,
      };
    } else if (runPlan.requested_operation === "request_runtime_rollup") {
      const rollupRows = await base.supabaseGet("runtime_army_health_rollups?select=*&order=created_at.desc&limit=1");
      const rollup = Array.isArray(rollupRows) && rollupRows.length ? rollupRows[0] : null;
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        rollup: rollup || null,
      };
    } else if (runPlan.requested_operation === "request_harness_stop") {
      await base.supabasePatch(`continual_harness_sessions?component_name=eq.${encodeURIComponent("Continual Harness")}&component_version=eq.${encodeURIComponent("v5.0.0")}`, [{
        status: "paused",
        stopped_at: new Date().toISOString(),
        stopped_reason: base.text(planBody.reason || payload.reason || "Operator stop requested.", 4000),
        current_scope: runPlan.requested_scope,
        current_operation: runPlan.requested_operation,
        active_run_plan_id: runPlan.run_plan_id,
      }]);
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        session_status: "paused",
      };
    } else if (runPlan.requested_operation === "run_mvp_validators") {
      result = {
        operation: runPlan.requested_operation,
        status: "completed",
        requested_validators: Array.isArray(planBody.validators) ? planBody.validators : [],
        note: "Validator execution is recorded as a controlled operator action.",
      };
    }

    await base.supabasePatch(`continual_harness_run_plans?run_plan_id=eq.${encodeURIComponent(runPlan.run_plan_id)}`, [{
      execution_status: "completed",
    }]);

    await base.supabasePost("continual_harness_operator_events", [{
      run_plan_id: runPlan.run_plan_id,
      event_type: "allowlisted_plan_action_completed",
      event_summary: `Allowlisted plan action completed: ${runPlan.requested_operation}`,
      event_payload: {
        result,
        requested_scope: runPlan.requested_scope,
        requested_operation: runPlan.requested_operation,
      },
    }]);

    return base.jsonResponse(200, {
      ok: true,
      run_plan: runPlan,
      result,
      session,
      circuit_breaker: circuitBreaker,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" });
    }

    return base.jsonResponse(500, {
      ok: false,
      error: "Continual Harness allowlisted operation execution failed.",
    });
  }
};
