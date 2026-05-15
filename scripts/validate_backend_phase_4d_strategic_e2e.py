#!/usr/bin/env python3
import ast
import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VALIDATOR_CHAIN = [
    "scripts/validate_backend_phase_4d_schema_previews.py",
    "scripts/validate_backend_phase_4d_disabled_ui.py",
    "scripts/validate_backend_phase_4d_strategic_build.py",
    "scripts/validate_backend_phase_4c_snapshot.py",
    "scripts/validate_backend_phase_4d_gate_review.py",
    "scripts/validate_backend_phase_4c_planning.py",
    "scripts/validate_backend_phase_4b_planning.py",
    "scripts/validate_backend_phase_4a_foundation.py",
]

DANGEROUS_TEXT_PATTERNS = [
    "child_process",
    "process.env",
    "workflow_dispatch",
    "merge_pull_request",
    "create_pull_request",
    "update_file",
    "delete_file",
    "netlify deploy",
    "deploy_controls true",
    "merge_controls true",
    "push_controls true",
]

JS_DANGEROUS_PATTERNS = [
    "api.github.com",
    "api.netlify.com",
    "github.com/repos",
    "netlify.com/api",
]

SCAN_PATHS = [
    ROOT / "13_web_dashboard",
    ROOT / "14_backend",
    ROOT / "scripts" / "validate_backend_phase_4d_schema_previews.py",
    ROOT / "scripts" / "validate_backend_phase_4d_disabled_ui.py",
    ROOT / "scripts" / "validate_backend_phase_4d_strategic_build.py",
    ROOT / "scripts" / "validate_backend_phase_4d_strategic_e2e.py",
]


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _run(path):
    return subprocess.run([sys.executable, str(ROOT / path)], capture_output=True, text=True)


def _should_scan(path):
    if path.is_dir():
        return False
    if path.suffix not in {".py", ".js", ".html", ".css", ".json"}:
        return False
    return True


