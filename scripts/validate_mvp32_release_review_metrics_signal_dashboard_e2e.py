#!/usr/bin/env python3
import subprocess
from pathlib import Path

from _validator_runner import run_validator_cmd

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def run_with_timeout(cmd, timeout=120):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"TIMEOUT after {timeout}s: {cmd}", 1


def main():
    # Direct validators
    direct_validators = [
        "python3 scripts/validate_mvp32_release_review_metrics_signal_dashboard.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]
    for v in direct_validators:
        stdout, stderr, code = run_with_timeout(v, 120)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts" / "validate_mvp32_release_review_metrics_signal_dashboard.py").read_text(
        encoding="utf-8", errors="replace"
    )

    required_checks = [
        "no_fake_metrics",
        "no_fake_reviewer_results",
        "email_sending_enabled",
        "browser_persistence_enabled",
        "service_role_used",
        "browser_direct_supabase_calls",
        "deploy_merge_push_controls_enabled",
        "mvp32_release_review_signal_manifest.json",
        "mvp32_reviewer_signal_summary.md",
        "mvp32_demo_session_signal_summary.md",
        "mvp32_release_readiness_scorecard.md",
        "mvp32_product_decision_signal_rollup.md",
        "mvp32_release_review_signal_packet.md",
    ]
    for item in required_checks:
        if item not in direct:
            fail(f"DIRECT_VALIDATOR_MVP32_CHECK_MISSING: {item}")

    bad_fragments = [
        "send" "Email(",
        "email" "js",
        "mail" "to:",
        "local" "Storage.setItem",
        "session" "Storage.setItem",
        "document." "cookie =",
        "indexed" "DB.open",
        "create" "Client(",
        "supabase." "createClient",
    ]
    for item in bad_fragments:
        if item.lower() in direct.lower():
            fail(f"DIRECT_BAD_MVP32_FRAGMENT_REMAINS: {item}")
    
    print("MVP32_RELEASE_REVIEW_METRICS_SIGNAL_DASHBOARD_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
