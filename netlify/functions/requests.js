const { jsonResponse, errorResponse } = require("./_shared/response");
const { buildSupabaseProviderStatus } = require("./_shared/provider_config");
const { buildAuthContext } = require("./_shared/auth_context");

const REQUEST_BOUNDARY_MARKERS = {
  SUPABASE_PROVIDER_NOT_CONFIGURED: "SUPABASE_PROVIDER_NOT_CONFIGURED",
  REQUEST_API_DISABLED: "REQUEST_API_DISABLED",
  AUTH_DISABLED_BY_DEFAULT: "AUTH_DISABLED_BY_DEFAULT",
  AUTHORIZATION_REQUIRED: "AUTHORIZATION_REQUIRED",
  AUTHENTICATED_READ_BOUNDARY_READY: "AUTHENTICATED_READ_BOUNDARY_READY",
  REQUEST_API_WRITES_DISABLED: "REQUEST_API_WRITES_DISABLED",
  RLS_POLICY_REQUIRED: "RLS_POLICY_REQUIRED",
};

exports.handler = async function(event) {
  const method = String(event.httpMethod || "GET").toUpperCase();
  if (method !== "GET" && method !== "POST") {
    return errorResponse("Method Not Allowed", 405);
  }

  const providerStatus = buildSupabaseProviderStatus();
  const authContext = buildAuthContext({
    authorizationHeader: event.headers && (event.headers.authorization || event.headers.Authorization),
    providerStatus,
  });
  const boundaryMarkers = {
    ...REQUEST_BOUNDARY_MARKERS,
    provider_configured: Boolean(providerStatus.provider_configured),
    request_api_enabled: Boolean(providerStatus.request_api_enabled),
    request_api_writes_enabled: Boolean(providerStatus.request_api_writes_enabled),
  };

  if (!providerStatus.provider_configured) {
    return jsonResponse({
      ok: false,
      error_code: REQUEST_BOUNDARY_MARKERS.SUPABASE_PROVIDER_NOT_CONFIGURED,
      request_api_state: "provider_not_configured",
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
    }, 409);
  }

  if (!providerStatus.request_api_enabled) {
    return jsonResponse({
      ok: false,
      error_code: REQUEST_BOUNDARY_MARKERS.REQUEST_API_DISABLED,
      request_api_state: "disabled_by_default",
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
    }, 409);
  }

  if (!authContext.auth_enabled) {
    return jsonResponse({
      ok: false,
      error_code: REQUEST_BOUNDARY_MARKERS.AUTH_DISABLED_BY_DEFAULT,
      request_api_state: "auth_disabled_by_default",
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
    }, 409);
  }

  if (!authContext.bearer_token_present) {
    return jsonResponse({
      ok: false,
      error_code: REQUEST_BOUNDARY_MARKERS.AUTHORIZATION_REQUIRED,
      request_api_state: "authorization_required",
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
    }, 401);
  }

  if (method === "GET") {
    return jsonResponse({
      ok: true,
      error_code: null,
      request_api_state: REQUEST_BOUNDARY_MARKERS.AUTHENTICATED_READ_BOUNDARY_READY,
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
      note: "MVP-5 keeps GET boundary-only and does not execute Supabase network calls yet.",
    });
  }

  if (method === "POST" && !providerStatus.request_api_writes_enabled) {
    return jsonResponse({
      ok: false,
      error_code: REQUEST_BOUNDARY_MARKERS.REQUEST_API_WRITES_DISABLED,
      request_api_state: "writes_disabled_by_default",
      provider_status: providerStatus,
      auth_context: authContext,
      request_api_markers: boundaryMarkers,
    }, 409);
  }

  return jsonResponse({
    ok: false,
    error_code: REQUEST_BOUNDARY_MARKERS.RLS_POLICY_REQUIRED,
    request_api_state: "rls_review_required",
    provider_status: providerStatus,
    auth_context: authContext,
    request_api_markers: boundaryMarkers,
    note: "MVP-5 keeps production writes disabled and requires RLS review before any write path is opened.",
  }, 409);
};
