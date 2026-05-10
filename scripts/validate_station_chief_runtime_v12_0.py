#!/usr/bin/env python3
"""
Station Chief Runtime v12.0 Validator.
Verifies Station Chief v12.0 build, autonomous worker army release candidate metadata, and safety boundaries.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "10_runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from station_chief_runtime import (  # noqa: E402
    STATION_CHIEF_RUNTIME_VERSION,
    build_runtime_index_entry,
    generate_run_id,
    run_station_chief,
)
from station_chief_release_lock import STABLE_RUNTIME_VERSION  # noqa: E402
from station_chief_adapters import ADAPTER_MODULE_VERSION  # noqa: E402
from station_chief_v12_autonomous_worker_army_release_candidate import (  # noqa: E402
    STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_VERSION,
    STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_STATUS,
    STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_PHASE,
    STATION_CHIEF_V12_ARMY_WORKER_IDS,
    STATION_CHIEF_V12_ARMY_SQUAD_IDS,
    STATION_CHIEF_V12_MISSION_ENVELOPE_IDS,
    STATION_CHIEF_V12_VIRTUAL_ARMY_COMMAND_MANIFEST_ID,
    STATION_CHIEF_V12_VIRTUAL_QUEUE_CONTROL_RECORD_ID,
    STATION_CHIEF_V12_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION,
    canonical_json,
    sha256_digest,
    normalize_label,
    create_autonomous_worker_army_profiles,
    create_autonomous_worker_squad_registry,
    create_virtual_army_command_manifest,
    create_mission_envelope_registry,
    create_autonomy_policy_gate,
    create_permissioned_army_dispatch_matrix,
    create_virtual_queue_control_record,
    create_metadata_only_army_cycle_plan,
    create_worker_readiness_receipts,
    create_autonomous_worker_army_release_candidate_audit_record,
    create_autonomous_worker_army_safety_boundary_matrix,
    create_station_chief_v12_autonomous_worker_army_release_candidate_schema,
    create_station_chief_v12_autonomous_worker_army_release_candidate_bundle,
)


def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        raise SystemExit(1)


def run_script(args, env=None):
    return subprocess.run(args, capture_output=True, text=True, env=env)


def _source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ensure_forbidden_patterns_absent(source: str, patterns: list[str], subject: str) -> None:
    for pattern in patterns:
        ensure(pattern not in source, f"Forbidden pattern {pattern!r} found in {subject}")


def _cli_json(args):
    result = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), *args])
    ensure(result.returncode == 0, f"CLI call failed for {' '.join(args)}: {result.stderr}")
    return json.loads(result.stdout)


def _run_prior_validator(script_name: str) -> None:
    env = os.environ.copy()
    env["STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"] = "1"
    result = run_script([sys.executable, str(REPO_ROOT / script_name)], env=env)
    ensure(
        result.returncode == 0,
        f"Prior validator {script_name} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
    )
    expected_token_map = {
        "scripts/validate_station_chief_runtime_v11_0.py": "STATION_CHIEF_RUNTIME_V11_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v10_0.py": "STATION_CHIEF_RUNTIME_V10_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v9_0.py": "STATION_CHIEF_RUNTIME_V9_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v8_0.py": "STATION_CHIEF_RUNTIME_V8_0_VALIDATION_PASS",
    }
    if script_name in expected_token_map:
        ensure(expected_token_map[script_name] in result.stdout, f"Prior validator {script_name} did not report success")


def _assert_no_future_files() -> None:
    forbidden_globs = ["*v12_1*", "*v12.1*", "*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18*"]
    for glob_pattern in forbidden_globs:
        matches = [
            path
            for path in REPO_ROOT.rglob(glob_pattern)
            if "__pycache__" not in str(path) and path.suffix != ".pyc"
        ]
        ensure(not matches, f"Unexpected future files for glob {glob_pattern}: {matches}")


def _assert_protected_paths_unmodified() -> None:
    result = run_script(["git", "-C", str(REPO_ROOT), "status", "--short"])
    ensure(result.returncode == 0, f"git status failed: {result.stderr}")
    allowed_paths = {
        "09_exports/station_chief_v12_0_autonomous_worker_army_release_candidate_preflight_audit.md",
        "09_exports/station_chief_v13_0_external_tool_api_pilot_hardening_preflight_audit.md",
        "10_runtime/station_chief_v12_autonomous_worker_army_release_candidate.py",
        "10_runtime/station_chief_v13_external_tool_api_pilot_hardening.py",
        "09_exports/station_chief_runtime_v12_0_report.md",
        "09_exports/station_chief_runtime_v13_0_report.md",
        "scripts/validate_station_chief_runtime_v12_0.py",
        "scripts/validate_station_chief_runtime_v13_0.py",
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_adapters.py",
        "10_runtime/station_chief_release_lock.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        ".github/workflows/station-chief-validation.yml",
        "scripts/validate_station_chief_runtime_v11_0.py",
        "scripts/validate_station_chief_runtime_v10_0.py",
        "scripts/validate_station_chief_runtime_v9_0.py",
        "scripts/validate_station_chief_runtime_v8_0.py",
        "scripts/validate_station_chief_runtime_v6_6.py",
        "scripts/validate_station_chief_runtime_v6_4.py",
        "scripts/validate_station_chief_runtime_v5_8.py",
        "scripts/validate_station_chief_runtime_v5_7.py",
        "scripts/validate_station_chief_runtime_v5_6.py",
        "scripts/validate_station_chief_runtime_v5_5.py",
        "scripts/validate_station_chief_runtime_v5_4.py",
        "scripts/validate_station_chief_runtime_v5_3.py",
        "scripts/validate_station_chief_runtime_v5_2.py",
        "scripts/validate_station_chief_runtime_v5_1.py",
        "scripts/validate_station_chief_runtime_v5_0.py",
    }
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 and line[1:3] == " " else line
        path = path.lstrip(" M?AD")
        if path.startswith("__pycache__"):
            continue
        ensure(path in allowed_paths or "validate_station_chief_runtime_" in path or ("v14" in path and "v14_1" not in path and "v14.1" not in path) or ("v15" in path and "v15_1" not in path and "v15.1" not in path) or ("v16" in path and "v16_1" not in path and "v16.1" not in path) or ("v17" in path and "v17_1" not in path and "v17.1" not in path and "v18" not in path) or path.startswith("10_runtime/__pycache__") or path.startswith("scripts/__pycache__"), f"Unexpected modified path: {path}")


def main():
    required_files = [
        "09_exports/station_chief_v12_0_autonomous_worker_army_release_candidate_preflight_audit.md",
        "10_runtime/station_chief_v12_autonomous_worker_army_release_candidate.py",
        "09_exports/station_chief_runtime_v12_0_report.md",
        "scripts/validate_station_chief_runtime_v12_0.py",
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_adapters.py",
        "10_runtime/station_chief_release_lock.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        ".github/workflows/station-chief-validation.yml",
        "scripts/validate_station_chief_runtime_v11_0.py",
        "scripts/validate_station_chief_runtime_v10_0.py",
        "scripts/validate_station_chief_runtime_v9_0.py",
        "scripts/validate_station_chief_runtime_v8_0.py",
    ]
    for path in required_files:
        ensure((REPO_ROOT / path).exists(), f"Required file missing: {path}")

    ensure(STATION_CHIEF_RUNTIME_VERSION == "12.0.0", f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION == "12.0.0", f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION == "12.0.0", f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_VERSION == "12.0.0", "v12 module version mismatch")
    ensure(STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_STATUS == "STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_LOCAL_DETERMINISTIC_ONLY", "v12 module status mismatch")
    ensure(STATION_CHIEF_V12_AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_PHASE == "Station Chief v12.0 Autonomous Worker Army Release Candidate", "v12 module phase mismatch")
    ensure(STATION_CHIEF_V12_VIRTUAL_ARMY_COMMAND_MANIFEST_ID == "station-chief-virtual-army-command-manifest-001", "command manifest id mismatch")
    ensure(STATION_CHIEF_V12_VIRTUAL_QUEUE_CONTROL_RECORD_ID == "station-chief-virtual-army-queue-control-record-001", "virtual queue control record id mismatch")
    ensure(STATION_CHIEF_V12_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION == "v12.1 or v13.0 requires explicit operator instruction", "next version label mismatch")

    module_source = _source_text(REPO_ROOT / "10_runtime/station_chief_v12_autonomous_worker_army_release_candidate.py")
    validator_source = _source_text(Path(__file__))
    forbidden_patterns = [
        "import requests",
        "from requests",
        "import urllib",
        "import socket",
        "import subprocess",
        "os.",
        "os[",
        "getenv(",
        ".environ",
        "eval(",
        "exec(",
        "compile(",
        "__import__(",
        "import threading",
        "import multiprocessing",
        "import asyncio",
        "open(",
        "shlex",
        "system(",
        "popen",
        "invoke_tool(",
        "tool_invoked = True",
        "external_tool_invocation_performed = True",
        "run_task",
        "execute_task",
        "execute_user",
        "arbitrary_user_task_execution_performed = True",
        "user_task_execution_performed = True",
        "worker.start",
        "start_worker",
        "real_worker_activation_performed = True",
        "daemon_started = True",
        "background_process_started = True",
        "create_real_queue",
        "queue_write_performed = True",
        "enqueue_live",
        "route_live",
        "orchestrate_live",
        "api_call_performed = True",
        "network_access_performed = True",
        "deploy(",
        "production_execution_performed = True",
        "full_external_prod_agent_army_activation_performed = True",
        "TODO",
        "NotImplemented",
    ]
    _ensure_forbidden_patterns_absent(module_source, forbidden_patterns, "v12 module")

    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v12 validation context")
    ensure("validate_station_chief_runtime_v11_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v11 validation context")
    ensure("validate_station_chief_runtime_v10_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v10 validation context")
    ensure("validate_station_chief_runtime_v9_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v9 validation context")
    ensure("validate_station_chief_runtime_v8_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v8 validation context")
    ensure("validate_station_chief_runtime_v6_6.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.6 validation context")
    ensure("validate_station_chief_runtime_v6_5.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.5 validation context")
    ensure("validate_station_chief_runtime_v6_4.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.4 validation context")
    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_release_lock.py"), "Release lock selector missing v12 validation context")
    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_adapters.py"), "Adapter selector missing v12 validation context")

    ensure(callable(canonical_json), "canonical_json missing or not callable")
    ensure(callable(sha256_digest), "sha256_digest missing or not callable")
    ensure(callable(normalize_label), "normalize_label missing or not callable")
    ensure(callable(create_autonomous_worker_army_profiles), "worker profile function missing or not callable")
    ensure(callable(create_autonomous_worker_squad_registry), "squad registry function missing or not callable")
    ensure(callable(create_virtual_army_command_manifest), "command manifest function missing or not callable")
    ensure(callable(create_mission_envelope_registry), "mission envelope function missing or not callable")
    ensure(callable(create_autonomy_policy_gate), "policy gate function missing or not callable")
    ensure(callable(create_permissioned_army_dispatch_matrix), "dispatch matrix function missing or not callable")
    ensure(callable(create_virtual_queue_control_record), "virtual queue control function missing or not callable")
    ensure(callable(create_metadata_only_army_cycle_plan), "cycle plan function missing or not callable")
    ensure(callable(create_worker_readiness_receipts), "readiness receipts function missing or not callable")
    ensure(callable(create_autonomous_worker_army_release_candidate_audit_record), "audit record function missing or not callable")
    ensure(callable(create_autonomous_worker_army_safety_boundary_matrix), "safety boundary function missing or not callable")
    ensure(callable(create_station_chief_v12_autonomous_worker_army_release_candidate_schema), "schema function missing or not callable")
    ensure(callable(create_station_chief_v12_autonomous_worker_army_release_candidate_bundle), "bundle function missing or not callable")
    ensure(callable(run_station_chief), "runtime wrapper missing or not callable")

    help_result = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--help"])
    ensure(help_result.returncode == 0, f"Runtime help failed: {help_result.stderr}")
    for flag in [
        "--station-chief-v12-autonomous-worker-army-release-candidate-schema",
        "--station-chief-v12-autonomous-worker-army-release-candidate",
        "--station-chief-v12-army-workers",
        "--station-chief-v12-army-squads",
        "--station-chief-v12-command-manifest",
        "--station-chief-v12-mission-envelopes",
        "--station-chief-v12-dispatch-matrix",
        "--station-chief-v12-army-cycle-plan",
        "--station-chief-v12-readiness-receipts",
        "--station-chief-v12-army-audit",
    ]:
        ensure(flag in help_result.stdout, f"CLI flag missing from help output: {flag}")

    schema = _cli_json(["--station-chief-v12-autonomous-worker-army-release-candidate-schema"])
    ensure(schema["schema_version"] == "12.0.0", "Schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v12_autonomous_worker_army_release_candidate", "Schema type mismatch")
    for key in [
        "no_full_external_prod_agent_army_activation_authorized",
        "no_real_worker_activation_authorized",
        "no_real_tool_invocation_authorized",
        "no_external_tool_invocation_authorized",
        "no_arbitrary_task_execution_authorized",
        "no_user_task_execution_authorized",
        "no_worker_process_start_authorized",
        "no_real_queue_authorized",
        "no_queue_write_authorized",
        "no_live_routing_authorized",
        "no_live_orchestration_authorized",
        "no_api_network_deployment_production_authorized",
    ]:
        ensure(schema[key] is True, f"Schema contract mismatch for {key}")
    required_sections = schema["required_sections"]
    for section_name in [
        "autonomous_worker_army_profiles",
        "autonomous_worker_squad_registry",
        "virtual_army_command_manifest",
        "mission_envelope_registry",
        "autonomy_policy_gate",
        "permissioned_army_dispatch_matrix",
        "virtual_queue_control_record",
        "metadata_only_army_cycle_plan",
        "worker_readiness_receipts",
        "autonomous_worker_army_release_candidate_audit_record",
        "autonomous_worker_army_safety_boundary_matrix",
        "autonomous_worker_army_readiness_summary",
    ]:
        ensure(section_name in required_sections, f"Schema missing required section: {section_name}")

    bundle = create_station_chief_v12_autonomous_worker_army_release_candidate_bundle()
    ensure(bundle["runtime_version"] == "12.0.0", "Bundle version mismatch")
    ensure(bundle["army_release_candidate_status"] == "AUTONOMOUS_WORKER_ARMY_RELEASE_CANDIDATE_READY", "Bundle status mismatch")
    ensure(bundle["worker_count"] == 12, "Bundle worker count mismatch")
    ensure(bundle["squad_count"] == 4, "Bundle squad count mismatch")
    ensure(bundle["mission_envelope_count"] == 4, "Bundle mission envelope count mismatch")
    ensure(bundle["readiness_receipt_count"] == 12, "Bundle readiness receipt count mismatch")
    ensure(bundle["autonomous_worker_profiles_registered"] is True, "Bundle worker registration flag mismatch")
    ensure(bundle["autonomous_worker_squads_registered"] is True, "Bundle squad registration flag mismatch")
    ensure(bundle["virtual_army_command_manifest_created"] is True, "Bundle command manifest flag mismatch")
    ensure(bundle["mission_envelope_registry_created"] is True, "Bundle mission registry flag mismatch")
    ensure(bundle["autonomy_policy_gate_created"] is True, "Bundle policy gate flag mismatch")
    ensure(bundle["permissioned_army_dispatch_matrix_created"] is True, "Bundle dispatch matrix flag mismatch")
    ensure(bundle["virtual_queue_control_record_created"] is True, "Bundle queue control flag mismatch")
    ensure(bundle["metadata_only_army_cycle_plan_created"] is True, "Bundle cycle plan flag mismatch")
    ensure(bundle["worker_readiness_receipts_generated"] is True, "Bundle readiness receipts flag mismatch")
    ensure(bundle["full_external_prod_agent_army_activation_performed"] is False, "Bundle live army flag mismatch")
    ensure(bundle["real_worker_activation_performed"] is False, "Bundle real worker activation flag mismatch")
    ensure(bundle["real_tool_invocation_performed"] is False, "Bundle real tool flag mismatch")
    ensure(bundle["external_tool_invocation_performed"] is False, "Bundle external tool flag mismatch")
    ensure(bundle["real_queue_created"] is False, "Bundle real queue flag mismatch")
    ensure(bundle["queue_write_performed"] is False, "Bundle queue write flag mismatch")
    ensure(bundle["live_task_enqueued"] is False, "Bundle live task enqueue flag mismatch")
    ensure(bundle["live_task_executed"] is False, "Bundle live task execution flag mismatch")
    ensure(bundle["live_worker_routing_performed"] is False, "Bundle live routing flag mismatch")
    ensure(bundle["live_orchestration_performed"] is False, "Bundle live orchestration flag mismatch")
    ensure(bundle["arbitrary_task_execution_performed"] is False, "Bundle arbitrary task flag mismatch")
    ensure(bundle["user_task_execution_performed"] is False, "Bundle user task flag mismatch")
    ensure(bundle["shell_executed"] is False, "Bundle shell execution flag mismatch")
    ensure(bundle["subprocess_started"] is False, "Bundle subprocess flag mismatch")
    ensure(bundle["api_call_performed"] is False, "Bundle api flag mismatch")
    ensure(bundle["network_access_performed"] is False, "Bundle network flag mismatch")
    ensure(bundle["credential_access_performed"] is False, "Bundle credential flag mismatch")
    ensure(bundle["secret_read_performed"] is False, "Bundle secret flag mismatch")
    ensure(bundle["environment_read_performed"] is False, "Bundle environment flag mismatch")
    ensure(bundle["filesystem_mutation_performed"] is False, "Bundle filesystem mutation flag mismatch")
    ensure(bundle["deployment_performed"] is False, "Bundle deployment flag mismatch")
    ensure(bundle["production_execution_performed"] is False, "Bundle production execution flag mismatch")
    ensure(bundle["full_workforce_activation_performed"] is False, "Bundle workforce activation flag mismatch")
    ensure(bundle["v12_1_created"] is False, "Bundle v12.1 flag mismatch")
    ensure(bundle["v13_created"] is False, "Bundle v13 flag mismatch")

    worker_profiles = bundle["autonomous_worker_army_profiles"]
    squad_registry = bundle["autonomous_worker_squad_registry"]
    command_manifest = bundle["virtual_army_command_manifest"]
    mission_envelopes = bundle["mission_envelope_registry"]
    policy_gate = bundle["autonomy_policy_gate"]
    dispatch_matrix = bundle["permissioned_army_dispatch_matrix"]
    queue_control_record = bundle["virtual_queue_control_record"]
    army_cycle_plan = bundle["metadata_only_army_cycle_plan"]
    readiness_receipts = bundle["worker_readiness_receipts"]
    audit_record = bundle["autonomous_worker_army_release_candidate_audit_record"]
    safety_matrix = bundle["autonomous_worker_army_safety_boundary_matrix"]
    readiness_summary = bundle["autonomous_worker_army_readiness_summary"]

    ensure(list(worker_profiles.keys()) == STATION_CHIEF_V12_ARMY_WORKER_IDS, "Worker IDs are not deterministic")
    ensure(len(worker_profiles) == 12, "Expected exactly 12 worker profiles")
    for index, worker_id in enumerate(STATION_CHIEF_V12_ARMY_WORKER_IDS, start=1):
        profile = worker_profiles[worker_id]
        expected_squad = STATION_CHIEF_V12_ARMY_SQUAD_IDS[0 if index <= 3 else 1 if index <= 6 else 2 if index <= 9 else 3]
        ensure(profile["worker_id"] == worker_id, f"Worker id mismatch for {worker_id}")
        ensure(profile["worker_type"] == "autonomous_worker_army_release_candidate_profile", f"Worker type mismatch for {worker_id}")
        ensure(profile["worker_mode"] == "deterministic_local_metadata_only", f"Worker mode mismatch for {worker_id}")
        ensure(profile["worker_index"] == index, f"Worker index mismatch for {worker_id}")
        ensure(profile["assigned_squad_id"] == expected_squad, f"Worker squad mismatch for {worker_id}")
        ensure(profile["autonomy_level"] == "release_candidate_metadata_only", f"Worker autonomy level mismatch for {worker_id}")
        ensure(profile["worker_started"] is False, f"Worker start flag mismatch for {worker_id}")
        ensure(profile["daemon_started"] is False, f"Worker daemon flag mismatch for {worker_id}")
        ensure(profile["background_process_started"] is False, f"Worker background flag mismatch for {worker_id}")
        ensure(profile["subprocess_allowed"] is False, f"Worker subprocess flag mismatch for {worker_id}")
        ensure(profile["shell_allowed"] is False, f"Worker shell flag mismatch for {worker_id}")
        ensure(profile["network_allowed"] is False, f"Worker network flag mismatch for {worker_id}")
        ensure(profile["api_allowed"] is False, f"Worker api flag mismatch for {worker_id}")
        ensure(profile["external_tool_allowed"] is False, f"Worker external tool flag mismatch for {worker_id}")
        ensure(profile["credential_access_allowed"] is False, f"Worker credential flag mismatch for {worker_id}")
        ensure(profile["secret_read_allowed"] is False, f"Worker secret flag mismatch for {worker_id}")
        ensure(profile["environment_read_allowed"] is False, f"Worker environment flag mismatch for {worker_id}")
        ensure(profile["filesystem_mutation_allowed"] is False, f"Worker filesystem flag mismatch for {worker_id}")
        ensure(profile["production_allowed"] is False, f"Worker production flag mismatch for {worker_id}")
        ensure(profile["arbitrary_task_allowed"] is False, f"Worker arbitrary task flag mismatch for {worker_id}")
        ensure(profile["user_task_allowed"] is False, f"Worker user task flag mismatch for {worker_id}")
        ensure(profile["live_execution_allowed"] is False, f"Worker live execution flag mismatch for {worker_id}")
        ensure(profile["max_mission_envelopes_allowed"] == 1, f"Worker mission envelope limit mismatch for {worker_id}")

    ensure(list(squad_registry.keys()) == STATION_CHIEF_V12_ARMY_SQUAD_IDS, "Squad IDs are not deterministic")
    for squad_id in STATION_CHIEF_V12_ARMY_SQUAD_IDS:
        squad = squad_registry[squad_id]
        ensure(squad["squad_id"] == squad_id, f"Squad id mismatch for {squad_id}")
        ensure(squad["squad_name"] in {"planning", "execution", "audit", "recovery"}, f"Squad name mismatch for {squad_id}")
        ensure(squad["squad_type"] == "autonomous_worker_army_release_candidate_squad", f"Squad type mismatch for {squad_id}")
        ensure(squad["squad_mode"] == "deterministic_local_metadata_only", f"Squad mode mismatch for {squad_id}")
        ensure(len(squad["worker_ids"]) == 3, f"Squad worker count mismatch for {squad_id}")
        ensure(squad["worker_count"] == 3, f"Squad declared worker count mismatch for {squad_id}")
        ensure(squad["live_squad_activation_allowed"] is False, f"Squad activation mismatch for {squad_id}")
        ensure(squad["live_execution_allowed"] is False, f"Squad live execution mismatch for {squad_id}")
        ensure(squad["real_worker_start_allowed"] is False, f"Squad worker start mismatch for {squad_id}")
        ensure(squad["queue_write_allowed"] is False, f"Squad queue write mismatch for {squad_id}")
        ensure(squad["tool_invocation_allowed"] is False, f"Squad tool invocation mismatch for {squad_id}")
        ensure(squad["api_allowed"] is False, f"Squad api mismatch for {squad_id}")
        ensure(squad["network_allowed"] is False, f"Squad network mismatch for {squad_id}")
        ensure(squad["production_allowed"] is False, f"Squad production mismatch for {squad_id}")

    ensure(command_manifest["command_manifest_id"] == STATION_CHIEF_V12_VIRTUAL_ARMY_COMMAND_MANIFEST_ID, "Command manifest id mismatch")
    ensure(command_manifest["command_manifest_type"] == "metadata_only_virtual_army_command_manifest", "Command manifest type mismatch")
    ensure(command_manifest["runtime_version"] == "12.0.0", "Command manifest runtime mismatch")
    ensure(command_manifest["worker_count"] == 12, "Command manifest worker count mismatch")
    ensure(command_manifest["squad_count"] == 4, "Command manifest squad count mismatch")
    ensure(command_manifest["command_mode"] == "release_candidate_non_executing_army_readiness", "Command manifest mode mismatch")
    ensure(command_manifest["real_command_dispatch_allowed"] is False, "Command manifest real dispatch mismatch")
    ensure(command_manifest["live_worker_activation_allowed"] is False, "Command manifest live activation mismatch")
    ensure(command_manifest["live_orchestration_allowed"] is False, "Command manifest live orchestration mismatch")
    ensure(command_manifest["external_tool_invocation_allowed"] is False, "Command manifest external tool mismatch")
    ensure(command_manifest["api_network_deployment_production_allowed"] is False, "Command manifest api/network/deployment mismatch")

    ensure(list(mission_envelopes.keys()) == STATION_CHIEF_V12_MISSION_ENVELOPE_IDS, "Mission envelope IDs are not deterministic")
    for index, mission_envelope_id in enumerate(STATION_CHIEF_V12_MISSION_ENVELOPE_IDS, start=1):
        mission = mission_envelopes[mission_envelope_id]
        expected_squad = STATION_CHIEF_V12_ARMY_SQUAD_IDS[index - 1]
        ensure(mission["mission_envelope_id"] == mission_envelope_id, f"Mission id mismatch for {mission_envelope_id}")
        ensure(mission["mission_type"] == "metadata_only_army_readiness_mission", f"Mission type mismatch for {mission_envelope_id}")
        ensure(mission["mission_index"] == index, f"Mission index mismatch for {mission_envelope_id}")
        ensure(mission["assigned_squad_id"] == expected_squad, f"Mission squad mismatch for {mission_envelope_id}")
        ensure(len(mission["assigned_worker_ids"]) == 3, f"Mission worker count mismatch for {mission_envelope_id}")
        ensure(mission["mission_payload"] == {"operation": "army_readiness_metadata_check", "expected_result": "readiness_receipts_recorded"}, f"Mission payload mismatch for {mission_envelope_id}")
        ensure(mission["arbitrary_user_content_allowed"] is False, f"Mission user content mismatch for {mission_envelope_id}")
        ensure(mission["shell_command_allowed"] is False, f"Mission shell mismatch for {mission_envelope_id}")
        ensure(mission["subprocess_allowed"] is False, f"Mission subprocess mismatch for {mission_envelope_id}")
        ensure(mission["network_allowed"] is False, f"Mission network mismatch for {mission_envelope_id}")
        ensure(mission["api_allowed"] is False, f"Mission api mismatch for {mission_envelope_id}")
        ensure(mission["external_tool_allowed"] is False, f"Mission external tool mismatch for {mission_envelope_id}")
        ensure(mission["filesystem_mutation_allowed"] is False, f"Mission filesystem mismatch for {mission_envelope_id}")
        ensure(mission["production_allowed"] is False, f"Mission production mismatch for {mission_envelope_id}")
        ensure(mission["live_execution_allowed"] is False, f"Mission live execution mismatch for {mission_envelope_id}")
        ensure(mission["execution_mode"] == "metadata_readiness_receipt_only", f"Mission execution mode mismatch for {mission_envelope_id}")

    ensure(policy_gate["autonomy_metadata_authorized"] is True, "Policy gate failed to authorize metadata")
    ensure(policy_gate["real_worker_activation_authorized"] is False, "Policy gate incorrectly authorized real worker activation")
    ensure(policy_gate["real_tool_invocation_authorized"] is False, "Policy gate incorrectly authorized real tool invocation")
    ensure(policy_gate["external_tool_invocation_authorized"] is False, "Policy gate incorrectly authorized external tools")
    ensure(policy_gate["real_execution_authorized"] is False, "Policy gate incorrectly authorized real execution")
    ensure(policy_gate["arbitrary_execution_authorized"] is False, "Policy gate incorrectly authorized arbitrary execution")
    ensure(policy_gate["user_task_execution_authorized"] is False, "Policy gate incorrectly authorized user tasks")
    ensure(policy_gate["real_queue_authorized"] is False, "Policy gate incorrectly authorized real queue")
    ensure(policy_gate["queue_write_authorized"] is False, "Policy gate incorrectly authorized queue writes")
    ensure(policy_gate["live_routing_authorized"] is False, "Policy gate incorrectly authorized live routing")
    ensure(policy_gate["live_orchestration_authorized"] is False, "Policy gate incorrectly authorized live orchestration")
    ensure(policy_gate["api_network_deployment_production_authorized"] is False, "Policy gate incorrectly authorized api/network/deployment/production")

    ensure(dispatch_matrix["dispatch_matrix_type"] == "metadata_only_permissioned_army_dispatch_matrix", "Dispatch matrix type mismatch")
    ensure(dispatch_matrix["runtime_version"] == "12.0.0", "Dispatch matrix runtime mismatch")
    ensure(dispatch_matrix["dispatch_count"] == 4, "Dispatch count mismatch")
    ensure(dispatch_matrix["worker_count"] == 12, "Dispatch worker count mismatch")
    ensure(dispatch_matrix["squad_count"] == 4, "Dispatch squad count mismatch")
    ensure(dispatch_matrix["mission_envelope_count"] == 4, "Dispatch mission count mismatch")
    ensure(dispatch_matrix["dispatch_strategy"] == "deterministic_squad_to_mission_envelope_metadata_mapping", "Dispatch strategy mismatch")
    ensure(dispatch_matrix["autonomy_metadata_authorized"] is True, "Dispatch matrix authorization mismatch")
    ensure(dispatch_matrix["real_dispatch_performed"] is False, "Dispatch matrix real dispatch mismatch")
    ensure(dispatch_matrix["live_worker_activation_performed"] is False, "Dispatch matrix live activation mismatch")
    ensure(dispatch_matrix["live_tool_invocation_performed"] is False, "Dispatch matrix live tool mismatch")
    ensure(dispatch_matrix["live_task_routing_performed"] is False, "Dispatch matrix live routing mismatch")
    ensure(dispatch_matrix["live_orchestration_performed"] is False, "Dispatch matrix live orchestration mismatch")
    ensure(dispatch_matrix["queue_write_performed"] is False, "Dispatch matrix queue write mismatch")
    ensure(dispatch_matrix["task_executed"] is False, "Dispatch matrix task execution mismatch")
    ensure(len(dispatch_matrix["dispatch_entries"]) == 4, "Dispatch entries count mismatch")

    ensure(queue_control_record["virtual_queue_control_record_id"] == STATION_CHIEF_V12_VIRTUAL_QUEUE_CONTROL_RECORD_ID, "Queue control record id mismatch")
    ensure(queue_control_record["queue_control_type"] == "metadata_only_virtual_army_queue_control_record", "Queue control record type mismatch")
    ensure(queue_control_record["runtime_version"] == "12.0.0", "Queue control record runtime mismatch")
    ensure(queue_control_record["virtual_queue_mode"] == "deterministic_non_live_army_queue_control", "Queue control record mode mismatch")
    ensure(queue_control_record["mission_envelope_count"] == 4, "Queue control record mission count mismatch")
    ensure(queue_control_record["dispatch_count"] == 4, "Queue control record dispatch count mismatch")
    ensure(queue_control_record["real_queue_created"] is False, "Queue control record real queue mismatch")
    ensure(queue_control_record["queue_write_performed"] is False, "Queue control record queue write mismatch")
    ensure(queue_control_record["live_enqueue_performed"] is False, "Queue control record live enqueue mismatch")
    ensure(queue_control_record["live_dequeue_performed"] is False, "Queue control record live dequeue mismatch")
    ensure(queue_control_record["live_routing_performed"] is False, "Queue control record live routing mismatch")
    ensure(queue_control_record["live_orchestration_performed"] is False, "Queue control record live orchestration mismatch")
    ensure(queue_control_record["scheduler_write_performed"] is False, "Queue control record scheduler write mismatch")
    ensure(queue_control_record["cron_write_performed"] is False, "Queue control record cron write mismatch")
    ensure(queue_control_record["task_executed"] is False, "Queue control record task execution mismatch")

    ensure(army_cycle_plan["army_cycle_plan_type"] == "metadata_only_autonomous_worker_army_cycle_plan", "Cycle plan type mismatch")
    ensure(army_cycle_plan["runtime_version"] == "12.0.0", "Cycle plan runtime mismatch")
    ensure(army_cycle_plan["cycle_mode"] == "release_candidate_non_executing_readiness_cycle", "Cycle plan mode mismatch")
    ensure(army_cycle_plan["cycle_step_count"] == 6, "Cycle plan step count mismatch")
    ensure(army_cycle_plan["cycle_steps"] == [
        "register_worker_profiles_metadata",
        "register_squad_metadata",
        "register_mission_envelopes_metadata",
        "authorize_metadata_only_policy_gate",
        "create_permissioned_dispatch_matrix_metadata",
        "record_worker_readiness_receipts_metadata",
    ], "Cycle plan steps mismatch")
    ensure(army_cycle_plan["autonomy_metadata_authorized"] is True, "Cycle plan authorization mismatch")
    ensure(army_cycle_plan["real_cycle_execution_performed"] is False, "Cycle plan real execution mismatch")
    ensure(army_cycle_plan["live_worker_activation_performed"] is False, "Cycle plan live worker mismatch")
    ensure(army_cycle_plan["live_task_execution_performed"] is False, "Cycle plan live task mismatch")
    ensure(army_cycle_plan["live_tool_invocation_performed"] is False, "Cycle plan live tool mismatch")
    ensure(army_cycle_plan["live_orchestration_performed"] is False, "Cycle plan live orchestration mismatch")
    ensure(army_cycle_plan["api_network_deployment_production_performed"] is False, "Cycle plan api/network/deployment/production mismatch")

    ensure(len(readiness_receipts) == 12, "Readiness receipt count mismatch")
    ensure(list(readiness_receipts.keys()), "Readiness receipts must not be empty")
    receipt_worker_ids = set()
    for receipt_id, receipt in readiness_receipts.items():
        ensure(receipt["receipt_type"] == "metadata_only_worker_army_readiness_receipt", f"Receipt type mismatch for {receipt_id}")
        ensure(receipt["readiness_status"] == "ARMY_WORKER_METADATA_READY", f"Receipt readiness status mismatch for {receipt_id}")
        ensure(receipt["readiness_receipt_generated"] is True, f"Receipt generation flag mismatch for {receipt_id}")
        ensure(receipt["worker_started"] is False, f"Receipt worker start mismatch for {receipt_id}")
        ensure(receipt["agent_started"] is False, f"Receipt agent start mismatch for {receipt_id}")
        ensure(receipt["daemon_started"] is False, f"Receipt daemon start mismatch for {receipt_id}")
        ensure(receipt["external_tool_invocation_performed"] is False, f"Receipt external tool mismatch for {receipt_id}")
        ensure(receipt["live_dispatch_performed"] is False, f"Receipt live dispatch mismatch for {receipt_id}")
        ensure(receipt["task_executed"] is False, f"Receipt task execution mismatch for {receipt_id}")
        ensure(receipt["api_call_performed"] is False, f"Receipt api mismatch for {receipt_id}")
        ensure(receipt["network_access_performed"] is False, f"Receipt network mismatch for {receipt_id}")
        ensure(receipt["filesystem_mutation_performed"] is False, f"Receipt filesystem mismatch for {receipt_id}")
        ensure(receipt["production_execution_performed"] is False, f"Receipt production mismatch for {receipt_id}")
        ensure(receipt["arbitrary_task_execution_performed"] is False, f"Receipt arbitrary task mismatch for {receipt_id}")
        ensure(receipt["user_task_execution_performed"] is False, f"Receipt user task mismatch for {receipt_id}")
        receipt_worker_ids.add(receipt["worker_id"])
    ensure(receipt_worker_ids == set(STATION_CHIEF_V12_ARMY_WORKER_IDS), "Receipt worker coverage mismatch")

    ensure(audit_record["audit_type"] == "autonomous_worker_army_release_candidate_audit", "Audit type mismatch")
    ensure(audit_record["runtime_version"] == "12.0.0", "Audit runtime mismatch")
    ensure(audit_record["worker_count"] == 12, "Audit worker count mismatch")
    ensure(audit_record["squad_count"] == 4, "Audit squad count mismatch")
    ensure(audit_record["mission_envelope_count"] == 4, "Audit mission count mismatch")
    ensure(audit_record["readiness_receipt_count"] == 12, "Audit receipt count mismatch")
    ensure(audit_record["autonomy_metadata_authorized"] is True, "Audit authorization mismatch")
    ensure(audit_record["all_readiness_receipts_recorded"] is True, "Audit receipt recording mismatch")
    for key in [
        "no_real_worker_activation",
        "no_agent_started",
        "no_daemon_started",
        "no_real_tool_invocation",
        "no_external_tool_invocation",
        "no_real_queue_created",
        "no_queue_write",
        "no_live_task_enqueued",
        "no_live_task_executed",
        "no_live_worker_routing",
        "no_live_orchestration",
        "no_shell_executed",
        "no_subprocess_started",
        "no_api_call",
        "no_network_access",
        "no_filesystem_mutation",
        "no_production_execution",
        "no_arbitrary_task_execution",
        "no_user_task_execution",
        "no_full_external_prod_agent_army_activation",
    ]:
        ensure(audit_record[key] is True, f"Audit negative assertion mismatch for {key}")

    ensure(all(value == "DENIED" for value in safety_matrix.values()), "Safety boundary matrix contains non-denied action")
    for action in [
        "full_external_prod_agent_army_activation",
        "real_worker_activation",
        "real_tool_invocation",
        "external_tool_invocation",
        "worker_process_start",
        "daemon_start",
        "background_process_start",
        "agent_start",
        "subprocess_start",
        "shell_execution",
        "arbitrary_command_execution",
        "arbitrary_task_execution",
        "user_task_execution",
        "real_queue_creation",
        "queue_write",
        "scheduler_write",
        "cron_write",
        "live_task_enqueue",
        "live_task_dequeue",
        "live_task_execution",
        "live_worker_routing",
        "live_orchestration",
        "api_call",
        "network_access",
        "socket_access",
        "dns_resolution",
        "credential_use",
        "secret_read",
        "environment_read",
        "deployment",
        "production_execution",
        "database_mutation",
        "full_workforce_activation",
        "v12_1_creation",
        "v13_creation",
    ]:
        ensure(safety_matrix.get(action) == "DENIED", f"Safety boundary missing denial for {action}")

    ensure(readiness_summary["autonomous_worker_profiles_registered"] is True, "Readiness summary worker profile flag mismatch")
    ensure(readiness_summary["autonomous_worker_squads_registered"] is True, "Readiness summary squad flag mismatch")
    ensure(readiness_summary["virtual_army_command_manifest_created"] is True, "Readiness summary command manifest flag mismatch")
    ensure(readiness_summary["mission_envelope_registry_created"] is True, "Readiness summary mission registry flag mismatch")
    ensure(readiness_summary["autonomy_policy_gate_created"] is True, "Readiness summary policy gate flag mismatch")
    ensure(readiness_summary["permissioned_dispatch_matrix_created"] is True, "Readiness summary dispatch matrix flag mismatch")
    ensure(readiness_summary["virtual_queue_control_record_created"] is True, "Readiness summary queue control flag mismatch")
    ensure(readiness_summary["metadata_only_army_cycle_plan_created"] is True, "Readiness summary cycle plan flag mismatch")
    ensure(readiness_summary["metadata_only_worker_readiness_receipts_generated"] is True, "Readiness summary readiness receipts flag mismatch")

    runtime_result = run_station_chief("build station chief v12 autonomous worker army release candidate")
    ensure(runtime_result["station_chief_runtime_version"] == "12.0.0", "Runtime wrapper version mismatch")
    ensure(runtime_result["runtime_status"] == "station_chief_v12_autonomous_worker_army_release_candidate", "Runtime wrapper status mismatch")
    ensure(isinstance(runtime_result.get("next_step"), str) and runtime_result["next_step"].startswith("Next step:"), "Runtime wrapper next step mismatch")
    ensure(runtime_result["baseline_preserved"] is True, "Runtime wrapper baseline mismatch")

    index_entry = build_runtime_index_entry(runtime_result, generate_run_id("build station chief v12 autonomous worker army release candidate"))
    ensure(index_entry["runtime_version"] == "12.0.0", "Runtime index version mismatch")
    ensure(index_entry["artifact_type"] == "station_chief_runtime_v12_0_artifacts", "Runtime index artifact type mismatch")
    ensure(generate_run_id("build station chief v12 autonomous worker army release candidate").startswith("station-chief-v12-0-"), "Run ID prefix mismatch")

    assert_index = create_station_chief_v12_autonomous_worker_army_release_candidate_bundle()["bundle_digest"]
    ensure(isinstance(assert_index, str) and len(assert_index) == 64, "Bundle digest mismatch")
    ensure(canonical_json({"a": 1, "b": 2}) == '{"a":1,"b":2}', "Canonical JSON mismatch")
    ensure(sha256_digest({"a": 1}) == sha256_digest({"a": 1}), "Digest function must be deterministic")
    ensure(normalize_label(None, "planning") == "planning", "Label normalization default mismatch")
    ensure(normalize_label("Planning Squad", "planning") == "planning-squad", "Label normalization mismatch")

    _assert_no_future_files()
    _assert_protected_paths_unmodified()

    ensure("Station Chief Runtime upgraded to v12.0.0" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime_readme.md"), "README missing v12 doctrine")
    ensure("v12.1 or v13.0 requires explicit operator instruction" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime_readme.md"), "README missing next-step label")
    ensure("Station Chief Runtime upgraded to v12.0.0" in _source_text(REPO_ROOT / "09_exports/station_chief_runtime_skeleton_report.md"), "Skeleton report missing v12 doctrine")
    ensure("v12.1 or v13.0 requires explicit operator instruction" in _source_text(REPO_ROOT / "09_exports/station_chief_runtime_skeleton_report.md"), "Skeleton report missing next-step label")

    _ensure_forbidden_patterns_absent(_source_text(REPO_ROOT / "10_runtime/station_chief_v12_autonomous_worker_army_release_candidate.py"), [
        "TODO",
        "NotImplemented",
        "open(",
        "requests",
        "eval(",
        "exec(",
        "compile(",
        "__import__(",
    ], "v12 module")

    _run_prior_validator("scripts/validate_station_chief_runtime_v11_0.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v10_0.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v9_0.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v8_0.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_6.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_5.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_4.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_3.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_2.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_1.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v6_0.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_9.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_8.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_7.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_6.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_5.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_4.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_3.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_2.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_1.py")
    _run_prior_validator("scripts/validate_station_chief_runtime_v5_0.py")

    print("STATION_CHIEF_RUNTIME_V12_0_VALIDATION_PASS")


if __name__ == "__main__":
    main()
