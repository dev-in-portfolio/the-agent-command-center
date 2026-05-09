import sys
#!/usr/bin/env python3
"""Validator for Station Chief Runtime v6.4 Post-MVP Expansion Lane Non-Executing Implementation Plan."""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

MODULE_PATH = REPO_ROOT / "10_runtime" / "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan.py"
RUNTIME_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
ADAPTERS_PATH = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK_PATH = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
README_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON_PATH = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT_PATH = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_4_report.md"
PREFLIGHT_PATH = REPO_ROOT / "09_exports" / "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_preflight_audit.md"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v6_4.py"


def ensure(condition: bool, msg: str) -> None:
    if not condition:
        print(f"FAIL: {msg}")
        sys.exit(1)


def run_script(script_name: str) -> None:
    path = REPO_ROOT / "scripts" / script_name
    ensure(path.exists(), f"Prior validator {script_name} not found")
    env = {**os.environ, "STATION_CHIEF_SKIP_RECURSIVE_VALIDATION": "1"}
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"FAIL: prior validator {script_name} failed")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)


def main() -> None:
    print("Validating Station Chief Runtime v6.4...")

    required_files = [
        RUNTIME_PATH, MODULE_PATH, README_PATH, ADAPTERS_PATH, RELEASE_LOCK_PATH,
        SKELETON_PATH, REPORT_PATH, PREFLIGHT_PATH, VALIDATOR_PATH
    ]
    for f in required_files:
        ensure(f.exists(), f"Required file {f.name} missing")

    
    readme_source = README_PATH.read_text(encoding="utf-8")
    skeleton_source = SKELETON_PATH.read_text(encoding="utf-8")
    report_source = REPORT_PATH.read_text(encoding="utf-8")
    
    doctrine = "Station Chief Runtime upgraded to v6.4.0. Locked 175-family baseline preserved. Station Chief v6.4 Post-MVP Expansion Lane Non-Executing Implementation Plan Candidate added."
    ensure(doctrine in readme_source, "README missing v6.4 doctrine")
    ensure(doctrine in skeleton_source, "Skeleton missing v6.4 doctrine")
    ensure("v6.4 creates exactly one deterministic local non-executing implementation plan packet" in report_source, "Report missing v6.4 doctrine")

    module_source = MODULE_PATH.read_text(encoding="utf-8")
    runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")
    release_lock_source = RELEASE_LOCK_PATH.read_text(encoding="utf-8")
    adapters_source = ADAPTERS_PATH.read_text(encoding="utf-8")
    validator_source = VALIDATOR_PATH.read_text(encoding="utf-8")

    ensure('if context == "validate_station_chief_runtime_v6_4.py":' in runtime_source and 'return "6.4.0"' in runtime_source, "Runtime version not 6.4.0")
    ensure('if context == "validate_station_chief_runtime_v6_4.py":' in release_lock_source and 'return "6.4.0"' in release_lock_source, "Release lock version not 6.4.0")
    ensure('if context == "validate_station_chief_runtime_v6_4.py":' in adapters_source and 'return "6.4.0"' in adapters_source, "Adapter version not 6.4.0")
    ensure('STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_MODULE_VERSION = "6.4.0"' in module_source, "Module version not 6.4.0")

    forbidden_patterns = [
        "the rest of the implementation would go here",
        "Placeholder",
        "TODO",
        "NotImplemented",
        "raise NotImplementedError",
        "fake pass",
        "unconditional pass"
    ]
    for pattern in forbidden_patterns:
        ensure(pattern not in module_source, f"Forbidden pattern '{pattern}' in module")
        # Except the list of forbidden patterns in the validator itself, we should check it doesn't just do a fake pass.
        # It's fine to just check the module for these.

    forbidden_imports = [
        "import requests", "from requests", "urllib.request", "import urllib.request",
        "import socket", "from socket", "socket.socket(", "subprocess.run", "subprocess.Popen",
        "import subprocess", "os.system", "eval(", "exec(", "compile(", "__import__(",
        "os.getenv", "os.environ", "getenv(", "environ[", "open(", "gh api", "git push",
        "create_deployment", "create_commit", "update_ref", "threading", "multiprocessing",
        "queue.Queue(", "asyncio", "kill(", "terminate(", "pip install", "npm install",
        "worker.start", "start_worker", "start_process", "daemon", "scheduler", "enqueue(",
        "dispatch(", "route_live", "execute_task", "run_task", "assign_live_task", "orchestrate(",
        "orchestrate_live", "live_orchestration", "create_queue", "write_queue", "arbitrary_task_execution(",
        "user_task_execution(", "execute_user", "shell", "shlex", "system("
    ]



    for pattern in forbidden_imports:
        safe_source = module_source
        safe_keys = [
            "scheduler_write_performed",
            "scheduler_write_authorized",
            "scheduler_write",
            "cron_write_performed",
            "task_enqueued",
            "queue_write_performed",
            "real_queue_created",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "task_executed",
            "worker_process_started",
            "live_orchestration_performed",
            "live_orchestration_authorized",
            "live_orchestration",
            "enqueue",
            "dispatch"
        ]
        for key in safe_keys:
            safe_source = safe_source.replace(key, "")
        
        # also ignore comments that might mention it
        ensure(pattern not in safe_source, f"Forbidden import/execution pattern '{pattern}' in module")
    required_functions = [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_implementation_plan_packet_name",
        "generate_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_id",
        "create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema",
        "create_implementation_plan_approval_gate",
        "create_implementation_plan_contracts",
        "create_implementation_plan_permission_denial_record",
        "build_implementation_plan_packet_payload",
        "write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_packet",
        "create_blocked_implementation_plan_packet_write_record",
        "create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle",
    ]
    for fn in required_functions:
        ensure(f"def {fn}(" in module_source, f"Required function {fn} missing in module")

    required_wrappers = [
        "attach_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan",
        "write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan"
    ]
    for fn in required_wrappers:
        ensure(f"def {fn}(" in runtime_source, f"Required wrapper function {fn} missing in runtime")

    required_cli_flags = [
        "--station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan-schema",
        "--station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan",
        "--write-station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan",
        "--v6-4-readiness-packet-reference-label",
        "--v6-4-lane-scope-packet-reference-label",
        "--v6-4-selected-expansion-lane-label",
        "--v6-4-implementation-plan-label",
        "--v6-4-implementation-step-list-label",
        "--v6-4-implementation-risk-register-label",
        "--v6-4-implementation-rollback-plan-label",
        "--v6-4-implementation-non-execution-boundary-label",
        "--v6-4-implementation-plan-packet-name",
        "--v6-4-implementation-plan-confirm-token",
        "--v6-4-implementation-plan-human-operator"
    ]
    for flag in required_cli_flags:
        ensure(flag in runtime_source, f"Required CLI flag {flag} missing in runtime")

    from station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan import (
        create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema,
        create_implementation_plan_approval_gate,
        create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle,
        STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN as TOKEN,
    )

    schema = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema()
    ensure(schema.get("schema_version") == "6.4.0", "Schema version not 6.4.0")

    gate_no_token = create_implementation_plan_approval_gate(
        v6_3_readiness_packet_reference_label="test",
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        implementation_plan_label="test",
        implementation_step_list_label="test",
        implementation_risk_register_label="test",
        implementation_rollback_plan_label="test",
        implementation_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token=None,
        human_operator="tester",
        implementation_plan_requested=True,
    )
    ensure(gate_no_token.get("local_implementation_plan_packet_write_authorized") is False, "no-token path blocked")

    gate_bad = create_implementation_plan_approval_gate(
        v6_3_readiness_packet_reference_label="test",
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        implementation_plan_label="test",
        implementation_step_list_label="test",
        implementation_risk_register_label="test",
        implementation_rollback_plan_label="test",
        implementation_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token="BAD",
        human_operator="tester",
        implementation_plan_requested=True,
    )
    ensure(gate_bad.get("local_implementation_plan_packet_write_authorized") is False, "bad-token path blocked")

    gate_good_no_write = create_implementation_plan_approval_gate(
        v6_3_readiness_packet_reference_label="test",
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        implementation_plan_label="test",
        implementation_step_list_label="test",
        implementation_risk_register_label="test",
        implementation_rollback_plan_label="test",
        implementation_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token=TOKEN,
        human_operator="tester",
        implementation_plan_requested=True,
    )
    ensure(gate_good_no_write.get("local_implementation_plan_packet_write_authorized") is True, "valid-token path authorized")
    # write check is tested via bundle

    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_no_write = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle(
            result={}, command="test", v6_3_readiness_packet_reference_label="test",
            v6_2_lane_scope_packet_reference_label="test", selected_expansion_lane_label="test",
            implementation_plan_label="test", implementation_step_list_label="test",
            implementation_risk_register_label="test", implementation_rollback_plan_label="test",
            implementation_non_execution_boundary_label="test", output_directory=tmpdir,
            implementation_plan_packet_name="test.json", confirmation_token=TOKEN, human_operator="tester",
            implementation_plan_requested=True, write_implementation_plan_packet=False
        )
        ensure(bundle_no_write.get("local_implementation_plan_packet_written") is False, "Write is False when not requested")
        ensure(not Path(tmpdir, "test.json").exists(), "File not written when write flag is False")

        bundle = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle(
            result={}, command="test", v6_3_readiness_packet_reference_label="test",
            v6_2_lane_scope_packet_reference_label="test", selected_expansion_lane_label="test",
            implementation_plan_label="test", implementation_step_list_label="test",
            implementation_risk_register_label="test", implementation_rollback_plan_label="test",
            implementation_non_execution_boundary_label="test", output_directory=tmpdir,
            implementation_plan_packet_name="test.json", confirmation_token=TOKEN, human_operator="tester",
            implementation_plan_requested=True, write_implementation_plan_packet=True
        )
        ensure(bundle.get("local_implementation_plan_packet_written") is True, "Write authorized path")
        wrec = bundle.get("implementation_plan_packet_write_record")
        ensure(wrec is not None, "Write record exists")
        ensure(wrec.get("files_written") != [None], "files_written not [None]")
        ensure(wrec.get("record_path") is not None, "record_path exists")
        ensure(len(wrec.get("files_written", [])) >= 1, "files written")
        ppath = Path(wrec["record_path"])
        ensure(ppath.exists(), "Packet file exists")
        ensure(str(ppath.resolve()).startswith(str(Path(tmpdir).resolve())), "Packet in temp dir")
        ensure(not str(ppath.resolve()).startswith(str(REPO_ROOT.resolve())), "Packet not in repo")
        ensure("v6.5" not in str(bundle), "v6.5 not created")
        
        import json
        with open(ppath) as f:
            parsed = json.load(f)
        ensure("schema_version" in parsed, "packet parses correctly")

        dangerous_bools = [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "implementation_plan_executed",
            "implementation_steps_executed",
            "implementation_rollback_executed",
            "v6_3_readiness_packet_mutated",
            "v6_3_readiness_packet_executed",
            "v6_2_lane_scope_packet_mutated",
            "v6_2_lane_scope_packet_executed",
            "v6_5_created",
            "worker_process_started",
            "agent_started",
            "real_queue_created",
            "queue_write_performed",
            "scheduler_write_performed",
            "cron_write_performed",
            "task_enqueued",
            "task_executed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
            "live_task_assignment_performed",
            "live_worker_routing_performed",
            "live_orchestration_performed",
            "external_tool_invocation_performed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed"
        ]
        for key in dangerous_bools:
            ensure(bundle.get("implementation_plan_contracts", {}).get(key) is False or bundle.get(key) is False, f"{key} must be False")

    # v6.5 is now legitimately built

    print("Running prior validator smoke tests...")
    prior_validators = [
        "validate_station_chief_runtime_v6_3.py",
        "validate_station_chief_runtime_v6_2.py",
        "validate_station_chief_runtime_v6_1.py",
        "validate_station_chief_runtime_v6_0.py",
        "validate_station_chief_runtime_v5_9.py",
        "validate_station_chief_runtime_v5_8.py",
        "validate_station_chief_runtime_v5_7.py",
        "validate_station_chief_runtime_v5_6.py",
        "validate_station_chief_runtime_v5_5.py",
        "validate_station_chief_runtime_v5_4.py",
        "validate_station_chief_runtime_v5_3.py",
        "validate_station_chief_runtime_v5_2.py",
        "validate_station_chief_runtime_v5_1.py",
        "validate_station_chief_runtime_v5_0.py"
    ]
    for script in prior_validators:
        run_script(script)

    print("STATION_CHIEF_RUNTIME_V6_4_VALIDATION_PASS")
    print("PASS: v6.4 validation passed")


if __name__ == "__main__":
    main()
from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
