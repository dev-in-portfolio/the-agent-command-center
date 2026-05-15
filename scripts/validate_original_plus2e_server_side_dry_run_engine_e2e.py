import os
import subprocess

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"Command failed: {cmd}\n{res.stdout}\n{res.stderr}")
    return res.stdout

def check():
    validators = [
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_original_plus2d_approval_gate_storage.py",
        "python3 scripts/validate_original_plus2c_immutable_audit_log.py",
        "python3 scripts/validate_original_plus2b_persistent_request_storage.py",
        "python3 scripts/validate_original_plus2a_backend_auth_foundation.py",
        "python3 scripts/validate_original_plus1e_backend_implementation_gate.py",
        "python3 scripts/validate_original_plus1d_backend_boundary_blueprint.py",
        "python3 scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "python3 scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
        "python3 scripts/validate_original_plus1_controlled_automation_readiness.py",
        "python3 scripts/validate_original_phase_5e_runbook_simulator.py",
        "python3 scripts/validate_original_phase_5d_handoff_composer.py",
        "python3 scripts/validate_original_phase_5c_review_board.py",
        "python3 scripts/validate_original_phase_5b_request_packet_builder.py",
        "python3 scripts/validate_original_phase_5a_client_side_workflow_shell.py",
        "python3 scripts/validate_original_phase_4_hosted_dashboard_polish.py",
        "python3 scripts/validate_backend_phase_4d_schema_previews.py",
        "python3 scripts/validate_backend_phase_4d_disabled_ui.py",
        "python3 scripts/validate_backend_phase_4c_snapshot.py",
        "python3 scripts/validate_backend_phase_4a_foundation.py"
    ]
    
    for v in validators:
        run_cmd(v)
        
    diff = run_cmd("git diff --name-only origin/master..HEAD")
    for line in diff.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("09_exports/interface_phase_1/"):
            raise SystemExit(f"FAIL: Phase 1 changes not allowed: {line}")
        if line.startswith("09_exports/interface_phase_2/"):
            raise SystemExit(f"FAIL: Phase 2 changes not allowed: {line}")
        if line.startswith("09_exports/interface_phase_3/"):
            raise SystemExit(f"FAIL: Phase 3 report changes not allowed: {line}")
        if line.startswith("09_exports/interface_phase_4/"):
            raise SystemExit(f"FAIL: Phase 4 report changes not allowed: {line}")
        if line.startswith("11_interface/"):
            raise SystemExit(f"FAIL: Interface changes not allowed: {line}")
        if line.startswith("12_tui/"):
            raise SystemExit(f"FAIL: TUI changes not allowed: {line}")
        if line.startswith("10_runtime/"):
            raise SystemExit(f"FAIL: Runtime changes not allowed: {line}")
            
    print("ORIGINAL_PLUS2E_SERVER_SIDE_DRY_RUN_ENGINE_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    check()
