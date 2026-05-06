#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import runpy
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V4_5_MODULE = REPO_ROOT / "10_runtime" / "station_chief_task_assignment_audit_closeout_candidate.py"
V4_4_MODULE = REPO_ROOT / "10_runtime" / "station_chief_permissioned_worker_task_assignment_candidate.py"
V4_3_MODULE = REPO_ROOT / "10_runtime" / "station_chief_limited_live_worker_activation_candidate.py"
V4_2_MODULE = REPO_ROOT / "10_runtime" / "station_chief_supervised_rollback_cleanup_candidate.py"
V4_1_MODULE = REPO_ROOT / "10_runtime" / "station_chief_post_action_verification_and_audit_review.py"
V4_0_MODULE = REPO_ROOT / "10_runtime" / "station_chief_first_tiny_real_world_supervised_execution_candidate.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v4_5_report.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_7.py"

WRAPPER_FILES = [
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_skeleton.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v2_8.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v2_9.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_0.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_1.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_2.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_3.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_4.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_5.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_6.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_7.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_8.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_9.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_0.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_1.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_2.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_3.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_4.py",
]

EXPECTED_V4_0_TOKEN = "YES_I_APPROVE_FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE"
EXPECTED_V4_1_TOKEN = "YES_I_APPROVE_POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW"
EXPECTED_V4_2_TOKEN = "YES_I_APPROVE_SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE"
EXPECTED_V4_3_TOKEN = "YES_I_APPROVE_LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE"
EXPECTED_V4_4_TOKEN = "YES_I_APPROVE_PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE"
EXPECTED_V4_5_TOKEN = "YES_I_APPROVE_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE"
HUMAN_OPERATOR = "Devin O’Rourke"
WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
TASK_LABEL = "station-chief-sandbox-observation-task"
WORKER_RECORD_NAME = "permissioned_worker_task_assignment_candidate_record.json"
CLOSEOUT_RECORD_NAME = "task_assignment_audit_closeout_candidate_record.json"

FORBIDDEN_PATTERNS = [
    "import requests",
    "from requests",
    "urllib.request",
    "import urllib.request",
    "import socket",
    "from socket",
    "socket.socket(",
    "subprocess.run",
    "subprocess.Popen",
    "import subprocess",
    "os.system",
    "eval(",
    "exec(",
    "compile(",
    "__import__(",
    "os.getenv",
    "os.environ",
    "getenv(",
    "environ[",
    "open(",
    "gh api",
    "git push",
    "create_deployment",
    "create_commit",
    "update_ref",
    "threading",
    "multiprocessing",
    "kill(",
    "terminate(",
    "pip install",
    "npm install",
    "worker.start",
    "queue.put",
    "task.execute",
]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_script(path: Path) -> dict:
    old_sys_path = sys.path[:]
    sys.path.insert(0, str(REPO_ROOT / "10_runtime"))
    sys.path.insert(0, str(REPO_ROOT))
    try:
        return runpy.run_path(str(path), run_name="__validator__")
    finally:
        sys.path[:] = old_sys_path


def run_script(path: Path, argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    old_argv = sys.argv[:]
    old_sys_path = sys.path[:]
    sys.argv = [str(path), *argv]
    sys.path.insert(0, str(REPO_ROOT / "10_runtime"))
    sys.path.insert(0, str(REPO_ROOT))
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                runpy.run_path(str(path), run_name="__main__")
                code = 0
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 0
    finally:
        sys.argv = old_argv
        sys.path[:] = old_sys_path
    return code, stdout.getvalue(), stderr.getvalue()


def run_json(path: Path, argv: list[str]) -> dict:
    code, stdout, stderr = run_script(path, argv)
    ensure(code == 0, f"command failed: {path.name} {' '.join(argv)}\nstdout:\n{stdout}\nstderr:\n{stderr}")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"invalid json from {path.name} {' '.join(argv)}: {exc}\nstdout:\n{stdout}\nstderr:\n{stderr}"
        ) from exc


def ensure_required_files() -> None:
    for path in [
        RUNTIME,
        V4_5_MODULE,
        V4_4_MODULE,
        V4_3_MODULE,
        V4_2_MODULE,
        V4_1_MODULE,
        V4_0_MODULE,
        README,
        SKELETON,
        REPORT,
        ADAPTERS,
        RELEASE_LOCK,
    ]:
        ensure(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}")


