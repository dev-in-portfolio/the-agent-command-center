#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import runpy
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V4_4_MODULE = REPO_ROOT / "10_runtime" / "station_chief_permissioned_worker_task_assignment_candidate.py"
V4_3_MODULE = REPO_ROOT / "10_runtime" / "station_chief_limited_live_worker_activation_candidate.py"
V4_2_MODULE = REPO_ROOT / "10_runtime" / "station_chief_supervised_rollback_cleanup_candidate.py"
V4_1_MODULE = REPO_ROOT / "10_runtime" / "station_chief_post_action_verification_and_audit_review.py"
V4_0_MODULE = REPO_ROOT / "10_runtime" / "station_chief_first_tiny_real_world_supervised_execution_candidate.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v4_4_report.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

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
]

EXPECTED_V4_0_TOKEN = "YES_I_APPROVE_FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE"
EXPECTED_V4_1_TOKEN = "YES_I_APPROVE_POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW"
EXPECTED_V4_2_TOKEN = "YES_I_APPROVE_SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE"
EXPECTED_V4_3_TOKEN = "YES_I_APPROVE_LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE"
EXPECTED_V4_4_TOKEN = "YES_I_APPROVE_PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE"
HUMAN_OPERATOR = "Devin O’Rourke"
WORKER_TEMPLATE_LABEL = "station-chief-sandbox-observer-worker-template"
TASK_LABEL = "station-chief-sandbox-observation-task"
WORKER_RECORD_NAME = "permissioned_worker_task_assignment_candidate_record.json"
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
    files_to_scan = [
        V4_4_MODULE,
        ADAPTERS,
        RELEASE_LOCK,
    ]
    for path in files_to_scan:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            ensure(pattern not in text, f"forbidden pattern found in {path.relative_to(REPO_ROOT)}: {pattern}")
        for whole_word in [
            r"\bworker\.start\b",
            r"\bstart_worker\b",
            r"\bstart_process\b",
            r"\bdaemon\b",
            r"\bscheduler\b",
            r"\benqueue\b",
            r"\bqueue\.put\b",
            r"\btask\.execute\b",
            r"\bexecute_task\b",
        ]:
            ensure(re.search(whole_word, text) is None, f"forbidden implementation pattern found in {path.relative_to(REPO_ROOT)}: {whole_word}")


def ensure_module_exports() -> None:
    module = load_script(V4_4_MODULE)
    for name in [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_task_assignment_record_name",
        "generate_permissioned_worker_task_assignment_candidate_id",
        "create_permissioned_worker_task_assignment_candidate_schema",
        "create_permissioned_worker_task_assignment_candidate_approval_gate",
        "create_worker_template_reference_contract",
        "create_task_label_reference_contract",
        "create_one_worker_one_task_assignment_scope_contract",
        "create_non_execution_task_boundary",
        "create_task_permission_denial_record",
        "create_worker_task_assignment_candidate_record",
        "create_task_assignment_audit_record",
        "create_task_assignment_ledger",
        "create_task_assignment_readiness_summary",
        "create_task_assignment_audit_closeout_candidate_bridge",
        "build_task_assignment_record_payload",
        "write_permissioned_worker_task_assignment_record",
        "create_blocked_task_assignment_write_record",
        "create_permissioned_worker_task_assignment_candidate_bundle",
    ]:
        ensure(name in module and callable(module[name]), f"missing v4.4 module export: {name}")


def ensure_versions() -> None:
    runtime = load_script(RUNTIME)
    release_lock = load_script(RELEASE_LOCK)
    adapters = load_script(ADAPTERS)
    ensure(runtime["STATION_CHIEF_RUNTIME_VERSION"] == "4.4.0", "runtime version mismatch")
    ensure(runtime["generate_run_id"]("check please").startswith("station-chief-v4-4-"), "run id prefix mismatch")
    ensure(runtime["run_station_chief"]("check please")["runtime_status"] == "permissioned_worker_task_assignment_candidate", "runtime status mismatch")
    ensure(release_lock["RELEASE_LOCK_MODULE_VERSION"] == "4.4.0", "release lock module version mismatch")
    ensure(release_lock["STABLE_RUNTIME_VERSION"] == "4.4.0", "release lock version mismatch")
    ensure(adapters["ADAPTER_MODULE_VERSION"] == "4.4.0", "adapter module version mismatch")
    noop = adapters["SUPPORTED_ADAPTERS"]["noop"]
    ensure(noop["supports_permissioned_worker_task_assignment_candidate"] is True, "adapter permissioned worker support mismatch")
    ensure(noop["one_local_worker_task_assignment_record_allowed_with_v4_4_token"] is True, "adapter v4.4 token metadata mismatch")


