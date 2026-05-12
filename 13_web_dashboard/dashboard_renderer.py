import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "templates" / "index_template.html"


def _e(value):
    return html.escape("" if value is None else str(value))


def _badge(label, css_class):
    return f'<span class="badge {css_class}">{_e(label)}</span>'


def _status_badge(status):
    normalized = (status or "unknown").upper()
    css_class = {
        "PASS": "pass",
        "WARNING": "warning",
        "FAIL": "fail",
        "LOCKED": "locked",
        "DISABLED": "disabled",
        "INFO": "info",
        "UNKNOWN": "unknown",
    }.get(normalized, "unknown")
    return _badge(normalized, css_class)


def _bool_badge(flag):
    return _status_badge("PASS" if flag else "DISABLED")


def _category_badge(category):
    normalized = (category or "unknown").lower()
    mapping = {
        "safe": ("SAFE", "pass"),
        "controlled": ("CONTROLLED", "warning"),
        "locked": ("LOCKED", "locked"),
    }
    label, css_class = mapping.get(normalized, (normalized.upper(), "unknown"))
    return _badge(label, css_class)


def _risk_badge(risk_level):
    normalized = (risk_level or "unknown").lower()
    mapping = {
        "none": ("NONE", "pass"),
        "low": ("LOW", "pass"),
        "medium": ("MEDIUM", "warning"),
        "high": ("HIGH", "fail"),
        "locked": ("LOCKED", "locked"),
    }
    label, css_class = mapping.get(normalized, (normalized.upper(), "unknown"))
    return _badge(label, css_class)


def _confidence_badge(confidence):
    normalized = (confidence or "unknown").lower()
    mapping = {
        "direct_module_read": ("DIRECT", "info"),
        "report_derived": ("REPORT", "pass"),
        "file_existence_check": ("EXISTS", "warning"),
        "generated_static_snapshot": ("GENERATED", "info"),
        "unknown": ("UNKNOWN", "unknown"),
    }
    label, css_class = mapping.get(normalized, (normalized.upper(), "unknown"))
    return _badge(label, css_class)


def _card(title, status, body, extra=None):
    extra_html = f"<div class=\"card-extra\">{extra}</div>" if extra else ""
    return f"""
    <article class="card">
      <div class="card-head">
        <h3 class="card-title">{_e(title)}</h3>
        {_status_badge(status)}
      </div>
      <p class="card-body">{_e(body)}</p>
      {extra_html}
    </article>
    """


def _details(title, body_html, group, open_by_default=True, panel_id=None):
    open_attr = " open" if open_by_default else ""
    panel_attr = f' id="{_e(panel_id)}"' if panel_id else ""
    return f"""
    <details class="panel" data-section-group="{_e(group)}"{open_attr}{panel_attr}>
      <summary>{_e(title)}</summary>
      <div class="panel-body">
        {body_html}
      </div>
    </details>
    """


def _stat(label, value, badge=None):
    badge_html = f"<span class=\"mini-status\">{badge}</span>" if badge else ""
    return f"""
    <div class="stat">
      <span>{_e(label)}</span>
      <strong>{_e(value)}</strong>
      {badge_html}
    </div>
    """


def _table(headers, rows, table_id, caption, empty_message="No data available."):
    body_rows = "".join(rows) if rows else f'<tr><td colspan="{len(headers)}" class="empty">{_e(empty_message)}</td></tr>'
    return f"""
    <div class="table-wrap">
      <table class="data-table" id="{_e(table_id)}" data-table-id="{_e(table_id)}">
        <caption>{_e(caption)}</caption>
        <thead>
          <tr>{''.join(f'<th scope="col">{_e(h)}</th>' for h in headers)}</tr>
        </thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
    """


def _copy_button(label, text, aria=None, kind="copy-button"):
    aria_label = aria or label
    return f'<button type="button" class="{kind}" data-copy-text="{_e(text)}" aria-label="{_e(aria_label)}">{_e(label)}</button>'


def _toolbar_button(label, action, target="all", state="open", kind="toggle-button"):
    return (
        f'<button type="button" class="{kind}" '
        f'data-panel-action="{_e(action)}" '
        f'data-panel-target="{_e(target)}" '
        f'data-panel-state="{_e(state)}">'
        f'{_e(label)}</button>'
    )


def _open_section_button(label, panel_id):
    return (
        f'<button type="button" class="section-button" '
        f'data-open-panel="{_e(panel_id)}" '
        f'aria-controls="{_e(panel_id)}">'
        f'{_e(label)}</button>'
    )


