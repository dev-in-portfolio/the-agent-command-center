#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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


def main():
    required_files = [
        ROOT / "14_backend/product_runtime/providers/supabase/auth_policy_model.json",
        ROOT / "14_backend/product_runtime/providers/supabase/rls_policy_model.json",
        ROOT / "14_backend/product_runtime/providers/supabase/migrations/002_supabase_auth_rls_policies.sql",
        ROOT / "netlify/functions/_shared/auth_context.js",
        ROOT / "netlify/functions/auth-status.js",
        ROOT / "netlify/functions/requests.js",
        ROOT / "13_web_dashboard/build_mvp4_supabase_auth_rls.py",
        ROOT / "13_web_dashboard/dist/mvp4_auth_rls_request_api_model.json",
        ROOT / "09_exports/mvp_product_track/mvp4_supabase_auth_policy_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_rls_policy_scaffold_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_authenticated_request_api_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_request_api_gate_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_security_boundary_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_next_product_step_report.md",
        ROOT / "09_exports/mvp_product_track/mvp4_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(ROOT / "13_web_dashboard/dist/index.html")
    required_strings = [
        "MVP-4",
        "SUPABASE AUTH POLICY",
        "RLS POLICY SCAFFOLD",
        "AUTHENTICATED REQUEST API",
        "BEARER TOKEN REQUIRED",
        "ANONYMOUS REQUESTS BLOCKED",
        "SERVICE ROLE NEVER EXPOSED TO BROWSER",
        "RLS REQUIRED BEFORE WRITES",
        "REQUEST API REQUIRES AUTH",
        "WRITES DISABLED UNTIL RLS REVIEW",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_APPLY_RLS_MIGRATION_AND_ENABLE_READS",
        "Auth Policy Panel",
        "RLS Policy Panel",
        "Request API Gate Panel",
        "Endpoint Panel",
        "Security Boundary Panel",
        "Next Product Decision Panel",
        "Copy auth policy summary",
        "Copy RLS policy summary",
        "Copy request API gate checklist",
        "Copy endpoint checklist",
        "Copy migration review checklist",
        "Copy MVP-4 validation checklist",
    ]
    for text in required_strings:
        if text not in index:
            fail(f"Missing from index.html: {text}")

    for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
        label = match.group(2).strip().lower()
        if label.startswith("copy ") or label.startswith("load ") or label.startswith("open "):
            continue
        if any(term in label for term in [
            "apply migration",
            "enable writes",
            "expose service role",
            "login",
            "execute request",
            "deploy",
            "merge",
            "push",
            "create pr",
            "start automation",
        ]):
            fail(f"Forbidden button label present: {match.group(2).strip()}")

    acceptance = read_text(ROOT / "09_exports/mvp_product_track/mvp4_acceptance_report.md")
    for text in [
        "SUPABASE_AUTH_RLS_REQUEST_API_SCAFFOLD_READY",
        "PASS_WITH_HIGH_CONFIDENCE",
        "REQUEST_API_REQUIRES_AUTH",
        "WRITES_DISABLED_UNTIL_RLS_REVIEW",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        if text not in acceptance:
            fail(f"Acceptance report missing marker: {text}")

    auth_policy = read_text(ROOT / "14_backend/product_runtime/providers/supabase/auth_policy_model.json")
    rls_policy = read_text(ROOT / "14_backend/product_runtime/providers/supabase/rls_policy_model.json")
    migration_sql = read_text(ROOT / "14_backend/product_runtime/providers/supabase/migrations/002_supabase_auth_rls_policies.sql")
    auth_context = read_text(ROOT / "netlify/functions/_shared/auth_context.js")
    auth_status = read_text(ROOT / "netlify/functions/auth-status.js")
    requests_js = read_text(ROOT / "netlify/functions/requests.js")
    backend_manifest = read_text(ROOT / "netlify/functions/backend-manifest.js")
    dashboard_builder = read_text(ROOT / "13_web_dashboard/build_mvp4_supabase_auth_rls.py")
    model_json = read_text(ROOT / "13_web_dashboard/dist/mvp4_auth_rls_request_api_model.json")

    file_map = {
        "auth_policy_model.json": auth_policy,
        "rls_policy_model.json": rls_policy,
        "002_supabase_auth_rls_policies.sql": migration_sql,
        "auth_context.js": auth_context,
        "auth-status.js": auth_status,
        "requests.js": requests_js,
        "backend-manifest.js": backend_manifest,
        "build_mvp4_supabase_auth_rls.py": dashboard_builder,
        "mvp4_auth_rls_request_api_model.json": model_json,
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
        "indexeddb",
        "document.cookie",
    ]

    for name, text in file_map.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    process_env_files = [
        "auth_policy_model.json",
        "rls_policy_model.json",
        "002_supabase_auth_rls_policies.sql",
        "auth_context.js",
        "auth-status.js",
        "requests.js",
        "backend-manifest.js",
        "build_mvp4_supabase_auth_rls.py",
        "mvp4_auth_rls_request_api_model.json",
    ]
    for name, text in file_map.items():
        if "process.env" in text and name not in []:
            fail(f"Forbidden env read in MVP-4 scaffold file: {name}")

    if "AUTH_DISABLED_BY_DEFAULT" not in requests_js:
        fail("requests.js missing AUTH_DISABLED_BY_DEFAULT boundary response")
    if "AUTHORIZATION_REQUIRED" not in requests_js:
        fail("requests.js missing AUTHORIZATION_REQUIRED boundary response")
    if "REQUEST_API_WRITES_DISABLED" not in requests_js:
        fail("requests.js missing REQUEST_API_WRITES_DISABLED boundary response")
    if "RLS_POLICY_REQUIRED" not in requests_js:
        fail("requests.js missing RLS_POLICY_REQUIRED boundary response")
    if "SUPABASE_AUTH_POLICY_READY" not in auth_context:
        fail("auth_context.js missing auth policy ready marker")
    if "AUTHORIZATION_REQUIRED" not in auth_context:
        fail("auth_context.js missing authorization required marker")
    if "provider: \"supabase_auth\"" not in auth_status:
        fail("auth-status.js missing provider marker")
    if "/api/auth-status" not in backend_manifest:
        fail("backend-manifest.js missing auth-status endpoint")
    if "SUPABASE_AUTH_RLS_SCAFFOLD_READY" not in model_json:
        fail("mvp4 model missing scaffold-ready marker")
    if "REQUEST_API_REQUIRES_AUTH" not in model_json:
        fail("mvp4 model missing request api auth marker")
    if "WRITES_DISABLED_UNTIL_RLS_REVIEW" not in model_json:
        fail("mvp4 model missing writes disabled marker")

    print("MVP4_SUPABASE_AUTH_RLS_REQUEST_API_VALIDATION_PASS")


if __name__ == "__main__":
    main()
