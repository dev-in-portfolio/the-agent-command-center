const { jsonResponse, errorResponse } = require("./_shared/response");
const { buildSupabaseProviderStatus } = require("./_shared/provider_config");
const { buildAuthContext } = require("./_shared/auth_context");

exports.handler = async function(event) {
  if (event.httpMethod !== "GET") {
    return errorResponse("Method Not Allowed", 405);
  }

  const providerStatus = buildSupabaseProviderStatus();
  const authContext = buildAuthContext({
    authorizationHeader: event.headers && (event.headers.authorization || event.headers.Authorization),
    providerStatus,
  });

  return jsonResponse({
    ok: true,
    provider: "supabase_auth",
    provider_configured: Boolean(providerStatus.provider_configured),
    auth_enabled: Boolean(authContext.auth_enabled),
    bearer_token_present: Boolean(authContext.bearer_token_present),
    authorization_required: Boolean(authContext.authorization_required),
    token_validation_enabled: Boolean(authContext.token_validation_enabled),
    supabase_url_configured: Boolean(authContext.supabase_url_configured),
    supabase_anon_key_configured: Boolean(authContext.supabase_anon_key_configured),
    anonymous_requests_allowed: false,
    service_role_browser_exposure_allowed: false,
    current_recommendation: authContext.current_recommendation,
    env_presence: {
      SUPABASE_URL: Boolean(providerStatus.project_url),
      SUPABASE_ANON_KEY: Boolean(providerStatus.configured_env_vars.SUPABASE_ANON_KEY),
      SUPABASE_SERVICE_ROLE_KEY: Boolean(providerStatus.configured_env_vars.SUPABASE_SERVICE_ROLE_KEY),
      SUPABASE_DB_PASSWORD: Boolean(providerStatus.configured_env_vars.SUPABASE_DB_PASSWORD),
      DATABASE_URL: Boolean(providerStatus.configured_env_vars.DATABASE_URL),
      MVP_ENABLE_SUPABASE_REQUEST_API: Boolean(providerStatus.configured_env_vars.MVP_ENABLE_SUPABASE_REQUEST_API),
      MVP_ENABLE_REQUEST_API_WRITES: Boolean(providerStatus.configured_env_vars.MVP_ENABLE_REQUEST_API_WRITES),
      MVP_ENABLE_SUPABASE_AUTH: Boolean(providerStatus.configured_env_vars.MVP_ENABLE_SUPABASE_AUTH),
    },
    request_api_state: authContext.auth_state,
    bearer_token_present: Boolean(authContext.bearer_token_present),
  });
};
