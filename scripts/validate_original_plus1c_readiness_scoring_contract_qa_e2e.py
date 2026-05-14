#!/usr/bin/env python3
"""Original +1C readiness scoring, contract QA, and no-go decision e2e validator."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "09_exports" / "original_plus1"


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
    print("Running Original +1C Readiness Scoring Contract QA E2E Validator...\n")

    for script_name in [
        "validate_original_plus1c_readiness_scoring_contract_qa.py",
        "validate_phase5_plus1_master_validator_wall.py",
        "validate_original_plus1b_operator_console_contract_layer.py",
        "validate_original_plus1b_operator_console_contract_layer_e2e.py",
        "validate_original_plus1_controlled_automation_readiness.py",
        "validate_original_plus1_controlled_automation_readiness_e2e.py",
        "validate_original_phase_5e_runbook_simulator.py",
        "validate_original_phase_5e_runbook_simulator_e2e.py",
        "validate_original_phase_5d_handoff_composer.py",
        "validate_original_phase_5d_handoff_composer_e2e.py",
        "validate_original_phase_5c_review_board.py",
        "validate_original_phase_5c_review_board_e2e.py",
        "validate_original_phase_5b_request_packet_builder.py",
        "validate_original_phase_5b_request_packet_builder_e2e.py",
        "validate_original_phase_5a_client_side_workflow_shell.py",
        "validate_original_phase_5a_client_side_workflow_e2e.py",
        "validate_original_phase_4_hosted_dashboard_polish.py",
        "validate_original_phase_4_hosted_dashboard_e2e.py",
        "validate_backend_phase_4d_schema_previews.py",
        "validate_backend_phase_4d_disabled_ui.py",
        "validate_backend_phase_4d_strategic_build.py",
        "validate_backend_phase_4d_strategic_e2e.py",
        "validate_backend_phase_4c_snapshot.py",
        "validate_backend_phase_4a_foundation.py",
        "validate_backend_phase_4a_e2e.py",
        "validate_interface_phase_3_dashboard.py",
        "validate_interface_phase_3_e2e.py",
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
        "13_web_dashboard/",
        "09_exports/original_plus1/",
        "09_exports/interface_phase_5/",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa.py",
        "scripts/validate_original_plus1c_readiness_scoring_contract_qa_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer.py",
        "scripts/validate_original_plus1b_operator_console_contract_layer_e2e.py",
        "scripts/validate_original_plus1_controlled_automation_readiness.py",
        "scripts/validate_original_plus1_controlled_automation_readiness_e2e.py",
        "scripts/validate_original_phase_5e_runbook_simulator.py",
        "scripts/validate_original_phase_5e_runbook_simulator_e2e.py",
        "scripts/validate_original_phase_5d_handoff_composer.py",
        "scripts/validate_original_phase_5d_handoff_composer_e2e.py",
        "scripts/validate_original_phase_5c_review_board.py",
        "scripts/validate_original_phase_5c_review_board_e2e.py",
        "scripts/validate_original_phase_5b_request_packet_builder.py",
        "scripts/validate_original_phase_5b_request_packet_builder_e2e.py",
        "scripts/validate_original_phase_5a_client_side_workflow_shell.py",
        "scripts/validate_original_phase_5a_client_side_workflow_e2e.py",
        "scripts/validate_original_phase_4_hosted_dashboard_polish.py",
        "scripts/validate_original_phase_4_hosted_dashboard_e2e.py",
        "scripts/validate_backend_phase_4d_schema_previews.py",
        "scripts/validate_backend_phase_4d_disabled_ui.py",
        "scripts/validate_backend_phase_4d_strategic_build.py",
        "scripts/validate_backend_phase_4d_strategic_e2e.py",
        "scripts/validate_backend_phase_4c_snapshot.py",
        "scripts/validate_backend_phase_4a_foundation.py",
        "scripts/validate_backend_phase_4a_e2e.py",
        "scripts/validate_interface_phase_3_dashboard.py",
        "scripts/validate_interface_phase_3_e2e.py",
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

    for path in changed:
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                errors.append(f"Forbidden changed path: {path}")
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            errors.append(f"Unexpected changed path: {path}")

    for report_name in [
        "original_plus1c_readiness_scoring_report.md",
        "original_plus1c_contract_qa_report.md",
        "original_plus1c_no_go_decision_report.md",
        "original_plus1c_dependency_gap_report.md",
        "original_plus1c_validator_confidence_report.md",
        "original_plus1c_design_report.md",
        "original_plus1c_safety_report.md",
        "original_plus1c_acceptance_report.md",
    ]:
        path = REPORTS / report_name
        check(path.exists(), f"missing report: {report_name}", errors)
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            check("PASS_WITH_HIGH_CONFIDENCE" in text, f"report missing PASS_WITH_HIGH_CONFIDENCE: {report_name}", errors)

    if errors:
        print("\nVALIDATION_FAIL")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("ORIGINAL_PLUS1C_READINESS_SCORING_CONTRACT_QA_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    raise SystemExit(main())
