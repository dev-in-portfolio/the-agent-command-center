#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def check_forbidden_paths():
    print("Checking forbidden diff paths...")
    result = subprocess.run(["git", "diff", "--name-only", "origin/master..HEAD"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print("WARNING: Could not check git diff, assuming detached head or CI.")
        return
        
    changed_files = result.stdout.splitlines()
    forbidden_prefixes = [
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "11_interface/",
        "12_tui/",
        "10_runtime/"
    ]
    
    allowed_prefixes = [
        "scripts/validate_original_plus2c",
        "scripts/validate_original_plus2b",
        "scripts/validate_original_plus2a",
        "netlify/functions/audit-log-status.js",
        "14_backend/audit_log/",
        "13_web_dashboard/",
        "14_backend/auth/",
        "14_backend/request_storage/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "09_exports/interface_phase_5/",
        "09_exports/original_plus1/",
        "09_exports/original_plus2/",
        "netlify/functions/auth-status.js",
        "netlify/functions/role-matrix.js",
        "netlify/functions/request-storage-status.js",
        "netlify/functions/backend-manifest.js",
        "netlify/functions/_shared/models/",
        "scripts/validate_",
    ]
    
    for f in changed_files:
        if any(f.startswith(p) for p in allowed_prefixes):
            continue
        for prefix in forbidden_prefixes:
            if f.startswith(prefix):
                _fail(f"Forbidden path modified: {f}")

def check_fetch_targets():
    print("Checking fetch targets...")
    import re
    allowed_targets = [
        "./original_plus2c_audit_log_model.json",
        "/api/audit-log-status",
        '/api/health', '/api/status', '/api/backend-manifest',
        '/api/auth-status', '/api/role-matrix', '/api/request-storage-status',
        './status_snapshot.json',
        './phase4d_identity_schema.json', './phase4d_action_schema.json',
        './phase4d_audit_schema.json', './phase4d_approval_schema.json',
        './phase4d_risk_model.json',
        './original_plus1b_contract_schemas.json',
        './original_plus1c_readiness_qa_model.json',
        './original_plus1d_backend_boundary_model.json',
        './original_plus1e_backend_build_tickets.json',
        './original_plus2a_auth_foundation_model.json',
        './original_plus2b_request_storage_model.json',
    ]
    
    js_path = ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js"
    if js_path.exists():
        js_content = js_path.read_text(encoding="utf-8", errors="replace")
        fetches = re.findall(r'fetch\(["\']([^"\']+)["\']\)', js_content)
        for target in fetches:
            if target not in allowed_targets:
                _fail(f"Unauthorized fetch target found in JS: {target}")

def main():
    check_forbidden_paths()
    # 1. Run Foundation validator
    res = _run([sys.executable, str(ROOT / "scripts" / "validate_backend_phase_4a_foundation.py")])
    if res.returncode != 0:
        _fail(f"Foundation validation failed: {res.stdout} {res.stderr}")
    
    # 2. Run Phase 3 validators (to ensure no regressions)
    res = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_3_dashboard.py")])
    if res.returncode != 0:
        _fail(f"Phase 3 Dashboard validation failed: {res.stdout} {res.stderr}")

    res = _run([sys.executable, str(ROOT / "scripts" / "validate_interface_phase_3_e2e.py")])
    if res.returncode != 0:
        _fail(f"Phase 3 E2E validation failed: {res.stdout} {res.stderr}")

    # 3. Check for specific panel in built index.html
    index_html = (ROOT / "13_web_dashboard" / "dist" / "index.html").read_text()
    if 'id="backend-status-panel"' not in index_html:
        _fail("Backend status panel missing from built index.html")

    check_fetch_targets()

    print("BACKEND_PHASE_4A_E2E_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
