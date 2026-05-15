const { jsonResponse, errorResponse } = require("./_shared/response");
const { buildSupabaseProviderStatus } = require("./_shared/provider_config");
const { buildAuthContext } = require("./_shared/auth_context");

function loadMigrationReadinessModel() {
  return {
    model_id: "supabase-migration-readiness-model",
    model_version: "1.0",
    project_ref: "mobvzrkcsfbumgbwvkcp",
    project_url: "https://mobvzrkcsfbumgbwvkcp.supabase.co",
    required_migrations: [
      "001_supabase_request_runtime.sql",
      "002_supabase_auth_rls_policies.sql",
    ],
    migration_apply_mode: "manual_only",
    production_apply_automatic: false,
    supabase_cli_required: true,
    rls_review_required: true,
    writes_enabled_after_migration: false,
    reads_allowed_after_auth_review: "boundary_only",
    current_recommendation: [
      "MIGRATION_READINESS_CHECK_READY",
      "MANUAL_MIGRATION_REVIEW_REQUIRED",
      "AUTHENTICATED_READS_BOUNDARY_READY",
      "WRITES_DISABLED_UNTIL_RLS_REVIEW",
      "NOT_READY_FOR_REAL_AUTOMATION",
    ],
  };
}

function loadControlledMigrationApplyModel() {
  return {
    model_id: "supabase-controlled-migration-apply-model",
    model_version: "1.0",
    project_ref: "mobvzrkcsfbumgbwvkcp",
    project_url: "https://mobvzrkcsfbumgbwvkcp.supabase.co",
    required_migrations: [
      "001_supabase_request_runtime.sql",
      "002_supabase_auth_rls_policies.sql",
    ],
    apply_mode: "controlled_cli_apply",
    migration_apply_allowed_in_this_phase: true,
    required_preflight: [
      "supabase_cli_available",
      "linked_project_ref_matches",
      "readiness_checker_passes",
      "no_secret_leaks",
      "no_broad_public_writes",
      "writes_flag_remains_false",
    ],
    forbidden: [
      "print_secrets",
      "commit_secrets",
      "expose_service_role_to_browser",
      "enable_writes",
      "automation",
    ],
    current_recommendation: [
      "CONTROLLED_MIGRATION_APPLY_READY",
      "APPLY_SCHEMA_AND_RLS_ONLY",
      "ENABLE_AUTHENTICATED_READS_ONLY",
      "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
      "NOT_READY_FOR_REAL_AUTOMATION",
    ],
  };
}

function loadPostMigrationVerificationModel() {
  return {
    model_id: "supabase-post-migration-verification-model",
    model_version: "1.0",
    required_tables: [
      "app_users",
      "app_roles",
      "requests",
      "request_lifecycle_events",
      "approvals",
      "audit_events",
      "dry_run_results",
      "no_go_flags",
    ],
    required_rls_tables: [
      "app_users",
      "app_roles",
      "requests",
      "request_lifecycle_events",
      "approvals",
      "audit_events",
      "dry_run_results",
      "no_go_flags",
    ],
    verification_mode: "schema_metadata_only",
    no_row_data_required: true,
    no_secret_output: true,
  };
}

function loadAuthenticatedReadsEnablementModel() {
  return {
    model_id: "supabase-authenticated-reads-enablement-model",
    model_version: "1.0",
    request_api_reads_target: "enabled",
    request_api_writes_target: "disabled",
    supabase_auth_target: "enabled",
    bearer_token_required: true,
    service_role_used_for_reads: false,
    anon_key_plus_user_token: true,
    current_status: "pending_env_activation",
    current_recommendation: [
      "CONTROLLED_MIGRATION_APPLY_READY",
      "AUTHENTICATED_READS_ENABLEMENT_READY",
      "REQUEST_API_READS_ENABLED_TARGET",
      "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
      "NOT_READY_FOR_REAL_AUTOMATION",
    ],
  };
}

function loadRequestReadModel() {
  return {
    model_id: "supabase-request-read-model",
    model_version: "1.0",
    endpoint: "/api/requests",
    method: "GET",
    requires_provider_configured: true,
    requires_request_api_enabled: true,
    requires_supabase_auth_enabled: true,
    requires_bearer_token: true,
    uses_service_role: false,
    uses_anon_key_with_user_bearer: true,
    returns_only_user_owned_requests: true,
    writes_enabled: false,
    current_status: "scaffold_only_boundary",
    current_recommendation: [
      "MIGRATION_READINESS_CHECK_READY",
      "MANUAL_MIGRATION_REVIEW_REQUIRED",
      "AUTHENTICATED_READS_BOUNDARY_READY",
      "WRITES_DISABLED_UNTIL_RLS_REVIEW",
      "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS",
    ],
  };
}

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
    provider: "supabase",
    migration_readiness: loadMigrationReadinessModel(),
    request_read_model: loadRequestReadModel(),
    provider_configured: Boolean(providerStatus.provider_configured),
    request_api_enabled: Boolean(providerStatus.request_api_enabled),
    auth_enabled: Boolean(authContext.auth_enabled),
    bearer_token_present: Boolean(authContext.bearer_token_present),
    controlled_migration_apply_ready: false,
    post_migration_verification_required: true,
    authenticated_reads_enablement_ready: Boolean(
      providerStatus.provider_configured &&
      providerStatus.request_api_enabled &&
      authContext.auth_enabled &&
      authContext.bearer_token_present
    ),
    writes_remain_disabled: true,
    real_automation_enabled: false,
    controlled_migration_apply_model: loadControlledMigrationApplyModel(),
    post_migration_verification_model: loadPostMigrationVerificationModel(),
    authenticated_reads_enablement_model: loadAuthenticatedReadsEnablementModel(),
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
    current_recommendation: [
      "CONTROLLED_MIGRATION_APPLY_READY",
      "APPLY_SCHEMA_AND_RLS_ONLY",
      "AUTHENTICATED_READS_ENABLEMENT_READY",
      "REQUEST_API_READS_ENABLED_TARGET",
      "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
      "NOT_READY_FOR_REAL_AUTOMATION",
    ],
  });
};
