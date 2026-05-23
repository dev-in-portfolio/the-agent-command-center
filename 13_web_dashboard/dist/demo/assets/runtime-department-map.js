(() => {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-departments",
    detail: "/.netlify/functions/get-runtime-department",
    assign: "/.netlify/functions/assign-department-runtime-lane",
    readiness: "/.netlify/functions/update-department-readiness",
    note: "/.netlify/functions/create-department-readiness-note",
    rollup: "/.netlify/functions/department-runtime-rollup",
  };

  const backendUnavailableMessage = "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    rollup: null,
    config: {},
    departments: [],
    laneOptions: [],
    subdivisionOptions: [],
    pageInfo: { limit: 100, offset: 0, returned: 0, total_filtered_departments: 0, total_departments: 1777 },
    filters: { search: "", status: "", family: "", unit: "", lane: "" },
    selectedDepartmentId: "",
    selectedDepartmentDetail: null,
    selectedDepartmentSummary: null,
  };

  const ids = {
    backendStatusMessage: "backendStatusMessage",
    backendConnectionState: "backendConnectionState",
    runtimeMappingReadyState: "runtimeMappingReadyState",
    liveRuntimeAgentsSummaryState: "liveRuntimeAgentsSummaryState",
    totalRegisteredAgentsState: "totalRegisteredAgentsState",
    totalDepartmentsState: "totalDepartmentsState",
    totalUnitsState: "totalUnitsState",
    totalFamiliesState: "totalFamiliesState",
    mappingStatusState: "mappingStatusState",
    mappedDepartmentsState: "mappedDepartmentsState",
    liveRuntimeAgentsState: "liveRuntimeAgentsState",
    killSwitchState: "killSwitchState",
    backendUnavailableNotice: "backendUnavailableNotice",
    rollupMappedDepartmentsState: "rollupMappedDepartmentsState",
    rollupReadinessReviewState: "rollupReadinessReviewState",
    rollupEligibleState: "rollupEligibleState",
    rollupBlockedState: "rollupBlockedState",
    rollupDisabledState: "rollupDisabledState",
    rollupNotesState: "rollupNotesState",
    rollupEventsState: "rollupEventsState",
    departmentSearchInput: "departmentSearchInput",
    statusFilterSelect: "statusFilterSelect",
    familyFilterInput: "familyFilterInput",
    unitFilterInput: "unitFilterInput",
    laneFilterInput: "laneFilterInput",
    pageSizeSelect: "pageSizeSelect",
    searchDepartmentsButton: "searchDepartmentsButton",
    refreshRollupButton: "refreshRollupButton",
    resetFiltersButton: "resetFiltersButton",
    exportMappingButton: "exportMappingButton",
    departmentPageSummary: "departmentPageSummary",
    departmentTableBody: "departmentTableBody",
    previousPageButton: "previousPageButton",
    nextPageButton: "nextPageButton",
    selectedDepartmentSummary: "selectedDepartmentSummary",
    selectedDepartmentId: "selectedDepartmentId",
    selectedDepartmentName: "selectedDepartmentName",
    selectedDepartmentFamily: "selectedDepartmentFamily",
    selectedDepartmentUnit: "selectedDepartmentUnit",
    selectedDepartmentLane: "selectedDepartmentLane",
    selectedDepartmentSubdivision: "selectedDepartmentSubdivision",
    selectedDepartmentStatus: "selectedDepartmentStatus",
    selectedDepartmentEligibility: "selectedDepartmentEligibility",
    selectedDepartmentAudit: "selectedDepartmentAudit",
    selectedDepartmentNotes: "selectedDepartmentNotes",
    selectedDepartmentLastUpdate: "selectedDepartmentLastUpdate",
    selectedDepartmentUnits: "selectedDepartmentUnits",
    selectedDepartmentTimeline: "selectedDepartmentTimeline",
    assignDepartmentId: "assignDepartmentId",
    assignLaneSelect: "assignLaneSelect",
    assignSubdivisionSelect: "assignSubdivisionSelect",
    assignCapacityInput: "assignCapacityInput",
    assignActorInput: "assignActorInput",
    assignLaneButton: "assignLaneButton",
    readinessDepartmentId: "readinessDepartmentId",
    readinessStatusSelect: "readinessStatusSelect",
    readinessEligibleSelect: "readinessEligibleSelect",
    readinessReasonInput: "readinessReasonInput",
    readinessActorInput: "readinessActorInput",
    updateReadinessButton: "updateReadinessButton",
    noteDepartmentId: "noteDepartmentId",
    noteTypeInput: "noteTypeInput",
    noteBodyInput: "noteBodyInput",
    noteActorInput: "noteActorInput",
    createNoteButton: "createNoteButton",
    rollupTotalDepartmentsState: "rollupTotalDepartmentsState",
    rollupMappedDepartmentsState2: "rollupMappedDepartmentsState2",
    rollupReadinessReviewState2: "rollupReadinessReviewState2",
    rollupEligibleState2: "rollupEligibleState2",
    rollupBlockedState2: "rollupBlockedState2",
    rollupDisabledState2: "rollupDisabledState2",
    rollupHeartbeatCountState: "rollupHeartbeatCountState",
    rollupReadinessNoteCountState: "rollupReadinessNoteCountState",
    rollupAuditEventCountState: "rollupAuditEventCountState",
  };

  function byId(id) {
    return document.getElementById(id);
  }

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

  function requestJson(url, options = {}) {
    return fetch(url, {
      ...options,
      headers: {
        "content-type": "application/json",
        ...(options.headers || {}),
      },
    }).then(async (response) => {
      const contentType = response.headers.get("content-type") || "";
      const payload = contentType.includes("application/json") ? await response.json() : { raw: await response.text() };
      if (!response.ok) {
        const error = new Error(payload && payload.error ? payload.error : response.statusText);
        error.status = response.status;
        error.payload = payload;
        throw error;
      }
      return payload;
    });
  }

  function setMessage(text, type = "info") {
    const el = byId(ids.backendStatusMessage);
    if (!el) return;
    el.textContent = text;
    el.dataset.state = type;
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    const notice = byId(ids.backendUnavailableNotice);
    if (notice) {
      notice.hidden = false;
      notice.textContent = message;
    }
    renderShell();
  }

  function setBackendReady(payload) {
    state.backendConfigured = true;
    state.backendStatus = payload.backend_status || {};
    state.rollup = payload.rollup || null;
    state.config = payload.config || {};
    state.departments = payload.departments || [];
    state.pageInfo = payload.page_info || state.pageInfo;
    state.filters = payload.filters || state.filters;
    state.laneOptions = payload.lane_options || [];
    state.subdivisionOptions = payload.subdivision_options || [];
    const notice = byId(ids.backendUnavailableNotice);
    if (notice) {
      notice.hidden = true;
    }
    syncFilterInputs();
    syncLaneOptions();
    renderShell();
  }

  function syncFilterInputs() {
    const filters = state.filters || {};
    if (byId(ids.departmentSearchInput)) byId(ids.departmentSearchInput).value = filters.search || "";
    if (byId(ids.statusFilterSelect)) byId(ids.statusFilterSelect).value = filters.status || "";
    if (byId(ids.familyFilterInput)) byId(ids.familyFilterInput).value = filters.family || "";
    if (byId(ids.unitFilterInput)) byId(ids.unitFilterInput).value = filters.unit || "";
    if (byId(ids.laneFilterInput)) byId(ids.laneFilterInput).value = filters.lane || "";
    if (byId(ids.pageSizeSelect)) byId(ids.pageSizeSelect).value = String(state.pageInfo.limit || 100);
  }

  function syncLaneOptions() {
    const laneSelect = byId(ids.assignLaneSelect);
    const subdivisionSelect = byId(ids.assignSubdivisionSelect);
    if (laneSelect) {
      laneSelect.innerHTML = state.laneOptions.map((lane) => `<option value="${escapeHtml(lane.runtime_lane_id)}">${escapeHtml(lane.runtime_lane_name)} (${escapeHtml(lane.runtime_lane_id)})</option>`).join("");
    }
    if (subdivisionSelect) {
      subdivisionSelect.innerHTML = state.subdivisionOptions.map((subdivision) => `<option value="${escapeHtml(subdivision.subdivision_id)}">${escapeHtml(subdivision.subdivision_name)} (${escapeHtml(subdivision.subdivision_id)})</option>`).join("");
    }
    if (state.laneOptions[0]) {
      laneSelect && (laneSelect.value = laneSelect.value || state.laneOptions[0].runtime_lane_id);
    }
    if (state.subdivisionOptions[0]) {
      subdivisionSelect && (subdivisionSelect.value = subdivisionSelect.value || state.subdivisionOptions[0].subdivision_id);
    }
  }

  function currentFilters() {
    return {
      search: textInput(ids.departmentSearchInput),
      status: textInput(ids.statusFilterSelect),
      family: textInput(ids.familyFilterInput),
      unit: textInput(ids.unitFilterInput),
      lane: textInput(ids.laneFilterInput),
    };
  }

  function textInput(id) {
    const el = byId(id);
    return el ? String(el.value || "").trim() : "";
  }

  function renderShell() {
    renderStatusPanel();
    renderRollupPanel();
    renderDepartmentTable();
    renderDepartmentSummary();
    renderSelectedDepartment();
    renderDepartmentTimeline();
    renderPagination();
  }

  function renderStatusPanel() {
    const backend = state.backendStatus || {};
    byId(ids.backendConnectionState).textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    byId(ids.runtimeMappingReadyState).textContent = state.backendStatus ? String(Boolean(backend.full_department_runtime_mapping_ready || backend.runtime_department_mapping_ready)) : "false";
    byId(ids.liveRuntimeAgentsSummaryState).textContent = state.backendStatus ? `${Number(backend.live_runtime_agents_enabled || 0)} of 1,000` : "0 of 1,000";
    byId(ids.totalRegisteredAgentsState).textContent = state.backendStatus ? String(Number(backend.total_registered_agents || 47979)) : "47,979";
    byId(ids.totalDepartmentsState).textContent = state.backendStatus ? String(Number(backend.total_departments || 1777)) : "1,777";
    byId(ids.totalUnitsState).textContent = state.backendStatus ? String(Number(backend.total_units || 5331)) : "5,331";
    byId(ids.totalFamiliesState).textContent = state.backendStatus ? String(Number(backend.total_families || 175)) : "175";
    byId(ids.mappingStatusState).textContent = state.backendStatus ? "Ready" : "Loading";
    byId(ids.mappedDepartmentsState).textContent = state.rollup ? String(Number(state.rollup.mapped_departments || 1777)) : "1,777";
    byId(ids.liveRuntimeAgentsState).textContent = state.backendStatus ? `${Number(backend.live_runtime_agents_enabled || 0)}–1,000` : "0–1,000";
    byId(ids.killSwitchState).textContent = state.backendStatus && backend.kill_switch_visible ? "Visible" : "Visible";
    if (state.backendStatus) {
      byId(ids.backendStatusMessage).textContent = `Runtime department backend ready. Live runtime agents enabled: ${Number(backend.live_runtime_agents_enabled || 0)} of 1,000.`;
    }
  }

  function renderRollupPanel() {
    const rollup = state.rollup || {};
    byId(ids.rollupMappedDepartmentsState).textContent = String(Number(rollup.mapped_departments || 1777));
    byId(ids.rollupReadinessReviewState).textContent = String(Number(rollup.readiness_review_departments || 0));
    byId(ids.rollupEligibleState).textContent = String(Number(rollup.eligible_departments || 0));
    byId(ids.rollupBlockedState).textContent = String(Number(rollup.blocked_departments || 0));
    byId(ids.rollupDisabledState).textContent = String(Number(rollup.disabled_departments || 0));
    byId(ids.rollupNotesState).textContent = String(Number(state.rollup && state.rollup.notes_count ? state.rollup.notes_count : 0));
    byId(ids.rollupEventsState).textContent = String(Number(state.rollup && state.rollup.events_count ? state.rollup.events_count : 0));
    byId(ids.rollupTotalDepartmentsState).textContent = String(Number(rollup.total_departments || 1777));
    byId(ids.rollupMappedDepartmentsState2).textContent = String(Number(rollup.mapped_departments || 1777));
    byId(ids.rollupReadinessReviewState2).textContent = String(Number(rollup.readiness_review_departments || 0));
    byId(ids.rollupEligibleState2).textContent = String(Number(rollup.eligible_departments || 0));
    byId(ids.rollupBlockedState2).textContent = String(Number(rollup.blocked_departments || 0));
    byId(ids.rollupDisabledState2).textContent = String(Number(rollup.disabled_departments || 0));
    byId(ids.rollupHeartbeatCountState).textContent = String(Number(state.rollup && state.rollup.heartbeat_count ? state.rollup.heartbeat_count : 0));
    byId(ids.rollupReadinessNoteCountState).textContent = String(Number(state.rollup && state.rollup.readiness_note_count ? state.rollup.readiness_note_count : 0));
    byId(ids.rollupAuditEventCountState).textContent = String(Number(state.rollup && state.rollup.audit_event_count ? state.rollup.audit_event_count : 0));
  }

  function renderDepartmentSummary() {
    const summary = byId(ids.departmentPageSummary);
    if (!summary) return;
    if (!state.pageInfo) {
      summary.textContent = "Loading department list...";
      return;
    }
    summary.textContent = `Showing ${Number(state.pageInfo.returned || 0)} of ${Number(state.pageInfo.total_filtered_departments || 0)} filtered departments from ${Number(state.pageInfo.total_departments || 1777)} total.`;
  }

  function renderDepartmentTable() {
    const tbody = byId(ids.departmentTableBody);
    if (!tbody) return;
    if (!state.departments.length) {
      tbody.innerHTML = '<tr><td colspan="12">No departments loaded yet.</td></tr>';
      return;
    }

    tbody.innerHTML = state.departments.map((department) => {
      const selected = department.department_id === state.selectedDepartmentId;
      return `
        <tr class="${selected ? 'is-selected' : ''}">
          <td>${escapeHtml(department.department_id)}</td>
          <td>${escapeHtml(department.family_name || department.family_id || 'n/a')}<br><span class="legal-muted">${escapeHtml(department.department_name)}</span></td>
          <td>${escapeHtml(department.unit_name || department.unit_id || 'n/a')}</td>
          <td>${escapeHtml(String(department.registered_agent_count || 0))}</td>
          <td>${escapeHtml(department.mapped_runtime_lane_name || department.mapped_runtime_lane_id || 'n/a')}</td>
          <td>${escapeHtml(department.mapped_runtime_subdivision_name || department.mapped_runtime_subdivision_id || 'n/a')}</td>
          <td>${escapeHtml(department.runtime_status || 'mapped_readonly')}</td>
          <td>${escapeHtml(String(Boolean(department.activation_eligible)))}</td>
          <td>${escapeHtml(department.audit_status || 'no_audit_events')}</td>
          <td>${escapeHtml(String(department.notes_count || 0))}</td>
          <td>${escapeHtml(fmtDate(department.last_readiness_update))}</td>
          <td><button class="button" type="button" data-action="open-department" data-department-id="${escapeHtml(department.department_id)}">Open</button></td>
        </tr>`;
    }).join('');
  }

  function renderPagination() {
    const prev = byId(ids.previousPageButton);
    const next = byId(ids.nextPageButton);
    if (prev) prev.disabled = Number(state.pageInfo.offset || 0) <= 0;
    if (next) next.disabled = Number(state.pageInfo.offset || 0) + Number(state.pageInfo.limit || 100) >= Number(state.pageInfo.total_filtered_departments || 0);
  }

  function renderSelectedDepartment() {
    const dept = state.selectedDepartmentDetail && state.selectedDepartmentDetail.department;
    if (!dept) {
      byId(ids.selectedDepartmentSummary).textContent = state.selectedDepartmentId ? `Loading ${state.selectedDepartmentId}...` : 'Select a department to inspect lane coverage, readiness, notes, and audit history.';
      byId(ids.selectedDepartmentId).textContent = 'n/a';
      byId(ids.selectedDepartmentName).textContent = 'n/a';
      byId(ids.selectedDepartmentFamily).textContent = 'n/a';
      byId(ids.selectedDepartmentUnit).textContent = 'n/a';
      byId(ids.selectedDepartmentLane).textContent = 'n/a';
      byId(ids.selectedDepartmentSubdivision).textContent = 'n/a';
      byId(ids.selectedDepartmentStatus).textContent = 'n/a';
      byId(ids.selectedDepartmentEligibility).textContent = 'n/a';
      byId(ids.selectedDepartmentAudit).textContent = 'n/a';
      byId(ids.selectedDepartmentNotes).textContent = '0';
      byId(ids.selectedDepartmentLastUpdate).textContent = 'n/a';
      byId(ids.selectedDepartmentUnits).textContent = '';
      return;
    }

    byId(ids.selectedDepartmentSummary).textContent = `Department ${dept.department_id} is mapped to ${dept.mapped_runtime_lane_name || dept.mapped_runtime_lane_id || 'n/a'} and remains read-only until readiness is explicitly updated.`;
    byId(ids.selectedDepartmentId).textContent = dept.department_id || 'n/a';
    byId(ids.selectedDepartmentName).textContent = dept.department_name || 'n/a';
    byId(ids.selectedDepartmentFamily).textContent = `${dept.family_id || 'n/a'} · ${dept.family_name || 'n/a'}`;
    byId(ids.selectedDepartmentUnit).textContent = `${dept.unit_id || 'n/a'} · ${dept.unit_name || 'n/a'}`;
    byId(ids.selectedDepartmentLane).textContent = `${dept.mapped_runtime_lane_id || 'n/a'} · ${dept.mapped_runtime_lane_name || 'n/a'}`;
    byId(ids.selectedDepartmentSubdivision).textContent = `${dept.mapped_runtime_subdivision_id || 'n/a'} · ${dept.mapped_runtime_subdivision_name || 'n/a'}`;
    byId(ids.selectedDepartmentStatus).textContent = dept.runtime_status || 'mapped_readonly';
    byId(ids.selectedDepartmentEligibility).textContent = String(Boolean(dept.activation_eligible));
    byId(ids.selectedDepartmentAudit).textContent = dept.audit_status || 'no_audit_events';
    byId(ids.selectedDepartmentNotes).textContent = String(Number(dept.notes_count || 0));
    byId(ids.selectedDepartmentLastUpdate).textContent = fmtDate(dept.last_readiness_update);
    byId(ids.selectedDepartmentUnits).textContent = `Units: ${(dept.unit_ids || []).join(', ') || 'n/a'} · Unit names: ${(dept.unit_names || []).join(', ') || 'n/a'}`;

    byId(ids.assignDepartmentId).value = dept.department_id || '';
    byId(ids.readinessDepartmentId).value = dept.department_id || '';
    byId(ids.noteDepartmentId).value = dept.department_id || '';
    if (byId(ids.assignCapacityInput) && !byId(ids.assignCapacityInput).value) {
      byId(ids.assignCapacityInput).value = String(Number(dept.registered_agent_count || 27));
    }
    if (byId(ids.readinessStatusSelect)) byId(ids.readinessStatusSelect).value = dept.runtime_status || 'mapped_readonly';
    if (byId(ids.readinessEligibleSelect)) byId(ids.readinessEligibleSelect).value = String(Boolean(dept.activation_eligible));
  }

  function renderDepartmentTimeline() {
    const timeline = byId(ids.departmentEventTimeline);
    const detailTimeline = byId(ids.selectedDepartmentTimeline);
    const dept = state.selectedDepartmentDetail || {};
    const entries = [];
    (dept.readiness_notes || []).forEach((note) => {
      entries.push({
        type: note.note_type || 'readiness_note',
        title: note.note_type || 'readiness_note',
        body: note.note_body || '',
        actor: note.actor || 'n/a',
        created_at: note.created_at,
        badge: 'note',
      });
    });
    (dept.department_events || []).forEach((event) => {
      entries.push({
        type: event.event_type || 'event',
        title: event.event_type || 'event',
        body: event.event_summary || '',
        actor: event.actor || 'n/a',
        created_at: event.created_at,
        badge: 'event',
      });
    });
    entries.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

    const html = entries.length ? entries.slice(0, 25).map((entry) => `
      <article class="runtime-audit-item">
        <h4>${escapeHtml(entry.title)}</h4>
        <p><strong>${escapeHtml(entry.actor)}</strong> · ${escapeHtml(fmtDate(entry.created_at))}</p>
        <p>${escapeHtml(entry.body)}</p>
      </article>`).join('') : '<article class="runtime-audit-item"><h4>No department events yet</h4><p>Select a department to inspect readiness notes and audit events.</p></article>';

    if (timeline) timeline.innerHTML = html;
    if (detailTimeline) detailTimeline.innerHTML = html;
  }

  function loadFiltersFromUi() {
    state.filters = currentFilters();
    state.pageInfo.limit = Number(byId(ids.pageSizeSelect).value || 100);
  }

  function buildQueryParams() {
    const params = new URLSearchParams();
    params.set('limit', String(state.pageInfo.limit || 100));
    params.set('offset', String(state.pageInfo.offset || 0));
    if (state.filters.search) params.set('search', state.filters.search);
    if (state.filters.status) params.set('status', state.filters.status);
    if (state.filters.family) params.set('family', state.filters.family);
    if (state.filters.unit) params.set('unit', state.filters.unit);
    if (state.filters.lane) params.set('lane', state.filters.lane);
    return params;
  }

  async function loadDepartments() {
    try {
      setMessage('Loading department mapping...');
      const payload = await requestJson(`${ENDPOINTS.list}?${buildQueryParams().toString()}`);
      setBackendReady(payload);
      if (!state.selectedDepartmentId && state.departments.length) {
        await selectDepartment(state.departments[0].department_id, { keepSelection: true });
      } else if (state.selectedDepartmentId) {
        const selectedExists = state.departments.some((department) => department.department_id === state.selectedDepartmentId);
        if (!selectedExists && state.departments.length) {
          await selectDepartment(state.departments[0].department_id, { keepSelection: true });
        } else if (selectedExists) {
          await selectDepartment(state.selectedDepartmentId, { keepSelection: true });
        }
      }
      setMessage('Department mapping loaded.', 'success');
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        setMessage('Backend not configured.', 'warning');
        return;
      }
      setMessage(error && error.message ? error.message : 'Failed to load department mapping.', 'danger');
    }
  }

  async function refreshRollup() {
    try {
      setMessage('Refreshing rollup...');
      await requestJson(ENDPOINTS.rollup);
      await loadDepartments();
      setMessage('Rollup refreshed.', 'success');
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        return;
      }
      setMessage(error && error.message ? error.message : 'Failed to refresh rollup.', 'danger');
    }
  }

  async function loadDepartmentDetail(departmentId) {
    if (!departmentId) return;
    try {
      const payload = await requestJson(`${ENDPOINTS.detail}?department_id=${encodeURIComponent(departmentId)}`);
      state.selectedDepartmentDetail = payload;
      renderSelectedDepartment();
      renderDepartmentTimeline();
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        return;
      }
      setMessage(error && error.message ? error.message : `Failed to load department ${departmentId}.`, 'danger');
    }
  }

  async function selectDepartment(departmentId, options = {}) {
    state.selectedDepartmentId = departmentId;
    renderDepartmentTable();
    await loadDepartmentDetail(departmentId);
  }

  function showCurrentSelectionInForms(departmentId) {
    if (!departmentId) return;
    if (byId(ids.assignDepartmentId)) byId(ids.assignDepartmentId).value = departmentId;
    if (byId(ids.readinessDepartmentId)) byId(ids.readinessDepartmentId).value = departmentId;
    if (byId(ids.noteDepartmentId)) byId(ids.noteDepartmentId).value = departmentId;
  }

  async function submitLaneAssignment() {
    const payload = {
      department_id: textInput(ids.assignDepartmentId),
      runtime_lane_id: textInput(ids.assignLaneSelect),
      runtime_subdivision_id: textInput(ids.assignSubdivisionSelect),
      mapped_agent_capacity: textInput(ids.assignCapacityInput),
      actor: textInput(ids.assignActorInput),
    };
    try {
      setMessage('Assigning runtime lane...');
      await requestJson(ENDPOINTS.assign, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setMessage('Runtime lane assigned. Mapping remains non-executing.', 'success');
      await loadDepartments();
      await loadDepartmentDetail(payload.department_id);
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        return;
      }
      setMessage(error && error.message ? error.message : 'Failed to assign runtime lane.', 'danger');
    }
  }

  async function submitReadinessUpdate() {
    const payload = {
      department_id: textInput(ids.readinessDepartmentId),
      runtime_status: textInput(ids.readinessStatusSelect),
      activation_eligible: textInput(ids.readinessEligibleSelect) === 'true',
      actor: textInput(ids.readinessActorInput),
      reason: textInput(ids.readinessReasonInput),
    };
    try {
      setMessage('Updating readiness status...');
      await requestJson(ENDPOINTS.readiness, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setMessage('Readiness status updated. Eligible does not mean executing.', 'success');
      await loadDepartments();
      await loadDepartmentDetail(payload.department_id);
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        return;
      }
      setMessage(error && error.message ? error.message : 'Failed to update readiness.', 'danger');
    }
  }

  async function submitReadinessNote() {
    const payload = {
      department_id: textInput(ids.noteDepartmentId),
      note_type: textInput(ids.noteTypeInput),
      note_body: textInput(ids.noteBodyInput),
      actor: textInput(ids.noteActorInput),
    };
    try {
      setMessage('Creating readiness note...');
      await requestJson(ENDPOINTS.note, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setMessage('Readiness note created.', 'success');
      await loadDepartments();
      await loadDepartmentDetail(payload.department_id);
    } catch (error) {
      if (error && error.status === 503) {
        setBackendUnavailable(error.payload && error.payload.error ? error.payload.error : backendUnavailableMessage);
        return;
      }
      setMessage(error && error.message ? error.message : 'Failed to create readiness note.', 'danger');
    }
  }

  function exportCurrentMappingView() {
    const payload = {
      generated_at: new Date().toISOString(),
      source: 'mvp59_department_runtime_mapping',
      filters: state.filters,
      page_info: state.pageInfo,
      backend_status: state.backendStatus,
      rollup: state.rollup,
      departments: state.departments,
      selected_department_detail: state.selectedDepartmentDetail,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'runtime-department-map-view.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  function resetFilters() {
    byId(ids.departmentSearchInput).value = '';
    byId(ids.statusFilterSelect).value = '';
    byId(ids.familyFilterInput).value = '';
    byId(ids.unitFilterInput).value = '';
    byId(ids.laneFilterInput).value = '';
    byId(ids.pageSizeSelect).value = '100';
    state.pageInfo.limit = 100;
    state.pageInfo.offset = 0;
    state.filters = { search: '', status: '', family: '', unit: '', lane: '' };
    loadDepartments();
  }

  function attachEvents() {
    byId(ids.searchDepartmentsButton).addEventListener('click', () => {
      state.pageInfo.offset = 0;
      loadFiltersFromUi();
      loadDepartments();
    });
    byId(ids.refreshRollupButton).addEventListener('click', () => refreshRollup());
    byId(ids.resetFiltersButton).addEventListener('click', () => resetFilters());
    byId(ids.exportMappingButton).addEventListener('click', () => exportCurrentMappingView());
    byId(ids.previousPageButton).addEventListener('click', () => {
      state.pageInfo.offset = Math.max(Number(state.pageInfo.offset || 0) - Number(state.pageInfo.limit || 100), 0);
      loadDepartments();
    });
    byId(ids.nextPageButton).addEventListener('click', () => {
      state.pageInfo.offset = Number(state.pageInfo.offset || 0) + Number(state.pageInfo.limit || 100);
      loadDepartments();
    });
    byId(ids.assignLaneButton).addEventListener('click', () => submitLaneAssignment());
    byId(ids.updateReadinessButton).addEventListener('click', () => submitReadinessUpdate());
    byId(ids.createNoteButton).addEventListener('click', () => submitReadinessNote());
    byId(ids.departmentTableBody).addEventListener('click', (event) => {
      const button = event.target.closest('[data-action="open-department"]');
      if (!button) return;
      const departmentId = button.getAttribute('data-department-id');
      if (departmentId) {
        state.selectedDepartmentId = departmentId;
        showCurrentSelectionInForms(departmentId);
        loadDepartmentDetail(departmentId);
        renderDepartmentTable();
      }
    });
    [ids.departmentSearchInput, ids.familyFilterInput, ids.unitFilterInput, ids.laneFilterInput].forEach((id) => {
      byId(id).addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          state.pageInfo.offset = 0;
          loadFiltersFromUi();
          loadDepartments();
        }
      });
    });
    byId(ids.statusFilterSelect).addEventListener('change', () => {
      state.pageInfo.offset = 0;
      loadFiltersFromUi();
      loadDepartments();
    });
    byId(ids.pageSizeSelect).addEventListener('change', () => {
      state.pageInfo.limit = Number(byId(ids.pageSizeSelect).value || 100);
      state.pageInfo.offset = 0;
      loadDepartments();
    });
  }

  function boot() {
    attachEvents();
    syncFilterInputs();
    syncLaneOptions();
    loadDepartments();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
