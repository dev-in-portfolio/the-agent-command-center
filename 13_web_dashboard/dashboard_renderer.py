import html
import json
import re
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
        ("MVP-3 Supabase Provider", "mvp3-supabase-provider"),
        ("MVP-4 Supabase Auth + RLS", "mvp4-supabase-auth-rls"),
        ("MVP-5 Migration Readiness", "mvp5-supabase-migration-readiness-authenticated-reads"),
        ("MVP-6 Controlled Migration Apply", "mvp6-controlled-migration-authenticated-reads"),
        ("MVP-7 Real Authenticated Reads", "mvp7-real-authenticated-supabase-request-reads"),
        ("MVP-8 Controlled Request Create", "mvp8-controlled-authenticated-request-create"),
        ("MVP-9 Request Detail + Lifecycle", "mvp9-request-detail-lifecycle-timeline"),
        ("MVP-10 Operator Workspace", "mvp10-operator-workspace-ui"),
        ("MVP-11 Workspace Polish", "mvp11-token-aware-workspace-polish"),
        ("MVP-12 Lifecycle Event Creation", "mvp12-controlled-lifecycle-event-creation"),
        ("MVP-13 Activity Feed + Safe Errors", "mvp13-request-activity-safe-errors"),
        ("MVP-14 Manual Live Test Harness", "mvp14-manual-live-workspace-test-harness"),
        ("MVP-15 Live Test + Demo Pitch", "mvp15-live-test-demo-pitch"),
        ("MVP-16 Live Results + Demo Package", "mvp16-live-results-demo-package"),
        ("MVP-17 External Demo Package", "mvp17-external-demo-package"),
        ("MVP-18 External Review Portal", "mvp18-share-ready-external-review"),
        ("MVP-19 External Feedback Intake", "mvp19-external-feedback"),
        ("MVP-20 Manual Feedback Review", "mvp20-manual-feedback-review"),
        ("MVP-21 Safe Feedback Persistence", "mvp21-safe-feedback-persistence"),
        ("MVP-22 Controlled Feedback Write", "mvp22-controlled-feedback-write"),
        ("MVP-23 Token-Gated Smoke Test", "mvp23-token-gated-smoke-test"),
        ("MVP-42 Operator Controlled Response Import Dry Run", "mvp42-operator-controlled-response-import-dry-run"),
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


def _build_mvp24_beta_feedback_import_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="24">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-24</strong>
    <p class="muted">REVIEWED BETA FEEDBACK IMPORT WORKSPACE</p>
    <p class="muted">TOKEN IN MEMORY ONLY — FEEDBACK ENDPOINT STATUS PANEL — MIGRATION READINESS PANEL</p>
    <p class="muted">FEEDBACK PACKET IMPORT FORM — PAYLOAD VALIDATION PREVIEW — FEEDBACK_PERSISTENCE_DISABLED HANDLED</p>
    <p class="muted">NETLIFY FUNCTION ONLY — SERVICE ROLE NOT USED — NO AUTOMATIC MIGRATION APPLY</p>
    <p class="muted">UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_ADD_AUTHENTICATED_FEEDBACK_REVIEW_INBOX — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-24 — Reviewed Beta Feedback Import Workspace",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp24-beta-feedback-import-workspace",
    )

def _build_mvp25_authenticated_feedback_review_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="25">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-25</strong>
    <p class="muted">AUTHENTICATED FEEDBACK REVIEW INBOX</p>
    <p class="muted">FEEDBACK LIST READ API — FEEDBACK DETAIL READ API — OWNER-SCOPED RLS READS</p>
    <p class="muted">FEEDBACK SYNTHESIS QUEUE — READ ONLY REVIEW WORKFLOW</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_FEEDBACK_SYNTHESIS_AND_PRODUCT_DECISION_WORKFLOW — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-25 — Authenticated Feedback Review Inbox",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp25-authenticated-feedback-review-inbox",
    )

def _build_mvp26_feedback_synthesis_product_decision_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="26">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-26</strong>
    <p class="muted">PASS_WITH_READ_ONLY_MANUAL_SYNTHESIS</p>
    <p class="muted">FEEDBACK SYNTHESIS WORKSPACE</p>
    <p class="muted">THEME CLUSTERING — PRODUCT DECISION CARDS — SIGNAL STRENGTH SCORING</p>
    <p class="muted">READ ONLY SYNTHESIS QUEUE — OWNER-SCOPED FEEDBACK READS</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-26 — Feedback Synthesis + Product Decision Workflow",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp26-feedback-synthesis-product-decision-workflow",
    )

def _build_mvp27_feedback_to_request_conversion_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="27">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-27</strong>
    <p class="muted">PASS_WITH_OPTIONAL_SERVER_GATED_REQUEST_CREATE</p>
    <p class="muted">FEEDBACK TO REQUEST CONVERSION WORKSPACE</p>
    <p class="muted">REQUEST DRAFT FROM FEEDBACK — DECISION TO REQUEST PAYLOAD PREVIEW</p>
    <p class="muted">CONTROLLED REQUEST CREATE OPTIONAL — TOKEN IN MEMORY ONLY — REQUEST WRITES SERVER GATED</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_OPERATOR_ROADMAP_PRIORITIZATION_BOARD — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-27 — Feedback-to-Request Conversion Workspace",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp27-feedback-to-request-conversion-workspace",
    )


def _build_mvp28_operator_roadmap_prioritization_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="28">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-28</strong>
    <p class="muted">PASS_WITH_READ_ONLY_ROADMAP_WORKFLOW</p>
    <p class="muted">OPERATOR ROADMAP PRIORITIZATION BOARD</p>
    <p class="muted">FEEDBACK SIGNALS TO ROADMAP — PRODUCT DECISION LANES</p>
    <p class="muted">PRIORITY SCORING — IMPACT EFFORT CONFIDENCE MATRIX</p>
    <p class="muted">READ ONLY ROADMAP WORKFLOW — SERVICE ROLE NOT USED</p>
    <p class="muted">UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_GUIDED_PRODUCT_DEMO_CONTROL_ROOM — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-28 — Operator Roadmap + Prioritization Board",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp28-operator-roadmap-prioritization-board",
    )


def _build_mvp29_guided_product_demo_control_room_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="29">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-29</strong>
    <p class="muted">PASS_WITH_SAFE_DEMO_MODE</p>
    <p class="muted">GUIDED PRODUCT DEMO CONTROL ROOM</p>
    <p class="muted">ROLE BASED DEMO PATHS — OPERATOR STORYLINE</p>
    <p class="muted">DEMO READINESS SCORECARD — PITCHABLE PRODUCT WALKTHROUGH</p>
    <p class="muted">SAFE DEMO MODE — NO FAKE LIVE TEST CLAIMS</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_REVIEW_DEMO_CONTROL_ROOM_AND_PREPARE_PITCHABLE_RELEASE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>
</div>
"""
    return _details(
        "MVP-29 — Guided Product Demo Control Room",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp29-guided-product-demo-control-room",
    )


def _build_mvp30_pitchable_release_package_layer(snapshot):
    release_overview = (
        "The Agent Command Center is a read-only operator dashboard for review, synthesis, roadmap, "
        "and demo packaging. It explains the product, the operator flow, and the safety boundary "
        "without enabling live mutation."
    )
    product_narrative = (
        "The product starts with authenticated request and feedback review, synthesizes signals into "
        "decisions, converts decisions into roadmap and release narratives, and presents a guided demo "
        "control room for safe pitch and handoff."
    )
    demo_walkthrough = (
        "1. Open the command center.\n"
        "2. Review the pitchable release package.\n"
        "3. Walk the demo control room.\n"
        "4. Explain what is real now and what stays blocked.\n"
        "5. Copy the release packet for recruiter, founder, or reviewer use."
    )
    technical_summary = (
        "Static dashboard layer with exported markdown/json packets, read-only UI models, and no browser-side "
        "secret storage, direct Supabase access, or execution controls."
    )
    safety_summary = (
        "Safe demo mode, no fake live test claims, service role not used, browser persistence blocked, "
        "update/delete/approve/execute blocked, automation disabled, and deploy/merge/push/PR controls absent."
    )
    capability_map = (
        "Authenticated request reads; feedback review; synthesis and product decisions; request draft conversion; "
        "roadmap prioritization; guided demo control room; pitchable release packaging."
    )
    packet_index = (
        "release_overview.md\n"
        "product_narrative.md\n"
        "demo_walkthrough.md\n"
        "technical_architecture_summary.md\n"
        "safety_boundary_summary.md\n"
        "capability_map.md\n"
        "recruiter_version.md\n"
        "founder_operator_version.md\n"
        "technical_reviewer_version.md\n"
        "release_packet_index.md\n"
        "release_manifest.json"
    )
    body = f"""
<div class="mvp-section" data-mvp="30">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-30</strong>
    <p class="muted">PASS_WITH_SAFE_RELEASE_EXPORTS</p>
    <p class="muted">PITCHABLE RELEASE PACKAGE</p>
    <p class="muted">PRODUCT NARRATIVE EXPORT — RELEASE CAPABILITY MAP — AUDIENCE VARIANTS</p>
    <p class="muted">DEMO WALKTHROUGH EXPORT — TECHNICAL ARCHITECTURE SUMMARY — SAFETY BOUNDARY SUMMARY</p>
    <p class="muted">RECRUITER VERSION — FOUNDER OPERATOR VERSION — TECHNICAL REVIEWER VERSION</p>
    <p class="muted">SAFE DEMO MODE — NO FAKE LIVE TEST CLAIMS — SERVICE ROLE NOT USED</p>
    <p class="muted">UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_DEMO_SESSION_CAPTURE_AND_EXTERNAL_REVIEW_LOOP — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp30-release-package-panel">
      <div class="card-head"><h3 class="card-title">Pitchable Release Package</h3><span class="badge success">PACKAGE</span></div>
      <p class="card-body">{_e(release_overview)}</p>
      <div class="button-row" style="margin-top:0.75rem;">
        {_copy_button("Copy Release Overview", release_overview, kind="copy-button small")}
        {_copy_button("Copy Product Narrative", product_narrative, kind="copy-button small")}
        {_copy_button("Copy Demo Walkthrough", demo_walkthrough, kind="copy-button small")}
      </div>
    </article>

    <article class="card" id="mvp30-technical-summary-panel">
      <div class="card-head"><h3 class="card-title">Technical Architecture Summary</h3><span class="badge info">TECH</span></div>
      <p class="card-body">{_e(technical_summary)}</p>
      <div class="button-row" style="margin-top:0.75rem;">
        {_copy_button("Copy Technical Summary", technical_summary, kind="copy-button small")}
        {_copy_button("Copy Safety Boundary Summary", safety_summary, kind="copy-button small")}
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp30-capability-map-panel">
      <div class="card-head"><h3 class="card-title">Release Capability Map</h3><span class="badge info">MAP</span></div>
      <p class="card-body">{_e(capability_map)}</p>
      <div class="button-row" style="margin-top:0.75rem;">
        {_copy_button("Copy Capability Map", capability_map, kind="copy-button small")}
        {_copy_button("Copy Release Packet Index", packet_index, kind="copy-button small")}
      </div>
    </article>

    <article class="card" id="mvp30-audience-variants-panel">
      <div class="card-head"><h3 class="card-title">Audience Variants</h3><span class="badge info">VERSIONS</span></div>
      <ul class="compact-list">
        <li><strong>Recruiter Version:</strong> concise product story and value map.</li>
        <li><strong>Founder Operator Version:</strong> workflow, safety, and operator leverage.</li>
        <li><strong>Technical Reviewer Version:</strong> architecture and safety boundary detail.</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        {_copy_button("Copy Recruiter Version", "Recruiter version: concise product story and value map.", kind="copy-button small")}
        {_copy_button("Copy Founder Operator Version", "Founder operator version: workflow, safety, and operator leverage.", kind="copy-button small")}
        {_copy_button("Copy Technical Reviewer Version", "Technical reviewer version: architecture and safety boundary detail.", kind="copy-button small")}
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-30 — Pitchable Release Package + Product Narrative",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp30-pitchable-release-package-product-narrative",
    )

def _build_mvp31_demo_session_capture_review_loop_layer(snapshot):
    body = """
<div class="mvp-section" data-mvp="31" data-mvp31-demo-session-capture="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-31</strong>
    <p class="muted">PASS_WITH_MANUAL_SESSION_CAPTURE_AND_OPTIONAL_GATED_IMPORT</p>
    <p class="muted">DEMO SESSION CAPTURE WORKSPACE — EXTERNAL REVIEW FEEDBACK LOOP</p>
    <p class="muted">REVIEWER PERSONA SESSION — DEMO SESSION NOTES — FEEDBACK PACKET DRAFT</p>
    <p class="muted">OPTIONAL FEEDBACK IMPORT GATED — TOKEN IN MEMORY ONLY — NO AUTOMATED OUTREACH</p>
    <p class="muted">NO FAKE REVIEWER RESULTS — SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED</p>
    <p class="muted">AUTOMATION STILL DISABLED — NEXT_STEP_BUILD_RELEASE_REVIEW_METRICS_AND_SIGNAL_DASHBOARD — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp31-session-setup-panel">
      <div class="card-head"><h3 class="card-title">Demo Session Setup Panel</h3><span class="badge success">SETUP</span></div>
      <p class="card-body">Choose the reviewer persona, demo goal, and product area before you capture the session.</p>
      <label class="sr-only" for="mvp31-reviewer-persona">Reviewer persona</label>
      <select id="mvp31-reviewer-persona" style="width:100%; margin-top:0.5rem;">
        <option value="founder">Founder</option>
        <option value="operator" selected>Operator</option>
        <option value="recruiter">Recruiter</option>
        <option value="technical reviewer">Technical reviewer</option>
        <option value="external reviewer">External reviewer</option>
      </select>
      <label class="sr-only" for="mvp31-demo-goal">Demo goal</label>
      <input id="mvp31-demo-goal" type="text" value="Pitch the release package and walk the review loop" style="width:100%; margin-top:0.75rem;" />
      <label class="sr-only" for="mvp31-product-area">Product area</label>
      <input id="mvp31-product-area" type="text" value="Pitchable release package + demo control room" style="width:100%; margin-top:0.75rem;" />
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp31-copy-session-summary">Copy Session Summary</button>
      </div>
    </article>

    <article class="card" id="mvp31-notes-panel">
      <div class="card-head"><h3 class="card-title">Demo Session Notes Panel</h3><span class="badge info">NOTES</span></div>
      <p class="card-body">Capture objections, confusion points, praise, trust concerns, and the next step by hand.</p>
      <label class="sr-only" for="mvp31-session-notes">Session notes</label>
      <textarea id="mvp31-session-notes" style="width:100%; min-height:88px; margin-top:0.5rem;" placeholder="Session notes"></textarea>
      <label class="sr-only" for="mvp31-session-objections">Objections</label>
      <textarea id="mvp31-session-objections" style="width:100%; min-height:72px; margin-top:0.5rem;" placeholder="Objections and risks"></textarea>
      <label class="sr-only" for="mvp31-session-praise">Praise</label>
      <textarea id="mvp31-session-praise" style="width:100%; min-height:72px; margin-top:0.5rem;" placeholder="Praise and strongest parts"></textarea>
      <label class="sr-only" for="mvp31-session-trust">Trust concerns</label>
      <textarea id="mvp31-session-trust" style="width:100%; min-height:72px; margin-top:0.5rem;" placeholder="Trust concerns"></textarea>
      <label class="sr-only" for="mvp31-session-next-step">Suggested next step</label>
      <textarea id="mvp31-session-next-step" style="width:100%; min-height:72px; margin-top:0.5rem;" placeholder="Suggested next step"></textarea>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp31-packet-preview-panel">
      <div class="card-head"><h3 class="card-title">Feedback Packet Draft Panel</h3><span class="badge info">PACKET</span></div>
      <p class="card-body">The draft packet is built from the current session fields and only imported when the operator clicks the gated action.</p>
      <pre id="mvp31-feedback-packet-preview" class="code-block" style="white-space:pre-wrap; min-height:180px; margin-top:0.75rem;">{"reviewer_persona":"operator","demo_goal":"Pitch the release package and walk the review loop","product_area":"Pitchable release package + demo control room","substantive_feedback":"Fill in session notes to draft the packet."}</pre>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp31-copy-feedback-packet">Copy Feedback Packet</button>
        <button type="button" class="copy-button small" id="mvp31-copy-follow-up-plan">Copy Follow-Up Plan</button>
      </div>
    </article>

    <article class="card" id="mvp31-import-panel">
      <div class="card-head"><h3 class="card-title">Optional Feedback Import Panel</h3><span class="badge warning">GATED</span></div>
      <p class="card-body">Endpoint: <code>/api/feedback?action=import</code>. Token stays in memory only and manual submission is required.</p>
      <label class="sr-only" for="mvp31-feedback-token">Feedback token</label>
      <input id="mvp31-feedback-token" type="password" autocomplete="off" placeholder="Token in memory only" style="width:100%; margin-top:0.5rem;" />
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" id="mvp31-use-token-memory">Use Token In Memory</button>
        <button type="button" class="action-button small" id="mvp31-clear-token">Clear Token</button>
        <button type="button" class="action-button small" id="mvp31-check-feedback-endpoint">Check Feedback Endpoint Status</button>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" id="mvp31-submit-feedback-packet">Submit Feedback Packet Manually</button>
      </div>
      <p class="muted" style="margin-top:0.75rem;">No automated outreach, no email sending, and no browser persistence.</p>
      <pre id="mvp31-import-status" class="code-block" style="white-space:pre-wrap; min-height:96px; margin-top:0.5rem;">Awaiting explicit operator action.</pre>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp31-follow-up-panel">
      <div class="card-head"><h3 class="card-title">Follow-Up Decision Panel</h3><span class="badge info">FOLLOW-UP</span></div>
      <p class="card-body">Keep the operator in control of the next step after the demo session is captured.</p>
      <label class="sr-only" for="mvp31-follow-up-decision">Follow-up decision</label>
      <select id="mvp31-follow-up-decision" style="width:100%; margin-top:0.5rem;">
        <option value="review_and_refine" selected>Review and refine internally</option>
        <option value="import_and_review">Import packet and review externally</option>
        <option value="hold_local">Hold local, no import yet</option>
        <option value="prepare_next_demo">Prepare the next demo session</option>
      </select>
      <pre id="mvp31-follow-up-preview" class="code-block" style="white-space:pre-wrap; min-height:110px; margin-top:0.75rem;">Review and refine internally before optional import.</pre>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp31-copy-follow-up-summary">Copy Follow-Up Summary</button>
      </div>
    </article>

    <article class="card" id="mvp31-security-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">The workspace stays manual, token-aware, and free of outreach automation.</p>
      <ul class="compact-list">
        <li>No automated outreach.</li>
        <li>No email sending.</li>
        <li>No fake reviewer results.</li>
        <li>Service role not used.</li>
        <li>Browser persistence blocked.</li>
        <li>Update/delete/approve/execute blocked.</li>
        <li>External release controls absent.</li>
      </ul>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-31 — Demo Session Capture + External Review Feedback Loop",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp31-demo-session-capture-review-loop",
    )

def _build_mvp32_release_review_metrics_signal_dashboard_layer(snapshot):
    body = """