def _list(items):
    if not items:
        return '<p class="muted">None detected.</p>'
    return '<ul class="compact-list">' + "".join(f"<li>{_e(item)}</li>" for item in items) + "</ul>"


def _build_safety_boundary(snapshot):
    rows = []
    for label, value in [
        ("Official repo", "LOCKED"),
        ("Repo 2", "LOCKED"),
        ("Repo 3", "LOCKED"),
        ("Deployment", "DISABLED"),
        ("Secrets", "DISABLED"),
        ("Credentials", "DISABLED"),
        ("Command packet execution", "DISABLED"),
        ("Free-form shell", "DISABLED"),
        ("Merge", "DISABLED"),
        ("Push", "DISABLED"),
        ("PR creation", "DISABLED"),
        ("Network behavior", "DISABLED"),
        ("API server", "DISABLED"),
        ("Hosted app", "DISABLED"),
    ]:
        rows.append(f"<tr><th scope=\"row\">{_e(label)}</th><td>{_status_badge(value)}</td></tr>")
    return _table(
        ["Boundary", "State"],
        rows,
        "safety-boundary-table",
        "Safety boundary states",
    )


def _build_action_rows(actions):
    rows = []
    for action in actions:
        rows.append(
            "<tr "
            f'data-action-category="{_e(action["category"])}" '
            f'data-action-risk="{_e(action["risk_level"])}" '
            f'data-action-dashboard-allowed="{str(bool(action["dashboard_allowed"])).lower()}" '
            f'data-search-text="{_e(" ".join([action["action_id"], action["label"], action["category"], action["risk_level"], action["reason"]]))}"'
            ">"
            f"<th scope=\"row\"><code>{_e(action['action_id'])}</code></th>"
            f"<td>{_e(action['label'])}</td>"
            f"<td>{_category_badge(action['category'])}</td>"
            f"<td>{_risk_badge(action['risk_level'])}</td>"
            f"<td>{'Yes' if action['writes_files'] else 'No'}</td>"
            f"<td>{'Yes' if action['runs_commands'] else 'No'}</td>"
            f"<td>{_bool_badge(action['dashboard_allowed'])}</td>"
            f"<td>{_e(action['reason'])}</td>"
            "</tr>"
        )
    return rows


def _build_artifact_rows(packages):
    rows = []
    for pkg in packages:
        row_state = "PASS" if pkg["exists"] and pkg["warnings_count"] == 0 and pkg["missing_expected_files_count"] == 0 else "WARNING"
        if not pkg["exists"]:
            row_state = "FAIL"
        rows.append(
            "<tr "
            f'data-package-exists="{str(bool(pkg["exists"])).lower()}" '
            f'data-package-warnings="{pkg["warnings_count"]}" '
            f'data-package-missing="{pkg["missing_expected_files_count"]}" '
            f'data-package-verdict="{_e(pkg["final_verdict"])}" '
            f'data-search-text="{_e(" ".join([pkg["package_id"], pkg["package_name"], pkg["final_verdict"], pkg["report_path"], " ".join(pkg.get("missing_expected_files", [])), " ".join(pkg.get("warnings", []))]))}"'
            ">"
            f"<th scope=\"row\"><code>{_e(pkg['package_id'])}</code></th>"
            f"<td>{_e(pkg['package_name'])}</td>"
            f"<td>{_status_badge('PASS' if pkg['exists'] else 'FAIL')}</td>"
            f"<td>{_status_badge(row_state)}</td>"
            f"<td>{_e(pkg['missing_expected_files_count'])}</td>"
            f"<td>{_e(pkg['zero_byte_count'])}</td>"
            f"<td>{_e(pkg['warnings_count'])}</td>"
            f"<td>{_e(pkg['report_path'])}</td>"
            "</tr>"
        )
    return rows


