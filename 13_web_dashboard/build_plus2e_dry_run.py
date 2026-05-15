import json
from pathlib import Path

def _load_json(path_str):
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_plus2e_dry_run_model():
    status_model = _load_json("14_backend/dry_run/status_model.json")
    schemas = _load_json("14_backend/dry_run/schemas.json")
    
    future_dry_run_dependencies = [
        {"item": "approved dry-run sandbox", "status": "missing"},
        {"item": "request storage dependency", "status": "ready"},
        {"item": "audit log dependency", "status": "ready"},
        {"item": "approval gate dependency", "status": "ready"},
        {"item": "no-go dependency", "status": "ready"},
        {"item": "safe diff/evidence generator", "status": "missing"},
        {"item": "command execution approval", "status": "blocked"},
        {"item": "production sandbox hardening", "status": "missing"}
    ]
    
    model = {
        "dry_run_readiness_model": status_model,
        "dry_run_request_schema": schemas.get("dry_run_request_schema", {}),
        "dry_run_plan_schema": schemas.get("dry_run_plan_schema", {}),
        "dry_run_result_schema": schemas.get("dry_run_result_schema", {}),
        "dry_run_impact_model": schemas.get("impact_model", {}),
        "dry_run_adapter_contract": {
            "methods": [
                "get_dry_run_status()",
                "validate_dry_run_request(payload)",
                "generate_dry_run_plan(payload)",
                "run_dry_run(payload)",
                "get_dry_run_result(dry_run_result_id)",
                "list_dry_run_results()",
                "package_dry_run_evidence(dry_run_result_id)"
            ],
            "current_behavior": "DRY_RUN_EXECUTION_NOT_CONFIGURED"
        },
        "dry_run_evidence_package_contract": {
            "fields": [
                "evidence_package_id",
                "dry_run_result_id",
                "generated_at",
                "evidence_summary",
                "simulated_diff_summary",
                "safety_check_results",
                "blocked_operation_list",
                "required_human_review",
                "audit_reference"
            ],
            "storage_status": "DRY_RUN_STORAGE_NOT_CONFIGURED"
        },
        "future_dry_run_dependencies": future_dry_run_dependencies
    }
    
    Path("13_web_dashboard/dist/original_plus2e_dry_run_engine_model.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model

if __name__ == "__main__":
    build_plus2e_dry_run_model()
    print("Built +2E dry-run engine model JSON")