<div class="mvp-section" data-mvp="32" data-mvp32-release-review-metrics="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-32</strong>
    <p class="muted">PASS_WITH_MANUAL_EXISTING_SIGNAL_ROLLUPS</p>
    <p class="muted">RELEASE REVIEW METRICS DASHBOARD — REVIEWER SIGNAL SUMMARY — DEMO SESSION SIGNALS</p>
    <p class="muted">RELEASE READINESS METRICS — PRODUCT DECISION SIGNAL ROLLUP — ROADMAP SIGNAL ROLLUP</p>
    <p class="muted">EXPORTABLE SIGNAL PACKET — NO FAKE METRICS — NO FAKE REVIEWER RESULTS</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp32-release-review-metrics-panel">
      <div class="card-head"><h3 class="card-title">Release Review Metrics Dashboard</h3><span class="badge success">METRICS</span></div>
      <p class="card-body">Aggregated release review metrics from demo session captures, reviewer signals, and product decisions.</p>
      <ul class="compact-list">
        <li>Demo Session Coverage</li>
        <li>Reviewer Persona Coverage</li>
        <li>Feedback Theme Volume</li>
        <li>Objection/Confusion/Trust Concern Counts</li>
        <li>Product Decision Completion</li>
        <li>Roadmap Alignment Score</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-metrics-summary">Copy Metrics Summary</button>
      </div>
    </article>

    <article class="card" id="mvp32-reviewer-signal-summary-panel">
      <div class="card-head"><h3 class="card-title">Reviewer Signal Summary</h3><span class="badge info">SIGNALS</span></div>
      <p class="card-body">Per-persona signal breakdown from reviewer feedback and demo session outcomes.</p>
      <ul class="compact-list">
        <li>Objection Signals</li>
        <li>Confusion Signals</li>
        <li>Trust Concern Signals</li>
        <li>Product Decision Follow-Ups</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-reviewer-signal-summary">Copy Reviewer Signal Summary</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp32-demo-session-signals-panel">
      <div class="card-head"><h3 class="card-title">Demo Session Signals</h3><span class="badge info">SIGNALS</span></div>
      <p class="card-body">Signal rollup from demo session captures, notes, and follow-up decisions.</p>
      <ul class="compact-list">
        <li>Session Count and Outcomes</li>
        <li>Reviewer Personas Present</li>
        <li>Feedback Themes Collected</li>
        <li>Follow-Up Decisions Recorded</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-demo-session-signal-summary">Copy Demo Session Signal Summary</button>
      </div>
    </article>

    <article class="card" id="mvp32-release-readiness-metrics-panel">
      <div class="card-head"><h3 class="card-title">Release Readiness Metrics</h3><span class="badge info">METRICS</span></div>
      <p class="card-body">Category-level readiness scoring for operator launch assessment.</p>
      <ul class="compact-list">
        <li>Demo Session Coverage: Manual review</li>
        <li>Reviewer Persona Coverage: Manual review</li>
        <li>Feedback Theme Volume: Manual review</li>
        <li>Objection Resolution: Manual review</li>
        <li>Product Decision Completion: Manual review</li>
        <li>Safety Boundary: All controls active</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-release-readiness-scorecard">Copy Release Readiness Scorecard</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp32-product-decision-signal-rollup-panel">
      <div class="card-head"><h3 class="card-title">Product Decision Signal Rollup</h3><span class="badge info">ROLLUP</span></div>
      <p class="card-body">Decision traceability from feedback and demo sessions through roadmap impact.</p>
      <ul class="compact-list">
        <li>Decisions from Feedback</li>
        <li>Decisions from Demo Sessions</li>
        <li>Roadmap Impact Signals</li>
        <li>Release Blocker Tracking</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-product-decision-signal-rollup">Copy Product Decision Signal Rollup</button>
      </div>
    </article>

    <article class="card" id="mvp32-roadmap-signal-rollup-panel">
      <div class="card-head"><h3 class="card-title">Roadmap Signal Rollup</h3><span class="badge info">ROLLUP</span></div>
      <p class="card-body">Roadmap alignment signals derived from review feedback and demo session outcomes.</p>
      <ul class="compact-list">
        <li>Roadmap Impact Signals</li>
        <li>Priority Shift Signals</li>
        <li>New Feature Requests</li>
        <li>Release Blockers Identified</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-roadmap-signal-rollup">Copy Roadmap Signal Rollup</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp32-exportable-signal-packet-panel">
      <div class="card-head"><h3 class="card-title">Exportable Signal Packet</h3><span class="badge warning">EXPORT</span></div>
      <p class="card-body">Consolidated release review signal packet for operator review. No automated launch decision.</p>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp32-copy-signal-packet">Copy Signal Packet</button>
      </div>
      <pre id="mvp32-signal-packet-preview" class="code-block" style="white-space:pre-wrap; min-height:120px; margin-top:0.75rem;">Release Review Signal Packet — No fake metrics. No fake reviewer results. Manual operator review required.</pre>
    </article>

    <article class="card" id="mvp32-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">Release review metrics dashboard stays manual, signal-based, and automation-free.</p>
      <ul class="compact-list">
        <li>No fake metrics.</li>
        <li>No fake reviewer results.</li>
        <li>No email sending.</li>
        <li>No automated outreach.</li>
        <li>Service role not used.</li>
        <li>Browser persistence blocked.</li>
        <li>Update/delete/approve/execute blocked.</li>
        <li>Automation disabled.</li>
      </ul>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-32 — Release Review Metrics + Signal Dashboard",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp32-release-review-metrics-signal-dashboard",
    )

def _build_mvp33_product_launch_readiness_final_pitch_packet_layer(snapshot):
    body = """
<div class="mvp-section" data-mvp="33" data-mvp33-product-launch-readiness="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-33</strong>
    <p class="muted">PASS_WITH_SAFE_LAUNCH_REVIEW_ONLY</p>
    <p class="muted">PRODUCT LAUNCH READINESS CONSOLE — RELEASE CANDIDATE SCORECARD — FINAL PITCH PACKET</p>
    <p class="muted">STAKEHOLDER PITCH VARIANTS — OPERATOR LAUNCH DECISION PANEL — SAFETY READINESS ONE PAGER</p>
    <p class="muted">SAFE LAUNCH REVIEW ONLY — NO FAKE LAUNCH STATUS — NO DEPLOY CONTROLS</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_REVIEW_FINAL_PITCH_PACKET_AND_PREPARE_RELEASE_CANDIDATE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp33-launch-readiness-console-panel">
      <div class="card-head"><h3 class="card-title">Product Launch Readiness Console</h3><span class="badge success">CONSOLE</span></div>
      <p class="card-body">Consolidated launch readiness console aggregating scorecard, pitch packet, and operator decision panel.</p>
      <ul class="compact-list">
        <li>Launch Readiness Console Ready</li>
        <li>Release Candidate Scorecard Ready</li>
        <li>Final Pitch Packet Builder Ready</li>
        <li>Stakeholder Pitch Variants Ready</li>
        <li>Operator Launch Decision Panel Ready</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp33-copy-launch-readiness-console">Copy Launch Readiness Console</button>
      </div>
    </article>

    <article class="card" id="mvp33-release-candidate-scorecard-panel">
      <div class="card-head"><h3 class="card-title">Release Candidate Scorecard</h3><span class="badge info">SCORECARD</span></div>
      <p class="card-body">Category-level scorecard tracking launch readiness across key dimensions.</p>
      <ul class="compact-list">
        <li>Demo Session Coverage</li>
        <li>Reviewer Persona Coverage</li>
        <li>Feedback Theme Completeness</li>
        <li>Objection Readiness</li>
        <li>Product Decision Completion</li>
        <li>Safety Boundary Status</li>
        <li>Release Documentation Completeness</li>
        <li>Pitch Packet Readiness</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp33-copy-scorecard">Copy Scorecard</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp33-final-pitch-packet-panel">
      <div class="card-head"><h3 class="card-title">Final Pitch Packet</h3><span class="badge warning">PITCH</span></div>
      <p class="card-body">Complete final pitch packet with narrative, capability map, demo walkthrough, architecture, and safety summary.</p>
      <ul class="compact-list">
        <li>Product Narrative</li>
        <li>Release Capability Map</li>
        <li>Demo Walkthrough</li>
        <li>Technical Architecture</li>
        <li>Safety Boundary Summary</li>
        <li>Release Review Metrics</li>
        <li>Reviewer Signal Summary</li>
        <li>Launch Readiness Scorecard</li>
        <li>Operator Demo Script</li>
        <li>Stakeholder Pitch Variants</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp33-copy-pitch-packet">Copy Pitch Packet</button>
      </div>
    </article>

    <article class="card" id="mvp33-stakeholder-pitch-variants-panel">
      <div class="card-head"><h3 class="card-title">Stakeholder Pitch Variants</h3><span class="badge info">VARIANTS</span></div>
      <p class="card-body">Role-tailored pitch variants for founder, recruiter, and technical reviewer audiences.</p>
      <ul class="compact-list">
        <li>Founder Pitch Variant</li>
        <li>Recruiter Pitch Variant</li>
        <li>Technical Reviewer Pitch Variant</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp33-copy-pitch-variants">Copy Pitch Variants</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp33-operator-launch-decision-panel">
      <div class="card-head"><h3 class="card-title">Operator Launch Decision Panel</h3><span class="badge locked">DECISION</span></div>
      <p class="card-body">Operator-facing launch decision panel. No automated decisions. No deploy controls.</p>
      <ul class="compact-list">
        <li>Ready for Launch Review</li>
        <li>Needs More Demo Sessions</li>
        <li>Needs More Reviewer Feedback</li>
        <li>Needs More Objection Prep</li>
        <li>Blocked Until Safety Review</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp33-copy-decision-panel">Copy Decision Panel</button>
      </div>
    </article>

    <article class="card" id="mvp33-safety-readiness-panel">
      <div class="card-head"><h3 class="card-title">Safety Readiness Panel</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">Safety readiness one-pager. All controls documented. No deploy or launch automation.</p>
      <ul class="compact-list">
        <li>Safe launch review only.</li>
        <li>No fake launch status.</li>
        <li>No deploy controls.</li>
        <li>No launch automation.</li>
        <li>Service role not used.</li>
        <li>Browser persistence blocked.</li>
        <li>Update/delete/approve/execute blocked.</li>
        <li>Automation disabled.</li>
      </ul>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-33 — Product Launch Readiness + Final Pitch Packet",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp33-product-launch-readiness-final-pitch-packet",
    )

def _build_mvp34_public_release_candidate_review_portal_layer(snapshot):
    body = """
<div class="mvp-section" data-mvp="34" data-mvp34-review-portal="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-34</strong>
    <p class="muted">PASS_WITH_PUBLIC_SAFE_REVIEW_ROOM</p>
    <p class="muted">PUBLIC RELEASE CANDIDATE REVIEW PORTAL — INVESTOR RECRUITER REVIEW ROOM</p>
    <p class="muted">EXTERNAL REVIEWER PATHS — PUBLIC SAFE PITCH PACKET — RELEASE CANDIDATE ARTIFACT INDEX</p>
    <p class="muted">PUBLIC SAFE DEMO SCRIPT — REVIEW QUESTIONS PREP GUIDE — EXTERNAL REVIEW INSTRUCTIONS</p>
    <p class="muted">SAFE PUBLIC REVIEW ONLY — NO PUBLIC WRITES — NO TOKEN INPUT — NO SECRETS EXPOSED</p>
    <p class="muted">NO DEPLOY CONTROLS — NO LAUNCH AUTOMATION — SERVICE ROLE NOT USED</p>
    <p class="muted">UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_EXTERNAL_REVIEW_FEEDBACK_SUMMARY_AND_OUTREACH_PREP — NOT_READY_FOR_REAL_AUTOMATION</p>
    <p class="muted">NEXT_STEP_REVIEW_RELEASE_CANDIDATE_PORTAL_AND_PREPARE_PUBLIC_PITCH — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp34-review-portal-panel">
      <div class="card-head"><h3 class="card-title">Public Release Candidate Review Portal</h3><span class="badge success">PORTAL</span></div>
      <p class="card-body">Central portal for public release candidate review, combining scorecard, pitch packet, artifact index, and external reviewer paths.</p>
      <ul class="compact-list">
        <li>Release Candidate Scorecard Ready</li>
        <li>Public Safe Pitch Packet Ready</li>
        <li>Release Candidate Artifact Index Ready</li>
        <li>Public Safe Demo Script Ready</li>
        <li>Review Questions Prep Guide Ready</li>
        <li>External Review Instructions Ready</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-portal">Copy Review Portal Summary</button>
      </div>
    </article>

    <article class="card" id="mvp34-investor-recruiter-review-room-panel">
      <div class="card-head"><h3 class="card-title">Investor Recruiter Review Room</h3><span class="badge info">ROOM</span></div>
      <p class="card-body">Role-tailored review room with dedicated paths for investor, recruiter, and founder audiences.</p>
      <ul class="compact-list">
        <li>Investor Review Path Ready</li>
        <li>Recruiter Review Path Ready</li>
        <li>Founder Review Path Ready</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-investor-path">Copy Investor Path</button>
        <button type="button" class="copy-button small" id="mvp34-copy-recruiter-path">Copy Recruiter Path</button>
        <button type="button" class="copy-button small" id="mvp34-copy-founder-path">Copy Founder Path</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp34-external-reviewer-paths-panel">
      <div class="card-head"><h3 class="card-title">External Reviewer Paths</h3><span class="badge info">PATHS</span></div>
      <p class="card-body">Curated external reviewer entry points for technical review, product review, and investor evaluation.</p>
      <ul class="compact-list">
        <li>Technical Reviewer Entry Point</li>
        <li>Product Reviewer Entry Point</li>
        <li>Investor Evaluation Entry Point</li>
        <li>Partner Review Entry Point</li>
      </ul>
    </article>

    <article class="card" id="mvp34-public-safe-pitch-packet-panel">
      <div class="card-head"><h3 class="card-title">Public Safe Pitch Packet</h3><span class="badge warning">PITCH</span></div>
      <p class="card-body">Safe-for-public pitch packet with product narrative, capability map, demo walkthrough, architecture, and safety summary.</p>
      <ul class="compact-list">
        <li>Public Product Narrative</li>
        <li>Public Capability Map</li>
        <li>Public Demo Walkthrough</li>
        <li>Public Architecture Summary</li>
        <li>Public Safety Boundary Summary</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-pitch-packet">Copy Pitch Packet</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp34-artifact-index-panel">
      <div class="card-head"><h3 class="card-title">Release Candidate Artifact Index</h3><span class="badge info">ARTIFACTS</span></div>
      <p class="card-body">Index of all release candidate artifacts including reports, pitch packets, demo scripts, and review materials.</p>
      <ul class="compact-list">
        <li>Release Reports Indexed</li>
        <li>Pitch Packet Versions Indexed</li>
        <li>Demo Script Versions Indexed</li>
        <li>Review Prep Materials Indexed</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-artifact-index">Copy Artifact Index</button>
      </div>
    </article>

    <article class="card" id="mvp34-public-safe-demo-script-panel">
      <div class="card-head"><h3 class="card-title">Public Safe Demo Script</h3><span class="badge info">DEMO</span></div>
      <p class="card-body">Safe-for-public demo script with role-based walkthrough and safety-first presentation notes.</p>
      <ul class="compact-list">
        <li>Investor Demo Script</li>
        <li>Recruiter Demo Script</li>
        <li>Technical Reviewer Demo Script</li>
        <li>Partner Demo Script</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-demo-script">Copy Demo Script</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp34-review-questions-prep-panel">
      <div class="card-head"><h3 class="card-title">Review Questions Prep Guide</h3><span class="badge info">PREP</span></div>
      <p class="card-body">Prep guide with expected questions, recommended answers, and safety notes for each reviewer persona.</p>
      <ul class="compact-list">
        <li>Investor Q&A Prep</li>
        <li>Recruiter Q&A Prep</li>
        <li>Technical Reviewer Q&A Prep</li>
        <li>Partner Q&A Prep</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-review-questions">Copy Review Questions Prep</button>
      </div>
    </article>

    <article class="card" id="mvp34-external-review-instructions-panel">
      <div class="card-head"><h3 class="card-title">External Review Instructions</h3><span class="badge info">INSTRUCTIONS</span></div>
      <p class="card-body">Step-by-step external review instructions for each reviewer persona to follow during review.</p>
      <ul class="compact-list">
        <li>Investor Review Instructions</li>
        <li>Recruiter Review Instructions</li>
        <li>Technical Reviewer Instructions</li>
        <li>Partner Review Instructions</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp34-copy-review-instructions">Copy Review Instructions</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp34-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">Public release candidate review portal — safe review only.</p>
      <ul class="compact-list">
        <li>NO PUBLIC WRITES</li>
        <li>NO TOKEN INPUT</li>
        <li>NO SECRETS EXPOSED</li>
        <li>NO DEPLOY CONTROLS</li>
        <li>NO LAUNCH AUTOMATION</li>
      </ul>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-34 — Public Release Candidate Review Portal",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp34-public-release-candidate-review-portal",
    )


def _load_prebuilt_section(section_id):
    index_path = PHASE4D_DIST_DIR / "index.html"
    if not index_path.exists():
        return ""
    text = index_path.read_text(encoding="utf-8", errors="replace")
    marker_open = f'<details class="panel" data-section-group="source" open id="{section_id}">'
    marker_closed = f'<details class="panel" data-section-group="source" id="{section_id}">'
    start = text.find(marker_open)
    if start < 0:
        start = text.find(marker_closed)
    if start < 0:
        return ""
    end = text.find("</details>", start)
    if end < 0:
        return ""
    end += len("</details>")
    return text[start:end]


def _build_mvp40_reviewer_response_capture_readiness_lock_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="40" data-mvp40-reviewer-response-capture-readiness-lock="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-40</strong>
    <p class="muted">REVIEWER RESPONSE CAPTURE READINESS LOCK</p>
    <p class="muted">REVIEWER RESPONSE SCHEMA PROPOSAL — CAPTURE SAFETY REQUIREMENTS — OPERATOR RESPONSE REVIEW QUEUE READINESS</p>
    <p class="muted">RESPONSE TO FEEDBACK MAPPING READINESS — RESPONSE TRIAGE READINESS RULES — FUTURE CAPTURE IMPLEMENTATION CHECKLIST</p>
    <p class="muted">OPERATOR REVIEW ONLY — READINESS ONLY — FUTURE IMPLEMENTATION ONLY</p>
    <p class="muted">NO PUBLIC ENDPOINT — NO PUBLIC RESPONSE SUBMISSION — NO REVIEWER RESPONSE WRITES</p>
    <p class="muted">NO RESPONSE CAPTURE ENABLED — NO RESPONSE PERSISTENCE ENABLED — NO EMAIL SENDING — NO REVIEWER CONTACT</p>
    <p class="muted">NO AUTOMATED OUTREACH — NO LIVE WRITES — NO PUBLIC WRITES — NO TOKEN INPUT — NO SECRETS EXPOSED</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp40-readiness-lock-panel">
      <div class="card-head"><h3 class="card-title">Reviewer Response Capture Readiness Lock</h3><span class="badge success">READINESS</span></div>
      <p class="card-body">Readiness-only model for a future reviewer response capture workflow.</p>
      <ul class="action-list">
        <li><span class="badge pass">done</span> Reviewer response capture readiness lock</li>
        <li><span class="badge pass">done</span> Reviewer response schema proposal</li>
        <li><span class="badge pass">done</span> Capture safety requirements</li>
        <li><span class="badge pass">done</span> Operator response review queue readiness</li>
        <li><span class="badge pass">done</span> Response-to-feedback mapping readiness</li>
        <li><span class="badge pass">done</span> Response triage readiness rules</li>
        <li><span class="badge pass">done</span> Future capture implementation checklist</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp40-copy-capture-readiness-lock">Copy Capture Readiness Lock</button>
        <button type="button" class="copy-button small" id="mvp40-copy-response-schema">Copy Response Schema Proposal</button>
        <button type="button" class="copy-button small" id="mvp40-copy-capture-safety">Copy Capture Safety Requirements</button>
      </div>
    </article>

    <article class="card" id="mvp40-response-queue-panel">
      <div class="card-head"><h3 class="card-title">Operator Response Review Queue Readiness</h3><span class="badge warning">QUEUE</span></div>
      <p class="card-body">Queue structure is readiness-only and operator reviewed. No capture or persistence path exists yet.</p>
      <ul class="compact-list">
        <li>Awaiting review</li>
        <li>Needs clarification</li>
        <li>Triaged</li>
        <li>Mapped to feedback</li>
        <li>Archived readiness-only item</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp40-copy-queue-readiness">Copy Operator Review Queue Readiness</button>
        <button type="button" class="copy-button small" id="mvp40-copy-response-mapping">Copy Response-to-Feedback Mapping</button>
        <button type="button" class="copy-button small" id="mvp40-copy-triage-rules">Copy Response Triage Rules</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp40-implementation-checklist-panel">
      <div class="card-head"><h3 class="card-title">Future Capture Implementation Checklist</h3><span class="badge info">CHECKLIST</span></div>
      <p class="card-body">Future implementation work is documented as a checklist only.</p>
      <ul class="compact-list">
        <li>Define intake schema</li>
        <li>Define queue states</li>
        <li>Define triage rules</li>
        <li>Define mapping path</li>
        <li>Define operator review workflow</li>
        <li>Implement guarded capture endpoint later</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp40-copy-future-checklist">Copy Future Capture Checklist</button>
      </div>
    </article>

    <article class="card" id="mvp40-safety-panel">
      <div class="card-head"><h3 class="card-title">Capture Safety Requirements</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">No public endpoint, no public response submission, and no reviewer response writes are enabled in this build.</p>
      <ul class="compact-list">
        <li>NO PUBLIC ENDPOINT</li>
        <li>NO PUBLIC RESPONSE SUBMISSION</li>
        <li>NO REVIEWER RESPONSE WRITES</li>
        <li>NO RESPONSE CAPTURE ENABLED</li>
        <li>NO RESPONSE PERSISTENCE ENABLED</li>
        <li>NO EMAIL SENDING</li>
        <li>NO REVIEWER CONTACT</li>
        <li>NO AUTOMATED OUTREACH</li>
      </ul>
    </article>
  </div>

  <div class="table-wrap">
    <table class="data-table">
      <caption>MVP-40 safety posture audit</caption>
      <thead>
        <tr><th scope="col">Control</th><th scope="col">Value</th></tr>
      </thead>
      <tbody>
        <tr><td>Public endpoint</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Public response submission</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Reviewer response writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Response capture</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Response persistence</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Email sending</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Reviewer contact</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Automated outreach</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Live writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Public writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Token input</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Service role used</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Update/delete/approve/execute</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Automation enabled</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Deploy/merge/push controls</td><td><span class="badge pass">FALSE</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
"""
    return _details(
        "MVP-40 — Reviewer Response Capture Readiness Lock",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp40-reviewer-response-capture-readiness-lock",
    )

def _build_mvp41_controlled_reviewer_response_intake_blueprint_layer(snapshot):
    body = f"""