def ensure_no_forbidden_patterns() -> None:
    for path in [V4_5_MODULE, ADAPTERS, RELEASE_LOCK]:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            ensure(pattern not in text, f"forbidden pattern found in {path.relative_to(REPO_ROOT)}: {pattern}")
        for whole_word in [
            r"\bworker\.start\b",
            r"\bdaemon\b",
            r"\bscheduler\b",
            r"\benqueue\b",
            r"\bqueue\.put\b",
            r"\btask\.execute\b",
            r"\bexecute_task\b",
        ]:
            ensure(re.search(whole_word, text) is None, f"forbidden implementation pattern found in {path.relative_to(REPO_ROOT)}: {whole_word}")


def ensure_module_exports() -> None:
    module = load_script(V4_5_MODULE)
    for name in [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_closeout_record_name",
        "generate_task_assignment_audit_closeout_candidate_id",
        "create_task_assignment_audit_closeout_candidate_schema",
        "create_task_assignment_audit_closeout_candidate_approval_gate",
        "create_v4_4_task_assignment_record_reference_contract",
        "create_task_assignment_record_integrity_verification",
        "create_task_assignment_record_path_containment_review",
        "create_task_assignment_safety_boolean_review",
        "create_non_execution_closeout_boundary",
        "create_operator_closeout_acknowledgement",
        "create_task_assignment_closeout_audit_record",
        "create_task_assignment_closeout_ledger",
        "create_task_assignment_closeout_readiness_summary",
        "create_non_executing_task_queue_preview_candidate_bridge",
        "build_task_assignment_audit_closeout_record_payload",
        "write_task_assignment_audit_closeout_record",
        "create_blocked_closeout_write_record",
        "create_task_assignment_audit_closeout_candidate_bundle",
    ]:
        ensure(name in module and callable(module[name]), f"missing v4.5 module export: {name}")


def ensure_versions() -> None:
    runtime = load_script(RUNTIME)
    release_lock = load_script(RELEASE_LOCK)
    adapters = load_script(ADAPTERS)
    ensure(runtime["STATION_CHIEF_RUNTIME_VERSION"] == "4.5.0", "runtime version mismatch")
    ensure(runtime["generate_run_id"]("check please").startswith("station-chief-v4-5-"), "run id prefix mismatch")
    ensure(runtime["run_station_chief"]("check please")["runtime_status"] == "task_assignment_audit_closeout_candidate", "runtime status mismatch")
    ensure(release_lock["RELEASE_LOCK_MODULE_VERSION"] == "4.5.0", "release lock module version mismatch")
    ensure(release_lock["STABLE_RUNTIME_VERSION"] == "4.5.0", "release lock version mismatch")
    ensure(adapters["ADAPTER_MODULE_VERSION"] == "4.5.0", "adapter module version mismatch")
    noop = adapters["SUPPORTED_ADAPTERS"]["noop"]
    ensure(noop["supports_task_assignment_audit_closeout_candidate"] is True, "adapter v4.5 support mismatch")
    ensure(noop["task_assignment_audit_closeout_candidate_requires_specific_token"] is True, "adapter v4.5 token metadata mismatch")
    ensure(noop["one_local_task_assignment_closeout_record_allowed_with_v4_5_token"] is True, "adapter v4.5 record allowance mismatch")
    ensure(noop["referenced_task_assignment_record_mutation_allowed"] is False, "adapter v4.5 mutation denial mismatch")


