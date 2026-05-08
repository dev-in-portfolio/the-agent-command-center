#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V6_2_MODULE = REPO_ROOT / "10_runtime" / "station_chief_v6_2_post_mvp_expansion_lane_scope.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_2_report.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

sys.path.append(str(REPO_ROOT / "10_runtime"))

EXPECTED_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE"
HUMAN_OPERATOR = "Devin"
V6_1_REVIEW_PACKET_REFERENCE_LABEL = "v6.1 review packet reference alpha"
SELECTED_EXPANSION_LANE_LABEL = "local_worker_persona_expansion_scope"
LANE_SCOPE_LABEL = "lane scope alpha"
LANE_CONSTRAINT_LABEL = "lane constraint alpha"
LANE_SUCCESS_CRITERIA_LABEL = "lane success criteria alpha"
LANE_NON_EXECUTION_BOUNDARY_LABEL = "lane non execution boundary alpha"
DEFAULT_PACKET_NAME = "station_chief_v6_2_post_mvp_expansion_lane_scope_packet.json"

FORBIDDEN_REGEXES = [
    r"import\s+requests\b",
    r"from\s+requests\b",
    r"urllib\.request",
    r"import\s+urllib\.request",
    r"import\s+socket\b",
    r"from\s+socket\b",
    r"socket\.socket\(",
    r"subprocess\.run\(",
    r"subprocess\.Popen\(",
    r"import\s+subprocess\b",
    r"os\.system\(",
    r"eval\(",
    r"exec\(",
    r"compile\(",
    r"__import__\(",
    r"os\.getenv\b",
    r"os\.environ\b",
    r"getenv\(",
    r"environ\[",
    r"open\(",
    r"gh api",
    r"git push",
    r"create_deployment",
    r"create_commit",
    r"update_ref",
    r"threading\b",
    r"multiprocessing\b",
    r"queue\.Queue\(",
    r"asyncio\b",
    r"kill\(",
    r"terminate\(",
    r"pip install",
    r"npm install",
    r"worker\.start\(",
    r"start_worker\(",
    r"start_process\(",
    r"daemon\(",
    r"scheduler\(",
    r"enqueue\(",
    r"dispatch\(",
    r"route_live\(",
    r"execute_task\(",
    r"run_task\(",
    r"assign_live_task\(",
    r"orchestrate\(",
    r"orchestrate_live\(",
    r"live_orchestration\(",
    r"create_queue\(",
    r"write_queue\(",
    r"arbitrary_task_execution\(",
    r"user_task_execution\(",
    r"execute_user\(",
    r"shlex\b",
    r"system\(",
]

PROTECTED_PATHS = [
    "02_departments/",
    "04_workflow_templates/",
    "09_exports/dashboard_seed.json",
    "09_exports/org_chart_export.json",
    "09_exports/master_department_list.md",
]

SAFE_KEYS = [
    "local_lane_scope_packet_written",
    "station_chief_v6_2_lane_scope_created",
    "post_mvp_expansion_lane_scope_recorded",
    "selected_expansion_lane_implemented",
    "selected_expansion_lane_executed",
    "post_mvp_expansion_executed",
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
    "v6_3_created",
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
    "api_call_performed",
    "network_access_performed",
    "socket_opened",
    "environment_read",
    "deployment_performed",
    "production_execution_performed",
]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        print(f"VALIDATION_FAILURE: {message}")
        sys.exit(1)


def run_json(script_path: Path, args: list[str]) -> dict:
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"DEBUG: Failed to parse JSON from: {result.stdout}")
        raise


