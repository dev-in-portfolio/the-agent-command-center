import os
from pathlib import Path

def check():
    dist_dir = Path("13_web_dashboard/dist")
    if not dist_dir.exists():
        raise SystemExit("FAIL: dist dir not found")
        
    index = dist_dir / "index.html"
    if not index.exists():
        raise SystemExit("FAIL: index.html not found")
        
    js = dist_dir / "static/dashboard.js"
    css = dist_dir / "static/dashboard.css"
    if not js.exists() or not css.exists():
        raise SystemExit("FAIL: JS/CSS not found")
        
    index_text = index.read_text(encoding="utf-8")
    
    required_strings = [
        "Original +2A",
        "Backend Auth Foundation",
        "BACKEND AUTH FOUNDATION",
        "READ-ONLY AUTH STATUS",
        "ROLE / PERMISSION MATRIX",
        "DEMO IDENTITY MODEL",
        "AUTH FOUNDATION ONLY",
        "NO LIVE AUTH PROVIDER",
        "NO SESSION COOKIES",
        "NO TOKENS",
        "NO SECRETS",
        "NO EXECUTION",
        "NO MUTATION",
        "NO BACKEND WRITES",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "READY_FOR_AUTH_FOUNDATION_REVIEW_ONLY",
        "Auth Foundation Status Panel",
        "Demo Identity Panel",
        "Role / Permission Matrix Panel",
        "Permission Check Preview Panel",
        "Forbidden Permission Boundary Panel",
        "Future Auth Dependency Panel",
        "Copy auth foundation summary",
        "Copy role matrix",
        "Copy permission boundary report",
        "Copy future auth dependency checklist",
        "Copy +2A validation checklist"
    ]
    
    for req in required_strings:
        if req not in index_text:
            raise SystemExit(f"FAIL: Missing from index.html: {req}")
            
    forbidden_controls = [
        "Login",
        "Logout",
        "Sign up",
        "Save user",
        "Create session",
        "Issue token",
        ">Execute<",
        ">Deploy<",
        ">Merge<",
        ">Push<",
        ">Create PR<",
        ">Start automation<"
    ]
    for req in forbidden_controls:
        if f"<button>{req}</button>" in index_text or f"\"{req}\"" in index_text:
            raise SystemExit(f"FAIL: Forbidden control found: {req}")

    js_text = js.read_text(encoding="utf-8")
    
    forbidden_js = [
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "IndexedDB",
        "method: \"POST\"",
        "method:'POST'",
        "method: \"PUT\"",
        "method:'PUT'",
        "method: \"PATCH\"",
        "method:'PATCH'",
        "method: \"DELETE\"",
        "method:'DELETE'",
        "api.github.com",
        "api.netlify.com",
        "WebSocket",
        "EventSource",
        "sendBeacon",
        "eval(",
        "Function(",
        "import(",
        "Blob",
        "URL.createObjectURL",
        "FileReader"
    ]
    for req in forbidden_js:
        if req in js_text:
            raise SystemExit(f"FAIL: Forbidden JS found: {req}")
            
    # Check allowed fetches
    import re
    fetches = re.findall(r'fetch\(["\']([^"\']+)["\']', js_text)
    allowed_fetch = {
        "/api/health",
        "/api/status",
        "/api/backend-manifest",
        "/api/auth-status",
        "/api/role-matrix",
        "./status_snapshot.json",
        "./phase4d_identity_schema.json",
        "./phase4d_action_schema.json",
        "./phase4d_audit_schema.json",
        "./phase4d_approval_schema.json",
        "./phase4d_risk_model.json",
        "./original_plus1b_contract_schemas.json",
        "./original_plus1c_readiness_qa_model.json",
        "./original_plus1d_backend_boundary_model.json",
        "./original_plus1e_backend_build_tickets.json",
        "./original_plus2a_auth_foundation_model.json"
    }
    for f in fetches:
        if f not in allowed_fetch:
            raise SystemExit(f"FAIL: Unauthorized fetch: {f}")

    if not Path("14_backend/auth").exists():
        raise SystemExit("FAIL: Missing 14_backend/auth directory")
        
    role_matrix = Path("14_backend/auth/role_matrix.json").read_text(encoding="utf-8")
    for role in ["viewer", "operator", "reviewer", "approver", "automation_admin", "break_glass_admin"]:
        if f'"{role}"' not in role_matrix:
            raise SystemExit(f"FAIL: Missing role {role}")
            
    forbidden_permissions = [
        "execute_command",
        "mutate_backend",
        "mutate_github",
        "mutate_netlify",
        "deploy_site",
        "merge_branch",
        "push_branch",
        "create_pr",
        "trigger_workflow",
        "store_request",
        "store_approval",
        "queue_job"
    ]
    for p in forbidden_permissions:
        if f'"{p}"' not in role_matrix:
            raise SystemExit(f"FAIL: Missing forbidden permission {p}")

    acc_report = Path("09_exports/original_plus2/original_plus2a_acceptance_report.md").read_text(encoding="utf-8")
    req_acc = [
        "PASS_WITH_HIGH_CONFIDENCE",
        "AUTH_FOUNDATION_ONLY",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]
    for r in req_acc:
        if r not in acc_report:
            raise SystemExit(f"FAIL: Missing from acceptance report: {r}")
            
    # Check backend code for safety
    for root, _, files in os.walk("14_backend/auth"):
        for f in files:
            if not f.endswith(".py"): continue
            content = Path(os.path.join(root, f)).read_text(encoding="utf-8")
            if "os.system" in content or "subprocess" in content:
                raise SystemExit(f"FAIL: Dangerous module used in {f}")

    print("ORIGINAL_PLUS2A_BACKEND_AUTH_FOUNDATION_VALIDATION_PASS")

if __name__ == "__main__":
    check()
