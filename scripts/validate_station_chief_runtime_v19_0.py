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
    v19_module = runtime_dir / "station_chief_v19_multi_agent_live_work_router.py"
    v19_audit = exports_dir / "station_chief_v19_0_multi_agent_live_work_router_preflight_audit.md"
    v19_report = exports_dir / "station_chief_runtime_v19_0_report.md"

    ensure(v19_module.exists(), "v19.0 module missing")
    ensure(v19_audit.exists(), "v19.0 preflight audit missing")
    ensure(v19_report.exists(), "v19.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"(19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0|23\.0\.0)"', "Runtime version not 19.0.0 or 20.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"(19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0|23\.0\.0)"', "Release lock not 19.0.0 or 20.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"(19\.0\.0|20\.0\.0|21\.0\.0|22\.0\.0|23\.0\.0)"', "Adapter version not 19.0.0 or 20.0.0")

    # Future files
    
    # Fast future file check (non-recursive to avoid huge node_modules scan)
    future_patterns = ["*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23_1*", "*v23.1*", "*v24*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")
    

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v19_0\.py",', "v19.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v19_0\.py",', "v19.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v19_0\.py":\s+return "19\.0\.0"', "v19.0 selector missing in runtime")

    # Read v19 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v19_multi_agent_live_work_router as v19

    # Check constants
    ensure(v19.STATION_CHIEF_V19_MULTI_AGENT_LIVE_WORK_ROUTER_VERSION == "19.0.0", "Module constant version mismatch")
    ensure(v19.STATION_CHIEF_V19_APPROVAL_PHRASE == "I_APPROVE_V19_MULTI_AGENT_LIVE_ROUTED_WORK", "Approval phrase mismatch")

    # Check roles
    squad_registry = v19.create_live_agent_squad_registry()
    ensure(len(squad_registry) == 6, "Must have exactly 6 logical agent roles")
    for role in squad_registry.values():
        ensure(role["live_worker_process_started"] == False, "Real worker process started in logical registry")
        ensure(role["background_agent_started"] == False, "Background agent started in logical registry")

    # Test preview-only path
    bundle_preview = v19.create_station_chief_v19_multi_agent_live_work_router_bundle(execute_routed_work=False)
    ensure(bundle_preview["multi_agent_live_work_status"] == "MULTI_AGENT_LIVE_WORK_ROUTER_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["routed_live_work_performed"] == False, "Routed work performed in preview")

    # Test approved execution path
    bundle_approved = v19.create_station_chief_v19_multi_agent_live_work_router_bundle(
        approval_phrase="I_APPROVE_V19_MULTI_AGENT_LIVE_ROUTED_WORK",
        execute_routed_work=True
    )
    ensure(bundle_approved["multi_agent_live_work_status"] == "SUPERVISED_MULTI_AGENT_ROUTED_WORK_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["routed_live_work_performed"] == True, "Routed work not performed in approved")
    ensure(bundle_approved["wrapped_v18_controlled_adapter_execution_performed"] == True, "v18 logic not performed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Incorrect file count in v19 receipt")
    ensure(bundle_approved["real_worker_process_started"] == False, "Real worker process started in approved path")
    ensure(bundle_approved["background_agent_started"] == False, "Background agent started in approved path")

    # Check handoff ledger
    handoff_ledger = bundle_approved["agent_handoff_receipt_ledger"]
    ensure(handoff_ledger["handoff_receipt_count"] == 6, "Must have exactly 6 handoff receipts")
    for receipt in handoff_ledger["receipts"].values():
        ensure(receipt["live_worker_process_started"] == False, "Real worker started in handoff")
        ensure(receipt["background_agent_started"] == False, "Background agent started in handoff")

    # Test denied execution path
    bundle_denied = v19.create_station_chief_v19_multi_agent_live_work_router_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_routed_work=True
    )
    ensure(bundle_denied["multi_agent_live_work_status"] == "SUPERVISED_MULTI_AGENT_ROUTED_WORK_DENIED", "Denied status mismatch")
    ensure(bundle_denied["routed_live_work_performed"] == False, "Routed work performed in denied")

    # Boundary matrix
    matrix = v19.create_multi_agent_live_work_safety_boundary_matrix()
    ensure(matrix["routed_controlled_v18_adapter_execution"] == "ALLOWED", "Routed v18 adapter not allowed in matrix")
    ensure(matrix["real_worker_process_start"] == "DENIED", "Real worker start not denied in matrix")

    # Forbidden patterns
    forbidden_v19 = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "open(", "import shlex", "system(", "popen", "invoke_tool(",
        "tool_invoked = True", "external_tool_invocation_performed = True", "api_call_performed = True",
        "network_access_performed = True", "socket_access_performed = True", "dns_resolution_performed = True",
        "credential_access_performed = True", "credential_vault_access_performed = True", "token_access_performed = True",
        "secret_read_performed = True", "private_key_read_performed = True", "signing_key_read_performed = True",
        "environment_read_performed = True", "real_signature_performed = True", "real_encryption_performed = True",
        "real_decryption_performed = True", "key_generation_performed = True", "run_task", "execute_task", "execute_user",
        "arbitrary_user_task_execution_performed = True", "user_task_execution_performed = True",
        "worker.start", "start_worker", "real_worker_process_started = True", "background_agent_started = True",
        "live_worker_started = True", "daemon_started = True", "background_process_started = True",
        "create_real_queue", "queue_write_performed = True", "enqueue_live", "route_live", "orchestrate_live",
        "deployment_performed = True", "production_execution_performed = True", "rollback_execution_performed = True",
        "recovery_execution_performed = True", "autonomous_self_activation_performed = True",
        "full_external_prod_agent_army_activation_performed = True",
        "write_text(", "write_bytes(", "unlink(", "rename(", "replace(", "mkdir(", "rmdir(", "glob(", "rglob(",
        "TO" + "DO", "Not" + "Implemented"
    ]
    check_forbidden_patterns(v19_module, forbidden_v19)

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v19-approved-routed-work', "Missing v19 CLI flag")

    # Doctrine
    check_file_content(v19_report, "Multi-Agent Live Work Router", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v19.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "18_0", "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V19_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