def ensure_cli_flags() -> None:
    code, stdout, stderr = run_script(RUNTIME, ["--help"])
    ensure(code == 0, f"runtime --help failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
    for flag in [
        "--task-assignment-audit-closeout-candidate-schema",
        "--task-assignment-audit-closeout-candidate",
        "--write-task-assignment-audit-closeout-candidate",
        "--v4-closeout-label",
        "--v4-closeout-task-assignment-record-path",
        "--v4-closeout-expected-task-assignment-output-directory",
        "--v4-closeout-record-name",
        "--v4-closeout-confirm-token",
        "--v4-closeout-human-operator",
    ]:
        ensure(flag in stdout, f"missing CLI flag: {flag}")


def ensure_v40_v41_v42_v43_smoke_tests() -> None:
    v4_0_schema = run_json(RUNTIME, ["--first-tiny-real-world-supervised-execution-candidate-schema"])
    ensure(v4_0_schema["first_tiny_real_world_supervised_execution_candidate_schema_version"] == "4.0.0", "v4.0 schema version mismatch")
    ensure(v4_0_schema["required_confirmation_token"] == EXPECTED_V4_0_TOKEN, "v4.0 token mismatch")
    v4_0_dir = Path(tempfile.mkdtemp(prefix="station_chief_v4_0_", dir="/tmp"))
    v4_0_write = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--write-first-tiny-real-world-supervised-execution-candidate",
            str(v4_0_dir),
            "--v4-candidate-confirm-token",
            EXPECTED_V4_0_TOKEN,
            "--v4-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    v4_0_artifact_path = Path(v4_0_write["artifact_path"])
    ensure(v4_0_artifact_path.exists(), "v4.0 proof artifact missing")
    ensure(v4_0_artifact_path.name == "first_tiny_supervised_execution_candidate_proof.json", "v4.0 artifact name mismatch")
    ensure(v4_0_artifact_path.resolve().is_relative_to(v4_0_dir.resolve()), "v4.0 artifact escaped output directory")
    v4_0_payload = json.loads(v4_0_artifact_path.read_text(encoding="utf-8"))
    ensure(v4_0_payload["runtime_version"] == "4.0.0", "v4.0 artifact runtime version mismatch")

    v4_1_schema = run_json(RUNTIME, ["--post-action-verification-and-audit-review-schema"])
    ensure(v4_1_schema["post_action_verification_and_audit_review_schema_version"] == "4.1.0", "v4.1 schema version mismatch")
    ensure(v4_1_schema["required_confirmation_token"] == EXPECTED_V4_1_TOKEN, "v4.1 token mismatch")
    v4_1_review = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--post-action-verification-and-audit-review",
            "--v4-review-artifact-path",
            str(v4_0_artifact_path),
            "--v4-review-expected-output-directory",
            str(v4_0_dir),
            "--v4-review-confirm-token",
            EXPECTED_V4_1_TOKEN,
            "--v4-review-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    ensure(v4_1_review["artifact_integrity_verification_record"]["verification_status"] == "PASS", "v4.1 artifact integrity should pass")
    ensure(v4_1_review["safety_boolean_review"]["safety_review_status"] == "PASS", "v4.1 safety review should pass")
    ensure(v4_1_review["cleanup_instruction_review"]["cleanup_instruction_review_status"] == "PASS", "v4.1 cleanup instruction review should pass")

    v4_2_schema = run_json(RUNTIME, ["--supervised-rollback-cleanup-candidate-schema"])
    ensure(v4_2_schema["supervised_rollback_cleanup_candidate_schema_version"] == "4.2.0", "v4.2 schema version mismatch")
    ensure(v4_2_schema["required_confirmation_token"] == EXPECTED_V4_2_TOKEN, "v4.2 token mismatch")
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_2_", dir="/tmp") as v4_2_dir:
        v4_2_cleanup = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--execute-supervised-rollback-cleanup-candidate",
                v4_2_dir,
                "--v4-cleanup-artifact-path",
                str(v4_0_artifact_path),
                "--v4-cleanup-expected-output-directory",
                str(v4_0_dir),
                "--v4-cleanup-confirm-token",
                EXPECTED_V4_2_TOKEN,
                "--v4-cleanup-human-operator",
                HUMAN_OPERATOR,
                "--json",
            ],
        )
        cleanup_record = v4_2_cleanup["cleanup_execution_record"]
        ensure(cleanup_record["cleanup_execution_status"] == "LOCAL_ARTIFACT_CLEANUP_PERFORMED", "v4.2 cleanup should perform deletion")
        ensure(cleanup_record["deleted_file_count"] == 1, "v4.2 cleanup should delete exactly one file")
        ensure(cleanup_record["artifact_deleted"] is True, "v4.2 cleanup should mark artifact deleted")

    v4_3_schema = run_json(RUNTIME, ["--limited-live-worker-activation-candidate-schema"])
    ensure(v4_3_schema["limited_live_worker_activation_candidate_schema_version"] == "4.3.0", "v4.3 schema version mismatch")
    ensure(v4_3_schema["required_confirmation_token"] == EXPECTED_V4_3_TOKEN, "v4.3 token mismatch")
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_3_", dir="/tmp") as v4_3_dir:
        v4_3_write = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-limited-live-worker-activation-candidate",
                v4_3_dir,
                "--v4-worker-template-label",
                WORKER_TEMPLATE_LABEL,
                "--v4-worker-activation-confirm-token",
                EXPECTED_V4_3_TOKEN,
                "--v4-worker-activation-human-operator",
                HUMAN_OPERATOR,
                "--json",
            ],
        )
        v4_3_record_path = Path(v4_3_write["record_path"])
        ensure(v4_3_record_path.exists(), "v4.3 activation record missing")
        ensure(v4_3_record_path.name == "limited_live_worker_activation_candidate_record.json", "v4.3 activation record filename mismatch")
        v4_3_payload = json.loads(v4_3_record_path.read_text(encoding="utf-8"))
        ensure(v4_3_payload["runtime_version"] == "4.3.0", "v4.3 activation record runtime version mismatch")
        ensure(v4_3_payload["activation_type"] == "limited_local_worker_activation_record", "v4.3 activation type mismatch")
        ensure(v4_3_payload["worker_process_started"] is False, "v4.3 payload should not start a worker process")
        ensure(v4_3_payload["live_task_assignment_performed"] is False, "v4.3 payload should not assign tasks")
        ensure(v4_3_payload["live_worker_routing_performed"] is False, "v4.3 payload should not route workers")
        ensure(v4_3_payload["full_workforce_activation_performed"] is False, "v4.3 payload should not activate workforce")


