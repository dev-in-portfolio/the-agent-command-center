#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
NEW_MODULE = REPO_ROOT / "10_runtime" / "station_chief_first_tiny_real_world_supervised_execution_candidate.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
V4_REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v4_0_report.md"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
WRAPPER_FILES = [
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_9.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_8.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_7.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_6.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_5.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_4.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_3.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_2.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_1.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_0.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v2_9.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v2_8.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_skeleton.py",
]
V41_GLOB_PATTERNS = ["*v4_1*"]
EXPECTED_V4_TOKEN = "YES_I_APPROVE_FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE"
HUMAN_OPERATOR = "Devin O’Rourke"
DANGEROUS_KEYS = {
    "external_actions_taken",
    "live_external_action_performed",
    "live_api_call_performed",
    "network_access_performed",
    "socket_opened",
    "dns_resolution_performed",
    "outbound_connection_performed",
    "inbound_connection_performed",
    "webhook_call_performed",
    "credential_vault_access_performed",
    "credentials_used",
    "secrets_read",
    "environment_read",
    "tokens_read",
    "api_keys_read",
    "oauth_used",
    "service_account_used",
    "deployment_performed",
    "deployment_rollback_performed",
    "production_execution_performed",
    "production_activation_performed",
    "real_external_tool_invocation_performed",
    "real_task_execution_performed",
    "live_task_assignment_performed",
    "live_worker_routing_performed",
    "live_orchestration_performed",
    "worker_processes_started",
    "real_rollback_performed",
    "real_recovery_performed",
    "processes_terminated",
    "workers_terminated",
    "production_state_changed",
    "repo_files_modified",
    "execution_authorized",
    "full_workforce_activation_performed",
}

