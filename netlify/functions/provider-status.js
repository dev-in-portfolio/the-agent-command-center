const { jsonResponse, errorResponse } = require("./_shared/response");
const { buildSupabaseProviderStatus } = require("./_shared/provider_config");

const PROVIDER_STATUS_MARKER = "provider_configured";

exports.handler = async function(event) {
  if (event.httpMethod !== "GET") {
    return errorResponse("Method Not Allowed", 405);
  }

  const status = buildSupabaseProviderStatus();
  return jsonResponse({
    ...status,
    status_marker: PROVIDER_STATUS_MARKER,
  });
};
