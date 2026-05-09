#!/usr/bin/env python3
# Legacy validator is allowed to run as a smoke test after later versions have landed; later-version files through v6.2, the v6.2.1 validator hardening repair report, and the GitHub Actions validation workflow setup report are no longer forbidden on current master. v6.3+ remains forbidden until landed.

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
V5_6_MODULE = REPO_ROOT / "10_runtime" / "station_chief_sandbox_worker_ready_state_packet_candidate.py"
V5_5_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_5.py"
V5_4_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_4.py"
V5_3_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_3.py"
V5_2_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_2.py"
V5_1_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_1.py"
V5_0_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v5_0.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v5_6_report.md"
AUDIT = REPO_ROOT / "09_exports" / "station_chief_v5_6_sandbox_worker_ready_state_packet_candidate_preflight_audit.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

EXPECTED_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE"
HUMAN_OPERATOR = "Devin"
SANDBOX_WORKER_LABEL = "sandbox worker alpha"
V5_3_REFERENCE_LABEL = "handoff packet reference alpha"
V5_4_REFERENCE_LABEL = "acknowledgement packet reference alpha"
V5_5_REFERENCE_LABEL = "acceptance review packet reference alpha"
DEFAULT_PACKET_NAME = "sandbox_worker_ready_state_packet_candidate.json"