def _scan_python_ast(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(ROOT)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        _fail(f"Syntax error while scanning {rel}: {exc}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"requests", "urllib", "socket"}:
                    _fail(f"Dangerous import found in {rel}: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module in {"requests", "urllib", "socket", "child_process"}:
                _fail(f"Dangerous import-from found in {rel}: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                owner = getattr(node.func.value, "id", "")
                attr = node.func.attr
                if owner == "os" and attr in {"system", "getenv"}:
                    _fail(f"Dangerous os call found in {rel}: os.{attr}")
                if owner == "subprocess" and attr == "run":
                    if "scripts/validate_backend_phase_4d_" not in str(rel).replace("\\", "/"):
                        _fail(f"Unauthorized subprocess.run found in {rel}")
            elif isinstance(node.func, ast.Name):
                if node.func.id in {"exec", "eval"}:
                    _fail(f"Dangerous builtin call found in {rel}: {node.func.id}")
        elif isinstance(node, ast.Attribute):
            owner = getattr(node.value, "id", "")
            if owner == "os" and node.attr == "environ":
                _fail(f"Dangerous os.environ access found in {rel}")


def _scan_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(ROOT)
    if path.suffix == ".py":
        _scan_python_ast(path)
    else:
        for pattern in DANGEROUS_TEXT_PATTERNS:
            if pattern in text:
                _fail(f"Dangerous pattern found in {rel}: {pattern}")
    if path.suffix in {".js", ".html"}:
        for pattern in JS_DANGEROUS_PATTERNS:
            if pattern in text:
                _fail(f"Dangerous external integration pattern found in {rel}: {pattern}")
    if path.suffix == ".json":
        lowered = text.lower()
        for pattern in ["deploy_controls\": true", "merge_controls\": true", "push_controls\": true"]:
            if pattern in lowered:
                _fail(f"Dangerous true control flag found in {rel}: {pattern}")


def _scan_paths():
    for scan_path in SCAN_PATHS:
        if scan_path.is_dir():
            for path in scan_path.rglob("*"):
                if _should_scan(path):
                    _scan_file(path)
        elif scan_path.exists():
            _scan_file(scan_path)


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
        "scripts/validate_original_plus2d_approval_gate_storage_e2e.py",
        "scripts/validate_original_plus2c_immutable_audit_log.py",
        "scripts/validate_original_plus2a_backend_auth_foundation_e2e.py",
        "scripts/validate_original_plus1e_backend_implementation_gate_e2e.py",
        "scripts/validate_original_plus1e_backend_implementation_gate.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa_e2e.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer_e2e.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5b_request_packet_builder.py",
        "scripts/validate_backend_phase_4d_strategic_e2e.py",
        "scripts/validate_backend_phase_4c_e2e.py",
        "scripts/validate_interface_phase_3_dashboard.py",
        "scripts/validate_backend_phase_4b_e2e.py",
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
        "scripts/validate_original_plus2c_immutable_audit_log_e2e.py",
        "scripts/validate_original_plus2b_persistent_request_storage_e2e.py",
        "scripts/validate_original_plus2b_persistent_request_storage.py",
        "scripts/validate_original_plus2a_backend_auth_foundation.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint_e2e.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint.py",
        "scripts/validate_original_plus1_controlled_automation_readiness_e2e.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_phase_5e_runbook_simulator_e2e.py",
        "scripts/validate_original_phase_5d_handoff_composer_e2e.py",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5c_review_board_e2e.py",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5b_request_packet_builder_e2e.py",
        "scripts/validate_original_phase_5a_client_side_workflow_shell.py",
        "scripts/validate_original_phase_5a_client_side_workflow_e2e.py",
        "scripts/validate_original_phase_4_hosted_dashboard_polish.py",
        "scripts/validate_original_phase_4_hosted_dashboard_e2e.py",
        "scripts/validate_backend_phase_4c_snapshot_and_4d_gate_e2e.py",
        "scripts/validate_backend_phase_4a_e2e.py",
        "scripts/validate_interface_phase_3_e2e.py",
        "scripts/validate_interface_phase_2_e2e.py",
        "scripts/validate_interface_phase_1_e2e.py",
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
        "14_backend/auth/",
        "14_backend/request_storage/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "09_exports/original_plus2/",
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
                _fail(f"Forbidden path modified: {f}")


def check_fetch_targets():
    print("Checking fetch targets...")
    allowed_targets = [
        "./original_plus2c_audit_log_model.json",
        "/api/audit-log-status",
        '/api/health', '/api/status', '/api/backend-manifest',
        '/api/auth-status', '/api/role-matrix', '/api/request-storage-status',
        './status_snapshot.json',
        './phase4d_identity_schema.json', './phase4d_action_schema.json',
        './phase4d_audit_schema.json', './phase4d_approval_schema.json',
        './phase4d_risk_model.json',
        './original_plus1b_contract_schemas.json',
        './original_plus1c_readiness_qa_model.json',
        './original_plus1d_backend_boundary_model.json',
        './original_plus1e_backend_build_tickets.json',
        './original_plus2a_auth_foundation_model.json',
        './original_plus2b_request_storage_model.json',
    ]
    
    html = (ROOT / "13_web_dashboard/dist/index.html").read_text(encoding="utf-8")
    for forbidden in ["http://", "https://"]:
        if forbidden in html:
            # Simple w3/Netlify exclusion
            if "http://www.w3.org" in html and forbidden == "http://":
                continue
            if ".netlify.app" in html:
                continue
            _fail(f"Forbidden external reference found in dashboard HTML: {forbidden}")

    # Check JS for unauthorized fetches
    js_path = ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js"
    if js_path.exists():
        js_content = js_path.read_text(encoding="utf-8", errors="replace")
        fetches = re.findall(r'fetch\(["\']([^"\']+)["\']\)', js_content)
        for target in fetches:
            if target not in allowed_targets:
                _fail(f"Unauthorized fetch target found in JS: {target}")


def main():
    check_forbidden_paths()
    for validator in VALIDATOR_CHAIN:
        result = _run(validator)
        if result.returncode != 0:
            _fail(f"{validator} failed: {result.stdout}{result.stderr}")

    _scan_paths()

    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4d_strategic_build_acceptance_report.md").read_text(encoding="utf-8")
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Strategic build acceptance report missing required verdict")

    check_fetch_targets()

    print("BACKEND_PHASE_4D_STRATEGIC_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
