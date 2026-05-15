#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _table_names(sql_text):
    tables = []
    for line in sql_text.splitlines():
      stripped = line.strip().lower()
      if stripped.startswith("create table if not exists "):
        remainder = stripped.split("create table if not exists ", 1)[1]
        table_name = remainder.split(" ", 1)[0].strip('"')
        if table_name and table_name not in tables:
          tables.append(table_name)
    return tables


def build_mvp3_supabase_provider_model():
    status_model = _load_json(SUPABASE_DIR / "status_model.json")
    env_contract = _load_json(SUPABASE_DIR / "env_contract.json")
    migration_sql = _load_text(SUPABASE_DIR / "migrations" / "001_supabase_request_runtime.sql")

    env_names = [item.get("name", "") for item in env_contract.get("environment_variables", [])]
    env_summary = {
        "environment_variables": env_names,
        "feature_flags_default": {
            "MVP_ENABLE_SUPABASE_REQUEST_API": False,
            "MVP_ENABLE_REQUEST_API_WRITES": False,
            "MVP_ENABLE_SUPABASE_AUTH": False,
        },
        "browser_safe_variables": ["SUPABASE_PROJECT_REF", "SUPABASE_URL"],
        "server_secret_variables": [
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_DB_PASSWORD",
            "DATABASE_URL",
        ],
        "current_required": False,
    }

    request_api_boundary = {
        "endpoints": [
            {
                "path": "/api/provider-status",
                "method": "GET",
                "purpose": "Read-only Supabase provider status",
                "boundary_state": "read_only",
            },
            {
                "path": "/api/requests",
                "method": "GET",
                "purpose": "Read-only request API boundary scaffold",
                "boundary_state": "disabled_by_default",
            },
            {
                "path": "/api/requests",
                "method": "POST",
                "purpose": "Write boundary scaffold with writes disabled by default",
                "boundary_state": "writes_disabled_by_default",
            },
        ],
        "disabled_unless_configured": True,
        "writes_disabled_by_default": True,
        "no_supabase_network_calls": True,
        "no_command_execution": True,
        "no_external_mutation": True,
    }

    migration_scaffold = {
        "file_path": "14_backend/product_runtime/providers/supabase/migrations/001_supabase_request_runtime.sql",
        "tables": _table_names(migration_sql) or [
            "app_users",
            "app_roles",
            "requests",
            "request_lifecycle_events",
            "approvals",
            "audit_events",
            "dry_run_results",
            "no_go_flags",
        ],
        "rls_required_before_production_writes": True,
        "auth_uid_binding_required": True,
        "service_role_never_exposed_to_browser": True,
        "migrations_not_auto_applied": True,
    }

    status_summary = {
        "provider": status_model.get("provider", "supabase"),
        "provider_configured": bool(status_model.get("provider_configured", False)),
        "request_api_enabled": bool(status_model.get("request_api_enabled", False)),
        "request_api_writes_enabled": bool(status_model.get("request_api_writes_enabled", False)),
        "project_ref": status_model.get("project_ref", "mobvzrkcsfbumgbwvkcp"),
        "project_url": status_model.get("project_url", "https://mobvzrkcsfbumgbwvkcp.supabase.co"),
    }

    model = {
        "model_id": "mvp3-supabase-provider-request-api-scaffold",
        "model_version": "1.0",
        "provider_status_model": status_model,
        "env_contract": env_contract,
        "provider_decision": {
            "selected_database_provider": "Supabase Postgres",
            "selected_auth_provider": "Supabase Auth",
            "project_ref": status_summary["project_ref"],
            "project_url": status_summary["project_url"],
            "configured_status": "not_configured" if not status_summary["provider_configured"] else "configured",
        },
        "env_contract_summary": env_summary,
        "request_api_boundary": request_api_boundary,
        "supabase_migration_scaffold_summary": migration_scaffold,
        "auth_binding_gap": [
            "real auth provider binding is still required",
            "auth.uid() binding is not applied yet",
            "service role key remains server-side only",
            "browser exposure is forbidden",
        ],
        "rls_requirement": [
            "enable row-level security before production writes",
            "review all policies manually",
            "do not auto-apply production migrations",
        ],
        "netlify_env_status_model": status_summary,
        "security_boundary": [
            "no service role in browser",
            "no hardcoded secrets",
            "no env values printed",
            "RLS required before production writes",
            "auth.uid() binding required",
            "no production writes yet",
        ],
        "product_gap": [
            "confirm Netlify env values",
            "apply migration manually after review",
            "configure Supabase Auth",
            "wire real auth binding",
            "enable request API reads first",
            "enable writes only after RLS/auth review",
        ],
        "next_product_step": [
            "configure_supabase_auth_policy",
            "configure_rls_policy",
            "then_build_mvp4_authenticated_request_api",
        ],
        "current_recommendation": [
            "SUPABASE_PROVIDER_SELECTED",
            "ENV_CONFIGURATION_REQUIRED",
            "REQUEST_API_DISABLED_UNTIL_CONFIGURED",
            "REAL_AUTH_BINDING_REQUIRED",
            "NEXT_STEP_CONFIGURE_SUPABASE_PROJECT_AND_AUTH",
        ],
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp3_supabase_provider_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp3_supabase_provider_model(), indent=2, sort_keys=False))
