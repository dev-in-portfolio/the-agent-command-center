#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def run(cmd):
    try:
        res = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True, cwd=ROOT)
        return res.stdout, res.stderr, res.returncode
    except Exception as exc:
        fail(f"Execution error for {cmd}: {exc}")


def main():
    validators = [
        "python3 scripts/validate_mvp28_operator_roadmap_prioritization.py",
        "python3 scripts/validate_mvp27_feedback_to_request_conversion_e2e.py",
        "python3 scripts/validate_mvp26_feedback_synthesis_product_decision_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts" / "validate_mvp28_operator_roadmap_prioritization.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "OPERATOR_ROADMAP_PRIORITIZATION_BOARD_READY",
        "PASS_WITH_READ_ONLY_ROADMAP_WORKFLOW",
        "FEEDBACK_SIGNALS_TO_ROADMAP_READY",
        "PRODUCT_DECISION_LANES_READY",
        "PRIORITY_SCORING_READY",
        "IMPACT_EFFORT_CONFIDENCE_MATRIX_READY",
        "READ_ONLY_ROADMAP_WORKFLOW",
        "SERVICE ROLE NOT USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_GUIDED_PRODUCT_DEMO_CONTROL_ROOM",
        "operator_roadmap_board_model.json",
        "roadmap_priority_scoring_model.json",
        "roadmap_lane_model.json",
        "feedback_request_roadmap_link_model.json",
        "mvp28_operator_roadmap_prioritization_model.json",
        "mvp28_acceptance_report.md",
        "mvp28_validator_wall_review.md",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "browser_direct_supabase_calls",
        "service_role_used",
        "automation_enabled",
        "MVP28_OPERATOR_ROADMAP_PRIORITIZATION_VALIDATION_PASS",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"Direct validator missing check: {item}")

    print("MVP28_OPERATOR_ROADMAP_PRIORITIZATION_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
