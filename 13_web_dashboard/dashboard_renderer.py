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
        ("Phase 5B Packet Builder", "phase5b-packet-builder"),
        ("Phase 5C Review Board", "phase5c-review-board"),
        ("Phase 5D Handoff Composer", "phase5d-handoff-composer"),
        ("Phase 5E Runbook Simulator", "phase5e-runbook-simulator"),
        ("Original +1 Readiness Layer", "plus1-controlled-automation-readiness-layer"),
        ("Original +1B Contract Layer", "plus1b-operator-console-contract-layer"),
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


def _build_phase5b_request_packet_builder():
    body = """
<div class="phase5b-packet-builder" data-phase5b-builder="true">
  <div class="callout" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.05);">
    <strong style="color: var(--warning);">CLIENT-SIDE REQUEST PACKET BUILDER</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      GENERATED LOCALLY — COPY ONLY — NO PERSISTENCE — NO BACKEND WRITES — NO EXECUTION — NO MUTATION — NO DEPLOY / MERGE / PUSH / PR CONTROLS
    </p>
  </div>

  <div class="phase5b-preview-grid">
    <article class="card phase5b-packet-panel" id="phase5b-packet-panel">
      <div class="card-head">
        <h3 class="card-title">Operator Request Packet Panel</h3>
        <span class="badge info">PACKET</span>
      </div>
      <p class="card-body">Generate a structured request packet from the Phase 5A draft. Packet is local, copy-only, and not persisted.</p>
      <div class="button-row" style="margin-top:1rem;">
        <button type="button" class="section-button" id="phase5b-generate-packet-button">Generate request packet</button>
        <button type="button" class="toggle-button" id="phase5b-clear-packet-button">Clear packet</button>
      </div>
      <div id="phase5b-packet-fields" style="display:none;margin-top:1rem;">
        <div class="stat-grid" id="phase5b-packet-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      </div>
    </article>

    <article class="card phase5b-validation-panel" id="phase5b-validation-panel">
      <div class="card-head">
        <h3 class="card-title">Packet Validation Panel</h3>
        <span class="badge info" id="phase5b-validation-badge">NOT VALIDATED</span>
      </div>
      <p class="card-body" id="phase5b-validation-description">Generate a packet to see local validation results.</p>
      <div id="phase5b-validation-details" style="display:none;margin-top:0.75rem;">
        <div class="stat-grid" id="phase5b-validation-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
        <div class="callout" style="margin-top:0.75rem;">
          <p class="muted" style="font-size:0.8rem;">Validation is local only. No external API call. No execution.</p>
        </div>
      </div>
    </article>
  </div>

  <div class="phase5b-preview-grid">
    <article class="card phase5b-json-preview" id="phase5b-json-panel" style="display:none;">
      <div class="card-head">
        <h3 class="card-title">Packet JSON Preview</h3>
        <span class="badge info">JSON</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5b-copy-json-button" data-phase5b-copy="json">Copy packet JSON</button>
      </div>
      <pre class="code-block" id="phase5b-json-preview" style="max-height:360px;overflow:auto;">No packet generated yet.</pre>
    </article>

    <article class="card phase5b-markdown-preview" id="phase5b-markdown-panel" style="display:none;">
      <div class="card-head">
        <h3 class="card-title">Packet Markdown Preview</h3>
        <span class="badge info">MARKDOWN</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5b-copy-markdown-button" data-phase5b-copy="markdown">Copy packet Markdown</button>
      </div>
      <pre class="code-block" id="phase5b-markdown-preview" style="max-height:360px;overflow:auto;">No packet generated yet.</pre>
    </article>
  </div>

  <article class="card phase5b-safety-summary" id="phase5b-safety-summary" style="display:none;">
    <div class="card-head">
      <h3 class="card-title">Safety Summary Panel</h3>
      <span class="badge pass">SAFE</span>
    </div>
    <div class="stat-grid" id="phase5b-safety-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr));">
      <div class="stat"><span>Generated</span><strong>Locally</strong></div>
      <div class="stat"><span>Saved</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Sent anywhere</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Queued</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Executed</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Backend write</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>GitHub mutation</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Netlify mutation</span><strong class="badge fail">No</strong></div>
    </div>
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted">This packet is generated locally. It is not saved. It is not sent anywhere. It is not queued. It is not executed. It does not write to the backend. It does not mutate GitHub or Netlify. It disappears on refresh unless the operator copies it manually.</p>
    </div>
    <div class="button-row" style="margin-top:0.75rem;">
      <button type="button" class="copy-button" id="phase5b-copy-safety-button" data-phase5b-copy="safety">Copy safety summary</button>
    </div>
  </article>
</div>
"""
    return _details(
        "Original Phase 5B — Client-Side Operator Request Packet Builder",
        body,
        "source",
        open_by_default=True,
        panel_id="phase5b-packet-builder"
    )