ALLOWED_DIRTY_PATHS = {
    "09_exports/station_chief_runtime_v4_0_report.md",
    "09_exports/station_chief_runtime_skeleton_report.md",
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_runtime_readme.md",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_release_lock.py",
    "10_runtime/station_chief_first_tiny_real_world_supervised_execution_candidate.py",
    "scripts/validate_station_chief_runtime_v4_0.py",
    "scripts/validate_station_chief_runtime_v3_9.py",
    "scripts/validate_station_chief_runtime_v3_8.py",
    "scripts/validate_station_chief_runtime_v3_7.py",
    "scripts/validate_station_chief_runtime_v3_6.py",
    "scripts/validate_station_chief_runtime_v3_5.py",
    "scripts/validate_station_chief_runtime_v3_4.py",
    "scripts/validate_station_chief_runtime_v3_3.py",
    "scripts/validate_station_chief_runtime_v3_2.py",
    "scripts/validate_station_chief_runtime_v3_1.py",
    "scripts/validate_station_chief_runtime_v3_0.py",
    "scripts/validate_station_chief_runtime_v2_9.py",
    "scripts/validate_station_chief_runtime_v2_8.py",
    "scripts/validate_station_chief_runtime_skeleton.py",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def run_json(args: list[str]) -> dict:
    proc = run_command(args)
    if proc.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(args)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid json from {' '.join(args)}: {exc}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}") from exc


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def scan_dangerous_booleans(value: object, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key.endswith("_verification") or key.endswith("_verification_record"):
                continue
            if key in DANGEROUS_KEYS and item is True:
                hits.append(next_path)
            hits.extend(scan_dangerous_booleans(item, next_path))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            hits.extend(scan_dangerous_booleans(item, f"{path}[{idx}]"))
    return hits


def ensure_only_allowed_changes() -> None:
    proc = run_command(["git", "status", "--short"])
    ensure(proc.returncode == 0, "git status --short failed")
    dirty = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    for line in dirty:
        # git status --short emits entries like "M path" or "?? path".
        # Split once on whitespace and keep the actual path intact.
        parts = line.split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else ""
        if "__pycache__" in path:
            continue
        ensure(path in ALLOWED_DIRTY_PATHS, f"unexpected dirty file: {line}")


def ensure_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        ensure(snippet in text, f"{path.relative_to(REPO_ROOT)} missing snippet: {snippet}")


def main() -> None:
    for path in [RUNTIME, NEW_MODULE, README, SKELETON, V4_REPORT, RELEASE_LOCK, ADAPTERS]:
        ensure(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}")
    for pattern in V41_GLOB_PATTERNS:
        for path in REPO_ROOT.rglob(pattern):
            ensure("v4_1" not in path.name.lower(), f"forbidden v4.1 file unexpectedly exists: {path.relative_to(REPO_ROOT)}")

    ensure_only_allowed_changes()

    help_text = run_command(["python3", str(RUNTIME), "--help"]).stdout
    for flag in [
        "--first-tiny-real-world-supervised-execution-candidate-schema",
        "--first-tiny-real-world-supervised-execution-candidate",
        "--write-first-tiny-real-world-supervised-execution-candidate",
        "--v4-candidate-label",
        "--v4-candidate-confirm-token",
        "--v4-human-operator",
        "--v4-artifact-name",
    ]:
        ensure(flag in help_text, f"missing CLI flag: {flag}")

    demo = run_json(["python3", str(RUNTIME), "--demo"])
    ensure(demo["station_chief_runtime_version"] == "4.0.0", "demo runtime version mismatch")
    ensure(demo["runtime_status"] == "first_tiny_real_world_supervised_execution_candidate", "demo runtime status mismatch")
    ensure(demo["release_status"] == "STABLE_LOCKED", "demo release status mismatch")
    ensure(not scan_dangerous_booleans(demo), f"dangerous booleans found in demo: {scan_dangerous_booleans(demo)}")

    fixture = run_json(["python3", str(RUNTIME), "--fixture-test"])
    ensure(fixture.get("fixture_test_status") in {"PASS", "PASSED"} or fixture.get("failed") in {0, False}, "fixture-test did not report pass")

    fixture_cli = run_command(["python3", str(REPO_ROOT / "10_runtime" / "station_chief_fixture_tests.py")])
    ensure(fixture_cli.returncode == 0, f"fixture tests failed\nstdout:\n{fixture_cli.stdout}\nstderr:\n{fixture_cli.stderr}")

    stable = run_json(["python3", str(RUNTIME), "--stable-release-manifest"])
    stable_manifest = stable.get("stable_release_manifest", stable)
    ensure(stable_manifest["runtime_version"] == "4.0.0", "stable release manifest version mismatch")
    ensure(not scan_dangerous_booleans(stable), f"dangerous booleans found in stable manifest: {scan_dangerous_booleans(stable)}")

    schema = run_json(["python3", str(RUNTIME), "--first-tiny-real-world-supervised-execution-candidate-schema"])
    ensure(schema["first_tiny_real_world_supervised_execution_candidate_schema_version"] == "4.0.0", "schema version mismatch")
    ensure(schema["schema_status"] == "FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_LOCAL_ONLY", "schema status mismatch")
    ensure(schema["candidate_type"] == "local_deterministic_reversible_proof_artifact", "candidate type mismatch")
    ensure(schema["required_confirmation_token"] == EXPECTED_V4_TOKEN, "schema token mismatch")
    ensure(schema["baseline_preserved"] is True, "schema baseline invariant missing")
    ensure(schema["local_proof_artifact_write_performed"] is False, "schema write flag should be false")
    ensure(not scan_dangerous_booleans(schema), f"dangerous booleans found in schema: {scan_dangerous_booleans(schema)}")

    no_token = run_json(["python3", str(RUNTIME), "--command", "check please", "--first-tiny-real-world-supervised-execution-candidate", "--json"])
    gate = no_token["first_tiny_real_world_supervised_execution_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is False, "no-token path should block")
    ensure(gate["local_candidate_records_authorized"] is False, "no-token path should block records")
    ensure(gate["local_proof_artifact_write_authorized"] is False, "no-token path should block writes")
    ensure(gate["gate_status"] == "BLOCKED_PENDING_V4_LOCAL_CANDIDATE_APPROVAL", "no-token gate status mismatch")
    ensure(no_token["local_proof_artifact_execution_record"]["local_proof_artifact_write_performed"] is False, "no-token path should not write")
    ensure(not scan_dangerous_booleans(no_token), f"dangerous booleans found in no-token output: {scan_dangerous_booleans(no_token)}")

    bad_token = run_json(["python3", str(RUNTIME), "--command", "check please", "--first-tiny-real-world-supervised-execution-candidate", "--v4-candidate-confirm-token", "BAD_TOKEN", "--v4-human-operator", HUMAN_OPERATOR, "--json"])
    gate = bad_token["first_tiny_real_world_supervised_execution_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is False, "bad-token path should block")
    ensure(gate["local_candidate_records_authorized"] is False, "bad-token path should block records")
    ensure(gate["local_proof_artifact_write_authorized"] is False, "bad-token path should block writes")
    ensure(gate["gate_status"] == "BLOCKED_PENDING_V4_LOCAL_CANDIDATE_APPROVAL", "bad-token gate status mismatch")
    ensure(not scan_dangerous_booleans(bad_token), f"dangerous booleans found in bad-token output: {scan_dangerous_booleans(bad_token)}")

    valid_token = run_json(["python3", str(RUNTIME), "--command", "check please", "--first-tiny-real-world-supervised-execution-candidate", "--v4-candidate-confirm-token", EXPECTED_V4_TOKEN, "--v4-human-operator", HUMAN_OPERATOR, "--json"])
    gate = valid_token["first_tiny_real_world_supervised_execution_candidate_approval_gate"]
    ensure(gate["confirmation_token_valid"] is True, "valid-token path should authorize records")
    ensure(gate["local_candidate_records_authorized"] is True, "valid-token path should authorize records")
    ensure(gate["local_proof_artifact_write_authorized"] is False, "valid-token no-output-dir path should not authorize writes")
    ensure(valid_token["local_proof_artifact_execution_record"]["local_proof_artifact_write_performed"] is False, "valid-token no-write path should not write")
    ensure(not scan_dangerous_booleans(valid_token), f"dangerous booleans found in valid-token output: {scan_dangerous_booleans(valid_token)}")

    with tempfile.TemporaryDirectory(prefix="station_chief_v4_candidate_", dir="/tmp") as temp_dir:
        temp_path = Path(temp_dir)
        write_result = run_json(["python3", str(RUNTIME), "--command", "check please", "--write-first-tiny-real-world-supervised-execution-candidate", temp_dir, "--v4-candidate-confirm-token", EXPECTED_V4_TOKEN, "--v4-human-operator", HUMAN_OPERATOR])
        ensure(write_result["local_proof_artifact_write_performed"] is True, "write flag should write artifact")
        ensure(write_result["first_tiny_real_world_supervised_execution_candidate_dir"] == temp_dir, "write flag output dir mismatch")
        artifact_path = Path(write_result["artifact_path"])
        ensure(artifact_path.exists(), "written artifact missing")
        ensure(temp_path in artifact_path.parents, "artifact path escaped output directory")
        artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
        ensure(artifact_data["runtime_version"] == "4.0.0", "artifact runtime version mismatch")
        ensure(artifact_data["approval_token_valid"] is True, "artifact token flag mismatch")
        ensure(artifact_data["timestamp_mode"] == "deterministic_no_wall_clock_timestamp", "artifact timestamp mode mismatch")
        ensure(not scan_dangerous_booleans(write_result), f"dangerous booleans found in write output: {scan_dangerous_booleans(write_result)}")

    with tempfile.TemporaryDirectory(prefix="station_chief_v4_full_", dir="/tmp") as run_dir, tempfile.TemporaryDirectory(prefix="station_chief_v4_registry_", dir="/tmp") as reg_dir:
        full = run_json(["python3", str(RUNTIME), "--command", "check please", "--write-artifacts", run_dir, "--registry-dir", reg_dir, "--first-tiny-real-world-supervised-execution-candidate", "--v4-candidate-confirm-token", EXPECTED_V4_TOKEN, "--v4-human-operator", HUMAN_OPERATOR])
        artifact_summary = full["artifact_write_summary"]
        ensure(artifact_summary["run_id"].startswith("station-chief-v4-0-check-please-"), "run id prefix mismatch")
        artifact_dir = Path(artifact_summary["artifact_dir"])
        registry_dir = Path(artifact_summary["registry_dir"])
        ensure(artifact_dir.exists(), "artifact directory missing")
        ensure(registry_dir.exists(), "registry directory missing")
        manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
        run_registry = json.loads((registry_dir / "run_registry.json").read_text(encoding="utf-8"))
        runtime_index = json.loads((registry_dir / "runtime_index.json").read_text(encoding="utf-8"))
        ensure(manifest["runtime_version"] == "4.0.0", "manifest runtime version mismatch")
        ensure(manifest["artifact_type"] == "station_chief_runtime_v4_0_artifacts", "manifest artifact type mismatch")
        ensure(run_registry["registry_version"] == "4.0.0", "registry version mismatch")
        ensure(runtime_index["index_version"] == "4.0.0", "index version mismatch")
        ensure(manifest["baseline_preserved"] is True, "manifest baseline invariant mismatch")
        ensure(manifest["external_actions_taken"] is False, "manifest external actions should be false")
        ensure(not scan_dangerous_booleans(full), f"dangerous booleans found in full writer output: {scan_dangerous_booleans(full)}")

    ensure_contains(README, ["Station Chief Runtime v4.0.0", "one local deterministic reversible proof artifact"])
    ensure_contains(SKELETON, ["Station Chief Runtime upgraded to v4.0.0", "build post-action verification and audit review"])
    ensure_contains(V4_REPORT, ["Station Chief Runtime v4.0.0", "Devin O’Rourke", "post-action verification and audit review"])

    for wrapper in WRAPPER_FILES:
        text = wrapper.read_text(encoding="utf-8")
        ensure("runpy.run_path" in text, f"wrapper missing runpy handoff: {wrapper.relative_to(REPO_ROOT)}")
        if wrapper.name == "validate_station_chief_runtime_v3_9.py":
            ensure("validate_station_chief_runtime_v4_0.py" in text, f"v3_9 wrapper not delegated to v4 validator: {wrapper.relative_to(REPO_ROOT)}")
        else:
            ensure(
                "validate_station_chief_runtime_v3_9.py" in text or "validate_station_chief_runtime_v4_0.py" in text,
                f"wrapper not delegated through validator chain: {wrapper.relative_to(REPO_ROOT)}",
            )

    print("PASS: Station Chief Runtime v4.0 valid.")


if __name__ == "__main__":
    main()
