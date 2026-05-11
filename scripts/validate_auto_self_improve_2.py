#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
import re
import os
import json

def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)

def main():
    print("Starting auto-self-improve-2 Lab Validation...")

    root_dir = Path(__file__).parent.parent
    runtime_dir = root_dir / "10_runtime"
    scripts_dir = root_dir / "scripts"
    exports_dir = root_dir / "09_exports"
    
    # 1. Basic File Presence
    lab_module = runtime_dir / "auto_self_improve_2_sandbox.py"
    ensure(lab_module.exists(), "Lab module missing")
    ensure((exports_dir / "auto_self_improve_2_lab_doctrine.md").exists(), "Lab doctrine missing")
    ensure((exports_dir / "auto_self_improve_2_report.md").exists(), "Lab report missing")
    ensure((exports_dir / "auto_self_improve_2_promotion_barrier.md").exists(), "Promotion barrier missing")

    # 2. Module Constants and Imports
    sys.path.insert(0, str(runtime_dir))
    import auto_self_improve_2_sandbox as lab2
    
    ensure(lab2.AUTO_SELF_IMPROVE_2_LAB_ID == "auto-self-improve-2", "Lab ID mismatch")
    ensure(lab2.AUTO_SELF_IMPROVE_2_CAN_SELF_AUTHORIZE_SANDBOX is True, "Self-authorization must be allowed for sandbox")
    ensure(lab2.AUTO_SELF_IMPROVE_2_CAN_MUTATE_OFFICIAL is False, "Official mutation must be denied")
    
    # 3. Forbidden Implementation Patterns
    content = lab_module.read_text()
    forbidden = [
        "import os", "import subprocess", "import socket", "import urllib", "import requests",
        "import threading", "import multiprocessing", "import asyncio", "import importlib",
        "shutil", "tempfile"
    ]
    for pattern in forbidden:
        ensure(pattern not in content, f"Forbidden pattern '{pattern}' found in module")

    # 4. Functional Checks: Sandbox Authorization
    manifest = lab2.create_auto_self_improve_2_manifest()
    ensure(manifest["sandbox_self_authorization_allowed"] is True, "Manifest denies sandbox self-authorization")
    ensure(manifest["official_mutation_allowed"] is False, "Manifest allows official mutation")
    
    # Check low-risk authorization
    candidate_low = lab2.create_sandbox_improvement_candidate(candidate_title="low_risk", risk_level="low")
    eval_low = lab2.evaluate_sandbox_candidate(candidate_low)
    receipt_low = lab2.create_sandbox_self_authorization_receipt(candidate_low, eval_low)
    ensure(receipt_low["sandbox_self_authorization_granted"] is True, "Authorization denied for low risk candidate")
    
    # Check high-risk authorization
    candidate_high = lab2.create_sandbox_improvement_candidate(candidate_title="high_risk", risk_level="high")
    eval_high = lab2.evaluate_sandbox_candidate(candidate_high)
    receipt_high = lab2.create_sandbox_self_authorization_receipt(candidate_high, eval_high)
    ensure(receipt_high["sandbox_self_authorization_granted"] is False, "Authorization granted for high risk candidate")

    # 5. Sandbox Artifact Writes
    print("Testing sandbox artifact writes...")
    res = lab2.write_sandbox_artifact("sandbox_mutation_audit", {"test": True}, receipt_low)
    ensure(res["artifact_write_performed"] is True, "Sandbox write failed")
    ensure(res["controlled_artifact_path"].startswith("/tmp/auto_self_improve_2_sandbox"), "Wrong sandbox path")
    ensure("agent-command-center" not in res["controlled_artifact_path"], "Sandbox path in repo")

    # 6. Core v25 Validator Pass
    print("Verifying core v25 validator status...")
    v25_script = scripts_dir / "validate_station_chief_runtime_v25_0.py"
    if v25_script.exists():
        result = subprocess.run(["python3", str(v25_script)], capture_output=True, text=True)
        ensure(result.returncode == 0, f"v25 core validator failed:\n{result.stdout}\n{result.stderr}")

    # 7. Workflow Integration
    workflow_path = root_dir / ".github/workflows/station-chief-validation.yml"
    if workflow_path.exists():
        wf_content = workflow_path.read_text()
        ensure("validate_auto_self_improve_2.py" in wf_content, "Validator missing from CI workflow")

    print("AUTO_SELF_IMPROVE_2_VALIDATION_PASS")

if __name__ == "__main__":
    main()