def _build_phase5c_review_board():
    body = """
<div class="phase5c-review-board" data-phase5c-review-board="true">
  <div class="callout" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.05);">
    <strong style="color: var(--warning);">CLIENT-SIDE REVIEW BOARD</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      DECISION LEDGER PREVIEW — TEMPORARY IN-BROWSER STATE ONLY — NO PERSISTENCE — NO BACKEND WRITES — NO EXECUTION — NO MUTATION — NO DEPLOY / MERGE / PUSH / PR CONTROLS
    </p>
  </div>

  <div class="phase5c-preview-grid">
    <article class="card phase5c-intake-panel" id="phase5c-intake-panel">
      <div class="card-head">
        <h3 class="card-title">Review Board Intake Panel</h3>
        <span class="badge info">INTAKE</span>
      </div>
      <p class="card-body">Add a generated Phase 5B packet to the review board, or paste packet JSON into the textarea below.</p>
      <div class="phase5c-intake-actions">
        <button type="button" class="section-button" id="phase5c-add-current-packet">Add current packet</button>
        <button type="button" class="toggle-button" id="phase5c-clear-review-board">Clear review board</button>
      </div>
      <div style="margin-top: 0.75rem;">
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Pasted Packet JSON</span>
          <textarea id="phase5c-pasted-json" class="table-filter" rows="4" placeholder="Paste packet JSON here..." style="width:100%;resize:vertical;font-family:var(--mono);font-size:0.8rem;"></textarea>
        </label>
        <div class="button-row" style="margin-top:0.5rem;">
          <button type="button" class="section-button" id="phase5c-parse-pasted-packet">Parse pasted packet</button>
        </div>
        <p class="muted" style="font-size:0.75rem;margin-top:0.25rem;">Forbidden: file upload, file import, fetch from URL, backend submit, queue packet, save packet.</p>
      </div>
    </article>

    <article class="card phase5c-review-list" id="phase5c-review-list-panel">
      <div class="card-head">
        <h3 class="card-title">Review Board List Panel</h3>
        <span class="badge info">LIST</span>
      </div>
      <p class="card-body">DISPLAY-ONLY REVIEW LIST — NOT A QUEUE</p>
      <div class="table-wrap" style="max-height:300px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="phase5c-review-table">
          <caption>Local in-memory review board — no persistent storage</caption>
          <thead>
            <tr>
              <th scope="col">Packet ID</th>
              <th scope="col">Title</th>
              <th scope="col">Workflow</th>
              <th scope="col">Risk</th>
              <th scope="col">State</th>
              <th scope="col">Decision</th>
              <th scope="col">Notes</th>
            </tr>
          </thead>
          <tbody id="phase5c-review-body">
            <tr><td colspan="7" class="empty">No packets in review board. Add a packet to begin.</td></tr>
          </tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="phase5c-preview-grid">
    <article class="card phase5c-decision-panel" id="phase5c-decision-panel">
      <div class="card-head">
        <h3 class="card-title">Decision Panel</h3>
        <span class="badge info">DECISION</span>
      </div>
      <p class="card-body">Select a packet from the list above, then choose a decision. Local only — not saved, not submitted.</p>
      <div style="margin-top:0.75rem;">
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Packet ID</span>
          <select id="phase5c-decision-packet-select" class="table-filter" style="width:100%;">
            <option value="">— No packets available —</option>
          </select>
        </label>
        <label style="display:grid;gap:0.25rem;margin-top:0.5rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Decision</span>
          <select id="phase5c-decision-select" class="table-filter" style="width:100%;">
            <option value="pending_review">Pending Review</option>
            <option value="needs_changes">Needs Changes</option>
            <option value="accepted_for_future_phase">Accepted for Future Phase</option>
            <option value="rejected">Rejected</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <label style="display:grid;gap:0.25rem;margin-top:0.5rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Review Note</span>
          <textarea id="phase5c-review-note" class="table-filter" rows="2" placeholder="Free-text human review note..." style="width:100%;resize:vertical;"></textarea>
        </label>
        <div class="button-row" style="margin-top:0.5rem;">
          <button type="button" class="section-button" id="phase5c-record-decision">Record decision</button>
        </div>
        <p class="muted" style="font-size:0.75rem;margin-top:0.25rem;">Every decision updates local in-memory state only. Not saved. Not submitted. Not executed.</p>
      </div>
    </article>

    <article class="card phase5c-ledger-panel" id="phase5c-ledger-panel">
      <div class="card-head">
        <h3 class="card-title">Decision Ledger Panel</h3>
        <span class="badge info">LEDGER</span>
      </div>
      <p class="card-body">Local in-memory ledger of all decision events.</p>
      <div class="table-wrap" style="max-height:300px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="phase5c-ledger-table">
          <caption>Local in-memory decision ledger — no persistent storage</caption>
          <thead>
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">Packet ID</th>
              <th scope="col">Previous</th>
              <th scope="col">Decision</th>
              <th scope="col">Review Note</th>
              <th scope="col">Risk</th>
            </tr>
          </thead>
          <tbody id="phase5c-ledger-body">
            <tr><td colspan="6" class="empty">No ledger events yet. Record a decision to populate.</td></tr>
          </tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="phase5c-preview-grid">
    <article class="card phase5c-json-preview" id="phase5c-ledger-json-panel" style="display:none;">
      <div class="card-head">
        <h3 class="card-title">Ledger JSON Preview</h3>
        <span class="badge info">JSON</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5c-copy-ledger-json">Copy review ledger JSON</button>
      </div>
      <pre class="code-block" id="phase5c-ledger-json-preview" style="max-height:360px;overflow:auto;">No ledger generated yet.</pre>
    </article>

    <article class="card phase5c-markdown-preview" id="phase5c-ledger-markdown-panel" style="display:none;">
      <div class="card-head">
        <h3 class="card-title">Ledger Markdown Preview</h3>
        <span class="badge info">MARKDOWN</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5c-copy-ledger-markdown">Copy review ledger Markdown</button>
      </div>
      <pre class="code-block" id="phase5c-ledger-markdown-preview" style="max-height:360px;overflow:auto;">No ledger generated yet.</pre>
    </article>
  </div>

  <div class="button-row" style="margin-top:0.5rem;">
    <button type="button" class="copy-button" id="phase5c-copy-decision-summary">Copy decision summary</button>
  </div>

  <article class="card phase5c-safety-summary" id="phase5c-safety-summary" style="margin-top:1rem;">
    <div class="card-head">
      <h3 class="card-title">Safety Summary Panel</h3>
      <span class="badge pass">SAFE</span>
    </div>
    <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));">
      <div class="stat"><span>Review board</span><strong>Temporary</strong></div>
      <div class="stat"><span>Ledger</span><strong>Local only</strong></div>
      <div class="stat"><span>Saved anywhere</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Sent anywhere</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Queued</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Executed</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Backend write</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>GitHub mutation</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Netlify mutation</span><strong class="badge fail">No</strong></div>
    </div>
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted">Review board state is temporary and in-memory only. The ledger is generated locally and is copy-only. Nothing is saved. Nothing is sent. Nothing is queued. Nothing is executed. Nothing writes to the backend. Nothing mutates GitHub or Netlify. Refresh clears state unless copied manually.</p>
    </div>
  </article>
</div>
"""
    return _details(
        "Original Phase 5C — Client-Side Operator Review Board & Decision Ledger",
        body,
        "source",
        open_by_default=True,
        panel_id="phase5c-review-board"
    )


