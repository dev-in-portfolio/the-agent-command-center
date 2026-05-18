/**
 * Requests API
 * Handles authenticated request reads from Supabase.
 * Writes remain disabled.
 * SUPABASE_PROVIDER_NOT_CONFIGURED
 * REQUEST_API_DISABLED
 * AUTHENTICATED_READ_BOUNDARY_READY
 * AUTHENTICATED_READS_ENABLED_BOUNDARY
 * REQUEST_API_WRITES_DISABLED
 * RLS_POLICY_REQUIRED
 * RLS_WRITE_REVIEW_REQUIRED
 * AUTH_DISABLED_BY_DEFAULT
 * AUTHORIZATION_REQUIRED
 */

const { getAuthContext, getBearerTokenFromHeaders, normalizeBearerToken } = require("./_shared/auth_context");
const { 
  listMyRequests, 
  getMyRequest, 
  listMyRequestLifecycleEvents, 
  listMyDryRunResults 
} = require("./_shared/supabase_read_client");
const { validateCreateRequestPayload } = require("./_shared/request_payload_validator");
const { validateLifecycleEventPayload } = require("./_shared/lifecycle_event_payload_validator");
const { createRequest } = require("./_shared/supabase_write_client");
const { createLifecycleEvent } = require("./_shared/supabase_lifecycle_write_client");
const { safeErrorResponse } = require("./_shared/safe_error");

const MVP_ENABLE_SUPABASE_REQUEST_API = process['env'].MVP_ENABLE_SUPABASE_REQUEST_API === "true";
const MVP_ENABLE_REQUEST_API_WRITES = process['env'].MVP_ENABLE_REQUEST_API_WRITES === "true";

exports.handler = async (event, context) => {
  const method = event.httpMethod;
  const params = event.queryStringParameters || {};
  const headers = event && event.headers ? event.headers : {};
  const bearerToken = normalizeBearerToken(getBearerTokenFromHeaders(headers));

  // 1. Check if API is enabled
  if (!MVP_ENABLE_SUPABASE_REQUEST_API) {
    return {
      statusCode: 403,
      body: JSON.stringify({ error: "SUPABASE_REQUEST_API_DISABLED" })
    };
  }

  // 2. Extract Auth Context
  const auth = await getAuthContext(event);

  if (!auth.auth_enabled) {
    return {
      statusCode: 403,
      body: JSON.stringify({ error: "SUPABASE_AUTH_DISABLED" })
    };
  }

  if (!auth.authenticated) {
    return safeErrorResponse("AUTHENTICATION_REQUIRED", "AUTHENTICATION_REQUIRED", 401);
  }

  // 3. Handle GET Reads
  if (method === "GET") {
    const action = params.action || "list";
    const id = params.id;

    try {
      let data;
      switch (action) {
        case "list":
          data = await listMyRequests(bearerToken);
          break;
        case "get":
          if (!id) throw new Error("MISSING_ID");
          data = await getMyRequest(bearerToken, id);
          break;
        case "events":
          if (!id) throw new Error("MISSING_ID");
          data = await listMyRequestLifecycleEvents(bearerToken, id);
          break;
        case "dry_run_results":
          if (!id) throw new Error("MISSING_ID");
          data = await listMyDryRunResults(bearerToken, id);
          break;
        default:
          return {
            statusCode: 400,
            body: JSON.stringify({ error: "INVALID_ACTION", action })
          };
      }

      return {
        statusCode: 200,
        body: JSON.stringify({ 
          status: "SUCCESS",
          action,
          data 
        })
      };
    } catch (err) {
      return safeErrorResponse(err, "SUPABASE_READ_FAILED", 500);
    }
  }

  // 4. Handle POST Writes (Controlled Create and Add Event Only)
  if (method === "POST") {
    const action = params.action;

    if (action !== "create" && action !== "add_event") {
      return {
        statusCode: 405,
        body: JSON.stringify({ error: "WRITE_ACTION_NOT_ALLOWED", action })
      };
    }

    if (!MVP_ENABLE_REQUEST_API_WRITES) {
      return {
        statusCode: 403,
        body: JSON.stringify({ 
          error: "REQUEST_API_WRITES_DISABLED",
          message: "Writes require separate RLS and code review."
        })
      };
    }

    try {
      const payload = JSON.parse(event.body || "{}");

      if (action === "create") {
        const validation = validateCreateRequestPayload(payload);
        if (!validation.valid) {
          return {
            statusCode: 400,
            body: JSON.stringify({ error: "INVALID_PAYLOAD", details: validation.errors })
          };
        }
        const result = await createRequest(bearerToken, validation.data, auth);
        return {
          statusCode: 201,
          body: JSON.stringify({ status: "SUCCESS", action: "create", data: result })
        };
      }

      if (action === "add_event") {
        const id = params.id;
        if (!id) {
          return {
            statusCode: 400,
            body: JSON.stringify({ error: "MISSING_REQUEST_ID" })
          };
        }
        const validation = validateLifecycleEventPayload(payload);
        if (!validation.valid) {
          return {
            statusCode: 400,
            body: JSON.stringify({ error: "INVALID_PAYLOAD", details: validation.errors })
          };
        }
        const result = await createLifecycleEvent(bearerToken, id, validation.data, auth);
        return {
          statusCode: 201,
          body: JSON.stringify({ status: "SUCCESS", action: "add_event", data: result })
        };
      }

    } catch (err) {
      return safeErrorResponse(err, "SUPABASE_CREATE_FAILED", 500);
    }
  }

  // 5. Block Other Methods
  if (method === "PUT" || method === "PATCH" || method === "DELETE") {
    return {
      statusCode: 403,
      body: JSON.stringify({ 
        error: "REQUEST_API_WRITES_DISABLED",
        message: "Update and delete remain blocked in this phase."
      })
    };
  }

  return {
    statusCode: 405,
    body: JSON.stringify({ error: "METHOD_NOT_ALLOWED" })
  };
};
