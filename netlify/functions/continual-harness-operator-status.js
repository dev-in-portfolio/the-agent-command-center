const base = require("./_shared/continual_harness_operator_helpers");

async function readCircuitBreaker() {
  try {
    const rows = await base.supabaseGet("runtime_army_circuit_breakers?select=*&order=updated_at.desc&limit=1");
    return Array.isArray(rows) && rows.length ? rows[0] : { breaker_status: "clear" };
  } catch {
    return { breaker_status: "clear" };
  }
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" });
  }

  if (!base.isConfigured()) {
    return base.backendUnavailable();
  }

  try {
    const [sessions, permissions, operations, plans, events, notes] = await Promise.all([
      base.supabaseGet("continual_harness_sessions?select=*&order=updated_at.desc,started_at.desc&limit=1"),
      base.supabaseGet("continual_harness_permissions?select=*&order=scope.asc"),
      base.supabaseGet("continual_harness_allowlisted_operations?select=*&order=operation_id.asc"),
      base.supabaseGet("continual_harness_run_plans?select=*&order=created_at.desc&limit=25"),
      base.supabaseGet("continual_harness_operator_events?select=*&order=created_at.desc&limit=25"),
      base.supabaseGet("continual_harness_readiness_notes?select=*&order=created_at.desc&limit=25"),
    ]);

    const circuitBreaker = await readCircuitBreaker();
    const session = Array.isArray(sessions) && sessions.length ? sessions[0] : null;

    return base.jsonResponse(200, base.buildOperatorStatus({
      session,
      permissions: Array.isArray(permissions) ? permissions : [],
      operations: Array.isArray(operations) ? operations : [],
      plans: Array.isArray(plans) ? plans : [],
      events: Array.isArray(events) ? events : [],
      notes: Array.isArray(notes) ? notes : [],
      circuitBreaker,
    }));
  } catch {
    return base.jsonResponse(500, {
      ok: false,
      error: "Continual Harness operator status failed.",
    });
  }
};
