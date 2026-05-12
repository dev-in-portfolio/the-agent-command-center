#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "13_web_dashboard"
DIST_DIR = DASHBOARD_DIR / "dist"
REPORTS_DIR = ROOT / "09_exports" / "interface_phase_3"
PHASE1_DIR = ROOT / "11_interface"
PHASE2_DIR = ROOT / "12_tui"
RUNTIME_DIR = ROOT / "10_runtime"

REQUIRED_PHASE3_FILES = [
    DASHBOARD_DIR / "README.md",
    DASHBOARD_DIR / "build_phase3_dashboard.py",
    DASHBOARD_DIR / "dashboard_data.py",
    DASHBOARD_DIR / "dashboard_renderer.py",
    DASHBOARD_DIR / "dashboard_safety.py",
    DASHBOARD_DIR / "dashboard_schema.py",
    DASHBOARD_DIR / "templates" / "index_template.html",
    DASHBOARD_DIR / "static" / "dashboard.css",
    DASHBOARD_DIR / "static" / "dashboard.js",
    DASHBOARD_DIR / "dist" / "index.html",
    DASHBOARD_DIR / "dist" / "dashboard_data.json",
    DASHBOARD_DIR / "dist" / "print.html",
    DASHBOARD_DIR / "dist" / "static" / "dashboard.css",
    DASHBOARD_DIR / "dist" / "static" / "dashboard.js",
]

REQUIRED_REPORTS = [
    REPORTS_DIR / "interface_phase_3_acceptance_report.md",
    REPORTS_DIR / "interface_phase_3_operator_quickstart.md",
    REPORTS_DIR / "interface_phase_3_dashboard_map.md",
    REPORTS_DIR / "interface_phase_3_backend_reuse_report.md",
    REPORTS_DIR / "interface_phase_3_safety_report.md",
    REPORTS_DIR / "interface_phase_3_generated_artifact_hygiene_report.md",
    REPORTS_DIR / "interface_phase_3_static_build_report.md",
    REPORTS_DIR / "interface_phase_3_phase_4_handoff_contract.md",
    REPORTS_DIR / "snapshot_schema_contract.md",
    REPORTS_DIR / "interface_phase_3_final_acceptance_report.md",
    REPORTS_DIR / "interface_phase_3_release_candidate_report.md",
    REPORTS_DIR / "interface_phase_3_final_diff_audit.md",
    REPORTS_DIR / "interface_phase_3_clean_checkout_checklist.md",
    REPORTS_DIR / "interface_phase_3_operator_command_card.md",
    REPORTS_DIR / "interface_phase_3_visual_qa_report.md",
    REPORTS_DIR / "merge_readiness" / "interface_phase_3_merge_readiness_packet.md",
]


def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _run(cmd, expected_rc=0):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != expected_rc:
        raise RuntimeError(f"command failed: {' '.join(cmd)} rc={result.returncode}\n{result.stderr}")
    return result


def _read_text(path):
    return path.read_text(encoding="utf-8")


