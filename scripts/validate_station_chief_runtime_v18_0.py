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
    v18_module = runtime_dir / "station_chief_v18_universal_tool_permission_layer.py"
    v18_audit = exports_dir / "station_chief_v18_0_universal_tool_permission_layer_preflight_audit.md"
    v18_report = exports_dir / "station_chief_runtime_v18_0_report.md"

    ensure(v18_module.exists(), "v18.0 module missing")
    ensure(v18_audit.exists(), "v18.0 preflight audit missing")
    ensure(v18_report.exists(), "v18.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"(18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0)"', "Runtime version not 18.0.0 or 19.0.0, or 20.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"(18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0)"', "Release lock not 18.0.0 or 19.0.0, or 20.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"(18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0)"', "Adapter version not 18.0.0 or 19.0.0, or 20.0.0")

    # Future files
    
    # Fast future file check (non-recursive to avoid huge node_modules scan)
    future_patterns = ["*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")
    

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v18_0\.py",', "v18.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v18_0\.py",', "v18.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v18_0\.py":\s+return "18\.0\.0"', "v18.0 selector missing in runtime")

    # Read v18 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v18_universal_tool_permission_layer as v18

    # Check constants
    ensure(v18.STATION_CHIEF_V18_UNIVERSAL_TOOL_PERMISSION_LAYER_VERSION == "18.0.0", "Module constant version mismatch")
    ensure(v18.STATION_CHIEF_V18_APPROVAL_PHRASE == "I_APPROVE_V18_CONTROLLED_TOOL_ADAPTER_EXECUTION", "Approval phrase mismatch")

    # Check categories
    cat_reg = v18.create_universal_tool_category_registry()
    ensure(len(cat_reg) == 13, "Must have exactly 13 tool categories")
    
    # Check adapters
    adapter_reg = v18.create_controlled_tool_adapter_registry(cat_reg)
    ensure(len(adapter_reg) == 13, "Must have exactly 13 tool adapters")
    
    executable_adapters = [a_id for a_id, a in adapter_reg.items() if a.get("executable_in_v18")]
    ensure(len(executable_adapters) == 1, f"Must have exactly 1 executable adapter, found {len(executable_adapters)}")
    ensure(executable_adapters[0] == v18.STATION_CHIEF_V18_ALLOWED_LIVE_ADAPTER_ID, "Incorrect live adapter ID")

    # Test preview-only path
    bundle_preview = v18.create_station_chief_v18_universal_tool_permission_layer_bundle(execute_controlled_adapter=False)
    ensure(bundle_preview["universal_tool_permission_status"] == "UNIVERSAL_TOOL_LAYER_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["live_tool_adapter_execution_performed"] == False, "Execution performed in preview")

    # Test approved execution path
    bundle_approved = v18.create_station_chief_v18_universal_tool_permission_layer_bundle(
        approval_phrase="I_APPROVE_V18_CONTROLLED_TOOL_ADAPTER_EXECUTION",
        execute_controlled_adapter=True
    )
    ensure(bundle_approved["universal_tool_permission_status"] == "CONTROLLED_TOOL_ADAPTER_EXECUTION_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["live_tool_adapter_execution_performed"] == True, "Execution not performed in approved")
    ensure(bundle_approved["wrapped_v17_readonly_inspection_performed"] == True, "v17 logic not performed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Incorrect file count in v18 receipt")

    # Test denied execution path
    bundle_denied = v18.create_station_chief_v18_universal_tool_permission_layer_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_controlled_adapter=True
    )
    ensure(bundle_denied["universal_tool_permission_status"] == "CONTROLLED_TOOL_ADAPTER_EXECUTION_DENIED", "Denied status mismatch")
    ensure(bundle_denied["live_tool_adapter_execution_performed"] == False, "Execution performed in denied")

    # Boundary matrix
    matrix = v18.create_universal_tool_safety_boundary_matrix()
    ensure(matrix["controlled_repo_readonly_integrity_adapter_execution"] == "ALLOWED", "Live adapter not allowed in matrix")
    ensure(matrix["live_email_execution"] == "DENIED", "Email execution not denied in matrix")

    # Forbidden patterns
    forbidden_v18 = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "open(", "import shlex", "system(", "popen", "invoke_tool(",
        "tool_invoked = True", "external_tool_invocation_performed = True", "api_call_performed = True",
        "network_access_performed = True", "socket_access_performed = True", "dns_resolution_performed = True",
        "credential_access_performed = True", "credential_vault_access_performed = True", "token_access_performed = True",
        "secret_read_performed = True", "private_key_read_performed = True", "signing_key_read_performed = True",
        "environment_read_performed = True", "run_task", "execute_task", "execute_user",
        "arbitrary_user_task_execution_performed = True", "user_task_execution_performed = True",
        "worker.start", "start_worker", "real_worker_activation_performed = True", "daemon_started = True",
        "background_process_started = True", "create_real_queue", "queue_write_performed = True",
        "enqueue_live", "route_live", "orchestrate_live", "deployment_performed = True",
        "production_execution_performed = True", "rollback_execution_performed = True", "recovery_execution_performed = True",
        "autonomous_self_activation_performed = True", "full_external_prod_agent_army_activation_performed = True",
        "write_text(", "write_bytes(", "unlink(", "rename(", "replace(", "mkdir(", "rmdir(", "glob(", "rglob(",
        "TO" + "DO", "Not" + "Implemented"
    ]
    check_forbidden_patterns(v18_module, forbidden_v18)

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v18-approved-tool-adapter-execution', "Missing v18 CLI flag")

    # Doctrine
    check_file_content(v18_report, "Universal Tool Permission Layer", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v18.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V18_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
