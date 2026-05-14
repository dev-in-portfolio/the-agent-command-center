(function () {
  var state = {
    search: "",
    actionFilter: "all",
    artifactFilter: "all",
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function getDashboardData() {
    var node = byId("dashboard-data");
    if (!node) {
      return {};
    }
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (error) {
      return {};
    }
  }

  function setStatus(message, level) {
    var node = byId("copy-status");
    if (!node) {
      return;
    }
    node.textContent = message;
    node.dataset.level = level || "info";
  }

  function supportsClipboard() {
    return !!(navigator.clipboard && navigator.clipboard.writeText);
  }

  function fallbackCopy(text) {
    var field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "readonly");
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.focus();
    field.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (error) {
      ok = false;
    }
    document.body.removeChild(field);
    return Promise.resolve(ok);
  }

  function copyText(text) {
    if (!text) {
      return Promise.resolve(false);
    }
    if (supportsClipboard()) {
      return navigator.clipboard.writeText(text).then(function () {
        return true;
      }).catch(function () {
        return fallbackCopy(text);
      });
    }
    return fallbackCopy(text);
  }

  function wireCopyButtons() {
    document.querySelectorAll("[data-copy-text]").forEach(function (button) {
      button.addEventListener("click", function () {
        var text = button.getAttribute("data-copy-text");
        Promise.resolve(copyText(text)).then(function (ok) {
          setStatus(ok ? "Copied to clipboard." : "Clipboard unavailable.", ok ? "pass" : "warning");
        });
      });
    });
  }

  function normalizeText(value) {
    return (value || "").toLowerCase().trim();
  }

  function rowSearchText(row) {
    return normalizeText(row.getAttribute("data-search-text") || row.textContent);
  }

  function matchesSearch(value, needle) {
    if (!needle) {
      return true;
    }
    return normalizeText(value).indexOf(needle) !== -1;
  }

  function applyGlobalSearch() {
    var needle = normalizeText(state.search);
    document.querySelectorAll(".card, .summary-strip .stat, details.panel").forEach(function (element) {
      if (!needle) {
        element.hidden = false;
        return;
      }
      var text = normalizeText(element.getAttribute("data-search-text") || element.textContent);
      element.hidden = text.indexOf(needle) === -1;
    });

    document.querySelectorAll("tr[data-search-text]").forEach(function (row) {
      if (!needle) {
        row.hidden = false;
        return;
      }
      row.hidden = rowSearchText(row).indexOf(needle) === -1;
    });
  }

  function applyActionFilter() {
    document.querySelectorAll("#action-table tbody tr").forEach(function (row) {
      var category = normalizeText(row.getAttribute("data-action-category"));
      var allowed = state.actionFilter === "all" || category === state.actionFilter;
      if (!allowed) {
        row.hidden = true;
        return;
      }
      if (state.search) {
        row.hidden = rowSearchText(row).indexOf(normalizeText(state.search)) === -1;
      } else {
        row.hidden = false;
      }
    });
  }

  function applyArtifactFilter() {
    document.querySelectorAll("#artifact-table tbody tr").forEach(function (row) {
      var exists = row.getAttribute("data-package-exists") === "true";
      var warnings = Number(row.getAttribute("data-package-warnings") || "0");
      var missing = Number(row.getAttribute("data-package-missing") || "0");
      var verdict = normalizeText(row.getAttribute("data-package-verdict"));
      var allowed = true;
      switch (state.artifactFilter) {
        case "exists":
          allowed = exists;
          break;
        case "missing":
          allowed = !exists || missing > 0;
          break;
        case "warning":
          allowed = warnings > 0 || missing > 0 || verdict.indexOf("warn") !== -1;
          break;
        default:
          allowed = true;
      }
      if (!allowed) {
        row.hidden = true;
        return;
      }
      if (state.search) {
        row.hidden = rowSearchText(row).indexOf(normalizeText(state.search)) === -1;
      } else {
        row.hidden = false;
      }
    });
  }

  function applyTableSearches() {
    document.querySelectorAll("[data-search-target]").forEach(function (input) {
      var tableId = input.getAttribute("data-search-target");
      var needle = normalizeText(input.value);
      var table = byId(tableId);
      if (!table) {
        return;
      }
      table.querySelectorAll("tbody tr").forEach(function (row) {
        var rowText = rowSearchText(row);
        if (!needle) {
          if (!row.hidden) {
            row.hidden = false;
          }
          return;
        }
        if (!row.dataset.forcedHidden) {
          row.hidden = rowText.indexOf(needle) === -1;
        }
      });
    });
  }

  function sortTable(tableId, key) {
    var table = byId(tableId);
    if (!table) {
      return;
    }
    var tbody = table.tBodies[0];
    if (!tbody) {
      return;
    }
    var rows = Array.prototype.slice.call(tbody.rows);

    function riskScore(row) {
      var category = normalizeText(row.getAttribute("data-action-category"));
      return { locked: 3, controlled: 2, safe: 1 }[category] || 0;
    }

    function numberAttr(row, name) {
      return Number(row.getAttribute(name) || "0");
    }

    rows.sort(function (a, b) {
      if (key === "risk") {
        return riskScore(b) - riskScore(a);
      }
      if (key === "warnings") {
        return numberAttr(b, "data-package-warnings") - numberAttr(a, "data-package-warnings");
      }
      if (key === "missing") {
        return numberAttr(b, "data-package-missing") - numberAttr(a, "data-package-missing");
      }
      return 0;
    });

    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
  }

  function wireSearchInputs() {
    document.querySelectorAll("[data-search-target]").forEach(function (input) {
      input.addEventListener("input", function () {
        if (input.getAttribute("data-search-target") === "action-table") {
          state.actionFilter = "all";
        }
        if (input.getAttribute("data-search-target") === "artifact-table") {
          state.artifactFilter = "all";
        }
        applyFilters();
      });
    });

    var globalSearch = byId("global-search");
    if (globalSearch) {
      globalSearch.addEventListener("input", function () {
        state.search = globalSearch.value;
        applyFilters();
      });
    }
  }

  function applyPanelState(target, action) {
    var panels = document.querySelectorAll("details.panel");
    panels.forEach(function (panel) {
      if (target !== "all" && panel.getAttribute("data-section-group") !== target) {
        return;
      }
      panel.open = action === "expand";
    });
  }

  function wirePanelButtons() {
    document.querySelectorAll("[data-panel-action]").forEach(function (button) {
      button.addEventListener("click", function () {
        var action = button.getAttribute("data-panel-action");
        var target = button.getAttribute("data-panel-target") || "all";
        if (action === "compact") {
          document.body.classList.toggle("compact-view");
          button.setAttribute("data-panel-state", document.body.classList.contains("compact-view") ? "on" : "off");
          button.textContent = document.body.classList.contains("compact-view") ? "Full view" : "Compact view";
          setStatus(document.body.classList.contains("compact-view") ? "Compact view enabled." : "Compact view disabled.", "info");
          return;
        }
        applyPanelState(target, action);
        setStatus((action === "expand" ? "Expanded" : "Collapsed") + " panels in " + target + " group.", "info");
      });
    });
  }

  function wireOpenSectionButtons() {
    document.querySelectorAll("[data-open-panel]").forEach(function (button) {
      button.addEventListener("click", function () {
        var panelId = button.getAttribute("data-open-panel");
        var panel = byId(panelId);
        if (!panel) {
          return;
        }
        panel.open = true;
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
        setStatus("Opened " + button.textContent + ".", "info");
      });
    });
  }

  function wireFilterButtons() {
    document.querySelectorAll("[data-action-filter]").forEach(function (button) {
      button.addEventListener("click", function () {
        state.actionFilter = button.getAttribute("data-action-filter") || "all";
        applyFilters();
      });
    });

    document.querySelectorAll("[data-artifact-filter]").forEach(function (button) {
      button.addEventListener("click", function () {
        state.artifactFilter = button.getAttribute("data-artifact-filter") || "all";
        applyFilters();
      });
    });
  }

  function wireSortButtons() {
    document.querySelectorAll("[data-sort-table]").forEach(function (button) {
      button.addEventListener("click", function () {
        var tableId = button.getAttribute("data-sort-table");
        var key = button.getAttribute("data-sort-key");
        sortTable(tableId, key);
        setStatus("Sorted " + tableId + " by " + key + ".", "info");
      });
    });
  }

  function applyFilters() {
    applyGlobalSearch();
    applyActionFilter();
    applyArtifactFilter();
    applyTableSearches();
  }

  function installKeyboardShortcut() {
    document.addEventListener("keydown", function (event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        var search = byId("global-search");
        if (search) {
          event.preventDefault();
          search.focus();
          search.select();
        }
      }
    });
  }

  function wireBackendButtons() {
    var checkButton = byId("check-backend-button");
    if (!checkButton) {
      return;
    }
    checkButton.addEventListener("click", function () {
      var statusText = byId("backend-fetch-status");
      var responseArea = byId("backend-response-area");
      var responseJson = byId("backend-response-json");

      if (statusText) statusText.textContent = "Checking...";
      
      fetch("/api/health").then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      }).then(function (data) {
        if (statusText) statusText.textContent = "Backend reachable (Phase 4A Foundation).";
        if (responseArea) responseArea.style.display = "block";
        if (responseJson) responseJson.textContent = JSON.stringify(data, null, 2);
        setStatus("Backend status check successful.", "pass");
      }).catch(function (err) {
        if (statusText) statusText.textContent = "Backend not reachable in this preview environment.";
        if (responseArea) responseArea.style.display = "none";
        setStatus("Backend check failed: " + err.message, "warning");
      });
    });
  }

  function wireSnapshotButtons() {
    var loadButton = byId("load-snapshot-button");
    if (!loadButton) {
      return;
    }
    loadButton.addEventListener("click", function () {
      var statusText = byId("snapshot-fetch-status");
      var responseArea = byId("snapshot-response-area");
      var responseJson = byId("snapshot-response-json");

      if (statusText) statusText.textContent = "Loading snapshot...";

      fetch("./status_snapshot.json").then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      }).then(function (data) {
        if (statusText) statusText.textContent = "Static snapshot loaded (v1).";
        if (responseArea) responseArea.style.display = "block";
        if (responseJson) responseJson.textContent = JSON.stringify({
          snapshot_version: data.snapshot_version,
          mode: data.mode,
          phase_status: data.phase_status,
          live_external_api_calls: data.live_external_api_calls,
          github_api_calls: data.github_api_calls,
          netlify_api_calls: data.netlify_api_calls,
          timestamp_utc: data.timestamp_utc
        }, null, 2);
        setStatus("Snapshot load successful.", "pass");
      }).catch(function (err) {
        if (statusText) statusText.textContent = "Static snapshot not available in this build.";
        if (responseArea) responseArea.style.display = "none";
        setStatus("Snapshot load failed: " + err.message, "warning");
      });
    });
  }

  function wirePhase4dSchemaButton(buttonId, schemaPath, statusId) {
    var button = byId(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var statusText = byId(statusId);
      var responseArea = byId("phase4d-schema-output-panel");
      var responseJson = byId("phase4d-shared-response-json");

      // Reset all status texts first
      ["phase4d-identity-status", "phase4d-action-status", "phase4d-audit-status", "phase4d-risk-status"].forEach(function(id) {
         var el = byId(id);
         if(el) el.textContent = "Not loaded.";
      });

      if (statusText) {
        statusText.textContent = "Loading schema...";
      }

      var request;
      if (schemaPath === "./phase4d_identity_schema.json") {
        request = fetch("./phase4d_identity_schema.json");
      } else if (schemaPath === "./phase4d_action_schema.json") {
        request = fetch("./phase4d_action_schema.json");
      } else if (schemaPath === "./phase4d_audit_schema.json") {
        request = fetch("./phase4d_audit_schema.json");
      } else if (schemaPath === "./phase4d_risk_model.json") {
        request = fetch("./phase4d_risk_model.json");
      } else if (schemaPath === "./phase4d_approval_schema.json") {
        request = fetch("./phase4d_approval_schema.json");
      } else {
        request = Promise.reject(new Error("Unsupported schema path"));
      }

      request.then(function (res) {
        if (!res.ok) {
          throw new Error("HTTP " + res.status);
        }
        return res.json();
      }).then(function (data) {
        var summary = {
          schema_id: data.schema_id || "unknown",
          title: data.title || "unknown",
          schema_mode: data.schema_mode,
          live_external_api_calls: data.live_external_api_calls,
          github_api_calls: data.github_api_calls,
          netlify_api_calls: data.netlify_api_calls,
          browser_external_fetches: data.browser_external_fetches,
          command_execution: data.command_execution,
          github_mutation: data.github_mutation,
          netlify_mutation: data.netlify_mutation,
          deploy_controls: data.deploy_controls,
          merge_controls: data.merge_controls,
          push_controls: data.push_controls,
          pr_controls: data.pr_controls,
          action_execution: data.action_execution,
          action_queue_live: data.action_queue_live
        };
        if (statusText) {
          statusText.textContent = "Schema loaded.";
        }
        if (responseArea) {
          responseArea.style.display = "block";
        }
        if (responseJson) {
          responseJson.textContent = JSON.stringify(summary, null, 2);
        }
        setStatus("Loaded schema preview: " + schemaPath, "pass");
      }).catch(function (err) {
        if (statusText) {
          statusText.textContent = "Schema unavailable in this build.";
        }
        if (responseArea) {
          responseArea.style.display = "none";
        }
        setStatus("Schema load failed: " + err.message, "warning");
      });
    });
  }

  function init() {
    var dashboardData = getDashboardData();
    window.__DASHBOARD_DATA__ = dashboardData;
    wireCopyButtons();
    wireSearchInputs();
    wirePanelButtons();
    wireOpenSectionButtons();
    wireFilterButtons();
    wireSortButtons();
    wireBackendButtons();
    wireSnapshotButtons();
    wirePhase4dSchemaButton("load-phase4d-identity-schema-button", "./phase4d_identity_schema.json", "phase4d-identity-status");
    wirePhase4dSchemaButton("load-phase4d-action-schema-button", "./phase4d_action_schema.json", "phase4d-action-status");
    wirePhase4dSchemaButton("load-phase4d-audit-schema-button", "./phase4d_audit_schema.json", "phase4d-audit-status");
    wirePhase4dSchemaButton("load-phase4d-risk-schema-button", "./phase4d_risk_model.json", "phase4d-risk-status");
    wirePhase4dSchemaButton("load-phase4d-approval-schema-button", "./phase4d_approval_schema.json", "phase4d-risk-status");
    installKeyboardShortcut();
    applyFilters();
    setStatus("Local UI ready.", "info");
  }

  init();
})();

