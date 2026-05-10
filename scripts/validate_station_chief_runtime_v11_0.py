#!/usr/bin/env python3
"""
Station Chief Runtime v11.0 Validator.
Verifies Station Chief v11.0 build, permissioned tool/task/queue layer, and safety boundaries.
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(REPO_ROOT / "10_runtime"))

from station_chief_v11_permissioned_tool_task_queue_layer import (
    STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION,
    STATION_CHIEF_V11_SANDBOX_TOOL_IDS,
    STATION_CHIEF_V11_TASK_ENVELOPE_IDS,
    STATION_CHIEF_V11_VIRTUAL_QUEUE_ID,
    create_station_chief_v11_permissioned_tool_task_queue_layer_schema,
    create_station_chief_v11_permissioned_tool_task_queue_layer_bundle
)

def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        sys.exit(1)

def run_script(args):
    return subprocess.run(args, capture_output=True, text=True)

def main():
    print("Validating Station Chief Runtime v11.0.0...")

    # 1. Required Files Exist
    required_files = [
        "09_exports/station_chief_v11_0_permissioned_tool_task_queue_layer_preflight_audit.md",
        "10_runtime/station_chief_v11_permissioned_tool_task_queue_layer.py",
        "09_exports/station_chief_runtime_v11_0_report.md",
        "scripts/validate_station_chief_runtime_v11_0.py",
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_adapters.py",
        "10_runtime/station_chief_release_lock.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        ".github/workflows/station-chief-validation.yml"
    ]
    for f in required_files:
        ensure((REPO_ROOT / f).exists(), f"Required file missing: {f}")

    # 2. Version Consistency
    from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
    from station_chief_release_lock import STABLE_RUNTIME_VERSION
    from station_chief_adapters import ADAPTER_MODULE_VERSION

    ensure(STATION_CHIEF_RUNTIME_VERSION == "11.0.0", f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION == "11.0.0", f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION == "11.0.0", f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V11_PERMISSIONED_TOOL_TASK_QUEUE_LAYER_VERSION == "11.0.0", "v11.0 module version mismatch")

    # 3. v11.0 Module Implementation Integrity
    module_path = REPO_ROOT / "10_runtime/station_chief_v11_permissioned_tool_task_queue_layer.py"
    with open(module_path, "r") as f:
        module_source = f.read()

    forbidden_patterns = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess",
        "os.", "os[", "getenv(", ".environ", "eval(", "exec(", "compile(",
        "__import__(", "import threading", "import multiprocessing", "import asyncio", "open(",
        "shlex", "system(", "popen", "invoke_tool(", "tool_invoked = True",
        "external_tool_invocation_performed = True", "run_task(", "execute_task(",
        "execute_user(", "arbitrary_user_task_execution_performed = True",
        "user_task_execution_performed = True", "worker.start", "start_worker",
        "daemon_started = True", "background_process_started = True",
        "create_real_queue", "queue_write_performed = True", "enqueue_live",
        "route_live", "orchestrate_live", "api_call_performed = True",
        "network_access_performed = True", "deploy(", "production_execution_performed = True"
    ]
    for p in forbidden_patterns:
        ensure(p not in module_source, f"Forbidden implementation pattern '{p}' found in v11.0 module")

    # 4. CLI Flag Integration
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v11-permissioned-tool-task-queue-layer-schema"])
    ensure(res.returncode == 0, "CLI schema flag failed")
    schema = json.loads(res.stdout)
    ensure(schema["schema_version"] == "11.0.0", "CLI schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v11_permissioned_tool_task_queue_layer", "Schema type mismatch")

    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v11-permissioned-tool-task-queue-layer"])
    ensure(res.returncode == 0, "CLI layer flag failed")
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v11_permissioned_tool_task_queue_layer")
    ensure(bundle is not None, "v11.0 bundle missing from CLI output")
    ensure(bundle["runtime_version"] == "11.0.0", "Bundle version mismatch")

    # 5. Permissioned Layer Data Integrity
    tools = bundle["permissioned_sandbox_tool_registry"]
    tasks = bundle["permissioned_task_envelopes"]
    queue = bundle["virtual_queue_manifest"]
    gate = bundle["permission_policy_gate"]
    receipts = bundle["permission_receipts"]
    audit = bundle["permissioned_queue_task_tool_audit_record"]
    matrix = bundle["permissioned_tool_task_queue_safety_boundary_matrix"]

    ensure(len(tools) == 3, f"Expected 3 tools, found {len(tools)}")
    ensure(len(tasks) == 3, f"Expected 3 tasks, found {len(tasks)}")
    ensure(queue["virtual_queue_id"] == STATION_CHIEF_V11_VIRTUAL_QUEUE_ID, "Virtual queue ID mismatch")
    ensure(gate["permission_metadata_authorized"] is True, "Policy gate failed to authorize metadata")
    ensure(gate["real_tool_invocation_authorized"] is False, "Policy gate incorrectly authorized real tools")
    ensure(len(receipts) == 3, f"Expected 3 receipts, found {len(receipts)}")
    
    for rid, r in receipts.items():
        ensure(r["tool_invoked"] is False, f"Receipt {rid} shows tool invoked")
        ensure(r["task_executed"] is False, f"Receipt {rid} shows task executed")
        ensure(r["permission_receipt_generated"] is True, f"Receipt {rid} not generated")

    ensure(audit["no_real_tool_invocation"] is True, "Audit failed: real tool invocation detected")
    ensure(audit["no_live_task_executed"] is True, "Audit failed: live task execution detected")
    ensure(matrix["real_tool_invocation"] == "DENIED", "Safety matrix failed: real tool invocation NOT DENIED")

    # 6. Future File Check
    forbidden_globs = ["*v11_1*", "*v11.1*", "*v12_1*", "*v12.1*", "*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18_1*", "*v18.1*", "*v19_1*", "*v19.1*", "*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23*"]
    for glob in forbidden_globs:
        found = list(REPO_ROOT.rglob(glob))
        found = [f for f in found if "__pycache__" not in str(f) and f.suffix != ".pyc"]
        ensure(len(found) == 0, f"Forbidden future files found for glob {glob}: {found}")

    # 7. Documentation Check
    readme_path = REPO_ROOT / "10_runtime/station_chief_runtime_readme.md"
    with open(readme_path, "r") as f:
        readme_content = f.read()
    ensure("Station Chief Runtime upgraded to v11.0.0" in readme_content, "README not updated")
    ensure("v11.1 or v12.0 requires explicit operator instruction" in readme_content, "README missing next step label")

    # 8. Validation Context Selectors Integrity
    for f_path in ["10_runtime/station_chief_runtime.py", "10_runtime/station_chief_release_lock.py", "10_runtime/station_chief_adapters.py"]:
        with open(REPO_ROOT / f_path, "r") as f:
            src = f.read()
        ensure("validate_station_chief_runtime_v11_0.py" in src, f"v11.0 selector missing in {f_path}")
        ensure("validate_station_chief_runtime_v10_0.py" in src, f"v10.0 selector missing in {f_path}")
        ensure("validate_station_chief_runtime_v9_0.py" in src, f"v9.0 selector missing in {f_path}")

    # 9. Legacy Validator Shortcuts Check
    for v in ["scripts/validate_station_chief_runtime_v10_0.py", "scripts/validate_station_chief_runtime_v9_0.py", "scripts/validate_station_chief_runtime_v8_0.py"]:
        with open(REPO_ROOT / v, "r") as f:
            v_source = f.read()
            ensure("or '11.0.0'" not in v_source, f"Legacy validator {v} contains OR-version shortcut for v11.0")
            ensure('or "11.0.0"' not in v_source, f"Legacy validator {v} contains OR-version shortcut for v11.0")

    # 10. Smoke Tests for Prior Validators
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") == "1":
        print("Skipping recursive prior version smoke tests (env var set)...")
    else:
        print("Running prior validator smoke tests...")
        prior_validators = [
            "scripts/validate_station_chief_runtime_v10_0.py",
            "scripts/validate_station_chief_runtime_v9_0.py",
            "scripts/validate_station_chief_runtime_v8_0.py",
            "scripts/validate_station_chief_runtime_v6_6.py",
            "scripts/validate_station_chief_runtime_v6_5.py",
            "scripts/validate_station_chief_runtime_v6_4.py",
            "scripts/validate_station_chief_runtime_v6_3.py",
            "scripts/validate_station_chief_runtime_v6_2.py",
            "scripts/validate_station_chief_runtime_v6_1.py",
            "scripts/validate_station_chief_runtime_v6_0.py",
            "scripts/validate_station_chief_runtime_v5_9.py",
            "scripts/validate_station_chief_runtime_v5_8.py",
            "scripts/validate_station_chief_runtime_v5_7.py",
            "scripts/validate_station_chief_runtime_v5_6.py",
            "scripts/validate_station_chief_runtime_v5_5.py",
            "scripts/validate_station_chief_runtime_v5_4.py",
            "scripts/validate_station_chief_runtime_v5_3.py",
            "scripts/validate_station_chief_runtime_v5_2.py",
            "scripts/validate_station_chief_runtime_v5_1.py",
            "scripts/validate_station_chief_runtime_v5_0.py"
        ]
        for v in prior_validators:
            print(f"Running {v}...")
            env = os.environ.copy()
            env["STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"] = "1"
            res = subprocess.run([sys.executable, str(REPO_ROOT / v)], capture_output=True, text=True, env=env)
            ensure(res.returncode == 0, f"Prior validator {v} failed:\n{res.stdout}\n{res.stderr}")

    print("STATION_CHIEF_RUNTIME_V11_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
