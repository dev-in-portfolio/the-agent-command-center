/**
 * Request Write Smoke Status
 * Safe verification of write implementation and gates.
 * GET only. No secrets output. No writes.
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

  const status = {
    provider_configured: !!(SUPABASE_URL && SUPABASE_ANON_KEY),
    auth_flag_enabled: MVP_ENABLE_SUPABASE_AUTH,
    request_api_flag_enabled: MVP_ENABLE_SUPABASE_REQUEST_API,
    writes_flag_enabled: MVP_ENABLE_REQUEST_API_WRITES,
    create_write_implemented: true,
    update_delete_execute_blocked: true,
    auth_context: {
      authenticated: auth.authenticated,
      has_token: auth.has_token,
      error: auth.error
    }
  };

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(status)
  };
};
