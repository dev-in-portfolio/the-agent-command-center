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
        SUPABASE_DIR / "migration_readiness_model.json",
        SUPABASE_DIR / "migration_readiness_check.py",
        SUPABASE_DIR / "request_read_model.json",
        SUPABASE_DIR / "request_read_adapter_contract.json",
        ROOT / "netlify/functions/request-readiness-status.js",
        ROOT / "netlify/functions/requests.js",
        ROOT / "13_web_dashboard/build_mvp5_supabase_migration_readiness.py",
        DIST_DIR / "mvp5_migration_readiness_reads_model.json",
        REPORT_DIR / "mvp5_migration_readiness_report.md",
        REPORT_DIR / "mvp5_manual_migration_review_report.md",
        REPORT_DIR / "mvp5_authenticated_request_reads_report.md",
        REPORT_DIR / "mvp5_request_read_adapter_contract_report.md",
        REPORT_DIR / "mvp5_security_boundary_report.md",
        REPORT_DIR / "mvp5_next_product_step_report.md",
        REPORT_DIR / "mvp5_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-5",
        "MIGRATION READINESS CHECK",
        "MANUAL MIGRATION REVIEW REQUIRED",
        "AUTHENTICATED REQUEST READS",
        "READS REQUIRE BEARER TOKEN",
        "ANON KEY + USER TOKEN ONLY",
        "SERVICE ROLE NOT USED FOR READS",
        "WRITES STILL DISABLED",
        "RLS REVIEW REQUIRED",
        "NO AUTOMATIC MIGRATION APPLY",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS",
        "Migration Readiness Panel",
        "Migration Safety Checklist Panel",
        "Authenticated Reads Panel",
        "Request Read Adapter Contract Panel",
        "Endpoint Status Panel",
        "Next Product Decision Panel",
        "Copy migration readiness checklist",
        "Copy manual migration review checklist",
        "Copy authenticated reads checklist",
        "Copy request read adapter contract",
        "Copy MVP-5 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp5_acceptance_report.md")
    for text in [
        "MIGRATION_READINESS_AUTHENTICATED_READS_SCAFFOLD_READY",
        "PASS_WITH_HIGH_CONFIDENCE",
        "MANUAL_MIGRATION_REVIEW_REQUIRED",
        "AUTHENTICATED_READS_BOUNDARY_READY",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    migration_model = json.loads(read_text(SUPABASE_DIR / "migration_readiness_model.json"))
    request_model = json.loads(read_text(SUPABASE_DIR / "request_read_model.json"))
    adapter_contract = json.loads(read_text(SUPABASE_DIR / "request_read_adapter_contract.json"))
    rendered_model = json.loads(read_text(DIST_DIR / "mvp5_migration_readiness_reads_model.json"))

    if migration_model.get("migration_apply_mode") != "manual_only":
        fail("migration_apply_mode must be manual_only")
    if migration_model.get("production_apply_automatic") is not False:
        fail("production_apply_automatic must be false")
    if migration_model.get("supabase_cli_required") is not True:
        fail("supabase_cli_required must be true")
    if migration_model.get("rls_review_required") is not True:
        fail("rls_review_required must be true")
    if migration_model.get("writes_enabled_after_migration") is not False:
        fail("writes_enabled_after_migration must be false")

    if request_model.get("uses_service_role") is not False:
        fail("request read model must not use service role")
    if request_model.get("uses_anon_key_with_user_bearer") is not True:
        fail("request read model must use anon key with user bearer")
    if request_model.get("writes_enabled") is not False:
        fail("request read model writes must be false")

    security = adapter_contract.get("security", {})
    if security.get("bearer_token_required") is not True:
        fail("request read adapter contract must require bearer token")
    if security.get("auth_uid_binding_required") is not True:
        fail("request read adapter contract must require auth uid binding")
    if security.get("rls_required") is not True:
        fail("request read adapter contract must require rls")
    if security.get("service_role_forbidden_in_browser") is not True:
        fail("request read adapter contract must forbid service role in browser")
    if security.get("no_writes") is not True:
        fail("request read adapter contract must block writes")

    if rendered_model.get("current_recommendation", []) != [
        "MIGRATION_READINESS_CHECK_READY",
        "MANUAL_MIGRATION_REVIEW_REQUIRED",
        "AUTHENTICATED_READS_BOUNDARY_READY",
        "WRITES_DISABLED_UNTIL_RLS_REVIEW",
        "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS",
    ]:
        fail("rendered MVP-5 model recommendation mismatch")

    scan_targets = {
        "migration_readiness_check.py": read_text(SUPABASE_DIR / "migration_readiness_check.py"),
        "request-readiness-status.js": read_text(ROOT / "netlify/functions/request-readiness-status.js"),
        "requests.js": read_text(ROOT / "netlify/functions/requests.js"),
        "build_mvp5_supabase_migration_readiness.py": read_text(ROOT / "13_web_dashboard/build_mvp5_supabase_migration_readiness.py"),
        "dashboard_renderer.py": read_text(ROOT / "13_web_dashboard/dashboard_renderer.py"),
        "mvp5_migration_readiness_reads_model.json": read_text(DIST_DIR / "mvp5_migration_readiness_reads_model.json"),
    }

    forbidden_patterns = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "api.github.com",
        "api.netlify.com",
        "subprocess",
        "os.system",
        "exec(",
        "spawn(",
        "execSync(",
        "child_process",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexeddb",
        "fetch(",
    ]
    for name, text in scan_targets.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    if "process.env" in scan_targets["request-readiness-status.js"]:
        fail("request-readiness-status.js must not read env directly")
    if "process.env" in scan_targets["dashboard_renderer.py"]:
        fail("dashboard_renderer.py must not read env directly")

    if "AUTHENTICATED_READ_BOUNDARY_READY" not in scan_targets["requests.js"]:
        fail("requests.js missing authenticated read boundary marker")
    if "REQUEST_API_WRITES_DISABLED" not in scan_targets["requests.js"]:
        fail("requests.js missing writes disabled marker")
    if "RLS_POLICY_REQUIRED" not in scan_targets["requests.js"]:
        fail("requests.js missing rls policy required marker")
    if "MIGRATION_READINESS_CHECK_READY" not in scan_targets["mvp5_migration_readiness_reads_model.json"]:
        fail("rendered MVP-5 model missing readiness marker")
    if "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS" not in scan_targets["mvp5_migration_readiness_reads_model.json"]:
        fail("rendered MVP-5 model missing next-step marker")

    print("MVP5_MIGRATION_READINESS_AUTHENTICATED_READS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