(function () {
  var phase5aState = null;
  var auditEvents = [];

  var ALLOWED_STATES = ["draft", "needs_review", "review_ready", "changes_requested", "approved_for_future_phase", "rejected", "cancelled", "archived"];

  var FORBIDDEN_STATES = ["executing", "deployed", "merged", "pushed", "pr_created", "mutation_completed"];

  var ALLOWED_TRANSITIONS = {
    "draft": ["needs_review", "cancelled"],
    "needs_review": ["review_ready", "changes_requested", "rejected", "cancelled"],
    "review_ready": ["approved_for_future_phase", "changes_requested", "rejected", "cancelled"],
    "changes_requested": ["draft", "cancelled"],
    "approved_for_future_phase": ["archived"],
    "rejected": ["archived"],
    "cancelled": ["archived"],
    "archived": [],
  };

  function p5( id ) { return document.getElementById(id); }

  function generateId() {
    if (window.crypto && window.crypto.randomUUID) {
      return crypto.randomUUID().slice(0, 8);
    }
    return Math.random().toString(36).slice(2, 10);
  }

  function timestamp() { return new Date().toISOString(); }

  function classifyRisk(title, intent, workflowType) {
    var combined = ((title || "") + " " + (intent || "")).toLowerCase();
    var dangerWords = ["deploy", "merge", "push", "pr ", "execute", "command", "mutate", "github write", "netlify write"];
    for (var i = 0; i < dangerWords.length; i++) {
      if (combined.indexOf(dangerWords[i]) !== -1) {
        return { level: "RED_FORBIDDEN_MUTATION", badge: "fail", label: "RED — FORBIDDEN MUTATION" };
      }
    }
    if (workflowType === "Validator Review" || workflowType === "Report Review") {
      return { level: "YELLOW_REVIEW_ONLY", badge: "warning", label: "YELLOW — REVIEW ONLY" };
    }
    if (workflowType === "Dashboard Polish Request" || workflowType === "Phase Planning Request") {
      return { level: "GREEN_READ_ONLY", badge: "pass", label: "GREEN — READ ONLY" };
    }
    return { level: "ORANGE_REQUIRES_FUTURE_AUTH_STORAGE", badge: "warning", label: "ORANGE — FUTURE AUTH/STORAGE" };
  }

  function updatePhase5aUI() {
    var shell = document.querySelector("[data-phase5a-shell]");
    if (!shell) return;

    var stateDisplay = p5("phase5a-current-state-display");
    if (stateDisplay) {
      stateDisplay.textContent = phase5aState ? phase5aState.current_state : "none";
    }

    ALLOWED_STATES.forEach(function (s) {
      var btn = p5("phase5a-state-" + s);
      if (!btn) return;
      if (!phase5aState) {
        btn.disabled = true;
        return;
      }
      var allowed = ALLOWED_TRANSITIONS[phase5aState.current_state] || [];
      btn.disabled = allowed.indexOf(s) === -1;
    });

    var riskBadge = p5("phase5a-risk-badge");
    var riskDesc = p5("phase5a-risk-description");
    if (riskBadge && riskDesc) {
      if (phase5aState && phase5aState.risk) {
        riskBadge.textContent = phase5aState.risk.label;
        riskBadge.className = "badge " + phase5aState.risk.badge;
        riskDesc.textContent = "Risk classified as " + phase5aState.risk.level + ". Classification based on workflow type and intent content.";
      } else {
        riskBadge.textContent = "NOT CLASSIFIED";
        riskBadge.className = "badge info";
        riskDesc.textContent = "Complete the drafting panel and create a draft to see risk classification.";
      }
    }

    var summaryCard = p5("phase5a-summary-card");
    var summaryGrid = p5("phase5a-summary-grid");
    if (summaryCard && summaryGrid) {
      if (phase5aState) {
        summaryCard.style.display = "block";
        summaryGrid.innerHTML =
          "<div class=\"stat\"><span>Request ID</span><strong>" + phase5aState.request_id + "</strong></div>" +
          "<div class=\"stat\"><span>Current State</span><strong>" + phase5aState.current_state + "</strong></div>" +
          "<div class=\"stat\"><span>Workflow Type</span><strong>" + phase5aState.workflow_type + "</strong></div>" +
          "<div class=\"stat\"><span>Risk Level</span><strong>" + (phase5aState.risk ? phase5aState.risk.level : "none") + "</strong></div>" +
          "<div class=\"stat\"><span>Intent</span><strong>" + (phase5aState.intent || "(none)") + "</strong></div>" +
          "<div class=\"stat\"><span>Disabled Reason</span><strong>DISABLED — PLANNING ONLY</strong></div>" +
          "<div class=\"stat\"><span>Execution Allowed</span><strong class=\"badge fail\">false</strong></div>" +
          "<div class=\"stat\"><span>Mutation Allowed</span><strong class=\"badge fail\">false</strong></div>" +
          "<div class=\"stat\"><span>Backend Write Performed</span><strong class=\"badge fail\">false</strong></div>" +
          "<div class=\"stat\"><span>Required Future</span><strong>Auth, Storage, Queue</strong></div>";
      } else {
        summaryCard.style.display = "none";
      }
    }

    var approvalCard = p5("phase5a-approval-card");
    var approvalGrid = p5("phase5a-approval-grid");
    if (approvalCard && approvalGrid) {
      if (phase5aState && phase5aState.current_state === "approved_for_future_phase") {
        approvalCard.style.display = "block";
        approvalGrid.innerHTML =
          "<div class=\"stat\"><span>Approval Required</span><strong class=\"badge warning\">YES — DISPLAY ONLY</strong></div>" +
          "<div class=\"stat\"><span>Approval State</span><strong>approved_for_future_phase</strong></div>" +
          "<div class=\"stat\"><span>Why Required</span><strong>Future phases will require human approval before any execution or mutation</strong></div>" +
          "<div class=\"stat\"><span>Why No Execution</span><strong>Approval does not execute anything — no auth, no storage, no queue implemented</strong></div>";
      } else if (phase5aState && (phase5aState.current_state === "review_ready" || phase5aState.current_state === "needs_review")) {
        approvalCard.style.display = "block";
        approvalGrid.innerHTML =
          "<div class=\"stat\"><span>Approval Required</span><strong class=\"badge warning\">PENDING REVIEW</strong></div>" +
          "<div class=\"stat\"><span>Approval State</span><strong>pending_human_review</strong></div>" +
          "<div class=\"stat\"><span>Note</span><strong>Approval display only — does not execute. No auth implemented.</strong></div>";
      } else {
        approvalCard.style.display = "none";
      }
    }

    var auditSection = p5("phase5a-audit-trail");
    var auditBody = p5("phase5a-audit-body");
    if (auditSection && auditBody) {
      if (auditEvents.length > 0) {
        auditSection.style.display = "block";
        auditBody.innerHTML = auditEvents.map(function (e) {
          var ts = e.timestamp ? e.timestamp.replace("T", " ").slice(0, 19) : "unknown";
          return "<tr><td><code>" + ts + "</code></td>" +
            "<td>" + e.event_type + "</td>" +
            "<td>" + (e.previous_state || "-") + "</td>" +
            "<td>" + (e.next_state || "-") + "</td>" +
            "<td>" + (e.reason || "-") + "</td>" +
            "<td><span class=\"badge " + (e.risk_badge || "info") + "\">" + (e.risk_label || "-") + "</span></td></tr>";
        }).join("");
      } else {
        auditSection.style.display = "none";
      }
    }

    var dryRunCard = p5("phase5a-dryrun-card");
    if (dryRunCard) {
      dryRunCard.style.display = phase5aState ? "block" : "none";
    }
  }

  function addAuditEvent(eventType, previousState, nextState, reason) {
    auditEvents.push({
      timestamp: timestamp(),
      event_type: eventType,
      previous_state: previousState,
      next_state: nextState,
      reason: reason,
      risk_label: phase5aState && phase5aState.risk ? phase5aState.risk.label : "NONE",
      risk_badge: phase5aState && phase5aState.risk ? phase5aState.risk.badge : "info",
    });
  }

  function createDraft() {
    var titleInput = p5("phase5a-request-title");
    var intentInput = p5("phase5a-intent");
    var scopeInput = p5("phase5a-target-scope");
    var notesInput = p5("phase5a-operator-notes");
    var workflowSelect = p5("phase5a-workflow-type");

    var title = titleInput ? titleInput.value.trim() : "";
    var intent = intentInput ? intentInput.value.trim() : "";
    var scope = scopeInput ? scopeInput.value.trim() : "";
    var notes = notesInput ? notesInput.value.trim() : "";
    var workflowType = workflowSelect ? workflowSelect.value : "Status Review";

    if (!title && !intent) {
      var status = p5("copy-status");
      if (status) status.textContent = "Please enter at least a title or intent.";
      return;
    }

    var risk = classifyRisk(title, intent, workflowType);

    phase5aState = {
      request_id: "REQ-" + generateId().toUpperCase(),
      created_at: timestamp(),
      workflow_type: workflowType,
      title: title,
      intent: intent,
      target_scope: scope,
      operator_notes: notes,
      risk: risk,
      current_state: "draft",
    };

    auditEvents = [];
    addAuditEvent("draft_created", "none", "draft", "Request draft created");
    updatePhase5aUI();

    var status = p5("copy-status");
    if (status) status.textContent = "Draft created: " + phase5aState.request_id;
  }

  function transitionState(nextState) {
    if (!phase5aState) {
      var status = p5("copy-status");
      if (status) status.textContent = "Create a draft first.";
      return;
    }
    var allowed = ALLOWED_TRANSITIONS[phase5aState.current_state] || [];
    if (allowed.indexOf(nextState) === -1) {
      var status = p5("copy-status");
      if (status) status.textContent = "Transition not allowed from " + phase5aState.current_state + " to " + nextState + ".";
      return;
    }
    var prev = phase5aState.current_state;
    phase5aState.current_state = nextState;
    addAuditEvent("state_transition", prev, nextState, "Transitioned to " + nextState);
    updatePhase5aUI();

    var status = p5("copy-status");
    if (status) status.textContent = "State changed: " + prev + " -> " + nextState;
  }

  function resetWorkflow() {
    phase5aState = null;
    auditEvents = [];
    var inputs = ["phase5a-request-title", "phase5a-intent", "phase5a-target-scope", "phase5a-operator-notes"];
    inputs.forEach(function (id) {
      var el = p5(id);
      if (el) el.value = "";
    });
    var wf = p5("phase5a-workflow-type");
    if (wf) wf.selectedIndex = 0;
    updatePhase5aUI();
    var status = p5("copy-status");
    if (status) status.textContent = "Workflow reset. Local state cleared.";
  }

  function initPhase5a() {
    var shell = document.querySelector("[data-phase5a-shell]");
    if (!shell) return;

    var createBtn = p5("phase5a-create-draft-button");
    if (createBtn) createBtn.addEventListener("click", createDraft);

    var resetBtn = p5("phase5a-reset-button");
    if (resetBtn) resetBtn.addEventListener("click", resetWorkflow);

    var stateMap = {
      "phase5a-state-draft": "draft",
      "phase5a-state-needs-review": "needs_review",
      "phase5a-state-review-ready": "review_ready",
      "phase5a-state-changes-requested": "changes_requested",
      "phase5a-state-approved": "approved_for_future_phase",
      "phase5a-state-rejected": "rejected",
      "phase5a-state-cancelled": "cancelled",
      "phase5a-state-archived": "archived",
    };

    Object.keys(stateMap).forEach(function (btnId) {
      var btn = p5(btnId);
      if (btn) {
        btn.addEventListener("click", (function (state) {
          return function () { transitionState(state); };
        })(stateMap[btnId]));
      }
    });

    updatePhase5aUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPhase5a);
  } else {
    initPhase5a();
  }
})();

