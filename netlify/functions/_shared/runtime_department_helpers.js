const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const SUBDIVISION_GROUPS = [
  { prefix: "intake", label: "Intake", description: "Controlled intake and triage subdivision." },
  { prefix: "validation", label: "Validation", description: "Controlled validation and readiness subdivision." },
  { prefix: "audit", label: "Audit", description: "Audit visibility and recordkeeping subdivision." },
  { prefix: "approval", label: "Approval", description: "Approval review and decision subdivision." },
  { prefix: "dry_run", label: "Dry Run", description: "Dry-run and preview subdivision." },
  { prefix: "monitoring", label: "Monitoring", description: "Monitoring and readiness tracking subdivision." },
  { prefix: "safety", label: "Safety", description: "Safety boundary and kill-switch subdivision." },
  { prefix: "registry", label: "Registry", description: "Registry and roster verification subdivision." },
  { prefix: "review", label: "Review", description: "Human review and QA subdivision." },
  { prefix: "reporting", label: "Reporting", description: "Reporting and summary subdivision." },
];

const ALLOWED_RUNTIME_SUBDIVISIONS = SUBDIVISION_GROUPS.map((group, index) => ({
  subdivision_id: `${group.prefix}_subdivision`,
  subdivision_name: `${group.label} Subdivision`,
  subdivision_order: index + 1,
  subdivision_description: group.description,
}));

const ALLOWED_RUNTIME_LANES = (() => {
  const lanes = [];
  let laneOrder = 1;
  for (const subdivision of ALLOWED_RUNTIME_SUBDIVISIONS) {
    const prefix = subdivision.subdivision_id.replace("_subdivision", "");
    const label = subdivision.subdivision_name.replace(" Subdivision", "");
    for (let laneIndex = 1; laneIndex <= 10; laneIndex += 1) {
      lanes.push({
        runtime_lane_id: `${prefix}_lane_${String(laneIndex).padStart(3, "0")}`,
        runtime_lane_name: `${label} Lane ${String(laneIndex).padStart(3, "0")}`,
        runtime_lane_order: laneOrder++,
        runtime_lane_index: laneIndex,
        runtime_subdivision_id: subdivision.subdivision_id,
        runtime_subdivision_name: subdivision.subdivision_name,
        runtime_subdivision_order: subdivision.subdivision_order,
      });
    }
  }
  return lanes;
})();

const ALLOWED_RUNTIME_STATUS = new Set([
  "unmapped",
  "mapped_readonly",
  "readiness_review",
  "eligible_for_supervised_runtime",
  "blocked",
  "disabled",
]);

const ALLOWED_ASSIGNMENT_STATUS = new Set([
  "mapped_readonly",
  "readiness_review",
  "eligible",
  "blocked",
  "disabled",
]);

function isConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY);
}

function jsonResponse(statusCode, data, mode = "mvp59-1777-department-runtime-mapping") {
  return {
    statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-agent-command-center-mode": mode,
    },
    body: JSON.stringify(data, null, 2),
  };
}

function backendUnavailable(message = "Runtime department backend is not configured.") {
  return jsonResponse(503, {
    ok: false,
    error: message,
  });
}

function text(value, maxLength) {
  return String(value == null ? "" : value).trim().slice(0, maxLength);
}

function parseBody(event, maxLength = 48000) {
  const raw = event && typeof event.body === "string" ? event.body : "";
  if (raw.length > maxLength) {
    throw new Error("PAYLOAD_TOO_LARGE");
  }
  return raw ? JSON.parse(raw) : {};
}

function supabaseHeaders(extra = {}) {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
    ...extra,
  };
}

async function supabaseRequest(method, path, body, extraHeaders = {}) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers: supabaseHeaders(extraHeaders),
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const bodyText = await response.text();
  const parsed = bodyText ? JSON.parse(bodyText) : null;

  if (!response.ok) {
    const error = new Error(parsed && parsed.message ? parsed.message : response.statusText);
    error.payload = parsed;
    error.status = response.status;
    throw error;
  }

  return parsed;
}

function supabaseGet(path) {
  return supabaseRequest("GET", path);
}

function supabasePost(path, body, extraHeaders = {}) {
  return supabaseRequest("POST", path, body, extraHeaders);
}

function supabasePatch(path, body, extraHeaders = {}) {
  return supabaseRequest("PATCH", path, body, extraHeaders);
}

function supabaseDelete(path, extraHeaders = {}) {
  return supabaseRequest("DELETE", path, undefined, extraHeaders);
}

function toConfigObject(rows) {
  return Object.fromEntries((rows || []).map((row) => [row.key, row.value]));
}

function normalizeStatus(value) {
  return text(value, 80).toLowerCase();
}

function normalizeBoolean(value) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  const normalized = text(value, 12).toLowerCase();
  return normalized === "true" || normalized === "1" || normalized === "yes";
}

function normalizeNumber(value, fallback = 0, min = 0, max = Number.POSITIVE_INFINITY) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.min(Math.max(Math.trunc(parsed), min), max);
}

function laneById(runtimeLaneId) {
  const key = text(runtimeLaneId, 80);
  return ALLOWED_RUNTIME_LANES.find((lane) => lane.runtime_lane_id === key) || null;
}

