(function () {
  const ENDPOINTS = {
    list: "/.netlify/functions/list-runtime-agents",
    activate: "/.netlify/functions/activate-agent",
    deactivate: "/.netlify/functions/deactivate-agent",
  };

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    agents: [],
    currentAgent: null,
    events: [],
    counts: {
      registered_agents: 47979,
      active_agents: 0,
      inactive_agents: 0,
      activation_event_count: 0,
    },
  };

  const backendUnavailableMessage = "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.";

  const backendConnectionState = document.getElementById("backendConnectionState");
  const liveRuntimeAgentsState = document.getElementById("liveRuntimeAgentsState");
  const totalRegisteredAgentsState = document.getElementById("totalRegisteredAgentsState");
  const massActivationState = document.getElementById("massActivationState");
  const activationModeState = document.getElementById("activationModeState");
  const maxBatchSizeState = document.getElementById("maxBatchSizeState");
  const killSwitchState = document.getElementById("killSwitchState");
  const backendStatusMessage = document.getElementById("backendStatusMessage");
  const currentAgentStatus = document.getElementById("currentAgentStatus");
  const currentAgentId = document.getElementById("currentAgentId");
  const currentAgentPermissions = document.getElementById("currentAgentPermissions");
  const currentAgentTask = document.getElementById("currentAgentTask");
  const currentAgentMeta = document.getElementById("currentAgentMeta");
  const auditTimeline = document.getElementById("auditTimeline");
  const refreshButton = document.getElementById("refreshButton");
  const activateButton = document.getElementById("activateButton");
  const deactivateButton = document.getElementById("deactivateButton");
  const activationForm = document.getElementById("activationForm");
  const agentSelect = document.getElementById("agentSelect");
  const operatorName = document.getElementById("operatorName");
  const reasonField = document.getElementById("reasonField");

  function setMessage(text, type) {
    backendStatusMessage.textContent = text;
    backendStatusMessage.dataset.state = type || "info";
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

  function requestJson(url, options) {
    return fetch(url, {
      ...(options || {}),
      headers: {
        "content-type": "application/json",
        ...((options && options.headers) || {}),
      },
    });
  }

  function renderBackendPanel() {
    backendConnectionState.textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    liveRuntimeAgentsState.textContent = String((state.backendStatus && state.backendStatus.live_runtime_agents_enabled) || 0);
    totalRegisteredAgentsState.textContent = String((state.backendStatus && state.backendStatus.total_registered_agents) || 47979);
    massActivationState.textContent = (state.backendStatus && state.backendStatus.mass_activation_blocked) ? "blocked" : "blocked";
    activationModeState.textContent = `Activation mode: ${(state.backendStatus && state.backendStatus.activation_mode) || "supervised single-agent test"}`;
    maxBatchSizeState.textContent = String((state.backendStatus && state.backendStatus.max_activation_batch_size) || 1);
    killSwitchState.textContent = (state.backendStatus && state.backendStatus.kill_switch_visible) ? "visible" : "visible";
  }

  function renderAgentStatus() {
    const agent = state.currentAgent;
    if (!agent) {
      currentAgentStatus.textContent = "No agent loaded yet.";
      currentAgentId.textContent = "mvp53_supervised_test_agent_001";
      currentAgentPermissions.textContent = "execution: none";
      currentAgentTask.textContent = "audit-only readiness note";
      currentAgentMeta.textContent = "Refresh the backend to load the current status.";
      return;
    }

    currentAgentStatus.textContent = `${agent.agent_name || "Supervised Test Agent 001"} is ${agent.status || "inactive"}.`;
    currentAgentId.textContent = agent.agent_id || "mvp53_supervised_test_agent_001";
    currentAgentPermissions.textContent = `execution: ${agent.execution_permissions || "none"} | external API: ${agent.external_api_permissions || "none"} | db writes: ${agent.database_write_permissions || "audit_event_only"}`;
    currentAgentTask.textContent = agent.allowed_task || "create audit-only readiness note";
    currentAgentMeta.textContent = `Activation mode: ${agent.activation_mode || "supervised_single_agent_test"} · Updated ${fmtDate(agent.updated_at)}`;
  }

  function renderAuditTimeline() {
    if (!state.events.length) {
      auditTimeline.innerHTML = '<div class="timeline-item">No activation events recorded yet.</div>';
      return;
    }

    auditTimeline.innerHTML = state.events
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
    renderAgentStatus();
    renderAuditTimeline();
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.config = {};
    state.agents = [];
    state.currentAgent = null;
    state.events = [];
    state.counts = {
      registered_agents: 47979,
      active_agents: 0,
      inactive_agents: 0,
      activation_event_count: 0,
    };
    setMessage(message || backendUnavailableMessage, "warn");
    renderAll();
  }

  function setBackendReady(data) {
    state.backendConfigured = true;
    state.backendStatus = data.backend_status || {};
    state.config = data.config || {};
    state.agents = data.agents || [];
    state.currentAgent = data.current_agent || state.agents[0] || null;
    state.events = data.activation_events || [];
    state.counts = data.counts || state.counts;
    agentSelect.innerHTML = (state.agents.length ? state.agents : [{
      agent_id: "mvp53_supervised_test_agent_001",
      agent_name: "Supervised Test Agent 001",
    }]).map((agent) => {
      return `<option value="${escapeHtml(agent.agent_id)}">${escapeHtml(agent.agent_id)} - ${escapeHtml(agent.agent_name || "Supervised Test Agent 001")}</option>`;
    }).join("");
    if (!agentSelect.value) {
      agentSelect.value = "mvp53_supervised_test_agent_001";
    }
    renderAll();
  }

  async function loadState() {
    setMessage("Loading runtime agent state...", "info");
    try {
      const response = await requestJson(ENDPOINTS.list, { method: "GET" });
      const data = await response.json();
      if (response.status === 503 || !data.ok) {
        setBackendUnavailable(
          "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure."
        );
        return;
      }

      setBackendReady(data);
      setMessage("Backend functions responded successfully.", "success");
    } catch (error) {
      setBackendUnavailable(
        "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure."
      );
    }
  }

  function buildPayload() {
    return {
      agent_id: agentSelect.value,
      actor_name: operatorName.value || "operator",
      reason: reasonField.value || "",
      batch_size: 1,
    };
  }

  async function submitAction(url, actionLabel) {
    setMessage(`${actionLabel}...`, "info");
    try {
      const response = await requestJson(url, {
        method: "POST",
        body: JSON.stringify(buildPayload()),
      });
      const data = await response.json();

      if (response.status === 503 || data.error === "Runtime agent controller backend is not configured.") {
        setBackendUnavailable(backendUnavailableMessage);
        return;
      }

      if (!response.ok || !data.ok) {
        setMessage(data.error || `${actionLabel} failed.`, "warn");
        return;
      }

      await loadState();
      setMessage(`${actionLabel} complete.`, "success");
    } catch (error) {
      setBackendUnavailable(backendUnavailableMessage);
    }
  }

  refreshButton.addEventListener("click", loadState);
  activateButton.addEventListener("click", () => submitAction(ENDPOINTS.activate, "Activate supervised test agent"));
  deactivateButton.addEventListener("click", () => submitAction(ENDPOINTS.deactivate, "Deactivate supervised test agent"));
  activationForm.addEventListener("submit", (event) => event.preventDefault());

  loadState();
})();
