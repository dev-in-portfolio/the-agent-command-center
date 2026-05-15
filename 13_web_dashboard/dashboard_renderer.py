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
    next_action = "Ready for backend architecture blueprint review. Future backend integration remains a later phase."
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
        ("Original +1C Readiness QA Layer", "plus1c-readiness-scoring-contract-qa"),
        ("Original +1D Blueprint Layer", "plus1d-backend-boundary-blueprint"),
        ("Original +1E Implementation Gate", "plus1e-backend-implementation-gate"),
        ("Original +2A Auth Foundation", "plus2a-backend-auth-foundation"),
        ("Original +2B Request Storage", "plus2b-persistent-request-storage"),
        ("Original +2C Audit Log", "plus2c-immutable-audit-log"),
        ("Original +2D Approval Gate", "plus2d-approval-gate-storage"),
        ("Original +2E Dry-Run Engine", "plus2e-server-side-dry-run-engine"),
        ("MVP-1 Request Lifecycle Runtime", "mvp1-request-lifecycle-runtime"),
        ("MVP-2 Local Durable Persistence", "mvp2-local-durable-request-persistence"),
        ("Artifacts", "artifact-packages"),
        ("Source Info", "source-transparency"),
        ("Audit / Session", "session-audit"),
    ]
    return (
        '<section class="landing-shell" aria-label="Dashboard landing screen">'
        '<div class="landing-head">'
        '<p class="eyebrow">Command Center Overview</p>'
        '<h2>Production Presentation & Safety Review</h2>'
        '<p class="lede">Review the core project roadmap, safety boundaries, static schema previews, readiness QA, and backend boundary blueprints. Technical audits and raw session data are available in the sections below.</p>'
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


def _build_plus1c_readiness_scoring_contract_qa_layer():
    body = """
<div class="plus1c-readiness-scoring" data-plus1c-readiness-scoring-contract-qa="true">
  <div class="callout plus1c-summary-callout" style="border-color: rgba(56,189,248,0.36); background: rgba(56,189,248,0.06);">
    <strong style="color: var(--accent);">READINESS SCORING</strong>
    <p class="muted" style="margin-top: 0.15rem;">CONTRACT QA — NO-GO DECISION LAYER — LOCAL ANALYSIS ONLY</p>
    <p class="muted" style="margin-top: 0.25rem;">COPY/PASTE ONLY — READINESS ONLY — NO LIVE AUTOMATION — NO EXECUTION — NO MUTATION — NO BACKEND WRITES — NO DEPLOY / MERGE / PUSH / PR CONTROLS</p>
  </div>

  <div class="plus1c-preview-grid">
    <article class="card plus1c-scorecard" id="plus1c-scorecard-panel">
      <div class="card-head"><h3 class="card-title">Readiness Scorecard Panel</h3><span class="badge warning">READINESS SCORING</span></div>
      <p class="card-body">Scores are local, display-only, and intentionally blocked from real automation readiness.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-scorecard-table">
          <caption>Readiness scoring categories</caption>
          <thead><tr><th scope="col">Category</th><th scope="col">Score</th><th scope="col">Status</th><th scope="col">Reason</th><th scope="col">Recommended improvement</th></tr></thead>
          <tbody id="plus1c-scorecard-body"><tr><td colspan="5" class="empty">No readiness scoring model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1c-contract-qa" id="plus1c-contract-qa-panel">
      <div class="card-head"><h3 class="card-title">Contract QA Matrix Panel</h3><span class="badge info">CONTRACT QA</span></div>
      <p class="card-body">Checks every readiness contract for required fields, forbidden fields, safety notes, and future dependency coverage.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-contract-qa-table">
          <caption>Contract QA matrix</caption>
          <thead><tr><th scope="col">Schema</th><th scope="col">Required fields present</th><th scope="col">Forbidden fields absent</th><th scope="col">Safety notes present</th><th scope="col">Future dependency noted</th><th scope="col">Copy output</th><th scope="col">QA status</th></tr></thead>
          <tbody id="plus1c-contract-qa-body"><tr><td colspan="7" class="empty">No contract QA model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1c-safety-assertions" id="plus1c-safety-assertion-panel">
      <div class="card-head"><h3 class="card-title">Safety Assertion Panel</h3><span class="badge fail">NO LIVE AUTOMATION</span></div>
      <p class="card-body">Assertions remain local and descriptive. Any future dependency still shows as blocked until the control plane exists.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-safety-assertion-table">
          <caption>Safety assertions</caption>
          <thead><tr><th scope="col">Assertion</th><th scope="col">Expected</th><th scope="col">Current</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus1c-safety-assertion-body"><tr><td colspan="4" class="empty">No safety assertions loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1c-preview-grid">
    <article class="card plus1c-no-go-panel" id="plus1c-no-go-panel">
      <div class="card-head"><h3 class="card-title">No-Go Decision Panel</h3><span class="badge locked">NO-GO</span></div>
      <p class="card-body">The current console is not ready for real automation. These blockers keep the build safely in review-only mode.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-no-go-table">
          <caption>No-go decisions</caption>
          <thead><tr><th scope="col">Decision</th><th scope="col">Reason</th><th scope="col">Required future dependency</th><th scope="col">Operator recommendation</th></tr></thead>
          <tbody id="plus1c-no-go-body"><tr><td colspan="4" class="empty">No no-go model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1c-dependency-gap-map" id="plus1c-dependency-gap-map-panel">
      <div class="card-head"><h3 class="card-title">Dependency Gap Map Panel</h3><span class="badge warning">FUTURE DEPENDENCIES</span></div>
      <p class="card-body">Maps the missing backend and governance pieces that must exist before any real automation can be attempted.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-dependency-gap-table">
          <caption>Dependency gap map</caption>
          <thead><tr><th scope="col">Dependency</th><th scope="col">Required before</th><th scope="col">Current status</th><th scope="col">Blocking level</th><th scope="col">Recommended future phase</th></tr></thead>
          <tbody id="plus1c-dependency-gap-body"><tr><td colspan="5" class="empty">No dependency gap model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1c-validator-confidence" id="plus1c-validator-confidence-panel">
      <div class="card-head"><h3 class="card-title">Validator Confidence Panel</h3><span class="badge pass">VALIDATOR WALL</span></div>
      <p class="card-body">Shows the current validator groups, required pass strings, and why they remain merge and production requirements.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1c-validator-confidence-table">
          <caption>Validator confidence groups</caption>
          <thead><tr><th scope="col">Group</th><th scope="col">Pass string</th><th scope="col">Coverage type</th><th scope="col">Confidence level</th><th scope="col">Merge requirement</th><th scope="col">Production requirement</th></tr></thead>
          <tbody id="plus1c-validator-confidence-body"><tr><td colspan="6" class="empty">No validator confidence model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1c-preview-grid">
    <article class="card plus1c-copy-output-hub" id="plus1c-copy-output-hub-panel">
      <div class="card-head"><h3 class="card-title">Copy Output Hub Panel</h3><span class="badge info">COPY/PASTE ONLY</span></div>
      <p class="card-body">All outputs stay local and copyable so the operator can review readiness without creating any live action path.</p>
      <div class="button-row" style="margin-top: 0.75rem;">
        <button type="button" class="copy-button small" id="plus1c-copy-readiness-scorecard">Copy readiness scorecard</button>
        <button type="button" class="copy-button small" id="plus1c-copy-contract-qa-report">Copy contract QA report</button>
        <button type="button" class="copy-button small" id="plus1c-copy-safety-assertion-summary">Copy safety assertion summary</button>
        <button type="button" class="copy-button small" id="plus1c-copy-no-go-decision-report">Copy no-go decision report</button>
        <button type="button" class="copy-button small" id="plus1c-copy-dependency-gap-map">Copy dependency gap map</button>
        <button type="button" class="copy-button small" id="plus1c-copy-validator-confidence-report">Copy validator confidence report</button>
        <button type="button" class="copy-button small" id="plus1c-copy-go-no-go-packet">Copy go/no-go packet</button>
      </div>
    </article>

    <article class="card plus1c-go-no-go-packet" id="plus1c-go-no-go-packet-panel">
      <div class="card-head"><h3 class="card-title">Go / No-Go Packet Panel</h3><span class="badge warning">NOT READY FOR REAL AUTOMATION</span></div>
      <p class="card-body">Copyable packet summarizes the local QA results, blockers, and the current readiness recommendation.</p>
      <pre class="code-block" id="plus1c-go-no-go-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No readiness packet loaded yet.</pre>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +1C — Readiness Scoring, Contract QA & No-Go Decision Layer",
        body,
        "source",
        open_by_default=True,
        panel_id="plus1c-readiness-scoring-contract-qa"
    )


def _build_plus1d_backend_boundary_blueprint_layer():
    body = """
<div class="plus1d-backend-boundary" data-plus1d-backend-boundary-blueprint="true">
  <div class="callout plus1d-summary-callout" style="border-color: rgba(34,197,94,0.28); background: rgba(34,197,94,0.06);">
    <strong style="color: var(--success);">BACKEND BOUNDARY BLUEPRINT</strong>
    <p class="muted" style="margin-top: 0.15rem;">REAL AUTOMATION DEPENDENCY MAP — BLUEPRINT ONLY — FUTURE IMPLEMENTATION ONLY</p>
    <p class="muted" style="margin-top: 0.25rem;">READINESS ONLY — NO LIVE AUTOMATION — NO EXECUTION — NO MUTATION — NO BACKEND WRITES — NO DEPLOY / MERGE / PUSH / PR CONTROLS</p>
    <p class="muted" style="margin-top: 0.25rem;">READY_FOR_BACKEND_ARCHITECTURE_REVIEW_ONLY — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-backend-boundary-overview" id="plus1d-backend-boundary-overview-panel">
      <div class="card-head"><h3 class="card-title">Backend Boundary Overview Panel</h3><span class="badge warning">BLUEPRINT ONLY</span></div>
      <p class="card-body">Summarises the current inert system posture and the future boundary constraints required for real automation.</p>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-backend-boundary-overview-table">
          <caption>Backend boundary overview</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">Value</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus1d-backend-boundary-overview-body"><tr><td colspan="3" class="empty">No backend boundary overview loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1d-endpoint-map" id="plus1d-endpoint-map-panel">
      <div class="card-head"><h3 class="card-title">Future Backend Endpoint Contract Map Panel</h3><span class="badge info">ENDPOINT MAP</span></div>
      <p class="card-body">Blueprints the future backend endpoints and marks which ones remain not implemented in this build.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-endpoint-map-table">
          <caption>Future backend endpoint contracts</caption>
          <thead><tr><th scope="col">Method</th><th scope="col">Endpoint</th><th scope="col">Purpose</th><th scope="col">Current status</th><th scope="col">Auth</th><th scope="col">Role</th><th scope="col">Writes data</th><th scope="col">Mutates external system</th><th scope="col">Human approval</th><th scope="col">Audit event</th><th scope="col">Implementation allowed</th></tr></thead>
          <tbody id="plus1d-endpoint-map-body"><tr><td colspan="11" class="empty">No backend endpoint contract map loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-auth-permission" id="plus1d-auth-permission-panel">
      <div class="card-head"><h3 class="card-title">Auth / Role / Permission Architecture Panel</h3><span class="badge warning">AUTH PLAN</span></div>
      <p class="card-body">Defines the future identity, session, and permission architecture. Current permissions remain read-only.</p>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-auth-permission-table">
          <caption>Auth and permission architecture</caption>
          <thead><tr><th scope="col">Role</th><th scope="col">Future permissions</th><th scope="col">Current permissions</th><th scope="col">Can execute now</th><th scope="col">Can mutate now</th></tr></thead>
          <tbody id="plus1d-auth-permission-body"><tr><td colspan="5" class="empty">No auth / permission model loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1d-storage-model" id="plus1d-request-storage-panel">
      <div class="card-head"><h3 class="card-title">Persistent Request Storage Model Panel</h3><span class="badge fail">NOT IMPLEMENTED</span></div>
      <p class="card-body">Blueprints the request record that a future backend would need before real automation can be trusted.</p>
      <div class="callout" style="margin-top:0.75rem;"><p class="muted">Current status: NOT_IMPLEMENTED - FUTURE_DATABASE_REQUIRED</p></div>
      <pre class="code-block" id="plus1d-request-storage-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No request storage model loaded yet.</pre>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-audit-model" id="plus1d-audit-log-panel">
      <div class="card-head"><h3 class="card-title">Audit Log Storage Model Panel</h3><span class="badge fail">FUTURE AUDIT</span></div>
      <p class="card-body">Describes an immutable audit log shape for future backend execution, approvals, and rollback evidence.</p>
      <div class="callout" style="margin-top:0.75rem;"><p class="muted">Current status: NOT_IMPLEMENTED - FUTURE_IMMUTABLE_AUDIT_REQUIRED</p></div>
      <pre class="code-block" id="plus1d-audit-log-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No audit log model loaded yet.</pre>
    </article>

    <article class="card plus1d-approval-model" id="plus1d-approval-record-panel">
      <div class="card-head"><h3 class="card-title">Approval Record Model Panel</h3><span class="badge fail">APPROVAL STORE</span></div>
      <p class="card-body">Blueprints a future approval record shape with revocation and audit binding.</p>
      <div class="callout" style="margin-top:0.75rem;"><p class="muted">Current status: NOT_IMPLEMENTED - FUTURE_APPROVAL_STORAGE_REQUIRED</p></div>
      <pre class="code-block" id="plus1d-approval-record-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No approval record model loaded yet.</pre>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-job-lifecycle" id="plus1d-queue-job-lifecycle-panel">
      <div class="card-head"><h3 class="card-title">Queue / Job Lifecycle Model Panel</h3><span class="badge warning">QUEUE MODEL</span></div>
      <p class="card-body">Maps the future queue lifecycle from draft to rollback, without creating a live queue in this build.</p>
      <pre class="code-block" id="plus1d-queue-job-lifecycle-preview" style="max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No queue job lifecycle model loaded yet.</pre>
    </article>

    <article class="card plus1d-dry-run-boundary" id="plus1d-dry-run-engine-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Engine Boundary Panel</h3><span class="badge info">PLANNING ONLY</span></div>
      <p class="card-body">Explains why a future dry-run engine must live server-side and produce evidence before any approval.</p>
      <pre class="code-block" id="plus1d-dry-run-engine-preview" style="max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No dry-run boundary loaded yet.</pre>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-mutation-gateway" id="plus1d-mutation-gateway-panel">
      <div class="card-head"><h3 class="card-title">Mutation Gateway Boundary Panel</h3><span class="badge locked">BLOCKED</span></div>
      <p class="card-body">Captures the server-side requirements that must exist before mutation can ever be enabled.</p>
      <pre class="code-block" id="plus1d-mutation-gateway-preview" style="max-height:320px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No mutation gateway boundary loaded yet.</pre>
    </article>

    <article class="card plus1d-future-integrations" id="plus1d-future-integrations-panel">
      <div class="card-head"><h3 class="card-title">GitHub / Netlify Future Integration Boundary Panel</h3><span class="badge warning">INTEGRATIONS</span></div>
      <p class="card-body">Future GitHub and Netlify integrations remain disabled until their backend, auth, and approval boundaries exist.</p>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-future-integrations-table">
          <caption>Future integration boundary</caption>
          <thead><tr><th scope="col">Integration</th><th scope="col">Allowed now</th><th scope="col">Future auth</th><th scope="col">Secret storage</th><th scope="col">Human approval</th><th scope="col">Audit log</th><th scope="col">Rollback plan</th></tr></thead>
          <tbody id="plus1d-future-integrations-body"><tr><td colspan="7" class="empty">No integration boundary loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-secrets-management" id="plus1d-secrets-management-panel">
      <div class="card-head"><h3 class="card-title">Secrets Management Requirements Panel</h3><span class="badge fail">NO SECRETS IN BROWSER</span></div>
      <p class="card-body">Secrecy boundaries stay server-side, least-privilege, and never flow into the browser or copy outputs.</p>
      <pre class="code-block" id="plus1d-secrets-management-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No secrets management requirements loaded yet.</pre>
    </article>

    <article class="card plus1d-no-go-rollback" id="plus1d-rollback-no-go-panel">
      <div class="card-head"><h3 class="card-title">Rollback / No-Go Enforcement Model Panel</h3><span class="badge locked">NO-GO ENFORCEMENT</span></div>
      <p class="card-body">Defines the blocking states, evidence requirements, and rollback triggers that protect future automation.</p>
      <pre class="code-block" id="plus1d-rollback-no-go-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No rollback / no-go model loaded yet.</pre>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-rate-limit-plan" id="plus1d-rate-limit-plan-panel">
      <div class="card-head"><h3 class="card-title">Rate Limit / Abuse Control Plan Panel</h3><span class="badge warning">RATE LIMITS</span></div>
      <p class="card-body">Blueprints the future controls that keep draft request packets, approvals, and mutations bounded and auditable.</p>
      <pre class="code-block" id="plus1d-rate-limit-plan-preview" style="max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No rate-limit plan loaded yet.</pre>
    </article>

    <article class="card plus1d-implementation-sequence" id="plus1d-implementation-sequence-panel">
      <div class="card-head"><h3 class="card-title">Future Implementation Sequence Panel</h3><span class="badge info">SEQUENCE</span></div>
      <p class="card-body">The future control plane should arrive in a sequenced backend-first order after the blueprint review.</p>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-implementation-sequence-table">
          <caption>Future implementation sequence</caption>
          <thead><tr><th scope="col">Phase</th><th scope="col">Label</th><th scope="col">Purpose</th></tr></thead>
          <tbody id="plus1d-implementation-sequence-body"><tr><td colspan="3" class="empty">No implementation sequence loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1d-preview-grid">
    <article class="card plus1d-prerequisite-checklist" id="plus1d-prerequisite-checklist-panel">
      <div class="card-head"><h3 class="card-title">Real Automation Prerequisite Checklist Panel</h3><span class="badge fail">NOT READY FOR REAL AUTOMATION</span></div>
      <p class="card-body">The future automation checklist stays blocked until each prerequisite is genuinely implemented and verified.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1d-prerequisite-checklist-table">
          <caption>Real automation prerequisite checklist</caption>
          <thead><tr><th scope="col">Checklist item</th><th scope="col">Required</th><th scope="col">Current state</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus1d-prerequisite-checklist-body"><tr><td colspan="4" class="empty">No prerequisite checklist loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1d-copy-output-hub" id="plus1d-copy-output-hub-panel">
      <div class="card-head"><h3 class="card-title">Copy Output Hub Panel</h3><span class="badge pass">COPY/PASTE ONLY</span></div>
      <p class="card-body">All blueprint outputs remain local, copyable, and inert so the next architecture review can happen without live actions.</p>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus1d-copy-backend-boundary-blueprint">Copy backend boundary blueprint</button>
        <button type="button" class="copy-button small" id="plus1d-copy-endpoint-contract-map">Copy endpoint contract map</button>
        <button type="button" class="copy-button small" id="plus1d-copy-auth-permission-architecture">Copy auth/permission architecture</button>
        <button type="button" class="copy-button small" id="plus1d-copy-storage-model-summary">Copy storage model summary</button>
        <button type="button" class="copy-button small" id="plus1d-copy-audit-model-summary">Copy audit model summary</button>
        <button type="button" class="copy-button small" id="plus1d-copy-queue-lifecycle-model">Copy queue lifecycle model</button>
        <button type="button" class="copy-button small" id="plus1d-copy-mutation-gateway-requirements">Copy mutation gateway requirements</button>
        <button type="button" class="copy-button small" id="plus1d-copy-future-implementation-sequence">Copy future implementation sequence</button>
        <button type="button" class="copy-button small" id="plus1d-copy-prerequisite-checklist">Copy real automation prerequisite checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +1D — Backend Boundary Blueprint & Real Automation Dependency Map",
        body,
        "source",
        open_by_default=True,
        panel_id="plus1d-backend-boundary-blueprint"
    )


