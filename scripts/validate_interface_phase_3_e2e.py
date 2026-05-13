#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "13_web_dashboard" / "build_phase3_dashboard.py"
HTML = ROOT / "13_web_dashboard" / "dist" / "index.html"
PRINT_HTML = ROOT / "13_web_dashboard" / "dist" / "print.html"
DATA_JSON = ROOT / "13_web_dashboard" / "dist" / "dashboard_data.json"
DIST_CSS = ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.css"
DIST_JS = ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js"
PHASE4D_IDENTITY = ROOT / "13_web_dashboard" / "dist" / "phase4d_identity_schema.json"
PHASE4D_ACTION = ROOT / "13_web_dashboard" / "dist" / "phase4d_action_schema.json"
PHASE4D_AUDIT = ROOT / "13_web_dashboard" / "dist" / "phase4d_audit_schema.json"
SNAPSHOT_DIR = ROOT / "09_exports" / "interface_phase_3" / "snapshots"
GITIGNORE = ROOT / ".gitignore"
HYGIENE_REPORT = ROOT / "09_exports" / "interface_phase_3" / "interface_phase_3_generated_artifact_hygiene_report.md"
MERGE_PACKET = ROOT / "09_exports" / "interface_phase_3" / "merge_readiness" / "interface_phase_3_merge_readiness_packet.md"
OPERATOR_CARD = ROOT / "09_exports" / "interface_phase_3" / "interface_phase_3_operator_command_card.md"
README = ROOT / "13_web_dashboard" / "README.md"
VISUAL_QA_REPORT = ROOT / "09_exports" / "interface_phase_3" / "interface_phase_3_visual_qa_report.md"


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _parse_saved_path(output):
    for line in output.splitlines():
        if line.startswith("Saved snapshot: "):
            return Path(line.split("Saved snapshot: ", 1)[1].strip())
    return None


def _assert_no_traceback(result, label):
    if "Traceback" in result.stderr or "Traceback" in result.stdout:
        raise RuntimeError(f"{label} produced a traceback")


def _assert_contains(path, needles, label=None):
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise RuntimeError(f"{label or path.name} missing {needle}")