def _build_reports_rows(documents):
    rows = []
    for doc in documents:
        preview = doc.get("preview", "")
        title = doc["title"]
        report_path = doc["path"]
        rows.append(
            "<tr "
            f'data-document-category="{_e(doc["category"])}" '
            f'data-document-verdict="{_e(doc["detected_verdict"])}" '
            f'data-search-text="{_e(" ".join([doc["document_id"], doc["title"], doc["path"], str(doc["exists"]), doc["category"], doc["detected_verdict"], preview]))}"'
            ">"
            f"<th scope=\"row\"><code>{_e(doc['document_id'])}</code></th>"
            f"<td>{_e(doc['title'])}</td>"
            f"<td><a href=\"../../{_e(report_path)}\" target=\"_blank\" rel=\"noreferrer\">{_e(report_path)}</a></td>"
            f"<td>{_status_badge('PASS' if doc['exists'] else 'FAIL') if doc['exists'] else _badge('MISSING', 'fail')}</td>"
            f"<td>{_e(doc['category'])}</td>"
            f"<td>{_status_badge(doc['detected_verdict']) if str(doc['detected_verdict']).upper() in {'PASS_WITH_HIGH_CONFIDENCE','PASS_WITH_NOTES','PASS','WARNING','FAIL'} else _badge(str(doc['detected_verdict']).upper(), 'unknown')}</td>"
            f"<td>{_confidence_badge(doc['source_confidence'])}</td>"
            f"<td>{_e(doc['recommended_review_order'])}</td>"
            f"<td>{_e(preview)}</td>"
            f"<td>{_copy_button('Copy path', report_path, aria='Copy report path for ' + title, kind='copy-button small')}</td>"
            "</tr>"
        )
    return rows


def _build_validator_rows(commands, phase_label):
    rows = []
    for cmd in commands:
        command_text = cmd["command"]
        rows.append(
            "<tr "
            f'data-validator-phase="{_e(phase_label)}" '
            f'data-validator-status="{_e(cmd["last_known_status"])}" '
            f'data-search-text="{_e(" ".join([cmd["command"], cmd["purpose"], cmd["expected_pass_string"], cmd["last_known_status"]]))}"'
            ">"
            f"<th scope=\"row\"><code>{_e(cmd['command'])}</code></th>"
            f"<td>{_e(cmd['purpose'])}</td>"
            f"<td>{_e(cmd['expected_pass_string'])}</td>"
            f"<td>{_e(cmd['recommended_run_order'])}</td>"
            f"<td>{_e(cmd['post_merge_run_order'])}</td>"
            f"<td>{_status_badge(cmd['last_known_status'])}</td>"
            f"<td>{_copy_button('Copy command', cmd['copy_text'], aria='Copy validator command for ' + command_text, kind='copy-button small')}</td>"
            "</tr>"
        )
    return rows


def _build_compare_phase_rows(phases):
    rows = []
    for phase in phases:
        rows.append(
            "<tr "
            f'data-search-text="{_e(" ".join([phase["phase"], phase["interface_type"], phase["main_entrypoint"], phase["status"], phase["safety_boundary"]]))}"'
            ">"
            f"<th scope=\"row\">{_e(phase['phase'])}</th>"
            f"<td>{_e(phase['status'])}</td>"
            f"<td>{_e(phase['interface_type'])}</td>"
            f"<td><code>{_e(phase['main_entrypoint'])}</code></td>"
            f"<td>{_bool_badge(phase['can_render_status'])}</td>"
            f"<td>{_bool_badge(phase['can_prepare_packets'])}</td>"
            f"<td>{_bool_badge(phase['can_execute_packets'])}</td>"
            f"<td>{_bool_badge(phase['can_merge'])}</td>"
            f"<td>{_bool_badge(phase['can_deploy'])}</td>"
            f"<td>{_bool_badge(phase['can_use_secrets'])}</td>"
            f"<td>{_e(', '.join(phase['validators']))}</td>"
            f"<td>{_e(', '.join(phase['main_docs']))}</td>"
            f"<td>{_e(phase['safety_boundary'])}</td>"
            "</tr>"
        )
    return rows


def _stat_grid(entries):
    return '<div class="stat-grid">' + "".join(entries) + "</div>"


def _render_meta_card(snapshot):
    phase_3 = snapshot.get("phase_3_status", {})
    validator_status = snapshot.get("validator_status", {})
    data_freshness = snapshot.get("data_freshness", {})
    return _card(
        "Dashboard meta",
        "INFO",
        "Static local browser dashboard with read-only source reuse and local exports.",
        extra=_stat_grid([
            _stat("Repo", snapshot.get("repo", "unknown")),
            _stat("Source lineage", snapshot.get("source_lineage", "unknown")),
            _stat("Generated", snapshot.get("created_at_utc", "unknown")),
            _stat("Mode", snapshot.get("mode", "unknown")),
            _stat("Build", phase_3.get("output_path", "unknown"), _status_badge(phase_3.get("detected_verdict", "unknown"))),
            _stat("Data freshness", data_freshness.get("freshness_status", "unknown"), _status_badge(data_freshness.get("freshness_status", "unknown"))),
            _stat("Phase 3 validator", validator_status.get("phase_3_dashboard", {}).get("status", "unknown"), _status_badge(validator_status.get("phase_3_dashboard", {}).get("status", "unknown"))),
        ]),
    )


