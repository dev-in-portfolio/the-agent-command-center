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
    if not js.exists():
        raise SystemExit("FAIL: dashboard.js not found")
        
    index_text = index.read_text(encoding="utf-8")
    
    required_strings = [
        "Original +2C",
        "Immutable Audit Log Foundation",
        "IMMUTABLE AUDIT LOG FOUNDATION",
        "AUDIT EVENT CONTRACT",
        "HASH CHAIN CONTRACT",
        "AUDIT STORAGE NOT CONFIGURED",
        "AUDIT APPEND DISABLED",
        "AUDIT STATUS",
        "AUDIT EVENT SCHEMA",
        "AUDIT ADAPTER BOUNDARY",
        "NO EXECUTION",
        "NO MUTATION",
        "NO EXTERNAL SYSTEM WRITES",
        "NOT_READY_FOR_AUDIT_PERSISTENCE",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Audit Log Status Panel",
        "Audit Event Schema Panel",
        "Audit Event Category Boundary Panel",
        "Hash Chain Contract Panel",
        "Audit Adapter Boundary Panel",
        "Audit Validation Preview Panel",
        "Disabled Audit Append Boundary Panel",
        "Retention / Redaction Policy Panel",
        "Future Audit Dependency Panel",
        "Copy audit event schema",
        "Copy hash chain contract",
        "Copy audit adapter boundary",
        "Copy disabled audit append boundary report",
        "Copy retention/redaction policy",
        "Copy future audit dependency checklist",
        "Copy +2C validation checklist"
    ]
    
    for req in required_strings:
        if req not in index_text:
            raise SystemExit(f"FAIL: Missing from index.html: {req}")
            
    forbidden_controls = [
        "Append audit event",
        "Save audit event",
        "Create audit event",
        "Delete audit event",
        "Verify live chain"
    ]
    for req in forbidden_controls:
        if f"<button>{req}</button>" in index_text:
            raise SystemExit(f"FAIL: Forbidden control found: {req}")

    js_text = js.read_text(encoding="utf-8")
    
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
        "/api/audit-log-status",
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
        "./original_plus2b_request_storage_model.json",
        "./original_plus2c_audit_log_model.json"
    }
    for f in fetches:
        if f not in allowed_fetch:
            raise SystemExit(f"FAIL: Unauthorized fetch: {f}")

    if not Path("14_backend/audit_log").exists():
        raise SystemExit("FAIL: Missing 14_backend/audit_log directory")
        
    schemas = Path("14_backend/audit_log/schemas.json").read_text(encoding="utf-8")
    for key in ["audit_event_schema", "audit_event_categories", "hash_chain_contract"]:
        if f'"{key}"' not in schemas:
            raise SystemExit(f"FAIL: Missing key {key} in schemas.json")
            
    acc_report = Path("09_exports/original_plus2/original_plus2c_acceptance_report.md").read_text(encoding="utf-8")
    req_acc = [
        "PASS_WITH_HIGH_CONFIDENCE",
        "AUDIT_FOUNDATION_ONLY",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]
    for r in req_acc:
        if r not in acc_report:
            raise SystemExit(f"FAIL: Missing from acceptance report: {r}")
            
    # Check backend code for safety
    for root, _, files in os.walk("14_backend/audit_log"):
        for f in files:
            if not f.endswith(".py"): continue
            content = Path(os.path.join(root, f)).read_text(encoding="utf-8")
            if "os.system" in content or "subprocess" in content:
                raise SystemExit(f"FAIL: Dangerous module used in {f}")

    print("ORIGINAL_PLUS2C_IMMUTABLE_AUDIT_LOG_VALIDATION_PASS")

if __name__ == "__main__":
    check()
