import json
import os

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def check_permission(identity_id, requested_permission):
    role_matrix = load_json(os.path.join(os.path.dirname(__file__), 'role_matrix.json'))
    
    # 1. Check if permission is globally forbidden
    forbidden = role_matrix.get("forbidden_permissions", [])
    if requested_permission in forbidden:
        return {"allowed": False, "reason": "Permission is globally forbidden.", "current_mode": "READ_ONLY_AUTH_FOUNDATION"}
        
    # 2. Find identity
    identities = role_matrix.get("demo_identities", [])
    identity = next((i for i in identities if i.get("user_id") == identity_id), None)
    if not identity:
        return {"allowed": False, "reason": "Identity not found.", "current_mode": "READ_ONLY_AUTH_FOUNDATION"}
        
    # 3. Find role
    roles = role_matrix.get("roles", {})
    role_id = identity.get("role")
    role_def = roles.get(role_id)
    if not role_def:
        return {"allowed": False, "reason": f"Role '{role_id}' not found.", "current_mode": "READ_ONLY_AUTH_FOUNDATION"}
        
    # 4. Check permission
    permissions = role_def.get("permissions", [])
    if requested_permission in permissions:
        return {"allowed": True, "reason": "Permission granted.", "current_mode": "READ_ONLY_AUTH_FOUNDATION"}
        
    return {"allowed": False, "reason": "Permission not found for role.", "current_mode": "READ_ONLY_AUTH_FOUNDATION"}
