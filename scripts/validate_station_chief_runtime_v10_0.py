import sys
#!/usr/bin/env python3
"""
Station Chief Runtime v10.0 Validator.
Verifies Station Chief v10.0 build, multi-worker sandbox coordination, and safety boundaries.
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

from station_chief_v10_multi_worker_sandbox_coordination import (
    STATION_CHIEF_V10_MULTI_WORKER_SANDBOX_COORDINATION_VERSION,
    STATION_CHIEF_V10_SANDBOX_WORKER_IDS,
    STATION_CHIEF_V10_SANDBOX_TASK_IDS,
    create_station_chief_v10_multi_worker_sandbox_coordination_schema,
    create_station_chief_v10_multi_worker_sandbox_coordination_bundle
)

def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        sys.exit(1)

def run_script(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result

def main():
    print("Validating Station Chief Runtime v10.0.0...")

    # 1. Required files
    required_files = [
        "10_runtime/station_chief_v10_multi_worker_sandbox_coordination.py",
        "09_exports/station_chief_v10_0_multi_worker_sandbox_coordination_preflight_audit.md",
        "09_exports/station_chief_runtime_v10_0_report.md",
        "scripts/validate_station_chief_runtime_v10_0.py"
    ]
    for f in required_files:
        ensure((REPO_ROOT / f).exists(), f"File {f} must exist")

    # 2. Version consistency
    from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
    from station_chief_release_lock import STABLE_RUNTIME_VERSION
    from station_chief_adapters import ADAPTER_MODULE_VERSION
    ensure(STATION_CHIEF_RUNTIME_VERSION == "10.0.0", f"Runtime version must be 10.0.0, got {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION == "10.0.0", f"Release lock version must be 10.0.0, got {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION == "10.0.0", f"Adapter version must be 10.0.0, got {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V10_MULTI_WORKER_SANDBOX_COORDINATION_VERSION == "10.0.0", "v10.0 module version mismatch")

    # 3. Forbidden Implementation Patterns Check
    module_path = REPO_ROOT / "10_runtime/station_chief_v10_multi_worker_sandbox_coordination.py"
    module_source = module_path.read_text(encoding="utf-8")
    
    forbidden_patterns = [
        r"import\s+requests", r"from\s+requests", r"urllib", r"socket",
        r"subprocess", r"os\.", r"os\[", r"getenv", r"environ",
        r"eval\(", r"exec\(", r"compile\(", r"__import__\(",
        r"threading", r"multiprocessing", r"asyncio",
        r"shlex", r"system\(", r"popen",
        r"run_task", r"execute_task", r"execute_user",
        r"arbitrary_user_task_execution_performed\s*=\s*True",
        r"user_task_execution_performed\s*=\s*True",
        r"worker\.start", r"start_worker",
        r"daemon_started\s*=\s*True",
        r"background_process_started\s*=\s*True",
        r"create_queue", r"write_queue", r"enqueue_live",
        r"route_live", r"orchestrate_live",
        r"api_call_performed\s*=\s*True",
        r"network_access_performed\s*=\s*True",
        r"deploy",
        r"production_execution_performed\s*=\s*True"
    ]
    
    for pattern in forbidden_patterns:
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
                "external_tool_invocation", "worker.start", "start_worker", "real_queue_authorized",
                "live_routing_authorized", "live_orchestration_authorized"
            ]
            
            # Re-verify if the trigger is part of a larger safe string
            is_truly_forbidden = True
            for safe in safe_exceptions:
                if trigger.lower() in safe.lower() and safe.lower() in module_source.lower():
                    # Look for the safe word surrounding the match
                    full_match_context = module_source[max(0, match.start()-20) : min(len(module_source), match.end()+20)]
                    if safe.lower() in full_match_context.lower():
                        is_truly_forbidden = False
                        break
            
            if is_truly_forbidden:
                ensure(False, f"Forbidden pattern '{pattern}' found in v10.0 module at index {match.start()}")

    # 4. CLI Behavior: Schema Flag
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v10-multi-worker-sandbox-coordination-schema"])
    ensure(res.returncode == 0, f"Schema flag failed: {res.stderr}")
    schema = json.loads(res.stdout)
    ensure(schema["schema_version"] == "10.0.0", "Schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v10_multi_worker_sandbox_coordination", "Schema type mismatch")

    # 5. CLI Behavior: Multi-Worker Sandbox Coordination Flag (Bundle inspection)
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v10-multi-worker-sandbox-coordination"])
    ensure(res.returncode == 0, f"Coordination flag failed: {res.stderr}")
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v10_multi_worker_sandbox_coordination")
    ensure(bundle is not None, "v10.0 coordination bundle missing in output")
    ensure(bundle["runtime_version"] == "10.0.0", "Bundle version mismatch")
    ensure(bundle["coordination_status"] == "MULTI_WORKER_SANDBOX_COORDINATION_READY", "Bundle status mismatch")

    # 6. Coordination State Checks
    workers = bundle.get("sandbox_worker_profiles", {})
    ensure(len(workers) == 3, f"Expected exactly 3 worker profiles, got {len(workers)}")
    for wid in STATION_CHIEF_V10_SANDBOX_WORKER_IDS:
        ensure(wid in workers, f"Worker {wid} missing in profiles")
        ensure(workers[wid]["worker_started"] is False, f"Worker {wid} must NOT be started")

    tasks = bundle.get("fixed_synthetic_sandbox_tasks", {})
    ensure(len(tasks) == 3, f"Expected exactly 3 sandbox tasks, got {len(tasks)}")
    for tid in STATION_CHIEF_V10_SANDBOX_TASK_IDS:
        ensure(tid in tasks, f"Task {tid} missing in tasks")
        ensure(tasks[tid]["arbitrary_user_content_allowed"] is False, f"Task {tid} must deny user content")

    assignments = bundle.get("deterministic_worker_assignment_map", {}).get("assignments", {})
    ensure(len(assignments) == 3, "Expected exactly 3 assignments")
    for i in range(3):
        wid = STATION_CHIEF_V10_SANDBOX_WORKER_IDS[i]
        tid = STATION_CHIEF_V10_SANDBOX_TASK_IDS[i]
        ensure(assignments.get(wid) == tid, f"Assignment mismatch for {wid}")

    results = bundle.get("sandbox_noop_results", {})
    ensure(len(results) == 3, "Expected exactly 3 no-op results")
    for rid, r in results.items():
        ensure(r["result_status"] == "NOOP_ACKNOWLEDGED", f"Result {rid} status mismatch")
        ensure(r["task_executed"] is False, f"Result {rid} must NOT be marked as executed")

    ledger = bundle.get("multi_worker_coordination_ledger", {})
    ensure(ledger["result_count"] == 3, "Ledger result count mismatch")
    ensure(ledger["no_live_orchestration"] is True, "Ledger must prove no live orchestration")

    audit = bundle.get("multi_worker_sandbox_audit_record", {})
    ensure(audit["all_results_noop_acknowledged"] is True, "Audit failed to acknowledge all results")
    ensure(audit["no_real_execution"] is True, "Audit must prove no real execution")

    # 7. Safety Boundary Matrix
    matrix = bundle.get("multi_worker_sandbox_safety_boundary_matrix", {})
    dangerous_actions = [
        "worker_process_start", "agent_start", "real_queue_creation", "queue_write",
        "live_task_enqueue", "live_task_execution", "live_worker_routing", "live_orchestration",
        "api_call", "network_access", "deployment", "production_execution"
    ]
    for action in dangerous_actions:
        ensure(matrix.get(action) == "DENIED", f"Safety matrix failed to deny {action}")

    # 8. Forbidden files check
    forbidden_globs = ["*v10_1*", "*v10.1*", "*v11_1*", "*v11.1*", "*v12_1*", "*v12.1*", "*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18_1*", "*v18.1*", "*v19_1*", "*v19.1*", "*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23_1*", "*v23.1*",  "*v24_1*", "*v24.1*",  "*v25_1*", "*v25.1*", "*v26*"]
    for glob in forbidden_globs:
        matches = list(REPO_ROOT.glob(f"**/{glob}"))
        matches = [m for m in matches if "__pycache__" not in str(m)]
        ensure(len(matches) == 0, f"Forbidden future files found for glob {glob}: {matches}")

    # 9. Legacy Validator Doctrine Check (No OR-version shortcuts)
    legacy_validators = ["v9_0", "v8_0", "v6_6", "v6_5", "v6_4"]
    for v in legacy_validators:
        v_path = REPO_ROOT / f"scripts/validate_station_chief_runtime_{v}.py"
        if v_path.exists():
            v_source = v_path.read_text()
            ensure("or '10.0.0'" not in v_source, f"Legacy validator {v} contains OR-version shortcut for v10.0")
            ensure('or "10.0.0"' not in v_source, f"Legacy validator {v} contains OR-version shortcut for v10.0")

    # 10. Smoke Tests for Prior Validators
    if not os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"):
        print("Running prior validator smoke tests...")
        prior_validators = [
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

    print("STATION_CHIEF_RUNTIME_V10_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
