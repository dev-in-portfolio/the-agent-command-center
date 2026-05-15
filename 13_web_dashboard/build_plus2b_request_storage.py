import json
from pathlib import Path

def _load_json(path_str):
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_plus2b_request_storage_model():
    status_model = _load_json("14_backend/request_storage/status_model.json")
    schemas = _load_json("14_backend/request_storage/schemas.json")
    
    future_storage_dependencies = [
        {"item": "approved durable storage provider", "status": "missing"},
        {"item": "server-side auth binding", "status": "missing"},
        {"item": "audit log dependency", "status": "missing"},
        {"item": "approval record dependency", "status": "missing"},
        {"item": "migration plan", "status": "missing"},
        {"item": "backup/restore plan", "status": "missing"},
        {"item": "retention policy", "status": "missing"}
    ]
    
    model = {
        "storage_readiness_model": status_model,
        "request_draft_schema": schemas.get("request_draft_schema", {}),
        "request_record_schema": schemas.get("request_record_schema", {}),
        "request_lifecycle_state_model": schemas.get("lifecycle_model", {}),
        "storage_adapter_contract": {
            "methods": [
                "get_storage_status()",
                "validate_request_draft(payload)",
                "create_request_draft(payload)",
                "get_request_draft(request_id)",
                "list_request_drafts()",
                "update_request_draft(request_id, payload)",
                "archive_request_draft(request_id)"
            ],
            "current_behavior": "STORAGE_NOT_CONFIGURED"
        },
        "request_id_strategy": "REQ-DEMO-YYYYMMDD-HHMMSS",
        "future_storage_dependencies": future_storage_dependencies
    }
    
    Path("13_web_dashboard/dist/original_plus2b_request_storage_model.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model

if __name__ == "__main__":
    build_plus2b_request_storage_model()
    print("Built +2B request storage model JSON")
