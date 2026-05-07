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
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V5_4_MODULE = REPO_ROOT / "10_runtime" / "station_chief_sandbox_worker_acknowledgement_candidate.py"
V5_3_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_3.py"
V5_2_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_2.py"
V5_1_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_1.py"
V5_0_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_0.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v5_4_report.md"
AUDIT = REPO_ROOT / "09_exports" / "station_chief_v5_4_sandbox_worker_acknowledgement_candidate_preflight_audit.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

EXPECTED_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE"
HUMAN_OPERATOR = "Devin"
SANDBOX_WORKER_LABEL = "sandbox worker alpha"
V5_3_REFERENCE_LABEL = "handoff packet reference alpha"
DEFAULT_PACKET_NAME = "sandbox_worker_acknowledgement_candidate_packet.json"

ALLOWED_CHANGED_PATHS = {
    "09_exports/station_chief_v5_4_sandbox_worker_acknowledgement_candidate_preflight_audit.md",
    "10_runtime/station_chief_sandbox_worker_acknowledgement_candidate.py",
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_runtime_readme.md",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_release_lock.py",
    "09_exports/station_chief_runtime_skeleton_report.md",
    "09_exports/station_chief_runtime_v5_4_report.md",
    "scripts/validate_station_chief_runtime_v5_4.py",
    "scripts/validate_station_chief_runtime_v5_3.py",
    "scripts/validate_station_chief_runtime_v5_2.py",
    "scripts/validate_station_chief_runtime_v5_1.py",
    "scripts/validate_station_chief_runtime_v5_0.py",
    "scripts/validate_station_chief_runtime_v4_9.py",
    "scripts/validate_station_chief_runtime_v4_7.py",
}

