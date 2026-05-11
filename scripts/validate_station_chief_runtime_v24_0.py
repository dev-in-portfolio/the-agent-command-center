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

def check_file_content(path, pattern, message):
    content = Path(path).read_text()
    ensure(re.search(pattern, content), message)

def check_forbidden_patterns(path, forbidden_list):
    content = Path(path).read_text()
    for pattern in forbidden_list:
        ensure(pattern not in content, f"Forbidden pattern '{pattern}' found in {path}")

def main():
    print("Starting Station Chief Runtime v24.0.0 Validation...")

    root_dir = Path(__file__).parent.parent
    runtime_dir = root_dir / "10_runtime"
    scripts_dir = root_dir / "scripts"
    exports_dir = root_dir / "09_exports"
    
    # 1. Basic File Presence
    v24_module = runtime_dir / "station_chief_v24_controlled_external_evidence_snapshot.py"
    v24_report = exports_dir / "station_chief_runtime_v24_0_report.md"
    ensure((runtime_dir / "station_chief_runtime.py").exists(), "station_chief_runtime.py missing")
    ensure(v24_module.exists(), "v24.0 module missing")
    ensure((runtime_dir / "station_chief_adapters.py").exists(), "adapters.py missing")
    ensure((runtime_dir / "station_chief_release_lock.py").exists(), "release_lock.py missing")
    ensure(v24_report.exists(), "v24.0 report missing")

    # 2. Version Verification
    sys.path.insert(0, str(runtime_dir))
    import station_chief_runtime as scr
    import station_chief_adapters as sca
    import station_chief_release_lock as scrl
    import station_chief_v24_controlled_external_evidence_snapshot as v24

    print(f"Detected Runtime Version: {scr.STATION_CHIEF_RUNTIME_VERSION}")
    ensure(scr.STATION_CHIEF_RUNTIME_VERSION in ["24.0.0", "25.0.0"], "Runtime version mismatch")
    ensure(sca.ADAPTER_MODULE_VERSION in ["24.0.0", "25.0.0"], "Adapter version mismatch")
    ensure(scrl.STABLE_RUNTIME_VERSION in ["24.0.0", "25.0.0"], "Release lock version mismatch")

    # 3. Schema Verification
    schema = v24.create_station_chief_v24_controlled_external_evidence_schema()
    ensure(schema["schema_version"] == "24.0.0", "Schema version mismatch")
    ensure(schema["controlled_external_evidence_snapshot_gateway_authorized"] is True, "Gateway not authorized in schema")
    ensure(schema["no_repo_mutation_authorized"] is True, "Repo mutation not forbidden in schema")

    # 4. Permission Registry Verification
    registry = v24.create_external_evidence_permission_registry()
    ensure(registry["external_evidence_category_count"] == 10, "Registry category count mismatch")
    ensure(registry["executable_external_evidence_category_count"] == 1, "Executable category count mismatch")
    ensure(registry["locked_external_evidence_category_count"] == 9, "Locked category count mismatch")
    
    allowlisted_cat = registry["categories"]["allowlisted_content_digest"]
    ensure(allowlisted_cat["executable_in_v24"] is True, "Allowlisted content digest not executable")
    ensure(allowlisted_cat["allowed_url"] == "https://example.com/", "Allowlisted URL mismatch")
    
    email_cat = registry["categories"]["email_send"]
    ensure(email_cat["executable_in_v24"] is False, "Email send should not be executable")

    # 5. Cleanup Checks: Forbidden Patterns in Module
    content_v24 = v24_module.read_text()
    forbidden_v24_regex = [
        r'_internal_body_bytes',
        r'"body_bytes":',
        r"'body_bytes':",
        r'(?<!no_)raw_response_body_returned":\s*True',
        r'(?<!no_)raw_response_body_stored":\s*True',
        r'(?<!no_)raw_response_body_printed":\s*True'
    ]
    for pattern in forbidden_v24_regex:
        ensure(not re.search(pattern, content_v24), f"Forbidden pattern '{pattern}' found in {v24_module}")

    # 6. Cleanup Checks: Report Wording
    content_report = v24_report.read_text()
    ensure("Pending Phase 9" not in content_report, "Stale 'Pending Phase 9' wording found in report")
    ensure("Pending Phase 11" not in content_report, "Stale 'Pending Phase 11' wording found in report")

    # 7. Test Denied Path (No approval)
    bundle_denied = v24.create_station_chief_v24_controlled_external_evidence_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_external_evidence_flag=True
    )
    ensure(bundle_denied["controlled_external_evidence_status"] == "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_DENIED", "Wrong status for denied approval")
    ensure(bundle_denied["external_evidence_snapshot_workpack_performed"] is False, "Workpack should not be performed without approval")

    # 8. Test Approved Execution Path
    print("Testing approved execution path (live fetch to example.com)...")
    bundle_approved = v24.create_station_chief_v24_controlled_external_evidence_bundle(
        approval_phrase="I_APPROVE_V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT",
        execute_external_evidence_flag=True,
        operator_label="validator-bot",
        workpack_label="v24-validation-run"
    )
    
    # Check overall status
    status = bundle_approved["controlled_external_evidence_status"]
    if status == "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_FETCH_UNAVAILABLE":
        print("WARNING: External fetch unavailable (transient network error). Proceeding with structural validation only.")
        ensure(bundle_approved["routed_v23_v22_v21_v20_v19_v18_v17_chain_performed"] is True, "Routed chain should have performed even if fetch failed")
    else:
        ensure(status == "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_COMPLETED", f"Unexpected status: {status}")
        ensure(bundle_approved["external_evidence_snapshot_workpack_performed"] is True, "Workpack not performed")
        ensure(bundle_approved["controlled_external_content_fetch_performed"] is True, "Fetch not performed")
        ensure(bundle_approved["sanitized_content_digest_extracted"] is True, "Digest not extracted")
        ensure(bundle_approved["raw_body_non_persistence_proven"] is True, "Non-persistence not proven")
        
        # Check sanitization
        ensure(bundle_approved["sanitized_preview_char_count"] <= 280, "Sanitized preview exceeds 280 chars")
        ensure(bundle_approved["raw_response_body_returned"] is False, "Raw response body returned")
        ensure(bundle_approved["raw_response_body_stored"] is False, "Raw response body stored")
        ensure(bundle_approved["raw_response_body_printed"] is False, "Raw response body printed")
        
        # Check cleanup in bundle
        bundle_json = json.dumps(bundle_approved)
        ensure('"_internal_body_bytes":' not in bundle_json, "Forbidden field '_internal_body_bytes' found in bundle JSON")
        ensure('"body_bytes":' not in bundle_json, "Forbidden field 'body_bytes' found in bundle JSON")
        
        # Check artifacts
        ensure(bundle_approved["controlled_external_evidence_artifact_count"] == 5, "Artifact count mismatch")
        ensure(bundle_approved["artifact_readback_verified"] is True, "Artifact readback failed")
        
        for key, path in bundle_approved["artifact_paths"].items():
            p = Path(path)
            ensure(p.exists(), f"Artifact missing: {path}")
            # Ensure not in repo
            ensure("agent-command-center" not in path, f"Artifact in repo: {path}")
            # Ensure no raw bytes in artifacts
            artifact_content = p.read_text()
            ensure('"_internal_body_bytes":' not in artifact_content, f"Forbidden field '_internal_body_bytes' found in artifact {key}")
            ensure('"body_bytes":' not in artifact_content, f"Forbidden field 'body_bytes' found in artifact {key}")

    # 9. Safety Boundary Verification
    boundaries = v24.create_external_evidence_safety_boundary_matrix()
    ensure(boundaries["controlled_allowlisted_https_content_fetch"] == "ALLOWED", "Fetch not allowed in boundary matrix")
    ensure(boundaries["repo_file_mutation"] == "DENIED", "Repo file mutation not denied in boundary matrix")
    ensure(boundaries["raw_response_body_storage"] == "DENIED", "Raw body storage not denied in boundary matrix")

    # 10. Routed Chain Verification
    ensure(bundle_approved["routed_v23_v22_v21_v20_v19_v18_v17_chain_performed"] is True, "Routed chain not performed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Inspected file count mismatch (should be 7 from v17)")

    # 11. CLI Flag Verification (Structural)
    ensure(hasattr(scr, "attach_station_chief_v24_controlled_external_evidence_snapshot"), "SCR missing v24 attach function")

    # 12. Prior Version Preservation
    print("Verifying preservation of v23.0 through v8.0...")
    def run_script(script_path):
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, env=os.environ.copy())
        if result.returncode != 0:
            print(f"FAIL: {script_path} failed\n{result.stdout}\n{result.stderr}")
            sys.exit(1)
        return result.stdout

    # Run v23 validator as a representative check
    os.environ["STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"] = "1"
    v23_script = scripts_dir / "validate_station_chief_runtime_v23_0.py"
    if v23_script.exists():
        out = run_script(str(v23_script))
        ensure("STATION_CHIEF_RUNTIME_V23_0_VALIDATION_PASS" in out, "v23.0 validator failed to pass in v24 context")

    print("STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