def ensure_v44_smoke_tests() -> tuple[Path, str]:
    schema = run_json(RUNTIME, ["--permissioned-worker-task-assignment-candidate-schema"])
    ensure(schema["permissioned_worker_task_assignment_candidate_schema_version"] == "4.4.0", "v4.4 schema version mismatch")
    ensure(schema["required_confirmation_token"] == EXPECTED_V4_4_TOKEN, "v4.4 token mismatch")
    ensure(schema["assignment_type"] == "permissioned_local_worker_task_assignment_record", "v4.4 assignment type mismatch")
    task_dir = Path(tempfile.mkdtemp(prefix="station_chief_v4_4_task_", dir="/tmp"))

    code, stdout, stderr = run_script(
        RUNTIME,
        [
            "--command",
            "check please",
            "--permissioned-worker-task-assignment-candidate",
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    ensure(code == 0, f"v4.4 no-token candidate command failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
    no_token = json.loads(stdout)
    ensure(no_token["task_assignment_write_record"]["write_status"] == "BLOCKED", "v4.4 no-token write record should be blocked")

    bad_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--permissioned-worker-task-assignment-candidate",
            "--v4-task-assignment-confirm-token",
            "BAD_TOKEN",
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--json",
        ],
    )
    ensure(bad_token["permissioned_worker_task_assignment_candidate_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V4_4_TASK_ASSIGNMENT_APPROVAL", "v4.4 bad token should block")
    ensure(bad_token["task_assignment_write_record"]["write_status"] == "BLOCKED", "v4.4 bad token write record should block")

    valid_no_write = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--permissioned-worker-task-assignment-candidate",
            "--v4-task-assignment-confirm-token",
            EXPECTED_V4_4_TOKEN,
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--json",
        ],
    )
    ensure(valid_no_write["permissioned_worker_task_assignment_candidate_approval_gate"]["gate_status"] == "APPROVED_FOR_ONE_LOCAL_WORKER_TASK_ASSIGNMENT_RECORD", "v4.4 token should approve one record")
    ensure(valid_no_write["permissioned_worker_task_assignment_candidate_bundle"]["local_task_assignment_record_written"] is False, "v4.4 no-write path should not write record")
    ensure(valid_no_write["task_assignment_write_record"]["write_status"] == "BLOCKED", "v4.4 no-write path should block writing")

    write_result = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--write-permissioned-worker-task-assignment-candidate",
            str(task_dir),
            "--v4-task-assignment-confirm-token",
            EXPECTED_V4_4_TOKEN,
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--json",
        ],
    )
    write_record = write_result["task_assignment_write_record"]
    ensure(write_record["write_status"] == "LOCAL_WORKER_TASK_ASSIGNMENT_RECORD_WRITTEN", "v4.4 write path should write one record")
    ensure(write_record["local_task_assignment_record_written"] is True, "v4.4 write record should mark local write")
    ensure(write_result["permissioned_worker_task_assignment_candidate_bundle"]["local_task_assignment_record_written"] is True, "v4.4 bundle should report local write")
    records = list(task_dir.iterdir())
    ensure(len(records) == 1, f"expected exactly one task assignment record, found {len(records)}")
    record_path = records[0]
    ensure(record_path.name == WORKER_RECORD_NAME, "task assignment record filename mismatch")
    ensure(record_path.resolve().is_relative_to(task_dir.resolve()), "task assignment record escaped output directory")
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    ensure(payload["runtime_version"] == "4.4.0", "task assignment record runtime version mismatch")
    ensure(payload["assignment_type"] == "permissioned_local_worker_task_assignment_record", "task assignment record type mismatch")
    ensure(payload["task_executed"] is False, "task assignment record should not execute a task")
    ensure(payload["task_enqueued"] is False, "task assignment record should not enqueue a task")
    ensure(payload["worker_process_started"] is False, "task assignment record should not start a worker process")
    ensure(payload["live_task_assignment_performed"] is False, "task assignment record should not assign live tasks")
    ensure(payload["live_worker_routing_performed"] is False, "task assignment record should not route workers")
    ensure(payload["full_workforce_activation_performed"] is False, "task assignment record should not activate workforce")
    return task_dir, str(record_path)


