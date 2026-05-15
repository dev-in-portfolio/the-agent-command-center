#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Unable to read {path}: {exc}")


def ensure_exists(path):
    if not path.exists():
        fail(f"Missing required file: {path}")


def assert_contains(text, needle, label):
    if needle not in text:
        fail(f"Missing {label}: {needle}")


def main():
    required_files = [
        SUPABASE_DIR / "controlled_migration_apply_model.json",
        SUPABASE_DIR / "post_migration_verification_model.json",
        SUPABASE_DIR / "authenticated_reads_enablement_model.json",
        SUPABASE_DIR / "migration_readiness_model.json",
        SUPABASE_DIR / "request_read_model.json",
        ROOT / "netlify/functions/request-readiness-status.js",
        ROOT / "netlify/functions/requests.js",
        ROOT / "netlify/functions/backend-manifest.js",
        ROOT / "13_web_dashboard/build_mvp6_controlled_migration_authenticated_reads.py",
        DIST_DIR / "mvp6_controlled_migration_reads_model.json",
        REPORT_DIR / "mvp6_controlled_migration_apply_report.md",
        REPORT_DIR / "mvp6_migration_apply_result_report.md",
        REPORT_DIR / "mvp6_post_migration_verification_report.md",
        REPORT_DIR / "mvp6_authenticated_reads_enablement_report.md",
        REPORT_DIR / "mvp6_feature_flag_enablement_report.md",
        REPORT_DIR / "mvp6_security_boundary_report.md",
        REPORT_DIR / "mvp6_next_product_step_report.md",
        REPORT_DIR / "mvp6_acceptance_report.md",
        REPORT_DIR / "mvp6_validator_wall_review.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-6",
        "CONTROLLED MIGRATION APPLY",
        "SCHEMA AND RLS MIGRATION",
        "POST-MIGRATION VERIFICATION",
        "AUTHENTICATED READS ENABLEMENT",
        "REQUEST API READS ENABLED TARGET",
        "REQUEST API WRITES STILL DISABLED",
        "SERVICE ROLE NOT EXPOSED TO BROWSER",
        "WRITES REQUIRE SEPARATE REVIEW",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_VERIFY_AUTHENTICATED_READS_WITH_REAL_USER_TOKEN",
        "Controlled Migration Apply Panel",
        "Post-Migration Verification Panel",
        "Authenticated Reads Enablement Panel",
        "Feature Flag Panel",
        "Safety Boundary Panel",
        "Next Product Decision Panel",
        "Copy migration readiness checklist",
        "Copy manual migration review checklist",
        "Copy authenticated reads checklist",
        "Copy request read adapter contract",
        "Copy MVP-6 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp6_acceptance_report.md")
    for text in [
        "CONTROLLED_MIGRATION_AUTHENTICATED_READS_READY",
        "PASS_WITH_CONDITIONAL_LIVE_DEPENDENCY",
        "NEXT_STEP_VERIFY_AUTHENTICATED_READS_WITH_REAL_USER_TOKEN",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    model = json.loads(read_text(DIST_DIR / "mvp6_controlled_migration_reads_model.json"))
    controlled = model.get("controlled_migration_apply_model", {})
    verification = model.get("post_migration_verification_model", {})
    auth_reads = model.get("authenticated_reads_enablement_model", {})

    if controlled.get("apply_mode") != "controlled_cli_apply":
        fail("controlled migration apply mode must be controlled_cli_apply")
    if controlled.get("migration_apply_allowed_in_this_phase") is not True:
        fail("controlled migration apply must be allowed in this phase")
    if verification.get("verification_mode") != "schema_metadata_only":
        fail("post migration verification must be schema_metadata_only")
    if verification.get("no_row_data_required") is not True:
        fail("post migration verification must not require row data")
    if auth_reads.get("request_api_reads_target") != "enabled":
        fail("authenticated reads target must be enabled")
    if auth_reads.get("request_api_writes_target") != "disabled":
        fail("authenticated writes target must remain disabled")
    if auth_reads.get("service_role_used_for_reads") is not False:
        fail("service role must not be used for reads")
    if auth_reads.get("anon_key_plus_user_token") is not True:
        fail("anon key plus user token must be true")

    request_readiness = read_text(ROOT / "netlify/functions/request-readiness-status.js")
    requests_js = read_text(ROOT / "netlify/functions/requests.js")
    builder = read_text(ROOT / "13_web_dashboard/build_mvp6_controlled_migration_authenticated_reads.py")
    backend_manifest = read_text(ROOT / "netlify/functions/backend-manifest.js")

    file_map = {
        "controlled_migration_apply_model.json": read_text(SUPABASE_DIR / "controlled_migration_apply_model.json"),
        "post_migration_verification_model.json": read_text(SUPABASE_DIR / "post_migration_verification_model.json"),
        "authenticated_reads_enablement_model.json": read_text(SUPABASE_DIR / "authenticated_reads_enablement_model.json"),
        "request-readiness-status.js": request_readiness,
        "requests.js": requests_js,
        "build_mvp6_controlled_migration_authenticated_reads.py": builder,
        "backend-manifest.js": backend_manifest,
        "mvp6_controlled_migration_reads_model.json": read_text(DIST_DIR / "mvp6_controlled_migration_reads_model.json"),
    }

    forbidden_patterns = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "api.github.com",
        "api.netlify.com",
        "os.system",
        "exec(",
        "spawn(",
        "execSync(",
        "child_process",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexeddb",
    ]
    for name, text in file_map.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    if "process.env" in file_map["request-readiness-status.js"]:
        fail("request-readiness-status.js must not read env directly")
    if "process.env" in file_map["build_mvp6_controlled_migration_authenticated_reads.py"]:
        fail("build_mvp6_controlled_migration_authenticated_reads.py must not read env directly")

    for marker in [
        "CONTROLLED_MIGRATION_APPLY_READY",
        "APPLY_SCHEMA_AND_RLS_ONLY",
        "ENABLE_AUTHENTICATED_READS_ONLY",
        "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(file_map["controlled_migration_apply_model.json"], marker, "controlled migration model marker")

    for marker in [
        "POST_MIGRATION_SCHEMA_VERIFICATION_READY",
        "RLS_METADATA_VERIFICATION_REQUIRED",
        "NO_ROW_DATA_REQUIRED",
        "NO_SECRET_OUTPUT",
    ]:
        assert_contains(file_map["post_migration_verification_model.json"], marker, "post migration verification marker")

    for marker in [
        "CONTROLLED_MIGRATION_APPLY_READY",
        "AUTHENTICATED_READS_ENABLEMENT_READY",
        "REQUEST_API_READS_ENABLED_TARGET",
        "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
    ]:
        assert_contains(file_map["authenticated_reads_enablement_model.json"], marker, "authenticated reads marker")

    assert_contains(request_readiness, "controlled_migration_apply_ready", "request readiness status field")
    assert_contains(request_readiness, "post_migration_verification_required", "request readiness status field")
    assert_contains(request_readiness, "authenticated_reads_enablement_ready", "request readiness status field")
    assert_contains(request_readiness, "writes_remain_disabled", "request readiness status field")
    assert_contains(request_readiness, "real_automation_enabled", "request readiness status field")
    assert_contains(requests_js, "AUTHENTICATED_READS_ENABLED_BOUNDARY", "requests.js marker")
    assert_contains(requests_js, "RLS_WRITE_REVIEW_REQUIRED", "requests.js marker")
    assert_contains(backend_manifest, "Phase 4F: controlled migration apply and authenticated read enablement", "backend manifest marker")

    print("MVP6_CONTROLLED_MIGRATION_AUTHENTICATED_READS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