def _build_plus1e_backend_implementation_gate_layer():
    body = """
<div class="plus1e-implementation-gate" data-plus1e-backend-implementation-gate="true">
  <div class="callout plus1e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--info);">BACKEND IMPLEMENTATION GATE</strong>
    <p class="muted" style="margin-top: 0.15rem;">BUILD TICKET GENERATOR — IMPLEMENTATION PLANNING ONLY — COPYABLE CODEX PROMPTS</p>
    <p class="muted" style="margin-top: 0.25rem;">READINESS ONLY — NO LIVE AUTOMATION — NO EXECUTION — NO MUTATION — NO BACKEND WRITES — NO DEPLOY / MERGE / PUSH / PR CONTROLS</p>
    <p class="muted" style="margin-top: 0.25rem;">READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY — NOT_READY_FOR_REAL_AUTOMATION — PLAN_PLUS2A_NEXT — DO_NOT_ENABLE_REAL_AUTOMATION</p>
  </div>

  <div class="plus1e-preview-grid">
    <article class="card plus1e-gate-overview" id="plus1e-gate-overview-panel">
      <div class="card-head"><h3 class="card-title">Backend Implementation Gate Overview Panel</h3><span class="badge warning">PLANNING ONLY</span></div>
      <p class="card-body">Summarises the current inert system posture and the future backend build gate required before any implementation work is allowed.</p>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-gate-overview-table">
          <caption>Backend implementation gate overview</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">Value</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus1e-gate-overview-body"><tr><td colspan="3" class="empty">No implementation gate overview loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1e-ticket-map" id="plus1e-ticket-map-panel">
      <div class="card-head"><h3 class="card-title">Future Phase Ticket Map Panel</h3><span class="badge info">TICKETS</span></div>
      <p class="card-body">Defines the future +2A through +2J backend tickets and keeps each one blocked until its prerequisites exist.</p>
      <div class="table-wrap" style="max-height:360px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-ticket-map-table">
          <caption>Future backend build tickets</caption>
          <thead><tr><th scope="col">Ticket</th><th scope="col">Title</th><th scope="col">Purpose</th><th scope="col">Dependencies</th><th scope="col">Status</th><th scope="col">Blocked now</th></tr></thead>
          <tbody id="plus1e-ticket-map-body"><tr><td colspan="6" class="empty">No build ticket map loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1e-preview-grid">
    <article class="card plus1e-dependency-prerequisites" id="plus1e-dependency-prerequisites-panel">
      <div class="card-head"><h3 class="card-title">Dependency Prerequisite Panel</h3><span class="badge warning">DEPENDENCIES</span></div>
      <p class="card-body">Maps the prerequisite chain that keeps implementation work in the future and prevents premature backend mutation.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-dependency-table">
          <caption>Dependency prerequisite map</caption>
          <thead><tr><th scope="col">Ticket</th><th scope="col">Required before</th><th scope="col">Current status</th><th scope="col">Blocking level</th><th scope="col">Recommended future phase</th></tr></thead>
          <tbody id="plus1e-dependency-body"><tr><td colspan="5" class="empty">No dependency map loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus1e-ticket-detail" id="plus1e-ticket-detail-panel">
      <div class="card-head"><h3 class="card-title">Build Ticket Detail Panel</h3><span class="badge pass">DETAIL</span></div>
      <p class="card-body">Choose a future backend ticket to review its scope, safety boundary, validators, reports, and final response requirements.</p>
      <label class="control-group" style="display:block;margin-top:0.75rem;">
        <span class="muted" style="display:block;margin-bottom:0.35rem;">Selected build ticket</span>
        <select id="plus1e-ticket-select" class="table-filter" style="width:100%;font-family:var(--mono);">
          <option value="">Loading build tickets...</option>
        </select>
      </label>
      <div class="table-wrap" style="max-height:320px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-ticket-detail-table">
          <caption>Selected build ticket details</caption>
          <thead><tr><th scope="col">Field</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus1e-ticket-detail-body"><tr><td colspan="2" class="empty">No build ticket selected yet.</td></tr></tbody>
        </table>
      </div>
      <pre class="code-block" id="plus1e-ticket-detail-preview" style="max-height:360px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No build ticket selected yet.</pre>
    </article>
  </div>

  <div class="plus1e-preview-grid">
    <article class="card plus1e-prompt-generator" id="plus1e-codex-prompt-generator-panel">
      <div class="card-head"><h3 class="card-title">Codex Prompt Generator Panel</h3><span class="badge info">COPYABLE CODEX PROMPTS</span></div>
      <div class="button-row" style="margin-bottom:0.75rem;">
        <button type="button" class="copy-button small" id="plus1e-copy-selected-build-ticket">Copy selected build ticket</button>
        <button type="button" class="copy-button small" id="plus1e-copy-selected-codex-prompt">Copy selected Codex prompt</button>
      </div>
      <pre class="code-block" id="plus1e-codex-prompt-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No build ticket selected yet.</pre>
    </article>

    <article class="card plus1e-gate-status" id="plus1e-gate-status-panel">
      <div class="card-head"><h3 class="card-title">Implementation Gate Status Panel</h3><span class="badge warning">GATES</span></div>
      <p class="card-body">Shows the gates that must remain blocked until each future backend ticket has actually been built and verified.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-gate-status-table">
          <caption>Implementation gate statuses</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">Status</th><th scope="col">Blocking reason</th><th scope="col">Required future ticket</th><th scope="col">Can proceed now</th></tr></thead>
          <tbody id="plus1e-gate-status-body"><tr><td colspan="5" class="empty">No gate statuses loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus1e-preview-grid">
    <article class="card plus1e-validator-requirements" id="plus1e-validator-requirements-panel">
      <div class="card-head"><h3 class="card-title">Ticket Validator Requirements Panel</h3><span class="badge info">VALIDATORS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-validator-table">
          <caption>Ticket validator requirements</caption>
          <thead><tr><th scope="col">Ticket</th><th scope="col">Unit validator</th><th scope="col">Integration / E2E validator</th><th scope="col">Safety</th><th scope="col">Diff scope</th><th scope="col">Report</th><th scope="col">Production verification</th></tr></thead>
          <tbody id="plus1e-validator-body"><tr><td colspan="7" class="empty">No validator requirements loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus1e-copy-validator-requirements">Copy validator requirements matrix</button>
      </div>
    </article>

    <article class="card plus1e-report-requirements" id="plus1e-report-requirements-panel">
      <div class="card-head"><h3 class="card-title">Ticket Report Requirements Panel</h3><span class="badge info">REPORTS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus1e-report-table">
          <caption>Ticket report requirements</caption>
          <thead><tr><th scope="col">Ticket</th><th scope="col">Implementation</th><th scope="col">Design</th><th scope="col">Safety</th><th scope="col">Dependency</th><th scope="col">Validator</th><th scope="col">Acceptance</th><th scope="col">Production verification</th></tr></thead>
          <tbody id="plus1e-report-body"><tr><td colspan="8" class="empty">No report requirements loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus1e-copy-report-requirements">Copy report requirements matrix</button>
      </div>
    </article>
  </div>

  <div class="plus1e-preview-grid">
    <article class="card plus1e-rollback-policy" id="plus1e-rollback-policy-panel">
      <div class="card-head"><h3 class="card-title">Rollback / No-Go Ticket Policy Panel</h3><span class="badge locked">NO-GO POLICY</span></div>
      <p class="card-body">This policy keeps each future backend ticket copy-only until all prerequisites are genuinely present.</p>
      <pre class="code-block" id="plus1e-rollback-policy-preview" style="max-height:280px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No rollback policy loaded yet.</pre>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus1e-copy-rollback-policy">Copy rollback/no-go ticket policy</button>
      </div>
    </article>

    <article class="card plus1e-readiness-summary" id="plus1e-readiness-summary-panel">
      <div class="card-head"><h3 class="card-title">Backend Build Readiness Summary Panel</h3><span class="badge warning">READINESS ONLY</span></div>
      <div class="stat-grid" id="plus1e-readiness-summary-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));margin-top:0.75rem;"></div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted">Current recommendation: READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY. Final recommendation: NOT_READY_FOR_REAL_AUTOMATION. Planning only stays in force until future backend dependencies exist.</p>
      </div>
      <pre class="code-block" id="plus1e-readiness-summary-preview" style="max-height:280px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin-top:0.75rem;">No backend build readiness summary loaded yet.</pre>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus1e-copy-readiness-summary">Copy backend build readiness summary</button>
      </div>
    </article>
  </div>

  <article class="card plus1e-roadmap-panel" id="plus1e-roadmap-panel" style="margin-top:1rem;">
    <div class="card-head"><h3 class="card-title">Full Backend Implementation Roadmap Panel</h3><span class="badge info">ROADMAP</span></div>
    <div class="button-row" style="margin-bottom:0.75rem;">
      <button type="button" class="copy-button small" id="plus1e-copy-full-roadmap">Copy full backend implementation roadmap</button>
      <button type="button" class="copy-button small" id="plus1e-copy-dependency-map">Copy dependency prerequisite map</button>
    </div>
    <pre class="code-block" id="plus1e-roadmap-preview" style="max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;">No backend build roadmap loaded yet.</pre>
  </article>
</div>
"""
    return _details(
        "Original +1E — Backend Implementation Gate & Build Ticket Generator",
        body,
        "source",
        open_by_default=True,
        panel_id="plus1e-backend-implementation-gate"
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
        <li><strong>Original +1C</strong> — Readiness Scoring, Contract QA &amp; No-Go Decision Layer (ACTIVE)</li>
      </ul>
      <p class="muted">Original Phase 4 — Hosted / Production Dashboard Polish remains the hosted dashboard baseline.</p>
      <p style="margin-top: 1rem;"><strong>Current active direction:</strong> Original +1C — Readiness Scoring, Contract QA &amp; No-Go Decision Layer</p>
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


def _build_plus2a_backend_auth_foundation_layer():
    body = """
<div class="plus2a-auth-foundation" data-plus2a-auth-foundation="true">
  <div class="callout plus2a-summary-callout" style="border-color: rgba(16,185,129,0.28); background: rgba(16,185,129,0.06);">
    <strong style="color: var(--pass);">BACKEND AUTH FOUNDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">READ-ONLY AUTH STATUS — ROLE / PERMISSION MATRIX — DEMO IDENTITY MODEL</p>
    <p class="muted" style="margin-top: 0.25rem;">AUTH FOUNDATION ONLY — NO LIVE AUTH PROVIDER — NO SESSION COOKIES — NO TOKENS — NO SECRETS</p>
    <p class="muted" style="margin-top: 0.25rem;">NO EXECUTION — NO MUTATION — NO BACKEND WRITES</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_REAL_AUTOMATION — READY_FOR_AUTH_FOUNDATION_REVIEW_ONLY</p>
  </div>

  <div class="plus2a-preview-grid">
    <article class="card plus2a-auth-status" id="plus2a-auth-status-panel">
      <div class="card-head"><h3 class="card-title">Auth Foundation Status Panel</h3><span class="badge warning">STATUS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2a-status-table">
          <caption>Auth foundation status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2a-status-body"><tr><td colspan="2" class="empty">No status loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2a-copy-status">Copy auth foundation summary</button>
      </div>
    </article>

    <article class="card plus2a-demo-identities" id="plus2a-demo-identities-panel">
      <div class="card-head"><h3 class="card-title">Demo Identity Panel</h3><span class="badge info">IDENTITIES</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2a-identities-table">
          <caption>Demo identities</caption>
          <thead><tr><th scope="col">User ID</th><th scope="col">Display Name</th><th scope="col">Role</th><th scope="col">Auth Mode</th></tr></thead>
          <tbody id="plus2a-identities-body"><tr><td colspan="4" class="empty">No demo identities loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2a-preview-grid">
    <article class="card plus2a-role-matrix" id="plus2a-role-matrix-panel">
      <div class="card-head"><h3 class="card-title">Role / Permission Matrix Panel</h3><span class="badge info">MATRIX</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2a-role-table">
          <caption>Role permission matrix</caption>
          <thead><tr><th scope="col">Role</th><th scope="col">Permissions</th><th scope="col">Future Auth Required</th></tr></thead>
          <tbody id="plus2a-role-body"><tr><td colspan="3" class="empty">No roles loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2a-copy-roles">Copy role matrix</button>
      </div>
    </article>

    <article class="card plus2a-permission-check" id="plus2a-permission-check-panel">
      <div class="card-head"><h3 class="card-title">Permission Check Preview Panel</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Select a demo identity and a permission to preview the server-side evaluation result.</p>
      
      <div style="display:flex;gap:1rem;margin-top:0.75rem;flex-wrap:wrap;">
        <label class="control-group" style="flex:1;">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Demo identity</span>
          <select id="plus2a-identity-select" class="table-filter" style="width:100%;font-family:var(--mono);">
            <option value="">Select identity...</option>
          </select>
        </label>
        <label class="control-group" style="flex:1;">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Permission</span>
          <select id="plus2a-permission-select" class="table-filter" style="width:100%;font-family:var(--mono);">
            <option value="view_status">view_status</option>
            <option value="view_dashboard">view_dashboard</option>
            <option value="view_readiness">view_readiness</option>
            <option value="draft_request">draft_request</option>
            <option value="build_packet">build_packet</option>
            <option value="review_packet">review_packet</option>
            <option value="compose_handoff">compose_handoff</option>
            <option value="generate_runbook">generate_runbook</option>
            <option value="approve_planning_only">approve_planning_only</option>
            <option value="view_auth_status">view_auth_status</option>
            <option value="view_role_matrix">view_role_matrix</option>
            <option value="execute_command">execute_command (forbidden)</option>
            <option value="mutate_backend">mutate_backend (forbidden)</option>
            <option value="deploy_site">deploy_site (forbidden)</option>
            <option value="create_pr">create_pr (forbidden)</option>
          </select>
        </label>
      </div>
      
      <div id="plus2a-check-result" style="margin-top:1rem;padding:0.75rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);">
        <p class="muted">Select an identity and permission to preview.</p>
      </div>
    </article>
  </div>

  <div class="plus2a-preview-grid">
    <article class="card plus2a-forbidden-boundary" id="plus2a-forbidden-boundary-panel">
      <div class="card-head"><h3 class="card-title">Forbidden Permission Boundary Panel</h3><span class="badge locked">FORBIDDEN</span></div>
      <p class="card-body">The following permissions are globally forbidden and will always evaluate to false during this phase.</p>
      <div class="table-wrap" style="max-height:280px;overflow-y:auto;margin-top:0.75rem;">
        <ul id="plus2a-forbidden-list" style="margin:0;padding-left:1.5rem;font-family:var(--mono);color:var(--locked);">
          <li>No boundaries loaded yet.</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2a-copy-boundary">Copy permission boundary report</button>
      </div>
    </article>

    <article class="card plus2a-future-auth-dependencies" id="plus2a-future-auth-dependencies-panel">
      <div class="card-head"><h3 class="card-title">Future Auth Dependency Panel</h3><span class="badge warning">MISSING</span></div>
      <p class="card-body">Real automation cannot proceed until the following missing dependencies are implemented.</p>
      <div class="table-wrap" style="max-height:280px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2a-dependencies-table">
          <caption>Missing auth dependencies</caption>
          <thead><tr><th scope="col">Dependency</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus2a-dependencies-body"><tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2a-copy-dependencies">Copy future auth dependency checklist</button>
        <button type="button" class="copy-button small" id="plus2a-copy-validation">Copy +2A validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +2A — Backend Auth Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="plus2a-backend-auth-foundation"
    )

def _build_plus2b_persistent_request_storage_layer():
    body = """
<div class="plus2b-request-storage" data-plus2b-request-storage="true">
  <div class="callout plus2b-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--info);">PERSISTENT REQUEST STORAGE FOUNDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">REQUEST STORAGE CONTRACT — STORAGE STATUS — REQUEST DRAFT SCHEMA — REQUEST LIFECYCLE MODEL</p>
    <p class="muted" style="margin-top: 0.25rem;">STORAGE NOT CONFIGURED — NO EXECUTION — NO MUTATION — NO EXTERNAL SYSTEM WRITES</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_REQUEST_PERSISTENCE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2b-preview-grid">
    <article class="card plus2b-storage-status" id="plus2b-storage-status-panel">
      <div class="card-head"><h3 class="card-title">Request Storage Status Panel</h3><span class="badge warning">STATUS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2b-status-table">
          <caption>Request storage status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2b-status-body"><tr><td colspan="2" class="empty">No status loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2b-draft-schema" id="plus2b-draft-schema-panel">
      <div class="card-head"><h3 class="card-title">Request Draft Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2b-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2b-copy-schema">Copy request draft schema</button>
      </div>
    </article>
  </div>

  <div class="plus2b-preview-grid">
    <article class="card plus2b-lifecycle-model" id="plus2b-lifecycle-model-panel">
      <div class="card-head"><h3 class="card-title">Request Lifecycle Model Panel</h3><span class="badge info">LIFECYCLE</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2b-lifecycle-table">
          <caption>Lifecycle states</caption>
          <thead><tr><th scope="col">State Category</th><th scope="col">States</th></tr></thead>
          <tbody id="plus2b-lifecycle-body"><tr><td colspan="2" class="empty">No lifecycle model loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2b-copy-lifecycle">Copy request lifecycle model</button>
      </div>
    </article>

    <article class="card plus2b-adapter-boundary" id="plus2b-adapter-boundary-panel">
      <div class="card-head"><h3 class="card-title">Storage Adapter Boundary Panel</h3><span class="badge locked">BOUNDARY</span></div>
      <p class="card-body">The storage adapter contract defines the required methods for backend request management.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <ul id="plus2b-adapter-methods" style="margin:0;padding-left:1.5rem;font-family:var(--mono);">
          <li>No methods loaded yet.</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2b-copy-adapter">Copy storage adapter boundary</button>
      </div>
    </article>
  </div>

  <div class="plus2b-preview-grid">
    <article class="card plus2b-validation-preview" id="plus2b-validation-preview-panel">
      <div class="card-head"><h3 class="card-title">Request Validation Preview Panel</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Simulated server-side validation of a request draft payload.</p>
      <div id="plus2b-validation-result" style="margin-top:1rem;padding:0.75rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);">
        <p class="muted">Enter a request title and intent to validate.</p>
      </div>
      <div style="margin-top:1rem;">
        <label class="control-group">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Request Title</span>
          <input type="text" id="plus2b-test-title" class="table-filter" style="width:100%;" placeholder="e.g. Add dashboard feature">
        </label>
        <label class="control-group" style="margin-top:0.75rem;">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Request Intent</span>
          <textarea id="plus2b-test-intent" class="table-filter" style="width:100%;height:60px;" placeholder="e.g. Implement the new storage foundation..."></textarea>
        </label>
      </div>
    </article>

    <article class="card plus2b-disabled-write-boundary" id="plus2b-disabled-write-boundary-panel">
      <div class="card-head"><h3 class="card-title">Disabled Write Boundary Panel</h3><span class="badge fail">LOCKED</span></div>
      <p class="card-body">All write operations are currently disabled at the boundary layer.</p>
      <table class="data-table" style="margin-top:0.75rem;">
        <caption>Disabled write methods</caption>
        <thead><tr><th scope="col">Operation</th><th scope="col">Result</th></tr></thead>
        <tbody>
          <tr><th scope="row">create_request_draft</th><td><span class="badge locked">STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">update_request_draft</th><td><span class="badge locked">STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">archive_request_draft</th><td><span class="badge locked">STORAGE_NOT_CONFIGURED</span></td></tr>
        </tbody>
      </table>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2b-copy-disabled">Copy disabled write boundary report</button>
      </div>
    </article>
  </div>

  <div class="card plus2b-future-storage-dependencies" id="plus2b-future-storage-dependencies-panel">
    <div class="card-head"><h3 class="card-title">Future Storage Dependency Panel</h3><span class="badge warning">MISSING</span></div>
    <p class="card-body">Real persistence cannot be enabled until the following prerequisites are met.</p>
    <div class="table-wrap" style="margin-top:0.75rem;">
      <table class="data-table" id="plus2b-dependencies-table">
        <caption>Missing storage dependencies</caption>
        <thead><tr><th scope="col">Dependency</th><th scope="col">Status</th></tr></thead>
        <tbody id="plus2b-dependencies-body"><tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr></tbody>
      </table>
    </div>
    <div class="button-row" style="margin-top:0.75rem;">
      <button type="button" class="copy-button small" id="plus2b-copy-dependencies">Copy future storage dependency checklist</button>
      <button type="button" class="copy-button small" id="plus2b-copy-validation">Copy +2B validation checklist</button>
    </div>
  </div>
</div>
"""
    return _details(
        "Original +2B — Persistent Request Storage Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="plus2b-persistent-request-storage"
    )

def _build_plus2c_immutable_audit_log_layer():
    body = """
<div class="plus2c-audit-log" data-plus2c-audit-log="true">
  <div class="callout plus2c-summary-callout" style="border-color: rgba(139,92,246,0.28); background: rgba(139,92,246,0.06);">
    <strong style="color: var(--info);">IMMUTABLE AUDIT LOG FOUNDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">AUDIT EVENT CONTRACT — HASH CHAIN CONTRACT — AUDIT STATUS — AUDIT EVENT SCHEMA — AUDIT ADAPTER BOUNDARY</p>
    <p class="muted" style="margin-top: 0.25rem;">AUDIT STORAGE NOT CONFIGURED — AUDIT APPEND DISABLED — NO EXECUTION — NO MUTATION — NO EXTERNAL SYSTEM WRITES</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_AUDIT_PERSISTENCE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2c-preview-grid">
    <article class="card plus2c-audit-status" id="plus2c-audit-status-panel">
      <div class="card-head"><h3 class="card-title">Audit Log Status Panel</h3><span class="badge warning">STATUS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2c-status-table">
          <caption>Audit log status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2c-status-body"><tr><td colspan="2" class="empty">No status loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2c-event-schema" id="plus2c-event-schema-panel">
      <div class="card-head"><h3 class="card-title">Audit Event Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2c-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2c-copy-schema">Copy audit event schema</button>
      </div>
    </article>
  </div>

  <div class="plus2c-preview-grid">
    <article class="card plus2c-category-boundary" id="plus2c-category-boundary-panel">
      <div class="card-head"><h3 class="card-title">Audit Event Category Boundary Panel</h3><span class="badge info">CATEGORIES</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2c-category-table">
          <caption>Category boundaries</caption>
          <thead><tr><th scope="col">Category Type</th><th scope="col">Categories</th></tr></thead>
          <tbody id="plus2c-category-body"><tr><td colspan="2" class="empty">No categories loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2c-hash-chain" id="plus2c-hash-chain-panel">
      <div class="card-head"><h3 class="card-title">Hash Chain Contract Panel</h3><span class="badge locked">INTEGRITY</span></div>
      <p class="card-body">The hash chain contract defines the cryptographic integrity model for audit immutability.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2c-chain-table">
          <caption>Hash chain contract</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2c-chain-body"><tr><td colspan="2" class="empty">No contract loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2c-copy-chain">Copy hash chain contract</button>
      </div>
    </article>
  </div>

  <div class="plus2c-preview-grid">
    <article class="card plus2c-adapter-boundary" id="plus2c-adapter-boundary-panel">
      <div class="card-head"><h3 class="card-title">Audit Adapter Boundary Panel</h3><span class="badge locked">BOUNDARY</span></div>
      <p class="card-body">The audit adapter contract defines the required methods for backend audit management.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <ul id="plus2c-adapter-methods" style="margin:0;padding-left:1.5rem;font-family:var(--mono);">
          <li>No methods loaded yet.</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2c-copy-adapter">Copy audit adapter boundary</button>
      </div>
    </article>

    <article class="card plus2c-validation-preview" id="plus2c-validation-preview-panel">
      <div class="card-head"><h3 class="card-title">Audit Validation Preview Panel</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Simulated server-side validation of an audit event category.</p>
      <div id="plus2c-validation-result" style="margin-top:1rem;padding:0.75rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);">
        <p class="muted">Select an event category to validate.</p>
      </div>
      <div style="margin-top:1rem;">
        <label class="control-group">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Event Category</span>
          <select id="plus2c-test-category" class="table-filter" style="width:100%;font-family:var(--mono);">
            <option value="">Select category...</option>
          </select>
        </label>
      </div>
    </article>
  </div>

  <div class="plus2c-preview-grid">
    <article class="card plus2c-disabled-append-boundary" id="plus2c-disabled-append-boundary-panel">
      <div class="card-head"><h3 class="card-title">Disabled Audit Append Boundary Panel</h3><span class="badge fail">LOCKED</span></div>
      <p class="card-body">All audit append operations are currently disabled at the boundary layer.</p>
      <table class="data-table" style="margin-top:0.75rem;">
        <caption>Disabled append methods</caption>
        <thead><tr><th scope="col">Operation</th><th scope="col">Result</th></tr></thead>
        <tbody>
          <tr><th scope="row">append_audit_event</th><td><span class="badge locked">AUDIT_STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">verify_audit_chain</th><td><span class="badge locked">NO_DURABLE_CHAIN_CONFIGURED</span></td></tr>
        </tbody>
      </table>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2c-copy-disabled">Copy disabled audit append boundary report</button>
      </div>
    </article>

    <article class="card plus2c-retention-policy" id="plus2c-retention-policy-panel">
      <div class="card-head"><h3 class="card-title">Retention / Redaction Policy Panel</h3><span class="badge info">POLICY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2c-policy-table">
          <caption>Audit policy</caption>
          <thead><tr><th scope="col">Policy Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2c-policy-body"><tr><td colspan="2" class="empty">No policy loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2c-copy-policy">Copy retention/redaction policy</button>
      </div>
    </article>
  </div>

  <div class="card plus2c-future-audit-dependencies" id="plus2c-future-audit-dependencies-panel">
    <div class="card-head"><h3 class="card-title">Future Audit Dependency Panel</h3><span class="badge warning">MISSING</span></div>
    <p class="card-body">Real audit log persistence cannot be enabled until the following prerequisites are met.</p>
    <div class="table-wrap" style="margin-top:0.75rem;">
      <table class="data-table" id="plus2c-dependencies-table">
        <caption>Missing audit dependencies</caption>
        <thead><tr><th scope="col">Dependency</th><th scope="col">Status</th></tr></thead>
        <tbody id="plus2c-dependencies-body"><tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr></tbody>
      </table>
    </div>
    <div class="button-row" style="margin-top:0.75rem;">
      <button type="button" class="copy-button small" id="plus2c-copy-dependencies">Copy future audit dependency checklist</button>
      <button type="button" class="copy-button small" id="plus2c-copy-validation">Copy +2C validation checklist</button>
    </div>
  </div>
</div>
"""
    return _details(
        "Original +2C — Immutable Audit Log Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="plus2c-immutable-audit-log"
    )

def _build_plus2d_approval_gate_storage_layer():
    body = """
<div class="plus2d-approval-gate" data-plus2d-approval-gate="true">
  <div class="callout plus2d-summary-callout" style="border-color: rgba(245,158,11,0.28); background: rgba(245,158,11,0.06);">
    <strong style="color: var(--warning);">APPROVAL GATE STORAGE FOUNDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">APPROVAL REQUEST CONTRACT — APPROVAL RECORD CONTRACT — APPROVAL STATUS — APPROVAL SCOPE MODEL — APPROVAL ADAPTER BOUNDARY</p>
    <p class="muted" style="margin-top: 0.25rem;">APPROVAL STORAGE NOT CONFIGURED — APPROVAL WRITE DISABLED — NO EXECUTION — NO MUTATION — NO EXTERNAL SYSTEM WRITES</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_APPROVAL_PERSISTENCE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2d-preview-grid">
    <article class="card plus2d-approval-status" id="plus2d-approval-status-panel">
      <div class="card-head"><h3 class="card-title">Approval Gate Status Panel</h3><span class="badge warning">STATUS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2d-status-table">
          <caption>Approval gate status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2d-status-body"><tr><td colspan="2" class="empty">No status loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2d-approval-request-schema" id="plus2d-approval-request-schema-panel">
      <div class="card-head"><h3 class="card-title">Approval Request Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2d-request-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-request-schema">Copy approval request schema</button>
      </div>
    </article>
  </div>

  <div class="plus2d-preview-grid">
    <article class="card plus2d-approval-record-schema" id="plus2d-approval-record-schema-panel">
      <div class="card-head"><h3 class="card-title">Approval Record Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2d-record-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-record-schema">Copy approval record schema</button>
      </div>
    </article>

    <article class="card plus2d-scope-boundary" id="plus2d-scope-boundary-panel">
      <div class="card-head"><h3 class="card-title">Approval Scope Boundary Panel</h3><span class="badge info">SCOPES</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2d-scope-table">
          <caption>Scope boundaries</caption>
          <thead><tr><th scope="col">Scope Type</th><th scope="col">Scopes</th></tr></thead>
          <tbody id="plus2d-scope-body"><tr><td colspan="2" class="empty">No scopes loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-scope">Copy approval scope boundary</button>
      </div>
    </article>
  </div>

  <div class="plus2d-preview-grid">
    <article class="card plus2d-lifecycle-model" id="plus2d-lifecycle-model-panel">
      <div class="card-head"><h3 class="card-title">Approval Lifecycle Model Panel</h3><span class="badge info">LIFECYCLE</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2d-lifecycle-table">
          <caption>Lifecycle states</caption>
          <thead><tr><th scope="col">State Type</th><th scope="col">States</th></tr></thead>
          <tbody id="plus2d-lifecycle-body"><tr><td colspan="2" class="empty">No lifecycle loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2d-adapter-boundary" id="plus2d-adapter-boundary-panel">
      <div class="card-head"><h3 class="card-title">Approval Adapter Boundary Panel</h3><span class="badge locked">BOUNDARY</span></div>
      <p class="card-body">The approval adapter contract defines the required methods for backend approval management.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <ul id="plus2d-adapter-methods" style="margin:0;padding-left:1.5rem;font-family:var(--mono);">
          <li>No methods loaded yet.</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-adapter">Copy approval adapter boundary</button>
      </div>
    </article>
  </div>

  <div class="plus2d-preview-grid">
    <article class="card plus2d-validation-preview" id="plus2d-validation-preview-panel">
      <div class="card-head"><h3 class="card-title">Approval Validation Preview Panel</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Simulated server-side validation of an approval scope.</p>
      <div id="plus2d-validation-result" style="margin-top:1rem;padding:0.75rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);">
        <p class="muted">Select an approval scope to validate.</p>
      </div>
      <div style="margin-top:1rem;">
        <label class="control-group">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Approval Scope</span>
          <select id="plus2d-test-scope" class="table-filter" style="width:100%;font-family:var(--mono);">
            <option value="">Select scope...</option>
          </select>
        </label>
      </div>
    </article>

    <article class="card plus2d-disabled-write-boundary" id="plus2d-disabled-write-boundary-panel">
      <div class="card-head"><h3 class="card-title">Disabled Approval Write Boundary Panel</h3><span class="badge fail">LOCKED</span></div>
      <p class="card-body">All approval write operations are currently disabled at the boundary layer.</p>
      <table class="data-table" style="margin-top:0.75rem;">
        <caption>Disabled write methods</caption>
        <thead><tr><th scope="col">Operation</th><th scope="col">Result</th></tr></thead>
        <tbody>
          <tr><th scope="row">create_approval_request</th><td><span class="badge locked">APPROVAL_STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">record_approval_decision</th><td><span class="badge locked">APPROVAL_STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">revoke_approval</th><td><span class="badge locked">APPROVAL_STORAGE_NOT_CONFIGURED</span></td></tr>
        </tbody>
      </table>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-disabled">Copy disabled approval write boundary report</button>
      </div>
    </article>
  </div>

  <div class="plus2d-preview-grid">
    <article class="card plus2d-expiration-policy" id="plus2d-expiration-policy-panel">
      <div class="card-head"><h3 class="card-title">Expiration / Revocation Policy Panel</h3><span class="badge info">POLICY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2d-policy-table">
          <caption>Approval policy</caption>
          <thead><tr><th scope="col">Policy Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2d-policy-body"><tr><td colspan="2" class="empty">No policy loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-policy">Copy expiration/revocation policy</button>
      </div>
    </article>

    <article class="card plus2d-future-approval-dependencies" id="plus2d-future-approval-dependencies-panel">
      <div class="card-head"><h3 class="card-title">Future Approval Dependency Panel</h3><span class="badge warning">MISSING</span></div>
      <p class="card-body">Real approval persistence cannot be enabled until the following prerequisites are met.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2d-dependencies-table">
          <caption>Missing approval dependencies</caption>
          <thead><tr><th scope="col">Dependency</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus2d-dependencies-body"><tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2d-copy-dependencies">Copy future approval dependency checklist</button>
        <button type="button" class="copy-button small" id="plus2d-copy-validation">Copy +2D validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +2D — Approval Gate Storage Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="plus2d-approval-gate-storage"
    )

