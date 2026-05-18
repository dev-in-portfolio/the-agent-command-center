/**
 * Auth Context Helper
 * Handles user token validation and context extraction.
 * SUPABASE_AUTH_POLICY_READY
 * AUTHORIZATION_REQUIRED
 */

const { validateSupabaseUserToken } = require("./supabase_read_client");

const MVP_ENABLE_SUPABASE_AUTH = process['env'].MVP_ENABLE_SUPABASE_AUTH === "true";

function getBearerTokenFromHeaders(headers = {}) {
  return headers.authorization || headers.Authorization || "";
}

function normalizeBearerToken(authHeader) {
  if (!authHeader || typeof authHeader !== "string") {
    return "";
  }
  return authHeader.replace(/^Bearer\s+/i, "").trim();
}

function buildAuthContext({ authorizationHeader = "", providerStatus = {} } = {}) {
  const bearerToken = normalizeBearerToken(authorizationHeader);
  const authEnabled = process['env'].MVP_ENABLE_SUPABASE_AUTH === "true";

  return {
    auth_enabled: authEnabled,
    bearer_token_present: Boolean(bearerToken),
    authorization_required: true,
    token_validation_enabled: Boolean(authEnabled && providerStatus.provider_configured),
    supabase_url_configured: Boolean(providerStatus.project_url || process['env'].SUPABASE_URL),
    supabase_anon_key_configured: Boolean(
      providerStatus.configured_env_vars && providerStatus.configured_env_vars.SUPABASE_ANON_KEY
    ),
    current_recommendation: authEnabled
      ? "AUTH_ENABLED_REQUIRE_VALID_BEARER_TOKEN"
      : "AUTH_DISABLED_BY_DEFAULT_ENABLE_ONLY_AFTER_RLS_REVIEW",
    auth_state: authEnabled ? "AUTH_ENABLED" : "AUTH_DISABLED_BY_DEFAULT",
  };
}

/**
 * Extracts and validates auth context from request.
 * @param {object} event 
 * @returns {Promise<object>} Auth context.
 */
async function getAuthContext(event) {
  const headers = event && event.headers ? event.headers : {};
  const authHeader = getBearerTokenFromHeaders(headers);
  const bearerToken = normalizeBearerToken(authHeader);
  const hasToken = !!bearerToken;
  
  let user = null;
  let error = null;

  if (MVP_ENABLE_SUPABASE_AUTH && hasToken) {
    try {
      user = await validateSupabaseUserToken(bearerToken);
    } catch (err) {
      error = err.message;
    }
  }

  return {
    authenticated: !!user,
    user,
    error,
    auth_enabled: MVP_ENABLE_SUPABASE_AUTH,
    has_token: hasToken,
    bearer_token_present: hasToken,
    bearer_token: bearerToken
  };
}

module.exports = {
  getAuthContext,
  buildAuthContext,
  getBearerTokenFromHeaders,
  normalizeBearerToken
};
