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


def build_mvp5_supabase_migration_readiness_reads_model():
    migration_readiness_model = _load_json(SUPABASE_DIR / "migration_readiness_model.json")
    request_read_model = _load_json(SUPABASE_DIR / "request_read_model.json")
    request_read_adapter_contract = _load_json(SUPABASE_DIR / "request_read_adapter_contract.json")

    model = {
        "model_id": "mvp5-supabase-migration-readiness-authenticated-reads",
        "model_version": "1.0",
        "migration_readiness_model": migration_readiness_model,
        "request_read_model": request_read_model,
        "request_read_adapter_contract": request_read_adapter_contract,
        "manual_migration_checklist": [
            "review required migrations",
            "verify RLS enable statements",
            "confirm no broad anonymous write policies",
            "apply migrations outside Codex after confirmation",
        ],
        "authenticated_reads_checklist": [
            "confirm provider configured",
            "confirm request API enabled",
            "confirm auth enabled",
            "confirm bearer token is present",
            "confirm reads stay boundary-only until the read adapter is explicitly activated",
        ],
        "current_recommendation": [
            "MIGRATION_READINESS_CHECK_READY",
            "MANUAL_MIGRATION_REVIEW_REQUIRED",
            "AUTHENTICATED_READS_BOUNDARY_READY",
            "WRITES_DISABLED_UNTIL_RLS_REVIEW",
            "NEXT_STEP_MANUALLY_APPLY_MIGRATIONS_AND_ENABLE_AUTH_READS",
        ],
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp5_migration_readiness_reads_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp5_supabase_migration_readiness_reads_model(), indent=2, sort_keys=False))
