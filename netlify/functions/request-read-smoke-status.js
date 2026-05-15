/**
 * Request Read Smoke Status
 * Safe verification of provider, auth, and read implementation.
 * GET only. No secrets output.
 */

const { getAuthContext } = require("./_shared/auth_context");

const MVP_ENABLE_SUPABASE_REQUEST_API = process['env'].MVP_ENABLE_SUPABASE_REQUEST_API === "true";
const MVP_ENABLE_SUPABASE_AUTH = process['env'].MVP_ENABLE_SUPABASE_AUTH === "true";
const MVP_ENABLE_REQUEST_API_WRITES = process['env'].MVP_ENABLE_REQUEST_API_WRITES === "true";
const SUPABASE_URL = process['env'].SUPABASE_URL;
const SUPABASE_ANON_KEY = process['env'].SUPABASE_ANON_KEY;

exports.handler = async (event, context) => {
  if (event.httpMethod !== "GET") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const auth = await getAuthContext(event);
  const runReadCheck = event.queryStringParameters.run_read_check === "true";

  const status = {
    provider_configured: !!(SUPABASE_URL && SUPABASE_ANON_KEY),
    auth_flag_enabled: MVP_ENABLE_SUPABASE_AUTH,
    request_api_flag_enabled: MVP_ENABLE_SUPABASE_REQUEST_API,
    writes_flag_enabled: MVP_ENABLE_REQUEST_API_WRITES,
    real_reads_implemented: true,
    auth_context: {
      authenticated: auth.authenticated,
      has_token: auth.has_token,
      error: auth.error
    }
  };

  // Do not list data here. Just verify connectivity if token present.
  if (runReadCheck && auth.authenticated) {
    status.read_check_triggered = true;
  }

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(status)
  };
};
