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


def build_mvp4_supabase_auth_rls_request_api_model():
    auth_policy_model = _load_json(SUPABASE_DIR / "auth_policy_model.json")
    rls_policy_model = _load_json(SUPABASE_DIR / "rls_policy_model.json")
    auth_migration_sql = _load_text(SUPABASE_DIR / "migrations" / "002_supabase_auth_rls_policies.sql")
    provider_status = _load_json(SUPABASE_DIR / "status_model.json")

    endpoint_list = [
        {
            "path": "/api/provider-status",
            "method": "GET",
            "purpose": "Read-only Supabase provider status",
            "gated": True,
        },
        {
            "path": "/api/auth-status",
            "method": "GET",
            "purpose": "Read-only Supabase auth status",
            "gated": True,
        },
        {
            "path": "/api/requests",
            "method": "GET",
            "purpose": "Authenticated request API boundary scaffold",
            "gated": True,
        },
        {
            "path": "/api/requests",
            "method": "POST",
            "purpose": "Authenticated request write boundary scaffold",
            "gated": True,
        },
    ]

    auth_gate_model = {
        "provider_configured_required": True,
        "request_api_enabled_required": True,
        "auth_enabled_required": True,
        "bearer_token_required": True,
        "writes_enabled_required_for_post": True,
        "rls_review_required": True,
        "anonymous_access_blocked": True,
        "service_role_never_exposed_to_browser": True,
        "current_recommendation": [
            "SUPABASE_AUTH_RLS_SCAFFOLD_READY",
            "REQUEST_API_REQUIRES_AUTH",
            "WRITES_DISABLED_UNTIL_RLS_REVIEW",
            "NOT_READY_FOR_REAL_AUTOMATION",
            "NEXT_STEP_APPLY_RLS_MIGRATION_AND_ENABLE_READS",
        ],
    }

    model = {
        "model_id": "mvp4-supabase-auth-rls-authenticated-request-api",
        "model_version": "1.0",
        "auth_policy_model": auth_policy_model,
        "rls_policy_model": rls_policy_model,
        "auth_migration_scaffold": {
            "file_path": "14_backend/product_runtime/providers/supabase/migrations/002_supabase_auth_rls_policies.sql",
            "tables": _table_names(auth_migration_sql) or rls_policy_model.get("tables_requiring_rls", []),
            "manual_apply_only": True,
            "rls_required_before_writes": True,
            "auth_uid_binding_required": True,
            "service_role_browser_exposure_allowed": False,
        },
        "endpoint_list": endpoint_list,
        "request_api_gate_model": auth_gate_model,
        "provider_status_model": provider_status,
        "current_recommendation": [
            "SUPABASE_AUTH_RLS_SCAFFOLD_READY",
            "REQUEST_API_REQUIRES_AUTH",
            "WRITES_DISABLED_UNTIL_RLS_REVIEW",
            "NOT_READY_FOR_REAL_AUTOMATION",
            "NEXT_STEP_APPLY_RLS_MIGRATION_AND_ENABLE_READS",
        ],
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp4_auth_rls_request_api_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp4_supabase_auth_rls_request_api_model(), indent=2, sort_keys=False))
