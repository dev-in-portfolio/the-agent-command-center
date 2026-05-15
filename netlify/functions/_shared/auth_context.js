const { buildSupabaseProviderStatus } = require("./provider_config");

function hasBearerToken(authorizationHeader) {
  const header = String(authorizationHeader || "").trim();
  return /^Bearer\s+\S+/i.test(header);
}

function extractBearerToken(authorizationHeader) {
  const header = String(authorizationHeader || "").trim();
  if (!hasBearerToken(header)) {
    return "";
  }
  return header.replace(/^Bearer\s+/i, "").trim();
}

function buildAuthContext({ authorizationHeader, providerStatus } = {}) {
  const status = providerStatus || buildSupabaseProviderStatus();
  const authEnabled = Boolean(status.configured_env_vars && status.configured_env_vars.MVP_ENABLE_SUPABASE_AUTH);
  const bearerToken = extractBearerToken(authorizationHeader);
  const bearerTokenPresent = bearerToken.length > 0;
  const anonKeyConfigured = Boolean(status.configured_env_vars && status.configured_env_vars.SUPABASE_ANON_KEY);
  const urlConfigured = Boolean(status.project_url);

  if (!authEnabled) {
    return {
      auth_enabled: false,
      bearer_token_present: bearerTokenPresent,
      auth_state: "AUTH_DISABLED_BY_DEFAULT",
      validation_state: "scaffold_only",
      authorization_required: false,
      token_validation_enabled: false,
      supabase_url_configured: urlConfigured,
      supabase_anon_key_configured: anonKeyConfigured,
      current_recommendation: [
        "SUPABASE_AUTH_DISABLED_BY_DEFAULT",
        "AUTHORIZATION_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
      ],
    };
  }

  if (!bearerTokenPresent) {
    return {
      auth_enabled: true,
      bearer_token_present: false,
      auth_state: "AUTHORIZATION_REQUIRED",
      validation_state: "boundary_only",
      authorization_required: true,
      token_validation_enabled: false,
      supabase_url_configured: urlConfigured,
      supabase_anon_key_configured: anonKeyConfigured,
      current_recommendation: [
        "AUTHORIZATION_REQUIRED",
        "REQUEST_API_REQUIRES_BEARER_TOKEN",
        "NOT_READY_FOR_REAL_AUTOMATION",
      ],
    };
  }

  return {
    auth_enabled: true,
    bearer_token_present: true,
    auth_state: "AUTHENTICATED_REQUEST_BOUNDARY_ONLY",
    validation_state: "boundary_only",
    authorization_required: true,
    token_validation_enabled: false,
    supabase_url_configured: urlConfigured,
    supabase_anon_key_configured: anonKeyConfigured,
    current_recommendation: [
      "SUPABASE_AUTH_POLICY_READY",
      "RLS_POLICY_REQUIRED",
      "REQUEST_API_REQUIRES_BEARER_TOKEN",
      "WRITES_DISABLED_UNTIL_RLS_REVIEW",
      "NOT_READY_FOR_REAL_AUTOMATION",
    ],
  };
}

module.exports = {
  hasBearerToken,
  extractBearerToken,
  buildAuthContext,
};
