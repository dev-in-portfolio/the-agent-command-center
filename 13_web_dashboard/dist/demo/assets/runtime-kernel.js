(() => {
  const ENDPOINTS = {
    create: "/.netlify/functions/runtime-request-create",
    list: "/.netlify/functions/runtime-request-list",
    decision: "/.netlify/functions/runtime-request-decision",
  };

  const state = {
    backendConfigured: false,
    backendStatus: null,
    config: {},
    requests: [],
    approvalQueue: [],
    auditEvents: [],
    counts: {
      request_count: 0,
      pending_approval_count: 0,
      blocked_count: 0,
      approved_count: 0,
      denied_count: 0,
      audit_event_count: 0,
    },
    lastResponse: null,
  };

  const form = document.getElementById("runtimeRequestForm");
  const refreshButton = document.getElementById("refreshKernelButton");
  const backendStatusMessage = document.getElementById("backendStatusMessage");
  const backendConnectionState = document.getElementById("backendConnectionState");
  const runtimeActivationState = document.getElementById("runtimeActivationState");
  const liveRuntimeAgentsState = document.getElementById("liveRuntimeAgentsState");
  const commandExecutionState = document.getElementById("commandExecutionState");
  const automationState = document.getElementById("automationState");
  const rollbackState = document.getElementById("rollbackState");
  const alertState = document.getElementById("alertState");
  const countsState = document.getElementById("countsState");
  const requestIdState = document.getElementById("requestIdState");
  const requestStatusState = document.getElementById("requestStatusState");
  const riskLevelState = document.getElementById("riskLevelState");
  const blockedState = document.getElementById("blockedState");
  const approvalStatusState = document.getElementById("approvalStatusState");
  const dryRunSummaryState = document.getElementById("dryRunSummaryState");
  const approvalQueueList = document.getElementById("approvalQueueList");
  const auditTimeline = document.getElementById("auditTimeline");
  const backendUnavailableNotice = document.getElementById("backendUnavailableNotice");

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll("\"", "&quot;")
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
    backendStatusMessage.textContent = text;
    backendStatusMessage.dataset.state = type;
  }

  function setBackendUnavailable(message) {
    state.backendConfigured = false;
    state.backendStatus = null;
    state.config = {};
    state.requests = [];
    state.approvalQueue = [];
    state.auditEvents = [];
    state.counts = {
      request_count: 0,
      pending_approval_count: 0,
      blocked_count: 0,
      approved_count: 0,
      denied_count: 0,
      audit_event_count: 0,
    };
    backendUnavailableNotice.hidden = false;
    backendUnavailableNotice.classList.remove("hidden");
    backendUnavailableNotice.textContent = message;
    renderKernelState();
  }

  function setBackendReady(payload) {
    state.backendConfigured = true;
    state.backendStatus = payload.backend_status || {};
    state.config = payload.config || {};
    state.requests = payload.requests || [];
    state.approvalQueue = payload.approval_queue || [];
    state.auditEvents = payload.audit_events || [];
    state.counts = payload.counts || state.counts;
    backendUnavailableNotice.hidden = true;
    backendUnavailableNotice.classList.add("hidden");
    renderKernelState();
  }

  function renderBackendPanel() {
    backendConnectionState.textContent = state.backendConfigured ? "Configured and responding" : "Not configured";
    runtimeActivationState.textContent = state.backendStatus ? String(Boolean(state.backendStatus.runtime_activation_started)) : "false";
    liveRuntimeAgentsState.textContent = state.backendStatus ? String(Number(state.backendStatus.live_runtime_agents_enabled || 0)) : "0";
    commandExecutionState.textContent = state.backendStatus ? String(Boolean(state.backendStatus.command_execution_enabled)) : "false";
    automationState.textContent = state.backendStatus ? String(Boolean(state.backendStatus.automation_enabled)) : "false";
    rollbackState.textContent = state.backendStatus ? String(Boolean(state.backendStatus.rollback_execution_enabled)) : "false";
    alertState.textContent = state.backendStatus ? String(Boolean(state.backendStatus.alert_sending_enabled)) : "false";
    countsState.textContent = state.backendConfigured
      ? `Requests ${state.counts.request_count}, pending ${state.counts.pending_approval_count}, audits ${state.counts.audit_event_count}`
      : "No backend data loaded yet.";
  }

  function renderResultPanel() {
    const request = state.lastResponse && state.lastResponse.request ? state.lastResponse.request : state.requests[0];

    if (!request) {
      requestIdState.textContent = "n/a";
      requestStatusState.textContent = "n/a";
      riskLevelState.textContent = "n/a";
      blockedState.textContent = "n/a";
      approvalStatusState.textContent = "n/a";
      dryRunSummaryState.textContent = "Submit a request to see the dry-run summary here.";
      return;
    }

    requestIdState.textContent = request.id || request.request_id || "n/a";
    requestStatusState.textContent = request.status || "n/a";
    riskLevelState.textContent = request.risk_level || "n/a";
    blockedState.textContent = request.status === "blocked" || state.lastResponse?.blocked ? "yes" : "no";
    approvalStatusState.textContent = request.approval_status || state.lastResponse?.approval_status || "n/a";
    dryRunSummaryState.textContent = JSON.stringify(request.dry_run_summary || state.lastResponse?.dry_run_summary || {}, null, 2);
  }

  function renderApprovalQueue() {
    const pending = (state.requests || []).filter((request) => {
      return request.status === "pending_approval" || request.approval_status === "pending";
    });

    if (!pending.length) {
      approvalQueueList.innerHTML = '<div class="empty-state">No pending approval queue items yet.</div>';
      return;
    }

    approvalQueueList.innerHTML = pending
      .map((request) => {
        const title = escapeHtml(request.request_title || request.title || "Untitled request");
        const type = escapeHtml(request.request_type || "unknown");
        const body = escapeHtml(request.request_body || "");
        const owner = escapeHtml(request.requester_name || request.requester_email || "unknown");
        const requestId = escapeHtml(request.id || request.request_id || "");
        const risk = escapeHtml(request.risk_level || "unclassified");
        const status = escapeHtml(request.status || "pending_approval");

        return `
          <article class="queue-item pending" data-request-id="${requestId}">
            <div class="toolbar">
              <div>
                <p class="mini-label">${requestId}</p>
                <strong>${title}</strong>
              </div>
              <span class="risk-pill risk-${risk}">${risk}</span>
            </div>
            <p class="hint">${body || "No body provided."}</p>
            <div class="meta-row">
              <span class="badge info">${type}</span>
              <span class="badge">${owner}</span>
              <span class="badge">${status}</span>
            </div>
            <div class="queue-actions">
              <button class="button primary" type="button" data-approve="${requestId}">Approve</button>
              <button class="button" type="button" data-deny="${requestId}">Deny</button>
            </div>
            <p class="hint">Approval is not execution. MVP-52 never executes the requested action.</p>
          </article>
        `;
      })
      .join("");
  }

  function renderAuditTimeline() {
    if (!state.auditEvents.length) {
      auditTimeline.innerHTML = '<div class="empty-state">No audit events have been recorded yet.</div>';
      return;
    }

    auditTimeline.innerHTML = state.auditEvents
      .map((event) => {
        const requestId = escapeHtml(event.request_id || "n/a");
        const eventType = escapeHtml(event.event_type || "unknown");
        const summary = escapeHtml(event.event_summary || "");
        const actor = escapeHtml(event.actor || "system");
        const payload = escapeHtml(JSON.stringify(event.event_payload || {}, null, 2));
        return `
          <article class="timeline-item">
            <div class="toolbar">
              <div>
                <p class="mini-label">${escapeHtml(event.id || "")}</p>
                <strong>${eventType}</strong>
              </div>
              <span class="badge ghost">${fmtDate(event.created_at)}</span>
            </div>
            <div class="meta-row" style="margin-top: 10px;">
              <span class="badge info">${requestId}</span>
              <span class="badge">${actor}</span>
            </div>
            <p class="hint" style="margin-top: 10px;">${summary}</p>
            <details>
              <summary class="mini-label">Payload</summary>
              <pre class="code-block">${payload}</pre>
            </details>
          </article>
        `;
      })
      .join("");
  }

  function renderKernelState() {
    renderBackendPanel();
    renderResultPanel();
    renderApprovalQueue();
    renderAuditTimeline();
  }

  function readFormData() {
    const formData = new FormData(form);
    return {
      requester_name: formData.get("requester_name"),
      requester_email: formData.get("requester_email"),
      request_title: formData.get("request_title"),
      request_type: formData.get("request_type"),
      request_body: formData.get("request_body"),
    };
  }

  async function loadKernelState() {
    setMessage("Loading backend state...");
    try {
      const response = await requestJson(ENDPOINTS.list, { method: "GET" });
      const data = await response.json();
      if (response.status === 503 || !data.ok) {
        setBackendUnavailable(
          "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables."
        );
        setMessage("Backend not configured yet.", "warn");
        return;
      }

      setBackendReady(data);
      setMessage("Backend functions responded successfully.", "success");
    } catch (error) {
      setBackendUnavailable(
        "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables."
      );
      setMessage("Backend unavailable right now.", "warn");
    }
  }

  function applySubmissionResult(data) {
    state.lastResponse = data;
    if (data.request) {
      const request = data.request;
      const existingIndex = state.requests.findIndex((item) => (item.id || item.request_id) === (request.id || request.request_id));
      if (existingIndex >= 0) {
        state.requests[existingIndex] = {
          ...state.requests[existingIndex],
          ...request,
        };
      } else {
        state.requests = [request, ...state.requests];
      }
    }
    if (Array.isArray(data.audit_events)) {
      state.auditEvents = [...data.audit_events, ...state.auditEvents].slice(0, 50);
    }
    if (data.approval_queue) {
      const queueEntry = data.approval_queue;
      const queueIndex = state.approvalQueue.findIndex((item) => item.id === queueEntry.id);
      if (queueIndex >= 0) {
        state.approvalQueue[queueIndex] = queueEntry;
      } else {
        state.approvalQueue = [queueEntry, ...state.approvalQueue];
      }
    }
    renderKernelState();
  }

  async function submitRuntimeRequest(event) {
    event.preventDefault();
    const payload = readFormData();
    setMessage("Submitting runtime request...", "info");

    try {
      const response = await requestJson(ENDPOINTS.create, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Runtime request submission failed.");
      }

      applySubmissionResult(data);
      setMessage("Runtime request persisted, audited, and queued.", "success");
      form.reset();
      await loadKernelState();
    } catch (error) {
      setBackendUnavailable(
        "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables."
      );
      setMessage("Runtime request submission failed.", "warn");
    }
  }

  async function submitDecision(requestId, decision) {
    const approverName = prompt("Approver name");
    if (!approverName) {
      return;
    }
    const approverEmail = prompt("Approver email") || "";
    const decisionReason = prompt("Decision reason") || "";

    setMessage(`Sending ${decision} decision...`, "info");

    try {
      const response = await requestJson(ENDPOINTS.decision, {
        method: "POST",
        body: JSON.stringify({
          request_id: requestId,
          decision,
          approver_name: approverName,
          approver_email: approverEmail,
          decision_reason: decisionReason,
        }),
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Runtime approval decision failed.");
      }

      state.lastResponse = {
        request: data.request,
        approval_status: data.approval_status,
      };
      await loadKernelState();
      setMessage(`Request ${decision}. Approval is not execution.`, "success");
    } catch (error) {
      setBackendUnavailable(
        "Backend functions or Supabase environment variables are not configured yet. The UI is ready, but persistence requires Supabase URL and service-role key configured in Netlify environment variables."
      );
      setMessage("Runtime approval decision failed.", "warn");
    }
  }

  approvalQueueList.addEventListener("click", (event) => {
    const approveId = event.target && event.target.getAttribute("data-approve");
    const denyId = event.target && event.target.getAttribute("data-deny");

    if (approveId) {
      submitDecision(approveId, "approved");
    }
    if (denyId) {
      submitDecision(denyId, "denied");
    }
  });

  refreshButton.addEventListener("click", () => {
    loadKernelState();
  });

  form.addEventListener("submit", submitRuntimeRequest);

  loadKernelState();
})();