def _render_overview_cards(snapshot):
    phase1 = snapshot.get("phase_1_status", {})
    phase2 = snapshot.get("phase_2_status", {})
    phase3 = snapshot.get("phase_3_status", {})
    safety_scan = snapshot.get("phase_3_safety_scan", {})
    safety = snapshot.get("safety_status", {})
    next_action = snapshot.get("recommended_next_action", "unknown")
    merge_ready_status = "PASS" if "ready_for_merge_review" in next_action else "INFO"
    cards = [
        _card("Phase 1 status", phase1.get("detected_verdict", "unknown"), phase1.get("summary", "Phase 1 backend source of truth is present.")),
        _card("Phase 2 status", phase2.get("detected_verdict", "unknown"), phase2.get("summary", "Phase 2 TUI contracts and docs are present.")),
        _card("Phase 3 build status", phase3.get("detected_verdict", "unknown"), phase3.get("summary", "Static dashboard build and exports are available.")),
        _card("Safety status", "LOCKED", safety_scan.get("status", "PASS")),
        _card("Merge readiness", merge_ready_status, next_action),
    ]
    return '<section class="cards-grid">' + "".join(cards) + "</section>"


def _build_landing_screen(snapshot):
    phase1 = snapshot.get("phase_1_status", {})
    phase2 = snapshot.get("phase_2_status", {})
    phase3 = snapshot.get("phase_3_status", {})
    safety_scan = snapshot.get("phase_3_safety_scan", {})
    next_action = snapshot.get("recommended_next_action", "unknown")
    merge_ready_status = "PASS" if "ready_for_merge_review" in next_action else "INFO"
    cards = [
        _card("Phase 1 status", phase1.get("detected_verdict", "unknown"), phase1.get("summary", "Phase 1 backend source of truth is present.")),
        _card("Phase 2 status", phase2.get("detected_verdict", "unknown"), phase2.get("summary", "Phase 2 TUI contracts and docs are present.")),
        _card("Phase 3 status", phase3.get("detected_verdict", "unknown"), phase3.get("summary", "Static dashboard build and exports are available.")),
        _card("Safety status", safety_scan.get("status", "unknown"), "Static local read-only dashboard with deployment, merge, push, secret access, and command packet execution disabled."),
        _card("Merge readiness", merge_ready_status, next_action),
    ]
    buttons = [
        ("Safety Boundary", "safety-boundary"),
        ("Action Registry", "action-registry"),
        ("Artifact Deep Dive", "artifact-packages"),
        ("Reports Library", "reports-library"),
        ("Validator Command Center", "validator-command-center"),
        ("Source Transparency", "source-transparency"),
        ("Compare Phases", "compare-phases"),
        ("Branch Review", "branch-review"),
        ("Approval Ledger", "approval-ledger"),
        ("Audit / Session Data", "session-audit"),
    ]
    return (
        '<section class="landing-shell" aria-label="Dashboard landing screen">'
        '<div class="landing-head">'
        '<p class="eyebrow">Operator Landing Screen</p>'
        '<h2>Phase status and controlled navigation</h2>'
        '<p class="lede">Open only the section you want to inspect. Heavy tables and audit dumps stay collapsed until requested.</p>'
        '</div>'
        '<div class="landing-cards">' + "".join(cards) + "</div>"
        '<div class="landing-actions"><h3>Open section buttons</h3><div class="section-grid">' +
        "".join(_open_section_button(label, panel_id) for label, panel_id in buttons) +
        "</div></div></section>"
    )