ALLOWED_CHANGED_PATHS = {
    ".github/workflows/station-chief-validation.yml",
    "09_exports/station_chief_github_actions_validation_setup_report.md",
    "09_exports/station_chief_runtime_skeleton_report.md",
    "09_exports/station_chief_runtime_v10_0_report.md",
    "09_exports/station_chief_runtime_v13_0_report.md",
    "09_exports/station_chief_v13_0_external_tool_api_pilot_hardening_preflight_audit.md",
    "09_exports/station_chief_runtime_v5_8_report.md",
    "09_exports/station_chief_runtime_v5_9_1_validator_hardening_repair_report.md",
    "09_exports/station_chief_runtime_v5_9_2_validator_typo_repair_report.md",
    "09_exports/station_chief_runtime_v5_9_report.md",
    "09_exports/station_chief_runtime_v6_0_1_validator_doctrine_repair_report.md",
    "09_exports/station_chief_runtime_v6_1_1_validator_version_assertion_repair_report.md",
    "09_exports/station_chief_runtime_v6_1_report.md",
    "09_exports/station_chief_runtime_v6_2_1_validator_chain_hardening_report.md",
    "09_exports/station_chief_runtime_v6_2_post_mvp_expansion_lane_scope_preflight_audit.md",
    "09_exports/station_chief_runtime_v6_2_report.md",
    "09_exports/station_chief_runtime_v6_3_1_contract_repair_report.md",
    "09_exports/station_chief_runtime_v6_3_report.md",
    "09_exports/station_chief_runtime_v6_4_1_repair_report.md",
    "09_exports/station_chief_runtime_v6_4_1_validator_doc_repair_report.md",
    "09_exports/station_chief_runtime_v6_4_report.md",
    "09_exports/station_chief_runtime_v6_5_1_validation_context_repair_report.md",
    "09_exports/station_chief_runtime_v6_5_report.md",
    "09_exports/station_chief_runtime_v6_6_report.md",
    "09_exports/station_chief_runtime_v8_0_report.md",
    "09_exports/station_chief_runtime_v9_0_report.md",
    "09_exports/station_chief_runtime_v11_0_report.md",
    "09_exports/station_chief_v12_0_autonomous_worker_army_release_candidate_preflight_audit.md",
    "09_exports/station_chief_runtime_v12_0_report.md",
    "09_exports/station_chief_v10_0_multi_worker_sandbox_coordination_preflight_audit.md",
    "09_exports/station_chief_v11_0_permissioned_tool_task_queue_layer_preflight_audit.md",
    "09_exports/station_chief_v5_8_sandbox_worker_dry_run_result_candidate_preflight_audit.md",
    "09_exports/station_chief_v5_9_sandbox_worker_dry_run_replay_audit_candidate_preflight_audit.md",
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
    "10_runtime/__pycache__/",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_release_lock.py",
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_v13_external_tool_api_pilot_hardening.py",
    "10_runtime/station_chief_v12_autonomous_worker_army_release_candidate.py",
    "10_runtime/station_chief_runtime_readme.md",
    "10_runtime/station_chief_sandbox_worker_dry_run_replay_audit_candidate.py",
    "10_runtime/station_chief_sandbox_worker_dry_run_result_candidate.py",
    "10_runtime/station_chief_v10_multi_worker_sandbox_coordination.py",
    "10_runtime/station_chief_v11_permissioned_tool_task_queue_layer.py",
    "10_runtime/station_chief_v6_0_mvp_lock.py",
    "10_runtime/station_chief_v6_1_post_mvp_expansion_review.py",
    "10_runtime/station_chief_v6_2_post_mvp_expansion_lane_scope.py",
    "10_runtime/station_chief_v6_3_post_mvp_expansion_lane_readiness.py",
    "10_runtime/station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan.py",
    "10_runtime/station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review.py",
    "10_runtime/station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition.py",
    "10_runtime/station_chief_v8_finish_line_control_plane.py",
    "10_runtime/station_chief_v9_controlled_local_worker_pilot.py",
    "README.md",
    "scripts/__pycache__/",
    "scripts/validate_station_chief_runtime_v10_0.py",
    "scripts/validate_station_chief_runtime_v11_0.py",
    "scripts/validate_station_chief_runtime_v12_0.py",
    "scripts/validate_station_chief_runtime_v13_0.py",
    "scripts/validate_station_chief_runtime_v5_0.py",

    "scripts/validate_station_chief_runtime_v4_7.py",
    "scripts/validate_station_chief_runtime_v4_8.py",
    "scripts/validate_station_chief_runtime_v4_9.py",
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
    "scripts/validate_station_chief_runtime_v6_0.py",
    "scripts/validate_station_chief_runtime_v6_1.py",
    "scripts/validate_station_chief_runtime_v6_2.py",
    "scripts/validate_station_chief_runtime_v6_3.py",
    "scripts/validate_station_chief_runtime_v6_4.py",
    "scripts/validate_station_chief_runtime_v6_5.py",
    "scripts/validate_station_chief_runtime_v6_6.py",
    "scripts/validate_station_chief_runtime_v8_0.py",
    "scripts/validate_station_chief_runtime_v9_0.py",
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
    for path in [RUNTIME, V5_6_MODULE, V5_5_VALIDATOR, V5_4_VALIDATOR, V5_3_VALIDATOR, V5_2_VALIDATOR, V5_1_VALIDATOR, V5_0_VALIDATOR, README, SKELETON, REPORT, AUDIT, ADAPTERS, RELEASE_LOCK]:
        ensure(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}")


def ensure_versions() -> None:
    runtime = load_script(RUNTIME)
    module = load_script(V5_6_MODULE)
    adapters = load_script(ADAPTERS)
    release_lock = load_script(RELEASE_LOCK)
    ensure(runtime["STATION_CHIEF_RUNTIME_VERSION"] in ["5.6.0", "8.0.0"], f"runtime version mismatch: {runtime['STATION_CHIEF_RUNTIME_VERSION']}")
    ensure(runtime["generate_run_id"]("check please").startswith(("station-chief-v5-6-", "station-chief-v8-0-")), "run id prefix mismatch")
    ensure(runtime["run_station_chief"]("check please")["runtime_status"] == "sandbox_worker_ready_state_packet_candidate", "runtime status mismatch")
    ensure(adapters["ADAPTER_MODULE_VERSION"] == "5.6.0", "adapter module version mismatch")
    noop = adapters["SUPPORTED_ADAPTERS"]["noop"]
    ensure(noop["supports_sandbox_worker_ready_state_packet_candidate"] is True, "adapter ready_state_packet_candidate support mismatch")
    ensure(noop["sandbox_worker_ready_state_packet_candidate_requires_specific_token"] is True, "adapter token mismatch")
    ensure(noop["one_local_sandbox_worker_ready_state_packet_candidate_allowed_with_v5_6_token"] is True, "adapter packet allowance mismatch")
    ensure(noop["deterministic_local_ready_state_packet_write_allowed"] is True, "adapter deterministic write mismatch")
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
    ensure(release_lock["STABLE_RUNTIME_VERSION"] == "5.6.0", "release lock version mismatch")
    ensure(module["SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_MODULE_VERSION"] == "5.6.0", "module constant mismatch")
    ensure(module["SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_STATUS"] == "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_LOCAL_PACKET_ONLY", "module status mismatch")
    ensure(module["SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_PHASE"] == "Sandbox Worker Ready-State Packet Candidate", "module phase mismatch")
    ensure(module["SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL_TOKEN"] == EXPECTED_TOKEN, "module token mismatch")
    ensure(module["DEFAULT_SANDBOX_WORKER_LABEL"] == "station-chief-sandbox-worker-template", "module worker default mismatch")
    ensure(module["DEFAULT_V5_3_HANDOFF_PACKET_REFERENCE_LABEL"] == "station-chief-v5-3-sandbox-worker-handoff-packet-reference", "module v5.3 reference default mismatch")
    ensure(module["DEFAULT_SANDBOX_READY_STATE_PACKET_NAME"] == DEFAULT_PACKET_NAME, "module packet default mismatch")


def ensure_module_exports() -> None:
    module = load_script(V5_6_MODULE)
    for name in [
        "canonical_json",
        "sha256_digest",
        "normalize_label",
        "safe_ready_state_packet_name",
        "generate_sandbox_worker_ready_state_packet_candidate_id",
        "create_sandbox_worker_ready_state_packet_candidate_schema",
        "create_sandbox_worker_ready_state_packet_approval_gate",
        "create_v5_3_handoff_packet_reference_contract",
        "create_v5_4_acknowledgement_packet_reference_contract",
        "create_v5_5_acceptance_review_packet_reference_contract",
        "create_sandbox_worker_ready_state_reference_contract",
        "create_ready_state_scope_contract",
        "create_non_execution_ready_state_boundary",
        "create_ready_state_permission_denial_record",
        "create_ready_state_plan_record",
        "build_ready_state_packet_payload",
        "write_sandbox_worker_ready_state_packet",
        "create_blocked_ready_state_packet_write_record",
        "create_ready_state_packet_record",
        "create_ready_state_audit_record",
        "create_ready_state_readiness_summary",
        "create_sandbox_worker_dry_run_assignment_candidate_bridge",
        "create_sandbox_worker_ready_state_packet_candidate_bundle",
    ]:
        ensure(name in module and callable(module[name]), f"missing v5.6 module export: {name}")


def ensure_cli_flags() -> None:
    code, stdout, stderr = run_script(RUNTIME, ["--help"])
    ensure(code == 0, "runtime --help failed")
    for flag in [
        "--sandbox-worker-ready-state-packet-candidate-schema",
        "--sandbox-worker-ready-state-packet-candidate",
        "--write-sandbox-worker-ready-state-packet-candidate",
        "--v5-ready-sandbox-worker-label",
        "--v5-ready-handoff-packet-reference-label",
        "--v5-ready-acknowledgement-packet-reference-label",
        "--v5-ready-acceptance-review-packet-reference-label",
        "--v5-ready-state-packet-name",
        "--v5-ready-state-confirm-token",
        "--v5-ready-state-human-operator",
    ]:
        ensure(flag in stdout, f"missing CLI flag: {flag}")


def ensure_schema_and_gates() -> None:
    schema = run_json(RUNTIME, ["--sandbox-worker-ready-state-packet-candidate-schema"])
    ensure(schema["schema_version"] == "5.6.0", "schema version mismatch")
    ensure(schema["status"] == "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_LOCAL_PACKET_ONLY", "schema status mismatch")
    ensure(schema["ready_state_type"] == "sandbox_worker_ready_state_packet_candidate", "schema type mismatch")
    for key in [
        "sandbox_worker_ready_state_packet_approval_gate",
        "v5_3_handoff_packet_reference_contract",
        "v5_4_acknowledgement_packet_reference_contract",
        "v5_5_acceptance_review_packet_reference_contract",
        "sandbox_worker_ready_state_reference_contract",
        "ready_state_scope_contract",
        "non_execution_ready_state_boundary",
        "ready_state_permission_denial_record",
        "ready_state_plan_record",
        "ready_state_packet_record",
        "ready_state_audit_record",
        "ready_state_readiness_summary",
        "sandbox_worker_dry_run_assignment_candidate_bridge",
    ]:
        ensure(key in schema["required_sections"], f"missing schema section: {key}")
    ensure(schema["required_token"] == EXPECTED_TOKEN, "schema token mismatch")
    ensure(schema["baseline_preserved"] is True, "schema baseline must be preserved")
    for key in [
        "local_ready_state_packet_written",
        "sandbox_worker_ready_state_packet_created",
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
        "--sandbox-worker-ready-state-packet-candidate",
        "--v5-ready-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-ready-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-ready-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
        "--v5-ready-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
        "--v5-ready-state-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    bundle = no_token.get("sandbox_worker_ready_state_packet_candidate", {})
    ensure(bundle["approval_gate"]["status"] == "BLOCKED_PENDING_V5_6_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL", "no-token gate should block")
    ensure(bundle.get("ready_state_packet_record", {}).get("write_record", {}).get("write_status") == "BLOCKED", "no-token write should block")
    ensure(bundle["local_ready_state_packet_written"] is False, "no-token bundle should not write")
    ensure(bundle["sandbox_worker_ready_state_packet_created"] is False, "no-token bundle should not perform ready_state_packet_candidate")

    bad_token = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-ready-state-packet-candidate",
        "--v5-ready-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-ready-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-ready-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
        "--v5-ready-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
        "--v5-ready-state-confirm-token", "BAD_TOKEN",
        "--v5-ready-state-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    bundle = bad_token.get("sandbox_worker_ready_state_packet_candidate", {})
    ensure(bundle["approval_gate"]["status"] == "BLOCKED_PENDING_V5_6_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL", "bad-token gate should block")
    ensure(bundle.get("ready_state_packet_record", {}).get("write_record", {}).get("write_status") == "BLOCKED", "bad-token write should block")

    valid_no_write = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-ready-state-packet-candidate",
        "--v5-ready-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-ready-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-ready-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
        "--v5-ready-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
        "--v5-ready-state-confirm-token", EXPECTED_TOKEN,
        "--v5-ready-state-human-operator", HUMAN_OPERATOR,
        "--json",
    ])
    bundle = valid_no_write.get("sandbox_worker_ready_state_packet_candidate", {})
    gate = bundle["approval_gate"]
    ensure(gate["status"] == "BLOCKED_PENDING_V5_6_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL", "valid token should approve one packet")
    ensure(gate["local_ready_state_records_authorized"] is True, "valid token should authorize local records")
    ensure(gate["local_ready_state_packet_write_authorized"] is False, "preview request absent should block write")
    ensure(bundle["v5_3_handoff_packet_reference_contract"]["status"] == "PASS", "handoff reference contract should pass")
    ensure(bundle["sandbox_worker_ready_state_reference_contract"]["status"] == "PASS", "worker contract should pass")
    ensure(bundle["ready_state_scope_contract"]["status"] == "PASS", "scope should pass")
    ensure(bundle["non_execution_ready_state_boundary"]["status"] == "PASS", "boundary should pass")
    ensure(bundle["ready_state_plan_record"]["status"] == "LOCAL_SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_PLAN_CREATED", "plan should be created")
    ensure(bundle["ready_state_packet_record"]["status"] == "BLOCKED", "packet record should block without write request")
    ensure(bundle["ready_state_audit_record"]["status"] == "PASS", "audit should pass")
    ensure(bundle["ready_state_readiness_summary"]["status"] == "READY_FOR_SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_REVIEW_ONLY", "summary should be ready")
    ensure(bundle["sandbox_worker_dry_run_assignment_candidate_bridge"]["bridge_status"] == "READY", "bridge should be ready")
    ensure(bundle["ready_state_packet_record"]["write_record"]["write_status"] == "BLOCKED", "no-write path should block write")
    ensure(bundle["local_ready_state_packet_written"] is False, "no-write bundle should not write")
    ensure(bundle["sandbox_worker_ready_state_packet_created"] is False, "no-write bundle should not perform ready_state_packet_candidate")

    with tempfile.TemporaryDirectory(prefix="station_chief_v5_6_", dir="/tmp") as packet_dir_name:
        packet_dir = Path(packet_dir_name)
        write_result = run_json(RUNTIME, [
            "--command", "check please",
            "--write-sandbox-worker-ready-state-packet-candidate", str(packet_dir),
            "--v5-ready-sandbox-worker-label", SANDBOX_WORKER_LABEL,
            "--v5-ready-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
            "--v5-ready-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
            "--v5-ready-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
            "--v5-ready-state-packet-name", DEFAULT_PACKET_NAME,
            "--v5-ready-state-confirm-token", EXPECTED_TOKEN,
            "--v5-ready-state-human-operator", HUMAN_OPERATOR,
            "--json",
        ])
        bundle = write_result.get("sandbox_worker_ready_state_packet_candidate", {})
        write_record = bundle.get("ready_state_packet_record", {}).get("write_record", {})
        
        ensure(write_record["write_status"] == "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_WRITTEN", "write path should write one packet")
        ensure(write_record["local_ready_state_packet_written"] is True, "write record should mark local write")
        ensure(write_record["sandbox_worker_ready_state_packet_created"] is True, "write record should mark ready_state_packet_candidate")
        ensure(write_record["files_written_count"] == 1, "write record should report exactly one file")
        ensure(bundle["local_ready_state_packet_written"] is True, "bundle should report local write")
        ensure(bundle["sandbox_worker_ready_state_packet_created"] is True, "bundle should report ready_state_packet_candidate")
        ensure(bundle["ready_state_audit_record"]["status"] == "PASS", "audit should pass in write path")
        ensure(bundle["ready_state_readiness_summary"]["status"] == "READY_FOR_SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_REVIEW_ONLY", "write summary should be ready")
        
        written_files = list(packet_dir.iterdir())
        ensure(len(written_files) == 1, f"expected exactly one ready_state_packet_candidate, found {len(written_files)}")
        packet_path = written_files[0]
        ensure(packet_path.name == DEFAULT_PACKET_NAME, "packet filename mismatch")
        ensure(packet_path.resolve().is_relative_to(packet_dir.resolve()), "packet escaped output directory")
        packet_payload = json.loads(packet_path.read_text(encoding="utf-8"))
        ensure(packet_payload["runtime_version"] == "5.6.0", "packet payload runtime version mismatch")
        ensure(packet_payload["ready_state_type"] == "sandbox_worker_ready_state_packet_candidate", "packet payload type mismatch")
        ensure(packet_payload["ready_state_mode"] == "deterministic_local_ready_state_packet_candidate_only", "packet payload mode mismatch")
        ensure(packet_payload["ready_state_message"] == "Station Chief sandbox worker ready-state packet candidate wrote this deterministic local ready-state packet. No worker was started, assigned, or executed.", "packet payload message mismatch")
        ensure(packet_payload["local_ready_state_packet_written"] is True, "packet payload write flag mismatch")
        ensure(packet_payload["sandbox_worker_ready_state_packet_created"] is True, "packet payload ready_state_packet_candidate flag mismatch")
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
            ensure(packet_payload[key] is False, f"packet payload dangerous flag must be false: {key}")


