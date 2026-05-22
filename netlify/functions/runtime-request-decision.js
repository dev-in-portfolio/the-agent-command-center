const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data) {
  return {
    statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-agent-command-center-mode": "mvp52-real-runtime-kernel",
    },
    body: JSON.stringify(data, null, 2),
  };
}

function backendUnavailable() {
  return jsonResponse(503, {
    ok: false,
    error: "Runtime kernel backend is not configured.",
  });
}

function text(value, maxLength) {
  return String(value == null ? "" : value).trim().slice(0, maxLength);
}

function parseBody(event) {
  const raw = event && typeof event.body === "string" ? event.body : "";
  if (raw.length > 12000) {
    throw new Error("PAYLOAD_TOO_LARGE");
  }
  return raw ? JSON.parse(raw) : {};
}

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
  };
}

async function supabaseRpc(functionName, payload) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${functionName}`, {
    method: "POST",
    headers: supabaseHeaders(),
    body: JSON.stringify(payload),
  });

  const bodyText = await response.text();
  const parsed = bodyText ? JSON.parse(bodyText) : null;

  if (!response.ok) {
    const error = new Error(parsed && parsed.message ? parsed.message : response.statusText);
    error.payload = parsed;
    error.status = response.status;
    throw error;
  }

  return parsed;
}

function mapDecisionError(errorMessage) {
  if (!errorMessage) return { statusCode: 500, error: "Runtime approval decision failed." };
  if (errorMessage.includes("BLOCKED_REQUEST_CANNOT_BE_APPROVED")) {
    return { statusCode: 409, error: "BLOCKED_REQUEST_CANNOT_BE_APPROVED" };
  }
  if (
    errorMessage.includes("INVALID_PAYLOAD") ||
    errorMessage.includes("REQUEST_NOT_FOUND") ||
    errorMessage.includes("APPROVAL_QUEUE_MISSING") ||
    errorMessage.includes("APPROVAL_ALREADY_DECIDED")
  ) {
    return { statusCode: 400, error: errorMessage };
  }
  if (errorMessage.includes("EXECUTION_MUST_REMAIN_FALSE")) {
    return { statusCode: 409, error: errorMessage };
  }
  return { statusCode: 500, error: "Runtime approval decision failed." };
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable();
  }

  try {
    const payload = parseBody(event);
    const requestId = text(payload.request_id, 64);
    const decision = text(payload.decision, 16);
    const approverName = text(payload.approver_name, 120);
    const approverEmail = text(payload.approver_email, 254);
    const decisionReason = text(payload.decision_reason, 2000);

    if (payload.execution_enabled === true || payload.execution_enabled === "true") {
      return jsonResponse(400, {
        ok: false,
        error: "EXECUTION_MUST_REMAIN_FALSE",
      });
    }

    if (!requestId || !decision || !approverName) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "request_id, decision, and approver_name are required.",
      });
    }

    if (!/^[0-9a-fA-F-]{36}$/.test(requestId)) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "request_id must be a UUID.",
      });
    }

    if (decision !== "approved" && decision !== "denied") {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "decision must be approved or denied.",
      });
    }

    const result = await supabaseRpc("runtime_kernel_decide_request", {
      p_request_id: requestId,
      p_decision: decision,
      p_approver_name: approverName,
      p_approver_email: approverEmail,
      p_decision_reason: decisionReason,
    });

    return jsonResponse(200, {
      ok: true,
      operation: "runtime-request-decision",
      request: result.request,
      approval_queue: result.approval_queue,
      audit_event: result.audit_event,
      approval_status: result.approval_queue ? result.approval_queue.approval_status : decision,
      blocked: false,
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      });
    }

    const mapped = mapDecisionError(error && error.message ? error.message : "");
    return jsonResponse(mapped.statusCode, {
      ok: false,
      error: mapped.error,
    });
  }
};
