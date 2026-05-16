/**
 * Supabase Write Client Helper (Netlify Server-Side Only)
 * Handles real PostgREST POST inserts.
 * Uses anon key + user bearer token only.
 * No service role usage. No update/delete.
 */

const crypto = require("crypto");

const SUPABASE_URL = process['env'].SUPABASE_URL;
const SUPABASE_ANON_KEY = process['env'].SUPABASE_ANON_KEY;

/**
 * Creates a new request in Supabase.
 * Maps validated payload to requests table schema.
 * @param {string} bearerToken 
 * @param {object} validatedPayload 
 * @param {object} authContext 
 */
async function createRequest(bearerToken, validatedPayload, authContext) {
  if (!bearerToken) throw new Error("MISSING_BEARER_TOKEN");
  if (!authContext || !authContext.user) throw new Error("UNAUTHORIZED_CONTEXT");

  // Map payload to table schema (from 001 migration)
  const insertData = {
    id: crypto.randomUUID(), // Generate UUID server-side as 001 didn't specify default
    actor_id: authContext.user.id,
    actor_role: "viewer", // Default as per 001
    title: validatedPayload.title,
    intent: validatedPayload.summary || "No summary provided",
    requested_action: validatedPayload.request_type,
    lifecycle_state: "request_received" // Default as per 001
    // created_at and updated_at handled by Postgres defaults
  };

  const response = await fetch(`${SUPABASE_URL}/rest/v1/requests`, {
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
    throw new Error(`SUPABASE_CREATE_FAILED: ${error.message || response.statusText}`);
  }

  const result = await response.json();
  return result[0];
}

module.exports = {
  createRequest
};