def _build_phase5d_handoff_composer():
    body = """
<div class="phase5d-handoff-composer" data-phase5d-handoff="true">
  <div class="callout" style="border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.05);">
    <strong style="color: var(--warning);">CLIENT-SIDE HANDOFF COMPOSER</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      GENERATED LOCALLY — COPY/PASTE HANDOFF ONLY — TEMPORARY IN-BROWSER STATE ONLY — NO PERSISTENCE — NO BACKEND WRITES — NO EXECUTION — NO MUTATION — NO DEPLOY / MERGE / PUSH / PR CONTROLS
    </p>
  </div>

  <div class="phase5d-preview-grid">
    <article class="card phase5d-source-panel" id="phase5d-source-panel">
      <div class="card-head">
        <h3 class="card-title">Handoff Source Panel</h3>
        <span class="badge info">SOURCE</span>
      </div>
      <p class="card-body">Select Phase 5C review board decisions to include in the handoff package. The composer also references the current local request packet and the review ledger where available.</p>
      <div class="phase5d-source-grid" style="margin-top:0.75rem;">
        <section class="phase5d-source-section">
          <h4 style="margin:0 0 0.5rem 0;">Current Local Request Packet</h4>
          <div class="stat-grid" id="phase5d-request-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,180px),1fr));"></div>
          <pre class="code-block" id="phase5d-request-preview" style="max-height:240px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No current request packet drafted yet.</pre>
        </section>

        <section class="phase5d-source-section">
          <h4 style="margin:0 0 0.5rem 0;">Review Ledger Snapshot</h4>
          <div class="stat-grid" id="phase5d-ledger-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,180px),1fr));"></div>
          <div class="table-wrap" style="max-height:260px;overflow-y:auto;margin-top:0.75rem;">
            <table class="data-table" id="phase5d-composition-table">
              <caption>Included packets for the current handoff draft</caption>
              <thead>
                <tr>
                  <th scope="col">Packet ID</th>
                  <th scope="col">Title</th>
                  <th scope="col">Workflow</th>
                  <th scope="col">Risk</th>
                  <th scope="col">Decision</th>
                  <th scope="col">Included</th>
                </tr>
              </thead>
              <tbody id="phase5d-composition-body">
                <tr><td colspan="6" class="empty">No handoff composed yet. Use Phase 5C decisions to compose a handoff.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <div style="margin-top: 0.75rem;">
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Include decisions by status</span>
          <div class="phase5d-filter-grid" id="phase5d-decision-filters">
            <label class="phase5d-filter-option"><input type="checkbox" value="accepted_for_future_phase" checked> Accepted</label>
            <label class="phase5d-filter-option"><input type="checkbox" value="needs_changes"> Needs Changes</label>
            <label class="phase5d-filter-option"><input type="checkbox" value="pending_review"> Pending Review</label>
            <label class="phase5d-filter-option"><input type="checkbox" value="rejected"> Rejected</label>
            <label class="phase5d-filter-option"><input type="checkbox" value="archived"> Archived</label>
          </div>
        </label>
        <div class="button-row" style="margin-top: 0.75rem;">
          <button type="button" class="section-button" id="phase5d-compose-handoff">Compose handoff from 5C decisions</button>
          <button type="button" class="toggle-button" id="phase5d-clear-handoff">Clear handoff</button>
        </div>
      </div>
      <div style="margin-top: 0.75rem;">
        <label style="display:grid;gap:0.25rem;">
          <span style="font-size:0.8rem;color:var(--muted);">Pasted Handoff JSON</span>
          <textarea id="phase5d-pasted-json" class="table-filter" rows="3" placeholder="Paste handoff JSON here..." style="width:100%;resize:vertical;font-family:var(--mono);font-size:0.8rem;"></textarea>
        </label>
        <div class="button-row" style="margin-top:0.5rem;">
          <button type="button" class="section-button" id="phase5d-parse-pasted-handoff">Parse pasted handoff</button>
        </div>
        <p class="muted" style="font-size:0.75rem;margin-top:0.25rem;">Forbidden: file upload, file import, fetch from URL, backend submit, queue packet, save packet.</p>
      </div>
    </article>

    <article class="card phase5d-notes-panel" id="phase5d-notes-panel">
      <div class="card-head">
        <h3 class="card-title">Handoff Notes Panel</h3>
        <span class="badge info">NOTES</span>
      </div>
      <p class="card-body">Notes remain temporary and in-memory only. Use them to capture operator guidance, caveats, or merge-prep reminders that should travel with the final handoff text.</p>
      <label style="display:grid;gap:0.25rem;margin-top:0.75rem;">
        <span style="font-size:0.8rem;color:var(--muted);">Local Handoff Notes</span>
        <textarea id="phase5d-handoff-notes" class="table-filter" rows="8" placeholder="Type local handoff notes here..." style="width:100%;resize:vertical;font-family:var(--mono);font-size:0.85rem;min-height:180px;"></textarea>
      </label>
      <pre class="code-block" id="phase5d-handoff-notes-preview" style="max-height:240px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No notes captured yet.</pre>
    </article>

    <article class="card phase5d-implementation-prompt-preview" id="phase5d-implementation-prompt-panel">
      <div class="card-head">
        <h3 class="card-title">Implementation Prompt Preview</h3>
        <span class="badge info">PROMPT</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5d-copy-implementation-prompt">Copy implementation prompt</button>
      </div>
      <pre class="code-block" id="phase5d-implementation-prompt-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No handoff generated yet.</pre>
    </article>

    <article class="card phase5d-safety-summary-preview" id="phase5d-safety-summary-preview-panel">
      <div class="card-head">
        <h3 class="card-title">Safety Summary Preview</h3>
        <span class="badge pass">SAFE</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5d-copy-safety-summary">Copy safety summary</button>
      </div>
      <pre class="code-block" id="phase5d-safety-summary-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No handoff generated yet.</pre>
    </article>

    <article class="card phase5d-acceptance-checklist-preview" id="phase5d-acceptance-checklist-preview-panel">
      <div class="card-head">
        <h3 class="card-title">Acceptance Checklist Preview</h3>
        <span class="badge info">CHECKLIST</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5d-copy-acceptance-checklist">Copy acceptance checklist</button>
      </div>
      <pre class="code-block" id="phase5d-acceptance-checklist-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No handoff generated yet.</pre>
    </article>

    <article class="card phase5d-rollback-notes-preview" id="phase5d-rollback-notes-preview-panel">
      <div class="card-head">
        <h3 class="card-title">Rollback / No-Go Notes Preview</h3>
        <span class="badge warning">ROLLBACK</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5d-copy-rollback-notes">Copy rollback/no-go notes</button>
      </div>
      <pre class="code-block" id="phase5d-rollback-notes-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No handoff generated yet.</pre>
    </article>

    <article class="card phase5d-full-markdown-preview phase5d-wide-panel" id="phase5d-full-markdown-preview-panel">
      <div class="card-head">
        <h3 class="card-title">Full Handoff Markdown Preview</h3>
        <span class="badge info">MARKDOWN</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5d-copy-full-handoff-markdown">Copy full handoff Markdown</button>
      </div>
      <pre class="code-block" id="phase5d-full-markdown-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No handoff generated yet.</pre>
    </article>

  <article class="card phase5d-safety-summary" id="phase5d-safety-summary" style="margin-top:1rem;">
    <div class="card-head">
      <h3 class="card-title">Safety Summary Panel</h3>
      <span class="badge pass">SAFE</span>
    </div>
    <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%),200px));">
      <div class="stat"><span>Handoff state</span><strong>Temporary</strong></div>
      <div class="stat"><span>Composition</span><strong>Local only</strong></div>
      <div class="stat"><span>Saved anywhere</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Sent anywhere</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Queued</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Executed</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Backend write</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>GitHub mutation</span><strong class="badge fail">No</strong></div>
      <div class="stat"><span>Netlify mutation</span><strong class="badge fail">No</strong></div>
    </div>
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted">Handoff composition is temporary and in-memory only. The handoff package is generated locally and is copy/paste only. Nothing is saved. Nothing is sent. Nothing is queued. Nothing is executed. Nothing writes to the backend. Nothing mutates GitHub or Netlify. Refresh clears state unless copied manually.</p>
    </div>
  </article>
</div>
"""
    return _details(
        "Original Phase 5D — Client-Side Operator Handoff Composer",
        body,
        "source",
        open_by_default=True,
        panel_id="phase5d-handoff-composer"
    )


