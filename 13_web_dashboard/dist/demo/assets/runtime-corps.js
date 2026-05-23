(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-corps",
    rollup: "/.netlify/functions/runtime-corps-rollup",
    activateCohort: "/.netlify/functions/activate-runtime-corps-cohort",
    deactivateCohort: "/.netlify/functions/deactivate-runtime-corps-cohort",
    activateDepartment: "/.netlify/functions/activate-approved-department-cohort",
    deactivateDepartment: "/.netlify/functions/deactivate-approved-department-cohort",
    heartbeat: "/.netlify/functions/runtime-corps-heartbeat",
    note: "/.netlify/functions/create-runtime-corps-readiness-note",
  };

  const backendUnavailableMessage = "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    caps: {},
    rollup: null,
    departments: [],
    activeCohorts: [],
    recentEvents: [],
    pageInfo: {
      limit: 100,
      offset: 0,
      returned: 0,
      total_filtered_departments: 0,
      total_departments: 0,
    },
    filters: {
      search: "",
      status: "",
      lane: "",
    },
    message: backendUnavailableMessage,
    selectedDepartmentId: "",
  };

  const el = {
    backendStatusMessage: document.getElementById("backendStatusMessage"),
    backendConnectionState: document.getElementById("backendConnectionState"),
    currentLiveAgentsState: document.getElementById("currentLiveAgentsState"),
    globalLiveCapState: document.getElementById("globalLiveCapState"),
    maxCohortSizeState: document.getElementById("maxCohortSizeState"),
    maxChunkSizeState: document.getElementById("maxChunkSizeState"),
    approvedGatesState: document.getElementById("approvedGatesState"),
    activeGatesState: document.getElementById("activeGatesState"),
    activeCohortsState: document.getElementById("activeCohortsState"),
    totalRegisteredAgentsState: document.getElementById("totalRegisteredAgentsState"),
    totalDepartmentsState: document.getElementById("totalDepartmentsState"),
    departmentGatedActivationState: document.getElementById("departmentGatedActivationState"),
    fullActivationState: document.getElementById("fullActivationState"),
    commandExecutionState: document.getElementById("commandExecutionState"),
    deployExecutionState: document.getElementById("deployExecutionState"),
    rollbackExecutionState: document.getElementById("rollbackExecutionState"),
    alertSendingState: document.getElementById("alertSendingState"),
    pageInfo: document.getElementById("pageInfo"),
    searchInput: document.getElementById("searchInput"),
    statusFilter: document.getElementById("statusFilter"),
    laneFilter: document.getElementById("laneFilter"),
    departmentSelect: document.getElementById("departmentSelect"),
    applyFiltersButton: document.getElementById("applyFiltersButton"),
    prevPageButton: document.getElementById("prevPageButton"),
    nextPageButton: document.getElementById("nextPageButton"),
    corpsTableBody: document.getElementById("corpsTableBody"),
    activeCohortsBody: document.getElementById("activeCohortsBody"),
    eventTimeline: document.getElementById("eventTimeline"),
    refreshButton: document.getElementById("refreshButton"),
    exportButton: document.getElementById("exportButton"),
    statusMessage: document.getElementById("statusMessage"),
    activationForm: document.getElementById("activationForm"),
    activationDepartmentId: document.getElementById("activationDepartmentId"),
    activationCount: document.getElementById("activationCount"),
    activationActor: document.getElementById("activationActor"),
    activationReason: document.getElementById("activationReason"),
    activateButton: document.getElementById("activateButton"),
    cohortDeactivationForm: document.getElementById("cohortDeactivationForm"),
    cohortIdInput: document.getElementById("cohortIdInput"),
    cohortActorInput: document.getElementById("cohortActorInput"),
    cohortReasonInput: document.getElementById("cohortReasonInput"),
    deactivateCohortButton: document.getElementById("deactivateCohortButton"),
    departmentDeactivationForm: document.getElementById("departmentDeactivationForm"),
    departmentDeactivateInput: document.getElementById("departmentDeactivateInput"),
    departmentDeactivateActor: document.getElementById("departmentDeactivateActor"),
    departmentDeactivateReason: document.getElementById("departmentDeactivateReason"),
    deactivateDepartmentButton: document.getElementById("deactivateDepartmentButton"),
    heartbeatForm: document.getElementById("heartbeatForm"),
    heartbeatActor: document.getElementById("heartbeatActor"),
    heartbeatReason: document.getElementById("heartbeatReason"),
    heartbeatButton: document.getElementById("heartbeatButton"),
    noteForm: document.getElementById("noteForm"),
    noteDepartmentId: document.getElementById("noteDepartmentId"),
    noteActor: document.getElementById("noteActor"),
    noteType: document.getElementById("noteType"),
    noteBody: document.getElementById("noteBody"),
    noteButton: document.getElementById("noteButton"),
    rollupApprovedGates: document.getElementById("rollupApprovedGates"),
    rollupActiveGates: document.getElementById("rollupActiveGates"),
    rollupActiveCohorts: document.getElementById("rollupActiveCohorts"),
    rollupGateEvents: document.getElementById("rollupGateEvents"),
    rollupCohortEvents: document.getElementById("rollupCohortEvents"),
    rollupLiveAgents: document.getElementById("rollupLiveAgents"),
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function fmtNumber(value) {
    return Number(value || 0).toLocaleString("en-US");
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
    renderStatusMessage();
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.caps = {};
    state.rollup = null;
    state.departments = [];
    state.activeCohorts = [];
    state.recentEvents = [];
    state.selectedDepartmentId = "";
    state.message = message || backendUnavailableMessage;
    renderAll();
  }

  function renderStatusMessage() {
    el.backendStatusMessage.textContent = state.message || backendUnavailableMessage;
    el.backendStatusMessage.dataset.state = state.backendConfigured ? "success" : "warn";
    el.statusMessage.textContent = state.message || backendUnavailableMessage;
  }

  function renderStatusPanel() {
    el.backendConnectionState.textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    el.currentLiveAgentsState.textContent = fmtNumber(state.rollup ? state.rollup.current_live_runtime_agents : state.backendStatus ? state.backendStatus.current_live_runtime_agents : 0);
    el.globalLiveCapState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.global_live_agent_cap : 5000);
    el.maxCohortSizeState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.max_cohort_activation_size : 500);
    el.maxChunkSizeState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.max_operation_chunk_size : 250);
    el.approvedGatesState.textContent = fmtNumber(state.rollup ? state.rollup.approved_department_gates : 0);
    el.activeGatesState.textContent = fmtNumber(state.rollup ? state.rollup.active_department_gates : 0);
    el.activeCohortsState.textContent = fmtNumber(state.rollup ? state.rollup.active_cohorts : 0);
    el.totalRegisteredAgentsState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_registered_agents : 47979);
    el.totalDepartmentsState.textContent = fmtNumber(state.backendStatus ? state.backendStatus.total_departments : 1777);
    el.departmentGatedActivationState.textContent = state.backendStatus && state.backendStatus.department_gated_activation_required ? "true" : "true";
    el.fullActivationState.textContent = state.backendStatus && state.backendStatus.full_47979_activation_blocked ? "blocked" : "blocked";
    el.commandExecutionState.textContent = state.backendStatus && state.backendStatus.command_execution_enabled ? "enabled" : "disabled";
    el.deployExecutionState.textContent = state.backendStatus && state.backendStatus.deploy_execution_enabled ? "enabled" : "disabled";
    el.rollbackExecutionState.textContent = state.backendStatus && state.backendStatus.rollback_execution_enabled ? "enabled" : "disabled";
    el.alertSendingState.textContent = state.backendStatus && state.backendStatus.alert_sending_enabled ? "enabled" : "disabled";
    el.rollupApprovedGates.textContent = fmtNumber(state.rollup ? state.rollup.approved_department_gates : 0);
    el.rollupActiveGates.textContent = fmtNumber(state.rollup ? state.rollup.active_department_gates : 0);
    el.rollupActiveCohorts.textContent = fmtNumber(state.rollup ? state.rollup.active_cohorts : 0);
    el.rollupGateEvents.textContent = fmtNumber(state.rollup ? state.rollup.gate_event_count : 0);
    el.rollupCohortEvents.textContent = fmtNumber(state.rollup ? state.rollup.cohort_event_count : 0);
    el.rollupLiveAgents.textContent = fmtNumber(state.rollup ? state.rollup.current_live_runtime_agents : 0);
  }

  function renderPageInfo() {
    const total = state.pageInfo.total_filtered_departments || 0;
    const returned = state.pageInfo.returned || 0;
    const start = total === 0 ? 0 : state.pageInfo.offset + 1;
    const end = Math.min(state.pageInfo.offset + returned, total);
    el.pageInfo.textContent = `Showing ${start}-${end} of ${fmtNumber(total)} approved gates. Page size ${state.pageInfo.limit}.`;
    el.prevPageButton.disabled = state.pageInfo.offset <= 0;
    el.nextPageButton.disabled = state.pageInfo.offset + state.pageInfo.limit >= total;
  }

  function gateClass(status) {
    switch (String(status || "").toLowerCase()) {
      case "approved":
      case "active":
        return "badge success";
      case "blocked":
      case "disabled":
        return "badge danger";
      default:
        return "badge info";
    }
  }

  function renderDepartmentSelect() {
    const options = ['<option value="">Select approved department gate</option>'];
    for (const department of state.departments) {
      options.push(
        `<option value="${escapeHtml(department.department_id)}">${escapeHtml(department.department_id)} · ${escapeHtml(department.department_name || "")}</option>`,
      );
    }
    el.departmentSelect.innerHTML = options.join("");
    if (state.selectedDepartmentId) {
      el.departmentSelect.value = state.selectedDepartmentId;
    }
  }

  function renderDepartmentsTable() {
    if (!state.departments.length) {
      el.corpsTableBody.innerHTML = '<tr><td colspan="6">No approved department gates match the current filters.</td></tr>';
      return;
    }

    el.corpsTableBody.innerHTML = state.departments
      .map((department) => {
        const selected = department.department_id === state.selectedDepartmentId;
        return `
          <tr class="${selected ? "is-selected" : ""}" data-department-id="${escapeHtml(department.department_id)}">
            <td>
              <strong>${escapeHtml(department.department_id)}</strong><br>
              <span>${escapeHtml(department.department_name || "")}</span>
              <div class="badge-row mt-12">
                <span class="badge ghost">${escapeHtml(department.family_id || "n/a")} · ${escapeHtml(department.family_name || "n/a")}</span>
                <span class="badge ghost">${escapeHtml(department.unit_id || "n/a")} · ${escapeHtml(department.unit_name || "n/a")}</span>
              </div>
            </td>
            <td>
              <div>${escapeHtml(department.mapped_runtime_lane_id || "n/a")}</div>
              <div class="badge-row mt-12">
                <span class="badge ghost">${escapeHtml(department.mapped_runtime_subdivision_name || department.mapped_runtime_subdivision_id || "n/a")}</span>
              </div>
            </td>
            <td>
              <span class="${gateClass(department.gate_status)}">${escapeHtml(department.gate_status || "closed")}</span>
              <div class="badge-row mt-12">
                <span class="badge ghost">runtime: ${escapeHtml(department.runtime_status || "n/a")}</span>
                <span class="badge ghost">eligible: ${department.activation_eligible ? "true" : "false"}</span>
              </div>
            </td>
            <td>
              <div>cap ${fmtNumber(department.activation_cap || 0)}</div>
              <div class="badge-row mt-12">
                <span class="badge ghost">live ${fmtNumber(department.currently_active_agents || 0)}</span>
              </div>
            </td>
            <td>
              <div>${fmtNumber(department.cohort_count || 0)} cohort(s)</div>
              <div class="badge-row mt-12">
                <span class="badge ghost">${escapeHtml(department.last_gate_event_type || "n/a")}</span>
              </div>
            </td>
            <td>
              <button class="button secondary select-department-button" type="button" data-department-id="${escapeHtml(department.department_id)}">Select</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderActiveCohorts() {
    if (!state.activeCohorts.length) {
      el.activeCohortsBody.innerHTML = '<tr><td colspan="6">No active cohorts.</td></tr>';
      return;
    }

    el.activeCohortsBody.innerHTML = state.activeCohorts
      .map((cohort) => `
        <tr data-cohort-id="${escapeHtml(cohort.cohort_id)}">
          <td><strong>${escapeHtml(cohort.cohort_id)}</strong><br><span>${escapeHtml(cohort.cohort_name || "")}</span></td>
          <td>
            <strong>${escapeHtml(cohort.department_id || "")}</strong>
            <div class="badge-row mt-12">
              <span class="badge ghost">${escapeHtml(cohort.actor || "operator")}</span>
            </div>
          </td>
          <td>
            <div>requested ${fmtNumber(cohort.requested_agent_count || 0)}</div>
            <div class="badge-row mt-12">
              <span class="badge ghost">active ${fmtNumber(cohort.activated_agent_count || 0)}</span>
            </div>
          </td>
          <td><span class="${gateClass(cohort.cohort_status)}">${escapeHtml(cohort.cohort_status || "active")}</span></td>
          <td><span class="runtime-note">${escapeHtml(cohort.reason || "n/a")}</span></td>
          <td><button class="button secondary deactivate-cohort-row-button" type="button" data-cohort-id="${escapeHtml(cohort.cohort_id)}" data-department-id="${escapeHtml(cohort.department_id || "")}">Deactivate</button></td>
        </tr>
      `)
      .join("");
  }

  function renderTimeline() {
    if (!state.recentEvents.length) {
      el.eventTimeline.innerHTML = '<div class="timeline-item"><p class="runtime-notice">No runtime corps events yet.</p></div>';
      return;
    }

    el.eventTimeline.innerHTML = state.recentEvents
      .slice(0, 30)
      .map((event, index) => `
        <article class="timeline-item">
          <div class="timeline-step">${String(index + 1).padStart(2, "0")}</div>
          <div>
            <h3>${escapeHtml(event.event_type || "EVENT")}</h3>
            <p><strong>${escapeHtml(event.department_id || "global")}</strong> · ${fmtDate(event.created_at)} · ${escapeHtml(event.actor || "operator")}</p>
            <p>${escapeHtml(event.event_summary || "")}</p>
          </div>
        </article>
      `)
      .join("");
  }

  function renderAll() {
    renderStatusMessage();
    renderStatusPanel();
    renderPageInfo();
    renderDepartmentSelect();
    renderDepartmentsTable();
    renderActiveCohorts();
    renderTimeline();
  }

  function syncSelectedDepartment(value) {
    state.selectedDepartmentId = value || "";
    el.activationDepartmentId.value = state.selectedDepartmentId;
    el.departmentDeactivateInput.value = state.selectedDepartmentId;
    el.noteDepartmentId.value = state.selectedDepartmentId;
    renderDepartmentSelect();
    renderDepartmentsTable();
  }

  function selectedDepartmentFromTable(row) {
    if (!row) return null;
    return state.departments.find((department) => department.department_id === row.dataset.departmentId) || null;
  }

  function findCohortById(cohortId) {
    return state.activeCohorts.find((cohort) => cohort.cohort_id === cohortId) || null;
  }

  async function fetchCorpsData() {
    const params = new URLSearchParams();
    params.set("limit", String(state.pageInfo.limit));
    params.set("offset", String(state.pageInfo.offset));
    if (state.filters.search) params.set("search", state.filters.search);
    if (state.filters.status) params.set("status", state.filters.status);
    if (state.filters.lane) params.set("lane", state.filters.lane);

    const [listResponse, rollupResponse] = await Promise.all([
      requestJson(`${ENDPOINTS.list}?${params.toString()}`),
      requestJson(ENDPOINTS.rollup),
    ]);

    if (!listResponse.ok) {
      if (listResponse.status === 503) {
        throw new Error("BACKEND_UNAVAILABLE");
      }
      throw new Error("LIST_FAILED");
    }

    if (!rollupResponse.ok) {
      if (rollupResponse.status === 503) {
        throw new Error("BACKEND_UNAVAILABLE");
      }
      throw new Error("ROLLUP_FAILED");
    }

    const listData = await listResponse.json();
    const rollupData = await rollupResponse.json();

    state.backendConfigured = Boolean(listData.backend_configured);
    state.backendStatus = listData.backend_status || rollupData.backend_status || null;
    state.caps = listData.caps || rollupData.caps || {};
    state.rollup = rollupData.rollup || listData.rollup || null;
    state.departments = listData.departments || [];
    state.activeCohorts = listData.active_cohorts || [];
    state.recentEvents = listData.recent_events || rollupData.recent_events || [];
    state.pageInfo = listData.page_info || state.pageInfo;
    state.message = state.backendConfigured
      ? `Runtime corps backend configured. Current live runtime agents: ${fmtNumber(state.rollup ? state.rollup.current_live_runtime_agents : 0)}.`
      : backendUnavailableMessage;
    if (!state.selectedDepartmentId && state.departments.length) {
      state.selectedDepartmentId = state.departments[0].department_id;
    }
    renderAll();
  }

  async function refreshData() {
    try {
      await fetchCorpsData();
    } catch (error) {
      if (error && error.message === "BACKEND_UNAVAILABLE") {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }
      setMessage("Runtime corps refresh failed.");
    }
  }

  async function submitAction(url, payload, successMessage) {
    const response = await requestJson(url, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
      throw new Error(data && data.error ? data.error : "Request failed");
    }

    setMessage(successMessage);
    await refreshData();
    return data;
  }

  async function exportState() {
    const snapshot = {
      backend_configured: state.backendConfigured,
      backend_status: state.backendStatus,
      caps: state.caps,
      rollup: state.rollup,
      departments: state.departments,
      active_cohorts: state.activeCohorts,
      recent_events: state.recentEvents,
      page_info: state.pageInfo,
      filters: state.filters,
    };

    const json = JSON.stringify(snapshot, null, 2);
    const link = document.createElement("a");
    link.href = `data:application/json;charset=utf-8,${encodeURIComponent(json)}`;
    link.download = "runtime-corps-state.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  function bindEvents() {
    el.refreshButton.addEventListener("click", () => {
      refreshData();
    });

    el.exportButton.addEventListener("click", () => {
      exportState();
    });

    el.applyFiltersButton.addEventListener("click", (event) => {
      event.preventDefault();
      state.filters.search = el.searchInput.value.trim();
      state.filters.status = el.statusFilter.value.trim();
      state.filters.lane = el.laneFilter.value.trim();
      state.pageInfo.offset = 0;
      refreshData();
    });

    el.prevPageButton.addEventListener("click", () => {
      state.pageInfo.offset = Math.max(0, state.pageInfo.offset - state.pageInfo.limit);
      refreshData();
    });

    el.nextPageButton.addEventListener("click", () => {
      state.pageInfo.offset += state.pageInfo.limit;
      refreshData();
    });

    el.departmentSelect.addEventListener("change", () => {
      syncSelectedDepartment(el.departmentSelect.value);
    });

    document.addEventListener("click", (event) => {
      const selectButton = event.target.closest(".select-department-button");
      if (selectButton) {
        syncSelectedDepartment(selectButton.dataset.departmentId || "");
        return;
      }

      const deactivateCohortButton = event.target.closest(".deactivate-cohort-row-button");
      if (deactivateCohortButton) {
        syncSelectedDepartment(deactivateCohortButton.dataset.departmentId || "");
        el.cohortIdInput.value = deactivateCohortButton.dataset.cohortId || "";
      }
    });

    el.activationForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitAction(ENDPOINTS.activateDepartment, {
          department_id: el.activationDepartmentId.value.trim(),
          requested_agent_count: Number(el.activationCount.value),
          actor: el.activationActor.value.trim(),
          reason: el.activationReason.value.trim(),
        }, "Department-gated cohort activated.");
      } catch (error) {
        setMessage(error.message || "Cohort activation failed.");
      }
    });

    el.cohortDeactivationForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitAction(ENDPOINTS.deactivateCohort, {
          cohort_id: el.cohortIdInput.value.trim(),
          actor: el.cohortActorInput.value.trim(),
          reason: el.cohortReasonInput.value.trim(),
        }, "Cohort deactivated.");
      } catch (error) {
        setMessage(error.message || "Cohort deactivation failed.");
      }
    });

    el.departmentDeactivationForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitAction(ENDPOINTS.deactivateDepartment, {
          department_id: el.departmentDeactivateInput.value.trim(),
          actor: el.departmentDeactivateActor.value.trim(),
          reason: el.departmentDeactivateReason.value.trim(),
        }, "Department cohorts deactivated.");
      } catch (error) {
        setMessage(error.message || "Department deactivation failed.");
      }
    });

    el.heartbeatForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitAction(ENDPOINTS.heartbeat, {
          actor: el.heartbeatActor.value.trim(),
          reason: el.heartbeatReason.value.trim(),
        }, "Runtime corps heartbeat recorded.");
      } catch (error) {
        setMessage(error.message || "Heartbeat failed.");
      }
    });

    el.noteForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await submitAction(ENDPOINTS.note, {
          department_id: el.noteDepartmentId.value.trim(),
          note_type: el.noteType.value.trim(),
          note_body: el.noteBody.value.trim(),
          actor: el.noteActor.value.trim(),
        }, "Readiness note created.");
      } catch (error) {
        setMessage(error.message || "Readiness note failed.");
      }
    });
  }

  bindEvents();
  renderAll();
  refreshData();
})();
