#!/usr/bin/env python3
import json
import re
import sys
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
        ROOT / "14_backend/product_runtime/providers/supabase/__init__.py",
        ROOT / "14_backend/product_runtime/providers/supabase/env_contract.json",
        ROOT / "14_backend/product_runtime/providers/supabase/status_model.json",
        ROOT / "14_backend/product_runtime/providers/supabase/migrations/001_supabase_request_runtime.sql",
        ROOT / "13_web_dashboard/build_mvp3_supabase_provider.py",
        ROOT / "13_web_dashboard/dist/mvp3_supabase_provider_model.json",
        ROOT / "netlify/functions/_shared/provider_config.js",
        ROOT / "netlify/functions/provider-status.js",
        ROOT / "netlify/functions/requests.js",
        ROOT / "netlify/functions/backend-manifest.js",
        ROOT / "09_exports/mvp_product_track/mvp3_supabase_provider_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_env_contract_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_request_api_boundary_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_supabase_migration_scaffold_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_security_boundary_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_product_gap_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_safety_report.md",
        ROOT / "09_exports/mvp_product_track/mvp3_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(ROOT / "13_web_dashboard/dist/index.html")
    required_strings = [
        "MVP-3",
        "SUPABASE PROVIDER SELECTED",
        "PRODUCTION POSTGRES TARGET",
        "SUPABASE AUTH TARGET",
        "ENV CONFIGURATION REQUIRED",
        "REQUEST API DISABLED UNTIL CONFIGURED",
        "REQUEST API WRITES DISABLED",
        "SERVICE ROLE NEVER EXPOSED TO BROWSER",
        "RLS REQUIRED BEFORE PRODUCTION WRITES",
        "REAL AUTH BINDING REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_CONFIGURE_SUPABASE_PROJECT_AND_AUTH",
        "Provider Decision Panel",
        "Env Contract Panel",
        "Request API Boundary Panel",
        "Supabase Migration Scaffold Panel",
        "Security Boundary Panel",
        "Product Gap Panel",
        "Next Product Decision Panel",
        "Copy Supabase provider summary",
        "Copy env contract",
        "Copy request API boundary",
        "Copy migration scaffold summary",
        "Copy security checklist",
        "Copy next Supabase setup checklist",
        "Copy MVP-3 validation checklist",
    ]
    for text in required_strings:
        if text not in index:
            fail(f"Missing from index.html: {text}")

    for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
        label = match.group(2).strip().lower()
        if label.startswith("copy ") or label.startswith("load ") or label.startswith("open "):
            continue
        if any(term in label for term in [
            "connect supabase now",
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

    acceptance = read_text(ROOT / "09_exports/mvp_product_track/mvp3_acceptance_report.md")
    for text in [
        "SUPABASE_PROVIDER_SCAFFOLD_READY",
        "PASS_WITH_HIGH_CONFIDENCE",
        "REQUEST_API_DISABLED_UNTIL_CONFIGURED",
        "REAL_AUTH_BINDING_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        if text not in acceptance:
            fail(f"Acceptance report missing marker: {text}")

    provider_config = read_text(ROOT / "netlify/functions/_shared/provider_config.js")
    provider_status = read_text(ROOT / "netlify/functions/provider-status.js")
    requests_js = read_text(ROOT / "netlify/functions/requests.js")
    backend_manifest = read_text(ROOT / "netlify/functions/backend-manifest.js")
    dashboard_builder = read_text(ROOT / "13_web_dashboard/build_mvp3_supabase_provider.py")
    model_json = read_text(ROOT / "13_web_dashboard/dist/mvp3_supabase_provider_model.json")
    env_contract = read_text(ROOT / "14_backend/product_runtime/providers/supabase/env_contract.json")
    status_model = read_text(ROOT / "14_backend/product_runtime/providers/supabase/status_model.json")
    migration_sql = read_text(ROOT / "14_backend/product_runtime/providers/supabase/migrations/001_supabase_request_runtime.sql")

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
        "workflow_dispatch",
        "create_pull_request",
        "merge_pull_request",
        "deploy",
        "shell",
    ]

    file_map = {
        "provider_config.js": provider_config,
        "provider-status.js": provider_status,
        "requests.js": requests_js,
        "backend-manifest.js": backend_manifest,
        "build_mvp3_supabase_provider.py": dashboard_builder,
        "mvp3_supabase_provider_model.json": model_json,
        "env_contract.json": env_contract,
        "status_model.json": status_model,
        "001_supabase_request_runtime.sql": migration_sql,
    }

    for name, text in file_map.items():
        lowered = text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {name}: {pattern}")

    for name in ["provider_status.js", "requests.js", "backend-manifest.js", "dashboard_builder", "dashboard_renderer.py"]:
        text = file_map.get(name) if name in file_map else None
        if text is None:
            continue

    process_env_files = [
        "provider_config.js",
    ]
    for name, text in file_map.items():
        if "process.env" in text and name not in process_env_files:
            fail(f"Forbidden env read outside provider_config.js: {name}")

    if "process.env" not in provider_config:
        fail("provider_config.js missing env reads")

    if "SUPABASE_PROVIDER_NOT_CONFIGURED" not in requests_js:
        fail("requests.js missing not-configured boundary response")
    if "REQUEST_API_DISABLED" not in requests_js:
        fail("requests.js missing disabled boundary response")
    if "REQUEST_API_WRITES_DISABLED" not in requests_js:
        fail("requests.js missing writes-disabled boundary response")
    if "provider_configured" not in provider_status:
        fail("provider-status.js missing provider status output")
    if "provider_configured" not in model_json:
        fail("mvp3 model missing provider configured marker")
    if "SUPABASE_PROVIDER_SELECTED" not in model_json:
        fail("mvp3 model missing provider selection marker")
    if "ENV_CONFIGURATION_REQUIRED" not in model_json:
        fail("mvp3 model missing env configuration marker")
    if "REQUEST_API_DISABLED_UNTIL_CONFIGURED" not in model_json:
        fail("mvp3 model missing request api disabled marker")
    if "REAL_AUTH_BINDING_REQUIRED" not in model_json:
        fail("mvp3 model missing real auth binding marker")

    print("MVP3_SUPABASE_PROVIDER_REQUEST_API_VALIDATION_PASS")


if __name__ == "__main__":
    main()
