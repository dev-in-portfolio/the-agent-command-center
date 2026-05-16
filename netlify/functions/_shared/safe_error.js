/**
 * Safe Error Helper
 * Maps internal errors to safe, user-facing error codes and messages.
 * Prevents leakage of tokens, env values, and internal stack traces.
 */

const SAFE_ERROR_MAP = {
  "MISSING_BEARER_TOKEN": {
    code: "MISSING_BEARER_TOKEN",
    message: "Authentication token is missing from the request."
  },
  "UNAUTHORIZED_CONTEXT": {
    code: "UNAUTHORIZED_CONTEXT",
    message: "Valid authentication context is required for this action."
  },
  "MISSING_REQUEST_ID": {
    code: "MISSING_REQUEST_ID",
    message: "A request ID is required for this action."
  },
  "MISSING_ID": {
    code: "MISSING_ID",
    message: "An ID is required for this action."
  },
  "INVALID_PAYLOAD": {
    code: "INVALID_PAYLOAD",
    message: "The provided payload did not pass schema validation."
  },
  "INVALID_ACTION": {
    code: "INVALID_ACTION",
    message: "The requested action is not supported."
  },
  "WRITE_ACTION_NOT_ALLOWED": {
    code: "WRITE_ACTION_NOT_ALLOWED",
    message: "The requested write action is not allowed."
  },
  "REQUEST_API_WRITES_DISABLED": {
    code: "REQUEST_API_WRITES_DISABLED",
    message: "Writes are currently disabled for this endpoint."
  },
  "SUPABASE_REQUEST_API_DISABLED": {
    code: "SUPABASE_REQUEST_API_DISABLED",
    message: "The request API is currently disabled."
  },
  "SUPABASE_AUTH_DISABLED": {
    code: "SUPABASE_AUTH_DISABLED",
    message: "Authentication is currently disabled."
  },
  "AUTHENTICATION_REQUIRED": {
    code: "AUTHENTICATION_REQUIRED",
    message: "Valid authentication is required to access this resource."
  },
  "READ_SCHEMA_MISMATCH": {
    code: "READ_SCHEMA_MISMATCH",
    message: "A schema mismatch occurred during read."
  },
  "CREATE_SCHEMA_MISMATCH": {
    code: "CREATE_SCHEMA_MISMATCH",
    message: "A schema mismatch occurred during creation."
  },
  "LIFECYCLE_EVENT_SCHEMA_MISMATCH": {
    code: "LIFECYCLE_EVENT_SCHEMA_MISMATCH",
    message: "A schema mismatch occurred during event creation."
  },
  "RLS_DENIED_OR_NOT_FOUND": {
    code: "RLS_DENIED_OR_NOT_FOUND",
    message: "The requested resource was not found or access is denied."
  },
  "SUPABASE_READ_FAILED": {
    code: "SUPABASE_READ_FAILED",
    message: "Failed to read data from the provider."
  },
  "SUPABASE_CREATE_REQUEST_FAILED": {
    code: "SUPABASE_CREATE_REQUEST_FAILED",
    message: "Failed to create the request."
  },
  "SUPABASE_CREATE_LIFECYCLE_EVENT_FAILED": {
    code: "SUPABASE_CREATE_LIFECYCLE_EVENT_FAILED",
    message: "Failed to create the lifecycle event."
  },
  "UNKNOWN_SAFE_SERVER_ERROR": {
    code: "UNKNOWN_SAFE_SERVER_ERROR",
    message: "An unexpected server error occurred."
  }
};

/**
 * Returns a safe error code based on the raw error message.
 */
function safeErrorCode(error, fallbackCode = "UNKNOWN_SAFE_SERVER_ERROR") {
  if (!error) return fallbackCode;
  
  const msg = typeof error === 'string' ? error : (error.message || "");
  
  for (const key of Object.keys(SAFE_ERROR_MAP)) {
    if (msg.includes(key)) {
      return key;
    }
  }
  
  // Additional specific mappings for common generic errors
  if (msg.includes("PGRST116") || msg.includes("row level security")) {
      return "RLS_DENIED_OR_NOT_FOUND";
  }
  
  return fallbackCode;
}

/**
 * Returns a generic safe error message for a given code.
 */
function sanitizeErrorMessage(code) {
  const mapping = SAFE_ERROR_MAP[code];
  return mapping ? mapping.message : SAFE_ERROR_MAP["UNKNOWN_SAFE_SERVER_ERROR"].message;
}

/**
 * Constructs a fully safe error response object.
 */
function safeErrorResponse(error, fallbackCode = "UNKNOWN_SAFE_SERVER_ERROR", statusCode = 500) {
  const code = safeErrorCode(error, fallbackCode);
  const message = sanitizeErrorMessage(code);
  
  // Safe internal logging of just the code, never the raw error or token
  // console.error(`[API_ERROR] ${code}`);

  return {
    statusCode,
    body: JSON.stringify({
      error: code,
      message: message,
      request_safe: true
    })
  };
}

module.exports = {
  safeErrorResponse,
  safeErrorCode,
  sanitizeErrorMessage,
  UNKNOWN_SAFE_SERVER_ERROR: "UNKNOWN_SAFE_SERVER_ERROR"
};
