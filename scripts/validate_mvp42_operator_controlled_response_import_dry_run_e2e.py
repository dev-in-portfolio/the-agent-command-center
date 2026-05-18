#!/usr/bin/env python3
# MVP42_E2E_VALIDATOR_FULL_SAFETY_CONTRACT

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# MVP42_E2E_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP42_E2E_DIRECT_VALIDATOR_RUN_CHECK
# MVP42_E2E_MVP41_DIRECT_CHAIN_CHECK
# MVP42_E2E_MVP40_DIRECT_CHAIN_CHECK
# MVP42_E2E_LIVE_PAGE_CONTEXT_SCAN_CHECK
# MVP42_E2E_HELPER_TEST_CHECK
# MVP42_E2E_MASTER_WALL_CHECK

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def run_script(name: str) -> str:
    path = ROOT / "scripts" / name
    if not path.is_file():
        return f"[FAIL] Script not found: {name}"
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return "[FAIL] Timeout"
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return f"[FAIL] Exit code {result.returncode}\n{stdout}\n{stderr}"
    return result.stdout.strip()


def expect_contains(output: str, marker: str, label: str) -> None:
    if marker not in output:
        FAILURES.append(f"{label} missing marker: {marker}")
        print(f"  [FAIL] {label}")
        print(output)
    else:
        print(f"  [PASS] {label}")


def main() -> None:
    print("MVP-42 E2E Validation")
    print()

    print("Phase 1 — MVP-42 Direct Validator")
    direct_output = run_script("validate_mvp42_operator_controlled_response_import_dry_run.py")
    expect_contains(direct_output, "MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_VALIDATION_PASS", "MVP-42 direct validator")

    print()
    print("Phase 2 — MVP-41 Direct Validator")
    mvp41_output = run_script("validate_mvp41_controlled_reviewer_response_intake_blueprint.py")
    expect_contains(mvp41_output, "MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT_VALIDATION_PASS", "MVP-41 direct validator")

    print()
    print("Phase 3 — MVP-40 Direct Validator")
    mvp40_output = run_script("validate_mvp40_reviewer_response_capture_readiness_lock.py")
    expect_contains(mvp40_output, "MVP40_REVIEWER_RESPONSE_CAPTURE_READINESS_LOCK_VALIDATION_PASS", "MVP-40 direct validator")

    print()
    print("Phase 4 — Live-Page Context-Aware Scan")
    live_scan_output = run_script("validate_live_page_context_aware_control_scan.py")
    expect_contains(live_scan_output, "LIVE_PAGE_CONTEXT_AWARE_CONTROL_SCAN_PASS", "Live-page context scan")

    print()
    print("Phase 5 — Validation Helper Test")
    helper_output = run_script("test_validation_helpers_control_scan.py")
    expect_contains(helper_output, "VALIDATION_HELPERS_CONTROL_SCAN_TEST_PASS", "Validation helper test")

    print()
    print("Phase 6 — Master Validator Wall")
    wall_output = run_script("validate_phase5_plus1_master_validator_wall.py")
    expect_contains(wall_output, "PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS", "Master validator wall")

    print()
    print("Phase 7 — Direct Validator Source Self-Check")
    source = (ROOT / "scripts" / "validate_mvp42_operator_controlled_response_import_dry_run.py").read_text(encoding="utf-8", errors="replace")
    required_markers = [
        "MVP42_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT",
        "MVP42_NO_PUBLIC_ENDPOINT_CHECK",
        "MVP42_NO_LIVE_INTAKE_CHECK",
        "MVP42_NO_PUBLIC_RESPONSE_SUBMISSION_CHECK",
        "MVP42_NO_REVIEWER_RESPONSE_WRITES_CHECK",
        "MVP42_NO_RESPONSE_CAPTURE_ENABLED_CHECK",
        "MVP42_NO_RESPONSE_PERSISTENCE_ENABLED_CHECK",
        "MVP42_NO_REAL_IMPORT_CHECK",
        "MVP42_NO_AUTOMATIC_IMPORT_CHECK",
        "MVP42_NO_EMAIL_SENDING_CHECK",
        "MVP42_NO_REVIEWER_CONTACT_CHECK",
        "MVP42_NO_AUTOMATED_OUTREACH_CHECK",
        "MVP42_NO_LIVE_WRITES_CHECK",
        "MVP42_NO_PUBLIC_WRITES_CHECK",
        "MVP42_NO_TOKEN_INPUT_CHECK",
        "MVP42_NO_SECRETS_EXPOSED_CHECK",
        "MVP42_NO_SERVICE_ROLE_CHECK",
        "MVP42_NO_BROWSER_PERSISTENCE_CHECK",
        "MVP42_NO_DIRECT_SUPABASE_CHECK",
        "MVP42_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK",
        "MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_EXPORT_ARTIFACTS_CHECK",
        "MVP42_NO_WHOLE_FILE_SAFETY_LABEL_SKIP",
        "operator_controlled_response_import_dry_run_ready",
        "dry_run_response_import_packet_ready",
        "operator_import_preview_queue_ready",
        "dry_run_validation_result_ready",
        "response_normalization_preview_ready",
        "response_to_feedback_conversion_preview_ready",
        "dry_run_audit_rollback_blueprint_ready",
        "public_endpoint_enabled",
        "live_intake_enabled",
        "public_response_submission_enabled",
        "reviewer_response_write_enabled",
        "response_capture_enabled",
        "response_persistence_enabled",
        "real_import_enabled",
        "automatic_import_enabled",
        "email_sending_enabled",
        "reviewer_contact_enabled",
        "automated_outreach_enabled",
        "contact_automation_enabled",
        "live_write_enabled",
        "public_write_enabled",
        "token_input_enabled",
        "secrets_exposed",
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "automation_enabled",
        "deploy_controls_enabled",
        "launch_automation_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "deploy_merge_push_controls_enabled",
    ]
    missing = [marker for marker in required_markers if marker not in source]
    if missing:
        FAILURES.append(f"Direct validator source missing markers: {', '.join(missing)}")
        print(f"  [FAIL] Direct validator source missing markers: {', '.join(missing)}")
    else:
        print("  [PASS] Direct validator source contract verified")

    if FAILURES:
        print("MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_E2E_VALIDATION_FAIL")
        for failure in FAILURES:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