def _build_phase5e_runbook_simulator():
    body = """
<div class="phase5e-runbook-simulator" data-phase5e-runbook-simulator="true">
  <div class="callout" style="border-color: rgba(59,130,246,0.4); background: rgba(59,130,246,0.05);">
    <strong style="color: var(--accent);">CLIENT-SIDE RUNBOOK SIMULATOR</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      END-TO-END OPERATOR FLOW — SCENARIO PREVIEW ONLY — GENERATED LOCALLY — TEMPORARY IN-BROWSER STATE ONLY — NO PERSISTENCE — NO BACKEND WRITES — NO EXECUTION — NO MUTATION — NO DEPLOY / MERGE / PUSH / PR CONTROLS
    </p>
  </div>
  <p class="muted" style="margin-top: 0.25rem;">
    Client-Side End-to-End Operator Runbook & Scenario Simulator: Safe Status Review, Validator Review, Dashboard Polish Request, Safety Review Request, Forbidden Mutation Attempt.
  </p>

  <div class="phase5e-preview-grid">
    <article class="card phase5e-scenario-selector" id="phase5e-scenario-selector-panel">
      <div class="card-head">
        <h3 class="card-title">Scenario Selector Panel</h3>
        <span class="badge info">SCENARIOS</span>
      </div>
      <p class="card-body">Choose a safe local scenario preset to simulate the end-to-end operator flow across Phase 5A, 5B, 5C, and 5D.</p>
      <label style="display:grid;gap:0.25rem;margin-top:0.75rem;">
        <span style="font-size:0.8rem;color:var(--muted);">Scenario preset</span>
        <select id="phase5e-scenario-select" class="table-filter" style="width:100%;font-family:var(--mono);"></select>
      </label>
      <div class="stat-grid" id="phase5e-scenario-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));margin-top:0.75rem;"></div>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="phase5e-scenario-table">
          <caption>Local in-memory scenario presets</caption>
          <thead>
            <tr>
              <th scope="col">Scenario ID</th>
              <th scope="col">Title</th>
              <th scope="col">Workflow</th>
              <th scope="col">Request</th>
              <th scope="col">Risk</th>
              <th scope="col">Decision</th>
              <th scope="col">Handoff</th>
              <th scope="col">Safety Note</th>
            </tr>
          </thead>
          <tbody id="phase5e-scenario-body">
            <tr><td colspan="8" class="empty">No scenario selected yet.</td></tr>
          </tbody>
        </table>
      </div>
    </article>

    <article class="card phase5e-step-tracker" id="phase5e-step-tracker-panel">
      <div class="card-head">
        <h3 class="card-title">Runbook Step Tracker Panel</h3>
        <span class="badge info">FLOW</span>
      </div>
      <p class="card-body">The flow tracker shows each operator step, the simulated status, and whether the path is completed, pending, blocked, or warning-only.</p>
      <div class="stat-grid" id="phase5e-step-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));margin-top:0.75rem;"></div>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="phase5e-step-table">
          <caption>Simulated operator flow</caption>
          <thead>
            <tr>
              <th scope="col">Step</th>
              <th scope="col">Status</th>
              <th scope="col">Detail</th>
            </tr>
          </thead>
          <tbody id="phase5e-step-body">
            <tr><td colspan="3" class="empty">No simulated flow yet.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" id="phase5e-step-summary-text">Select a scenario to generate the local operator flow.</p>
      </div>
    </article>
  </div>

  <div class="phase5e-preview-grid">
    <article class="card phase5e-transcript-panel" id="phase5e-transcript-panel">
      <div class="card-head">
        <h3 class="card-title">Scenario Transcript Panel</h3>
        <span class="badge info">TRANSCRIPT</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5e-copy-transcript">Copy scenario transcript</button>
      </div>
      <pre class="code-block" id="phase5e-transcript-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No scenario selected yet.</pre>
    </article>

    <article class="card phase5e-safety-gate" id="phase5e-safety-gate-panel">
      <div class="card-head">
        <h3 class="card-title">Safety Gate Panel</h3>
        <span class="badge pass">SAFE</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="phase5e-copy-safety-gate">Copy safety gate summary</button>
      </div>
      <div class="stat-grid" id="phase5e-safety-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      <pre class="code-block" id="phase5e-safety-gate-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No scenario selected yet.</pre>
    </article>
  </div>

  <article class="card phase5e-runbook-preview phase5e-wide-panel" id="phase5e-runbook-preview-panel">
    <div class="card-head">
      <h3 class="card-title">Full Runbook Markdown Preview</h3>
      <span class="badge info">MARKDOWN</span>
    </div>
    <div class="button-row" style="margin-bottom:0.75rem;">
      <button type="button" class="copy-button small" id="phase5e-copy-runbook-markdown">Copy full runbook Markdown</button>
    </div>
    <pre class="code-block" id="phase5e-runbook-markdown-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No scenario selected yet.</pre>
  </article>

  <article class="card phase5e-safety-summary" id="phase5e-safety-summary" style="margin-top:1rem;">
    <div class="card-head">
      <h3 class="card-title">Safety Summary Panel</h3>
      <span class="badge pass">SAFE</span>
    </div>
    <div class="button-row" style="margin-bottom:0.75rem;">
      <button type="button" class="copy-button small" id="phase5e-copy-next-action">Copy next-action recommendation</button>
    </div>
    <div class="stat-grid" id="phase5e-summary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%),200px),1fr);"></div>
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted" id="phase5e-safety-summary-text">Scenario state is simulated locally. Runbook output is generated locally and is copy/paste only. Nothing is saved. Nothing is sent. Nothing is queued. Nothing is executed. Nothing writes to the backend. Nothing mutates GitHub or Netlify. Refresh clears state unless copied manually.</p>
    </div>
  </article>
</div>
"""
    return _details(
        "Original Phase 5E — Client-Side End-to-End Operator Runbook & Scenario Simulator",
        body,
        "source",
        open_by_default=True,
        panel_id="phase5e-runbook-simulator"
    )