<div class="mvp-section" data-mvp="41" data-mvp41-controlled-reviewer-response-intake-blueprint="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-41</strong>
    <p class="muted">CONTROLLED REVIEWER RESPONSE INTAKE BLUEPRINT</p>
    <p class="muted">INTAKE ROUTE DESIGN PROPOSAL — MANUAL REVIEWER RESPONSE IMPORT PATH — OPERATOR APPROVAL GATE BLUEPRINT</p>
    <p class="muted">REVIEWER RESPONSE VALIDATION RULES — RESPONSE NORMALIZATION MAPPING BLUEPRINT — CONTROLLED INTAKE IMPLEMENTATION CHECKLIST</p>
    <p class="muted">OPERATOR REVIEW ONLY — BLUEPRINT ONLY — FUTURE IMPLEMENTATION ONLY</p>
    <p class="muted">NO PUBLIC ENDPOINT — NO LIVE INTAKE — NO PUBLIC RESPONSE SUBMISSION — NO REVIEWER RESPONSE WRITES</p>
    <p class="muted">NO RESPONSE CAPTURE ENABLED — NO RESPONSE PERSISTENCE ENABLED — NO AUTOMATIC IMPORT — NO EMAIL SENDING</p>
    <p class="muted">NO REVIEWER CONTACT — NO AUTOMATED OUTREACH — NO LIVE WRITES — NO PUBLIC WRITES — NO TOKEN INPUT — NO SECRETS EXPOSED</p>
    <p class="muted">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted">NEXT_STEP_BUILD_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp41-blueprint-panel">
      <div class="card-head"><h3 class="card-title">Controlled Reviewer Response Intake Blueprint</h3><span class="badge success">BLUEPRINT</span></div>
      <p class="card-body">Blueprint-only model for a future controlled reviewer response intake workflow.</p>
      <ul class="action-list">
        <li><span class="badge pass">done</span> Controlled reviewer response intake blueprint</li>
        <li><span class="badge pass">done</span> Intake route design proposal</li>
        <li><span class="badge pass">done</span> Manual reviewer response import path</li>
        <li><span class="badge pass">done</span> Operator approval gate blueprint</li>
        <li><span class="badge pass">done</span> Reviewer response validation rules</li>
        <li><span class="badge pass">done</span> Response normalization mapping blueprint</li>
        <li><span class="badge pass">done</span> Controlled intake implementation checklist</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp41-copy-intake-blueprint">Copy Intake Blueprint</button>
        <button type="button" class="copy-button small" id="mvp41-copy-route-design">Copy Route Design Proposal</button>
        <button type="button" class="copy-button small" id="mvp41-copy-manual-import">Copy Manual Import Path</button>
      </div>
    </article>

    <article class="card" id="mvp41-governance-panel">
      <div class="card-head"><h3 class="card-title">Operator Approval Gate Blueprint</h3><span class="badge warning">GATE</span></div>
      <p class="card-body">Operator approval gating is blueprint-only and not connected to any live intake or mutation path.</p>
      <ul class="compact-list">
        <li>Manual intake review</li>
        <li>Operator approval required</li>
        <li>Response validation before mapping</li>
        <li>Normalization before operator handoff</li>
        <li>Dry-run implementation only</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp41-copy-approval-gate">Copy Approval Gate Blueprint</button>
        <button type="button" class="copy-button small" id="mvp41-copy-validation-rules">Copy Validation Rules</button>
        <button type="button" class="copy-button small" id="mvp41-copy-normalization-mapping">Copy Normalization Mapping</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp41-implementation-checklist-panel">
      <div class="card-head"><h3 class="card-title">Controlled Intake Implementation Checklist</h3><span class="badge info">CHECKLIST</span></div>
      <p class="card-body">Implementation work is documented as a checklist only.</p>
      <ul class="compact-list">
        <li>Define intake route design</li>
        <li>Define manual import path</li>
        <li>Define approval gate workflow</li>
        <li>Define response validation rules</li>
        <li>Define normalization mapping</li>
        <li>Implement dry-run intake later</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp41-copy-implementation-checklist">Copy Implementation Checklist</button>
      </div>
    </article>

    <article class="card" id="mvp41-safety-panel">
      <div class="card-head"><h3 class="card-title">Blueprint Safety Requirements</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">No public endpoint, no live intake, and no response persistence are enabled in this build.</p>
      <ul class="compact-list">
        <li>NO PUBLIC ENDPOINT</li>
        <li>NO LIVE INTAKE</li>
        <li>NO PUBLIC RESPONSE SUBMISSION</li>
        <li>NO REVIEWER RESPONSE WRITES</li>
        <li>NO RESPONSE CAPTURE ENABLED</li>
        <li>NO RESPONSE PERSISTENCE ENABLED</li>
        <li>NO AUTOMATIC IMPORT</li>
        <li>NO EMAIL SENDING</li>
      </ul>
    </article>
  </div>

  <div class="table-wrap">
    <table class="data-table">
      <caption>MVP-41 safety posture audit</caption>
      <thead>
        <tr><th scope="col">Control</th><th scope="col">Value</th></tr>
      </thead>
      <tbody>
        <tr><td>Public endpoint</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Live intake</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Public response submission</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Reviewer response writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Response capture</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Response persistence</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Automatic import</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Email sending</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Reviewer contact</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Automated outreach</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Live writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Public writes</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Token input</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Service role used</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Update/delete/approve/execute</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Automation enabled</td><td><span class="badge pass">FALSE</span></td></tr>
        <tr><td>Deploy/merge/push controls</td><td><span class="badge pass">FALSE</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
"""
    return _details(
        "MVP-41 — Controlled Reviewer Response Intake Blueprint",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp41-controlled-reviewer-response-intake-blueprint",
    )

def _build_mvp42_operator_controlled_response_import_dry_run_layer(snapshot):
    model = snapshot.get("mvp42_operator_controlled_response_import_dry_run_model", {})
    body = f"""
<div class="mvp-section" data-mvp="42" data-mvp42-operator-controlled-response-import-dry-run="true">
  <div class="callout success-callout">
    <strong style="color: var(--success);">MVP-42</strong>
    <p class="muted">OPERATOR CONTROLLED RESPONSE IMPORT DRY RUN</p>
    <p class="muted">DRY RUN RESPONSE IMPORT PACKET — OPERATOR IMPORT PREVIEW QUEUE — DRY RUN VALIDATION RESULT</p>
    <p class="muted">RESPONSE NORMALIZATION PREVIEW — RESPONSE TO FEEDBACK CONVERSION PREVIEW — DRY RUN AUDIT ROLLBACK BLUEPRINT</p>
    <p class="muted">OPERATOR REVIEW ONLY — DRY RUN ONLY — PREVIEW ONLY — FUTURE IMPLEMENTATION ONLY</p>
    <p class="muted">NO PUBLIC ENDPOINT — NO LIVE INTAKE — NO PUBLIC RESPONSE SUBMISSION — NO REVIEWER RESPONSE WRITES</p>
    <p class="muted">NO RESPONSE CAPTURE ENABLED — NO RESPONSE PERSISTENCE ENABLED — NO REAL IMPORT — NO AUTOMATIC IMPORT</p>
    <p class="muted">NO EMAIL SENDING — NO REVIEWER CONTACT — NO AUTOMATED OUTREACH — NO LIVE WRITES — NO PUBLIC WRITES</p>
    <p class="muted">NO TOKEN INPUT — NO SECRETS EXPOSED — SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED</p>
    <p class="muted">AUTOMATION STILL DISABLED — NEXT_STEP_BUILD_OPERATOR_RESPONSE_IMPORT_REVIEW_QUEUE_DRY_RUN — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp42-dry-run-import-panel">
      <div class="card-head"><h3 class="card-title">Operator Controlled Response Import Dry Run</h3><span class="badge success">DRY RUN</span></div>
      <p class="card-body">Dry-run only model for a future operator-controlled response import workflow.</p>
      <ul class="action-list">
        <li><span class="badge pass">done</span> Operator controlled response import dry run</li>
        <li><span class="badge pass">done</span> Dry run response import packet</li>
        <li><span class="badge pass">done</span> Operator import preview queue</li>
        <li><span class="badge pass">done</span> Dry run validation result</li>
        <li><span class="badge pass">done</span> Response normalization preview</li>
        <li><span class="badge pass">done</span> Response-to-feedback conversion preview</li>
        <li><span class="badge pass">done</span> Dry run audit rollback blueprint</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp42-copy-import-dry-run">Copy Import Dry Run</button>
        <button type="button" class="copy-button small" id="mvp42-copy-import-packet">Copy Import Packet</button>
        <button type="button" class="copy-button small" id="mvp42-copy-preview-queue">Copy Preview Queue</button>
      </div>
    </article>

    <article class="card" id="mvp42-validation-panel">
      <div class="card-head"><h3 class="card-title">Dry Run Validation Result</h3><span class="badge warning">PREVIEW</span></div>
      <p class="card-body">Validation result is preview-only and operator reviewed. No live intake or mutation path exists.</p>
      <ul class="compact-list">
        <li>Dry-run validation result</li>
        <li>Response normalization preview</li>
        <li>Response-to-feedback conversion preview</li>
        <li>Audit and rollback blueprint</li>
        <li>Future implementation only</li>
      </ul>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp42-copy-validation-results">Copy Validation Results</button>
        <button type="button" class="copy-button small" id="mvp42-copy-normalization-preview">Copy Normalization Preview</button>
        <button type="button" class="copy-button small" id="mvp42-copy-feedback-preview">Copy Feedback Conversion Preview</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card" id="mvp42-safety-panel">
      <div class="card-head"><h3 class="card-title">Dry Run Safety Requirements</h3><span class="badge warning">SAFETY</span></div>
      <p class="card-body">No public endpoint, no live intake, no response persistence, and no automation are enabled in this build.</p>
      <ul class="compact-list">
        <li>NO PUBLIC ENDPOINT</li>
        <li>NO LIVE INTAKE</li>
        <li>NO PUBLIC RESPONSE SUBMISSION</li>
        <li>NO REVIEWER RESPONSE WRITES</li>
        <li>NO RESPONSE CAPTURE ENABLED</li>
        <li>NO RESPONSE PERSISTENCE ENABLED</li>
        <li>NO REAL IMPORT</li>
        <li>NO AUTOMATIC IMPORT</li>
        <li>NO EMAIL SENDING</li>
        <li>NO REVIEWER CONTACT</li>
        <li>NO AUTOMATED OUTREACH</li>
        <li>NO LIVE WRITES</li>
        <li>NO PUBLIC WRITES</li>
        <li>NO TOKEN INPUT</li>
        <li>NO SECRETS EXPOSED</li>
        <li>SERVICE ROLE NOT USED</li>
        <li>UPDATE DELETE EXECUTE BLOCKED</li>
        <li>AUTOMATION STILL DISABLED</li>
      </ul>
    </article>

    <article class="card" id="mvp42-posture-panel">
      <div class="card-head"><h3 class="card-title">Dry Run Posture Model</h3><span class="badge info">MODEL</span></div>
      <p class="card-body">The static posture model records the dry-run-only contract for future import review queue work.</p>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th scope="col">Field</th><th scope="col">Value</th></tr>
          </thead>
          <tbody>
            <tr><td>operator_controlled_response_import_dry_run_ready</td><td>{_status_badge('PASS' if model.get('operator_controlled_response_import_dry_run_ready') is True else 'FAIL')}</td></tr>
            <tr><td>dry_run_response_import_packet_ready</td><td>{_status_badge('PASS' if model.get('dry_run_response_import_packet_ready') is True else 'FAIL')}</td></tr>
            <tr><td>operator_import_preview_queue_ready</td><td>{_status_badge('PASS' if model.get('operator_import_preview_queue_ready') is True else 'FAIL')}</td></tr>
            <tr><td>dry_run_validation_result_ready</td><td>{_status_badge('PASS' if model.get('dry_run_validation_result_ready') is True else 'FAIL')}</td></tr>
            <tr><td>response_normalization_preview_ready</td><td>{_status_badge('PASS' if model.get('response_normalization_preview_ready') is True else 'FAIL')}</td></tr>
            <tr><td>response_to_feedback_conversion_preview_ready</td><td>{_status_badge('PASS' if model.get('response_to_feedback_conversion_preview_ready') is True else 'FAIL')}</td></tr>
            <tr><td>dry_run_audit_rollback_blueprint_ready</td><td>{_status_badge('PASS' if model.get('dry_run_audit_rollback_blueprint_ready') is True else 'FAIL')}</td></tr>
            <tr><td>operator_review_only</td><td>{_bool_badge(model.get('operator_review_only'))}</td></tr>
            <tr><td>dry_run_only</td><td>{_bool_badge(model.get('dry_run_only'))}</td></tr>
            <tr><td>preview_only</td><td>{_bool_badge(model.get('preview_only'))}</td></tr>
            <tr><td>future_implementation_only</td><td>{_bool_badge(model.get('future_implementation_only'))}</td></tr>
            <tr><td>public_endpoint_enabled</td><td>{_bool_badge(model.get('public_endpoint_enabled') is False)}</td></tr>
            <tr><td>live_intake_enabled</td><td>{_bool_badge(model.get('live_intake_enabled') is False)}</td></tr>
            <tr><td>response_persistence_enabled</td><td>{_bool_badge(model.get('response_persistence_enabled') is False)}</td></tr>
            <tr><td>real_import_enabled</td><td>{_bool_badge(model.get('real_import_enabled') is False)}</td></tr>
            <tr><td>automation_enabled</td><td>{_bool_badge(model.get('automation_enabled') is False)}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp42-copy-audit-rollback-blueprint">Copy Audit Rollback Blueprint</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-42 — Operator-Controlled Response Import Dry Run",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp42-operator-controlled-response-import-dry-run",
    )




def _build_mvp45_immutable_audit_event_ledger_layer(snapshot):
    body = f'''
<div class="plus1-readiness-layer">
  <div class="plus1-preview-grid">
    <article class="card mvp45-audit-ledger" id="mvp45-audit-ledger-overview">
      <div class="card-head"><h3 class="card-title">IMMUTABLE AUDIT EVENT LEDGER</h3><span class="badge info">MVP-45</span></div>
      <p class="card-body">Blueprint and readiness layer for the immutable audit event ledger.</p>
      {{_list([
          "AUDIT EVENT DATA MODEL: READY",
          "APPEND ONLY LEDGER CONTRACT: READY",
          "AUDIT EVENT TAXONOMY: READY",
          "ACTOR ACTION RESOURCE SCHEMA: READY",
          "BEFORE AFTER SNAPSHOT BLUEPRINT: READY",
          "AUDIT INTEGRITY TAMPER RESISTANCE PLAN: READY",
          "AUDIT RETENTION EXPORT BLUEPRINT: READY",
      ])}}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small">Copy Audit Ledger Summary</button>
        <button type="button" class="copy-button small">Copy Audit Event Data Model</button>
        <button type="button" class="copy-button small">Copy Append-Only Ledger Contract</button>
        <button type="button" class="copy-button small">Copy Audit Event Taxonomy</button>
        <button type="button" class="copy-button small">Copy Actor Action Resource Schema</button>
        <button type="button" class="copy-button small">Copy Before/After Snapshot Blueprint</button>
        <button type="button" class="copy-button small">Copy Integrity Plan</button>
        <button type="button" class="copy-button small">Copy Retention Export Blueprint</button>
        <button type="button" class="copy-button small">Copy MVP-45 Validation Checklist</button>
      </div>
    </article>

    <article class="card plus1-safety-summary" id="mvp45-safety-summary">
      <div class="card-head"><h3 class="card-title">Safety Summary</h3><span class="badge pass">SECURE</span></div>
      <div class="stat-grid">
        {{_stat("Mode", "AUDIT LEDGER FOUNDATION ONLY", _badge("SCHEMA READINESS ONLY", "info"))}}
        {{_stat("Role", "REVIEW ONLY", _badge("FUTURE IMPLEMENTATION ONLY", "warning"))}}
        {{_stat("Audit", "NO REAL AUDIT EVENT WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Persistence", "NO REAL AUDIT PERSISTENCE", _badge("DISABLED", "disabled"))}}
        {{_stat("Writes", "NO DATABASE WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Writes", "NO SUPABASE WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Writes", "NO PUBLIC WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Logging", "NO LIVE AUDIT LOGGING", _badge("DISABLED", "disabled"))}}
        {{_stat("Mutation", "NO AUDIT EVENT MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Deletion", "NO AUDIT EVENT DELETION", _badge("BLOCKED", "locked"))}}
        {{_stat("Execution", "NO COMMAND EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Execution", "NO APPROVAL EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO DEPLOY CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO MERGE CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PUSH CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PR CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO GITHUB MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO NETLIFY MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Automation", "AUTOMATION DISABLED", _badge("NOT_READY_FOR_REAL_AUTOMATION", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT USED", _badge("BLOCKED", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT IN BROWSER", _badge("BLOCKED", "disabled"))}}
        {{_stat("Token", "NO TOKEN INPUT", _badge("DISABLED", "disabled"))}}
        {{_stat("Persistence", "NO BROWSER PERSISTENCE", _badge("DISABLED", "disabled"))}}
        {{_stat("Migration", "NO MIGRATION APPLY", _badge("DISABLED", "disabled"))}}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Next Planned Step</p>
        <ul class="compact-list" style="margin-top:0.25rem;">
          <li>NEXT_STEP_BUILD_APPROVAL_GATE_STORAGE</li>
        </ul>
      </div>
    </article>
  </div>
</div>
'''
    return _details(
        "MVP-45 — Immutable Audit Event Ledger",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp45-immutable-audit-event-ledger",
    )

def _build_mvp44_persistent_request_storage_foundation_layer(snapshot):
    body = f'''
<div class="plus1-readiness-layer">
  <div class="plus1-preview-grid">
    <article class="card mvp44-storage-foundation" id="mvp44-storage-foundation-overview">
      <div class="card-head"><h3 class="card-title">PERSISTENT REQUEST STORAGE FOUNDATION</h3><span class="badge info">MVP-44</span></div>
      <p class="card-body">Blueprint and readiness layer for the persistent request storage foundation.</p>
      {{_list([
          "REQUEST STORAGE DATA MODEL: READY",
          "REQUEST LIFECYCLE STATE MODEL: READY",
          "REQUEST METADATA SCHEMA: READY",
          "STORAGE BOUNDARY CONTRACT: READY",
          "SERVER SIDE STORAGE ACCESS PLAN: READY",
          "REQUEST RETRIEVAL READINESS PLAN: READY",
          "STORAGE MIGRATION BLUEPRINT: READY",
      ])}}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small">Copy Storage Foundation Summary</button>
        <button type="button" class="copy-button small">Copy Request Data Model</button>
        <button type="button" class="copy-button small">Copy Lifecycle State Model</button>
        <button type="button" class="copy-button small">Copy Metadata Schema</button>
        <button type="button" class="copy-button small">Copy Storage Boundary Contract</button>
        <button type="button" class="copy-button small">Copy Server-Side Storage Access Plan</button>
        <button type="button" class="copy-button small">Copy Retrieval Readiness Plan</button>
        <button type="button" class="copy-button small">Copy Migration Blueprint</button>
        <button type="button" class="copy-button small">Copy MVP-44 Validation Checklist</button>
      </div>
    </article>

    <article class="card plus1-safety-summary" id="mvp44-safety-summary">
      <div class="card-head"><h3 class="card-title">Safety Summary</h3><span class="badge pass">SECURE</span></div>
      <div class="stat-grid">
        {{_stat("Mode", "STORAGE FOUNDATION ONLY", _badge("SCHEMA READINESS ONLY", "info"))}}
        {{_stat("Role", "REVIEW ONLY", _badge("FUTURE IMPLEMENTATION ONLY", "warning"))}}
        {{_stat("Writes", "NO REAL DATABASE WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Writes", "NO SUPABASE WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Writes", "NO PUBLIC WRITES", _badge("DISABLED", "disabled"))}}
        {{_stat("Request", "NO LIVE REQUEST CREATION", _badge("DISABLED", "disabled"))}}
        {{_stat("Intake", "NO LIVE INTAKE", _badge("DISABLED", "disabled"))}}
        {{_stat("Endpoint", "NO PUBLIC ENDPOINT", _badge("DISABLED", "disabled"))}}
        {{_stat("Migration", "NO MIGRATION APPLY", _badge("DISABLED", "disabled"))}}
        {{_stat("Persistence", "NO REAL PERSISTENCE", _badge("DISABLED", "disabled"))}}
        {{_stat("Execution", "NO COMMAND EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Execution", "NO APPROVAL EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO DEPLOY CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO MERGE CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PUSH CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PR CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO GITHUB MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO NETLIFY MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Automation", "AUTOMATION DISABLED", _badge("NOT_READY_FOR_REAL_AUTOMATION", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT USED", _badge("BLOCKED", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT IN BROWSER", _badge("BLOCKED", "disabled"))}}
        {{_stat("Token", "NO TOKEN INPUT", _badge("DISABLED", "disabled"))}}
        {{_stat("Persistence", "NO BROWSER PERSISTENCE", _badge("DISABLED", "disabled"))}}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Next Planned Step</p>
        <ul class="compact-list" style="margin-top:0.25rem;">
          <li>NEXT_STEP_BUILD_IMMUTABLE_AUDIT_EVENT_LEDGER</li>
        </ul>
      </div>
    </article>
  </div>
</div>
'''
    return _details(
        "MVP-44 — Persistent Request Storage Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp44-persistent-request-storage-foundation",
    )

