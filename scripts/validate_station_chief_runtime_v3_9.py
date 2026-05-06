#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
MODULE = REPO_ROOT / "10_runtime" / "station_chief_live_external_action_final_preflight_gate.py"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v3_9_report.md"
PRE_V4_REPORT = REPO_ROOT / "09_exports" / "station_chief_pre_v4_readiness_deep_dive_report.md"
PRE_V4_SUMMARY = REPO_ROOT / "09_exports" / "station_chief_pre_v4_readiness_summary.json"
OLDER_VALIDATORS = [
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
ACCIDENTAL_V4_FILES = [
    REPO_ROOT / "10_runtime" / "station_chief_first_tiny_real_world_supervised_execution_candidate.py",
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_0.py",
    REPO_ROOT / "09_exports" / "station_chief_runtime_v4_0_report.md",
]

REQUIRED_FILES = [
    RUNTIME,
    MODULE,
    ADAPTERS,
    RELEASE_LOCK,
    README,
    SKELETON,
    REPORT,
    PRE_V4_REPORT,
    PRE_V4_SUMMARY,
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_9.py",
]


def err(message: str, errors: list[str]) -> None:
    errors.append(message)


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


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        err(message, errors)


def check_strings(path: Path, required: list[str], forbidden: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in required:
        require(token in text, f"{path.relative_to(REPO_ROOT)} missing required token: {token}", errors)
    for token in forbidden:
        require(token not in text, f"{path.relative_to(REPO_ROOT)} contains forbidden token: {token}", errors)


def check_exact_file_strings(path: Path, required: list[str], forbidden: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in required:
        require(token in text, f"{path.relative_to(REPO_ROOT)} missing required token: {token}", errors)
    for token in forbidden:
        require(token not in text, f"{path.relative_to(REPO_ROOT)} contains forbidden executable pattern: {token}", errors)


def check_no_accidental_v4_files(errors: list[str]) -> None:
    for path in ACCIDENTAL_V4_FILES:
        require(not path.exists(), f"accidental v4.0 file exists: {path.relative_to(REPO_ROOT)}", errors)


def check_prefix_and_bridge_safety(errors: list[str]) -> None:
    runtime_text = RUNTIME.read_text(encoding="utf-8")
    module_text = MODULE.read_text(encoding="utf-8")
    release_lock_text = RELEASE_LOCK.read_text(encoding="utf-8")
    for text, label in [
        (runtime_text, "runtime"),
        (module_text, "live gate module"),
        (release_lock_text, "release lock"),
    ]:
        require("3.9.0" in text, f"{label} missing 3.9.0 marker", errors)
    for token in [
        "station-chief-v3-9-",
        "live-external-action-final-preflight-gate-v3-9-",
    ]:
        require(token in runtime_text or token in module_text, f"v3.9 surfaces missing deterministic prefix: {token}", errors)
    for token in [
        "v3-8-",
        "v3-7-",
        "v3-6-",
        "v3-5-",
        "v3-4-",
    ]:
        require(token not in module_text, f"live gate module contains stale deterministic prefix: {token}", errors)
        require(token not in release_lock_text, f"release lock contains stale deterministic prefix: {token}", errors)
    require('"next_phase": "First Tiny Real-World Supervised Execution Candidate"' in release_lock_text, "release lock next layer incorrect", errors)
    require("ready_for_first_tiny_real_world_supervised_execution_candidate" in module_text, "live gate bridge key missing", errors)


def check_old_validator_delegation(errors: list[str]) -> None:
    for path in OLDER_VALIDATORS:
        text = path.read_text(encoding="utf-8")
        require("validate_station_chief_runtime_v3_9.py" in text, f"{path.relative_to(REPO_ROOT)} does not reference v3.9 validator", errors)
        require("runpy.run_path" in text, f"{path.relative_to(REPO_ROOT)} does not delegate with runpy.run_path", errors)


def check_pre_v4_artifacts(errors: list[str]) -> None:
    require(PRE_V4_REPORT.exists(), "missing pre-v4 readiness report", errors)
    require(PRE_V4_SUMMARY.exists(), "missing pre-v4 readiness summary", errors)
    summary = json.loads(PRE_V4_SUMMARY.read_text(encoding="utf-8"))
    require(summary.get("pre_v4_readiness_review_version") == "0.1", "pre-v4 summary version incorrect", errors)
    require(summary.get("runtime_version") == "3.9.0", "pre-v4 summary runtime version incorrect", errors)
    require(summary.get("current_layer") == "Live External Action Final Preflight Gate", "pre-v4 summary current layer incorrect", errors)
    require(summary.get("next_layer") == "First Tiny Real-World Supervised Execution Candidate", "pre-v4 summary next layer incorrect", errors)
    require(summary.get("v4_0_built") is False, "pre-v4 summary v4.0 built should be false", errors)
    require(summary.get("ready_for_v4_0_prompt") is True, "pre-v4 summary readiness for v4.0 prompt should be true", errors)
    require(summary.get("ready_for_v4_0_execution") is False, "pre-v4 summary readiness for v4.0 execution should be false", errors)
    require(summary.get("recommended_v4_0_candidate") == "local deterministic reversible proof artifact in explicit output directory", "pre-v4 recommended candidate incorrect", errors)
    guards = summary.get("guards", {})
    for key in [
        "stale_prefix_scan_passed",
        "forbidden_pattern_scan_passed",
        "old_validator_delegation_checked",
        "artifact_manifest_checked",
        "registry_index_checked",
        "v4_accidental_implementation_absent",
    ]:
        require(guards.get(key) is True, f"pre-v4 guard false: {key}", errors)
    scope = summary.get("scope", {})
    for key in [
        "baseline_files_modified",
        "devinization_overlays_modified",
        "generated_artifact_directories_committed",
        "dashboard_exports_modified",
        "ownership_metadata_modified",
    ]:
        require(scope.get(key) is False, f"pre-v4 scope flag should be false: {key}", errors)
    validator_status = summary.get("validator_status", {})
    require(validator_status.get("v3_9_validator_passed") is True, "pre-v4 validator status v3.9 should be true", errors)
    require(validator_status.get("validator_chain_passed") is True, "pre-v4 validator chain should be true", errors)
    blockers = summary.get("blockers", [])
    require(blockers == [], "pre-v4 summary blockers should be empty", errors)


def check_pre_v4_docs(errors: list[str]) -> None:
    for path in [README, SKELETON, REPORT]:
        text = path.read_text(encoding="utf-8")
        require("Pre-v4.0 readiness hardening pass" in text, f"{path.relative_to(REPO_ROOT)} missing pre-v4 note", errors)
    require("v4.0 is not built" in PRE_V4_REPORT.read_text(encoding="utf-8"), "pre-v4 report missing v4.0 not built statement", errors)


def check_demo(errors: list[str]) -> None:
    demo = run_json([sys.executable, str(RUNTIME), "--demo"])
    require(demo.get("station_chief_runtime_version") == "3.9.0", "demo runtime version is not 3.9.0", errors)
    require(demo.get("runtime_status") == "live_external_action_final_preflight_gate", "demo runtime status incorrect", errors)
    require(demo.get("release_status") == "STABLE_LOCKED", "demo release status incorrect", errors)
    evidence = demo.get("evidence", {})
    for key in [
        "baseline_preserved",
        "live_external_action_final_preflight_gate_available",
        "live_external_action_final_preflight_gate_preview_only",
        "live_external_action_final_preflight_gate_requires_token",
        "live_external_action_final_preflight_gate_does_not_call_live_apis",
        "live_external_action_final_preflight_gate_does_not_use_network_access",
        "live_external_action_final_preflight_gate_does_not_open_sockets",
        "live_external_action_final_preflight_gate_does_not_resolve_dns",
        "live_external_action_final_preflight_gate_does_not_make_outbound_connections",
        "live_external_action_final_preflight_gate_does_not_use_credentials",
        "live_external_action_final_preflight_gate_does_not_read_secrets",
        "live_external_action_final_preflight_gate_does_not_read_environment",
        "live_external_action_final_preflight_gate_does_not_deploy",
        "live_external_action_final_preflight_gate_does_not_execute_production",
        "live_external_action_final_preflight_gate_does_not_activate_production",
        "live_external_action_final_preflight_gate_does_not_assign_live_tasks",
        "live_external_action_final_preflight_gate_does_not_route_live_workers",
        "live_external_action_final_preflight_gate_does_not_perform_live_orchestration",
        "live_external_action_final_preflight_gate_does_not_start_worker_processes",
        "live_external_action_final_preflight_gate_does_not_modify_repo_files",
    ]:
        require(evidence.get(key) is True or demo.get(key) is True, f"demo missing true evidence: {key}", errors)
    require(evidence.get("external_actions_taken") is False, "demo external_actions_taken not false", errors)


def check_fixture_tests(errors: list[str]) -> None:
    fixture = run_json([sys.executable, str(RUNTIME), "--fixture-test"])
    require(fixture.get("fixture_test_status") == "PASS", "fixture tests failed", errors)
    require(fixture.get("runtime_version") == "3.9.0", "fixture runtime version incorrect", errors)
    require(fixture.get("case_count") == 5, "fixture case count incorrect", errors)
    require(fixture.get("failed") == 0, "fixture failed count not zero", errors)


def check_schema(errors: list[str]) -> None:
    schema = run_json([sys.executable, str(RUNTIME), "--live-external-action-final-preflight-gate-schema"])
    require(schema.get("live_external_action_final_preflight_gate_schema_version") == "3.9.0", "schema version incorrect", errors)
    require(schema.get("schema_status") == "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_PREVIEW_ONLY", "schema status incorrect", errors)
    for section in [
        "live_external_action_final_preflight_gate_approval_gate",
        "tiny_action_candidate_boundary_contract",
        "live_external_action_non_execution_contract",
        "blast_radius_ceiling_contract",
        "human_final_approval_requirement",
        "credential_secret_environment_re_denial_proof",
        "network_socket_api_re_denial_proof",
        "deployment_production_re_denial_proof",
        "rollback_recovery_availability_assertion",
        "final_preflight_ledger",
        "first_tiny_real_world_supervised_execution_candidate_bridge",
    ]:
        require(section in set(schema.get("required_sections", [])), f"schema missing required section: {section}", errors)
    for mode in [
        "live_api_call",
        "network_access",
        "socket_connection",
        "dns_resolution",
        "outbound_connection",
        "inbound_connection",
        "webhook_call",
        "credential_use",
        "credential_vault_access",
        "secret_read",
        "environment_variable_read",
        "deployment",
        "deployment_rollback",
        "production_execution",
        "production_activation",
        "real_external_tool_invocation",
        "real_task_execution",
        "live_task_assignment",
        "live_worker_routing",
        "live_orchestration",
        "worker_process_start",
        "automatic_execution",
        "queued_action_execution",
        "auto_approval",
        "approval_bypass",
        "actual_replay_execution",
        "real_rollback_execution",
        "real_recovery_execution",
        "process_termination",
        "worker_termination",
        "production_state_change",
        "full_workforce_activation",
    ]:
        require(mode in set(schema.get("blocked_preflight_modes", [])), f"schema missing blocked mode: {mode}", errors)
    require("YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE" in set(schema.get("required_confirmation_tokens", [])), "schema missing token requirement", errors)


def check_no_token_and_token_paths(errors: list[str]) -> None:
    base = [sys.executable, str(RUNTIME), "--command", "check please", "--live-external-action-final-preflight-gate", "--json"]
    no_token = run_json(base)
    require("live_external_action_final_preflight_gate_bundle" in no_token, "no-token result missing proof bundle", errors)
    bundle = no_token.get("live_external_action_final_preflight_gate_bundle", {})
    gate = no_token.get("live_external_action_final_preflight_gate_approval_gate", {})
    require(gate.get("gate_status") == "BLOCKED_PENDING_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_APPROVAL", "no-token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is False, "no-token validity incorrect", errors)
    require(gate.get("local_final_preflight_records_authorized") is False, "no-token local records authorization incorrect", errors)
    require(gate.get("live_external_action_authorized") is False, "no-token live external action authorization incorrect", errors)
    require(bundle.get("tiny_action_candidate_boundary_contract", {}).get("contract_status") == "BLOCKED", "no-token tiny action contract incorrect", errors)
    require(bundle.get("live_external_action_non_execution_contract", {}).get("contract_status") == "BLOCKED", "no-token non-execution contract incorrect", errors)
    require(bundle.get("blast_radius_ceiling_contract", {}).get("contract_status") == "BLOCKED", "no-token blast radius contract incorrect", errors)
    require(bundle.get("human_final_approval_requirement", {}).get("requirement_status") == "BLOCKED", "no-token human approval requirement incorrect", errors)
    require(bundle.get("credential_secret_environment_re_denial_proof", {}).get("proof_status") == "BLOCKED", "no-token credential denial proof incorrect", errors)
    require(bundle.get("network_socket_api_re_denial_proof", {}).get("proof_status") == "BLOCKED", "no-token network/socket proof incorrect", errors)
    require(bundle.get("deployment_production_re_denial_proof", {}).get("proof_status") == "BLOCKED", "no-token deployment proof incorrect", errors)
    require(bundle.get("rollback_recovery_availability_assertion", {}).get("assertion_status") == "BLOCKED", "no-token rollback/recovery assertion incorrect", errors)
    require(bundle.get("first_tiny_real_world_execution_candidate_audit_proof", {}).get("audit_status") == "BLOCKED", "no-token audit status incorrect", errors)
    require(bundle.get("final_preflight_ledger", {}).get("ledger_status") == "BLOCKED", "no-token ledger status incorrect", errors)
    require(bundle.get("first_tiny_real_world_supervised_execution_candidate_bridge", {}).get("ready_for_first_tiny_real_world_supervised_execution_candidate") is False, "no-token bridge readiness incorrect", errors)
    require(bundle.get("baseline_preserved") is True, "no-token baseline not preserved", errors)
    require(bundle.get("external_actions_taken") is False, "no-token external actions taken incorrect", errors)

    token = run_json([sys.executable, str(RUNTIME), "--command", "check please", "--live-external-action-final-preflight-gate", "--live-external-action-confirm-token", "YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE", "--json"])
    bundle = token.get("live_external_action_final_preflight_gate_bundle", {})
    gate = token.get("live_external_action_final_preflight_gate_approval_gate", {})
    require(gate.get("gate_status") == "APPROVED_FOR_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_RECORDS", "token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is True, "token validity incorrect", errors)
    require(gate.get("local_final_preflight_records_authorized") is True, "token local records authorization incorrect", errors)
    require(gate.get("live_external_action_authorized") is False, "token live external action authorization incorrect", errors)
    require(bundle.get("tiny_action_candidate_boundary_contract", {}).get("contract_status") == "TINY_ACTION_CANDIDATE_BOUNDARY_CONTRACT_CREATED", "token tiny action contract incorrect", errors)
    require(bundle.get("live_external_action_non_execution_contract", {}).get("contract_status") == "LIVE_EXTERNAL_ACTION_NON_EXECUTION_CONTRACT_CREATED", "token non-execution contract incorrect", errors)
    require(bundle.get("blast_radius_ceiling_contract", {}).get("contract_status") == "BLAST_RADIUS_CEILING_CONTRACT_CREATED", "token blast radius contract incorrect", errors)
    require(bundle.get("human_final_approval_requirement", {}).get("requirement_status") == "HUMAN_FINAL_APPROVAL_REQUIREMENT_CREATED", "token human approval requirement incorrect", errors)
    require(bundle.get("credential_secret_environment_re_denial_proof", {}).get("proof_status") == "CREDENTIAL_SECRET_ENVIRONMENT_RE_DENIAL_PROOF_CREATED", "token credential denial proof incorrect", errors)
    require(bundle.get("network_socket_api_re_denial_proof", {}).get("proof_status") == "NETWORK_SOCKET_API_RE_DENIAL_PROOF_CREATED", "token network/socket proof incorrect", errors)
    require(bundle.get("deployment_production_re_denial_proof", {}).get("proof_status") == "DEPLOYMENT_PRODUCTION_RE_DENIAL_PROOF_CREATED", "token deployment proof incorrect", errors)
    require(bundle.get("rollback_recovery_availability_assertion", {}).get("assertion_status") == "ROLLBACK_RECOVERY_AVAILABILITY_ASSERTION_CREATED", "token rollback/recovery assertion incorrect", errors)
    require(bundle.get("first_tiny_real_world_execution_candidate_audit_proof", {}).get("audit_status") == "PASS", "token audit status incorrect", errors)
    require(bundle.get("final_preflight_ledger", {}).get("ledger_status") == "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_LEDGER", "token ledger status incorrect", errors)
    require(bundle.get("first_tiny_real_world_supervised_execution_candidate_bridge", {}).get("ready_for_first_tiny_real_world_supervised_execution_candidate") is True, "token bridge readiness incorrect", errors)
    require(bundle.get("first_tiny_real_world_supervised_execution_candidate_bridge", {}).get("next_layer") == "First Tiny Real-World Supervised Execution Candidate", "token bridge next layer incorrect", errors)
    require(bundle.get("baseline_preserved") is True, "token baseline not preserved", errors)
    require(bundle.get("external_actions_taken") is False, "token external actions taken incorrect", errors)
    for key in [
        "live_external_action_authorized",
        "live_api_call_authorized",
        "network_access_authorized",
        "socket_access_authorized",
        "dns_resolution_authorized",
        "outbound_connection_authorized",
        "inbound_connection_authorized",
        "webhook_call_authorized",
        "credential_use_authorized",
        "credential_vault_access_authorized",
        "secret_read_authorized",
        "environment_read_authorized",
        "deployment_authorized",
        "deployment_rollback_authorized",
        "production_execution_authorized",
        "production_activation_authorized",
        "real_external_tool_invocation_authorized",
        "real_task_execution_authorized",
        "live_task_assignment_authorized",
        "live_worker_routing_authorized",
        "live_orchestration_authorized",
        "worker_process_start_authorized",
        "repo_mutation_authorized",
        "full_workforce_activation_authorized",
        "execution_authorized",
    ]:
        require(gate.get(key) is False, f"dangerous authorization unexpectedly true: {key}", errors)


def check_write_proof(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out = run_json([
            sys.executable,
            str(RUNTIME),
            "--command",
            "check please",
            "--write-live-external-action-final-preflight-gate",
            tmpdir,
            "--live-external-action-confirm-token",
            "YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE",
        ])
        summary = out.get("live_external_action_final_preflight_gate_write_summary", {})
        require(bool(summary), "write proof summary missing", errors)
        proof_dir = Path(summary.get("live_external_action_final_preflight_gate_dir", ""))
        require(proof_dir.exists(), "write proof directory missing", errors)
        expected = [
            "live_external_action_final_preflight_gate_bundle.json",
            "live_external_action_final_preflight_gate_schema.json",
            "live_external_action_final_preflight_gate_approval_gate.json",
            "tiny_action_candidate_boundary_contract.json",
            "live_external_action_non_execution_contract.json",
            "blast_radius_ceiling_contract.json",
            "human_final_approval_requirement.json",
            "credential_secret_environment_re_denial_proof.json",
            "network_socket_api_re_denial_proof.json",
            "deployment_production_re_denial_proof.json",
            "rollback_recovery_availability_assertion.json",
            "final_preflight_ledger.json",
            "first_tiny_real_world_supervised_execution_candidate_bridge.json",
            "live_external_action_final_preflight_gate_audit_proof.json",
            "live_external_action_final_preflight_gate_ledger.json",
            "live_external_action_final_preflight_gate_readiness_summary.json",
            "live_external_action_final_preflight_gate_manifest.json",
        ]
        for filename in expected:
            require((proof_dir / filename).exists(), f"write proof missing file: {filename}", errors)
        manifest = json.loads((proof_dir / "live_external_action_final_preflight_gate_manifest.json").read_text())
        require(manifest.get("runtime_version") == "3.9.0", "write proof manifest runtime version incorrect", errors)
        require(manifest.get("status") == "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_PREVIEW_ONLY", "write proof manifest status incorrect", errors)
        require(manifest.get("baseline_preserved") is True, "write proof manifest baseline incorrect", errors)
        require(manifest.get("external_actions_taken") is False, "write proof manifest external actions incorrect", errors)


def check_write_artifacts(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as run_dir, tempfile.TemporaryDirectory() as reg_dir:
        out = run_json([
            sys.executable,
            str(RUNTIME),
            "--command",
            "check please",
            "--write-artifacts",
            run_dir,
            "--registry-dir",
            reg_dir,
            "--live-external-action-final-preflight-gate",
            "--live-external-action-confirm-token",
            "YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE",
        ])
        summary = out.get("artifact_write_summary", {})
        require(bool(summary), "artifact write summary missing", errors)
        run_id = summary.get("run_id", "")
        require(run_id.startswith("station-chief-v3-9-check-please-"), "artifact write run id prefix incorrect", errors)
        artifact_dir = Path(summary.get("artifact_dir", ""))
        require(artifact_dir.exists(), "artifact directory missing", errors)
        for filename in [
            "live_external_action_final_preflight_gate_bundle.json",
            "live_external_action_final_preflight_gate_schema.json",
            "live_external_action_final_preflight_gate_approval_gate.json",
            "tiny_action_candidate_boundary_contract.json",
            "live_external_action_non_execution_contract.json",
            "blast_radius_ceiling_contract.json",
            "human_final_approval_requirement.json",
            "credential_secret_environment_re_denial_proof.json",
            "network_socket_api_re_denial_proof.json",
            "deployment_production_re_denial_proof.json",
            "rollback_recovery_availability_assertion.json",
            "first_tiny_real_world_execution_candidate_audit_proof.json",
            "final_preflight_ledger.json",
            "first_tiny_real_world_supervised_execution_candidate_bridge.json",
        ]:
            require((artifact_dir / filename).exists(), f"artifact directory missing file: {filename}", errors)
        manifest = json.loads((artifact_dir / "manifest.json").read_text())
        require(manifest.get("artifact_type") == "station_chief_runtime_v3_9_artifacts", "artifact manifest type incorrect", errors)
        require(manifest.get("runtime_version") == "3.9.0", "artifact manifest runtime version incorrect", errors)
        registry = json.loads((Path(reg_dir) / "run_registry.json").read_text())
        index = json.loads((Path(reg_dir) / "runtime_index.json").read_text())
        require(registry.get("registry_version") == "3.9.0", "registry version incorrect", errors)
        require(index.get("index_version") == "3.9.0", "runtime index version incorrect", errors)
        require(summary.get("registry_updated") is True, "registry not updated", errors)


def check_docs(errors: list[str]) -> None:
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    for text, label in [
        (readme, "README"),
        (skeleton, "skeleton report"),
        (report, "v3.9 report"),
    ]:
        require("Station Chief Runtime upgraded to v3.9.0." in text, f"{label} missing v3.9 status", errors)
        require("Live external action final preflight gate added." in text, f"{label} missing v3.9 capability phrase", errors)
    require("Next recommended step: build first tiny real-world supervised execution candidate." in readme, "README missing next-step text", errors)
    require("Next recommended build step: build first tiny real-world supervised execution candidate." in skeleton, "skeleton report missing next-step text", errors)
    require("Next recommended build step: build first tiny real-world supervised execution candidate." in report, "v3.9 report missing next-step text", errors)
    for text, label in [
        (readme, "README"),
        (skeleton, "skeleton report"),
    ]:
        for forbidden in ["Explain that", "Include:", "List:", "Write:"]:
            require(forbidden not in text, f"{label} contains scaffold wording: {forbidden}", errors)


def check_smoke(errors: list[str]) -> None:
    commands = [
        ["--list-overlays"],
        ["--list-adapters"],
        ["--command", "check please", "--simulate-adapter"],
        ["--stable-release-manifest"],
        ["--release-lock"],
        ["--controlled-execution"],
        ["--work-order-executor"],
        ["--worker-hiring-registry"],
        ["--department-routing"],
        ["--multi-agent-orchestration"],
        ["--operator-console"],
        ["--github-patch-hardening"],
        ["--deployment-packaging"],
        ["--controlled-worker-execution"],
        ["--tool-permission-binding"],
        ["--live-telemetry-abort"],
        ["--post-run-audit-expansion"],
        ["--multi-worker-sandbox-coordination"],
        ["--controlled-external-tool-preview"],
        ["--permissioned-external-api-dry-run"],
        ["--controlled-multi-worker-audit-replay-preview"],
        ["--operator-approval-queue-enforcement"],
        ["--release-candidate-hardening"],
        ["--controlled-production-readiness-gate"],
        ["--controlled-worker-hiring-activation-pilot"],
        ["--first-supervised-production-dry-run"],
        ["--limited-external-tool-supervised-pilot"],
        ["--supervised-external-api-pilot"],
        ["--monitored-rollback-recovery-drill"],
        ["--supervised-production-pilot-readiness-review"],
        ["--credential-vault-denial-secret-handling-proof"],
        ["--network-socket-lockdown-proof"],
        ["--live-external-action-final-preflight-gate"],
        ["--approval-handoff"],
    ]
    for extra in commands:
        proc = run_command([sys.executable, str(RUNTIME), "--command", "check please", "--json", *extra])
        require(proc.returncode == 0, f"smoke command failed: {' '.join(extra)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)


def check_cli_variants(errors: list[str]) -> None:
    proc = run_command([sys.executable, str(RUNTIME), "--command", "build first tiny real-world supervised execution candidate", "--brief"])
    require(proc.returncode == 0, f"brief command failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)
    require("First Tiny Real-World Supervised Execution Candidate" in proc.stdout or proc.stdout.strip() != "", "brief command produced no usable output", errors)

    proc = run_command([sys.executable, str(RUNTIME), "--command", "check please", "--simulate-adapter", "--json"])
    require(proc.returncode == 0, f"simulate-adapter command failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        require(False, f"simulate-adapter command did not emit JSON: {exc}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)
        return
    require(payload.get("adapter_result", {}).get("adapter_result_status") == "PASS", "simulate-adapter status incorrect", errors)


def main() -> None:
    errors: list[str] = []
    print("Manual scope check required: confirm git diff contains only the allowed pre-v4 hardening files.")

    for path in REQUIRED_FILES:
        require(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}", errors)

    check_strings(
        RUNTIME,
        [
            'STATION_CHIEF_RUNTIME_VERSION = "3.9.0"',
            "live_external_action_final_preflight_gate",
            "attach_live_external_action_final_preflight_gate",
            "write_live_external_action_final_preflight_gate",
            "--live-external-action-final-preflight-gate-schema",
            "--live-external-action-final-preflight-gate",
            "--write-live-external-action-final-preflight-gate",
            "--live-external-action-label",
            "--live-external-action-confirm-token",
            "--candidate-action-label",
            "--blast-radius-label",
            "--required-final-approver",
            "live_external_action_final_preflight_gate_bundle",
            "live_external_action_final_preflight_gate_schema",
            "live_external_action_final_preflight_gate_approval_gate",
            "tiny_action_candidate_boundary_contract",
            "live_external_action_non_execution_contract",
            "blast_radius_ceiling_contract",
            "human_final_approval_requirement",
            "credential_secret_environment_re_denial_proof",
            "network_socket_api_re_denial_proof",
            "deployment_production_re_denial_proof",
            "rollback_recovery_availability_assertion",
            "final_preflight_ledger",
            "first_tiny_real_world_supervised_execution_candidate_bridge",
        ],
        ["import requests", "urllib.request", "os.system", "pip install", "npm install", "API key", "import subprocess"],
        errors,
    )
    check_strings(
        MODULE,
        [
            'LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_MODULE_VERSION = "3.9.0"',
            "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_STATUS",
            "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_PHASE",
            "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_APPROVAL_TOKEN",
            "YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE",
            "canonical_json",
            "sha256_digest",
            "normalize_live_external_action_label",
            "generate_live_external_action_final_preflight_gate_id",
            "create_live_external_action_final_preflight_gate_schema",
            "create_live_external_action_final_preflight_gate_approval_gate",
            "create_tiny_action_candidate_boundary_contract",
            "create_live_external_action_non_execution_contract",
            "create_blast_radius_ceiling_contract",
            "create_human_final_approval_requirement",
            "create_credential_secret_environment_re_denial_proof",
            "create_network_socket_api_re_denial_proof",
            "create_deployment_production_re_denial_proof",
            "create_rollback_recovery_availability_assertion",
            "create_final_preflight_ledger",
            "create_first_tiny_real_world_supervised_execution_candidate_bridge",
            "create_live_external_action_final_preflight_gate_bundle",
        ],
        ["eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver", "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway", "render", "gh api", "git push", "create_commit", "update_ref", "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"],
        errors,
    )
    check_strings(
        ADAPTERS,
        [
            "ADAPTER_MODULE_VERSION = \"3.9.0\"",
        ],
        [],
        errors,
    )
    check_strings(
        RELEASE_LOCK,
        [
            'STABLE_RUNTIME_VERSION = "3.9.0"',
            '"current_phase": "Live External Action Final Preflight Gate"',
            '"next_phase": "First Tiny Real-World Supervised Execution Candidate"',
            '"v4.0 first tiny real-world supervised execution candidate"',
            '"v4.1 post-action verification and audit review"',
            '"v4.2 supervised rollback/recovery execution candidate"',
            '"v4.3 limited live worker activation candidate"',
        ],
        [],
        errors,
    )
    check_docs(errors)
    check_pre_v4_docs(errors)
    check_prefix_and_bridge_safety(errors)
    check_old_validator_delegation(errors)
    check_no_accidental_v4_files(errors)
    check_pre_v4_artifacts(errors)

    check_demo(errors)
    check_fixture_tests(errors)
    check_schema(errors)
    check_no_token_and_token_paths(errors)
    check_write_proof(errors)
    check_write_artifacts(errors)
    check_cli_variants(errors)
    check_smoke(errors)

    if errors:
        print("FAIL")
        for message in errors:
            print(message)
        sys.exit(1)

    print("PASS: Station Chief Runtime v3.9 pre-v4 readiness valid.")


if __name__ == "__main__":
    main()