def _build_toolbar(snapshot):
    dashboard_path = "13_web_dashboard/dist/index.html"
    summary = snapshot.get("phase_3_status", {}).get("summary", "Static local dashboard.")
    return f"""
    <section class="toolbar-shell" aria-label="Dashboard tools">
      <div class="toolbar-group">
        <label class="sr-only" for="global-search">Search dashboard</label>
        <input id="global-search" class="table-filter-wide" type="search" placeholder="Search all dashboard text" aria-label="Search all dashboard text">
      </div>
      <div class="toolbar-group">
        {_toolbar_button("Expand all groups", "expand", "all", "open", "toggle-button")}
        {_toolbar_button("Collapse all groups", "collapse", "all", "closed", "toggle-button")}
        {_toolbar_button("Compact view", "compact", "all", "off", "toggle-button")}
      </div>
      <div class="toolbar-group">
        {_toolbar_button("Expand source", "expand", "source", "open", "toggle-button")}
        {_toolbar_button("Collapse source", "collapse", "source", "closed", "toggle-button")}
        {_toolbar_button("Expand registry", "expand", "registry", "open", "toggle-button")}
        {_toolbar_button("Collapse registry", "collapse", "registry", "closed", "toggle-button")}
        {_toolbar_button("Expand reports", "expand", "reports", "open", "toggle-button")}
        {_toolbar_button("Collapse reports", "collapse", "reports", "closed", "toggle-button")}
        {_toolbar_button("Expand audit", "expand", "audit", "open", "toggle-button")}
        {_toolbar_button("Collapse audit", "collapse", "audit", "closed", "toggle-button")}
      </div>
      <div class="toolbar-group">
        {_copy_button("Copy dashboard path", dashboard_path, aria="Copy dashboard local file path")}
        {_copy_button("Copy summary", summary, aria="Copy dashboard summary")}
      </div>
      <div class="toolbar-group toolbar-note">
        <span class="muted">Local-only preview supported from dist. No product server. No deployment. No merge. No push.</span>
      </div>
      <div class="toolbar-status" aria-live="polite">
        <span id="copy-status" class="muted">Local UI ready.</span>
      </div>
    </section>
    """


def _build_safety_banner():
    return """
    <section class="safety-banner sticky-status" aria-label="Static local dashboard safety banner">
      <strong>STATIC LOCAL DASHBOARD</strong>
      <span>NO DEPLOY</span>
      <span>NO MERGE</span>
      <span>NO PUSH</span>
      <span>NO SECRET ACCESS</span>
      <span>NO COMMAND PACKET EXECUTION</span>
    </section>
    """


def _build_summary_strip(snapshot):
    phase1 = snapshot.get("phase_1_status", {})
    phase2 = snapshot.get("phase_2_status", {})
    phase3 = snapshot.get("phase_3_status", {})
    safety_scan = snapshot.get("phase_3_safety_scan", {})
    validator_status = snapshot.get("validator_status", {})
    action_summary = snapshot.get("action_registry_summary", {})
    artifact_summary = snapshot.get("artifact_summary", {})
    return """
    <section class="summary-strip" aria-label="Dashboard status summary">
      {phase1}{phase2}{phase3}{safety}{validators}{actions}{artifacts}
    </section>
    """.format(
        phase1=_stat("Phase 1", phase1.get("detected_verdict", "unknown"), _status_badge(phase1.get("detected_verdict", "unknown"))),
        phase2=_stat("Phase 2", phase2.get("detected_verdict", "unknown"), _status_badge(phase2.get("detected_verdict", "unknown"))),
        phase3=_stat("Phase 3", phase3.get("detected_verdict", "unknown"), _status_badge(phase3.get("detected_verdict", "unknown"))),
        safety=_stat("Safety scan", safety_scan.get("status", "unknown"), _status_badge(safety_scan.get("status", "unknown"))),
        validators=_stat("Validator status", validator_status.get("phase_3_dashboard", {}).get("status", "unknown"), _status_badge(validator_status.get("phase_3_dashboard", {}).get("status", "unknown"))),
        actions=_stat("Actions", action_summary.get("total_actions", 0), _status_badge("INFO")),
        artifacts=_stat("Packages", artifact_summary.get("package_count", 0), _status_badge("INFO")),
    )


def _build_source_transparency_panel(snapshot):
    rows = []
    for section in snapshot.get("source_transparency", {}).get("sections", []):
        rows.append(
            "<tr "
            f'data-search-text="{_e(" ".join([section["section_id"], section["title"], section["source_file_path"], section["source_type"], section["source_confidence"], str(section.get("detected_verdict", ""))]))}"'
            ">"
            f"<th scope=\"row\">{_e(section['title'])}</th>"
            f"<td><code>{_e(section['source_file_path'])}</code></td>"
            f"<td>{_status_badge('PASS' if section['source_exists'] else 'MISSING')}</td>"
            f"<td>{_e(section['source_type'])}</td>"
            f"<td>{_confidence_badge(section['source_confidence'])}</td>"
            f"<td>{_e(section.get('detected_verdict', 'unknown'))}</td>"
            "</tr>"
        )
    data_freshness = snapshot.get("data_freshness", {})
    freshness_body = _stat_grid([
        _stat("Generated at", data_freshness.get("generated_at_utc", snapshot.get("created_at_utc", "unknown"))),
        _stat("Freshness status", data_freshness.get("freshness_status", "unknown"), _status_badge(data_freshness.get("freshness_status", "unknown"))),
        _stat("Snapshot age seconds", data_freshness.get("snapshot_age_seconds", "unknown")),
        _stat("Source confidence", "generated_static_snapshot", _status_badge("INFO")),
    ])
    freshness_notes = _list(data_freshness.get("notes", []))
    return _details(
        "Source Transparency",
        freshness_body + freshness_notes + _table(
            ["Section", "Source path", "Exists", "Source type", "Confidence", "Detected verdict"],
            rows,
            "source-transparency-table",
            "Source transparency by section",
        ),
        "source",
        open_by_default=False,
        panel_id="source-transparency",
    )