def _require_no_modified_paths(*prefixes):
    result = subprocess.run(["git", "diff", "--name-only", "--", *prefixes], capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if changed:
        raise RuntimeError("unexpected modified paths: " + ", ".join(changed))


def _validate_snapshot_json(payload):
    required_fields = [
        "dashboard_id",
        "created_at_utc",
        "phase",
        "repo",
        "source_lineage",
        "mode",
        "phase_1_status",
        "phase_2_status",
        "phase_3_status",
        "safety_status",
        "boundary_status",
        "action_registry_summary",
        "artifact_summary",
        "approval_ledger_summary",
        "branch_review_summary",
        "session_summary",
        "validator_status",
        "document_index",
        "data_freshness",
        "source_transparency",
        "recommended_next_action",
    ]
    for field in required_fields:
        if field not in payload:
            raise RuntimeError(f"snapshot missing field: {field}")
    if payload["phase"] != "Read-Only Operations Dashboard":
        raise RuntimeError("snapshot phase mismatch")
    if payload["repo"] != "dev-in-portfolio/the-agent-command-center":
        raise RuntimeError("snapshot repo mismatch")
    if payload["mode"] != "static_local_dashboard":
        raise RuntimeError("snapshot mode mismatch")
    if not payload.get("document_index", {}).get("documents"):
        raise RuntimeError("document_index missing documents")
    if not payload.get("data_freshness", {}):
        raise RuntimeError("data_freshness missing")
    if not payload.get("source_transparency", {}).get("sections"):
        raise RuntimeError("source_transparency missing sections")
    boundary = payload.get("boundary_status", {})
    for key in [
        "official_repo_touched",
        "repo_2_touched",
        "repo_3_touched",
        "deployment_performed",
        "secrets_credentials_used",
        "command_packets_executed",
        "merge_performed",
        "push_performed",
        "pr_created",
        "network_used",
    ]:
        if boundary.get(key) is not False:
            raise RuntimeError(f"boundary {key} must be false")


def _validate_html_and_assets():
    html = _read_text(DIST_DIR / "index.html")
    for needle in [
        "The Agent Command Center",
        "READ-ONLY DASHBOARD",
        "BACKEND ACTIONS DISABLED",
        "NO COMMAND EXECUTION",
        "NO DEPLOY CONTROLS",
        "NO MERGE CONTROLS",
        "NO SECRET ACCESS",
        "Action Registry",
        "Artifact Deep Dive",
        "Reports Library",
        "Validator Command Center",
        "Data Freshness",
        "Source Transparency",
        "Compare Phases",
        "Branch Review",
        "Approval Ledger",
        "Safety Boundary",
        "skip-link",
        "dashboard-data",
        "landing-shell",
        "section-button",
        "dashboard-shell",
    ]:
        if needle not in html:
            raise RuntimeError(f"dashboard HTML missing {needle}")
    if "http://" in html or "https://" in html:
        raise RuntimeError("HTML contains external URLs")
    for needle in ["fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "analytics"]:
        if needle in html:
            raise RuntimeError(f"HTML contains forbidden token: {needle}")
    if "./static/dashboard.css" not in html or "./static/dashboard.js" not in html:
        raise RuntimeError("dashboard HTML missing self-contained dist asset links")
    if "../static/" in html:
        raise RuntimeError("dashboard HTML still references parent static assets")
    for needle in [
        '<details class="panel" data-section-group="registry" id="action-registry">',
        '<details class="panel" data-section-group="registry" id="artifact-packages">',
        '<details class="panel" data-section-group="reports" id="reports-library">',
        '<details class="panel" data-section-group="audit" id="validator-command-center">',
        '<details class="panel" data-section-group="source" id="source-transparency">',
    ]:
        if needle not in html:
            raise RuntimeError(f"collapsed section markup missing {needle}")

    css = _read_text(DIST_DIR / "static" / "dashboard.css")
    for needle in [
        "font-family",
        "body",
        ".dashboard-shell",
        ".summary-card",
        ".panel",
        ".badge",
        ".table-wrap",
        "@media",
        "@media print",
    ]:
        if needle not in css:
            raise RuntimeError(f"CSS missing {needle}")

    # Allow same-origin backend fetches
    allowed_fetches = ['fetch("/api/health")', "fetch('/api/health')", 'fetch("/api/status")', "fetch('/api/status')", 'fetch("/api/backend-manifest")', "fetch('/api/backend-manifest')"]
    
    js = _read_text(DIST_DIR / "static" / "dashboard.js")
    for line in js.splitlines():
        if "fetch(" in line:
            if not any(f in line for f in allowed_fetches):
                raise RuntimeError(f"JavaScript contains forbidden token: {line.strip()}")
    
    for needle in ["XMLHttpRequest", "WebSocket", "EventSource", "eval(", "Function(", "import(", "navigator.sendBeacon", "document.cookie", "localStorage", "sessionStorage"]:
        if needle in js:
            raise RuntimeError(f"JavaScript contains forbidden token: {needle}")


def _validate_scanner():
    sys.path.insert(0, str(DASHBOARD_DIR))
    from dashboard_safety import scan_phase3_safety

    result = scan_phase3_safety(DASHBOARD_DIR)
    if result["status"] == "FAIL":
        raise RuntimeError("dashboard safety scanner returned FAIL")
    if not result["files_scanned"]:
        raise RuntimeError("safety scanner did not scan any files")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        allowed = temp_dir / "allowed.py"
        forbidden = temp_dir / "forbidden.py"
        allowed.write_text('MESSAGE = "Deployment: DISABLED"\n', encoding="utf-8")
        forbidden.write_text('import os\nos.environ["TOKEN"] = "bad"\n', encoding="utf-8")
        allowed_result = scan_phase3_safety(files=[allowed])
        if allowed_result["status"] == "FAIL":
            raise RuntimeError("safety scanner false-failed on allowed safety text")
        forbidden_result = scan_phase3_safety(files=[forbidden])
        if forbidden_result["status"] != "FAIL":
            raise RuntimeError("safety scanner did not fail on active forbidden sample")


def _validate_generated_artifact_hygiene_docs():
    gitignore = _read_text(ROOT / ".gitignore")
    for needle in [
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.json",
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.md",
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.txt",
        "09_exports/interface_phase_3/test_runs/",
    ]:
        if needle not in gitignore:
            raise RuntimeError(f".gitignore missing hygiene rule: {needle}")

    hygiene_report = _read_text(REPORTS_DIR / "interface_phase_3_generated_artifact_hygiene_report.md")
    for needle in [
        "Read-Only Operations Dashboard Generated Artifact Hygiene Report",
        "PASS_WITH_HIGH_CONFIDENCE",
        "Generated Artifact Hygiene",
    ]:
        if needle not in hygiene_report:
            raise RuntimeError(f"hygiene report missing {needle}")

    merge_packet = _read_text(REPORTS_DIR / "merge_readiness" / "interface_phase_3_merge_readiness_packet.md")
    if "Generated Artifact Hygiene" not in merge_packet:
        raise RuntimeError("merge readiness packet missing generated artifact hygiene section")

    operator_card = _read_text(REPORTS_DIR / "interface_phase_3_operator_command_card.md")
    if "127.0.0.1:8080" not in operator_card:
        raise RuntimeError("operator command card missing preview URL")
    if "cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1" not in operator_card:
        raise RuntimeError("operator command card missing preview command")

    quickstart = _read_text(REPORTS_DIR / "interface_phase_3_operator_quickstart.md")
    if "127.0.0.1:8080" not in quickstart:
        raise RuntimeError("operator quickstart missing preview URL")

    readme = _read_text(DASHBOARD_DIR / "README.md")
    if "127.0.0.1:8080" not in readme:
        raise RuntimeError("README missing preview URL")
    if "cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1" not in readme:
        raise RuntimeError("README missing preview command")

    visual_qa = _read_text(REPORTS_DIR / "interface_phase_3_visual_qa_report.md")
    for needle in [
        "CSS loaded from dist/static/dashboard.css",
        "JS loaded from dist/static/dashboard.js",
        "dist/index.html self-contained relative asset paths",
        "http://127.0.0.1:8080",
        "PASS_WITH_HIGH_CONFIDENCE",
    ]:
        if needle not in visual_qa:
            raise RuntimeError(f"visual QA report missing {needle}")


def _validate_build_report():
    report = _read_text(REPORTS_DIR / "interface_phase_3_static_build_report.md")
    for needle in [
        "Validation status: PASS",
        "Output path: 13_web_dashboard/dist/index.html",
        "Print path: 13_web_dashboard/dist/print.html",
        "Dashboard data export: 13_web_dashboard/dist/dashboard_data.json",
    ]:
        if needle not in report:
            raise RuntimeError(f"build report missing {needle}")


def _validate_source_code_patterns():
    phase3_python_files = [
        DASHBOARD_DIR / "build_phase3_dashboard.py",
        DASHBOARD_DIR / "dashboard_data.py",
        DASHBOARD_DIR / "dashboard_renderer.py",
        DASHBOARD_DIR / "dashboard_schema.py",
        DASHBOARD_DIR / "dashboard_safety.py",
    ]
    forbidden = [
        "os.environ",
        "shell=True",
        "requests",
        "urllib",
        "http.client",
        "socket",
        "git push",
        "git merge",
        "gh pr",
        "curl",
        "wget",
        "ssh",
        "scp",
    ]
    for path in phase3_python_files:
        text = _read_text(path)
        for needle in forbidden:
            if needle in text:
                raise RuntimeError(f"forbidden pattern {needle} found in {path.relative_to(ROOT)}")


def main():
    for path in REQUIRED_PHASE3_FILES + REQUIRED_REPORTS:
        if not path.exists():
            return _fail(f"missing required file: {path.relative_to(ROOT)}")

    try:
        validate_only = _run([sys.executable, str(DASHBOARD_DIR / "build_phase3_dashboard.py"), "--validate-only"])
        if validate_only.returncode != 0 or "VALIDATION_PASS" not in validate_only.stdout:
            return _fail("validate-only command failed")
        help_result = _run([sys.executable, str(DASHBOARD_DIR / "build_phase3_dashboard.py"), "--help"])
        if "Read-Only Operations Dashboard" not in help_result.stdout:
            return _fail("help output missing Read-Only Operations Dashboard")
        snapshot_result = _run([sys.executable, str(DASHBOARD_DIR / "build_phase3_dashboard.py"), "--snapshot-json"])
        payload = json.loads(snapshot_result.stdout)
        _validate_snapshot_json(payload)
        _validate_html_and_assets()
        _validate_scanner()
        _validate_build_report()
        _validate_generated_artifact_hygiene_docs()
        _validate_source_code_patterns()

        for path in [
            PHASE1_DIR / "interface_action_registry.py",
            PHASE1_DIR / "interface_policy_enforcer.py",
            PHASE1_DIR / "interface_artifact_inspector.py",
            PHASE1_DIR / "interface_branch_review.py",
            PHASE1_DIR / "interface_approval_ledger.py",
            PHASE1_DIR / "interface_session_log.py",
            PHASE2_DIR / "tui_state.py",
            PHASE2_DIR / "tui_renderer.py",
            PHASE2_DIR / "tui_screens.py",
            PHASE2_DIR / "tui_keymap.py",
            PHASE2_DIR / "tui_safe_actions.py",
            PHASE2_DIR / "tui_safety_scanner.py",
        ]:
            if not path.exists():
                return _fail(f"missing backend module: {path.relative_to(ROOT)}")

        _require_no_modified_paths("11_interface", "12_tui", "10_runtime")

    except Exception as exc:
        return _fail(str(exc))

    print("INTERFACE_PHASE_3_DASHBOARD_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
