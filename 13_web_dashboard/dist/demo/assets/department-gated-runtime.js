(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-department-runtime-gates",
    rollup: "/.netlify/functions/department-gated-runtime-rollup",
    approve: "/.netlify/functions/approve-department-runtime-gate",
    block: "/.netlify/functions/block-department-runtime-gate",
    activate: "/.netlify/functions/activate-department-runtime",
    deactivate: "/.netlify/functions/deactivate-department-runtime",
  };

  const backendUnavailableMessage = "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    globalLimits: {},
    rollup: null,
    departments: [],
    gateEvents: [],
    pageInfo: {
      limit: 250,
      offset: 0,
      returned: 0,
      total_filtered_departments: 0,
      total_departments: 0,
    },
    filters: {
      search: "",
      status: "",
      family: "",
      unit: "",
      lane: "",
    },
    selectedDepartmentId: "",
    selectedDepartment: null,
    message: backendUnavailableMessage,
  };

  const backendStatusMessage = document.getElementById("backendStatusMessage");
  const backendConnectionState = document.getElementById("backendConnectionState");
  const currentLiveAgentsState = document.getElementById("currentLiveAgentsState");
  const globalLiveCapState = document.getElementById("globalLiveCapState");
  const perDepartmentCapState = document.getElementById("perDepartmentCapState");
  const approvedGatesState = document.getElementById("approvedGatesState");
  const activeGatesState = document.getElementById("activeGatesState");
  const blockedGatesState = document.getElementById("blockedGatesState");
  const totalRegisteredAgentsState = document.getElementById("totalRegisteredAgentsState");
  const totalDepartmentsState = document.getElementById("totalDepartmentsState");
  const totalUnitsState = document.getElementById("totalUnitsState");
  const totalFamiliesState = document.getElementById("totalFamiliesState");
  const fullActivationState = document.getElementById("fullActivationState");
  const deployExecutionState = document.getElementById("deployExecutionState");
  const rollbackExecutionState = document.getElementById("rollbackExecutionState");
  const alertSendingState = document.getElementById("alertSendingState");
  const pageInfo = document.getElementById("pageInfo");
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const familyFilter = document.getElementById("familyFilter");
  const unitFilter = document.getElementById("unitFilter");
  const laneFilter = document.getElementById("laneFilter");
  const applyFiltersButton = document.getElementById("applyFiltersButton");
  const prevPageButton = document.getElementById("prevPageButton");
  const nextPageButton = document.getElementById("nextPageButton");
  const gateTableBody = document.getElementById("gateTableBody");
  const refreshButton = document.getElementById("refreshButton");
  const exportButton = document.getElementById("exportButton");
  const approvalForm = document.getElementById("approvalForm");
  const approvalDepartmentId = document.getElementById("approvalDepartmentId");
  const approvalCap = document.getElementById("approvalCap");
  const approvalActor = document.getElementById("approvalActor");
  const approvalReason = document.getElementById("approvalReason");
  const approveButton = document.getElementById("approveButton");
  const activationForm = document.getElementById("activationForm");
  const activationDepartmentId = document.getElementById("activationDepartmentId");
  const activationCount = document.getElementById("activationCount");
  const activationActor = document.getElementById("activationActor");
  const activationReason = document.getElementById("activationReason");
  const activateButton = document.getElementById("activateButton");
  const deactivationForm = document.getElementById("deactivationForm");
  const deactivationDepartmentId = document.getElementById("deactivationDepartmentId");
  const deactivationActor = document.getElementById("deactivationActor");
  const deactivationReason = document.getElementById("deactivationReason");
  const deactivateButton = document.getElementById("deactivateButton");
  const blockButton = document.getElementById("blockButton");
  const selectedDepartmentBadges = document.getElementById("selectedDepartmentBadges");
  const selectedDepartmentSummary = document.getElementById("selectedDepartmentSummary");
  const selectedGateStatus = document.getElementById("selectedGateStatus");
  const selectedActivationCap = document.getElementById("selectedActivationCap");
  const selectedLiveAgents = document.getElementById("selectedLiveAgents");
  const selectedLane = document.getElementById("selectedLane");
  const selectedSubdivision = document.getElementById("selectedSubdivision");
  const selectedLastEvent = document.getElementById("selectedLastEvent");
  const selectedReasonNote = document.getElementById("selectedReasonNote");
  const selectedEventPayload = document.getElementById("selectedEventPayload");
  const gateEventTimeline = document.getElementById("gateEventTimeline");
  const rollupApprovedGates = document.getElementById("rollupApprovedGates");
  const rollupActiveGates = document.getElementById("rollupActiveGates");
  const rollupBlockedGates = document.getElementById("rollupBlockedGates");
  const rollupEligibleDepartments = document.getElementById("rollupEligibleDepartments");
  const rollupGateEvents = document.getElementById("rollupGateEvents");
  const rollupActivationEvents = document.getElementById("rollupActivationEvents");

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
    return new Intl.DateTimeFormat("en-US", {
      dateStyle: "medium",
      timeStyle: "short",
      hour12: false,
    }).format(date);
  }

  function fmtNumber(value) {
    return Number(value || 0).toLocaleString("en-US");
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

  function buildQuery() {
    const params = new URLSearchParams();
    params.set("limit", String(state.pageInfo.limit));
    params.set("offset", String(state.pageInfo.offset));
    if (state.filters.search) params.set("search", state.filters.search);
    if (state.filters.status) params.set("status", state.filters.status);
    if (state.filters.family) params.set("family", state.filters.family);
    if (state.filters.unit) params.set("unit", state.filters.unit);
    if (state.filters.lane) params.set("lane", state.filters.lane);
    return params.toString();
  }

  function currentDepartment() {
    return state.departments.find((department) => department.department_id === state.selectedDepartmentId) || state.departments[0] || null;
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.config = {};
    state.globalLimits = {};
    state.rollup = null;
    state.departments = [];
    state.gateEvents = [];
    state.selectedDepartmentId = "";
    state.selectedDepartment = null;
    state.message = message || backendUnavailableMessage;
    renderAll();
  }

  function setMessage(message) {
    state.message = message;
    renderAllStatusMessage();
  }

  function renderAllStatusMessage() {
    backendStatusMessage.textContent = state.message || backendUnavailableMessage;
    backendStatusMessage.dataset.state = state.backendConfigured ? "success" : "warn";
  }

  function renderBackendPanel() {
    backendConnectionState.textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    currentLiveAgentsState.textContent = fmtNumber(
      state.rollup
        ? state.rollup.current_live_runtime_agents
        : state.backendStatus
          ? state.backendStatus.live_runtime_agents_enabled || state.backendStatus.current_live_runtime_agents || 0
          : 0,
    );
    globalLiveCapState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.global_live_agent_cap : 2500);
    perDepartmentCapState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.max_department_activation_cap : 250);
    approvedGatesState.textContent = fmtNumber(state.rollup ? state.rollup.approved_gates : 0);
    activeGatesState.textContent = fmtNumber(state.rollup ? state.rollup.active_gates : 0);
    blockedGatesState.textContent = fmtNumber(state.rollup ? state.rollup.blocked_gates : 0);
    totalRegisteredAgentsState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_registered_agents : 47979);
    totalDepartmentsState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_departments : 1777);
    totalUnitsState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_units : 5331);
    totalFamiliesState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_families : 175);
    fullActivationState.textContent = state.backendStatus && state.backendStatus.full_47979_activation_blocked ? "blocked" : "blocked";
    deployExecutionState.textContent = state.backendStatus && state.backendStatus.deploy_execution_enabled ? "enabled" : "disabled";
    rollbackExecutionState.textContent = state.backendStatus && state.backendStatus.rollback_execution_enabled ? "enabled" : "disabled";
    alertSendingState.textContent = state.backendStatus && state.backendStatus.alert_sending_enabled ? "enabled" : "disabled";
  }

  function renderPageInfo() {
    if (!pageInfo) return;
    const total = state.pageInfo.total_filtered_departments || 0;
    const returned = state.pageInfo.returned || 0;
    const start = total === 0 ? 0 : state.pageInfo.offset + 1;
    const end = Math.min(state.pageInfo.offset + returned, total);
    pageInfo.textContent = `Showing ${start}-${end} of ${fmtNumber(total)} filtered departments. Page size ${state.pageInfo.limit}.`;
    prevPageButton.disabled = state.pageInfo.offset <= 0;
    nextPageButton.disabled = state.pageInfo.offset + state.pageInfo.limit >= total;
  }

  function gateBadgeClass(status) {
    switch (String(status || "").toLowerCase()) {
      case "approved":
      case "active":
        return "badge success";
      case "blocked":
      case "disabled":
        return "badge danger";
      case "pending_review":
        return "badge warning";
      default:
        return "badge info";
    }
  }

  function renderTable() {
    if (!state.departments.length) {
      gateTableBody.innerHTML = '<tr><td colspan="6">No departments match the current filters.</td></tr>';
      return;
    }

    gateTableBody.innerHTML = state.departments
      .map((department) => {
        const isSelected = department.department_id === state.selectedDepartmentId;
        const laneText = department.mapped_runtime_lane_id ? `${department.mapped_runtime_lane_id}` : "n/a";
        const subdivisionText = department.mapped_runtime_subdivision_name || department.mapped_runtime_subdivision_id || "n/a";
        const gateStatusText = department.gate_status || "closed";
        return `
          <tr class="${isSelected ? "is-selected" : ""}" data-department-id="${escapeHtml(department.department_id)}">
            <td>
              <strong>${escapeHtml(department.department_id)}</strong><br>
              <span>${escapeHtml(department.department_name || "")}</span>
              <div class="badge-row mt-12">
                <span class="badge ghost">${escapeHtml(department.family_id || "n/a")} · ${escapeHtml(department.family_name || "n/a")}</span>
                <span class="badge ghost">${escapeHtml(department.unit_id || "n/a")} · ${escapeHtml(department.unit_name || "n/a")}</span>
              </div>
            </td>
            <td>
              <div>${escapeHtml(laneText)}</div>
              <div class="badge-row mt-12">
                <span class="badge ghost">${escapeHtml(subdivisionText)}</span>
              </div>
            </td>
            <td>
              <span class="${gateBadgeClass(gateStatusText)}">${escapeHtml(gateStatusText)}</span>
              <div class="badge-row mt-12">
                <span class="badge ghost">runtime: ${escapeHtml(department.runtime_status || "n/a")}</span>
                <span class="badge ghost">eligible: ${department.activation_eligible ? "true" : "false"}</span>
              </div>
            </td>
            <td>
              <div><strong>${fmtNumber(department.activation_cap || 0)}</strong> cap</div>
              <div class="badge-row mt-12">
                <span class="badge info">${fmtNumber(department.currently_active_agents || 0)} active</span>
              </div>
            </td>
            <td>
              <div>Gate events: ${fmtNumber(department.gate_event_count || 0)}</div>
              <div>Readiness notes: ${fmtNumber(department.notes_count || 0)}</div>
              <div>Last event: ${escapeHtml(fmtDate(department.last_gate_event_at))}</div>
            </td>
            <td>
              <div class="button-row">
                <button class="button" type="button" data-action="select" data-department-id="${escapeHtml(department.department_id)}">Select</button>
                <button class="button secondary" type="button" data-action="prefill-approve" data-department-id="${escapeHtml(department.department_id)}">Approve</button>
                <button class="button secondary" type="button" data-action="prefill-activate" data-department-id="${escapeHtml(department.department_id)}">Activate</button>
                <button class="button secondary" type="button" data-action="prefill-deactivate" data-department-id="${escapeHtml(department.department_id)}">Deactivate</button>
                <button class="button danger" type="button" data-action="prefill-block" data-department-id="${escapeHtml(department.department_id)}">Block</button>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderSelectedDepartment() {
    const department = currentDepartment();
    if (!department) {
      selectedDepartmentBadges.innerHTML = '<span class="badge info">No department selected yet.</span>';
      selectedDepartmentSummary.textContent = "Select a department from the table to inspect its gate state, lane mapping, and audit trail.";
      selectedGateStatus.textContent = "n/a";
      selectedActivationCap.textContent = "n/a";
      selectedLiveAgents.textContent = "n/a";
      selectedLane.textContent = "n/a";
      selectedSubdivision.textContent = "n/a";
      selectedLastEvent.textContent = "n/a";
      selectedReasonNote.textContent = "Reason notes appear here from the selected gate event payload.";
      selectedEventPayload.textContent = "{}";
      return;
    }

    selectedDepartmentBadges.innerHTML = [
      `<span class="badge success">${escapeHtml(department.department_id)}</span>`,
      `<span class="badge info">${escapeHtml(department.department_name || "Unnamed department")}</span>`,
      `<span class="badge ghost">${escapeHtml(department.family_name || department.family_id || "n/a")}</span>`,
      `<span class="badge ghost">${escapeHtml(department.unit_name || department.unit_id || "n/a")}</span>`,
    ].join("");
    selectedDepartmentSummary.textContent = `Department ${department.department_id} is currently ${department.gate_status || "closed"} with ${fmtNumber(department.currently_active_agents || 0)} supervised runtime agents enabled.`;
    selectedGateStatus.textContent = department.gate_status || "closed";
    selectedActivationCap.textContent = fmtNumber(department.activation_cap || 0);
    selectedLiveAgents.textContent = fmtNumber(department.currently_active_agents || 0);
    selectedLane.textContent = department.mapped_runtime_lane_name || department.mapped_runtime_lane_id || "n/a";
    selectedSubdivision.textContent = department.mapped_runtime_subdivision_name || department.mapped_runtime_subdivision_id || "n/a";
    selectedLastEvent.textContent = department.last_gate_event_at ? `${department.last_gate_event_type || "event"} · ${fmtDate(department.last_gate_event_at)}` : "n/a";
    selectedReasonNote.textContent = department.last_gate_event_payload
      ? department.last_gate_event_payload.readiness_note || department.last_gate_event_payload.reason || department.last_gate_event_payload.blocked_reason || "No note payload found."
      : department.blocked_reason || "No note payload found.";
    selectedEventPayload.textContent = JSON.stringify(department.last_gate_event_payload || {}, null, 2);
  }

  function renderTimeline() {
    const events = (state.gateEvents || []).slice(0, 15);
    if (!events.length) {
      gateEventTimeline.innerHTML = '<div class="runtime-audit-item">No gate events recorded yet.</div>';
      return;
    }

    gateEventTimeline.innerHTML = events
      .map((event) => {
        return `
          <article class="runtime-audit-item">
            <h4>${escapeHtml(event.event_type || "UNKNOWN_EVENT")}</h4>
            <div class="badge-row">
              <span class="badge info">${escapeHtml(event.department_id || "n/a")}</span>
              <span class="badge ghost">${escapeHtml(event.actor || "operator")}</span>
              <span class="badge ghost">${escapeHtml(fmtDate(event.created_at))}</span>
            </div>
            <p class="runtime-audit-summary">${escapeHtml(event.event_summary || "")}</p>
            <details>
              <summary class="badge ghost">Payload</summary>
              <pre class="code-block">${escapeHtml(JSON.stringify(event.event_payload || {}, null, 2))}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  function renderRollupCards() {
    rollupApprovedGates.textContent = fmtNumber(state.rollup ? state.rollup.approved_gates : 0);
    rollupActiveGates.textContent = fmtNumber(state.rollup ? state.rollup.active_gates : 0);
    rollupBlockedGates.textContent = fmtNumber(state.rollup ? state.rollup.blocked_gates : 0);
    rollupEligibleDepartments.textContent = fmtNumber(state.rollup ? state.rollup.eligible_departments : 0);
    rollupGateEvents.textContent = fmtNumber(state.rollup ? state.rollup.gate_event_count : 0);
    rollupActivationEvents.textContent = fmtNumber(state.rollup ? state.rollup.activation_event_count : 0);
  }

  function renderAll() {
    renderAllStatusMessage();
    renderBackendPanel();
    renderPageInfo();
    renderTable();
    renderSelectedDepartment();
    renderTimeline();
    renderRollupCards();
  }

  function syncFiltersFromInputs() {
    state.filters.search = searchInput.value.trim();
    state.filters.status = statusFilter.value.trim();
    state.filters.family = familyFilter.value.trim();
    state.filters.unit = unitFilter.value.trim();
    state.filters.lane = laneFilter.value.trim();
  }

  function syncInputsFromState() {
    searchInput.value = state.filters.search;
    statusFilter.value = state.filters.status;
    familyFilter.value = state.filters.family;
    unitFilter.value = state.filters.unit;
    laneFilter.value = state.filters.lane;
  }

  function prefillFormsFromDepartment(department) {
    if (!department) return;
    approvalDepartmentId.value = department.department_id || "";
    approvalCap.value = String(Math.max(1, Number(department.activation_cap || 1)));
    approvalActor.value = approvalActor.value || "operator";
    approvalReason.value = department.last_gate_event_payload && (department.last_gate_event_payload.readiness_note || department.last_gate_event_payload.reason)
      ? String(department.last_gate_event_payload.readiness_note || department.last_gate_event_payload.reason)
      : approvalReason.value || `Department ${department.department_id} readiness note`;

    activationDepartmentId.value = department.department_id || "";
    activationCount.value = String(Math.max(1, Number(department.activation_cap || 1)));
    activationActor.value = activationActor.value || "operator";
    activationReason.value = activationReason.value || `Department ${department.department_id} activation note`;

    deactivationDepartmentId.value = department.department_id || "";
    deactivationActor.value = deactivationActor.value || "operator";
    deactivationReason.value = deactivationReason.value || `Department ${department.department_id} deactivation note`;
  }

  function selectDepartment(departmentId) {
    state.selectedDepartmentId = departmentId;
    state.selectedDepartment = currentDepartment();
    prefillFormsFromDepartment(state.selectedDepartment);
    renderAll();
  }

  function setBackendReady(listData, rollupData) {
    state.backendConfigured = true;
    state.backendStatus = listData.backend_status || {};
    state.config = listData.config || {};
    state.globalLimits = listData.global_limits || {};
    state.departments = listData.departments || [];
    state.gateEvents = listData.gate_events || [];
    state.pageInfo = listData.page_info || state.pageInfo;
    state.rollup = (rollupData && rollupData.rollup) || listData.rollup || null;
    if (!state.selectedDepartmentId || !state.departments.some((department) => department.department_id === state.selectedDepartmentId)) {
      state.selectedDepartmentId = state.departments[0] ? state.departments[0].department_id : "";
    }
    state.selectedDepartment = currentDepartment();
    if (state.selectedDepartment) {
      prefillFormsFromDepartment(state.selectedDepartment);
    }
    state.message = "Backend functions responded successfully.";
    syncInputsFromState();
    renderAll();
  }

  async function loadState() {
    setMessage("Loading department gate state...");
    try {
      const listResponse = await requestJson(`${ENDPOINTS.list}?${buildQuery()}`, { method: "GET" });
      const listData = await listResponse.json();

      if (listResponse.status === 503 || !listData.ok) {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }

      let rollupData = null;
      try {
        const rollupResponse = await requestJson(ENDPOINTS.rollup, { method: "GET" });
        const parsedRollup = await rollupResponse.json();
        if (rollupResponse.ok && parsedRollup.ok) {
          rollupData = parsedRollup;
        }
      } catch (error) {
        rollupData = null;
      }

      setBackendReady(listData, rollupData);
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
    }
  }

  async function submitMutation(url, payload, actionLabel) {
    setMessage(`${actionLabel}...`);
    try {
      const response = await requestJson(url, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (response.status === 503 || data.error === "Department-gated runtime backend is not configured.") {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }

      if (!response.ok || !data.ok) {
        setMessage(data.error || `${actionLabel} failed.`);
        return;
      }

      await loadState();
      setMessage(`${actionLabel} complete.`);
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
    }
  }

  function buildApprovePayload() {
    return {
      department_id: approvalDepartmentId.value.trim(),
      activation_cap: Number(approvalCap.value),
      actor: approvalActor.value.trim() || "operator",
      reason: approvalReason.value.trim(),
    };
  }

  function buildActivatePayload() {
    return {
      department_id: activationDepartmentId.value.trim(),
      requested_agent_count: Number(activationCount.value),
      actor: activationActor.value.trim() || "operator",
      reason: activationReason.value.trim(),
    };
  }

  function buildDeactivatePayload() {
    return {
      department_id: deactivationDepartmentId.value.trim(),
      actor: deactivationActor.value.trim() || "operator",
      reason: deactivationReason.value.trim(),
    };
  }

  function exportJson() {
    const payload = {
      backend_status: state.backendStatus,
      config: state.config,
      global_limits: state.globalLimits,
      rollup: state.rollup,
      page_info: state.pageInfo,
      filters: state.filters,
      departments: state.departments,
      gate_events: state.gateEvents,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "department-gated-runtime-state.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  gateTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    const row = event.target.closest("tr[data-department-id]");
    if (button) {
      const departmentId = button.getAttribute("data-department-id");
      const department = state.departments.find((entry) => entry.department_id === departmentId) || null;
      if (department) {
        selectDepartment(departmentId);
      }
      const action = button.getAttribute("data-action");
      if (action === "select" || action === "prefill-approve" || action === "prefill-activate" || action === "prefill-deactivate" || action === "prefill-block") {
        return;
      }
    }
    if (row && !button) {
      selectDepartment(row.getAttribute("data-department-id"));
    }
  });

  refreshButton.addEventListener("click", loadState);
  exportButton.addEventListener("click", exportJson);

  applyFiltersButton.closest("form").addEventListener("submit", (event) => {
    event.preventDefault();
    syncFiltersFromInputs();
    state.pageInfo.offset = 0;
    loadState();
  });

  prevPageButton.addEventListener("click", () => {
    state.pageInfo.offset = Math.max(state.pageInfo.offset - state.pageInfo.limit, 0);
    loadState();
  });

  nextPageButton.addEventListener("click", () => {
    state.pageInfo.offset = state.pageInfo.offset + state.pageInfo.limit;
    loadState();
  });

  approvalForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = buildApprovePayload();
    submitMutation(ENDPOINTS.approve, payload, "Approve department gate");
  });

  activationForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = buildActivatePayload();
    submitMutation(ENDPOINTS.activate, payload, "Activate department runtime");
  });

  deactivationForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = buildDeactivatePayload();
    submitMutation(ENDPOINTS.deactivate, payload, "Deactivate department runtime");
  });

  blockButton.addEventListener("click", () => {
    const payload = buildDeactivatePayload();
    submitMutation(ENDPOINTS.block, payload, "Block department gate");
  });

  [approvalDepartmentId, activationDepartmentId, deactivationDepartmentId].forEach((input) => {
    input.addEventListener("change", () => {
      const department = state.departments.find((entry) => entry.department_id === input.value.trim()) || state.selectedDepartment;
      if (department) {
        state.selectedDepartmentId = department.department_id;
        state.selectedDepartment = department;
        prefillFormsFromDepartment(department);
        renderAll();
      }
    });
  });

  loadState();
})();
