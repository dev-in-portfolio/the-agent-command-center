import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "templates" / "index_template.html"
PROJECT_ROOT = ROOT.parent
PHASE4D_SCHEMA_DIR = PROJECT_ROOT / "14_backend" / "schemas"
PHASE4D_DIST_DIR = PROJECT_ROOT / "13_web_dashboard" / "dist"


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


def _disabled_button(label):
    return f'<button type="button" class="toggle-button" disabled aria-disabled="true">{_e(label)}</button>'


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


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _json_preview(path, fallback_message):
    payload = _read_json(path)
    if payload is None:
        return f'<p class="muted">{_e(fallback_message)}</p>'
    return f'<pre class="code-block">{_e(json.dumps(payload, indent=2, sort_keys=False))}</pre>'


def _phase4d_schema_meta():
    items = []
    for name, title in [
        ("phase4d_identity_schema.json", "Identity schema"),
        ("phase4d_action_schema.json", "Action request schema"),
        ("phase4d_audit_schema.json", "Audit event schema"),
        ("phase4d_approval_schema.json", "Human approval schema"),
        ("phase4d_risk_model.json", "Risk model"),
    ]:
        dist_path = PHASE4D_DIST_DIR / name
        exists = dist_path.exists()
        items.append({
            "title": title,
            "path": f"13_web_dashboard/dist/{name}",
            "exists": exists,
        })
    return items


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
        "Read-Only Operations Dashboard with read-only source reuse and static hosting readiness.",
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
    next_action = "Ready for static hosting review after merge. Backend integration remains a later phase."
    merge_ready_status = "PASS" if "ready_for_merge_review" in next_action else "INFO"
    cards = [
        _card("Phase 1 status", phase1.get("detected_verdict", "unknown"), phase1.get("summary", "Phase 1 backend source of truth is present.")),
        _card("Phase 2 status", phase2.get("detected_verdict", "unknown"), phase2.get("summary", "Phase 2 TUI contracts and docs are present.")),
        _card("Phase 3 build status", phase3.get("detected_verdict", "unknown"), phase3.get("summary", "Read-Only Operations Dashboard build and exports are available.")),
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
    next_action = "Ready for production polish review. Backend integration remains a later phase."
    merge_ready_status = "PASS" if "ready_for_merge_review" in next_action else "INFO"
    cards = [
        _card("Phase 1 status", phase1.get("detected_verdict", "unknown"), phase1.get("summary", "Phase 1 backend source of truth is present.")),
        _card("Phase 2 status", phase2.get("detected_verdict", "unknown"), phase2.get("summary", "Phase 2 TUI contracts and docs are present.")),
        _card("Phase 3 status", phase3.get("detected_verdict", "unknown"), phase3.get("summary", "Read-Only Operations Dashboard build and exports are available.")),
        _card("Safety status", safety_scan.get("status", "unknown"), "Production-hosted dashboard with deployment, merge, push, secret access, and command execution disabled."),
        _card("Roadmap status", merge_ready_status, next_action),
    ]
    buttons = [
        ("Roadmap Re-Anchor", "roadmap-reanchor"),
        ("Safety Boundary", "safety-boundary"),
        ("Phase 4D Preview", "phase4d-strategic-preview"),
        ("Action Registry", "action-registry"),
        ("Reports Library", "reports-library"),
        ("Validator Center", "validator-command-center"),
        ("Status Snapshot", "status-snapshot-panel"),
        ("Backend Status", "backend-status-panel"),
        ("Phase 5A Workflow Shell", "phase5a-workflow-shell"),
        ("Artifacts", "artifact-packages"),
        ("Source Info", "source-transparency"),
        ("Audit / Session", "session-audit"),
    ]
    return (
        '<section class="landing-shell" aria-label="Dashboard landing screen">'
        '<div class="landing-head">'
        '<p class="eyebrow">Command Center Overview</p>'
        '<h2>Production Presentation & Safety Review</h2>'
        '<p class="lede">Review the core project roadmap, safety boundaries, and static schema previews. Technical audits and raw session data are available in the sections below.</p>'
        '</div>'
        '<div class="landing-cards">' + "".join(cards) + "</div>"
        '<div class="landing-actions"><h3>Jump to section</h3><div class="section-grid">' +
        "".join(_open_section_button(label, panel_id) for label, panel_id in buttons) +
        "</div></div></section>"
    )


def _build_toolbar(snapshot):
    dashboard_path = "13_web_dashboard/dist/index.html"
    summary = snapshot.get("phase_3_status", {}).get("summary", "Read-Only Operations Dashboard.")
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
        <span class="muted">Current build: static preview. Hosting readiness: static hosting ready. Backend integration: planned, disabled in this build. Controls: read-only display.</span>
      </div>
      <div class="toolbar-status" aria-live="polite">
        <span id="copy-status" class="muted">Local UI ready.</span>
      </div>
    </section>
    """


def _build_safety_banner():
    return """
    <section class="safety-banner sticky-status" aria-label="Read-Only Operations Dashboard safety banner">
      <strong>READ-ONLY DASHBOARD</strong>
      <span>BACKEND ACTIONS DISABLED</span>
      <span>NO COMMAND EXECUTION</span>
      <span>NO DEPLOY CONTROLS</span>
      <span>NO MERGE CONTROLS</span>
      <span>NO SECRET ACCESS</span>
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


def _build_phase5a_workflow_shell():
    workflow_types = [
        "Status Review",
        "Report Review",
        "Validator Review",
        "Dashboard Polish Request",
        "Phase Planning Request",
        "Safety Review Request",
    ]
    type_options = "".join(f'<option value="{_e(t)}">{_e(t)}</option>' for t in workflow_types)
    states = ["draft", "needs_review", "review_ready", "changes_requested", "approved_for_future_phase", "rejected", "cancelled", "archived"]
    state_options = "".join(f'<option value="{_e(s)}">{_e(s)}</option>' for s in states)

    body = f"""
<div class="phase5a-workflow-shell" data-phase5a-shell="true">
  <div class="callout" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.05);">
    <strong style="color: var(--warning);">CLIENT-SIDE WORKFLOW SHELL</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      TEMPORARY IN-BROWSER STATE ONLY — NO PERSISTENCE — NO BACKEND WRITES — NO EXECUTION — NO MUTATION — NO DEPLOY / MERGE / PUSH / PR CONTROLS
    </p>
  </div>

  <div class="phase5a-form-grid">
    <article class="card" id="phase5a-drafting-panel">
      <div class="card-head">
        <h3 class="card-title">Request Drafting Panel</h3>
        <span class="badge info">DRAFT</span>
      </div>
      <div class="phase5a-form-fields">
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Workflow Type</span>
          <select id="phase5a-workflow-type" class="table-filter" style="width:100%;">{type_options}</select>
        </label>
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Request Title</span>
          <input id="phase5a-request-title" class="table-filter" type="text" placeholder="e.g. Review Phase 3 validator output" style="width:100%;">
        </label>
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Plain-Language Intent</span>
          <textarea id="phase5a-intent" class="table-filter" rows="3" placeholder="Describe what you want to review or accomplish..." style="width:100%;resize:vertical;"></textarea>
        </label>
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Target Scope</span>
          <input id="phase5a-target-scope" class="table-filter" type="text" placeholder="e.g. 13_web_dashboard, scripts/" style="width:100%;">
        </label>
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Operator Notes</span>
          <textarea id="phase5a-operator-notes" class="table-filter" rows="2" placeholder="Optional notes..." style="width:100%;resize:vertical;"></textarea>
        </label>
      </div>
      <div class="button-row" style="margin-top:1rem;">
        <button type="button" class="section-button" id="phase5a-create-draft-button">Create draft</button>
        <button type="button" class="toggle-button" id="phase5a-reset-button">Reset local workflow</button>
      </div>
      <p class="muted" style="margin-top:0.5rem;font-size:0.75rem;">DISABLED — PLANNING ONLY. No persistence. No backend writes.</p>
    </article>

    <article class="card" id="phase5a-risk-panel">
      <div class="card-head">
        <h3 class="card-title">Risk Preview Panel</h3>
        <span class="badge info" id="phase5a-risk-badge">NOT CLASSIFIED</span>
      </div>
      <p class="card-body" id="phase5a-risk-description">Complete the drafting panel and create a draft to see risk classification.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="font-size:0.8rem;">Risk is classified locally using static rules. No external API call. No execution.</p>
      </div>
    </article>
  </div>

  <div class="phase5a-state-machine" id="phase5a-state-machine">
    <h4>Request State: <span id="phase5a-current-state-display" style="color:var(--accent);">none</span></h4>
    <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,130px),1fr));">
      <button type="button" class="toggle-button" id="phase5a-state-draft" disabled>Set Draft</button>
      <button type="button" class="toggle-button" id="phase5a-state-needs-review" disabled>Needs Review</button>
      <button type="button" class="toggle-button" id="phase5a-state-review-ready" disabled>Review Ready</button>
      <button type="button" class="toggle-button" id="phase5a-state-changes-requested" disabled>Request Changes</button>
      <button type="button" class="toggle-button" id="phase5a-state-approved" disabled>Approve for Future</button>
      <button type="button" class="toggle-button" id="phase5a-state-rejected" disabled>Reject</button>
      <button type="button" class="toggle-button" id="phase5a-state-cancelled" disabled>Cancel</button>
      <button type="button" class="toggle-button" id="phase5a-state-archived" disabled>Archive</button>
    </div>
    <p class="muted" style="font-size:0.75rem;margin-top:0.5rem;">Approval display only — does not execute. No execution, no deploy, no merge, no push, no PR.</p>
  </div>

  <div class="phase5a-summary-card" id="phase5a-summary-card" style="display:none;">
    <h4>Review Summary</h4>
    <div class="stat-grid" id="phase5a-summary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
  </div>

  <div class="phase5a-summary-card" id="phase5a-approval-card" style="display:none;border-color:rgba(245,158,11,0.3);">
    <h4>Approval Required</h4>
    <div class="stat-grid" id="phase5a-approval-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
  </div>

  <div class="phase5a-summary-card" id="phase5a-dryrun-card" style="display:none;">
    <h4>Dry-Run Preview</h4>
    <div class="callout">
      <p class="muted">Dry-run preview is future-only. No command execution. No external API calls. No filesystem changes. No deploy/merge/push/PR action.</p>
      <p class="muted" style="margin-top:0.25rem;font-size:0.8rem;">DISABLED — NO EXECUTION IN PHASE 5. This preview would require execution engine, queue, auth, and storage dependencies before becoming operational.</p>
    </div>
  </div>

  <div class="phase5a-audit-trail" id="phase5a-audit-trail" style="display:none;">
    <h4>Audit Trail Preview</h4>
    <div class="table-wrap" style="max-height:300px;overflow-y:auto;">
      <table class="data-table" id="phase5a-audit-table">
        <caption>Local in-memory audit events — no persistent storage</caption>
        <thead>
          <tr>
            <th scope="col">Timestamp</th>
            <th scope="col">Event</th>
            <th scope="col">Previous State</th>
            <th scope="col">Next State</th>
            <th scope="col">Reason</th>
            <th scope="col">Risk</th>
          </tr>
        </thead>
        <tbody id="phase5a-audit-body">
          <tr><td colspan="6" class="empty">No audit events. Create a draft to begin.</td></tr>
        </tbody>
      </table>
    </div>
    <p class="muted" style="font-size:0.75rem;margin-top:0.25rem;">DISABLED — FUTURE STORAGE REQUIRED. Audit trail is in-memory only and will be lost on page refresh.</p>
  </div>
</div>
"""
    return _details(
        "Original Phase 5A — Client-Side Operator Workflow Shell",
        body,
        "source",
        open_by_default=True,
        panel_id="phase5a-workflow-shell"
    )


def _build_footer():
    return """
    <footer class="footer">
      <p>Generated statically. Static files. Backend integration is planned for a later phase and is intentionally not included in this static dashboard build. No secrets used. No commands executed except dashboard build/validation.</p>
    </footer>
    """


def _build_status_snapshot_panel(snapshot):
    body = """
    <div class="stat-grid">
      <div class="stat"><span>Snapshot mode</span><strong>static read-only</strong></div>
      <div class="stat"><span>Source</span><strong>local repository reports</strong></div>
      <div class="stat"><span>Live external API</span><strong>Disabled</strong></div>
      <div class="stat"><span>Secrets/tokens</span><strong>Not used</strong></div>
      <div class="stat"><span>Mutation</span><strong>Disabled</strong></div>
    </div>
    <div class="toolbar-group" style="margin-top: 1rem;">
      <button type="button" class="section-button" id="load-snapshot-button">Load static snapshot</button>
      <span id="snapshot-fetch-status" class="muted" style="margin-left: 1rem;">Not loaded.</span>
    </div>
    <div id="snapshot-response-area" style="margin-top: 1rem; display: none;">
      <h4>Latest static snapshot</h4>
      <pre class="code-block" id="snapshot-response-json"></pre>
    </div>
    """
    return _details(
        "Static Status Snapshot",
        body,
        "audit",
        open_by_default=True,
        panel_id="status-snapshot-panel"
    )


def _build_backend_status_panel(snapshot):
    body = """
    <div class="stat-grid">
      <div class="stat"><span>Backend integration</span><strong>Phase 4A read-only foundation</strong></div>
      <div class="stat"><span>Backend actions</span><strong>Disabled</strong></div>
      <div class="stat"><span>Command execution</span><strong>Disabled</strong></div>
      <div class="stat"><span>GitHub mutation</span><strong>Disabled</strong></div>
      <div class="stat"><span>Controls</span><strong>Disabled</strong></div>
    </div>
    <div class="toolbar-group" style="margin-top: 1rem;">
      <button type="button" class="section-button" id="check-backend-button">Check backend status</button>
      <span id="backend-fetch-status" class="muted" style="margin-left: 1rem;">Not checked.</span>
    </div>
    <div id="backend-response-area" style="margin-top: 1rem; display: none;">
      <h4>Latest backend response</h4>
      <pre class="code-block" id="backend-response-json"></pre>
    </div>
    """
    return _details(
        "Backend Status",
        body,
        "audit",
        open_by_default=True,
        panel_id="backend-status-panel"
    )


def _build_phase4d_preview_panel():
    schema_meta = _phase4d_schema_meta()
    schema_rows = []
    for item in schema_meta:
        schema_rows.append(
            "<tr>"
            f"<th scope=\"row\">{_e(item['title'])}</th>"
            f"<td><code>{_e(item['path'])}</code></td>"
            f"<td>{_status_badge('PASS' if item['exists'] else 'FAIL')}</td>"
            "</tr>"
        )

    control_room = """
    <div class="phase4d-preview-grid">
      <article class="card">
        <div class="card-head">
          <h3 class="card-title">Phase 4D Control Room Preview</h3>
          {status}
        </div>
        <p class="card-body">DISABLED MOCK. SCHEMA PREVIEW ONLY. NO EXECUTION. NO MUTATION. NO DEPLOY. NO MERGE. NO PUSH. NO SECRET ACCESS.</p>
        <div class="button-row">
          {request_button}
          {approve_button}
          {deploy_button}
          {merge_button}
        </div>
      </article>
      <article class="card">
        <div class="card-head">
          <h3 class="card-title">Identity & Permissions Preview</h3>
          {status}
        </div>
        <p class="card-body">Recommended provider, roles, and permission boundaries are documented only.</p>
        <div class="button-row">
          {identity_load_button}
          {role_button}
        </div>
        <div class="callout">
          <p class="muted">DISABLED — SCHEMA PREVIEW ONLY</p>
          <span id="phase4d-identity-status" class="muted">Not loaded.</span>
        </div>
      </article>
      <article class="card">
        <div class="card-head">
          <h3 class="card-title">Action Request Queue Preview</h3>
          {status}
        </div>
        <p class="card-body">Queue intake is request-only and non-executing in this build.</p>
        <div class="button-row">
          {action_load_button}
          {push_button}
        </div>
        <div class="callout">
          <p class="muted">DISABLED — SCHEMA PREVIEW ONLY</p>
          <span id="phase4d-action-status" class="muted">Not loaded.</span>
        </div>
      </article>
      <article class="card">
        <div class="card-head">
          <h3 class="card-title">Audit Event Schema Preview</h3>
          {status}
        </div>
        <p class="card-body">Audit, approval, and risk schemas are available as static previews.</p>
        <div class="button-row">
          {audit_load_button}
          {pr_button}
        </div>
        <div class="callout">
          <p class="muted">DISABLED — SCHEMA PREVIEW ONLY</p>
          <span id="phase4d-audit-status" class="muted">Not loaded.</span>
        </div>
      </article>
      <article class="card">
        <div class="card-head">
          <h3 class="card-title">Risk Model Preview</h3>
          {status}
        </div>
        <p class="card-body">Risk classes remain static and inert in Phase 4D.</p>
        <div class="button-row">
          {risk_load_button}
          {approval_load_button}
        </div>
        <div class="callout">
          <p class="muted">DISABLED — SCHEMA PREVIEW ONLY</p>
          <span id="phase4d-risk-status" class="muted">Not loaded.</span>
        </div>
      </article>
      
      <section class="schema-output-panel" id="phase4d-schema-output-panel" style="display: none;">
        <h4>Static schema preview output</h4>
        <pre class="code-block schema-preview-code" id="phase4d-shared-response-json"></pre>
      </section>
    </div>
    """.format(
        status=_status_badge("DISABLED"),
        request_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        approve_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        deploy_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        merge_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        identity_load_button='<button type="button" class="section-button" id="load-phase4d-identity-schema-button">Load identity schema</button>',
        role_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        action_load_button='<button type="button" class="section-button" id="load-phase4d-action-schema-button">Load action schema</button>',
        push_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        audit_load_button='<button type="button" class="section-button" id="load-phase4d-audit-schema-button">Load audit schema</button>',
        pr_button=_disabled_button("DISABLED — SCHEMA PREVIEW ONLY"),
        risk_load_button='<button type="button" class="section-button" id="load-phase4d-risk-schema-button">Load risk model</button>',
        approval_load_button='<button type="button" class="section-button" id="load-phase4d-approval-schema-button">Load approval schema</button>',
    )

    schema_summary = _stat_grid([
        _stat("Live auth", "false", _status_badge("DISABLED")),
        _stat("Database", "false", _status_badge("DISABLED")),
        _stat("Queue storage", "false", _status_badge("DISABLED")),
        _stat("Execution", "false", _status_badge("DISABLED")),
        _stat("External APIs", "false", _status_badge("DISABLED")),
    ])

    docs = [
        "14_backend/phase_4d_identity_selection_recommendation.md",
        "14_backend/phase_4d_role_permission_implementation_contract.md",
        "14_backend/phase_4d_request_only_endpoint_contract.md",
        "14_backend/phase_4d_disabled_dashboard_ui_contract.md",
        "14_backend/phase_4d_execution_boundary_contract.md",
        "14_backend/phase_4d_phase_4e_handoff_contract.md",
    ]
    docs_body = "<h4>Phase 4D contracts</h4>" + _list(docs)
    previews = """
    <h4>Schema preview copies</h4>
    {table}
    """.format(
        table=_table(["Preview", "Dist path", "Exists"], schema_rows, "phase4d-schema-table", "Phase 4D static schema previews"),
    )

    return _details(
        "Phase 4D Strategic Preview",
        schema_summary + control_room + docs_body + previews,
        "audit",
        open_by_default=True,
        panel_id="phase4d-strategic-preview",
    )


def _build_roadmap_panel():
    body = """
    <div class="callout">
      <p>The inserted backend safety track is now locked and verified.</p>
      <p>The project is returning to the original roadmap:</p>
      <ul class="compact-list">
        <li><strong>Original Phase 1</strong> — CLI / Command Packet Layer (Complete)</li>
        <li><strong>Original Phase 2</strong> — TUI / Terminal Operator Layer (Complete)</li>
        <li><strong>Original Phase 3</strong> — Static Dashboard (Complete)</li>
        <li><strong>Original Phase 4</strong> — Hosted / Production Dashboard Polish (ACTIVE)</li>
        <li><strong>Original Phase 5</strong> — Interactive Operator Workflow Layer (Planned)</li>
        <li><strong>Original +1</strong> — Controlled Agent / Automation Layer (Planned)</li>
      </ul>
      <p style="margin-top: 1rem;"><strong>Current active direction:</strong> Original Phase 4 — Hosted / Production Dashboard Polish</p>
      <p class="muted">Note: Phase 4E is intentionally deferred.</p>
    </div>
    """
    return _details(
        "Roadmap Re-Anchor",
        body,
        "source",
        open_by_default=True,
        panel_id="roadmap-reanchor"
    )


def render_html(snapshot, compact_view=False, print_mode=False):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    header = f"""
    <header class="hero dashboard-shell">
      <div class="hero-copy">
        <h1>The Agent Command Center</h1>
        <p class="lede">A read-only production dashboard for reviewing system status, safety boundaries, static schemas, and operator workflow readiness. Includes Original Phase 5A client-side operator workflow shell.</p>
        <p class="muted" style="margin-top: 0.5rem; font-size: 0.85rem;">Production-hosted. Static/inert. No command execution. No deploy, merge, push, or mutation controls.</p>
      </div>
    </header>
    """

    toolbar = _build_toolbar(snapshot) if not print_mode else ""
    sections = [
        _build_safety_banner(),
        _build_landing_screen(snapshot),
        _details("Safety Boundary Summary", _build_safety_boundary(snapshot), "source", open_by_default=True, panel_id="safety-boundary"),
        _build_roadmap_panel(),
        _build_phase4d_preview_panel(),
        _build_status_snapshot_panel(snapshot),
        _build_backend_status_panel(snapshot),
        _build_phase5a_workflow_shell(),
        _build_action_panel(snapshot),
        _build_reports_panel(snapshot),
        _build_validator_panel(snapshot),
        _build_artifact_panel(snapshot),
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
        "{{TITLE}}": "The Agent Command Center - Read-Only Operations Dashboard",
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
