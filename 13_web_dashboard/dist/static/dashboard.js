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
  var runbookState = {
    selectedScenarioId: "safe_status_review",
  };

  var stepTitles = [
    "Draft request",
    "Classify risk",
    "Generate request packet",
    "Add to review board",
    "Record review decision",
    "Generate decision ledger",
    "Compose handoff",
    "Copy final runbook",
  ];

  var scenarios = [
    {
      scenario_id: "safe_status_review",
      scenario_title: "Safe Status Review",
      workflow_type: "Read-only status review",
      sample_request_title: "Review the current dashboard state",
      sample_intent: "Confirm the dashboard remains static, local, and ready for operator review.",
      sample_scope: "13_web_dashboard and interface_phase_5 reports",
      expected_risk: "LOW_READ_ONLY",
      expected_review_decision: "approve_for_future_phase",
      expected_handoff_type: "copyable_runbook_summary",
      safety_note: "No write path is present; the runbook stays local and temporary.",
      operator_goal: "Validate the dashboard and preserve a clean operator handoff.",
      request_draft: "Draft a read-only review request for the current dashboard state.",
      packet_summary: "Packet stays local and captures the read-only review scope.",
      review_decision_summary: "Review board marks the flow as safe for a local handoff summary.",
      ledger_summary: "Decision ledger records a read-only approval with no mutation path.",
      handoff_summary: "Handoff stays copy/paste only and references only local state.",
      next_action: "Review the transcript, copy the runbook if useful, and continue the local operator workflow.",
      blocked_actions: [],
      step_statuses: ["completed", "completed", "completed", "completed", "completed", "completed", "completed", "completed"],
      step_details: [
        "Request drafted as a read-only operator review.",
        "Risk remains low because nothing persists or mutates.",
        "Packet is generated in memory only.",
        "Review board snapshot stays local to the dashboard.",
        "Decision is recorded as a safe local review.",
        "Decision ledger remains temporary and copy-only.",
        "Handoff composer references only in-browser state.",
        "Final runbook is available for copy/paste.",
      ],
    },
    {
      scenario_id: "validator_review",
      scenario_title: "Validator Review",
      workflow_type: "Validator and report audit",
      sample_request_title: "Review phase validators and reports",
      sample_intent: "Confirm the validators, reports, and dashboard markers remain consistent after a local change.",
      sample_scope: "scripts/ and 09_exports/interface_phase_5/",
      expected_risk: "LOW_REVIEW",
      expected_review_decision: "approve_with_notes",
      expected_handoff_type: "validator_runbook_summary",
      safety_note: "The flow is still copy-only and does not allow backend mutation.",
      operator_goal: "Audit validator output and package the result as a local runbook.",
      request_draft: "Draft a validator review request for the current local phase work.",
      packet_summary: "Packet captures the validator set and the relevant report scope.",
      review_decision_summary: "Review board records an approve-with-notes decision for local follow-up.",
      ledger_summary: "Ledger keeps the validator review trail in memory only.",
      handoff_summary: "Handoff captures the validator review notes and copyable summary.",
      next_action: "Read the validator notes, copy the runbook summary, and continue with the next local check.",
      blocked_actions: [],
      step_statuses: ["completed", "completed", "completed", "completed", "warning", "completed", "completed", "warning"],
      step_details: [
        "Request drafted around validator and report review.",
        "Risk stays low because the path is local-only.",
        "Request packet is generated in memory.",
        "Review board receives the packet snapshot.",
        "Decision is recorded with a small warning for follow-up.",
        "Decision ledger stays local and temporary.",
        "Handoff is composed as copy/paste only.",
        "Runbook copy remains optional and local.",
      ],
    },
    {
      scenario_id: "dashboard_polish_request",
      scenario_title: "Dashboard Polish Request",
      workflow_type: "UI polish request",
      sample_request_title: "Polish the read-only dashboard layout",
      sample_intent: "Review compact layout refinements, spacing, and readability without changing behavior.",
      sample_scope: "13_web_dashboard static surface",
      expected_risk: "LOW_UI",
      expected_review_decision: "approve_with_layout_notes",
      expected_handoff_type: "ui_polish_runbook_summary",
      safety_note: "This remains a local presentation review with no execution or storage.",
      operator_goal: "Check the presentation surface and keep the review narrow.",
      request_draft: "Draft a layout polish request for the dashboard surface.",
      packet_summary: "Packet describes the compact UI surface and the desired polish scope.",
      review_decision_summary: "Review board approves the polish request with layout notes.",
      ledger_summary: "Ledger notes the compact UI follow-up and keeps it local.",
      handoff_summary: "Handoff is a local summary for the next presentation pass.",
      next_action: "Review the compact UI notes, then keep the dashboard focused and static.",
      blocked_actions: [],
      step_statuses: ["completed", "completed", "completed", "completed", "completed", "completed", "completed", "warning"],
      step_details: [
        "Draft describes the surface polish request.",
        "Risk remains low because the flow is presentation-only.",
        "Packet is generated locally.",
        "Review board captures the UI polish request.",
        "Decision is recorded with layout notes.",
        "Decision ledger stays temporary.",
        "Handoff remains copy/paste only.",
        "Final copy is optional and local.",
      ],
    },
    {
      scenario_id: "safety_review_request",
      scenario_title: "Safety Review Request",
      workflow_type: "Safety review",
      sample_request_title: "Review safety boundaries and no-go conditions",
      sample_intent: "Confirm the operator flow remains local, temporary, and free of mutation paths.",
      sample_scope: "Phase 5A through Phase 5E dashboard flow",
      expected_risk: "MEDIUM_SAFETY",
      expected_review_decision: "approve_with_safety_notes",
      expected_handoff_type: "safety_runbook_summary",
      safety_note: "Safety boundaries remain explicit and no mutable actions are allowed.",
      operator_goal: "Check the safety boundary and keep the workflow in read-only mode.",
      request_draft: "Draft a safety review request for the end-to-end simulator.",
      packet_summary: "Packet records the safety boundary review and local-only rule set.",
      review_decision_summary: "Review board approves the safety review with notes to keep the flow temporary.",
      ledger_summary: "Ledger records the safety review and the no-go conditions.",
      handoff_summary: "Handoff points to the safety boundary and the local-only rule set.",
      next_action: "Re-read the safety gate and keep the operator flow copy-only.",
      blocked_actions: [],
      step_statuses: ["completed", "completed", "completed", "warning", "completed", "warning", "completed", "warning"],
      step_details: [
        "Draft frames the safety review request.",
        "Risk is elevated only to the safety-check level.",
        "Packet remains local and temporary.",
        "Review board highlights the safety boundary.",
        "Decision focuses on explicit no-go conditions.",
        "Decision ledger keeps the safety notes local.",
        "Handoff summarises the safety gate and no-go notes.",
        "Copy step remains optional and local.",
      ],
    },
    {
      scenario_id: "forbidden_mutation_attempt",
      scenario_title: "Forbidden Mutation Attempt",
      workflow_type: "Mutation attempt blocked",
      sample_request_title: "Try to mutate the dashboard or backend",
      sample_intent: "Provoke the safety gate with an explicitly forbidden mutation path.",
      sample_scope: "Any write, deploy, merge, push, or PR path",
      expected_risk: "RED_FORBIDDEN_MUTATION",
      expected_review_decision: "reject_and_rewrite_as_planning_only",
      expected_handoff_type: "planning_only_no_go_note",
      safety_note: "The simulator must stop the mutation path and keep the runbook planning-only.",
      operator_goal: "Surface the no-go boundary and keep the scenario local only.",
      request_draft: "Draft a forbidden mutation attempt to prove the simulator blocks it.",
      packet_summary: "Packet remains local, but the mutation path is blocked before any action can proceed.",
      review_decision_summary: "Review board rejects the mutation path and redirects to planning-only text.",
      ledger_summary: "Ledger records the rejection and the blocked mutation attempt.",
      handoff_summary: "Handoff recommendation is no-go unless rewritten as planning-only.",
      next_action: "Rewrite the request as planning-only and stop before any mutation or execution.",
      blocked_actions: ["mutation path", "execution path", "write path", "deploy path", "merge path", "push path", "PR path"],
      step_statuses: ["completed", "warning", "blocked", "blocked", "blocked", "blocked", "blocked", "blocked"],
      step_details: [
        "Draft exists only to show the blocked path.",
        "Risk is classified as RED_FORBIDDEN_MUTATION.",
        "Request packet generation is blocked immediately.",
        "Review board intake is blocked for the mutation path.",
        "Decision cannot proceed on the forbidden path.",
        "Decision ledger stays blocked and local.",
        "Handoff recommendation is no-go unless rewritten as planning-only.",
        "Copy step remains a planning-only reminder.",
      ],
    },
  ];

  function p5e(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function timestamp() {
    return new Date().toISOString();
  }

  function textOf(node) {
    return node ? node.textContent.replace(/\s+/g, " ").trim() : "";
  }

  function stat(label, value, badgeClass) {
    var strongClass = badgeClass ? ' class="badge ' + badgeClass + '"' : "";
    return "<div class=\"stat\"><span>" + escapeHtml(label) + "</span><strong" + strongClass + ">" + escapeHtml(value) + "</strong></div>";
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p5e("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p5e(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function getScenario(id) {
    for (var i = 0; i < scenarios.length; i++) {
      if (scenarios[i].scenario_id === id) {
        return scenarios[i];
      }
    }
    return scenarios[0];
  }

  function getSelectedScenario() {
    return getScenario(runbookState.selectedScenarioId);
  }

  function badgeForStatus(status) {
    switch (status) {
      case "completed":
        return "pass";
      case "blocked":
        return "fail";
      case "warning":
        return "warning";
      case "pending":
      default:
        return "info";
    }
  }

  function renderScenarioRows() {
    return scenarios.map(function (scenario) {
      return "<tr>" +
        "<td><code>" + escapeHtml(scenario.scenario_id) + "</code></td>" +
        "<td>" + escapeHtml(scenario.scenario_title) + "</td>" +
        "<td>" + escapeHtml(scenario.workflow_type) + "</td>" +
        "<td>" + escapeHtml(scenario.sample_request_title) + "</td>" +
        "<td>" + escapeHtml(scenario.expected_risk) + "</td>" +
        "<td>" + escapeHtml(scenario.expected_review_decision) + "</td>" +
        "<td>" + escapeHtml(scenario.expected_handoff_type) + "</td>" +
        "<td>" + escapeHtml(scenario.safety_note) + "</td>" +
        "</tr>";
    }).join("");
  }

  function renderScenarioOptions(currentId) {
    return scenarios.map(function (scenario) {
      var selected = scenario.scenario_id === currentId ? " selected" : "";
      return '<option value="' + escapeHtml(scenario.scenario_id) + '"' + selected + '>' + escapeHtml(scenario.scenario_title) + "</option>";
    }).join("");
  }

  function renderStepRows(scenario) {
    return stepTitles.map(function (title, index) {
      var status = scenario.step_statuses[index] || "pending";
      var detail = scenario.step_details[index] || "";
      return "<tr>" +
        "<td>" + escapeHtml(title) + "</td>" +
        "<td><span class=\"badge " + badgeForStatus(status) + "\">" + escapeHtml(status.toUpperCase()) + "</span></td>" +
        "<td>" + escapeHtml(detail) + "</td>" +
        "</tr>";
    }).join("");
  }

  function getCurrentStepLabel(scenario) {
    for (var i = 0; i < scenario.step_statuses.length; i++) {
      if (scenario.step_statuses[i] !== "completed") {
        return stepTitles[i];
      }
    }
    return stepTitles[stepTitles.length - 1];
  }

  function countStatus(statuses, target) {
    var total = 0;
    for (var i = 0; i < statuses.length; i++) {
      if (statuses[i] === target) {
        total += 1;
      }
    }
    return total;
  }

  function buildSafetyGate(scenario) {
    return {
      execution_allowed: false,
      mutation_allowed: false,
      backend_write_performed: false,
      persistence_used: false,
      deploy_controls_available: false,
      merge_controls_available: false,
      push_controls_available: false,
      pr_controls_available: false,
      risk: scenario.expected_risk,
      blocked_actions: scenario.blocked_actions.slice(),
    };
  }

  function renderSafetyGateText(gate) {
    var lines = [
      "execution_allowed: false",
      "mutation_allowed: false",
      "backend_write_performed: false",
      "persistence_used: false",
      "deploy_controls_available: false",
      "merge_controls_available: false",
      "push_controls_available: false",
      "pr_controls_available: false",
      "risk: " + gate.risk,
      "blocked_actions: " + (gate.blocked_actions.length ? gate.blocked_actions.join(", ") : "none"),
    ];
    return lines.join("\n");
  }

  function buildTranscript(scenario, stepRows, gate) {
    var lines = [
      "Timestamp: " + timestamp(),
      "Selected Scenario: " + scenario.scenario_title,
      "Scenario ID: " + scenario.scenario_id,
      "Workflow Type: " + scenario.workflow_type,
      "Simulated Draft Summary: " + scenario.request_draft,
      "Simulated Packet Summary: " + scenario.packet_summary,
      "Simulated Review Decision: " + scenario.review_decision_summary,
      "Simulated Handoff Summary: " + scenario.handoff_summary,
      "Safety Notes: " + scenario.safety_note,
      "Blocked Actions: " + (gate.blocked_actions.length ? gate.blocked_actions.join(", ") : "none"),
      "Current Step: " + getCurrentStepLabel(scenario),
    ];
    for (var i = 0; i < stepRows.length; i++) {
      lines.push(stepRows[i].step + ": " + stepRows[i].status.toUpperCase() + " - " + stepRows[i].detail);
    }
    return lines.join("\n");
  }

  function buildRunbookMarkdown(scenario, stepRows, gate) {
    var lines = [];
    lines.push("# Original Phase 5E - Client-Side End-to-End Operator Runbook & Scenario Simulator");
    lines.push("");
    lines.push("## Scenario Title");
    lines.push("");
    lines.push(scenario.scenario_title);
    lines.push("");
    lines.push("## Operator Goal");
    lines.push("");
    lines.push(scenario.operator_goal);
    lines.push("");
    lines.push("## Request Draft");
    lines.push("");
    lines.push(scenario.request_draft);
    lines.push("");
    lines.push("## Risk Classification");
    lines.push("");
    lines.push(scenario.expected_risk);
    lines.push("");
    lines.push("## Packet Summary");
    lines.push("");
    lines.push(scenario.packet_summary);
    lines.push("");
    lines.push("## Review Decision");
    lines.push("");
    lines.push(scenario.review_decision_summary);
    lines.push("");
    lines.push("## Decision Ledger Summary");
    lines.push("");
    lines.push(scenario.ledger_summary);
    lines.push("");
    lines.push("## Handoff Recommendation");
    lines.push("");
    lines.push(scenario.handoff_summary);
    lines.push("");
    lines.push("## Acceptance Checklist");
    lines.push("");
    lines.push("- [ ] The scenario is simulated locally.");
    lines.push("- [ ] The runbook is generated locally.");
    lines.push("- [ ] Nothing is saved.");
    lines.push("- [ ] Nothing is sent.");
    lines.push("- [ ] Nothing is queued.");
    lines.push("- [ ] Nothing is executed.");
    lines.push("- [ ] Nothing writes to the backend.");
    lines.push("- [ ] Nothing mutates GitHub or Netlify.");
    lines.push("- [ ] The copy buttons remain copy/paste only.");
    lines.push("");
    lines.push("## Safety Boundary");
    lines.push("");
    lines.push("execution_allowed: false");
    lines.push("mutation_allowed: false");
    lines.push("backend_write_performed: false");
    lines.push("persistence_used: false");
    lines.push("deploy_controls_available: false");
    lines.push("merge_controls_available: false");
    lines.push("push_controls_available: false");
    lines.push("pr_controls_available: false");
    lines.push("risk: " + gate.risk);
    lines.push("");
    lines.push("## No-Go Conditions");
    lines.push("");
    lines.push("- Stop if the flow suggests any execution, mutation, deploy, merge, push, or PR path.");
    lines.push("- Stop if the scenario would require persistence or backend writes.");
    lines.push("- Stop if the scenario leaves copy/paste-only mode.");
    if (scenario.scenario_id === "forbidden_mutation_attempt") {
      lines.push("- Stop if the scenario is not rewritten as planning-only.");
    }
    lines.push("");
    lines.push("## Next Recommended Operator Action");
    lines.push("");
    lines.push(scenario.next_action);
    return lines.join("\n");
  }

  function buildSummaryGrid(scenario, stepRows, gate) {
    return [
      stat("Scenario ID", scenario.scenario_id),
      stat("Expected risk", scenario.expected_risk, scenario.scenario_id === "forbidden_mutation_attempt" ? "fail" : "pass"),
      stat("Review decision", scenario.expected_review_decision),
      stat("Handoff type", scenario.expected_handoff_type),
      stat("Current step", getCurrentStepLabel(scenario)),
      stat("Completed steps", String(countStatus(scenario.step_statuses, "completed"))),
      stat("Warning steps", String(countStatus(scenario.step_statuses, "warning"))),
      stat("Blocked steps", String(countStatus(scenario.step_statuses, "blocked"))),
    ].join("");
  }

  function buildStepSummaryGrid(scenario) {
    return [
      stat("Workflow type", scenario.workflow_type),
      stat("Operator goal", scenario.operator_goal),
      stat("Expected handoff", scenario.expected_handoff_type),
      stat("Safety note", scenario.safety_note),
    ].join("");
  }

  function buildSafetyGrid(gate) {
    return [
      stat("execution_allowed", String(gate.execution_allowed), gate.execution_allowed ? "pass" : "fail"),
      stat("mutation_allowed", String(gate.mutation_allowed), gate.mutation_allowed ? "pass" : "fail"),
      stat("backend_write_performed", String(gate.backend_write_performed), gate.backend_write_performed ? "pass" : "fail"),
      stat("persistence_used", String(gate.persistence_used), gate.persistence_used ? "pass" : "fail"),
      stat("deploy_controls_available", String(gate.deploy_controls_available), gate.deploy_controls_available ? "pass" : "fail"),
      stat("merge_controls_available", String(gate.merge_controls_available), gate.merge_controls_available ? "pass" : "fail"),
      stat("push_controls_available", String(gate.push_controls_available), gate.push_controls_available ? "pass" : "fail"),
      stat("pr_controls_available", String(gate.pr_controls_available), gate.pr_controls_available ? "pass" : "fail"),
    ].join("");
  }

  function renderSnapshot() {
    var scenario = getSelectedScenario();
    var stepRows = stepTitles.map(function (title, index) {
      return {
        step: title,
        status: scenario.step_statuses[index] || "pending",
        detail: scenario.step_details[index] || "",
      };
    });
    var gate = buildSafetyGate(scenario);
    return {
      scenario: scenario,
      step_rows: stepRows,
      gate: gate,
      transcript: buildTranscript(scenario, stepRows, gate),
      runbook_markdown: buildRunbookMarkdown(scenario, stepRows, gate),
      next_action: scenario.next_action,
      scenario_summary_grid: buildSummaryGrid(scenario, stepRows, gate),
      step_summary_grid: buildStepSummaryGrid(scenario),
      safety_grid: buildSafetyGrid(gate),
      safety_gate_text: renderSafetyGateText(gate),
      safety_summary_text: "Scenario state is simulated locally. Runbook output is generated locally and is copy/paste only. Nothing is saved. Nothing is sent. Nothing is queued. Nothing is executed. Nothing writes to the backend. Nothing mutates GitHub or Netlify. Refresh clears state unless copied manually.",
      scenario_rows: renderScenarioRows(),
      step_rows_html: stepRows.map(function (row) {
        return "<tr>" +
          "<td>" + escapeHtml(row.step) + "</td>" +
          "<td><span class=\"badge " + badgeForStatus(row.status) + "\">" + escapeHtml(row.status.toUpperCase()) + "</span></td>" +
          "<td>" + escapeHtml(row.detail) + "</td>" +
          "</tr>";
      }).join(""),
      scenario_options: renderScenarioOptions(scenario.scenario_id),
    };
  }

  function updatePhase5eUI() {
    var snapshot = renderSnapshot();
    var selector = p5e("phase5e-scenario-select");
    var scenarioBody = p5e("phase5e-scenario-body");
    var scenarioSummary = p5e("phase5e-scenario-summary");
    var stepSummary = p5e("phase5e-step-summary");
    var stepBody = p5e("phase5e-step-body");
    var stepSummaryText = p5e("phase5e-step-summary-text");
    var transcript = p5e("phase5e-transcript-preview");
    var safetyGrid = p5e("phase5e-safety-grid");
    var safetyPreview = p5e("phase5e-safety-gate-preview");
    var runbookPreview = p5e("phase5e-runbook-markdown-preview");
    var safetySummaryGrid = p5e("phase5e-summary-grid");
    var safetySummaryText = p5e("phase5e-safety-summary-text");

    if (selector) {
      selector.innerHTML = snapshot.scenario_options;
    }
    if (scenarioBody) {
      scenarioBody.innerHTML = snapshot.scenario_rows;
    }
    if (scenarioSummary) {
      scenarioSummary.innerHTML = snapshot.scenario_summary_grid;
    }
    if (stepSummary) {
      stepSummary.innerHTML = snapshot.step_summary_grid;
    }
    if (stepBody) {
      stepBody.innerHTML = snapshot.step_rows_html;
    }
    if (stepSummaryText) {
      stepSummaryText.textContent = snapshot.scenario.scenario_title + " remains local only, with the current flow at " + getCurrentStepLabel(snapshot.scenario) + ".";
    }
    if (transcript) {
      transcript.textContent = snapshot.transcript;
    }
    if (safetyGrid) {
      safetyGrid.innerHTML = snapshot.safety_grid;
    }
    if (safetyPreview) {
      safetyPreview.textContent = snapshot.safety_gate_text;
    }
    if (runbookPreview) {
      runbookPreview.textContent = snapshot.runbook_markdown;
    }
    if (safetySummaryGrid) {
      safetySummaryGrid.innerHTML = [
        stat("Scenario state", "Simulated locally", "pass"),
        stat("Runbook state", "Generated locally", "pass"),
        stat("Saved anywhere", "No", "fail"),
        stat("Sent anywhere", "No", "fail"),
        stat("Queued", "No", "fail"),
        stat("Executed", "No", "fail"),
        stat("Backend write", "No", "fail"),
        stat("GitHub mutation", "No", "fail"),
        stat("Netlify mutation", "No", "fail"),
        stat("Refresh clears state", "Yes", "warning"),
      ].join("");
    }
    if (safetySummaryText) {
      safetySummaryText.textContent = snapshot.safety_summary_text;
    }
  }

  function initPhase5e() {
    var shell = document.querySelector("[data-phase5e-runbook-simulator]");
    if (!shell) {
      return;
    }

    var selector = p5e("phase5e-scenario-select");
    if (selector) {
      selector.addEventListener("change", function () {
        runbookState.selectedScenarioId = selector.value;
        updatePhase5eUI();
      });
    }

    bindCopyButton("phase5e-copy-transcript", function (snapshot) {
      return snapshot ? snapshot.transcript : "";
    }, "Phase 5E: Select a scenario first.", "Phase 5E: Scenario transcript copied.");

    bindCopyButton("phase5e-copy-safety-gate", function (snapshot) {
      return snapshot ? snapshot.safety_gate_text : "";
    }, "Phase 5E: Select a scenario first.", "Phase 5E: Safety gate copied.");

    bindCopyButton("phase5e-copy-runbook-markdown", function (snapshot) {
      return snapshot ? snapshot.runbook_markdown : "";
    }, "Phase 5E: Select a scenario first.", "Phase 5E: Runbook Markdown copied.");

    bindCopyButton("phase5e-copy-next-action", function (snapshot) {
      return snapshot ? snapshot.next_action : "";
    }, "Phase 5E: Select a scenario first.", "Phase 5E: Next-action recommendation copied.");

    updatePhase5eUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPhase5e);
  } else {
    initPhase5e();
  }
})();

