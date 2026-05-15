#!/usr/bin/env python3
"""E2E validation for Original Phase 5A client-side operator workflow shell."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errors = []

def run_validator(script_name):
    path = ROOT / "scripts" / script_name
    if not path.exists():
        errors.append(f"Missing validator: {script_name}")
        return None
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        errors.append(f"{script_name} exited with code {result.returncode}")
        if result.stderr:
            errors.append(f"  stderr: {result.stderr.strip()[:200]}")
    return result.stdout.strip()

# Run Phase 5A shell validator
shell_out = run_validator("validate_original_phase_5a_client_side_workflow_shell.py")
if shell_out and "ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_SHELL_VALIDATION_PASS" not in shell_out:
    errors.append("Phase 5A shell validator did not pass")

# Run Phase 4 validators
for validator in [
    "validate_original_phase_4_hosted_dashboard_polish.py",
    "validate_backend_phase_4d_schema_previews.py",
    "validate_backend_phase_4d_disabled_ui.py",
    "validate_backend_phase_4c_snapshot.py",
    "validate_backend_phase_4a_foundation.py",
]:
    out = run_validator(validator)
    if validator == "validate_original_phase_4_hosted_dashboard_polish.py" and out:
        if "ORIGINAL_PHASE_4_HOSTED_DASHBOARD_POLISH_VALIDATION_PASS" not in out:
            errors.append(f"{validator} did not pass")

# Check for forbidden changes
result = subprocess.run(
    ["git", "diff", "--name-only", "origin/master..HEAD"],
    capture_output=True, text=True, cwd=ROOT
)
changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

allowed_prefixes = [
        "scripts/validate_original_plus2e_server_side_dry_run_engine_e2e.py",
        "scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "14_backend/dry_run/",
        "netlify/functions/dry-run-status.js",
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
        "scripts/validate_backend_phase_4b_planning.py",
        "scripts/validate_backend_phase_4a_foundation.py",
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
        "scripts/validate_backend_phase_4d_strategic_build.py",
        "scripts/validate_backend_phase_4d_schema_previews.py",
        "scripts/validate_backend_phase_4d_disabled_ui.py",
        "scripts/validate_backend_phase_4d_gate_review.py",
        "scripts/validate_backend_phase_4c_snapshot_and_4d_gate_e2e.py",
        "scripts/validate_backend_phase_4c_snapshot.py",
        "scripts/validate_backend_phase_4c_planning.py",
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

for path in changed:
    if any(path.startswith(p) for p in allowed_prefixes):
        continue
        
    if path.startswith("09_exports/interface_phase_1/"):
        errors.append(f"Phase 1 files changed: {path}")
    elif path.startswith("09_exports/interface_phase_2/"):
        errors.append(f"Phase 2 files changed: {path}")
    elif path.startswith("11_interface/"):
        errors.append(f"Interface files changed: {path}")
    elif path.startswith("12_tui/"):
        errors.append(f"TUI files changed: {path}")
    elif path.startswith("10_runtime/"):
        errors.append(f"Runtime files changed: {path}")
    elif path.startswith("netlify/functions/"):
        errors.append(f"netlify/functions changed: {path}")
    elif path.startswith("14_backend/"):
        errors.append(f"Backend files changed: {path}")
    else:
        errors.append(f"Unexpected file changed: {path}")

# Reports contain PASS_WITH_HIGH_CONFIDENCE
reports_dir = ROOT / "09_exports" / "interface_phase_5"
for report in ["original_phase_5a_safety_report.md", "original_phase_5a_acceptance_report.md"]:
    path = reports_dir / report
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "PASS_WITH_HIGH_CONFIDENCE" not in content:
            errors.append(f"{report} missing PASS_WITH_HIGH_CONFIDENCE")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print("ORIGINAL_PHASE_5A_CLIENT_SIDE_WORKFLOW_E2E_VALIDATION_PASS")
