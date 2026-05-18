/**
 * MVP-22: Feedback Payload Validator
 * Enforces strict schema for imported feedback packets.
 */

function validateFeedbackPayload(payload) {
  if (!payload || typeof payload !== "object") {
    throw new Error("INVALID_PAYLOAD_FORMAT");
  }

  const errors = [];

  // 1. Required Fields
  if (!payload.reviewer_persona || typeof payload.reviewer_persona !== "string") {
    errors.push("MISSING_REVIEWER_PERSONA");
  }

  // 2. Substantive Feedback Check (must have at least one text or rating field)
  const substantiveFields = [
    "reviewer_context", "strongest_parts", "confusing_parts", 
    "blockers", "trust_concerns", "suggested_next_step",
    "clarity_rating", "confidence_rating", "demo_readiness_rating", "pitchability_rating"
  ];
  const hasSubstantive = substantiveFields.some(field => payload[field] !== undefined && payload[field] !== null && payload[field] !== "");
  if (!hasSubstantive) {
    errors.push("NO_SUBSTANTIVE_FEEDBACK_PROVIDED");
  }

  // 3. Block Dangerous Fields (must not be provided by client)
  const forbidden = [
    "id", "owner_user_id", "actor_id", "user_id", "service_role", "serviceRole",
    "token", "secret", "api_key", "command", "shell", "script", "execute", 
    "approve", "deploy", "merge", "push", "automation", "created_at", "updated_at"
  ];
  forbidden.forEach(field => {
    if (payload[field] !== undefined) {
      errors.push(`FORBIDDEN_FIELD_IN_PAYLOAD: ${field}`);
    }
  });

  // 4. Rating Validation (1-5)
  const ratingFields = ["clarity_rating", "confidence_rating", "demo_readiness_rating", "pitchability_rating"];
  ratingFields.forEach(field => {
    if (payload[field] !== undefined && payload[field] !== null) {
      const val = parseInt(payload[field], 10);
      if (isNaN(val) || val < 1 || val > 5) {
        errors.push(`INVALID_RATING_VALUE: ${field}`);
      }
    }
  });

  if (errors.length > 0) {
    const err = new Error("PAYLOAD_VALIDATION_FAILED");
    err.details = errors;
    throw err;
  }

  // 5. Sanitize and Return
  return {
    reviewer_persona: String(payload.reviewer_persona).trim(),
    reviewer_context: payload.reviewer_context ? String(payload.reviewer_context).trim() : null,
    clarity_rating: payload.clarity_rating ? parseInt(payload.clarity_rating, 10) : null,
    confidence_rating: payload.confidence_rating ? parseInt(payload.confidence_rating, 10) : null,
    demo_readiness_rating: payload.demo_readiness_rating ? parseInt(payload.demo_readiness_rating, 10) : null,
    pitchability_rating: payload.pitchability_rating ? parseInt(payload.pitchability_rating, 10) : null,
    strongest_parts: payload.strongest_parts ? String(payload.strongest_parts).trim() : null,
    confusing_parts: payload.confusing_parts ? String(payload.confusing_parts).trim() : null,
    blockers: payload.blockers ? String(payload.blockers).trim() : null,
    trust_concerns: payload.trust_concerns ? String(payload.trust_concerns).trim() : null,
    suggested_next_step: payload.suggested_next_step ? String(payload.suggested_next_step).trim() : null,
    would_share: payload.would_share === true,
    raw_packet: payload.raw_packet && typeof payload.raw_packet === "object" ? payload.raw_packet : {},
    source: payload.source ? String(payload.source).trim() : "manual_import"
  };
}

module.exports = {
  validateFeedbackPayload
};