(function () {
  var plus1State = {
    selectedActionId: "planning_handoff",
    selectedRoleId: "viewer",
    approvalState: "not_requested",
  };

  var actionTypes = [
    {
      action_id: "read_only_status",
      action_title: "READ_ONLY_STATUS",
      action_class: "Read-only status",
      allowed_now: true,
      requires_future_auth: false,
      requires_future_storage: false,
      requires_human_gate: false,
      requires_dry_run: false,
      mutation_risk: "NONE",
      execution_risk: "NONE",
      current_status: "READY_NOW",
      target_scope: "Current dashboard status and reports",
      expected_read_operations: "Read dashboard panels, reports, and validator output.",
      expected_write_operations: "none",
      required_validators: "Phase 5E and downstream read-only validators",
      required_reports: "Phase 5E final acceptance report",
      expected_artifacts: "Read-only status brief",
      rollback_no_go: "Stop only if read-only data is missing or stale.",
      human_approval_requirement: "No human gate required for read-only review.",
      future_dependencies: "none",
    },
    {
      action_id: "report_generation",
      action_title: "REPORT_GENERATION",
      action_class: "Report generation",
      allowed_now: true,
      requires_future_auth: false,
      requires_future_storage: false,
      requires_human_gate: false,
      requires_dry_run: false,
      mutation_risk: "NONE",
      execution_risk: "NONE",
      current_status: "READY_NOW",
      target_scope: "Local Markdown and dashboard report artifacts",
      expected_read_operations: "Read current local state and compose reports.",
      expected_write_operations: "none",
      required_validators: "Phase 5 validator chain",
      required_reports: "Original Phase 5 final reports",
      expected_artifacts: "Copyable report drafts",
      rollback_no_go: "Stop if report content would imply live automation.",
      human_approval_requirement: "Human approval not needed for local report drafting.",
      future_dependencies: "none",
    },
    {
      action_id: "validator_review",
      action_title: "VALIDATOR_REVIEW",
      action_class: "Validator review",
      allowed_now: true,
      requires_future_auth: false,
      requires_future_storage: false,
      requires_human_gate: false,
      requires_dry_run: false,
      mutation_risk: "NONE",
      execution_risk: "NONE",
      current_status: "READY_NOW",
      target_scope: "Read-only validator and report audit surface",
      expected_read_operations: "Inspect validators, diff scope, and report verdicts.",
      expected_write_operations: "none",
      required_validators: "Original Phase 5 validator chain",
      required_reports: "Validator and acceptance reports",
      expected_artifacts: "Validator review summary",
      rollback_no_go: "Stop if a validator needs unsafe scope expansion.",
      human_approval_requirement: "No live approval gate required for review-only work.",
      future_dependencies: "none",
    },
    {
      action_id: "dashboard_polish",
      action_title: "DASHBOARD_POLISH",
      action_class: "Dashboard polish",
      allowed_now: true,
      requires_future_auth: false,
      requires_future_storage: false,
      requires_human_gate: false,
      requires_dry_run: false,
      mutation_risk: "LOW",
      execution_risk: "NONE",
      current_status: "READY_NOW",
      target_scope: "Static dashboard presentation and spacing only",
      expected_read_operations: "Review card layout, copy, and compactness.",
      expected_write_operations: "none",
      required_validators: "Phase 4 and Phase 5 dashboard validators",
      required_reports: "UI design and safety reports",
      expected_artifacts: "Dashboard polish notes",
      rollback_no_go: "Stop if polish drifts into live automation behavior.",
      human_approval_requirement: "No live approval gate required for presentation polish.",
      future_dependencies: "none",
    },
    {
      action_id: "planning_handoff",
      action_title: "PLANNING_HANDOFF",
      action_class: "Planning handoff",
      allowed_now: true,
      requires_future_auth: false,
      requires_future_storage: false,
      requires_human_gate: false,
      requires_dry_run: false,
      mutation_risk: "NONE",
      execution_risk: "NONE",
      current_status: "READY_NOW",
      target_scope: "Copy-only planning and handoff preparation",
      expected_read_operations: "Read current phase reports and handoff notes.",
      expected_write_operations: "none",
      required_validators: "Phase 5 handoff validators",
      required_reports: "Phase 5D and Phase 5E reports",
      expected_artifacts: "Automation readiness handoff draft",
      rollback_no_go: "Stop if the handoff starts to imply real execution.",
      human_approval_requirement: "Planning handoff is informational only.",
      future_dependencies: "none",
    },
    {
      action_id: "dry_run_required",
      action_title: "DRY_RUN_REQUIRED",
      action_class: "Dry-run planning",
      allowed_now: true,
      requires_future_auth: true,
      requires_future_storage: true,
      requires_human_gate: true,
      requires_dry_run: true,
      mutation_risk: "LOW_IF_PLANNED",
      execution_risk: "NONE_NOW",
      current_status: "FUTURE_GATED",
      target_scope: "Future action planning and dry-run evidence only",
      expected_read_operations: "Inspect proposed scope and readiness evidence.",
      expected_write_operations: "none",
      required_validators: "Future automation validators and read-only checks",
      required_reports: "Dry-run plan and evidence bundle",
      expected_artifacts: "Copyable dry-run evidence",
      rollback_no_go: "Stop if the plan needs real execution or backend mutation.",
      human_approval_requirement: "Future human approval required before any live action.",
      future_dependencies: "Future auth, storage, audit, and approval systems",
    },
    {
      action_id: "human_approval_required",
      action_title: "HUMAN_APPROVAL_REQUIRED",
      action_class: "Human approval gate",
      allowed_now: true,
      requires_future_auth: true,
      requires_future_storage: true,
      requires_human_gate: true,
      requires_dry_run: true,
      mutation_risk: "NONE_NOW",
      execution_risk: "NONE_NOW",
      current_status: "DISPLAY_ONLY",
      target_scope: "Approval-state simulation and readiness documentation",
      expected_read_operations: "Read the gate state and explain its meaning.",
      expected_write_operations: "none",
      required_validators: "Future approval and audit validators",
      required_reports: "Approval gate readiness report",
      expected_artifacts: "Human gate simulator copy",
      rollback_no_go: "Stop if approval is treated as live execution.",
      human_approval_requirement: "Human approval is a future requirement, not a live action.",
      future_dependencies: "Future auth, storage, and approval persistence",
    },
    {
      action_id: "forbidden_mutation",
      action_title: "FORBIDDEN_MUTATION",
      action_class: "Forbidden mutation",
      allowed_now: false,
      requires_future_auth: true,
      requires_future_storage: true,
      requires_human_gate: true,
      requires_dry_run: true,
      mutation_risk: "RED",
      execution_risk: "RED",
      current_status: "BLOCKED",
      target_scope: "Any write, deploy, merge, push, or PR path",
      expected_read_operations: "Read-only explanation of why the path is blocked.",
      expected_write_operations: "none",
      required_validators: "Future safety validators only if rewritten as planning",
      required_reports: "Safety rejection note",
      expected_artifacts: "No-go summary",
      rollback_no_go: "Do not proceed unless rewritten as planning-only.",
      human_approval_requirement: "Human approval cannot override the no-go boundary.",
      future_dependencies: "A full future control plane that is not present now",
    },
    {
      action_id: "forbidden_execution",
      action_title: "FORBIDDEN_EXECUTION",
      action_class: "Forbidden execution",
      allowed_now: false,
      requires_future_auth: true,
      requires_future_storage: true,
      requires_human_gate: true,
      requires_dry_run: true,
      mutation_risk: "RED",
      execution_risk: "RED",
      current_status: "BLOCKED",
      target_scope: "Command execution or backend action path",
      expected_read_operations: "Read-only explanation of blocked execution.",
      expected_write_operations: "none",
      required_validators: "Future safety validators only if rewritten as planning",
      required_reports: "Execution no-go note",
      expected_artifacts: "Blocked execution summary",
      rollback_no_go: "Do not proceed unless a future execution engine is explicitly built.",
      human_approval_requirement: "No approval state can make this build execute commands.",
      future_dependencies: "Command engine, auth, audit, storage, and approval systems",
    },
  ];

  var roles = [
    { role_id: "viewer", role_title: "viewer", can_view_status: true, can_draft_request: false, can_review_packet: false, can_approve_future_action: false, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
    { role_id: "operator", role_title: "operator", can_view_status: true, can_draft_request: true, can_review_packet: true, can_approve_future_action: false, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
    { role_id: "reviewer", role_title: "reviewer", can_view_status: true, can_draft_request: true, can_review_packet: true, can_approve_future_action: false, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
    { role_id: "approver", role_title: "approver", can_view_status: true, can_draft_request: true, can_review_packet: true, can_approve_future_action: true, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
    { role_id: "automation_admin", role_title: "automation_admin", can_view_status: true, can_draft_request: true, can_review_packet: true, can_approve_future_action: true, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
    { role_id: "break_glass_admin", role_title: "break_glass_admin", can_view_status: true, can_draft_request: true, can_review_packet: true, can_approve_future_action: true, can_execute_now: false, can_mutate_now: false, requires_future_auth: true },
  ];

  var approvalStates = [
    { state_id: "not_requested", state_title: "not_requested", meaning: "No approval has been requested yet.", live_action: false },
    { state_id: "pending_review", state_title: "pending_review", meaning: "A future request is waiting on human review.", live_action: false },
    { state_id: "approved_for_planning", state_title: "approved_for_planning", meaning: "Planning is allowed, but nothing executes.", live_action: false },
    { state_id: "approved_for_dry_run_only", state_title: "approved_for_dry_run_only", meaning: "Only dry-run evidence may be prepared.", live_action: false },
    { state_id: "rejected", state_title: "rejected", meaning: "The request is rejected and must be rewritten.", live_action: false },
    { state_id: "blocked_by_safety", state_title: "blocked_by_safety", meaning: "Safety policy blocks the request entirely.", live_action: false },
    { state_id: "expired", state_title: "expired", meaning: "The approval window elapsed before any action.", live_action: false },
  ];

  var preflightChecklist = [
    { item: "auth exists", status: "not_ready", note: "Future real automation will need explicit auth." },
    { item: "user role verified", status: "not_ready", note: "Role checks are currently only simulated." },
    { item: "permission checked", status: "not_ready", note: "Permission gating is still future work." },
    { item: "request stored", status: "not_ready", note: "No persistent queue or storage exists." },
    { item: "audit log active", status: "not_ready", note: "Audit persistence is not implemented." },
    { item: "dry-run completed", status: "not_ready", note: "Dry-run evidence is copy-only and local." },
    { item: "diff reviewed", status: "ready_read_only", note: "Read-only diff review is already safe now." },
    { item: "rollback plan exists", status: "not_ready", note: "Rollback planning must be added before real execution." },
    { item: "human approval recorded", status: "not_ready", note: "Approval is display-only in this build." },
    { item: "execution window approved", status: "not_ready", note: "No execution window exists yet." },
    { item: "rate-limit controls present", status: "not_ready", note: "Rate-limit controls are future backend work." },
    { item: "secrets unavailable to browser", status: "verified", note: "The browser build does not read secrets." },
    { item: "backend mutation endpoint explicitly authorized", status: "not_ready", note: "No mutation endpoint is implemented." },
  ];

  function p1(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function timestamp() {
    return new Date().toISOString();
  }

  function stat(label, value, badgeClass) {
    var strongClass = badgeClass ? ' class="badge ' + badgeClass + '"' : "";
    return "<div class=\"stat\"><span>" + escapeHtml(label) + "</span><strong" + strongClass + ">" + escapeHtml(value) + "</strong></div>";
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p1("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p1(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function getAction(id) {
    for (var i = 0; i < actionTypes.length; i++) {
      if (actionTypes[i].action_id === id) {
        return actionTypes[i];
      }
    }
    return actionTypes[0];
  }

  function getRole(id) {
    for (var i = 0; i < roles.length; i++) {
      if (roles[i].role_id === id) {
        return roles[i];
      }
    }
    return roles[0];
  }

  function getApprovalState(id) {
    for (var i = 0; i < approvalStates.length; i++) {
      if (approvalStates[i].state_id === id) {
        return approvalStates[i];
      }
    }
    return approvalStates[0];
  }

  function badgeForTruth(value) {
    return value ? "pass" : "fail";
  }

  function badgeForStatus(status) {
    switch (status) {
      case "verified":
      case "ready_now":
        return "pass";
      case "not_ready":
        return "warning";
      case "ready_read_only":
        return "info";
      case "blocked":
      case "red":
        return "fail";
      default:
        return "info";
    }
  }

  function renderActionRows(selectedId) {
    return actionTypes.map(function (action) {
      var selected = action.action_id === selectedId ? " class=\"selected\"" : "";
      return "<tr" + selected + ">" +
        "<td><code>" + escapeHtml(action.action_title) + "</code></td>" +
        "<td><span class=\"badge " + badgeForTruth(action.allowed_now) + "\">" + (action.allowed_now ? "YES" : "NO") + "</span></td>" +
        "<td>" + escapeHtml(String(action.requires_future_auth)) + "</td>" +
        "<td>" + escapeHtml(String(action.requires_future_storage)) + "</td>" +
        "<td>" + escapeHtml(String(action.requires_human_gate)) + "</td>" +
        "<td>" + escapeHtml(String(action.requires_dry_run)) + "</td>" +
        "<td>" + escapeHtml(action.mutation_risk) + "</td>" +
        "<td>" + escapeHtml(action.execution_risk) + "</td>" +
        "<td><span class=\"badge " + badgeForStatus(action.current_status.toLowerCase()) + "\">" + escapeHtml(action.current_status) + "</span></td>" +
        "</tr>";
    }).join("");
  }

  function renderRoleRows() {
    return roles.map(function (role) {
      return "<tr>" +
        "<td><code>" + escapeHtml(role.role_title) + "</code></td>" +
        "<td><span class=\"badge " + badgeForTruth(role.can_view_status) + "\">" + (role.can_view_status ? "YES" : "NO") + "</span></td>" +
        "<td><span class=\"badge " + badgeForTruth(role.can_draft_request) + "\">" + (role.can_draft_request ? "YES" : "NO") + "</span></td>" +
        "<td><span class=\"badge " + badgeForTruth(role.can_review_packet) + "\">" + (role.can_review_packet ? "YES" : "NO") + "</span></td>" +
        "<td><span class=\"badge " + badgeForTruth(role.can_approve_future_action) + "\">" + (role.can_approve_future_action ? "YES" : "NO") + "</span></td>" +
        "<td><span class=\"badge fail\">NO</span></td>" +
        "<td><span class=\"badge fail\">NO</span></td>" +
        "<td>" + escapeHtml(String(role.requires_future_auth)) + "</td>" +
        "</tr>";
    }).join("");
  }

  function renderApprovalRows(selectedId) {
    return approvalStates.map(function (state) {
      var selected = state.state_id === selectedId ? " class=\"selected\"" : "";
      return "<tr" + selected + ">" +
        "<td><code>" + escapeHtml(state.state_title) + "</code></td>" +
        "<td>" + escapeHtml(state.meaning) + "</td>" +
        "<td><span class=\"badge fail\">" + (state.live_action ? "YES" : "NO") + "</span></td>" +
        "</tr>";
    }).join("");
  }

  function renderPreflightRows() {
    return preflightChecklist.map(function (item) {
      return "<tr>" +
        "<td>" + escapeHtml(item.item) + "</td>" +
        "<td><span class=\"badge " + badgeForStatus(item.status) + "\">" + escapeHtml(item.status.toUpperCase()) + "</span></td>" +
        "<td>" + escapeHtml(item.note) + "</td>" +
        "</tr>";
    }).join("");
  }

  function buildReadinessSummary(action, role, approval) {
    return [
      stat("Original +1 status", "READINESS_ONLY", "warning"),
      stat("Selected action", action.action_title, action.allowed_now ? "pass" : "fail"),
      stat("Role preview", role.role_title, "info"),
      stat("Approval gate", approval.state_title, approval.live_action ? "pass" : "warning"),
      stat("Live automation enabled", "false", "fail"),
      stat("Execution enabled", "false", "fail"),
      stat("Mutation enabled", "false", "fail"),
      stat("Backend writes enabled", "false", "fail"),
      stat("Auth implemented", "false", "fail"),
      stat("Audit persistence", "false", "fail"),
    ].join("");
  }

  function buildDryRunSummary(action, role, approval) {
    return [
      stat("Action class", action.action_class),
      stat("Allowed now", String(action.allowed_now), action.allowed_now ? "pass" : "fail"),
      stat("Requires dry-run", String(action.requires_dry_run), action.requires_dry_run ? "warning" : "pass"),
      stat("Requires human gate", String(action.requires_human_gate), action.requires_human_gate ? "warning" : "pass"),
      stat("Role", role.role_title),
      stat("Approval state", approval.state_title),
    ].join("");
  }

  function buildBoundaryGrid() {
    return [
      stat("current build can execute commands", "false", "fail"),
      stat("current build can mutate GitHub", "false", "fail"),
      stat("current build can mutate Netlify", "false", "fail"),
      stat("current build can deploy", "false", "fail"),
      stat("current build can merge", "false", "fail"),
      stat("current build can push", "false", "fail"),
      stat("current build can create PRs", "false", "fail"),
      stat("current build can write backend data", "false", "fail"),
      stat("current build can store queues", "false", "fail"),
      stat("current build can persist approvals", "false", "fail"),
    ].join("");
  }

  function buildSafetySummaryGrid(action, role, approval) {
    return [
      stat("Scenario state", "Readiness only", "warning"),
      stat("Saved anywhere", "No", "fail"),
      stat("Sent anywhere", "No", "fail"),
      stat("Queued", "No", "fail"),
      stat("Executed", "No", "fail"),
      stat("Backend write", "No", "fail"),
      stat("GitHub mutation", "No", "fail"),
      stat("Netlify mutation", "No", "fail"),
      stat("Future auth required", String(action.requires_future_auth || role.requires_future_auth), "warning"),
      stat("Future storage required", String(action.requires_future_storage), "warning"),
    ].join("");
  }

  function buildDryRunMarkdown(action, role, approval) {
    var lines = [];
    lines.push("# Original +1 - Controlled Automation Readiness Layer");
    lines.push("");
    lines.push("## Selected Action");
    lines.push("");
    lines.push(action.action_title);
    lines.push("");
    lines.push("## Action Class");
    lines.push("");
    lines.push(action.action_class);
    lines.push("");
    lines.push("## Role Preview");
    lines.push("");
    lines.push(role.role_title);
    lines.push("");
    lines.push("## Human Approval Gate");
    lines.push("");
    lines.push(approval.state_title);
    lines.push(" - " + approval.meaning);
    lines.push("");
    lines.push("## Dry-Run Plan");
    lines.push("");
    lines.push("- Target scope: " + action.target_scope);
    lines.push("- Expected read operations: " + action.expected_read_operations);
    lines.push("- Expected write operations: none");
    lines.push("- Required validators: " + action.required_validators);
    lines.push("- Required reports: " + action.required_reports);
    lines.push("- Expected artifacts: " + action.expected_artifacts);
    lines.push("- Rollback / no-go: " + action.rollback_no_go);
    lines.push("- Human approval requirement: " + action.human_approval_requirement);
    lines.push("- Future dependencies: " + action.future_dependencies);
    lines.push("");
    lines.push("## Preflight Checklist");
    lines.push("");
    for (var i = 0; i < preflightChecklist.length; i++) {
      lines.push("- [" + (preflightChecklist[i].status === "verified" ? "x" : " ") + "] " + preflightChecklist[i].item + " - " + preflightChecklist[i].note);
    }
    lines.push("");
    lines.push("## Execution Boundary");
    lines.push("");
    lines.push("- current build cannot execute commands");
    lines.push("- current build cannot mutate GitHub");
    lines.push("- current build cannot mutate Netlify");
    lines.push("- current build cannot deploy");
    lines.push("- current build cannot merge");
    lines.push("- current build cannot push");
    lines.push("- current build cannot create PRs");
    lines.push("- current build cannot write backend data");
    lines.push("- current build cannot store queues");
    lines.push("- current build cannot persist approvals");
    return lines.join("\n");
  }

  function buildHandoffContractMarkdown(action, role, approval) {
    var lines = [];
    lines.push("# Original +1 Automation Handoff Contract");
    lines.push("");
    lines.push("## Proposed Future Automation Action");
    lines.push("");
    lines.push(action.action_title);
    lines.push("");
    lines.push("## Classification");
    lines.push("");
    lines.push(action.action_class);
    lines.push("");
    lines.push("## Required Auth");
    lines.push("");
    lines.push(action.requires_future_auth ? "Future auth required." : "No future auth requirement for this action preview.");
    lines.push("");
    lines.push("## Required Storage");
    lines.push("");
    lines.push(action.requires_future_storage ? "Future storage required." : "No future storage requirement for this action preview.");
    lines.push("");
    lines.push("## Required Audit Persistence");
    lines.push("");
    lines.push(action.requires_future_storage ? "Audit persistence required before live execution." : "Audit persistence not required for the current preview.");
    lines.push("");
    lines.push("## Required Dry-Run Evidence");
    lines.push("");
    lines.push(action.expected_read_operations);
    lines.push("");
    lines.push("## Required Approval Gate");
    lines.push("");
    lines.push(approval.state_title + " - " + approval.meaning);
    lines.push("");
    lines.push("## Rollback Plan");
    lines.push("");
    lines.push(action.rollback_no_go);
    lines.push("");
    lines.push("## Forbidden Conditions");
    lines.push("");
    lines.push("- No command execution.");
    lines.push("- No backend writes.");
    lines.push("- No GitHub mutation.");
    lines.push("- No Netlify mutation.");
    lines.push("- No deploy, merge, push, or PR controls.");
    lines.push("");
    lines.push("## Validator Requirements");
    lines.push("");
    lines.push(action.required_validators);
    lines.push("");
    lines.push("## Human Review Checklist");
    lines.push("");
    lines.push("- Confirm the action remains readiness-only.");
    lines.push("- Confirm dry-run evidence is local and copy-only.");
    lines.push("- Confirm required future auth and storage are not yet implemented.");
    lines.push("- Confirm no execution or mutation controls are present.");
    lines.push("");
    lines.push("## Final No-Go Conditions");
    lines.push("");
    lines.push("- Stop if the action requires real execution.");
    lines.push("- Stop if the action requires backend writes.");
    lines.push("- Stop if the action requires live approvals not yet implemented.");
    lines.push("- Stop if the action requires command, deploy, merge, push, or PR controls.");
    return lines.join("\n");
  }

  function buildReadinessSummaryMarkdown(action, role, approval) {
    var lines = [];
    lines.push("# Original +1 Readiness Summary");
    lines.push("");
    lines.push("Original +1 status: READINESS_ONLY");
    lines.push("Selected action: " + action.action_title);
    lines.push("Selected role: " + role.role_title);
    lines.push("Approval gate: " + approval.state_title);
    lines.push("");
    lines.push("This layer is copy-only, local-only, and inert.");
    lines.push("No live automation is enabled.");
    lines.push("No execution, mutation, backend write, deploy, merge, push, or PR control is enabled.");
    return lines.join("\n");
  }

  function buildPreflightMarkdown() {
    var lines = [];
    lines.push("# Original +1 Preflight Checklist");
    lines.push("");
    for (var i = 0; i < preflightChecklist.length; i++) {
      lines.push("- [" + (preflightChecklist[i].status === "verified" ? "x" : " ") + "] " + preflightChecklist[i].item + " - " + preflightChecklist[i].note);
    }
    return lines.join("\n");
  }

  function buildSafetySummaryMarkdown(action, role, approval) {
    var lines = [];
    lines.push("# Original +1 Safety Summary");
    lines.push("");
    lines.push("- Scenario state: readiness-only");
    lines.push("- Live automation: false");
    lines.push("- Execution: false");
    lines.push("- Mutation: false");
    lines.push("- Backend writes: false");
    lines.push("- GitHub mutation: false");
    lines.push("- Netlify mutation: false");
    lines.push("- Future auth required: " + String(action.requires_future_auth || role.requires_future_auth));
    lines.push("- Future storage required: " + String(action.requires_future_storage));
    lines.push("- Approval gate: " + approval.state_title);
    return lines.join("\n");
  }

  function renderSnapshot() {
    var action = getAction(plus1State.selectedActionId);
    var role = getRole(plus1State.selectedRoleId);
    var approval = getApprovalState(plus1State.approvalState);
    return {
      action: action,
      role: role,
      approval: approval,
      action_rows_html: renderActionRows(action.action_id),
      role_rows_html: renderRoleRows(),
      approval_rows_html: renderApprovalRows(approval.state_id),
      preflight_rows_html: renderPreflightRows(),
      readiness_summary_grid: buildReadinessSummary(action, role, approval),
      dry_run_summary_grid: buildDryRunSummary(action, role, approval),
      boundary_grid: buildBoundaryGrid(),
      safety_summary_grid: buildSafetySummaryGrid(action, role, approval),
      readiness_summary_markdown: buildReadinessSummaryMarkdown(action, role, approval),
      dry_run_markdown: buildDryRunMarkdown(action, role, approval),
      preflight_markdown: buildPreflightMarkdown(),
      handoff_contract_markdown: buildHandoffContractMarkdown(action, role, approval),
      safety_summary_markdown: buildSafetySummaryMarkdown(action, role, approval),
      overview_note: "Original +1 remains readiness-only. Nothing executes, nothing mutates, and no future automation wiring is active yet.",
      approval_note: approval.meaning + " Approval does not execute, deploy, merge, push, or create PRs.",
    };
  }

  function updatePlus1UI() {
    var snapshot = renderSnapshot();
    var actionSelect = p1("plus1-action-select");
    var roleSelect = p1("plus1-role-select");
    var approvalSelect = p1("plus1-approval-select");
    var actionBody = p1("plus1-action-body");
    var roleBody = p1("plus1-role-body");
    var approvalBody = p1("plus1-approval-body");
    var preflightBody = p1("plus1-preflight-body");
    var overviewSummary = p1("plus1-overview-summary");
    var overviewNote = p1("plus1-overview-note");
    var dryRunSummary = p1("plus1-dry-run-summary");
    var dryRunPreview = p1("plus1-dry-run-plan-preview");
    var boundaryGrid = p1("plus1-boundary-grid");
    var contractPreview = p1("plus1-contract-preview");
    var safetySummaryGrid = p1("plus1-safety-summary-grid");
    var safetySummaryText = p1("plus1-safety-summary-text");
    var approvalNote = p1("plus1-approval-note");

    if (actionSelect) {
      actionSelect.innerHTML = actionTypes.map(function (action) {
        var selected = action.action_id === snapshot.action.action_id ? " selected" : "";
        return '<option value="' + escapeHtml(action.action_id) + '"' + selected + '>' + escapeHtml(action.action_title) + "</option>";
      }).join("");
    }
    if (roleSelect) {
      roleSelect.innerHTML = roles.map(function (role) {
        var selected = role.role_id === snapshot.role.role_id ? " selected" : "";
        return '<option value="' + escapeHtml(role.role_id) + '"' + selected + '>' + escapeHtml(role.role_title) + "</option>";
      }).join("");
    }
    if (approvalSelect) {
      approvalSelect.innerHTML = approvalStates.map(function (approval) {
        var selected = approval.state_id === snapshot.approval.state_id ? " selected" : "";
        return '<option value="' + escapeHtml(approval.state_id) + '"' + selected + '>' + escapeHtml(approval.state_title) + "</option>";
      }).join("");
    }
    if (actionBody) {
      actionBody.innerHTML = snapshot.action_rows_html;
    }
    if (roleBody) {
      roleBody.innerHTML = snapshot.role_rows_html;
    }
    if (approvalBody) {
      approvalBody.innerHTML = snapshot.approval_rows_html;
    }
    if (preflightBody) {
      preflightBody.innerHTML = snapshot.preflight_rows_html;
    }
    if (overviewSummary) {
      overviewSummary.innerHTML = snapshot.readiness_summary_grid;
    }
    if (overviewNote) {
      overviewNote.textContent = snapshot.overview_note;
    }
    if (dryRunSummary) {
      dryRunSummary.innerHTML = snapshot.dry_run_summary_grid;
    }
    if (dryRunPreview) {
      dryRunPreview.textContent = snapshot.dry_run_markdown;
    }
    if (boundaryGrid) {
      boundaryGrid.innerHTML = snapshot.boundary_grid;
    }
    if (contractPreview) {
      contractPreview.textContent = snapshot.handoff_contract_markdown;
    }
    if (safetySummaryGrid) {
      safetySummaryGrid.innerHTML = snapshot.safety_summary_grid;
    }
    if (safetySummaryText) {
      safetySummaryText.textContent = "Original +1 is readiness-only. Nothing is automated, nothing is executed, nothing is saved, nothing is sent, nothing writes to the backend, and nothing mutates GitHub or Netlify.";
    }
    if (approvalNote) {
      approvalNote.textContent = snapshot.approval_note;
    }
  }

  function initPlus1() {
    var shell = document.querySelector("[data-plus1-controlled-automation-readiness-layer]");
    if (!shell) {
      return;
    }

    var actionSelect = p1("plus1-action-select");
    var roleSelect = p1("plus1-role-select");
    var approvalSelect = p1("plus1-approval-select");

    if (actionSelect) {
      actionSelect.addEventListener("change", function () {
        plus1State.selectedActionId = actionSelect.value;
        updatePlus1UI();
      });
    }
    if (roleSelect) {
      roleSelect.addEventListener("change", function () {
        plus1State.selectedRoleId = roleSelect.value;
        updatePlus1UI();
      });
    }
    if (approvalSelect) {
      approvalSelect.addEventListener("change", function () {
        plus1State.approvalState = approvalSelect.value;
        updatePlus1UI();
      });
    }

    bindCopyButton("plus1-copy-readiness-summary", function (snapshot) {
      return snapshot ? snapshot.readiness_summary_markdown : "";
    }, "Original +1: Select an action first.", "Original +1: Readiness summary copied.");

    bindCopyButton("plus1-copy-dry-run-plan", function (snapshot) {
      return snapshot ? snapshot.dry_run_markdown : "";
    }, "Original +1: Select an action first.", "Original +1: Dry-run plan copied.");

    bindCopyButton("plus1-copy-preflight-checklist", function (snapshot) {
      return snapshot ? snapshot.preflight_markdown : "";
    }, "Original +1: Select an action first.", "Original +1: Preflight checklist copied.");

    bindCopyButton("plus1-copy-handoff-contract", function (snapshot) {
      return snapshot ? snapshot.handoff_contract_markdown : "";
    }, "Original +1: Select an action first.", "Original +1: Automation handoff contract copied.");

    bindCopyButton("plus1-copy-safety-summary", function (snapshot) {
      return snapshot ? snapshot.safety_summary_markdown : "";
    }, "Original +1: Select an action first.", "Original +1: Safety summary copied.");

    updatePlus1UI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus1);
  } else {
    initPlus1();
  }
})();

(function () {
  var plus1bState = {
    pack: null,
    selectedContractId: "automation_readiness_contract_schema",
    selectedModeId: "automation_readiness_mode",
  };

  var flowRail = [
    { stage: "Phase 5A", status: "complete", purpose: "Client-side operator workflow shell", output_type: "Workflow shell", safety_boundary: "Local-only shell", next_handoff: "Phase 5B" },
    { stage: "Phase 5B", status: "complete", purpose: "Request packet builder", output_type: "Request packet", safety_boundary: "Copy/paste only", next_handoff: "Phase 5C" },
    { stage: "Phase 5C", status: "complete", purpose: "Review board and decision ledger", output_type: "Decision ledger", safety_boundary: "Read-only review", next_handoff: "Phase 5D" },
    { stage: "Phase 5D", status: "complete", purpose: "Handoff composer", output_type: "Handoff document", safety_boundary: "Temporary in-browser state", next_handoff: "Phase 5E" },
    { stage: "Phase 5E", status: "complete", purpose: "Runbook simulator", output_type: "Scenario transcript", safety_boundary: "Scenario preview only", next_handoff: "Original +1" },
    { stage: "Original +1", status: "readiness_only", purpose: "Controlled automation readiness", output_type: "Readiness contract", safety_boundary: "Readiness-only", next_handoff: "Original +1B" },
    { stage: "Original +1B", status: "readiness_only", purpose: "Operator console consolidation and contract layer", output_type: "Contract pack", safety_boundary: "Contracts only", next_handoff: "Future automation phase" },
  ];

  var modes = [
    { mode_id: "planning_mode", mode_title: "Planning Mode", emphasizes: "Scope, sequencing, and local review.", not_enabled: "Does not enable execution or mutation.", useful_copy_outputs: "Copy implementation prompt, copy full runbook." },
    { mode_id: "review_mode", mode_title: "Review Mode", emphasizes: "Validator results and safety notes.", not_enabled: "Does not enable deploy, merge, or push.", useful_copy_outputs: "Copy validator checklist, copy no-go report." },
    { mode_id: "dry_run_mode", mode_title: "Dry-Run Planning Mode", emphasizes: "Evidence, dry-run plans, and preflight checks.", not_enabled: "Does not enable live action or backend writes.", useful_copy_outputs: "Copy dry-run plan, copy preflight checklist." },
    { mode_id: "handoff_mode", mode_title: "Handoff Mode", emphasizes: "Copyable runbook and contract handoff text.", not_enabled: "Does not create PRs or queue actions.", useful_copy_outputs: "Copy automation readiness contract, copy merge-readiness summary." },
    { mode_id: "readiness_mode", mode_title: "Automation Readiness Mode", emphasizes: "Future dependencies and safety gating.", not_enabled: "Does not implement auth or storage.", useful_copy_outputs: "Copy automation readiness contract, copy validator checklist." },
    { mode_id: "no_go_mode", mode_title: "No-Go Mode", emphasizes: "Blocked operations and rollback boundaries.", not_enabled: "Does not allow execution, mutation, or deployment.", useful_copy_outputs: "Copy no-go report, copy merge-readiness summary." },
  ];

  var validatorWall = [
    { group: "Phase 5A validators", pass_string: "ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_SHELL_VALIDATION_PASS", safety_category: "read-only", required_before_merge: true, required_before_production: true },
    { group: "Phase 5B validators", pass_string: "ORIGINAL_PHASE_5B_REQUEST_PACKET_BUILDER_VALIDATION_PASS", safety_category: "read-only", required_before_merge: true, required_before_production: true },
    { group: "Phase 5C validators", pass_string: "ORIGINAL_PHASE_5C_REVIEW_BOARD_VALIDATION_PASS", safety_category: "read-only", required_before_merge: true, required_before_production: true },
    { group: "Phase 5D validators", pass_string: "ORIGINAL_PHASE_5D_HANDOFF_COMPOSER_VALIDATION_PASS", safety_category: "read-only", required_before_merge: true, required_before_production: true },
    { group: "Phase 5E validators", pass_string: "ORIGINAL_PHASE_5E_RUNBOOK_SIMULATOR_VALIDATION_PASS", safety_category: "read-only", required_before_merge: true, required_before_production: true },
    { group: "Original +1 validators", pass_string: "ORIGINAL_PLUS1_CONTROLLED_AUTOMATION_READINESS_VALIDATION_PASS", safety_category: "readiness-only", required_before_merge: true, required_before_production: true },
    { group: "Original +1B validators", pass_string: "ORIGINAL_PLUS1B_OPERATOR_CONSOLE_CONTRACT_LAYER_VALIDATION_PASS", safety_category: "readiness-only", required_before_merge: true, required_before_production: true },
    { group: "Phase 4 / 4D / 4C / 4A validators", pass_string: "BACKEND_PHASE_4A_FOUNDATION_VALIDATION_PASS", safety_category: "foundation", required_before_merge: true, required_before_production: true },
    { group: "Phase 3 validators", pass_string: "INTERFACE_PHASE_3_DASHBOARD_VALIDATION_PASS", safety_category: "static-dashboard", required_before_merge: true, required_before_production: true },
  ];

  function p1b(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p1b("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function stat(label, value, badgeClass) {
    var strongClass = badgeClass ? ' class="badge ' + badgeClass + '"' : "";
    return "<div class=\"stat\"><span>" + escapeHtml(label) + "</span><strong" + strongClass + ">" + escapeHtml(value) + "</strong></div>";
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p1b(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function getContract(id) {
    var pack = plus1bState.pack;
    if (!pack || !pack.schemas) {
      return null;
    }
    for (var i = 0; i < pack.schemas.length; i++) {
      if (pack.schemas[i].schema_id === id) {
        return pack.schemas[i];
      }
    }
    return pack.schemas[0] || null;
  }

  function getMode(id) {
    for (var i = 0; i < modes.length; i++) {
      if (modes[i].mode_id === id) {
        return modes[i];
      }
    }
    return modes[0];
  }

  function boolBadge(value) {
    return value ? "pass" : "disabled";
  }

  function buildFlowRows() {
    return flowRail.map(function (item) {
      return "<tr>" +
        "<th scope=\"row\"><code>" + escapeHtml(item.stage) + "</code></th>" +
        "<td>" + escapeHtml(item.status) + "</td>" +
        "<td>" + escapeHtml(item.purpose) + "</td>" +
        "<td>" + escapeHtml(item.output_type) + "</td>" +
        "<td>" + escapeHtml(item.safety_boundary) + "</td>" +
        "<td>" + escapeHtml(item.next_handoff) + "</td>" +
        "</tr>";
    }).join("");
  }

  function buildCockpitGrid(pack) {
    var schemas = pack && pack.schemas ? pack.schemas : [];
    return [
      stat("Current system stage", "ORIGINAL +1B", "warning"),
      stat("Production phase status", "PRODUCTION_VISIBLE", "pass"),
      stat("Readiness layer status", "READINESS_ONLY", "pass"),
      stat("Automation enabled", "false", "disabled"),
      stat("Execution enabled", "false", "disabled"),
      stat("Mutation enabled", "false", "disabled"),
      stat("Backend writes enabled", "false", "disabled"),
      stat("Persistence enabled", "false", "disabled"),
      stat("Real queue enabled", "false", "disabled"),
      stat("Live auth enabled", "false", "disabled"),
      stat("Safe outputs available", "copy/paste only", "info"),
      stat("Missing dependencies", "auth, storage, queue, audit, approval, backend write", "warning"),
      stat("Contract schemas", String(schemas.length || 0), "info"),
    ].join("");
  }

  function buildSafetyGrid() {
    return [
      stat("Local outputs", "true", "pass"),
      stat("Copy/paste only", "true", "pass"),
      stat("Save/submit/queue", "false", "disabled"),
      stat("Execute/deploy/merge/push", "false", "disabled"),
      stat("Backend writes", "false", "disabled"),
      stat("GitHub/Netlify mutation", "false", "disabled"),
      stat("Future automation", "separate phase", "warning"),
    ].join("");
  }

  function buildSchemaRows(pack) {
    if (!pack || !pack.schemas || !pack.schemas.length) {
      return '<tr><td colspan="7" class="empty">No contract schema pack loaded yet.</td></tr>';
    }
    return pack.schemas.map(function (schema) {
      return "<tr data-search-text=\"" + escapeHtml([
        schema.schema_id, schema.schema_version, schema.purpose,
        (schema.required_fields || []).join(" "),
        (schema.forbidden_fields || []).join(" "),
        schema.safety_notes,
        schema.future_backend_dependency,
      ].join(" ")) + "\">" +
        "<th scope=\"row\">" + escapeHtml(schema.schema_id) + "</th>" +
        "<td>" + escapeHtml(schema.schema_version) + "</td>" +
        "<td>" + escapeHtml(schema.purpose) + "</td>" +
        "<td>" + escapeHtml((schema.required_fields || []).join(", ")) + "</td>" +
        "<td>" + escapeHtml((schema.forbidden_fields || []).join(", ")) + "</td>" +
        "<td>" + escapeHtml(schema.safety_notes) + "</td>" +
        "<td>" + escapeHtml(schema.future_backend_dependency) + "</td>" +
      "</tr>";
    }).join("");
  }

  function buildValidatorRows() {
    return validatorWall.map(function (row) {
      return "<tr>" +
        "<th scope=\"row\">" + escapeHtml(row.group) + "</th>" +
        "<td><code>" + escapeHtml(row.pass_string) + "</code></td>" +
        "<td>" + escapeHtml(row.safety_category) + "</td>" +
        "<td>" + (row.required_before_merge ? "Yes" : "No") + "</td>" +
        "<td>" + (row.required_before_production ? "Yes" : "No") + "</td>" +
      "</tr>";
    }).join("");
  }

  function buildModeRows() {
    return modes.map(function (mode) {
      return "<tr>" +
        "<th scope=\"row\">" + escapeHtml(mode.mode_title) + "</th>" +
        "<td>" + escapeHtml(mode.emphasizes) + "</td>" +
        "<td>" + escapeHtml(mode.not_enabled) + "</td>" +
        "<td>" + escapeHtml(mode.useful_copy_outputs) + "</td>" +
      "</tr>";
    }).join("");
  }

  function buildReadinessContractMarkdown(contract, mode) {
    if (!contract) {
      return "No contract selected yet.";
    }
    return [
      "# Original +1B Automation Readiness Contract",
      "",
      "## Contract Title",
      contract.contract_title,
      "",
      "## Source Phase",
      contract.source_phase,
      "",
      "## Intended Future Automation Type",
      contract.intended_future_automation_type,
      "",
      "## Action Classification",
      contract.action_classification,
      "",
      "## Required Role",
      contract.required_role,
      "",
      "## Required Approval Gate",
      contract.required_approval_gate,
      "",
      "## Required Dry-Run Evidence",
      contract.required_dry_run_evidence,
      "",
      "## Required Audit Event Model",
      contract.required_audit_event_model,
      "",
      "## Required Rollback / No-Go Policy",
      contract.required_rollback_policy,
      "",
      "## Required Validators",
      contract.required_validators,
      "",
      "## Required Production Verification",
      contract.required_production_verification,
      "",
      "## Forbidden Operations",
      (contract.forbidden_operations || []).map(function (item) { return "- " + item; }).join("\n"),
      "",
      "## Future Dependencies",
      contract.future_dependencies,
      "",
      "## Mode Emphasis",
      mode.mode_title + " — " + mode.emphasizes,
    ].join("\n");
  }

  function buildImplementationPrompt(contract) {
    if (!contract) {
      return "No contract selected yet.";
    }
    return [
      "# Implementation Prompt",
      "",
      "Build the Original +1B operator console as a readiness-only control layer.",
      "",
      "Contract title: " + contract.contract_title,
      "Source phase: " + contract.source_phase,
      "Intended future automation: " + contract.intended_future_automation_type,
      "Action classification: " + contract.action_classification,
      "Required role: " + contract.required_role,
      "Required approval gate: " + contract.required_approval_gate,
      "Required dry-run evidence: " + contract.required_dry_run_evidence,
      "Required audit event model: " + contract.required_audit_event_model,
      "Required rollback policy: " + contract.required_rollback_policy,
      "Required validators: " + contract.required_validators,
      "Required production verification: " + contract.required_production_verification,
      "Forbidden operations: " + (contract.forbidden_operations || []).join(", "),
      "Future dependencies: " + contract.future_dependencies,
    ].join("\n");
  }

  function buildFullRunbookMarkdown(contract, mode) {
    return [
      "# Original +1B Full Runbook",
      "",
      "1. Review the unified operator flow rail.",
      "2. Confirm the master cockpit remains READINESS_ONLY.",
      "3. Load the formal contract schema pack.",
      "4. Review the automation contract builder output.",
      "5. Copy the local runbook outputs into your operator notes.",
      "6. Verify the validator wall remains green.",
      "7. Keep the mode emphasis display-only and inert.",
      "",
      "Selected contract: " + (contract ? contract.contract_title : "none"),
      "Selected mode: " + mode.mode_title,
      "",
      "Safety boundary: nothing executes, mutates, deploys, merges, pushes, or creates PRs.",
    ].join("\n");
  }

  function buildDryRunPlanMarkdown(contract) {
    if (!contract) {
      return "No contract selected yet.";
    }
    return [
      "# Original +1B Dry-Run Plan",
      "",
      "Action label: " + contract.schema_id,
      "Action class: " + contract.action_classification,
      "Target scope: " + contract.source_phase,
      "Expected read operations: " + contract.required_dry_run_evidence,
      "Expected write operations: none",
      "Required validators: " + contract.required_validators,
      "Required reports: Original +1B acceptance and production verification reports",
      "Expected artifacts: Copyable contract bundle and merged readiness notes",
      "Rollback / no-go conditions: " + contract.required_rollback_policy,
      "Human approval requirement: " + contract.required_approval_gate,
      "Future dependencies: " + contract.future_dependencies,
    ].join("\n");
  }

  function buildPreflightChecklistMarkdown(contract) {
    return [
      "# Original +1B Preflight Checklist",
      "",
      "- [ ] auth exists",
      "- [ ] user role verified",
      "- [ ] permission checked",
      "- [ ] request stored",
      "- [ ] audit log active",
      "- [ ] dry-run completed",
      "- [ ] diff reviewed",
      "- [ ] rollback plan exists",
      "- [ ] human approval recorded",
      "- [ ] execution window approved",
      "- [ ] rate-limit controls present",
      "- [ ] secrets unavailable to browser",
      "- [ ] backend mutation endpoint explicitly authorized",
      "",
      "Current contract: " + (contract ? contract.contract_title : "none"),
    ].join("\n");
  }

  function buildNoGoReportMarkdown(contract) {
    return [
      "# Original +1B No-Go Report",
      "",
      "The console is readiness-only.",
      "No live automation is enabled.",
      "No execution is enabled.",
      "No mutation is enabled.",
      "No backend writes are enabled.",
      "No deploy, merge, push, or PR controls are enabled.",
      "",
      "Current contract: " + (contract ? contract.contract_title : "none"),
      "Forbidden operations: " + (contract ? (contract.forbidden_operations || []).join(", ") : "none"),
      "Future dependencies: " + (contract ? contract.future_dependencies : "none"),
    ].join("\n");
  }

  function buildValidatorChecklistMarkdown() {
    return [
      "# Original +1B Validator Checklist",
      "",
      "- Phase 5A validators",
      "- Phase 5B validators",
      "- Phase 5C validators",
      "- Phase 5D validators",
      "- Phase 5E validators",
      "- Original +1 validators",
      "- Original +1B validators",
      "- Phase 4 / 4D / 4C / 4A validators",
      "- Phase 3 validators",
    ].join("\n");
  }

  function buildMergeReadinessSummaryMarkdown(contract, mode) {
    return [
      "# Original +1B Merge Readiness Summary",
      "",
      "Status: READINESS_ONLY",
      "Mode: " + mode.mode_title,
      "Contract: " + (contract ? contract.contract_title : "none"),
      "",
      "This layer is copy/paste only and remains inert.",
      "Nothing is saved, submitted, queued, executed, deployed, merged, pushed, or PR-created.",
    ].join("\n");
  }

  function renderSnapshot() {
    var pack = plus1bState.pack;
    var contract = getContract(plus1bState.selectedContractId);
    var mode = getMode(plus1bState.selectedModeId);
    return {
      pack: pack,
      contract: contract,
      mode: mode,
      flow_rows_html: buildFlowRows(),
      cockpit_grid_html: buildCockpitGrid(pack || {}),
      schema_rows_html: buildSchemaRows(pack),
      schema_preview_text: pack ? JSON.stringify(pack, null, 2) : "No contract schema pack loaded yet.",
      contract_preview_text: buildReadinessContractMarkdown(contract, mode),
      safety_grid_html: buildSafetyGrid(),
      validator_rows_html: buildValidatorRows(),
      mode_rows_html: buildModeRows(),
      implementation_prompt_markdown: buildImplementationPrompt(contract),
      full_runbook_markdown: buildFullRunbookMarkdown(contract, mode),
      readiness_contract_markdown: buildReadinessContractMarkdown(contract, mode),
      dry_run_markdown: buildDryRunPlanMarkdown(contract),
      preflight_markdown: buildPreflightChecklistMarkdown(contract),
      no_go_markdown: buildNoGoReportMarkdown(contract),
      validator_checklist_markdown: buildValidatorChecklistMarkdown(),
      merge_readiness_markdown: buildMergeReadinessSummaryMarkdown(contract, mode),
    };
  }

  function updatePlus1BUI() {
    var snapshot = renderSnapshot();
    var flowBody = p1b("plus1b-flow-body");
    var cockpitGrid = p1b("plus1b-master-cockpit-grid");
    var cockpitNote = p1b("plus1b-master-cockpit-note");
    var schemaBody = p1b("plus1b-contract-schema-body");
    var schemaPreview = p1b("plus1b-contract-schema-preview");
    var contractPreview = p1b("plus1b-contract-preview");
    var safetyGrid = p1b("plus1b-safety-boundary-grid");
    var safetyNote = p1b("plus1b-safety-boundary-note");
    var validatorBody = p1b("plus1b-validator-wall-body");
    var modeBody = p1b("plus1b-mode-body");

    if (flowBody) flowBody.innerHTML = snapshot.flow_rows_html;
    if (cockpitGrid) cockpitGrid.innerHTML = snapshot.cockpit_grid_html;
    if (cockpitNote) cockpitNote.textContent = "The console remains readiness-only. Nothing executes, nothing mutates, and no backend dependency is live yet.";
    if (schemaBody) schemaBody.innerHTML = snapshot.schema_rows_html;
    if (schemaPreview) schemaPreview.textContent = snapshot.schema_preview_text;
    if (contractPreview) contractPreview.textContent = snapshot.contract_preview_text;
    if (safetyGrid) safetyGrid.innerHTML = snapshot.safety_grid_html;
    if (safetyNote) safetyNote.textContent = "Future real automation requires separate auth, storage, audit, queue, approval, and backend write systems that are not present yet.";
    if (validatorBody) validatorBody.innerHTML = snapshot.validator_rows_html;
    if (modeBody) modeBody.innerHTML = snapshot.mode_rows_html;
  }

  function loadSchemaPack() {
    var schemaPreview = p1b("plus1b-contract-schema-preview");
    var dashboardData = getDashboardData();
    var embeddedPack = dashboardData.original_plus1b_contract_schemas || null;
    if (schemaPreview) {
      schemaPreview.textContent = embeddedPack ? "Loading contract schema pack from dashboard data..." : "No contract schema pack loaded yet.";
    }
    plus1bState.pack = embeddedPack;
    updatePlus1BUI();
    if (schemaPreview) {
      schemaPreview.textContent = embeddedPack ? JSON.stringify(embeddedPack, null, 2) : "No contract schema pack loaded yet.";
    }
    var status = p1b("copy-status");
    if (status && embeddedPack) {
      status.textContent = "Original +1B contract schema pack loaded from dashboard data.";
    }
  }

  function initPlus1B() {
    var shell = document.querySelector("[data-plus1b-operator-console-contract-layer]");
    if (!shell) {
      return;
    }

    bindCopyButton("plus1b-copy-implementation-prompt", function (snapshot) { return snapshot.implementation_prompt_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Implementation prompt copied.");
    bindCopyButton("plus1b-copy-full-runbook", function (snapshot) { return snapshot.full_runbook_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Full runbook copied.");
    bindCopyButton("plus1b-copy-readiness-contract", function (snapshot) { return snapshot.readiness_contract_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Readiness contract copied.");
    bindCopyButton("plus1b-copy-dry-run-plan", function (snapshot) { return snapshot.dry_run_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Dry-run plan copied.");
    bindCopyButton("plus1b-copy-preflight-checklist", function (snapshot) { return snapshot.preflight_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Preflight checklist copied.");
    bindCopyButton("plus1b-copy-no-go-report", function (snapshot) { return snapshot.no_go_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: No-go report copied.");
    bindCopyButton("plus1b-copy-validator-checklist", function (snapshot) { return snapshot.validator_checklist_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Validator checklist copied.");
    bindCopyButton("plus1b-copy-merge-readiness-summary", function (snapshot) { return snapshot.merge_readiness_markdown; }, "Original +1B: Load a contract schema first.", "Original +1B: Merge-readiness summary copied.");

    var loadButton = p1b("plus1b-load-schema-pack-button");
    if (loadButton) {
      loadButton.addEventListener("click", loadSchemaPack);
    }

    updatePlus1BUI();
    loadSchemaPack();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus1B);
  } else {
    initPlus1B();
  }
})();

(function () {
  var plus1cState = {
    model: null,
  };

  function p1c(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p1c("dashboard-data");
    if (!node) {
      return {};
    }
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (error) {
      return {};
    }
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p1c("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p1c(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function statusBadgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "pass" || value === "complete") {
      return "pass";
    }
    if (value === "warning") {
      return "warning";
    }
    if (value === "blocked" || value === "fail") {
      return "locked";
    }
    return "info";
  }

  function buildRows(items, columns, emptyText) {
    if (!items || !items.length) {
      return emptyText;
    }
    return items.map(function (item) {
      return "<tr>" + columns(item) + "</tr>";
    }).join("");
  }

  function buildScorecardRows(model) {
    return buildRows(model && model.scorecard, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.category) + '</th>',
        '<td><span class="badge ' + statusBadgeClass(item.status) + '">' + escapeHtml(String(item.score)) + '</span></td>',
        '<td><span class="badge ' + statusBadgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
        '<td>' + escapeHtml(item.reason) + '</td>',
        '<td>' + escapeHtml(item.recommended_improvement) + '</td>',
      ].join("");
    }, '<tr><td colspan="5" class="empty">No readiness scoring model loaded yet.</td></tr>');
  }

  function buildContractQaRows(model) {
    return buildRows(model && model.contract_qa_matrix, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.schema_id) + '</th>',
        '<td>' + escapeHtml(item.required_fields_present) + '</td>',
        '<td>' + escapeHtml(item.forbidden_fields_absent) + '</td>',
        '<td>' + escapeHtml(item.safety_notes_present) + '</td>',
        '<td>' + escapeHtml(item.future_dependency_noted) + '</td>',
        '<td>' + escapeHtml(item.copy_output_available) + '</td>',
        '<td><span class="badge ' + statusBadgeClass(item.qa_status) + '">' + escapeHtml(item.qa_status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="7" class="empty">No contract QA model loaded yet.</td></tr>');
  }

  function buildSafetyAssertionRows(model) {
    return buildRows(model && model.safety_assertions, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.assertion) + '</th>',
        '<td>' + escapeHtml(item.expected_value) + '</td>',
        '<td>' + escapeHtml(item.current_value) + '</td>',
        '<td><span class="badge ' + statusBadgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="4" class="empty">No safety assertions loaded yet.</td></tr>');
  }

  function buildNoGoDecisionRows(model) {
    return buildRows(model && model.no_go_decisions, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.decision_id) + '</th>',
        '<td>' + escapeHtml(item.reason) + '</td>',
        '<td>' + escapeHtml(item.required_future_dependency) + '</td>',
        '<td>' + escapeHtml(item.operator_recommendation) + '</td>',
      ].join("");
    }, '<tr><td colspan="4" class="empty">No no-go model loaded yet.</td></tr>');
  }

  function buildDependencyGapRows(model) {
    return buildRows(model && model.dependency_gap_map, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.dependency) + '</th>',
        '<td>' + escapeHtml(item.required_before) + '</td>',
        '<td>' + escapeHtml(item.current_status) + '</td>',
        '<td><span class="badge ' + statusBadgeClass(item.blocking_level) + '">' + escapeHtml(item.blocking_level) + '</span></td>',
        '<td>' + escapeHtml(item.recommended_future_phase) + '</td>',
      ].join("");
    }, '<tr><td colspan="5" class="empty">No dependency gap model loaded yet.</td></tr>');
  }

  function buildValidatorConfidenceRows(model) {
    return buildRows(model && model.validator_confidence_groups, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.group) + '</th>',
        '<td><code>' + escapeHtml(item.pass_string) + '</code></td>',
        '<td>' + escapeHtml(item.coverage_type) + '</td>',
        '<td><span class="badge ' + statusBadgeClass(item.confidence_level) + '">' + escapeHtml(item.confidence_level) + '</span></td>',
        '<td>' + escapeHtml(item.merge_requirement) + '</td>',
        '<td>' + escapeHtml(item.production_requirement) + '</td>',
      ].join("");
    }, '<tr><td colspan="6" class="empty">No validator confidence model loaded yet.</td></tr>');
  }

  function buildScorecardMarkdown(model) {
    var items = model && model.scorecard ? model.scorecard : [];
    var lines = ["# Original +1C Readiness Scorecard", "", "Status: " + (model ? model.overall_status : "READINESS_ONLY"), "Recommendation: " + (model ? model.current_recommendation : "READY_FOR_READINESS_REVIEW_ONLY"), ""];
    items.forEach(function (item) {
      lines.push("## " + item.category);
      lines.push("- Score: " + item.score);
      lines.push("- Status: " + item.status);
      lines.push("- Reason: " + item.reason);
      lines.push("- Recommended improvement: " + item.recommended_improvement);
      lines.push("");
    });
    return lines.join("\n").trim();
  }

  function buildContractQaMarkdown(model) {
    var items = model && model.contract_qa_matrix ? model.contract_qa_matrix : [];
    var lines = ["# Original +1C Contract QA Report", "", "## Summary", "Local contract QA stays read-only and copy-only.", ""];
    items.forEach(function (item) {
      lines.push("## " + item.schema_id);
      lines.push("- Required fields present: " + item.required_fields_present);
      lines.push("- Forbidden fields absent: " + item.forbidden_fields_absent);
      lines.push("- Safety notes present: " + item.safety_notes_present);
      lines.push("- Future dependency noted: " + item.future_dependency_noted);
      lines.push("- Copy output available: " + item.copy_output_available);
      lines.push("- QA status: " + item.qa_status);
      lines.push("");
    });
    return lines.join("\n").trim();
  }

  function buildSafetyAssertionsMarkdown(model) {
    var items = model && model.safety_assertions ? model.safety_assertions : [];
    var lines = ["# Original +1C Safety Assertion Summary", "", "## Assertions"];
    items.forEach(function (item) {
      lines.push("- " + item.assertion + ": expected " + item.expected_value + ", current " + item.current_value + " (" + item.status + ")");
    });
    return lines.join("\n").trim();
  }

  function buildNoGoDecisionMarkdown(model) {
    var items = model && model.no_go_decisions ? model.no_go_decisions : [];
    var lines = ["# Original +1C No-Go Decision Report", "", "## Decisions"];
    items.forEach(function (item) {
      lines.push("- " + item.decision_id + ": " + item.reason + " | dependency: " + item.required_future_dependency + " | recommendation: " + item.operator_recommendation);
    });
    return lines.join("\n").trim();
  }

  function buildDependencyGapMarkdown(model) {
    var items = model && model.dependency_gap_map ? model.dependency_gap_map : [];
    var lines = ["# Original +1C Dependency Gap Map", "", "## Gaps"];
    items.forEach(function (item) {
      lines.push("- " + item.dependency + ": required before " + item.required_before + " | current " + item.current_status + " | blocking " + item.blocking_level + " | future phase " + item.recommended_future_phase);
    });
    return lines.join("\n").trim();
  }

  function buildValidatorConfidenceMarkdown(model) {
    var items = model && model.validator_confidence_groups ? model.validator_confidence_groups : [];
    var lines = ["# Original +1C Validator Confidence Report", "", "## Groups"];
    items.forEach(function (item) {
      lines.push("- " + item.group + ": " + item.pass_string + " | coverage: " + item.coverage_type + " | confidence: " + item.confidence_level);
    });
    return lines.join("\n").trim();
  }

  function buildGoNoGoPacketMarkdown(model) {
    if (!model) {
      return "No readiness QA model loaded yet.";
    }
    return [
      "# Original +1C Go / No-Go Packet",
      "",
      "Status: " + model.overall_status,
      "Recommendation: " + model.current_recommendation,
      "Final recommendation: " + model.final_recommendation,
      "",
      buildScorecardMarkdown(model),
      "",
      buildContractQaMarkdown(model),
      "",
      buildSafetyAssertionsMarkdown(model),
      "",
      buildNoGoDecisionMarkdown(model),
      "",
      buildDependencyGapMarkdown(model),
      "",
      buildValidatorConfidenceMarkdown(model),
    ].join("\n");
  }

  function renderSnapshot() {
    var dashboardData = readDashboardData();
    var model = plus1cState.model || dashboardData.original_plus1c_readiness_qa_model || null;
    plus1cState.model = model;
    return {
      model: model,
      scorecard_rows_html: buildScorecardRows(model),
      contract_qa_rows_html: buildContractQaRows(model),
      safety_assertion_rows_html: buildSafetyAssertionRows(model),
      no_go_rows_html: buildNoGoDecisionRows(model),
      dependency_gap_rows_html: buildDependencyGapRows(model),
      validator_confidence_rows_html: buildValidatorConfidenceRows(model),
      readiness_scorecard_markdown: buildScorecardMarkdown(model),
      contract_qa_markdown: buildContractQaMarkdown(model),
      safety_assertion_markdown: buildSafetyAssertionsMarkdown(model),
      no_go_decision_markdown: buildNoGoDecisionMarkdown(model),
      dependency_gap_markdown: buildDependencyGapMarkdown(model),
      validator_confidence_markdown: buildValidatorConfidenceMarkdown(model),
      go_no_go_packet_markdown: buildGoNoGoPacketMarkdown(model),
    };
  }

  function updatePlus1CUI() {
    var snapshot = renderSnapshot();
    var scorecardBody = p1c("plus1c-scorecard-body");
    var contractQaBody = p1c("plus1c-contract-qa-body");
    var safetyAssertionBody = p1c("plus1c-safety-assertion-body");
    var noGoBody = p1c("plus1c-no-go-body");
    var dependencyGapBody = p1c("plus1c-dependency-gap-body");
    var validatorConfidenceBody = p1c("plus1c-validator-confidence-body");
    var goNoGoPreview = p1c("plus1c-go-no-go-preview");

    if (scorecardBody) scorecardBody.innerHTML = snapshot.scorecard_rows_html;
    if (contractQaBody) contractQaBody.innerHTML = snapshot.contract_qa_rows_html;
    if (safetyAssertionBody) safetyAssertionBody.innerHTML = snapshot.safety_assertion_rows_html;
    if (noGoBody) noGoBody.innerHTML = snapshot.no_go_rows_html;
    if (dependencyGapBody) dependencyGapBody.innerHTML = snapshot.dependency_gap_rows_html;
    if (validatorConfidenceBody) validatorConfidenceBody.innerHTML = snapshot.validator_confidence_rows_html;
    if (goNoGoPreview) goNoGoPreview.textContent = snapshot.go_no_go_packet_markdown;
  }

  function initPlus1C() {
    var shell = document.querySelector("[data-plus1c-readiness-scoring-contract-qa]");
    if (!shell) {
      return;
    }

    plus1cState.model = readDashboardData().original_plus1c_readiness_qa_model || null;

    bindCopyButton("plus1c-copy-readiness-scorecard", function (snapshot) { return snapshot.readiness_scorecard_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Readiness scorecard copied.");
    bindCopyButton("plus1c-copy-contract-qa-report", function (snapshot) { return snapshot.contract_qa_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Contract QA report copied.");
    bindCopyButton("plus1c-copy-safety-assertion-summary", function (snapshot) { return snapshot.safety_assertion_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Safety assertion summary copied.");
    bindCopyButton("plus1c-copy-no-go-decision-report", function (snapshot) { return snapshot.no_go_decision_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: No-go decision report copied.");
    bindCopyButton("plus1c-copy-dependency-gap-map", function (snapshot) { return snapshot.dependency_gap_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Dependency gap map copied.");
    bindCopyButton("plus1c-copy-validator-confidence-report", function (snapshot) { return snapshot.validator_confidence_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Validator confidence report copied.");
    bindCopyButton("plus1c-copy-go-no-go-packet", function (snapshot) { return snapshot.go_no_go_packet_markdown; }, "Original +1C: Load readiness data first.", "Original +1C: Go/no-go packet copied.");

    updatePlus1CUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus1C);
  } else {
    initPlus1C();
  }
})();

(function () {
  var plus1dState = {
    model: null,
  };

  function p1d(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p1d("dashboard-data");
    if (!node) {
      return {};
    }
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (error) {
      return {};
    }
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p1d("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p1d(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function badgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "pass" || value === "complete" || value === "yes" || value === "true" || value === "existing read-only endpoint") {
      return "pass";
    }
    if (value === "warning" || value === "blueprint_only" || value === "planning_only" || value === "info") {
      return "warning";
    }
    if (value === "blocked" || value === "fail" || value === "false" || value === "not_implemented" || value === "not implemented") {
      return "locked";
    }
    return "info";
  }

  function boolValue(value) {
    return value ? "yes" : "no";
  }

  function buildRows(items, renderer, emptyText) {
    if (!items || !items.length) {
      return emptyText;
    }
    return items.map(function (item) {
      return "<tr>" + renderer(item) + "</tr>";
    }).join("");
  }

  function buildOverviewRows(model) {
    return buildRows(model && model.backend_boundary_overview, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.label) + '</th>',
        '<td>' + escapeHtml(item.value) + '</td>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="3" class="empty">No backend boundary overview loaded yet.</td></tr>');
  }

  function buildEndpointRows(model) {
    return buildRows(model && model.endpoint_contract_map, function (item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.method + " " + item.path) + '</code></th>',
        '<td>' + escapeHtml(item.purpose) + '</td>',
        '<td>' + escapeHtml(item.current_status) + '</td>',
        '<td>' + escapeHtml(item.required_auth) + '</td>',
        '<td>' + escapeHtml(item.required_role) + '</td>',
        '<td><span class="badge ' + badgeClass(item.writes_data) + '">' + escapeHtml(boolValue(item.writes_data)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.mutates_external_system) + '">' + escapeHtml(boolValue(item.mutates_external_system)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.requires_human_approval) + '">' + escapeHtml(boolValue(item.requires_human_approval)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.requires_audit_event) + '">' + escapeHtml(boolValue(item.requires_audit_event)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.current_implementation_allowed) + '">' + escapeHtml(boolValue(item.current_implementation_allowed)) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="11" class="empty">No backend endpoint contract map loaded yet.</td></tr>');
  }

  function buildRoleRows(model) {
    return buildRows(model && model.auth_role_permission_architecture, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.role) + '</th>',
        '<td>' + escapeHtml(item.future_permissions) + '</td>',
        '<td>' + escapeHtml(item.current_permissions) + '</td>',
        '<td><span class="badge ' + badgeClass(item.can_execute_now) + '">' + escapeHtml(boolValue(item.can_execute_now)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.can_mutate_now) + '">' + escapeHtml(boolValue(item.can_mutate_now)) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="5" class="empty">No auth / permission model loaded yet.</td></tr>');
  }

  function buildTableRows(items, keyLabels) {
    return (items || []).map(function (item) {
      return "<tr>" + keyLabels.map(function (key) {
        var value = item[key];
        if (typeof value === "boolean") {
          return '<td><span class="badge ' + badgeClass(value) + '">' + escapeHtml(boolValue(value)) + '</span></td>';
        }
        return "<td>" + escapeHtml(Array.isArray(value) ? value.join(", ") : value) + "</td>";
      }).join("") + "</tr>";
    }).join("");
  }

  function buildSequenceRows(model) {
    return buildRows(model && model.future_implementation_sequence, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.phase) + '</th>',
        '<td>' + escapeHtml(item.label) + '</td>',
        '<td>' + escapeHtml(item.purpose) + '</td>',
      ].join("");
    }, '<tr><td colspan="3" class="empty">No implementation sequence loaded yet.</td></tr>');
  }

  function buildChecklistRows(model) {
    return buildRows(model && model.real_automation_prerequisite_checklist, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.item) + '</th>',
        '<td><span class="badge ' + badgeClass(item.required) + '">' + escapeHtml(boolValue(item.required)) + '</span></td>',
        '<td>' + escapeHtml(item.current_state) + '</td>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="4" class="empty">No prerequisite checklist loaded yet.</td></tr>');
  }

  function buildIntegrationRows(model) {
    return buildRows(model && model.github_netlify_future_integration_boundary, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.integration) + '</th>',
        '<td><span class="badge ' + badgeClass(item.allowed_now) + '">' + escapeHtml(boolValue(item.allowed_now)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.required_future_auth) + '">' + escapeHtml(boolValue(item.required_future_auth)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.required_secret_storage) + '">' + escapeHtml(boolValue(item.required_secret_storage)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.required_human_approval) + '">' + escapeHtml(boolValue(item.required_human_approval)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.required_audit_log) + '">' + escapeHtml(boolValue(item.required_audit_log)) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.required_rollback_plan) + '">' + escapeHtml(boolValue(item.required_rollback_plan)) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="7" class="empty">No integration boundary loaded yet.</td></tr>');
  }

  function markdownHeader(title, recommendation) {
    return ["# Original +1D Backend Boundary Blueprint", "", "## " + title, recommendation ? "- Recommendation: " + recommendation : ""].filter(Boolean).join("\n");
  }

  function markdownList(title, items, formatter) {
    var lines = ["## " + title];
    (items || []).forEach(function (item) {
      lines.push("- " + formatter(item));
    });
    return lines.join("\n");
  }

  function buildBackendBoundaryMarkdown(model) {
    if (!model) {
      return "No backend boundary blueprint loaded yet.";
    }
    return [
      "# Original +1D Backend Boundary Blueprint",
      "",
      "Status: " + model.overall_status,
      "Recommendation: " + model.current_recommendation,
      "Final recommendation: " + model.final_recommendation,
      "",
      markdownList("Backend boundary overview", model.backend_boundary_overview, function (item) {
        return item.label + ": " + item.value + " (" + item.status + ")";
      }),
      "",
      markdownList("Endpoint contract map", model.endpoint_contract_map, function (item) {
        return item.method + " " + item.path + " | " + item.purpose + " | current: " + item.current_status + " | role: " + item.required_role + " | allowed now: " + boolValue(item.current_implementation_allowed);
      }),
      "",
      markdownList("Auth / role / permission architecture", model.auth_role_permission_architecture, function (item) {
        return item.role + " | future: " + item.future_permissions + " | current: " + item.current_permissions;
      }),
      "",
      buildStorageMarkdown("Persistent request storage model", model.persistent_request_storage_model),
      "",
      buildStorageMarkdown("Audit log storage model", model.audit_log_storage_model),
      "",
      buildStorageMarkdown("Approval record model", model.approval_record_model),
      "",
      buildQueueMarkdown(model),
      "",
      buildDryRunMarkdown(model),
      "",
      buildMutationMarkdown(model),
      "",
      markdownList("GitHub / Netlify future integration boundary", model.github_netlify_future_integration_boundary, function (item) {
        return item.integration + " | allowed now: " + boolValue(item.allowed_now) + " | auth: " + boolValue(item.required_future_auth) + " | approval: " + boolValue(item.required_human_approval);
      }),
      "",
      buildSimpleListMarkdown("Secrets management requirements", model.secrets_management_requirements),
      "",
      buildSimpleListMarkdown("Rollback / no-go enforcement model", model.rollback_no_go_enforcement_model),
      "",
      buildSimpleListMarkdown("Rate limit / abuse control plan", model.rate_limit_abuse_control_plan),
      "",
      markdownList("Future implementation sequence", model.future_implementation_sequence, function (item) {
        return item.phase + " " + item.label + " | " + item.purpose;
      }),
      "",
      markdownList("Real automation prerequisite checklist", model.real_automation_prerequisite_checklist, function (item) {
        return item.item + " | required: " + boolValue(item.required) + " | state: " + item.current_state + " | status: " + item.status;
      }),
    ].filter(Boolean).join("\n");
  }

  function buildStorageMarkdown(title, modelSection) {
    if (!modelSection) {
      return "## " + title + "\n- No data loaded.";
    }
    return [
      "## " + title,
      "- Status: " + modelSection.status,
      "- Future dependency: " + modelSection.future_dependency,
      "- Fields: " + modelSection.fields.join(", "),
    ].join("\n");
  }

  function buildQueueMarkdown(model) {
    var queueModel = model && model.queue_job_lifecycle_model;
    if (!queueModel) {
      return "## Queue / Job Lifecycle Model\n- No data loaded.";
    }
    return [
      "## Queue / Job Lifecycle Model",
      "- Status: " + queueModel.status,
      "- Future dependency: " + queueModel.future_dependency,
      "- States: " + queueModel.states.join(" -> "),
    ].join("\n");
  }

  function buildDryRunMarkdown(model) {
    var dryRun = model && model.dry_run_engine_boundary;
    if (!dryRun) {
      return "## Dry-Run Engine Boundary\n- No data loaded.";
    }
    return [
      "## Dry-Run Engine Boundary",
      "- Status: " + dryRun.status,
      "- Requirements:",
    ].concat(dryRun.requirements.map(function (item) { return "  - " + item; })).join("\n");
  }

  function buildMutationMarkdown(model) {
    var mutation = model && model.mutation_gateway_boundary;
    if (!mutation) {
      return "## Mutation Gateway Boundary\n- No data loaded.";
    }
    return [
      "## Mutation Gateway Boundary",
      "- Status: " + mutation.status,
      "- Future dependency: " + mutation.future_dependency,
      "- Requirements:",
    ].concat(mutation.requirements.map(function (item) { return "  - " + item; })).join("\n");
  }

  function buildSimpleListMarkdown(title, items) {
    return ["## " + title].concat((items || []).map(function (item) {
      return "- " + item;
    })).join("\n");
  }

  function buildEndpointMapMarkdown(model) {
    var items = model && model.endpoint_contract_map ? model.endpoint_contract_map : [];
    var lines = ["# Original +1D Endpoint Contract Map", ""];
    items.forEach(function (item) {
      lines.push("## " + item.method + " " + item.path);
      lines.push("- Purpose: " + item.purpose);
      lines.push("- Current status: " + item.current_status);
      lines.push("- Required auth: " + item.required_auth);
      lines.push("- Required role: " + item.required_role);
      lines.push("- Writes data: " + boolValue(item.writes_data));
      lines.push("- Mutates external system: " + boolValue(item.mutates_external_system));
      lines.push("- Requires human approval: " + boolValue(item.requires_human_approval));
      lines.push("- Requires audit event: " + boolValue(item.requires_audit_event));
      lines.push("- Current implementation allowed: " + boolValue(item.current_implementation_allowed));
      lines.push("");
    });
    return lines.join("\n").trim();
  }

  function buildAuthPermissionMarkdown(model) {
    var items = model && model.auth_role_permission_architecture ? model.auth_role_permission_architecture : [];
    var lines = ["# Original +1D Auth / Role / Permission Architecture", ""];
    items.forEach(function (item) {
      lines.push("## " + item.role);
      lines.push("- Future permissions: " + item.future_permissions);
      lines.push("- Current permissions: " + item.current_permissions);
      lines.push("- Can execute now: " + boolValue(item.can_execute_now));
      lines.push("- Can mutate now: " + boolValue(item.can_mutate_now));
      lines.push("");
    });
    return lines.join("\n").trim();
  }

  function buildModelMarkdown(title, section, lines) {
    var out = ["# Original +1D " + title, "", "## Status", section.status, "", "## Future dependency", section.future_dependency, "", "## Fields"];
    (section.fields || []).forEach(function (field) {
      out.push("- " + field);
    });
    if (lines && lines.length) {
      out.push("");
      out = out.concat(lines);
    }
    return out.join("\n").trim();
  }

  function buildStorageModelMarkdown(title, section) {
    return buildModelMarkdown(title, section, []);
  }

  function buildSequenceMarkdown(model) {
    var items = model && model.future_implementation_sequence ? model.future_implementation_sequence : [];
    var lines = ["# Original +1D Future Implementation Sequence", ""];
    items.forEach(function (item) {
      lines.push("- " + item.phase + " " + item.label + ": " + item.purpose);
    });
    return lines.join("\n").trim();
  }

  function buildChecklistMarkdown(model) {
    var items = model && model.real_automation_prerequisite_checklist ? model.real_automation_prerequisite_checklist : [];
    var lines = ["# Original +1D Real Automation Prerequisite Checklist", ""];
    items.forEach(function (item) {
      lines.push("- " + item.item + ": required " + boolValue(item.required) + ", state " + item.current_state + ", status " + item.status);
    });
    return lines.join("\n").trim();
  }

  function buildIntegrationMarkdown(model) {
    var items = model && model.github_netlify_future_integration_boundary ? model.github_netlify_future_integration_boundary : [];
    var lines = ["# Original +1D GitHub / Netlify Future Integration Boundary", ""];
    items.forEach(function (item) {
      lines.push("- " + item.integration + ": allowed now " + boolValue(item.allowed_now) + ", future auth " + boolValue(item.required_future_auth) + ", approval " + boolValue(item.required_human_approval));
    });
    return lines.join("\n").trim();
  }

  function buildListMarkdown(title, items) {
    var lines = ["# Original +1D " + title, ""];
    (items || []).forEach(function (item) {
      lines.push("- " + item);
    });
    return lines.join("\n").trim();
  }

  function buildBlueprintPacketMarkdown(model) {
    if (!model) {
      return "No backend boundary blueprint loaded yet.";
    }
    return [
      "# Original +1D Backend Boundary Blueprint Packet",
      "",
      "Status: " + model.overall_status,
      "Recommendation: " + model.current_recommendation,
      "Final recommendation: " + model.final_recommendation,
      "",
      buildBackendBoundaryMarkdown(model),
    ].join("\n");
  }

  function renderSnapshot() {
    var dashboardData = readDashboardData();
    var model = plus1dState.model || dashboardData.original_plus1d_backend_boundary_model || null;
    plus1dState.model = model;
    return {
      model: model,
      backend_boundary_overview_rows_html: buildOverviewRows(model),
      endpoint_contract_map_rows_html: buildEndpointRows(model),
      auth_permission_rows_html: buildRoleRows(model),
      request_storage_preview_text: model ? JSON.stringify(model.persistent_request_storage_model, null, 2) : "No request storage model loaded yet.",
      audit_log_preview_text: model ? JSON.stringify(model.audit_log_storage_model, null, 2) : "No audit log model loaded yet.",
      approval_record_preview_text: model ? JSON.stringify(model.approval_record_model, null, 2) : "No approval record model loaded yet.",
      queue_job_lifecycle_preview_text: model ? JSON.stringify(model.queue_job_lifecycle_model, null, 2) : "No queue job lifecycle model loaded yet.",
      dry_run_engine_preview_text: model ? JSON.stringify(model.dry_run_engine_boundary, null, 2) : "No dry-run boundary loaded yet.",
      mutation_gateway_preview_text: model ? JSON.stringify(model.mutation_gateway_boundary, null, 2) : "No mutation gateway boundary loaded yet.",
      future_integrations_rows_html: buildIntegrationRows(model),
      secrets_management_preview_text: model ? buildListMarkdown("Secrets Management Requirements", model.secrets_management_requirements) : "No secrets management requirements loaded yet.",
      rollback_no_go_preview_text: model ? buildListMarkdown("Rollback / No-Go Enforcement Model", model.rollback_no_go_enforcement_model) : "No rollback / no-go model loaded yet.",
      rate_limit_plan_preview_text: model ? buildListMarkdown("Rate Limit / Abuse Control Plan", model.rate_limit_abuse_control_plan) : "No rate-limit plan loaded yet.",
      implementation_sequence_rows_html: buildSequenceRows(model),
      prerequisite_checklist_rows_html: buildChecklistRows(model),
      backend_boundary_blueprint_markdown: buildBlueprintPacketMarkdown(model),
      endpoint_contract_map_markdown: buildEndpointMapMarkdown(model),
      auth_permission_markdown: buildAuthPermissionMarkdown(model),
      request_storage_markdown: buildStorageModelMarkdown("Persistent Request Storage Model", model ? model.persistent_request_storage_model : null),
      audit_log_markdown: buildStorageModelMarkdown("Audit Log Storage Model", model ? model.audit_log_storage_model : null),
      approval_record_markdown: buildStorageModelMarkdown("Approval Record Model", model ? model.approval_record_model : null),
      queue_job_lifecycle_markdown: buildQueueMarkdown(model),
      dry_run_engine_markdown: buildDryRunMarkdown(model),
      mutation_gateway_markdown: buildMutationMarkdown(model),
      future_integrations_markdown: buildIntegrationMarkdown(model),
      secrets_management_markdown: buildListMarkdown("Secrets Management Requirements", model ? model.secrets_management_requirements : []),
      rollback_no_go_markdown: buildListMarkdown("Rollback / No-Go Enforcement Model", model ? model.rollback_no_go_enforcement_model : []),
      rate_limit_plan_markdown: buildListMarkdown("Rate Limit / Abuse Control Plan", model ? model.rate_limit_abuse_control_plan : []),
      implementation_sequence_markdown: buildSequenceMarkdown(model),
      prerequisite_checklist_markdown: buildChecklistMarkdown(model),
    };
  }

  function updatePlus1DUI() {
    var snapshot = renderSnapshot();
    var overviewBody = p1d("plus1d-backend-boundary-overview-body");
    var endpointBody = p1d("plus1d-endpoint-map-body");
    var authBody = p1d("plus1d-auth-permission-body");
    var requestPreview = p1d("plus1d-request-storage-preview");
    var auditPreview = p1d("plus1d-audit-log-preview");
    var approvalPreview = p1d("plus1d-approval-record-preview");
    var queuePreview = p1d("plus1d-queue-job-lifecycle-preview");
    var dryRunPreview = p1d("plus1d-dry-run-engine-preview");
    var mutationPreview = p1d("plus1d-mutation-gateway-preview");
    var integrationBody = p1d("plus1d-future-integrations-body");
    var secretsPreview = p1d("plus1d-secrets-management-preview");
    var rollbackPreview = p1d("plus1d-rollback-no-go-preview");
    var rateLimitPreview = p1d("plus1d-rate-limit-plan-preview");
    var sequenceBody = p1d("plus1d-implementation-sequence-body");
    var checklistBody = p1d("plus1d-prerequisite-checklist-body");
    if (overviewBody) overviewBody.innerHTML = snapshot.backend_boundary_overview_rows_html;
    if (endpointBody) endpointBody.innerHTML = snapshot.endpoint_contract_map_rows_html;
    if (authBody) authBody.innerHTML = snapshot.auth_permission_rows_html;
    if (requestPreview) requestPreview.textContent = snapshot.request_storage_preview_text;
    if (auditPreview) auditPreview.textContent = snapshot.audit_log_preview_text;
    if (approvalPreview) approvalPreview.textContent = snapshot.approval_record_preview_text;
    if (queuePreview) queuePreview.textContent = snapshot.queue_job_lifecycle_preview_text;
    if (dryRunPreview) dryRunPreview.textContent = snapshot.dry_run_engine_preview_text;
    if (mutationPreview) mutationPreview.textContent = snapshot.mutation_gateway_preview_text;
    if (integrationBody) integrationBody.innerHTML = snapshot.future_integrations_rows_html;
    if (secretsPreview) secretsPreview.textContent = snapshot.secrets_management_preview_text;
    if (rollbackPreview) rollbackPreview.textContent = snapshot.rollback_no_go_preview_text;
    if (rateLimitPreview) rateLimitPreview.textContent = snapshot.rate_limit_plan_preview_text;
    if (sequenceBody) sequenceBody.innerHTML = snapshot.implementation_sequence_rows_html;
    if (checklistBody) checklistBody.innerHTML = snapshot.prerequisite_checklist_rows_html;
  }

  function initPlus1D() {
    var shell = document.querySelector("[data-plus1d-backend-boundary-blueprint]");
    if (!shell) {
      return;
    }

    plus1dState.model = readDashboardData().original_plus1d_backend_boundary_model || null;

    bindCopyButton("plus1d-copy-backend-boundary-blueprint", function (snapshot) { return snapshot.backend_boundary_blueprint_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Backend boundary blueprint copied.");
    bindCopyButton("plus1d-copy-endpoint-contract-map", function (snapshot) { return snapshot.endpoint_contract_map_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Endpoint contract map copied.");
    bindCopyButton("plus1d-copy-auth-permission-architecture", function (snapshot) { return snapshot.auth_permission_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Auth/permission architecture copied.");
    bindCopyButton("plus1d-copy-storage-model-summary", function (snapshot) { return snapshot.request_storage_markdown + "\n\n" + snapshot.audit_log_markdown + "\n\n" + snapshot.approval_record_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Storage model summary copied.");
    bindCopyButton("plus1d-copy-audit-model-summary", function (snapshot) { return snapshot.audit_log_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Audit model summary copied.");
    bindCopyButton("plus1d-copy-queue-lifecycle-model", function (snapshot) { return snapshot.queue_job_lifecycle_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Queue lifecycle model copied.");
    bindCopyButton("plus1d-copy-mutation-gateway-requirements", function (snapshot) { return snapshot.mutation_gateway_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Mutation gateway requirements copied.");
    bindCopyButton("plus1d-copy-future-implementation-sequence", function (snapshot) { return snapshot.implementation_sequence_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Future implementation sequence copied.");
    bindCopyButton("plus1d-copy-prerequisite-checklist", function (snapshot) { return snapshot.prerequisite_checklist_markdown; }, "Original +1D: Load backend boundary data first.", "Original +1D: Real automation prerequisite checklist copied.");

    updatePlus1DUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus1D);
  } else {
    initPlus1D();
  }
})();

(function () {
  var plus1eState = {
    model: null,
    selectedTicketId: null,
  };

  function p1e(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p1e("dashboard-data");
    if (!node) {
      return {};
    }
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (error) {
      return {};
    }
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p1e("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p1e(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function badgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "pass" || value === "complete" || value === "yes" || value === "true" || value === "ready_for_planning_only" || value === "ready_for_backend_implementation_planning_only" || value === "not_started") {
      return "pass";
    }
    if (value === "warning" || value === "planning_only" || value === "info") {
      return "warning";
    }
    if (value === "blocked" || value === "fail" || value === "false" || value === "not_ready_for_real_automation" || value === "not implemented") {
      return "locked";
    }
    return "info";
  }

  function boolValue(value) {
    return value ? "yes" : "no";
  }

  function buildRows(items, renderer, emptyText) {
    if (!items || !items.length) {
      return emptyText;
    }
    return items.map(function (item) {
      return "<tr>" + renderer(item) + "</tr>";
    }).join("");
  }

  function getModel() {
    var dashboardData = readDashboardData();
    var model = plus1eState.model || dashboardData.original_plus1e_backend_build_tickets || null;
    plus1eState.model = model;
    return model;
  }

  function selectedTicket(model) {
    if (!model) {
      return null;
    }
    var lookup = model.ticket_lookup || {};
    var ticket = lookup[plus1eState.selectedTicketId];
    if (ticket) {
      return ticket;
    }
    var tickets = model.future_phase_ticket_map || [];
    if (!tickets.length) {
      return null;
    }
    plus1eState.selectedTicketId = tickets[0].ticket_id;
    return tickets[0];
  }

  function buildGateRows(model) {
    return buildRows(model && model.backend_implementation_gate_overview, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.label) + '</th>',
        '<td>' + escapeHtml(item.value) + '</td>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="3" class="empty">No implementation gate overview loaded yet.</td></tr>');
  }

  function buildTicketRows(model) {
    return buildRows(model && model.future_phase_ticket_map, function (item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.ticket_id) + '</code></th>',
        '<td>' + escapeHtml(item.title) + '</td>',
        '<td>' + escapeHtml(item.purpose) + '</td>',
        '<td>' + escapeHtml(item.dependencies) + '</td>',
        '<td><span class="badge ' + badgeClass(item.current_status) + '">' + escapeHtml(item.current_status) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.blocked_for_now) + '">' + escapeHtml(boolValue(item.blocked_for_now)) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="6" class="empty">No build ticket map loaded yet.</td></tr>');
  }

  function buildDependencyRows(model) {
    return buildRows(model && model.dependency_prerequisite_map, function (item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.ticket_id) + '</code></th>',
        '<td>' + escapeHtml(item.required_before) + '</td>',
        '<td><span class="badge ' + badgeClass(item.current_status) + '">' + escapeHtml(item.current_status) + '</span></td>',
        '<td><span class="badge ' + badgeClass(item.blocking_level) + '">' + escapeHtml(item.blocking_level) + '</span></td>',
        '<td>' + escapeHtml(item.recommended_future_phase) + '</td>',
      ].join("");
    }, '<tr><td colspan="5" class="empty">No dependency map loaded yet.</td></tr>');
  }

  function buildGateStatusRows(model) {
    return buildRows(model && model.implementation_gate_statuses, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.gate) + '</th>',
        '<td><span class="badge ' + badgeClass(item.current_status) + '">' + escapeHtml(item.current_status) + '</span></td>',
        '<td>' + escapeHtml(item.blocking_reason) + '</td>',
        '<td>' + escapeHtml(item.required_future_ticket) + '</td>',
        '<td><span class="badge ' + badgeClass(item.can_proceed_now) + '">' + escapeHtml(boolValue(item.can_proceed_now)) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="5" class="empty">No gate statuses loaded yet.</td></tr>');
  }

  function buildValidatorRows(model) {
    return buildRows(model && model.ticket_validator_requirements, function (item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.ticket_id) + '</code></th>',
        '<td>' + escapeHtml(item.unit_validator) + '</td>',
        '<td>' + escapeHtml(item.integration_validator) + '</td>',
        '<td>' + escapeHtml(item.safety_validator) + '</td>',
        '<td>' + escapeHtml(item.diff_scope_validator) + '</td>',
        '<td>' + escapeHtml(item.report_validator) + '</td>',
        '<td>' + escapeHtml(item.production_verification_validator) + '</td>',
      ].join("");
    }, '<tr><td colspan="7" class="empty">No validator requirements loaded yet.</td></tr>');
  }

  function buildReportRows(model) {
    return buildRows(model && model.ticket_report_requirements, function (item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.ticket_id) + '</code></th>',
        '<td>' + escapeHtml(item.implementation_report) + '</td>',
        '<td>' + escapeHtml(item.design_report) + '</td>',
        '<td>' + escapeHtml(item.safety_report) + '</td>',
        '<td>' + escapeHtml(item.dependency_report) + '</td>',
        '<td>' + escapeHtml(item.validator_report) + '</td>',
        '<td>' + escapeHtml(item.acceptance_report) + '</td>',
        '<td>' + escapeHtml(item.production_verification_report) + '</td>',
      ].join("");
    }, '<tr><td colspan="8" class="empty">No report requirements loaded yet.</td></tr>');
  }

  function buildReadinessRows(model) {
    return buildRows(model && model.backend_build_readiness_summary, function (item) {
      return [
        '<th scope="row">' + escapeHtml(item.label) + '</th>',
        '<td>' + escapeHtml(item.value) + '</td>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="3" class="empty">No backend build readiness summary loaded yet.</td></tr>');
  }

  function buildTicketDetailRows(ticket) {
    if (!ticket) {
      return '<tr><td colspan="2" class="empty">No build ticket selected yet.</td></tr>';
    }
    var rows = [
      ["Ticket ID", ticket.ticket_id],
      ["Title", ticket.title],
      ["Branch", ticket.branch],
      ["Purpose", ticket.purpose],
      ["Dependencies", ticket.dependencies],
      ["Allowed Files", (ticket.allowed_files || []).join(", ")],
      ["Forbidden Files", (ticket.forbidden_files || []).join(", ")],
      ["Implementation Boundary", ticket.implementation_boundary],
      ["Required Inputs", (ticket.required_inputs || []).join(", ")],
      ["Required Outputs", (ticket.required_outputs || []).join(", ")],
      ["Required Tests", (ticket.required_tests || []).join(", ")],
      ["Required Validators", (ticket.required_validators || []).join(", ")],
      ["Required Reports", (ticket.required_reports || []).join(", ")],
      ["No-Go Conditions", (ticket.no_go_conditions || []).join(", ")],
      ["Rollback Requirements", (ticket.rollback_requirements || []).join(", ")],
      ["Acceptance Criteria", (ticket.acceptance_criteria || []).join(", ")],
      ["Final Response Requirements", (ticket.final_response_requirements || []).join(", ")],
      ["Current Status", ticket.current_status],
      ["Blocked Now", boolValue(ticket.blocked_for_now)],
    ];
    return rows.map(function (row) {
      return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td>" + escapeHtml(row[1]) + "</td></tr>";
    }).join("");
  }

  function buildTicketSelectOptions(model) {
    var tickets = model && model.future_phase_ticket_map ? model.future_phase_ticket_map : [];
    if (!tickets.length) {
      return '<option value="">No build tickets loaded yet.</option>';
    }
    return tickets.map(function (ticket) {
      return '<option value="' + escapeHtml(ticket.ticket_id) + '">' + escapeHtml(ticket.ticket_id + " - " + ticket.title) + '</option>';
    }).join("");
  }

  function buildModelMarkdown(model, key) {
    return model && model[key] ? model[key] : "No data loaded yet.";
  }

  function updateTicketSelect(model) {
    var select = p1e("plus1e-ticket-select");
    if (!select) {
      return;
    }
    var tickets = model && model.future_phase_ticket_map ? model.future_phase_ticket_map : [];
    select.innerHTML = buildTicketSelectOptions(model);
    if (tickets.length) {
      if (!plus1eState.selectedTicketId || !model.ticket_lookup || !model.ticket_lookup[plus1eState.selectedTicketId]) {
        plus1eState.selectedTicketId = tickets[0].ticket_id;
      }
      select.value = plus1eState.selectedTicketId;
    }
  }

  function renderSnapshot() {
    var model = getModel();
    var ticket = selectedTicket(model);
    return {
      model: model,
      selected_ticket: ticket,
      gate_overview_rows_html: buildGateRows(model),
      ticket_map_rows_html: buildTicketRows(model),
      dependency_rows_html: buildDependencyRows(model),
      gate_status_rows_html: buildGateStatusRows(model),
      validator_rows_html: buildValidatorRows(model),
      report_rows_html: buildReportRows(model),
      readiness_rows_html: buildReadinessRows(model),
      ticket_detail_rows_html: buildTicketDetailRows(ticket),
      ticket_detail_markdown: ticket ? ticket.ticket_markdown : "No build ticket selected yet.",
      codex_prompt_markdown: ticket ? ticket.codex_prompt : "No build ticket selected yet.",
      roadmap_markdown: buildModelMarkdown(model, "roadmap_markdown"),
      dependency_prerequisite_markdown: buildModelMarkdown(model, "dependency_prerequisite_markdown"),
      implementation_gate_status_markdown: buildModelMarkdown(model, "implementation_gate_status_markdown"),
      ticket_validator_requirements_markdown: buildModelMarkdown(model, "ticket_validator_requirements_markdown"),
      ticket_report_requirements_markdown: buildModelMarkdown(model, "ticket_report_requirements_markdown"),
      rollback_no_go_ticket_policy_markdown: buildModelMarkdown(model, "rollback_no_go_ticket_policy_markdown"),
      backend_build_readiness_summary_markdown: buildModelMarkdown(model, "backend_build_readiness_summary_markdown"),
    };
  }

  function updatePlus1EUI() {
    var snapshot = renderSnapshot();
    var gateOverviewBody = p1e("plus1e-gate-overview-body");
    var ticketMapBody = p1e("plus1e-ticket-map-body");
    var dependencyBody = p1e("plus1e-dependency-body");
    var ticketDetailBody = p1e("plus1e-ticket-detail-body");
    var gateStatusBody = p1e("plus1e-gate-status-body");
    var validatorBody = p1e("plus1e-validator-body");
    var reportBody = p1e("plus1e-report-body");
    var readinessGrid = p1e("plus1e-readiness-summary-grid");
    var roadmapPreview = p1e("plus1e-roadmap-preview");
    var ticketDetailPreview = p1e("plus1e-ticket-detail-preview");
    var promptPreview = p1e("plus1e-codex-prompt-preview");
    var policyPreview = p1e("plus1e-rollback-policy-preview");
    var readinessPreview = p1e("plus1e-readiness-summary-preview");
    if (gateOverviewBody) gateOverviewBody.innerHTML = snapshot.gate_overview_rows_html;
    if (ticketMapBody) ticketMapBody.innerHTML = snapshot.ticket_map_rows_html;
    if (dependencyBody) dependencyBody.innerHTML = snapshot.dependency_rows_html;
    if (ticketDetailBody) ticketDetailBody.innerHTML = snapshot.ticket_detail_rows_html;
    if (gateStatusBody) gateStatusBody.innerHTML = snapshot.gate_status_rows_html;
    if (validatorBody) validatorBody.innerHTML = snapshot.validator_rows_html;
    if (reportBody) reportBody.innerHTML = snapshot.report_rows_html;
    if (readinessGrid) readinessGrid.innerHTML = snapshot.readiness_rows_html;
    if (roadmapPreview) roadmapPreview.textContent = snapshot.roadmap_markdown;
    if (ticketDetailPreview) ticketDetailPreview.textContent = snapshot.ticket_detail_markdown;
    if (promptPreview) promptPreview.textContent = snapshot.codex_prompt_markdown;
    if (policyPreview) policyPreview.textContent = snapshot.rollback_no_go_ticket_policy_markdown;
    if (readinessPreview) readinessPreview.textContent = snapshot.backend_build_readiness_summary_markdown;
    updateTicketSelect(snapshot.model);
  }

  function initPlus1E() {
    var shell = document.querySelector("[data-plus1e-backend-implementation-gate]");
    if (!shell) {
      return;
    }

    plus1eState.model = readDashboardData().original_plus1e_backend_build_tickets || null;
    if (plus1eState.model && plus1eState.model.future_phase_ticket_map && plus1eState.model.future_phase_ticket_map.length) {
      plus1eState.selectedTicketId = plus1eState.model.future_phase_ticket_map[0].ticket_id;
    }

    bindCopyButton("plus1e-copy-selected-build-ticket", function (snapshot) {
      return snapshot.ticket_detail_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Build ticket copied.");
    bindCopyButton("plus1e-copy-selected-codex-prompt", function (snapshot) {
      return snapshot.codex_prompt_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Codex prompt copied.");
    bindCopyButton("plus1e-copy-full-roadmap", function (snapshot) {
      return snapshot.roadmap_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Full backend implementation roadmap copied.");
    bindCopyButton("plus1e-copy-dependency-map", function (snapshot) {
      return snapshot.dependency_prerequisite_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Dependency prerequisite map copied.");
    bindCopyButton("plus1e-copy-validator-requirements", function (snapshot) {
      return snapshot.ticket_validator_requirements_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Validator requirements matrix copied.");
    bindCopyButton("plus1e-copy-report-requirements", function (snapshot) {
      return snapshot.ticket_report_requirements_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Report requirements matrix copied.");
    bindCopyButton("plus1e-copy-rollback-policy", function (snapshot) {
      return snapshot.rollback_no_go_ticket_policy_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Rollback policy copied.");
    bindCopyButton("plus1e-copy-readiness-summary", function (snapshot) {
      return snapshot.backend_build_readiness_summary_markdown;
    }, "Original +1E: Load backend build tickets first.", "Original +1E: Backend build readiness summary copied.");

    var select = p1e("plus1e-ticket-select");
    if (select) {
      select.addEventListener("change", function () {
        plus1eState.selectedTicketId = select.value;
        updatePlus1EUI();
      });
    }

    updatePlus1EUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus1E);
  } else {
    initPlus1E();
  }
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

(function () {
  var handoffMeta = null;
  var handoffNotes = "";

  function p5d(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function generateId() {
    if (window.crypto && window.crypto.randomUUID) {
      return crypto.randomUUID().slice(0, 8);
    }
    return Math.random().toString(36).slice(2, 10);
  }

  function timestamp() {
    return new Date().toISOString();
  }

  function textOf(node) {
    return node ? node.textContent.replace(/\s+/g, " ").trim() : "";
  }

  function readStatValue(container, label) {
    if (!container) {
      return "";
    }
    var stats = container.querySelectorAll(".stat");
    for (var i = 0; i < stats.length; i++) {
      var stat = stats[i];
      var labelNode = stat.querySelector("span");
      if (labelNode && labelNode.textContent.trim() === label) {
        return textOf(stat.querySelector("strong"));
      }
    }
    return "";
  }

  function getPhase5cReviewBoard() {
    if (typeof reviewBoard !== "undefined" && Array.isArray(reviewBoard)) {
      return reviewBoard;
    }
    return [];
  }

  function getPhase5cLedger() {
    if (typeof ledgerEvents !== "undefined" && Array.isArray(ledgerEvents)) {
      return ledgerEvents;
    }
    return [];
  }

  function getSelectedFilters() {
    var checkboxes = document.querySelectorAll("#phase5d-decision-filters input[type='checkbox']:checked");
    var values = [];
    checkboxes.forEach(function (cb) {
      values.push(cb.value);
    });
    return values;
  }

  function getHandoffNotesText() {
    var field = p5d("phase5d-handoff-notes");
    if (field) {
      handoffNotes = field.value || "";
    }
    return handoffNotes;
  }

  function getCurrentRequestPacket() {
    var shell = document.querySelector("[data-phase5a-shell]");
    if (!shell) {
      return null;
    }

    var workflowType = textOf(p5d("phase5a-workflow-type")) || "";
    var requestTitle = textOf(p5d("phase5a-request-title")) || "";
    var intent = textOf(p5d("phase5a-intent")) || "";
    var targetScope = textOf(p5d("phase5a-target-scope")) || "";
    var operatorNotes = textOf(p5d("phase5a-operator-notes")) || "";
    var stateDisplay = textOf(p5d("phase5a-current-state-display")) || "none";
    var riskBadge = p5d("phase5a-risk-badge");
    var riskLabel = riskBadge ? textOf(riskBadge) : "NOT CLASSIFIED";
    var requestSummary = p5d("phase5a-summary-grid");
    var requestId = readStatValue(requestSummary, "Request ID");
    var currentState = readStatValue(requestSummary, "Current State") || stateDisplay;
    var summaryGrid = p5d("phase5a-summary-grid");
    var hasLiveFields = [workflowType, requestTitle, intent, targetScope, operatorNotes].some(function (value) {
      return value.trim().length > 0;
    });
    var hasDraft = !!requestId;
    if (!hasLiveFields && !hasDraft && stateDisplay === "none") {
      return null;
    }

    var packet = {
      request_id: requestId || "UNASSIGNED",
      current_state: currentState,
      workflow_type: workflowType || "Unspecified",
      request_title: requestTitle || "(untitled)",
      intent: intent || "(none)",
      target_scope: targetScope || "(none)",
      operator_notes: operatorNotes || "(none)",
      risk_label: riskLabel || "NOT CLASSIFIED",
      risk_description: riskBadge ? textOf(p5d("phase5a-risk-description")) : "",
      summary_present: !!summaryGrid,
    };

    return packet;
  }

  function buildIncludedPackets(reviewBoard, selectedDecisions) {
    var packets = [];
    for (var i = 0; i < reviewBoard.length; i++) {
      var packet = reviewBoard[i];
      if (selectedDecisions.indexOf(packet.review_decision) !== -1) {
        packets.push({
          packet_id: packet.packet_id,
          request_title: packet.request_title,
          workflow_type: packet.workflow_type,
          risk_classification: packet.risk_classification,
          current_state: packet.current_state,
          review_decision: packet.review_decision,
          decision_timestamp: packet.decision_timestamp,
          notes_count: packet.notes_count,
        });
      }
    }
    return packets;
  }

  function stat(label, value) {
    return "<div class=\"stat\"><span>" + escapeHtml(label) + "</span><strong>" + escapeHtml(value) + "</strong></div>";
  }

  function renderRequestPreview(packet) {
    if (!packet) {
      return "No current request packet drafted yet.\nPopulate Phase 5A to enrich the handoff.";
    }
    return [
      "Request ID: " + packet.request_id,
      "Current State: " + packet.current_state,
      "Workflow Type: " + packet.workflow_type,
      "Request Title: " + packet.request_title,
      "Plain-Language Intent: " + packet.intent,
      "Target Scope: " + packet.target_scope,
      "Operator Notes: " + packet.operator_notes,
      "Risk Label: " + packet.risk_label,
    ].join("\n");
  }

  function renderLedgerPreview(reviewBoard, ledgerEvents, includedPackets, selectedDecisions) {
    return [
      "Review Board Packets: " + reviewBoard.length,
      "Ledger Events: " + ledgerEvents.length,
      "Selected Decisions: " + (selectedDecisions.length ? selectedDecisions.join(", ") : "none"),
      "Included Packets: " + includedPackets.length,
    ].join("\n");
  }

  function renderImplementationPrompt(state) {
    var lines = [];
    lines.push("Implement the Original Phase 5D client-side operator handoff composer.");
    lines.push("");
    lines.push("Context");
    lines.push("- Current request packet: " + (state.request_packet ? state.request_packet.request_title : "none"));
    lines.push("- Request state: " + (state.request_packet ? state.request_packet.current_state : "none"));
    lines.push("- Review board packets selected: " + state.included_packets.length + " of " + state.review_board.length);
    lines.push("- Review ledger events: " + state.ledger_events.length);
    lines.push("- Local handoff notes: " + (state.notes_text ? state.notes_text : "none"));
    lines.push("");
    lines.push("Requirements");
    lines.push("- Keep the handoff composer client-side only.");
    lines.push("- Generate copy/paste handoff text only.");
    lines.push("- Keep the state temporary and in-browser only.");
    lines.push("- Do not add persistence, backend writes, auth, database, queue storage, or action execution.");
    lines.push("- Do not add command execution, GitHub API calls, Netlify API calls, external API calls, or browser external fetches.");
    lines.push("- Do not add GitHub or Netlify mutation controls, deploy controls, merge controls, push controls, or PR controls.");
    lines.push("- Preserve Phase 4E as not started and Original +1 automation as not started.");
    lines.push("");
    lines.push("Deliverables");
    lines.push("- Handoff Source Panel");
    lines.push("- Handoff Notes Panel");
    lines.push("- Implementation Prompt Preview");
    lines.push("- Safety Summary Preview");
    lines.push("- Acceptance Checklist Preview");
    lines.push("- Rollback / No-Go Notes Preview");
    lines.push("- Full Handoff Markdown Preview");
    return lines.join("\n");
  }

  function renderSafetySummary(state) {
    var lines = [];
    lines.push("Original Phase 5D Safety Summary");
    lines.push("");
    lines.push("Verdict: PASS_WITH_HIGH_CONFIDENCE");
    lines.push("Client-side only: yes");
    lines.push("Generated locally: yes");
    lines.push("Copy/paste only: yes");
    lines.push("Temporary in-browser state only: yes");
    lines.push("No persistence: yes");
    lines.push("No backend writes: yes");
    lines.push("No Netlify Functions modified: yes");
    lines.push("No auth: yes");
    lines.push("No database: yes");
    lines.push("No queue storage: yes");
    lines.push("No action execution: yes");
    lines.push("No command execution: yes");
    lines.push("No GitHub API calls: yes");
    lines.push("No Netlify API calls: yes");
    lines.push("No external API calls: yes");
    lines.push("No browser external fetches: yes");
    lines.push("No secrets/tokens/env reads: yes");
    lines.push("No GitHub/Netlify mutation: yes");
    lines.push("No deploy/merge/push/PR controls: yes");
    lines.push("Phase 4E started: no");
    lines.push("Original +1 automation started: no");
    return lines.join("\n");
  }

  function renderAcceptanceChecklist(state) {
    var lines = [];
    lines.push("- [ ] Handoff Source Panel is visible and shows the live request packet plus review ledger snapshot.");
    lines.push("- [ ] Handoff Notes Panel captures local handoff notes in memory only.");
    lines.push("- [ ] Implementation Prompt Preview is available for copy/paste.");
    lines.push("- [ ] Safety Summary Preview is available for copy/paste.");
    lines.push("- [ ] Acceptance Checklist Preview is available for copy/paste.");
    lines.push("- [ ] Rollback / No-Go Notes Preview is available for copy/paste.");
    lines.push("- [ ] Full Handoff Markdown Preview is available for copy/paste.");
    lines.push("- [ ] Copy buttons work for the implementation prompt, safety summary, acceptance checklist, rollback notes, and full handoff markdown.");
    lines.push("- [ ] No persistence, backend writes, auth, database, queue storage, action execution, or command execution were added.");
    lines.push("- [ ] No GitHub API calls, Netlify API calls, external API calls, or browser external fetches were added.");
    lines.push("- [ ] No deploy, merge, push, or PR controls were added.");
    lines.push("- [ ] Phase 4E remains not started.");
    lines.push("- [ ] Original +1 automation remains not started.");
    return lines.join("\n");
  }

  function renderRollbackNotes(state) {
    var lines = [];
    lines.push("Rollback / No-Go Notes");
    lines.push("");
    lines.push("- Stop if the current request packet is blank and no Phase 5C packets are selected.");
    lines.push("- Stop if any preview block begins to exceed contained scroll height or becomes unreadable.");
    lines.push("- Stop if the composer shows any enabled submit, queue, save, execute, deploy, merge, push, or create PR control.");
    lines.push("- Stop if any persistence, backend write, auth, database, queue, command execution, or mutation path appears.");
    lines.push("- Stop if the handoff would require Phase 4E or Original +1 automation to complete.");
    lines.push("- Stop if the generated text needs file upload, file import, binary export, or external fetch behavior.");
    lines.push("- If the source packet or review ledger changes materially, re-compose before handing off.");
    return lines.join("\n");
  }

  function renderFullMarkdown(state) {
    var lines = [];
    lines.push("# Original Phase 5D - Client-Side Operator Handoff Composer");
    lines.push("");
    lines.push("## Handoff Source Panel");
    lines.push("");
    lines.push("### Current Local Request Packet");
    lines.push("");
    lines.push("```text");
    lines.push(renderRequestPreview(state.request_packet));
    lines.push("```");
    lines.push("");
    lines.push("### Review Ledger Snapshot");
    lines.push("");
    lines.push("```text");
    lines.push(renderLedgerPreview(state.review_board, state.ledger_events, state.included_packets, state.selected_decisions));
    lines.push("```");
    lines.push("");
    lines.push("### Included Packets");
    lines.push("");
    if (state.included_packets.length === 0) {
      lines.push("_No review board packets are currently included in this handoff draft._");
    } else {
      for (var i = 0; i < state.included_packets.length; i++) {
        var packet = state.included_packets[i];
        lines.push("- **" + packet.packet_id + "**: " + packet.request_title + " (" + packet.workflow_type + ") - Risk: " + packet.risk_classification + " - Decision: " + packet.review_decision);
      }
    }
    lines.push("");
    lines.push("## Handoff Notes Panel");
    lines.push("");
    lines.push(state.notes_text ? state.notes_text : "_No local handoff notes captured yet._");
    lines.push("");
    lines.push("## Implementation Prompt");
    lines.push("");
    lines.push("```text");
    lines.push(renderImplementationPrompt(state));
    lines.push("```");
    lines.push("");
    lines.push("## Safety Summary");
    lines.push("");
    lines.push("```text");
    lines.push(renderSafetySummary(state));
    lines.push("```");
    lines.push("");
    lines.push("## Acceptance Checklist");
    lines.push("");
    lines.push("```text");
    lines.push(renderAcceptanceChecklist(state));
    lines.push("```");
    lines.push("");
    lines.push("## Rollback / No-Go Notes");
    lines.push("");
    lines.push("```text");
    lines.push(renderRollbackNotes(state));
    lines.push("```");
    lines.push("");
    lines.push("## Recommended Next Operator Decision");
    lines.push("");
    lines.push("review_phase_5d_local_preview_then_prepare_merge_or_refine_ui");
    return lines.join("\n");
  }

  function statHTML(items, emptyLabel) {
    if (!items || !items.length) {
      items = [{ label: "Status", value: emptyLabel || "No source data yet" }];
    }
    return items.map(function (item) {
      return stat(item.label, item.value);
    }).join("");
  }

  function renderRequestTable(state) {
    if (!state.included_packets.length) {
      return '<tr><td colspan="6" class="empty">No handoff composed yet. Use Phase 5C decisions to compose a handoff.</td></tr>';
    }
    return state.included_packets.map(function (packet) {
      return "<tr>" +
        "<td><code>" + escapeHtml(packet.packet_id) + "</code></td>" +
        "<td>" + escapeHtml(packet.request_title) + "</td>" +
        "<td>" + escapeHtml(packet.workflow_type) + "</td>" +
        "<td>" + escapeHtml(packet.risk_classification) + "</td>" +
        "<td>" + escapeHtml(packet.review_decision) + "</td>" +
        "<td><span class=\"badge pass\">YES</span></td>" +
        "</tr>";
    }).join("");
  }

  function renderSnapshot() {
    var requestPacket = getCurrentRequestPacket();
    var reviewBoard = getPhase5cReviewBoard();
    var ledgerEvents = getPhase5cLedger();
    var selectedDecisions = getSelectedFilters();
    var notesText = getHandoffNotesText();
    var includedPackets = buildIncludedPackets(reviewBoard, selectedDecisions);
    var sourcePresent = !!requestPacket || reviewBoard.length > 0 || ledgerEvents.length > 0 || includedPackets.length > 0 || !!notesText.trim() || !!handoffMeta;
    if (!sourcePresent) {
      return null;
    }

    var meta = handoffMeta || {
      handoff_id: "HANDOFF-DRAFT",
      generated_at: "Draft preview only",
    };

    return {
      handoff_id: meta.handoff_id,
      generated_at: meta.generated_at,
      request_packet: requestPacket,
      review_board: reviewBoard,
      ledger_events: ledgerEvents,
      selected_decisions: selectedDecisions,
      included_packets: includedPackets,
      notes_text: notesText,
      implementation_prompt: renderImplementationPrompt({
        request_packet: requestPacket,
        review_board: reviewBoard,
        ledger_events: ledgerEvents,
        selected_decisions: selectedDecisions,
        included_packets: includedPackets,
        notes_text: notesText,
      }),
      safety_summary: renderSafetySummary({
        request_packet: requestPacket,
        review_board: reviewBoard,
        ledger_events: ledgerEvents,
        selected_decisions: selectedDecisions,
        included_packets: includedPackets,
        notes_text: notesText,
      }),
      acceptance_checklist: renderAcceptanceChecklist({
        request_packet: requestPacket,
        review_board: reviewBoard,
        ledger_events: ledgerEvents,
        selected_decisions: selectedDecisions,
        included_packets: includedPackets,
        notes_text: notesText,
      }),
      rollback_notes: renderRollbackNotes({
        request_packet: requestPacket,
        review_board: reviewBoard,
        ledger_events: ledgerEvents,
        selected_decisions: selectedDecisions,
        included_packets: includedPackets,
        notes_text: notesText,
      }),
      full_markdown: renderFullMarkdown({
        handoff_id: meta.handoff_id,
        generated_at: meta.generated_at,
        request_packet: requestPacket,
        review_board: reviewBoard,
        ledger_events: ledgerEvents,
        selected_decisions: selectedDecisions,
        included_packets: includedPackets,
        notes_text: notesText,
      }),
      request_summary_items: [
        { label: "Request ID", value: requestPacket ? requestPacket.request_id : "UNASSIGNED" },
        { label: "Current State", value: requestPacket ? requestPacket.current_state : "none" },
        { label: "Workflow Type", value: requestPacket ? requestPacket.workflow_type : "unspecified" },
        { label: "Risk Label", value: requestPacket ? requestPacket.risk_label : "NOT CLASSIFIED" },
      ],
      ledger_summary_items: [
        { label: "Review Board Packets", value: String(reviewBoard.length) },
        { label: "Ledger Events", value: String(ledgerEvents.length) },
        { label: "Selected Decisions", value: selectedDecisions.length ? selectedDecisions.join(", ") : "none" },
        { label: "Included Packets", value: String(includedPackets.length) },
      ],
    };
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p5d("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p5d(buttonId);
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      var snapshot = renderSnapshot();
      var text = getter(snapshot);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function composeHandoffFrom5c() {
    var snapshot = renderSnapshot();
    if (!snapshot) {
      var status = p5d("copy-status");
      if (status) status.textContent = "Phase 5D: Add a request packet, review packet, or notes first.";
      return;
    }
    handoffMeta = {
      handoff_id: "HANDOFF-" + generateId().toUpperCase(),
      generated_at: timestamp(),
    };
    updateHandoffUI();
    var status = p5d("copy-status");
    if (status) status.textContent = "Phase 5D: Handoff composed locally.";
  }

  function parsePastedHandoff() {
    var textarea = p5d("phase5d-pasted-json");
    if (!textarea || !textarea.value.trim()) {
      var status = p5d("copy-status");
      if (status) status.textContent = "Phase 5D: Paste handoff JSON first.";
      return;
    }
    try {
      var parsed = JSON.parse(textarea.value.trim());
      if (!parsed.handoff_id && !parsed.packets) {
        var status = p5d("copy-status");
        if (status) status.textContent = "Phase 5D: Pasted JSON has no handoff_id or packets.";
        return;
      }
      handoffMeta = {
        handoff_id: parsed.handoff_id || "HANDOFF-" + generateId().toUpperCase(),
        generated_at: parsed.generated_at || timestamp(),
      };
      handoffNotes = parsed.notes || parsed.local_notes || "";
      var notesField = p5d("phase5d-handoff-notes");
      if (notesField) {
        notesField.value = handoffNotes;
      }
      updateHandoffUI();
      textarea.value = "";
      var status = p5d("copy-status");
      if (status) status.textContent = "Phase 5D: Pasted handoff parsed locally.";
    } catch (e) {
      var status = p5d("copy-status");
      if (status) status.textContent = "Phase 5D: Invalid JSON — " + e.message;
    }
  }

  function clearHandoff() {
    handoffMeta = null;
    handoffNotes = "";
    var notesField = p5d("phase5d-handoff-notes");
    if (notesField) {
      notesField.value = "";
    }
    var pasted = p5d("phase5d-pasted-json");
    if (pasted) {
      pasted.value = "";
    }
    updateHandoffUI();
    var status = p5d("copy-status");
    if (status) status.textContent = "Phase 5D: Handoff cleared.";
  }

  function updateSourcePanels(snapshot) {
    var requestSummary = p5d("phase5d-request-summary");
    var ledgerSummary = p5d("phase5d-ledger-summary");
    var requestPreview = p5d("phase5d-request-preview");
    var notesPreview = p5d("phase5d-handoff-notes-preview");
    var compositionBody = p5d("phase5d-composition-body");

    if (requestSummary) {
      requestSummary.innerHTML = snapshot ? statHTML(snapshot.request_summary_items, "No current request packet yet") : statHTML(null, "No current request packet yet");
    }
    if (ledgerSummary) {
      ledgerSummary.innerHTML = snapshot ? statHTML(snapshot.ledger_summary_items, "No review ledger yet") : statHTML(null, "No review ledger yet");
    }
    if (requestPreview) {
      requestPreview.textContent = snapshot ? renderRequestPreview(snapshot.request_packet) : "No current request packet drafted yet.\nPopulate Phase 5A to enrich the handoff.";
    }
    if (notesPreview) {
      notesPreview.textContent = snapshot && snapshot.notes_text ? snapshot.notes_text : "No notes captured yet.";
    }
    if (compositionBody) {
      compositionBody.innerHTML = snapshot ? renderRequestTable(snapshot) : '<tr><td colspan="6" class="empty">No handoff composed yet. Use Phase 5C decisions to compose a handoff.</td></tr>';
    }
  }

  function updatePreviewBlocks(snapshot) {
    var implementationPreview = p5d("phase5d-implementation-prompt-preview");
    var safetyPreview = p5d("phase5d-safety-summary-preview");
    var acceptancePreview = p5d("phase5d-acceptance-checklist-preview");
    var rollbackPreview = p5d("phase5d-rollback-notes-preview");
    var fullPreview = p5d("phase5d-full-markdown-preview");
    var meta = snapshot || {
      request_packet: null,
      review_board: [],
      ledger_events: [],
      selected_decisions: [],
      included_packets: [],
      notes_text: "",
      implementation_prompt: "No handoff generated yet.",
      safety_summary: "No handoff generated yet.",
      acceptance_checklist: "No handoff generated yet.",
      rollback_notes: "No handoff generated yet.",
      full_markdown: "No handoff generated yet.",
    };

    if (implementationPreview) {
      implementationPreview.textContent = meta.implementation_prompt || "No handoff generated yet.";
    }
    if (safetyPreview) {
      safetyPreview.textContent = meta.safety_summary || "No handoff generated yet.";
    }
    if (acceptancePreview) {
      acceptancePreview.textContent = meta.acceptance_checklist || "No handoff generated yet.";
    }
    if (rollbackPreview) {
      rollbackPreview.textContent = meta.rollback_notes || "No handoff generated yet.";
    }
    if (fullPreview) {
      fullPreview.textContent = meta.full_markdown || "No handoff generated yet.";
    }
  }

  function updateHandoffUI() {
    var snapshot = renderSnapshot();
    updateSourcePanels(snapshot);
    updatePreviewBlocks(snapshot);
  }

  function initPhase5d() {
    var shell = document.querySelector("[data-phase5d-handoff]");
    if (!shell) {
      return;
    }

    var composeBtn = p5d("phase5d-compose-handoff");
    if (composeBtn) {
      composeBtn.addEventListener("click", composeHandoffFrom5c);
    }

    var clearBtn = p5d("phase5d-clear-handoff");
    if (clearBtn) {
      clearBtn.addEventListener("click", clearHandoff);
    }

    var parseBtn = p5d("phase5d-parse-pasted-handoff");
    if (parseBtn) {
      parseBtn.addEventListener("click", parsePastedHandoff);
    }

    var notesField = p5d("phase5d-handoff-notes");
    if (notesField) {
      notesField.addEventListener("input", function () {
        handoffNotes = notesField.value || "";
        updateHandoffUI();
      });
    }

    var decisionFilterInputs = document.querySelectorAll("#phase5d-decision-filters input[type='checkbox']");
    decisionFilterInputs.forEach(function (input) {
      input.addEventListener("change", updateHandoffUI);
    });

    bindCopyButton("phase5d-copy-implementation-prompt", function (snapshot) {
      return snapshot ? snapshot.implementation_prompt : "";
    }, "Phase 5D: Compose a handoff first.", "Phase 5D: Implementation prompt copied.");

    bindCopyButton("phase5d-copy-safety-summary", function (snapshot) {
      return snapshot ? snapshot.safety_summary : "";
    }, "Phase 5D: Compose a handoff first.", "Phase 5D: Safety summary copied.");

    bindCopyButton("phase5d-copy-acceptance-checklist", function (snapshot) {
      return snapshot ? snapshot.acceptance_checklist : "";
    }, "Phase 5D: Compose a handoff first.", "Phase 5D: Acceptance checklist copied.");

    bindCopyButton("phase5d-copy-rollback-notes", function (snapshot) {
      return snapshot ? snapshot.rollback_notes : "";
    }, "Phase 5D: Compose a handoff first.", "Phase 5D: Rollback notes copied.");

    bindCopyButton("phase5d-copy-full-handoff-markdown", function (snapshot) {
      return snapshot ? snapshot.full_markdown : "";
    }, "Phase 5D: Compose a handoff first.", "Phase 5D: Full handoff Markdown copied.");

    updateHandoffUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPhase5d);
  } else {
    initPhase5d();
  }
})();

(function () {
  var plus2aState = {
    model: null,
  };

  function p2a(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p2a("dashboard-data");
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (e) {
      return {};
    }
  }

  function getModel() {
    var dashboardData = readDashboardData();
    var model = plus2aState.model || dashboardData.original_plus2a_auth_foundation_model || null;
    plus2aState.model = model;
    return model;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function badgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "true" || value === "yes" || value === "ready_for_demo_only" || value === "read_only_auth_foundation" || value === "ready_for_auth_foundation_review_only") {
      return "pass";
    }
    if (value === "false" || value === "no" || value === "missing" || value === "not_ready_for_real_automation") {
      return "locked";
    }
    return "info";
  }

  function buildRows(items, renderer, emptyText) {
    if (!items || !items.length) return emptyText;
    return items.map(function (item) {
      return "<tr>" + renderer(item) + "</tr>";
    }).join("");
  }

  function boolValue(value) {
    return value ? "true" : "false";
  }

  function buildStatusRows(model) {
    if (!model || !model.auth_status_model) return '<tr><td colspan="2" class="empty">No status loaded yet.</td></tr>';
    var status = model.auth_status_model;
    var rows = [
      ["Auth Foundation Status", status.auth_foundation_status],
      ["Live Auth Enabled", boolValue(status.live_auth_enabled)],
      ["External Provider Enabled", boolValue(status.external_provider_enabled)],
      ["Session Persistence Enabled", boolValue(status.session_persistence_enabled)],
      ["Cookie Auth Enabled", boolValue(status.cookie_auth_enabled)],
      ["Token Auth Enabled", boolValue(status.token_auth_enabled)],
      ["Real User Database Enabled", boolValue(status.real_user_database_enabled)],
      ["Current Mode", status.current_mode],
    ];
    return rows.map(function(row) {
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + badgeClass(row[1]) + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildIdentityRows(model) {
    return buildRows(model && model.demo_identity_model, function(item) {
      return [
        '<th scope="row"><code>' + escapeHtml(item.user_id) + '</code></th>',
        '<td>' + escapeHtml(item.display_name) + '</td>',
        '<td>' + escapeHtml(item.role) + '</td>',
        '<td><span class="badge ' + badgeClass(item.auth_mode === "DEMO_DETERMINISTIC" ? "pass" : "info") + '">' + escapeHtml(item.auth_mode) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="4" class="empty">No demo identities loaded yet.</td></tr>');
  }

  function buildRoleRows(model) {
    if (!model || !model.role_model) return '<tr><td colspan="3" class="empty">No roles loaded yet.</td></tr>';
    var roles = model.role_model;
    var rows = [];
    for (var key in roles) {
      if (roles.hasOwnProperty(key)) {
        var role = roles[key];
        rows.push([
          '<th scope="row"><code>' + escapeHtml(key) + '</code></th>',
          '<td>' + escapeHtml((role.permissions || []).join(", ")) + '</td>',
          '<td><span class="badge ' + badgeClass(role.future_auth_required) + '">' + escapeHtml(boolValue(role.future_auth_required)) + '</span></td>',
        ].join(""));
      }
    }
    if (!rows.length) return '<tr><td colspan="3" class="empty">No roles loaded yet.</td></tr>';
    return "<tr>" + rows.join("</tr><tr>") + "</tr>";
  }

  function buildForbiddenRows(model) {
    var forbidden = model && model.forbidden_permission_boundary ? model.forbidden_permission_boundary : [];
    if (!forbidden.length) return '<li>No boundaries loaded yet.</li>';
    return forbidden.map(function(item) {
      return '<li>' + escapeHtml(item) + '</li>';
    }).join("");
  }

  function buildDependencyRows(model) {
    return buildRows(model && model.future_auth_dependencies, function(item) {
      return [
        '<th scope="row">' + escapeHtml(item.item) + '</th>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr>');
  }

  function updateIdentitySelect(model) {
    var select = p2a("plus2a-identity-select");
    if (!select) return;
    var identities = model && model.demo_identity_model ? model.demo_identity_model : [];
    if (!identities.length) {
      select.innerHTML = '<option value="">No identities loaded yet.</option>';
      return;
    }
    select.innerHTML = identities.map(function(item) {
       return '<option value="' + escapeHtml(item.user_id) + '">' + escapeHtml(item.display_name + " (" + item.role + ")") + '</option>';
    }).join("");
  }
  
  function checkPermissionLocal(model, userId, permission) {
    if (!model) return { allowed: false, reason: "Model not loaded.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
    var forbidden = model.forbidden_permission_boundary || [];
    if (forbidden.indexOf(permission) !== -1) {
       return { allowed: false, reason: "Permission is globally forbidden.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
    }
    var identities = model.demo_identity_model || [];
    var identity = null;
    for (var i = 0; i < identities.length; i++) {
       if (identities[i].user_id === userId) {
          identity = identities[i];
          break;
       }
    }
    if (!identity) return { allowed: false, reason: "Identity not found.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
    var roles = model.role_model || {};
    var role = roles[identity.role];
    if (!role) return { allowed: false, reason: "Role not found.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
    var permissions = role.permissions || [];
    if (permissions.indexOf(permission) !== -1) {
       return { allowed: true, reason: "Permission granted.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
    }
    return { allowed: false, reason: "Permission not found for role.", current_mode: "READ_ONLY_AUTH_FOUNDATION" };
  }

  function updatePermissionCheck(model) {
    var resultDiv = p2a("plus2a-check-result");
    var identitySelect = p2a("plus2a-identity-select");
    var permissionSelect = p2a("plus2a-permission-select");
    if (!resultDiv || !identitySelect || !permissionSelect || !model) return;
    
    var userId = identitySelect.value;
    var permission = permissionSelect.value.split(" ")[0]; // remove " (forbidden)" if present
    
    if (!userId || !permission) {
       resultDiv.innerHTML = '<p class="muted">Select an identity and permission to preview.</p>';
       return;
    }
    
    var result = checkPermissionLocal(model, userId, permission);
    var badge = result.allowed ? '<span class="badge pass">ALLOWED</span>' : '<span class="badge locked">DENIED</span>';
    
    resultDiv.innerHTML = [
       '<p style="margin-bottom:0.5rem;"><strong>Result:</strong> ' + badge + '</p>',
       '<p style="margin-bottom:0.5rem;" class="muted"><strong>Reason:</strong> ' + escapeHtml(result.reason) + '</p>',
       '<p class="muted"><strong>Mode:</strong> <code>' + escapeHtml(result.current_mode) + '</code></p>'
    ].join("");
  }

  function updatePlus2AUI() {
    var model = getModel();
    var statusBody = p2a("plus2a-status-body");
    var identitiesBody = p2a("plus2a-identities-body");
    var roleBody = p2a("plus2a-role-body");
    var forbiddenList = p2a("plus2a-forbidden-list");
    var dependenciesBody = p2a("plus2a-dependencies-body");
    
    if (statusBody) statusBody.innerHTML = buildStatusRows(model);
    if (identitiesBody) identitiesBody.innerHTML = buildIdentityRows(model);
    if (roleBody) roleBody.innerHTML = buildRoleRows(model);
    if (forbiddenList) forbiddenList.innerHTML = buildForbiddenRows(model);
    if (dependenciesBody) dependenciesBody.innerHTML = buildDependencyRows(model);
    
    updateIdentitySelect(model);
    updatePermissionCheck(model);
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p2a("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p2a(buttonId);
    if (!button) return;
    button.addEventListener("click", function () {
      var model = getModel();
      var text = getter(model);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function initPlus2A() {
    var shell = document.querySelector("[data-plus2a-auth-foundation]");
    if (!shell) return;

    bindCopyButton("plus2a-copy-status", function(m) { return JSON.stringify(m && m.auth_status_model, null, 2); }, "No status loaded.", "Auth foundation status copied.");
    bindCopyButton("plus2a-copy-roles", function(m) { return JSON.stringify(m && m.role_model, null, 2); }, "No roles loaded.", "Role matrix copied.");
    bindCopyButton("plus2a-copy-boundary", function(m) { return JSON.stringify(m && m.forbidden_permission_boundary, null, 2); }, "No boundary loaded.", "Forbidden boundary copied.");
    bindCopyButton("plus2a-copy-dependencies", function(m) { return JSON.stringify(m && m.future_auth_dependencies, null, 2); }, "No dependencies loaded.", "Dependencies copied.");
    bindCopyButton("plus2a-copy-validation", function(m) { return "Requires: validate_original_plus2a_backend_auth_foundation.py\nRequires: validate_original_plus2a_backend_auth_foundation_e2e.py"; }, "Error", "Validation checklist copied.");

    var identitySelect = p2a("plus2a-identity-select");
    var permissionSelect = p2a("plus2a-permission-select");
    if (identitySelect) identitySelect.addEventListener("change", function() { updatePermissionCheck(getModel()); });
    if (permissionSelect) permissionSelect.addEventListener("change", function() { updatePermissionCheck(getModel()); });

    updatePlus2AUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus2A);
  } else {
    initPlus2A();
  }
})();

(function () {
  var plus2bState = {
    model: null,
  };

  function p2b(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p2b("dashboard-data");
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (e) {
      return {};
    }
  }

  function getModel() {
    var dashboardData = readDashboardData();
    var model = plus2bState.model || dashboardData.original_plus2b_request_storage_model || null;
    plus2bState.model = model;
    return model;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function badgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "true" || value === "yes" || value === "ready_for_foundation_review_only" || value === "storage_foundation_only" || value === "storage_contract_ready") {
      return "pass";
    }
    if (value === "false" || value === "no" || value === "missing" || value === "durable_storage_not_configured" || value === "not_ready_for_request_persistence" || value === "not_ready_for_real_automation" || value === "storage_not_configured") {
      return "locked";
    }
    return "info";
  }

  function buildRows(items, renderer, emptyText) {
    if (!items || !items.length) return emptyText;
    return items.map(function (item) {
      return "<tr>" + renderer(item) + "</tr>";
    }).join("");
  }

  function boolValue(value) {
    return value ? "true" : "false";
  }

  function buildStatusRows(model) {
    if (!model || !model.storage_readiness_model) return '<tr><td colspan="2" class="empty">No status loaded yet.</td></tr>';
    var status = model.storage_readiness_model;
    var rows = [
      ["Storage Foundation Status", status.storage_foundation_status],
      ["Durable Storage Configured", boolValue(status.durable_storage_configured)],
      ["Write Endpoint Enabled", boolValue(status.write_endpoint_enabled)],
      ["Persistence Verified", boolValue(status.persistence_verified)],
      ["Env Required", boolValue(status.env_required)],
      ["Secrets Required", boolValue(status.secrets_required)],
      ["Current Mode", status.current_mode],
    ];
    return rows.map(function(row) {
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + badgeClass(row[1]) + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildLifecycleRows(model) {
    if (!model || !model.request_lifecycle_state_model) return '<tr><td colspan="2" class="empty">No lifecycle model loaded yet.</td></tr>';
    var lcm = model.request_lifecycle_state_model;
    var rows = [
      ["Allowed States", (lcm.allowed_states || []).join(", ")],
      ["Forbidden Current States", (lcm.forbidden_states || []).join(", ")]
    ];
    return rows.map(function(row) {
       var cls = row[0].indexOf("Forbidden") !== -1 ? "locked" : "pass";
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + cls + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildAdapterMethods(model) {
    var methods = model && model.storage_adapter_contract ? model.storage_adapter_contract.methods : [];
    if (!methods || !methods.length) return '<li>No methods loaded yet.</li>';
    return methods.map(function(m) {
      return '<li><code>' + escapeHtml(m) + '</code></li>';
    }).join("");
  }

  function buildDependencyRows(model) {
    return buildRows(model && model.future_storage_dependencies, function(item) {
      return [
        '<th scope="row">' + escapeHtml(item.item) + '</th>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr>');
  }

  function validateRequestLocal(model, title, intent) {
     if (!title || title.length < 5) return { valid: false, error: "Title too short (min 5 chars)." };
     if (!intent || intent.length < 10) return { valid: false, error: "Intent too short (min 10 chars)." };
     
     var lowerIntent = intent.toLowerCase();
     var forbidden = ["execute", "mutate", "deploy", "merge", "push", "delete"];
     for (var i = 0; i < forbidden.length; i++) {
        if (lowerIntent.indexOf(forbidden[i]) !== -1) {
           return { valid: false, error: "Forbidden intent keyword: " + forbidden[i] };
        }
     }
     return { valid: True };
  }

  function updateValidationPreview(model) {
    var resultDiv = p2b("plus2b-validation-result");
    var titleInput = p2b("plus2b-test-title");
    var intentInput = p2b("plus2b-test-intent");
    if (!resultDiv || !titleInput || !intentInput) return;
    
    var title = titleInput.value;
    var intent = intentInput.value;
    
    if (!title && !intent) {
       resultDiv.innerHTML = '<p class="muted">Enter a request title and intent to validate.</p>';
       return;
    }
    
    var res = validateRequestLocal(model, title, intent);
    var badge = res.valid ? '<span class="badge pass">VALID</span>' : '<span class="badge locked">INVALID</span>';
    var error = res.error ? '<p class="muted" style="margin-top:0.5rem;"><strong>Error:</strong> ' + escapeHtml(res.error) + '</p>' : '';
    
    resultDiv.innerHTML = '<p><strong>Result:</strong> ' + badge + '</p>' + error;
  }

  function updatePlus2BUI() {
    var model = getModel();
    var statusBody = p2b("plus2b-status-body");
    var schemaPreview = p2b("plus2b-schema-preview");
    var lifecycleBody = p2b("plus2b-lifecycle-body");
    var adapterMethods = p2b("plus2b-adapter-methods");
    var dependenciesBody = p2b("plus2b-dependencies-body");
    
    if (statusBody) statusBody.innerHTML = buildStatusRows(model);
    if (schemaPreview && model) schemaPreview.textContent = JSON.stringify(model.request_draft_schema, null, 2);
    if (lifecycleBody) lifecycleBody.innerHTML = buildLifecycleRows(model);
    if (adapterMethods) adapterMethods.innerHTML = buildAdapterMethods(model);
    if (dependenciesBody) dependenciesBody.innerHTML = buildDependencyRows(model);
    
    updateValidationPreview(model);
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p2b("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p2b(buttonId);
    if (!button) return;
    button.addEventListener("click", function () {
      var model = getModel();
      var text = getter(model);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function initPlus2B() {
    var shell = document.querySelector("[data-plus2b-request-storage]");
    if (!shell) return;

    bindCopyButton("plus2b-copy-schema", function(m) { return JSON.stringify(m && m.request_draft_schema, null, 2); }, "No schema loaded.", "Schema copied.");
    bindCopyButton("plus2b-copy-lifecycle", function(m) { return JSON.stringify(m && m.request_lifecycle_state_model, null, 2); }, "No model loaded.", "Lifecycle model copied.");
    bindCopyButton("plus2b-copy-adapter", function(m) { return JSON.stringify(m && m.storage_adapter_contract, null, 2); }, "No contract loaded.", "Contract copied.");
    bindCopyButton("plus2b-copy-disabled", function(m) { return "DURABLE_STORAGE_NOT_CONFIGURED"; }, "Error", "Boundary report copied.");
    bindCopyButton("plus2b-copy-dependencies", function(m) { return JSON.stringify(m && m.future_storage_dependencies, null, 2); }, "No dependencies loaded.", "Dependencies copied.");
    bindCopyButton("plus2b-copy-validation", function(m) { return "Requires: validate_original_plus2b_persistent_request_storage.py\nRequires: validate_original_plus2b_persistent_request_storage_e2e.py"; }, "Error", "Validation checklist copied.");

    var titleInput = p2b("plus2b-test-title");
    var intentInput = p2b("plus2b-test-intent");
    if (titleInput) titleInput.addEventListener("input", function() { updateValidationPreview(getModel()); });
    if (intentInput) intentInput.addEventListener("input", function() { updateValidationPreview(getModel()); });

    updatePlus2BUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus2B);
  } else {
    initPlus2B();
  }
})();

(function () {
  var plus2cState = {
    model: null,
  };

  function p2c(id) {
    return document.getElementById(id);
  }

  function readDashboardData() {
    var node = p2c("dashboard-data");
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (e) {
      return {};
    }
  }

  function getModel() {
    var dashboardData = readDashboardData();
    var model = plus2cState.model || dashboardData.original_plus2c_audit_log_model || null;
    plus2cState.model = model;
    return model;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function badgeClass(status) {
    var value = String(status || "").toLowerCase();
    if (value === "true" || value === "yes" || value === "ready_for_foundation_review_only" || value === "audit_foundation_only" || value === "audit_contract_ready") {
      return "pass";
    }
    if (value === "false" || value === "no" || value === "missing" || value === "durable_audit_storage_not_configured" || value === "not_ready_for_audit_persistence" || value === "not_ready_for_real_automation" || value === "audit_storage_not_configured" || value === "no_durable_chain_configured") {
      return "locked";
    }
    return "info";
  }

  function buildRows(items, renderer, emptyText) {
    if (!items || !items.length) return emptyText;
    return items.map(function (item) {
      return "<tr>" + renderer(item) + "</tr>";
    }).join("");
  }

  function boolValue(value) {
    return value ? "true" : "false";
  }

  function buildStatusRows(model) {
    if (!model || !model.audit_readiness_model) return '<tr><td colspan="2" class="empty">No status loaded yet.</td></tr>';
    var status = model.audit_readiness_model;
    var rows = [
      ["Audit Foundation Status", status.audit_foundation_status],
      ["Durable Audit Storage Configured", boolValue(status.durable_audit_storage_configured)],
      ["Append Endpoint Enabled", boolValue(status.append_endpoint_enabled)],
      ["Immutable Chain Verified", boolValue(status.immutable_chain_verified)],
      ["Persistence Verified", boolValue(status.persistence_verified)],
      ["Hash Algorithm", status.hash_algorithm],
      ["Current Mode", status.current_mode],
    ];
    return rows.map(function(row) {
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + badgeClass(row[1]) + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildCategoryRows(model) {
    if (!model || !model.audit_event_categories) return '<tr><td colspan="2" class="empty">No categories loaded yet.</td></tr>';
    var cats = model.audit_event_categories;
    var rows = [
      ["Allowed Categories", (cats.allowed || []).join(", ")],
      ["Forbidden Categories", (cats.forbidden || []).join(", ")]
    ];
    return rows.map(function(row) {
       var cls = row[0].indexOf("Forbidden") !== -1 ? "locked" : "pass";
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + cls + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildChainRows(model) {
    if (!model || !model.immutable_hash_chain_contract) return '<tr><td colspan="2" class="empty">No contract loaded yet.</td></tr>';
    var contract = model.immutable_hash_chain_contract;
    var rows = [
      ["Hash Algorithm", contract.hash_algorithm],
      ["Canonical Serialization", contract.canonical_serialization],
      ["Integrity Fields", (contract.integrity_fields || []).join(", ")],
      ["Tamper Detection", contract.tamper_detection],
    ];
    return rows.map(function(row) {
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td>" + escapeHtml(row[1]) + "</td></tr>";
    }).join("");
  }

  function buildAdapterMethods(model) {
    var methods = model && model.audit_adapter_contract ? model.audit_adapter_contract.methods : [];
    if (!methods || !methods.length) return '<li>No methods loaded yet.</li>';
    return methods.map(function(m) {
      return '<li><code>' + escapeHtml(m) + '</code></li>';
    }).join("");
  }

  function buildPolicyRows(model) {
    if (!model || !model.retention_redaction_policy) return '<tr><td colspan="2" class="empty">No policy loaded yet.</td></tr>';
    var policy = model.retention_redaction_policy;
    var rows = [
      ["Retention Class", policy.retention_class],
      ["Redaction Allowed", boolValue(policy.redaction_allowed_for_payload_summary)],
      ["Immutable Core Fields", boolValue(policy.immutable_core_fields)],
      ["PII Policy", policy.pii_policy],
      ["Secret Redaction Required", boolValue(policy.secret_redaction_required)],
      ["Token Redaction Required", boolValue(policy.token_redaction_required)],
      ["No Secret Storage", boolValue(policy.no_secret_storage)],
    ];
    return rows.map(function(row) {
       return "<tr><th scope=\"row\">" + escapeHtml(row[0]) + "</th><td><span class=\"badge " + badgeClass(row[1]) + "\">" + escapeHtml(row[1]) + "</span></td></tr>";
    }).join("");
  }

  function buildDependencyRows(model) {
    return buildRows(model && model.future_audit_dependencies, function(item) {
      return [
        '<th scope="row">' + escapeHtml(item.item) + '</th>',
        '<td><span class="badge ' + badgeClass(item.status) + '">' + escapeHtml(item.status) + '</span></td>',
      ].join("");
    }, '<tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr>');
  }

  function validateCategoryLocal(model, category) {
     if (!category) return { valid: false, error: "No category selected." };
     var cats = model.audit_event_categories || {};
     var allowed = cats.allowed || [];
     var forbidden = cats.forbidden || [];
     
     if (forbidden.indexOf(category) !== -1) {
        return { valid: false, error: "Forbidden category for current phase: " + category };
     }
     if (allowed.indexOf(category) !== -1) {
        return { valid: true };
     }
     return { valid: false, error: "Unknown category: " + category };
  }

  function updateValidationPreview(model) {
    var resultDiv = p2c("plus2c-validation-result");
    var categorySelect = p2c("plus2c-test-category");
    if (!resultDiv || !categorySelect || !model) return;
    
    var category = categorySelect.value;
    
    if (!category) {
       resultDiv.innerHTML = '<p class="muted">Select an event category to validate.</p>';
       return;
    }
    
    var res = validateCategoryLocal(model, category);
    var badge = res.valid ? '<span class="badge pass">VALID</span>' : '<span class="badge locked">INVALID</span>';
    var error = res.error ? '<p class="muted" style="margin-top:0.5rem;"><strong>Error:</strong> ' + escapeHtml(res.error) + '</p>' : '';
    
    resultDiv.innerHTML = '<p><strong>Result:</strong> ' + badge + '</p>' + error;
  }

  function updateCategorySelect(model) {
    var select = p2c("plus2c-test-category");
    if (!select || !model) return;
    var cats = model.audit_event_categories || {};
    var all = (cats.allowed || []).concat(cats.forbidden || []);
    if (!all.length) {
      select.innerHTML = '<option value="">No categories loaded yet.</option>';
      return;
    }
    var current = select.value;
    select.innerHTML = '<option value="">Select category...</option>' + all.map(function(item) {
       var label = item + (cats.forbidden.indexOf(item) !== -1 ? " (forbidden)" : "");
       return '<option value="' + escapeHtml(item) + '">' + escapeHtml(label) + '</option>';
    }).join("");
    select.value = current;
  }

  function updatePlus2CUI() {
    var model = getModel();
    var statusBody = p2c("plus2c-status-body");
    var schemaPreview = p2c("plus2c-schema-preview");
    var categoryBody = p2c("plus2c-category-body");
    var chainBody = p2c("plus2c-chain-body");
    var adapterMethods = p2c("plus2c-adapter-methods");
    var policyBody = p2c("plus2c-policy-body");
    var dependenciesBody = p2c("plus2c-dependencies-body");
    
    if (statusBody) statusBody.innerHTML = buildStatusRows(model);
    if (schemaPreview && model) schemaPreview.textContent = JSON.stringify(model.audit_event_schema, null, 2);
    if (categoryBody) categoryBody.innerHTML = buildCategoryRows(model);
    if (chainBody) chainBody.innerHTML = buildChainRows(model);
    if (adapterMethods) adapterMethods.innerHTML = buildAdapterMethods(model);
    if (policyBody) policyBody.innerHTML = buildPolicyRows(model);
    if (dependenciesBody) dependenciesBody.innerHTML = buildDependencyRows(model);
    
    updateCategorySelect(model);
    updateValidationPreview(model);
  }

  function copyRenderedText(text, emptyMessage, successMessage) {
    var status = p2c("copy-status");
    if (!text) {
      if (status) status.textContent = emptyMessage;
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        if (status) status.textContent = successMessage;
      }).catch(function () {});
      return;
    }
    var field = document.createElement("textarea");
    field.value = text;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    document.body.removeChild(field);
    if (status) status.textContent = successMessage;
  }

  function bindCopyButton(buttonId, getter, emptyMessage, successMessage) {
    var button = p2c(buttonId);
    if (!button) return;
    button.addEventListener("click", function () {
      var model = getModel();
      var text = getter(model);
      copyRenderedText(text, emptyMessage, successMessage);
    });
  }

  function initPlus2C() {
    var shell = document.querySelector("[data-plus2c-audit-log]");
    if (!shell) return;

    bindCopyButton("plus2c-copy-schema", function(m) { return JSON.stringify(m && m.audit_event_schema, null, 2); }, "No schema loaded.", "Schema copied.");
    bindCopyButton("plus2c-copy-chain", function(m) { return JSON.stringify(m && m.immutable_hash_chain_contract, null, 2); }, "No contract loaded.", "Contract copied.");
    bindCopyButton("plus2c-copy-adapter", function(m) { return JSON.stringify(m && m.audit_adapter_contract, null, 2); }, "No adapter loaded.", "Adapter copied.");
    bindCopyButton("plus2c-copy-disabled", function(m) { return "AUDIT_STORAGE_NOT_CONFIGURED"; }, "Error", "Boundary report copied.");
    bindCopyButton("plus2c-copy-policy", function(m) { return JSON.stringify(m && m.retention_redaction_policy, null, 2); }, "No policy loaded.", "Policy copied.");
    bindCopyButton("plus2c-copy-dependencies", function(m) { return JSON.stringify(m && m.future_audit_dependencies, null, 2); }, "No dependencies loaded.", "Dependencies copied.");
    bindCopyButton("plus2c-copy-validation", function(m) { return "Requires: validate_original_plus2c_immutable_audit_log.py\nRequires: validate_original_plus2c_immutable_audit_log_e2e.py"; }, "Error", "Validation checklist copied.");

    var categorySelect = p2c("plus2c-test-category");
    if (categorySelect) categorySelect.addEventListener("change", function() { updateValidationPreview(getModel()); });

    updatePlus2CUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlus2C);
  } else {
    initPlus2C();
  }
})();