function subdivisionById(runtimeSubdivisionId) {
  const key = text(runtimeSubdivisionId, 80);
  return ALLOWED_RUNTIME_SUBDIVISIONS.find((subdivision) => subdivision.subdivision_id === key) || null;
}

function isApprovedLane(runtimeLaneId, runtimeSubdivisionId) {
  const lane = laneById(runtimeLaneId);
  if (!lane) return false;
  if (!runtimeSubdivisionId) return true;
  return lane.runtime_subdivision_id === text(runtimeSubdivisionId, 80);
}

function buildRollupSnapshot(departments, config = {}) {
  const totalDepartments = (departments || []).length;
  const mappedDepartments = (departments || []).filter((department) => department.runtime_status !== "unmapped").length;
  const readinessReviewDepartments = (departments || []).filter((department) => department.runtime_status === "readiness_review").length;
  const eligibleDepartments = (departments || []).filter((department) => department.runtime_status === "eligible_for_supervised_runtime").length;
  const blockedDepartments = (departments || []).filter((department) => department.runtime_status === "blocked").length;
  const disabledDepartments = (departments || []).filter((department) => department.runtime_status === "disabled").length;
  const totalRegisteredAgents = (departments || []).reduce((sum, department) => sum + Number(department.registered_agent_count || 0), 0);

  return {
    total_departments: totalDepartments || 1777,
    mapped_departments: mappedDepartments,
    readiness_review_departments: readinessReviewDepartments,
    eligible_departments: eligibleDepartments,
    blocked_departments: blockedDepartments,
    disabled_departments: disabledDepartments,
    total_registered_agents: Number(config.total_registered_agents || totalRegisteredAgents || 47979),
    live_runtime_agents_enabled: Number(config.live_runtime_agents_enabled || 0),
    full_47979_activation_blocked: true,
    command_execution_enabled: false,
    deploy_execution_enabled: false,
    rollback_execution_enabled: false,
    alert_sending_enabled: false,
    source: "mvp59_department_runtime_mapping",
  };
}

function enrichDepartmentRecords(departments, assignments, notes, events) {
  const assignmentMap = new Map((assignments || []).map((assignment) => [assignment.department_id, assignment]));
  const noteBuckets = new Map();
  const eventBuckets = new Map();

  for (const note of notes || []) {
    if (!note || !note.department_id) continue;
    const bucket = noteBuckets.get(note.department_id) || { count: 0, latest: null };
    bucket.count += 1;
    if (!bucket.latest || new Date(note.created_at || 0) > new Date(bucket.latest.created_at || 0)) {
      bucket.latest = note;
    }
    noteBuckets.set(note.department_id, bucket);
  }

  for (const event of events || []) {
    if (!event || !event.department_id) continue;
    const bucket = eventBuckets.get(event.department_id) || { count: 0, latest: null };
    bucket.count += 1;
    if (!bucket.latest || new Date(event.created_at || 0) > new Date(bucket.latest.created_at || 0)) {
      bucket.latest = event;
    }
    eventBuckets.set(event.department_id, bucket);
  }

  return (departments || []).map((department) => {
    const assignment = assignmentMap.get(department.department_id) || null;
    const noteBucket = noteBuckets.get(department.department_id) || { count: 0, latest: null };
    const eventBucket = eventBuckets.get(department.department_id) || { count: 0, latest: null };
    const lane = assignment ? laneById(assignment.runtime_lane_id) : null;
    const subdivision = assignment ? subdivisionById(assignment.runtime_subdivision_id || (lane && lane.runtime_subdivision_id)) : null;

    return {
      ...department,
      mapped_runtime_lane_id: assignment ? assignment.runtime_lane_id : null,
      mapped_runtime_lane_name: lane ? lane.runtime_lane_name : null,
      mapped_runtime_subdivision_id: assignment ? assignment.runtime_subdivision_id || null : null,
      mapped_runtime_subdivision_name: subdivision ? subdivision.subdivision_name : null,
      mapped_agent_capacity: assignment ? Number(assignment.mapped_agent_capacity || 0) : 0,
      assignment_status: assignment ? assignment.assignment_status : "mapped_readonly",
      notes_count: noteBucket.count,
      last_readiness_update: noteBucket.latest ? noteBucket.latest.created_at : null,
      audit_status: eventBucket.count > 0 ? "audited" : "no_audit_events",
      events_count: eventBucket.count,
      latest_event_type: eventBucket.latest ? eventBucket.latest.event_type : null,
      latest_event_at: eventBucket.latest ? eventBucket.latest.created_at : null,
    };
  });
}

module.exports = {
  ALLOWED_ASSIGNMENT_STATUS,
  ALLOWED_RUNTIME_LANES,
  ALLOWED_RUNTIME_STATUS,
  ALLOWED_RUNTIME_SUBDIVISIONS,
  backendUnavailable,
  buildRollupSnapshot,
  enrichDepartmentRecords,
  isApprovedLane,
  isConfigured,
  jsonResponse,
  laneById,
  normalizeBoolean,
  normalizeNumber,
  normalizeStatus,
  parseBody,
  subdivisionById,
  supabaseDelete,
  supabaseGet,
  supabasePatch,
  supabasePost,
  supabaseRequest,
  text,
  toConfigObject,
};
