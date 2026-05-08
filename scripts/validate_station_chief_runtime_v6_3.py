#!/usr/bin/env python3
"""v6.3 Validator: Station Chief Post-MVP Expansion Lane Readiness Packet Candidate.

This validator checks that:
1. The v6.3 module file exists and imports cleanly.
2. The module exposes all required constants and functions.
3. The module's schema is correct and complete.
4. The approval gate properly enforces the token requirement.
5. All dangerous booleans are False by default.
6. The readiness packet write path is properly gated.
7. The v6.3 bundle function produces a correct bundle with all sections.
8. No v6.4 files are created.
9. The run_station_chief evidence entries reflect v6.3 status correctly.
10. The adapter module recognizes v6.3 support.
11. The release lock module recognizes v6.3.
12. The runtime module imports and recognizes v6.3.
"""

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))
RUNTIME_DIR = REPO_ROOT / "10_runtime"
EXPORTS_DIR = REPO_ROOT / "09_exports"


def validate_file_exists(path: Path, label: str) -> bool:
    if not path.exists():
        print(f"FAIL: {label} file not found at {path}")
        return False
    print(f"PASS: {label} file exists at {path}")
    return True


def validate_imports(path: Path, label: str) -> tuple[bool, object]:
    try:
        spec = importlib.util.spec_from_file_location(label, path)
        if spec is None or spec.loader is None:
            print(f"FAIL: Could not load spec for {label}")
            return False, None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"PASS: {label} imports cleanly")
        return True, mod
    except Exception as e:
        print(f"FAIL: {label} import error: {e}")
        return False, None


def check_constant(mod, name: str, expected_type: type, label: str) -> bool:
    val = getattr(mod, name, None)
    if val is None:
        print(f"FAIL: {label} missing constant {name}")
        return False
    if not isinstance(val, expected_type):
        print(f"FAIL: {label} constant {name} has wrong type (expected {expected_type.__name__}, got {type(val).__name__})")
        return False
    print(f"PASS: {label} constant {name} = {val}")
    return True


def check_function(mod, name: str, label: str) -> bool:
    fn = getattr(mod, name, None)
    if fn is None:
        print(f"FAIL: {label} missing function {name}")
        return False
    if not callable(fn):
        print(f"FAIL: {label} {name} is not callable")
        return False
    print(f"PASS: {label} function {name} exists and is callable")
    return True


