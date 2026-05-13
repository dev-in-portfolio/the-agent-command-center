/**
 * Shared response helpers for read-only backend foundation
 * Phase 4A - No external dependencies, no secrets, no filesystem mutation
 */

const HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
  'x-agent-command-center-mode': 'read-only-backend-foundation'
};

exports.jsonResponse = (data, statusCode = 200) => {
  return {
    statusCode,
    headers: HEADERS,
    body: JSON.stringify(data, null, 2)
  };
};

exports.errorResponse = (message, statusCode = 400) => {
  return exports.jsonResponse({
    ok: false,
    error: message,
    service: "the-agent-command-center-backend",
    phase: "Phase 4A"
  }, statusCode);
};
