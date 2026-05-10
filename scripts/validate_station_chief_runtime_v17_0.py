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
    v17_module = runtime_dir / "station_chief_v17_live_activation_protocol.py"
    v17_audit = exports_dir / "station_chief_v17_0_live_activation_protocol_preflight_audit.md"
    v17_report = exports_dir / "station_chief_runtime_v17_0_report.md"

    ensure(v17_module.exists(), "v17.0 module missing")
    ensure(v17_audit.exists(), "v17.0 preflight audit missing")
    ensure(v17_report.exists(), "v17.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"(17\.0\.0|18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0)"', "Runtime version not 17.0.0, 18.0.0, or 19.0.0, or 20.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"(17\.0\.0|18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0)"', "Release lock not 17.0.0, 18.0.0, or 19.0.0, or 20.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"(17\.0\.0|18\.0\.0|19\.0\.0|20\.0\.0|21\.0\.0)"', "Adapter version not 17.0.0, 18.0.0, or 19.0.0, or 20.0.0")

    # Future files
    
    
    
    # Fast future file check (non-recursive to avoid huge node_modules scan)
    future_patterns = ["*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")
    

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v17_0\.py",', "v17.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v17_0\.py",', "v17.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v17_0\.py":\s+return "17\.0\.0"', "v17.0 selector missing in runtime")

    # Read v17 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v17_live_activation_protocol as v17

    # Check constants
    ensure(v17.STATION_CHIEF_V17_LIVE_ACTIVATION_PROTOCOL_VERSION == "17.0.0", "Module constant version mismatch")
    ensure(v17.STATION_CHIEF_V17_APPROVAL_PHRASE == "I_APPROVE_V17_READ_ONLY_REPO_INTEGRITY_INSPECTION", "Approval phrase mismatch")

    # Check schema
    schema = v17.create_live_activation_protocol_schema()
    ensure(schema["protocol_version"] == "17.0.0", "Schema version mismatch")
    ensure(schema["human_approval_required"] == True, "human approval not required in schema")

    # Test preview-only path (no phrase)
    bundle_preview = v17.create_station_chief_v17_live_activation_protocol_bundle(execute_live_readonly_inspection=False)
    ensure(bundle_preview["live_activation_status"] == "HUMAN_GATED_LIVE_ACTION_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["live_action_performed"] == False, "live_action_performed must be False for preview")
    ensure(bundle_preview["inspected_file_count"] == 0, "inspected_file_count must be 0 for preview")

    # Test approved execution path (correct phrase)
    bundle_approved = v17.create_station_chief_v17_live_activation_protocol_bundle(
        approval_phrase="I_APPROVE_V17_READ_ONLY_REPO_INTEGRITY_INSPECTION",
        execute_live_readonly_inspection=True
    )
    ensure(bundle_approved["live_activation_status"] == "HUMAN_GATED_LIVE_READONLY_ACTION_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["live_action_performed"] == True, "live_action_performed must be True for approved")
    ensure(bundle_approved["inspected_file_count"] == 7, "Must have inspected exactly 7 files")
    
    # Check inspected file records
    for record in bundle_approved["controlled_readonly_repo_integrity_inspection"]["inspected_files"]:
        ensure(record["read_performed"] == True, f"Read not performed for {record['relative_path']}")
        ensure("sha256" in record, f"SHA256 missing for {record['relative_path']}")
        ensure(record["content_printed"] == False, "Content must not be printed")
        ensure(record["mutation_performed"] == False, "Mutation must not be performed")

    # Test denied execution path (incorrect phrase)
    bundle_denied = v17.create_station_chief_v17_live_activation_protocol_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_live_readonly_inspection=True
    )
    ensure(bundle_denied["live_activation_status"] == "HUMAN_GATED_LIVE_ACTION_DENIED", "Denied status mismatch")
    ensure(bundle_denied["live_action_performed"] == False, "live_action_performed must be False for denied")
    ensure(bundle_denied["inspected_file_count"] == 0, "inspected_file_count must be 0 for denied")

    # Boundary matrix
    matrix = v17.create_live_activation_safety_boundary_matrix()
    ensure(matrix["controlled_local_repo_readonly_integrity_inspection"] == "ALLOWED", "Real action class not allowed in matrix")
    ensure(matrix["production_execution"] == "DENIED", "production_execution not denied in matrix")

    # Forbidden patterns
    forbidden_v17 = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "open(", "import shlex", "system(", "popen", "invoke_tool(",
        "tool_invoked = True", "external_tool_invocation_performed = True", "api_call_performed = True",
        "network_access_performed = True", "socket_access_performed = True", "dns_resolution_performed = True",
        "credential_access_performed = True", "credential_vault_access_performed = True", "secret_read_performed = True",
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
    check_forbidden_patterns(v17_module, forbidden_v17)

    # Check CLI flags in runtime source
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v17-approved-readonly-repo-inspection', "Missing v17 CLI flag")

    # Doctrine
    check_file_content(v17_report, "Human-Gated Live Activation Protocol", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v17.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V17_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