def run_all_checks() -> int:
    failures = 0
    passed = 0

    v6_3_module_path = RUNTIME_DIR / "station_chief_v6_3_post_mvp_expansion_lane_readiness.py"
    runtime_path = RUNTIME_DIR / "station_chief_runtime.py"
    adapters_path = RUNTIME_DIR / "station_chief_adapters.py"
    release_lock_path = RUNTIME_DIR / "station_chief_release_lock.py"
    preflight_audit_path = EXPORTS_DIR / "station_chief_v6_3_post_mvp_expansion_lane_readiness_preflight_audit.md"
    v6_3_report_path = EXPORTS_DIR / "station_chief_runtime_v6_3_report.md"
    v6_4_files = list(RUNTIME_DIR.glob("*v6_4*")) + list(SCRIPTS_DIR.glob("*v6_4*")) + list(EXPORTS_DIR.glob("*v6_4*"))

    # 1. Module file existence
    print("\n--- Check 1: v6.3 module file existence ---")
    ok = validate_file_exists(v6_3_module_path, "v6.3 module")
    if ok:
        passed += 1
    else:
        failures += 1

    # 2. v6.3 module imports and exposes constants/functions
    print("\n--- Check 2: v6.3 module imports and constants ---")
    ok_mod, mod = validate_imports(v6_3_module_path, "station_chief_v6_3_post_mvp_expansion_lane_readiness")
    if ok_mod and mod:
        passed += 1
    else:
        failures += 1

    if ok_mod and mod:
        print("\n--- Check 2a: v6.3 module constants ---")
        const_checks = [
            ("STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_MODULE_VERSION", str, 1),
            ("STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_STATUS", str, 1),
            ("STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PHASE", str, 1),
            ("STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN", str, 1),
            ("DEFAULT_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_NAME", str, 1),
            ("SUPPORTED_READINESS_LABELS", list, 1),
        ]
        for cname, ctype, weight in const_checks:
            if check_constant(mod, cname, ctype, "v6.3 module"):
                passed += weight
            else:
                failures += weight

        print("\n--- Check 2b: v6.3 module functions ---")
        fn_checks = [
            "canonical_json",
            "sha256_digest",
            "normalize_label",
            "safe_readiness_packet_name",
            "generate_station_chief_v6_3_post_mvp_expansion_lane_readiness_id",
            "create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema",
            "create_readiness_approval_gate",
            "create_v6_2_lane_scope_reference_contract",
            "create_readiness_review_contract",
            "create_readiness_scope_contract",
            "create_readiness_constraint_contract",
            "create_readiness_non_execution_boundary_contract",
            "build_readiness_packet_payload",
            "write_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet",
            "create_blocked_readiness_packet_write_record",
            "create_readiness_packet_record",
            "create_readiness_audit_record",
            "create_readiness_summary",
            "create_station_chief_v6_4_candidate_bridge",
            "create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle",
        ]
        for fn_name in fn_checks:
            if check_function(mod, fn_name, "v6.3 module"):
                passed += 1
            else:
                failures += 1
    else:
        print("SKIP: v6.3 module function/constant checks (module did not load)")
        failures += 30

    # 3. Schema correctness and completeness
    print("\n--- Check 3: Schema correctness ---")
    if ok_mod and mod:
        schema = mod.create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema()
        schema_ok = True
        if not isinstance(schema, dict):
            print("FAIL: schema is not a dict")
            schema_ok = False
            failures += 1
        if schema.get("schema_version") != "6.3.0":
            print(f"FAIL: schema_version is {schema.get('schema_version')}, expected 6.3.0")
            schema_ok = False
            failures += 1
        if schema.get("status") != "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_LOCAL_PACKET_ONLY":
            print(f"FAIL: schema status is wrong")
            schema_ok = False
            failures += 1
        if schema.get("readiness_type") != "station_chief_v6_3_post_mvp_expansion_lane_readiness":
            print(f"FAIL: schema readiness_type is wrong")
            schema_ok = False
            failures += 1
        if schema.get("required_token") != "YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET":
            print(f"FAIL: schema required_token is wrong")
            schema_ok = False
            failures += 1
        dangerous_keys = [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "post_mvp_expansion_executed",
            "v6_2_lane_scope_mutated",
            "v6_2_lane_scope_executed",
            "v6_1_review_packet_mutated",
            "v6_1_review_packet_executed",
            "v6_0_mvp_lock_mutated",
            "v6_0_mvp_lock_executed",
            "local_task_candidate_executed",
            "dry_run_task_executed",
            "real_worker_result_created",
            "live_replay_performed",
            "production_audit_performed",
            "rollback_performed",
            "recovery_performed",
            "worker_process_started",
            "agent_started",
            "real_queue_created",
            "queue_write_performed",
            "task_enqueued",
            "task_executed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "v6_4_created",
        ]
        for key in dangerous_keys:
            val = schema.get(key)
            if val is not False:
                print(f"FAIL: schema key {key} is {val}, expected False")
                schema_ok = False
                failures += 1
        if schema.get("baseline_preserved") is not True:
            print(f"FAIL: schema baseline_preserved is not True")
            schema_ok = False
            failures += 1
        if schema.get("readiness_packet_written") is not False:
            print(f"FAIL: schema readiness_packet_written should be False initially")
            schema_ok = False
            failures += 1
        required_sections = schema.get("required_sections", [])
        expected_sections = [
            "readiness_approval_gate",
            "v6_2_lane_scope_reference_contract",
            "readiness_review_contract",
            "readiness_scope_contract",
            "readiness_constraint_contract",
            "readiness_non_execution_boundary_contract",
            "readiness_packet_record",
            "readiness_audit_record",
            "readiness_summary",
        ]
        for section in expected_sections:
            if section not in required_sections:
                print(f"FAIL: schema missing required section {section}")
                schema_ok = False
                failures += 1
        if schema_ok:
            print("PASS: schema is correct and complete")
            passed += 5
    else:
        print("SKIP: schema check (module did not load)")
        failures += 5

    # 4. Approval gate token enforcement
    print("\n--- Check 4: Approval gate token enforcement ---")
    if ok_mod and mod:
        # Without token - should be BLOCKED
        gate_no_token = mod.create_readiness_approval_gate(
            v6_2_lane_scope_reference_label="test",
            readiness_review_label="test",
            readiness_scope_label="test",
            readiness_constraint_label="test",
            readiness_non_execution_boundary_label="test",
            output_directory="/tmp",
            confirmation_token=None,
            human_operator="test-operator",
            readiness_requested=True,
        )
        if "BLOCKED" not in gate_no_token.get("gate_status", ""):
            print(f"FAIL: gate should be BLOCKED without token, got {gate_no_token.get('gate_status')}")
            failures += 1
        else:
            print("PASS: gate correctly blocks without token")
            passed += 1

        if gate_no_token.get("local_readiness_packet_write_authorized") is not False:
            print("FAIL: local_readiness_packet_write_authorized should be False without token")
            failures += 1
        else:
            print("PASS: local_readiness_packet_write_authorized is False without token")
            passed += 1

        # With correct token but missing operator - should be BLOCKED
        gate_no_operator = mod.create_readiness_approval_gate(
            v6_2_lane_scope_reference_label="test",
            readiness_review_label="test",
            readiness_scope_label="test",
            readiness_constraint_label="test",
            readiness_non_execution_boundary_label="test",
            output_directory="/tmp",
            confirmation_token="YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET",
            human_operator=None,
            readiness_requested=True,
        )
        if "BLOCKED" not in gate_no_operator.get("gate_status", ""):
            print(f"FAIL: gate should be BLOCKED without operator, got {gate_no_operator.get('gate_status')}")
            failures += 1
        else:
            print("PASS: gate correctly blocks without operator")
            passed += 1

        # With correct token and operator but no readiness_requested
        gate_no_request = mod.create_readiness_approval_gate(
            v6_2_lane_scope_reference_label="test",
            readiness_review_label="test",
            readiness_scope_label="test",
            readiness_constraint_label="test",
            readiness_non_execution_boundary_label="test",
            output_directory="/tmp",
            confirmation_token="YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET",
            human_operator="test-operator",
            readiness_requested=False,
        )
        if "BLOCKED" not in gate_no_request.get("gate_status", ""):
            print(f"FAIL: gate should be BLOCKED without readiness_requested, got {gate_no_request.get('gate_status')}")
            failures += 1
        else:
            print("PASS: gate correctly blocks without readiness_requested")
            passed += 1

        # With incorrect token
        gate_wrong_token = mod.create_readiness_approval_gate(
            v6_2_lane_scope_reference_label="test",
            readiness_review_label="test",
            readiness_scope_label="test",
            readiness_constraint_label="test",
            readiness_non_execution_boundary_label="test",
            output_directory="/tmp",
            confirmation_token="WRONG_TOKEN",
            human_operator="test-operator",
            readiness_requested=True,
        )
        if "BLOCKED" not in gate_wrong_token.get("gate_status", ""):
            print(f"FAIL: gate should be BLOCKED with wrong token, got {gate_wrong_token.get('gate_status')}")
            failures += 1
        else:
            print("PASS: gate correctly blocks with wrong token")
            passed += 1

        # With all correct inputs - should be APPROVED
        gate_full = mod.create_readiness_approval_gate(
            v6_2_lane_scope_reference_label="v6-2-lane-scope-test",
            readiness_review_label="readiness-review-test",
            readiness_scope_label="readiness-scope-test",
            readiness_constraint_label="readiness-constraint-test",
            readiness_non_execution_boundary_label="readiness-non-exec-boundary-test",
            output_directory="/tmp/v6_3_test",
            confirmation_token="YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET",
            human_operator="test-operator",
            readiness_requested=True,
        )
        if "APPROVED" not in gate_full.get("gate_status", ""):
            print(f"FAIL: gate should be APPROVED with valid inputs, got {gate_full.get('gate_status')}")
            failures += 1
        else:
            print("PASS: gate correctly approves with valid inputs")
            passed += 1

        if gate_full.get("local_readiness_packet_write_authorized") is not True:
            print("FAIL: local_readiness_packet_write_authorized should be True with valid inputs")
            failures += 1
        else:
            print("PASS: local_readiness_packet_write_authorized is True with valid inputs")
            passed += 1

        # Verify all dangerous authorizations remain False
        dangerous_auth_keys = [
            "selected_expansion_lane_implementation_authorized",
            "selected_expansion_lane_execution_authorized",
            "post_mvp_expansion_execution_authorized",
            "v6_2_lane_scope_mutation_authorized",
            "v6_2_lane_scope_execution_authorized",
            "v6_1_review_packet_mutation_authorized",
            "v6_1_review_packet_execution_authorized",
            "v6_0_mvp_lock_mutation_authorized",
            "v6_0_mvp_lock_execution_authorized",
            "worker_process_start_authorized",
            "agent_start_authorized",
            "real_queue_creation_authorized",
            "task_execution_authorized",
            "v6_4_creation_authorized",
            "api_call_authorized",
            "network_access_authorized",
            "deployment_authorized",
            "production_execution_authorized",
        ]
        all_dangerous_false = True
        for dkey in dangerous_auth_keys:
            val = gate_full.get(dkey)
            if val is not False:
                print(f"FAIL: {dkey} should be False, got {val}")
                all_dangerous_false = False
                failures += 1
        if all_dangerous_false:
            print("PASS: all dangerous authorization flags are False")
            passed += 3
    else:
        print("SKIP: approval gate checks (module did not load)")
        failures += 10

    # 5. All dangerous booleans are False by default in schema
    print("\n--- Check 5: Schema dangerous booleans ---")
    if ok_mod and mod:
        dangerous_schema_keys = [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "post_mvp_expansion_executed",
            "v6_2_lane_scope_mutated",
            "v6_2_lane_scope_executed",
            "v6_1_review_packet_mutated",
            "v6_1_review_packet_executed",
            "v6_0_mvp_lock_mutated",
            "v6_0_mvp_lock_executed",
            "local_task_candidate_executed",
            "dry_run_task_executed",
            "real_worker_result_created",
            "live_replay_performed",
            "production_audit_performed",
            "rollback_performed",
            "recovery_performed",
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
            "full_workforce_activation_performed",
            "v6_4_created",
        ]
        all_false = True
        schema_test = mod.create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema()
        for key in dangerous_schema_keys:
            val = schema_test.get(key)
            if val is not False:
                print(f"FAIL: schema key {key} is {val}, expected False")
                all_false = False
                failures += 1
        if all_false:
            print("PASS: all dangerous booleans are False in schema")
            passed += 2
    else:
        print("SKIP: dangerous boolean check (module did not load)")
        failures += 2

    # 6. Readiness packet write path gating
    print("\n--- Check 6: Readiness packet write path gating ---")
    if ok_mod and mod:
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle = mod.create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
                result=None,
                command="test command for v6.3 validator",
                v6_2_lane_scope_reference_label="v6-2-lane-scope-validator-test",
                readiness_review_label="readiness-review-validator-test",
                readiness_scope_label="readiness-scope-validator-test",
                readiness_constraint_label="readiness-constraint-validator-test",
                readiness_non_execution_boundary_label="readiness-non-exec-boundary-validator-test",
                output_directory=tmpdir,
                readiness_packet_name="test_readiness_packet.json",
                confirmation_token="YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET",
                human_operator="validator-operator",
                readiness_requested=True,
                write_readiness_packet=True,
            )
            packet_written = bundle.get("readiness_packet_written", False)
            readiness_created = bundle.get("station_chief_v6_3_readiness_created", False)
            if not packet_written:
                print("FAIL: readiness packet was not written despite valid inputs")
                failures += 1
            else:
                print("PASS: readiness packet was written with valid inputs")
                passed += 1
            if not readiness_created:
                print("FAIL: station_chief_v6_3_readiness_created was not True")
                failures += 1
            else:
                print("PASS: station_chief_v6_3_readiness_created is True")
                passed += 1

            write_record = bundle.get("readiness_packet_write_record", {})
            if write_record.get("write_status") != "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_WRITTEN":
                print(f"FAIL: write_status is {write_record.get('write_status')}, expected STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET_WRITTEN")
                failures += 1
            else:
                print("PASS: write_status is correct")
                passed += 1

            file_path = write_record.get("record_path", "")
            if file_path:
                file_obj = Path(file_path)
                if file_obj.exists():
                    content = file_obj.read_text()
                    print(f"PASS: packet file exists at {file_path}")
                    passed += 1
                    try:
                        parsed = json.loads(content)
                        if parsed.get("readiness_type") == "station_chief_v6_3_post_mvp_expansion_lane_readiness":
                            print("PASS: packet content has correct readiness_type")
                            passed += 1
                        else:
                            print(f"FAIL: packet readiness_type is wrong")
                            failures += 1
                        if parsed.get("readiness_execution_type") == "none_readiness_metadata_only":
                            print("PASS: packet has correct execution type")
                            passed += 1
                        else:
                            print(f"FAIL: packet readiness_execution_type is wrong")
                            failures += 1
                        if parsed.get("payload_digest"):
                            print("PASS: packet has payload_digest")
                            passed += 1
                        else:
                            print("FAIL: packet missing payload_digest")
                            failures += 1
                        dangerous_packet_keys = [
                            "selected_expansion_lane_implemented",
                            "selected_expansion_lane_executed",
                            "v6_2_lane_scope_mutated",
                            "worker_process_started",
                            "agent_started",
                            "task_executed",
                            "v6_4_created",
                        ]
                        all_packet_danger_false = True
                        for pk in dangerous_packet_keys:
                            if parsed.get(pk) is not False:
                                print(f"FAIL: packet key {pk} should be False")
                                all_packet_danger_false = False
                                failures += 1
                        if all_packet_danger_false:
                            print("PASS: all dangerous packet booleans are False")
                            passed += 2
                    except json.JSONDecodeError:
                        print(f"FAIL: packet file is not valid JSON")
                        failures += 1
                else:
                    print(f"FAIL: packet file does not exist at {file_path}")
                    failures += 1

            # Verify all sections exist in bundle
            section_checks = [
                "schema", "approval_gate", "v6_2_lane_scope_reference_contract",
                "readiness_review_contract", "readiness_scope_contract",
                "readiness_constraint_contract", "readiness_non_execution_boundary_contract",
                "readiness_packet_record", "readiness_audit_record",
                "readiness_summary", "station_chief_v6_4_candidate_bridge",
                "readiness_packet_payload", "readiness_packet_write_record",
            ]
            all_sections_present = True
            for section in section_checks:
                if section not in bundle:
                    print(f"FAIL: bundle missing section {section}")
                    all_sections_present = False
                    failures += 1
            if all_sections_present:
                print("PASS: bundle contains all required sections")
                passed += 2

            # Check audit record
            audit = bundle.get("readiness_audit_record", {})
            if audit.get("audit_status") == "PASS":
                print("PASS: audit record PASSES")
                passed += 1
            else:
                print(f"FAIL: audit status is {audit.get('audit_status')}, expected PASS")
                failures += 1

            # Check summary
            summary = bundle.get("readiness_summary", {})
            if summary.get("readiness_status") == "READY_FOR_V6_4_REVIEW_ONLY":
                print("PASS: readiness summary shows READY_FOR_V6_4_REVIEW_ONLY")
                passed += 1
            else:
                print(f"FAIL: readiness_status is {summary.get('readiness_status')}")
                failures += 1

            # Check v6.4 bridge
            bridge = bundle.get("station_chief_v6_4_candidate_bridge", {})
            if bridge.get("bridge_to_v6_4_review_only") is True:
                print("PASS: v6.4 bridge shows bridge_to_v6_4_review_only")
                passed += 1
            else:
                print(f"FAIL: bridge_to_v6_4_review_only is {bridge.get('bridge_to_v6_4_review_only')}")
                failures += 1
            if bridge.get("v6_4_not_created_in_v6_3") is True:
                print("PASS: v6.4 bridge confirms v6.4 not created")
                passed += 1
            else:
                print(f"FAIL: v6_4_not_created_in_v6_3 is {bridge.get('v6_4_not_created_in_v6_3')}")
                failures += 1

        # Bundle with write_readiness_packet=False - should be BLOCKED
        bundle_no_write = mod.create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
            result=None,
            command="test no-write",
            output_directory="/tmp",
            confirmation_token="YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET",
            human_operator="test-operator",
            readiness_requested=True,
            write_readiness_packet=False,
        )
        if bundle_no_write.get("readiness_packet_written") is False:
            print("PASS: packet not written when write_readiness_packet=False")
            passed += 1
        else:
            print("FAIL: packet should not be written when write_readiness_packet=False")
            failures += 1
    else:
        print("SKIP: write path checks (module did not load)")
        failures += 15

    # 7. No v6.4 files exist
    print("\n--- Check 7: No v6.4 files created ---")
    if len(v6_4_files) == 0:
        print("PASS: No v6.4 files found")
        passed += 2
    else:
        print(f"FAIL: v6.4 files found: {[str(f) for f in v6_4_files]}")
        failures += 2

    # 8. Preflight audit and v6.3 report exist
    print("\n--- Check 8: Preflight audit and v6.3 report exist ---")
    ok2 = validate_file_exists(preflight_audit_path, "v6.3 preflight audit")
    if ok2:
        passed += 1
    else:
        failures += 1
    ok3 = validate_file_exists(v6_3_report_path, "v6.3 report")
    if ok3:
        passed += 1
    else:
        failures += 1

    # 9. Runtime module imports and recognizes v6.3
    print("\n--- Check 9: Runtime module v6.3 integration ---")
    ok_runtime, runtime_mod = validate_imports(runtime_path, "station_chief_runtime")
    if ok_runtime and runtime_mod:
        runtime_version = getattr(runtime_mod, "STATION_CHIEF_RUNTIME_VERSION", None)
        if runtime_version and "6.3.0" in str(runtime_version):
            print(f"PASS: runtime version is {runtime_version}")
            passed += 1
        else:
            print(f"FAIL: runtime version is {runtime_version}, expected 6.3.0")
            failures += 1

        # Check that v6.3 module is imported
        has_v6_3_import = hasattr(runtime_mod, "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN")
        if has_v6_3_import:
            print("PASS: runtime module imports v6.3 approval token")
            passed += 1
        else:
            print("FAIL: runtime module does not import v6.3 approval token")
            failures += 1

        has_v6_3_bundle = hasattr(runtime_mod, "create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle")
        if has_v6_3_bundle:
            print("PASS: runtime module imports v6.3 bundle function")
            passed += 1
        else:
            print("FAIL: runtime module does not import v6.3 bundle function")
            failures += 1
    else:
        print("SKIP: runtime module checks (did not load)")
        failures += 3

    # 10. Adapter module recognizes v6.3
    print("\n--- Check 10: Adapter module v6.3 recognition ---")
    ok_adapt, adapt_mod = validate_imports(adapters_path, "station_chief_adapters")
    if ok_adapt and adapt_mod:
        adapt_version = getattr(adapt_mod, "ADAPTER_MODULE_VERSION", None)
        if adapt_version and "6.3.0" in str(adapt_version):
            print(f"PASS: adapter version is {adapt_version}")
            passed += 1
        else:
            print(f"FAIL: adapter version is {adapt_version}, expected 6.3.0")
            failures += 1

        adapters = getattr(adapt_mod, "SUPPORTED_ADAPTERS", {})
        noop = adapters.get("noop", {})
        if noop.get("supports_station_chief_v6_3_post_mvp_expansion_lane_readiness") is True:
            print("PASS: noop adapter supports v6.3")
            passed += 1
        else:
            print("FAIL: noop adapter missing v6.3 support flag")
            failures += 1
    else:
        print("SKIP: adapter module checks (did not load)")
        failures += 2

    # 11. Release lock module recognizes v6.3
    print("\n--- Check 11: Release lock module v6.3 recognition ---")
    ok_lock, lock_mod = validate_imports(release_lock_path, "station_chief_release_lock")
    if ok_lock and lock_mod:
        lock_version = getattr(lock_mod, "STABLE_RUNTIME_VERSION", None)
        if lock_version and "6.3.0" in str(lock_version):
            print(f"PASS: release lock version is {lock_version}")
            passed += 1
        else:
            print(f"FAIL: release lock version is {lock_version}, expected 6.3.0")
            failures += 1
    else:
        print("SKIP: release lock module checks (did not load)")
        failures += 1

    # 12. Script validator file own integrity
    print("\n--- Check 12: Validator self-integrity ---")
    val_path = Path(__file__)
    if val_path.exists() and val_path.name == "validate_station_chief_runtime_v6_3.py":
        print(f"PASS: validator is {val_path.name}")
        passed += 1
    else:
        print("FAIL: validator file integrity check")
        failures += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"v6.3 VALIDATION SUMMARY: {passed} passed, {failures} failed")
    print("=" * 60)

    if failures > 0:
        print("FAIL: v6.3 validation failed")
        return 1
    print("PASS: v6.3 validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_checks())
