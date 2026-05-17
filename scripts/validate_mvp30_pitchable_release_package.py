#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
RELEASE_DIR = ROOT / "09_exports" / "release_package"
SCRIPT_DIR = ROOT / "scripts"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        fail(f"Unable to read {path}: {exc}")


def ensure_exists(path):
    if not path.exists():
        fail(f"Missing required file: {path}")


def assert_contains(text, needle, label):
    if needle not in text:
        fail(f"Missing {label}: {needle}")


def walk_json_flags(path):
    data = json.loads(read_text(path))
    expected_true = [
        "release_package_ready",
        "product_narrative_export_ready",
        "capability_map_ready",
        "audience_variants_ready",
        "demo_walkthrough_export_ready",
        "safe_demo_mode",
        "no_fake_live_test_claims",
    ]
    for key in expected_true:
        if key in data and data[key] is not True:
            fail(f"{path.name} gate not true: {key}")

    expected_false = [
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "automation_enabled",
        "deploy_merge_push_controls_enabled",
    ]
    for key in expected_false:
        if key in data and data[key] is not False:
            fail(f"{path.name} forbidden flag not false: {key}")


def main():
    required_models = [
        UI_MODEL_DIR / "pitchable_release_package_model.json",
        UI_MODEL_DIR / "product_narrative_export_model.json",
        UI_MODEL_DIR / "release_capability_map_model.json",
        UI_MODEL_DIR / "release_audience_variant_model.json",
        UI_MODEL_DIR / "demo_walkthrough_export_model.json",
        DIST_DIR / "mvp30_pitchable_release_package_model.json",
    ]
    required_release_files = [
        RELEASE_DIR / "mvp30_release_overview.md",
        RELEASE_DIR / "mvp30_product_narrative.md",
        RELEASE_DIR / "mvp30_demo_walkthrough.md",
        RELEASE_DIR / "mvp30_technical_architecture_summary.md",
        RELEASE_DIR / "mvp30_safety_boundary_summary.md",
        RELEASE_DIR / "mvp30_capability_map.md",
        RELEASE_DIR / "mvp30_recruiter_version.md",
        RELEASE_DIR / "mvp30_founder_operator_version.md",
        RELEASE_DIR / "mvp30_technical_reviewer_version.md",
        RELEASE_DIR / "mvp30_release_packet_index.md",
        RELEASE_DIR / "mvp30_release_manifest.json",
    ]
    required_reports = [
        REPORT_DIR / "mvp30_pitchable_release_package_report.md",
        REPORT_DIR / "mvp30_product_narrative_export_report.md",
        REPORT_DIR / "mvp30_capability_map_report.md",
        REPORT_DIR / "mvp30_audience_variants_report.md",
        REPORT_DIR / "mvp30_demo_walkthrough_export_report.md",
        REPORT_DIR / "mvp30_release_manifest_report.md",
        REPORT_DIR / "mvp30_security_boundary_report.md",
        REPORT_DIR / "mvp30_next_product_step_report.md",
        REPORT_DIR / "mvp30_validator_quality_report.md",
        REPORT_DIR / "mvp30_acceptance_report.md",
        REPORT_DIR / "mvp30_validator_wall_review.md",
    ]
    for path in required_models + required_release_files + required_reports:
        ensure_exists(path)

    acceptance = read_text(REPORT_DIR / "mvp30_acceptance_report.md")
    for marker in [
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
    ]:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    index = read_text(DIST_DIR / "index.html")
    for marker in [
        "MVP-30",
        "PITCHABLE RELEASE PACKAGE",
        "PRODUCT NARRATIVE EXPORT",
        "RELEASE CAPABILITY MAP",
        "AUDIENCE VARIANTS",
        "DEMO WALKTHROUGH EXPORT",
        "TECHNICAL ARCHITECTURE SUMMARY",
        "SAFETY BOUNDARY SUMMARY",
        "RECRUITER VERSION",
        "FOUNDER OPERATOR VERSION",
        "TECHNICAL REVIEWER VERSION",
        "SAFE DEMO MODE",
        "NO FAKE LIVE TEST CLAIMS",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_DEMO_SESSION_CAPTURE_AND_EXTERNAL_REVIEW_LOOP",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(index, marker, f"index marker {marker}")

    forbidden_labels = [
        "Deploy",
        "Merge",
        "Push",
        "Create PR",
        "Execute",
        "Approve",
        "Start Automation",
        "Apply Migration",
        "Enable Writes",
        "Enable Feedback Persistence",
        "Submit to Supabase",
        "Save to Database",
    ]
    section_match = re.search(
        r'<details[^>]*id="mvp30-pitchable-release-package-product-narrative".*?</details>',
        index,
        re.S,
    )
    if not section_match:
        fail("Missing MVP-30 release package section block in index.html")
    section_html = section_match.group(0)
    for label in forbidden_labels:
        if label in section_html:
            fail(f"Forbidden enabled button label in MVP-30 section: {label}")

    for path in required_models:
        walk_json_flags(path)
    manifest = json.loads(read_text(RELEASE_DIR / "mvp30_release_manifest.json"))
    for key in [
        "release_package_ready",
        "product_narrative_export_ready",
        "capability_map_ready",
        "audience_variants_ready",
        "demo_walkthrough_export_ready",
    ]:
        if manifest.get(key) is not True:
            fail(f"Release manifest gate not true: {key}")
    for key in [
        "safe_demo_mode",
        "no_fake_live_test_claims",
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "automation_enabled",
        "deploy_merge_push_controls_enabled",
    ]:
        if key not in manifest:
            fail(f"Release manifest missing field: {key}")
    for key in [
        "service_role_used",
        "browser_direct_supabase_calls",
        "browser_persistence_enabled",
        "update_enabled",
        "delete_enabled",
        "approve_enabled",
        "execute_enabled",
        "automation_enabled",
        "deploy_merge_push_controls_enabled",
    ]:
        if manifest[key] is not False:
            fail(f"Release manifest forbidden flag not false: {key}")
    if manifest["safe_demo_mode"] is not True or manifest["no_fake_live_test_claims"] is not True:
        fail("Release manifest safety flags are not true")

    release_docs = [
        RELEASE_DIR / "mvp30_release_overview.md",
        RELEASE_DIR / "mvp30_product_narrative.md",
        RELEASE_DIR / "mvp30_demo_walkthrough.md",
        RELEASE_DIR / "mvp30_technical_architecture_summary.md",
        RELEASE_DIR / "mvp30_safety_boundary_summary.md",
        RELEASE_DIR / "mvp30_capability_map.md",
        RELEASE_DIR / "mvp30_recruiter_version.md",
        RELEASE_DIR / "mvp30_founder_operator_version.md",
        RELEASE_DIR / "mvp30_technical_reviewer_version.md",
        RELEASE_DIR / "mvp30_release_packet_index.md",
    ]
    for path in release_docs:
        content = read_text(path)
        if "secret" in content.lower() or "token" in content.lower() and "token in in-memory only" not in content.lower():
            # Only the package text should remain generic; no secrets/env values should appear.
            if "token" in content.lower():
                fail(f"Unexpected token-related content in {path}")
        for bad in [
            "live test passed",
            "service role key",
            "localStorage",
            "sessionStorage",
            "indexedDB",
        ]:
            if bad.lower() in content.lower():
                fail(f"Forbidden content in {path}: {bad}")

    renderer = read_text(ROOT / "13_web_dashboard" / "dashboard_renderer.py")
    for marker in [
        "MVP-30",
        "PITCHABLE RELEASE PACKAGE",
        "PRODUCT NARRATIVE EXPORT",
        "RELEASE CAPABILITY MAP",
        "AUDIENCE VARIANTS",
        "DEMO WALKTHROUGH EXPORT",
        "TECHNICAL ARCHITECTURE SUMMARY",
        "SAFETY BOUNDARY SUMMARY",
        "RECRUITER VERSION",
        "FOUNDER OPERATOR VERSION",
        "TECHNICAL REVIEWER VERSION",
        "NEXT_STEP_BUILD_DEMO_SESSION_CAPTURE_AND_EXTERNAL_REVIEW_LOOP",
    ]:
        assert_contains(renderer, marker, f"renderer marker {marker}")

    runtime_files = [
        ROOT / "13_web_dashboard" / "static" / "dashboard.js",
        DIST_DIR / "static" / "dashboard.js",
        DIST_DIR / "index.html",
        DIST_DIR / "print.html",
    ]
    forbidden_runtime_tokens = [
        "localStorage.setItem",
        "sessionStorage.setItem",
        "document.cookie =",
        "indexedDB.open",
        "createClient(",
        "supabase.createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
    ]
    for path in runtime_files:
        content = read_text(path)
        for token in forbidden_runtime_tokens:
            if token in content:
                fail(f"Forbidden runtime token in {path}: {token}")

    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, RELEASE_DIR, SCRIPT_DIR, ROOT / "netlify" / "functions"]
    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
                continue
            content = read_text(path)
            if "scripts/validate_" in str(path):
                continue
            if "sb_secret_" in content or "postgresql://postgres:" in content or "SUPABASE_SERVICE_ROLE_KEY=sb_" in content:
                fail(f"Forbidden secret pattern in {path}")

    print("MVP30_PITCHABLE_RELEASE_PACKAGE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