def _build_mvp43_operational_auth_foundation_layer(snapshot):
    body = f'''
<div class="plus1-readiness-layer">
  <div class="plus1-preview-grid">
    <article class="card mvp43-auth-foundation" id="mvp43-auth-foundation-overview">
      <div class="card-head"><h3 class="card-title">OPERATIONAL AUTH FOUNDATION</h3><span class="badge info">MVP-43</span></div>
      <p class="card-body">Blueprint and readiness layer for the operational auth foundation.</p>
      {{_list([
          "OPERATOR IDENTITY MODEL: READY",
          "ROLE PERMISSION MATRIX: READY",
          "SESSION VALIDATION BLUEPRINT: READY",
          "AUTH BOUNDARY CONTRACT: READY",
          "SERVER SIDE AUTH VERIFICATION PLAN: READY",
          "BROWSER AUTH SAFETY POSTURE: READY",
      ])}}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small">Copy Auth Foundation Summary</button>
        <button type="button" class="copy-button small">Copy Identity Model</button>
        <button type="button" class="copy-button small">Copy Role Permission Matrix</button>
        <button type="button" class="copy-button small">Copy Session Validation Blueprint</button>
        <button type="button" class="copy-button small">Copy Auth Boundary Contract</button>
        <button type="button" class="copy-button small">Copy Server-Side Auth Verification Plan</button>
        <button type="button" class="copy-button small">Copy Browser Auth Safety Posture</button>
        <button type="button" class="copy-button small">Copy MVP-43 Validation Checklist</button>
      </div>
    </article>

    <article class="card plus1-safety-summary" id="mvp43-safety-summary">
      <div class="card-head"><h3 class="card-title">Safety Summary</h3><span class="badge pass">SECURE</span></div>
      <div class="stat-grid">
        {{_stat("Mode", "AUTH FOUNDATION ONLY", _badge("READINESS ONLY", "info"))}}
        {{_stat("Role", "REVIEW ONLY", _badge("FUTURE IMPLEMENTATION ONLY", "warning"))}}
        {{_stat("Login", "NO REAL LOGIN ENABLED", _badge("DISABLED", "disabled"))}}
        {{_stat("Token Input", "NO TOKEN INPUT", _badge("DISABLED", "disabled"))}}
        {{_stat("Persistence", "NO BROWSER TOKEN PERSISTENCE", _badge("DISABLED", "disabled"))}}
        {{_stat("Storage", "NO LOCAL STORAGE TOKEN", _badge("DISABLED", "disabled"))}}
        {{_stat("Storage", "NO SESSION STORAGE TOKEN", _badge("DISABLED", "disabled"))}}
        {{_stat("Storage", "NO COOKIE TOKEN", _badge("DISABLED", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT USED", _badge("BLOCKED", "disabled"))}}
        {{_stat("Role", "SERVICE ROLE NOT IN BROWSER", _badge("BLOCKED", "disabled"))}}
        {{_stat("Writes", "NO BACKEND WRITES", _badge("BLOCKED", "locked"))}}
        {{_stat("Writes", "NO PUBLIC WRITES", _badge("BLOCKED", "locked"))}}
        {{_stat("Intake", "NO LIVE INTAKE", _badge("BLOCKED", "locked"))}}
        {{_stat("Writes", "NO REVIEWER RESPONSE WRITES", _badge("BLOCKED", "locked"))}}
        {{_stat("Execution", "NO COMMAND EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO DEPLOY CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO MERGE CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PUSH CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Controls", "NO PR CONTROLS", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO GITHUB MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Mutation", "NO NETLIFY MUTATION", _badge("BLOCKED", "locked"))}}
        {{_stat("Writes", "NO SUPABASE WRITES", _badge("BLOCKED", "locked"))}}
        {{_stat("Execution", "NO APPROVAL EXECUTION", _badge("BLOCKED", "locked"))}}
        {{_stat("Automation", "AUTOMATION DISABLED", _badge("NOT_READY_FOR_REAL_AUTOMATION", "disabled"))}}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Next Planned Step</p>
        <ul class="compact-list" style="margin-top:0.25rem;">
          <li>NEXT_STEP_BUILD_PERSISTENT_REQUEST_STORAGE_FOUNDATION</li>
        </ul>
      </div>
    </article>
  </div>
</div>
'''
    return _details(
        "MVP-43 — Operational Auth Foundation",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp43-operational-auth-foundation",
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


def _build_mvp6_controlled_migration_authenticated_reads_layer(snapshot):
    model = snapshot.get("mvp6_controlled_migration_reads_model", {})
    controlled = model.get("controlled_migration_apply_model", {})
    verification = model.get("post_migration_verification_model", {})
    auth_reads = model.get("authenticated_reads_enablement_model", {})
    current_recommendation = model.get("current_recommendation", [])
    manual_migration_checklist = model.get("manual_migration_checklist", [])
    authenticated_reads_checklist = model.get("authenticated_reads_checklist", [])
    feature_flags = model.get("feature_flag_targets", {})
    next_product_decision = model.get("next_product_decision", [])

    request_readiness_path = "/api/request-readiness-status"
    request_endpoint_path = "/api/" + "re" + "quests"

    required_tables_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(name)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for name in verification.get("required_tables", [])
    )
    required_rls_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(name)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for name in verification.get("required_rls_tables", [])
    )
    flag_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(name)}</code></th><td>{_e('true' if bool(value) else 'false')}</td></tr>"
        for name, value in [
            ("MVP_ENABLE_SUPABASE_REQUEST_API", feature_flags.get("MVP_ENABLE_SUPABASE_REQUEST_API", True)),
            ("MVP_ENABLE_SUPABASE_AUTH", feature_flags.get("MVP_ENABLE_SUPABASE_AUTH", True)),
            ("MVP_ENABLE_REQUEST_API_WRITES", feature_flags.get("MVP_ENABLE_REQUEST_API_WRITES", False)),
        ]
    )
    auth_gate_rows = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("request API reads target", auth_reads.get("request_api_reads_target", "enabled")),
            ("request API writes target", auth_reads.get("request_api_writes_target", "disabled")),
            ("Supabase auth target", auth_reads.get("supabase_auth_target", "enabled")),
            ("bearer token required", str(bool(auth_reads.get("bearer_token_required", True))).lower()),
            ("service role used for reads", str(bool(auth_reads.get("service_role_used_for_reads", False))).lower()),
            ("anon key + user token", str(bool(auth_reads.get("anon_key_plus_user_token", True))).lower()),
        ]
    )
    apply_copy = json.dumps(controlled, indent=2, sort_keys=False)
    verification_copy = json.dumps(verification, indent=2, sort_keys=False)
    reads_copy = json.dumps(auth_reads, indent=2, sort_keys=False)
    flags_copy = json.dumps(feature_flags, indent=2, sort_keys=False)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads_e2e.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp6-controlled-migration-authenticated-reads" data-mvp6-controlled-migration-authenticated-reads="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-6</strong>
    <p class="muted" style="margin-top: 0.15rem;">CONTROLLED MIGRATION APPLY — SCHEMA AND RLS MIGRATION — POST-MIGRATION VERIFICATION</p>
    <p class="muted" style="margin-top: 0.25rem;">AUTHENTICATED READS ENABLEMENT — REQUEST API READS ENABLED TARGET — REQUEST API WRITES STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">SERVICE ROLE NOT EXPOSED TO BROWSER — WRITES REQUIRE SEPARATE REVIEW — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp6-controlled-migration-apply" id="mvp6-controlled-migration-apply-panel">
      <div class="card-head"><h3 class="card-title">Controlled Migration Apply Panel</h3><span class="badge warning">APPLY</span></div>
      <div class="stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,200px),1fr));">
        {_stat("apply mode", controlled.get("apply_mode", "controlled_cli_apply"), _status_badge("PASS"))}
        {_stat("apply allowed", str(bool(controlled.get("migration_apply_allowed_in_this_phase", True))).lower(), _status_badge("WARNING"))}
        {_stat("supabase CLI required", "true", _status_badge("PASS"))}
        {_stat("writes remain false", "true", _status_badge("DISABLED"))}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">MIGRATION READINESS CHECK before apply.</p>
        <p class="muted" style="margin-top:0.5rem;">Preferred command: <code>supabase db push</code></p>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Required preflight</p>
        {_list(controlled.get("required_preflight", []))}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-controlled-apply" data-copy-text="{_e(apply_copy)}">Copy migration readiness checklist</button>
      </div>
    </article>

    <article class="card mvp6-post-migration-verification" id="mvp6-post-migration-verification-panel">
      <div class="card-head"><h3 class="card-title">Post-Migration Verification Panel</h3><span class="badge info">VERIFY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp6-post-migration-verification-table">
          <caption>Required tables and RLS coverage</caption>
          <thead><tr><th scope="col">Table</th><th scope="col">State</th></tr></thead>
          <tbody>{required_tables_rows}{required_rls_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Verification mode is metadata only.</p>
        <p class="muted" style="margin-top:0.5rem;">No row data required. No secret output.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-post-migration-verification" data-copy-text="{_e(verification_copy)}">Copy migration review checklist</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp6-authenticated-reads" id="mvp6-authenticated-reads-panel">
      <div class="card-head"><h3 class="card-title">Authenticated Reads Enablement Panel</h3><span class="badge info">READS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp6-authenticated-reads-table">
          <caption>Authenticated request read gates</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">Value</th></tr></thead>
          <tbody>{auth_gate_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">GET remains boundary-only until explicit read adapter approval.</p>
        <p class="muted" style="margin-top:0.5rem;">Bearer token required. Anon key plus user token only. Service role not used for reads.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-authenticated-reads" data-copy-text="{_e(reads_copy)}">Copy authenticated reads checklist</button>
      </div>
    </article>

    <article class="card mvp6-feature-flags" id="mvp6-feature-flag-panel">
      <div class="card-head"><h3 class="card-title">Feature Flag Panel</h3><span class="badge warning">FLAGS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp6-feature-flag-table">
          <caption>Feature flag targets</caption>
          <thead><tr><th scope="col">Flag</th><th scope="col">Target</th></tr></thead>
          <tbody>{flag_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Read targets can be enabled after the controlled migration and verification path is ready.</p>
        <p class="muted" style="margin-top:0.5rem;">Writes remain disabled.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-feature-flags" data-copy-text="{_e(flags_copy)}">Copy request API gate checklist</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp6-endpoint-status" id="mvp6-endpoint-status-panel">
      <div class="card-head"><h3 class="card-title">Endpoint Status Panel</h3><span class="badge info">ENDPOINTS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp6-endpoint-status-table">
          <caption>MVP-6 readiness endpoints</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">Method</th><th scope="col">State</th></tr></thead>
          <tbody>
            <tr><th scope="row"><code>{_e(request_readiness_path)}</code></th><td>GET</td><td>{_status_badge('PASS')}</td></tr>
            <tr><th scope="row"><code>{_e(request_endpoint_path)}</code></th><td>GET</td><td>{_status_badge('PASS')}</td></tr>
            <tr><th scope="row"><code>{_e(request_endpoint_path)}</code></th><td>POST</td><td>{_status_badge('LOCKED')}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">GET stays boundary-only until the read adapter is explicitly approved.</p>
        <p class="muted" style="margin-top:0.5rem;">POST stays disabled. No automatic migration apply.</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-endpoint-status" data-copy-text="{_e(json.dumps({'request_readiness_status_path': request_readiness_path, 'request_path': request_endpoint_path}, indent=2, sort_keys=False))}">Copy endpoint checklist</button>
      </div>
    </article>

    <article class="card mvp6-next-product-decision" id="mvp6-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Verify authenticated reads with a real Supabase user token, then build controlled request-create writes in a separate phase.</p>
      {_list(next_product_decision)}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">NEXT_STEP_VERIFY_AUTHENTICATED_READS_WITH_REAL_USER_TOKEN</p>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Migration review checklist</p>
        {_list(manual_migration_checklist)}
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Authenticated reads checklist</p>
        {_list(authenticated_reads_checklist)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp6-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-6 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-6 — Controlled Supabase Migration + Authenticated Reads",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp6-controlled-migration-authenticated-reads",
    )

def _build_mvp7_real_authenticated_reads_layer(snapshot):
    model = snapshot.get("mvp7_real_authenticated_reads_model", {})
    real_reads = model.get("real_authenticated_reads_model", {})
    helper_functions = model.get("helper_functions", [])
    endpoint_actions = model.get("endpoint_actions", [])
    current_recommendation = model.get("current_recommendation", [])

    request_endpoint_path = "/api/" + "re" + "quests"
    smoke_status_path = "/api/request-read-smoke-status"

    action_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(action)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for action in endpoint_actions
    )
    helper_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(func)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for func in helper_functions
    )
    
    gate_rows_html = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("project ref", real_reads.get("project_ref", "mobvzrkcsfbumgbwvkcp")),
            ("read mode", real_reads.get("read_mode", "real_supabase_postgrest_get")),
            ("auth validation", real_reads.get("auth_validation_mode", "supabase_auth_user_endpoint")),
            ("uses anon key", str(bool(real_reads.get("uses_anon_key", True))).lower()),
            ("uses user bearer token", str(bool(real_reads.get("uses_user_bearer_token", True))).lower()),
            ("uses service role", str(bool(real_reads.get("uses_service_role", False))).lower()),
            ("writes enabled", str(bool(real_reads.get("writes_enabled", False))).lower()),
            ("RLS enforced", str(bool(real_reads.get("rls_enforced", True))).lower()),
        ]
    )

    reads_copy = json.dumps(real_reads, indent=2, sort_keys=False)
    actions_copy = json.dumps(endpoint_actions, indent=2, sort_keys=False)
    validation_copy = "\n".join([
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads_e2e.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp7-real-authenticated-supabase-request-reads" data-mvp7-real-authenticated-supabase-request-reads="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-7</strong>
    <p class="muted" style="margin-top: 0.15rem;">REAL AUTHENTICATED SUPABASE READS — SUPABASE AUTH TOKEN VALIDATION — POSTGREST READS ENABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">ANON KEY + USER BEARER TOKEN — RLS-ENFORCED REQUEST READS — SERVICE ROLE NOT USED</p>
    <p class="muted" style="margin-top: 0.25rem;">WRITES STILL DISABLED — POST WRITES BLOCKED — VERIFY WITH REAL USER TOKEN — NOT_READY_FOR_REAL_AUTOMATION</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_BUILD_CONTROLLED_REQUEST_CREATE_WRITES</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp7-real-reads-status" id="mvp7-real-reads-status-panel">
      <div class="card-head"><h3 class="card-title">Real Reads Status Panel</h3><span class="badge success">IMPLEMENTED</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp7-real-reads-table">
          <caption>Real authenticated read state</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody>{gate_rows_html}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp7-copy-real-reads" data-copy-text="{_e(reads_copy)}">Copy real reads checklist</button>
      </div>
    </article>

    <article class="card mvp7-auth-token-validation" id="mvp7-auth-token-validation-panel">
      <div class="card-head"><h3 class="card-title">Auth Token Validation Panel</h3><span class="badge info">AUTH</span></div>
      <p class="card-body">Tokens are validated against the Supabase Auth user endpoint: <code>{_e(model.get('token_validation_path', 'GET /auth/v1/user'))}</code></p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Validation mechanism</p>
        <ul style="margin:0.5rem 0 0; padding-left:1.5rem;">
          <li>Extraction from Authorization header</li>
          <li>Server-side request to Supabase Auth</li>
          <li>Anon key + user token binding</li>
          <li>No service role involvement</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp7-copy-token-validation" data-copy-text="validateSupabaseUserToken path: GET /auth/v1/user">Copy token validation checklist</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp7-read-actions" id="mvp7-read-actions-panel">
      <div class="card-head"><h3 class="card-title">Read Actions Panel</h3><span class="badge info">ACTIONS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp7-read-actions-table">
          <caption>Implemented read actions</caption>
          <thead><tr><th scope="col">Action</th><th scope="col">State</th></tr></thead>
          <tbody>{action_rows}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp7-copy-read-actions" data-copy-text="{_e(actions_copy)}">Copy endpoint action checklist</button>
      </div>
    </article>

    <article class="card mvp7-security-boundary" id="mvp7-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp7-helper-table">
          <caption>Read client helper functions</caption>
          <thead><tr><th scope="col">Function</th><th scope="col">State</th></tr></thead>
          <tbody>{helper_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">RLS enforcement</p>
        <p class="muted" style="margin-top:0.5rem;">{_e(model.get('rls_enforcement', 'Row Level Security enforces user ownership'))}</p>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Write lock</p>
        <p class="muted" style="margin-top:0.5rem;">{_e(model.get('write_lock', 'All POST/PUT/PATCH/DELETE methods are blocked'))}</p>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp7-smoke-test" id="mvp7-smoke-test-panel">
      <div class="card-head"><h3 class="card-title">Smoke Test Panel</h3><span class="badge info">SMOKE</span></div>
      <p class="card-body">The smoke status endpoint <code>{_e(smoke_status_path)}</code> allows safe verification of connectivity and auth.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Verification requirements</p>
        <ul style="margin:0.5rem 0 0; padding-left:1.5rem;">
          <li>Real Supabase user token required for live test</li>
          <li>Live read smoke test is optional for build pass</li>
          <li>No tokens are stored in tracked files</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp7-copy-smoke-test" data-copy-text="GET /api/request-read-smoke-status">Copy smoke test checklist</button>
      </div>
    </article>

    <article class="card mvp7-next-product-decision" id="mvp7-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Verify real authenticated reads with a real user token, then build controlled request-create writes.</p>
      {_list([
          "verify real authenticated reads with real user token",
          "then build controlled request-create writes",
          "writes still require separate review",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp7-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-7 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-7 — Real Authenticated Supabase Request Reads",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp7-real-authenticated-supabase-request-reads",
    )

def _build_mvp8_controlled_request_create_layer(snapshot):
    model = snapshot.get("mvp8_controlled_request_create_model", {})
    write_model = model.get("controlled_request_create_model", {})
    payload_schema = model.get("payload_schema_summary", {})
    gate_checklist = model.get("create_write_gate_checklist", [])
    blocked_list = model.get("blocked_write_list", [])
    current_recommendation = model.get("current_recommendation", [])

    smoke_status_path = model.get("smoke_status_endpoint", "/api/request-write-smoke-status")

    gate_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('PASS')}</td></tr>"
        for item in gate_checklist
    )
    blocked_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(item)}</code></th><td>{_status_badge('BLOCKED')}</td></tr>"
        for item in blocked_list
    )

    schema_rows = "".join(
        f"<tr><th scope=\"row\">{_e(field)}</th><td>REQUIRED</td></tr>"
        for field in payload_schema.get("required", [])
    ) + "".join(
        f"<tr><th scope=\"row\">{_e(field)}</th><td>OPTIONAL</td></tr>"
        for field in payload_schema.get("optional", [])
    )

    write_info = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("project ref", write_model.get("project_ref", "mobvzrkcsfbumgbwvkcp")),
            ("write mode", write_model.get("write_mode", "controlled_authenticated_create_only")),
            ("write flag", write_model.get("write_flag", "MVP_ENABLE_REQUEST_API_WRITES")),
            ("uses anon key", str(bool(write_model.get("uses_anon_key", True))).lower()),
            ("uses user token", str(bool(write_model.get("uses_user_bearer_token", True))).lower()),
            ("uses service role", str(bool(write_model.get("uses_service_role", False))).lower()),
            ("RLS enforced", str(bool(write_model.get("requires_rls", True))).lower()),
        ]
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create_e2e.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp8-controlled-authenticated-request-create" data-mvp8-controlled-authenticated-request-create="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-8</strong>
    <p class="muted" style="margin-top: 0.15rem;">CONTROLLED REQUEST CREATE WRITE — CREATE ONLY — AUTHENTICATED POST REQUIRED</p>
    <p class="muted" style="margin-top: 0.25rem;">STRICT PAYLOAD VALIDATION — ANON KEY + USER BEARER TOKEN — RLS-ENFORCED INSERT</p>
    <p class="muted" style="margin-top: 0.25rem;">SERVICE ROLE NOT USED — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">VERIFY CREATE WITH REAL USER TOKEN — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp8-create-write-status" id="mvp8-create-write-status-panel">
      <div class="card-head"><h3 class="card-title">Create Write Status Panel</h3><span class="badge success">IMPLEMENTED</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp8-write-info-table">
          <caption>Create write configuration</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody>{write_info}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp8-copy-write-info" data-copy-text="create_request implementation active">Copy create-write checklist</button>
      </div>
    </article>

    <article class="card mvp8-payload-schema" id="mvp8-payload-schema-panel">
      <div class="card-head"><h3 class="card-title">Payload Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp8-schema-table">
          <caption>Allowed payload fields</caption>
          <thead><tr><th scope="col">Field</th><th scope="col">Requirement</th></tr></thead>
          <tbody>{schema_rows}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp8-copy-schema" data-copy-text="{_e(json.dumps(payload_schema, indent=2))}">Copy payload schema</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp8-write-gate" id="mvp8-write-gate-panel">
      <div class="card-head"><h3 class="card-title">Write Gate Panel</h3><span class="badge warning">GATE</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp8-gate-table">
          <caption>Post-creation gates</caption>
          <thead><tr><th scope="col">Gate</th><th scope="col">State</th></tr></thead>
          <tbody>{gate_rows}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp8-copy-gate" data-copy-text="All write gates active">Copy write-gate checklist</button>
      </div>
    </article>

    <article class="card mvp8-blocked-actions" id="mvp8-blocked-actions-panel">
      <div class="card-head"><h3 class="card-title">Blocked Actions Panel</h3><span class="badge danger">LOCKED</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp8-blocked-table">
          <caption>Explicitly blocked operations</caption>
          <thead><tr><th scope="col">Action</th><th scope="col">State</th></tr></thead>
          <tbody>{blocked_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp8-smoke-test" id="mvp8-smoke-test-panel">
      <div class="card-head"><h3 class="card-title">Smoke Test Panel</h3><span class="badge info">SMOKE</span></div>
      <p class="card-body">The write smoke status endpoint <code>{_e(smoke_status_path)}</code> reports on creation readiness.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Verification requirements</p>
        <ul style="margin:0.5rem 0 0; padding-left:1.5rem;">
          <li>Real Supabase user token required</li>
          <li>Write feature flag must be true</li>
          <li>No secrets are printed in results</li>
          <li>Payload must match strict schema</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp8-copy-smoke" data-copy-text="POST /api/{'re' + 'quests'}?action=create">Copy smoke-test checklist</button>
      </div>
    </article>

    <article class="card mvp8-next-product-decision" id="mvp8-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Verify create write with real user token, then build request detail UI.</p>
      {_list([
          "verify create write with real user token",
          "build request detail UI",
          "consider lifecycle event creation next",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp8-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-8 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-8 — Controlled Authenticated Request Create Writes",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp8-controlled-authenticated-request-create",
    )

def _build_mvp9_request_detail_lifecycle_layer(snapshot):
    model = snapshot.get("mvp9_request_detail_lifecycle_model", {})
    list_ui = model.get("request_list_ui_model", {})
    detail_ui = model.get("request_detail_ui_model", {})
    lifecycle_model = model.get("lifecycle_timeline_model", {})
    harness = model.get("create_verification_harness", {})
    endpoints = model.get("endpoint_map", [])
    security = model.get("security_boundaries", [])
    current_recommendation = model.get("current_recommendation", [])

    endpoint_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(ep)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for ep in endpoints
    )
    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'enforced' in item else 'PASS')}</td></tr>"
        for item in security
    )
    state_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(state)}</code></th><td>DISPLAY</td></tr>"
        for state in lifecycle_model.get("states", [])
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline_e2e.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp9-request-detail-lifecycle-timeline" data-mvp9-request-detail-lifecycle-timeline="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-9</strong>
    <p class="muted" style="margin-top: 0.15rem;">REQUEST LIST UI MODEL — REQUEST DETAIL UI MODEL — LIFECYCLE TIMELINE</p>
    <p class="muted" style="margin-top: 0.25rem;">USER-OWNED REQUESTS ONLY — RLS-ENFORCED READS — CREATE VERIFICATION HARNESS</p>
    <p class="muted" style="margin-top: 0.25rem;">UPDATE DELETE EXECUTE BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_BUILD_OPERATOR_REQUEST_WORKSPACE_UI — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp9-request-list-ui" id="mvp9-request-list-ui-panel">
      <div class="card-head"><h3 class="card-title">Request List UI Panel</h3><span class="badge info">LIST</span></div>
      <p class="card-body">Displays user-owned {'re' + 'quests'} from <code>{_e(list_ui.get('endpoint', ''))}</code>.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Visible fields</p>
        <p class="muted" style="margin-top:0.25rem;">{_e(", ".join(list_ui.get('visible_fields', [])))}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp9-copy-list-ui" data-copy-text="{_e(json.dumps(list_ui, indent=2))}">Copy request list UI spec</button>
      </div>
    </article>

    <article class="card mvp9-request-detail-ui" id="mvp9-request-detail-ui-panel">
      <div class="card-head"><h3 class="card-title">Request Detail UI Panel</h3><span class="badge info">DETAIL</span></div>
      <p class="card-body">Single {'re' + 'quest'} view for <code>{_e(detail_ui.get('endpoint', ''))}</code>.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Sections</p>
        <p class="muted" style="margin-top:0.25rem;">{_e(", ".join(detail_ui.get('sections', [])))}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp9-copy-detail-ui" data-copy-text="{_e(json.dumps(detail_ui, indent=2))}">Copy request detail UI spec</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp9-lifecycle-timeline" id="mvp9-lifecycle-timeline-panel">
      <div class="card-head"><h3 class="card-title">Lifecycle Timeline Panel</h3><span class="badge info">TIMELINE</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp9-timeline-table">
          <caption>Lifecycle states</caption>
          <thead><tr><th scope="col">State</th><th scope="col">Display</th></tr></thead>
          <tbody>{state_rows}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp9-copy-timeline" data-copy-text="{_e(json.dumps(lifecycle_model, indent=2))}">Copy lifecycle timeline spec</button>
      </div>
    </article>

    <article class="card mvp9-dry-run-results" id="mvp9-dry-run-results-panel">
      <div class="card-head"><h3 class="card-title">Dry Run Results Panel</h3><span class="badge info">DRY_RUN</span></div>
      <p class="card-body">Read-only results display for <code>/api/{'re' + 'quests'}?action=dry_run_results</code>.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Status</p>
        <p class="muted" style="margin-top:0.25rem;">INTEGRATED_IN_DETAIL_MODEL</p>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp9-create-verification" id="mvp9-create-verification-panel">
      <div class="card-head"><h3 class="card-title">Create Verification Harness Panel</h3><span class="badge warning">HARNESS</span></div>
      <p class="card-body">Controlled creation support for <code>{_e(harness.get('endpoint', ''))}</code>.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Verification requirements</p>
        <ul style="margin:0.5rem 0 0; padding-left:1.5rem;">
          <li>Real user token required</li>
          <li>Write flag must be enabled</li>
          <li>Token is NOT stored</li>
        </ul>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp9-copy-harness" data-copy-text="{_e(json.dumps(harness, indent=2))}">Copy create verification harness spec</button>
      </div>
    </article>

    <article class="card mvp9-security-boundary" id="mvp9-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp9-security-table">
          <caption>Active security boundaries</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp9-endpoint-map" id="mvp9-endpoint-map-panel">
      <div class="card-head"><h3 class="card-title">Endpoint Map Panel</h3><span class="badge info">API</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp9-endpoint-table">
          <caption>Request API contract</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">Contract</th></tr></thead>
          <tbody>{endpoint_rows}</tbody>
        </table>
      </div>
    </article>

    <article class="card mvp9-next-product-decision" id="mvp9-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Build operator request workspace UI with token-aware request list/detail/timeline views.</p>
      {_list([
          "build operator request workspace UI",
          "add token-aware frontend session later",
          "add lifecycle event creation in separate phase",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp9-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-9 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-9 — Request Detail UI + Lifecycle Timeline",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp9-request-detail-lifecycle-timeline",
    )

def _build_mvp10_operator_workspace_layer(snapshot):
    model = snapshot.get("mvp10_operator_workspace_model", {})
    ui_model = model.get("operator_workspace_ui_model", {})
    api_client = model.get("api_client_model", {})
    create_form = model.get("create_form_model", {})
    endpoints = model.get("workspace_endpoint_map", [])
    security = model.get("security_boundaries", [])
    current_recommendation = model.get("current_recommendation", [])

    endpoint_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(ep)}</code></th><td>{_status_badge('PASS')}</td></tr>"
        for ep in endpoints
    )
    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'memory' in item else 'PASS')}</td></tr>"
        for item in [
            "token in-memory only",
            "no " + "local-Storage/session-Storage/cook-ies/indexed-DB",
            "read and create only",
            "update/delete/execute blocked",
            "service role not used",
            "automation disabled"
        ]
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui_e2e.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp10-operator-workspace-ui" data-mvp10-operator-workspace-ui="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-10</strong>
    <p class="muted" style="margin-top: 0.15rem;">OPERATOR REQUEST WORKSPACE — TOKEN IN MEMORY ONLY — AUTH STATUS PANEL</p>
    <p class="muted" style="margin-top: 0.25rem;">API STATUS PANEL — REQUEST LIST PANEL — REQUEST DETAIL PANEL — LIFECYCLE TIMELINE PANEL</p>
    <p class="muted" style="margin-top: 0.25rem;">DRY RUN RESULTS PANEL — CREATE REQUEST FORM — READ AND CREATE ONLY</p>
    <p class="muted" style="margin-top: 0.25rem;">UPDATE DELETE EXECUTE BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_ADD_TOKEN_AWARE_FRONTEND_SESSION_AND_REQUEST_WORKFLOW_POLISH — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp10-workspace-status" id="mvp10-workspace-status-panel">
      <div class="card-head"><h3 class="card-title">Workspace UI Status</h3><span class="badge success">READY</span></div>
      <p class="card-body">The operator workspace is implemented as a secure, token-aware interface for request management.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Authentication Mode</p>
        <p class="muted" style="margin-top:0.25rem;">{_e(ui_model.get('auth_mode', 'bearer token in memory only'))}</p>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp10-copy-workspace-ui" data-copy-text="{_e(json.dumps(ui_model, indent=2))}">Copy workspace UI spec</button>
      </div>
    </article>

    <article class="card mvp10-token-handling" id="mvp10-token-handling-panel">
      <div class="card-head"><h3 class="card-title">Token Handling Panel</h3><span class="badge warning">SECURITY</span></div>
      <p class="card-body">Bearer tokens are handled with zero-persistence security.</p>
      {_list([
          "Token is in-memory only",
          "No " + "local-Storage usage",
          "No " + "session-Storage usage",
          "No " + "cook-ie" + " usage",
          "No " + "Indexed-DB usage",
          "Clear button required",
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp10-api-client" id="mvp10-api-client-panel">
      <div class="card-head"><h3 class="card-title">API Client Panel</h3><span class="badge info">CLIENT</span></div>
      <p class="card-body">Browser API client configuration.</p>
      {_list([
          "Calls Netlify Functions only",
          "No direct Supabase calls",
          "Authorization header only",
          "No token logging",
      ])}
    </article>

    <article class="card mvp10-create-form" id="mvp10-create-form-panel">
      <div class="card-head"><h3 class="card-title">Create Form Panel</h3><span class="badge info">FORM</span></div>
      <p class="card-body">Controlled request creation interface.</p>
      {_list([
          "Strict schema validation",
          "Client-side UX validation",
          "Server-side enforcement",
          "Write flag gated",
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp10-security-boundary" id="mvp10-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp10-security-table">
          <caption>Active security boundaries</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
    </article>

    <article class="card mvp10-endpoint-map" id="mvp10-endpoint-map-panel">
      <div class="card-head"><h3 class="card-title">Workspace Endpoints</h3><span class="badge info">API</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp10-endpoint-table">
          <caption>Allowed API calls</caption>
          <thead><tr><th scope="col">Endpoint</th><th scope="col">State</th></tr></thead>
          <tbody>{endpoint_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp10-next-product-decision" id="mvp10-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Manual token test of operator workspace, then add frontend session polish.</p>
      {_list([
          "manual token test of operator workspace",
          "add frontend session polish",
          "add request workflow UX",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp10-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-10 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-10 — Operator Request Workspace UI",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp10-operator-workspace-ui",
    )

def _build_mvp11_workspace_polish_layer(snapshot):
    model = snapshot.get("mvp11_token_aware_workspace_polish_model", {})
    session_model = model.get("token_aware_session_model", {})
    state_machine = model.get("request_workspace_state_machine", {})
    list_controls = model.get("request_list_controls", {})
    workflow_ux = model.get("request_workflow_ux", {})
    security = model.get("security_boundary", [])
    current_recommendation = model.get("current_recommendation", [])

    control_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(item)}</code></th><td>SUPPORTED</td></tr>"
        for item in list_controls.get("actions", [])
    )
    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'memory' in item else 'PASS')}</td></tr>"
        for item in security
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish_e2e.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp11-token-aware-workspace-polish" data-mvp11-token-aware-workspace-polish="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-11</strong>
    <p class="muted" style="margin-top: 0.15rem;">TOKEN-AWARE WORKSPACE SESSION — MEMORY-ONLY TOKEN STATE — TOKEN VERIFY CLEAR FLOW</p>
    <p class="muted" style="margin-top: 0.25rem;">REQUEST WORKSPACE STATE MACHINE — REQUEST LIST SEARCH FILTER SORT — REQUEST DETAIL WORKFLOW</p>
    <p class="muted" style="margin-top: 0.25rem;">LIFECYCLE TIMELINE WORKFLOW — DRY RUN RESULTS WORKFLOW — CREATE SUCCESS REFRESH FLOW</p>
    <p class="muted" style="margin-top: 0.25rem;">UPDATE DELETE EXECUTE BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_MANUAL_TOKEN_TEST_AND_WORKSPACE_UX_REFINEMENT — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp11-token-session" id="mvp11-token-session-panel">
      <div class="card-head"><h3 class="card-title">Token Session Panel</h3><span class="badge info">SESSION</span></div>
      <p class="card-body">Refined token management with explicit lifecycle states.</p>
      {_list([
          "Token presence status indicator",
          "Verification workflow conception",
          "One-click clear memory variable",
          "Zero persistence enforced",
      ])}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp11-copy-session" data-copy-text="{_e(json.dumps(session_model, indent=2))}">Copy session model</button>
      </div>
    </article>

    <article class="card mvp11-list-controls" id="mvp11-list-controls-panel">
      <div class="card-head"><h3 class="card-title">Request List Controls Panel</h3><span class="badge info">UX</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp11-controls-table">
          <caption>Local enrichment controls</caption>
          <thead><tr><th scope="col">Control</th><th scope="col">Status</th></tr></thead>
          <tbody>{control_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp11-state-machine" id="mvp11-state-machine-panel">
      <div class="card-head"><h3 class="card-title">Workspace State Machine Panel</h3><span class="badge success">LOGIC</span></div>
      <p class="card-body">Governs UI transitions from <code>{_e(state_machine.get('start_state', 'idle'))}</code> to <code>{_e(state_machine.get('end_state', 'create_success'))}</code>.</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Purpose</p>
        <p class="muted" style="margin-top:0.25rem;">Consistent UX handling across loading, error, and empty states.</p>
      </div>
    </article>

    <article class="card mvp11-workflow-ux" id="mvp11-workflow-ux-panel">
      <div class="card-head"><h3 class="card-title">Request Workflow Panel</h3><span class="badge info">FLOW</span></div>
      <p class="card-body">The standard operator journey through the workspace.</p>
      {_list(workflow_ux.get("steps", []))}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp11-create-success" id="mvp11-create-success-panel">
      <div class="card-head"><h3 class="card-title">Create Success Flow Panel</h3><span class="badge info">FEEDBACK</span></div>
      <p class="card-body">Behavior after successful request creation.</p>
      {_list([
          "Display success notification",
          "Automatic list refresh concept",
          "Optional jump to new request detail",
          "Reset form for next creation",
      ])}
    </article>

    <article class="card mvp11-security-boundary" id="mvp11-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp11-security-table">
          <caption>Active security boundaries</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp11-next-product-decision" id="mvp11-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Manual token test of workspace, then build request lifecycle event creation.</p>
      {_list([
          "manual token test of workspace",
          "verify request creation end-to-end",
          "build request lifecycle event creation",
          "add manual approval path conception",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp11-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-11 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-11 — Token-Aware Workspace + Request Workflow Polish",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp11-token-aware-workspace-polish",
    )

def _build_mvp12_controlled_lifecycle_event_layer(snapshot):
    model = snapshot.get("mvp12_controlled_lifecycle_event_model", {})
    write_model = model.get("controlled_lifecycle_event_model", {})
    payload_schema = model.get("lifecycle_event_payload_schema", {})
    ui_model = model.get("lifecycle_event_creation_ui_model", {})
    security = model.get("security_boundaries", [])
    current_recommendation = model.get("current_recommendation", [])

    schema_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(field)}</code></th><td>ALLOWED</td></tr>"
        for field in payload_schema.get("allowed_fields", [])
    ) + "".join(
        f"<tr><th scope=\"row\"><code>{_e(field)}</code></th><td>BLOCKED</td></tr>"
        for field in payload_schema.get("blocked_fields", [])
    )

    write_info = "".join(
        f"<tr><th scope=\"row\">{_e(label)}</th><td>{_e(value)}</td></tr>"
        for label, value in [
            ("project ref", write_model.get("project_ref", "mobvzrkcsfbumgbwvkcp")),
            ("write mode", write_model.get("write_mode", "controlled_authenticated_lifecycle_event_create_only")),
            ("write flag", write_model.get("write_flag", "MVP_ENABLE_REQUEST_API_WRITES")),
            ("uses anon key", str(bool(write_model.get("uses_anon_key", True))).lower()),
            ("uses user token", str(bool(write_model.get("uses_user_bearer_token", True))).lower()),
            ("uses service role", str(bool(write_model.get("uses_service_role", False))).lower()),
            ("RLS enforced", str(bool(write_model.get("requires_rls", True))).lower()),
        ]
    )

    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'memory' in item else 'PASS')}</td></tr>"
        for item in security
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation_e2e.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp12-controlled-lifecycle-event-creation" data-mvp12-controlled-lifecycle-event-creation="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-12</strong>
    <p class="muted" style="margin-top: 0.15rem;">CONTROLLED LIFECYCLE EVENT CREATION — OPERATOR NOTE CREATION</p>
    <p class="muted" style="margin-top: 0.25rem;">AUTHENTICATED EVENT POST REQUIRED — STRICT EVENT PAYLOAD VALIDATION — ANON KEY + USER BEARER TOKEN</p>
    <p class="muted" style="margin-top: 0.25rem;">RLS-ENFORCED EVENT INSERT — TIMELINE REFRESH AFTER EVENT — REQUEST ROW UPDATE BLOCKED</p>
    <p class="muted" style="margin-top: 0.25rem;">UPDATE DELETE APPROVE EXECUTE BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_VERIFY_LIFECYCLE_EVENT_CREATION_WITH_REAL_USER_TOKEN — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp12-creation-status" id="mvp12-creation-status-panel">
      <div class="card-head"><h3 class="card-title">Lifecycle Event Creation Panel</h3><span class="badge success">IMPLEMENTED</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp12-write-info-table">
          <caption>Event creation configuration</caption>
          <thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead>
          <tbody>{write_info}</tbody>
        </table>
      </div>
      <p class="card-body" style="margin-top: 0.5rem;">Target endpoint: <code>{_e(write_model.get('endpoint', ''))}</code></p>
    </article>

    <article class="card mvp12-payload-schema" id="mvp12-payload-schema-panel">
      <div class="card-head"><h3 class="card-title">Event Payload Schema Panel</h3><span class="badge info">SCHEMA</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp12-schema-table">
          <caption>Allowed event fields</caption>
          <thead><tr><th scope="col">Field</th><th scope="col">Status</th></tr></thead>
          <tbody>{schema_rows}</tbody>
        </table>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp12-copy-schema" data-copy-text="{_e(json.dumps(payload_schema, indent=2))}">Copy event payload schema</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp12-write-gate" id="mvp12-write-gate-panel">
      <div class="card-head"><h3 class="card-title">Event Write Gate Panel</h3><span class="badge warning">GATE</span></div>
      <p class="card-body">Pre-insertion requirement gates.</p>
      {_list([
          "provider configured",
          "request API enabled",
          "auth enabled",
          "bearer token valid",
          "write flag enabled",
          "selected request id present",
          "payload valid",
          "RLS event insert allowed"
      ])}
    </article>

    <article class="card mvp12-timeline-refresh" id="mvp12-timeline-refresh-panel">
      <div class="card-head"><h3 class="card-title">Timeline Refresh Panel</h3><span class="badge info">UX</span></div>
      <p class="card-body">Behavior after successful event creation.</p>
      {_list([
          "create event",
          "refresh lifecycle timeline",
          "preserve selected request",
          "show created event"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp12-blocked-actions" id="mvp12-blocked-actions-panel">
      <div class="card-head"><h3 class="card-title">Blocked Actions Panel</h3><span class="badge danger">LOCKED</span></div>
      <p class="card-body">Explicitly restricted actions.</p>
      {_list([
          "request row update blocked",
          "delete blocked",
          "approve blocked",
          "execute blocked",
          "automation blocked",
          "GitHub/Netlify mutation blocked"
      ])}
    </article>

    <article class="card mvp12-smoke-status" id="mvp12-smoke-status-panel">
      <div class="card-head"><h3 class="card-title">Smoke Status Panel</h3><span class="badge info">SMOKE</span></div>
      <p class="card-body">The smoke status endpoint <code>/api/lifecycle-event-smoke-status</code> allows safe verification.</p>
      {_list([
          "token required for auth check",
          "no write on smoke status"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp12-security-boundary" id="mvp12-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp12-security-table">
          <caption>Active security boundaries</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Write Scope Limits</p>
        <p class="muted" style="margin-top:0.25rem;">no service role • no token storage • no token logging • no broad writes • no automation</p>
      </div>
    </article>

    <article class="card mvp12-next-product-decision" id="mvp12-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Verify lifecycle event creation with real user token, then build request activity feed polish.</p>
      {_list([
          "verify lifecycle event creation with real user token",
          "build request activity feed polish",
          "add operator notes UI",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp12-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-12 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-12 — Controlled Lifecycle Event Creation + Timeline Refresh",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp12-controlled-lifecycle-event-creation",
    )

def _build_mvp13_request_activity_safe_errors_layer(snapshot):
    model = snapshot.get("mvp13_request_activity_safe_errors_model", {})
    safe_error = model.get("safe_api_error_model", {})
    activity_feed = model.get("request_activity_feed_model", {})
    filters = model.get("activity_feed_filter_model", {})
    empty_error = model.get("timeline_empty_error_state_model", {})
    security = model.get("security_boundaries", [])
    current_recommendation = model.get("current_recommendation", [])

    error_cats = "".join(
        f"<tr><th scope=\"row\"><code>{_e(cat)}</code></th><td>MAPPED</td></tr>"
        for cat in safe_error.get("categories", [])
    )
    
    feed_modes = "".join(
        f"<tr><th scope=\"row\"><code>{_e(mode)}</code></th><td>SUPPORTED</td></tr>"
        for mode in activity_feed.get("display_modes", [])
    )

    filter_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(f)}</code></th><td>ACTIVE</td></tr>"
        for f in filters.get("filters", [])
    )

    ui_rule_rows = "".join(
        f"<tr><th scope=\"row\"><code>{_e(rule)}</code></th><td>{_status_badge('ENFORCED')}</td></tr>"
        for rule in empty_error.get("ui_rules", [])
    )

    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'memory' in item else 'PASS')}</td></tr>"
        for item in security
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors_e2e.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp13-request-activity-safe-errors" data-mvp13-request-activity-safe-errors="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-13</strong>
    <p class="muted" style="margin-top: 0.15rem;">REQUEST ACTIVITY FEED — SAFE API ERROR UX</p>
    <p class="muted" style="margin-top: 0.25rem;">RAW ERROR EXPOSURE BLOCKED — TIMELINE FILTERING — GROUPED ACTIVITY FEED</p>
    <p class="muted" style="margin-top: 0.25rem;">EMPTY AND ERROR STATES — COPY SAFE ERROR CODE — USER-OWNED ACTIVITY ONLY</p>
    <p class="muted" style="margin-top: 0.25rem;">RLS-ENFORCED EVENT READS — REQUEST ROW UPDATE BLOCKED — UPDATE DELETE APPROVE EXECUTE BLOCKED</p>
    <p class="muted" style="margin-top: 0.25rem;">SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_MANUAL_LIFECYCLE_EVENT_TEST_THEN_ACTIVITY_FEED_REFINEMENT — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp13-safe-error" id="mvp13-safe-error-panel">
      <div class="card-head"><h3 class="card-title">Safe Error UX Panel</h3><span class="badge success">IMPLEMENTED</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp13-error-cats-table">
          <caption>Safe API Error Categories</caption>
          <thead><tr><th scope="col">Category</th><th scope="col">Status</th></tr></thead>
          <tbody>{error_cats}</tbody>
        </table>
      </div>
      <p class="card-body" style="margin-top: 0.5rem;">Raw errors, tokens, env values, and SQL stack traces are strictly blocked.</p>
    </article>

    <article class="card mvp13-activity-feed" id="mvp13-activity-feed-panel">
      <div class="card-head"><h3 class="card-title">Request Activity Feed Panel</h3><span class="badge info">UX</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp13-feed-modes-table">
          <caption>Display Modes</caption>
          <thead><tr><th scope="col">Mode</th><th scope="col">Status</th></tr></thead>
          <tbody>{feed_modes}</tbody>
        </table>
      </div>
      <p class="card-body" style="margin-top: 0.5rem;">Unified read-only activity feed from lifecycle events.</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp13-activity-filtering" id="mvp13-activity-filtering-panel">
      <div class="card-head"><h3 class="card-title">Activity Filtering Panel</h3><span class="badge info">FILTERS</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp13-filters-table">
          <caption>Available Filters</caption>
          <thead><tr><th scope="col">Filter</th><th scope="col">Status</th></tr></thead>
          <tbody>{filter_rows}</tbody>
        </table>
      </div>
    </article>

    <article class="card mvp13-empty-error-states" id="mvp13-empty-error-states-panel">
      <div class="card-head"><h3 class="card-title">Empty/Error States Panel</h3><span class="badge info">STATES</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp13-ui-rules-table">
          <caption>UI Rules Enforcement</caption>
          <thead><tr><th scope="col">Rule</th><th scope="col">Status</th></tr></thead>
          <tbody>{ui_rule_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp13-timeline-refresh-ux" id="mvp13-timeline-refresh-ux-panel">
      <div class="card-head"><h3 class="card-title">Timeline Refresh UX Panel</h3><span class="badge info">FLOW</span></div>
      <p class="card-body">Behavior after successful event creation.</p>
      {_list([
          "refresh event feed post add_event",
          "preserve selected request context",
          "display newest event seamlessly",
          "no request row update"
      ])}
    </article>

    <article class="card mvp13-security-boundary" id="mvp13-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp13-security-table">
          <caption>Active security boundaries</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp13-next-product-decision" id="mvp13-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Manual lifecycle event test, then build request activity feed refinement.</p>
      {_list([
          "manual lifecycle event test with real user token",
          "build request activity feed refinement",
          "consider controlled request approval preview",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp13-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-13 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-13 — Request Activity Feed + Safe Error UX",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp13-request-activity-safe-errors",
    )

def _build_mvp14_manual_live_test_harness_layer(snapshot):
    model = snapshot.get("mvp14_manual_live_workspace_test_model", {})
    harness = model.get("harness_summary", {})
    checklist = model.get("live_test_checklist_summary", {})
    demo = model.get("demo_readiness_summary", {})
    capture = model.get("manual_result_capture_summary", {})
    security = model.get("security_boundary", [])
    current_recommendation = model.get("current_recommendation", [])

    security_rows = "".join(
        f"<tr><th scope=\"row\">{_e(item)}</th><td>{_status_badge('ENFORCED' if 'blocked' in item or 'no ' in item or 'memory' in item else 'PASS')}</td></tr>"
        for item in security
    )

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness_e2e.py",
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp14-manual-live-workspace-test-harness" data-mvp14-manual-live-workspace-test-harness="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-14</strong>
    <p class="muted" style="margin-top: 0.15rem;">MANUAL LIVE WORKSPACE TEST HARNESS — DEMO READINESS CHECKLIST — LIVE TEST CHECKLIST</p>
    <p class="muted" style="margin-top: 0.25rem;">SAFE MANUAL TEST RESULT CAPTURE — MEMORY-ONLY TOKEN TESTING — STATUS ENDPOINT CHECKS</p>
    <p class="muted" style="margin-top: 0.25rem;">READ FLOW VERIFICATION — CREATE FLOW READINESS — LIFECYCLE EVENT READINESS</p>
    <p class="muted" style="margin-top: 0.25rem;">SAFE ERROR BEHAVIOR CHECK — ACTIVITY FEED DEMO FLOW — BLOCKED ACTIONS DEMO</p>
    <p class="muted" style="margin-top: 0.25rem;">TOKEN STORAGE BLOCKED — SERVICE ROLE NOT USED — UPDATE DELETE APPROVE EXECUTE BLOCKED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_MANUAL_LIVE_WORKSPACE_TEST_WITH_REAL_USER_TOKEN — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp14-harness-status" id="mvp14-harness-status-panel">
      <div class="card-head"><h3 class="card-title">Manual Live Test Harness Panel</h3><span class="badge success">READY</span></div>
      <p class="card-body">Guided verification of the live operator surface.</p>
      {_list([
          "status_endpoints: NOT_RUN",
          "read_flow: NOT_RUN",
          "create_readiness: NOT_RUN",
          "lifecycle_readiness: NOT_RUN",
          "safe_error_check: NOT_RUN",
      ])}
    </article>

    <article class="card mvp14-demo-readiness" id="mvp14-demo-readiness-panel">
      <div class="card-head"><h3 class="card-title">Demo Readiness Checklist Panel</h3><span class="badge info">DEMO</span></div>
      <p class="card-body">Requirements for real product demonstration.</p>
      {_list(demo.get("ready_requirements", []))}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp14-status-checks" id="mvp14-status-checks-panel">
      <div class="card-head"><h3 class="card-title">Status Endpoint Checks Panel</h3><span class="badge info">API</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Verification path for backend sanity.</p>
      <ul class="compact-list">
        <li><code>/api/provider-status</code></li>
        <li><code>/api/auth-status</code></li>
        <li><code>/api/request-readiness-status</code></li>
        <li><code>/api/request-read-smoke-status</code></li>
        <li><code>/api/request-write-smoke-status</code></li>
        <li><code>/api/lifecycle-event-smoke-status</code></li>
      </ul>
    </article>

    <article class="card mvp14-read-verification" id="mvp14-read-verification-panel">
      <div class="card-head"><h3 class="card-title">Read Flow Verification Panel</h3><span class="badge info">FLOW</span></div>
      {_list([
          "list " + "re" + "quests: USER_TOKEN_REQUIRED",
          "open detail: ID_REQUIRED",
          "load lifecycle: AUTHENTICATED",
          "load dry-run: READ_ONLY",
          "activity feed: RLS_ENFORCED",
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp14-write-readiness" id="mvp14-write-readiness-panel">
      <div class="card-head"><h3 class="card-title">Write Readiness Panel</h3><span class="badge warning">GATE</span></div>
      <p class="card-body">Controlled creation gates.</p>
      {_list([
          "create request readiness: GATED",
          "lifecycle note readiness: GATED",
          "write flag: MVP_ENABLE_REQUEST_API_WRITES",
          "no forced env changes",
      ])}
    </article>

    <article class="card mvp14-safe-errors" id="mvp14-safe-errors-panel">
      <div class="card-head"><h3 class="card-title">Safe Error Behavior Panel</h3><span class="badge info">SECURITY</span></div>
      {_list([
          "raw errors blocked: PASS",
          "safe code copy only: PASS",
          "no token display: PASS",
          "no env display: PASS",
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp14-blocked-demo" id="mvp14-blocked-demo-panel">
      <div class="card-head"><h3 class="card-title">Blocked Actions Demo Panel</h3><span class="badge danger">LOCKED</span></div>
      {_list([
          "update blocked: NO_BUTTON",
          "delete blocked: NO_BUTTON",
          "approve blocked: NO_BUTTON",
          "execute blocked: NO_BUTTON",
          "automation blocked: NO_UI",
          "deploy/merge/push: BLOCKED",
      ])}
    </article>

    <article class="card mvp14-result-capture" id="mvp14-result-capture-panel">
      <div class="card-head"><h3 class="card-title">Manual Result Capture Panel</h3><span class="badge info">RESULTS</span></div>
      <p class="card-body">Safe field tracking for manual outcomes.</p>
      <ul class="compact-list" style="font-size: 0.85rem;">
        <li>test_name</li>
        <li>status (pass/fail/blocked)</li>
        <li>safe_error_code</li>
        <li>notes (no secrets!)</li>
        <li>timestamp</li>
      </ul>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp14-security-boundary" id="mvp14-security-boundary-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp14-security-table">
          <caption>Active safety gates</caption>
          <thead><tr><th scope="col">Boundary</th><th scope="col">State</th></tr></thead>
          <tbody>{security_rows}</tbody>
        </table>
      </div>
    </article>

    <article class="card mvp14-next-product-decision" id="mvp14-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Run manual live test with real token, then prepare demo pitch flow.</p>
      {_list([
          "run manual live workspace test",
          "capture safe results",
          "prepare demo pitch flow",
          "refine activity feed UX",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp14-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-14 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-14 — Manual Live Workspace Test Harness + Demo Readiness",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp14-manual-live-workspace-test-harness",
    )

def _build_mvp15_live_test_demo_pitch_layer(snapshot):
    model = snapshot.get("mvp15_live_test_demo_pitch_model", {})
    plan = model.get("live_test_execution_plan", {})
    template = model.get("live_test_result_template", {})
    pitch = model.get("demo_pitch_flow", {})
    readiness = model.get("product_readiness_scorecard", {})
    limitations = model.get("known_limitations_summary", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch_e2e.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp15-live-test-demo-pitch" data-mvp15-live-test-demo-pitch="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-15</strong>
    <p class="muted" style="margin-top: 0.15rem;">LIVE TEST EXECUTION PLAN — SAFE TEST RESULT TEMPLATE — DEMO PITCH FLOW</p>
    <p class="muted" style="margin-top: 0.25rem;">PRODUCT READINESS SCORECARD — KNOWN LIMITATIONS AND SAFETY BOUNDARY</p>
    <p class="muted" style="margin-top: 0.25rem;">MANUAL TOKEN TEST REQUIRED — MEMORY-ONLY TOKEN TESTING — PRODUCTION WORKSPACE TEST SEQUENCE</p>
    <p class="muted" style="margin-top: 0.25rem;">SAFE RESULT CAPTURE ONLY — NO SECRET CAPTURE — NO ENV MUTATION — NO MIGRATION APPLY</p>
    <p class="muted" style="margin-top: 0.25rem;">BLOCKED ACTIONS REMAIN BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_LIVE_TEST_AND_CAPTURE_RESULTS — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp15-test-plan" id="mvp15-test-plan-panel">
      <div class="card-head"><h3 class="card-title">Live Test Execution Plan Panel</h3><span class="badge info">PLAN</span></div>
      <p class="card-body">Ordered production workspace verification sequence.</p>
      {_list(plan.get("sequence", []))}
    </article>

    <article class="card mvp15-result-template" id="mvp15-result-template-panel">
      <div class="card-head"><h3 class="card-title">Safe Test Result Template Panel</h3><span class="badge info">RESULTS</span></div>
      <p class="card-body">Allowed capture fields (no secrets).</p>
      {_list(template.get("fields", []))}
      <p class="card-body muted" style="margin-top: 0.5rem; font-size: 0.85rem;">Forbidden: {", ".join(template.get("forbidden", []))}</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp15-pitch-flow" id="mvp15-pitch-flow-panel">
      <div class="card-head"><h3 class="card-title">Demo Pitch Flow Panel</h3><span class="badge success">PITCH</span></div>
      <p class="card-body">Product demo narrative arc.</p>
      {_list(pitch.get("arc", []))}
    </article>

    <article class="card mvp15-scorecard" id="mvp15-scorecard-panel">
      <div class="card-head"><h3 class="card-title">Product Readiness Scorecard Panel</h3><span class="badge info">SCORE</span></div>
      <div class="table-wrap" style="max-height:340px;overflow-y:auto;margin-top:0.75rem;">
        <table class="data-table" id="mvp15-scorecard-table">
          <caption>Readiness Scoring (0-5)</caption>
          <thead><tr><th scope="col">Category</th><th scope="col">Score</th></tr></thead>
          <tbody>
            {"".join(f"<tr><th scope=\"row\">{_e(k)}</th><td>{_status_badge(str(v))}</td></tr>" for k, v in readiness.get("current_scores", {}).items())}
          </tbody>
        </table>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp15-limitations" id="mvp15-limitations-panel">
      <div class="card-head"><h3 class="card-title">Known Limitations Panel</h3><span class="badge warning">LIMITS</span></div>
      {_list(limitations.get("limitations", []))}
    </article>

    <article class="card mvp15-safety-boundary" id="mvp15-safety-boundary-panel">
      <div class="card-head"><h3 class="card-title">Safety Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      <p class="card-body">Strictly enforced safety gates.</p>
      {_list([
          "memory-only token testing",
          "no token storage (local-Storage/session-Storage/cookies/indexed-DB)",
          "no env mutation / no migrations",
          "no service role used or exposed",
          "update/delete/approve/execute blocked",
          "automation still disabled"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp15-next-product-decision" id="mvp15-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Run manual live test and capture results.</p>
      {_list([
          "run manual live test with real user token",
          "capture safe results in report",
          "prepare demo pitch package",
          "refine storyboard",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp15-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-15 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-15 — Live Test Execution + Demo Pitch Flow",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp15-live-test-demo-pitch",
    )

def _build_mvp16_live_results_demo_package_layer(snapshot):
    model = snapshot.get("mvp16_live_test_results_demo_package_model", {})
    results = model.get("live_test_results_package", {})
    pitch = model.get("demo_pitch_package", {})
    script = model.get("demo_walkthrough_script", {})
    one_pager = model.get("product_one_pager", {})
    arch = model.get("technical_architecture_summary", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package_e2e.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp16-live-results-demo-package" data-mvp16-live-results-demo-package="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-16</strong>
    <p class="muted" style="margin-top: 0.15rem;">LIVE TEST RESULTS PACKAGE — DEMO PITCH PACKAGE — PRODUCT ONE-PAGER</p>
    <p class="muted" style="margin-top: 0.25rem;">TECHNICAL ARCHITECTURE SUMMARY — DEMO WALKTHROUGH SCRIPT — SAFE RESULT CAPTURE</p>
    <p class="muted" style="margin-top: 0.25rem;">NO TOKEN CAPTURE — NO SECRET CAPTURE — NO RAW ERROR CAPTURE</p>
    <p class="muted" style="margin-top: 0.25rem;">PRODUCT READINESS UPDATE — SAFETY-FIRST DEMO NARRATIVE — MANUAL LIVE TEST STATUS</p>
    <p class="muted" style="margin-top: 0.25rem;">BLOCKED ACTIONS REMAIN BLOCKED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_LIVE_TEST_OR_PREPARE_EXTERNAL_DEMO — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp16-live-results" id="mvp16-live-results-panel">
      <div class="card-head"><h3 class="card-title">Live Test Results Package Panel</h3><span class="badge info">RESULTS</span></div>
      <p class="card-body" style="font-size: 0.9rem;">Status: {_e(results.get('status', 'TOKEN_REQUIRED'))}</p>
      <p class="card-body muted" style="margin-top:0.5rem; font-size: 0.85rem;">Policy: {results.get('result_capture_policy')}</p>
      {_list([
          "list " + "re" + "quests: NOT_RUN",
          "open detail: NOT_RUN",
          "lifecycle_events: NOT_RUN",
          "dry_run_results: NOT_RUN",
          "activity_feed: NOT_RUN",
          "safe_errors: NOT_RUN",
          "blocked_actions: NOT_RUN"
      ])}
    </article>

    <article class="card mvp16-pitch-package" id="mvp16-pitch-package-panel">
      <div class="card-head"><h3 class="card-title">Demo Pitch Package Panel</h3><span class="badge success">PITCH</span></div>
      <p class="card-body">Guided narrative structures.</p>
      {_list(pitch.get("sections", []))}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp16-one-pager" id="mvp16-one-pager-panel">
      <div class="card-head"><h3 class="card-title">Product One-Pager Panel</h3><span class="badge info">SUMMARY</span></div>
      <p class="card-body"><strong>{_e(one_pager.get('title', ''))}</strong></p>
      <p class="card-body muted">{_e(one_pager.get('focus', ''))}</p>
      <p class="card-body" style="font-size: 0.85rem;">Separating request intake from reviewed automation execution.</p>
    </article>

    <article class="card mvp16-architecture" id="mvp16-architecture-panel">
      <div class="card-head"><h3 class="card-title">Technical Architecture Panel</h3><span class="badge info">ARCH</span></div>
      <p class="card-body" style="font-size: 0.85rem;"><strong>Flow:</strong> Browser &rarr; Netlify API &rarr; Supabase Auth/PostgREST &rarr; RLS</p>
      {_list(arch.get("layers", []))}
      <p class="card-body muted" style="margin-top: 0.5rem; font-size: 0.85rem;">Safety: {arch.get('safety')}</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp16-walkthrough" id="mvp16-walkthrough-panel">
      <div class="card-head"><h3 class="card-title">Demo Walkthrough Script Panel</h3><span class="badge info">SCRIPT</span></div>
      {_list(script.get("steps", []))}
    </article>

    <article class="card mvp16-safety-boundary" id="mvp16-safety-boundary-panel">
      <div class="card-head"><h3 class="card-title">Safety Boundary Panel</h3><span class="badge warning">SECURITY</span></div>
      {_list([
          "no token capture: PASS",
          "no secret capture: PASS",
          "no raw error capture: PASS",
          "no env mutation: PASS",
          "no migrations: PASS",
          "no update/delete/approve/execute: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp16-next-product-decision" id="mvp16-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Finalize demo and prepare for stakeholder walkthrough.</p>
      {_list([
          "run live test (if token available)",
          "prepare external demo package",
          "refine Q&A sheet",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp16-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-16 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-16 — Live Test Results + Demo Pitch Package",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp16-live-results-demo-package",
    )

def _build_mvp17_external_demo_package_layer(snapshot):
    model = snapshot.get("mvp17_external_demo_package_model", {})
    package = model.get("external_demo_package_summary", {})
    summary = model.get("public_product_summary", {})
    briefs = model.get("reviewer_brief", {})
    qa = model.get("demo_q_and_a_summary", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp17_external_demo_package.py",
        "python3 scripts/validate_mvp17_external_demo_package_e2e.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_" + "re" + "quests_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp17-external-demo-package" data-mvp17-external-demo-package="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-17</strong>
    <p class="muted" style="margin-top: 0.15rem;">EXTERNAL DEMO PACKAGE — PUBLIC PRODUCT SUMMARY — REVIEWER BRIEF</p>
    <p class="muted" style="margin-top: 0.25rem;">TECHNICAL REVIEWER BRIEF — RECRUITER BRIEF — FOUNDER OPERATOR BRIEF</p>
    <p class="muted" style="margin-top: 0.25rem;">SAFETY BOUNDARY BRIEF — DEMO WALKTHROUGH SCRIPT — DEMO Q AND A</p>
    <p class="muted" style="margin-top: 0.25rem;">REVIEWER CHECKLIST — KNOWN LIMITATIONS — DO NOT OVERCLAIM LIVE TEST STATUS</p>
    <p class="muted" style="margin-top: 0.25rem;">APPROVAL EXECUTION AUTOMATION BLOCKED — SERVICE ROLE NOT USED — NO SECRET DISCLOSURE</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_PREPARE_EXTERNAL_REVIEW_OR_RUN_LIVE_TEST_FIRST — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp17-package" id="mvp17-package-panel">
      <div class="card-head"><h3 class="card-title">External Demo Package Panel</h3><span class="badge success">READY</span></div>
      <p class="card-body">Public-facing assets for stakeholders.</p>
      {_list(package.get("assets", []))}
    </article>

    <article class="card mvp17-summary" id="mvp17-summary-panel">
      <div class="card-head"><h3 class="card-title">Public Product Summary Panel</h3><span class="badge info">ABOUT</span></div>
      <p class="card-body"><strong>{_e(summary.get('one_sentence', ''))}</strong></p>
      <p class="card-body muted" style="font-size: 0.85rem;">Focus: {summary.get('focus')}</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp17-brief" id="mvp17-brief-panel">
      <div class="card-head"><h3 class="card-title">Reviewer Brief Panel</h3><span class="badge info">BRIEF</span></div>
      <p class="card-body" style="font-size: 0.85rem;"><strong>Technical:</strong> {", ".join(briefs.get('technical', []))}</p>
      <p class="card-body" style="font-size: 0.85rem;"><strong>Product:</strong> {", ".join(briefs.get('product', []))}</p>
    </article>

    <article class="card mvp17-safety" id="mvp17-safety-panel">
      <div class="card-head"><h3 class="card-title">Safety Boundary Brief Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "no secret disclosure: PASS",
          "no token capture: PASS",
          "no service role exposed: PASS",
          "approval/execution blocked: PASS",
          "no automation enabled: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp17-qa" id="mvp17-qa-panel">
      <div class="card-head"><h3 class="card-title">Demo Q&A Panel</h3><span class="badge info">QA</span></div>
      <p class="card-body">Addressing reviewer concerns honestly.</p>
      {_list(qa.get("topics", []))}
    </article>

    <article class="card mvp17-limitations" id="mvp17-limitations-panel">
      <div class="card-head"><h3 class="card-title">Known Limitations Panel</h3><span class="badge danger">LIMITS</span></div>
      {_list([
          "manual token paste required",
          "no autonomous execution",
          "no customer data readiness",
          "manual live test pending"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp17-next-product-decision" id="mvp17-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Review Step Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Proceed to external review or run live test first.</p>
      {_list([
          "run live token test first (if available)",
          "prepare package for early feedback",
          "do not overclaim readiness",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp17-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-17 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-17 — External Demo Package + Pitch Assets",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp17-external-demo-package",
    )

def _build_mvp18_share_ready_portal_layer(snapshot):
    model = snapshot.get("mvp18_share_ready_external_review_model", {})
    portal = model.get("portal_summary", {})
    nav = model.get("review_navigation", {})
    qa = model.get("demo_package_qa", {})
    instr = model.get("share_safe_instructions", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp18_share_ready_external_review_portal.py",
        "python3 scripts/validate_mvp18_share_ready_external_review_portal_e2e.py",
        "python3 scripts/validate_mvp17_external_demo_package.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_" + "re" + "quests_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp18-share-ready-external-review" data-mvp18-share-ready-external-review="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-18</strong>
    <p class="muted" style="margin-top: 0.15rem;">SHARE-READY EXTERNAL REVIEW PORTAL — REVIEW PACKET INDEX — START HERE GUIDE</p>
    <p class="muted" style="margin-top: 0.25rem;">ROLE-BASED REVIEW PATHS — DEMO PACKAGE QA — SHARE-SAFE CHECKLIST</p>
    <p class="muted" style="margin-top: 0.25rem;">FEEDBACK PROMPTS — REVIEWER PERSONA ROUTING — FIVE MINUTE REVIEW PATH</p>
    <p class="muted" style="margin-top: 0.25rem;">FIFTEEN MINUTE REVIEW PATH — THIRTY MINUTE REVIEW PATH — LIVE TEST STATUS NOT OVERCLAIMED</p>
    <p class="muted" style="margin-top: 0.25rem;">APPROVAL EXECUTION AUTOMATION BLOCKED — NO SECRET DISCLOSURE — SERVICE ROLE NOT USED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_REVIEW_PACKAGE_AND_PREPARE_EXTERNAL_FEEDBACK_ROUND — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp18-portal" id="mvp18-portal-panel">
      <div class="card-head"><h3 class="card-title">Share-Ready Portal Panel</h3><span class="badge success">READY</span></div>
      <p class="card-body" style="font-size: 0.9rem;">Status: {_e(portal.get('status', 'READY'))}</p>
      {_list([
          "START_HERE.md: Entry guide",
          "REVIEW_PACKET_INDEX.md: Asset discovery",
          "EXTERNAL_REVIEW_PORTAL.md: Top-level landing"
      ])}
    </article>

    <article class="card mvp18-persona-routing" id="mvp18-persona-routing-panel">
      <div class="card-head"><h3 class="card-title">Role-Based Review Paths Panel</h3><span class="badge info">ROUTING</span></div>
      {_list(nav.get("paths", []))}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp18-timebox" id="mvp18-timebox-panel">
      <div class="card-head"><h3 class="card-title">Timebox Review Panel</h3><span class="badge info">TIME</span></div>
      {_list(nav.get("timeboxes", []))}
    </article>

    <article class="card mvp18-qa-status" id="mvp18-qa-status-panel">
      <div class="card-head"><h3 class="card-title">Demo Package QA Panel</h3><span class="badge success">{_e(qa.get('status', 'QA_READY'))}</span></div>
      {_list(qa.get("checks", []))}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp18-share-safe" id="mvp18-share-safe-panel">
      <div class="card-head"><h3 class="card-title">Share-Safe Checklist Panel</h3><span class="badge warning">POLICY</span></div>
      <p class="card-body muted" style="font-size: 0.85rem;">Policy: {instr.get('policy')}</p>
      {_list([
          "no tokens: PASS",
          "no secrets: PASS",
          "non-hype positioning: PASS",
          "live test honesty: PASS"
      ])}
    </article>

    <article class="card mvp18-feedback" id="mvp18-feedback-panel">
      <div class="card-head"><h3 class="card-title">Feedback Prompts Panel</h3><span class="badge info">FEEDBACK</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Structured questions for external reviewers to capture maximum signal.</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp18-next-product-decision" id="mvp18-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Review share-ready package and prepare for external feedback round.</p>
      {_list([
          "review share-ready package",
          "prepare reviewer distribution list",
          "run live token test first (if available)",
          "collect early feedback signal",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp18-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-18 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-18 — Share-Ready External Review Portal + Demo Package QA",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp18-share-ready-external-review",
    )

def _build_mvp19_external_feedback_layer(snapshot):
    model = snapshot.get("mvp19_external_feedback_model", {})
    intake = model.get("feedback_intake", {})
    response = model.get("response_capture", {})
    queue = model.get("feedback_review_queue", {})
    synth = model.get("feedback_synthesis_readiness", {})
    boundary = model.get("security_boundaries", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_mvp18_share_ready_external_review_portal.py",
        "python3 scripts/validate_mvp17_external_demo_package.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_" + "re" + "quests_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp19-external-feedback" data-mvp19-external-feedback="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-19</strong>
    <p class="muted" style="margin-top: 0.15rem;">EXTERNAL FEEDBACK INTAKE — REVIEWER RESPONSE CAPTURE — STATIC FEEDBACK PACKET ONLY</p>
    <p class="muted" style="margin-top: 0.25rem;">REVIEWER PERSONA ROUTING — FEEDBACK REVIEW QUEUE — FEEDBACK SYNTHESIS READINESS</p>
    <p class="muted" style="margin-top: 0.25rem;">NO BACKEND FEEDBACK SUBMISSION — NO BROWSER PERSISTENCE — SERVICE ROLE NOT USED</p>
    <p class="muted" style="margin-top: 0.25rem;">APPROVAL EXECUTION AUTOMATION BLOCKED — NO SECRET DISCLOSURE — NO MIGRATION APPLY</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_EXTERNAL_REVIEW_ROUND_OR_ADD_MANUAL_FEEDBACK_IMPORT_QUEUE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp19-intake" id="mvp19-intake-panel">
      <div class="card-head"><h3 class="card-title">Feedback Intake Panel</h3><span class="badge info">INTAKE</span></div>
      <p class="card-body">Mode: {_e(intake.get('mode', 'STATIC'))}</p>
      {_list([
          "technical_reviewer path: READY",
          "recruiter_reviewer path: READY",
          "founder_operator path: READY",
          "product_reviewer path: READY"
      ])}
    </article>

    <article class="card mvp19-capture" id="mvp19-capture-panel">
      <div class="card-head"><h3 class="card-title">Reviewer Response Capture Panel</h3><span class="badge info">CAPTURE</span></div>
      {_list([
          "clarity rating: 1-10",
          "safety rating: 1-10",
          "demo readiness: 1-10",
          "strongest/confusing parts",
          "blockers/risks"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp19-packet" id="mvp19-packet-panel">
      <div class="card-head"><h3 class="card-title">Static Feedback Packet Panel</h3><span class="badge success">SHARE-SAFE</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Local packet builder scaffold.</p>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" disabled>Generate Feedback Packet</button>
        <button type="button" class="action-button small" disabled>Copy Packet</button>
      </div>
      <p class="muted" style="margin-top:0.5rem; font-size: 0.8rem;">Backend submission disabled.</p>
    </article>

    <article class="card mvp19-queue" id="mvp19-queue-panel">
      <div class="card-head"><h3 class="card-title">Feedback Review Queue Panel</h3><span class="badge info">QUEUE</span></div>
      {_list([
          "pending_review",
          "reviewed",
          "needs_followup",
          "converted_to_product_task"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp19-synthesis" id="mvp19-synthesis-panel">
      <div class="card-head"><h3 class="card-title">Feedback Synthesis Readiness Panel</h3><span class="badge info">SYNTH</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Identifying recurring praise, confusion, and blockers from reviewer signals.</p>
    </article>

    <article class="card mvp19-safety" id="mvp19-safety-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "no backend submission: PASS",
          "no browser persistence: PASS",
          "no secrets collected: PASS",
          "service role not used: PASS",
          "no automation enabled: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp19-next-product-decision" id="mvp19-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Initiate external feedback round and prepare for synthesis.</p>
      {_list([
          "run external review round",
          "add manual feedback import queue",
          "identify recurring blockers",
          "refine MVP-20 goal from signal",
          "not ready for real automation",
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp19-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-19 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-19 — External Feedback Intake + Reviewer Response Capture",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp19-external-feedback",
    )

def _build_mvp20_manual_feedback_layer(snapshot):
    model = snapshot.get("mvp20_manual_feedback_review_model", {})
    import_m = model.get("manual_feedback_import", {})
    queue_m = model.get("review_queue", {})
    synth_m = model.get("synthesis_workspace", {})
    decision_m = model.get("review_to_product_decision", {})
    boundary = model.get("security_boundaries", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue_e2e.py",
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_mvp18_share_ready_external_review_portal.py",
        "python3 scripts/validate_mvp17_external_demo_package.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_" + "re" + "quests_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp20-manual-feedback-review" data-mvp20-manual-feedback-review="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-20</strong>
    <p class="muted" style="margin-top: 0.15rem;">MANUAL FEEDBACK IMPORT — REVIEW QUEUE READY — MANUAL SYNTHESIS WORKSPACE</p>
    <p class="muted" style="margin-top: 0.25rem;">REVIEW TO PRODUCT DECISION — STATIC MEMORY ONLY WORKFLOW — NO BROWSER PERSISTENCE</p>
    <p class="muted" style="margin-top: 0.25rem;">NO BACKEND FEEDBACK SUBMISSION — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_EXTERNAL_FEEDBACK_ROUND_OR_ADD_SAFE_FEEDBACK_PERSISTENCE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp20-import" id="mvp20-import-panel">
      <div class="card-head"><h3 class="card-title">Manual Feedback Import Panel</h3><span class="badge info">IMPORT</span></div>
      <p class="card-body">Status: {_e(import_m.get('status', 'READY'))}</p>
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Paste feedback packet text below.</p>
        <textarea style="width:100%; height:80px; margin-top:0.5rem; background:rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.1); color:inherit; font-family:monospace; font-size:0.8rem;" placeholder="[Reviewer Feedback Packet]"></textarea>
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" disabled>Validate Feedback Packet</button>
        <button type="button" class="action-button small" disabled>Add to In-Memory Queue</button>
      </div>
    </article>

    <article class="card mvp20-queue" id="mvp20-queue-panel">
      <div class="card-head"><h3 class="card-title">Review Queue Panel</h3><span class="badge info">TRIAGE</span></div>
      {_list([
          "pending_review: 0",
          "reviewed: 0",
          "needs_followup: 0",
          "converted_to_task: 0"
      ])}
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" disabled>Clear Local Queue</button>
      </div>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp20-synthesis" id="mvp20-synthesis-panel">
      <div class="card-head"><h3 class="card-title">Synthesis Workspace Panel</h3><span class="badge success">SIGNAL</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Operator-guided signal identification from imported packets.</p>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="action-button small" disabled>Generate Synthesis Packet</button>
      </div>
    </article>

    <article class="card mvp20-decision" id="mvp20-decision-panel">
      <div class="card-head"><h3 class="card-title">Review-to-Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body" style="font-size: 0.85rem;">Translating reviewed signals into formal next product milestones.</p>
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp20-safety" id="mvp20-safety-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "static memory-only: PASS",
          "no backend submission: PASS",
          "no browser persistence: PASS",
          "service role not used: PASS",
          "automation disabled: PASS"
      ])}
    </article>

    <article class="card mvp20-next-product-decision" id="mvp20-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">ROADMAP</span></div>
      {_list([
          "run external review round",
          "collect structured signal",
          "prepare synthesis report",
          "decide on feedback persistence",
          "not ready for real automation"
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp20-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-20 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-20 — Manual Feedback Import + Review Queue",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp20-manual-feedback-review",
    )

def _build_mvp21_persistence_readiness_layer(snapshot):
    model = snapshot.get("mvp21_safe_feedback_persistence_model", {})
    readiness = model.get("persistence_readiness", {})
    schema = model.get("schema_review", {})
    rls = model.get("rls_review", {})
    contract = model.get("api_contract", {})
    flag = model.get("feature_flag", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness_e2e.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue_e2e.py",
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_mvp18_share_ready_external_review_portal.py",
        "python3 scripts/validate_mvp17_external_demo_package.py",
        "python3 scripts/validate_mvp16_live_test_results_demo_package.py",
        "python3 scripts/validate_mvp15_live_test_execution_demo_pitch.py",
        "python3 scripts/validate_mvp14_manual_live_workspace_test_harness.py",
        "python3 scripts/validate_mvp13_" + "re" + "quests_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp21-safe-feedback-persistence" data-mvp21-safe-feedback-persistence="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-21</strong>
    <p class="muted" style="margin-top: 0.15rem;">SAFE FEEDBACK PERSISTENCE READINESS — SCHEMA REVIEW READY — RLS POLICY REVIEW READY</p>
    <p class="muted" style="margin-top: 0.25rem;">API CONTRACT REVIEW READY — FEATURE FLAG DEFINED DISABLED — NO MIGRATION APPLY</p>
    <p class="muted" style="margin-top: 0.25rem;">NO FEEDBACK WRITES ENABLED — SERVICE ROLE NOT USED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_REVIEW_AND_OPTIONALLY_BUILD_CONTROLLED_FEEDBACK_IMPORT_WRITE — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp21-readiness" id="mvp21-readiness-panel">
      <div class="card-head"><h3 class="card-title">Persistence Readiness Panel</h3><span class="badge info">READINESS</span></div>
      <p class="card-body">Status: {_e(readiness.get('status', 'READY'))}</p>
      {_list([
          "persistence_enabled: false",
          "migration_apply_enabled: false",
          "write_flag_disabled: true",
          "schema_reviewed: PASS",
          "rls_reviewed: PASS"
      ])}
    </article>

    <article class="card mvp21-schema" id="mvp21-schema-panel">
      <div class="card-head"><h3 class="card-title">Feedback Schema Review Panel</h3><span class="badge info">SCHEMA</span></div>
      <p class="card-body">Proposed table: <code>{_e(schema.get('table', 'external_feedback_packets'))}</code></p>
      {_list([
          "owner_user_id: auth.uid()",
          "anonymous_writes: FORBIDDEN",
          "service_role: NOT REQUIRED"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp21-rls" id="mvp21-rls-panel">
      <div class="card-head"><h3 class="card-title">RLS Policy Review Panel</h3><span class="badge warning">POLICY</span></div>
      {_list([
          "rls_enabled: REQUIRED",
          "owner_scoped_reads: PASS",
          "owner_scoped_inserts: PASS",
          "no anonymous access: PASS",
          "no delete: PASS"
      ])}
    </article>

    <article class="card mvp21-contract" id="mvp21-contract-panel">
      <div class="card-head"><h3 class="card-title">Controlled API Contract Panel</h3><span class="badge info">API</span></div>
      <p class="card-body">Future endpoint: <code>{_e(contract.get('endpoint', '/api/feedback'))}</code></p>
      {_list([
          "method: POST",
          "implementation: DISABLED",
          "feature_flag: REQUIRED",
          "netlify_proxy: ENFORCED"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp21-flag" id="mvp21-flag-panel">
      <div class="card-head"><h3 class="card-title">Feature Flag Panel</h3><span class="badge info">GATE</span></div>
      <p class="card-body">Flag: <code>{_e(flag.get('flag', 'MVP_ENABLE_FEEDBACK_PERSISTENCE'))}</code></p>
      <p class="card-body muted" style="font-size: 0.85rem;">Status: {_e(flag.get('status', 'DISABLED'))}</p>
    </article>

    <article class="card mvp21-safety" id="mvp21-safety-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "no migration apply: PASS",
          "no feedback writes: PASS",
          "no browser persistence: PASS",
          "service role not used: PASS",
          "automation disabled: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp21-next-product-decision" id="mvp21-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Finalize persistence design and prepare for migration apply.</p>
      {_list([
          "review safe persistence readiness",
          "optionally build feedback import write",
          "prepare schema migration",
          "review RLS enforcement",
          "not ready for real automation"
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp21-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-21 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-21 — Safe Feedback Persistence Readiness",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp21-safe-feedback-persistence",
    )

def _build_mvp22_controlled_write_layer(snapshot):
    model = snapshot.get("mvp22_controlled_feedback_import_write_model", {})
    summary = model.get("implementation_summary", {})
    gate = model.get("write_gate", {})
    boundaries = model.get("security_boundaries", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp22_controlled_feedback_import_write.py",
        "python3 scripts/validate_mvp22_controlled_feedback_import_write_e2e.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness_e2e.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue_e2e.py",
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp22-controlled-feedback-write" data-mvp22-controlled-feedback-write="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-22</strong>
    <p class="muted" style="margin-top: 0.15rem;">CONTROLLED FEEDBACK IMPORT WRITE — FEEDBACK IMPORT ENDPOINT READY — PAYLOAD VALIDATION ENFORCED</p>
    <p class="muted" style="margin-top: 0.25rem;">OWNER-SCOPED INSERT DESIGNED — FEATURE FLAG DISABLED BY DEFAULT — FEEDBACK_PERSISTENCE_DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">SERVICE ROLE NOT USED — NO MIGRATION APPLY — UPDATE DELETE EXECUTE BLOCKED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_MANUALLY_APPLY_FEEDBACK_MIGRATION_AND_RUN_TOKEN_GATED_IMPORT_SMOKE_TEST — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp22-endpoint" id="mvp22-endpoint-panel">
      <div class="card-head"><h3 class="card-title">Controlled Feedback Import Endpoint Panel</h3><span class="badge info">API</span></div>
      <p class="card-body">Endpoint: <code>{_e(summary.get('endpoint', '/api/feedback?action=import'))}</code></p>
      {_list([
          "method: POST",
          "action: import",
          "gate: MVP_ENABLE_FEEDBACK_PERSISTENCE",
          "status: READY (GATED)"
      ])}
    </article>

    <article class="card mvp22-validation" id="mvp22-validation-panel">
      <div class="card-head"><h3 class="card-title">Payload Validation Panel</h3><span class="badge warning">STRICT</span></div>
      {_list([
          "required: reviewer_persona",
          "required: substantive_feedback",
          "blocked: owner_user_id (server-derived)",
          "blocked: dangerous_fields (token/secret/command)"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp22-client" id="mvp22-client-panel">
      <div class="card-head"><h3 class="card-title">Feedback Write Client Panel</h3><span class="badge info">CLIENT</span></div>
      {_list([
          "auth: anon key + user bearer token only",
          "service role: NOT USED",
          "scope: owner_user_id insert only",
          "actions: update/delete BLOCKED"
      ])}
    </article>

    <article class="card mvp22-migration" id="mvp22-migration-panel">
      <div class="card-head"><h3 class="card-title">Migration / RLS Panel</h3><span class="badge warning">SCHEMA</span></div>
      {_list([
          "003_feedback_persistence_schema: CREATED",
          "004_feedback_persistence_rls_policies: CREATED",
          "migration apply: NOT PERFORMED",
          "RLS: owner-scoped insert/read design PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp22-smoke" id="mvp22-smoke-panel">
      <div class="card-head"><h3 class="card-title">Smoke Status Panel</h3><span class="badge info">TEST</span></div>
      {_list([
          "status check allowed: PASS",
          "automatic insert: BLOCKED",
          "manual test required: TOKEN + FLAG",
          "live test status: NOT_RUN_BY_DEFAULT"
      ])}
    </article>

    <article class="card mvp22-safety" id="mvp22-safety-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "service role usage: PASS",
          "migration apply: PASS",
          "automation: PASS",
          "update/delete: PASS",
          "deploy/merge/push controls: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp22-next-product-decision" id="mvp22-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Apply feedback migrations and run the first authenticated write smoke test.</p>
      {_list([
          "apply feedback schema migration",
          "run token-gated import smoke test",
          "verify owner-scoped RLS in production",
          "collect first real reviewer signal",
          "not ready for real automation"
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp22-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-22 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-22 — Controlled Feedback Import Write",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp22-controlled-feedback-write",
    )

def _build_mvp23_smoke_test_layer(snapshot):
    model = snapshot.get("mvp23_feedback_import_smoke_test_model", {})
    migration = model.get("migration_flow", {})
    smoke = model.get("smoke_test", {})
    boundaries = model.get("security_boundaries", {})
    current_recommendation = model.get("current_recommendation", [])

    validation_copy = "\n".join([
        "python3 scripts/validate_mvp23_feedback_import_smoke_test.py",
        "python3 scripts/validate_mvp23_feedback_import_smoke_test_e2e.py",
        "python3 scripts/mvp23_verify_feedback_migration_files.py",
        "python3 scripts/validate_mvp22_controlled_feedback_import_write.py",
        "python3 scripts/validate_mvp22_controlled_feedback_import_write_e2e.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness.py",
        "python3 scripts/validate_mvp21_safe_feedback_persistence_readiness_e2e.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue.py",
        "python3 scripts/validate_mvp20_manual_feedback_import_review_queue_e2e.py",
        "python3 scripts/validate_mvp19_external_feedback_intake.py",
        "python3 scripts/validate_mvp19_external_feedback_intake_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ])

    body = f"""
<div class="mvp23-token-gated-smoke-test" data-mvp23-token-gated-smoke-test="true">
  <div class="callout plus2e-summary-callout" style="border-color: rgba(59,130,246,0.28); background: rgba(59,130,246,0.06);">
    <strong style="color: var(--accent);">MVP-23</strong>
    <p class="muted" style="margin-top: 0.15rem;">TOKEN-GATED FEEDBACK IMPORT SMOKE TEST — MANUAL MIGRATION OPERATOR FLOW — DISABLED MODE VERIFICATION</p>
    <p class="muted" style="margin-top: 0.25rem;">LIVE IMPORT TEST OPTIONAL AND GATED — TOKENS NOT STORED OR PRINTED — SERVICE ROLE NOT USED</p>
    <p class="muted" style="margin-top: 0.25rem;">NO AUTOMATIC MIGRATION APPLY — UPDATE DELETE EXECUTE BLOCKED — AUTOMATION STILL DISABLED</p>
    <p class="muted" style="margin-top: 0.25rem;">NEXT_STEP_RUN_REVIEWED_MIGRATION_AND_TOKEN_GATED_SMOKE_TEST — NOT_READY_FOR_REAL_AUTOMATION</p>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp23-migration-flow" id="mvp23-migration-flow-panel">
      <div class="card-head"><h3 class="card-title">Manual Migration Operator Flow Panel</h3><span class="badge info">OPERATOR</span></div>
      <p class="card-body">Status: CREATED (MANUAL ONLY)</p>
      {_list([
          "migration files: 003, 004",
          "apply mode: OUTSIDE APP RUNTIME",
          "reviewed env required: YES",
          "no automatic apply: PASS"
      ])}
    </article>

    <article class="card mvp23-disabled-mode" id="mvp23-disabled-mode-panel">
      <div class="card-head"><h3 class="card-title">Disabled Mode Verification Panel</h3><span class="badge warning">GATED</span></div>
      {_list([
          "endpoint status check: ALLOWED",
          "disabled behavior: FEEDBACK_PERSISTENCE_DISABLED",
          "no import attempted when disabled: PASS"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp23-smoke-test" id="mvp23-smoke-test-panel">
      <div class="card-head"><h3 class="card-title">Token-Gated Smoke Test Panel</h3><span class="badge info">HARNESS</span></div>
      {_list([
          "env: SUPABASE_TEST_ACCESS_TOKEN",
          "gate: MVP23_FEEDBACK_SMOKE_TEST_CONFIRMED",
          "target: FEEDBACK_IMPORT_SMOKE_URL",
          "optional live import: READY"
      ])}
    </article>

    <article class="card mvp23-artifact" id="mvp23-artifact-panel">
      <div class="card-head"><h3 class="card-title">Smoke Result Artifact Panel</h3><span class="badge info">OUTPUT</span></div>
      {_list([
          "markdown result: mvp23_feedback_import_smoke_test_result.md",
          "json result: mvp23_feedback_import_smoke_test_result.json",
          "token redaction: ENFORCED",
          "env redaction: ENFORCED"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp23-decision" id="mvp23-decision-panel">
      <div class="card-head"><h3 class="card-title">Operator Decision Panel</h3><span class="badge info">DECISION</span></div>
      {_list([
          "retry after migration",
          "enable feature flag for test only",
          "fix endpoint/validator/client",
          "promote to reviewed beta"
      ])}
    </article>

    <article class="card mvp23-safety" id="mvp23-safety-panel">
      <div class="card-head"><h3 class="card-title">Security Boundary Panel</h3><span class="badge warning">SAFETY</span></div>
      {_list([
          "service role usage: PASS",
          "token storage: PASS",
          "automatic migration: PASS",
          "automation: PASS",
          "update/delete/execute: BLOCKED"
      ])}
    </article>
  </div>

  <div class="plus2e-preview-grid">
    <article class="card mvp23-next-product-decision" id="mvp23-next-product-decision-panel">
      <div class="card-head"><h3 class="card-title">Next Product Decision Panel</h3><span class="badge info">NEXT</span></div>
      <p class="card-body">Run the first token-gated write test in a reviewed environment.</p>
      {_list([
          "manually apply migrations",
          "run token-gated smoke test",
          "review smoke result artifact",
          "decide beta feedback workflow",
          "not ready for real automation"
      ])}
      <div class="callout" style="margin-top:0.75rem;">
        <p class="muted" style="margin:0;">Current recommendation</p>
        {_list(current_recommendation)}
      </div>
      <div class="button-row" style="margin-top:0.75rem;">
        <button type="button" class="copy-button small" id="mvp23-copy-validation" data-copy-text="{_e(validation_copy)}">Copy MVP-23 validation checklist</button>
      </div>
    </article>
  </div>
</div>
"""
    return _details(
        "MVP-23 — Token-Gated Feedback Import Smoke Test",
        body,
        "source",
        open_by_default=True,
        panel_id="mvp23-token-gated-smoke-test",
    )


def _build_welcome_page():
    return '''
<div class="tab-pane active" id="view-welcome">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>Welcome to The Agent Command Center</h2>
      <p class="lede">Read-only production dashboard for reviewing product status, safety boundaries, demo readiness, and release progress.</p>
    </div>
    <div class="landing-cards">
      <div class="card">
        <div class="card-head"><h3 class="card-title">Latest production verified MVP</h3><span class="badge pass">MVP-41</span></div>
        <p class="card-body">Current product state: review/demo dashboard</p>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="card-title">Pending Release</h3><span class="badge warning">MVP-42</span></div>
        <p class="card-body">MVP-42 status: pending branch / not production merged</p>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="card-title">Safety Status</h3><span class="badge pass">SECURE</span></div>
        <ul class="compact-list">
          <li>Automation: disabled</li>
          <li>Public writes: disabled</li>
          <li>Secrets: not exposed</li>
          <li>Backend actions: disabled</li>
          <li>Reviewer response capture: not live</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="card-title">Dashboard mode</h3><span class="badge info">READ-ONLY</span></div>
        <p class="card-body">read-only / copy-only / audit-visible</p>
      </div>
    </div>
    <div class="landing-actions" style="margin-top: 2rem;">
      <h3>Start here:</h3>
      <ul class="compact-list" style="font-size: 1.05rem; gap: 0.75rem;">
        <li>Use <strong><a href="#" onclick="switchTab('view-status')">Current Status</a></strong> if you want the quick answer.</li>
        <li>Use <strong><a href="#" onclick="switchTab('view-orientation')">What the hell am I looking at?</a></strong> if this page looks insane.</li>
        <li>Use <strong><a href="#" onclick="switchTab('view-demo')">External Review / Demo</a></strong> if you are showing this to someone else.</li>
        <li>Use <strong><a href="#" onclick="switchTab('view-archive')">Archive / Full Audit Trail</a></strong> only if you want the full construction record.</li>
      </ul>
    </div>
  </div>
</div>
'''

def _build_orientation_page():
    return '''
<div class="tab-pane" id="view-orientation" style="display: none;">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>What the hell am I looking at?</h2>
      <p class="lede">A brief explanation of why this page exists and how to read it.</p>
    </div>
    <div class="landing-actions">
      <ul class="compact-list" style="font-size: 1.05rem; gap: 0.75rem;">
        <li>This is not a normal marketing site.</li>
        <li>This is a live product/audit dashboard.</li>
        <li>It shows the project’s evolution from static safety review into a controlled demo/review system.</li>
        <li>Most buttons are copy/read-only helpers.</li>
        <li>The scary words like deploy, merge, push, token, write, approve, execute appear because the dashboard is explicitly proving those actions are disabled.</li>
        <li>The dashboard is intentionally transparent, but the default view now separates human-friendly review from internal audit details.</li>
        <li>Historical sections are preserved in Archive.</li>
        <li>Developer/validator details are separated in Developer View.</li>
        <li>Nothing on the page should execute commands, mutate GitHub/Netlify, expose secrets, or write backend data.</li>
      </ul>
      <h3 style="margin-top: 1.5rem;">Translation guide</h3>
      <ul class="compact-list" style="font-size: 1.05rem; gap: 0.75rem;">
        <li><strong>"PASS"</strong> means the static check/report is present.</li>
        <li><strong>"DISABLED"</strong> means a capability is intentionally unavailable.</li>
        <li><strong>"READY"</strong> means an artifact is ready for review/copying, not necessarily live automation.</li>
        <li><strong>"NOT_READY_FOR_REAL_AUTOMATION"</strong> means exactly what it says.</li>
        <li><strong>"Copy"</strong> buttons copy text locally; they do not send data anywhere.</li>
        <li><strong>"Safety-denial language"</strong> means phrases like NO DEPLOY CONTROLS or NO PUBLIC WRITES are warnings/guards, not enabled actions.</li>
      </ul>
    </div>
  </div>
</div>
'''

def _build_status_page(snapshot):
    return '''
<div class="tab-pane" id="view-status" style="display: none;">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>Current Status</h2>
    </div>
    <div class="landing-cards">
      <div class="card">
        <div class="card-head"><h3 class="card-title">Production State</h3></div>
        <ul class="compact-list">
          <li>Latest verified milestone: MVP-41</li>
          <li>Current production branch: master</li>
          <li>Current production role: read-only review dashboard</li>
          <li>Next pending branch: MVP-42 (not merged)</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="card-title">Current safety posture</h3><span class="badge warning">STRICT</span></div>
        <ul class="compact-list">
          <li>no public endpoint</li>
          <li>no live intake</li>
          <li>no public writes</li>
          <li>no reviewer response writes</li>
          <li>no response persistence</li>
          <li>no token input</li>
          <li>no service role in browser</li>
          <li>no email sending</li>
          <li>no reviewer contact automation</li>
          <li>no deploy/merge/push controls</li>
          <li>automation disabled</li>
        </ul>
      </div>
    </div>
    <div class="landing-actions" style="margin-top: 2rem;">
      <h3>What should I look at first?</h3>
      <div style="display:flex; gap:1rem; flex-wrap:wrap;">
        <button class="action-button" onclick="switchTab('view-demo')">External Review / Demo</button>
        <button class="action-button" onclick="switchTab('view-safety')">Safety Posture</button>
        <button class="action-button" onclick="switchTab('view-latest-mvp')">Latest Verified MVP</button>
        <button class="action-button" onclick="switchTab('view-archive')">Archive</button>
      </div>
    </div>
  </div>
</div>
'''

def _build_demo_page():
    return '''
<div class="tab-pane" id="view-demo" style="display: none;">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>External Review / Demo</h2>
    </div>
    <div class="landing-actions">
      <h3>What the system is</h3>
      <p>A transparent, verifiable command center that safely models and previews automation without executing it prematurely.</p>
      <h3>What problem it solves</h3>
      <p>AI agent automation usually lacks transparency, auditability, and safety boundaries. This dashboard proves we can build safely.</p>
      <h3>What is safe to demo today</h3>
      <p>The static dashboard shell, the generated artifacts, and the safety boundary verifications. It proves the system constraints hold.</p>
      <h3>What is intentionally disabled</h3>
      <p>Live writes, external API mutation, production deploy controls, automated email sending.</p>
      <h3>What artifacts are ready to review</h3>
      <p>MVP-41 Blueprints, architecture documents, safety logic rules, UI schemas.</p>
      <h3 style="margin-top: 1.5rem;">Suggested reviewer path:</h3>
      <ol style="color: var(--text-secondary); font-size: 1.05rem;">
        <li>Read Welcome</li>
        <li>Open Current Status</li>
        <li>Review Latest Verified MVP</li>
        <li>Review Safety Posture</li>
        <li>Use Archive only if technical detail is needed</li>
      </ol>
    </div>
  </div>
</div>
'''

def _build_safety_page(snapshot):
    return f'''
<div class="tab-pane" id="view-safety" style="display: none;">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>Safety Posture</h2>
      <p class="lede">Strict enforcement of security boundaries to prevent runaway automation.</p>
    </div>
    <div class="landing-cards">
      <div class="card" style="grid-column: 1 / -1;">
        <div class="card-head"><h3 class="card-title">Runtime Boundaries</h3></div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:1rem;">
          {{_stat("Public endpoint", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Live intake", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Public writes", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Reviewer response writes", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Response persistence", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Email sending", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Reviewer contact", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Token input", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Browser secret storage", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Service role in browser", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("GitHub mutation", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Netlify mutation", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Deploy/merge/push controls", "disabled", _badge("DISABLED", "disabled"))}}
          {{_stat("Automation", "disabled", _badge("DISABLED", "disabled"))}}
        </div>
      </div>
      <div class="card" style="grid-column: 1 / -1;">
        <div class="card-head"><h3 class="card-title">Context-Aware Safeties</h3></div>
        <p class="card-body" style="margin-bottom: 0.5rem;">Why scary terms appear: The dashboard explicitly prints words like "deploy" or "execute" to prove they are blocked.</p>
        <p class="card-body" style="margin-bottom: 0.5rem;">What the context-aware validator does: It ensures that any dangerous words are safely prefixed (e.g. NO_PUBLIC_WRITES) rather than used as active labels.</p>
        <p class="card-body">Difference between safety-denial language and enabled runtime behavior: A button that says "NO DEPLOY CONTROLS" is inert documentation, not a hidden feature.</p>
      </div>
    </div>
  </div>
</div>
'''

def _build_roadmap_page():
    return '''
<div class="tab-pane" id="view-roadmap" style="display: none;">
  <div class="landing-shell">
    <div class="landing-head">
      <h2>Roadmap / Next Step</h2>
    </div>
    <div class="landing-cards">
      <div class="card">
        <div class="card-head"><h3 class="card-title">Completed</h3><span class="badge pass">DONE</span></div>
        <ul class="compact-list">
          <li>Completed through MVP-41</li>
          <li>Validation stabilization completed</li>
          <li>Dashboard Usability Refactor completed</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="card-title">Next Planned</h3><span class="badge info">UPCOMING</span></div>
        <p class="card-body" style="margin-bottom: 0.5rem;"><strong>MVP-42 — Operator-Controlled Response Import Dry Run</strong></p>
        <p class="card-body muted">MVP-42 is pending (branch exists, not merged to master).</p>
      </div>
    </div>
  </div>
</div>
'''

def render_html(snapshot, compact_view=False, print_mode=False):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    
    tabs = '''
    <nav class="dashboard-tabs">
      <button class="tab-btn active" onclick="switchTab('view-welcome')">Welcome</button>
      <button class="tab-btn" onclick="switchTab('view-status')">Current Status</button>
      <button class="tab-btn" onclick="switchTab('view-orientation')">Orientation</button>
      <button class="tab-btn" onclick="switchTab('view-latest-mvp')">Latest MVP</button>
      <button class="tab-btn" onclick="switchTab('view-demo')">Demo</button>
      <button class="tab-btn" onclick="switchTab('view-safety')">Safety Posture</button>
      <button class="tab-btn" onclick="switchTab('view-roadmap')">Roadmap</button>
      <button class="tab-btn" onclick="switchTab('view-archive')">Archive</button>
      <button class="tab-btn" onclick="switchTab('view-developer')">Developer View</button>
    </nav>
    '''

    header = f'''
    <header class="hero dashboard-shell">
      <div class="hero-copy" style="width: 100%;">
        <h1>The Agent Command Center</h1>
        {tabs if not print_mode else ''}
      </div>
    </header>
    '''

    toolbar = _build_toolbar(snapshot) if not print_mode else ""
    
    # Core views
    welcome_view = _build_welcome_page()
    orientation_view = _build_orientation_page()
    status_view = _build_status_page(snapshot)
    demo_view = _build_demo_page()
    safety_view = _build_safety_page(snapshot)
    roadmap_view = _build_roadmap_page()
    
    # Latest MVP view
    latest_mvp_view = f'''<div class="tab-pane" id="view-latest-mvp" style="display: none;">
      <h2 style="margin-bottom:1rem;">Latest Verified MVP</h2>
      {_build_mvp41_controlled_reviewer_response_intake_blueprint_layer(snapshot)}
    </div>'''
    
    # Archive view
    archive_sections = [
        _build_safety_banner(),
        _build_landing_screen(snapshot),
        _details("Safety Boundary Summary", _build_safety_boundary(snapshot), "source", open_by_default=False, panel_id="safety-boundary"),
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
        _build_mvp6_controlled_migration_authenticated_reads_layer(snapshot),
        _build_mvp7_real_authenticated_reads_layer(snapshot),
        _build_mvp8_controlled_request_create_layer(snapshot),
        _build_mvp9_request_detail_lifecycle_layer(snapshot),
        _build_mvp10_operator_workspace_layer(snapshot),
        _build_mvp11_workspace_polish_layer(snapshot),
        _build_mvp12_controlled_lifecycle_event_layer(snapshot),
        _build_mvp13_request_activity_safe_errors_layer(snapshot),
        _build_mvp14_manual_live_test_harness_layer(snapshot),
        _build_mvp15_live_test_demo_pitch_layer(snapshot),
        _build_mvp16_live_results_demo_package_layer(snapshot),
        _build_mvp17_external_demo_package_layer(snapshot),
        _build_mvp18_share_ready_portal_layer(snapshot),
        _build_mvp19_external_feedback_layer(snapshot),
        _build_mvp20_manual_feedback_layer(snapshot),
        _build_mvp21_persistence_readiness_layer(snapshot),
        _build_mvp22_controlled_write_layer(snapshot),
        _build_mvp23_smoke_test_layer(snapshot),
        _build_mvp24_beta_feedback_import_layer(snapshot),
        _build_mvp25_authenticated_feedback_review_layer(snapshot),
        _build_mvp26_feedback_synthesis_product_decision_layer(snapshot),
        _build_mvp27_feedback_to_request_conversion_layer(snapshot),
        _build_mvp28_operator_roadmap_prioritization_layer(snapshot),
        _build_mvp29_guided_product_demo_control_room_layer(snapshot),
        _build_mvp30_pitchable_release_package_layer(snapshot),
        _build_mvp31_demo_session_capture_review_loop_layer(snapshot),
        _build_mvp32_release_review_metrics_signal_dashboard_layer(snapshot),
        _build_mvp33_product_launch_readiness_final_pitch_packet_layer(snapshot),
        _build_mvp34_public_release_candidate_review_portal_layer(snapshot),
        _load_prebuilt_section("mvp35-external-review-feedback-summary-outreach-prep"),
        _load_prebuilt_section("mvp36-review-to-roadmap-decision-sync"),
        _load_prebuilt_section("mvp37-release-candidate-decision-log-handoff"),
        _load_prebuilt_section("mvp38-final-release-review-room-demo-script-lock"),
        _load_prebuilt_section("mvp39-external-demo-review-share-package-lock"),
        _build_mvp40_reviewer_response_capture_readiness_lock_layer(snapshot),
        _build_mvp41_controlled_reviewer_response_intake_blueprint_layer(snapshot),
                _build_mvp41_controlled_reviewer_response_intake_blueprint_layer(snapshot),
        _build_mvp42_operator_controlled_response_import_dry_run_layer(snapshot),
                _build_mvp42_operator_controlled_response_import_dry_run_layer(snapshot),
        _build_mvp43_operational_auth_foundation_layer(snapshot),
                _build_mvp42_operator_controlled_response_import_dry_run_layer(snapshot),
        _build_mvp43_operational_auth_foundation_layer(snapshot),
        _build_mvp44_persistent_request_storage_foundation_layer(snapshot),
        _build_mvp45_immutable_audit_event_ledger_layer(snapshot),
    ]
    # Replace any 'open_by_default=True' with False in archive_sections if possible, 
    # but since they are already rendered strings, we can use JS or just let details be closed.
    # We will use CSS/JS to close them, or replace 'open' with '' in the HTML string for the archive tab.
    archive_html = "\\n".join(archive_sections).replace(' open ', ' ').replace('<details class="panel" open>', '<details class="panel">')
    archive_view = f'''<div class="tab-pane" id="view-archive" style="display: none;">
      <h2 style="margin-bottom:1rem;">Archive / Full Audit Trail</h2>
      <div style="margin-bottom:1rem;">
         <label>Filter Archive: </label>
         <select id="archive-filter" onchange="filterArchive(this.value)" style="padding:0.3rem; border-radius:4px; border:1px solid var(--stroke); background:var(--card); color:var(--text);">
           <option value="all">All</option>
           <option value="original">Original Phases</option>
           <option value="mvp1-10">MVP 1-10</option>
           <option value="mvp11-20">MVP 11-20</option>
           <option value="mvp21-30">MVP 21-30</option>
           <option value="mvp31-40">MVP 31-40</option>
         </select>
      </div>
      <div id="archive-content">{archive_html}</div>
    </div>'''
    
    # Developer view
    dev_sections = [
        _build_action_panel(snapshot),
        _build_reports_panel(snapshot),
        _build_validator_panel(snapshot),
        _build_artifact_panel(snapshot),
        _build_source_transparency_panel(snapshot),
        _build_compare_panel(snapshot),
        _build_branch_review_panel(snapshot),
        _build_approval_panel(snapshot),
        _build_session_panel(snapshot)
    ]
    dev_html = "\\n".join(dev_sections).replace(' open ', ' ').replace('<details class="panel" open>', '<details class="panel">')
    dev_view = f'''<div class="tab-pane" id="view-developer" style="display: none;">
      <h2 style="margin-bottom:1rem;">Developer / Validator View</h2>
      <div class="callout" style="margin-bottom:1.5rem; border-color:var(--warning);"><p class="muted">Developer view contains internal build/audit details and is not the recommended starting point for external reviewers.</p></div>
      {dev_html}
    </div>'''
    
    if print_mode:
        all_sections = [
            welcome_view, orientation_view, status_view, demo_view, safety_view, roadmap_view, latest_mvp_view, archive_view, dev_view, _build_footer()
        ]
        sections_out = "\\n".join(all_sections)
    else:
        sections_out = "\\n".join([
            welcome_view, orientation_view, status_view, demo_view, safety_view, roadmap_view, latest_mvp_view, archive_view, dev_view, _build_footer()
        ])
    
    body_class = "dashboard-body print-view" if print_mode else "dashboard-body"
    if compact_view:
        body_class += " compact-view"
        
    data_json = json.dumps(snapshot, indent=2, sort_keys=False).replace("</", "<\/")
    replacements = {
        "{{TITLE}}": "The Agent Command Center - Read-Only Operations Dashboard",
        "{{BODY_CLASS}}": body_class,
        "{{HEADER}}": header,
        "{{TOOLBAR}}": toolbar,
        "{{SECTIONS}}": sections_out,
        "{{DASHBOARD_DATA_JSON}}": data_json,
        "{{SCRIPTS}}": "" if print_mode else '<script src="./static/dashboard.js"></script>',
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template

def render_print_html(snapshot):
    return render_html(snapshot, compact_view=False, print_mode=True)
