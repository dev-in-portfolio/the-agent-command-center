#!/usr/bin/env python3
import subprocess
from pathlib import Path

subprocess._USE_POSIX_SPAWN = False
from _validator_runner import run_validator_cmd

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def run(cmd):
    return run_validator_cmd(cmd, ROOT)


def main():
    validators = [
        "python3 scripts/validate_mvp27_feedback_to_request_conversion.py",
        "python3 scripts/validate_mvp26_feedback_synthesis_product_decision_e2e.py",
        "python3 scripts/validate_mvp25_authenticated_feedback_review_inbox_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts/validate_mvp27_feedback_to_request_conversion.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE_READY",
        "PASS_WITH_OPTIONAL_SERVER_GATED_REQUEST_CREATE",
        "REQUEST_DRAFT_FROM_FEEDBACK_READY",
        "DECISION_TO_REQUEST_PAYLOAD_PREVIEW_READY",
        "CONTROLLED_REQUEST_CREATE_OPTIONAL",
        "TOKEN_IN_MEMORY_ONLY",
        "REQUEST_WRITES_SERVER_GATED",
        "NEXT_STEP_BUILD_OPERATOR_ROADMAP_PRIORITIZATION_BOARD",
        "feedback_to_request_conversion_workspace_model.json",
        "request_draft_from_feedback_model.json",
        "feedback_decision_to_request_payload_model.json",
        "controlled_request_creation_from_feedback_model.json",
        "mvp27_feedback_to_request_conversion_model.json",
        "mvp27_acceptance_report.md",
        "mvp27_validator_wall_review.md",
        "POST /api/requests?action=create",
        "manual",
        "fetch('/api/requests?action=create'",
        'fetch("/api/requests?action=create"',
        "axios.post('/api/requests?action=create'",
        'axios.post("/api/requests?action=create"',
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "browser_direct_supabase_calls",
        "service_role_used",
        "approve_enabled",
        "execute_enabled",
        "MVP27_FEEDBACK_TO_REQUEST_CONVERSION_VALIDATION_PASS",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"Direct validator missing check: {item}")

    print("MVP27_FEEDBACK_TO_REQUEST_CONVERSION_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
