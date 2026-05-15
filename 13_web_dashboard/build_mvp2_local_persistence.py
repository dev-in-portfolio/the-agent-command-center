#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PRODUCT_RUNTIME_DIR = ROOT / "14_backend" / "product_runtime" / "persistence"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_mvp2_local_persistence_model():
    status_model = _load_json(PRODUCT_RUNTIME_DIR / "status_model.json")
    demo_fixture = _load_json(ROOT / "14_backend" / "product_runtime" / "demo_fixture.json")

    adapter_methods = [
        "initialize_local_dev_database",
        "create_request",
        "get_request",
        "list_requests",
        "update_request_state",
        "add_lifecycle_event",
        "get_lifecycle_events",
        "close",
    ]
    repository_responsibilities = [
        "wrap the SQLite adapter",
        "validate request payloads before local storage",
        "create and fetch requests",
        "list requests",
        "transition lifecycle state",
        "record lifecycle events",
        "never execute automation",
    ]
    migration_behavior = {
        "file_path": "14_backend/product_runtime/persistence/apply_local_migrations.py",
        "sql_path": "14_backend/product_runtime/migrations/001_mvp_request_lifecycle.sql",
        "apply_mode": "explicit local-dev only",
        "production_safe": True,
        "database_url_read": False,
        "env_reads": False,
        "external_network": False,
    }
    lifecycle_demo = {
        "request_title": demo_fixture.get("title", "Prepare safe deployment review packet"),
        "states": [
            "request_received",
            "request_validated",
            "dry_run_plan_generated",
            "approval_required",
            "audit_event_prepared",
            "blocked_before_execution",
            "ready_for_human_review",
        ],
        "persisted_locally": True,
        "no_external_mutation": True,
        "real_automation_enabled": False,
    }
    production_gap = [
        "choose production Postgres provider",
        "choose auth provider",
        "add env/secrets later",
        "add production migrations later",
        "add real request API later",
        "add server-side identity binding later",
    ]
    next_decision = [
        "choose_production_postgres_provider",
        "choose_auth_provider",
        "wire_real_request_create_list_get_api",
        "then_add_server_side_identity_binding",
    ]

    model = {
        "model_id": "mvp2-local-durable-request-persistence-runtime",
        "model_version": "1.0",
        "local_persistence_status": status_model,
        "adapter_methods": adapter_methods,
        "request_repository_responsibilities": repository_responsibilities,
        "local_dev_database_path": ".agent_command_center/demo_runtime.sqlite3",
        "local_dev_database_path_explanation": "The demo runner writes to a local SQLite file only for development and preview runs.",
        "migration_behavior": migration_behavior,
        "lifecycle_persistence_demo_summary": lifecycle_demo,
        "production_persistence_gap": production_gap,
        "next_product_decision": next_decision,
        "current_recommendation": status_model.get("current_recommendation", []),
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp2_local_persistence_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp2_local_persistence_model(), indent=2, sort_keys=False))