def ensure_v45_schema_and_gates(task_record_path: Path, task_output_dir: Path) -> tuple[str, str, str]:
    schema = run_json(RUNTIME, ["--task-assignment-audit-closeout-candidate-schema"])
    ensure(schema["task_assignment_audit_closeout_candidate_schema_version"] == "4.5.0", "v4.5 schema version mismatch")
    ensure(schema["schema_status"] == "TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_LOCAL_RECORD_ONLY", "v4.5 schema status mismatch")
    ensure(schema["closeout_type"] == "local_task_assignment_audit_closeout_record", "v4.5 closeout type mismatch")
    ensure(schema["required_confirmation_token"] == EXPECTED_V4_5_TOKEN, "v4.5 token mismatch")
    ensure(schema["baseline_preserved"] is True, "v4.5 baseline invariant missing")
    ensure(schema["local_closeout_record_written"] is False, "v4.5 schema write flag should be false")

    closeout_dir = Path(tempfile.mkdtemp(prefix="station_chief_v4_5_closeout_", dir="/tmp"))
    no_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--task-assignment-audit-closeout-candidate",
            "--v4-closeout-human-operator",
            HUMAN_OPERATOR,
            "--v4-closeout-task-assignment-record-path",
            str(task_record_path),
            "--v4-closeout-expected-task-assignment-output-directory",
            str(task_output_dir),
            "--json",
        ],
    )
    ensure(no_token["task_assignment_audit_closeout_candidate_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V4_5_CLOSEOUT_APPROVAL", "v4.5 no-token path should block")
    ensure(no_token["task_assignment_closeout_write_record"]["write_status"] == "BLOCKED", "v4.5 no-token write record should block")

    bad_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--task-assignment-audit-closeout-candidate",
            "--v4-closeout-confirm-token",
            "BAD_TOKEN",
            "--v4-closeout-human-operator",
            HUMAN_OPERATOR,
            "--v4-closeout-task-assignment-record-path",
            str(task_record_path),
            "--v4-closeout-expected-task-assignment-output-directory",
            str(task_output_dir),
            "--json",
        ],
    )
    ensure(bad_token["task_assignment_audit_closeout_candidate_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V4_5_CLOSEOUT_APPROVAL", "v4.5 bad token should block")
    ensure(bad_token["task_assignment_closeout_write_record"]["write_status"] == "BLOCKED", "v4.5 bad token write record should block")

    valid_no_write = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--task-assignment-audit-closeout-candidate",
            "--v4-closeout-confirm-token",
            EXPECTED_V4_5_TOKEN,
            "--v4-closeout-human-operator",
            HUMAN_OPERATOR,
            "--v4-closeout-task-assignment-record-path",
            str(task_record_path),
            "--v4-closeout-expected-task-assignment-output-directory",
            str(task_output_dir),
            "--json",
        ],
    )
    ensure(valid_no_write["task_assignment_audit_closeout_candidate_approval_gate"]["gate_status"] == "APPROVED_FOR_ONE_LOCAL_TASK_ASSIGNMENT_CLOSEOUT_RECORD", "v4.5 valid token should approve one closeout record")
    ensure(valid_no_write["task_assignment_record_integrity_verification"]["verification_status"] == "PASS", "v4.5 integrity verification should pass")
    ensure(valid_no_write["task_assignment_record_path_containment_review"]["containment_status"] == "PASS", "v4.5 containment review should pass")
    ensure(valid_no_write["operator_closeout_acknowledgement"]["acknowledgement_status"] == "PASS", "v4.5 operator acknowledgement should pass")
    ensure(valid_no_write["task_assignment_closeout_ledger"]["ledger_status"] == "PASS", "v4.5 ledger should pass")
    ensure(valid_no_write["task_assignment_closeout_readiness_summary"]["readiness_status"] == "READY_FOR_NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE", "v4.5 readiness should be ready")
    ensure(valid_no_write["task_assignment_closeout_write_record"]["write_status"] == "BLOCKED", "v4.5 valid no-write path should not write")
    ensure(len(list(closeout_dir.iterdir())) == 0, "v4.5 valid no-write path should not create files")

    task_record_digest_before = hashlib.sha256(task_record_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    write_result = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--write-task-assignment-audit-closeout-candidate",
            str(closeout_dir),
            "--v4-closeout-confirm-token",
            EXPECTED_V4_5_TOKEN,
            "--v4-closeout-human-operator",
            HUMAN_OPERATOR,
            "--v4-closeout-task-assignment-record-path",
            str(task_record_path),
            "--v4-closeout-expected-task-assignment-output-directory",
            str(task_output_dir),
            "--json",
        ],
    )
    write_record = write_result["task_assignment_closeout_write_record"]
    ensure(write_record["write_status"] == "LOCAL_TASK_ASSIGNMENT_AUDIT_CLOSEOUT_RECORD_WRITTEN", "v4.5 write path should write one closeout record")
    ensure(write_record["local_closeout_record_written"] is True, "v4.5 write record should mark local write")
    ensure(write_result["task_assignment_audit_closeout_candidate_bundle"]["local_closeout_record_written"] is True, "v4.5 bundle should report local write")
    records = list(closeout_dir.iterdir())
    ensure(len(records) == 1, f"expected exactly one closeout record, found {len(records)}")
    record_path = records[0]
    ensure(record_path.name == CLOSEOUT_RECORD_NAME, "closeout record filename mismatch")
    ensure(record_path.resolve().is_relative_to(closeout_dir.resolve()), "closeout record escaped output directory")
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    ensure(payload["runtime_version"] == "4.5.0", "closeout record runtime version mismatch")
    ensure(payload["closeout_type"] == "local_task_assignment_audit_closeout_record", "closeout record type mismatch")
    ensure(payload["task_executed"] is False, "closeout record should not execute a task")
    ensure(payload["task_enqueued"] is False, "closeout record should not enqueue a task")
    ensure(payload["worker_process_started"] is False, "closeout record should not start a worker process")
    ensure(payload["live_task_assignment_performed"] is False, "closeout record should not assign live tasks")
    ensure(payload["live_worker_routing_performed"] is False, "closeout record should not route workers")
    ensure(payload["full_workforce_activation_performed"] is False, "closeout record should not activate workforce")
    ensure(payload["referenced_task_assignment_record_mutated"] is False, "closeout record should not mutate referenced record")
    ensure(write_record["record_path"] == str(record_path), "closeout write record path mismatch")
    ensure(hashlib.sha256(task_record_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest() == task_record_digest_before, "referenced v4.4 task assignment record was mutated")
    closeout_record_digest = hashlib.sha256(record_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    return str(task_record_path), str(record_path), closeout_record_digest


def ensure_v45_artifact_writer(task_record_path: str) -> None:
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_5_run_", dir="/tmp") as run_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_5_registry_", dir="/tmp") as reg_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_5_closeout_", dir="/tmp") as closeout_dir:
        bundle = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-artifacts",
                run_dir,
                "--registry-dir",
                reg_dir,
                "--write-task-assignment-audit-closeout-candidate",
                closeout_dir,
                "--v4-closeout-confirm-token",
                EXPECTED_V4_5_TOKEN,
                "--v4-closeout-human-operator",
                HUMAN_OPERATOR,
                "--v4-closeout-task-assignment-record-path",
                task_record_path,
                "--v4-closeout-expected-task-assignment-output-directory",
                str(Path(task_record_path).parent),
                "--json",
            ],
        )
        summary = bundle["artifact_write_summary"]
        ensure(summary["run_id"].startswith("station-chief-v4-5-check-please-"), "artifact writer run id prefix mismatch")
        artifact_dir = Path(summary["artifact_dir"])
        registry_dir = Path(summary["registry_dir"])
        ensure(artifact_dir.exists(), "artifact directory missing")
        ensure(registry_dir.exists(), "registry directory missing")
        manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
        registry = json.loads((registry_dir / "run_registry.json").read_text(encoding="utf-8"))
        index = json.loads((registry_dir / "runtime_index.json").read_text(encoding="utf-8"))
        ensure(manifest["runtime_version"] == "4.5.0", "manifest runtime version mismatch")
        ensure(manifest["artifact_type"] == "station_chief_runtime_v4_5_artifacts", "manifest artifact type mismatch")
        ensure(registry["registry_version"] == "4.5.0", "registry version mismatch")
        ensure(index["index_version"] == "4.5.0", "index version mismatch")
        ensure((artifact_dir / "task_assignment_audit_closeout_candidate_bundle.json").exists(), "v4.5 bundle missing from artifact dir")
        ensure((artifact_dir / "task_assignment_closeout_write_record.json").exists(), "v4.5 closeout write record missing from artifact dir")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["local_closeout_record_written"] is True, "v4.5 bundle should report local write")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["task_executed"] is False, "v4.5 bundle should not execute a task")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["task_enqueued"] is False, "v4.5 bundle should not enqueue a task")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["worker_process_started"] is False, "v4.5 bundle should not start worker process")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["live_task_assignment_performed"] is False, "v4.5 bundle should not assign live tasks")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["live_worker_routing_performed"] is False, "v4.5 bundle should not route workers")
        ensure(bundle["task_assignment_audit_closeout_candidate_bundle"]["full_workforce_activation_performed"] is False, "v4.5 bundle should not activate workforce")


