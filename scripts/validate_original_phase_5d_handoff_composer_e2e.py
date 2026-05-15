#!/usr/bin/env python3
"""Original Phase 5D handoff composer e2e validator."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "09_exports" / "interface_phase_5"


def run_validator(script_name):
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / script_name)], capture_output=True, text=True, cwd=ROOT)
    print(f"  {script_name}: exit={result.returncode}")
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
    if result.stderr.strip():
        for line in result.stderr.strip().splitlines():
            print(f"    STDERR: {line}")
    return result.returncode == 0


def check(condition, message, errors):
    if not condition:
        errors.append(message)


def main():
    errors = []
    print("Running Original Phase 5D Handoff Composer E2E Validator...\n")

    for script_name in [
        "validate_original_phase_5d_handoff_composer.py",
        "validate_original_phase_5c_review_board.py",
        "validate_original_phase_5c_review_board.py",
        "validate_original_phase_5b_request_packet_builder.py",
        "validate_original_phase_5b_request_packet_builder.py",
        "validate_original_phase_5a_client_side_workflow_shell.py",
        "validate_original_phase_5a_client_side_workflow_shell.py",
        "validate_original_phase_4_hosted_dashboard_polish.py",
        "validate_original_phase_4_hosted_dashboard_polish.py",
        "validate_backend_phase_4d_schema_previews.py",
        "validate_backend_phase_4d_disabled_ui.py",
        "validate_backend_phase_4d_strategic_build.py",
        "validate_backend_phase_4d_strategic_build.py",
        "validate_backend_phase_4c_snapshot.py",
        "validate_backend_phase_4a_foundation.py",
        "validate_backend_phase_4a_foundation.py",
        "validate_interface_phase_3_dashboard.py",
        "validate_interface_phase_3_dashboard.py",
    ]:
        ok = run_validator(script_name)
        check(ok, f"validator failed: {script_name}", errors)

    changed = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    ).stdout.strip().splitlines()

    allowed_prefixes = [
        "scripts/validate_original_plus2d_approval_gate_storage_e2e.py",
        "scripts/validate_original_plus2c_immutable_audit_log.py",
        "scripts/validate_original_plus2a_backend_auth_foundation_e2e.py",
        "scripts/validate_original_plus1e_backend_implementation_gate_e2e.py",
        "scripts/validate_original_plus1e_backend_implementation_gate.py",
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
        "scripts/validate_original_phase_5c_review_board_e2e.py",
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
        "scripts/validate_original_plus2d",
        "scripts/validate_original_plus2c",
        "scripts/validate_original_plus2b",
        "scripts/validate_original_plus2a",
        "netlify/functions/audit-log-status.js",
        "14_backend/audit_log/",
        "09_exports/original_plus2/",
        "13_web_dashboard/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5d_handoff_composer_e2e.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint.py",
        "scripts/validate_original_plus1d_backend_boundary_blueprint_e2e.py",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5b_request_packet_builder_e2e.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5e_runbook_simulator_e2e.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_plus1_controlled_automation_readiness_e2e.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer_e2e.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    forbidden_prefixes = [
        "netlify/functions/",
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "11_interface/",
        "12_tui/",
        "10_runtime/",
        "14_backend/",
    ]

    authorized_functions = [
        "netlify/functions/approval-gate-status.js",
        "netlify/functions/auth-status.js",
        "netlify/functions/role-matrix.js",
        "netlify/functions/request-storage-status.js",
        "netlify/functions/audit-log-status.js",
        "netlify/functions/backend-manifest.js",
        "netlify/functions/_shared/models/"
    ]
    authorized_backend = [
        "14_backend/approval_gate/",
        "14_backend/auth/",
        "14_backend/request_storage/",
        "14_backend/audit_log/"
    ]

    for path in changed:
        if not path: continue
        
        # Check forbidden
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                # Exception for authorized paths
                if prefix == "netlify/functions/" and any(path == f or path.startswith("netlify/functions/_shared/models/") for f in authorized_functions):
                    continue
                if prefix == "14_backend/" and any(path.startswith(p) for p in authorized_backend):
                    continue
                errors.append(f"Forbidden changed path: {path}")
        
        # Check allowed
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            # Check authorized exceptions
            is_authorized = False
            if path.startswith("netlify/functions/") and any(path == f or path.startswith("netlify/functions/_shared/models/") for f in authorized_functions):
                is_authorized = True
            if path.startswith("14_backend/") and any(path.startswith(p) for p in authorized_backend):
                is_authorized = True
                
            if not is_authorized:
                errors.append(f"Unexpected changed path: {path}")

    for report_name in [
        "original_phase_5d_client_side_handoff_composer_report.md",
        "original_phase_5d_design_report.md",
        "original_phase_5d_safety_report.md",
        "original_phase_5d_validator_report.md",
        "original_phase_5d_acceptance_report.md",
    ]:
        path = REPORTS / report_name
        check(path.exists(), f"missing report: {report_name}", errors)
        if path.exists():
            check("PASS_WITH_HIGH_CONFIDENCE" in path.read_text(encoding="utf-8"), f"report missing PASS_WITH_HIGH_CONFIDENCE: {report_name}", errors)

    if errors:
        print("\nVALIDATION_FAIL")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("ORIGINAL_PHASE_5D_HANDOFF_COMPOSER_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
