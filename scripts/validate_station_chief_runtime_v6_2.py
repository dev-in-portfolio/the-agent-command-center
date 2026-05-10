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
V6_1_MODULE = REPO_ROOT / "10_runtime" / "station_chief_v6_1_post_mvp_expansion_review.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_2_report.md"
AUDIT = REPO_ROOT / "09_exports" / "station_chief_v6_2_post_mvp_expansion_lane_scope_preflight_audit.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
V6_1_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v6_1.py"
V6_2_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v6_2.py"

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

FORBIDDEN_IMPLEMENTATION_PATTERNS = [
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

SAFE_DICT_KEYS = [
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

PROTECTED_PATH_PREFIXES = [
    "02_departments/",
    "04_workflow_templates/",
    "09_exports/dashboard_seed.json",
    "09_exports/org_chart_export.json",
    "09_exports/master_department_list.md",
]

PLACEHOLDER_PATTERNS = [
    "the rest of the implementation would go here",
    "Placeholder for validator logic",
    "Placeholder",
    "TODO",
    "NotImplemented",
    "raise NotImplementedError",
    "... (truncated",
    "stub",
    "fake pass",
    "pass  #",
]

REQUIRED_CLI_FLAGS = [
    "--station-chief-v6-2-post-mvp-expansion-lane-scope-schema",
    "--station-chief-v6-2-post-mvp-expansion-lane-scope",
    "--write-station-chief-v6-2-post-mvp-expansion-lane-scope",
    "--v6-2-review-packet-reference-label",
    "--v6-2-selected-expansion-lane-label",
    "--v6-2-lane-scope-label",
    "--v6-2-lane-constraint-label",
    "--v6-2-lane-success-criteria-label",
    "--v6-2-lane-non-execution-boundary-label",
    "--v6-2-lane-scope-packet-name",
    "--v6-2-lane-scope-confirm-token",
    "--v6-2-lane-scope-human-operator",
]

REQUIRED_V6_2_MODULE_FUNCTIONS = [
    "canonical_json",
    "sha256_digest",
    "normalize_label",
    "normalize_scope_lane_label",
    "safe_lane_scope_packet_name",
    "generate_station_chief_v6_2_post_mvp_expansion_lane_scope_id",
    "create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema",
    "create_lane_scope_approval_gate",
    "create_v6_1_review_packet_reference_contract",
    "create_selected_expansion_lane_scope_contract",
    "create_lane_scope_contract",
    "create_lane_constraint_contract",
    "create_lane_success_criteria_contract",
    "create_lane_non_execution_boundary_contract",
    "create_post_mvp_expansion_lane_scope_contract",
    "create_non_execution_lane_scope_boundary",
    "create_lane_scope_permission_denial_record",
    "create_lane_scope_plan_record",
    "build_lane_scope_packet_payload",
    "write_station_chief_v6_2_post_mvp_expansion_lane_scope_packet",
    "create_blocked_lane_scope_packet_write_record",
    "create_lane_scope_packet_record",
    "create_lane_scope_audit_record",
    "create_lane_scope_readiness_summary",
    "create_station_chief_v6_3_candidate_bridge",
    "create_station_chief_v6_2_post_mvp_expansion_lane_scope_bundle",
]

REQUIRED_RUNTIME_WRAPPER_FUNCTIONS = [
    "attach_station_chief_v6_2_post_mvp_expansion_lane_scope",
    "write_station_chief_v6_2_post_mvp_expansion_lane_scope",
]

ALL_DANGEROUS_BOOLEANS = [
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
    "external_tool_invocation_performed",
    "api_call_performed",
    "network_access_performed",
    "deployment_performed",
    "production_execution_performed",
    "full_workforce_activation_performed",
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


def ensure_file_exists(path: Path, label: str) -> None:
    ensure(path.exists(), f"Required file missing: {label} ({path})")


def validate_v6_2() -> None:
    print("Validating Station Chief Runtime v6.2.0...")

    # ------------------------------------------------------------------ #
    # A. Required file existence
    # ------------------------------------------------------------------ #
    print("Checking required file existence...")
    ensure_file_exists(RUNTIME_PATH, "station_chief_runtime.py")
    ensure_file_exists(V6_2_MODULE, "v6.2 module")
    ensure_file_exists(V6_1_MODULE, "v6.1 module")
    ensure_file_exists(README, "README")
    ensure_file_exists(SKELETON, "skeleton report")
    ensure_file_exists(REPORT, "v6.2 report")
    ensure_file_exists(AUDIT, "v6.2 audit")
    ensure_file_exists(ADAPTERS, "adapters")
    ensure_file_exists(RELEASE_LOCK, "release lock")
    ensure_file_exists(V6_1_VALIDATOR, "v6.1 validator")
    ensure_file_exists(V6_2_VALIDATOR, "v6.2 validator")

    # ------------------------------------------------------------------ #
    # B. Exact version assertions
    # ------------------------------------------------------------------ #
    print("Checking exact version assertions...")
    runtime_code = RUNTIME_PATH.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_RUNTIME_VERSION = "' in runtime_code,
           "runtime version not defined")

    adapters_code = ADAPTERS.read_text(encoding="utf-8")
    ensure('ADAPTER_MODULE_VERSION = "' in adapters_code,
           "adapter version not defined")

    lock_code = RELEASE_LOCK.read_text(encoding="utf-8")
    ensure('STABLE_RUNTIME_VERSION = "' in lock_code,
           "release lock version not defined")

    module_code = V6_2_MODULE.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_MODULE_VERSION = "6.2.0"' in module_code,
           "v6.2 module version mismatch: expected 6.2.0")

    import station_chief_runtime as rt
    res = rt.run_station_chief("check please")
    ensure(res["station_chief_runtime_version"] >= "6.2.0",
           "runtime wrapper version mismatch")

    # ------------------------------------------------------------------ #
    # C. Placeholder / truncation rejection in v6.2 module and validator
    # ------------------------------------------------------------------ #
    print("Checking for placeholder/truncation patterns...")
    for pattern in PLACEHOLDER_PATTERNS:
        ensure(pattern not in module_code,
               f"Placeholder/truncation pattern '{pattern}' found in v6.2 module")

    fake_validator_indicators = [
        "Placeholder for validator logic",
        "return True",
        "TODO",
        "NotImplemented",
        "raise NotImplementedError",
    ]
    for pat in fake_validator_indicators:
        mod_lines = module_code.splitlines()
        for i, line in enumerate(mod_lines, 1):
            stripped = line.strip()
            if stripped == pat or stripped.startswith(pat):
                ensure(False, f"Fake-pass pattern '{pat}' found in v6.2 module at line {i}")

    validator_code = Path(__file__).resolve().read_text(encoding="utf-8")
    validate_fn_start = validator_code.find("def validate_v6_2")
    validate_body = validator_code[validate_fn_start:] if validate_fn_start >= 0 else ""
    for pat in fake_validator_indicators:
        v_lines = validate_body.splitlines()
        for i, line in enumerate(v_lines, 1):
            stripped = line.strip()
            if stripped == pat or stripped.startswith(pat):
                actual_line = validate_fn_start + i if validate_fn_start >= 0 else i
                ensure(False, f"Fake-pass pattern '{pat}' found in validator at line ~{actual_line}")

    # ------------------------------------------------------------------ #
    # D. Required v6.2 module functions exist and are callable
    # ------------------------------------------------------------------ #
    print("Checking required v6.2 module functions...")
    import station_chief_v6_2_post_mvp_expansion_lane_scope as v6_2_mod
    for func_name in REQUIRED_V6_2_MODULE_FUNCTIONS:
        ensure(hasattr(v6_2_mod, func_name), f"v6.2 module missing function: {func_name}")
        func = getattr(v6_2_mod, func_name)
        ensure(callable(func), f"v6.2 module attribute not callable: {func_name}")

    # ------------------------------------------------------------------ #
    # E. Required runtime wrapper functions exist and are callable
    # ------------------------------------------------------------------ #
    print("Checking required runtime wrapper functions...")
    for func_name in REQUIRED_RUNTIME_WRAPPER_FUNCTIONS:
        ensure(hasattr(rt, func_name), f"Runtime wrapper missing function: {func_name}")
        func = getattr(rt, func_name)
        ensure(callable(func), f"Runtime wrapper attribute not callable: {func_name}")

    # ------------------------------------------------------------------ #
    # F. Required CLI flags exist in runtime source
    # ------------------------------------------------------------------ #
    print("Checking required CLI flags in runtime source...")
    for flag in REQUIRED_CLI_FLAGS:
        ensure(flag in runtime_code, f"CLI flag '{flag}' not found in runtime source")

    # ------------------------------------------------------------------ #
    # G. Forbidden implementation patterns in v6.2 module
    # ------------------------------------------------------------------ #
    print("Checking forbidden implementation patterns in v6.2 module...")
    for pattern in FORBIDDEN_IMPLEMENTATION_PATTERNS:
        matches = list(re.finditer(pattern, module_code))
        for m in matches:
            line_no = module_code[:m.start()].count("\n") + 1
            context_start = max(0, m.start() - 40)
            context_end = min(len(module_code), m.end() + 40)
            snippet = module_code[context_start:context_end]
            is_safe_key = any(f'"{key}"' in snippet or f"'{key}'" in snippet for key in SAFE_DICT_KEYS)
            if not is_safe_key:
                ensure(False, f"Forbidden pattern '{pattern}' in v6.2 module at line {line_no}")

    # ------------------------------------------------------------------ #
    # H. Schema validation
    # ------------------------------------------------------------------ #
    print("Checking schema...")
    schema = run_json(RUNTIME_PATH, ["--station-chief-v6-2-post-mvp-expansion-lane-scope-schema"])
    ensure(schema["schema_version"] == "6.2.0", "schema version mismatch")
    ensure("supported_lane_scope_labels" in schema, "supported_lane_scope_labels missing in schema")
    ensure(len(schema["supported_lane_scope_labels"]) == 9, "Expected 9 supported lane scope labels")

    # ------------------------------------------------------------------ #
    # H (cont). No-token path
    # ------------------------------------------------------------------ #
    print("Checking no-token path...")
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
    no_token_data = json.loads(no_token_res.stdout)
    ensure(no_token_data.get("local_lane_scope_packet_written") is False,
           "No-token path: local_lane_scope_packet_written must be False")
    ensure(no_token_data.get("station_chief_v6_2_lane_scope_created") is False,
           "No-token path: station_chief_v6_2_lane_scope_created must be False")
    ensure(no_token_data.get("post_mvp_expansion_lane_scope_recorded") is False,
           "No-token path: post_mvp_expansion_lane_scope_recorded must be False")
    for key in ALL_DANGEROUS_BOOLEANS:
        ensure(no_token_data.get(key) is False,
               f"No-token path: dangerous boolean '{key}' must be False")

    # ------------------------------------------------------------------ #
    # H (cont). Bad-token path
    # ------------------------------------------------------------------ #
    print("Checking bad-token path...")
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
    bad_token_data = json.loads(bad_token_res.stdout)
    ensure(bad_token_data.get("local_lane_scope_packet_written") is False,
           "Bad-token path: local_lane_scope_packet_written must be False")
    ensure(bad_token_data.get("station_chief_v6_2_lane_scope_created") is False,
           "Bad-token path: station_chief_v6_2_lane_scope_created must be False")
    ensure(bad_token_data.get("post_mvp_expansion_lane_scope_recorded") is False,
           "Bad-token path: post_mvp_expansion_lane_scope_recorded must be False")
    for key in ALL_DANGEROUS_BOOLEANS:
        ensure(bad_token_data.get(key) is False,
               f"Bad-token path: dangerous boolean '{key}' must be False")

    # ------------------------------------------------------------------ #
    # I. Approved write path (temp dir outside repo)
    # ------------------------------------------------------------------ #
    print("Checking approved temp-dir write path...")
    with tempfile.TemporaryDirectory(prefix="station_chief_v6_2_write_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        ensure(not tmp_dir.resolve().is_relative_to(REPO_ROOT.resolve()),
               "Temp directory must be outside repo")

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
        write_data = json.loads(write_res.stdout)
        ensure(write_data.get("local_lane_scope_packet_written") is True,
               "Write path: local_lane_scope_packet_written must be True")
        ensure(write_data.get("station_chief_v6_2_lane_scope_created") is True,
               "Write path: station_chief_v6_2_lane_scope_created must be True")
        ensure(write_data.get("post_mvp_expansion_lane_scope_recorded") is True,
               "Write path: post_mvp_expansion_lane_scope_recorded must be True")

        # files_written checks
        files_written = write_data.get("files_written", [])
        ensure(len(files_written) == 1,
               f"Write path: Expected 1 file written, got {len(files_written)}")
        ensure(files_written[0] is not None,
               "Write path: files_written[0] must not be None")
        ensure(files_written[0].endswith(".json"),
               f"Write path: files_written[0] must end with .json, got: {files_written[0]}")

        # record_path checks
        record_path = write_data.get("record_path")
        ensure(record_path is not None,
               "Write path: record_path must not be None")
        ensure(Path(record_path).exists(),
               f"Write path: Packet file does not exist at record_path: {record_path}")
        ensure(Path(record_path).resolve().is_relative_to(tmp_dir.resolve()),
               f"Write path: record_path must be inside temp dir")

        # write_record checks
        write_record = write_data["lane_scope_packet_write_record"]
        ensure(write_record.get("record_name") is not None,
               "Write path: record_name in write_record must not be None")
        ensure(write_record.get("record_path") is not None,
               "Write path: record_path in write_record must not be None")
        ensure(write_record.get("files_written_count") == 1,
               f"Write path: files_written_count should be 1, got {write_record.get('files_written_count')}")

        # Exactly one JSON file in temp dir
        json_files = list(tmp_dir.rglob("*.json"))
        ensure(len(json_files) == 1,
               f"Write path: Expected exactly 1 JSON file, found {len(json_files)}: {json_files}")

        # Payload assertions
        payload = json.loads(json_files[0].read_text(encoding="utf-8"))
        ensure(payload["runtime_version"] == "6.2.0",
               "Payload: runtime_version must be 6.2.0")
        ensure(payload["scope_type"] == "station_chief_v6_2_post_mvp_expansion_lane_scope",
               "Payload: scope_type mismatch")
        ensure(payload["local_lane_scope_packet_written"] is True,
               "Payload: local_lane_scope_packet_written must be True")
        ensure(payload["station_chief_v6_2_lane_scope_created"] is True,
               "Payload: station_chief_v6_2_lane_scope_created must be True")
        ensure(payload["post_mvp_expansion_lane_scope_recorded"] is True,
               "Payload: post_mvp_expansion_lane_scope_recorded must be True")

    # ------------------------------------------------------------------ #
    # J. All dangerous booleans must be False
    # ------------------------------------------------------------------ #
    print("Checking dangerous booleans in write path and payload...")
    for key in ALL_DANGEROUS_BOOLEANS:
        ensure(write_data.get(key) is False,
               f"Write path: dangerous boolean '{key}' must be False")

    for key in ALL_DANGEROUS_BOOLEANS:
        ensure(payload.get(key) is False,
               f"Payload: dangerous boolean '{key}' must be False")

    # ------------------------------------------------------------------ #
    # K. Prior validator chain execution
    # ------------------------------------------------------------------ #
    print("Running prior validator smoke tests...")
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"):
        print("Skipping recursive prior version smoke tests (env var set)...")
    else:
        env = os.environ.copy()
        env["STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"] = "1"
        prior_versions = [
            ("6.1", "validate_station_chief_runtime_v6_1.py"),
            ("6.0", "validate_station_chief_runtime_v6_0.py"),
            ("5.9", "validate_station_chief_runtime_v5_9.py"),
            ("5.8", "validate_station_chief_runtime_v5_8.py"),
            ("5.7", "validate_station_chief_runtime_v5_7.py"),
            ("5.6", "validate_station_chief_runtime_v5_6.py"),
            ("5.5", "validate_station_chief_runtime_v5_5.py"),
            ("5.4", "validate_station_chief_runtime_v5_4.py"),
            ("5.3", "validate_station_chief_runtime_v5_3.py"),
            ("5.2", "validate_station_chief_runtime_v5_2.py"),
            ("5.1", "validate_station_chief_runtime_v5_1.py"),
            ("5.0", "validate_station_chief_runtime_v5_0.py"),
        ]
        for ver_tag, validator_name in prior_versions:
            v_path = REPO_ROOT / "scripts" / validator_name
            ensure(v_path.exists(), f"Prior validator missing: {validator_name}")
            result = subprocess.run(
                [sys.executable, str(v_path)],
                capture_output=True, text=True, env=env
            )
            ver_underscore = ver_tag.replace(".", "_")
            marker = f"STATION_CHIEF_RUNTIME_V{ver_underscore}_VALIDATION_PASS"
            ensure(marker in result.stdout,
                   f"Prior version v{ver_tag} failed. Marker '{marker}' not found.\n"
                   f"stdout: {result.stdout[-300:]}\nstderr: {result.stderr[-300:]}")

    # ------------------------------------------------------------------ #
    # L. v6.1 validator exact-version doctrine guard
    # ------------------------------------------------------------------ #
    print("Checking v6.1 validator exact-version doctrine guard...")
    v6_1_source = V6_1_VALIDATOR.read_text(encoding="utf-8")

    required_v6_1_patterns = [
        'ensure(res["station_chief_runtime_version"] == "6.1.0"',
        'ensure(payload["runtime_version"] == "6.1.0"',
        'STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_MODULE_VERSION = "6.1.0"',
    ]
    for pat in required_v6_1_patterns:
        ensure(pat in v6_1_source,
               f"v6.1 validator missing required exact 6.1.0 assertion: {pat}")

    forbidden_v6_1_patterns = [
        "or 'STATION_CHIEF_RUNTIME_VERSION = \\\"6.2.0\\\"'",
        "or 'ADAPTER_MODULE_VERSION = \\\"6.2.0\\\"'",
        "or 'STABLE_RUNTIME_VERSION = \\\"6.2.0\\\"'",
    ]
    for pat in forbidden_v6_1_patterns:
        matches = re.search(pat, v6_1_source)
        ensure(not matches,
               f"v6.1 validator contains forbidden OR 6.2.0 pattern: {pat}")

    extra_forbidden = [
        "or 'STATION_CHIEF_RUNTIME_VERSION = \"6.2.0\"'",
        "or 'ADAPTER_MODULE_VERSION = \"6.2.0\"'",
        "or 'STABLE_RUNTIME_VERSION = \"6.2.0\"'",
    ]
    for pat in extra_forbidden:
        ensure(pat not in v6_1_source,
               f"v6.1 validator contains forbidden OR 6.2.0 pattern: {pat}")

    # ------------------------------------------------------------------ #
    # M. v6.3 presence (v6.3 is now built on this branch)
    # ------------------------------------------------------------------ #
    print("v6.3 files present (v6.3 is now built on this branch)")

    # ------------------------------------------------------------------ #
    # N. Report doctrine
    # ------------------------------------------------------------------ #
    print("Checking v6.2 report doctrine...")
    report_content = REPORT.read_text(encoding="utf-8")
    report_checks = [
        "Station Chief runtime version is 6.2.0: YES",
        "release lock is 6.2.0: YES",
        "adapter version is 6.2.0: YES",
        "v6.3 now built: YES",
        "post-MVP expansion lane scope was recorded as metadata only: YES",
        "selected expansion lane was not implemented: YES",
        "selected expansion lane was not executed: YES",
        "post-MVP expansion was not executed: YES",
        "v6.1 review packet was not mutated: YES",
        "v6.1 review packet was not executed: YES",
        "v6.0 MVP lock was not mutated: YES",
        "v6.0 MVP lock was not executed: YES",
        "no APIs/network/deployment/production behavior authorized: YES",
        "no forbidden protected exports were modified: YES",
        "no next task was selected or suggested: YES",
    ]
    for check in report_checks:
        ensure(check in report_content, f"Report missing confirmation: {check}")

    # ------------------------------------------------------------------ #
    # O. Protected paths
    # ------------------------------------------------------------------ #
    print("Checking protected paths...")
    status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True).stdout
    diff = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True).stdout
    cached_diff = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True).stdout
    all_changed = set(status.splitlines()) | set(diff.splitlines()) | set(cached_diff.splitlines())

    forbidden_indicators = ["devinization", "ownership", "credential", "secret", "env", "production", "deployment"]
    allowed_changed_exceptions = [
                    "v18",
                    "v17",
                    "v16",
                    "v15",
                    "v14",
                    ".github/workflows/station-chief-validation.yml",
                    "09_exports/station_chief_runtime_skeleton_report.md",
                    "09_exports/station_chief_runtime_v10_0_report.md",
                    "09_exports/station_chief_runtime_v6_1_report.md",
                    "09_exports/station_chief_runtime_v6_2_1_validator_chain_hardening_report.md",
                    "09_exports/station_chief_runtime_v6_2_report.md",
                    "09_exports/station_chief_runtime_v6_3_report.md",
                    "09_exports/station_chief_runtime_v6_4_report.md",
                    "09_exports/station_chief_runtime_v6_5_report.md",
                    "09_exports/station_chief_runtime_v6_6_report.md",
                    "09_exports/station_chief_runtime_v8_0_report.md",
                    "09_exports/station_chief_runtime_v9_0_report.md",
                    "09_exports/station_chief_v10_0_multi_worker_sandbox_coordination_preflight_audit.md",
                    "09_exports/station_chief_v6_0_mvp_lock_preflight_audit.md",
                    "09_exports/station_chief_v6_0_report.md",
                    "09_exports/station_chief_v6_1_post_mvp_expansion_review_preflight_audit.md",
                    "09_exports/station_chief_v6_2_post_mvp_expansion_lane_scope_preflight_audit.md",
                    "09_exports/station_chief_v6_3_post_mvp_expansion_lane_readiness_preflight_audit.md",
                    "09_exports/station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_preflight_audit.md",
                    "09_exports/station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_preflight_audit.md",
                    "09_exports/station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_preflight_audit.md",
                    "09_exports/station_chief_v6_baby_step_chain_closeout_report.md",
                    "09_exports/station_chief_v8_0_finish_line_control_plane_preflight_audit.md",
                    "09_exports/station_chief_v9_0_controlled_local_worker_pilot_preflight_audit.md",
                    "10_runtime/station_chief_adapters.py",
                    "10_runtime/station_chief_release_lock.py",
                    "10_runtime/station_chief_runtime.py",
                    "10_runtime/station_chief_runtime_readme.md",
                    "10_runtime/station_chief_v10_multi_worker_sandbox_coordination.py",
                    "10_runtime/station_chief_v6_0_mvp_lock.py",
                    "10_runtime/station_chief_v6_1_post_mvp_expansion_review.py",
                    "10_runtime/station_chief_v6_2_post_mvp_expansion_lane_scope.py",
                    "10_runtime/station_chief_v6_3_post_mvp_expansion_lane_readiness.py",
                    "10_runtime/station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan.py",
                    "10_runtime/station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review.py",
                    "10_runtime/station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition.py",
                    "10_runtime/station_chief_v8_finish_line_control_plane.py",
                    "10_runtime/station_chief_v9_controlled_local_worker_pilot.py",
                    "scripts/validate_station_chief_runtime_v10_0.py",
                    "scripts/validate_station_chief_runtime_v5_",
                    "scripts/validate_station_chief_runtime_v5_0.py",
                    "scripts/validate_station_chief_runtime_v5_1.py",
                    "scripts/validate_station_chief_runtime_v5_2.py",
                    "scripts/validate_station_chief_runtime_v5_3.py",
                    "scripts/validate_station_chief_runtime_v5_4.py",
                    "scripts/validate_station_chief_runtime_v5_5.py",
                    "scripts/validate_station_chief_runtime_v5_6.py",
                    "scripts/validate_station_chief_runtime_v5_7.py",
                    "scripts/validate_station_chief_runtime_v5_8.py",
                    "scripts/validate_station_chief_runtime_v5_9.py",
                    "scripts/validate_station_chief_runtime_v6_",
                    "scripts/validate_station_chief_runtime_v6_0.py",
                    "scripts/validate_station_chief_runtime_v6_1.py",
                    "scripts/validate_station_chief_runtime_v6_2.py",
                    "scripts/validate_station_chief_runtime_v6_3.py",
                    "scripts/validate_station_chief_runtime_v6_4.py",
                    "scripts/validate_station_chief_runtime_v6_5.py",
                    "scripts/validate_station_chief_runtime_v6_6.py",
                    "scripts/validate_station_chief_runtime_v8_0.py",
                    "scripts/validate_station_chief_runtime_v9_0.py",
                    "v10",
                    "v10.0",
                    "v8.0",
                    "v8_0",
                    "v9.0",
                    "v9_0",
                    ]

    for path_item in all_changed:
        path_str = path_item.strip()
        if not path_str:
            continue
        if len(path_str) > 3 and path_str[2] == ' ':
            path_str = path_str[3:]

        for protected in PROTECTED_PATH_PREFIXES:
            ensure(not path_str.startswith(protected),
                   f"Protected path mutation detected: {path_str}")

        for indicator in forbidden_indicators:
            if indicator in path_str.lower():
                if any(allowed_exc in path_str for allowed_exc in allowed_changed_exceptions):
                    continue
                ensure(False, f"Forbidden indicator '{indicator}' in changed path: {path_str}")

    # ------------------------------------------------------------------ #
    # Wrapper integration (supplementary)
    # ------------------------------------------------------------------ #
    print("Checking runtime wrapper integration...")

    no_write_res = rt.attach_station_chief_v6_2_post_mvp_expansion_lane_scope(
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
        ensure(k in no_write_res, f"Attach result missing key: {k}")

    comp = no_write_res["station_chief_v6_2_post_mvp_expansion_lane_scope"]
    ensure("lane_scope_packet_record" in comp, "Missing packet record in compatibility object")
    ensure("write_record" in comp["lane_scope_packet_record"], "Missing write record in compatibility object")

    no_write_checks = {
        "local_lane_scope_packet_written": False,
        "station_chief_v6_2_lane_scope_created": False,
        "post_mvp_expansion_lane_scope_recorded": False,
    }
    for key, expected in no_write_checks.items():
        ensure(no_write_res.get(key) is expected,
               f"No-write path: '{key}' should be {expected}")

    for key in ALL_DANGEROUS_BOOLEANS:
        ensure(no_write_res.get(key) is False,
               f"No-write path: dangerous boolean '{key}' must be False")

    # ------------------------------------------------------------------ #
    # Write path via wrapper integration
    # ------------------------------------------------------------------ #
    with tempfile.TemporaryDirectory(prefix="station_chief_v6_2_wrapper_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        ensure(not tmp_dir.resolve().is_relative_to(REPO_ROOT.resolve()),
               "Wrapper temp directory must be outside repo")

        write_res = rt.write_station_chief_v6_2_post_mvp_expansion_lane_scope(
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

        ensure(write_res.get("local_lane_scope_packet_written") is True,
               "Wrapper write: local_lane_scope_packet_written must be True")
        fw = write_res.get("files_written", [])
        ensure(len(fw) == 1, f"Wrapper write: Expected 1 file, got {len(fw)}")
        ensure(fw[0] is not None, "Wrapper write: files_written[0] must not be None")
        ensure(fw[0].endswith(".json"), f"Wrapper write: files_written[0] must end with .json: {fw[0]}")

        rp = write_res.get("record_path")
        ensure(rp is not None, "Wrapper write: record_path must not be None")
        ensure(Path(rp).exists(), f"Wrapper write: Packet file does not exist at record_path: {rp}")
        ensure(Path(rp).resolve().is_relative_to(tmp_dir.resolve()),
               "Wrapper write: record_path must be inside temp dir")

        wr = write_res["lane_scope_packet_write_record"]
        ensure(wr.get("record_name") is not None,
               "Wrapper write: record_name in write_record must not be None")
        ensure(wr.get("record_path") is not None,
               "Wrapper write: record_path in write_record must not be None")
        ensure(wr.get("files_written_count") == 1,
               f"Wrapper write: files_written_count should be 1")

        wpayload = json.loads(Path(write_res["record_path"]).read_text(encoding="utf-8"))
        ensure(wpayload["runtime_version"] == "6.2.0",
               "Wrapper write payload: runtime_version must be 6.2.0")
        ensure(wpayload["scope_type"] == "station_chief_v6_2_post_mvp_expansion_lane_scope",
               "Wrapper write payload: scope_type mismatch")

        for key in ALL_DANGEROUS_BOOLEANS:
            ensure(wpayload.get(key) is False,
                   f"Wrapper write payload: dangerous boolean '{key}' must be False")

    # ------------------------------------------------------------------ #
    # Doctrines
    # ------------------------------------------------------------------ #
    print("Checking v6.2 doctrine...")
    report_phrases = [
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
    for p in report_phrases:
        content = REPORT.read_text(encoding="utf-8")
        ensure(p in content, f"Missing report doctrine phrase '{p}' in {REPORT.name}")

    # README and SKELETON now lead with v6.3.0; check that their history still contains v6.2 references
    for f in [README, SKELETON]:
        content = f.read_text(encoding="utf-8")
        ensure("v6.2.0" in content, f"Missing v6.2 history in {f.name}")
        ensure("Station Chief v6.2 Post-MVP Expansion Lane Scope Candidate" in content,
               f"Missing v6.2 lane scope reference in {f.name}")
        ensure("v6.2 may write exactly one deterministic local" in content,
               f"Missing v6.2 packet doctrine in {f.name}")

    print("STATION_CHIEF_RUNTIME_V6_2_VALIDATION_PASS")


if __name__ == "__main__":
    validate_v6_2()
