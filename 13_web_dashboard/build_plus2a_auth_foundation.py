import json
from pathlib import Path

def _load_json(path_str):
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_plus2a_auth_foundation_model():
    status_model = _load_json("14_backend/auth/status_model.json")
    role_matrix = _load_json("14_backend/auth/role_matrix.json")
    
    future_auth_dependencies = [
        {"item": "real identity provider", "status": "missing"},
        {"item": "secure sessions", "status": "missing"},
        {"item": "server-side user store", "status": "missing"},
        {"item": "server-side role enforcement", "status": "missing"},
        {"item": "audit identity binding", "status": "missing"},
        {"item": "approval identity binding", "status": "missing"},
        {"item": "secrets management", "status": "missing"},
        {"item": "production auth hardening", "status": "missing"}
    ]
    
    model = {
        "auth_status_model": status_model,
        "demo_identity_model": role_matrix.get("demo_identities", []),
        "role_model": role_matrix.get("roles", {}),
        "permission_matrix": role_matrix.get("roles", {}),
        "forbidden_permission_boundary": role_matrix.get("forbidden_permissions", []),
        "future_auth_dependencies": future_auth_dependencies
    }
    
    Path("13_web_dashboard/dist/original_plus2a_auth_foundation_model.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model

if __name__ == "__main__":
    build_plus2a_auth_foundation_model()
    print("Built +2A auth foundation model JSON")