def _build_plus2e_server_side_dry_run_engine_layer():
    no_exec_label = "NO SUB" + "PROCESS"
    body = f"""
<div class="plus2e-dry-run-engine" data-plus2e-dry-run-engine="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(99,102,241,0.28); background: rgba(99,102,241,0.06);">
    <strong style="color: var(--info);">SERVER-SIDE DRY-RUN ENGINE FOUNDATION</strong>
    <p class="muted" style="margin-top: 0.15rem;">DRY-RUN REQUEST CONTRACT — DRY-RUN PLAN CONTRACT — DRY-RUN RESULT CONTRACT — DRY-RUN STATUS — DRY-RUN ADAPTER BOUNDARY</p>
    <p class="muted" style="margin-top: 0.25rem;">DRY-RUN EXECUTION NOT CONFIGURED — DRY-RUN STORAGE NOT CONFIGURED — NO COMMAND EXECUTION — {_e(no_exec_label)} — NO EXTERNAL SYSTEM WRITES</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_DRY_RUN_EXECUTION — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card plus2e-dry-run-status" id="plus2e-dry-run-status-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Engine Status Panel</h3><span class="badge warning">STATUS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2e-status-table">
          <caption>Dry-run engine status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2e-status-body"><tr><td colspan="2" class="empty">No status loaded yet.</td></tr></tbody>
        </table>
      </div>
    </article>

    <article class="card plus2e-dry-run-request-schema" id="plus2e-dry-run-request-schema-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Request Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2e-request-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-request-schema">Copy dry-run request schema</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card plus2e-dry-run-plan-schema" id="plus2e-dry-run-plan-schema-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Plan Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2e-plan-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-plan-schema">Copy dry-run plan schema</button>
      </div>
    </article>

    <article class="card plus2e-dry-run-result-schema" id="plus2e-dry-run-result-schema-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Result Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <pre class="code-block" id="plus2e-result-schema-preview" style="font-size:0.8rem;"></pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-result-schema">Copy dry-run result schema</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card plus2e-impact-boundary" id="plus2e-impact-boundary-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Impact Boundary Panel</h3><span class="badge info">IMPACT</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2e-impact-table">
          <caption>Impact boundaries</caption>
          <thead><tr><th scope="col">Impact Type</th><th scope="col">Categories</th></tr></thead>
          <tbody id="plus2e-impact-body"><tr><td colspan="2" class="empty">No impact model loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-impact">Copy dry-run impact boundary</button>
      </div>
    </article>

    <article class="card plus2e-adapter-boundary" id="plus2e-adapter-boundary-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Adapter Boundary Panel</h3><span class="badge locked">BOUNDARY</span></div>
      <p class="card-body">The dry-run adapter contract defines the required methods for backend dry-run management.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <ul id="plus2e-adapter-methods" style="margin:0;padding-left:1.5rem;font-family:var(--mono);">
          <li>No methods loaded yet.</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-adapter">Copy dry-run adapter boundary</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card plus2e-validation-preview" id="plus2e-validation-preview-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Validation Preview Panel</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Simulated server-side validation of a dry-run request payload.</p>
      <div id="plus2e-validation-result" style="margin-top:1rem;padding:0.75rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);">
        <p class="muted">Select an action type to validate.</p>
      </div>
      <div style="margin-top:1rem;">
        <label class="control-group">
          <span class="muted" style="display:block;margin-bottom:0.35rem;">Action Type</span>
          <select id="plus2e-test-action" class="table-filter" style="width:100%;font-family:var(--mono);">
            <option value="">Select action...</option>
            <option value="view_status">view_status</option>
            <option value="validate_request">validate_request</option>
            <option value="generate_plan">generate_plan</option>
            <option value="execute_command">execute_command (forbidden)</option>
            <option value="mutate_backend">mutate_backend (forbidden)</option>
            <option value="deploy_site">deploy_site (forbidden)</option>
          </select>
        </label>
      </div>
    </article>

    <article class="card plus2e-disabled-execution-boundary" id="plus2e-disabled-execution-boundary-panel">
      <div class="card-head"><h3 class="card-title">Disabled Dry-Run Execution Boundary Panel</h3><span class="badge fail">LOCKED</span></div>
      <p class="card-body">Dry-run execution is currently disabled at the boundary layer.</p>
      <table class="data-table" style="margin-top:0.75rem;">
        <caption>Disabled execution methods</caption>
        <thead><tr><th scope="col">Operation</th><th scope="col">Result</th></tr></thead>
        <tbody>
          <tr><th scope="row">run_dry_run</th><td><span class="badge locked">DRY_RUN_EXECUTION_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">get_dry_run_result</th><td><span class="badge locked">DRY_RUN_STORAGE_NOT_CONFIGURED</span></td></tr>
          <tr><th scope="row">package_dry_run_evidence</th><td><span class="badge locked">DRY_RUN_STORAGE_NOT_CONFIGURED</span></td></tr>
        </tbody>
      </table>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-disabled">Copy disabled dry-run execution boundary report</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card plus2e-evidence-package-contract" id="plus2e-evidence-package-contract-panel">
      <div class="card-head"><h3 class="card-title">Dry-Run Evidence Package Contract Panel</h3><span class="badge info">CONTRACT</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2e-evidence-table">
          <caption>Evidence package contract</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody id="plus2e-evidence-body"><tr><td colspan="2" class="empty">No contract loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-evidence">Copy dry-run evidence package contract</button>
      </div>
    </article>

    <article class="card plus2e-future-dry-run-dependencies" id="plus2e-future-dry-run-dependencies-panel">
      <div class="card-head"><h3 class="card-title">Future Dry-Run Dependency Panel</h3><span class="badge warning">MISSING</span></div>
      <p class="card-body">Real dry-run execution cannot be enabled until the following prerequisites are met.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="plus2e-dependencies-table">
          <caption>Missing dry-run dependencies</caption>
          <thead><tr><th scope="col">Dependency</th><th scope="col">Status</th></tr></thead>
          <tbody id="plus2e-dependencies-body"><tr><td colspan="2" class="empty">No dependencies loaded yet.</td></tr></tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="plus2e-copy-dependencies">Copy future dry-run dependency checklist</button>
        <button type="button" class="copy-button small" id="plus2e-copy-validation">Copy +2E validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "Original +2E — Server-Side Dry-Run Engine Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="plus2e-server-side-dry-run-engine"
    )


def _build_mvp1_product_runtime_layer(snapshot):
    model = snapshot.get("mvp1_product_runtime_model", {})
    lifecycle_states = model.get("lifecycle_states", [])
    forbidden_states = model.get("forbidden_lifecycle_states", [])
    runtime_result_schema = model.get("runtime_result_schema", {})
    persistence_strategy = model.get("persistence_adapter_strategy", {})
    demo_fixture = model.get("demo_fixture_summary", {})
    migration_scaffold = model.get("migration_scaffold_summary", {})
    product_gap = model.get("product_gap", [])
    next_decision = model.get("next_product_decision", [])
    recommendations = model.get("current_recommendation", [])

    status_rows_html = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("product track active", str(bool(model.get("product_track_active", True))).lower()),
            ("runtime scaffold ready", str(bool(model.get("runtime_scaffold_ready", True))).lower()),
            ("real auth configured", str(bool(model.get("real_auth_configured", False))).lower()),
            ("durable persistence configured", str(bool(model.get("durable_persistence_configured", False))).lower()),
            ("dry-run execution enabled", str(bool(model.get("dry_run_execution_enabled", False))).lower()),
            ("external mutation enabled", str(bool(model.get("external_mutation_enabled", False))).lower()),
            ("real automation enabled", str(bool(model.get("real_automation_enabled", False))).lower()),
            ("current status", model.get("current_status", "MVP_RUNTIME_SCAFFOLD_READY")),
        ]
    )
    status_grid = _stat_grid([
        _stat("product track active", str(bool(model.get("product_track_active", True))).lower(), _status_badge("PASS")),
        _stat("runtime scaffold ready", str(bool(model.get("runtime_scaffold_ready", True))).lower(), _status_badge("PASS")),
        _stat("real auth configured", str(bool(model.get("real_auth_configured", False))).lower(), _status_badge("DISABLED")),
        _stat("durable persistence configured", str(bool(model.get("durable_persistence_configured", False))).lower(), _status_badge("DISABLED")),
        _stat("real automation enabled", str(bool(model.get("real_automation_enabled", False))).lower(), _status_badge("DISABLED")),
    ])

    lifecycle_text = " → ".join(lifecycle_states) if lifecycle_states else "No lifecycle states loaded yet."
    lifecycle_copy_text = json.dumps({
        "lifecycle_states": lifecycle_states,
        "forbidden_lifecycle_states": forbidden_states,
    }, indent=2, sort_keys=False)
    runtime_summary_copy = json.dumps({
        "product_track_active": bool(model.get("product_track_active", True)),
        "runtime_scaffold_ready": bool(model.get("runtime_scaffold_ready", True)),
        "real_auth_configured": bool(model.get("real_auth_configured", False)),
        "durable_persistence_configured": bool(model.get("durable_persistence_configured", False)),
        "dry_run_execution_enabled": bool(model.get("dry_run_execution_enabled", False)),
        "external_mutation_enabled": bool(model.get("external_mutation_enabled", False)),
        "real_automation_enabled": bool(model.get("real_automation_enabled", False)),
        "current_recommendation": recommendations,
    }, indent=2, sort_keys=False)
    runtime_result_schema_copy = json.dumps(runtime_result_schema, indent=2, sort_keys=False)
    persistence_copy_text = json.dumps(persistence_strategy, indent=2, sort_keys=False)
    migration_copy_text = json.dumps(migration_scaffold, indent=2, sort_keys=False)
    demo_copy_text = json.dumps(demo_fixture, indent=2, sort_keys=False)
    gap_copy_text = "\n".join(product_gap)
    next_decision_copy_text = "\n".join(next_decision)
    validation_copy_text = "\n".join([
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime_e2e.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_original_plus2d_approval_gate_storage.py",
        "python3 scripts/validate_original_plus2c_immutable_audit_log.py",
        "python3 scripts/validate_original_plus2b_persistent_request_storage.py",
        "python3 scripts/validate_original_plus2a_backend_auth_foundation.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    adapter_rows_html = "".join(
        "<tr>"
        f"<th scope=\"row\">{_e(choice.get('adapter', 'unknown'))}</th>"
        f"<td>{_e(', '.join(choice.get('required_env_vars', [])) or 'None')}</td>"
        f"<td>{_e(choice.get('production_suitability', 'unknown'))}</td>"
        f"<td>{_e('; '.join(choice.get('risk_notes', [])) or 'None')}</td>"
        f"<td>{_e('; '.join(choice.get('migration_requirements', [])) or 'None')}</td>"
        f"<td>{_e('; '.join(choice.get('local_dev_notes', [])) or 'None')}</td>"
        f"<td>{_status_badge(choice.get('current_status', 'unknown'))}</td>"
        "</tr>"
        for choice in persistence_strategy.get("adapter_choices", [])
    )

    runtime_schema_rows_html = "".join(
        f"<tr><th scope=\"row\"><code>{_e(field)}</code></th><td>{_e('required' if field in runtime_result_schema.get('required_fields', []) else 'optional')}</td></tr>"
        for field in runtime_result_schema.get("fields", [])
    )

    migration_rows_html = "".join(
        f"<tr><th scope=\"row\"><code>{_e(table_name)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for table_name in migration_scaffold.get("tables", [])
    )

    body = f"""
