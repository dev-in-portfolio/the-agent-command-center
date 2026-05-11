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
    v22_module = runtime_dir / "station_chief_v22_controlled_business_workflow_workpack.py"
    v22_audit = exports_dir / "station_chief_v22_0_controlled_business_workflow_workpack_preflight_audit.md"
    v22_report = exports_dir / "station_chief_runtime_v22_0_report.md"

    ensure(v22_module.exists(), "v22.0 module missing")
    ensure(v22_audit.exists(), "v22.0 preflight audit missing")
    ensure(v22_report.exists(), "v22.0 report missing")

    # Versions
    check_file_content(runtime_dir / "station_chief_runtime.py", r'STATION_CHIEF_RUNTIME_VERSION\s*=\s*"(22\.0\.0|23\.0\.0|24\.0\.0|25\.0\.0)"', "Runtime version not 22.0.0 or 23.0.0")
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'STABLE_RUNTIME_VERSION\s*=\s*"(22\.0\.0|23\.0\.0|24\.0\.0|25\.0\.0)"', "Release lock not 22.0.0 or 23.0.0")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'ADAPTER_MODULE_VERSION\s*=\s*"(22\.0\.0|23\.0\.0|24\.0\.0|25\.0\.0)"', "Adapter version not 22.0.0 or 23.0.0")

    # Fast future file check
    future_patterns = ["*v23_1*", "*v23.1*",  "*v24_1*", "*v24.1*",  "*v25_1*", "*v25.1*", "*v26*"]
    found_future = []
    for p in future_patterns:
        found_future.extend(list(root_dir.glob(p)))
        found_future.extend(list((root_dir / "10_runtime").glob(p)))
        found_future.extend(list((root_dir / "scripts").glob(p)))
        found_future.extend(list((root_dir / "09_exports").glob(p)))
    ensure(not found_future, f"Future files exist: {found_future}")

    # Context selectors
    check_file_content(runtime_dir / "station_chief_release_lock.py", r'"validate_station_chief_runtime_v22_0\.py",', "v22.0 selector missing in release lock")
    check_file_content(runtime_dir / "station_chief_adapters.py", r'"validate_station_chief_runtime_v22_0\.py",', "v22.0 selector missing in adapters")
    check_file_content(runtime_dir / "station_chief_runtime.py", r'if context == "validate_station_chief_runtime_v22_0\.py":\s+return "22\.0\.0"', "v22.0 selector missing in runtime")

    # Read v22 module
    sys.path.insert(0, str(runtime_dir))
    import station_chief_v22_controlled_business_workflow_workpack as v22

    # Check constants
    ensure(v22.STATION_CHIEF_V22_CONTROLLED_BUSINESS_WORKFLOW_VERSION == "22.0.0", "Module constant version mismatch")
    ensure(v22.STATION_CHIEF_V22_APPROVAL_PHRASE == "I_APPROVE_V22_CONTROLLED_BUSINESS_WORKFLOW_WORKPACK", "Approval phrase mismatch")

    # Clean stale workspace artifacts before test
    workspace_dir = Path(v22.STATION_CHIEF_V22_CONTROLLED_WORKSPACE_DIR)
    if workspace_dir.exists():
        for f in workspace_dir.glob("*"):
            f.unlink()

    # Test preview-only path
    bundle_preview = v22.create_station_chief_v22_controlled_business_workflow_bundle(execute_business_workflow_flag=False)
    ensure(bundle_preview["controlled_business_workflow_status"] == "CONTROLLED_BUSINESS_WORKFLOW_PREVIEW_ONLY", "Preview status mismatch")
    ensure(bundle_preview["business_workflow_workpack_performed"] == False, "Workpack performed in preview")
    
    for key, path_str in v22.STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS.items():
        ensure(not Path(path_str).exists(), f"Artifact {key} created in preview")

    # Test approved execution path
    bundle_approved = v22.create_station_chief_v22_controlled_business_workflow_bundle(
        approval_phrase="I_APPROVE_V22_CONTROLLED_BUSINESS_WORKFLOW_WORKPACK",
        execute_business_workflow_flag=True,
        client_label="TestClient"
    )
    ensure(bundle_approved["controlled_business_workflow_status"] == "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_COMPLETED", "Approved status mismatch")
    ensure(bundle_approved["business_workflow_workpack_performed"] == True, "Workpack not performed in approved")
    ensure(bundle_approved["completed_action_count"] == 7, "Action count mismatch")
    ensure(bundle_approved["routed_v21_v20_v19_v18_v17_chain_performed"] == True, "Operational chain not performed")
    ensure(bundle_approved["project_brief_artifact_written"] == True, "Brief not written")
    ensure(bundle_approved["execution_plan_artifact_written"] == True, "Plan not written")
    ensure(bundle_approved["tracker_csv_artifact_written"] == True, "Tracker not written")
    ensure(bundle_approved["client_ready_summary_artifact_written"] == True, "Summary not written")
    ensure(bundle_approved["qa_checklist_artifact_written"] == True, "Checklist not written")
    ensure(bundle_approved["business_workflow_manifest_written"] == True, "Manifest not written")
    ensure(bundle_approved["artifact_readback_verified"] == True, "Readback verification failed")
    ensure(bundle_approved["inspected_file_count"] == 7, "Incorrect file count from routed chain")

    # Verify artifacts content
    for key, path_str in v22.STATION_CHIEF_V22_CONTROLLED_ARTIFACT_PATHS.items():
        p = Path(path_str)
        ensure(p.exists(), f"Artifact {key} missing after write")
        content = p.read_text()
        ensure("secrets" not in content.lower(), f"Secrets leaked to {key}")
        ensure("tokens" not in content.lower(), f"Tokens leaked to {key}")
        ensure("credentials" not in content.lower(), f"Credentials leaked to {key}")
        if key == "tracker_csv":
            ensure("item,artifact_key" in content, "CSV header missing")
        if key == "project_brief_md":
            ensure("# Station Chief v22 Business Workflow Project Brief" in content, "Brief title missing")
        if key == "client_ready_summary_md":
            ensure("# Client-Ready Business Workflow Summary" in content, "Summary title missing")

    # Test denied execution path
    bundle_denied = v22.create_station_chief_v22_controlled_business_workflow_bundle(
        approval_phrase="WRONG_PHRASE",
        execute_business_workflow_flag=True
    )
    ensure(bundle_denied["controlled_business_workflow_status"] == "CONTROLLED_BUSINESS_WORKFLOW_WORKPACK_DENIED", "Denied status mismatch")
    ensure(bundle_denied["business_workflow_workpack_performed"] == False, "Workpack performed in denied")

    # Boundary matrix
    matrix = v22.create_business_workflow_safety_boundary_matrix()
    ensure(matrix["controlled_project_brief_markdown"] == "ALLOWED", "Brief not allowed in matrix")
    ensure(matrix["email_send"] == "DENIED", "Email send not denied in matrix")
    ensure(matrix["repo_write"] == "DENIED", "Repo write not denied in matrix")

    # Forbidden patterns
    forbidden_v22 = [
        "import requests", "from requests", "import urllib", "import socket", "import subprocess", "os.", "os[",
        "os.getenv", "os.environ", "eval(", "exec(", "compile(", "__import__(", "import threading", 
        "import multiprocessing", "import asyncio", "open(", "import shlex", "system(", "popen", "invoke_tool(",
        "external_tool_invocation_performed = True", "api_call_performed = True",
        "network_access_performed = True", "socket_access_performed = True", "dns_resolution_performed = True",
        "credential_access_performed = True", "credential_vault_access_performed = True", "token_access_performed = True",
        "secret_read_performed = True", "private_key_read_performed = True", "signing_key_read_performed = True",
        "environment_read_performed = True", "real_signature_performed = True", "real_encryption_performed = True",
        "real_decryption_performed = True", "email_sent = True", "calendar_event_created = True", "web_request_performed = True",
        "run_task", "execute_task", "execute_user",
        "arbitrary_user_task_execution_performed = True", "user_task_execution_performed = True",
        "worker.start", "start_worker", "real_worker_process_started = True", "background_agent_started = True",
        "live_worker_started = True", "daemon_started = True", "background_process_started = True",
        "create_real_queue", "queue_write_performed = True", "enqueue_live", "route_live", "orchestrate_live",
        "deployment_performed = True", "production_execution_performed = True", "rollback_execution_performed = True",
        "recovery_execution_performed = True", "autonomous_self_activation_performed = True",
        "full_external_prod_agent_army_activation_performed = True",
        "glob(", "rglob(", "TO" + "DO", "Not" + "Implemented"
    ]
    check_forbidden_patterns(v22_module, forbidden_v22)

    # Check CLI flags
    check_file_content(runtime_dir / "station_chief_runtime.py", r'--station-chief-v22-approved-business-workflow', "Missing v22 CLI flag")

    # Doctrine
    check_file_content(v22_report, "Controlled Business Workflow Tool Expansion", "Report missing doctrine")
    check_file_content(root_dir / "10_runtime/station_chief_runtime_readme.md", "Station Chief Runtime upgraded to v22.0.0", "Readme missing doctrine")

    # Run prior smoke tests if not skipping
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") != "1":
        validators = [
            "21_0", "20_0", "19_0", "18_0", "17_0", "16_0", "15_0", "14_0", "13_0", "12_0", "11_0", "10_0", "9_0", "8_0", 
            "6_6", "6_5", "6_4", "6_3", "6_2", "6_1", "6_0", 
            "5_9", "5_8", "5_7", "5_6", "5_5", "5_4", "5_3", "5_2", "5_1", "5_0"
        ]
        for v in validators:
            v_path = root_dir / f"scripts/validate_station_chief_runtime_v{v}.py"
            if v_path.exists():
                run_script(v_path)
    else:
        print("Skipping recursive prior version smoke tests (env var set)...")

    print("STATION_CHIEF_RUNTIME_V22_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
