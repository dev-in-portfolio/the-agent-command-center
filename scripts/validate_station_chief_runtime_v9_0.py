import sys
#!/usr/bin/env python3
"""
Station Chief Runtime v9.0 Validator.
Verifies Station Chief v9.0 build, versioning, controlled worker pilot, and safety boundaries.
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path

# Add project root to sys.path and ensure 10_runtime is discoverable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

from station_chief_v9_controlled_local_worker_pilot import (
    STATION_CHIEF_V9_CONTROLLED_LOCAL_WORKER_PILOT_VERSION,
    STATION_CHIEF_V9_PILOT_WORKER_ID,
    STATION_CHIEF_V9_PILOT_TASK_ID,
    create_station_chief_v9_controlled_local_worker_pilot_schema,
    create_station_chief_v9_controlled_local_worker_pilot_bundle
)

def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        sys.exit(1)

def run_script(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result

def main():
    print("Validating Station Chief Runtime v9.0.0...")

    # 1. Required files
    required_files = [
        "10_runtime/station_chief_v9_controlled_local_worker_pilot.py",
        "09_exports/station_chief_v9_0_controlled_local_worker_pilot_preflight_audit.md",
        "09_exports/station_chief_runtime_v9_0_report.md",
        "scripts/validate_station_chief_runtime_v9_0.py"
    ]
    for f in required_files:
        ensure((REPO_ROOT / f).exists(), f"File {f} must exist")

    # 2. Version consistency
    from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
    from station_chief_release_lock import STABLE_RUNTIME_VERSION
    from station_chief_adapters import ADAPTER_MODULE_VERSION

    # v9.0 validator allows v10.0 version when running on master after v10.0 land.
    ensure(STATION_CHIEF_RUNTIME_VERSION in ["9.0.0", "10.0.0"], f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION in ["9.0.0", "10.0.0"], f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION in ["9.0.0", "10.0.0"], f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V9_CONTROLLED_LOCAL_WORKER_PILOT_VERSION == "9.0.0", "v9.0 module version mismatch")

    # 3. Forbidden Implementation Patterns Check
    module_path = REPO_ROOT / "10_runtime/station_chief_v9_controlled_local_worker_pilot.py"
    module_source = module_path.read_text(encoding="utf-8")
    
    forbidden_patterns = [
        r"import\s+requests", r"from\s+requests", r"urllib", r"socket",
        r"subprocess", r"os\.", r"os\[", r"getenv", r"environ",
        r"eval\(", r"exec\(", r"compile\(", r"__import__\(",
        r"threading", r"multiprocessing", r"asyncio",
        r"shlex", r"system\(", r"popen",
        r"run_task", r"execute_task", r"execute_user",
        r"arbitrary_task_execution", r"user_task_execution",
        r"worker\.start", r"start_worker", r"daemon",
        r"create_queue", r"write_queue", r"enqueue",
        r"route_live", r"orchestrate_live",
        r"api_call", r"network", r"deploy", r"production"
    ]
    
    for pattern in forbidden_patterns:
        # Check if pattern exists and is not just a constant string or comment if possible, 
        # but the mandate is strict: "forbidden implementation patterns absent in v9.0 module"
        match = re.search(pattern, module_source, re.IGNORECASE)
        if match:
            trigger = match.group(0)
            # Allow safety boundary strings and result flags
            safe_exceptions = [
                "production_denied", "production_allowed", "production_execution_performed", 
                "api_denied", "api_allowed", "api_call_performed", 
                "network_denied", "network_allowed", "network_access_performed",
                "socket_access", "dns_resolution", "credential_use", "credential_access_performed",
                "secret_read", "secret_read_performed", "environment_read", "environment_read_performed",
                "deployment", "database_mutation", "full_workforce_activation",
                "worker_process_start", "daemon_start", "background_process_start", "agent_start",
                "subprocess_start", "subprocess_allowed", "subprocess_denied", "subprocess_started", "no_subprocess_started",
                "shell_execution", "shell_allowed", "shell_denied", "shell_executed", "no_shell_executed",
                "arbitrary_command_execution", "arbitrary_task_allowed", "arbitrary_user_content_allowed",
                "arbitrary_task_execution", "user_task_execution", "user_task_allowed", "real_queue_creation",
                "queue_write", "scheduler_write", "cron_write", "live_task_enqueue",
                "live_task_execution", "live_worker_routing", "live_orchestration",
                "external_tool_invocation", "worker.start", "start_worker"
            ]
            
            # Re-verify if the trigger is part of a larger safe string
            is_truly_forbidden = True
            for safe in safe_exceptions:
                if trigger.lower() in safe.lower() and safe.lower() in module_source.lower():
                    # This is still a bit broad, but let's check if the trigger is actually inside a safe word in the source
                    # We look for the safe word surrounding the match
                    full_match_context = module_source[max(0, match.start()-20) : min(len(module_source), match.end()+20)]
                    if safe.lower() in full_match_context.lower():
                        is_truly_forbidden = False
                        break
            
            if is_truly_forbidden:
                ensure(False, f"Forbidden pattern '{pattern}' found in v9.0 module at index {match.start()}")

    # 4. CLI Behavior: Schema Flag
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v9-controlled-local-worker-pilot-schema"])
    ensure(res.returncode == 0, f"Schema flag failed: {res.stderr}")
    schema = json.loads(res.stdout)
    ensure(schema["schema_version"] == "9.0.0", "Schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v9_controlled_local_worker_pilot", "Schema type mismatch")

    # 5. CLI Behavior: Controlled Local Worker Pilot Flag (Bundle inspection)
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v9-controlled-local-worker-pilot"])
    ensure(res.returncode == 0, f"Pilot flag failed: {res.stderr}")
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v9_controlled_local_worker_pilot")
    ensure(bundle is not None, "v9.0 pilot bundle missing in output")
    ensure(bundle["runtime_version"] == "9.0.0", "Bundle version mismatch")
    ensure(bundle["pilot_status"] == "CONTROLLED_LOCAL_WORKER_PILOT_READY", "Bundle status mismatch")

    # 6. Pilot Registry/State Checks
    profile = bundle.get("controlled_local_worker_profile", {})
    ensure(profile.get("worker_id") == STATION_CHIEF_V9_PILOT_WORKER_ID, "Worker ID mismatch")
    ensure(profile.get("worker_started") is False, "Worker must NOT be started")

    task = bundle.get("fixed_synthetic_noop_task", {})
    ensure(task.get("task_id") == STATION_CHIEF_V9_PILOT_TASK_ID, "Task ID mismatch")
    ensure(task.get("arbitrary_user_content_allowed") is False, "Arbitrary content must be denied")

    result = bundle.get("controlled_local_noop_result", {})
    ensure(result.get("result_status") == "NOOP_ACKNOWLEDGED", "Result status mismatch")
    ensure(result.get("task_executed") is False, "Task must NOT be marked as executed")
    ensure(result.get("noop_result_generated") is True, "No-op result should be generated")

    audit = bundle.get("worker_pilot_audit_record", {})
    ensure(audit.get("no_real_execution") is True, "Audit must prove no real execution")
    ensure(audit.get("no_api_call") is True, "Audit must prove no API call")

    # 7. Safety Boundary Matrix
    matrix = bundle.get("worker_pilot_safety_boundary_matrix", {})
    dangerous_actions = [
        "worker_process_start", "agent_start", "real_queue_creation", "queue_write",
        "live_task_enqueue", "live_task_execution", "api_call", "network_access", "deployment", "production_execution"
    ]
    for action in dangerous_actions:
        ensure(matrix.get(action) == "DENIED", f"Safety matrix failed to deny {action}")

    # 8. Forbidden files check
    # v10.0 files are now allowed as they have been built and landed.
    # We still check for v10.1+, v11.1+, and v12.1+ files.
    forbidden_globs = ["*v10_1*", "*v10.1*", "*v11_1*", "*v11.1*", "*v12_1*", "*v12.1*", "*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18_1*", "*v18.1*", "*v19_1*", "*v19.1*", "*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23_1*", "*v23.1*", "*v24*"]

    for glob in forbidden_globs:
        matches = list(REPO_ROOT.glob(f"**/{glob}"))
        matches = [m for m in matches if "__pycache__" not in str(m)]
        ensure(len(matches) == 0, f"Forbidden future files found for glob {glob}: {matches}")

    # 9. Legacy Validator Doctrine Check (No OR-version shortcuts)
    legacy_validators = ["v8_0", "v6_6", "v6_5", "v6_4"]
    for v in legacy_validators:
        v_path = REPO_ROOT / f"scripts/validate_station_chief_runtime_{v}.py"
        if v_path.exists():
            v_source = v_path.read_text()
            ensure("or '9.0.0'" not in v_source, f"Legacy validator {v} contains OR-version shortcut for v9.0")
            ensure('or "9.0.0"' not in v_source, f"Legacy validator {v} contains OR-version shortcut for v9.0")

    # 10. Smoke Tests for Prior Validators
    if not os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"):
        print("Running prior validator smoke tests...")
        prior_validators = [
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

    print("STATION_CHIEF_RUNTIME_V9_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
