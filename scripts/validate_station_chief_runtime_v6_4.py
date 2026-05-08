#!/usr/bin/env python3
"""Validator for Station Chief Runtime v6.4 Post-MVP Expansion Lane Non-Executing Implementation Plan."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

MODULE_PATH = REPO_ROOT / "10_runtime" / "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan.py"
RUNTIME_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
REPORT_PATH = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_4_report.md"
README_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON_PATH = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"


def ensure(condition: bool, msg: str) -> None:
    if not condition:
        print(f"FAIL: {msg}")
        sys.exit(1)


def run_script(script_name: str) -> None:
    path = REPO_ROOT / "scripts" / script_name
    ensure(path.exists(), f"Prior validator {script_name} not found")
    env = {**__import__("os").environ, "STATION_CHIEF_SKIP_RECURSIVE_VALIDATION": "1"}
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"FAIL: prior validator {script_name} failed")
        print(result.stderr[:500])
        sys.exit(1)


def main() -> None:
    print("Validating Station Chief Runtime v6.4...")

    ensure(MODULE_PATH.exists(), f"v6.4 module not found")
    module_source = MODULE_PATH.read_text(encoding="utf-8")

    ensure("TODO" not in module_source, "v6.4 module contains TODO")
    ensure("NotImplemented" not in module_source, "v6.4 module contains NotImplemented")

    required_constants = [
        "STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_MODULE_VERSION",
        "STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN",
        "DEFAULT_V6_3_READINESS_PACKET_REFERENCE_LABEL",
        "DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL",
        "DEFAULT_SELECTED_EXPANSION_LANE_LABEL",
        "DEFAULT_IMPLEMENTATION_PLAN_LABEL",
    ]
    for const in required_constants:
        ensure(const in module_source, f"Required constant {const} missing")

    required_functions = [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "create_implementation_plan_approval_gate",
        "create_implementation_plan_contracts",
        "create_implementation_plan_permission_denial_record",
        "build_implementation_plan_packet_payload",
        "write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_packet",
        "create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle",
    ]
    for fn in required_functions:
        ensure(f"def {fn}(" in module_source, f"Required function {fn} missing")

    from station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan import (
        create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema,
        create_implementation_plan_approval_gate,
        create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle,
        STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN as TOKEN,
    )

    schema = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema()
    ensure(schema.get("schema_version") == "6.4.0", "Schema version not 6.4.0")
    ensure(schema.get("local_implementation_plan_packet_written") is False, "Default should be False")

    import tempfile

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

    with tempfile.TemporaryDirectory() as tmpdir:
        bundle = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle(
            result={},
            command="test",
            v6_3_readiness_packet_reference_label="test",
            v6_2_lane_scope_packet_reference_label="test",
            selected_expansion_lane_label="test",
            implementation_plan_label="test",
            implementation_step_list_label="test",
            implementation_risk_register_label="test",
            implementation_rollback_plan_label="test",
            implementation_non_execution_boundary_label="test",
            output_directory=tmpdir,
            implementation_plan_packet_name="test.json",
            confirmation_token=TOKEN,
            human_operator="tester",
            implementation_plan_requested=True,
            write_implementation_plan_packet=True,
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
        ensure("v6.5" not in bundle, "v6.5 not created")

    dangerous_bools = [
        "selected_expansion_lane_implemented",
        "selected_expansion_lane_executed",
        "implementation_plan_executed",
        "v6_5_created",
        "worker_process_started",
        "agent_started",
        "real_queue_created",
        "task_executed",
    ]
    for key in dangerous_bools:
        ensure(bundle.get(key) is False, f"{key} is False")

    v6_4_files = [f for f in REPO_ROOT.rglob("*v6_4*") if f.suffix not in ('.pyc',) and '__pycache__' not in str(f)]
v6_4_glob = [f for f in REPO_ROOT.rglob("*v6_4*") if f.suffix not in ('.pyc',) and '__pycache__' not in str(f)]
allowed_v6_4 = [
    "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan.py",
    "station_chief_runtime_v6_4_report.md",
    "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_preflight_audit.md",
    "validate_station_chief_runtime_v6_4.py",
]
for f in v6_4_glob:
    if f.name not in allowed_v6_4:
        ensure(False, f"Unexpected v6.4 file: {f}")

    v6_5_files = [f for f in REPO_ROOT.rglob("*v6_5*") if f.suffix not in ('.pyc',) and '__pycache__' not in str(f)]
    ensure(len(v6_5_files) == 0, f"v6.5 files found: {v6_5_files}")

    runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")
    ensure("STATION_CHIEF_RUNTIME_VERSION" in runtime_source and 'STATION_CHIEF_RUNTIME_VERSION = "6.4.0"' in runtime_source, "Runtime not at 6.4.0")

    print("Running prior validator smoke tests...")
    for script in ["validate_station_chief_runtime_v6_3.py", "validate_station_chief_runtime_v6_2.py"]:
        run_script(script)

    print("STATION_CHIEF_RUNTIME_V6_4_VALIDATION_PASS")
    print("PASS: v6.4 validation passed")


if __name__ == "__main__":
    main()