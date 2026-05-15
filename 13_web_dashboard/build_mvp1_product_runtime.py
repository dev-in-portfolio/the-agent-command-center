#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCT_RUNTIME_DIR = ROOT / "14_backend" / "product_runtime"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_mvp1_product_runtime_model():
    state_model = _load_json(PRODUCT_RUNTIME_DIR / "state_model.json")
    runtime_result_schema = _load_json(PRODUCT_RUNTIME_DIR / "runtime_result_schema.json")
    persistence_strategy = _load_json(PRODUCT_RUNTIME_DIR / "persistence_adapter_strategy.json")
    demo_fixture = _load_json(PRODUCT_RUNTIME_DIR / "demo_fixture.json")

    migration_tables = [
        "users",
        "roles",
        "requests",
        "request_lifecycle_events",
        "approvals",
        "audit_events",
        "dry_run_results",
        "no_go_flags",
    ]

    model = {
        "model_id": "mvp1-request-lifecycle-runtime-scaffold",
        "model_version": "1.0",
        "product_track_active": state_model.get("product_track_active", True),
        "runtime_scaffold_ready": state_model.get("runtime_scaffold_ready", True),
        "real_auth_configured": state_model.get("real_auth_configured", False),
        "durable_persistence_configured": state_model.get("durable_persistence_configured", False),
        "dry_run_execution_enabled": state_model.get("dry_run_execution_enabled", False),
        "external_mutation_enabled": state_model.get("external_mutation_enabled", False),
        "real_automation_enabled": state_model.get("real_automation_enabled", False),
        "current_status": state_model.get("current_status", "MVP_RUNTIME_SCAFFOLD_READY"),
        "current_recommendation": state_model.get("current_recommendation", []),
        "lifecycle_states": state_model.get("lifecycle_states", []),
        "forbidden_lifecycle_states": state_model.get("forbidden_lifecycle_states", []),
        "runtime_result_schema": runtime_result_schema,
        "persistence_adapter_strategy": persistence_strategy,
        "demo_fixture_summary": {
            "title": demo_fixture.get("title", "unknown"),
            "requested_action": demo_fixture.get("requested_action", "unknown"),
            "expected_result": demo_fixture.get("expected_result", "unknown"),
            "scope": demo_fixture.get("scope", "unknown"),
            "no_real_deploy": bool(demo_fixture.get("no_real_deploy", False)),
            "no_external_mutation": bool(demo_fixture.get("no_external_mutation", False)),
        },
        "migration_scaffold_summary": {
            "file_path": "14_backend/product_runtime/migrations/001_mvp_request_lifecycle.sql",
            "tables": migration_tables,
            "status": "SCAFFOLD_ONLY",
            "do_not_execute": True,
        },
        "product_gap": [
            "real auth provider",
            "durable database",
            "migrations applied",
            "server-side request create/list/read endpoints",
            "real audit append",
            "real approval record persistence",
            "real dry-run evidence persistence",
            "first safe GitHub action after persistence/auth",
        ],
        "next_product_decision": [
            "choose_storage_provider",
            "choose_auth_provider",
            "wire_real_request_persistence",
            "then_build_first_safe_github_issue_or_draft_pr_action",
        ],
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "mvp1_product_runtime_model.json").write_text(
        json.dumps(model, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return model


if __name__ == "__main__":
    print(json.dumps(build_mvp1_product_runtime_model(), indent=2, sort_keys=False))
