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
    
    # 2.1 Timestamp Logic Verification
    ensure(hasattr(lab2, "create_sandbox_audit_timestamp"), "create_sandbox_audit_timestamp helper missing")
    ts_meta = lab2.create_sandbox_audit_timestamp()
    ensure(ts_meta["timestamp_format"] == "utc_iso_8601", "Invalid timestamp format")
    ensure(ts_meta["timestamp_source"] == "python_datetime_standard_library", "Invalid timestamp source")
    ensure(ts_meta["environment_read_performed"] is False, "Timestamp helper must not read environment")
    ensure(ts_meta["credential_access_performed"] is False, "Timestamp helper must not access credentials")
    ensure(ts_meta["secret_read_performed"] is False, "Timestamp helper must not read secrets")
    ensure(ts_meta["network_access_performed"] is False, "Timestamp helper must not access network")
    
    ts_val = ts_meta["timestamp_utc"]
    ensure(isinstance(ts_val, str) and len(ts_val) > 0, "Timestamp value must be a non-empty string")
    ensure("+00:00" in ts_val or ts_val.endswith("Z"), "Timestamp must contain UTC timezone info")
    
    # Check placeholder removal
    lab_content = lab_module.read_text()
    ensure("'timestamp': 0" not in lab_content, "Placeholder 'timestamp': 0 still exists")
    ensure('"timestamp": 0' not in lab_content, 'Placeholder "timestamp": 0 still exists')
    ensure("timestamp_created_for" in lab_content, "Audit timestamp implementation not found in module")
    
    # 2.2 Evidence Path Verification
    ensure(hasattr(lab2, "verify_repo_relative_evidence_paths"), "verify_repo_relative_evidence_paths missing")
    ev_res = lab2.verify_repo_relative_evidence_paths(["10_runtime/auto_self_improve_2_sandbox.py"])
    ensure(ev_res["all_paths_exist"] is True, "Valid path failed verification")
    ensure(ev_res["valid_path_count"] == 1, "Wrong valid path count")
    
    ev_res_fake = lab2.verify_repo_relative_evidence_paths(["no_such_file_ever.py"])
    ensure(ev_res_fake["all_paths_exist"] is False, "Fake path passed verification")
    
    ev_res_abs = lab2.verify_repo_relative_evidence_paths(["/etc/passwd"])
    ensure(ev_res_abs["all_paths_repo_relative"] is False, "Absolute path not rejected")
    
    # 2.3 Barrier Doctrine Hashing
    ensure(hasattr(lab2, "create_promotion_barrier_doctrine_hash"), "create_promotion_barrier_doctrine_hash missing")
    barrier_hash = lab2.create_promotion_barrier_doctrine_hash()
    ensure(barrier_hash["doctrine_file_exists"] is True, "Doctrine file not found")
    ensure(barrier_hash["doctrine_sha256"] is not None, "Doctrine hash missing")
    ensure(barrier_hash["doctrine_content_returned"] is False, "Doctrine content leaked in manifest")
    
    # 2.4 Sandbox Isolation
    ensure(hasattr(lab2, "create_sandbox_run_directory"), "create_sandbox_run_directory missing")
    run_dir = lab2.create_sandbox_run_directory(candidate_id="test-c-001")
    ensure(run_dir["run_directory"].startswith("/tmp/auto_self_improve_2_sandbox/test-c-001"), "Run directory isolation failed")
    
    # 2.5 Runtime Checksum Manifest
    ensure(hasattr(lab2, "create_lab_runtime_checksum_manifest"), "create_lab_runtime_checksum_manifest missing")
    checksums = lab2.create_lab_runtime_checksum_manifest()
    ensure(checksums["file_count"] == 4, f"Checksum file count mismatch: {checksums['file_count']}")
    ensure(checksums["all_expected_files_present"] is True, "Missing files in checksum manifest")
    
    # 2.6 Promotion Snippet
    ensure(hasattr(lab2, "create_operator_promotion_review_snippet"), "create_operator_promotion_review_snippet missing")
    snippet = lab2.create_operator_promotion_review_snippet()
    ensure(snippet["official_promotion_performed"] is False, "Snippet must not perform promotion")
    ensure(snippet["operator_approval_required"] is True, "Snippet must require operator approval")
    
    # 2.7 Heuristic Scoring
    ensure(hasattr(lab2, "score_candidate_utility"), "score_candidate_utility missing")
    score_low = lab2.score_candidate_utility({"title": "Fix typo", "risk_level": "low"})
    score_high = lab2.score_candidate_utility({"title": "Critical barrier fix", "risk_level": "low"})
    # Barrier fix should score higher on safety
    ensure(score_high["safety_value_score"] > score_low["safety_value_score"], "Scoring heuristic not working for safety")

    # 2.8 Safety Matrix
    ensure(hasattr(lab2, "get_auto_self_improve_2_safety_matrix"), "get_auto_self_improve_2_safety_matrix missing")
    safety_matrix = lab2.get_auto_self_improve_2_safety_matrix()
    ensure("allowed" in safety_matrix, "Safety matrix missing allowed list")
    ensure("denied" in safety_matrix, "Safety matrix missing denied list")
    ensure("mutate_official_repo" in safety_matrix["denied"], "Official mutation not denied in matrix")

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
    
    # Check low-risk authorization (Positive Control)
    candidate_low = lab2.create_sandbox_improvement_candidate(
        candidate_title="low_risk", 
        risk_level="low", 
        evidence_paths=["10_runtime/auto_self_improve_2_sandbox.py"]
    )
    eval_low = lab2.evaluate_sandbox_candidate(candidate_low)
    receipt_low = lab2.create_sandbox_self_authorization_receipt(candidate_low, eval_low)
    ensure(receipt_low["sandbox_self_authorization_granted"] is True, "Authorization denied for valid low risk candidate")
    
    # BG001 Regression: Fake evidence must deny self-authorization
    candidate_fake = lab2.create_sandbox_improvement_candidate(
        candidate_title="fake_evidence", 
        risk_level="low", 
        evidence_paths=["no_such_file_should_exist_12345.py"]
    )
    eval_fake = lab2.evaluate_sandbox_candidate(candidate_fake)
    receipt_fake = lab2.create_sandbox_self_authorization_receipt(candidate_fake, eval_fake)
    ensure(candidate_fake["evidence_paths_verified"] is False, "Fake evidence path verified")
    ensure(candidate_fake["evidence_verified"] is False, "Fake evidence flagged as verified")
    ensure(candidate_fake["self_authorization_eligible"] is False, "Fake evidence candidate eligible")
    ensure(receipt_fake["sandbox_self_authorization_granted"] is False, "Authorization granted for fake evidence")
    ensure(receipt_fake["fake_evidence_self_authorization_allowed"] is False, "Fake evidence explicitly allowed")
    ensure(receipt_fake["denial_reason"] == "missing_verified_evidence_denied", "Wrong denial reason for fake evidence")
    
    # BG004 Regression: external repo_root override probe blocked
    override_check = lab2.verify_repo_relative_evidence_paths(["etc/passwd"], repo_root="/")
    ensure(override_check["repo_root_override_requested"] is True, "Override not logged")
    ensure(override_check["repo_root_override_allowed"] is False, "Override mistakenly allowed")
    ensure(override_check["repo_root_override_rejected"] is True, "Override not rejected")
    ensure(override_check["external_repo_root_probe_blocked"] is True, "External probe not blocked")
    ensure(override_check["all_paths_exist"] is False, "External path checked and found")
    ensure(override_check["verification_passed"] is False, "Override probe passed verification")
    ensure(override_check["repo_root_used"] != "/", "Used external repo root")
    
    # BG012 Regression: No evidence low-risk must deny self-authorization
    candidate_none = lab2.create_sandbox_improvement_candidate(
        candidate_title="no_evidence", 
        risk_level="low", 
        evidence_paths=None
    )
    eval_none = lab2.evaluate_sandbox_candidate(candidate_none)
    receipt_none = lab2.create_sandbox_self_authorization_receipt(candidate_none, eval_none)
    ensure(candidate_none["evidence_path_verification"]["path_count"] == 0, "Non-zero path count for None")
    ensure(candidate_none["evidence_present"] is False, "Evidence marked present for None")
    ensure(candidate_none["evidence_verified"] is False, "None evidence flagged as verified")
    ensure(candidate_none["self_authorization_eligible"] is False, "None evidence candidate eligible")
    ensure(receipt_none["sandbox_self_authorization_granted"] is False, "Authorization granted for no evidence")
    ensure(receipt_none["no_evidence_self_authorization_allowed"] is False, "No evidence explicitly allowed")
    ensure(receipt_none["denial_reason"] == "missing_verified_evidence_denied", "Wrong denial reason for no evidence")
    
    # Check high-risk authorization
    candidate_high = lab2.create_sandbox_improvement_candidate(candidate_title="high_risk", risk_level="high")
    eval_high = lab2.evaluate_sandbox_candidate(candidate_high)
    receipt_high = lab2.create_sandbox_self_authorization_receipt(candidate_high, eval_high)
    ensure(receipt_high["sandbox_self_authorization_granted"] is False, "Authorization granted for high risk candidate")
    ensure(receipt_high["official_repo_authorization_granted"] is False, "High risk must not allow official mutation")
    ensure(receipt_high["promotion_authorization_granted"] is False, "High risk must not allow promotion")
    ensure(receipt_high["deployment_authorization_granted"] is False, "High risk must not allow deployment")
    ensure(receipt_high["credentials_authorization_granted"] is False, "High risk must not allow credentials")
    
    # Ensure dynamic_bytecode_patching is denied
    bundle_bad = lab2.create_auto_self_improve_2_bundle(
        candidate_title="dynamic_bytecode_patching", 
        risk_level="high",
        evidence_paths=["10_runtime/auto_self_improve_2_sandbox.py"]
    )
    ensure("dynamic_bytecode_patching" in bundle_bad["safety_matrix"]["denied"], "Bytecode patching not in denied list")

    # 5. Sandbox Artifact Writes
    print("Testing sandbox artifact writes...")
    # Trigger a full bundle to test manifest creation
    bundle_test = lab2.create_auto_self_improve_2_bundle(
        candidate_title="manifest_test", 
        risk_level="low",
        evidence_paths=["10_runtime/auto_self_improve_2_sandbox.py"]
    )
    writes = bundle_test.get("artifact_writes", {})
    
    ensure("audit" in writes and writes["audit"]["artifact_write_performed"] is True, "Sandbox audit write failed")
    ensure("manifest" in writes and writes["manifest"]["artifact_write_performed"] is True, "Sandbox manifest write failed")
    
    manifest_path = writes["manifest"]["controlled_artifact_path"]
    ensure(manifest_path.startswith("/tmp/auto_self_improve_2_sandbox"), "Wrong sandbox path for manifest")
    ensure("agent-command-center" not in manifest_path, "Sandbox path in repo")

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

    # 8. Discovery and Menu Verification
    menu_path = exports_dir / "station_chief_v25_0_operator_command_menu.md"
    if menu_path.exists():
        menu_content = menu_path.read_text()
        ensure("agent-command-center-3" in menu_content, "Menu missing lab 2 repo")
        ensure("auto-self-improve-2" in menu_content, "Menu missing lab 2 identity")
        ensure("Contained sandbox self-improvement" in menu_content, "Menu missing lab 2 mode")

    print("AUTO_SELF_IMPROVE_2_VALIDATION_PASS")

if __name__ == "__main__":
    main()
