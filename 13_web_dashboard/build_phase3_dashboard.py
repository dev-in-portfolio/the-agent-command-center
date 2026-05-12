#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "13_web_dashboard"
DIST_DIR = DASHBOARD_DIR / "dist"
REPORTS_DIR = ROOT / "09_exports" / "interface_phase_3"
SNAPSHOT_DIR = REPORTS_DIR / "snapshots"

sys.path.insert(0, str(DASHBOARD_DIR))

from dashboard_data import build_dashboard_snapshot
from dashboard_renderer import render_html, render_print_html
from dashboard_schema import validate_snapshot
from dashboard_safety import scan_phase3_safety


def _emit_error(message):
    print(f"ERROR: {message}", file=sys.stderr)


def _timestamp():
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}-{uuid4().hex[:8]}"


def _write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_build_report(snapshot, validation_result, safety_result):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "interface_phase_3_static_build_report.md"
    lines = [
        "# Interface Phase 3 Static Build Report",
        "",
        f"- Dashboard ID: {snapshot['dashboard_id']}",
        f"- Created at UTC: {snapshot['created_at_utc']}",
        f"- Repo: {snapshot['repo']}",
        f"- Source lineage: {snapshot['source_lineage']}",
        f"- Mode: {snapshot['mode']}",
        f"- Validation status: {validation_result['status']}",
        f"- Validation errors: {len(validation_result['errors'])}",
        f"- Safety scan status: {safety_result['status']}",
        f"- Output path: 13_web_dashboard/dist/index.html",
        f"- Print path: 13_web_dashboard/dist/print.html",
        f"- Dashboard data export: 13_web_dashboard/dist/dashboard_data.json",
        f"- Dist CSS path: 13_web_dashboard/dist/static/dashboard.css",
        f"- Dist JS path: 13_web_dashboard/dist/static/dashboard.js",
        f"- Snapshot schema contract: 09_exports/interface_phase_3/snapshot_schema_contract.md",
        "",
        "## Build Inputs",
        "- Phase 1 backend modules were read only.",
        "- Phase 2 reference docs were read only.",
        "- No application/API backend server is included in Phase 3.",
        "- No outbound API calls, remote data fetching, analytics, tracking, or live backend connections are included in Phase 3.",
        "- No secrets or credentials were accessed.",
        "- No command packets were executed.",
        "- Built HTML references only relative dist/static assets.",
        "",
        "## Generated Artifact Policy",
        "- Intentionally tracked: 13_web_dashboard/dist/index.html",
        "- Intentionally tracked: 13_web_dashboard/dist/print.html",
        "- Intentionally tracked: 13_web_dashboard/dist/dashboard_data.json",
        "- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.css",
        "- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.js",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.json",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.md",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.txt",
        "- Ignored going forward: 09_exports/interface_phase_3/test_runs/",
        "",
        "## Snapshot / Export Modes",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot` defaults to JSON when no snapshot mode is given.",
    ]
    _write_text(report_path, "\n".join(lines))
    return report_path


def _write_snapshot_export(mode_name, content):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _timestamp()
    ext_map = {
        "json": "json",
        "markdown": "md",
        "summary": "txt",
        "full": "txt",
    }
    ext = ext_map[mode_name]
    suffix = f"_{mode_name}" if mode_name in {"summary", "full"} else ""
    path = SNAPSHOT_DIR / f"dashboard_snapshot_{timestamp}{suffix}.{ext}"
    counter = 1
    while path.exists():
        path = SNAPSHOT_DIR / f"dashboard_snapshot_{timestamp}{suffix}_{counter}.{ext}"
        counter += 1
    _write_text(path, content)
    return path


def _render_snapshot(mode_name, snapshot):
    if mode_name == "json":
        return json.dumps(snapshot, indent=2, sort_keys=False)
    if mode_name == "markdown":
        lines = [
            "# Interface Phase 3 Dashboard Snapshot",
            "",
            f"- Dashboard ID: {snapshot['dashboard_id']}",
            f"- Created at UTC: {snapshot['created_at_utc']}",
            f"- Repo: {snapshot['repo']}",
            f"- Source lineage: {snapshot['source_lineage']}",
            f"- Mode: {snapshot['mode']}",
            f"- Recommended next action: {snapshot['recommended_next_action']}",
            "",
            "## Phase 3 Status",
            f"- Build command: {snapshot['phase_3_status']['build_command']}",
            f"- Output path: {snapshot['phase_3_status']['output_path']}",
            f"- Print page: {snapshot['phase_3_status']['print_html_path']}",
            f"- Dashboard data export: {snapshot['phase_3_status']['dashboard_data_json_path']}",
            f"- Snapshot schema contract: {snapshot['phase_3_status']['snapshot_schema_contract_path']}",
            "",
            "## Safety",
            f"- Scanner status: {snapshot['phase_3_safety_scan']['status']}",
            f"- Boundary status: {json.dumps(snapshot['boundary_status'], sort_keys=True)}",
            "",
            "## Reports",
        ]
        for doc in snapshot["document_index"]["documents"]:
            lines.append(f"- {doc['recommended_review_order']}. {doc['title']} ({doc['path']})")
        return "\n".join(lines)
    if mode_name == "summary":
        return "\n".join([
            "Interface Phase 3 dashboard snapshot",
            f"Dashboard ID: {snapshot['dashboard_id']}",
            f"Phase 3 verdict: {snapshot['phase_3_status'].get('detected_verdict', 'unknown')}",
            f"Action registry actions: {snapshot['action_registry_summary'].get('total_actions', 0)}",
            f"Artifact packages: {snapshot['artifact_summary'].get('package_count', 0)}",
            f"Reports indexed: {snapshot['document_index'].get('document_count', 0)}",
        ])
    if mode_name == "full":
        return "\n".join([
            "# Interface Phase 3 Dashboard Snapshot (Full)",
            "",
            json.dumps(snapshot, indent=2, sort_keys=False),
        ])
    raise ValueError(f"unknown snapshot mode: {mode_name}")


def _validate_source_snapshot():
    snapshot = build_dashboard_snapshot()
    validation_result = validate_snapshot(snapshot)
    safety_result = scan_phase3_safety(DASHBOARD_DIR)
    if safety_result["status"] == "FAIL":
        validation_result["errors"].append("phase_3_safety_scan returned FAIL")
    if validation_result["errors"]:
        validation_result["status"] = "FAIL"
    return snapshot, validation_result, safety_result


def _build_outputs(snapshot, validation_result, safety_result):
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    dist_static_dir = DIST_DIR / "static"
    dist_static_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.css", dist_static_dir / "dashboard.css")
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.js", dist_static_dir / "dashboard.js")
    _write_text(DIST_DIR / "index.html", render_html(snapshot))
    _write_text(DIST_DIR / "print.html", render_print_html(snapshot))
    _write_text(DIST_DIR / "dashboard_data.json", json.dumps(snapshot, indent=2, sort_keys=False))
    report_path = _write_build_report(snapshot, validation_result, safety_result)
    return report_path


def _print_snapshot(mode_name, snapshot):
    print(_render_snapshot(mode_name, snapshot))


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="build_phase3_dashboard.py",
        description="Build the Interface Phase 3 static local web dashboard.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--snapshot-json", action="store_true", help="Print the dashboard snapshot as JSON and exit.")
    mode.add_argument("--snapshot-markdown", action="store_true", help="Print the dashboard snapshot as markdown and exit.")
    mode.add_argument("--snapshot-summary", action="store_true", help="Print a short dashboard snapshot summary and exit.")
    mode.add_argument("--snapshot-full", action="store_true", help="Print a verbose dashboard snapshot and exit.")
    mode.add_argument("--validate-only", action="store_true", help="Validate the dashboard snapshot and exit.")
    parser.add_argument("--save-snapshot", action="store_true", help="Save the selected snapshot mode under 09_exports/interface_phase_3/snapshots/. Defaults to JSON when no snapshot mode is supplied.")
    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    snapshot, validation_result, safety_result = _validate_source_snapshot()

    if args.validate_only:
        print(f"VALIDATION_{validation_result['status']}")
        for error in validation_result["errors"]:
            print(f"- {error}")
        return 0 if validation_result["status"] == "PASS" else 1

    if args.snapshot_json or args.snapshot_markdown or args.snapshot_summary or args.snapshot_full:
        mode_name = "json"
        if args.snapshot_markdown:
            mode_name = "markdown"
        elif args.snapshot_summary:
            mode_name = "summary"
        elif args.snapshot_full:
            mode_name = "full"
        if args.save_snapshot:
            saved_path = _write_snapshot_export(mode_name, _render_snapshot(mode_name, snapshot))
            print(f"Saved snapshot: {saved_path}")
        _print_snapshot(mode_name, snapshot)
        return 0 if validation_result["status"] == "PASS" else 1

    if args.save_snapshot:
        saved_path = _write_snapshot_export("json", _render_snapshot("json", snapshot))
        print(f"Saved snapshot: {saved_path}")
        return 0 if validation_result["status"] == "PASS" else 1

    if validation_result["status"] != "PASS":
        _emit_error("snapshot validation failed")
        for error in validation_result["errors"]:
            _emit_error(error)
        return 1

    report_path = _build_outputs(snapshot, validation_result, safety_result)
    print(f"Built dashboard: {DIST_DIR / 'index.html'}")
    print(f"Built print page: {DIST_DIR / 'print.html'}")
    print(f"Built data export: {DIST_DIR / 'dashboard_data.json'}")
    print(f"Build report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
