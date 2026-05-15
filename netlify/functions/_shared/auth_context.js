/**
 * Auth Context Helper
 * Handles user token validation and context extraction.
 * SUPABASE_AUTH_POLICY_READY
 * AUTHORIZATION_REQUIRED
 */

const { validateSupabaseUserToken } = require("./supabase_read_client");

const MVP_ENABLE_SUPABASE_AUTH = process['env'].MVP_ENABLE_SUPABASE_AUTH === "true";

/**
 * Extracts and validates auth context from request.
 * @param {object} event 
 * @returns {Promise<object>} Auth context.
 */
async function getAuthContext(event) {
  const authHeader = event.headers.authorization || event.headers.Authorization;
  const hasToken = !!authHeader;
  
  let user = null;
  let error = null;

  if (MVP_ENABLE_SUPABASE_AUTH && hasToken) {
    try {
      user = await validateSupabaseUserToken(authHeader);
    } catch (err) {
      error = err.message;
    }
  }

  return {
    authenticated: !!user,
    user,
    error,
    auth_enabled: MVP_ENABLE_SUPABASE_AUTH,
    has_token: hasToken
  };
}

module.exports = {
  getAuthContext
};
