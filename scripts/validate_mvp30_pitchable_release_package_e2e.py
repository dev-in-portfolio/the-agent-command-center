#!/usr/bin/env python3
from pathlib import Path

from _validator_runner import run_validator_cmd

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def main():
    validators = [
        "python3 scripts/validate_mvp30_pitchable_release_package.py",
        "python3 scripts/validate_mvp29_guided_product_demo_control_room.py",
        "python3 scripts/validate_mvp28_operator_roadmap_prioritization.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run_validator_cmd(v, ROOT)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    direct = Path(ROOT / "scripts" / "validate_mvp30_pitchable_release_package.py").read_text(encoding="utf-8", errors="replace")
    required_direct = [
        "PITCHABLE_RELEASE_PACKAGE_READY",
        "PASS_WITH_SAFE_RELEASE_EXPORTS",
        "PRODUCT_NARRATIVE_EXPORT_READY",
        "RELEASE_CAPABILITY_MAP_READY",
        "AUDIENCE_VARIANTS_READY",
        "DEMO_WALKTHROUGH_EXPORT_READY",
        "TECHNICAL_ARCHITECTURE_SUMMARY_READY",
        "SAFETY_BOUNDARY_SUMMARY_READY",
        "SAFE_DEMO_MODE",
        "NO_FAKE_LIVE_TEST_CLAIMS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_DEMO_SESSION_CAPTURE_AND_EXTERNAL_REVIEW_LOOP",
        "mvp30_release_overview.md",
        "mvp30_product_narrative.md",
        "mvp30_demo_walkthrough.md",
        "mvp30_technical_architecture_summary.md",
        "mvp30_safety_boundary_summary.md",
        "mvp30_capability_map.md",
        "mvp30_recruiter_version.md",
        "mvp30_founder_operator_version.md",
        "mvp30_technical_reviewer_version.md",
        "mvp30_release_manifest.json",
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        "browser_persistence_enabled",
        "deploy_merge_push_controls_enabled",
        "no_fake_live_test_claims",
        "MVP30_PITCHABLE_RELEASE_PACKAGE_VALIDATION_PASS",
    ]
    for item in required_direct:
        if item not in direct:
            fail(f"Direct validator missing check: {item}")

    print("MVP30_PITCHABLE_RELEASE_PACKAGE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
