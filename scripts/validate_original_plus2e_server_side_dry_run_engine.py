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
        "Original +2E",
        "Server-Side Dry-Run Engine Foundation",
        "SERVER-SIDE DRY-RUN ENGINE FOUNDATION",
        "DRY-RUN REQUEST CONTRACT",
        "DRY-RUN PLAN CONTRACT",
        "DRY-RUN RESULT CONTRACT",
        "DRY-RUN EXECUTION NOT CONFIGURED",
        "DRY-RUN STORAGE NOT CONFIGURED",
        "DRY-RUN STATUS",
        "DRY-RUN ADAPTER BOUNDARY",
        "NO COMMAND EXECUTION",
        "NO SUBPROCESS",
        "NO EXTERNAL SYSTEM WRITES",
        "NO DEPLOY / MERGE / PUSH / PR CONTROLS",
        "NOT_READY_FOR_DRY_RUN_EXECUTION",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Dry-Run Engine Status Panel",
        "Dry-Run Request Schema Panel",
        "Dry-Run Plan Schema Panel",
        "Dry-Run Result Schema Panel",
        "Dry-Run Impact Boundary Panel",
        "Dry-Run Adapter Boundary Panel",
        "Dry-Run Validation Preview Panel",
        "Disabled Dry-Run Execution Boundary Panel",
        "Dry-Run Evidence Package Contract Panel",
        "Future Dry-Run Dependency Panel",
        "Copy dry-run request schema",
        "Copy dry-run plan schema",
        "Copy dry-run result schema",
        "Copy dry-run impact boundary",
        "Copy dry-run adapter boundary",
        "Copy disabled dry-run execution boundary report",
        "Copy dry-run evidence package contract",
        "Copy future dry-run dependency checklist",
        "Copy +2E validation checklist"
    ]
    
    for req in required_strings:
        if req not in index_text:
            raise SystemExit(f"FAIL: Missing from index.html: {req}")
            
    forbidden_controls = [
        "Run dry-run",
        "Execute dry-run",
        "Start dry-run",
        "Save dry-run result",
        "Create evidence package"
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
        "/api/approval-gate-status",
        "/api/dry-run-status",
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
        "./original_plus2c_audit_log_model.json",
        "./original_plus2d_approval_gate_model.json",
        "./original_plus2e_dry_run_engine_model.json"
    }
    for f in fetches:
        if f not in allowed_fetch:
            raise SystemExit(f"FAIL: Unauthorized fetch: {f}")

    if not Path("14_backend/dry_run").exists():
        raise SystemExit("FAIL: Missing 14_backend/dry_run directory")
        
    schemas = Path("14_backend/dry_run/schemas.json").read_text(encoding="utf-8")
    for key in ["dry_run_request_schema", "dry_run_plan_schema", "dry_run_result_schema", "impact_model"]:
        if f'"{key}"' not in schemas:
            raise SystemExit(f"FAIL: Missing key {key} in schemas.json")
            
    acc_report = Path("09_exports/original_plus2/original_plus2e_acceptance_report.md").read_text(encoding="utf-8")
    req_acc = [
        "PASS_WITH_HIGH_CONFIDENCE",
        "DRY_RUN_FOUNDATION_ONLY",
        "NOT_READY_FOR_REAL_AUTOMATION"
    ]
    for r in req_acc:
        if r not in acc_report:
            raise SystemExit(f"FAIL: Missing from acceptance report: {r}")
            
    # Check backend code for safety
    for root, _, files in os.walk("14_backend/dry_run"):
        for f in files:
            if not f.endswith(".py"): continue
            content = Path(os.path.join(root, f)).read_text(encoding="utf-8")
            if "os.system" in content or "subprocess" in content or "shutil" in content:
                # Exception for shutil only if it's safe (it's not authorized here)
                raise SystemExit(f"FAIL: Dangerous module used in {f}")

    print("ORIGINAL_PLUS2E_SERVER_SIDE_DRY_RUN_ENGINE_VALIDATION_PASS")

if __name__ == "__main__":
    check()
