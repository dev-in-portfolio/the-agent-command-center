(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-group",
    activateGroup: "/.netlify/functions/activate-runtime-group",
    deactivateGroup: "/.netlify/functions/deactivate-runtime-group",
    activateLane: "/.netlify/functions/activate-group-lane",
    deactivateLane: "/.netlify/functions/deactivate-group-lane",
    heartbeat: "/.netlify/functions/group-heartbeat",
    readinessNote: "/.netlify/functions/create-group-readiness-note",
  };

  const backendUnavailableMessage = "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    groupRollup: null,
    laneRollups: [],
    lanes: [],
    agents: [],
    activationEvents: [],
    heartbeatEvents: [],
    readinessNotes: [],
    auditEvents: [],
    selectedLaneKey: "intake_lane_01",
    selectedAgentId: "mvp57_group_agent_001",
  };

  const ids = {
    backendStatusMessage: "backendStatusMessage",
    backendConnectionState: "backendConnectionState",
    runtimeActivationState: "runtimeActivationState",
    runtimeGroupSizeState: "runtimeGroupSizeState",
    liveRuntimeAgentsState: "liveRuntimeAgentsState",
    maxBatchSizeState: "maxBatchSizeState",
    activeLanesState: "activeLanesState",
    inactiveLanesState: "inactiveLanesState",
    groupHealthState: "groupHealthState",
    heartbeatCountState: "heartbeatCountState",
    readinessNoteCountState: "readinessNoteCountState",
    totalRegisteredAgentsState: "totalRegisteredAgentsState",
    killSwitchState: "killSwitchState",
    groupRollupSummary: "groupRollupSummary",
    laneRoster: "laneRoster",
    auditTimeline: "auditTimeline",
    backendUnavailableNotice: "backendUnavailableNotice",
    selectedLaneSelect: "selectedLaneSelect",
    selectedAgentSelect: "selectedAgentSelect",
    heartbeatStatus: "heartbeatStatus",
    heartbeatNote: "heartbeatNote",
    readinessTitle: "readinessTitle",
    readinessBody: "readinessBody",
    readinessLevel: "readinessLevel",
    currentLaneStatus: "currentLaneStatus",
    currentLaneMeta: "currentLaneMeta",
    currentAgentMeta: "currentAgentMeta",
    currentAgentPermissions: "currentAgentPermissions",
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

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.config = {};
    state.groupRollup = null;
    state.laneRollups = [];
    state.lanes = [];
    state.agents = [];
    state.activationEvents = [];
    state.heartbeatEvents = [];
    state.readinessNotes = [];
    state.auditEvents = [];
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
    state.groupRollup = payload.group_rollup || null;
    state.laneRollups = payload.lane_rollups || [];
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
    if (!state.selectedLaneKey && state.lanes.length) {
      state.selectedLaneKey = state.lanes[0].lane_key;
    }
    if (!state.selectedAgentId && state.agents.length) {
      state.selectedAgentId = state.agents[0].agent_id;
    }
    renderAll();
  }

  function getSelectedLane() {
    const select = byId(ids.selectedLaneSelect);
    if (select && select.value) {
      state.selectedLaneKey = select.value;
    }
    return state.lanes.find((lane) => lane.lane_key === state.selectedLaneKey) || state.lanes[0] || null;
  }

  function getSelectedAgent() {
    const select = byId(ids.selectedAgentSelect);
    if (select && select.value) {
      state.selectedAgentId = select.value;
    }
    return state.agents.find((agent) => agent.agent_id === state.selectedAgentId) || state.agents[0] || null;
  }

  function getAgentsForLane(laneKey) {
    return state.agents.filter((agent) => agent.lane_key === laneKey);
  }

  function renderBackendPanel() {
    byId(ids.backendConnectionState).textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    byId(ids.runtimeActivationState).textContent = state.backendStatus ? String(Boolean(state.backendStatus.runtime_activation_started)) : "false";
    byId(ids.runtimeGroupSizeState).textContent = state.backendStatus ? String(Number(state.backendStatus.runtime_group_size || 500)) : "500";
    byId(ids.liveRuntimeAgentsState).textContent = state.backendStatus ? `${Number(state.backendStatus.live_runtime_agents_enabled || 0)} of 500` : "0 of 500";
    byId(ids.maxBatchSizeState).textContent = state.backendStatus ? String(Number(state.backendStatus.max_activation_batch_size || 500)) : "500";
    byId(ids.activeLanesState).textContent = state.backendStatus ? `${Number(state.backendStatus.active_lanes_count || 0)} of 50` : "0 of 50";
    byId(ids.inactiveLanesState).textContent = state.backendStatus ? `${Number(state.backendStatus.inactive_lanes_count || 50)} of 50` : "50 of 50";
    byId(ids.groupHealthState).textContent = state.groupRollup ? String(state.groupRollup.group_health || "inactive") : "inactive";
    byId(ids.heartbeatCountState).textContent = String(state.heartbeatEvents.length);
    byId(ids.readinessNoteCountState).textContent = String(state.readinessNotes.length);
    byId(ids.totalRegisteredAgentsState).textContent = state.backendStatus ? String(Number(state.backendStatus.total_registered_agents || 47979)) : "47,979";
    byId(ids.killSwitchState).textContent = state.backendStatus && state.backendStatus.kill_switch_visible ? "visible" : "visible";
    byId(ids.groupRollupSummary).textContent = state.groupRollup
      ? `Group health ${state.groupRollup.group_health || "inactive"} · ${state.groupRollup.active_agents || 0} active agents · ${state.groupRollup.inactive_agents || 0} inactive agents · ${state.groupRollup.active_lanes || 0} active lanes · ${state.groupRollup.inactive_lanes || 0} inactive lanes · ${state.groupRollup.heartbeat_event_count || 0} heartbeats · ${state.groupRollup.readiness_note_count || 0} readiness notes`
      : "Loading group rollup...";
  }

  function renderSelects() {
    const laneSelect = byId(ids.selectedLaneSelect);
    const agentSelect = byId(ids.selectedAgentSelect);
    if (laneSelect) {
      laneSelect.innerHTML = state.lanes.map((lane) => `<option value="${escapeHtml(lane.lane_key)}">${escapeHtml(lane.lane_name || lane.lane_key)}</option>`).join("");
      laneSelect.value = state.selectedLaneKey || (state.lanes[0] && state.lanes[0].lane_key) || "";
    }
    if (agentSelect) {
      agentSelect.innerHTML = state.agents.map((agent) => `<option value="${escapeHtml(agent.agent_id)}">${escapeHtml(agent.agent_id)} - ${escapeHtml(agent.agent_name || agent.agent_id)}</option>`).join("");
      agentSelect.value = state.selectedAgentId || (state.agents[0] && state.agents[0].agent_id) || "";
    }
  }

  function renderLaneRoster() {
    const roster = byId(ids.laneRoster);
    if (!roster) return;

    if (!state.laneRollups.length) {
      roster.innerHTML = '<div class="empty-state">No group lanes loaded yet.</div>';
      return;
    }

    roster.innerHTML = state.laneRollups
      .map((lane) => {
        const laneAgents = getAgentsForLane(lane.lane_key);
        const activeAgents = laneAgents.filter((agent) => agent.status === "active").length;
        const inactiveAgents = laneAgents.length - activeAgents;
        const heartbeatCount = lane.heartbeat_count || state.heartbeatEvents.filter((event) => event.lane_key === lane.lane_key).length;
        const readinessCount = lane.readiness_note_count || state.readinessNotes.filter((note) => note.lane_key === lane.lane_key).length;
        const selected = lane.lane_key === state.selectedLaneKey;
        const agentRange = laneAgents.map((agent) => agent.agent_id).join(", ");
        const healthClass = lane.lane_health === "healthy" ? "success" : lane.lane_health === "partial" ? "warning" : "ghost";
        return `
          <article class="card" data-lane-key="${escapeHtml(lane.lane_key)}">
            <div class="toolbar">
              <div>
                <p class="mini-label">Lane ${escapeHtml(String(lane.lane_order || "n/a"))}</p>
                <strong>${escapeHtml(lane.lane_name || lane.lane_key)}</strong>
              </div>
              <span class="badge ${healthClass}">${escapeHtml(lane.lane_health || "inactive")}</span>
            </div>
            <p class="hint">${escapeHtml(lane.lane_key)}</p>
            <div class="meta-row">
              <span class="badge info">${activeAgents} active</span>
              <span class="badge ghost">${inactiveAgents} inactive</span>
              <span class="badge ghost">${heartbeatCount} heartbeats</span>
              <span class="badge ghost">${readinessCount} readiness notes</span>
              ${selected ? '<span class="badge warning">Selected</span>' : ""}
            </div>
            <p class="hint">Agents: ${escapeHtml(agentRange)}</p>
            <p class="hint">${escapeHtml(lane.lane_description || "")}</p>
          </article>
        `;
      })
      .join("");
  }

  function renderSelectedPanels() {
    const lane = getSelectedLane() || state.lanes[0] || null;
    const agent = getSelectedAgent() || state.agents[0] || null;

    const laneStatus = byId(ids.currentLaneStatus);
    const laneMeta = byId(ids.currentLaneMeta);
    const agentMeta = byId(ids.currentAgentMeta);
    const permissions = byId(ids.currentAgentPermissions);

    if (laneStatus) {
      laneStatus.textContent = lane ? `${lane.lane_name || lane.lane_key} is ${lane.lane_health || "inactive"}.` : "No lane loaded yet.";
    }
    if (laneMeta) {
      laneMeta.textContent = lane
        ? `Lane order ${lane.lane_order || "n/a"} · ${getAgentsForLane(lane.lane_key).filter((a) => a.status === "active").length} active of 10 · ${state.heartbeatEvents.filter((event) => event.lane_key === lane.lane_key).length} heartbeats · ${state.readinessNotes.filter((note) => note.lane_key === lane.lane_key).length} readiness notes`
        : "Select a lane to inspect its health.";
    }
    if (agentMeta) {
      agentMeta.textContent = agent
        ? `Lane ${agent.lane_key || "n/a"} · position ${agent.lane_position || "n/a"} · last heartbeat ${fmtDate(agent.last_heartbeat_at)} · last readiness note ${fmtDate(agent.last_readiness_note_at)}`
        : "Select an agent to inspect its status.";
    }
    if (permissions) {
      permissions.textContent = agent
        ? `execution: ${agent.execution_permissions || "none"} | external API: ${agent.external_api_permissions || "none"} | db writes: ${agent.database_write_permissions || "audit_event_only"}`
        : "Lane-scoped, supervised, audit-only, readiness-note only.";
    }
  }

  function renderAuditTimeline() {
    const timeline = byId(ids.auditTimeline);
    if (!timeline) return;
    if (!state.auditEvents.length) {
      timeline.innerHTML = '<div class="runtime-audit-item">No audit events have been recorded yet.</div>';
      return;
    }

    timeline.innerHTML = state.auditEvents
      .map((event) => `
        <article class="runtime-audit-item">
          <h4>${escapeHtml(event.event_type || "UNKNOWN_EVENT")}</h4>
          <div class="meta-row">
            <span class="badge info">${escapeHtml(event.lane_key || "n/a")}</span>
            <span class="badge ghost">${escapeHtml(event.agent_id || "n/a")}</span>
            <span class="badge ghost">${fmtDate(event.created_at)}</span>
            <span class="badge ghost">${escapeHtml(event.actor || "operator")}</span>
          </div>
          <p class="runtime-audit-summary">${escapeHtml(event.event_summary || "")}</p>
          <details>
            <summary class="badge ghost">Payload</summary>
            <pre class="code-block">${escapeHtml(JSON.stringify(event.event_payload || {}, null, 2))}</pre>
          </details>
        </article>
      `)
      .join("");
  }

  function renderAll() {
    renderBackendPanel();
    renderSelects();
    renderSelectedPanels();
    renderLaneRoster();
    renderAuditTimeline();
  }

  async function loadState() {
    setMessage("Loading runtime group state...", "info");
    try {
      const response = await requestJson(ENDPOINTS.list, { method: "GET" });
      const data = await response.json();
      if (response.status === 503 || !data.ok) {
        setBackendUnavailable(backendUnavailableMessage);
        setMessage("Backend not configured yet.", "warn");
        return;
      }
      setBackendReady(data);
      setMessage("Backend functions responded successfully.", "success");
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
      setMessage("Backend not configured yet.", "warn");
    }
  }

  function buildGroupAgentIds() {
    return state.agents.map((agent) => agent.agent_id);
  }

  function readHeartbeatPayload(scope) {
    const lane = getSelectedLane();
    return {
      scope,
      lane_key: scope === "lane" && lane ? lane.lane_key : "",
      actor_name: "operator",
      heartbeat_status: byId(ids.heartbeatStatus).value,
      heartbeat_note: byId(ids.heartbeatNote).value,
    };
  }

  function readReadinessPayload() {
    return {
      scope: "group",
      actor_name: "operator",
      note_title: byId(ids.readinessTitle).value,
      note_body: byId(ids.readinessBody).value,
      readiness_level: byId(ids.readinessLevel).value,
    };
  }

  async function submitAction(url, payload, successMessage) {
    setMessage(`${successMessage}...`, "info");
    try {
      const response = await requestJson(url, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (response.status === 503 || data.error === "Runtime group backend is not configured.") {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }

      if (!response.ok || !data.ok) {
        setMessage(data.error || `${successMessage} failed.`, "warn");
        return;
      }

      await loadState();
      setMessage(`${successMessage} complete.`, "success");
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
    }
  }

  function bindEvents() {
    byId("refreshButton")?.addEventListener("click", loadState);
    byId("activateGroupButton")?.addEventListener("click", () => {
      submitAction(ENDPOINTS.activateGroup, {
        agent_ids: buildGroupAgentIds(),
        actor_name: "operator",
        reason: "Controlled 500-agent group activation",
        batch_size: 500,
      }, "Activate full group");
    });
    byId("deactivateGroupButton")?.addEventListener("click", () => {
      submitAction(ENDPOINTS.deactivateGroup, {
        agent_ids: buildGroupAgentIds(),
        actor_name: "operator",
        reason: "Controlled 500-agent group deactivation",
        batch_size: 500,
      }, "Deactivate full group");
    });
    byId("activateLaneButton")?.addEventListener("click", () => {
      const lane = getSelectedLane();
      if (!lane) return;
      submitAction(ENDPOINTS.activateLane, {
        lane_key: lane.lane_key,
        actor_name: "operator",
        reason: `Controlled activation for ${lane.lane_name || lane.lane_key}`,
      }, "Activate one lane");
    });
    byId("deactivateLaneButton")?.addEventListener("click", () => {
      const lane = getSelectedLane();
      if (!lane) return;
      submitAction(ENDPOINTS.deactivateLane, {
        lane_key: lane.lane_key,
        actor_name: "operator",
        reason: `Controlled deactivation for ${lane.lane_name || lane.lane_key}`,
      }, "Deactivate one lane");
    });
    byId("activateAgentButton")?.addEventListener("click", () => {
      const agent = getSelectedAgent();
      if (!agent) return;
      submitAction(ENDPOINTS.activateGroup, {
        agent_id: agent.agent_id,
        agent_ids: [agent.agent_id],
        actor_name: "operator",
        reason: "Controlled individual agent activation",
        batch_size: 1,
      }, "Activate individual agent");
    });
    byId("deactivateAgentButton")?.addEventListener("click", () => {
      const agent = getSelectedAgent();
      if (!agent) return;
      submitAction(ENDPOINTS.deactivateGroup, {
        agent_id: agent.agent_id,
        agent_ids: [agent.agent_id],
        actor_name: "operator",
        reason: "Controlled individual agent deactivation",
        batch_size: 1,
      }, "Deactivate individual agent");
    });
    byId("groupHeartbeatButton")?.addEventListener("click", () => {
      submitAction(ENDPOINTS.heartbeat, readHeartbeatPayload("group"), "Send group heartbeat");
    });
    byId("laneHeartbeatButton")?.addEventListener("click", () => {
      submitAction(ENDPOINTS.heartbeat, readHeartbeatPayload("lane"), "Send lane heartbeat");
    });
    byId("readinessButton")?.addEventListener("click", () => {
      submitAction(ENDPOINTS.readinessNote, readReadinessPayload(), "Create readiness note");
    });
    byId(ids.selectedLaneSelect)?.addEventListener("change", () => {
      state.selectedLaneKey = byId(ids.selectedLaneSelect).value;
      renderSelectedPanels();
      renderLaneRoster();
    });
    byId(ids.selectedAgentSelect)?.addEventListener("change", () => {
      state.selectedAgentId = byId(ids.selectedAgentSelect).value;
      renderSelectedPanels();
      renderLaneRoster();
    });
  }

  bindEvents();
  loadState();
})();
