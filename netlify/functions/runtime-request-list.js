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

function supabaseHeaders() {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
  };
}

async function supabaseGet(path) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method: "GET",
    headers: supabaseHeaders(),
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

function buildBackendStatus(configRows) {
  const config = Object.fromEntries(
    (configRows || []).map((row) => [row.key, row.value])
  );

  return {
    runtime_activation_started: Boolean(config.runtime_activation_started),
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
    command_execution_enabled: Boolean(config.command_execution_enabled),
    automation_enabled: Boolean(config.automation_enabled),
    rollback_execution_enabled: Boolean(config.rollback_execution_enabled),
    alert_sending_enabled: Boolean(config.alert_sending_enabled),
  };
}

exports.handler = async function handler(event) {
  if (event.httpMethod !== "GET") {
    return jsonResponse(405, {
      ok: false,
      error: "Method Not Allowed",
    });
  }

  if (!isConfigured()) {
    return backendUnavailable();
  }

  try {
    const [configRows, requestRows, approvalRows, auditRows] = await Promise.all([
      supabaseGet("runtime_kernel_config?select=key,value,updated_at&order=key.asc"),
      supabaseGet("runtime_requests?select=*&order=created_at.desc&limit=50"),
      supabaseGet("runtime_approval_queue?select=*&order=created_at.desc&limit=50"),
      supabaseGet("runtime_audit_events?select=*&order=created_at.desc&limit=50"),
    ]);

    const approvalsByRequestId = new Map();
    for (const approval of approvalRows || []) {
      approvalsByRequestId.set(approval.request_id, approval);
    }

    const requests = (requestRows || []).map((request) => {
      const approval = approvalsByRequestId.get(request.id) || null;
      return {
        ...request,
        approval_status: approval ? approval.approval_status : null,
        approver_name: approval ? approval.approver_name : null,
        approver_email: approval ? approval.approver_email : null,
        decision_reason: approval ? approval.decision_reason : null,
        decision_at: approval ? approval.decision_at : null,
        required_level: approval ? approval.required_level : null,
      };
    });

    const counts = {
      request_count: requests.length,
      pending_approval_count: requests.filter((request) => request.status === "pending_approval").length,
      blocked_count: requests.filter((request) => request.status === "blocked").length,
      approved_count: requests.filter((request) => request.status === "approved").length,
      denied_count: requests.filter((request) => request.status === "denied").length,
      audit_event_count: (auditRows || []).length,
    };

    return jsonResponse(200, {
      ok: true,
      backend_configured: true,
      backend_status: buildBackendStatus(configRows),
      config: Object.fromEntries((configRows || []).map((row) => [row.key, row.value])),
      requests,
      approval_queue: approvalRows || [],
      audit_events: auditRows || [],
      counts,
    });
  } catch (error) {
    return jsonResponse(500, {
      ok: false,
      error: "Runtime kernel backend query failed.",
    });
  }
};
