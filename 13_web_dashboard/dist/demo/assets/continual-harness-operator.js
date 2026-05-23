(function () {
  const ENDPOINTS = {
    status: "/.netlify/functions/continual-harness-operator-status",
    createRunPlan: "/.netlify/functions/continual-harness-create-run-plan",
    validateRunPlan: "/.netlify/functions/continual-harness-validate-run-plan",
    executeOperation: "/.netlify/functions/continual-harness-execute-allowlisted-operation",
    stop: "/.netlify/functions/continual-harness-stop",
  };

  const state = {
    backendConfigured: false,
    session: null,
    permissionScopes: { enabled: [], blocked: [] },
    allowlistedOperations: [],
    runPlans: [],
    operatorEvents: [],
    readinessNotes: [],
    circuitBreaker: { breaker_status: "clear" },
    selectedRunPlanId: "",
    message: "Loading Continual Harness operator status...",
  };

  const el = {
    statusMessage: document.getElementById("statusMessage"),
    backendState: document.getElementById("backendState"),
    sessionState: document.getElementById("sessionState"),
    modeState: document.getElementById("modeState"),
    enabledScopesState: document.getElementById("enabledScopesState"),
    blockedScopesState: document.getElementById("blockedScopesState"),
    circuitBreakerState: document.getElementById("circuitBreakerState"),
    executionFlagsState: document.getElementById("executionFlagsState"),
    runPlansState: document.getElementById("runPlansState"),
    validationState: document.getElementById("validationState"),
    approvalState: document.getElementById("approvalState"),
    executionStatusState: document.getElementById("executionStatusState"),
    permissionsBody: document.getElementById("permissionsBody"),
    operationsBody: document.getElementById("operationsBody"),
    runPlansBody: document.getElementById("runPlansBody"),
    eventsBody: document.getElementById("eventsBody"),
    notesBody: document.getElementById("notesBody"),
    refreshButton: document.getElementById("refreshButton"),
    exportButton: document.getElementById("exportButton"),
    stopButton: document.getElementById("stopButton"),
    createPlanForm: document.getElementById("createPlanForm"),
    planTitle: document.getElementById("planTitle"),
    planScope: document.getElementById("planScope"),
    planOperation: document.getElementById("planOperation"),
    planBody: document.getElementById("planBody"),
    validateButton: document.getElementById("validateButton"),
    executeButton: document.getElementById("executeButton"),
    planSelect: document.getElementById("planSelect"),
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function fmtDate(value) {
    if (!value) return "n/a";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "n/a";
    return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short", hour12: false }).format(date);
  }

  function requestJson(url, options) {
    return fetch(url, {
      ...(options || {}),
      headers: {
        "content-type": "application/json",
        ...((options && options.headers) || {}),
      },
    });
  }

  function setMessage(message) {
    state.message = message;
    el.statusMessage.textContent = message;
  }

  function safeParseJson(value) {
    const raw = String(value || "").trim();
    if (!raw) return {};
    try {
      return JSON.parse(raw);
    } catch {
      return { raw };
    }
  }

  function renderStatus() {
    el.backendState.textContent = state.backendConfigured ? "Configured" : "Not configured";
    el.sessionState.textContent = state.session ? `${state.session.status} · ${state.session.component_version || "v5.0.0"}` : "No session";
    el.modeState.textContent = state.session ? state.session.mode || "operator_mode" : "operator_mode";
    el.enabledScopesState.textContent = state.permissionScopes.enabled.join(", ") || "none";
    el.blockedScopesState.textContent = state.permissionScopes.blocked.join(", ") || "none";
    el.circuitBreakerState.textContent = state.circuitBreaker && state.circuitBreaker.breaker_status ? state.circuitBreaker.breaker_status : "clear";
    el.executionFlagsState.textContent = "shell blocked · SQL blocked · deploy blocked · rollback blocked · alerts blocked · full fleet activation blocked";
    el.runPlansState.textContent = String(state.runPlans.length);
    el.validationState.textContent = state.runPlans[0] ? state.runPlans[0].validation_status : "pending";
    el.approvalState.textContent = state.runPlans[0] ? state.runPlans[0].approval_status : "pending";
    el.executionStatusState.textContent = state.runPlans[0] ? state.runPlans[0].execution_status : "not_started";
  }

  function renderPermissions() {
    el.permissionsBody.innerHTML = [
      ...state.permissionScopes.enabled.map((scope) => `<tr><td>${escapeHtml(scope)}</td><td><span class="badge success">enabled</span></td></tr>`),
      ...state.permissionScopes.blocked.map((scope) => `<tr><td>${escapeHtml(scope)}</td><td><span class="badge danger">blocked</span></td></tr>`),
    ].join("") || '<tr><td colspan="2">No permission scopes loaded.</td></tr>';
  }

  function renderOperations() {
    el.operationsBody.innerHTML = state.allowlistedOperations.length
      ? state.allowlistedOperations.map((op) => `
        <tr>
          <td>${escapeHtml(op.operation_id)}</td>
          <td>${escapeHtml(op.display_name)}</td>
          <td>${escapeHtml(op.scope)}</td>
          <td><span class="badge ${op.enabled ? "success" : "danger"}">${op.enabled ? "enabled" : "disabled"}</span></td>
          <td>${escapeHtml(op.risk_level || "medium")}</td>
        </tr>
      `).join("")
      : '<tr><td colspan="5">No allowlisted operations loaded.</td></tr>';
  }

  function renderRunPlans() {
    const options = ['<option value="">Select run plan</option>'];
    el.runPlansBody.innerHTML = state.runPlans.length
      ? state.runPlans.map((plan) => {
        options.push(`<option value="${escapeHtml(plan.run_plan_id)}">${escapeHtml(plan.title)} · ${escapeHtml(plan.requested_operation)}</option>`);
        const selected = plan.run_plan_id === state.selectedRunPlanId;
        return `
          <tr class="${selected ? "is-selected" : ""}">
            <td>${escapeHtml(plan.title)}</td>
            <td>${escapeHtml(plan.requested_scope)}</td>
            <td>${escapeHtml(plan.requested_operation)}</td>
            <td><span class="badge ${plan.validation_status === "passed" ? "success" : plan.validation_status === "blocked" ? "danger" : "info"}">${escapeHtml(plan.validation_status)}</span></td>
            <td><span class="badge ${plan.approval_status === "approved" || plan.approval_status === "not_required" ? "success" : plan.approval_status === "denied" ? "danger" : "info"}">${escapeHtml(plan.approval_status)}</span></td>
            <td><span class="badge ${plan.execution_status === "completed" ? "success" : plan.execution_status === "blocked" ? "danger" : "info"}">${escapeHtml(plan.execution_status)}</span></td>
          </tr>
        `;
      }).join("")
      : '<tr><td colspan="6">No run plans recorded yet.</td></tr>';
    el.planSelect.innerHTML = options.join("");
    if (state.selectedRunPlanId) {
      el.planSelect.value = state.selectedRunPlanId;
    }
  }

  function renderEvents() {
    el.eventsBody.innerHTML = state.operatorEvents.length
      ? state.operatorEvents.map((event) => `
        <tr>
          <td>${fmtDate(event.created_at)}</td>
          <td>${escapeHtml(event.event_type)}</td>
          <td>${escapeHtml(event.event_summary)}</td>
          <td>${escapeHtml(JSON.stringify(event.event_payload || {}))}</td>
        </tr>
      `).join("")
      : '<tr><td colspan="4">No audit events yet.</td></tr>';
  }

  function renderNotes() {
    el.notesBody.innerHTML = state.readinessNotes.length
      ? state.readinessNotes.map((note) => `
        <tr>
          <td>${fmtDate(note.created_at)}</td>
          <td>${escapeHtml(note.note_type)}</td>
          <td>${escapeHtml(note.note_body)}</td>
          <td>${escapeHtml(note.actor || "operator")}</td>
        </tr>
      `).join("")
      : '<tr><td colspan="4">No readiness notes yet.</td></tr>';
  }

  function renderAll() {
    renderStatus();
    renderPermissions();
    renderOperations();
    renderRunPlans();
    renderEvents();
    renderNotes();
  }

  async function refreshStatus() {
    const response = await requestJson(ENDPOINTS.status, { method: "GET" });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Unable to load operator status.");
    }
    state.backendConfigured = true;
    state.session = payload.session || null;
    state.permissionScopes = payload.permission_scopes || { enabled: [], blocked: [] };
    state.allowlistedOperations = payload.allowlisted_operations || [];
    state.runPlans = payload.run_plans || [];
    state.operatorEvents = payload.operator_events || [];
    state.readinessNotes = payload.readiness_notes || [];
    state.circuitBreaker = payload.circuit_breaker || { breaker_status: "clear" };
    state.selectedRunPlanId = state.runPlans[0] ? state.runPlans[0].run_plan_id : "";
    setMessage("Continual Harness operator status loaded.");
    renderAll();
  }

  async function createRunPlan(event) {
    event.preventDefault();
    const body = {
      title: el.planTitle.value.trim(),
      requested_scope: el.planScope.value,
      requested_operation: el.planOperation.value,
      plan_body: safeParseJson(el.planBody.value),
    };
    const response = await requestJson(ENDPOINTS.createRunPlan, {
      method: "POST",
      body: JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Unable to create run plan.");
    }
    setMessage("Run plan created.");
    await refreshStatus();
    if (payload.run_plan && payload.run_plan.run_plan_id) {
      state.selectedRunPlanId = payload.run_plan.run_plan_id;
      el.planSelect.value = payload.run_plan.run_plan_id;
    }
  }

  async function validateSelectedPlan() {
    const runPlanId = el.planSelect.value || state.selectedRunPlanId;
    if (!runPlanId) {
      throw new Error("Select a run plan first.");
    }
    const response = await requestJson(ENDPOINTS.validateRunPlan, {
      method: "POST",
      body: JSON.stringify({ run_plan_id: runPlanId }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Unable to validate run plan.");
    }
    setMessage("Run plan validated.");
    await refreshStatus();
  }

  async function executeSelectedPlan() {
    const runPlanId = el.planSelect.value || state.selectedRunPlanId;
    if (!runPlanId) {
      throw new Error("Select a run plan first.");
    }
    const response = await requestJson(ENDPOINTS.executeOperation, {
      method: "POST",
      body: JSON.stringify({ run_plan_id: runPlanId }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Unable to execute allowlisted operation.");
    }
    setMessage("Allowlisted operation executed.");
    await refreshStatus();
  }

  async function stopHarness() {
    const response = await requestJson(ENDPOINTS.stop, {
      method: "POST",
      body: JSON.stringify({ actor: "operator-ui", reason: "Stop requested from UI." }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Unable to stop harness.");
    }
    setMessage("Harness paused.");
    await refreshStatus();
  }

  function wireEvents() {
    el.refreshButton.addEventListener("click", () => {
      refreshStatus().catch((error) => setMessage(error.message));
    });
    el.exportButton.addEventListener("click", () => {
      const blob = new Blob([JSON.stringify({
        session: state.session,
        permission_scopes: state.permissionScopes,
        allowlisted_operations: state.allowlistedOperations,
        run_plans: state.runPlans,
        operator_events: state.operatorEvents,
        readiness_notes: state.readinessNotes,
        circuit_breaker: state.circuitBreaker,
      }, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "continual-harness-operator-state.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setMessage("Operator state exported.");
    });
    el.stopButton.addEventListener("click", () => {
      stopHarness().catch((error) => setMessage(error.message));
    });
    el.createPlanForm.addEventListener("submit", (event) => {
      createRunPlan(event).catch((error) => setMessage(error.message));
    });
    el.validateButton.addEventListener("click", () => {
      validateSelectedPlan().catch((error) => setMessage(error.message));
    });
    el.executeButton.addEventListener("click", () => {
      executeSelectedPlan().catch((error) => setMessage(error.message));
    });
    el.planSelect.addEventListener("change", (event) => {
      state.selectedRunPlanId = event.target.value;
      renderRunPlans();
    });
  }

  function boot() {
    wireEvents();
    refreshStatus().catch((error) => {
      state.backendConfigured = false;
      setMessage(error.message || "Continual Harness operator backend is not configured.");
      renderAll();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