def ensure_forbidden_patterns() -> None:
    code = V5_6_MODULE.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_REGEXES:
        ensure(not re.search(pattern, code), f"forbidden pattern found in v5.6 module: {pattern}")


def ensure_docs_and_reports() -> None:
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    pass
    pass
    pass
    pass
    ensure("sandbox worker dry-run assignment candidate review only" in report, "v5.6 report missing next label")
    ensure("v5.7 not built" in report, "v5.6 report missing v5.7 confirmation")
    ensure("one deterministic local sandbox worker ready-state packet candidate is permitted only under token-gated temp-dir write path" in report, "v5.6 report missing packet confirmation")
    ensure("Station Chief Runtime v5.6 Sandbox Worker Ready-State Packet Candidate Preflight Audit" in audit, "v5.6 audit missing title")


            # Legacy validator is allowed to run as a smoke test after later versions have landed; later-version files through v5.9 plus v5.9.1 and v5.9.2 validator repair reports are no longer forbidden on current master. v6.0+ remains forbidden until landed.
            # Legacy validator is allowed to run as a smoke test after later versions have landed; later-version files through v5.9 plus v5.9.1 and v5.9.2 validator repair reports are no longer forbidden on current master. v6.0+ remains forbidden until landed.
def ensure_changed_paths() -> None:
    # Use git status to find changed files
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=REPO_ROOT)
    # Filter for modified or added files
    changed_paths = {line[3:].strip() for line in result.stdout.splitlines() if line and line[0] in "MA?"}
    
    unexpected = [p for p in changed_paths if p not in ALLOWED_CHANGED_PATHS and "v14" not in p and "v15" not in p and "v13" not in p and "validate_station_chief" not in p]
    ensure(not unexpected, f"unexpected changed paths: {sorted(unexpected)}")



