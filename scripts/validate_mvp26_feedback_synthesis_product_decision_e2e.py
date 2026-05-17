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
        "python3 scripts/validate_mvp26_feedback_synthesis_product_decision.py",
        "python3 scripts/validate_mvp25_authenticated_feedback_review_inbox_e2e.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts/validate_mvp26_feedback_synthesis_product_decision.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "FEEDBACK_SYNTHESIS_PRODUCT_DECISION_WORKFLOW_READY",
        "PASS_WITH_READ_ONLY_MANUAL_SYNTHESIS",
        "FEEDBACK_SYNTHESIS_WORKSPACE_READY",
        "THEME_CLUSTERING_READY",
        "PRODUCT_DECISION_CARDS_READY",
        "SIGNAL_STRENGTH_SCORING_READY",
        "OWNER_SCOPED_FEEDBACK_READS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE",
        "feedback_synthesis_workspace_model.json",
        "feedback_theme_cluster_model.json",
        "product_decision_card_model.json",
        "feedback_to_product_signal_model.json",
        "mvp26_feedback_synthesis_product_decision_model.json",
        "mvp26_acceptance_report.md",
        "mvp26_validator_wall_review.md",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "api.github.com",
        "api.netlify.com",
        "createClient(",
        "supabase.createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
        "browser_direct_supabase_calls",
        "service_role_used",
        "MVP26_FEEDBACK_SYNTHESIS_PRODUCT_DECISION_VALIDATION_PASS",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"Direct validator missing check: {item}")

    print("MVP26_FEEDBACK_SYNTHESIS_PRODUCT_DECISION_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
