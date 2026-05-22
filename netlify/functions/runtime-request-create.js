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

function supabaseHeaders(extra = {}) {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
    ...extra,
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

function classifyRequestType(requestType) {
  if (requestType === "content_review" || requestType === "stakeholder_report") {
    return { risk_level: "low", blocked: false };
  }
  if (requestType === "deploy_request" || requestType === "rollback_request") {
    return { risk_level: "high", blocked: false };
  }
  if (requestType === "supabase_write" || requestType === "alert_send" || requestType === "command_execution") {
    return { risk_level: "blocked", blocked: true };
  }
  return { risk_level: "medium", blocked: false };
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
    const requesterName = text(payload.requester_name, 120);
    const requesterEmail = text(payload.requester_email, 254);
    const requestTitle = text(payload.request_title, 180);
    const requestType = text(payload.request_type, 64);
    const requestBody = text(payload.request_body, 8000);

    if (!requestTitle || !requestType) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "request_title and request_type are required.",
      });
    }

    const allowedTypes = new Set([
      "content_review",
      "stakeholder_report",
      "deploy_request",
      "rollback_request",
      "supabase_write",
      "alert_send",
      "command_execution",
    ]);

    if (!allowedTypes.has(requestType)) {
      return jsonResponse(400, {
        ok: false,
        error: "INVALID_PAYLOAD",
        message: "request_type is not allowed.",
      });
    }

    const classification = classifyRequestType(requestType);
    const dryRunSummary = {
      request_type: requestType,
      risk_level: classification.risk_level,
      blocked: classification.blocked,
      approval_required: !classification.blocked,
      execution_enabled: false,
      expected_changes: classification.blocked
        ? ["No execution will occur."]
        : [
            "Persist the runtime request.",
            "Persist an audit trail.",
            "Create a controlled approval queue record.",
          ],
      affected_systems: [
        "runtime_requests",
        "runtime_audit_events",
        "runtime_approval_queue",
      ],
      notes: classification.blocked
        ? "This request type is blocked in MVP-52."
        : "Approval is not execution. MVP-52 never executes the requested action.",
      source: "mvp52_real_runtime_kernel",
    };

    const result = await supabaseRpc("runtime_kernel_submit_request", {
      p_requester_name: requesterName,
      p_requester_email: requesterEmail,
      p_request_title: requestTitle,
      p_request_type: requestType,
      p_request_body: requestBody,
    });

    return jsonResponse(201, {
      ok: true,
      operation: "runtime-request-create",
      request: result.request,
      approval_queue: result.approval_queue,
      audit_events: result.audit_events,
      dry_run_summary: result.dry_run_summary || dryRunSummary,
      blocked: Boolean(result.blocked),
    });
  } catch (error) {
    if (error && error.message === "PAYLOAD_TOO_LARGE") {
      return jsonResponse(413, {
        ok: false,
        error: "PAYLOAD_TOO_LARGE",
      });
    }

    return jsonResponse(500, {
      ok: false,
      error: "Runtime request submission failed.",
    });
  }
};