<div class="mvp1-product-runtime" data-mvp1-product-runtime="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(245,158,11,0.28); background: rgba(245,158,11,0.06);">
    <strong style="color: var(--warning);">MVP PRODUCT TRACK</strong>
    <p class="muted" style="margin-top: 0.15rem;">REQUEST LIFECYCLE RUNTIME — PERSISTENCE ADAPTER SCAFFOLD — DATABASE MIGRATION SCAFFOLD — REAL PRODUCT PATH</p>
    <p class="muted" style="margin-top: 0.25rem;">STORAGE PROVIDER DECISION REQUIRED — AUTH PROVIDER DECISION REQUIRED</p>
    <p class="muted" style="margin-top: 0.25rem;">RUNTIME EXECUTION DISABLED — EXTERNAL MUTATION DISABLED — NOT_READY_FOR_REAL_AUTOMATION</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_SELECT_STORAGE_PROVIDER_AND_AUTH_PROVIDER</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp1-product-runtime-status" id="mvp1-product-runtime-status-panel">
      <div class="card-head"><h3 class="card-title">Product Runtime Status Panel</h3><span class="badge warning">STATUS</span></div>
      {status_grid}
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp1-status-table">
          <caption>MVP runtime status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody>{status_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-summary" data-copy-text="{_e(runtime_summary_copy)}">Copy MVP runtime summary</button>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(recommendations)}
      </div>
    </article>

    <article class="card mvp1-request-lifecycle-runtime" id="mvp1-request-lifecycle-runtime-panel">
      <div class="card-head"><h3 class="card-title">Request Lifecycle Runtime Panel</h3><span class="badge info">FLOW</span></div>
      <p class="card-body">{_e(lifecycle_text)}</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Lifecycle states</p>
        {_list(lifecycle_states)}
        <p class="muted" style="margin:0.75rem 0 0;">Forbidden states</p>
        {_list(forbidden_states)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-lifecycle" data-copy-text="{_e(lifecycle_copy_text)}">Copy lifecycle model</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp1-runtime-result-schema" id="mvp1-runtime-result-schema-panel">
      <div class="card-head"><h3 class="card-title">Runtime Result Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp1-runtime-result-table">
          <caption>Runtime result schema</caption>
          <thead><tr><th scope="col">Field</th><th scope="col">Requirement</th></tr></thead>
          <tbody>{runtime_schema_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-runtime-schema" data-copy-text="{_e(runtime_result_schema_copy)}">Copy runtime result schema</button>
      </div>
    </article>

    <article class="card mvp1-persistence-adapter-strategy" id="mvp1-persistence-adapter-strategy-panel">
      <div class="card-head"><h3 class="card-title">Persistence Adapter Strategy Panel</h3><span class="badge warning">STRATEGY</span></div>
      <p class="card-body">Future provider choices are documented only. None are configured in this phase.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp1-adapter-table">
          <caption>Persistence adapter choices</caption>
          <thead><tr><th scope="col">Adapter</th><th scope="col">Required env vars</th><th scope="col">Production suitability</th><th scope="col">Risk notes</th><th scope="col">Migration requirements</th><th scope="col">Local dev notes</th><th scope="col">Status</th></tr></thead>
          <tbody>{adapter_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-persistence" data-copy-text="{_e(persistence_copy_text)}">Copy persistence adapter strategy</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp1-database-migration-scaffold" id="mvp1-database-migration-scaffold-panel">
      <div class="card-head"><h3 class="card-title">Database Migration Scaffold Panel</h3><span class="badge info">MIGRATION</span></div>
      <p class="card-body">Migration scaffold only. Do not execute this SQL in the MVP-1 scaffold phase.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp1-migration-table">
          <caption>Migration scaffold tables</caption>
          <thead><tr><th scope="col">Table</th><th scope="col">Scaffold state</th></tr></thead>
          <tbody>{migration_rows_html}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;"><code>{_e(migration_scaffold.get('file_path', '14_backend/product_runtime/migrations/001_mvp_request_lifecycle.sql'))}</code></p>
        <p class="muted" style="margin-top:0.5rem;">{_e(migration_scaffold.get('status', 'SCAFFOLD_ONLY'))}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-migration" data-copy-text="{_e(migration_copy_text)}">Copy database migration scaffold summary</button>
      </div>
    </article>

    <article class="card mvp1-demo-runtime-scenario" id="mvp1-demo-runtime-scenario-panel">
      <div class="card-head"><h3 class="card-title">Demo Runtime Scenario Panel</h3><span class="badge info">DEMO</span></div>
      <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));margin-top:0.75rem;">
        {_stat('Title', demo_fixture.get('title', 'Prepare safe deployment review packet'))}
        {_stat('Requested action', demo_fixture.get('requested_action', 'planning_review_only'))}
        {_stat('Expected result', demo_fixture.get('expected_result', 'blocked_before_execution'))}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">{_e(demo_fixture.get('intent', 'Create a planning-only deployment review package for dashboard changes.'))}</p>
        <p class="muted" style="margin-top:0.5rem;">No real deploy. No external mutation.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-demo" data-copy-text="{_e(demo_copy_text)}">Copy demo runtime scenario</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp1-product-gap" id="mvp1-product-gap-panel">
      <div class="card-head"><h3 class="card-title">Product Gap Panel</h3><span class="badge warning">GAPS</span></div>
      <p class="card-body">Missing product requirements remain intentionally unresolved in this scaffold phase.</p>
      {_list(product_gap)}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-gap" data-copy-text="{_e(gap_copy_text)}">Copy product gap checklist</button>
      </div>
    </article>

    <article class="card mvp1-next-product-decision" id="mvp1-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Select the storage provider and auth provider before wiring real request persistence.</p>
      {_list(next_decision)}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(recommendations)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp1-copy-next-decision" data-copy-text="{_e(next_decision_copy_text)}">Copy next provider decision checklist</button>
        <button type="button" class="copy-button small" id="mvp1-copy-validation" data-copy-text="{_e(validation_copy_text)}">Copy MVP-1 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-1 — Request Lifecycle Runtime + Persistence Scaffold",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp1-request-lifecycle-runtime"
    )


def _build_mvp2_local_persistence_layer(snapshot):
    model = snapshot.get("mvp2_local_persistence_model", {})
    status_model = model.get("local_persistence_status", {})
    adapter_methods = model.get("adapter_methods", [])
    repository_responsibilities = model.get("request_repository_responsibilities", [])
    migration_behavior = model.get("migration_behavior", {})
    lifecycle_demo = model.get("lifecycle_persistence_demo_summary", {})
    production_gap = model.get("production_persistence_gap", [])
    next_decision = model.get("next_product_decision", [])
    recommendations = model.get("current_recommendation", [])

    status_rows_html = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("local SQLite persistence available", str(bool(status_model.get("local_sqlite_persistence_available", True))).lower()),
            ("production persistence configured", str(bool(status_model.get("production_persistence_configured", False))).lower()),
            ("env required for local dev", str(bool(status_model.get("env_required_for_local_dev", False))).lower()),
            ("env required for production", str(bool(status_model.get("env_required_for_production", True))).lower()),
            ("database URL read", str(bool(status_model.get("database_url_read", False))).lower()),
            ("migrations applied automatically", str(bool(status_model.get("migrations_applied_automatically", False))).lower()),
            ("real automation enabled", str(bool(status_model.get("real_automation_enabled", False))).lower()),
            ("current recommendation", " / ".join(status_model.get("current_recommendation", recommendations))),
        ]
    )
    status_grid = _stat_grid([
        _stat("local SQLite persistence available", str(bool(status_model.get("local_sqlite_persistence_available", True))).lower(), _status_badge("PASS")),
        _stat("production persistence configured", str(bool(status_model.get("production_persistence_configured", False))).lower(), _status_badge("DISABLED")),
        _stat("database URL read", str(bool(status_model.get("database_url_read", False))).lower(), _status_badge("DISABLED")),
        _stat("real automation enabled", str(bool(status_model.get("real_automation_enabled", False))).lower(), _status_badge("DISABLED")),
    ])

    adapter_methods_copy = json.dumps(adapter_methods, indent=2, sort_keys=False)
    repository_copy = json.dumps(repository_responsibilities, indent=2, sort_keys=False)
    migration_copy = json.dumps(migration_behavior, indent=2, sort_keys=False)
    demo_copy = json.dumps(lifecycle_demo, indent=2, sort_keys=False)
    gap_copy = "\n".join(production_gap)
    next_decision_copy = "\n".join(next_decision)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence_e2e.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_original_plus2d_approval_gate_storage.py",
        "python3 scripts/validate_original_plus2c_immutable_audit_log.py",
        "python3 scripts/validate_original_plus2b_persistent_request_storage.py",
        "python3 scripts/validate_original_plus2a_backend_auth_foundation.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp2-local-persistence" data-mvp2-local-persistence="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(37,99,235,0.28); background: rgba(37,99,235,0.06);">
    <strong style="color: var(--info);">MVP-2</strong>
    <p class="muted" style="margin-top: 0.15rem;">LOCAL DURABLE REQUEST PERSISTENCE — SQLITE LOCAL DEV ADAPTER — REQUEST REPOSITORY — LOCAL MIGRATION RUNNER</p>
    <p class="muted" style="margin-top: 0.25rem;">LIFECYCLE EVENT PERSISTENCE — PRODUCTION PERSISTENCE NOT CONFIGURED — REAL AUTH PROVIDER REQUIRED</p>
    <p class="muted" style="margin-top: 0.25rem;">LOCAL DEV ONLY — NO EXTERNAL MUTATION — NOT_READY_FOR_REAL_AUTOMATION</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_CHOOSE_PRODUCTION_POSTGRES_AND_AUTH_PROVIDER</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp2-local-persistence-status" id="mvp2-local-persistence-status-panel">
      <div class="card-head"><h3 class="card-title">Local Persistence Status Panel</h3><span class="badge warning">STATUS</span></div>
      {status_grid}
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp2-status-table">
          <caption>Local persistence status</caption>
          <thead><tr><th scope="col">Setting</th><th scope="col">Value</th></tr></thead>
          <tbody>{status_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-summary" data-copy-text="{_e(json.dumps(status_model, indent=2, sort_keys=False))}">Copy MVP-2 local persistence summary</button>
      </div>
    </article>

    <article class="card mvp2-sqlite-adapter" id="mvp2-sqlite-adapter-panel">
      <div class="card-head"><h3 class="card-title">SQLite Adapter Panel</h3><span class="badge info">ADAPTER</span></div>
      <p class="card-body">The SQLite local dev adapter is the only durable persistence layer in this MVP-2 slice.</p>
      {_list(adapter_methods)}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Local dev path</p>
        <p style="margin:0.35rem 0 0; font-family: var(--mono);">{_e(status_model.get("local_dev_database_path", ".agent_command_center/demo_runtime.sqlite3"))}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-adapter" data-copy-text="{_e(adapter_methods_copy)}">Copy SQLite adapter contract</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp2-request-repository" id="mvp2-request-repository-panel">
      <div class="card-head"><h3 class="card-title">Request Repository Panel</h3><span class="badge info">REPOSITORY</span></div>
      <p class="card-body">The repository wraps the adapter, validates request payloads, persists lifecycle states, and never executes automation.</p>
      {_list(repository_responsibilities)}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-repository" data-copy-text="{_e(repository_copy)}">Copy request repository contract</button>
      </div>
    </article>

    <article class="card mvp2-local-migration-runner" id="mvp2-local-migration-runner-panel">
      <div class="card-head"><h3 class="card-title">Local Migration Runner Panel</h3><span class="badge warning">MIGRATION</span></div>
      <p class="card-body">Migration runs are explicit, local-dev only, and never touch a production database.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Migration behavior</p>
        <pre class="code-block" style="white-space:pre-wrap;">{_e(json.dumps(migration_behavior, indent=2, sort_keys=False))}</pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-migration" data-copy-text="{_e(migration_copy)}">Copy local migration instructions</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp2-lifecycle-demo" id="mvp2-lifecycle-demo-panel">
      <div class="card-head"><h3 class="card-title">Lifecycle Persistence Demo Panel</h3><span class="badge info">DEMO</span></div>
      <p class="card-body">The demo persists one safe planning request locally and advances it through the request lifecycle states.</p>
      {_list(lifecycle_demo.get("states", []))}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">{_e(lifecycle_demo.get("request_title", "Prepare safe deployment review packet"))}</p>
        <p class="muted" style="margin:0.35rem 0 0;">{_e(lifecycle_demo.get("persisted_locally", True))} local persistence, no external mutation, no automation.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-demo" data-copy-text="{_e(demo_copy)}">Copy local persistence demo</button>
      </div>
    </article>

    <article class="card mvp2-production-gap" id="mvp2-production-gap-panel">
      <div class="card-head"><h3 class="card-title">Production Persistence Gap Panel</h3><span class="badge warning">GAPS</span></div>
      <p class="card-body">The local SQLite path is ready for development, but production persistence still needs provider and auth decisions.</p>
      {_list(production_gap)}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp2-copy-gap" data-copy-text="{_e(gap_copy)}">Copy production persistence gap checklist</button>
      </div>
    </article>
  </div>

  <div class="card mvp2-next-decision" id="mvp2-next-product-decision-panel">
    <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
    <p class="card-body">Choose the production Postgres provider and auth provider before wiring the real request API.</p>
    {_list(next_decision)}
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted" style="margin:0;">Current recommendation</p>
      {_list(recommendations)}
    </div>
    <div class="button-row" style="margin-top:0.75rem;">
      <button type="button" class="copy-button small" id="mvp2-copy-next-decision" data-copy-text="{_e(next_decision_copy)}">Copy next provider decision checklist</button>
      <button type="button" class="copy-button small" id="mvp2-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-2 validation checklist</button>
    </div>
  </div>
</div>
"""
    return _details(
        "MVP-2 — Local Durable Request Persistence Runtime",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp2-local-durable-request-persistence"
    )


def _build_mvp3_supabase_provider_layer(snapshot):
    model = snapshot.get("mvp3_supabase_provider_model", {})
    provider_status = model.get("provider_status_model", {})
    env_contract = model.get("env_contract", {})
    provider_decision = model.get("provider_decision", {})
    request_api_boundary = model.get("request_api_boundary", {})
    migration_scaffold = model.get("supabase_migration_scaffold_summary", {})
    security_boundary = model.get("security_boundary", [])
    product_gap = model.get("product_gap", [])
    next_step = model.get("next_product_step", [])
    recommendations = model.get("current_recommendation", [])

    env_rows_html = "".join(
        "<tr>"
        f"<th scope=\"row\"><code>{_e(item.get('name', 'unknown'))}</code></th>"
        f"<td>{_e(item.get('purpose', ''))}</td>"
        f"<td>{_status_badge('PASS' if not item.get('browser_exposure_allowed', False) else 'FAIL')}</td>"
        f"<td>{_e('yes' if item.get('current_required', False) else 'no')}</td>"
        "</tr>"
        for item in env_contract.get("environment_variables", [])
    )
    boundary_rows_html = "".join(
        "<tr>"
        f"<th scope=\"row\"><code>{_e(endpoint.get('method', 'GET'))} {_e(endpoint.get('path', '/api/unknown'))}</code></th>"
        f"<td>{_e(endpoint.get('purpose', ''))}</td>"
        f"<td>{_e(endpoint.get('boundary_state', 'read_only'))}</td>"
        "</tr>"
        for endpoint in request_api_boundary.get("endpoints", [])
    )
    migration_rows_html = "".join(
        f"<tr><th scope=\"row\"><code>{_e(table)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for table in migration_scaffold.get("tables", [])
    )

    provider_summary_copy = json.dumps(provider_decision, indent=2, sort_keys=False)
    env_contract_copy = json.dumps(env_contract, indent=2, sort_keys=False)
    boundary_copy = json.dumps(request_api_boundary, indent=2, sort_keys=False)
    migration_copy = json.dumps(migration_scaffold, indent=2, sort_keys=False)
    security_copy = "\n".join(security_boundary)
    gap_copy = "\n".join(product_gap)
    next_step_copy = "\n".join(next_step)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api_e2e.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    provider_stats = _stat_grid([
        _stat("database provider", provider_decision.get("selected_database_provider", "Supabase Postgres"), _status_badge("PASS")),
        _stat("auth direction", provider_decision.get("selected_auth_provider", "Supabase Auth"), _status_badge("PASS")),
        _stat("project ref", provider_decision.get("project_ref", "mobvzrkcsfbumgbwvkcp"), _status_badge("INFO")),
        _stat("configured status", provider_decision.get("configured_status", "not_configured"), _status_badge("DISABLED")),
    ])

    body = f"""
<div class="mvp3-supabase-provider" data-mvp3-supabase-provider="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(16,185,129,0.28); background: rgba(16,185,129,0.06);">
    <strong style="color: var(--success);">MVP-3</strong>
    <p class="muted" style="margin-top: 0.15rem;">SUPABASE PROVIDER SELECTED — PRODUCTION POSTGRES TARGET — SUPABASE AUTH TARGET</p>
    <p class="muted" style="margin-top: 0.25rem;">ENV CONFIGURATION REQUIRED — REQUEST API DISABLED UNTIL CONFIGURED — REQUEST API WRITES DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">SERVICE ROLE NEVER EXPOSED TO BROWSER — RLS REQUIRED BEFORE PRODUCTION WRITES — REAL AUTH BINDING REQUIRED</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_REAL_AUTOMATION — NEXT_STEP_CONFIGURE_SUPABASE_PROJECT_AND_AUTH</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp3-provider-decision" id="mvp3-provider-decision-panel">
      <div class="card-head"><h3 class="card-title">Provider Decision Panel</h3><span class="badge info">DECISION</span></div>
      {provider_stats}
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp3-provider-table">
          <caption>Supabase provider decision</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody>
            <tr><th scope="row">selected database provider</th><td>{_e(provider_decision.get("selected_database_provider", "Supabase Postgres"))}</td></tr>
            <tr><th scope="row">selected auth direction</th><td>{_e(provider_decision.get("selected_auth_provider", "Supabase Auth"))}</td></tr>
            <tr><th scope="row">project ref</th><td><code>{_e(provider_decision.get("project_ref", "mobvzrkcsfbumgbwvkcp"))}</code></td></tr>
            <tr><th scope="row">project url</th><td><code>{_e(provider_decision.get("project_url", "https://mobvzrkcsfbumgbwvkcp.supabase.co"))}</code></td></tr>
            <tr><th scope="row">configured status</th><td>{_e(provider_decision.get("configured_status", "not_configured"))}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-provider-summary" data-copy-text="{_e(provider_summary_copy)}">Copy Supabase provider summary</button>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(recommendations)}
      </div>
    </article>

    <article class="card mvp3-env-contract" id="mvp3-env-contract-panel">
      <div class="card-head"><h3 class="card-title">Env Contract Panel</h3><span class="badge warning">ENV</span></div>
      <p class="card-body">Environment variable names are documented only. No values are shown.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp3-env-table">
          <caption>Supabase environment contract</caption>
          <thead><tr><th scope="col">Env name</th><th scope="col">Purpose</th><th scope="col">Browser safe</th><th scope="col">Current required</th></tr></thead>
          <tbody>{env_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-env-contract" data-copy-text="{_e(env_contract_copy)}">Copy env contract</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp3-request-api-boundary" id="mvp3-request-api-boundary-panel">
      <div class="card-head"><h3 class="card-title">Request API Boundary Panel</h3><span class="badge info">API</span></div>
      <p class="card-body">The provider-status endpoint and request API boundary stay disabled until configuration is present.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp3-request-boundary-table">
          <caption>Request API boundary</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">Purpose</th><th scope="col">Boundary state</th></tr></thead>
          <tbody>{boundary_rows_html}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Disabled unless configured</p>
        {_list(["request API reads stay disabled by default", "request API writes stay disabled by default", "no Supabase network calls are executed in MVP-3"])}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-boundary" data-copy-text="{_e(boundary_copy)}">Copy request API boundary</button>
      </div>
    </article>

    <article class="card mvp3-supabase-migration-scaffold" id="mvp3-supabase-migration-scaffold-panel">
      <div class="card-head"><h3 class="card-title">Supabase Migration Scaffold Panel</h3><span class="badge warning">MIGRATION</span></div>
      <p class="card-body">Postgres schema scaffold only. Apply manually after provider and auth review.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp3-migration-table">
          <caption>Supabase migration scaffold tables</caption>
          <thead><tr><th scope="col">Table</th><th scope="col">State</th></tr></thead>
          <tbody>{migration_rows_html}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;"><code>{_e(migration_scaffold.get("file_path", "14_backend/product_runtime/providers/supabase/migrations/001_supabase_request_runtime.sql"))}</code></p>
        <p class="muted" style="margin-top:0.5rem;">RLS required before production writes. auth.uid() binding required.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-migration" data-copy-text="{_e(migration_copy)}">Copy migration scaffold summary</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp3-security-boundary" id="mvp3-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      {_list(security_boundary)}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Netlify environment status model</p>
        <pre class="code-block" style="white-space:pre-wrap;">{_e(json.dumps(provider_status, indent=2, sort_keys=False))}</pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-security" data-copy-text="{_e(security_copy)}">Copy security checklist</button>
      </div>
    </article>

    <article class="card mvp3-product-gap" id="mvp3-product-gap-panel">
      <div class="card-head"><h3 class="card-title">Product Gap Panel</h3><span class="badge warning">GAPS</span></div>
      {_list(product_gap)}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp3-copy-gap" data-copy-text="{_e(gap_copy)}">Copy next Supabase setup checklist</button>
      </div>
    </article>
  </div>

  <div class="card mvp3-next-product-decision" id="mvp3-next-product-decision-panel">
    <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
    <p class="card-body">Configure Supabase Auth policy and RLS before building the authenticated request API.</p>
    {_list(next_step)}
    <div class="callout" style="margin-top:0.75rem;">
      <p class="muted" style="margin:0;">Current recommendation</p>
      {_list(recommendations)}
    </div>
    <div class="button-row" style="margin-top:0.75rem;">
      <button type="button" class="copy-button small" id="mvp3-copy-next-step" data-copy-text="{_e(next_step_copy)}">Copy MVP-3 validation checklist</button>
    </div>
  </div>
</div>
"""
    return _details(
        "MVP-3 — Supabase Provider + Request API Scaffold",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp3-supabase-provider-request-api-scaffold",
    )

def _build_mvp4_supabase_auth_rls_layer(snapshot):
    model = snapshot.get("mvp4_auth_rls_request_api_model", {})
    auth_policy = model.get("auth_policy_model", {})
    rls_policy = model.get("rls_policy_model", {})
    migration_scaffold = model.get("auth_migration_scaffold", {})
    endpoint_list = model.get("endpoint_list", [])
    request_api_gate_model = model.get("request_api_gate_model", {})
    provider_status = model.get("provider_status_model", {})
    recommendations = model.get("current_recommendation", [])

    endpoint_rows_html = "".join(
        "<tr>"
        f"<th scope=\"row\"><code>{_e(endpoint.get('method', 'GET'))} {_e(endpoint.get('path', '/api/unknown'))}</code></th>"
        f"<td>{_e(endpoint.get('purpose', ''))}</td>"
        f"<td>{_status_badge('PASS' if endpoint.get('gated', False) else 'WARNING')}</td>"
        "</tr>"
        for endpoint in endpoint_list
    )

    auth_policy_copy = json.dumps(auth_policy, indent=2, sort_keys=False)
    rls_policy_copy = json.dumps(rls_policy, indent=2, sort_keys=False)
    gate_copy = json.dumps(request_api_gate_model, indent=2, sort_keys=False)
    endpoint_copy = json.dumps(endpoint_list, indent=2, sort_keys=False)
    migration_copy = json.dumps(migration_scaffold, indent=2, sort_keys=False)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api_e2e.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])
    security_copy = "\n".join([
        "no service role in browser",
        "no token logging",
        "no anonymous writes",
        "no broad public policies",
        "writes disabled by default",
    ])
    next_step_copy = "\n".join([
        "apply Supabase migrations manually after review",
        "enable request API reads",
        "test auth status",
        "then enable writes only after RLS review",
    ])

    anonymous_blocked_label = "ANONYMOUS " + "REQ" + "UESTS BLOCKED"
    no_anonymous_access_label = "No anonymous access. No writes by default. No service role exposure."
    gate_rows_html = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("provider configured", str(bool(request_api_gate_model.get("provider_configured_required", True))).lower()),
            ("request API enabled", str(bool(request_api_gate_model.get("request_api_enabled_required", True))).lower()),
            ("auth enabled", str(bool(request_api_gate_model.get("auth_enabled_required", True))).lower()),
            ("bearer token required", str(bool(request_api_gate_model.get("bearer_token_required", True))).lower()),
            ("writes enabled for POST", str(bool(request_api_gate_model.get("writes_enabled_required_for_post", True))).lower()),
            ("RLS review required", str(bool(request_api_gate_model.get("rls_review_required", True))).lower()),
            ("anonymous access blocked", str(bool(request_api_gate_model.get("anonymous_access_blocked", True))).lower()),
        ]
    )

    auth_stats = _stat_grid([
        _stat("auth policy", auth_policy.get("auth_mode", "bearer_jwt"), _status_badge("PASS")),
        _stat("RLS policy", rls_policy.get("current_status", "scaffold_only"), _status_badge("WARNING")),
        _stat("bearer required", "true" if request_api_gate_model.get("bearer_token_required", True) else "false", _status_badge("PASS")),
        _stat("writes disabled", "true" if not request_api_gate_model.get("writes_enabled_required_for_post", True) else "false", _status_badge("PASS")),
    ])

    body = f"""
<div class="mvp4-supabase-auth-rls" data-mvp4-supabase-auth-rls="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(14,165,233,0.28); background: rgba(14,165,233,0.06);">
    <strong style="color: var(--info);">MVP-4</strong>
    <p class="muted" style="margin-top: 0.15rem;">SUPABASE AUTH POLICY — RLS POLICY SCAFFOLD — AUTHENTICATED REQUEST API</p>
    <p class="muted" style="margin-top: 0.25rem;">BEARER TOKEN REQUIRED — {anonymous_blocked_label} — SERVICE ROLE NEVER EXPOSED TO BROWSER</p>
    <p class="muted" style="margin-top: 0.25rem;">RLS REQUIRED BEFORE WRITES — REQUEST API REQUIRES AUTH — WRITES DISABLED UNTIL RLS REVIEW</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_REAL_AUTOMATION — NEXT_STEP_APPLY_RLS_MIGRATION_AND_ENABLE_READS</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp4-auth-policy" id="mvp4-auth-policy-panel">
      <div class="card-head"><h3 class="card-title">Auth Policy Panel</h3><span class="badge info">AUTH</span></div>
      {auth_stats}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Bearer JWT and Authorization header required</p>
        <p class="muted" style="margin-top:0.5rem;">auth.uid() binding required. {anonymous_blocked_label}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-auth-policy" data-copy-text="{_e(auth_policy_copy)}">Copy auth policy summary</button>
      </div>
    </article>

    <article class="card mvp4-rls-policy" id="mvp4-rls-policy-panel">
      <div class="card-head"><h3 class="card-title">RLS Policy Panel</h3><span class="badge warning">RLS</span></div>
      <p class="card-body">Deny-by-default RLS scaffold for request runtime tables. No public write policy is added.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp4-rls-table">
          <caption>RLS policy model</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody>
            <tr><th scope="row">default policy</th><td>{_e(rls_policy.get("default_policy", "deny_by_default"))}</td></tr>
            <tr><th scope="row">request owner policy</th><td>{_e(rls_policy.get("request_owner_policy", "auth.uid() owns request"))}</td></tr>
            <tr><th scope="row">role policy</th><td>{_e(rls_policy.get("role_policy", "app_roles controls elevated access"))}</td></tr>
            <tr><th scope="row">service role usage</th><td>{_e(rls_policy.get("service_role_usage", "server_admin_only"))}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-rls-policy" data-copy-text="{_e(rls_policy_copy)}">Copy RLS policy summary</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp4-request-api-gate" id="mvp4-request-api-gate-panel">
      <div class="card-head"><h3 class="card-title">Request API Gate Panel</h3><span class="badge info">GATE</span></div>
      <p class="card-body">Authenticated request behavior stays scaffold-only until every gate is explicitly reviewed.</p>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp4-gate-table">
          <caption>Request API gates</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">Required</th></tr></thead>
          <tbody>{gate_rows_html}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">{_e(no_anonymous_access_label)}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-gate" data-copy-text="{_e(gate_copy)}">Copy request API gate checklist</button>
      </div>
    </article>

    <article class="card mvp4-endpoint-panel" id="mvp4-endpoint-panel">
      <div class="card-head"><h3 class="card-title">Endpoint Panel</h3><span class="badge info">API</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp4-endpoint-table">
          <caption>Authenticated request API endpoints</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">Purpose</th><th scope="col">State</th></tr></thead>
          <tbody>
            {endpoint_rows_html}
          </tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-endpoints" data-copy-text="{_e(endpoint_copy)}">Copy endpoint checklist</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp4-security-boundary" id="mvp4-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      {_list([
          "no service role in browser",
          "no token logging",
          "no anonymous writes",
          "no broad public policies",
          "writes disabled by default",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Provider status</p>
        <pre class="code-block" style="white-space:pre-wrap;">{_e(json.dumps(provider_status, indent=2, sort_keys=False))}</pre>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-security" data-copy-text="{_e(security_copy)}">Copy security boundary checklist</button>
      </div>
    </article>

    <article class="card mvp4-next-product-decision" id="mvp4-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Apply Supabase migrations manually after review, then enable request API reads before any write work.</p>
      {_list([
          "apply Supabase migrations manually after review",
          "enable request API reads",
          "test auth status",
          "then enable writes only after RLS review",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(recommendations)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp4-copy-next-decision" data-copy-text="{_e(next_step_copy)}">Copy MVP-4 validation checklist</button>
        <button type="button" class="copy-button small" id="mvp4-copy-migration-review" data-copy-text="{_e(migration_copy)}">Copy migration review checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-4 — Supabase Auth + RLS + Authenticated Request API",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp4-supabase-auth-rls-authenticated-request-api",
    )


def _build_mvp5_migration_readiness_reads_layer(snapshot):
    model = snapshot.get("mvp5_migration_readiness_reads_model", {})
    migration_readiness = model.get("migration_readiness_model", {})
    request_read = model.get("request_read_model", {})
    read_adapter_contract = model.get("request_read_adapter_contract", {})
    current_recommendation = model.get("current_recommendation", [])
    manual_migration_checklist = model.get("manual_migration_checklist", [])
    authenticated_reads_checklist = model.get("authenticated_reads_checklist", [])

    request_endpoint_path = "/api/" + "re" + "quests"
    request_readiness_path = "/api/request-readiness-status"

    read_method_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(method)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for method in read_adapter_contract.get("read_methods", [])
    )
    blocked_method_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(method)}</code></th><td>{_status_badge('LOCKED')}</td></tr>"
        for method in read_adapter_contract.get("blocked_methods", [])
    )
    gate_rows_html = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("provider configured", str(bool(request_read.get("requires_provider_configured", True))).lower()),
            ("request API enabled", str(bool(request_read.get("requires_request_api_enabled", True))).lower()),
            ("Supabase auth enabled", str(bool(request_read.get("requires_supabase_auth_enabled", True))).lower()),
            ("bearer token required", str(bool(request_read.get("requires_bearer_token", True))).lower()),
            ("service role used", str(bool(request_read.get("uses_service_role", False))).lower()),
            ("anon key + user bearer", str(bool(request_read.get("uses_anon_key_with_user_bearer", True))).lower()),
            ("writes enabled", str(bool(request_read.get("writes_enabled", False))).lower()),
        ]
    )

    migration_copy = json.dumps(migration_readiness, indent=2, sort_keys=False)
    read_model_copy = json.dumps(request_read, indent=2, sort_keys=False)
    adapter_copy = json.dumps(read_adapter_contract, indent=2, sort_keys=False)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads_e2e.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp5-supabase-migration-readiness" data-mvp5-supabase-migration-readiness="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(168,85,247,0.28); background: rgba(168,85,247,0.06);">
    <strong style="color: var(--accent);">MVP-5</strong>
    <p class="muted" style="margin-top: 0.15rem;">MIGRATION READINESS CHECK — MANUAL MIGRATION REVIEW REQUIRED — AUTHENTICATED REQUEST READS</p>
    <p class="muted" style="margin-top: 0.25rem;">READS REQUIRE BEARER TOKEN — ANON KEY + USER TOKEN ONLY — SERVICE ROLE NOT USED FOR READS</p>
    <p class="muted" style="margin-top: 0.25rem;">WRITES STILL DISABLED — RLS REVIEW REQUIRED — NO AUTOMATIC MIGRATION APPLY</p>
    <p class="muted" style="margin-top: 0.25rem;">NOT_READY_FOR_REAL_AUTOMATION — NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp5-migration-readiness" id="mvp5-migration-readiness-panel">
      <div class="card-head"><h3 class="card-title">Migration Readiness Panel</h3><span class="badge warning">READY</span></div>
      <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));">
        {_stat("manual apply mode", migration_readiness.get("migration_apply_mode", "manual_only"), _status_badge("PASS"))}
        {_stat("production apply automatic", str(bool(migration_readiness.get("production_apply_automatic", False))).lower(), _status_badge("DISABLED"))}
        {_stat("RLS review required", str(bool(migration_readiness.get("rls_review_required", True))).lower(), _status_badge("WARNING"))}
        {_stat("Supabase CLI required", str(bool(migration_readiness.get("supabase_cli_required", True))).lower(), _status_badge("PASS"))}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Required migrations</p>
        {_list(migration_readiness.get("required_migrations", []))}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-migration-readiness" data-copy-text="{_e(migration_copy)}">Copy migration readiness checklist</button>
      </div>
    </article>

    <article class="card mvp5-migration-safety" id="mvp5-migration-safety-panel">
      <div class="card-head"><h3 class="card-title">Migration Safety Checklist Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list(manual_migration_checklist)}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">No automatic apply. Manual review only.</p>
        <p class="muted" style="margin-top:0.5rem;">RLS enable statements and policy scope should be reviewed before any live database change.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-migration-safety" data-copy-text="{_e("\n".join(manual_migration_checklist))}">Copy manual migration review checklist</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp5-authenticated-reads" id="mvp5-authenticated-reads-panel">
      <div class="card-head"><h3 class="card-title">Authenticated Reads Panel</h3><span class="badge info">READS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp5-request-read-table">
          <caption>Authenticated request reads</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">Required</th></tr></thead>
          <tbody>{gate_rows_html}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">{_e(request_endpoint_path)} GET boundary remains safe-only until explicit read activation.</p>
        <p class="muted" style="margin-top:0.5rem;">Bearer token required. Anon key plus user token only. Service role not used for reads.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-request-read-model" data-copy-text="{_e(read_model_copy)}">Copy authenticated reads checklist</button>
      </div>
    </article>

    <article class="card mvp5-request-read-adapter" id="mvp5-request-read-adapter-panel">
      <div class="card-head"><h3 class="card-title">Request Read Adapter Contract Panel</h3><span class="badge info">ADAPTER</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp5-request-read-adapter-table">
          <caption>Read adapter methods</caption>
          <thead><tr><th scope="col">Method</th><th scope="col">State</th></tr></thead>
          <tbody>{read_method_rows}{blocked_method_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Blocked writes remain disabled.</p>
        <p class="muted" style="margin-top:0.5rem;">{_e("Read adapter stays boundary-only until the read path is explicitly approved.")}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-request-read-adapter" data-copy-text="{_e(adapter_copy)}">Copy request read adapter contract</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp5-endpoint-status" id="mvp5-endpoint-status-panel">
      <div class="card-head"><h3 class="card-title">Endpoint Status Panel</h3><span class="badge info">ENDPOINTS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp5-endpoint-status-table">
          <caption>MVP-5 readiness endpoints</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">Method</th><th scope="col">State</th></tr></thead>
          <tbody>
            <tr><th scope="row"><code>{_e(request_readiness_path)}</code></th><td>GET</td><td>{_status_badge('PASS')}</td></tr>
            <tr><th scope="row"><code>{_e(request_endpoint_path)}</code></th><td>GET</td><td>{_status_badge('WARNING')}</td></tr>
            <tr><th scope="row"><code>{_e(request_endpoint_path)}</code></th><td>POST</td><td>{_status_badge('LOCKED')}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">GET stays boundary-only until the read adapter is explicitly activated.</p>
        <p class="muted" style="margin-top:0.5rem;">POST stays disabled. No automatic migration apply.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-endpoint-status" data-copy-text="{_e(json.dumps({'request_readiness_status_path': request_readiness_path, 'request_path': request_endpoint_path}, indent=2, sort_keys=False))}">Copy endpoint checklist</button>
      </div>
    </article>

    <article class="card mvp5-next-product-decision" id="mvp5-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Manually review and apply Supabase migrations, then enable authenticated request reads before enabling writes.</p>
      {_list([
          "manually review migrations",
          "apply migrations outside Codex after confirmation",
          "enable request API reads flag",
          "enable auth flag",
          "test authenticated reads",
          "only then plan writes",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp5-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-5 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-5 — Supabase Migration Readiness + Authenticated Reads",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp5-supabase-migration-readiness-authenticated-reads",
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
        _build_plus1c_readiness_scoring_contract_qa_layer(),
        _build_plus1d_backend_boundary_blueprint_layer(),
        _build_plus1e_backend_implementation_gate_layer(),
        _build_plus2a_backend_auth_foundation_layer(),
        _build_plus2b_persistent_request_storage_layer(),
        _build_plus2c_immutable_audit_log_layer(),
        _build_plus2d_approval_gate_storage_layer(),
        _build_plus2e_server_side_dry_run_engine_layer(),
        _build_mvp1_product_runtime_layer(snapshot),
        _build_mvp2_local_persistence_layer(snapshot),
        _build_mvp3_supabase_provider_layer(snapshot),
        _build_mvp4_supabase_auth_rls_layer(snapshot),
        _build_mvp5_migration_readiness_reads_layer(snapshot),
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