FORBIDDEN_REGEXES = [
    r"import\s+requests",
    r"from\s+requests",
    r"urllib\.request",
    r"import\s+urllib\.request",
    r"import\s+socket",
    r"from\s+socket",
    r"socket\.socket\s*\(",
    r"subprocess\.run\s*\(",
    r"subprocess\.Popen\s*\(",
    r"import\s+subprocess",
    r"os\.system\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
    r"__import__\s*\(",
    r"os\.getenv",
    r"os\.environ",
    r"getenv\s*\(",
    r"environ\[",
    r"open\s*\(",
    r"gh api",
    r"git push",
    r"create_deployment",
    r"create_commit",
    r"update_ref",
    r"threading",
    r"multiprocessing",
    r"queue\.Queue\s*\(",
    r"asyncio",
    r"kill\s*\(",
    r"terminate\s*\(",
    r"pip install",
    r"npm install",
    r"worker\.start",
    r"start_worker",
    r"start_process",
    r"daemon",
    r"scheduler",
    r"enqueue\s*\(",
    r"dispatch\s*\(",
    r"route_live",
    r"execute_task",
    r"run_task",
    r"assign_live_task",
    r"orchestrate\s*\(",
    r"orchestrate_live",
    r"live_orchestration",
    r"create_queue",
    r"write_queue",
    r"arbitrary_task_execution",
    r"user_task_execution",
    r"execute_user",
    r"shell",
    r"shlex",
    r"system\s*\(",
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
        raise AssertionError(f"invalid json from {path.name} {' '.join(argv)}: {exc}\nstdout:\n{stdout}\nstderr:\n{stderr}") from exc


def ensure_required_files() -> None:
    for path in [RUNTIME, V5_4_MODULE, V5_3_VALIDATOR, V5_2_VALIDATOR, V5_1_VALIDATOR, V5_0_VALIDATOR, README, SKELETON, REPORT, AUDIT, ADAPTERS, RELEASE_LOCK]:
        ensure(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}")


def ensure_versions() -> None:
    runtime = load_script(RUNTIME)
    module = load_script(V5_4_MODULE)
    adapters = load_script(ADAPTERS)
    release_lock = load_script(RELEASE_LOCK)
    ensure(runtime["STATION_CHIEF_RUNTIME_VERSION"] == "5.4.0", "runtime version mismatch")
    ensure(runtime["generate_run_id"]("check please").startswith("station-chief-v5-4-"), "run id prefix mismatch")
    ensure(runtime["run_station_chief"]("check please")["runtime_status"] == "sandbox_worker_acknowledgement_candidate", "runtime status mismatch")
    ensure(adapters["ADAPTER_MODULE_VERSION"] == "5.4.0", "adapter module version mismatch")
    noop = adapters["SUPPORTED_ADAPTERS"]["noop"]
    ensure(noop["supports_sandbox_worker_acknowledgement_candidate"] is True, "adapter acknowledgement support mismatch")
    ensure(noop["sandbox_worker_acknowledgement_candidate_requires_specific_token"] is True, "adapter token mismatch")
    ensure(noop["one_local_sandbox_worker_acknowledgement_packet_allowed_with_v5_4_token"] is True, "adapter packet allowance mismatch")
    ensure(noop["deterministic_local_acknowledgement_packet_write_allowed"] is True, "adapter deterministic write mismatch")
    ensure(noop["sandbox_worker_process_start_allowed"] is False, "adapter worker start denial mismatch")
    ensure(noop["agent_start_allowed"] is False, "adapter agent start denial mismatch")
    ensure(noop["real_queue_creation_allowed"] is False, "adapter real queue creation denial mismatch")
    ensure(noop["queue_write_allowed"] is False, "adapter queue write denial mismatch")
    ensure(noop["scheduler_write_allowed"] is False, "adapter scheduler write denial mismatch")
    ensure(noop["cron_write_allowed"] is False, "adapter cron write denial mismatch")
    ensure(noop["task_enqueue_allowed"] is False, "adapter task enqueue denial mismatch")
    ensure(noop["arbitrary_task_execution_allowed"] is False, "adapter arbitrary task denial mismatch")
    ensure(noop["user_task_execution_allowed"] is False, "adapter user task denial mismatch")
    ensure(noop["worker_process_start_allowed"] is False, "adapter worker process denial mismatch")
    ensure(noop["live_task_assignment_allowed"] is False, "adapter live assignment denial mismatch")
    ensure(noop["live_worker_routing_allowed"] is False, "adapter live routing denial mismatch")
    ensure(noop["live_orchestration_allowed"] is False, "adapter live orchestration denial mismatch")
    ensure(noop["external_tool_invocation_allowed"] is False, "adapter external tool denial mismatch")
    ensure(noop["live_api_call_allowed"] is False, "adapter api denial mismatch")
    ensure(noop["network_access_allowed"] is False, "adapter network denial mismatch")
    ensure(noop["socket_access_allowed"] is False, "adapter socket denial mismatch")
    ensure(noop["credential_use_allowed"] is False, "adapter credential denial mismatch")
    ensure(noop["secret_read_allowed"] is False, "adapter secret denial mismatch")
    ensure(noop["environment_read_allowed"] is False, "adapter env denial mismatch")
    ensure(noop["deployment_allowed"] is False, "adapter deployment denial mismatch")
    ensure(noop["production_execution_allowed"] is False, "adapter production denial mismatch")
    ensure(noop["full_workforce_activation_allowed"] is False, "adapter workforce denial mismatch")
    ensure(release_lock["STABLE_RUNTIME_VERSION"] == "5.4.0", "release lock version mismatch")
    ensure(module["SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_MODULE_VERSION"] == "5.4.0", "module constant mismatch")
    ensure(module["SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_STATUS"] == "SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_LOCAL_PACKET_ONLY", "module status mismatch")
    ensure(module["SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_PHASE"] == "Sandbox Worker Acknowledgement Candidate", "module phase mismatch")
    ensure(module["SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN"] == EXPECTED_TOKEN, "module token mismatch")
    ensure(module["DEFAULT_SANDBOX_WORKER_LABEL"] == "station-chief-sandbox-worker-template", "module worker default mismatch")
    ensure(module["DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL"] == "station-chief-v5-3-repeatability-proof-reference", "module v5.3 reference default mismatch")
    ensure(module["DEFAULT_SANDBOX_ACKNOWLEDGEMENT_PACKET_NAME"] == DEFAULT_PACKET_NAME, "module packet default mismatch")


def ensure_module_exports() -> None:
    module = load_script(V5_4_MODULE)
    for name in [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_acknowledgement_packet_name",
        "generate_sandbox_worker_acknowledgement_candidate_id",
        "create_sandbox_worker_acknowledgement_candidate_schema",
        "create_sandbox_worker_acknowledgement_approval_gate",
        "create_v5_3_handoff_packet_reference_contract",
        "create_sandbox_worker_acknowledgement_reference_contract",
        "create_acknowledgement_scope_contract",
        "create_non_execution_acknowledgement_boundary",
        "create_acknowledgement_permission_denial_record",
        "create_acknowledgement_plan_record",
        "build_acknowledgement_packet_payload",
        "write_sandbox_worker_acknowledgement_packet",
        "create_blocked_acknowledgement_packet_write_record",
        "create_acknowledgement_packet_record",
        "create_acknowledgement_audit_record",
        "create_acknowledgement_readiness_summary",
        "create_sandbox_worker_acceptance_candidate_bridge",
        "create_sandbox_worker_acknowledgement_candidate_bundle",
    ]:
        ensure(name in module and callable(module[name]), f"missing v5.4 module export: {name}")


def ensure_no_forbidden_patterns() -> None:
    text = V5_4_MODULE.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_REGEXES:
        ensure(re.search(pattern, text) is None, f"forbidden pattern found in v5.4 module: {pattern}")


def ensure_cli_flags() -> None:
    code, stdout, stderr = run_script(RUNTIME, ["--help"])
    ensure(code == 0, f"runtime --help failed\nstdout:\n{stdout}\nstderr:\n{stderr}")
    for flag in [
        "--sandbox-worker-acknowledgement-candidate-schema",
        "--sandbox-worker-acknowledgement-candidate",
        "--write-sandbox-worker-acknowledgement-candidate",
        "--v5-ack-sandbox-worker-label",
        "--v5-handoff-packet-reference-label",
        "--v5-acknowledgement-packet-name",
        "--v5-acknowledgement-confirm-token",
        "--v5-acknowledgement-human-operator",
    ]:
        ensure(flag in stdout, f"missing CLI flag: {flag}")


def ensure_schema_and_gates() -> None:
    schema = run_json(RUNTIME, ["--sandbox-worker-acknowledgement-candidate-schema"])
    ensure(schema["schema_version"] == "5.4.0", "schema version mismatch")
    ensure(schema["status"] == "SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_LOCAL_PACKET_ONLY", "schema status mismatch")
    ensure(schema["acknowledgement_type"] == "sandbox_worker_acknowledgement_candidate", "schema type mismatch")
    for key in [
        "sandbox_worker_acknowledgement_approval_gate",
        "v5_3_handoff_packet_reference_contract",
        "sandbox_worker_acknowledgement_reference_contract",
        "acknowledgement_scope_contract",
        "non_execution_acknowledgement_boundary",
        "acknowledgement_permission_denial_record",
        "acknowledgement_plan_record",
        "acknowledgement_packet_record",
        "acknowledgement_audit_record",
        "acknowledgement_readiness_summary",
        "sandbox_worker_acceptance_candidate_bridge",
    ]:
        ensure(key in schema["required_sections"], f"missing schema section: {key}")
    ensure(schema["required_token"] == EXPECTED_TOKEN, "schema token mismatch")
    ensure(schema["baseline_preserved"] is True, "schema baseline must be preserved")
    for key in [
        "local_acknowledgement_packet_written",
        "sandbox_worker_acknowledgement_performed",
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
    ]:
        ensure(schema[key] is False, f"schema dangerous flag must be false: {key}")

    no_token = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-acknowledgement-candidate",
        "--v5-ack-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-acknowledgement-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    ensure(no_token["sandbox_worker_acknowledgement_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V5_4_SANDBOX_WORKER_ACKNOWLEDGEMENT_APPROVAL", "no-token gate should block")
    ensure(no_token["acknowledgement_packet_write_record"]["write_status"] == "BLOCKED", "no-token write should block")
    ensure(no_token["local_acknowledgement_packet_written"] is False, "no-token bundle should not write")
    ensure(no_token["sandbox_worker_acknowledgement_performed"] is False, "no-token bundle should not perform acknowledgement")

    bad_token = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-acknowledgement-candidate",
        "--v5-ack-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-acknowledgement-confirm-token", "BAD_TOKEN",
        "--v5-acknowledgement-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    ensure(bad_token["sandbox_worker_acknowledgement_approval_gate"]["gate_status"] == "BLOCKED_PENDING_V5_4_SANDBOX_WORKER_ACKNOWLEDGEMENT_APPROVAL", "bad-token gate should block")
    ensure(bad_token["acknowledgement_packet_write_record"]["write_status"] == "BLOCKED", "bad-token write should block")

    valid_no_write = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-acknowledgement-candidate",
        "--v5-ack-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-acknowledgement-confirm-token", EXPECTED_TOKEN,
        "--v5-acknowledgement-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    gate = valid_no_write["sandbox_worker_acknowledgement_approval_gate"]
    ensure(gate["gate_status"] == "APPROVED_FOR_ONE_LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET", "valid token should approve one packet")
    ensure(gate["local_acknowledgement_records_authorized"] is True, "valid token should authorize local records")
    ensure(gate["local_acknowledgement_packet_write_authorized"] is False, "preview request absent should block write")
    ensure(valid_no_write["v5_3_handoff_packet_reference_contract"]["contract_status"] == "CREATED", "handoff reference contract should be created")
    ensure(valid_no_write["sandbox_worker_acknowledgement_reference_contract"]["contract_status"] == "CREATED", "worker contract should be created")
    ensure(valid_no_write["acknowledgement_scope_contract"]["scope_status"] == "PASS", "scope should pass")
    ensure(valid_no_write["non_execution_acknowledgement_boundary"]["boundary_status"] == "PASS", "boundary should pass")
    ensure(valid_no_write["acknowledgement_plan_record"]["plan_status"] == "LOCAL_SANDBOX_WORKER_ACKNOWLEDGEMENT_PLAN_CREATED", "plan should be created")
    ensure(valid_no_write["acknowledgement_packet_record"]["packet_status"] == "BLOCKED", "packet record should block without write request")
    ensure(valid_no_write["acknowledgement_audit_record"]["audit_status"] == "PASS", "audit should pass")
    ensure(valid_no_write["acknowledgement_readiness_summary"]["readiness_status"] == "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY", "summary should be ready")
    ensure(valid_no_write["sandbox_worker_acceptance_candidate_bridge"]["bridge_status"] == "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY", "bridge should be ready")
    ensure(valid_no_write["acknowledgement_packet_write_record"]["write_status"] == "BLOCKED", "no-write path should block write")
    ensure(valid_no_write["local_acknowledgement_packet_written"] is False, "no-write bundle should not write")
    ensure(valid_no_write["sandbox_worker_acknowledgement_performed"] is False, "no-write bundle should not perform acknowledgement")

    with tempfile.TemporaryDirectory(prefix="station_chief_v5_4_", dir="/tmp") as packet_dir_name:
        packet_dir = Path(packet_dir_name)
        write_result = run_json(RUNTIME, [
            "--command", "check please",
            "--write-sandbox-worker-acknowledgement-candidate", str(packet_dir),
            "--v5-ack-sandbox-worker-label", SANDBOX_WORKER_LABEL,
            "--v5-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
            "--v5-acknowledgement-packet-name", DEFAULT_PACKET_NAME,
            "--v5-acknowledgement-confirm-token", EXPECTED_TOKEN,
            "--v5-acknowledgement-human-operator", HUMAN_OPERATOR,
            "--json",
        ])
        write_record = write_result["acknowledgement_packet_write_record"]
        bundle = write_result["sandbox_worker_acknowledgement_candidate_bundle"]
        ensure(write_record["write_status"] == "SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET_WRITTEN", "write path should write one packet")
        ensure(write_record["local_acknowledgement_packet_written"] is True, "write record should mark local write")
        ensure(write_record["sandbox_worker_acknowledgement_performed"] is True, "write record should mark acknowledgement")
        ensure(write_record["files_written_count"] == 1, "write record should report exactly one file")
        ensure(bundle["local_acknowledgement_packet_written"] is True, "bundle should report local write")
        ensure(bundle["sandbox_worker_acknowledgement_performed"] is True, "bundle should report acknowledgement")
        ensure(bundle["acknowledgement_audit_record"]["audit_status"] == "PASS", "audit should pass in write path")
        ensure(bundle["acknowledgement_readiness_summary"]["readiness_status"] == "READY_FOR_SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_ONLY", "write summary should be ready")
        ensure(write_result["sandbox_worker_acknowledgement_candidate_dir"] == str(packet_dir.resolve()), "write directory mismatch")
        ensure(write_result["execution_status"] == "SANDBOX_WORKER_ACKNOWLEDGEMENT_PACKET_WRITTEN", "write status mismatch")
        ensure(write_result["files_written"] == [DEFAULT_PACKET_NAME], "files_written mismatch")
        written_files = list(packet_dir.iterdir())
        ensure(len(written_files) == 1, f"expected exactly one acknowledgement packet, found {len(written_files)}")
        packet_path = written_files[0]
        ensure(packet_path.name == DEFAULT_PACKET_NAME, "packet filename mismatch")
        ensure(packet_path.resolve().is_relative_to(packet_dir.resolve()), "packet escaped output directory")
        packet_payload = json.loads(packet_path.read_text(encoding="utf-8"))
        ensure(packet_payload["runtime_version"] == "5.4.0", "packet payload runtime version mismatch")
        ensure(packet_payload["acknowledgement_type"] == "sandbox_worker_acknowledgement_candidate", "packet payload type mismatch")
        ensure(packet_payload["acknowledgement_mode"] == "deterministic_local_acknowledgement_packet_only", "packet payload mode mismatch")
        ensure(packet_payload["acknowledgement_message"] == "Station Chief sandbox worker acknowledgement candidate wrote this deterministic local acknowledgement packet. No worker was started.", "packet payload message mismatch")
        ensure(packet_payload["local_acknowledgement_packet_written"] is True, "packet payload write flag mismatch")
        ensure(packet_payload["sandbox_worker_acknowledgement_performed"] is True, "packet payload acknowledgement flag mismatch")
        for key in [
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
        ]:
            ensure(packet_payload[key] is False, f"packet payload {key} must be false")
        payload_for_digest = dict(packet_payload)
        payload_for_digest.pop("payload_digest", None)
        ensure(hashlib.sha256(json.dumps(payload_for_digest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest() == packet_payload["payload_digest"], "packet payload digest mismatch")
        ensure(write_record["record_path"] == str(packet_path), "packet record path mismatch")
        ensure(len(list(packet_dir.iterdir())) == 1, "expected exactly one acknowledgement packet file")

    runtime = load_script(RUNTIME)
    runtime_result = runtime["run_station_chief"]("check please")
    artifacts = runtime["build_runtime_artifacts"](runtime_result, runtime["generate_run_id"]("check please"))
    ensure("runtime_index_entry" in artifacts, "artifact builder missing runtime index entry")
    with tempfile.TemporaryDirectory(prefix="station_chief_v5_4_artifacts_", dir="/tmp") as artifact_tmp:
        artifact_dir = Path(artifact_tmp) / "artifacts"
        registry_dir = Path(artifact_tmp) / "registry"
        runtime = load_script(RUNTIME)
        artifact_write_result = runtime["write_runtime_artifacts"](runtime_result, artifact_dir, run_label="station-chief-runtime", registry_dir=registry_dir)
        ensure(artifact_write_result["runtime_index_entry"]["runtime_version"] == "5.4.0", "artifact writer runtime version mismatch")
        ensure(artifact_write_result["runtime_index_entry"]["artifact_type"] == "station_chief_runtime_v5_4_artifacts", "artifact writer type mismatch")
        registry = runtime["load_registry"](registry_dir)
        ensure(registry["registry_version"] == "5.4.0", "registry version mismatch")
        ensure(json.loads((registry_dir / "runtime_index.json").read_text(encoding="utf-8"))["index_version"] == "5.4.0", "registry index version mismatch")


def ensure_docs_and_reports() -> None:
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    ensure("Station Chief Runtime upgraded to v5.4.0. Locked 175-family baseline preserved. Sandbox Worker Acknowledgement Candidate added." in readme, "README missing v5.4 doctrine")
    ensure("v5.4 may write exactly one deterministic local sandbox worker acknowledgement packet only." in readme, "README missing v5.4 write note")
    ensure("v5.4 does not start a worker." in readme, "README missing v5.4 safety note")
    ensure("Next internal label: sandbox worker acceptance candidate review only." in readme, "README missing v5.4 next label")
    ensure("Station Chief Runtime upgraded to v5.4.0. Locked 175-family baseline preserved. Sandbox Worker Acknowledgement Candidate added." in skeleton, "skeleton missing v5.4 doctrine")
    ensure("v5.4 may write exactly one deterministic local sandbox worker acknowledgement packet only." in skeleton, "skeleton missing v5.4 write note")
    ensure("v5.4 does not start a worker." in skeleton, "skeleton missing v5.4 safety note")
    ensure("Next internal label: sandbox worker acceptance candidate review only." in skeleton, "skeleton missing v5.4 next label")
    ensure("Station Chief Runtime v5.4.0 Report" in report, "v5.4 report missing header")
    ensure("Devin O’Rourke" in report, "v5.4 report missing ownership attribution")
    ensure("sandbox worker acceptance candidate review only" in report, "v5.4 report missing next label")
    ensure("v5.5 not built" in report, "v5.4 report missing v5.5 confirmation")
    ensure("one deterministic local sandbox worker acknowledgement packet is permitted only under token-gated temp-dir write path" in report, "v5.4 report missing packet confirmation")
    ensure("Station Chief Runtime v5.4 Sandbox Worker Acknowledgement Candidate Preflight Audit" in audit, "v5.4 audit missing title")
    ensure("READY_FOR_SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_BUILD" in audit, "v5.4 audit missing readiness verdict")


def ensure_no_v55_files() -> None:
    ensure(not any(REPO_ROOT.rglob("*v5_5*")), "v5.5 path unexpectedly exists")


def ensure_smoke_tests() -> None:
    sentinel = "STATION_CHIEF_SKIP_NESTED_SMOKE_TESTS"
    previous = os.environ.get(sentinel)
    os.environ[sentinel] = "1"
    try:
        for validator in [V5_3_VALIDATOR, V5_2_VALIDATOR, V5_1_VALIDATOR, V5_0_VALIDATOR]:
            code, stdout, stderr = run_script(validator, [])
            ensure(code == 0, f"smoke test failed for {validator.name}\nstdout:\n{stdout}\nstderr:\n{stderr}")
    finally:
        if previous is None:
            os.environ.pop(sentinel, None)
        else:
            os.environ[sentinel] = previous


def ensure_protected_paths_and_docs() -> None:
    diff = subprocess.run(["git", "-C", str(REPO_ROOT), "diff", "--name-only"], check=True, text=True, capture_output=True)
    status = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--short"], check=True, text=True, capture_output=True)
    changed_paths = {line.strip() for line in diff.stdout.splitlines() if line.strip() and "__pycache__" not in line and not line.strip().endswith(".pyc")}
    changed_paths |= {
        line.split(maxsplit=1)[-1]
        for line in status.stdout.splitlines()
        if line.strip() and "__pycache__" not in line and not line.strip().endswith(".pyc")
    }
    ensure(changed_paths <= ALLOWED_CHANGED_PATHS, f"unexpected changed paths: {sorted(changed_paths - ALLOWED_CHANGED_PATHS)}")


def main() -> None:
    ensure_required_files()
    ensure_versions()
    ensure_module_exports()
    ensure_no_forbidden_patterns()
    ensure_cli_flags()
    ensure_schema_and_gates()
    ensure_docs_and_reports()
    ensure_no_v55_files()
    ensure_smoke_tests()
    ensure_protected_paths_and_docs()
    print("STATION_CHIEF_RUNTIME_V5_4_VALIDATION_PASS")


if __name__ == "__main__":
    main()