(function () {
  var packetState = null;

  function p5b(id) { return document.getElementById(id); }

  function generateId() {
    if (window.crypto && window.crypto.randomUUID) {
      return crypto.randomUUID().slice(0, 8);
    }
    return Math.random().toString(36).slice(2, 10);
  }

  function timestamp() { return new Date().toISOString(); }

  function readPhase5aState() {
    var wf = p5b("phase5a-workflow-type");
    var title = p5b("phase5a-request-title");
    var intent = p5b("phase5a-intent");
    var scope = p5b("phase5a-target-scope");
    var notes = p5b("phase5a-operator-notes");
    var stateDisplay = p5b("phase5a-current-state-display");
    var riskBadge = p5b("phase5a-risk-badge");
    var auditBody = p5b("phase5a-audit-body");

    var hasDraft = (title && title.value.trim()) || (intent && intent.value.trim());

    return {
      has_draft: !!hasDraft,
      workflow_type: wf ? wf.value : "Status Review",
      title: title ? title.value.trim() : "",
      intent: intent ? intent.value.trim() : "",
      target_scope: scope ? scope.value.trim() : "",
      operator_notes: notes ? notes.value.trim() : "",
      current_state: stateDisplay ? stateDisplay.textContent : "none",
      risk_label: riskBadge ? riskBadge.textContent : "NOT CLASSIFIED",
      risk_class: riskBadge ? riskBadge.className : "badge info",
      audit_event_count: auditBody ? auditBody.querySelectorAll("tr").length : 0,
    };
  }

  function classifyDangerousTerms(title, intent) {
    var combined = ((title || "") + " " + (intent || "")).toLowerCase();
    var dangerous = [];
    var keywords = ["deploy", "merge", "push", "pr ", "execute", "command", "mutate", "github write", "netlify write"];
    for (var i = 0; i < keywords.length; i++) {
      if (combined.indexOf(keywords[i]) !== -1) {
        dangerous.push(keywords[i].trim());
      }
    }
    return dangerous;
  }

  function requiredFutureDependencies(riskLabel) {
    if (riskLabel.indexOf("RED") !== -1) {
      return ["Human approval", "Auth system", "Persistent storage", "Queue engine", "Execution engine", "Safety review"];
    }
    if (riskLabel.indexOf("ORANGE") !== -1 || riskLabel.indexOf("YELLOW") !== -1) {
      return ["Human approval", "Auth system", "Persistent storage"];
    }
    return ["None required"];
  }

  function generatePacket() {
    var p5a = readPhase5aState();

    if (!p5a.has_draft) {
      var status = p5b("copy-status");
      if (status) status.textContent = "Phase 5B: Create a Phase 5A draft first.";
      return;
    }

    var dangerous = classifyDangerousTerms(p5a.title, p5a.intent);
    var deps = requiredFutureDependencies(p5a.risk_label);
    var executionAllowed = p5a.risk_label.indexOf("RED") === -1 ? "false — read-only phase" : "false — forbidden mutation";
    var mutationAllowed = p5a.risk_label.indexOf("RED") === -1 ? "false — read-only phase" : "false — forbidden mutation";

    var safetyWarnings = [];
    if (dangerous.length > 0) {
      safetyWarnings.push("Contains dangerous terms: " + dangerous.join(", "));
    }
    if (p5a.risk_label.indexOf("RED") !== -1) {
      safetyWarnings.push("Forbidden mutation risk — this request cannot proceed past Phase 5");
    }
    if (p5a.risk_label.indexOf("ORANGE") !== -1) {
      safetyWarnings.push("Requires future auth and storage dependencies");
    }
    if (p5a.current_state === "none" || p5a.current_state === "draft") {
      safetyWarnings.push("Request is still in early state — not reviewed");
    }
    if (safetyWarnings.length === 0) {
      safetyWarnings.push("No safety warnings detected for current draft");
    }

    var disabledReason = "DISABLED — Phase 5 is client-side only. No execution engine, queue, auth, or storage.";

    packetState = {
      packet_id: "PKT-" + generateId().toUpperCase(),
      packet_version: "1.0.0",
      generated_at: timestamp(),
      source_phase: "Original Phase 5A/5B",
      workflow_type: p5a.workflow_type,
      request_title: p5a.title,
      plain_language_intent: p5a.intent,
      target_scope: p5a.target_scope,
      operator_notes: p5a.operator_notes,
      current_state: p5a.current_state,
      risk_classification: p5a.risk_label,
      approval_required: p5a.current_state === "approved_for_future_phase" ? "YES — DISPLAY ONLY" : (p5a.current_state === "needs_review" || p5a.current_state === "review_ready" ? "PENDING REVIEW" : "NOT REQUIRED YET"),
      execution_allowed: executionAllowed,
      mutation_allowed: mutationAllowed,
      backend_write_performed: "false — read-only phase",
      persistence_used: "false — in-memory only",
      required_future_dependencies: deps,
      disabled_reason: disabledReason,
      safety_warnings: safetyWarnings,
      audit_event_count: p5a.audit_event_count,
    };

    updatePacketUI(p5a, dangerous);
  }

  function updatePacketUI(p5a, dangerous) {
    var fieldsArea = p5b("phase5b-packet-fields");
    var packetGrid = p5b("phase5b-packet-grid");
    if (fieldsArea && packetGrid) {
      fieldsArea.style.display = "block";
      packetGrid.innerHTML =
        "<div class=\"stat\"><span>Packet ID</span><strong>" + packetState.packet_id + "</strong></div>" +
        "<div class=\"stat\"><span>Version</span><strong>" + packetState.packet_version + "</strong></div>" +
        "<div class=\"stat\"><span>Generated</span><strong>" + packetState.generated_at.replace("T", " ").slice(0, 19) + "</strong></div>" +
        "<div class=\"stat\"><span>Source Phase</span><strong>" + packetState.source_phase + "</strong></div>" +
        "<div class=\"stat\"><span>Workflow Type</span><strong>" + packetState.workflow_type + "</strong></div>" +
        "<div class=\"stat\"><span>Title</span><strong>" + (packetState.request_title || "(none)") + "</strong></div>" +
        "<div class=\"stat\"><span>Intent</span><strong>" + (packetState.plain_language_intent || "(none)") + "</strong></div>" +
        "<div class=\"stat\"><span>Scope</span><strong>" + (packetState.target_scope || "(none)") + "</strong></div>" +
        "<div class=\"stat\"><span>Current State</span><strong>" + packetState.current_state + "</strong></div>" +
        "<div class=\"stat\"><span>Risk</span><strong class=\"" + p5a.risk_class + "\">" + p5a.risk_label + "</strong></div>" +
        "<div class=\"stat\"><span>Execution Allowed</span><strong>false</strong></div>" +
        "<div class=\"stat\"><span>Mutation Allowed</span><strong>false</strong></div>" +
        "<div class=\"stat\"><span>Backend Write</span><strong>false</strong></div>" +
        "<div class=\"stat\"><span>Persistence</span><strong>false</strong></div>" +
        "<div class=\"stat\"><span>Future Dependencies</span><strong>" + packetState.required_future_dependencies.join(", ") + "</strong></div>" +
        "<div class=\"stat\"><span>Disabled Reason</span><strong>" + packetState.disabled_reason + "</strong></div>" +
        "<div class=\"stat\"><span>Safety Warnings</span><strong>" + packetState.safety_warnings.join("; ") + "</strong></div>" +
        "<div class=\"stat\"><span>Audit Events</span><strong>" + packetState.audit_event_count + "</strong></div>";
    }

    var validationBadge = p5b("phase5b-validation-badge");
    var validationDesc = p5b("phase5b-validation-description");
    var validationDetails = p5b("phase5b-validation-details");
    var validationGrid = p5b("phase5b-validation-grid");

    if (validationBadge && validationDesc && validationDetails && validationGrid) {
      var hasDraft = p5a.has_draft;
      var hasTitleOrIntent = !!(packetState.request_title || packetState.plain_language_intent);
      var hasRisk = packetState.risk_classification !== "NOT CLASSIFIED";
      var hasState = packetState.current_state !== "none";
      var execFalse = packetState.execution_allowed.indexOf("false") !== -1;
      var mutFalse = packetState.mutation_allowed.indexOf("false") !== -1;
      var backendFalse = packetState.backend_write_performed.indexOf("false") !== -1;
      var persistFalse = packetState.persistence_used.indexOf("false") !== -1;
      var hasDangerous = dangerous.length > 0;
      var hasDeps = packetState.required_future_dependencies.length > 0 && packetState.required_future_dependencies[0] !== "None required";

      var checksPassed = 0;
      var checksTotal = 10;
      var checkResults = [];

      function addCheck(passed, label) {
        checkResults.push({ passed: passed, label: label });
        if (passed) checksPassed++;
      }

      addCheck(hasDraft, "Draft exists");
      addCheck(hasTitleOrIntent, "Title or intent exists");
      addCheck(hasRisk, "Risk classification exists");
      addCheck(hasState, "Current state exists");
      addCheck(execFalse, "Execution not allowed");
      addCheck(mutFalse, "Mutation not allowed");
      addCheck(backendFalse, "No backend write");
      addCheck(persistFalse, "No persistence");
      addCheck(!hasDangerous, "No dangerous terms flagged");
      addCheck(true, "Future dependencies listed");

      var allPass = checksPassed === checksTotal;
      var hasWarnings = !hasDangerous && checksPassed >= checksTotal - 2;

      var verdict, badgeClass;
      if (allPass) {
        verdict = "PACKET_VALID_LOCAL_ONLY";
        badgeClass = "pass";
      } else if (hasDangerous || checksPassed < checksTotal - 3) {
        verdict = "PACKET_BLOCKED_FORBIDDEN_MUTATION";
        badgeClass = "fail";
      } else {
        verdict = "PACKET_WARNING_REVIEW_REQUIRED";
        badgeClass = "warning";
      }

      validationBadge.textContent = verdict;
      validationBadge.className = "badge " + badgeClass;
      validationDesc.textContent = checksPassed + "/" + checksTotal + " validation checks passed. Verdict: " + verdict;
      validationDetails.style.display = "block";

      var gridHtml = "";
      for (var i = 0; i < checkResults.length; i++) {
        var c = checkResults[i];
        gridHtml += "<div class=\"stat\" style=\"padding:0.5rem 0.75rem;\">" +
          "<span>" + c.label + "</span>" +
          "<strong class=\"badge " + (c.passed ? "pass" : "fail") + "\" style=\"font-size:0.7rem;\">" + (c.passed ? "PASS" : "FAIL") + "</strong></div>";
      }
      validationGrid.innerHTML = gridHtml;
    }

    var jsonPanel = p5b("phase5b-json-panel");
    var jsonPreview = p5b("phase5b-json-preview");
    if (jsonPanel && jsonPreview) {
      jsonPanel.style.display = "block";
      jsonPreview.textContent = JSON.stringify(packetState, null, 2);
    }

    var mdPanel = p5b("phase5b-markdown-panel");
    var mdPreview = p5b("phase5b-markdown-preview");
    if (mdPanel && mdPreview) {
      mdPanel.style.display = "block";
      mdPreview.textContent = [
        "# Request Packet",
        "",
        "**Packet ID:** " + packetState.packet_id,
        "**Version:** " + packetState.packet_version,
        "**Generated At:** " + packetState.generated_at,
        "**Source Phase:** " + packetState.source_phase,
        "",
        "## Request",
        "**Workflow Type:** " + packetState.workflow_type,
        "**Title:** " + (packetState.request_title || "(none)"),
        "**Intent:** " + (packetState.plain_language_intent || "(none)"),
        "**Scope:** " + (packetState.target_scope || "(none)"),
        "**Notes:** " + (packetState.operator_notes || "(none)"),
        "",
        "## State & Risk",
        "**Current State:** " + packetState.current_state,
        "**Risk Classification:** " + packetState.risk_classification,
        "**Approval Required:** " + packetState.approval_required,
        "",
        "## Safety Boundary",
        "**Execution Allowed:** " + packetState.execution_allowed,
        "**Mutation Allowed:** " + packetState.mutation_allowed,
        "**Backend Write Performed:** " + packetState.backend_write_performed,
        "**Persistence Used:** " + packetState.persistence_used,
        "",
        "## Required Future Dependencies",
        packetState.required_future_dependencies.map(function (d) { return "- " + d; }).join("\n"),
        "",
        "## Safety Warnings",
        packetState.safety_warnings.map(function (w) { return "- " + w; }).join("\n"),
        "",
        "## Audit Summary",
        "**Audit Event Count:** " + packetState.audit_event_count,
        "",
        "## Disabled Reason",
        packetState.disabled_reason,
      ].join("\n");
    }

    var safetyCard = p5b("phase5b-safety-summary");
    if (safetyCard) {
      safetyCard.style.display = "block";
    }

    var status = p5b("copy-status");
    if (status) status.textContent = "Phase 5B: Packet generated: " + packetState.packet_id;
  }

  function clearPacket() {
    packetState = null;

    var fieldsArea = p5b("phase5b-packet-fields");
    if (fieldsArea) fieldsArea.style.display = "none";

    var validationBadge = p5b("phase5b-validation-badge");
    var validationDesc = p5b("phase5b-validation-description");
    var validationDetails = p5b("phase5b-validation-details");
    if (validationBadge) { validationBadge.textContent = "NOT VALIDATED"; validationBadge.className = "badge info"; }
    if (validationDesc) validationDesc.textContent = "Generate a packet to see local validation results.";
    if (validationDetails) validationDetails.style.display = "none";

    var jsonPanel = p5b("phase5b-json-panel");
    var jsonPreview = p5b("phase5b-json-preview");
    if (jsonPanel) jsonPanel.style.display = "none";
    if (jsonPreview) jsonPreview.textContent = "No packet generated yet.";

    var mdPanel = p5b("phase5b-markdown-panel");
    var mdPreview = p5b("phase5b-markdown-preview");
    if (mdPanel) mdPanel.style.display = "none";
    if (mdPreview) mdPreview.textContent = "No packet generated yet.";

    var safetyCard = p5b("phase5b-safety-summary");
    if (safetyCard) safetyCard.style.display = "none";

    var status = p5b("copy-status");
    if (status) status.textContent = "Phase 5B: Packet cleared.";
  }

  function getPacketCopyText(kind) {
    if (!packetState) return "";
    if (kind === "json") return JSON.stringify(packetState, null, 2);
    if (kind === "markdown") {
      var md = p5b("phase5b-markdown-preview");
      return md ? md.textContent : "";
    }
    if (kind === "safety") {
      return [
        "PHASE 5B SAFETY SUMMARY",
        "This packet is generated locally.",
        "It is not saved.",
        "It is not sent anywhere.",
        "It is not queued.",
        "It is not executed.",
        "It does not write to the backend.",
        "It does not mutate GitHub or Netlify.",
        "It disappears on refresh unless the operator copies it manually.",
        "Packet ID: " + (packetState.packet_id || "N/A"),
        "Risk: " + (packetState.risk_classification || "N/A"),
        "State: " + (packetState.current_state || "N/A"),
      ].join("\n");
    }
    return "";
  }

  function initPhase5b() {
    var shell = document.querySelector("[data-phase5b-builder]");
    if (!shell) return;

    var genBtn = p5b("phase5b-generate-packet-button");
    if (genBtn) genBtn.addEventListener("click", generatePacket);

    var clearBtn = p5b("phase5b-clear-packet-button");
    if (clearBtn) clearBtn.addEventListener("click", clearPacket);

    var copyJsonBtn = p5b("phase5b-copy-json-button");
    if (copyJsonBtn) {
      copyJsonBtn.addEventListener("click", function () {
        var text = getPacketCopyText("json");
        if (!text) return;
        Promise.resolve(
          navigator.clipboard && navigator.clipboard.writeText
            ? navigator.clipboard.writeText(text)
            : function () {
                var field = document.createElement("textarea");
                field.value = text;
                field.style.position = "fixed";
                field.style.left = "-9999px";
                document.body.appendChild(field);
                field.select();
                document.execCommand("copy");
                document.body.removeChild(field);
              }()
        ).then(function () {
          var status = p5b("copy-status");
          if (status) status.textContent = "Phase 5B: Packet JSON copied.";
        }).catch(function () {});
      });
    }

    var copyMdBtn = p5b("phase5b-copy-markdown-button");
    if (copyMdBtn) {
      copyMdBtn.addEventListener("click", function () {
        var text = getPacketCopyText("markdown");
        if (!text) return;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            var status = p5b("copy-status");
            if (status) status.textContent = "Phase 5B: Packet Markdown copied.";
          }).catch(function () {});
        }
      });
    }

    var copySafetyBtn = p5b("phase5b-copy-safety-button");
    if (copySafetyBtn) {
      copySafetyBtn.addEventListener("click", function () {
        var text = getPacketCopyText("safety");
        if (!text) return;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            var status = p5b("copy-status");
            if (status) status.textContent = "Phase 5B: Safety summary copied.";
          }).catch(function () {});
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPhase5b);
  } else {
    initPhase5b();
  }
})();