def ensure_cli_flags() -> None:
    code, stdout, stderr = run_script(RUNTIME, ["--help"])
    ensure(code == 0, f"runtime --help failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
    for flag in [
        "--permissioned-worker-task-assignment-candidate-schema",
        "--permissioned-worker-task-assignment-candidate",
        "--write-permissioned-worker-task-assignment-candidate",
        "--v4-task-worker-template-label",
        "--v4-task-label",
        "--v4-task-assignment-record-name",
        "--v4-task-assignment-confirm-token",
        "--v4-task-assignment-human-operator",
    ]:
        ensure(flag in stdout, f"missing CLI flag: {flag}")


def ensure_schema_and_gates() -> None:
    schema = run_json(RUNTIME, ["--permissioned-worker-task-assignment-candidate-schema"])
    ensure(schema["permissioned_worker_task_assignment_candidate_schema_version"] == "4.4.0", "schema version mismatch")
    ensure(schema["schema_status"] == "PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_LOCAL_RECORD_ONLY", "schema status mismatch")
    ensure(schema["assignment_type"] == "permissioned_local_worker_task_assignment_record", "schema assignment type mismatch")
    ensure(schema["required_confirmation_token"] == EXPECTED_V4_4_TOKEN, "schema token mismatch")
    ensure(schema["baseline_preserved"] is True, "schema baseline invariant missing")
    ensure(schema["local_task_assignment_record_written"] is False, "schema write flag should be false")
    ensure(schema["task_executed"] is False, "schema task executed flag should be false")
    ensure(schema["task_enqueued"] is False, "schema task enqueued flag should be false")
    ensure(schema["worker_process_started"] is False, "schema worker process flag should be false")
    ensure(schema["live_task_assignment_performed"] is False, "schema live task flag should be false")
    ensure(schema["live_worker_routing_performed"] is False, "schema live routing flag should be false")

    no_token = run_json(
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
    gate = no_token["permissioned_worker_task_assignment_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is False, "no-token path should block")
    ensure(gate["local_task_assignment_records_authorized"] is False, "no-token records should be blocked")
    ensure(gate["local_task_assignment_record_write_authorized"] is False, "no-token write should be blocked")
    ensure(gate["gate_status"] == "BLOCKED_PENDING_V4_4_TASK_ASSIGNMENT_APPROVAL", "no-token gate status mismatch")
    ensure(no_token["worker_task_assignment_candidate_record"]["candidate_status"] == "BLOCKED", "no-token candidate should be blocked")
    ensure(no_token["task_assignment_write_record"]["write_status"] == "BLOCKED", "no-token write should be blocked")

    bad_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--permissioned-worker-task-assignment-candidate",
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--v4-task-assignment-confirm-token",
            "BAD_TOKEN",
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    gate = bad_token["permissioned_worker_task_assignment_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is False, "bad-token path should block")
    ensure(gate["local_task_assignment_records_authorized"] is False, "bad-token records should be blocked")
    ensure(gate["local_task_assignment_record_write_authorized"] is False, "bad-token write should be blocked")
    ensure(gate["gate_status"] == "BLOCKED_PENDING_V4_4_TASK_ASSIGNMENT_APPROVAL", "bad-token gate status mismatch")

    valid_no_write = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--permissioned-worker-task-assignment-candidate",
            "--v4-task-worker-template-label",
            WORKER_TEMPLATE_LABEL,
            "--v4-task-label",
            TASK_LABEL,
            "--v4-task-assignment-confirm-token",
            EXPECTED_V4_4_TOKEN,
            "--v4-task-assignment-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    gate = valid_no_write["permissioned_worker_task_assignment_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is True, "valid token should authorize records")
    ensure(gate["local_task_assignment_records_authorized"] is True, "valid token records should be authorized")
    ensure(gate["local_task_assignment_record_write_authorized"] is False, "no output dir should block write authorization")
    ensure(gate["gate_status"] == "APPROVED_FOR_ONE_LOCAL_WORKER_TASK_ASSIGNMENT_RECORD", "valid-token gate status mismatch")
    ensure(valid_no_write["worker_task_assignment_candidate_record"]["candidate_status"] == "LOCAL_WORKER_TASK_ASSIGNMENT_CANDIDATE_RECORD_CREATED", "candidate record should be created")
    ensure(valid_no_write["task_assignment_write_record"]["write_status"] == "BLOCKED", "no-write path should block write")
    ensure(valid_no_write["local_task_assignment_record_written"] is False, "no-write path should not write")
    ensure(valid_no_write["task_executed"] is False, "candidate record should not execute a task")
    ensure(valid_no_write["task_enqueued"] is False, "candidate record should not enqueue a task")
    ensure(valid_no_write["worker_process_started"] is False, "candidate record should not start a worker process")
    ensure(valid_no_write["live_task_assignment_performed"] is False, "candidate record should not assign live tasks")
    ensure(valid_no_write["live_worker_routing_performed"] is False, "candidate record should not route workers")
    ensure(valid_no_write["full_workforce_activation_performed"] is False, "candidate record should not activate workforce")


def ensure_v40_v41_v42_v43_smoke_tests() -> None:
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_0_", dir="/tmp") as v4_0_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_1_", dir="/tmp") as v4_1_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_2_", dir="/tmp") as v4_2_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_3_", dir="/tmp") as v4_3_dir:
        v4_0_schema = run_json(RUNTIME, ["--first-tiny-real-world-supervised-execution-candidate-schema"])
        ensure(v4_0_schema["first_tiny_real_world_supervised_execution_candidate_schema_version"] == "4.0.0", "v4.0 schema version mismatch")
        ensure(v4_0_schema["required_confirmation_token"] == EXPECTED_V4_0_TOKEN, "v4.0 token mismatch")
        v4_0_write = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-first-tiny-real-world-supervised-execution-candidate",
                v4_0_dir,
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
        ensure(v4_0_artifact_path.resolve().is_relative_to(Path(v4_0_dir).resolve()), "v4.0 artifact escaped output directory")

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
                v4_0_dir,
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
                v4_0_dir,
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
        ensure(not v4_0_artifact_path.exists(), "v4.0 artifact should be deleted by v4.2 cleanup")
        ensure(Path(v4_0_dir).exists(), "v4.2 cleanup output directory should remain")
        ensure(v4_2_cleanup["cleanup_audit_record"]["audit_status"] == "PASS", "v4.2 cleanup audit should pass")
        ensure(v4_2_cleanup["cleanup_closeout_ledger"]["ledger_status"] == "PASS", "v4.2 cleanup ledger should pass")

        v4_3_schema = run_json(RUNTIME, ["--limited-live-worker-activation-candidate-schema"])
        ensure(v4_3_schema["limited_live_worker_activation_candidate_schema_version"] == "4.3.0", "v4.3 schema version mismatch")
        ensure(v4_3_schema["required_confirmation_token"] == EXPECTED_V4_3_TOKEN, "v4.3 token mismatch")
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
        ensure(v4_3_record_path.resolve().is_relative_to(Path(v4_3_dir).resolve()), "v4.3 activation record escaped output directory")
        v4_3_payload = json.loads(v4_3_record_path.read_text(encoding="utf-8"))
        ensure(v4_3_payload["runtime_version"] == "4.3.0", "v4.3 activation record runtime version mismatch")
        ensure(v4_3_payload["activation_type"] == "limited_local_worker_activation_record", "v4.3 activation type mismatch")
        ensure(v4_3_payload["worker_process_started"] is False, "v4.3 payload should not start a worker process")
        ensure(v4_3_payload["live_task_assignment_performed"] is False, "v4.3 payload should not assign tasks")
        ensure(v4_3_payload["live_worker_routing_performed"] is False, "v4.3 payload should not route workers")
        ensure(v4_3_payload["full_workforce_activation_performed"] is False, "v4.3 payload should not activate workforce")


def ensure_v44_write_path() -> None:
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_4_task_", dir="/tmp") as task_dir:
        code, stdout, stderr = run_script(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-permissioned-worker-task-assignment-candidate",
                task_dir,
                "--v4-task-worker-template-label",
                WORKER_TEMPLATE_LABEL,
                "--v4-task-label",
                TASK_LABEL,
                "--v4-task-assignment-confirm-token",
                EXPECTED_V4_4_TOKEN,
                "--v4-task-assignment-human-operator",
                HUMAN_OPERATOR,
            ],
        )
        ensure(code == 0, f"v4.4 write command failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
        records = list(Path(task_dir).iterdir())
        ensure(len(records) == 1, f"expected exactly one task assignment record, found {len(records)}")
        record_path = records[0]
        ensure(record_path.name == WORKER_RECORD_NAME, "task assignment record filename mismatch")
        ensure(record_path.resolve().is_relative_to(Path(task_dir).resolve()), "task assignment record escaped output directory")
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        ensure(payload["runtime_version"] == "4.4.0", "task assignment record runtime version mismatch")
        ensure(payload["assignment_type"] == "permissioned_local_worker_task_assignment_record", "task assignment record type mismatch")
        ensure(payload["task_executed"] is False, "task assignment record should not execute a task")
        ensure(payload["task_enqueued"] is False, "task assignment record should not enqueue a task")
        ensure(payload["worker_process_started"] is False, "task assignment record should not start a worker process")
        ensure(payload["live_task_assignment_performed"] is False, "task assignment record should not assign live tasks")
        ensure(payload["live_worker_routing_performed"] is False, "task assignment record should not route workers")
        ensure(payload["full_workforce_activation_performed"] is False, "task assignment record should not activate workforce")
        ensure(payload["safety_booleans"]["task_executed"] is False, "task assignment payload safety booleans should remain false")
        ensure(payload["safety_booleans"]["task_enqueued"] is False, "task assignment payload safety booleans should remain false")
        ensure(payload["safety_booleans"]["worker_process_started"] is False, "task assignment payload safety booleans should remain false")
        ensure(payload["safety_booleans"]["live_task_assignment_performed"] is False, "task assignment payload safety booleans should remain false")
        ensure(payload["safety_booleans"]["live_worker_routing_performed"] is False, "task assignment payload safety booleans should remain false")
        ensure(payload["safety_booleans"]["full_workforce_activation_performed"] is False, "task assignment payload safety booleans should remain false")


def ensure_v44_artifact_writer() -> None:
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_4_run_", dir="/tmp") as run_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_4_registry_", dir="/tmp") as reg_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_4_task_", dir="/tmp") as task_dir:
        bundle = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-artifacts",
                run_dir,
                "--registry-dir",
                reg_dir,
                "--write-permissioned-worker-task-assignment-candidate",
                task_dir,
                "--v4-task-worker-template-label",
                WORKER_TEMPLATE_LABEL,
                "--v4-task-label",
                TASK_LABEL,
                "--v4-task-assignment-confirm-token",
                EXPECTED_V4_4_TOKEN,
                "--v4-task-assignment-human-operator",
                HUMAN_OPERATOR,
                "--json",
            ],
        )
        summary = bundle["artifact_write_summary"]
        ensure(summary["run_id"].startswith("station-chief-v4-4-check-please-"), "artifact writer run id prefix mismatch")
        artifact_dir = Path(summary["artifact_dir"])
        registry_dir = Path(summary["registry_dir"])
        ensure(artifact_dir.exists(), "artifact directory missing")
        ensure(registry_dir.exists(), "registry directory missing")
        manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
        registry = json.loads((registry_dir / "run_registry.json").read_text(encoding="utf-8"))
        index = json.loads((registry_dir / "runtime_index.json").read_text(encoding="utf-8"))
        ensure(manifest["runtime_version"] == "4.4.0", "manifest runtime version mismatch")
        ensure(manifest["artifact_type"] == "station_chief_runtime_v4_4_artifacts", "manifest artifact type mismatch")
        ensure(registry["registry_version"] == "4.4.0", "registry version mismatch")
        ensure(index["index_version"] == "4.4.0", "index version mismatch")
        ensure((artifact_dir / "permissioned_worker_task_assignment_candidate_bundle.json").exists(), "v4.4 bundle missing from artifact dir")
        ensure((artifact_dir / "permissioned_worker_task_assignment_candidate_record.json").exists(), "v4.4 local record missing from artifact dir")
        ensure((artifact_dir / "task_assignment_write_record.json").exists(), "v4.4 write record missing from artifact dir")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["local_task_assignment_record_written"] is True, "v4.4 bundle should report local write")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["task_executed"] is False, "v4.4 bundle should not execute a task")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["task_enqueued"] is False, "v4.4 bundle should not enqueue a task")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["worker_process_started"] is False, "v4.4 bundle should not start worker process")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["live_task_assignment_performed"] is False, "v4.4 bundle should not assign live tasks")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["live_worker_routing_performed"] is False, "v4.4 bundle should not route workers")
        ensure(bundle["permissioned_worker_task_assignment_candidate_bundle"]["full_workforce_activation_performed"] is False, "v4.4 bundle should not activate workforce")


