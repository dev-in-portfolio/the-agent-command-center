const { jsonResponse, errorResponse } = require("./_shared/response");
const { buildRequestApiBoundary } = require("./_shared/provider_config");

const REQUEST_BOUNDARY_MARKERS = {
  SUPABASE_PROVIDER_NOT_CONFIGURED: "SUPABASE_PROVIDER_NOT_CONFIGURED",
  REQUEST_API_DISABLED: "REQUEST_API_DISABLED",
  REQUEST_API_WRITES_DISABLED: "REQUEST_API_WRITES_DISABLED",
};

exports.handler = async function(event) {
  const method = String(event.httpMethod || "GET").toUpperCase();
  if (method !== "GET" && method !== "POST") {
    return errorResponse("Method Not Allowed", 405);
  }

  const boundary = buildRequestApiBoundary(method);
  if (!boundary.body.error_code && REQUEST_BOUNDARY_MARKERS.SUPABASE_PROVIDER_NOT_CONFIGURED) {
    boundary.body.request_api_markers = REQUEST_BOUNDARY_MARKERS;
  }
  return jsonResponse(boundary.body, boundary.statusCode);
};