def ensure_doctrine() -> None:
    print("Checking v6.2 doctrine...")
    common_phrases = [
        "Station Chief Runtime v6.2.0",
        "Station Chief v6.2 Post-MVP Expansion Lane Scope Candidate",
        "v6.2 may write exactly one deterministic local Station Chief post-MVP expansion lane scope packet only",
        "records a selected post-MVP expansion lane scope candidate as metadata only",
        "v6.2 does not implement selected expansion lane",
        "v6.2 does not execute selected expansion lane",
        "v6.2 does not execute post-MVP expansion",
        "v6.2 does not mutate v6.1 review packet",
        "v6.2 does not execute v6.1 review packet",
        "v6.2 does not mutate v6.0 MVP lock",
        "v6.2 does not execute v6.0 MVP lock",
        "v6.2 does not execute a local task candidate",
        "v6.2 does not execute a dry-run task",
        "v6.2 does not create a real worker result",
        "v6.2 does not start a worker",
        "v6.2 does not start an agent",
        "v6.2 does not approve v6.3",
        "v6.3 requires explicit operator instruction",
    ]
    for f in [README, SKELETON, REPORT]:
        content = f.read_text(encoding="utf-8")
        for p in common_phrases:
            ensure(p in content, f"Missing common doctrine phrase '{p}' in {f.name}")

    report_content = REPORT.read_text(encoding="utf-8")
    ensure("Station Chief runtime version is 6.2.0" in report_content, "Missing version doctrine in report")
    ensure("release lock is 6.2.0" in report_content, "Missing release lock doctrine in report")
    ensure("post-MVP expansion lane scope was recorded as metadata only: YES" in report_content, "Missing metadata doctrine in report")


def ensure_protected_paths() -> None:
    print("Checking protected paths...")
    status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True).stdout
    diff = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True).stdout
    cached_diff = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True).stdout
    all_changed = set(status.splitlines()) | set(diff.splitlines()) | set(cached_diff.splitlines())
    forbidden_indicators = ["devinization", "ownership", "credential", "secret", "env", "production", "deployment"]
    for path in all_changed:
        path = path.strip()
        if not path:
            continue
        if len(path) > 3 and path[2] == ' ':
            path = path[3:]
        for protected in PROTECTED_PATHS:
            ensure(not path.startswith(protected), f"Protected path mutation detected: {path}")
        for indicator in forbidden_indicators:
            if indicator in path.lower():
                allowed_exceptions = [
                    "scripts/validate_station_chief_runtime_v6_2.py",
                    "scripts/validate_station_chief_runtime_v6_",
                    "scripts/validate_station_chief_runtime_v5_",
                    "09_exports/station_chief_runtime_v6_2_report.md",
                    "10_runtime/station_chief_v6_2_post_mvp_expansion_lane_scope.py",
                ]
                if any(allowed_exc in path for allowed_exc in allowed_exceptions):
                    continue
                ensure(False, f"Forbidden indicator '{indicator}' found in changed path: {path}")


def ensure_no_v63_files() -> None:
    print("Checking for v6.3 files...")
    for p in REPO_ROOT.rglob("*"):
        if p.is_dir() and ".git" in p.parts:
            continue
        rel_p = str(p.relative_to(REPO_ROOT))
        for indicator in ["v6_3", "v6.3"]:
            ensure(indicator not in rel_p.lower(), f"Unexpected v6.3 file found: {rel_p}")


