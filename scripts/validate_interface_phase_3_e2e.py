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


def check_forbidden_paths():
    print("Checking forbidden diff paths...")
    result = subprocess.run(["git", "diff", "--name-only", "origin/master..HEAD"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print("WARNING: Could not check git diff, assuming detached head or CI.")
        return
        
    changed_files = result.stdout.splitlines()
    forbidden_prefixes = [
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "11_interface/",
        "12_tui/",
        "10_runtime/"
    ]
    
    allowed_prefixes = [
        "scripts/validate_original_plus2d_approval_gate_storage.py",
        "scripts/validate_original_plus2c_immutable_audit_log.py",
        "scripts/validate_original_plus2a_backend_auth_foundation.py",
        "scripts/validate_original_plus1e_backend_implementation_gate.py",
        "scripts/validate_original_plus1e_backend_implementation_gate.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5b_request_packet_builder.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_backend_phase_4b_planning.py",
        "scripts/validate_backend_phase_4a_foundation.py",
        "scripts/validate_interface_phase_3_dashboard.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_interface_phase_2_tui.py",
        "scripts/validate_interface_phase_1_release_candidate.py",
        "scripts/validate_interface_phase_1_command_packets.py",
        "scripts/validate_interface_phase_1_cli.py",
        "scripts/validate_station_chief_runtime_v9_0.py",
        "scripts/validate_station_chief_runtime_v6_6.py",
        "scripts/validate_station_chief_runtime_v6_5.py",
        "scripts/validate_station_chief_runtime_v6_4.py",
        "scripts/validate_station_chief_runtime_v6_3.py",
        "scripts/validate_station_chief_runtime_v6_2.py",
        "scripts/validate_station_chief_runtime_v6_1.py",
        "scripts/validate_station_chief_runtime_v5_9.py",
        "scripts/validate_station_chief_runtime_v5_8.py",
        "scripts/validate_station_chief_runtime_v5_7.py",
        "scripts/validate_station_chief_runtime_v5_5.py",
        "scripts/validate_station_chief_runtime_v5_1.py",
        "scripts/validate_station_chief_runtime_v4_9.py",
        "scripts/validate_station_chief_runtime_v4_8.py",
        "scripts/validate_station_chief_runtime_v4_6.py",
        "scripts/validate_station_chief_runtime_v4_1.py",
        "scripts/validate_station_chief_runtime_v3_7.py",
        "scripts/validate_station_chief_runtime_v3_5.py",
        "scripts/validate_station_chief_runtime_v3_4.py",
        "scripts/validate_station_chief_runtime_v3_3.py",
        "scripts/validate_station_chief_runtime_v3_2.py",
        "scripts/validate_station_chief_runtime_v3_1.py",
        "scripts/validate_station_chief_runtime_v3_0.py",
        "scripts/validate_station_chief_runtime_v2_9.py",
        "scripts/validate_station_chief_runtime_v2_6.py",
        "scripts/validate_station_chief_runtime_v2_5.py",
        "scripts/validate_station_chief_runtime_v2_2.py",
        "scripts/validate_station_chief_runtime_v25_0.py",
        "scripts/validate_station_chief_runtime_v20_0.py",
        "scripts/validate_station_chief_runtime_v1_8.py",
        "scripts/validate_station_chief_runtime_v1_6.py",
        "scripts/validate_original_plus2d_approval_gate_storage.py",
        "scripts/validate_original_plus2c_immutable_audit_log.py",
        "scripts/validate_original_plus2b_persistent_request_storage.py",
        "scripts/validate_original_plus2b_persistent_request_storage.py",
        "scripts/validate_original_plus2a_backend_auth_foundation.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5b_request_packet_builder.py",
        "scripts/validate_original_phase_5a_client_side_workflow_shell.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_original_phase_4_hosted_dashboard_polish.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_backend_phase_4d_strategic_build.py",
        "scripts/validate_backend_phase_4d_schema_previews.py",
        "scripts/validate_backend_phase_4d_disabled_ui.py",
        "scripts/validate_backend_phase_4d_gate_review.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_backend_phase_4c_snapshot.py",
        "scripts/validate_backend_phase_4c_planning.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_interface_phase_3_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_station_chief_runtime_v8_0.py",
        "scripts/validate_station_chief_runtime_v6_0.py",
        "scripts/validate_station_chief_runtime_v5_6.py",
        "scripts/validate_station_chief_runtime_v5_4.py",
        "scripts/validate_station_chief_runtime_v5_3.py",
        "scripts/validate_station_chief_runtime_v5_2.py",
        "scripts/validate_station_chief_runtime_v5_0.py",
        "scripts/validate_station_chief_runtime_v4_7.py",
        "scripts/validate_station_chief_runtime_v4_5.py",
        "scripts/validate_station_chief_runtime_v4_4.py",
        "scripts/validate_station_chief_runtime_v4_3.py",
        "scripts/validate_station_chief_runtime_v4_2.py",
        "scripts/validate_station_chief_runtime_v4_0.py",
        "scripts/validate_station_chief_runtime_v3_9.py",
        "scripts/validate_station_chief_runtime_v3_8.py",
        "scripts/validate_station_chief_runtime_v3_6.py",
        "scripts/validate_station_chief_runtime_v2_8.py",
        "scripts/validate_station_chief_runtime_v2_7.py",
        "scripts/validate_station_chief_runtime_v2_4.py",
        "scripts/validate_station_chief_runtime_v2_3.py",
        "scripts/validate_station_chief_runtime_v2_1.py",
        "scripts/validate_station_chief_runtime_v2_0.py",
        "scripts/validate_station_chief_runtime_v24_0.py",
        "scripts/validate_station_chief_runtime_v23_0.py",
        "scripts/validate_station_chief_runtime_v22_0.py",
        "scripts/validate_station_chief_runtime_v21_0.py",
        "scripts/validate_station_chief_runtime_v1_7.py",
        "scripts/validate_station_chief_runtime_v1_5.py",
        "scripts/validate_station_chief_runtime_v1_4.py",
        "scripts/validate_station_chief_runtime_v1_3.py",
        "scripts/validate_station_chief_runtime_v1_2.py",
        "scripts/validate_station_chief_runtime_v1_1.py",
        "scripts/validate_station_chief_runtime_v1_0.py",
        "scripts/validate_station_chief_runtime_v19_0.py",
        "scripts/validate_station_chief_runtime_v18_0.py",
        "scripts/validate_station_chief_runtime_v17_0.py",
        "scripts/validate_station_chief_runtime_v16_0.py",
        "scripts/validate_station_chief_runtime_v15_0.py",
        "scripts/validate_station_chief_runtime_v14_0.py",
        "scripts/validate_station_chief_runtime_v13_0.py",
        "scripts/validate_station_chief_runtime_v12_0.py",
        "scripts/validate_station_chief_runtime_v11_0.py",
        "scripts/validate_station_chief_runtime_v10_0.py",
        "scripts/validate_station_chief_runtime_v0_9.py",
        "scripts/validate_station_chief_runtime_v0_8.py",
        "scripts/validate_station_chief_runtime_v0_7.py",
        "scripts/validate_station_chief_runtime_v0_6.py",
        "scripts/validate_station_chief_runtime_v0_5.py",
        "scripts/validate_station_chief_runtime_v0_4.py",
        "scripts/validate_station_chief_runtime_v0_3.py",
        "scripts/validate_station_chief_runtime_v0_2.py",
        "scripts/validate_station_chief_runtime_skeleton.py",
        "scripts/validate_registry.py",
        "scripts/validate_pre_hiring_devinization_note.py",
        "scripts/validate_full_expansion_completion.py",
        "scripts/validate_final_devinization_stack_lock.py",
        "scripts/validate_family_expansion.py",
        "scripts/validate_family_batch_175.py",
        "scripts/validate_family_batch_165_174.py",
        "scripts/validate_family_batch_155_164.py",
        "scripts/validate_family_batch_145_154.py",
        "scripts/validate_family_batch_135_144.py",
        "scripts/validate_family_batch_125_134.py",
        "scripts/validate_family_batch_115_124.py",
        "scripts/validate_family_batch_105_114.py",
        "scripts/validate_family_batch_095_104.py",
        "scripts/validate_family_batch_085_094.py",
        "scripts/validate_family_batch_075_084.py",
        "scripts/validate_family_batch_065_074.py",
        "scripts/validate_family_batch_055_064.py",
        "scripts/validate_family_batch_045_054.py",
        "scripts/validate_family_batch_035_044.py",
        "scripts/validate_family_batch_025_034.py",
        "scripts/validate_family_batch_015_024.py",
        "scripts/validate_family_batch_005_014.py",
        "scripts/validate_family_007_devinized_engineering_overload_pack.py",
        "scripts/validate_family_004_expansion.py",
        "scripts/validate_family_003_expansion.py",
        "scripts/validate_family_002_expansion.py",
        "scripts/validate_exports.py",
        "scripts/validate_devinization_pack_007_agent_governance_identity_accountability.py",
        "scripts/validate_devinization_pack_006_output_assembly_delivery_intelligence.py",
        "scripts/validate_devinization_pack_005_quality_standards_human_review.py",
        "scripts/validate_devinization_pack_004_execution_safety_tools_recovery.py",
        "scripts/validate_devinization_pack_003_prompt_memory_context_architecture.py",
        "scripts/validate_devinization_pack_002_runtime_routing_work_control.py",
        "scripts/validate_devinization_pack_001_command_brain.py",
        "scripts/validate_devin_ownership_metadata.py",
        "scripts/validate_auto_self_improve_2.py",
        "14_backend/approval_gate/",
        "netlify/functions/approval-gate-status.js",
        "scripts/validate_original_plus2d",
        "scripts/validate_original_plus2c",
        "scripts/validate_original_plus2b",
        "scripts/validate_original_plus2a",
        "netlify/functions/audit-log-status.js",
        "14_backend/audit_log/",
        "13_web_dashboard/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "09_exports/original_plus2/",
        "14_backend/auth/",
        "14_backend/request_storage/",
        "netlify/functions/auth-status.js",
        "netlify/functions/role-matrix.js",
        "netlify/functions/request-storage-status.js",
        "netlify/functions/backend-manifest.js",
        "netlify/functions/_shared/models/",
        "scripts/validate_",
    ]
    
    for f in changed_files:
        if any(f.startswith(p) for p in allowed_prefixes):
            continue
        for prefix in forbidden_prefixes:
            if f.startswith(prefix):
                print(f"FAIL: Forbidden path modified: {f}")
                sys.exit(1)


def main():
    check_forbidden_paths()
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
        "Risk Model Preview",
        "DISABLED MOCK",
        "SCHEMA PREVIEW ONLY",
        "NO EXECUTION",
        "NO MUTATION",
        "NO DEPLOY",
        "NO MERGE",
        "NO PUSH",
        "NO SECRET ACCESS",
        "DISABLED — SCHEMA PREVIEW ONLY",
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

    allowed_fetches = [
        "./original_plus2c_audit_log_model.json",
        "/api/audit-log-status",
        'fetch("/api/health")', "fetch('/api/health')",
        'fetch("/api/status")', "fetch('/api/status')",
        'fetch("/api/backend-manifest")', "fetch('/api/backend-manifest')",
        'fetch("/api/auth-status")', "fetch('/api/auth-status')",
        'fetch("/api/role-matrix")', "fetch('/api/role-matrix')",
        'fetch("/api/request-storage-status")', "fetch('/api/request-storage-status')",
        'fetch("./status_snapshot.json")', "fetch('./status_snapshot.json')",
        'fetch("./phase4d_identity_schema.json")', "fetch('./phase4d_identity_schema.json')",
        'fetch("./phase4d_action_schema.json")', "fetch('./phase4d_action_schema.json')",
        'fetch("./phase4d_audit_schema.json")', "fetch('./phase4d_audit_schema.json')",
        'fetch("./phase4d_risk_model.json")', "fetch('./phase4d_risk_model.json')",
        'fetch("./phase4d_approval_schema.json")', "fetch('./phase4d_approval_schema.json')",
        'fetch("./original_plus1b_contract_schemas.json")', "fetch('./original_plus1b_contract_schemas.json')",
        'fetch("./original_plus1c_readiness_qa_model.json")', "fetch('./original_plus1c_readiness_qa_model.json')",
        'fetch("./original_plus1d_backend_boundary_model.json")', "fetch('./original_plus1d_backend_boundary_model.json')",
        'fetch("./original_plus1e_backend_build_tickets.json")', "fetch('./original_plus1e_backend_build_tickets.json')",
        'fetch("./original_plus2a_auth_foundation_model.json")', "fetch('./original_plus2a_auth_foundation_model.json')",
        'fetch("./original_plus2b_request_storage_model.json")', "fetch('./original_plus2b_request_storage_model.json')"
    ]
    js = DIST_JS.read_text(encoding="utf-8")
    for line in js.splitlines():
        if "fetch(" in line and not any(f in line for f in allowed_fetches):
            return _fail(f"JavaScript contains forbidden fetch: {line.strip()}")

    phase2_tui = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_2_tui.py")])
    phase2_e2e = _run([sys.executable, str(ROOT / "scripts" / "validate_phase5_plus1_master_validator_wall.py")])
    if phase2_tui.returncode != 0 or phase2_e2e.returncode != 0:
        return _fail("phase 2 validators failed")

    phase1_cli = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_1_cli.py")])
    if phase1_cli.returncode != 0:
        return _fail("phase 1 CLI validator failed")

    print("INTERFACE_PHASE_3_E2E_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
