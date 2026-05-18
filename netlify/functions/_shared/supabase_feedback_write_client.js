/**
 * MVP-22: Supabase Feedback Write Client (Netlify Server-Side Only)
 * Handles authenticated PostgREST inserts into external_feedback_packets.
 * Uses anon key + user bearer token only.
 * No service role usage. No update/delete.
 */

const SUPABASE_URL = process['env'].SUPABASE_URL;
const SUPABASE_ANON_KEY = process['env'].SUPABASE_ANON_KEY;

/**
 * Imports a feedback packet into Supabase.
 * Maps sanitized payload to external_feedback_packets schema.
 * @param {string} bearerToken 
 * @param {object} sanitizedPayload 
 * @param {object} authContext 
 */
async function importFeedbackPacket(bearerToken, sanitizedPayload, authContext) {
  if (!bearerToken) throw new Error("MISSING_BEARER_TOKEN");
  if (!authContext || !authContext.user) throw new Error("UNAUTHORIZED_CONTEXT");
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) throw new Error("SUPABASE_REQUEST_API_DISABLED");

  // Map payload to table schema (from 003 migration)
  // owner_user_id is derived from auth, not client payload
  const insertData = {
    ...sanitizedPayload,
    owner_user_id: authContext.user.id
  };

  const response = await fetch(`${SUPABASE_URL}/rest/v1/external_feedback_packets`, {
    method: "POST",
    headers: {
      "apikey": SUPABASE_ANON_KEY,
      "Authorization": `Bearer ${bearerToken.replace(/^Bearer\s+/i, "")}`,
      "Content-Type": "application/json",
      "Prefer": "return=representation"
    },
    body: JSON.stringify(insertData)
  });

  if (!response.ok) {
    throw new Error("SUPABASE_CREATE_FAILED");
  }

  const result = await response.json();
  return result[0];
}

module.exports = {
  importFeedbackPacket
};
