const PROJECT_REF = "mobvzrkcsfbumgbwvkcp";
const PROJECT_URL = "https://mobvzrkcsfbumgbwvkcp.supabase.co";

const REQUIRED_ENV_NAMES = [
  "SUPABASE_ANON_KEY",
  "SUPABASE_SERVICE_ROLE_KEY",
  "SUPABASE_DB_PASSWORD",
  "DATABASE_URL",
];

const FLAG_ENV_NAMES = [
  "MVP_ENABLE_SUPABASE_REQUEST_API",
  "MVP_ENABLE_REQUEST_API_WRITES",
  "MVP_ENABLE_SUPABASE_AUTH",
];

function hasValue(value) {
  return String(value || "").trim().length > 0;
}

function isEnabled(value) {
  return String(value || "").trim().toLowerCase() === "true";
}

function missingEnvNames(env = process.env) {
  const names = [];
  for (const name of REQUIRED_ENV_NAMES) {
    if (!hasValue(env[name])) {
      names.push(name);
    }
  }
  return names;
}

function buildSupabaseProviderStatus(env = process.env) {
  const requestApiEnabled = isEnabled(env.MVP_ENABLE_SUPABASE_REQUEST_API);
  const requestApiWritesEnabled = isEnabled(env.MVP_ENABLE_REQUEST_API_WRITES);
  const supabaseAuthEnabled = isEnabled(env.MVP_ENABLE_SUPABASE_AUTH);
  const anonKeySet = hasValue(env.SUPABASE_ANON_KEY);
  const serviceRoleSet = hasValue(env.SUPABASE_SERVICE_ROLE_KEY);
  const dbPasswordSet = hasValue(env.SUPABASE_DB_PASSWORD);
  const databaseUrlSet = hasValue(env.DATABASE_URL);
  const providerConfigured =
    requestApiEnabled &&
    anonKeySet &&
    serviceRoleSet &&
    (dbPasswordSet || databaseUrlSet);

  return {
    provider: "supabase",
    project_ref: PROJECT_REF,
    project_url: PROJECT_URL,
    production_database_target: "postgres",
    production_auth_target: "supabase_auth",
    provider_configured: providerConfigured,
    request_api_enabled: requestApiEnabled,
    request_api_writes_enabled: requestApiWritesEnabled,
    service_role_required_for_admin_ops: true,
    browser_service_role_exposure_allowed: false,
    rls_required_before_production_writes: true,
    auth_uid_binding_required: true,
    current_recommendation: [
      "SUPABASE_PROVIDER_SELECTED",
      "ENV_CONFIGURATION_REQUIRED",
      "REQUEST_API_DISABLED_UNTIL_CONFIGURED",
      "REAL_AUTH_BINDING_REQUIRED",
      "NOT_READY_FOR_REAL_AUTOMATION",
      "NEXT_STEP_CONFIGURE_SUPABASE_PROJECT_AND_AUTH",
    ],
    missing_env_vars: missingEnvNames(env),
    configured_env_vars: {
      SUPABASE_ANON_KEY: anonKeySet,
      SUPABASE_SERVICE_ROLE_KEY: serviceRoleSet,
      SUPABASE_DB_PASSWORD: dbPasswordSet,
      DATABASE_URL: databaseUrlSet,
      MVP_ENABLE_SUPABASE_REQUEST_API: requestApiEnabled,
      MVP_ENABLE_REQUEST_API_WRITES: requestApiWritesEnabled,
      MVP_ENABLE_SUPABASE_AUTH: supabaseAuthEnabled,
    },
  };
}

function buildRequestApiBoundary(eventMethod, env = process.env) {
  const status = buildSupabaseProviderStatus(env);

  if (!status.provider_configured) {
    return {
      statusCode: 409,
      body: {
        ok: false,
        error_code: "SUPABASE_PROVIDER_NOT_CONFIGURED",
        request_api_state: "provider_not_configured",
        provider_status: status,
      },
    };
  }

  if (!status.request_api_enabled) {
    return {
      statusCode: 409,
      body: {
        ok: false,
        error_code: "REQUEST_API_DISABLED",
        request_api_state: "disabled_by_default",
        provider_status: status,
      },
    };
  }

  if (String(eventMethod || "GET").toUpperCase() === "POST" && !status.request_api_writes_enabled) {
    return {
      statusCode: 409,
      body: {
        ok: false,
        error_code: "REQUEST_API_WRITES_DISABLED",
        request_api_state: "writes_disabled_by_default",
        provider_status: status,
      },
    };
  }

  return {
    statusCode: 200,
    body: {
      ok: true,
      error_code: null,
      request_api_state: "REQUEST_API_BOUNDARY_ONLY",
      provider_status: status,
      note: "No Supabase network calls are executed in MVP-3.",
    },
  };
}

module.exports = {
  PROJECT_REF,
  PROJECT_URL,
  REQUIRED_ENV_NAMES,
  FLAG_ENV_NAMES,
  missingEnvNames,
  buildSupabaseProviderStatus,
  buildRequestApiBoundary,
};