def _build_validator_panel(snapshot):
    validator_status = snapshot.get("validator_status", {})
    phase1 = validator_status.get("phase_1", {})
    phase2 = validator_status.get("phase_2", {})
    phase3 = validator_status.get("phase_3_dashboard", {})
    runtime = validator_status.get("runtime", {})
    status_grid = _stat_grid([
        _stat("Phase 1", phase1.get("status", "unknown"), _status_badge(phase1.get("status", "unknown"))),
        _stat("Phase 2", phase2.get("status", "unknown"), _status_badge(phase2.get("status", "unknown"))),
        _stat("Phase 3 dashboard", phase3.get("status", "unknown"), _status_badge(phase3.get("status", "unknown"))),
        _stat("Runtime", runtime.get("status", "unknown"), _status_badge(runtime.get("status", "unknown"))),
    ])
    table_sections = []
    for title, key in [
        ("Phase 1", "phase_1"),
        ("Phase 2", "phase_2"),
        ("Phase 3", "phase_3_dashboard"),
        ("Runtime", "runtime"),
    ]:
        commands = validator_status.get(key, {}).get("commands", [])
        table_sections.append(f"<h4>{_e(title)} validator commands</h4>")
        table_sections.append(_table(
            ["Command", "Purpose", "Expected pass string", "Recommended run order", "Post-merge run order", "Last known status", "Copy"],
            _build_validator_rows(commands, title),
            f"validator-{key}-table",
            f"{title} validator command list",
        ))
    return _details(
        "Validator Command Center",
        status_grid + "".join(table_sections),
        "audit",
        open_by_default=False,
        panel_id="validator-command-center",
    )


def _build_action_panel(snapshot):
    action_summary = snapshot.get("action_registry_summary", {})
    rows = _build_action_rows(action_summary.get("actions", []))
    summary = _stat_grid([
        _stat("Total actions", action_summary.get("total_actions", 0)),
        _stat("Safe", action_summary.get("safe_count", 0), _status_badge("PASS")),
        _stat("Controlled", action_summary.get("controlled_count", 0), _status_badge("WARNING")),
        _stat("Locked", action_summary.get("locked_count", 0), _status_badge("LOCKED")),
    ])
    filters = """
    <div class="table-tools">
      <label for="action-search" class="sr-only">Filter actions</label>
      <input id="action-search" class="table-filter" type="search" placeholder="Search action rows" data-search-target="action-table" aria-label="Search action registry">
      <div class="button-row">
        <button type="button" class="toggle-button" data-action-filter="all">All</button>
        <button type="button" class="toggle-button" data-action-filter="safe">SAFE</button>
        <button type="button" class="toggle-button" data-action-filter="controlled">CONTROLLED</button>
        <button type="button" class="toggle-button" data-action-filter="locked">LOCKED</button>
        <button type="button" class="toggle-button" data-sort-table="action-table" data-sort-key="risk">Sort by risk</button>
      </div>
    </div>
    """
    return _details(
        "Action Registry",
        summary + filters + _table(
            ["Action ID", "Label", "Category", "Risk", "Writes files", "Runs commands", "Dashboard allowed", "Reason"],
            rows,
            "action-table",
            "Action registry details",
        ),
        "registry",
        open_by_default=False,
        panel_id="action-registry",
    )


