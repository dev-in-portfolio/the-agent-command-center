/**
 * Supabase Read Client Helper (Netlify Server-Side Only)
 * Handles real PostgREST GET reads and token validation.
 * Uses anon key + user bearer token only.
 * No service role usage. No writes.
 */

const SUPABASE_URL = process['env'].SUPABASE_URL;
const SUPABASE_ANON_KEY = process['env'].SUPABASE_ANON_KEY;

/**
 * Validates a Supabase user token against the auth user endpoint.
 * @param {string} bearerToken 
 * @returns {Promise<object>} User id/email if valid.
 */
async function validateSupabaseUserToken(bearerToken) {
  if (!bearerToken) throw new Error("MISSING_BEARER_TOKEN");
  
  const response = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    method: "GET",
    headers: {
      "apikey": SUPABASE_ANON_KEY,
      "Authorization": `Bearer ${bearerToken.replace('Bearer ', '')}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`AUTH_VALIDATION_FAILED: ${error.message || response.statusText}`);
  }

  const user = await response.json();
  return {
    id: user.id,
    email: user.email
  };
}

/**
 * Common GET helper for Supabase PostgREST.
 */
async function supabaseGet(path, bearerToken, options = {}) {
  const { limit = 25, select = "*" } = options;
  const url = new URL(`${SUPABASE_URL}/rest/v1/${path}`);
  url.searchParams.set("select", select);
  url.searchParams.set("limit", Math.min(limit, 100).toString());

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      "apikey": SUPABASE_ANON_KEY,
      "Authorization": `Bearer ${bearerToken.replace('Bearer ', '')}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`SUPABASE_READ_FAILED: ${error.message || response.statusText}`);
  }

  return await response.json();
}

/**
 * List requests owned by the authenticated user.
 * RLS enforces user ownership.
 */
async function listMyRequests(bearerToken, options = {}) {
  return await supabaseGet("requests", bearerToken, options);
}

/**
 * Get a single request by ID.
 * RLS enforces user ownership.
 */
async function getMyRequest(bearerToken, requestId) {
  const result = await supabaseGet(`requests?id=eq.${requestId}`, bearerToken, { limit: 1 });
  return result[0] || null;
}

/**
 * List lifecycle events for a specific request.
 * RLS enforces request ownership via requests table join.
 */
async function listMyRequestLifecycleEvents(bearerToken, requestId) {
  return await supabaseGet(`request_lifecycle_events?request_id=eq.${requestId}`, bearerToken);
}

/**
 * List dry run results for a specific request.
 * RLS enforces request ownership via requests table join.
 */
async function listMyDryRunResults(bearerToken, requestId) {
  return await supabaseGet(`dry_run_results?request_id=eq.${requestId}`, bearerToken);
}

module.exports = {
  validateSupabaseUserToken,
  listMyRequests,
  getMyRequest,
  listMyRequestLifecycleEvents,
  listMyDryRunResults
};