def ensure_docs_and_reports() -> None:
    readme = README.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    ensure("Station Chief Runtime v4.4.0" in readme, "README missing v4.4 header")
    ensure("Permissioned Worker Task Assignment Candidate" in readme, "README missing v4.4 doctrine")
    ensure("Next recommended step: build task assignment audit closeout candidate." in readme, "README missing v4.4 next step")
    ensure("Station Chief Runtime upgraded to v4.4.0" in skeleton, "skeleton report missing v4.4 status")
    ensure("Permissioned worker task assignment candidate added." in skeleton, "skeleton report missing v4.4 runtime capability note")
    ensure("build task assignment audit closeout candidate" in skeleton, "skeleton report missing v4.4 next step")
    ensure("Station Chief Runtime v4.4.0 Report" in report, "v4.4 report missing header")
    ensure("Devin O’Rourke" in report, "v4.4 report missing ownership attribution")
    ensure("Build task assignment audit closeout candidate." in report, "v4.4 report missing next step")


def ensure_no_v45_files() -> None:
    for relative in [
        "10_runtime/station_chief_task_assignment_audit_closeout_candidate.py",
        "scripts/validate_station_chief_runtime_v4_5.py",
        "09_exports/station_chief_runtime_v4_5_report.md",
    ]:
        ensure(not (REPO_ROOT / relative).exists(), f"forbidden v4.5 file exists: {relative}")
    for path in REPO_ROOT.rglob("*v4_5*"):
        ensure(False, f"forbidden v4.5 path unexpectedly exists: {path.relative_to(REPO_ROOT)}")


def ensure_wrappers_delegate() -> None:
    for wrapper in WRAPPER_FILES:
        text = wrapper.read_text(encoding="utf-8")
        ensure("runpy.run_path" in text, f"wrapper missing runpy handoff: {wrapper.relative_to(REPO_ROOT)}")
        ensure("validate_station_chief_runtime_v4_4.py" in text, f"wrapper not delegated to v4.4 validator: {wrapper.relative_to(REPO_ROOT)}")


def main() -> None:
    ensure_required_files()
    ensure_versions()
    ensure_cli_flags()
    ensure_module_exports()
    ensure_no_forbidden_patterns()
    ensure_schema_and_gates()
    ensure_v40_v41_v42_v43_smoke_tests()
    ensure_v44_write_path()
    ensure_v44_artifact_writer()
    ensure_docs_and_reports()
    ensure_no_v45_files()
    ensure_wrappers_delegate()
    print("PASS: Station Chief Runtime v4.4 valid.")


if __name__ == "__main__":
    main()
