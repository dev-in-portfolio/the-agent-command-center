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
    installKeyboardShortcut();
    applyFilters();
    setStatus("Local UI ready.", "info");
  }

  init();
})();
