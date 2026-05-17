#!/usr/bin/env python3
from pathlib import Path

from _validator_runner import run_validator_cmd

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def main():
    validators = [
        "python3 scripts/validate_mvp31_demo_session_capture_review_loop.py",
        "python3 scripts/validate_mvp30_pitchable_release_package_e2e.py",
        "python3 scripts/validate_mvp29_guided_product_demo_control_room_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run_validator_cmd(v, ROOT)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts" / "validate_mvp31_demo_session_capture_review_loop.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "DEMO_SESSION_CAPTURE_REVIEW_LOOP_READY",
        "PASS_WITH_MANUAL_SESSION_CAPTURE_AND_OPTIONAL_GATED_IMPORT",
        "DEMO_SESSION_CAPTURE_WORKSPACE_READY",
        "EXTERNAL_REVIEW_FEEDBACK_LOOP_READY",
        "REVIEWER_PERSONA_SESSION_READY",
        "FEEDBACK_PACKET_DRAFT_READY",
        "OPTIONAL_FEEDBACK_IMPORT_GATED",
        "TOKEN_IN_MEMORY_ONLY",
        "NO_AUTOMATED_OUTREACH",
        "NO_FAKE_REVIEWER_RESULTS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_RELEASE_REVIEW_METRICS_AND_SIGNAL_DASHBOARD",
        "demo_session_capture_workspace_model.json",
        "external_reviewer_persona_session_model.json",
        "demo_session_notes_model.json",
        "review_feedback_packet_draft_model.json",
        "demo_follow_up_decision_model.json",
        "mvp31_demo_session_capture_review_loop_model.json",
        "mvp31_acceptance_report.md",
        "mvp31_validator_wall_review.md",
        '"/api/feedback?action=import"',
        "mvp31-submit-feedback-packet",
        "mvp31-use-token-memory",
        "mvp31-clear-token",
        "mvp31-check-feedback-endpoint",
        "mvp31-feedback-token",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"DIRECT_VALIDATOR_MVP31_CHECK_MISSING: {item}")

    bad_fragments = [
        "send" "Email(",
        "email" "js",
        "mail" "to:",
        "Auto" " Follow-Up",
        "Start" " Outreach",
        "Automate" " Review",
        "submit" " on page load",
        "local" "Storage.setItem",
        "session" "Storage.setItem",
        "document." "cookie =",
        "indexed" "DB.open",
        "create" "Client(",
        "supabase." "createClient",
    ]
    for item in bad_fragments:
        if item.lower() in direct.lower():
            fail(f"DIRECT_BAD_MVP31_FRAGMENT_REMAINS: {item}")

    print("MVP31_DEMO_SESSION_CAPTURE_REVIEW_LOOP_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
