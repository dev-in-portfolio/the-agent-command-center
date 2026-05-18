/**
 * MVP-22: Feedback API Endpoint
 * Handles controlled authenticated feedback imports.
 * Strictly gated by feature flag.
 */

const { getAuthContext, getBearerTokenFromHeaders, normalizeBearerToken } = require("./_shared/auth_context");
const { validateFeedbackPayload } = require("./_shared/feedback_payload_validator");
const { importFeedbackPacket } = require("./_shared/supabase_feedback_write_client");
const { listFeedbackPackets, getFeedbackPacket } = require("./_shared/supabase_feedback_read_client");
const { safeErrorResponse } = require("./_shared/safe_error");

const MVP_ENABLE_FEEDBACK_PERSISTENCE = process['env'].MVP_ENABLE_FEEDBACK_PERSISTENCE === "true";

exports.handler = async (event, context) => {
  const method = event.httpMethod;
  const params = event.queryStringParameters || {};
  const headers = event && event.headers ? event.headers : {};
  const authHeader = getBearerTokenFromHeaders(headers);
  const bearerToken = normalizeBearerToken(authHeader);

  // 1. Handle POST Import (Gated)
  if (method === "POST") {
    const action = params.action;

    if (action !== "import") {
      return {
        statusCode: 405,
        body: JSON.stringify({ error: "WRITE_ACTION_NOT_ALLOWED", action })
      };
    }

    // GATED BY FEATURE FLAG
    if (!MVP_ENABLE_FEEDBACK_PERSISTENCE) {
      return {
        statusCode: 403,
        body: JSON.stringify({ 
          error: "FEEDBACK_PERSISTENCE_DISABLED",
          message: "Feedback storage is currently disabled by feature flag."
        })
      };
    }

    // REQUIRE AUTH
    const auth = await getAuthContext(event);
    if (!auth.authenticated) {
      return safeErrorResponse("AUTHENTICATION_REQUIRED", "AUTHENTICATION_REQUIRED", 401);
    }

    try {
      const payload = JSON.parse(event.body || "{}");
      
      // VALIDATE PAYLOAD
      const sanitized = validateFeedbackPayload(payload);

      // PERFORM INSERT (using auth context for owner_user_id)
      const result = await importFeedbackPacket(bearerToken, sanitized, auth);

      return {
        statusCode: 201,
        body: JSON.stringify({ 
          status: "SUCCESS", 
          action: "import", 
          data: result 
        })
      };

    } catch (err) {
      // Map validation or Supabase errors to safe responses
      if (err.message === "PAYLOAD_VALIDATION_FAILED") {
        return {
          statusCode: 400,
          body: JSON.stringify({ 
            error: "INVALID_PAYLOAD", 
            details: err.details 
          })
        };
      }
      return safeErrorResponse(err, "SUPABASE_CREATE_FAILED", 500);
    }
  }

  // 2. Handle GET Actions
  if (method === "GET") {
    const action = params.action || "status";
    
    if (action === "status") {
      return {
        statusCode: 200,
        body: JSON.stringify({
          status: "SUCCESS",
          endpoint: "feedback",
          persistence_gate: MVP_ENABLE_FEEDBACK_PERSISTENCE ? "ENABLED" : "DISABLED",
          write_ready: MVP_ENABLE_FEEDBACK_PERSISTENCE
        })
      };
    }
    
    if (action === "list" || action === "get") {
      const authRead = await getAuthContext(event);
      if (!authRead.authenticated) {
        return safeErrorResponse("AUTHENTICATION_REQUIRED", "AUTHENTICATION_REQUIRED", 401);
      }
      
      if (action === "list") {
        const result = await listFeedbackPackets(bearerToken);
        if (!result.success) {
          return safeErrorResponse(result.error, "SUPABASE_READ_FAILED", result.status || 500);
        }
        return { statusCode: 200, body: JSON.stringify({ status: "SUCCESS", data: result.data }) };
      }
      
      if (action === "get") {
        const result = await getFeedbackPacket(bearerToken, params.id);
        if (!result.success) {
          return safeErrorResponse(result.error, "SUPABASE_READ_FAILED", result.status || 500);
        }
        return { statusCode: 200, body: JSON.stringify({ status: "SUCCESS", data: result.data }) };
      }
    }

    return {
      statusCode: 400,
      body: JSON.stringify({ error: "INVALID_ACTION", action })
    };
  }

  // 3. Block Other Methods
  return {
    statusCode: 405,
    body: JSON.stringify({ error: "METHOD_NOT_ALLOWED" })
  };
};
