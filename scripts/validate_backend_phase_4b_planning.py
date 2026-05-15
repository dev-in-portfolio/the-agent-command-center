#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    required_docs = [
        "14_backend/phase_4b_auth_permissions_plan.md",
        "14_backend/phase_4b_role_model.md",
        "14_backend/phase_4b_endpoint_permission_matrix.md",
        "14_backend/phase_4b_secret_handling_plan.md",
        "14_backend/phase_4b_audit_logging_plan.md",
        "14_backend/phase_4b_rate_limit_and_abuse_plan.md",
        "14_backend/phase_4b_threat_model.md",
        "14_backend/phase_4b_action_queue_concept.md",
        "14_backend/phase_4b_dashboard_ui_implications.md",
        "14_backend/phase_4c_handoff_contract.md",
        "14_backend/phase_4d_handoff_contract.md",
    ]
    required_reports = [
        "09_exports/backend_phase_4/backend_phase_4b_acceptance_report.md",
        "09_exports/backend_phase_4/backend_phase_4b_security_architecture_report.md",
        "09_exports/backend_phase_4/backend_phase_4b_permission_model_report.md",
        "09_exports/backend_phase_4/backend_phase_4b_threat_model_report.md",
        "09_exports/backend_phase_4/backend_phase_4b_handoff_readiness_report.md",
    ]
    
    for f in required_docs + required_reports:
        if not (ROOT / f).exists():
            _fail(f"Required file missing: {f}")

    # Content checks
    doc_content = (ROOT / "14_backend/phase_4b_role_model.md").read_text()
    if "Public Viewer" not in doc_content or "Operator" not in doc_content or "Admin" not in doc_content:
        _fail("Role model doc missing required roles")

    matrix_content = (ROOT / "14_backend/phase_4b_endpoint_permission_matrix.md").read_text()
    if "/api/health" not in matrix_content or "/api/status" not in matrix_content:
        _fail("Endpoint matrix missing required endpoints")

    # Planning only checks
    for f in required_docs:
        content = (ROOT / f).read_text()
        if "planning document only" not in content and "planning only" not in content.lower():
             _fail(f"{f} missing 'planning only' disclaimer")

    # No implementation checks
    func_dir = ROOT / "netlify/functions"
    allowed_funcs = [
        "backend-manifest.js", 
        "health.js", 
        "status.js",
        "auth-status.js",
        "role-matrix.js",
        "request-storage-status.js",
        "audit-log-status.js",
        "approval-gate-status.js",
        "dry-run-status.js"
    ]
    actual_funcs = [f.name for f in func_dir.glob("*.js")]
    if sorted(actual_funcs) != sorted(allowed_funcs):
        _fail(f"Unexpected Netlify functions found: {actual_funcs}. Phase 4B should be planning only.")

    print("BACKEND_PHASE_4B_PLANNING_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