def _build_plus1_controlled_automation_readiness_layer():
    body = """
<div class="plus1-readiness-layer" data-plus1-controlled-automation-readiness-layer="true">
  <div class="callout" style="border-color: rgba(14,165,233,0.4); background: rgba(14,165,233,0.05);">
    <strong style="color: var(--accent);">CONTROLLED AUTOMATION READINESS</strong>
    <p class="muted" style="margin-top: 0.25rem;">
      READINESS ONLY — NO LIVE AUTOMATION — NO EXECUTION — NO MUTATION — NO BACKEND WRITES — NO DEPLOY / MERGE / PUSH / PR CONTROLS — FUTURE AUTH / STORAGE / APPROVAL REQUIRED
    </p>
  </div>
  <p class="muted" style="margin-top: 0.25rem;">
    Original +1 — Controlled Automation Readiness Layer. This control-room shell defines future automation boundaries, role gates, dry-run evidence, and rollback/no-go contracts without enabling real execution.
  </p>

  <div class="plus1-preview-grid">
    <article class="card plus1-overview-panel" id="plus1-overview-panel">
      <div class="card-head">
        <h3 class="card-title">Automation Readiness Overview Panel</h3>
        <span class="badge info">READINESS ONLY</span>
      </div>
      <p class="card-body">Select a future-facing action, role, and gate state to preview how the readiness layer classifies automation without turning it on.</p>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="plus1-copy-readiness-summary">Copy automation readiness summary</button>
      </div>
      <div class="plus1-control-grid">
        <label class="plus1-control">
          <span>Action class</span>
          <select id="plus1-action-select" class="table-filter" style="width:100%;font-family:var(--mono);"></select>
        </label>
        <label class="plus1-control">
          <span>Role preview</span>
          <select id="plus1-role-select" class="table-filter" style="width:100%;font-family:var(--mono);"></select>
        </label>
        <label class="plus1-control">
          <span>Approval gate</span>
          <select id="plus1-approval-select" class="table-filter" style="width:100%;font-family:var(--mono);"></select>
        </label>
      </div>
      <div class="stat-grid" id="plus1-overview-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));margin-top:0.75rem;"></div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" id="plus1-overview-note">Original +1 remains readiness-only. Nothing executes, nothing mutates, and no future automation wiring is active yet.</p>
      </div>
    </article>

    <article class="card plus1-classification-matrix" id="plus1-classification-matrix-panel">
      <div class="card-head">
        <h3 class="card-title">Action Classification Matrix Panel</h3>
        <span class="badge info">MATRIX</span>
      </div>
      <p class="card-body">Map each action family to its current readiness posture, future dependency, gate requirement, and execution risk.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1-action-table">
          <caption>Action classification matrix</caption>
          <thead>
            <tr>
              <th scope="col">Action</th>
              <th scope="col">Allowed now</th>
              <th scope="col">Future auth</th>
              <th scope="col">Future storage</th>
              <th scope="col">Human gate</th>
              <th scope="col">Dry-run</th>
              <th scope="col">Mutation risk</th>
              <th scope="col">Execution risk</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody id="plus1-action-body">
            <tr><td colspan="9" class="empty">No action matrix yet.</td></tr>
          </tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1-preview-grid">
    <article class="card plus1-role-permission-panel" id="plus1-role-permission-panel">
      <div class="card-head">
        <h3 class="card-title">Role / Permission Readiness Panel</h3>
        <span class="badge info">ROLES</span>
      </div>
      <p class="card-body">The role matrix stays informational only. It shows which future responsibilities would need auth, approval, storage, and dry-run evidence.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1-role-table">
          <caption>Role and permission readiness matrix</caption>
          <thead>
            <tr>
              <th scope="col">Role</th>
              <th scope="col">View status</th>
              <th scope="col">Draft request</th>
              <th scope="col">Review packet</th>
              <th scope="col">Approve future action</th>
              <th scope="col">Execute now</th>
              <th scope="col">Mutate now</th>
              <th scope="col">Future auth</th>
            </tr>
          </thead>
          <tbody id="plus1-role-body">
            <tr><td colspan="8" class="empty">No role matrix yet.</td></tr>
          </tbody>
        </table>
      </div>
    </article>

    <article class="card plus1-approval-gate-panel" id="plus1-approval-gate-panel">
      <div class="card-head">
        <h3 class="card-title">Human Approval Gate Simulator Panel</h3>
        <span class="badge warning">GATE</span>
      </div>
      <p class="card-body">Approval states are display-only. They explain how future automation would pause for humans without turning on live action.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1-approval-table">
          <caption>Human approval gate states</caption>
          <thead>
            <tr>
              <th scope="col">State</th>
              <th scope="col">Meaning</th>
              <th scope="col">Live action?</th>
            </tr>
          </thead>
          <tbody id="plus1-approval-body">
            <tr><td colspan="3" class="empty">No gate state yet.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" id="plus1-approval-note">Approval does not execute, deploy, merge, push, or create PRs. It only documents the readiness boundary.</p>
      </div>
    </article>
  </div>

  <div class="plus1-preview-grid">
    <article class="card plus1-dry-run-plan-panel" id="plus1-dry-run-plan-panel">
      <div class="card-head">
        <h3 class="card-title">Dry-Run Plan Builder Panel</h3>
        <span class="badge info">DRY-RUN</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="plus1-copy-dry-run-plan">Copy dry-run plan</button>
      </div>
      <div class="stat-grid" id="plus1-dry-run-summary" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      <pre class="code-block" id="plus1-dry-run-plan-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No readiness action selected yet.</pre>
    </article>

    <article class="card plus1-preflight-panel" id="plus1-preflight-panel">
      <div class="card-head">
        <h3 class="card-title">Preflight Checklist Panel</h3>
        <span class="badge warning">CHECKLIST</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="plus1-copy-preflight-checklist">Copy preflight checklist</button>
      </div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;">
        <table class="data-table" id="plus1-preflight-table">
          <caption>Future automation preflight requirements</caption>
          <thead>
            <tr>
              <th scope="col">Requirement</th>
              <th scope="col">Status</th>
              <th scope="col">Why it matters</th>
            </tr>
          </thead>
          <tbody id="plus1-preflight-body">
            <tr><td colspan="3" class="empty">No preflight checklist yet.</td></tr>
          </tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1-preview-grid">
    <article class="card plus1-execution-boundary-panel" id="plus1-execution-boundary-panel">
      <div class="card-head">
        <h3 class="card-title">Execution Boundary Panel</h3>
        <span class="badge fail">NO LIVE ACTION</span>
      </div>
      <p class="card-body">This boundary exists to show what is still impossible in the current build. It should remain inert until a future implementation phase adds the required backend, auth, and audit systems.</p>
      <div class="stat-grid" id="plus1-boundary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" id="plus1-boundary-note">The current build cannot execute commands, mutate GitHub or Netlify, deploy, merge, push, create PRs, write backend data, store queues, or persist approvals.</p>
      </div>
    </article>

    <article class="card plus1-contract-builder" id="plus1-contract-builder-panel">
      <div class="card-head">
        <h3 class="card-title">Automation Handoff Contract Builder Panel</h3>
        <span class="badge info">CONTRACT</span>
      </div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="plus1-copy-handoff-contract">Copy automation handoff contract</button>
      </div>
      <pre class="code-block" id="plus1-contract-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No readiness action selected yet.</pre>
    </article>
  </div>

  <article class="card plus1-safety-summary" id="plus1-safety-summary-panel" style="margin-top:1rem;">
    <div class="card-head">
      <h3 class="card-title">Original +1 Safety Summary Panel</h3>
      <span class="badge pass">READINESS ONLY</span>
    </div>
    <div class="button-row" style="margin-bottom:0.75rem;">
      <button type="button" class="copy-button small" id="plus1-copy-safety-summary">Copy Original +1 safety summary</button>
    </div>
    <div class="stat-grid" id="plus1-safety-summary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted" id="plus1-safety-summary-text">Original +1 is readiness-only. Nothing is automated, nothing is executed, nothing is saved, nothing is sent, nothing writes to the backend, and nothing mutates GitHub or Netlify.</p>
    </div>
  </article>
</div>
"""
    return _details(
        "Original +1 — Controlled Automation Readiness Layer",
        body,
        "source",
        open_by_default=True,
        panel_id="plus1-controlled-automation-readiness-layer"
    )