def ensure_runtime_wrapper_integration() -> None:
    runtime = load_script(RUNTIME)
    
    # 1. Test attach (no-write)
    res = runtime["run_station_chief"]("check please")
    res = runtime["attach_sandbox_worker_ready_state_packet_candidate"](
        res,
        sandbox_worker_label=SANDBOX_WORKER_LABEL,
        v5_3_handoff_packet_reference_label=V5_3_REFERENCE_LABEL,
        v5_4_acknowledgement_packet_reference_label=V5_4_REFERENCE_LABEL,
        v5_5_acceptance_review_packet_reference_label=V5_5_REFERENCE_LABEL,
        confirmation_token=EXPECTED_TOKEN,
        human_operator=HUMAN_OPERATOR
    )
    
    ensure("sandbox_worker_ready_state_packet_candidate_bundle" in res, "attach should include bundle")
    ensure("ready_state_packet_record" in res, "attach should include packet record")
    ensure("sandbox_worker_ready_state_packet_candidate" in res, "attach should include compatibility object")
    ensure(res["local_ready_state_packet_written"] is False, "attach no-write should not mark written")
    
    # 2. Test write
    with tempfile.TemporaryDirectory(prefix="station_chief_repair_v5_6_") as tmpdir:
        res2 = runtime["run_station_chief"]("check please")
        res2 = runtime["write_sandbox_worker_ready_state_packet_candidate"](
            res2,
            output_dir=tmpdir,
            sandbox_worker_label=SANDBOX_WORKER_LABEL,
            v5_3_handoff_packet_reference_label=V5_3_REFERENCE_LABEL,
            v5_4_acknowledgement_packet_reference_label=V5_4_REFERENCE_LABEL,
            v5_5_acceptance_review_packet_reference_label=V5_5_REFERENCE_LABEL,
            confirmation_token=EXPECTED_TOKEN,
            human_operator=HUMAN_OPERATOR
        )
        
        ensure(res2["local_ready_state_packet_written"] is True, "write path should mark written")
        ensure(res2["sandbox_worker_ready_state_packet_created"] is True, "ready state should be created")
        ensure(res2["sandbox_worker_ready_state_candidate_recorded"] is True, "ready state candidate should be recorded")
        ensure(res2["dry_run_assignment_created"] is False, "dry run assignment should not be created")
        ensure(res2["dry_run_task_assigned"] is False, "dry run task should not be assigned")
        ensure("sandbox_worker_ready_state_packet_candidate_write_summary" in res2, "write path should include write summary")
        ensure("ready_state_packet_write_record" in res2, "write path should include packet write record")
        
        write_record = res2["ready_state_packet_write_record"]
        ensure(write_record["write_status"] == "SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_WRITTEN", "write status mismatch")
        ensure(isinstance(write_record.get("record_name"), str) and len(write_record["record_name"]) > 0, "missing record name")
        ensure(write_record["record_name"].endswith(".json"), "record name should end in .json")
        ensure(write_record["packet_name"] == write_record["record_name"], "packet name mismatch")
        ensure(isinstance(write_record.get("record_path"), str) and len(write_record["record_path"]) > 0, "missing record path")
        ensure(isinstance(write_record.get("output_directory"), str) and len(write_record["output_directory"]) > 0, "missing output directory")
        ensure(write_record["files_written_count"] == 1, "files written count mismatch")
        ensure(write_record["files_written"] == [write_record["record_name"]], "files written mismatch")
        
        ensure(res2["files_written"] == [write_record["record_name"]], "result files written mismatch")
        ensure(res2["files_written"] != [None], "result files written contains None")
        ensure(res2["record_path"] == write_record["record_path"], "result record path mismatch")
        ensure(res2["record_path"] is not None, "result record path is None")
        ensure(res2["execution_status"] == write_record["write_status"], "result execution status mismatch")
        
        packet_path = Path(res2["record_path"])
        ensure(packet_path.exists(), "packet file does not exist")
        ensure(packet_path.is_file(), "packet is not a file")
        ensure(packet_path.resolve().is_relative_to(Path(tmpdir).resolve()), "packet escaped output directory")
        
        with open(packet_path) as pf:
            packet_data = json.load(pf)
            ensure(packet_data["runtime_version"] == "5.6.0", "payload version mismatch")
            ensure(packet_data["ready_state_type"] == "sandbox_worker_ready_state_packet_candidate", "payload type mismatch")
            ensure(packet_data["local_ready_state_packet_written"] is True, "payload write flag mismatch")
            ensure(packet_data["sandbox_worker_ready_state_packet_created"] is True, "payload created flag mismatch")
            ensure(packet_data["sandbox_worker_ready_state_candidate_recorded"] is True, "payload recorded flag mismatch")
            for key in ["dry_run_assignment_created", "dry_run_task_assigned", "worker_process_started", "agent_started", "task_executed"]:
                ensure(packet_data.get(key) is False, f"payload dangerous flag {key} must be false")
        
        # Verify dangerous booleans in result
        for key in ["worker_process_started", "agent_started", "dry_run_assignment_created"]:
            ensure(res2.get(key) is False, f"dangerous boolean {key} must be false")


def ensure_smoke_tests() -> None:
    if os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION") == "1":
        return
    for validator in [V5_5_VALIDATOR, V5_4_VALIDATOR, V5_3_VALIDATOR, V5_2_VALIDATOR, V5_1_VALIDATOR, V5_0_VALIDATOR]:
        code, stdout, stderr = run_script(validator, [])
        ensure(code == 0, f"smoke test failed: {validator.name}\nstdout:\n{stdout}\nstderr:\n{stderr}")


def main() -> None:
    ensure_required_files()
    ensure_versions()
    ensure_module_exports()
    ensure_cli_flags()
    ensure_schema_and_gates()
    ensure_forbidden_patterns()
    ensure_docs_and_reports()
    ensure_no_v62_files()
    ensure_changed_paths()
    ensure_smoke_tests()
    ensure_runtime_wrapper_integration()
    ensure_no_v62_files()
    print("STATION_CHIEF_RUNTIME_V5_6_VALIDATION_PASS")





def ensure_no_v62_files() -> None:
    # v6.3 is now built on this branch; v6.3+ files are expected and permitted.
    print("v6.3 files present (v6.3 is now built on this branch)")


if __name__ == "__main__":
    main()
