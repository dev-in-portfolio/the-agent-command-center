/**
 * Lifecycle Event Payload Validator
 * Enforces strict schema for add_event action.
 */

const ALLOWED_EVENT_TYPES = [
  "operator_note",
  "validation_note",
  "status_note",
  "dry_run_note",
  "client_visible_note",
  "internal_note"
];

const ALLOWED_LIFECYCLE_STATES = [
  "request_received",
  "validated",
  "dry_run_ready",
  "review_needed",
  "waiting_on_operator",
  "blocked",
  "completed_note",
  "failed_note"
];

const ALLOWED_VISIBILITIES = ["internal", "operator", "client_visible"];

const REJECTED_FIELDS = [
  "id", "actor_id", "user_id", "owner_id", "request_owner",
  "approved", "executed", "command", "shell", "script",
  "token", "secret", "service_role", "github", "netlify",
  "deploy", "merge", "push", "pull_request", "automation",
  "approval_granted", "execute_request", "automation_started",
  "automation_executed"
];

/**
 * Validates the lifecycle event payload.
 * @param {object} payload 
 * @returns {object} { valid: boolean, errors: string[], data: object }
 */
function validateLifecycleEventPayload(payload) {
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

  // event_type: required, string, enum
  if (!payload.event_type || !ALLOWED_EVENT_TYPES.includes(payload.event_type)) {
    errors.push(`INVALID_EVENT_TYPE: ${payload.event_type}`);
  } else {
    validatedData.event_type = payload.event_type;
  }

  // message: required, string, max 2000
  if (!payload.message || typeof payload.message !== "string") {
    errors.push("MISSING_OR_INVALID_MESSAGE");
  } else if (payload.message.length > 2000) {
    errors.push("MESSAGE_TOO_LONG");
  } else {
    validatedData.message = payload.message;
  }

  // lifecycle_state: optional, enum
  if (payload.lifecycle_state !== undefined) {
    if (!ALLOWED_LIFECYCLE_STATES.includes(payload.lifecycle_state)) {
      errors.push(`INVALID_LIFECYCLE_STATE: ${payload.lifecycle_state}`);
    } else {
      validatedData.lifecycle_state = payload.lifecycle_state;
    }
  }

  // visibility: optional, enum
  if (payload.visibility !== undefined) {
    if (!ALLOWED_VISIBILITIES.includes(payload.visibility)) {
      errors.push(`INVALID_VISIBILITY: ${payload.visibility}`);
    } else {
      validatedData.visibility = payload.visibility;
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
  validateLifecycleEventPayload
};