def _build_plus1b_operator_console_contract_layer():
    body = """
<div class="plus1b-console-consolidation" data-plus1b-operator-console-contract-layer="true">
  <div class="callout" style="border-color: rgba(139,92,246,0.42); background: rgba(139,92,246,0.06);">
    <strong style="color: var(--accent-2);">OPERATOR CONSOLE CONSOLIDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">AUTOMATION CONTRACT LAYER</p>
    <p class="muted" style="margin-top: 0.25rem;">CONTRACTS ONLY — COPY/PASTE ONLY — READINESS ONLY — NO LIVE AUTOMATION — NO EXECUTION — NO MUTATION — NO BACKEND WRITES — NO DEPLOY / MERGE / PUSH / PR CONTROLS</p>
  </div>
  <p class="muted" style="margin-top: 0.25rem;">Original +1B — Operator Console Consolidation &amp; Automation Contract Layer. This layer consolidates the Phase 5A-5E workflow and the Original +1 readiness shell into one coherent operator console without enabling live automation.</p>

  <div class="plus1b-preview-grid">
    <article class="card plus1b-flow-rail" id="plus1b-flow-rail-panel">
      <div class="card-head"><h3 class="card-title">Unified Operator Flow Rail Panel</h3><span class="badge info">FLOW RAIL</span></div>
      <p class="card-body">Shows the operator sequence from Phase 5A through Original +1B with status, purpose, output type, boundary, and next handoff target.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1b-flow-table">
          <caption>Unified operator flow rail</caption>
          <thead><tr><th scope="col">Stage</th><th scope="col">Status</th><th scope="col">Purpose</th><th scope="col">Output type</th><th scope="col">Safety boundary</th><th scope="col">Next handoff</th></tr></thead>
          <tbody id="plus1b-flow-body"><tr><td colspan="6" class="empty">No flow rail yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1b-master-cockpit" id="plus1b-master-cockpit-panel">
      <div class="card-head"><h3 class="card-title">Master Cockpit Summary Panel</h3><span class="badge warning">COCKPIT</span></div>
      <p class="card-body">Summarises the readiness posture and the missing dependencies before any future real automation could be built.</p>
      <div class="stat-grid" id="plus1b-master-cockpit-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      <div class="callout" style="margin-top:0.75rem;"><p class="muted" id="plus1b-master-cockpit-note">The console remains readiness-only. Nothing executes, nothing mutates, and no backend dependency is live yet.</p></div>
    </article>
  </div>

  <div class="plus1b-preview-grid">
  <article class="card plus1b-contract-schema-panel" id="plus1b-contract-schema-panel">
      <div class="card-head"><h3 class="card-title">Formal Automation Contract Schema Panel</h3><span class="badge info">SCHEMA PACK</span></div>
      <p class="card-body">Static contract previews define the request, review, approval, dry-run, audit, and rollback shapes without enabling them.</p>
      <p class="muted" style="margin-top:-0.25rem;">Schema coverage: Request Packet Schema, Review Decision Schema, Decision Ledger Schema, Handoff Contract Schema, Runbook Scenario Schema, Automation Readiness Contract Schema, Approval Gate Contract Schema, Dry-Run Plan Schema, Preflight Checklist Schema, No-Go / Rollback Policy Schema.</p>
      <div class="button-row" style="margin-bottom:0.75rem;"><button type="button" class="section-button" id="plus1b-load-schema-pack-button">Load contract schema pack</button></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;">
        <table class="data-table" id="plus1b-contract-schema-table">
          <caption>Formal automation contract schemas</caption>
          <thead><tr><th scope="col">Schema</th><th scope="col">Version</th><th scope="col">Purpose</th><th scope="col">Required fields</th><th scope="col">Forbidden fields</th><th scope="col">Safety notes</th><th scope="col">Future dependency</th></tr></thead>
          <tbody id="plus1b-contract-schema-body"><tr><td colspan="7" class="empty">No contract schema pack loaded yet.</td></tr></tbody>
        </table>
      </div>
      <pre class="code-block" id="plus1b-contract-schema-preview" style="max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No contract schema pack loaded yet.</pre>
    </article>

    <article class="card plus1b-contract-builder" id="plus1b-contract-builder-panel">
      <div class="card-head"><h3 class="card-title">Automation Contract Builder Panel</h3><span class="badge info">CONTRACT</span></div>
      <p class="card-body">Generates copyable contract Markdown for the selected schema pack item and mode emphasis.</p>
      <pre class="code-block" id="plus1b-contract-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No contract selected yet.</pre>
    </article>
  </div>

  <div class="plus1b-preview-grid">
    <article class="card plus1b-copy-output-hub" id="plus1b-copy-output-hub-panel">
      <div class="card-head"><h3 class="card-title">Copy Output Hub Panel</h3><span class="badge pass">COPY/PASTE ONLY</span></div>
      <p class="card-body">Central copy buttons keep the operator outputs local, temporary, and easy to carry into the next planning step.</p>
      <div class="button-row" style="margin-bottom:0.5rem;">
        <button type="button" class="copy-button small" id="plus1b-copy-implementation-prompt">Copy implementation prompt</button>
        <button type="button" class="copy-button small" id="plus1b-copy-full-runbook">Copy full runbook</button>
        <button type="button" class="copy-button small" id="plus1b-copy-readiness-contract">Copy automation readiness contract</button>
        <button type="button" class="copy-button small" id="plus1b-copy-dry-run-plan">Copy dry-run plan</button>
        <button type="button" class="copy-button small" id="plus1b-copy-preflight-checklist">Copy preflight checklist</button>
        <button type="button" class="copy-button small" id="plus1b-copy-no-go-report">Copy no-go report</button>
        <button type="button" class="copy-button small" id="plus1b-copy-validator-checklist">Copy validator checklist</button>
        <button type="button" class="copy-button small" id="plus1b-copy-merge-readiness-summary" data-variant="schema preview">Copy merge-readiness summary</button>
      </div>
      <div class="callout"><p class="muted">Save, submit, queue, execute, deploy, merge, push, and create PR actions are absent by design.</p></div>
    </article>

    <article class="card plus1b-safety-boundary" id="plus1b-safety-boundary-panel">
      <div class="card-head"><h3 class="card-title">Master Safety Boundary Panel</h3><span class="badge fail">SAFETY</span></div>
      <p class="card-body">All outputs are local, temporary, and copy/paste only. Nothing is saved, submitted, queued, executed, or sent to any backend or external service.</p>
      <div class="stat-grid" id="plus1b-safety-boundary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));"></div>
      <div class="callout" style="margin-top:0.75rem;"><p class="muted" id="plus1b-safety-boundary-note">Future real automation requires separate auth, storage, audit, queue, approval, and backend write systems that are not present yet.</p></div>
    </article>
  </div>

  <div class="plus1b-preview-grid">
    <article class="card plus1b-validator-wall" id="plus1b-validator-wall-panel">
      <div class="card-head"><h3 class="card-title">Master Validator Wall Panel</h3><span class="badge warning">VALIDATORS</span></div>
      <p class="card-body">Summarises the validator families that must stay green before any merge or production review can be trusted.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1b-validator-wall-table">
          <caption>Phase 5 + Original +1 + Original +1B validator wall</caption>
          <thead><tr><th scope="col">Validator group</th><th scope="col">Pass string</th><th scope="col">Safety category</th><th scope="col">Before merge</th><th scope="col">Before production</th></tr></thead>
          <tbody id="plus1b-validator-wall-body"><tr><td colspan="5" class="empty">No validator wall yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1b-mode-emphasis" id="plus1b-mode-emphasis-panel">
      <div class="card-head"><h3 class="card-title">Mode Emphasis Panel</h3><span class="badge info">MODES</span></div>
      <p class="card-body">Planning, review, dry-run, handoff, readiness, and no-go modes are display-only. They change emphasis, not permissions.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1b-mode-table">
          <caption>Mode emphasis reference</caption>
          <thead><tr><th scope="col">Mode</th><th scope="col">Emphasizes</th><th scope="col">Does not enable</th><th scope="col">Useful copy outputs</th></tr></thead>
          <tbody id="plus1b-mode-body"><tr><td colspan="4" class="empty">No mode emphasis yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +1B — Operator Console Consolidation & Automation Contract Layer",
        body,
        "source",
        open_by_default=True,
        panel_id="plus1b-operator-console-contract-layer"
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
        <li><strong>Original +1B</strong> — Operator Console Consolidation &amp; Automation Contract Layer (ACTIVE)</li>
      </ul>
      <p class="muted">Original Phase 4 — Hosted / Production Dashboard Polish remains the hosted dashboard baseline.</p>
      <p style="margin-top: 1rem;"><strong>Current active direction:</strong> Original +1B — Operator Console Consolidation &amp; Automation Contract Layer</p>
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
        <p class="lede">A read-only production dashboard for reviewing system status, safety boundaries, static schemas, and operator workflow readiness. Includes Original Phase 5A client-side operator workflow shell, Phase 5B request packet builder, Phase 5C review board, Phase 5D handoff composer, Phase 5E runbook simulator, Original +1 controlled automation readiness layer, and Original +1B operator console contract layer.</p>
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
        _build_phase5b_request_packet_builder(),
        _build_phase5c_review_board(),
        _build_phase5d_handoff_composer(),
        _build_phase5e_runbook_simulator(),
        _build_plus1_controlled_automation_readiness_layer(),
        _build_plus1b_operator_console_contract_layer(),
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
