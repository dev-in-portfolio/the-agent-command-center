#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    required_docs = [
        "14_backend/phase_4c_read_only_integration_plan.md",
        "14_backend/phase_4c_integration_source_inventory.md",
        "14_backend/phase_4c_github_read_only_contract.md",
        "14_backend/phase_4c_netlify_read_only_contract.md",
        "14_backend/phase_4c_status_snapshot_contract.md",
        "14_backend/phase_4c_external_api_safety_rules.md",
        "14_backend/phase_4c_cache_and_staleness_plan.md",
        "14_backend/phase_4c_error_handling_plan.md",
        "14_backend/phase_4c_observability_plan.md",
        "14_backend/phase_4c_dashboard_status_ui_plan.md",
        "14_backend/phase_4c_phase_4d_gate_review.md",
    ]
    required_reports = [
        "09_exports/backend_phase_4/backend_phase_4c_acceptance_report.md",
        "09_exports/backend_phase_4/backend_phase_4c_read_only_integration_report.md",
        "09_exports/backend_phase_4/backend_phase_4c_github_contract_report.md",
        "09_exports/backend_phase_4/backend_phase_4c_netlify_contract_report.md",
        "09_exports/backend_phase_4/backend_phase_4c_safety_report.md",
        "09_exports/backend_phase_4/backend_phase_4c_handoff_readiness_report.md",
    ]
    
    for f in required_docs + required_reports:
        if not (ROOT / f).exists():
            _fail(f"Required file missing: {f}")

    # Specific content checks
    github_contract = (ROOT / "14_backend/phase_4c_github_read_only_contract.md").read_text()
    if "Forbidden Actions" not in github_contract or "No Writing" not in github_contract:
        _fail("GitHub contract missing forbidden actions section")

    netlify_contract = (ROOT / "14_backend/phase_4c_netlify_read_only_contract.md").read_text()
    if "Forbidden Actions" not in netlify_contract or "No Manual Deploys" not in netlify_contract:
        _fail("Netlify contract missing forbidden actions section")

    safety_rules = (ROOT / "14_backend/phase_4c_external_api_safety_rules.md").read_text()
    if "Server-Side Execution" not in safety_rules or "Allowlisted Domains" not in safety_rules:
        _fail("External API safety rules missing core invariants")

    snapshot_contract = (ROOT / "14_backend/phase_4c_status_snapshot_contract.md").read_text()
    if "Static Snapshot" not in snapshot_contract or "Zero Secrets" not in snapshot_contract:
        _fail("Snapshot contract missing core concept")

    # Planning only checks
    for f in required_docs:
        content = (ROOT / f).read_text()
        if "planning document only" not in content and "planning only" not in content.lower():
             _fail(f"{f} missing 'planning only' disclaimer")

    # No implementation checks - ensure no new functions
    func_dir = ROOT / "netlify/functions"
    allowed_funcs = [
        "backend-manifest.js", 
        "health.js", 
        "status.js",
        "auth-status.js",
        "role-matrix.js",
        "request-storage-status.js",
        "audit-log-status.js",
        "approval-gate-status.js"
    ]
    actual_funcs = [f.name for f in func_dir.glob("*.js")]
    if sorted(actual_funcs) != sorted(allowed_funcs):
        _fail(f"Unexpected Netlify functions found: {actual_funcs}. Phase 4C should be planning only.")

    print("BACKEND_PHASE_4C_PLANNING_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