(function () {
  var reviewBoard = [];
  var ledgerEvents = [];
  var currentPacket = null;

  function p5c(id) { return document.getElementById(id); }

  function generateId() {
    if (window.crypto && window.crypto.randomUUID) {
      return crypto.randomUUID().slice(0, 8);
    }
    return Math.random().toString(36).slice(2, 10);
  }

  function timestamp() { return new Date().toISOString(); }

  function getPacketFromPhase5b() {
    var status = p5c("copy-status");
    var packetJson = p5c("phase5b-json-preview");
    if (!packetJson || !packetJson.textContent || packetJson.textContent === "No packet generated yet.") {
      if (status) status.textContent = "Phase 5C: Generate a Phase 5B packet first.";
      return null;
    }
    try {
      return JSON.parse(packetJson.textContent);
    } catch (e) {
      if (status) status.textContent = "Phase 5C: Could not parse Phase 5B packet.";
      return null;
    }
  }

  function addPacketToReviewBoard(packet) {
    if (!packet || !packet.packet_id) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Invalid packet.";
      return;
    }

    var exists = false;
    for (var i = 0; i < reviewBoard.length; i++) {
      if (reviewBoard[i].packet_id === packet.packet_id) {
        exists = true;
        break;
      }
    }
    if (exists) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Packet " + packet.packet_id + " already in review board.";
      return;
    }

    reviewBoard.push({
      packet_id: packet.packet_id || "unknown",
      request_title: packet.request_title || packet.title || "(untitled)",
      workflow_type: packet.workflow_type || "unknown",
      risk_classification: packet.risk_classification || "NOT CLASSIFIED",
      current_state: packet.current_state || "unknown",
      review_decision: "pending_review",
      decision_timestamp: null,
      notes_count: 0,
      _source: packet,
    });

    updateReviewBoardUI();
    var status = p5c("copy-status");
    if (status) status.textContent = "Phase 5C: Added " + packet.packet_id + " to review board.";
  }

  function parsePastedPacket() {
    var textarea = p5c("phase5c-pasted-json");
    if (!textarea || !textarea.value.trim()) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Paste packet JSON first.";
      return;
    }
    try {
      var parsed = JSON.parse(textarea.value.trim());
      if (!parsed.packet_id) {
        var status = p5c("copy-status");
        if (status) status.textContent = "Phase 5C: Pasted JSON has no packet_id.";
        return;
      }
      addPacketToReviewBoard(parsed);
      textarea.value = "";
    } catch (e) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Invalid JSON — " + e.message;
    }
  }

  function clearReviewBoard() {
    reviewBoard = [];
    ledgerEvents = [];
    updateReviewBoardUI();
    var status = p5c("copy-status");
    if (status) status.textContent = "Phase 5C: Review board cleared.";
  }

  function recordDecision() {
    var packetSelect = p5c("phase5c-decision-packet-select");
    var decisionSelect = p5c("phase5c-decision-select");
    var noteInput = p5c("phase5c-review-note");

    if (!packetSelect || !decisionSelect) return;

    var selectedPacketId = packetSelect.value;
    if (!selectedPacketId) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Select a packet first.";
      return;
    }

    var decision = decisionSelect.value || "pending_review";
    var note = noteInput ? noteInput.value.trim() : "";

    var found = null;
    for (var i = 0; i < reviewBoard.length; i++) {
      if (reviewBoard[i].packet_id === selectedPacketId) {
        found = reviewBoard[i];
        break;
      }
    }
    if (!found) {
      var status = p5c("copy-status");
      if (status) status.textContent = "Phase 5C: Packet not found in review board.";
      return;
    }

    var previousDecision = found.review_decision;
    found.review_decision = decision;
    found.decision_timestamp = timestamp();
    found.notes_count = note ? found.notes_count + 1 : found.notes_count;

    ledgerEvents.push({
      ledger_event_id: "LEDGER-" + generateId().toUpperCase(),
      timestamp: timestamp(),
      packet_id: found.packet_id,
      previous_decision: previousDecision,
      next_decision: decision,
      reviewer_display: "local-operator",
      note_summary: note || "(no note)",
      risk_classification: found.risk_classification,
      execution_allowed: false,
      mutation_allowed: false,
      backend_write_performed: false,
    });

    updateReviewBoardUI();

    var status = p5c("copy-status");
    if (status) status.textContent = "Phase 5C: Decision recorded for " + selectedPacketId + " -> " + decision;
  }

  function renderLedgerJSON() {
    var data = {
      review_board_version: "1.0.0",
      generated_at: timestamp(),
      packet_count: reviewBoard.length,
      ledger_event_count: ledgerEvents.length,
      packets: reviewBoard.map(function (p) {
        return {
          packet_id: p.packet_id,
          request_title: p.request_title,
          workflow_type: p.workflow_type,
          risk_classification: p.risk_classification,
          current_state: p.current_state,
          review_decision: p.review_decision,
          decision_timestamp: p.decision_timestamp,
          notes_count: p.notes_count,
        };
      }),
      decisions: ledgerEvents.map(function (e) {
        return {
          ledger_event_id: e.ledger_event_id,
          timestamp: e.timestamp,
          packet_id: e.packet_id,
          previous_decision: e.previous_decision,
          next_decision: e.next_decision,
          reviewer_display: e.reviewer_display,
          note_summary: e.note_summary,
          risk_classification: e.risk_classification,
          execution_allowed: e.execution_allowed,
          mutation_allowed: e.mutation_allowed,
          backend_write_performed: e.backend_write_performed,
        };
      }),
      safety_summary: {
        execution_allowed: false,
        mutation_allowed: false,
        backend_write_performed: false,
        persistence_used: false,
        external_api_calls: false,
      },
    };
    return JSON.stringify(data, null, 2);
  }

  function renderLedgerMarkdown() {
    var lines = [];
    lines.push("# Review Board & Decision Ledger");
    lines.push("");
    lines.push("**Generated At:** " + timestamp());
    lines.push("**Packet Count:** " + reviewBoard.length);
    lines.push("**Ledger Event Count:** " + ledgerEvents.length);
    lines.push("");
    lines.push("## Review Board Packet List");
    lines.push("");
    if (reviewBoard.length === 0) {
      lines.push("*No packets in review board.*");
    } else {
      for (var i = 0; i < reviewBoard.length; i++) {
        var p = reviewBoard[i];
        lines.push("- **" + p.packet_id + "**: " + p.request_title + " (" + p.workflow_type + ") — Risk: " + p.risk_classification + " — Decision: " + p.review_decision);
      }
    }
    lines.push("");
    lines.push("## Decision History");
    lines.push("");
    if (ledgerEvents.length === 0) {
      lines.push("*No decisions recorded.*");
    } else {
      for (var j = 0; j < ledgerEvents.length; j++) {
        var e = ledgerEvents[j];
        lines.push("- **" + e.ledger_event_id + "** (" + e.timestamp.replace("T", " ").slice(0, 19) + "): " + e.packet_id + " — " + e.previous_decision + " -> " + e.next_decision + " — Note: " + e.note_summary);
      }
    }
    lines.push("");
    lines.push("## Safety Boundary");
    lines.push("- Execution Allowed: false");
    lines.push("- Mutation Allowed: false");
    lines.push("- Backend Write Performed: false");
    lines.push("- Persistence Used: false");
    lines.push("- External API Calls: false");
    lines.push("");
    lines.push("## Future Dependency Warning");
    lines.push("This review board and decision ledger are temporary, local-only, and in-memory.");
    lines.push("No persistence, no backend writes, no execution, no mutation, no GitHub/Netlify API calls.");
    lines.push("Refresh clears all state unless manually copied.");
    return lines.join("\n");
  }

  function renderDecisionSummary() {
    var lines = [];
    lines.push("PHASE 5C DECISION SUMMARY");
    lines.push("Generated At: " + timestamp());
    lines.push("Packets in Review: " + reviewBoard.length);
    lines.push("Ledger Events: " + ledgerEvents.length);
    lines.push("");
    for (var i = 0; i < reviewBoard.length; i++) {
      var p = reviewBoard[i];
      lines.push("Packet: " + p.packet_id + " | " + p.request_title + " | Decision: " + p.review_decision + " | Risk: " + p.risk_classification);
    }
    lines.push("");
    lines.push("Safety: Execution=false Mutation=false BackendWrite=false Persistence=false");
    lines.push("This is a local-only review board. Nothing is saved, sent, or executed.");
    return lines.join("\n");
  }

  function updateReviewBoardUI() {
    var reviewBody = p5c("phase5c-review-body");
    if (reviewBody) {
      if (reviewBoard.length === 0) {
        reviewBody.innerHTML = '<tr><td colspan="7" class="empty">No packets in review board. Add a packet to begin.</td></tr>';
      } else {
        reviewBody.innerHTML = reviewBoard.map(function (p) {
          return "<tr>" +
            "<td><code>" + p.packet_id + "</code></td>" +
            "<td>" + p.request_title + "</td>" +
            "<td>" + p.workflow_type + "</td>" +
            "<td>" + p.risk_classification + "</td>" +
            "<td>" + p.current_state + "</td>" +
            "<td>" + p.review_decision + "</td>" +
            "<td>" + p.notes_count + "</td>" +
            "</tr>";
        }).join("");
      }
    }

    var ledgerBody = p5c("phase5c-ledger-body");
    if (ledgerBody) {
      if (ledgerEvents.length === 0) {
        ledgerBody.innerHTML = '<tr><td colspan="6" class="empty">No ledger events yet. Record a decision to populate.</td></tr>';
      } else {
        ledgerBody.innerHTML = ledgerEvents.map(function (e) {
          var ts = e.timestamp ? e.timestamp.replace("T", " ").slice(0, 19) : "unknown";
          return "<tr>" +
            "<td><code>" + ts + "</code></td>" +
            "<td><code>" + e.packet_id + "</code></td>" +
            "<td>" + (e.previous_decision || "-") + "</td>" +
            "<td>" + e.next_decision + "</td>" +
            "<td>" + e.note_summary + "</td>" +
            "<td>" + e.risk_classification + "</td>" +
            "</tr>";
        }).join("");
      }
    }

    var packetSelect = p5c("phase5c-decision-packet-select");
    if (packetSelect) {
      if (reviewBoard.length === 0) {
        packetSelect.innerHTML = '<option value="">— No packets available —</option>';
      } else {
        var options = reviewBoard.map(function (p) {
          return '<option value="' + p.packet_id + '">' + p.packet_id + " — " + p.request_title + "</option>";
        });
        packetSelect.innerHTML = '<option value="">— Select a packet —</option>' + options.join("");
      }
    }

    var jsonPanel = p5c("phase5c-ledger-json-panel");
    var jsonPreview = p5c("phase5c-ledger-json-preview");
    if (jsonPanel && jsonPreview) {
      if (reviewBoard.length > 0 || ledgerEvents.length > 0) {
        jsonPanel.style.display = "block";
        jsonPreview.textContent = renderLedgerJSON();
      } else {
        jsonPanel.style.display = "none";
        jsonPreview.textContent = "No ledger generated yet.";
      }
    }

    var mdPanel = p5c("phase5c-ledger-markdown-panel");
    var mdPreview = p5c("phase5c-ledger-markdown-preview");
    if (mdPanel && mdPreview) {
      if (reviewBoard.length > 0 || ledgerEvents.length > 0) {
        mdPanel.style.display = "block";
        mdPreview.textContent = renderLedgerMarkdown();
      } else {
        mdPanel.style.display = "none";
        mdPreview.textContent = "No ledger generated yet.";
      }
    }
  }

  function initPhase5c() {
    var shell = document.querySelector("[data-phase5c-review-board]");
    if (!shell) return;

    var addCurrentBtn = p5c("phase5c-add-current-packet");
    if (addCurrentBtn) {
      addCurrentBtn.addEventListener("click", function () {
        var packet = getPacketFromPhase5b();
        if (packet) addPacketToReviewBoard(packet);
      });
    }

    var parseBtn = p5c("phase5c-parse-pasted-packet");
    if (parseBtn) {
      parseBtn.addEventListener("click", parsePastedPacket);
    }

    var clearBtn = p5c("phase5c-clear-review-board");
    if (clearBtn) {
      clearBtn.addEventListener("click", clearReviewBoard);
    }

    var recordBtn = p5c("phase5c-record-decision");
    if (recordBtn) {
      recordBtn.addEventListener("click", recordDecision);
    }

    var copyJsonBtn = p5c("phase5c-copy-ledger-json");
    if (copyJsonBtn) {
      copyJsonBtn.addEventListener("click", function () {
        var text = renderLedgerJSON();
        var status = p5c("copy-status");
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            if (status) status.textContent = "Phase 5C: Ledger JSON copied.";
          }).catch(function () {});
        } else {
          var field = document.createElement("textarea");
          field.value = text;
          field.style.position = "fixed";
          field.style.left = "-9999px";
          document.body.appendChild(field);
          field.select();
          document.execCommand("copy");
          document.body.removeChild(field);
          if (status) status.textContent = "Phase 5C: Ledger JSON copied.";
        }
      });
    }

    var copyMdBtn = p5c("phase5c-copy-ledger-markdown");
    if (copyMdBtn) {
      copyMdBtn.addEventListener("click", function () {
        var text = renderLedgerMarkdown();
        var status = p5c("copy-status");
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            if (status) status.textContent = "Phase 5C: Ledger Markdown copied.";
          }).catch(function () {});
        } else {
          var field = document.createElement("textarea");
          field.value = text;
          field.style.position = "fixed";
          field.style.left = "-9999px";
          document.body.appendChild(field);
          field.select();
          document.execCommand("copy");
          document.body.removeChild(field);
          if (status) status.textContent = "Phase 5C: Ledger Markdown copied.";
        }
      });
    }

    var copySummaryBtn = p5c("phase5c-copy-decision-summary");
    if (copySummaryBtn) {
      copySummaryBtn.addEventListener("click", function () {
        var text = renderDecisionSummary();
        var status = p5c("copy-status");
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            if (status) status.textContent = "Phase 5C: Decision summary copied.";
          }).catch(function () {});
        } else {
          var field = document.createElement("textarea");
          field.value = text;
          field.style.position = "fixed";
          field.style.left = "-9999px";
          document.body.appendChild(field);
          field.select();
          document.execCommand("copy");
          document.body.removeChild(field);
          if (status) status.textContent = "Phase 5C: Decision summary copied.";
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPhase5c);
  } else {
    initPhase5c();
  }
})();
