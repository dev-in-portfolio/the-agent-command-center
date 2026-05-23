const base = require("./_shared/runtime_department_helpers");
const army = require("./_shared/runtime_army_helpers");

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return base.jsonResponse(405, { ok: false, error: "Method Not Allowed" }, "mvp62-20000-agent-department-gated-runtime-army");
  }

  if (!army.isConfigured()) {
    return army.backendUnavailable("Runtime army backend is not configured.");
  }

  try {
    const payload = army.parseBody(event);
    const action = army.text(payload.action, 30).toLowerCase();
    const breakerId = army.text(payload.breaker_id, 80);
    const breakerName = army.text(payload.breaker_name, 120) || "runtime_army_global";
    const reason = army.text(payload.reason, 4000);
    const actor = army.text(payload.actor, 120);
    const stageId = army.text(payload.stage_id, 80);
    const departmentId = army.text(payload.department_id, 80);

    if (action === "trigger") {
      const result = await army.supabaseRpc("runtime_army_trigger_circuit_breaker", {
        p_breaker_name: breakerName,
        p_trigger_reason: reason || "",
        p_actor: actor || "operator",
        p_stage_id: stageId || null,
        p_department_id: departmentId || null,
      });

      if (!result.ok) {
        return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "runtime-army-circuit-breaker-trigger", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
      }

      return base.jsonResponse(200, {
        ok: true,
        operation: "runtime-army-circuit-breaker-trigger",
        blocked: false,
        breaker: result.breaker || null,
        event: result.event || null,
        circuit_breaker_status: result.circuit_breaker_status || "triggered",
      }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    if (action === "clear") {
      if (!breakerId) {
        return base.jsonResponse(400, { ok: false, error: "breaker_id is required for clear." }, "mvp62-20000-agent-department-gated-runtime-army");
      }

      const result = await army.supabaseRpc("runtime_army_clear_circuit_breaker", {
        p_breaker_id: breakerId,
        p_actor: actor || "operator",
        p_reason: reason || "",
      });

      if (!result.ok) {
        return base.jsonResponse(result.blocked ? 409 : 400, { ok: false, operation: "runtime-army-circuit-breaker-clear", ...result }, "mvp62-20000-agent-department-gated-runtime-army");
      }

      return base.jsonResponse(200, {
        ok: true,
        operation: "runtime-army-circuit-breaker-clear",
        blocked: false,
        breaker: result.breaker || null,
        event: result.event || null,
        circuit_breaker_status: result.circuit_breaker_status || "clear",
      }, "mvp62-20000-agent-department-gated-runtime-army");
    }

    return base.jsonResponse(400, { ok: false, error: "action must be trigger or clear." }, "mvp62-20000-agent-department-gated-runtime-army");
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return base.jsonResponse(413, { ok: false, error: "PAYLOAD_TOO_LARGE" }, "mvp62-20000-agent-department-gated-runtime-army");
    }
    return base.jsonResponse(500, { ok: false, error: "Runtime army circuit breaker failed." }, "mvp62-20000-agent-department-gated-runtime-army");
  }
};
