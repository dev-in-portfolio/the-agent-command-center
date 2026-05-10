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

def run_script(script_path):
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") == "1":
        return ""
    result = subprocess.run(["python3", script_path], capture_output=True, text=True, env=os.environ.copy())
    if result.returncode != 0:
        print(f"FAIL: {script_path} failed with output:\n{result.stdout}\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def check_file_content(path, pattern, message):
    content = Path(path).read_text()
    ensure(re.search(pattern, content), message)

def check_forbidden_patterns(path, forbidden_list):
    content = Path(path).read_text()
    for pattern in forbidden_list:
        ensure(pattern not in content, f"Forbidden pattern '{pattern}' found in {path}")

def main():
    root_dir = Path(__file__).parent.parent
    runtime_dir = root_dir / "10_runtime"
    exports_dir = root_dir / "09_exports"

    # Required files
    v21_module = runtime_dir / "station_chief_v21_controlled_local_workspace_artifact_factory.py"
    v21_audit = exports_dir / "station_chief_v21_0_controlled_local_workspace_artifact_factory_preflight_audit.md"
    v21_report = exports_dir / "station_chief_runtime_v21_0_report.md"

    ensure(v21_module.exists(), "v21.0 module missing")
    ensure(v21_audit.exists(), "v21.0 preflight audit missing")
    ensure(v21_report.exists(), "v21.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"21\.0\.0"', "Runtime version not 21.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"21\.0\.0"', "Release lock not 21.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"21\.0\.0"', "Adapter version not 21.0.0")

    # Fast future file check
    future_patterns = ["*v21_1*", "*v21.1*", "*v22*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v21_0\.py",', "v21.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v21_0\.py",', "v21.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v21_0\.py":\s+return "21\.0\.0"', "v21.0 selector missing in runtime")

    # Read v21 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v21_controlled_local_workspace_artifact_factory as v21

    # Check constants
    ensure(v21.STATION_CHIEF_V21_CONTROLLED_LOCAL_WORKSPACE_VERSION == "21.0.0", "Module constant version mismatch")
    ensure(v21.STATION_CHIEF_V21_APPROVAL_PHRASE == "I_APPROVE_V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY", "Approval phrase mismatch")

    # Clean stale workspace artifacts before test
    workspace_dir = Path(v21.STATION_CHIEF_V21_CONTROLLED_WORKSPACE_DIR)
    if workspace_dir.exists():
        for f in workspace_dir.glob("*"):
            f.unlink()

    # Test preview-only path
    bundle_preview = v21.create_station_chief_v21_controlled_local_workspace_bundle(execute_artifact_factory_flag=False)
    ensure(bundle_preview["controlled_local_workspace_status"] == "CONTROLLED_LOCAL_WORKSPACE_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["artifact_factory_workpack_performed"] == False, "Workpack performed in preview")
    
    for key, path_str in v21.STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS.items():
        ensure(not Path(path_str).exists(), f"Artifact {key} created in preview")

    # Test approved execution path
    bundle_approved = v21.create_station_chief_v21_controlled_local_workspace_bundle(
        approval_phrase="I_APPROVE_V21_CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY",
        execute_artifact_factory_flag=True
    )
    ensure(bundle_approved["controlled_local_workspace_status"] == "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["artifact_factory_workpack_performed"] == True, "Workpack not performed in approved")
    ensure(bundle_approved["completed_action_count"] == 5, "Action count mismatch")
    ensure(bundle_approved["routed_v20_v19_v18_v17_operational_chain_performed"] == True, "Operational chain not performed")
    ensure(bundle_approved["json_receipt_artifact_written"] == True, "JSON not written")
    ensure(bundle_approved["markdown_summary_artifact_written"] == True, "Markdown not written")
    ensure(bundle_approved["csv_table_artifact_written"] == True, "CSV not written")
    ensure(bundle_approved["artifact_manifest_written"] == True, "Manifest not written")
    ensure(bundle_approved["artifact_readback_verified"] == True, "Readback verification failed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Incorrect file count")

    # Verify artifacts content
    for key, path_str in v21.STATION_CHIEF_V21_CONTROLLED_ARTIFACT_PATHS.items():
        p = Path(path_str)
        ensure(p.exists(), f"Artifact {key} missing after write")
        content = p.read_text()
        ensure("secrets" not in content.lower(), f"Secrets leaked to {key}")
        if key == "csv_table":
            ensure("property,value" in content, "CSV header missing")
        if key == "markdown_summary":
            ensure("# Station Chief v21" in content, "Markdown title missing")

    # Test denied execution path
    bundle_denied = v21.create_station_chief_v21_controlled_local_workspace_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_artifact_factory_flag=True
    )
    ensure(bundle_denied["controlled_local_workspace_status"] == "CONTROLLED_LOCAL_WORKSPACE_ARTIFACT_FACTORY_DENIED", "Denied status mismatch")
    ensure(bundle_denied["artifact_factory_workpack_performed"] == False, "Workpack performed in denied")

    # Boundary matrix
    matrix = v21.create_local_workspace_safety_boundary_matrix()
    ensure(matrix["controlled_json_receipt_artifact"] == "ALLOWED", "JSON not allowed in matrix")
    ensure(matrix["binary_document_generation"] == "DENIED", "Binary doc not denied in matrix")
    ensure(matrix["repo_write"] == "DENIED", "Repo write not denied in matrix")

    # Forbidden patterns
    forbidden_v21 = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "open(", "import shlex", "system(", "popen", "invoke_tool(",
        "external_tool_invocation_performed = True", "api_call_performed = True",
        "network_access_performed = True", "socket_access_performed = True", "dns_resolution_performed = True",
        "credential_access_performed = True", "credential_vault_access_performed = True", "token_access_performed = True",
        "secret_read_performed = True", "private_key_read_performed = True", "signing_key_read_performed = True",
        "environment_read_performed = True", "real_signature_performed = True", "real_encryption_performed = True",
        "real_decryption_performed = True", "run_task", "execute_task", "execute_user",
        "arbitrary_user_task_execution_performed = True", "user_task_execution_performed = True",
        "worker.start", "start_worker", "real_worker_process_started = True", "background_agent_started = True",
        "live_worker_started = True", "daemon_started = True", "background_process_started = True",
        "create_real_queue", "queue_write_performed = True", "enqueue_live", "route_live", "orchestrate_live",
        "deployment_performed = True", "production_execution_performed = True", "rollback_execution_performed = True",
        "recovery_execution_performed = True", "autonomous_self_activation_performed = True",
        "full_external_prod_agent_army_activation_performed = True",
        "glob(", "rglob(", "TO" + "DO", "Not" + "Implemented"
    ]
    check_forbidden_patterns(v21_module, forbidden_v21)

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v21-approved-artifact-factory', "Missing v21 CLI flag")

    # Doctrine
    check_file_content(v21_report, "Controlled Local Workspace Tool Expansion", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v21.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "20_0", "19_0", "18_0", "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V21_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
