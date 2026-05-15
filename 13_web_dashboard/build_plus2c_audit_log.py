import json
from pathlib import Path

def _load_json(path_str):
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_plus2c_audit_log_model():
    status_model = _load_json("14_backend/audit_log/status_model.json")
    schemas = _load_json("14_backend/audit_log/schemas.json")
    
    future_audit_dependencies = [
        {"item": "approved durable audit storage provider", "status": "missing"},
        {"item": "request storage dependency", "status": "missing"},
        {"item": "auth identity binding dependency", "status": "missing"},
        {"item": "approval record dependency", "status": "missing"},
        {"item": "append-only enforcement", "status": "missing"},
        {"item": "backup/restore plan", "status": "missing"},
        {"item": "retention policy", "status": "missing"}
    ]
    
    model = {
        "audit_readiness_model": status_model,
        "audit_event_schema": schemas.get("audit_event_schema", {}),
        "audit_event_categories": schemas.get("audit_event_categories", {}),
        "immutable_hash_chain_contract": schemas.get("hash_chain_contract", {}),
        "audit_adapter_contract": {
            "methods": [
                "get_audit_status()",
                "validate_audit_event(payload)",
                "compute_event_hash(payload)",
                "append_audit_event(payload)",
                "get_audit_event(audit_event_id)",
                "list_audit_events()",
                "verify_audit_chain()"
            ],
            "current_behavior": "AUDIT_STORAGE_NOT_CONFIGURED"
        },
        "retention_redaction_policy": {
            "retention_class": "STANDARD_OPERATIONAL",
            "redaction_allowed_for_payload_summary": True,
            "immutable_core_fields": True,
            "pii_policy": "NO_PII_ALLOWED",
            "secret_redaction_required": True,
            "token_redaction_required": True,
            "no_secret_storage": True
        },
        "future_audit_dependencies": future_audit_dependencies
    }
    
    Path("13_web_dashboard/dist/original_plus2c_audit_log_model.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model

if __name__ == "__main__":
    build_plus2c_audit_log_model()
    print("Built +2C audit log model JSON")
