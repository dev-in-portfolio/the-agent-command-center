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


def build_mvp6_controlled_migration_authenticated_reads_model():
    controlled_migration_apply_model = _load_json(SUPABASE_DIR / "controlled_migration_apply_model.json")
    post_migration_verification_model = _load_json(SUPABASE_DIR / "post_migration_verification_model.json")
    authenticated_reads_enablement_model = _load_json(SUPABASE_DIR / "authenticated_reads_enablement_model.json")
    migration_readiness_model = _load_json(SUPABASE_DIR / "migration_readiness_model.json")
    request_read_model = _load_json(SUPABASE_DIR / "request_read_model.json")

    model = {
        "model_id": "mvp6-controlled-supabase-migration-authenticated-reads",
        "model_version": "1.0",
        "controlled_migration_apply_model": controlled_migration_apply_model,
        "post_migration_verification_model": post_migration_verification_model,
        "authenticated_reads_enablement_model": authenticated_reads_enablement_model,
        "migration_readiness_model": migration_readiness_model,
        "request_read_model": request_read_model,
        "manual_migration_checklist": [
            "confirm supabase cli is available and linked to the project ref",
            "confirm readiness checker passes locally",
            "review the migration SQL files",
            "apply schema and RLS migrations only",
            "keep request writes disabled",
        ],
        "authenticated_reads_checklist": [
            "confirm provider configured",
            "confirm request API reads target is enabled",
            "confirm auth target is enabled",
            "confirm bearer token is required",
            "confirm service role stays server-only",
        ],
        "feature_flag_targets": {
            "MVP_ENABLE_SUPABASE_REQUEST_API": True,
            "MVP_ENABLE_SUPABASE_AUTH": True,
            "MVP_ENABLE_REQUEST_API_WRITES": False,
        },
        "endpoint_list": [
            "/api/request-readiness-status",
            "/api/requests GET",
            "/api/requests POST",
        ],
        "current_recommendation": [
            "CONTROLLED_MIGRATION_APPLY_READY",
            "APPLY_SCHEMA_AND_RLS_ONLY",
            "ENABLE_AUTHENTICATED_READS_ONLY",
            "WRITES_DISABLED_UNTIL_SEPARATE_REVIEW",
            "NOT_READY_FOR_REAL_AUTOMATION",
        ],
        "next_product_decision": [
            "verify_authenticated_reads_with_real_user_token",
            "then_build_controlled_request_create_writes",
        ],
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp6_controlled_migration_reads_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp6_controlled_migration_authenticated_reads_model(), indent=2, sort_keys=False))
