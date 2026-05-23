(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-division",
    activateDivision: "/.netlify/functions/activate-runtime-division",
    deactivateDivision: "/.netlify/functions/deactivate-runtime-division",
    activateSubdivision: "/.netlify/functions/activate-division-subdivision",
    deactivateSubdivision: "/.netlify/functions/deactivate-division-subdivision",
    activateLane: "/.netlify/functions/activate-division-lane",
    deactivateLane: "/.netlify/functions/deactivate-division-lane",
    heartbeat: "/.netlify/functions/division-heartbeat",
    readinessNote: "/.netlify/functions/create-division-readiness-note",
  };

  const backendUnavailableMessage = "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    divisionRollup: null,
    subdivisionRollups: [],
    laneRollups: [],
    subdivisions: [],
    lanes: [],
    agents: [],
    activationEvents: [],
    heartbeatEvents: [],
    readinessNotes: [],
    auditEvents: [],
    selectedSubdivisionKey: "intake_subdivision",
    selectedLaneKey: "intake_lane_001",
    selectedAgentId: "mvp58_division_agent_0001",
    lastResult: null,
  };

  const ids = {
    backendStatusMessage: "backendStatusMessage",
    backendConnectionState: "backendConnectionState",
    runtimeActivationState: "runtimeActivationState",
    runtimeDivisionSizeState: "runtimeDivisionSizeState",
    liveRuntimeAgentsState: "liveRuntimeAgentsState",
    maxBatchSizeState: "maxBatchSizeState",
    maxChunkSizeState: "maxChunkSizeState",
    activeSubdivisionsState: "activeSubdivisionsState",
    inactiveSubdivisionsState: "inactiveSubdivisionsState",
    activeLanesState: "activeLanesState",
    inactiveLanesState: "inactiveLanesState",
    divisionHealthState: "divisionHealthState",
    heartbeatCountState: "heartbeatCountState",
    readinessNoteCountState: "readinessNoteCountState",
    totalRegisteredAgentsState: "totalRegisteredAgentsState",
    killSwitchState: "killSwitchState",
    divisionRollupSummary: "divisionRollupSummary",
    subdivisionRoster: "subdivisionRoster",
    laneRoster: "laneRoster",
    auditTimeline: "auditTimeline",
    backendUnavailableNotice: "backendUnavailableNotice",
    selectedSubdivisionSelect: "selectedSubdivisionSelect",
    selectedLaneSelect: "selectedLaneSelect",
    selectedAgentSelect: "selectedAgentSelect",
    actorName: "actorName",
    reason: "reason",
    batchSize: "batchSize",
    chunkSize: "chunkSize",
    heartbeatStatus: "heartbeatStatus",
    heartbeatNote: "heartbeatNote",
    noteTitle: "noteTitle",
    noteBody: "noteBody",
    readinessLevel: "readinessLevel",
    currentSelectionSummary: "currentSelectionSummary",
    currentSubdivisionStatus: "currentSubdivisionStatus",
    currentLaneStatus: "currentLaneStatus",
    currentAgentStatus: "currentAgentStatus",
    lastOperation: "lastOperation",
    lastMessage: "lastMessage",
    lastResponse: "lastResponse",
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
    });
  }

  function setMessage(text, type = "info") {
    const el = byId(ids.backendStatusMessage);
    if (!el) return;
    el.textContent = text;
    el.dataset.state = type;
  }

  function resetCollections() {
    state.backendStatus = null;
    state.config = {};
    state.divisionRollup = null;
    state.subdivisionRollups = [];
    state.laneRollups = [];
    state.subdivisions = [];
    state.lanes = [];
    state.agents = [];
    state.activationEvents = [];
    state.heartbeatEvents = [];
    state.readinessNotes = [];
    state.auditEvents = [];
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    resetCollections();
    const notice = byId(ids.backendUnavailableNotice);
    if (notice) {
      notice.hidden = false;
      notice.classList.remove("hidden");
      notice.textContent = message;
    }
    renderAll();
  }

  function setBackendReady(payload) {
    state.backendConfigured = true;
    state.backendStatus = payload.backend_status || {};
    state.config = payload.config || {};
    state.divisionRollup = payload.division_rollup || null;
    state.subdivisionRollups = payload.subdivision_rollups || [];
    state.laneRollups = payload.lane_rollups || [];
    state.subdivisions = payload.subdivisions || [];
    state.lanes = payload.lanes || [];
    state.agents = payload.agents || [];
    state.activationEvents = payload.activation_events || [];
    state.heartbeatEvents = payload.heartbeat_events || [];
    state.readinessNotes = payload.readiness_notes || [];
    state.auditEvents = payload.audit_events || [];
    const notice = byId(ids.backendUnavailableNotice);
    if (notice) {
      notice.hidden = true;
      notice.classList.add("hidden");
    }
    if (!state.selectedSubdivisionKey && state.subdivisions.length) {
      state.selectedSubdivisionKey = state.subdivisions[0].subdivision_key;
    }
    if (!state.selectedLaneKey && state.lanes.length) {
      state.selectedLaneKey = state.lanes[0].lane_key;
    }
    if (!state.selectedAgentId && state.agents.length) {
      state.selectedAgentId = state.agents[0].agent_id;
    }
    renderAll();
  }

  function getSelectedSubdivision() {
    const select = byId(ids.selectedSubdivisionSelect);
    if (select && select.value) {
      state.selectedSubdivisionKey = select.value;
    }
    return state.subdivisionRollups.find((item) => item.subdivision_key === state.selectedSubdivisionKey) || state.subdivisionRollups[0] || null;
  }

  function getSelectedLane() {
    const select = byId(ids.selectedLaneSelect);
    if (select && select.value) {
      state.selectedLaneKey = select.value;
    }
    return state.laneRollups.find((item) => item.lane_key === state.selectedLaneKey) || state.laneRollups[0] || null;
  }

  function getSelectedAgent() {
    const select = byId(ids.selectedAgentSelect);
    if (select && select.value) {
      state.selectedAgentId = select.value;
    }
    return state.agents.find((item) => item.agent_id === state.selectedAgentId) || state.agents[0] || null;
  }

  function renderBackendPanel() {
    const backend = state.backendStatus || {};
    const rollup = state.divisionRollup || {};
    byId(ids.backendConnectionState).textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    byId(ids.runtimeActivationState).textContent = state.backendStatus ? String(Boolean(backend.runtime_activation_started)) : "false";
    byId(ids.runtimeDivisionSizeState).textContent = state.backendStatus ? String(Number(backend.runtime_division_size || 1000)) : "1,000";
    byId(ids.liveRuntimeAgentsState).textContent = state.backendStatus ? `${Number(backend.live_runtime_agents_enabled || 0)} of 1,000` : "0 of 1,000";
    byId(ids.maxBatchSizeState).textContent = state.backendStatus ? String(Number(backend.max_activation_batch_size || 1000)) : "1,000";
    byId(ids.maxChunkSizeState).textContent = state.backendStatus ? String(Number(backend.max_operation_chunk_size || 100)) : "100";
    byId(ids.activeSubdivisionsState).textContent = state.backendStatus ? `${Number(backend.active_subdivisions_count || 0)} of 10` : "0 of 10";
    byId(ids.inactiveSubdivisionsState).textContent = state.backendStatus ? `${Number(backend.inactive_subdivisions_count || 10)} of 10` : "10 of 10";
    byId(ids.activeLanesState).textContent = state.backendStatus ? `${Number(backend.active_lanes_count || 0)} of 100` : "0 of 100";
    byId(ids.inactiveLanesState).textContent = state.backendStatus ? `${Number(backend.inactive_lanes_count || 100)} of 100` : "100 of 100";
    byId(ids.divisionHealthState).textContent = rollup.division_health || "inactive";
    byId(ids.heartbeatCountState).textContent = String(state.heartbeatEvents.length);
    byId(ids.readinessNoteCountState).textContent = String(state.readinessNotes.length);
    byId(ids.totalRegisteredAgentsState).textContent = state.backendStatus ? String(Number(backend.total_registered_agents || 47979)) : "47,979";
    byId(ids.killSwitchState).textContent = state.backendStatus && backend.kill_switch_visible ? "Visible" : "Visible";
    byId(ids.divisionRollupSummary).textContent = state.divisionRollup
      ? `Division health ${rollup.division_health || "inactive"} · ${rollup.active_agents || 0} active agents · ${rollup.inactive_agents || 1000} inactive agents · ${rollup.active_subdivisions || 0} active subdivisions · ${rollup.active_lanes || 0} active lanes · ${rollup.heartbeat_event_count || 0} heartbeats · ${rollup.readiness_note_count || 0} readiness notes`
      : "Loading division rollup...";
  }

  function renderSelects() {
    const subdivisionSelect = byId(ids.selectedSubdivisionSelect);
    const laneSelect = byId(ids.selectedLaneSelect);
    const agentSelect = byId(ids.selectedAgentSelect);

    if (subdivisionSelect) {
      subdivisionSelect.innerHTML = state.subdivisionRollups
        .map((item) => `<option value="${escapeHtml(item.subdivision_key)}">${escapeHtml(item.subdivision_name || item.subdivision_key)}</option>`)
        .join("");
      subdivisionSelect.value = state.selectedSubdivisionKey || (state.subdivisionRollups[0] && state.subdivisionRollups[0].subdivision_key) || "";
    }

    if (laneSelect) {
      laneSelect.innerHTML = state.laneRollups
        .map((item) => `<option value="${escapeHtml(item.lane_key)}">${escapeHtml(item.lane_name || item.lane_key)}</option>`)
        .join("");
      laneSelect.value = state.selectedLaneKey || (state.laneRollups[0] && state.laneRollups[0].lane_key) || "";
    }

    if (agentSelect) {
      agentSelect.innerHTML = state.agents
        .map((item) => `<option value="${escapeHtml(item.agent_id)}">${escapeHtml(item.agent_id)} - ${escapeHtml(item.agent_name || item.agent_id)}</option>`)
        .join("");
      agentSelect.value = state.selectedAgentId || (state.agents[0] && state.agents[0].agent_id) || "";
    }
  }

  function renderCurrentScope() {
    const subdivision = getSelectedSubdivision();
    const lane = getSelectedLane();
    const agent = getSelectedAgent();

    const summary = byId(ids.currentSelectionSummary);
    const subdivisionStatus = byId(ids.currentSubdivisionStatus);
    const laneStatus = byId(ids.currentLaneStatus);
    const agentStatus = byId(ids.currentAgentStatus);

    if (summary) {
      summary.textContent = subdivision
        ? `Selected subdivision ${subdivision.subdivision_name || subdivision.subdivision_key}, lane ${lane ? lane.lane_name || lane.lane_key : "n/a"}, agent ${agent ? agent.agent_id : "n/a"}.`
        : "No division scope has been selected yet.";
    }

    if (subdivisionStatus) {
      subdivisionStatus.textContent = subdivision
        ? `${subdivision.subdivision_name || subdivision.subdivision_key} is ${subdivision.subdivision_health || "inactive"} with ${subdivision.active_agents || 0} active agents across ${subdivision.active_lanes || 0} active lanes.`
        : "Subdivision details will appear here.";
    }

    if (laneStatus) {
      laneStatus.textContent = lane
        ? `${lane.lane_name || lane.lane_key} is ${lane.lane_health || "inactive"} with ${lane.active_agents || 0} active agents and ${lane.heartbeat_count || 0} heartbeats.`
        : "Lane details will appear here.";
    }

    if (agentStatus) {
      agentStatus.textContent = agent
        ? `${agent.agent_id} is ${agent.status || "inactive"} and remains audit-only, heartbeat-only, and readiness-note-only.`
        : "Agent details will appear here.";
    }
  }

  function renderRoster() {
    const subdivisionRoster = byId(ids.subdivisionRoster);
    const laneRoster = byId(ids.laneRoster);

    if (subdivisionRoster) {
      subdivisionRoster.innerHTML = state.subdivisionRollups.length
        ? state.subdivisionRollups
            .map((item) => `
              <article class="timeline-item">
                <div class="timeline-step">${escapeHtml(String(item.subdivision_order || 0).padStart(2, "0"))}</div>
                <div>
                  <h3>${escapeHtml(item.subdivision_name || item.subdivision_key)}</h3>
                  <p>${escapeHtml(item.subdivision_health || "inactive")} · ${escapeHtml(String(item.active_agents || 0))} active agents · ${escapeHtml(String(item.active_lanes || 0))} active lanes · ${escapeHtml(String(item.heartbeat_count || 0))} heartbeats · ${escapeHtml(String(item.readiness_note_count || 0))} readiness notes</p>
                </div>
              </article>
            `)
            .join("")
        : '<div class="empty-state">No subdivision rollups loaded yet.</div>';
    }

    if (laneRoster) {
      laneRoster.innerHTML = state.laneRollups.length
        ? state.laneRollups
            .map((item) => `
              <article class="timeline-item">
                <div class="timeline-step">${escapeHtml(String(item.lane_order || 0).padStart(3, "0"))}</div>
                <div>
                  <h3>${escapeHtml(item.lane_name || item.lane_key)}</h3>
                  <p>${escapeHtml(item.lane_health || "inactive")} · ${escapeHtml(String(item.active_agents || 0))} active agents · ${escapeHtml(String(item.heartbeat_count || 0))} heartbeats · ${escapeHtml(String(item.readiness_note_count || 0))} readiness notes</p>
                </div>
              </article>
            `)
            .join("")
        : '<div class="empty-state">No lane rollups loaded yet.</div>';
    }
  }

  function renderAuditTimeline() {
    const timeline = byId(ids.auditTimeline);
    if (!timeline) return;

    const items = (state.auditEvents || []).slice(0, 20);
    if (!items.length) {
      timeline.innerHTML = '<div class="empty-state">No audit events yet.</div>';
      return;
    }

    timeline.innerHTML = items
      .map((event) => `
        <article class="timeline-item">
          <div class="timeline-step">${escapeHtml(fmtDate(event.created_at || event.timestamp)).slice(0, 12)}</div>
          <div>
            <h3>${escapeHtml(event.event_type || "AUDIT_EVENT")}</h3>
            <p>${escapeHtml(event.event_summary || "No summary")}</p>
            <p class="hint">${escapeHtml(event.subdivision_key || "division")} · ${escapeHtml(event.lane_key || "n/a")} · ${escapeHtml(event.agent_id || "n/a")} · ${escapeHtml(fmtDate(event.created_at || event.timestamp))}</p>
          </div>
        </article>
      `)
      .join("");
  }

  function renderResultPanel() {
    const op = byId(ids.lastOperation);
    const msg = byId(ids.lastMessage);
    const pre = byId(ids.lastResponse);
    const result = state.lastResult || {};
    if (op) op.textContent = result.operation ? `Last operation: ${result.operation}` : "No action submitted yet.";
    if (msg) msg.textContent = result.message || "Use the controls above to submit a controlled runtime action.";
    if (pre) pre.textContent = JSON.stringify(result.payload || {}, null, 2);
  }

  function renderAll() {
    renderBackendPanel();
    renderSelects();
    renderCurrentScope();
    renderRoster();
    renderAuditTimeline();
    renderResultPanel();
  }

  function getFormValues() {
    return {
      actor_name: byId(ids.actorName)?.value || "operator",
      reason: byId(ids.reason)?.value || "Controlled runtime division action",
      batch_size: Number(byId(ids.batchSize)?.value || 1000),
      chunk_size: Number(byId(ids.chunkSize)?.value || 100),
      heartbeat_status: byId(ids.heartbeatStatus)?.value || "healthy",
      heartbeat_note: byId(ids.heartbeatNote)?.value || "Division heartbeat received.",
      note_title: byId(ids.noteTitle)?.value || "Division readiness note",
      note_body: byId(ids.noteBody)?.value || "Division readiness note for controlled runtime scaling.",
      readiness_level: byId(ids.readinessLevel)?.value || "green",
      subdivision_key: state.selectedSubdivisionKey,
      lane_key: state.selectedLaneKey,
      agent_id: state.selectedAgentId,
    };
  }

  async function refreshData(silent = false) {
    if (!silent) {
      setMessage("Loading runtime division backend status...", "info");
    }

    try {
      const response = await requestJson(ENDPOINTS.list, { method: "GET" });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload && payload.error ? payload.error : "Runtime division list failed.");
      }

      if (payload.backend_configured) {
        setBackendReady(payload);
        setMessage("Runtime division backend connected and responding.", "success");
      } else {
        setBackendUnavailable(backendUnavailableMessage);
      }
    } catch (error) {
      const message = error && error.message ? error.message : "Runtime division backend failed.";
      if (message.includes("not configured") || message.includes("503")) {
        setBackendUnavailable(backendUnavailableMessage);
        setMessage(backendUnavailableMessage, "warning");
      } else {
        state.lastResult = {
          operation: "refresh",
          message,
          payload: { ok: false, error: message },
        };
        renderResultPanel();
        setMessage(message, "error");
      }
    }
  }

  function buildActionPayload(kind) {
    const values = getFormValues();
    switch (kind) {
      case "activate-division-full":
        return { actor_name: values.actor_name, reason: values.reason, batch_size: 1000, chunk_size: 100 };
      case "deactivate-division-full":
        return { actor_name: values.actor_name, reason: values.reason, batch_size: 1000, chunk_size: 100 };
      case "activate-subdivision":
      case "deactivate-subdivision":
        return { actor_name: values.actor_name, reason: values.reason, subdivision_key: values.subdivision_key, batch_size: 100, chunk_size: 100 };
      case "activate-lane":
      case "deactivate-lane":
        return { actor_name: values.actor_name, reason: values.reason, lane_key: values.lane_key, batch_size: 10, chunk_size: 100 };
      case "activate-agent":
      case "deactivate-agent":
        return { actor_name: values.actor_name, reason: values.reason, agent_id: values.agent_id, batch_size: 1, chunk_size: 1 };
      case "heartbeat-division":
        return { scope: "division", actor_name: values.actor_name, heartbeat_status: values.heartbeat_status, heartbeat_note: values.heartbeat_note };
      case "heartbeat-subdivision":
        return { scope: "subdivision", subdivision_key: values.subdivision_key, actor_name: values.actor_name, heartbeat_status: values.heartbeat_status, heartbeat_note: values.heartbeat_note };
      case "heartbeat-lane":
        return { scope: "lane", lane_key: values.lane_key, actor_name: values.actor_name, heartbeat_status: values.heartbeat_status, heartbeat_note: values.heartbeat_note };
      case "create-readiness-note":
        return {
          scope: values.subdivision_key ? "subdivision" : "division",
          subdivision_key: values.subdivision_key,
          lane_key: values.lane_key,
          agent_id: values.agent_id,
          actor_name: values.actor_name,
          note_title: values.note_title,
          note_body: values.note_body,
          readiness_level: values.readiness_level,
        };
      default:
        return { actor_name: values.actor_name, reason: values.reason };
    }
  }

  function actionEndpoint(kind) {
    switch (kind) {
      case "activate-division-full":
      case "activate-agent":
        return ENDPOINTS.activateDivision;
      case "deactivate-division-full":
      case "deactivate-agent":
        return ENDPOINTS.deactivateDivision;
      case "activate-subdivision":
        return ENDPOINTS.activateSubdivision;
      case "deactivate-subdivision":
        return ENDPOINTS.deactivateSubdivision;
      case "activate-lane":
        return ENDPOINTS.activateLane;
      case "deactivate-lane":
        return ENDPOINTS.deactivateLane;
      case "heartbeat-division":
      case "heartbeat-subdivision":
      case "heartbeat-lane":
        return ENDPOINTS.heartbeat;
      case "create-readiness-note":
        return ENDPOINTS.readinessNote;
      default:
        return ENDPOINTS.list;
    }
  }

  async function executeAction(kind) {
    if (kind === "refresh") {
      await refreshData();
      return;
    }

    const endpoint = actionEndpoint(kind);
    const payload = buildActionPayload(kind);

    try {
      setMessage(`Running ${kind}...`, "info");
      const response = await requestJson(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      state.lastResult = {
        operation: kind,
        message: body && body.blocked
          ? body.reason || body.error || "Request blocked."
          : body && body.ok
            ? "Request completed."
            : body && body.error
              ? body.error
              : "Request completed.",
        payload: body,
      };
      renderResultPanel();
      if (!response.ok && response.status !== 409) {
        throw new Error(body && body.error ? body.error : "Request failed.");
      }
      setMessage(body && body.blocked ? `Blocked: ${body.reason || body.error}` : `${kind} completed.`, body && body.blocked ? "warning" : "success");
      await refreshData(true);
    } catch (error) {
      const message = error && error.message ? error.message : "Request failed.";
      state.lastResult = {
        operation: kind,
        message,
        payload: { ok: false, error: message },
      };
      renderResultPanel();
      setMessage(message, "error");
    }
  }

  function bindActions() {
    document.querySelectorAll("[data-runtime-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.getAttribute("data-runtime-action");
        executeAction(action);
      });
    });

    [ids.selectedSubdivisionSelect, ids.selectedLaneSelect, ids.selectedAgentSelect].forEach((id) => {
      const select = byId(id);
      if (select) {
        select.addEventListener("change", () => {
          renderCurrentScope();
          renderRoster();
        });
      }
    });
  }

  bindActions();
  refreshData();
})();
