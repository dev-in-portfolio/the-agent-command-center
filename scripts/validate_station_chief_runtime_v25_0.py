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

def run_script(script_path):
    result = subprocess.run(["python3", script_path], capture_output=True, text=True, env=os.environ.copy())
    if result.returncode != 0:
        print(f"FAIL: {script_path} failed with output:\n{result.stdout}\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    print("Starting Station Chief Runtime v25.0.0 Validation...")

    root_dir = Path(__file__).parent.parent
    runtime_dir = root_dir / "10_runtime"
    scripts_dir = root_dir / "scripts"
    exports_dir = root_dir / "09_exports"
    
    # 1. Basic File Presence
    v25_module = runtime_dir / "station_chief_v25_general_operator_runtime.py"
    ensure((runtime_dir / "station_chief_runtime.py").exists(), "station_chief_runtime.py missing")
    ensure(v25_module.exists(), "v25.0 module missing")
    ensure((runtime_dir / "station_chief_adapters.py").exists(), "adapters.py missing")
    ensure((runtime_dir / "station_chief_release_lock.py").exists(), "release_lock.py missing")
    ensure((exports_dir / "station_chief_runtime_v25_0_report.md").exists(), "v25.0 report missing")
    ensure((exports_dir / "station_chief_v25_0_done_done_release_lock.md").exists(), "done-done release lock missing")
    ensure((exports_dir / "station_chief_v25_0_operator_command_menu.md").exists(), "operator command menu missing")
    ensure((exports_dir / "station_chief_v25_0_final_acceptance_report.md").exists(), "final acceptance report missing")

    # 2. Version Verification
    sys.path.insert(0, str(runtime_dir))
    import station_chief_runtime as scr
    import station_chief_adapters as sca
    import station_chief_release_lock as scrl
    import station_chief_v25_general_operator_runtime as v25

    print(f"Detected Runtime Version: {scr.STATION_CHIEF_RUNTIME_VERSION}")
    ensure(scr.STATION_CHIEF_RUNTIME_VERSION == "25.0.0", "Runtime version mismatch")
    ensure(sca.ADAPTER_MODULE_VERSION == "25.0.0", "Adapter version mismatch")
    ensure(scrl.STABLE_RUNTIME_VERSION == "25.0.0", "Release lock version mismatch")
    ensure(scrl.FINAL_DONE_DONE_RELEASE_VERSION == "25.0.0", "Final release version mismatch")
    ensure(scrl.NEXT_CORE_VERSION_REQUIRED is False, "Next core version should be false")

    # 3. Schema Verification
    schema = v25.create_station_chief_v25_general_operator_schema()
    ensure(schema["schema_version"] == "25.0.0", "Schema version mismatch")
    ensure(schema["core_command_center_operationally_complete"] is True, "Core not complete in schema")
    ensure(schema["next_core_version_required"] is False, "Next core version required in schema")

    # 4. Capability and Task Registry Verification
    registry = v25.create_installed_capability_registry()
    ensure(registry["installed_capability_count"] == 8, "Registry capability count mismatch")
    ensure(registry["executable_capability_count"] == 6, "Executable capability count mismatch")
    
    tt_registry = v25.create_supported_operator_task_type_registry()
    ensure(tt_registry["task_type_count"] == 8, "Task type count mismatch")
    ensure(tt_registry["supported_executable_task_type_count"] == 6, "Executable task count mismatch")

    # 5. Task Classification Verification
    test_cases = [
        ("Perform a repo integrity check", "repo_integrity_inspection"),
        ("Generate a project brief", "business_workflow_packet"),
        ("What can you do?", "capability_status_report"),
        ("External tool probe", "external_tool_gateway_probe"),
        ("Evidence snapshot", "external_evidence_snapshot"),
        ("Unsafe task delete everything", "unsupported_or_unsafe_task")
    ]
    for task_text, expected_type in test_cases:
        req = v25.create_general_operator_task_request(operator_task=task_text)
        classification = v25.classify_operator_task(req, tt_registry)
        ensure(classification["classified_task_type"] == expected_type, f"Classification failed for: {task_text}")

    # 6. Test Denied Path (No approval)
    bundle_denied = v25.create_station_chief_v25_general_operator_bundle(
        approval_phrase="WRONG_PHRASE",
        operator_task="Run operational workpack",
        execute_operator_task_flag=True
    )
    ensure(bundle_denied["general_operator_runtime_status"] == "GENERAL_OPERATOR_TASK_DENIED", "Wrong status for denied approval")
    ensure(bundle_denied["general_operator_task_performed"] is False, "Task should not be performed without approval")

    # 7. Test Approved Capability Status Report (Status only)
    print("Testing capability status report path...")
    bundle_status = v25.create_station_chief_v25_general_operator_bundle(
        operator_task="What are your capabilities?",
        execute_operator_task_flag=True
    )
    ensure(bundle_status["general_operator_runtime_status"] == "CAPABILITY_STATUS_REPORT_COMPLETED", "Wrong status for status report")
    ensure(bundle_status["general_operator_task_performed"] is True, "Status report should be performed")
    ensure(bundle_status["dispatch_performed"] is False, "Dispatch should not occur for status report")

    # 8. Test Approved Routed Dispatch (Repo Integrity)
    print("Testing approved routed dispatch (repo integrity)...")
    bundle_approved = v25.create_station_chief_v25_general_operator_bundle(
        approval_phrase="I_APPROVE_V25_OPEN_GATE_GENERAL_OPERATOR_RUNTIME",
        operator_task="Perform repo check",
        execute_operator_task_flag=True,
        operator_label="validator-bot"
    )
    ensure(bundle_approved["general_operator_runtime_status"] == "GENERAL_OPERATOR_TASK_COMPLETED", "Dispatch failed")
    ensure(bundle_approved["dispatch_performed"] is True, "Dispatch not performed")
    ensure(bundle_approved["prior_workpack_called"] is True, "Prior workpack not called")
    ensure(bundle_approved["classified_task_type"] == "repo_integrity_inspection", "Wrong task type")
    
    # Check artifacts
    ensure(bundle_approved["controlled_v25_artifact_count"] == 5, "Artifact count mismatch")
    ensure(bundle_approved["artifact_readback_verified"] is True, "Artifact readback failed")
    
    for key, path in bundle_approved["artifact_paths"].items():
        p = Path(path)
        ensure(p.exists(), f"Artifact missing: {path}")
        ensure("agent-command-center" not in path, f"Artifact in repo: {path}")

    # 9. Forbidden Patterns in v25 Module
    content_v25 = v25_module.read_text()
    forbidden_v25_regex = [
        r'import\s+requests',
        r'urllib',
        r'import\s+socket',
        r'import\s+subprocess',
        r'(?<!\w)os\.environ',
        r'environ\[',
        r'eval\(',
        r'exec\(',
        r'compile\(',
        r'__import__\(',
        r'threading',
        r'multiprocessing',
        r'asyncio',
        r'shlex',
        r'system\(',
        r'popen',
        r'invoke_tool\(',
        r'(?<!no_)credential_access_performed":\s*True',
        r'(?<!no_)token_access_performed":\s*True',
        r'(?<!no_)secret_read_performed":\s*True',
        r'(?<!no_)production_execution_performed":\s*True',
        r'(?<!no_)deployment_performed":\s*True',
        r'(?<!no_)repo_mutation_performed":\s*True',
        r'(?<!no_)response_body_printed":\s*True',
        r'(?<!no_)response_body_returned":\s*True',
        r'worker\.start',
        r'start_worker',
        r'live_worker_started":\s*True',
        r'create_real_queue',
        r'glob\(',
        r'rglob\('
    ]
    for pattern in forbidden_v25_regex:
        ensure(not re.search(pattern, content_v25), f"Forbidden pattern '{pattern}' found in {v25_module}")

    # 10. Future File Check
    future_patterns = ["*v25_1*", "*v25.1*", "*v26*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list(runtime_dir.glob(p)))
        found_future.extend(list(scripts_dir.glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")

    # 11. Doctrine Checks
    check_file_content(exports_dir / "station_chief_runtime_v25_0_report.md", "Core command center operationally complete", "Report missing doctrine")
    check_file_content(runtime_dir / "station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v25.0.0", "Readme missing doctrine")
    check_file_content(exports_dir / "station_chief_v25_0_done_done_release_lock.md", "CORE_COMMAND_CENTER_OPERATIONALLY_COMPLETE", "Release lock missing doctrine")

    # 12. Context Selector Checks
    for path in [runtime_dir / "station_chief_runtime.py", runtime_dir / "station_chief_adapters.py", runtime_dir / "station_chief_release_lock.py"]:
        check_file_content(path, r'"validate_station_chief_runtime_v25_0\.py",', f"v25.0 selector missing in {path.name}")

    # 13. Prior Version Preservation
    print("Verifying preservation of v24.0 through v8.0...")
    # Run v24 validator as a representative check
    os.environ["STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"] = "1"
    v24_script = scripts_dir / "validate_station_chief_runtime_v24_0.py"
    if v24_script.exists():
        out = run_script(str(v24_script))
        ensure("STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS" in out, "v24.0 validator failed to pass in v25 context")

    print("STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
