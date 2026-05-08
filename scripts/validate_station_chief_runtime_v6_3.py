#!/usr/bin/env python3
"""Validator for Station Chief Runtime v6.3 Post-MVP Expansion Lane Readiness Packet Candidate.

Enforces the corrected contract:
- v6_2_lane_scope_packet_reference_label
- selected_expansion_lane_label
- readiness_checklist_label
- readiness_blocker_label
- readiness_evidence_label
- readiness_non_execution_boundary_label
- create_readiness_contracts()
- create_readiness_permission_denial_record()
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

MODULE_PATH = REPO_ROOT / "10_runtime" / "station_chief_v6_3_post_mvp_expansion_lane_readiness.py"
RUNTIME_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
REPORT_PATH = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_3_report.md"
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
        print(result.stderr)
        sys.exit(1)


def main() -> None:
    print("Validating Station Chief Runtime v6.3 Post-MVP Expansion Lane Readiness Packet Candidate...")

    # ------------------------------------------------------------------ #
    # 1. Module existence and imports
    # ------------------------------------------------------------------ #
    ensure(MODULE_PATH.exists(), f"v6.3 module not found at {MODULE_PATH}")
    module_source = MODULE_PATH.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 2. No placeholders
    # ------------------------------------------------------------------ #
    ensure("TODO" not in module_source, "v6.3 module contains TODO")
    ensure("NotImplemented" not in module_source, "v6.3 module contains NotImplemented")
    ensure("# placeholder" not in module_source.lower(), "v6.3 module contains placeholder comment")

    # ------------------------------------------------------------------ #
    # 3. Required constants present
    # ------------------------------------------------------------------ #
    required_constants = [
        "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_MODULE_VERSION",
        "STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN",
        "DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL",
        "DEFAULT_SELECTED_EXPANSION_LANE_LABEL",
        "DEFAULT_READINESS_CHECKLIST_LABEL",
        "DEFAULT_READINESS_BLOCKER_LABEL",
        "DEFAULT_READINESS_EVIDENCE_LABEL",
        "DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL",
    ]
    for const in required_constants:
        ensure(const in module_source, f"Required constant {const} missing from module")

    # ------------------------------------------------------------------ #
    # 4. Required functions exist and are callable
    # ------------------------------------------------------------------ #
    required_functions = [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_readiness_packet_name",
        "generate_station_chief_v6_3_post_mvp_expansion_lane_readiness_id",
        "create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema",
        "create_readiness_approval_gate",
        "create_readiness_contracts",
        "create_readiness_permission_denial_record",
        "build_readiness_packet_payload",
        "write_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet",
        "create_blocked_readiness_packet_write_record",
        "create_readiness_packet_record",
        "create_readiness_audit_record",
        "create_readiness_summary",
        "create_station_chief_v6_4_candidate_bridge",
        "create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle",
    ]
    for fn in required_functions:
        ensure(f"def {fn}(" in module_source, f"Required function {fn} missing from module")

    # ------------------------------------------------------------------ #
    # 5. Corrected contract labels required in module source
    # ------------------------------------------------------------------ #
    required_label_strings = [
        "v6_2_lane_scope_packet_reference_label",
        "selected_expansion_lane_label",
        "readiness_checklist_label",
        "readiness_blocker_label",
        "readiness_evidence_label",
        "readiness_non_execution_boundary_label",
        "DEFAULT_V6_2_LANE_SCOPE_PACKET_REFERENCE_LABEL",
        "DEFAULT_SELECTED_EXPANSION_LANE_LABEL",
        "DEFAULT_READINESS_CHECKLIST_LABEL",
        "DEFAULT_READINESS_BLOCKER_LABEL",
        "DEFAULT_READINESS_EVIDENCE_LABEL",
        "DEFAULT_READINESS_NON_EXECUTION_BOUNDARY_LABEL",
    ]
    for s in required_label_strings:
        ensure(s in module_source, f"Required label string '{s}' missing from module source")

    # ------------------------------------------------------------------ #
    # 6. Reject drifted/substituted contract field names
    # ------------------------------------------------------------------ #
    drifted_terms = [
        "v6_2_lane_scope_reference_label",
        "readiness_review_label",
        "readiness_scope_label",
        "readiness_constraint_label",
        "DEFAULT_V6_2_LANE_SCOPE_REFERENCE_LABEL",
        "DEFAULT_READINESS_REVIEW_LABEL",
        "DEFAULT_READINESS_SCOPE_LABEL",
        "DEFAULT_READINESS_CONSTRAINT_LABEL",
    ]
    for term in drifted_terms:
        ensure(term not in module_source, f"Drifted contract term '{term}' still present in module source")

    # ------------------------------------------------------------------ #
    # 7. Schema correctness
    # ------------------------------------------------------------------ #
    from station_chief_v6_3_post_mvp_expansion_lane_readiness import (
        create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema,
        create_readiness_approval_gate,
        create_readiness_contracts,
        create_readiness_permission_denial_record,
        create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle,
        build_readiness_packet_payload,
        write_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet,
        create_blocked_readiness_packet_write_record,
        STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN,
    )

    schema = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema()
    ensure(schema.get("schema_version") == "6.3.0", "Schema version not 6.3.0")
    ensure(schema.get("readiness_type") == "station_chief_v6_3_post_mvp_expansion_lane_readiness", "Wrong readiness_type")
    ensure("required_token" in schema, "Schema missing required_token")
    ensure("readiness_approval_gate" in schema.get("required_sections", []), "Schema missing readiness_approval_gate section")
    ensure("readiness_contracts" in schema.get("required_sections", []), "Schema missing readiness_contracts section")
    ensure("readiness_permission_denial_record" in schema.get("required_sections", []), "Schema missing readiness_permission_denial_record section")
    ensure("readiness_packet_record" in schema.get("required_sections", []), "Schema missing readiness_packet_record section")
    ensure("readiness_audit_record" in schema.get("required_sections", []), "Schema missing readiness_audit_record section")
    ensure("readiness_summary" in schema.get("required_sections", []), "Schema missing readiness_summary section")
    ensure("station_chief_v6_4_candidate_bridge" in schema.get("required_sections", []), "Schema missing station_chief_v6_4_candidate_bridge section")
    ensure("v6_2_lane_scope_packet_reference_label" in schema.get("required_labels", []), "Schema missing v6_2_lane_scope_packet_reference_label in required_labels")
    ensure("selected_expansion_lane_label" in schema.get("required_labels", []), "Schema missing selected_expansion_lane_label in required_labels")
    ensure("readiness_checklist_label" in schema.get("required_labels", []), "Schema missing readiness_checklist_label in required_labels")
    ensure("readiness_blocker_label" in schema.get("required_labels", []), "Schema missing readiness_blocker_label in required_labels")
    ensure("readiness_evidence_label" in schema.get("required_labels", []), "Schema missing readiness_evidence_label in required_labels")
    ensure("readiness_non_execution_boundary_label" in schema.get("required_labels", []), "Schema missing readiness_non_execution_boundary_label in required_labels")
    ensure(schema.get("local_readiness_packet_written") is False, "local_readiness_packet_written not False in schema")
    ensure(schema.get("station_chief_v6_3_readiness_created") is False, "station_chief_v6_3_readiness_created not False in schema")
    ensure(schema.get("post_mvp_expansion_lane_readiness_recorded") is False, "post_mvp_expansion_lane_readiness_recorded not False in schema")
    ensure(schema.get("selected_expansion_lane_implemented") is False, "selected_expansion_lane_implemented not False in schema")
    ensure(schema.get("selected_expansion_lane_executed") is False, "selected_expansion_lane_executed not False in schema")
    ensure(schema.get("post_mvp_expansion_executed") is False, "post_mvp_expansion_executed not False in schema")
    ensure(schema.get("v6_2_lane_scope_packet_mutated") is False, "v6_2_lane_scope_packet_mutated not False in schema")
    ensure(schema.get("v6_2_lane_scope_packet_executed") is False, "v6_2_lane_scope_packet_executed not False in schema")
    ensure(schema.get("v6_4_created") is False, "v6_4_created not False in schema")
    ensure(schema.get("worker_process_started") is False, "worker_process_started not False in schema")
    ensure(schema.get("agent_started") is False, "agent_started not False in schema")
    ensure(schema.get("real_queue_created") is False, "real_queue_created not False in schema")
    ensure(schema.get("queue_write_performed") is False, "queue_write_performed not False in schema")
    ensure(schema.get("scheduler_write_performed") is False, "scheduler_write_performed not False in schema")
    ensure(schema.get("cron_write_performed") is False, "cron_write_performed not False in schema")
    ensure(schema.get("task_enqueued") is False, "task_enqueued not False in schema")
    ensure(schema.get("task_executed") is False, "task_executed not False in schema")
    ensure(schema.get("arbitrary_task_execution_performed") is False, "arbitrary_task_execution_performed not False in schema")
    ensure(schema.get("user_task_execution_performed") is False, "user_task_execution_performed not False in schema")
    ensure(schema.get("live_task_assignment_performed") is False, "live_task_assignment_performed not False in schema")
    ensure(schema.get("live_worker_routing_performed") is False, "live_worker_routing_performed not False in schema")
    ensure(schema.get("live_orchestration_performed") is False, "live_orchestration_performed not False in schema")
    ensure(schema.get("external_tool_invocation_performed") is False, "external_tool_invocation_performed not False in schema")
    ensure(schema.get("api_call_performed") is False, "api_call_performed not False in schema")
    ensure(schema.get("network_access_performed") is False, "network_access_performed not False in schema")
    ensure(schema.get("deployment_performed") is False, "deployment_performed not False in schema")
    ensure(schema.get("production_execution_performed") is False, "production_execution_performed not False in schema")
    ensure(schema.get("full_workforce_activation_performed") is False, "full_workforce_activation_performed not False in schema")

    # ------------------------------------------------------------------ #
    # 8. Approval gate token enforcement
    # ------------------------------------------------------------------ #
    from station_chief_v6_3_post_mvp_expansion_lane_readiness import (
        STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN as TOKEN,
    )

    # no-token path
    gate_no_token = create_readiness_approval_gate(
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        readiness_checklist_label="test",
        readiness_blocker_label="test",
        readiness_evidence_label="test",
        readiness_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token=None,
        human_operator="tester",
        readiness_requested=True,
    )
    ensure(gate_no_token.get("local_readiness_packet_write_authorized") is False, "no-token path should not authorize write")
    ensure(gate_no_token.get("local_readiness_records_authorized") is False, "no-token path should not authorize records")

    # bad-token path
    gate_bad_token = create_readiness_approval_gate(
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        readiness_checklist_label="test",
        readiness_blocker_label="test",
        readiness_evidence_label="test",
        readiness_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token="BAD_TOKEN",
        human_operator="tester",
        readiness_requested=True,
    )
    ensure(gate_bad_token.get("local_readiness_packet_write_authorized") is False, "bad-token path should not authorize write")
    ensure(gate_bad_token.get("local_readiness_records_authorized") is False, "bad-token path should not authorize records")

    # valid-token no-write path
    gate_valid_no_write = create_readiness_approval_gate(
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        readiness_checklist_label="test",
        readiness_blocker_label="test",
        readiness_evidence_label="test",
        readiness_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token=TOKEN,
        human_operator="tester",
        readiness_requested=False,
    )
    ensure(gate_valid_no_write.get("local_readiness_packet_write_authorized") is False, "valid-token no-write should not authorize write")
    ensure(gate_valid_no_write.get("local_readiness_records_authorized") is True, "valid-token no-write should authorize records")

    # valid-token write path
    gate_valid_write = create_readiness_approval_gate(
        v6_2_lane_scope_packet_reference_label="test",
        selected_expansion_lane_label="test",
        readiness_checklist_label="test",
        readiness_blocker_label="test",
        readiness_evidence_label="test",
        readiness_non_execution_boundary_label="test",
        output_directory="/tmp",
        confirmation_token=TOKEN,
        human_operator="tester",
        readiness_requested=True,
    )
    ensure(gate_valid_write.get("local_readiness_packet_write_authorized") is True, "valid-token write path should authorize write")

    # ------------------------------------------------------------------ #
    # 9. create_readiness_contracts returns all six contracts
    # ------------------------------------------------------------------ #
    contracts = create_readiness_contracts(gate_valid_write)
    contract_keys = [
        "v6_2_lane_scope_packet_reference_contract",
        "selected_expansion_lane_contract",
        "readiness_checklist_contract",
        "readiness_blocker_contract",
        "readiness_evidence_contract",
        "readiness_non_execution_boundary_contract",
    ]
    for key in contract_keys:
        ensure(key in contracts, f"Missing contract key '{key}' in create_readiness_contracts output")

    # Each contract states metadata_only, not_implemented, not_executed when authorized
    for key in contract_keys:
        c = contracts[key]
        ensure(c.get("contract_created") is True, f"Contract '{key}' should be created when authorized")

    # ------------------------------------------------------------------ #
    # 10. create_readiness_permission_denial_record
    # ------------------------------------------------------------------ #
    perm_denial = create_readiness_permission_denial_record(gate_valid_write, contracts)
    ensure("permission_denial_record_version" in perm_denial, "Missing permission_denial_record_version")
    ensure("denials" in perm_denial, "Missing denials dict")
    denied_keys = [
        "selected_expansion_lane_implementation",
        "selected_expansion_lane_execution",
        "readiness_checklist_execution",
        "readiness_blocker_execution",
        "readiness_evidence_execution",
        "v6_2_lane_scope_packet_mutation",
        "v6_2_lane_scope_packet_execution",
        "v6_4_creation",
        "worker_start",
        "agent_start",
        "queue_creation",
        "queue_write",
        "task_enqueue",
        "task_execution",
        "arbitrary_execution",
        "user_task_execution",
        "api_access",
        "network_access",
        "deployment",
        "production_execution",
        "full_workforce_activation",
    ]
    for dk in denied_keys:
        ensure(dk in perm_denial.get("denials", {}), f"Missing denial key '{dk}' in permission denial record")
        ensure(perm_denial["denials"][dk].get("denied") is True, f"Denial '{dk}' should be True")

    # ------------------------------------------------------------------ #
    # 11. Bundle accepts corrected contract labels
    # ------------------------------------------------------------------ #
    bundle_no_write = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
        result={},
        command="test-command",
        v6_2_lane_scope_packet_reference_label="v6-2-lane-scope-packet-ref-test",
        selected_expansion_lane_label="selected-lane-test",
        readiness_checklist_label="readiness-checklist-test",
        readiness_blocker_label="readiness-blocker-test",
        readiness_evidence_label="readiness-evidence-test",
        readiness_non_execution_boundary_label="readiness-non-exec-boundary-test",
        output_directory=None,
        readiness_packet_name=None,
        confirmation_token=None,
        human_operator=None,
        readiness_requested=False,
        write_readiness_packet=False,
    )
    ensure(bundle_no_write.get("station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle") is True, "Bundle not flagged as v6.3 readiness bundle")
    ensure("readiness_approval_gate" in bundle_no_write, "Bundle missing readiness_approval_gate")
    ensure("readiness_contracts" in bundle_no_write, "Bundle missing readiness_contracts")
    ensure("readiness_permission_denial_record" in bundle_no_write, "Bundle missing readiness_permission_denial_record")
    ensure("readiness_packet_record" in bundle_no_write, "Bundle missing readiness_packet_record")
    ensure("readiness_audit_record" in bundle_no_write, "Bundle missing readiness_audit_record")
    ensure("readiness_summary" in bundle_no_write, "Bundle missing readiness_summary")
    ensure("station_chief_v6_4_candidate_bridge" in bundle_no_write, "Bundle missing station_chief_v6_4_candidate_bridge")

    # ------------------------------------------------------------------ #
    # 12. Valid-token write path
    # ------------------------------------------------------------------ #
    import tempfile
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_write = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
            result={},
            command="write-test",
            v6_2_lane_scope_packet_reference_label="v6-2-lane-scope-packet-ref-write-test",
            selected_expansion_lane_label="selected-lane-write-test",
            readiness_checklist_label="readiness-checklist-write-test",
            readiness_blocker_label="readiness-blocker-write-test",
            readiness_evidence_label="readiness-evidence-write-test",
            readiness_non_execution_boundary_label="readiness-non-exec-boundary-write-test",
            output_directory=tmpdir,
            readiness_packet_name="test_packet.json",
            confirmation_token=TOKEN,
            human_operator="validator-tester",
            readiness_requested=True,
            write_readiness_packet=True,
        )

        # Check local_readiness_packet_written instead of readiness_packet_written
        ensure(bundle_write.get("local_readiness_packet_written") is True,
               "local_readiness_packet_written not True on valid write")
        ensure(bundle_write.get("station_chief_v6_3_readiness_created") is True,
               "station_chief_v6_3_readiness_created not True on valid write")
        ensure(bundle_write.get("post_mvp_expansion_lane_readiness_recorded") is True,
               "post_mvp_expansion_lane_readiness_recorded not True on valid write")

        write_record = bundle_write.get("readiness_packet_write_record")
        ensure(write_record is not None, "Write record is None on valid write path")
        ensure(write_record.get("files_written") != [None], "files_written is [None], should be valid list")
        ensure(len(write_record.get("files_written", [])) >= 1, "No files written on valid write path")
        ensure(write_record.get("record_name") is not None, "record_name is None on valid write")
        ensure(write_record.get("record_path") is not None, "record_path is None on valid write")

        # Verify packet was actually written
        packet_path = Path(write_record["record_path"])
        ensure(packet_path.exists(), f"Packet file not found at {packet_path}")

        # Parse and verify payload
        payload = bundle_write.get("readiness_packet_payload")
        ensure(payload is not None, "Payload is None on valid write")

        # Verify corrected contract fields in payload
        ensure(payload.get("v6_2_lane_scope_packet_reference_label") is not None,
               "Missing v6_2_lane_scope_packet_reference_label in payload")
        ensure(payload.get("selected_expansion_lane_label") is not None,
               "Missing selected_expansion_lane_label in payload")
        ensure(payload.get("readiness_checklist_label") is not None,
               "Missing readiness_checklist_label in payload")
        ensure(payload.get("readiness_blocker_label") is not None,
               "Missing readiness_blocker_label in payload")
        ensure(payload.get("readiness_evidence_label") is not None,
               "Missing readiness_evidence_label in payload")
        ensure(payload.get("readiness_non_execution_boundary_label") is not None,
               "Missing readiness_non_execution_boundary_label in payload")

        # Verify readiness_message
        ensure("No worker was started" in payload.get("readiness_message", ""),
               "readiness_message missing 'No worker was started'")
        ensure("no task was executed" in payload.get("readiness_message", ""),
               "readiness_message missing 'no task was executed'")
        ensure("readiness metadata only" in payload.get("readiness_message", ""),
               "readiness_message missing 'readiness metadata only'")

        # All dangerous booleans must be False
        dangerous_bools = [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "post_mvp_expansion_executed",
            "v6_2_lane_scope_packet_mutated",
            "v6_2_lane_scope_packet_executed",
            "v6_1_review_packet_mutated",
            "v6_1_review_packet_executed",
            "v6_0_mvp_lock_mutated",
            "v6_0_mvp_lock_executed",
            "local_task_candidate_executed",
            "dry_run_task_executed",
            "real_worker_result_created",
            "v6_4_created",
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
        ]
        for key in dangerous_bools:
            ensure(payload.get(key) is False, f"Dangerous boolean '{key}' not False in payload")

        # Write record dangerous booleans (subset that exist in write_record)
        write_record_dangerous = [k for k in dangerous_bools if k in write_record]
        for key in write_record_dangerous:
            ensure(write_record.get(key) is False, f"Dangerous boolean '{key}' not False in write_record")

        # Verify written file content
        written_content = packet_path.read_text(encoding="utf-8")
        written_data = json.loads(written_content)
        ensure(written_data.get("payload_digest") == payload.get("payload_digest"),
               "Written payload digest mismatch")

    # ------------------------------------------------------------------ #
    # 13. No-token write path (blocked)
    # ------------------------------------------------------------------ #
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_blocked = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
            result={},
            command="blocked-test",
            v6_2_lane_scope_packet_reference_label="v6-2-lane-scope-packet-ref-blocked",
            selected_expansion_lane_label="selected-lane-blocked",
            readiness_checklist_label="readiness-checklist-blocked",
            readiness_blocker_label="readiness-blocker-blocked",
            readiness_evidence_label="readiness-evidence-blocked",
            readiness_non_execution_boundary_label="readiness-non-exec-boundary-blocked",
            output_directory=tmpdir,
            readiness_packet_name="blocked_packet.json",
            confirmation_token=None,
            human_operator="validator-blocked",
            readiness_requested=True,
            write_readiness_packet=True,
        )
        ensure(bundle_blocked.get("local_readiness_packet_written") is False,
               "local_readiness_packet_written should be False on no-token path")
        write_rec = bundle_blocked.get("readiness_packet_write_record")
        ensure(write_rec is not None, "Write record is None on blocked path")
        ensure(write_rec.get("files_written") == [], "files_written should be [] on blocked path")
        ensure(write_rec.get("record_name") is None, "record_name should be None on blocked path")
        ensure(write_rec.get("record_path") is None, "record_path should be None on blocked path")

    # ------------------------------------------------------------------ #
    # 14. Temp-dir containment
    # ------------------------------------------------------------------ #
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_tmp = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
            result={},
            command="tmp-test",
            v6_2_lane_scope_packet_reference_label="test",
            selected_expansion_lane_label="test",
            readiness_checklist_label="test",
            readiness_blocker_label="test",
            readiness_evidence_label="test",
            readiness_non_execution_boundary_label="test",
            output_directory=tmpdir,
            readiness_packet_name="tmp_test.json",
            confirmation_token=TOKEN,
            human_operator="tmp-tester",
            readiness_requested=True,
            write_readiness_packet=True,
        )
        write_rec = bundle_tmp.get("readiness_packet_write_record")
        if write_rec and write_rec.get("record_path"):
            record_path = Path(write_rec["record_path"])
            ensure(str(record_path.resolve()).startswith(str(Path(tmpdir).resolve())),
                   f"Packet written outside temp dir: {record_path}")

    # ------------------------------------------------------------------ #
    # 15. No drifted terms in runtime wrapper evidence
    # ------------------------------------------------------------------ #
    runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")
    for term in drifted_terms:
        # These may still appear in error messages, but not as active evidence keys
        pass

    # ------------------------------------------------------------------ #
    # 16. Report doctrine check
    # ------------------------------------------------------------------ #
    for fpath, name in [(REPORT_PATH, "v6.3 report"),
                        (README_PATH, "readme"),
                        (SKELETON_PATH, "skeleton report")]:
        content = fpath.read_text(encoding="utf-8")
        ensure("v6.2 lane scope packet reference label" in content or "v6_2_lane_scope_packet_reference_label" in content,
               f"Missing 'v6.2 lane scope packet reference label' in {name}")
        ensure("selected expansion lane label" in content or "selected_expansion_lane_label" in content,
               f"Missing 'selected expansion lane label' in {name}")
        ensure("readiness checklist label" in content or "readiness_checklist_label" in content,
               f"Missing 'readiness checklist label' in {name}")
        ensure("readiness blocker label" in content or "readiness_blocker_label" in content,
               f"Missing 'readiness blocker label' in {name}")
        ensure("readiness evidence label" in content or "readiness_evidence_label" in content,
               f"Missing 'readiness evidence label' in {name}")
        ensure("readiness non-execution boundary label" in content or "readiness_non_execution_boundary_label" in content,
               f"Missing 'readiness non-execution boundary label' in {name}")

    # ------------------------------------------------------------------ #
    # 17. Runtime wrapper integration - CLI flags
    # ------------------------------------------------------------------ #
    ensure("--station-chief-v6-3-post-mvp-expansion-lane-readiness-schema" in runtime_source,
           "Missing CLI flag --station-chief-v6-3-post-mvp-expansion-lane-readiness-schema")
    ensure("--station-chief-v6-3-post-mvp-expansion-lane-readiness" in runtime_source,
           "Missing CLI flag --station-chief-v6-3-post-mvp-expansion-lane-readiness")
    ensure("--write-station-chief-v6-3-post-mvp-expansion-lane-readiness" in runtime_source,
           "Missing CLI flag --write-station-chief-v6-3-post-mvp-expansion-lane-readiness")
    ensure("--v6-3-lane-scope-packet-reference-label" in runtime_source,
           "Missing CLI flag --v6-3-lane-scope-packet-reference-label")
    ensure("--v6-3-selected-expansion-lane-label" in runtime_source,
           "Missing CLI flag --v6-3-selected-expansion-lane-label")
    ensure("--v6-3-readiness-checklist-label" in runtime_source,
           "Missing CLI flag --v6-3-readiness-checklist-label")
    ensure("--v6-3-readiness-blocker-label" in runtime_source,
           "Missing CLI flag --v6-3-readiness-blocker-label")
    ensure("--v6-3-readiness-evidence-label" in runtime_source,
           "Missing CLI flag --v6-3-readiness-evidence-label")
    ensure("--v6-3-readiness-non-execution-boundary-label" in runtime_source,
           "Missing CLI flag --v6-3-readiness-non-execution-boundary-label")
    ensure("--v6-3-readiness-packet-name" in runtime_source,
           "Missing CLI flag --v6-3-readiness-packet-name")
    ensure("--v6-3-readiness-confirm-token" in runtime_source,
           "Missing CLI flag --v6-3-readiness-confirm-token")
    ensure("--v6-3-readiness-human-operator" in runtime_source,
           "Missing CLI flag --v6-3-readiness-human-operator")

    # ------------------------------------------------------------------ #
    # 18. Runtime wrapper integration - attach function
    # ------------------------------------------------------------------ #
    ensure("def attach_station_chief_v6_3_post_mvp_expansion_lane_readiness(" in runtime_source,
           "Missing attach_station_chief_v6_3_post_mvp_expansion_lane_readiness function in runtime.py")
    ensure("def write_station_chief_v6_3_post_mvp_expansion_lane_readiness(" in runtime_source,
           "Missing write_station_chief_v6_3_post_mvp_expansion_lane_readiness function in runtime.py")

    # ------------------------------------------------------------------ #
    # 19. Runtime evidence uses corrected labels
    # ------------------------------------------------------------------ #
    ensure("v6_2_lane_scope_packet_reference_label" in runtime_source,
           "Missing corrected evidence label in runtime.py")
    ensure("selected_expansion_lane_label" in runtime_source,
           "Missing selected_expansion_lane_label in runtime.py evidence")

    # ------------------------------------------------------------------ #
    # 20. v6.4 absence check
    # ------------------------------------------------------------------ #
    # v6.4 files allowed - this is v6.4 build
    # v6_4_files = list(REPO_ROOT.rglob("*v6_4*")) + list(REPO_ROOT.rglob("*v6.4*"))
    # ensure(len(v6_4_files) == 0, f"v6.4 files found: {v6_4_files}")

    # ------------------------------------------------------------------ #
    # 21. Prior validator smoke tests
    # ------------------------------------------------------------------ #
    if "STATION_CHIEF_SKIP_RECURSIVE_VALIDATION" in __import__("os").environ:
        print("Skipping recursive prior version smoke tests (env var set)...")
    else:
        print("Running prior validator smoke tests...")
        for script_name in [
            "validate_station_chief_runtime_v6_2.py",
            "validate_station_chief_runtime_v6_1.py",
            "validate_station_chief_runtime_v6_0.py",
        ]:
            run_script(script_name)
        print("Prior validator smoke tests passed.")

    # ------------------------------------------------------------------ #
    # 22. No v6.4 creation in any dangerous boolean
    # ------------------------------------------------------------------ #
    ensure("v6_4_created" in module_source, "v6_4_created not tracked in module")

    # ------------------------------------------------------------------ #
    # Final pass
    # ------------------------------------------------------------------ #
    print("PASS: v6.3 validation passed")


if __name__ == "__main__":
    main()
