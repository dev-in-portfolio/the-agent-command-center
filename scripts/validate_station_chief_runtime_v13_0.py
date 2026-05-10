#!/usr/bin/env python3
"""
Station Chief Runtime v13.0 Validator.
Verifies Station Chief v13.0 build, external tool/API pilot hardening metadata, and safety boundaries.
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
from station_chief_v13_external_tool_api_pilot_hardening import (  # noqa: E402
    STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION,
    STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_STATUS,
    STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_PHASE,
    STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS,
    STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS,
    STATION_CHIEF_V13_EXTERNAL_PILOT_DRY_RUN_PLAN_ID,
    STATION_CHIEF_V13_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION,
    canonical_json,
    sha256_digest,
    normalize_label,
    create_external_interface_descriptor_registry,
    create_external_action_envelopes,
    create_external_access_policy_gate,
    create_credential_secret_denial_proof,
    create_network_api_denial_proof,
    create_external_pilot_dry_run_plan,
    create_external_permission_receipts,
    create_external_pilot_hardening_audit_record,
    create_external_tool_api_pilot_safety_boundary_matrix,
    create_station_chief_v13_external_tool_api_pilot_hardening_schema,
    create_station_chief_v13_external_tool_api_pilot_hardening_bundle,
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
        (
            f"Prior validator {script_name} failed:\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        ),
    )
    expected_token_map = {
        "scripts/validate_station_chief_runtime_v12_0.py": "STATION_CHIEF_RUNTIME_V12_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v11_0.py": "STATION_CHIEF_RUNTIME_V11_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v10_0.py": "STATION_CHIEF_RUNTIME_V10_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v9_0.py": "STATION_CHIEF_RUNTIME_V9_0_VALIDATION_PASS",
        "scripts/validate_station_chief_runtime_v8_0.py": "STATION_CHIEF_RUNTIME_V8_0_VALIDATION_PASS",
    }
    if script_name in expected_token_map:
        ensure(expected_token_map[script_name] in result.stdout, f"Prior validator {script_name} did not report success")


def _assert_no_future_files() -> None:
    forbidden_globs = ["*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18_1*", "*v18.1*", "*v19_1*", "*v19.1*", "*v20_1*", "*v20.1*", "*v21_1*", "*v21.1*", "*v22_1*", "*v22.1*", "*v23*"]
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
        "09_exports/station_chief_v13_0_external_tool_api_pilot_hardening_preflight_audit.md",
        "10_runtime/station_chief_v13_external_tool_api_pilot_hardening.py",
        "09_exports/station_chief_runtime_v13_0_report.md",
        "scripts/validate_station_chief_runtime_v13_0.py",
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_adapters.py",
        "10_runtime/station_chief_release_lock.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        ".github/workflows/station-chief-validation.yml",
        "scripts/validate_station_chief_runtime_v12_0.py",
        "scripts/validate_station_chief_runtime_v11_0.py",
        "scripts/validate_station_chief_runtime_v10_0.py",
        "scripts/validate_station_chief_runtime_v9_0.py",
        "scripts/validate_station_chief_runtime_v8_0.py",
        "scripts/validate_station_chief_runtime_v6_6.py",
        "scripts/validate_station_chief_runtime_v6_5.py",
        "scripts/validate_station_chief_runtime_v6_4.py",
        "scripts/validate_station_chief_runtime_v6_3.py",
        "scripts/validate_station_chief_runtime_v6_2.py",
        "scripts/validate_station_chief_runtime_v6_1.py",
        "scripts/validate_station_chief_runtime_v6_0.py",
        "scripts/validate_station_chief_runtime_v5_9.py",
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
        ensure(path in allowed_paths or "validate_station_chief_runtime_" in path or ("v14" in path and "v14_1" not in path and "v14.1" not in path) or ("v15" in path and "v15_1" not in path and "v15.1" not in path) or ("v16" in path and "v16_1" not in path and "v16.1" not in path) or ("v17" in path and "v17_1" not in path and "v17.1" not in path) or ("v18" in path and "v18_1" not in path and "v18.1" not in path) or ("v19" in path and "v19_1" not in path and "v19.1" not in path) or ("v20" in path and "v20_1" not in path and "v20.1" not in path) or ("v21" in path and "v21_1" not in path and "v21.1" not in path) or ("v22" in path and "v22_1" not in path and "v22.1" not in path and "v23" not in path) or path.startswith("10_runtime/__pycache__") or path.startswith("scripts/__pycache__"), f"Unexpected modified path: {path}")


def main():
    required_files = [
        "09_exports/station_chief_v13_0_external_tool_api_pilot_hardening_preflight_audit.md",
        "10_runtime/station_chief_v13_external_tool_api_pilot_hardening.py",
        "09_exports/station_chief_runtime_v13_0_report.md",
        "scripts/validate_station_chief_runtime_v13_0.py",
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
        "scripts/validate_station_chief_runtime_v6_6.py",
        "scripts/validate_station_chief_runtime_v6_5.py",
        "scripts/validate_station_chief_runtime_v6_4.py",
        "scripts/validate_station_chief_runtime_v6_3.py",
        "scripts/validate_station_chief_runtime_v6_2.py",
        "scripts/validate_station_chief_runtime_v6_1.py",
        "scripts/validate_station_chief_runtime_v6_0.py",
        "scripts/validate_station_chief_runtime_v5_9.py",
        "scripts/validate_station_chief_runtime_v5_8.py",
        "scripts/validate_station_chief_runtime_v5_7.py",
        "scripts/validate_station_chief_runtime_v5_6.py",
        "scripts/validate_station_chief_runtime_v5_5.py",
        "scripts/validate_station_chief_runtime_v5_4.py",
        "scripts/validate_station_chief_runtime_v5_3.py",
        "scripts/validate_station_chief_runtime_v5_2.py",
        "scripts/validate_station_chief_runtime_v5_1.py",
        "scripts/validate_station_chief_runtime_v5_0.py",
    ]
    for path in required_files:
        ensure((REPO_ROOT / path).exists(), f"Required file missing: {path}")

    ensure(STATION_CHIEF_RUNTIME_VERSION == "13.0.0", f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION == "13.0.0", f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION == "13.0.0", f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_VERSION == "13.0.0", "v13 module version mismatch")
    ensure(STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_STATUS == "STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_LOCAL_DETERMINISTIC_ONLY", "v13 module status mismatch")
    ensure(STATION_CHIEF_V13_EXTERNAL_TOOL_API_PILOT_HARDENING_PHASE == "Station Chief v13.0 External Tool / API Pilot Hardening Candidate", "v13 module phase mismatch")
    ensure(STATION_CHIEF_V13_EXTERNAL_PILOT_DRY_RUN_PLAN_ID == "station-chief-external-pilot-dry-run-plan-001", "dry run plan id mismatch")
    ensure(STATION_CHIEF_V13_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION == "v13.1 or v14.0 requires explicit operator instruction", "next version label mismatch")

    ensure(callable(canonical_json), "canonical_json missing or not callable")
    ensure(callable(sha256_digest), "sha256_digest missing or not callable")
    ensure(callable(normalize_label), "normalize_label missing or not callable")
    ensure(callable(create_external_interface_descriptor_registry), "interface registry function missing or not callable")
    ensure(callable(create_external_action_envelopes), "action envelopes function missing or not callable")
    ensure(callable(create_external_access_policy_gate), "policy gate function missing or not callable")
    ensure(callable(create_credential_secret_denial_proof), "credential denial proof function missing or not callable")
    ensure(callable(create_network_api_denial_proof), "network denial proof function missing or not callable")
    ensure(callable(create_external_pilot_dry_run_plan), "dry-run plan function missing or not callable")
    ensure(callable(create_external_permission_receipts), "permission receipts function missing or not callable")
    ensure(callable(create_external_pilot_hardening_audit_record), "audit record function missing or not callable")
    ensure(callable(create_external_tool_api_pilot_safety_boundary_matrix), "safety boundary matrix function missing or not callable")
    ensure(callable(create_station_chief_v13_external_tool_api_pilot_hardening_schema), "schema function missing or not callable")
    ensure(callable(create_station_chief_v13_external_tool_api_pilot_hardening_bundle), "bundle function missing or not callable")
    ensure(callable(run_station_chief), "runtime wrapper missing or not callable")

    help_result = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--help"])
    ensure(help_result.returncode == 0, f"Runtime help failed: {help_result.stderr}")
    for flag in [
        "--station-chief-v13-external-tool-api-pilot-hardening-schema",
        "--station-chief-v13-external-tool-api-pilot-hardening",
        "--station-chief-v13-external-interfaces",
        "--station-chief-v13-external-action-envelopes",
        "--station-chief-v13-external-access-policy-gate",
        "--station-chief-v13-credential-secret-denial-proof",
        "--station-chief-v13-network-api-denial-proof",
        "--station-chief-v13-external-pilot-dry-run-plan",
        "--station-chief-v13-external-permission-receipts",
        "--station-chief-v13-external-pilot-audit",
    ]:
        ensure(flag in help_result.stdout, f"CLI flag missing from help output: {flag}")

    schema = _cli_json(["--station-chief-v13-external-tool-api-pilot-hardening-schema"])
    ensure(schema["schema_version"] == "13.0.0", "Schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v13_external_tool_api_pilot_hardening", "Schema type mismatch")
    for key in [
        "no_real_tool_invocation_authorized",
        "no_external_tool_invocation_authorized",
        "no_api_call_authorized",
        "no_network_access_authorized",
        "no_socket_access_authorized",
        "no_dns_resolution_authorized",
        "no_credential_access_authorized",
        "no_credential_vault_access_authorized",
        "no_secret_read_authorized",
        "no_environment_read_authorized",
        "no_arbitrary_task_execution_authorized",
        "no_user_task_execution_authorized",
        "no_worker_process_start_authorized",
        "no_real_queue_authorized",
        "no_queue_write_authorized",
        "no_live_routing_authorized",
        "no_live_orchestration_authorized",
        "no_deployment_authorized",
        "no_production_execution_authorized",
    ]:
        ensure(schema[key] is True, f"Schema contract mismatch for {key}")
    ensure(schema["v13_1_created"] is False, "Schema v13.1 flag mismatch")
    ensure(schema["v14_created"] is False, "Schema v14 flag mismatch")
    for section_name in [
        "external_interface_descriptor_registry",
        "external_action_envelopes",
        "external_access_policy_gate",
        "credential_secret_denial_proof",
        "network_api_denial_proof",
        "external_pilot_dry_run_plan",
        "external_permission_receipts",
        "external_pilot_hardening_audit_record",
        "external_tool_api_pilot_safety_boundary_matrix",
        "external_tool_api_pilot_readiness_summary",
    ]:
        ensure(section_name in schema["required_sections"], f"Schema missing required section: {section_name}")

    bundle = create_station_chief_v13_external_tool_api_pilot_hardening_bundle()
    ensure(bundle["runtime_version"] == "13.0.0", "Bundle version mismatch")
    ensure(bundle["external_pilot_hardening_status"] == "EXTERNAL_TOOL_API_PILOT_HARDENING_READY", "Bundle status mismatch")
    ensure(bundle["interface_descriptor_count"] == 4, "Bundle interface descriptor count mismatch")
    ensure(bundle["action_envelope_count"] == 4, "Bundle action envelope count mismatch")
    ensure(bundle["permission_receipt_count"] == 4, "Bundle permission receipt count mismatch")
    ensure(bundle["external_interface_descriptors_registered"] is True, "Bundle interface registration flag mismatch")
    ensure(bundle["external_action_envelopes_registered"] is True, "Bundle action envelope flag mismatch")
    ensure(bundle["external_access_policy_gate_created"] is True, "Bundle policy gate flag mismatch")
    ensure(bundle["credential_secret_denial_proof_created"] is True, "Bundle credential proof flag mismatch")
    ensure(bundle["network_api_denial_proof_created"] is True, "Bundle network proof flag mismatch")
    ensure(bundle["external_pilot_dry_run_plan_created"] is True, "Bundle dry run plan flag mismatch")
    ensure(bundle["external_permission_receipts_generated"] is True, "Bundle receipt flag mismatch")
    for key in [
        "real_tool_invocation_performed",
        "external_tool_invocation_performed",
        "api_call_performed",
        "network_access_performed",
        "socket_access_performed",
        "dns_resolution_performed",
        "credential_access_performed",
        "credential_vault_access_performed",
        "secret_read_performed",
        "environment_read_performed",
        "real_worker_process_started",
        "daemon_started",
        "background_process_started",
        "agent_started",
        "real_queue_created",
        "queue_write_performed",
        "scheduler_write_performed",
        "cron_write_performed",
        "live_task_enqueued",
        "live_task_dequeued",
        "live_task_executed",
        "task_executed",
        "live_worker_routing_performed",
        "live_orchestration_performed",
        "arbitrary_task_execution_performed",
        "user_task_execution_performed",
        "shell_executed",
        "subprocess_started",
        "filesystem_mutation_performed",
        "deployment_performed",
        "production_execution_performed",
        "full_workforce_activation_performed",
        "full_external_prod_agent_army_activation_performed",
        "v13_1_created",
        "v14_created",
    ]:
        ensure(bundle[key] is False, f"Bundle negative flag mismatch for {key}")
    ensure(len(bundle["bundle_digest"]) == 64, "Bundle digest mismatch")

    interface_registry = bundle["external_interface_descriptor_registry"]
    action_envelopes = bundle["external_action_envelopes"]
    policy_gate = bundle["external_access_policy_gate"]
    credential_secret_denial_proof = bundle["credential_secret_denial_proof"]
    network_api_denial_proof = bundle["network_api_denial_proof"]
    dry_run_plan = bundle["external_pilot_dry_run_plan"]
    permission_receipts = bundle["external_permission_receipts"]
    audit_record = bundle["external_pilot_hardening_audit_record"]
    safety_matrix = bundle["external_tool_api_pilot_safety_boundary_matrix"]
    readiness_summary = bundle["external_tool_api_pilot_readiness_summary"]

    ensure(list(interface_registry.keys()) == STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS, "Interface IDs are not deterministic")
    for index, interface_id in enumerate(STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS, start=1):
        descriptor = interface_registry[interface_id]
        ensure(descriptor["interface_id"] == interface_id, f"Interface id mismatch for {interface_id}")
        ensure(descriptor["interface_type"] == "metadata_only_external_interface_descriptor", f"Interface type mismatch for {interface_id}")
        ensure(descriptor["descriptor_only"] is True, f"Interface descriptor flag mismatch for {interface_id}")
        ensure(descriptor["external_interface_registered"] is True, f"Interface registration mismatch for {interface_id}")
        for key in [
            "real_tool_invocation_allowed",
            "external_tool_invocation_allowed",
            "api_call_allowed",
            "network_access_allowed",
            "socket_access_allowed",
            "dns_resolution_allowed",
            "credential_access_allowed",
            "credential_vault_access_allowed",
            "secret_read_allowed",
            "environment_read_allowed",
            "filesystem_mutation_allowed",
            "subprocess_allowed",
            "shell_allowed",
            "production_allowed",
            "deployment_allowed",
            "arbitrary_task_allowed",
            "user_task_allowed",
        ]:
            ensure(descriptor[key] is False, f"Interface deny flag mismatch for {interface_id}: {key}")

    ensure(list(action_envelopes.keys()) == STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS, "Envelope IDs are not deterministic")
    for index, envelope_id in enumerate(STATION_CHIEF_V13_EXTERNAL_ACTION_ENVELOPE_IDS, start=1):
        envelope = action_envelopes[envelope_id]
        interface_id = STATION_CHIEF_V13_EXTERNAL_INTERFACE_IDS[index - 1]
        ensure(envelope["external_action_envelope_id"] == envelope_id, f"Envelope id mismatch for {envelope_id}")
        ensure(envelope["envelope_type"] == "metadata_only_external_action_envelope", f"Envelope type mismatch for {envelope_id}")
        ensure(envelope["envelope_index"] == index, f"Envelope index mismatch for {envelope_id}")
        ensure(envelope["bound_interface_id"] == interface_id, f"Envelope interface mismatch for {envelope_id}")
        ensure(envelope["envelope_payload"] == {"operation": "external_boundary_dry_run_metadata", "expected_result": "external_permission_receipt_recorded"}, f"Envelope payload mismatch for {envelope_id}")
        ensure(envelope["descriptor_only"] is True, f"Envelope descriptor flag mismatch for {envelope_id}")
        ensure(envelope["dry_run_only"] is True, f"Envelope dry-run flag mismatch for {envelope_id}")
        ensure(envelope["execution_mode"] == "metadata_external_permission_receipt_only", f"Envelope mode mismatch for {envelope_id}")
        for key in [
            "live_execution_allowed",
            "real_tool_invocation_allowed",
            "external_tool_invocation_allowed",
            "api_call_allowed",
            "network_access_allowed",
            "socket_access_allowed",
            "dns_resolution_allowed",
            "credential_access_allowed",
            "secret_read_allowed",
            "environment_read_allowed",
            "filesystem_mutation_allowed",
            "production_allowed",
            "deployment_allowed",
            "arbitrary_user_content_allowed",
            "arbitrary_task_allowed",
            "user_task_allowed",
        ]:
            ensure(envelope[key] is False, f"Envelope deny flag mismatch for {envelope_id}: {key}")

    ensure(policy_gate["external_metadata_authorized"] is True, "Policy gate failed to authorize metadata")
    for key in [
        "real_tool_invocation_authorized",
        "external_tool_invocation_authorized",
        "api_call_authorized",
        "network_access_authorized",
        "socket_access_authorized",
        "dns_resolution_authorized",
        "credential_access_authorized",
        "credential_vault_access_authorized",
        "secret_read_authorized",
        "environment_read_authorized",
        "deployment_authorized",
        "production_execution_authorized",
        "arbitrary_execution_authorized",
        "user_task_execution_authorized",
        "live_orchestration_authorized",
    ]:
        ensure(policy_gate[key] is False, f"Policy gate incorrectly authorized {key}")

    ensure(credential_secret_denial_proof["proof_type"] == "metadata_only_credential_secret_denial_proof", "Credential proof type mismatch")
    ensure(credential_secret_denial_proof["runtime_version"] == "13.0.0", "Credential proof runtime mismatch")
    ensure(credential_secret_denial_proof["credential_access_attempted"] is False, "Credential proof attempted flag mismatch")
    ensure(credential_secret_denial_proof["credential_vault_access_attempted"] is False, "Credential proof vault attempted flag mismatch")
    ensure(credential_secret_denial_proof["secret_read_attempted"] is False, "Credential proof secret attempted flag mismatch")
    ensure(credential_secret_denial_proof["environment_read_attempted"] is False, "Credential proof environment attempted flag mismatch")
    ensure(credential_secret_denial_proof["credential_access_authorized"] is False, "Credential proof access auth mismatch")
    ensure(credential_secret_denial_proof["credential_vault_access_authorized"] is False, "Credential proof vault auth mismatch")
    ensure(credential_secret_denial_proof["secret_read_authorized"] is False, "Credential proof secret auth mismatch")
    ensure(credential_secret_denial_proof["environment_read_authorized"] is False, "Credential proof environment auth mismatch")
    ensure(credential_secret_denial_proof["proof_status"] == "CREDENTIAL_SECRET_ENVIRONMENT_ACCESS_DENIED", "Credential proof status mismatch")
    ensure(credential_secret_denial_proof["external_metadata_authorized"] is True, "Credential proof metadata auth mismatch")

    ensure(network_api_denial_proof["proof_type"] == "metadata_only_network_api_denial_proof", "Network proof type mismatch")
    ensure(network_api_denial_proof["runtime_version"] == "13.0.0", "Network proof runtime mismatch")
    ensure(network_api_denial_proof["api_call_attempted"] is False, "Network proof api attempted flag mismatch")
    ensure(network_api_denial_proof["network_access_attempted"] is False, "Network proof network attempted flag mismatch")
    ensure(network_api_denial_proof["socket_access_attempted"] is False, "Network proof socket attempted flag mismatch")
    ensure(network_api_denial_proof["dns_resolution_attempted"] is False, "Network proof dns attempted flag mismatch")
    ensure(network_api_denial_proof["outbound_connection_attempted"] is False, "Network proof outbound attempted flag mismatch")
    ensure(network_api_denial_proof["inbound_connection_attempted"] is False, "Network proof inbound attempted flag mismatch")
    ensure(network_api_denial_proof["webhook_call_attempted"] is False, "Network proof webhook attempted flag mismatch")
    ensure(network_api_denial_proof["api_call_authorized"] is False, "Network proof api auth mismatch")
    ensure(network_api_denial_proof["network_access_authorized"] is False, "Network proof network auth mismatch")
    ensure(network_api_denial_proof["socket_access_authorized"] is False, "Network proof socket auth mismatch")
    ensure(network_api_denial_proof["dns_resolution_authorized"] is False, "Network proof dns auth mismatch")
    ensure(network_api_denial_proof["proof_status"] == "NETWORK_API_SOCKET_DNS_ACCESS_DENIED", "Network proof status mismatch")
    ensure(network_api_denial_proof["external_metadata_authorized"] is True, "Network proof metadata auth mismatch")

    ensure(dry_run_plan["external_pilot_dry_run_plan_id"] == STATION_CHIEF_V13_EXTERNAL_PILOT_DRY_RUN_PLAN_ID, "Dry run plan id mismatch")
    ensure(dry_run_plan["dry_run_plan_type"] == "metadata_only_external_tool_api_pilot_hardening_plan", "Dry run plan type mismatch")
    ensure(dry_run_plan["runtime_version"] == "13.0.0", "Dry run plan runtime mismatch")
    ensure(dry_run_plan["interface_count"] == 4, "Dry run plan interface count mismatch")
    ensure(dry_run_plan["action_envelope_count"] == 4, "Dry run plan action envelope count mismatch")
    ensure(dry_run_plan["dry_run_step_count"] == 6, "Dry run plan step count mismatch")
    ensure(dry_run_plan["dry_run_steps"] == [
        "register_external_interface_descriptors_metadata",
        "register_external_action_envelopes_metadata",
        "enforce_external_access_policy_gate_metadata",
        "record_credential_secret_denial_proof_metadata",
        "record_network_api_denial_proof_metadata",
        "record_external_permission_receipts_metadata",
    ], "Dry run plan steps mismatch")
    ensure(dry_run_plan["external_metadata_authorized"] is True, "Dry run plan auth mismatch")
    for key in [
        "real_tool_invocation_performed",
        "external_tool_invocation_performed",
        "api_call_performed",
        "network_access_performed",
        "credential_access_performed",
        "secret_read_performed",
        "environment_read_performed",
        "deployment_performed",
        "production_execution_performed",
    ]:
        ensure(dry_run_plan[key] is False, f"Dry run plan negative flag mismatch for {key}")
    ensure(dry_run_plan["dry_run_execution_only"] is True, "Dry run execution only mismatch")
    ensure(dry_run_plan["live_execution_performed"] is False, "Dry run live execution mismatch")

    ensure(len(permission_receipts) == 4, "Permission receipt count mismatch")
    receipt_worker_pairs = set()
    for receipt_id, receipt in permission_receipts.items():
        expected_receipt_id = sha256_digest({"envelope_id": receipt["external_action_envelope_id"], "interface_id": receipt["interface_id"], "version": "13.0.0"})
        ensure(receipt["receipt_id"] == expected_receipt_id, f"Receipt id mismatch for {receipt_id}")
        ensure(receipt["receipt_type"] == "metadata_only_external_permission_receipt", f"Receipt type mismatch for {receipt_id}")
        ensure(receipt["receipt_status"] == "EXTERNAL_PERMISSION_METADATA_RECORDED", f"Receipt status mismatch for {receipt_id}")
        ensure(receipt["external_permission_receipt_generated"] is True, f"Receipt generation flag mismatch for {receipt_id}")
        for key in [
            "real_tool_invocation_performed",
            "external_tool_invocation_performed",
            "api_call_performed",
            "network_access_performed",
            "socket_access_performed",
            "dns_resolution_performed",
            "credential_access_performed",
            "secret_read_performed",
            "environment_read_performed",
            "filesystem_mutation_performed",
            "deployment_performed",
            "production_execution_performed",
            "arbitrary_task_execution_performed",
            "user_task_execution_performed",
        ]:
            ensure(receipt[key] is False, f"Receipt negative flag mismatch for {receipt_id}: {key}")
        receipt_worker_pairs.add((receipt["external_action_envelope_id"], receipt["interface_id"]))
    ensure(len(receipt_worker_pairs) == 4, "Receipt coverage mismatch")

    ensure(audit_record["audit_type"] == "external_tool_api_pilot_hardening_audit", "Audit type mismatch")
    ensure(audit_record["runtime_version"] == "13.0.0", "Audit runtime mismatch")
    ensure(audit_record["interface_descriptor_count"] == 4, "Audit interface count mismatch")
    ensure(audit_record["action_envelope_count"] == 4, "Audit action count mismatch")
    ensure(audit_record["permission_receipt_count"] == 4, "Audit receipt count mismatch")
    ensure(audit_record["external_metadata_authorized"] is True, "Audit metadata auth mismatch")
    ensure(audit_record["all_permission_receipts_recorded"] is True, "Audit receipt recording mismatch")
    for key in [
        "no_real_tool_invocation",
        "no_external_tool_invocation",
        "no_api_call",
        "no_network_access",
        "no_socket_access",
        "no_dns_resolution",
        "no_credential_access",
        "no_credential_vault_access",
        "no_secret_read",
        "no_environment_read",
        "no_filesystem_mutation",
        "no_deployment",
        "no_production_execution",
        "no_worker_process_started",
        "no_agent_started",
        "no_subprocess_started",
        "no_shell_executed",
        "no_real_queue_created",
        "no_queue_write",
        "no_live_task_enqueued",
        "no_live_task_executed",
        "no_live_worker_routing",
        "no_live_orchestration",
        "no_arbitrary_task_execution",
        "no_user_task_execution",
        "no_full_external_prod_agent_army_activation",
    ]:
        ensure(audit_record[key] is True, f"Audit negative assertion mismatch for {key}")

    ensure(len(safety_matrix) >= 38, "Safety boundary matrix size mismatch")
    for action in [
        "full_external_prod_agent_army_activation",
        "real_tool_invocation",
        "external_tool_invocation",
        "api_call",
        "network_access",
        "socket_access",
        "dns_resolution",
        "outbound_connection",
        "inbound_connection",
        "webhook_call",
        "credential_use",
        "credential_vault_access",
        "secret_read",
        "environment_read",
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
        "filesystem_mutation",
        "deployment",
        "production_execution",
        "database_mutation",
        "full_workforce_activation",
        "v13_1_creation",
        "v14_creation",
    ]:
        ensure(safety_matrix.get(action) == "DENIED", f"Safety boundary missing denial for {action}")

    ensure(readiness_summary["external_interface_descriptors_registered"] is True, "Readiness summary interface registration mismatch")
    ensure(readiness_summary["external_action_envelopes_registered"] is True, "Readiness summary action registration mismatch")
    ensure(readiness_summary["external_access_policy_gate_created"] is True, "Readiness summary policy gate mismatch")
    ensure(readiness_summary["credential_secret_denial_proof_created"] is True, "Readiness summary credential proof mismatch")
    ensure(readiness_summary["network_api_denial_proof_created"] is True, "Readiness summary network proof mismatch")
    ensure(readiness_summary["external_pilot_dry_run_plan_created"] is True, "Readiness summary dry run mismatch")
    ensure(readiness_summary["external_permission_receipts_generated"] is True, "Readiness summary receipt mismatch")

    runtime_result = run_station_chief("build station chief v13 external tool api pilot hardening candidate")
    ensure(runtime_result["station_chief_runtime_version"] == "13.0.0", "Runtime wrapper version mismatch")
    ensure(runtime_result["runtime_status"] == "station_chief_v13_external_tool_api_pilot_hardening", "Runtime wrapper status mismatch")
    ensure(isinstance(runtime_result.get("next_step"), str) and runtime_result["next_step"].startswith("Next step:"), "Runtime wrapper next step mismatch")
    ensure(runtime_result["baseline_preserved"] is True, "Runtime wrapper baseline mismatch")

    index_entry = build_runtime_index_entry(runtime_result, generate_run_id("build station chief v13 external tool api pilot hardening candidate"))
    ensure(index_entry["runtime_version"] == "13.0.0", "Runtime index version mismatch")
    ensure(index_entry["artifact_type"] == "station_chief_runtime_v13_0_artifacts", "Runtime index artifact type mismatch")
    ensure(generate_run_id("build station chief v13 external tool api pilot hardening candidate").startswith("station-chief-v13-0-"), "Run ID prefix mismatch")

    assert_index = create_station_chief_v13_external_tool_api_pilot_hardening_bundle()["bundle_digest"]
    ensure(isinstance(assert_index, str) and len(assert_index) == 64, "Bundle digest mismatch")
    ensure(canonical_json({"a": 1, "b": 2}) == '{"a":1,"b":2}', "Canonical JSON mismatch")
    ensure(sha256_digest({"a": 1}) == sha256_digest({"a": 1}), "Digest function must be deterministic")
    ensure(normalize_label(None, "planning") == "planning", "Label normalization default mismatch")
    ensure(normalize_label("Planning Squad", "planning") == "planning-squad", "Label normalization mismatch")

    _assert_no_future_files()
    _assert_protected_paths_unmodified()

    ensure("Station Chief Runtime upgraded to v13.0.0" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime_readme.md"), "README missing v13 doctrine")
    ensure("v13.1 or v14.0 requires explicit operator instruction" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime_readme.md"), "README missing next-step label")
    ensure("Station Chief Runtime upgraded to v13.0.0" in _source_text(REPO_ROOT / "09_exports/station_chief_runtime_skeleton_report.md"), "Skeleton report missing v13 doctrine")
    ensure("v13.1 or v14.0 requires explicit operator instruction" in _source_text(REPO_ROOT / "09_exports/station_chief_runtime_skeleton_report.md"), "Skeleton report missing next-step label")

    v13_module_source = _source_text(REPO_ROOT / "10_runtime/station_chief_v13_external_tool_api_pilot_hardening.py")
    _ensure_forbidden_patterns_absent(v13_module_source, [
        "import " + "re" + "quests",
        "from " + "re" + "quests",
        "urllib",
        "import socket",
        "from socket",
        "socket.",
        "socket(",
        "import subprocess",
        "from subprocess",
        "subprocess.",
        "os.",
        "os[",
        "getenv(",
        ".environ",
        "ev" + "al(",
        "ex" + "ec(",
        "com" + "pile(",
        "__im" + "port__(",
        "threading",
        "multiprocessing",
        "asyncio",
        "op" + "en(",
        "shlex",
        "system(",
        "popen",
        "invoke_tool(",
        "tool_invoked = True",
        "external_tool_invocation_performed = True",
        "api_call_performed = True",
        "network_access_performed = True",
        "socket_access_performed = True",
        "dns_resolution_performed = True",
        "credential_access_performed = True",
        "credential_vault_access_performed = True",
        "secret_read_performed = True",
        "environment_read_performed = True",
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
        "deploy(",
        "production_execution_performed = True",
        "full_external_prod_agent_army_activation_performed = True",
        "TO" + "DO",
        "Not" + "Implemented",
    ], "v13 module")
    validator_forbidden_patterns = [
        "TO" + "DO",
        "Not" + "Implemented",
        "op" + "en(",
        "re" + "quests",
        "ev" + "al(",
        "ex" + "ec(",
        "com" + "pile(",
        "__im" + "port__(",
    ]
    _ensure_forbidden_patterns_absent(_source_text(Path(__file__)), validator_forbidden_patterns, "v13 validator")

    ensure("validate_station_chief_runtime_v13_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v13 validation context")
    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v12 validation context")
    ensure("validate_station_chief_runtime_v11_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v11 validation context")
    ensure("validate_station_chief_runtime_v10_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v10 validation context")
    ensure("validate_station_chief_runtime_v9_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v9 validation context")
    ensure("validate_station_chief_runtime_v8_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v8 validation context")
    ensure("validate_station_chief_runtime_v6_6.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.6 validation context")
    ensure("validate_station_chief_runtime_v6_5.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.5 validation context")
    ensure("validate_station_chief_runtime_v6_4.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "Runtime selector missing v6.4 validation context")
    ensure("validate_station_chief_runtime_v13_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_release_lock.py"), "Release lock selector missing v13 validation context")
    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_release_lock.py"), "Release lock selector missing v12 validation context")
    ensure("validate_station_chief_runtime_v13_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_adapters.py"), "Adapter selector missing v13 validation context")
    ensure("validate_station_chief_runtime_v12_0.py" in _source_text(REPO_ROOT / "10_runtime/station_chief_adapters.py"), "Adapter selector missing v12 validation context")

    ensure("or '13.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v12_0.py"), "v12 validator contains OR-version shortcut for v13.0")
    ensure('or "13.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v12_0.py"), "v12 validator contains OR-version shortcut for v13.0")
    ensure("or '12.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v11_0.py"), "v11 validator contains OR-version shortcut for v12.0")
    ensure('or "12.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v11_0.py"), "v11 validator contains OR-version shortcut for v12.0")
    ensure("or '13.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v11_0.py"), "v11 validator contains OR-version shortcut for v13.0")
    ensure('or "13.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v11_0.py"), "v11 validator contains OR-version shortcut for v13.0")
    ensure("or '11.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v11.0")
    ensure('or "11.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v11.0")
    ensure("or '12.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v12.0")
    ensure('or "12.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v12.0")
    ensure("or '13.0.0'" not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v13.0")
    ensure('or "13.0.0"' not in _source_text(REPO_ROOT / "scripts/validate_station_chief_runtime_v10_0.py"), "v10 validator contains OR-version shortcut for v13.0")

    _run_prior_validator("scripts/validate_station_chief_runtime_v12_0.py")
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

    print("STATION_CHIEF_RUNTIME_V13_0_VALIDATION_PASS")


if __name__ == "__main__":
    main()