def ensure_wrapper_integration() -> None:
    print("Checking runtime wrapper integration...")
    import station_chief_runtime

    res = station_chief_runtime.run_station_chief("check please")
    ensure(res["station_chief_runtime_version"] == "6.2.0", "Runtime version mismatch in wrapper")

    no_write_res = station_chief_runtime.attach_station_chief_v6_2_post_mvp_expansion_lane_scope(
        {"command": "check please"},
        v6_1_review_packet_reference_label=V6_1_REVIEW_PACKET_REFERENCE_LABEL,
        selected_expansion_lane_label=SELECTED_EXPANSION_LANE_LABEL,
        lane_scope_label=LANE_SCOPE_LABEL,
        lane_constraint_label=LANE_CONSTRAINT_LABEL,
        lane_success_criteria_label=LANE_SUCCESS_CRITERIA_LABEL,
        lane_non_execution_boundary_label=LANE_NON_EXECUTION_BOUNDARY_LABEL,
        confirmation_token=EXPECTED_TOKEN,
        human_operator=HUMAN_OPERATOR,
        lane_scope_requested=True,
        write_lane_scope_packet=False,
    )

    required_keys = [
        "station_chief_v6_2_post_mvp_expansion_lane_scope_bundle",
        "lane_scope_packet_record",
        "lane_scope_packet_write_record",
        "station_chief_v6_2_post_mvp_expansion_lane_scope",
    ]
    for k in required_keys:
        ensure(k in no_write_res, f"Missing key '{k}' in attach result")

    comp = no_write_res["station_chief_v6_2_post_mvp_expansion_lane_scope"]
    ensure("lane_scope_packet_record" in comp, "Missing packet record in compatibility object")
    ensure("write_record" in comp["lane_scope_packet_record"], "Missing write record in compatibility object")

    no_write_checks = {
        "local_lane_scope_packet_written": False,
        "station_chief_v6_2_lane_scope_created": False,
        "post_mvp_expansion_lane_scope_recorded": False,
        "selected_expansion_lane_implemented": False,
        "selected_expansion_lane_executed": False,
        "post_mvp_expansion_executed": False,
        "v6_1_review_packet_mutated": False,
        "v6_1_review_packet_executed": False,
        "v6_0_mvp_lock_mutated": False,
        "v6_0_mvp_lock_executed": False,
        "local_task_candidate_executed": False,
        "dry_run_task_executed": False,
        "real_worker_result_created": False,
        "live_replay_performed": False,
        "production_audit_performed": False,
        "rollback_performed": False,
        "recovery_performed": False,
        "v6_3_created": False,
    }
    for key, expected in no_write_checks.items():
        ensure(no_write_res.get(key) is expected, f"No-write path: '{key}' should be {expected}")

    with tempfile.TemporaryDirectory(prefix="station_chief_v6_2_test_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        ensure(not tmp_dir.resolve().is_relative_to(REPO_ROOT.resolve()), "Temp directory must be outside repo")

        write_res = station_chief_runtime.write_station_chief_v6_2_post_mvp_expansion_lane_scope(
            {"command": "check please"},
            str(tmp_dir),
            v6_1_review_packet_reference_label=V6_1_REVIEW_PACKET_REFERENCE_LABEL,
            selected_expansion_lane_label=SELECTED_EXPANSION_LANE_LABEL,
            lane_scope_label=LANE_SCOPE_LABEL,
            lane_constraint_label=LANE_CONSTRAINT_LABEL,
            lane_success_criteria_label=LANE_SUCCESS_CRITERIA_LABEL,
            lane_non_execution_boundary_label=LANE_NON_EXECUTION_BOUNDARY_LABEL,
            lane_scope_packet_name=DEFAULT_PACKET_NAME,
            confirmation_token=EXPECTED_TOKEN,
            human_operator=HUMAN_OPERATOR,
        )

        ensure(write_res.get("local_lane_scope_packet_written") is True, "Write path failed to mark written")
        files_written = write_res.get("files_written", [])
        ensure(len(files_written) == 1, f"Expected 1 file written, got {len(files_written)}")
        ensure(files_written[0] is not None, "files_written[0] is None")
        ensure(files_written[0].endswith(".json"), f"files_written[0] does not end with .json: {files_written[0]}")
        record_path = write_res.get("record_path")
        ensure(record_path is not None, "record_path is None on successful write")
        ensure(Path(record_path).exists(), f"Packet file does not exist at record_path: {record_path}")

        write_record = write_res["lane_scope_packet_write_record"]
        ensure(write_record.get("record_name") is not None, "record_name in write_record is None")
        ensure(write_record.get("record_path") is not None, "record_path in write_record is None")
        ensure(write_record.get("output_directory") == str(tmp_dir.resolve()), "output_directory mismatch")
        ensure(write_record.get("files_written_count") == 1, "files_written_count should be 1")

        payload = json.loads(Path(write_res["record_path"]).read_text(encoding="utf-8"))
        ensure(payload["runtime_version"] == "6.2.0", "Payload runtime version mismatch")
        ensure(payload["scope_type"] == "station_chief_v6_2_post_mvp_expansion_lane_scope", "Scope type mismatch")
        ensure(payload["local_lane_scope_packet_written"] is True, "Payload write flag mismatch")

        for key in [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "post_mvp_expansion_executed",
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
            "v6_3_created",
            "worker_process_started",
            "agent_started",
            "task_executed",
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
        ]:
            ensure(payload.get(key) is False, f"Dangerous flag '{key}' must be False in payload")


def validate_v6_2() -> None:
    print("Validating Station Chief Runtime v6.2.0...")

    ensure(RUNTIME_PATH.exists(), "runtime.py missing")
    ensure(V6_2_MODULE.exists(), "v6.2 module missing")
    ensure(README.exists(), "README missing")
    ensure(SKELETON.exists(), "skeleton report missing")
    ensure(REPORT.exists(), "v6.2 report missing")
    ensure(ADAPTERS.exists(), "adapters missing")
    ensure(RELEASE_LOCK.exists(), "release lock missing")

    runtime_code = RUNTIME_PATH.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_RUNTIME_VERSION = "6.2.0"' in runtime_code, "runtime version mismatch")

    adapters_code = ADAPTERS.read_text(encoding="utf-8")
    ensure('ADAPTER_MODULE_VERSION = "6.2.0"' in adapters_code, "adapter version mismatch")

    lock_code = RELEASE_LOCK.read_text(encoding="utf-8")
    ensure('STABLE_RUNTIME_VERSION = "6.2.0"' in lock_code, "release lock version mismatch")

    module_code = V6_2_MODULE.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_MODULE_VERSION = "6.2.0"' in module_code, "module version mismatch")

    for pattern in FORBIDDEN_REGEXES:
        matches = list(re.finditer(pattern, module_code))
        for m in matches:
            line = module_code[:m.start()].count("\n") + 1
            context_start = max(0, m.start() - 40)
            context_end = min(len(module_code), m.end() + 40)
            snippet = module_code[context_start:context_end]
            is_safe_key = any(f'"{key}"' in snippet or f"'{key}'" in snippet for key in SAFE_KEYS)
            if not is_safe_key:
                ensure(False, f"Forbidden implementation pattern '{pattern}' found in v6.2 module at line {line}")

    schema = run_json(RUNTIME_PATH, ["--station-chief-v6-2-post-mvp-expansion-lane-scope-schema"])
    ensure(schema["schema_version"] == "6.2.0", "schema version mismatch")
    ensure("supported_lane_scope_labels" in schema, "supported_lane_scope_labels missing in schema")
    ensure(len(schema["supported_lane_scope_labels"]) == 9, "Expected 9 supported lane scope labels")

    no_token_cmd = [
        sys.executable, str(RUNTIME_PATH),
        "--station-chief-v6-2-post-mvp-expansion-lane-scope",
        "--v6-2-review-packet-reference-label", V6_1_REVIEW_PACKET_REFERENCE_LABEL,
        "--v6-2-selected-expansion-lane-label", SELECTED_EXPANSION_LANE_LABEL,
        "--v6-2-lane-scope-label", LANE_SCOPE_LABEL,
        "--v6-2-lane-constraint-label", LANE_CONSTRAINT_LABEL,
        "--v6-2-lane-success-criteria-label", LANE_SUCCESS_CRITERIA_LABEL,
        "--v6-2-lane-non-execution-boundary-label", LANE_NON_EXECUTION_BOUNDARY_LABEL,
    ]
    no_token_res = subprocess.run(no_token_cmd, capture_output=True, text=True)
    try:
        no_token_data = json.loads(no_token_res.stdout)
    except json.JSONDecodeError:
        ensure(False, f"No-token path output not valid JSON: {no_token_res.stdout[:200]}")
    ensure(no_token_data.get("local_lane_scope_packet_written") is False, "No-token path should not write")
    ensure(no_token_data.get("station_chief_v6_2_lane_scope_created") is False, "No-token path should not create")

    bad_token_cmd = [
        sys.executable, str(RUNTIME_PATH),
        "--station-chief-v6-2-post-mvp-expansion-lane-scope",
        "--v6-2-review-packet-reference-label", V6_1_REVIEW_PACKET_REFERENCE_LABEL,
        "--v6-2-selected-expansion-lane-label", SELECTED_EXPANSION_LANE_LABEL,
        "--v6-2-lane-scope-label", LANE_SCOPE_LABEL,
        "--v6-2-lane-constraint-label", LANE_CONSTRAINT_LABEL,
        "--v6-2-lane-success-criteria-label", LANE_SUCCESS_CRITERIA_LABEL,
        "--v6-2-lane-non-execution-boundary-label", LANE_NON_EXECUTION_BOUNDARY_LABEL,
        "--v6-2-lane-scope-confirm-token", "BAD_TOKEN",
        "--v6-2-lane-scope-human-operator", HUMAN_OPERATOR,
    ]
    bad_token_res = subprocess.run(bad_token_cmd, capture_output=True, text=True)
    try:
        bad_token_data = json.loads(bad_token_res.stdout)
    except json.JSONDecodeError:
        ensure(False, f"Bad-token path output not valid JSON: {bad_token_res.stdout[:200]}")
    ensure(bad_token_data.get("local_lane_scope_packet_written") is False, "Bad-token path should not write")
    ensure(bad_token_data.get("station_chief_v6_2_lane_scope_created") is False, "Bad-token path should not create")

    with tempfile.TemporaryDirectory(prefix="station_chief_v6_2_write_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        write_cmd = [
            sys.executable, str(RUNTIME_PATH),
            "--write-station-chief-v6-2-post-mvp-expansion-lane-scope", str(tmp_dir),
            "--v6-2-review-packet-reference-label", V6_1_REVIEW_PACKET_REFERENCE_LABEL,
            "--v6-2-selected-expansion-lane-label", SELECTED_EXPANSION_LANE_LABEL,
            "--v6-2-lane-scope-label", LANE_SCOPE_LABEL,
            "--v6-2-lane-constraint-label", LANE_CONSTRAINT_LABEL,
            "--v6-2-lane-success-criteria-label", LANE_SUCCESS_CRITERIA_LABEL,
            "--v6-2-lane-non-execution-boundary-label", LANE_NON_EXECUTION_BOUNDARY_LABEL,
            "--v6-2-lane-scope-confirm-token", EXPECTED_TOKEN,
            "--v6-2-lane-scope-human-operator", HUMAN_OPERATOR,
        ]
        write_res = subprocess.run(write_cmd, capture_output=True, text=True)
        try:
            write_data = json.loads(write_res.stdout)
        except json.JSONDecodeError:
            ensure(False, f"Write-path output not valid JSON: {write_res.stdout[:200]}")
        ensure(write_data.get("local_lane_scope_packet_written") is True, "Write path should mark written")
        ensure(write_data.get("station_chief_v6_2_lane_scope_created") is True, "Write path should mark created")
        ensure(write_data.get("post_mvp_expansion_lane_scope_recorded") is True, "Write path should mark recorded")
        for key in [
            "selected_expansion_lane_implemented",
            "selected_expansion_lane_executed",
            "post_mvp_expansion_executed",
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
            "v6_3_created",
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
            "api_call_performed",
            "network_access_performed",
            "deployment_performed",
            "production_execution_performed",
            "full_workforce_activation_performed",
        ]:
            ensure(write_data.get(key) is False, f"Dangerous flag '{key}' must be False in write path")

        json_files = list(tmp_dir.rglob("*.json"))
        ensure(len(json_files) == 1, f"Expected exactly 1 JSON file, found {len(json_files)}: {json_files}")
        payload = json.loads(json_files[0].read_text(encoding="utf-8"))
        ensure(payload.get("runtime_version") == "6.2.0", "Payload runtime version mismatch")
        ensure(payload.get("scope_value") == "STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_RECORDED_METADATA_ONLY", "Scope value mismatch")

    ensure_doctrine()
    ensure_protected_paths()
    ensure_no_v63_files()
    ensure_wrapper_integration()

    print("STATION_CHIEF_RUNTIME_V6_2_VALIDATION_PASS")


if __name__ == "__main__":
    validate_v6_2()
