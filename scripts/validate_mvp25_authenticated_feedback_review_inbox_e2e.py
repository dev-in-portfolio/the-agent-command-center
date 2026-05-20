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
        "python3 scripts/validate_mvp25_authenticated_feedback_review_inbox.py",
        "python3 scripts/validate_mvp24_beta_feedback_import_workspace.py",
        "python3 scripts/validate_mvp23_feedback_import_smoke_test.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")


    # Wall awareness check
    wall = Path(ROOT / "scripts/validate_phase5_plus1_master_validator_wall.py").read_text()
    required_wall = [
        "MVP-25",
        "AUTHENTICATED FEEDBACK REVIEW INBOX",
        "FEEDBACK LIST READ API",
        "FEEDBACK DETAIL READ API",
        "OWNER-SCOPED RLS READS",
        "FEEDBACK SYNTHESIS QUEUE",
        "READ ONLY REVIEW WORKFLOW",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_FEEDBACK_SYNTHESIS_AND_PRODUCT_DECISION_WORKFLOW",
        "scripts/validate_mvp25_authenticated_feedback_review_inbox.py",
        "scripts/validate_mvp25_authenticated_feedback_review_inbox.py",
        "mvp25_acceptance_report.md",
        "mvp25_validator_wall_review.md",
        "mvp25_authenticated_feedback_review_inbox_model.json",
        "supabase_feedback_read_client.js",
    ]
    for w in required_wall:
        if w not in wall:
            fail(f"Master validator wall missing MVP-25 awareness: {w}")

    # Direct validator check
    direct = Path(ROOT / "scripts/validate_mvp25_authenticated_feedback_review_inbox.py").read_text()
    required_direct = [
        "supabase_feedback_read_client.js",
        "feedback.js",
        'action === "list"',
        'action === "get"',
        "getAuthContext",
        "bearerToken",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "api.github.com",
        "api.netlify.com",
        "service_role_used",
        "browser_direct_supabase_calls",
        "DASHBOARD_DIRECT_SUPABASE_FETCH_BLOCKED",
        "DASHBOARD_SUPABASE_CREATE_CLIENT_BLOCKED",
        "EXACT_SUPABASE_EXECUTABLE_PATTERN_SCAN",
        "SUPABASE_LABEL_TEXT_DOES_NOT_SUPPRESS_SCAN",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "supabase.co",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
        "createClient(",
        "supabase.createClient",
    ]
    for d in required_direct:
        if d not in direct:
            fail(f"Direct validator missing check: {d}")

    print("MVP25_AUTHENTICATED_FEEDBACK_REVIEW_INBOX_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    main()
