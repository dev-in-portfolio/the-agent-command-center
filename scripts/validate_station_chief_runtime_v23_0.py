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
    v23_module = runtime_dir / "station_chief_v23_controlled_live_external_tool_gateway.py"
    v23_audit = exports_dir / "station_chief_v23_0_controlled_live_external_tool_gateway_preflight_audit.md"
    v23_report = exports_dir / "station_chief_runtime_v23_0_report.md"

    ensure(v23_module.exists(), "v23.0 module missing")
    ensure(v23_audit.exists(), "v23.0 preflight audit missing")
    ensure(v23_report.exists(), "v23.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"23\.0\.0"', "Runtime version not 23.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"23\.0\.0"', "Release lock not 23.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"23\.0\.0"', "Adapter version not 23.0.0")

    # Fast future file check
    future_patterns = ["*v23_1*", "*v23.1*", "*v24*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v23_0\.py",', "v23.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v23_0\.py",', "v23.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v23_0\.py":\s+return "23\.0\.0"', "v23.0 selector missing in runtime")

    # Read v23 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v23_controlled_live_external_tool_gateway as v23

    # Check constants
    ensure(v23.STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION == "23.0.0", "Module constant version mismatch")
    ensure(v23.STATION_CHIEF_V23_APPROVAL_PHRASE == "I_APPROVE_V23_CONTROLLED_EXTERNAL_WEB_PROBE", "Approval phrase mismatch")

    # Clean stale artifacts before test
    workspace_dir = Path(v23.STATION_CHIEF_V23_CONTROLLED_WORKSPACE_DIR)
    if workspace_dir.exists():
        for f in workspace_dir.glob("*"):
            f.unlink()

    # Test preview-only path
    bundle_preview = v23.create_station_chief_v23_controlled_external_tool_bundle(execute_external_tool_flag=False)
    ensure(bundle_preview["controlled_external_tool_status"] == "CONTROLLED_EXTERNAL_TOOL_GATEWAY_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["external_tool_gateway_workpack_performed"] == False, "Workpack performed in preview")
    
    for key, path_str in v23.STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS.items():
        ensure(not Path(path_str).exists(), f"Artifact {key} created in preview")

    # Test approved execution path
    bundle_approved = v23.create_station_chief_v23_controlled_external_tool_bundle(
        approval_phrase="I_APPROVE_V23_CONTROLLED_EXTERNAL_WEB_PROBE",
        execute_external_tool_flag=True
    )
    
    # We handle potential transient network issues by allowing PROBE_UNAVAILABLE status
    # but workpack_performed is only true if artifacts are verified
    allowed_statuses = ["CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_COMPLETED", "CONTROLLED_EXTERNAL_TOOL_GATEWAY_PROBE_UNAVAILABLE"]
    ensure(bundle_approved["controlled_external_tool_status"] in allowed_statuses, f"Invalid status: {bundle_approved['controlled_external_tool_status']}")
    
    if bundle_approved["controlled_external_tool_status"] == "CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_COMPLETED":
        ensure(bundle_approved["external_tool_gateway_workpack_performed"] == True, "Workpack not performed in approved success")
        ensure(bundle_approved["completed_action_count"] == 6, "Action count mismatch")
        ensure(bundle_approved["controlled_external_web_probe_performed"] == True, "Probe not performed")
        ensure(bundle_approved["external_probe_receipt_artifact_written"] == True, "Receipt not written")
        ensure(bundle_approved["artifact_readback_verified"] == True, "Readback failed")
    else:
        print("Note: External probe unavailable (controlled transient error), skipping artifact content checks.")

    # Test denied execution path
    bundle_denied = v23.create_station_chief_v23_controlled_external_tool_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_external_tool_flag=True
    )
    ensure(bundle_denied["controlled_external_tool_status"] == "CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_DENIED", "Denied status mismatch")
    ensure(bundle_denied["external_tool_gateway_workpack_performed"] == False, "Workpack performed in denied")

    # Boundary matrix
    matrix = v23.create_external_tool_safety_boundary_matrix()
    ensure(matrix["controlled_allowlisted_https_get_probe"] == "ALLOWED", "Probe not allowed in matrix")
    ensure(matrix["arbitrary_web_browsing"] == "DENIED", "Arbitrary browsing not denied in matrix")
    ensure(matrix["repo_write"] == "DENIED", "Repo write not denied in matrix")

    # Forbidden patterns
    forbidden_v23 = [
        "import requests", "from requests", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "import shlex", "system(", "popen", "invoke_tool(",
        "credential_access_performed = True", "credential_vault_access_performed = True", "token_access_performed = True",
        "secret_read_performed = True", "private_key_read_performed = True", "signing_key_read_performed = True",
        "environment_read_performed = True", "real_signature_performed = True", "real_encryption_performed = True",
        "real_decryption_performed = True", "email_sent = True", "calendar_event_created = True", 
        "database_operation_performed = True", "deployment_performed = True", "production_execution_performed = True",
        "rollback_execution_performed = True", "recovery_execution_performed = True", "arbitrary_url_call_performed = True",
        "non_allowlisted_url_call_performed = True", "response_body_printed = True", "response_body_stored = True",
        "response_body_returned = True", "auth_headers_used = True", "cookies_used = True", "request_body_sent = True",
        "run_task", "execute_task", "execute_user",
        "arbitrary_user_task_execution_performed = True", "user_task_execution_performed = True",
        "worker.start", "start_worker", "real_worker_process_started = True", "background_agent_started = True",
        "live_worker_started = True", "daemon_started = True", "background_process_started = True",
        "create_real_queue", "queue_write_performed = True", "enqueue_live", "route_live", "orchestrate_live",
        "autonomous_self_activation_performed = True", "full_external_prod_agent_army_activation_performed = True",
        "glob(", "rglob(", "TO" + "DO", "Not" + "Implemented"
    ]
    check_forbidden_patterns(v23_module, forbidden_v23)
    
    # Specific check for open() that isn't urlopen()
    content = v23_module.read_text()
    ensure(not re.search(r'(?<!url)open\(', content), "Forbidden pattern 'open(' (not urlopen) found")

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v23-approved-external-web-probe', "Missing v23 CLI flag")

    # Doctrine
    check_file_content(v23_report, "Controlled Live External Tool Gateway", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v23.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "22_0", "21_0", "20_0", "19_0", "18_0", "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V23_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
