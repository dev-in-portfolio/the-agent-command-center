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
        "Original +2B",
        "Persistent Request Storage Foundation",
        "PERSISTENT REQUEST STORAGE FOUNDATION",
        "REQUEST STORAGE CONTRACT",
        "STORAGE STATUS",
        "STORAGE NOT CONFIGURED",
        "REQUEST DRAFT SCHEMA",
        "REQUEST LIFECYCLE MODEL",
        "Storage Adapter Boundary Panel",
        "NO EXECUTION",
        "NO MUTATION",
        "NO EXTERNAL SYSTEM WRITES",
        "NOT_READY_FOR_REQUEST_PERSISTENCE",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Request Storage Status Panel",
        "Request Draft Schema Panel",
        "Request Lifecycle Model Panel",
        "Storage Adapter Boundary Panel",
        "Request Validation Preview Panel",
        "Disabled Write Boundary Panel",
        "Future Storage Dependency Panel",
        "Copy request draft schema",
        "Copy request lifecycle model",
        "Copy storage adapter boundary",
        "Copy disabled write boundary report",
        "Copy future storage dependency checklist",
        "Copy +2B validation checklist"
    ]
    
    for req in required_strings:
        if req not in index_text:
            raise SystemExit(f"FAIL: Missing from index.html: {req}")
            
    forbidden_controls = [
        "Save request",
        "Create request",
        "Update request",
        "Delete request",
        "Queue request",
        "Execute",
        "Deploy",
        "Merge",
        "Push",
        "Create PR",
        "Start automation"
    ]
    for req in forbidden_controls:
        if f"<button>{req}</button>" in index_text:
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
        "/api/request-storage-status",
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
        "./original_plus2a_auth_foundation_model.json",
        "./original_plus2b_request_storage_model.json"
    }
    for f in fetches:
        if f not in allowed_fetch:
            raise SystemExit(f"FAIL: Unauthorized fetch: {f}")

    if not Path("14_backend/request_storage").exists():
        raise SystemExit("FAIL: Missing 14_backend/request_storage directory")
        
    schemas = Path("14_backend/request_storage/schemas.json").read_text(encoding="utf-8")
    for key in ["request_draft_schema", "request_record_schema", "lifecycle_model"]:
        if f'"{key}"' not in schemas:
            raise SystemExit(f"FAIL: Missing key {key} in schemas.json")
            
    acc_report = Path("09_exports/original_plus2/original_plus2b_acceptance_report.md").read_text(encoding="utf-8")
    req_acc = [
        "PASS_WITH_HIGH_CONFIDENCE",
        "STORAGE_FOUNDATION_ONLY",
        "DURABLE_STORAGE_NOT_CONFIGURED",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]
    for r in req_acc:
        if r not in acc_report:
            raise SystemExit(f"FAIL: Missing from acceptance report: {r}")
            
    # Check backend code for safety
    for root, _, files in os.walk("14_backend/request_storage"):
        for f in files:
            if not f.endswith(".py"): continue
            content = Path(os.path.join(root, f)).read_text(encoding="utf-8")
            if "os.system" in content or "subprocess" in content:
                raise SystemExit(f"FAIL: Dangerous module used in {f}")

    print("ORIGINAL_PLUS2B_PERSISTENT_REQUEST_STORAGE_VALIDATION_PASS")

if __name__ == "__main__":
    check()
