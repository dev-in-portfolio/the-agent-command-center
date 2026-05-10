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
    result = subprocess.run(["python3", script_path], capture_output=True, text=True)
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
    v20_module = runtime_dir / "station_chief_v20_operational_agent_army_mode.py"
    v20_audit = exports_dir / "station_chief_v20_0_operational_agent_army_mode_preflight_audit.md"
    v20_report = exports_dir / "station_chief_runtime_v20_0_report.md"

    ensure(v20_module.exists(), "v20.0 module missing")
    ensure(v20_audit.exists(), "v20.0 preflight audit missing")
    ensure(v20_report.exists(), "v20.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"20\.0\.0"', "Runtime version not 20.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"20\.0\.0"', "Release lock not 20.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"20\.0\.0"', "Adapter version not 20.0.0")

    # Future files
    
    # Fast future file check (non-recursive to avoid huge node_modules scan)
    future_patterns = ["*v20_1*", "*v20.1*", "*v21*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")
    

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v20_0\.py",', "v20.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v20_0\.py",', "v20.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v20_0\.py":\s+return "20\.0\.0"', "v20.0 selector missing in runtime")

    # Read v20 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v20_operational_agent_army_mode as v20

    # Check constants
    ensure(v20.STATION_CHIEF_V20_OPERATIONAL_AGENT_ARMY_MODE_VERSION == "20.0.0", "Module constant version mismatch")
    ensure(v20.STATION_CHIEF_V20_APPROVAL_PHRASE == "I_APPROVE_V20_OPERATIONAL_AGENT_ARMY_WORKPACK", "Approval phrase mismatch")

    # Clean stale sandbox artifact before test
    sandbox_artifact = Path(v20.STATION_CHIEF_V20_CONTROLLED_SANDBOX_ARTIFACT)
    if sandbox_artifact.exists():
        sandbox_artifact.unlink()

    # Test preview-only path
    bundle_preview = v20.create_station_chief_v20_operational_agent_army_mode_bundle(execute_operational_workpack_flag=False)
    ensure(bundle_preview["operational_agent_army_status"] == "OPERATIONAL_AGENT_ARMY_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["operational_workpack_performed"] == False, "Workpack performed in preview")
    ensure(not sandbox_artifact.exists(), "Sandbox artifact created in preview")

    # Test approved execution path
    bundle_approved = v20.create_station_chief_v20_operational_agent_army_mode_bundle(
        approval_phrase="I_APPROVE_V20_OPERATIONAL_AGENT_ARMY_WORKPACK",
        execute_operational_workpack_flag=True
    )
    ensure(bundle_approved["operational_agent_army_status"] == "OPERATIONAL_AGENT_ARMY_WORKPACK_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["operational_workpack_performed"] == True, "Workpack not performed in approved")
    ensure(bundle_approved["completed_action_count"] == 2, "Action count mismatch")
    ensure(bundle_approved["routed_v19_v18_v17_readonly_inspection_performed"] == True, "Inspection not performed")
    ensure(bundle_approved["controlled_sandbox_artifact_write_performed"] == True, "Artifact write not performed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Incorrect file count")
    ensure(bundle_approved["real_worker_process_started"] == False, "Real worker process started in approved path")
    ensure(bundle_approved["background_agent_started"] == False, "Background agent started in approved path")
    
    # Verify sandbox artifact
    ensure(sandbox_artifact.exists(), "Sandbox artifact missing after write")
    artifact_data = json.loads(sandbox_artifact.read_text())
    ensure(artifact_data["version"] == "20.0.0", "Artifact version mismatch")
    ensure(artifact_data["routed_inspection_performed"] == True, "Artifact content mismatch")
    ensure("secrets" not in str(artifact_data).lower(), "Secrets leaked to artifact")

    # Test denied execution path
    bundle_denied = v20.create_station_chief_v20_operational_agent_army_mode_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_operational_workpack_flag=True
    )
    ensure(bundle_denied["operational_agent_army_status"] == "OPERATIONAL_AGENT_ARMY_WORKPACK_DENIED", "Denied status mismatch")
    ensure(bundle_denied["operational_workpack_performed"] == False, "Workpack performed in denied")

    # Boundary matrix
    matrix = v20.create_operational_agent_army_safety_boundary_matrix()
    ensure(matrix["routed_v19_v18_v17_readonly_inspection"] == "ALLOWED", "Inspection not allowed in matrix")
    ensure(matrix["controlled_local_temp_sandbox_artifact_write"] == "ALLOWED", "Write not allowed in matrix")
    ensure(matrix["repo_write"] == "DENIED", "Repo write not denied in matrix")

    # Forbidden patterns
    forbidden_v20 = [
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
    check_forbidden_patterns(v20_module, forbidden_v20)

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v20-approved-operational-workpack', "Missing v20 CLI flag")

    # Doctrine
    check_file_content(v20_report, "Operational Agent Army Mode", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v20.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "19_0", "18_0", "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V20_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
