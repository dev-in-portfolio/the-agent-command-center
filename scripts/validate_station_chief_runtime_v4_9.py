#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import shutil
import subprocess
import runpy
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V4_9_MODULE = REPO_ROOT / "10_runtime" / "station_chief_live_queue_orchestration_candidate_review.py"
V4_8_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_8.py"
V4_7_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_7.py"
V4_6_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_6.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v4_9_report.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

EXPECTED_V4_9_TOKEN = "YES_I_APPROVE_LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_ONLY"
HUMAN_OPERATOR = "Devin O’Rourke"
V4_8_REFERENCE_LABEL = "sandbox routing preview reference"
DEFAULT_REVIEW_RECORD_NAME = "live_queue_orchestration_candidate_review_record.json"

ALLOWED_CHANGED_PATHS = {
    "10_runtime/station_chief_live_queue_orchestration_candidate_review.py",
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_runtime_readme.md",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_release_lock.py",
    "09_exports/station_chief_runtime_skeleton_report.md",
    "09_exports/station_chief_runtime_v4_9_report.md",
    "scripts/validate_station_chief_runtime_v4_8.py",
    "scripts/validate_station_chief_runtime_v4_9.py",
}

FORBIDDEN_REGEXES = [
    r"\bimport\s+requests\b",
    r"\bfrom\s+requests\b",
    r"\burllib\.request\b",
    r"\bimport\s+urllib\.request\b",
    r"\bimport\s+socket\b",
    r"\bfrom\s+socket\b",
    r"\bsocket\.socket\s*\(",
    r"\bsubprocess\.run\s*\(",
    r"\bsubprocess\.Popen\s*\(",
    r"\bimport\s+subprocess\b",
    r"\bos\.system\s*\(",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"\b__import__\s*\(",
    r"\bos\.getenv\b",
    r"\bos\.environ\b",
    r"\bgetenv\s*\(",
    r"\benviron\[",
    r"\bopen\s*\(",
    r"\bgh api\b",
    r"\bgit push\b",
    r"\bcreate_deployment\b",
    r"\bcreate_commit\b",
    r"\bupdate_ref\b",
    r"\bthreading\b",
    r"\bmultiprocessing\b",
    r"\bqueue\.Queue\s*\(",
    r"\basyncio\b",
    r"\bkill\s*\(",
    r"\bterminate\s*\(",
    r"\bpip install\b",
    r"\bnpm install\b",
    r"\bworker\.start\b",
    r"\bstart_worker\b",
    r"\bstart_process\b",
    r"\bdaemon\b",
    r"\bscheduler\.",
    r"\benqueue\s*\(",
    r"\bdispatch\s*\(",
    r"\broute_live\b",
    r"\bexecute_task\b",
    r"\brun_task\b",
    r"\bassign_live_task\b",
    r"\borchestrate\s*\(",
    r"\borchestrate_live\b",
    r"\blive_orchestration\b",
    r"\bcreate_queue\b",
    r"\bwrite_queue\b",
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
                code = int(exc.code) if isinstance(exc.code, int) else (0 if exc.code is None else 1)
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
    for path in [RUNTIME, V4_9_MODULE, README, SKELETON, REPORT, ADAPTERS, RELEASE_LOCK]:
        ensure(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}")


def ensure_versions() -> None:
    runtime = load_script(RUNTIME)
    adapters = load_script(ADAPTERS)
    release_lock = load_script(RELEASE_LOCK)
    ensure(runtime["STATION_CHIEF_RUNTIME_VERSION"] == "4.9.0", "runtime version mismatch")
    ensure(runtime["generate_run_id"]("check please").startswith("station-chief-v4-9-"), "run id prefix mismatch")
    ensure(runtime["run_station_chief"]("check please")["runtime_status"] == "live_queue_orchestration_candidate_review", "runtime status mismatch")
    ensure(adapters["ADAPTER_MODULE_VERSION"] == "4.9.0", "adapter module version mismatch")
    noop = adapters["SUPPORTED_ADAPTERS"]["noop"]
    ensure(noop["supports_live_queue_orchestration_candidate_review"] is True, "adapter v4.9 support mismatch")
    ensure(noop["live_queue_orchestration_candidate_review_requires_specific_token"] is True, "adapter v4.9 token metadata mismatch")
    ensure(noop["one_local_orchestration_candidate_review_record_allowed_with_v4_9_token"] is True, "adapter v4.9 record allowance mismatch")
    ensure(noop["real_queue_creation_allowed"] is False, "adapter real queue creation denial mismatch")
    ensure(noop["queue_write_allowed"] is False, "adapter queue write denial mismatch")
    ensure(noop["scheduler_write_allowed"] is False, "adapter scheduler write denial mismatch")
    ensure(noop["cron_write_allowed"] is False, "adapter cron write denial mismatch")
    ensure(noop["task_enqueue_allowed"] is False, "adapter task enqueue denial mismatch")
    ensure(noop["task_execution_allowed"] is False, "adapter task execution denial mismatch")
    ensure(noop["worker_process_start_allowed"] is False, "adapter worker start denial mismatch")
    ensure(noop["live_task_assignment_allowed"] is False, "adapter live assignment denial mismatch")
    ensure(noop["live_worker_routing_allowed"] is False, "adapter live routing denial mismatch")
    ensure(noop["live_orchestration_allowed"] is False, "adapter live orchestration denial mismatch")
    ensure(noop["full_workforce_activation_allowed"] is False, "adapter workforce denial mismatch")
    ensure(noop["live_api_call_allowed"] is False, "adapter api denial mismatch")
    ensure(noop["network_access_allowed"] is False, "adapter network denial mismatch")
    ensure(noop["socket_access_allowed"] is False, "adapter socket denial mismatch")
    ensure(noop["credential_use_allowed"] is False, "adapter credential denial mismatch")
    ensure(noop["secret_read_allowed"] is False, "adapter secret denial mismatch")
    ensure(noop["environment_read_allowed"] is False, "adapter env denial mismatch")
    ensure(noop["deployment_allowed"] is False, "adapter deployment denial mismatch")
    ensure(noop["production_execution_allowed"] is False, "adapter production denial mismatch")
    ensure(release_lock["STABLE_RUNTIME_VERSION"] == "4.9.0", "release lock version mismatch")


def ensure_module_exports() -> None:
    module = load_script(V4_9_MODULE)
    for name in [
        "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_MODULE_VERSION",
        "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_STATUS",
        "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_PHASE",
        "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN",
        "DEFAULT_V4_8_ROUTING_PREVIEW_REFERENCE_LABEL",
        "DEFAULT_ORCHESTRATION_REVIEW_RECORD_NAME",
    ]:
        ensure(name in module, f"missing v4.9 module constant: {name}")
    for name in [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_review_record_name",
        "generate_orchestration_candidate_review_id",
        "create_live_queue_orchestration_candidate_review_schema",
        "create_orchestration_review_approval_gate",
        "create_v4_8_queue_routing_preview_reference_contract",
        "create_orchestration_review_scope_contract",
        "create_non_execution_orchestration_boundary",
        "create_orchestration_permission_denial_record",
        "create_orchestration_candidate_review_record",
        "create_orchestration_review_audit_record",
        "create_orchestration_readiness_summary",
        "create_first_live_queue_execution_candidate_bridge",
        "build_orchestration_candidate_review_record_payload",
        "write_live_queue_orchestration_candidate_review_record",
        "create_blocked_orchestration_candidate_review_write_record",
        "create_live_queue_orchestration_candidate_review_bundle",
    ]:
        ensure(name in module and callable(module[name]), f"missing v4.9 module export: {name}")


def ensure_no_forbidden_patterns() -> None:
    text = V4_9_MODULE.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_REGEXES:
        ensure(re.search(pattern, text) is None, f"forbidden pattern found in v4.9 module: {pattern}")


def ensure_cli_flags() -> None:
    code, stdout, stderr = run_script(RUNTIME, ["--help"])
    ensure(code == 0, f"runtime --help failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
    for flag in [
        "--live-queue-orchestration-candidate-review-schema",
        "--live-queue-orchestration-candidate-review",
        "--write-live-queue-orchestration-candidate-review",
        "--v4-8-routing-preview-reference-label",
        "--v4-orchestration-review-record-name",
        "--v4-orchestration-review-confirm-token",
        "--v4-orchestration-review-human-operator",
    ]:
        ensure(flag in stdout, f"missing CLI flag: {flag}")


def ensure_schema_and_gates() -> None:
    schema = run_json(RUNTIME, ["--live-queue-orchestration-candidate-review-schema"])
    ensure(schema["schema_version"] == "4.9.0", "schema version mismatch")
    ensure(schema["status"] == "LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_LOCAL_RECORD_ONLY", "schema status mismatch")
    ensure(schema["review_type"] == "live_queue_orchestration_candidate_review", "schema review type mismatch")
    ensure(schema["required_token"] == EXPECTED_V4_9_TOKEN, "schema token mismatch")
    for key in [
        "orchestration_review_approval_gate",
        "v4_8_queue_routing_preview_reference_contract",
        "orchestration_review_scope_contract",
        "non_execution_orchestration_boundary",
        "orchestration_permission_denial_record",
        "orchestration_candidate_review_record",
        "orchestration_review_audit_record",
        "orchestration_readiness_summary",
        "first_live_queue_execution_candidate_bridge",
    ]:
        ensure(key in schema["required_sections"], f"missing schema section: {key}")
    ensure(schema["baseline_preserved"] is True, "schema baseline must be preserved")
    ensure(schema["local_orchestration_review_record_written"] is False, "schema write flag must be false")
    ensure(schema["real_queue_created"] is False, "schema real queue flag must be false")
    ensure(schema["queue_write_performed"] is False, "schema queue write flag must be false")
    ensure(schema["scheduler_write_performed"] is False, "schema scheduler write flag must be false")
    ensure(schema["cron_write_performed"] is False, "schema cron write flag must be false")
    ensure(schema["task_enqueued"] is False, "schema task enqueue flag must be false")
    ensure(schema["task_executed"] is False, "schema task executed flag must be false")
    ensure(schema["live_task_assignment_performed"] is False, "schema live task assignment flag must be false")
    ensure(schema["live_worker_routing_performed"] is False, "schema live worker routing flag must be false")
    ensure(schema["live_orchestration_performed"] is False, "schema live orchestration flag must be false")
    ensure(schema["worker_process_started"] is False, "schema worker process flag must be false")
    ensure(schema["full_workforce_activation_performed"] is False, "schema workforce flag must be false")

    no_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--live-queue-orchestration-candidate-review",
            "--v4-8-routing-preview-reference-label",
            V4_8_REFERENCE_LABEL,
            "--v4-orchestration-review-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    ensure(no_token["orchestration_review_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V4_9_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL", "no-token path should block")
    ensure(no_token["orchestration_candidate_review_write_record"]["write_status"] == "BLOCKED", "no-token write record should block")
    ensure(no_token["local_orchestration_review_record_written"] is False, "no-token bundle should not write")

    bad_token = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--live-queue-orchestration-candidate-review",
            "--v4-8-routing-preview-reference-label",
            V4_8_REFERENCE_LABEL,
            "--v4-orchestration-review-confirm-token",
            "BAD_TOKEN",
            "--v4-orchestration-review-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    ensure(bad_token["orchestration_review_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V4_9_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL", "bad-token path should block")
    ensure(bad_token["orchestration_candidate_review_write_record"]["write_status"] == "BLOCKED", "bad-token write record should block")

    valid_no_write = run_json(
        RUNTIME,
        [
            "--command",
            "check please",
            "--live-queue-orchestration-candidate-review",
            "--v4-8-routing-preview-reference-label",
            V4_8_REFERENCE_LABEL,
            "--v4-orchestration-review-confirm-token",
            EXPECTED_V4_9_TOKEN,
            "--v4-orchestration-review-human-operator",
            HUMAN_OPERATOR,
            "--json",
        ],
    )
    gate = valid_no_write["orchestration_review_approval_gate"]
    ensure(gate["gate_status"] == "APPROVED_FOR_ONE_LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD", "valid token should approve one record")
    ensure(gate["local_orchestration_review_records_authorized"] is True, "valid token should authorize local records")
    ensure(gate["local_orchestration_review_record_write_authorized"] is False, "preview request absent should block write")
    reference = valid_no_write["v4_8_queue_routing_preview_reference_contract"]
    scope = valid_no_write["orchestration_review_scope_contract"]
    boundary = valid_no_write["non_execution_orchestration_boundary"]
    denial = valid_no_write["orchestration_permission_denial_record"]
    candidate = valid_no_write["orchestration_candidate_review_record"]
    audit = valid_no_write["orchestration_review_audit_record"]
    summary = valid_no_write["orchestration_readiness_summary"]
    bridge = valid_no_write["first_live_queue_execution_candidate_bridge"]
    ensure(reference["contract_status"] == "CREATED", "reference contract should be created")
    ensure(scope["scope_status"] == "PASS", "scope should pass")
    ensure(boundary["boundary_status"] == "PASS", "boundary should pass")
    ensure(candidate["candidate_status"] == "LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD_CREATED", "candidate should be created")
    ensure(audit["audit_status"] == "PASS", "audit should pass")
    ensure(summary["readiness_status"] == "READY_FOR_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY", "summary should be ready")
    ensure(bridge["bridge_status"] == "READY_FOR_FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_ONLY", "bridge should be ready")
    ensure(valid_no_write["orchestration_candidate_review_write_record"]["write_status"] == "BLOCKED", "no-write path should block write")
    ensure(valid_no_write["local_orchestration_review_record_written"] is False, "no-write bundle should not write")
    ensure(valid_no_write["real_queue_created"] is False, "no-write bundle real queue should be false")
    ensure(valid_no_write["queue_write_performed"] is False, "no-write bundle queue write should be false")
    ensure(valid_no_write["scheduler_write_performed"] is False, "no-write bundle scheduler write should be false")
    ensure(valid_no_write["cron_write_performed"] is False, "no-write bundle cron write should be false")
    ensure(valid_no_write["task_enqueued"] is False, "no-write bundle task enqueue should be false")
    ensure(valid_no_write["task_executed"] is False, "no-write bundle task execution should be false")
    ensure(valid_no_write["worker_process_started"] is False, "no-write bundle worker start should be false")
    ensure(valid_no_write["live_task_assignment_performed"] is False, "no-write bundle live assignment should be false")
    ensure(valid_no_write["live_worker_routing_performed"] is False, "no-write bundle live routing should be false")
    ensure(valid_no_write["live_orchestration_performed"] is False, "no-write bundle live orchestration should be false")
    ensure(valid_no_write["full_workforce_activation_performed"] is False, "no-write bundle workforce activation should be false")
    payload_for_digest = dict(valid_no_write["orchestration_candidate_review_record_payload"])
    payload_for_digest.pop("payload_digest", None)
    payload_canonical = json.dumps(payload_for_digest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    ensure(hashlib.sha256(payload_canonical.encode("utf-8")).hexdigest() == valid_no_write["orchestration_candidate_review_record_payload"]["payload_digest"], "payload digest mismatch")

    with tempfile.TemporaryDirectory(prefix="station_chief_v4_9_", dir="/tmp") as review_dir:
        write_result = run_json(
            RUNTIME,
            [
                "--command",
                "check please",
                "--write-live-queue-orchestration-candidate-review",
                review_dir,
                "--v4-8-routing-preview-reference-label",
                V4_8_REFERENCE_LABEL,
                "--v4-orchestration-review-confirm-token",
                EXPECTED_V4_9_TOKEN,
                "--v4-orchestration-review-human-operator",
                HUMAN_OPERATOR,
                "--json",
            ],
        )
        write_record = write_result["orchestration_candidate_review_write_record"]
        ensure(write_record["write_status"] == "LOCAL_ORCHESTRATION_CANDIDATE_REVIEW_RECORD_WRITTEN", "write path should write one review record")
        ensure(write_record["local_orchestration_review_record_written"] is True, "write record should mark local write")
        ensure(write_record["files_written_count"] == 1, "write record should report exactly one file")
        ensure(write_result["local_orchestration_review_record_written"] is True, "bundle should report local write")
        written_files = list(Path(review_dir).iterdir())
        ensure(len(written_files) == 1, f"expected exactly one review record, found {len(written_files)}")
        review_path = written_files[0]
        ensure(review_path.name == DEFAULT_REVIEW_RECORD_NAME, "review record filename mismatch")
        ensure(review_path.resolve().is_relative_to(Path(review_dir).resolve()), "review record escaped output directory")
        review_payload = json.loads(review_path.read_text(encoding="utf-8"))
        ensure(review_payload["runtime_version"] == "4.9.0", "review payload runtime version mismatch")
        ensure(review_payload["review_type"] == "live_queue_orchestration_candidate_review", "review payload type mismatch")
        ensure(review_payload["timestamp_mode"] == "deterministic_no_wall_clock_timestamp", "review payload timestamp mode mismatch")
        ensure(review_payload["real_queue_created"] is False, "review payload real queue should be false")
        ensure(review_payload["queue_write_performed"] is False, "review payload queue write should be false")
        ensure(review_payload["scheduler_write_performed"] is False, "review payload scheduler write should be false")
        ensure(review_payload["cron_write_performed"] is False, "review payload cron write should be false")
        ensure(review_payload["task_enqueued"] is False, "review payload task enqueue should be false")
        ensure(review_payload["task_executed"] is False, "review payload task execution should be false")
        ensure(review_payload["live_task_assignment_performed"] is False, "review payload live assignment should be false")
        ensure(review_payload["live_worker_routing_performed"] is False, "review payload live routing should be false")
        ensure(review_payload["live_orchestration_performed"] is False, "review payload live orchestration should be false")
        ensure(review_payload["worker_process_started"] is False, "review payload worker start should be false")
        ensure(review_payload["full_workforce_activation_performed"] is False, "review payload workforce activation should be false")
        ensure(hashlib.sha256(json.dumps({k: v for k, v in review_payload.items() if k != "payload_digest"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest() == review_payload["payload_digest"], "review payload digest mismatch")
        ensure(write_result["orchestration_candidate_review_write_record"]["record_path"] == str(review_path), "write record path mismatch")


def ensure_protected_paths_and_docs() -> None:
    status_output = subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "status", "--short"],
        text=True,
    )
    changed_paths = {
        line[3:].strip()
        for line in status_output.splitlines()
        if line.strip()
    }
    ensure(changed_paths <= ALLOWED_CHANGED_PATHS, f"unexpected changed paths: {sorted(changed_paths - ALLOWED_CHANGED_PATHS)}")
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    ensure("Station Chief Runtime upgraded to v4.9.0. Locked 175-family baseline preserved. Live Queue Orchestration Candidate Review added." in readme, "README missing v4.9 doctrine")
    ensure("v4.9 does not create a real queue." in readme, "README missing v4.9 safety note")
    ensure("v4.9 does not approve v5.0." in readme, "README missing v4.9 boundary note")
    ensure("Next internal label: first live queue execution candidate review only." in readme, "README missing v4.9 next label")
    ensure("Station Chief Runtime upgraded to v4.9.0. Locked 175-family baseline preserved. Live Queue Orchestration Candidate Review added." in skeleton, "skeleton missing v4.9 doctrine")
    ensure("v4.9 does not create a real queue." in skeleton, "skeleton missing v4.9 safety note")
    ensure("v4.9 does not approve v5.0." in skeleton, "skeleton missing v4.9 boundary note")
    ensure("Next internal label: first live queue execution candidate review only." in skeleton, "skeleton missing v4.9 next label")
    ensure("Station Chief Runtime v4.9.0 Report" in report, "v4.9 report missing header")
    ensure("Devin O’Rourke" in report, "v4.9 report missing ownership attribution")
    ensure("first live queue execution candidate review only" in report, "v4.9 report missing next label")
    ensure(not any((REPO_ROOT / relative).exists() for relative in [
        "10_runtime/station_chief_first_live_queue_execution_candidate.py",
        "scripts/validate_station_chief_runtime_v5_0.py",
        "09_exports/station_chief_runtime_v5_0_report.md",
    ]), "v5.0 file unexpectedly exists")
    ensure(not any(REPO_ROOT.rglob("*v5_0*")), "v5.0 path unexpectedly exists")


def ensure_smoke_tests() -> None:
    hidden_paths = [V4_9_MODULE, REPORT, REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_9.py"]
    with tempfile.TemporaryDirectory(prefix="station_chief_v4_9_hidden_", dir="/tmp") as hidden_dir_name:
        hidden_dir = Path(hidden_dir_name)
        moved: list[tuple[Path, Path]] = []
        try:
            for path in hidden_paths:
                if path.exists():
                    hidden_target = hidden_dir / path.name
                    shutil.move(str(path), str(hidden_target))
                    moved.append((hidden_target, path))
            for validator in [V4_8_VALIDATOR, V4_7_VALIDATOR, V4_6_VALIDATOR]:
                code, stdout, stderr = run_script(validator, [])
                ensure(code == 0, f"smoke test failed for {validator.name}\nstdout:\n{stdout}\nstderr:\n{stderr}")
        finally:
            for hidden_target, original_path in reversed(moved):
                shutil.move(str(hidden_target), str(original_path))


def main() -> None:
    ensure_required_files()
    ensure_versions()
    ensure_module_exports()
    ensure_no_forbidden_patterns()
    ensure_cli_flags()
    ensure_schema_and_gates()
    ensure_smoke_tests()
    ensure_protected_paths_and_docs()
    print("STATION_CHIEF_RUNTIME_V4_9_VALIDATION_PASS")


if __name__ == "__main__":
    main()