def _build_artifact_panel(snapshot):
    artifact_summary = snapshot.get("artifact_summary", {})
    rows = _build_artifact_rows(artifact_summary.get("packages", []))
    summary = _stat_grid([
        _stat("Package count", artifact_summary.get("package_count", 0)),
        _stat("Warnings", artifact_summary.get("warnings_count", 0), _status_badge("WARNING" if artifact_summary.get("warnings_count", 0) else "PASS")),
        _stat("Missing files", artifact_summary.get("missing_count", 0), _status_badge("WARNING" if artifact_summary.get("missing_count", 0) else "PASS")),
        _stat("Zero-byte files", artifact_summary.get("zero_byte_count", 0), _status_badge("WARNING" if artifact_summary.get("zero_byte_count", 0) else "PASS")),
    ])
    filters = """
    <div class="table-tools">
      <label for="artifact-search" class="sr-only">Filter artifacts</label>
      <input id="artifact-search" class="table-filter" type="search" placeholder="Search artifact rows" data-search-target="artifact-table" aria-label="Search artifact packages">
      <div class="button-row">
        <button type="button" class="toggle-button" data-artifact-filter="all">All</button>
        <button type="button" class="toggle-button" data-artifact-filter="exists">Exists</button>
        <button type="button" class="toggle-button" data-artifact-filter="missing">Missing</button>
        <button type="button" class="toggle-button" data-artifact-filter="warning">Warning</button>
        <button type="button" class="toggle-button" data-sort-table="artifact-table" data-sort-key="warnings">Sort by warnings</button>
        <button type="button" class="toggle-button" data-sort-table="artifact-table" data-sort-key="missing">Sort by missing files</button>
      </div>
    </div>
    """
    return _details(
        "Artifact Deep Dive",
        summary + filters + _table(
            ["Package ID", "Package name", "Exists", "Verdict", "Missing files", "Zero-byte files", "Warnings", "Report path", "Copy"],
            rows,
            "artifact-table",
            "Artifact package details",
        ),
        "registry",
        open_by_default=False,
        panel_id="artifact-packages",
    )


def _build_reports_panel(snapshot):
    docs = snapshot.get("document_index", {}).get("documents", [])
    rows = _build_reports_rows(docs)
    summary = _stat_grid([
        _stat("Documents", snapshot.get("document_index", {}).get("document_count", 0)),
        _stat("Reports library", "Ready", _status_badge("INFO")),
    ])
    return _details(
        "Reports Library",
        summary + _table(
            ["Document ID", "Title", "Path", "Exists", "Category", "Verdict", "Confidence", "Order", "Preview", "Copy"],
            rows,
            "reports-table",
            "Phase 1, Phase 2, and Phase 3 documents",
        ),
        "reports",
        open_by_default=False,
        panel_id="reports-library",
    )


def _build_branch_review_panel(snapshot):
    branch = snapshot.get("branch_review_summary", {})
    packet = branch.get("latest_packet", {})
    grid = _stat_grid([
        _stat("Packet count", branch.get("packet_count", 0)),
        _stat("Prepared state", branch.get("prepared_state", "unknown")),
        _stat("Merge performed", str(bool(branch.get("merge_performed"))).lower(), _status_badge("DISABLED")),
        _stat("Deployment performed", str(bool(branch.get("deployment_performed"))).lower(), _status_badge("DISABLED")),
        _stat("Risk level", packet.get("risk_level", "unknown"), _risk_badge(packet.get("risk_level", "unknown"))),
    ])
    packet_card = f"""
    <div class="callout">
      <h4>Latest packet</h4>
      <pre class="code-block">{_e(json.dumps(packet, indent=2, sort_keys=False))}</pre>
      <p class="muted">Report path: <code>{_e(packet.get('review_path', 'unknown'))}</code></p>
    </div>
    """
    return _details(
        "Branch Review",
        grid + packet_card,
        "audit",
        open_by_default=False,
        panel_id="branch-review",
    )


def _build_approval_panel(snapshot):
    approval = snapshot.get("approval_ledger_summary", {})
    timeline_items = []
    for entry in approval.get("timeline", []):
        timeline_items.append(
            f"<li><code>{_e(entry.get('timestamp_utc', 'unknown'))}</code> - {_e(entry.get('packet_id', 'unknown'))} - {_e(entry.get('state', 'unknown'))} - execution_performed={_e(entry.get('execution_performed', False))}</li>"
        )
    timeline = "<ul class=\"compact-list\">" + "".join(timeline_items) + "</ul>" if timeline_items else '<p class="muted">No timeline entries detected.</p>'
    grid = _stat_grid([
        _stat("Record count", approval.get("record_count", 0)),
        _stat("Bad execution records", approval.get("bad_execution_records", 0), _status_badge("PASS" if approval.get("bad_execution_records", 0) == 0 else "FAIL")),
        _stat("Empty ledger allowed", str(bool(approval.get("empty_ledger_allowed"))).lower(), _status_badge("PASS" if approval.get("empty_ledger_allowed") else "WARNING")),
        _stat("Last record state", approval.get("last_record_state", "empty")),
        _stat("Execution invariant", "PASS" if approval.get("execution_performed_invariant") else "FAIL", _status_badge("PASS" if approval.get("execution_performed_invariant") else "FAIL")),
    ])
    return _details(
        "Approval Ledger",
        grid + timeline,
        "audit",
        open_by_default=False,
        panel_id="approval-ledger",
    )


