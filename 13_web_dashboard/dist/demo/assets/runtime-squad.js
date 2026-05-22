(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-squad",
    activate: "/.netlify/functions/activate-runtime-squad",
    deactivate: "/.netlify/functions/deactivate-runtime-squad",
    heartbeat: "/.netlify/functions/agent-heartbeat",
    readinessNote: "/.netlify/functions/create-readiness-note",
  };

  const backendUnavailableMessage = "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables.";

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    agents: [],
    heartbeatEvents: [],
    readinessNotes: [],
    auditEvents: [],
    counts: {},
    lastResponse: null,
    selectedAgentId: "mvp54_runtime_squad_agent_001",
  };

  const elementIds = {
    backendStatusMessage: "backendStatusMessage",
    backendConnectionState: "backendConnectionState",
    runtimeActivationState: "runtimeActivationState",
    runtimeSquadSizeState: "runtimeSquadSizeState",
    liveRuntimeAgentsState: "liveRuntimeAgentsState",
    maxBatchSizeState: "maxBatchSizeState",
    massActivationState: "massActivationState",
    fullActivationState: "fullActivationState",
    totalRegisteredAgentsState: "totalRegisteredAgentsState",
    killSwitchState: "killSwitchState",
    squadRoster: "squadRoster",
    auditTimeline: "auditTimeline",
    backendUnavailableNotice: "backendUnavailableNotice",
    selectedAgentSelect: "selectedAgentSelect",
    squadHeartbeatStatus: "squadHeartbeatStatus",
    squadHeartbeatNote: "squadHeartbeatNote",
    squadReadinessTitle: "squadReadinessTitle",
    squadReadinessBody: "squadReadinessBody",
    squadReadinessLevel: "squadReadinessLevel",
    currentAgentStatus: "currentAgentStatus",
    currentAgentMeta: "currentAgentMeta",
    currentAgentId: "currentAgentId",
    currentAgentPermissions: "currentAgentPermissions",
    currentAgentTask: "currentAgentTask",
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
    const el = byId(elementIds.backendStatusMessage);
    if (!el) return;
    el.textContent = text;
    el.dataset.state = type;
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.config = {};
    state.agents = [];
    state.heartbeatEvents = [];
    state.readinessNotes = [];
    state.auditEvents = [];
    state.counts = {};
    const notice = byId(elementIds.backendUnavailableNotice);
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
    state.agents = payload.agents || [];
    state.heartbeatEvents = payload.heartbeat_events || [];
    state.readinessNotes = payload.readiness_notes || [];
    state.auditEvents = payload.audit_events || [];
    state.counts = payload.counts || {};
    const notice = byId(elementIds.backendUnavailableNotice);
    if (notice) {
      notice.hidden = true;
      notice.classList.add("hidden");
    }
    if (!state.selectedAgentId && state.agents.length) {
      state.selectedAgentId = state.agents[0].agent_id;
    }
    renderAll();
  }

  function getSelectedAgentId() {
    const select = byId(elementIds.selectedAgentSelect);
    if (select && select.value) {
      state.selectedAgentId = select.value;
    }
    return state.selectedAgentId;
  }

  function getAgentById(agentId) {
    return state.agents.find((agent) => agent.agent_id === agentId) || null;
  }

  function renderBackendPanel() {
    byId(elementIds.backendConnectionState).textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    byId(elementIds.runtimeActivationState).textContent = state.backendStatus ? String(Boolean(state.backendStatus.runtime_activation_started)) : "false";
    byId(elementIds.runtimeSquadSizeState).textContent = state.backendStatus ? String(Number(state.backendStatus.runtime_squad_size || 10)) : "10";
    byId(elementIds.liveRuntimeAgentsState).textContent = state.backendStatus ? `${Number(state.backendStatus.live_runtime_agents_enabled || 0)} of 10` : "0 of 10";
    byId(elementIds.maxBatchSizeState).textContent = state.backendStatus ? String(Number(state.backendStatus.max_activation_batch_size || 10)) : "10";
    byId(elementIds.massActivationState).textContent = state.backendStatus && state.backendStatus.mass_activation_blocked ? "blocked" : "blocked";
    byId(elementIds.fullActivationState).textContent = state.backendStatus && state.backendStatus.full_47979_activation_blocked ? "blocked" : "blocked";
    byId(elementIds.totalRegisteredAgentsState).textContent = state.backendStatus ? String(Number(state.backendStatus.total_registered_agents || 47979)) : "47,979";
    byId(elementIds.killSwitchState).textContent = state.backendStatus && state.backendStatus.kill_switch_visible ? "visible" : "visible";
  }

  function renderCurrentAgent() {
    const agent = getAgentById(getSelectedAgentId()) || state.agents[0] || null;
    const statusEl = byId(elementIds.currentAgentStatus);
    const metaEl = byId(elementIds.currentAgentMeta);
    const idEl = byId(elementIds.currentAgentId);
    const permsEl = byId(elementIds.currentAgentPermissions);
    const taskEl = byId(elementIds.currentAgentTask);

    if (!agent) {
      if (statusEl) statusEl.textContent = "No squad agent loaded yet.";
      if (metaEl) metaEl.textContent = "Refresh to load the current squad state.";
      if (idEl) idEl.textContent = "mvp54_runtime_squad_agent_001";
      if (permsEl) permsEl.textContent = "execution: none";
      if (taskEl) taskEl.textContent = "create heartbeat and readiness note only";
      return;
    }

    if (statusEl) statusEl.textContent = `${agent.agent_name || agent.agent_id} is ${agent.status || "inactive"}.`;
    if (metaEl) metaEl.textContent = `Squad position ${agent.squad_position || "n/a"} · last heartbeat ${fmtDate(agent.last_heartbeat_at)} · last readiness note ${fmtDate(agent.last_readiness_note_at)}`;
    if (idEl) idEl.textContent = agent.agent_id || "mvp54_runtime_squad_agent_001";
    if (permsEl) {
      permsEl.textContent = `execution: ${agent.execution_permissions || "none"} | external API: ${agent.external_api_permissions || "none"} | db writes: ${agent.database_write_permissions || "audit_event_only"}`;
    }
    if (taskEl) taskEl.textContent = agent.allowed_task || "create heartbeat and readiness note only";
  }

  function renderSquadRoster() {
    const roster = byId(elementIds.squadRoster);
    if (!roster) return;

    if (!state.agents.length) {
      roster.innerHTML = '<div class="empty-state">No approved squad agents loaded yet.</div>';
      return;
    }

    roster.innerHTML = state.agents
      .map((agent) => {
        const heartbeat = agent.latest_heartbeat || null;
        const note = agent.latest_readiness_note || null;
        const isSelected = agent.agent_id === getSelectedAgentId();
        return `
          <article class="card" data-agent-id="${escapeHtml(agent.agent_id)}">
            <div class="toolbar">
              <div>
                <p class="mini-label">Squad ${escapeHtml(String(agent.squad_position || "n/a"))}</p>
                <strong>${escapeHtml(agent.agent_name || agent.agent_id)}</strong>
              </div>
              <span class="badge ${agent.status === "active" ? "success" : "ghost"}">${escapeHtml(agent.status || "inactive")}</span>
            </div>
            <p class="hint">${escapeHtml(agent.agent_id)}</p>
            <div class="meta-row">
              <span class="badge info">${escapeHtml(agent.allowed_task || "create heartbeat and readiness note only")}</span>
              <span class="badge">${agent.kill_switch_visible ? "Kill switch visible" : "Kill switch hidden"}</span>
              ${isSelected ? '<span class="badge warning">Selected</span>' : ""}
            </div>
            <p class="hint">Heartbeat: ${escapeHtml(fmtDate(heartbeat && heartbeat.created_at))}</p>
            <p class="hint">Readiness note: ${escapeHtml(fmtDate(note && note.created_at))}</p>
          </article>
        `;
      })
      .join("");
  }

  function renderAuditTimeline() {
    const timeline = byId(elementIds.auditTimeline);
    if (!timeline) return;
    if (!state.auditEvents.length) {
      timeline.innerHTML = '<div class="runtime-audit-item">No audit events have been recorded yet.</div>';
      return;
    }

    timeline.innerHTML = state.auditEvents
      .map((event) => {
        return `
          <article class="runtime-audit-item">
            <h4>${escapeHtml(event.event_type || "UNKNOWN_EVENT")}</h4>
            <div class="meta-row">
              <span class="badge info">${escapeHtml(event.agent_id || "n/a")}</span>
              <span class="badge ghost">${fmtDate(event.created_at)}</span>
              <span class="badge ghost">${escapeHtml(event.actor || "operator")}</span>
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

  function renderAll() {
    renderBackendPanel();
    renderCurrentAgent();
    renderSquadRoster();
    renderAuditTimeline();
  }

  function renderSelectOptions() {
    const select = byId(elementIds.selectedAgentSelect);
    if (!select) return;
    const agents = state.agents.length ? state.agents : [{
      agent_id: "mvp54_runtime_squad_agent_001",
      agent_name: "Runtime Squad Agent 001",
    }];

    select.innerHTML = agents
      .map((agent) => {
        return `<option value="${escapeHtml(agent.agent_id)}">${escapeHtml(agent.agent_id)} - ${escapeHtml(agent.agent_name || agent.agent_id)}</option>`;
      })
      .join("");

    if (!select.value) {
      select.value = state.selectedAgentId || agents[0].agent_id;
    }
  }

  function buildSquadAgentIds() {
    return state.agents.map((agent) => agent.agent_id);
  }

  async function loadState() {
    setMessage("Loading runtime squad state...", "info");
    try {
      const response = await requestJson(ENDPOINTS.list, { method: "GET" });
      const data = await response.json();
      if (response.status === 503 || !data.ok) {
        setBackendUnavailable(backendUnavailableMessage);
        setMessage("Backend not configured yet.", "warn");
        return;
      }

      setBackendReady(data);
      renderSelectOptions();
      setMessage("Backend functions responded successfully.", "success");
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
      setMessage("Backend not configured yet.", "warn");
    }
  }

  function readHeartbeatPayload() {
    return {
      agent_id: getSelectedAgentId(),
      actor_name: "operator",
      heartbeat_status: byId(elementIds.squadHeartbeatStatus).value,
      heartbeat_note: byId(elementIds.squadHeartbeatNote).value,
    };
  }

  function readReadinessPayload() {
    return {
      agent_id: getSelectedAgentId(),
      actor_name: "operator",
      note_title: byId(elementIds.squadReadinessTitle).value,
      note_body: byId(elementIds.squadReadinessBody).value,
      readiness_level: byId(elementIds.squadReadinessLevel).value,
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

      if (response.status === 503 || data.error === "Runtime squad backend is not configured.") {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }

      if (!response.ok || !data.ok) {
        setMessage(data.error || `${successMessage} failed.`, "warn");
        return;
      }

      state.lastResponse = data;
      await loadState();
      setMessage(`${successMessage} complete.`, "success");
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
    }
  }

  function bindEvents() {
    const activateSquadButton = byId("activateSquadButton");
    const deactivateSquadButton = byId("deactivateSquadButton");
    const activateAgentButton = byId("activateAgentButton");
    const deactivateAgentButton = byId("deactivateAgentButton");
    const heartbeatButton = byId("heartbeatButton");
    const readinessButton = byId("readinessButton");
    const refreshButton = byId("refreshButton");
    const agentSelect = byId(elementIds.selectedAgentSelect);

    refreshButton?.addEventListener("click", loadState);
    activateSquadButton?.addEventListener("click", () => {
      submitAction(
        ENDPOINTS.activate,
        {
          agent_ids: buildSquadAgentIds(),
          actor_name: "operator",
          reason: "Controlled 10-agent squad activation",
          batch_size: 10,
        },
        "Activate squad"
      );
    });
    deactivateSquadButton?.addEventListener("click", () => {
      submitAction(
        ENDPOINTS.deactivate,
        {
          agent_ids: buildSquadAgentIds(),
          actor_name: "operator",
          reason: "Controlled 10-agent squad deactivation",
          batch_size: 10,
        },
        "Deactivate squad"
      );
    });
    activateAgentButton?.addEventListener("click", () => {
      submitAction(
        ENDPOINTS.activate,
        {
          agent_id: getSelectedAgentId(),
          agent_ids: [getSelectedAgentId()],
          actor_name: "operator",
          reason: "Controlled individual agent activation",
          batch_size: 1,
        },
        "Activate individual agent"
      );
    });
    deactivateAgentButton?.addEventListener("click", () => {
      submitAction(
        ENDPOINTS.deactivate,
        {
          agent_id: getSelectedAgentId(),
          agent_ids: [getSelectedAgentId()],
          actor_name: "operator",
          reason: "Controlled individual agent deactivation",
          batch_size: 1,
        },
        "Deactivate individual agent"
      );
    });
    heartbeatButton?.addEventListener("click", () => {
      submitAction(ENDPOINTS.heartbeat, readHeartbeatPayload(), "Send heartbeat");
    });
    readinessButton?.addEventListener("click", () => {
      submitAction(ENDPOINTS.readinessNote, readReadinessPayload(), "Create readiness note");
    });
    agentSelect?.addEventListener("change", () => {
      state.selectedAgentId = agentSelect.value;
      renderCurrentAgent();
    });
  }

  bindEvents();
  loadState();
})();
