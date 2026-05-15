import json
from pathlib import Path

def _load_json(path_str):
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_plus2d_approval_gate_model():
    status_model = _load_json("14_backend/approval_gate/status_model.json")
    schemas = _load_json("14_backend/approval_gate/schemas.json")
    
    future_approval_dependencies = [
        {"item": "approved durable approval storage provider", "status": "missing"},
        {"item": "request storage dependency", "status": "ready"},
        {"item": "audit log dependency", "status": "ready"},
        {"item": "real auth identity binding", "status": "missing"},
        {"item": "approver role enforcement", "status": "missing"},
        {"item": "approval record retention policy", "status": "missing"},
        {"item": "production no-go enforcement", "status": "missing"}
    ]
    
    model = {
        "approval_readiness_model": status_model,
        "approval_request_schema": schemas.get("approval_request_schema", {}),
        "approval_record_schema": schemas.get("approval_record_schema", {}),
        "approval_scope_model": schemas.get("approval_scope_model", {}),
        "approval_lifecycle_model": schemas.get("approval_lifecycle_model", {}),
        "approval_adapter_contract": {
            "methods": [
                "get_approval_status()",
                "validate_approval_request(payload)",
                "create_approval_request(payload)",
                "get_approval_request(approval_request_id)",
                "list_approval_requests()",
                "record_approval_decision(payload)",
                "revoke_approval(approval_id)",
                "check_approval_gate(request_id, requested_action_type)"
            ],
            "current_behavior": "APPROVAL_STORAGE_NOT_CONFIGURED"
        },
        "expiration_revocation_policy": {
            "default_expiration_window_minutes": 60,
            "max_expiration_window_minutes": 480,
            "revocation_allowed": True,
            "revocation_audit_required": True,
            "expired_approval_blocks_action": True,
            "approval_cannot_authorize_forbidden_scope": True,
            "no_go_overrides_approval": True
        },
        "approval_identity_binding_contract": {
            "identity_required": True,
            "auth_mode": "bound_server_side",
            "approver_role_enforced": True,
            "demo_identity_only": True
        },
        "future_approval_dependencies": future_approval_dependencies
    }
    
    Path("13_web_dashboard/dist/original_plus2d_approval_gate_model.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model

if __name__ == "__main__":
    build_plus2d_approval_gate_model()
    print("Built +2D approval gate model JSON")