def main():
    result = _run([sys.executable, str(DASHBOARD), "--validate-only"])
    if result.returncode != 0 or "VALIDATION_PASS" not in result.stdout:
        return _fail("validate-only command failed")
    for path in [HTML, PRINT_HTML, DATA_JSON, DIST_CSS, DIST_JS, PHASE4D_IDENTITY, PHASE4D_ACTION, PHASE4D_AUDIT]:
        if not path.exists():
            return _fail(f"missing built artifact: {path.relative_to(ROOT)}")

    help_result = _run([sys.executable, str(DASHBOARD), "--help"])
    if help_result.returncode != 0 or "Read-Only Operations Dashboard" not in help_result.stdout:
        return _fail("help command failed")
    _assert_no_traceback(help_result, "help command")

    snapshot_json_result = _run([sys.executable, str(DASHBOARD), "--snapshot-json"])
    if snapshot_json_result.returncode != 0:
        return _fail("snapshot-json command failed")
    snapshot = json.loads(snapshot_json_result.stdout)
    if snapshot.get("phase") != "Read-Only Operations Dashboard":
        return _fail("snapshot phase mismatch")
    boundary = snapshot.get("boundary_status", {})
    if any(boundary.get(name) is not False for name in [
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
    ]):
        return _fail("boundary status not fully false")

    markdown_result = _run([sys.executable, str(DASHBOARD), "--snapshot-markdown"])
    summary_result = _run([sys.executable, str(DASHBOARD), "--snapshot-summary"])
    full_result = _run([sys.executable, str(DASHBOARD), "--snapshot-full"])
    for label, command_result, needle in [
        ("snapshot-markdown", markdown_result, "# Read-Only Operations Dashboard Snapshot"),
        ("snapshot-summary", summary_result, "Read-Only Operations Dashboard snapshot"),
        ("snapshot-full", full_result, "# Read-Only Operations Dashboard Snapshot (Full)"),
    ]:
        if command_result.returncode != 0 or needle not in command_result.stdout:
            return _fail(f"{label} command failed")
        _assert_no_traceback(command_result, label)

    snapshot_json_save = _run([sys.executable, str(DASHBOARD), "--snapshot-json", "--save-snapshot"])
    if snapshot_json_save.returncode != 0:
        return _fail("snapshot-json --save-snapshot command failed")
    _assert_no_traceback(snapshot_json_save, "snapshot-json --save-snapshot")

    validate_only = _run([sys.executable, str(DASHBOARD), "--validate-only"])
    if validate_only.returncode != 0:
        return _fail("validate-only command failed")

    save_json_1 = _run([sys.executable, str(DASHBOARD), "--save-snapshot"])
    save_json_2 = _run([sys.executable, str(DASHBOARD), "--save-snapshot"])
    for label, result_item in [("save-snapshot 1", save_json_1), ("save-snapshot 2", save_json_2)]:
        if result_item.returncode != 0:
          return _fail(f"{label} command failed")
        _assert_no_traceback(result_item, label)
    path_1 = _parse_saved_path(save_json_1.stdout)
    path_2 = _parse_saved_path(save_json_2.stdout)
    if not path_1 or not path_2:
        return _fail("save-snapshot output missing path")
    if path_1 == path_2:
        return _fail("save-snapshot overwrote an existing file name")
    for saved_path in [path_1, path_2]:
        if SNAPSHOT_DIR not in saved_path.parents:
            return _fail("saved snapshot escaped snapshots directory")
        if not saved_path.exists():
            return _fail(f"saved snapshot missing: {saved_path}")
        if saved_path.suffix != ".json":
            return _fail("default save-snapshot should create JSON")
        json.loads(saved_path.read_text(encoding="utf-8"))

    markdown_save = _run([sys.executable, str(DASHBOARD), "--snapshot-markdown", "--save-snapshot"])
    summary_save = _run([sys.executable, str(DASHBOARD), "--snapshot-summary", "--save-snapshot"])
    full_save = _run([sys.executable, str(DASHBOARD), "--snapshot-full", "--save-snapshot"])
    for label, result_item, expected_suffix in [
        ("markdown save", markdown_save, ".md"),
        ("summary save", summary_save, ".txt"),
        ("full save", full_save, ".txt"),
    ]:
        if result_item.returncode != 0:
            return _fail(f"{label} command failed")
        saved = _parse_saved_path(result_item.stdout)
        if not saved or saved.suffix != expected_suffix:
            return _fail(f"{label} saved path mismatch")
        if SNAPSHOT_DIR not in saved.parents or not saved.exists():
            return _fail(f"{label} saved path invalid")

    _assert_contains(GITIGNORE, [
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.json",
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.md",
        "09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.txt",
        "09_exports/interface_phase_3/test_runs/",
    ], ".gitignore")
    _assert_contains(HYGIENE_REPORT, [
        "Read-Only Operations Dashboard Generated Artifact Hygiene Report",
        "PASS_WITH_HIGH_CONFIDENCE",
        "Generated Artifact Hygiene",
    ], "hygiene report")
    _assert_contains(MERGE_PACKET, ["Generated Artifact Hygiene", "ready_for_merge_review"], "merge packet")
    _assert_contains(OPERATOR_CARD, [
        "cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1",
        "127.0.0.1:8080",
    ], "operator card")
    _assert_contains(README, [
        "cd 13_web_dashboard/dist && python3 -m http.server 8080 --bind 127.0.0.1",
        "127.0.0.1:8080",
    ], "README")
    _assert_contains(VISUAL_QA_REPORT, [
        "CSS loaded from dist/static/dashboard.css",
        "JS loaded from dist/static/dashboard.js",
        "dist/index.html self-contained relative asset paths",
        "major sections collapsed by default",
    ], "visual QA report")

    invalid_flag = _run([sys.executable, str(DASHBOARD), "--definitely-not-real"])
    if invalid_flag.returncode == 0:
        return _fail("invalid flag was not rejected safely")
    if "Traceback" in invalid_flag.stderr or "Traceback" in invalid_flag.stdout:
        return _fail("invalid flag produced traceback")

    positional = _run([sys.executable, str(DASHBOARD), "random_arg"])
    if positional.returncode == 0:
        return _fail("positional arg was not rejected safely")
    if "Traceback" in positional.stderr or "Traceback" in positional.stdout:
        return _fail("positional arg produced traceback")

    html = HTML.read_text(encoding="utf-8")
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
        "Phase 4D Control Room Preview",
        "Identity & Permissions Preview",
        "Action Request Queue Preview",
        "Audit Event Schema Preview",
        "All controls remain disabled in Phase 4D.",
    ]:
        if needle not in html:
            return _fail(f"HTML missing {needle}")
    if "http://" in html or "https://" in html:
        return _fail("HTML contains network URLs")
    for needle in ["fetch(", "WebSocket", "XMLHttpRequest", "EventSource", "analytics"]:
        if needle in html:
            return _fail(f"HTML contains forbidden token: {needle}")
    if "./static/dashboard.css" not in html or "./static/dashboard.js" not in html:
        return _fail("HTML missing self-contained CSS/JS links")
    if "../static/" in html:
        return _fail("HTML still references parent static directory")
    if 'data-open-panel="reports-library"' not in html:
        return _fail("HTML missing open section buttons")

    phase2_tui = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_2_tui.py")])
    phase2_e2e = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_2_e2e.py")])
    if phase2_tui.returncode != 0 or phase2_e2e.returncode != 0:
        return _fail("phase 2 validators failed")

    phase1_cli = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_1_cli.py")])
    if phase1_cli.returncode != 0:
        return _fail("phase 1 CLI validator failed")

    print("INTERFACE_PHASE_3_E2E_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