def ensure_docs_and_reports() -> None:
    readme = README.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    ensure("Station Chief Runtime upgraded to v4.5.0" in readme, "README missing v4.5 status")
    ensure("Task Assignment Audit Closeout Candidate" in readme, "README missing v4.5 doctrine")
    ensure("Next recommended step: build non-executing task queue preview candidate." in readme, "README missing v4.5 next step")
    ensure("Station Chief Runtime upgraded to v4.5.0" in skeleton, "skeleton report missing v4.5 status")
    ensure("Task Assignment Audit Closeout Candidate added." in skeleton, "skeleton report missing v4.5 runtime capability note")
    ensure("build non-executing task queue preview candidate" in skeleton, "skeleton report missing v4.5 next step")
    ensure("Station Chief Runtime v4.5.0 Report" in report, "v4.5 report missing header")
    ensure("Devin O’Rourke" in report, "v4.5 report missing ownership attribution")
    ensure("Build non-executing task queue preview candidate." in report, "v4.5 report missing next step")


def ensure_no_v46_files() -> None:
    for relative in [
        "10_runtime/station_chief_non_executing_task_queue_preview_candidate.py",
        "scripts/validate_station_chief_runtime_v4_7.py",
        "09_exports/station_chief_runtime_v4_6_report.md",
    ]:
        ensure(not (REPO_ROOT / relative).exists(), f"forbidden v4.6 file exists: {relative}")
    for path in REPO_ROOT.rglob("*v4_6*"):
        ensure(False, f"forbidden v4.6 path unexpectedly exists: {path.relative_to(REPO_ROOT)}")


def ensure_wrappers_delegate() -> None:
    for wrapper in WRAPPER_FILES:
        text = wrapper.read_text(encoding="utf-8")
        ensure("runpy.run_path" in text, f"wrapper missing runpy handoff: {wrapper.relative_to(REPO_ROOT)}")
        ensure("validate_station_chief_runtime_v4_5.py" in text, f"wrapper not delegated to v4.5 validator: {wrapper.relative_to(REPO_ROOT)}")


def main() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    runpy.run_path(str(TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
