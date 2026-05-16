/**
 * Supabase Lifecycle Write Client Helper (Netlify Server-Side Only)
 * Handles real PostgREST POST inserts for lifecycle events.
 * Uses anon key + user bearer token only.
 * No service role usage. No update/delete.
 */

const crypto = require("crypto");

const SUPABASE_URL = process['env'].SUPABASE_URL;
const SUPABASE_ANON_KEY = process['env'].SUPABASE_ANON_KEY;

/**
 * Creates a new lifecycle event in Supabase.
 * Maps validated payload to request_lifecycle_events table schema.
 * @param {string} bearerToken 
 * @param {string} requestId
 * @param {object} validatedPayload 
 * @param {object} authContext 
 */
async function createLifecycleEvent(bearerToken, requestId, validatedPayload, authContext) {
  if (!bearerToken) throw new Error("MISSING_BEARER_TOKEN");
  if (!authContext || !authContext.user) throw new Error("UNAUTHORIZED_CONTEXT");
  if (!requestId) throw new Error("MISSING_REQUEST_ID");

  // Map payload to table schema (from 001 migration)
  const insertData = {
    id: crypto.randomUUID(), // Generate UUID server-side
    request_id: requestId,
    actor_id: authContext.user.id,
    event_type: validatedPayload.event_type,
    lifecycle_state: validatedPayload.lifecycle_state || null,
    message: validatedPayload.message,
    visibility: validatedPayload.visibility || "internal" // Default to internal if not provided
    // created_at handled by Postgres defaults
  };

  const response = await fetch(`${SUPABASE_URL}/rest/v1/request_lifecycle_events`, {
    method: "POST",
    headers: {
      "apikey": SUPABASE_ANON_KEY,
      "Authorization": `Bearer ${bearerToken.replace('Bearer ', '')}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    },
    body: JSON.stringify(insertData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`SUPABASE_CREATE_LIFECYCLE_EVENT_FAILED: ${error.message || response.statusText}`);
  }

  const result = await response.json();
  return result[0];
}

module.exports = {
  createLifecycleEvent
};
