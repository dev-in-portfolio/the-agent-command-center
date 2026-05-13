#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    required_files = [
        "netlify.toml",
        "netlify/functions/_shared/response.js",
        "netlify/functions/health.js",
        "netlify/functions/status.js",
        "netlify/functions/backend-manifest.js",
        "14_backend/README.md",
        "14_backend/api_contract.md",
        "14_backend/security_model.md",
        "14_backend/netlify_functions_manifest.md",
        "14_backend/future_backend_plan.md",
        "09_exports/backend_phase_4/backend_phase_4a_acceptance_report.md",
        "09_exports/backend_phase_4/backend_phase_4a_safety_report.md",
        "09_exports/backend_phase_4/backend_phase_4a_api_contract_report.md",
        "09_exports/backend_phase_4/backend_phase_4a_frontend_integration_report.md",
        "09_exports/backend_phase_4/backend_phase_4b_handoff_contract.md",
    ]
    for f in required_files:
        if not (ROOT / f).exists():
            _fail(f"Required file missing: {f}")

    # netlify.toml checks
    toml = (ROOT / "netlify.toml").read_text()
    if 'publish = "13_web_dashboard/dist"' not in toml:
        _fail("netlify.toml missing correct publish directory")
    if 'directory = "netlify/functions"' not in toml:
        _fail("netlify.toml missing correct functions directory")
    if 'from = "/api/*"' not in toml or 'to = "/.netlify/functions/:splat"' not in toml:
        _fail("netlify.toml missing /api/* redirect")

    # function logic checks
    func_files = [
        ROOT / "netlify/functions/health.js",
        ROOT / "netlify/functions/status.js",
        ROOT / "netlify/functions/backend-manifest.js"
    ]
    forbidden = [
        "process.env", "child_process", "exec(", "spawn(", "shell: true", "git ", "gh ",
        "TOKEN_", "SECRET_", "CREDENTIAL_", "XMLHttpRequest", "axios", "http://", "https://"
    ]
    for fpath in func_files:
        content = fpath.read_text()
        if "exports.handler" not in content:
            _fail(f"{fpath.name} missing exports.handler")
        if "command_execution" in content and "false" not in content:
            _fail(f"{fpath.name} might have enabled command execution")
        for word in forbidden:
            if word in content:
                _fail(f"{fpath.name} contains forbidden word: {word}")

    # JS allowed fetch check
    js = (ROOT / "13_web_dashboard" / "static" / "dashboard.js").read_text()
    if 'fetch("/api/health")' not in js and "fetch('/api/health')" not in js:
        _fail("dashboard.js missing allowed backend health fetch")
    
    # check for unauthorized fetch
    lines = js.splitlines()
    for line in lines:
        if "fetch(" in line:
             # Allow specific backend status fetches
             if any(x in line for x in ['/api/health', '/api/status', '/api/backend-manifest', './status_snapshot.json']):
                 continue
             _fail(f"dashboard.js contains unauthorized fetch: {line.strip()}")

    print("BACKEND_PHASE_4A_FOUNDATION_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