def _build_session_panel(snapshot):
    session = snapshot.get("session_summary", {})
    grid = _stat_grid([
        _stat("Phase 1 sessions", session.get("phase_1_session_count", 0)),
        _stat("Phase 2 sessions", session.get("phase_2_session_count", 0)),
        _stat("Phase 3 note", session.get("phase_3_note", "unknown")),
        _stat("Read-only logs", str(bool(session.get("session_logs_read_only"))).lower(), _status_badge("PASS" if session.get("session_logs_read_only") else "WARNING")),
    ])
    left = "<h4>Phase 1 session paths</h4>" + _list(session.get("phase_1_sessions", []))
    right = "<h4>Phase 2 session paths</h4>" + _list(session.get("phase_2_sessions", []))
    reports = "<h4>Phase 1 session reports</h4>" + _list(session.get("phase_1_session_reports", [])) + "<h4>Phase 2 session reports</h4>" + _list(session.get("phase_2_session_reports", []))
    build_report = f'<p class="muted">Phase 3 build report: <code>{_e(session.get("phase_3_build_report", ""))}</code></p>'
    return _details(
        "Audit / Session Data",
        grid + build_report + f'<div class="split"><div>{left}</div><div>{right}</div></div>' + reports,
        "audit",
        open_by_default=False,
        panel_id="session-audit",
    )


def _build_compare_panel(snapshot):
    compare = snapshot.get("compare_phases", {})
    rows = _build_compare_phase_rows(compare.get("phases", []))
    return _details(
        "Compare Phases",
        _table(
            [
                "Phase",
                "Status",
                "Interface type",
                "Main entrypoint",
                "Can render status",
                "Can prepare packets",
                "Can execute packets",
                "Can merge",
                "Can deploy",
                "Can use secrets",
                "Validators",
                "Main docs",
                "Safety boundary",
            ],
            rows,
            "compare-phases-table",
            "Phase comparison summary",
        ),
        "source",
        open_by_default=False,
        panel_id="compare-phases",
    )


def _build_footer():
    return """
    <footer class="footer">
      <p>Generated locally. Static file. No server required. No network required. No secrets used. No commands executed except dashboard build/validation.</p>
    </footer>
    """


def render_html(snapshot, compact_view=False, print_mode=False):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    header = f"""
    <header class="hero dashboard-shell">
      <div class="hero-copy">
        <h1>The Agent Command Center</h1>
      </div>
    </header>
    """

    toolbar = _build_toolbar(snapshot) if not print_mode else ""
    sections = [
        _build_safety_banner(),
        _build_landing_screen(snapshot),
        _details("Safety Boundary", _build_safety_boundary(snapshot), "source", open_by_default=False, panel_id="safety-boundary"),
        _build_action_panel(snapshot),
        _build_artifact_panel(snapshot),
        _build_reports_panel(snapshot),
        _build_validator_panel(snapshot),
        _build_source_transparency_panel(snapshot),
        _build_compare_panel(snapshot),
        _build_branch_review_panel(snapshot),
        _build_approval_panel(snapshot),
        _build_session_panel(snapshot),
        _build_footer(),
    ]
    body_class = "dashboard-body print-view" if print_mode else "dashboard-body"
    if compact_view:
        body_class += " compact-view"
    data_json = json.dumps(snapshot, indent=2, sort_keys=False).replace("</", "<\\/")
    replacements = {
        "{{TITLE}}": "The Agent Command Center - Interface Phase 3",
        "{{BODY_CLASS}}": body_class,
        "{{HEADER}}": header,
        "{{TOOLBAR}}": toolbar,
        "{{SECTIONS}}": "\n".join(sections),
        "{{DASHBOARD_DATA_JSON}}": data_json,
        "{{SCRIPTS}}": "" if print_mode else '<script src="./static/dashboard.js"></script>',
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def render_print_html(snapshot):
    return render_html(snapshot, compact_view=False, print_mode=True)
