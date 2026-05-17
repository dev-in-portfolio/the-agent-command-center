#!/usr/bin/env python3
from pathlib import Path

from _validator_runner import run_validator_cmd

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def main():
    validators = [
        "python3 scripts/validate_mvp29_guided_product_demo_control_room.py",
        "python3 scripts/validate_mvp28_operator_roadmap_prioritization_e2e.py",
        "python3 scripts/validate_mvp27_feedback_to_request_conversion_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run_validator_cmd(v, ROOT)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts" / "validate_mvp29_guided_product_demo_control_room.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "GUIDED_PRODUCT_DEMO_CONTROL_ROOM_READY",
        "PASS_WITH_SAFE_DEMO_MODE",
        "ROLE_BASED_DEMO_PATHS_READY",
        "OPERATOR_STORYLINE_READY",
        "DEMO_READINESS_SCORECARD_READY",
        "PITCHABLE_PRODUCT_WALKTHROUGH_READY",
        "SAFE_DEMO_MODE",
        "NO_FAKE_LIVE_TEST_CLAIMS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_REVIEW_DEMO_CONTROL_ROOM_AND_PREPARE_PITCHABLE_RELEASE",
        "guided_product_demo_control_room_model.json",
        "demo_persona_path_model.json",
        "demo_storyline_model.json",
        "demo_readiness_scorecard_model.json",
        "mvp29_guided_product_demo_control_room_model.json",
        "mvp29_acceptance_report.md",
        "mvp29_validator_wall_review.md",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "browser_direct_supabase_calls",
        "service_role_used",
        "automation_enabled",
        "no_fake_live_test_claims",
        "MVP29_GUIDED_PRODUCT_DEMO_CONTROL_ROOM_VALIDATION_PASS",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"Direct validator missing check: {item}")

    print("MVP29_GUIDED_PRODUCT_DEMO_CONTROL_ROOM_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
