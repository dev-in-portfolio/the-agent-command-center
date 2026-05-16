/**
 * Request Payload Validator
 * Enforces strict schema for create_request action.
 */

const ALLOWED_REQUEST_TYPES = [
  "dashboard_task",
  "backend_task",
  "product_task",
  "validation_task",
  "documentation_task",
  "operator_note"
];

const ALLOWED_PRIORITIES = ["low", "normal", "high", "urgent"];
const ALLOWED_SOURCES = ["dashboard", "api", "operator"];

const REJECTED_FIELDS = [
  "id", "user_id", "owner_id", "actor_id", "created_by",
  "status", "lifecycle_state", "approved", "executed",
  "command", "shell", "script", "token", "secret",
  "service_role", "github", "netlify", "deploy", "merge",
  "push", "pull_request", "automation"
];

/**
 * Validates the create request payload.
 * @param {object} payload 
 * @returns {object} { valid: boolean, errors: string[], data: object }
 */
function validateCreateRequestPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return { valid: false, errors: ["INVALID_PAYLOAD_TYPE"], data: null };
  }

  const errors = [];
  const validatedData = {};

  // Check for rejected fields
  for (const field of REJECTED_FIELDS) {
    if (field in payload) {
      errors.push(`FORBIDDEN_FIELD: ${field}`);
    }
  }

  // title: required, string, max 160
  if (!payload.title || typeof payload.title !== "string") {
    errors.push("MISSING_OR_INVALID_TITLE");
  } else if (payload.title.length > 160) {
    errors.push("TITLE_TOO_LONG");
  } else {
    validatedData.title = payload.title;
  }

  // summary: optional, string, max 2000
  if (payload.summary !== undefined) {
    if (typeof payload.summary !== "string") {
      errors.push("INVALID_SUMMARY_TYPE");
    } else if (payload.summary.length > 2000) {
      errors.push("SUMMARY_TOO_LONG");
    } else {
      validatedData.summary = payload.summary;
    }
  }

  // request_type: required, enum
  if (!payload.request_type || !ALLOWED_REQUEST_TYPES.includes(payload.request_type)) {
    errors.push(`INVALID_REQUEST_TYPE: ${payload.request_type}`);
  } else {
    validatedData.request_type = payload.request_type;
  }

  // priority: optional, enum
  if (payload.priority !== undefined) {
    if (!ALLOWED_PRIORITIES.includes(payload.priority)) {
      errors.push(`INVALID_PRIORITY: ${payload.priority}`);
    } else {
      validatedData.priority = payload.priority;
    }
  }

  // source: optional, enum
  if (payload.source !== undefined) {
    if (!ALLOWED_SOURCES.includes(payload.source)) {
      errors.push(`INVALID_SOURCE: ${payload.source}`);
    } else {
      validatedData.source = payload.source;
    }
  }

  // metadata: optional, object, max serialized length 5000
  if (payload.metadata !== undefined) {
    if (typeof payload.metadata !== "object") {
      errors.push("INVALID_METADATA_TYPE");
    } else {
      const serialized = JSON.stringify(payload.metadata);
      if (serialized.length > 5000) {
        errors.push("METADATA_TOO_LARGE");
      } else {
        validatedData.metadata = payload.metadata;
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? validatedData : null
  };
}

module.exports = {
  validateCreateRequestPayload
};
