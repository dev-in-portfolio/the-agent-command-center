#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
READ_ME = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
V3_3_REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v3_3_report.md"
V3_3_MODULE = REPO_ROOT / "10_runtime" / "station_chief_limited_external_tool_supervised_pilot.py"
V3_3_VALIDATOR = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_3.py"

EXPECTED_FILES = [
    "10_runtime/station_chief_runtime.py",
    "10_runtime/station_chief_runtime_readme.md",
    "10_runtime/station_chief_adapters.py",
    "10_runtime/station_chief_execution_profiles.py",
    "10_runtime/station_chief_approval_handoff.py",
    "10_runtime/station_chief_approval_records.py",
    "10_runtime/station_chief_approval_ledger.py",
    "10_runtime/station_chief_release_lock.py",
    "10_runtime/station_chief_controlled_execution.py",
    "10_runtime/station_chief_work_order_executor.py",
    "10_runtime/station_chief_worker_hiring_registry.py",
    "10_runtime/station_chief_department_routing.py",
    "10_runtime/station_chief_multi_agent_orchestration.py",
    "10_runtime/station_chief_operator_console.py",
    "10_runtime/station_chief_github_patch_hardening.py",
    "10_runtime/station_chief_deployment_packaging.py",
    "10_runtime/station_chief_controlled_worker_execution.py",
    "10_runtime/station_chief_tool_permission_binding.py",
    "10_runtime/station_chief_live_execution_telemetry_abort.py",
    "10_runtime/station_chief_post_run_audit_expansion.py",
    "10_runtime/station_chief_multi_worker_sandbox_coordination.py",
    "10_runtime/station_chief_controlled_external_tool_adapter_preview.py",
    "10_runtime/station_chief_permissioned_external_api_dry_run_preview.py",
    "10_runtime/station_chief_controlled_multi_worker_audit_replay_preview.py",
    "10_runtime/station_chief_operator_approval_queue_enforcement.py",
    "10_runtime/station_chief_release_candidate_hardening.py",
    "10_runtime/station_chief_controlled_production_readiness_gate.py",
    "10_runtime/station_chief_controlled_worker_hiring_activation_pilot.py",
    "10_runtime/station_chief_first_supervised_production_dry_run.py",
    "10_runtime/station_chief_limited_external_tool_supervised_pilot.py",
    "09_exports/station_chief_runtime_skeleton_report.md",
    "09_exports/station_chief_runtime_v3_3_report.md",
    "scripts/validate_station_chief_runtime_v3_3.py",
    "scripts/validate_station_chief_runtime_skeleton.py",
    "scripts/validate_station_chief_runtime_v0_2.py",
    "scripts/validate_station_chief_runtime_v0_3.py",
    "scripts/validate_station_chief_runtime_v0_4.py",
    "scripts/validate_station_chief_runtime_v0_5.py",
    "scripts/validate_station_chief_runtime_v0_6.py",
    "scripts/validate_station_chief_runtime_v0_7.py",
    "scripts/validate_station_chief_runtime_v0_8.py",
    "scripts/validate_station_chief_runtime_v0_9.py",
    "scripts/validate_station_chief_runtime_v1_0.py",
    "scripts/validate_station_chief_runtime_v1_1.py",
    "scripts/validate_station_chief_runtime_v1_2.py",
    "scripts/validate_station_chief_runtime_v1_3.py",
    "scripts/validate_station_chief_runtime_v1_4.py",
    "scripts/validate_station_chief_runtime_v1_5.py",
    "scripts/validate_station_chief_runtime_v1_6.py",
    "scripts/validate_station_chief_runtime_v1_7.py",
    "scripts/validate_station_chief_runtime_v1_8.py",
    "scripts/validate_station_chief_runtime_v2_0.py",
    "scripts/validate_station_chief_runtime_v2_1.py",
    "scripts/validate_station_chief_runtime_v2_2.py",
    "scripts/validate_station_chief_runtime_v2_3.py",
    "scripts/validate_station_chief_runtime_v2_4.py",
    "scripts/validate_station_chief_runtime_v2_5.py",
    "scripts/validate_station_chief_runtime_v2_6.py",
    "scripts/validate_station_chief_runtime_v2_7.py",
    "scripts/validate_station_chief_runtime_v2_8.py",
    "scripts/validate_station_chief_runtime_v2_9.py",
    "scripts/validate_station_chief_runtime_v3_0.py",
    "scripts/validate_station_chief_runtime_v3_1.py",
    "scripts/validate_station_chief_runtime_v3_2.py",
]

REQUIRED_RUNTIME_STRINGS = [
    'STATION_CHIEF_RUNTIME_VERSION = "3.3.0"',
    "attach_limited_external_tool_supervised_pilot",
    "write_limited_external_tool_supervised_pilot",
    "--limited-external-tool-supervised-pilot-schema",
    "--limited-external-tool-supervised-pilot",
    "--write-limited-external-tool-supervised-pilot",
    "--tool-pilot-label",
    "--tool-pilot-confirm-token",
    "--tool-category-label",
    "--tool-pilot-required-preflight-approver",
    "--tool-request-label",
    "--tool-quarantine-label",
    "limited_external_tool_supervised_pilot_bundle",
    "limited_external_tool_supervised_pilot_schema",
    "limited_external_tool_supervised_pilot_approval_gate",
    "single_external_tool_category_contract",
    "tool_invocation_denial_by_default",
    "human_tool_use_preflight_gate",
    "tool_request_envelope_preview",
    "tool_response_quarantine_preview",
    "tool_audit_proof",
    "tool_pilot_ledger",
    "tool_pilot_readiness_summary",
    "supervised_external_api_pilot_bridge",
]

REQUIRED_MODULE_STRINGS = [
    'LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_MODULE_VERSION = "3.3.0"',
    "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_STATUS",
    "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PHASE",
    "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN",
    "canonical_json",
    "sha256_digest",
    "normalize_tool_pilot_label",
    "generate_limited_external_tool_supervised_pilot_id",
    "create_limited_external_tool_supervised_pilot_schema",
    "create_limited_external_tool_supervised_pilot_approval_gate",
    "create_single_external_tool_category_contract",
    "create_tool_invocation_denial_by_default",
    "create_human_tool_use_preflight_gate",
    "create_tool_request_envelope_preview",
    "create_tool_response_quarantine_preview",
    "create_tool_audit_proof",
    "create_tool_pilot_ledger",
    "create_tool_pilot_readiness_summary",
    "create_supervised_external_api_pilot_bridge",
    "create_limited_external_tool_supervised_pilot_bundle",
]

FORBIDDEN_MODULE_STRINGS = [
    "eval(",
    "exec(",
    "compile(",
    "open(",
    "import socket",
    "from socket",
    "http.server",
    "socketserver",
    "uvicorn",
    "streamlit",
    "netlify",
    "vercel",
    "cloudflare",
    "firebase",
    "railway",
    "render",
    "gh api",
    "git push",
    "create_deployment",
    "create_commit",
    "update_ref",
    "__import__",
    "threading",
    "multiprocessing",
    "kill(",
    "terminate(",
    "getenv(",
    "os.getenv",
    "os.environ",
    "environ[",
    "datetime.now",
    "time.time",
]

README_STRINGS = [
    "Station Chief Runtime upgraded to v3.3.0.",
    "Limited external tool supervised pilot added.",
    "limited external tool supervised pilot schema",
    "limited external tool supervised pilot approval gate",
    "single external tool category contract",
    "tool invocation denial by default",
    "human tool-use preflight gate",
    "tool request envelope preview",
    "tool response quarantine preview",
    "tool audit proof",
    "tool pilot ledger",
    "tool pilot readiness summary",
    "supervised external API pilot bridge",
    "no real external tool invocation",
    "no live API calls",
    "no credential use",
    "no secret reads",
    "no environment reads",
    "no network access",
    "no socket access",
    "no deployment",
    "no production execution",
    "no full workforce activation",
]

README_FORBIDDEN = ["Explain that", "Include:", "List:", "Write:"]


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_contains(errors: list[str], path: Path, needles: list[str]) -> None:
    text = read_text(path)
    for needle in needles:
        if needle not in text:
            add_error(errors, f"Missing required text in {path.relative_to(REPO_ROOT)}: {needle}")


def require_not_contains(errors: list[str], path: Path, needles: list[str]) -> None:
    text = read_text(path)
    for needle in needles:
        if needle in text:
            add_error(errors, f"Forbidden text present in {path.relative_to(REPO_ROOT)}: {needle}")


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, env=env)


def load_json_output(errors: list[str], args: list[str], label: str) -> dict | list | None:
    proc = run_command(args)
    if proc.returncode != 0:
        add_error(errors, f"{label} failed with exit {proc.returncode}: {proc.stderr.strip()}")
        return None
    try:
        return json.loads(proc.stdout.strip())
    except Exception as exc:
        add_error(errors, f"{label} did not produce valid JSON: {exc}; stdout={proc.stdout.strip()}")
        return None


def check_demo(errors: list[str]) -> None:
    demo = load_json_output(errors, ["python3", "10_runtime/station_chief_runtime.py", "--demo"], "--demo")
    if not isinstance(demo, dict):
        return
    require_fields = {
        "station_chief_runtime_version": "3.3.0",
        "runtime_status": "limited_external_tool_supervised_pilot",
        "release_status": "STABLE_LOCKED",
        "next_step": "Next step: build supervised external API pilot.",
    }
    for key, expected in require_fields.items():
        if demo.get(key) != expected:
            add_error(errors, f"--demo {key} mismatch: expected {expected!r}, got {demo.get(key)!r}")
    evidence = demo.get("evidence", {})
    evidence_checks = {
        "baseline_preserved": True,
        "external_actions_taken": False,
        "limited_external_tool_supervised_pilot_available": True,
        "limited_external_tool_supervised_pilot_preview_only": True,
        "limited_external_tool_supervised_pilot_requires_token": True,
        "single_external_tool_category_limit_is_one": True,
        "tool_invocation_denied_by_default": True,
        "limited_external_tool_supervised_pilot_does_not_invoke_external_tools": True,
        "limited_external_tool_supervised_pilot_does_not_call_live_apis": True,
        "limited_external_tool_supervised_pilot_does_not_use_network_access": True,
        "limited_external_tool_supervised_pilot_does_not_open_sockets": True,
        "limited_external_tool_supervised_pilot_does_not_use_credentials": True,
        "limited_external_tool_supervised_pilot_does_not_read_secrets": True,
        "limited_external_tool_supervised_pilot_does_not_read_environment": True,
        "limited_external_tool_supervised_pilot_does_not_deploy": True,
        "limited_external_tool_supervised_pilot_does_not_execute_production": True,
        "limited_external_tool_supervised_pilot_does_not_modify_repo_files": True,
        "supervised_external_api_pilot_not_yet_active": True,
    }
    for key, expected in evidence_checks.items():
        if evidence.get(key) is not expected:
            add_error(errors, f"--demo evidence.{key} mismatch: expected {expected!r}, got {evidence.get(key)!r}")


def check_fixture(errors: list[str]) -> None:
    fixture = load_json_output(errors, ["python3", "10_runtime/station_chief_runtime.py", "--fixture-test"], "--fixture-test")
    if not isinstance(fixture, dict):
        return
    checks = {
        "fixture_test_status": "PASS",
        "runtime_version": "3.3.0",
        "case_count": 5,
        "failed": 0,
    }
    for key, expected in checks.items():
        if fixture.get(key) != expected:
            add_error(errors, f"--fixture-test {key} mismatch: expected {expected!r}, got {fixture.get(key)!r}")


def check_schema(errors: list[str]) -> None:
    schema = load_json_output(errors, ["python3", "10_runtime/station_chief_runtime.py", "--limited-external-tool-supervised-pilot-schema"], "limited external tool schema")
    if not isinstance(schema, dict):
        return
    checks = {
        "limited_external_tool_supervised_pilot_schema_version": "3.3.0",
        "schema_status": "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PREVIEW_ONLY",
        "single_tool_category_limit": 1,
    }
    for key, expected in checks.items():
        if schema.get(key) != expected:
            add_error(errors, f"schema {key} mismatch: expected {expected!r}, got {schema.get(key)!r}")
    required_sections = set(schema.get("required_sections", []))
    for section in [
        "limited_external_tool_supervised_pilot_approval_gate",
        "single_external_tool_category_contract",
        "tool_invocation_denial_by_default",
        "human_tool_use_preflight_gate",
        "tool_request_envelope_preview",
        "tool_response_quarantine_preview",
        "tool_audit_proof",
        "tool_pilot_ledger",
        "tool_pilot_readiness_summary",
        "supervised_external_api_pilot_bridge",
    ]:
        if section not in required_sections:
            add_error(errors, f"schema missing required section: {section}")
    blocked = set(schema.get("blocked_tool_pilot_modes", []))
    for mode in [
        "real_external_tool_invocation",
        "live_api_call",
        "network_access",
        "socket_connection",
        "credential_use",
        "secret_read",
        "environment_variable_read",
        "deployment",
        "production_execution",
        "full_workforce_activation",
    ]:
        if mode not in blocked:
            add_error(errors, f"schema missing blocked mode: {mode}")
    required_tokens = set(schema.get("required_confirmation_tokens", []))
    if "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT" not in required_tokens:
        add_error(errors, "schema missing required confirmation token")
    for key, value in schema.items():
        if key.endswith("_performed") or key.endswith("_taken") or key.endswith("_authorized") or key in {"baseline_preserved", "external_actions_taken", "repo_files_modified", "execution_authorized"}:
            if value is not False and key != "baseline_preserved":
                add_error(errors, f"schema safety boolean not false: {key}={value!r}")


def check_default_and_token_paths(errors: list[str]) -> None:
    default_result = load_json_output(
        errors,
        [
            "python3",
            "10_runtime/station_chief_runtime.py",
            "--command",
            "check please",
            "--limited-external-tool-supervised-pilot",
            "--json",
        ],
        "default limited tool pilot",
    )
    if isinstance(default_result, dict):
        bundle = default_result.get("limited_external_tool_supervised_pilot_bundle")
        if not isinstance(bundle, dict):
            add_error(errors, "default limited pilot output missing bundle")
        else:
            checks = {
                "limited_external_tool_supervised_pilot_approval_gate.gate_status": "BLOCKED_PENDING_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL",
                "limited_external_tool_supervised_pilot_approval_gate.confirmation_token_valid": False,
                "limited_external_tool_supervised_pilot_approval_gate.local_tool_pilot_records_authorized": False,
                "single_external_tool_category_contract.contract_status": "BLOCKED",
                "tool_invocation_denial_by_default.denial_status": "BLOCKED",
                "human_tool_use_preflight_gate.preflight_status": "BLOCKED",
                "tool_request_envelope_preview.envelope_status": "BLOCKED",
                "tool_response_quarantine_preview.preview_status": "BLOCKED",
                "tool_audit_proof.audit_status": "BLOCKED",
                "tool_pilot_ledger.ledger_status": "BLOCKED",
                "tool_pilot_readiness_summary.readiness_status": "BLOCKED",
                "supervised_external_api_pilot_bridge.ready_for_supervised_external_api_pilot": False,
            }
            for dotted, expected in checks.items():
                current = bundle
                for part in dotted.split('.'):
                    current = current.get(part) if isinstance(current, dict) else None
                if current != expected:
                    add_error(errors, f"default limited pilot {dotted} mismatch: expected {expected!r}, got {current!r}")
            for section in [
                bundle.get("limited_external_tool_supervised_pilot_approval_gate", {}),
                bundle.get("single_external_tool_category_contract", {}),
                bundle.get("tool_invocation_denial_by_default", {}),
                bundle.get("human_tool_use_preflight_gate", {}),
                bundle.get("tool_request_envelope_preview", {}),
                bundle.get("tool_response_quarantine_preview", {}),
                bundle.get("tool_audit_proof", {}),
                bundle.get("tool_pilot_ledger", {}),
                bundle.get("tool_pilot_readiness_summary", {}),
                bundle.get("supervised_external_api_pilot_bridge", {}),
            ]:
                if isinstance(section, dict):
                    for key, value in section.items():
                        if key.endswith("_performed") or key.endswith("_taken") or key.endswith("_authorized") or key in {"baseline_preserved", "external_actions_taken", "repo_files_modified", "execution_authorized"}:
                            if key == "local_tool_pilot_records_authorized":
                                continue
                            if value is not False and key != "baseline_preserved":
                                add_error(errors, f"default limited pilot safety boolean not false: {key}={value!r}")

    token_result = load_json_output(
        errors,
        [
            "python3",
            "10_runtime/station_chief_runtime.py",
            "--command",
            "check please",
            "--limited-external-tool-supervised-pilot",
            "--tool-pilot-confirm-token",
            "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT",
            "--json",
        ],
        "token limited tool pilot",
    )
    if isinstance(token_result, dict):
        bundle = token_result.get("limited_external_tool_supervised_pilot_bundle")
        if not isinstance(bundle, dict):
            add_error(errors, "token limited pilot output missing bundle")
        else:
            checks = {
                "limited_external_tool_supervised_pilot_approval_gate.gate_status": "APPROVED_FOR_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_RECORDS",
                "limited_external_tool_supervised_pilot_approval_gate.confirmation_token_valid": True,
                "limited_external_tool_supervised_pilot_approval_gate.local_tool_pilot_records_authorized": True,
                "single_external_tool_category_contract.contract_status": "TOOL_CATEGORY_CONTRACT_CREATED",
                "single_external_tool_category_contract.single_tool_category_limit": 1,
                "tool_invocation_denial_by_default.denial_status": "TOOL_INVOCATION_DENIED_BY_DEFAULT",
                "human_tool_use_preflight_gate.preflight_status": "TOOL_USE_PREFLIGHT_REQUIREMENT_CREATED",
                "tool_request_envelope_preview.envelope_status": "TOOL_REQUEST_ENVELOPE_PREVIEW_CREATED",
                "tool_response_quarantine_preview.preview_status": "TOOL_RESPONSE_QUARANTINE_PREVIEW_CREATED",
                "tool_audit_proof.audit_status": "PASS",
                "tool_pilot_ledger.ledger_status": "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_LEDGER",
                "tool_pilot_readiness_summary.readiness_status": "READY_FOR_NEXT_LAYER",
                "supervised_external_api_pilot_bridge.next_layer": "Supervised External API Pilot",
                "supervised_external_api_pilot_bridge.ready_for_supervised_external_api_pilot": True,
            }
            for dotted, expected in checks.items():
                current = bundle
                for part in dotted.split('.'):
                    current = current.get(part) if isinstance(current, dict) else None
                if current != expected:
                    add_error(errors, f"token limited pilot {dotted} mismatch: expected {expected!r}, got {current!r}")
            for section in [
                bundle.get("limited_external_tool_supervised_pilot_approval_gate", {}),
                bundle.get("single_external_tool_category_contract", {}),
                bundle.get("tool_invocation_denial_by_default", {}),
                bundle.get("human_tool_use_preflight_gate", {}),
                bundle.get("tool_request_envelope_preview", {}),
                bundle.get("tool_response_quarantine_preview", {}),
                bundle.get("tool_audit_proof", {}),
                bundle.get("tool_pilot_ledger", {}),
                bundle.get("tool_pilot_readiness_summary", {}),
                bundle.get("supervised_external_api_pilot_bridge", {}),
            ]:
                if isinstance(section, dict):
                    for key, value in section.items():
                        if key.endswith("_performed") or key.endswith("_taken") or key.endswith("_authorized") or key in {"baseline_preserved", "external_actions_taken", "repo_files_modified", "execution_authorized"}:
                            if key == "local_tool_pilot_records_authorized":
                                continue
                            if value is not False and key != "baseline_preserved":
                                add_error(errors, f"token limited pilot safety boolean not false: {key}={value!r}")
            gate = bundle.get("limited_external_tool_supervised_pilot_approval_gate", {})
            for key in [
                "real_external_tool_invocation_authorized",
                "live_api_call_authorized",
                "network_access_authorized",
                "socket_access_authorized",
                "credential_use_authorized",
                "secret_read_authorized",
                "environment_read_authorized",
                "deployment_authorized",
                "production_execution_authorized",
                "production_activation_authorized",
                "real_task_execution_authorized",
                "live_task_assignment_authorized",
                "live_worker_routing_authorized",
                "live_orchestration_authorized",
                "worker_process_start_authorized",
                "repo_mutation_authorized",
                "external_actions_taken",
                "repo_files_modified",
                "execution_authorized",
            ]:
                if gate.get(key) is not False:
                    add_error(errors, f"token limited pilot dangerous authorization not false: {key}={gate.get(key)!r}")


def check_next_layer(errors: list[str]) -> None:
    result = load_json_output(
        errors,
        [
            "python3",
            "10_runtime/station_chief_runtime.py",
            "--command",
            "build supervised external API pilot",
            "--limited-external-tool-supervised-pilot",
            "--tool-pilot-confirm-token",
            "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT",
            "--json",
        ],
        "next-layer command",
    )
    if not isinstance(result, dict):
        return
    bundle = result.get("limited_external_tool_supervised_pilot_bundle", {})
    if not isinstance(bundle, dict):
        add_error(errors, "next-layer output missing bundle")
        return
    readiness = bundle.get("tool_pilot_readiness_summary", {})
    bridge = bundle.get("supervised_external_api_pilot_bridge", {})
    if readiness.get("readiness_status") != "READY_FOR_NEXT_LAYER":
        add_error(errors, f"next-layer readiness status mismatch: {readiness.get('readiness_status')!r}")
    if readiness.get("next_layer") != "Supervised External API Pilot":
        add_error(errors, f"next-layer summary mismatch: {readiness.get('next_layer')!r}")
    if bridge.get("next_layer") != "Supervised External API Pilot" or bridge.get("ready_for_supervised_external_api_pilot") is not True:
        add_error(errors, "next-layer bridge mismatch")
    if bundle.get("tool_audit_proof", {}).get("audit_status") != "PASS":
        add_error(errors, "next-layer audit proof not PASS")


def check_write_limited(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        result = load_json_output(
            errors,
            [
                "python3",
                "10_runtime/station_chief_runtime.py",
                "--command",
                "check please",
                "--write-limited-external-tool-supervised-pilot",
                temp_dir,
                "--tool-pilot-confirm-token",
                "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT",
            ],
            "write limited pilot",
        )
        if not isinstance(result, dict):
            return
        summary = result.get("limited_external_tool_supervised_pilot_write_summary")
        if not isinstance(summary, dict):
            add_error(errors, "write-limited output missing write summary")
            return
        write_dir = Path(summary.get("limited_external_tool_supervised_pilot_dir", ""))
        if not write_dir.exists():
            add_error(errors, f"limited pilot write dir does not exist: {write_dir}")
            return
        expected_files = [
            "limited_external_tool_supervised_pilot_bundle.json",
            "limited_external_tool_supervised_pilot_schema.json",
            "limited_external_tool_supervised_pilot_approval_gate.json",
            "single_external_tool_category_contract.json",
            "tool_invocation_denial_by_default.json",
            "human_tool_use_preflight_gate.json",
            "tool_request_envelope_preview.json",
            "tool_response_quarantine_preview.json",
            "tool_audit_proof.json",
            "tool_pilot_ledger.json",
            "tool_pilot_readiness_summary.json",
            "supervised_external_api_pilot_bridge.json",
            "limited_external_tool_supervised_pilot_manifest.json",
        ]
        for filename in expected_files:
            if not (write_dir / filename).exists():
                add_error(errors, f"missing limited pilot artifact: {filename}")
        manifest_path = write_dir / "limited_external_tool_supervised_pilot_manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("runtime_version") != "3.3.0":
                add_error(errors, "limited pilot manifest runtime version mismatch")
            if manifest.get("status") != "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PREVIEW_ONLY":
                add_error(errors, "limited pilot manifest status mismatch")
            if manifest.get("baseline_preserved") is not True or manifest.get("external_actions_taken") is not False:
                add_error(errors, "limited pilot manifest safety flags mismatch")


def check_write_artifacts(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as run_dir, tempfile.TemporaryDirectory() as registry_dir:
        result = load_json_output(
            errors,
            [
                "python3",
                "10_runtime/station_chief_runtime.py",
                "--command",
                "check please",
                "--write-artifacts",
                run_dir,
                "--registry-dir",
                registry_dir,
                "--limited-external-tool-supervised-pilot",
                "--tool-pilot-confirm-token",
                "YES_I_APPROVE_LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT",
            ],
            "write artifacts",
        )
        if not isinstance(result, dict):
            return
        summary = result.get("artifact_write_summary")
        if not isinstance(summary, dict):
            add_error(errors, "write-artifacts output missing artifact_write_summary")
            return
        run_id = summary.get("run_id", "")
        if not str(run_id).startswith("station-chief-v3-3-check-please-"):
            add_error(errors, f"artifact run_id prefix mismatch: {run_id!r}")
        artifact_dir = Path(summary.get("artifact_dir", ""))
        if not artifact_dir.exists():
            add_error(errors, f"artifact dir missing: {artifact_dir}")
            return
        manifest_path = artifact_dir / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("artifact_type") != "station_chief_runtime_v3_3_artifacts":
                add_error(errors, "artifact manifest type mismatch")
            if manifest.get("runtime_version") != "3.3.0":
                add_error(errors, "artifact manifest runtime version mismatch")
            if manifest.get("limited_external_tool_supervised_pilot_schema") is not True:
                add_error(errors, "artifact manifest missing limited pilot schema flag")
        registry_path = Path(registry_dir) / "run_registry.json"
        index_path = Path(registry_dir) / "runtime_index.json"
        if registry_path.exists():
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            if registry.get("registry_version") != "3.3.0":
                add_error(errors, "registry version mismatch")
        else:
            add_error(errors, "registry file missing")
        if index_path.exists():
            index = json.loads(index_path.read_text(encoding="utf-8"))
            if index.get("index_version") != "3.3.0":
                add_error(errors, "runtime index version mismatch")
        else:
            add_error(errors, "runtime index file missing")


def check_regressions(errors: list[str]) -> None:
    regression_checks = [
        (["python3", "10_runtime/station_chief_runtime.py", "--stable-release-manifest"], "stable_release_manifest"),
        (["python3", "10_runtime/station_chief_runtime.py", "--release-lock"], "release_lock_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-execution"], "controlled_execution_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--work-order-executor"], "work_order_executor_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--worker-hiring-registry"], "worker_hiring_registry_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--department-routing"], "department_routing_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--multi-agent-orchestration"], "multi_agent_orchestration_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--operator-console"], "operator_console_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--github-patch-hardening"], "github_patch_hardening_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--deployment-packaging"], "deployment_packaging_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-worker-execution"], "controlled_worker_execution_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--tool-permission-binding"], "tool_permission_binding_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--live-telemetry-abort"], "live_execution_telemetry_abort_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--post-run-audit-expansion"], "post_run_audit_expansion_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--multi-worker-sandbox-coordination"], "multi_worker_sandbox_coordination_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-external-tool-preview"], "controlled_external_tool_adapter_preview_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--permissioned-external-api-dry-run"], "permissioned_external_api_dry_run_preview_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-multi-worker-audit-replay-preview"], "controlled_multi_worker_audit_replay_preview_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--operator-approval-queue-enforcement"], "operator_approval_queue_enforcement_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--release-candidate-hardening"], "release_candidate_hardening_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-production-readiness-gate"], "controlled_production_readiness_gate_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--controlled-worker-hiring-activation-pilot"], "controlled_worker_hiring_activation_pilot_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--first-supervised-production-dry-run"], "first_supervised_production_dry_run_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--limited-external-tool-supervised-pilot"], "limited_external_tool_supervised_pilot_bundle"),
        (["python3", "10_runtime/station_chief_runtime.py", "--approval-handoff"], "approval_handoff_packet"),
    ]
    for args, expected_key in regression_checks:
        result = load_json_output(errors, args, "regression check " + " ".join(args[2:]))
        if not isinstance(result, dict):
            continue
        if expected_key not in result or result.get(expected_key) is None:
            add_error(errors, f"regression output missing expected key: {expected_key} for {' '.join(args)}")
        for key, value in result.items():
            if key in {"baseline_preserved", "external_actions_taken", "execution_authorized", "repo_files_modified"}:
                if key in {"baseline_preserved"} and value is not True:
                    add_error(errors, f"regression field {key} not true for {' '.join(args)}")
                if key in {"external_actions_taken", "execution_authorized", "repo_files_modified"} and value is not False:
                    add_error(errors, f"regression field {key} not false for {' '.join(args)}")


def check_texts(errors: list[str]) -> None:
    require_contains(errors, READ_ME, README_STRINGS)
    require_not_contains(errors, READ_ME, README_FORBIDDEN)
    require_contains(errors, SKELETON, [
        "Station Chief Runtime upgraded to v3.3.0.",
        "Limited external tool supervised pilot added.",
        "limited external tool supervised pilot schema",
        "limited external tool supervised pilot approval gate",
        "single external tool category contract",
        "tool invocation denial by default",
        "human tool-use preflight gate",
        "tool request envelope preview",
        "tool response quarantine preview",
        "tool audit proof",
        "tool pilot ledger",
        "tool pilot readiness summary",
        "supervised external API pilot bridge",
        "no real external tool invocation",
        "no live API calls",
        "no credential use",
        "no secret reads",
        "no environment reads",
        "no network access",
        "no socket access",
        "no deployment",
        "no production execution",
        "no full workforce activation",
        "python3 scripts/validate_station_chief_runtime_v3_3.py",
        "Next recommended build step: build supervised external API pilot.",
    ])
    require_not_contains(errors, SKELETON, README_FORBIDDEN)
    require_contains(errors, V3_3_REPORT, [
        "Station Chief Runtime upgraded to v3.3.0. Locked 175-family baseline preserved. Limited external tool supervised pilot added.",
        "limited external tool supervised pilot schema",
        "limited external tool supervised pilot approval gate",
        "single external tool category contract",
        "tool invocation denial by default",
        "human tool-use preflight gate",
        "tool request envelope preview",
        "tool response quarantine preview",
        "tool audit proof",
        "tool pilot ledger",
        "tool pilot readiness summary",
        "supervised external API pilot bridge",
        "no real external tool invocation",
        "no live API calls",
        "no credential use",
        "no secret reads",
        "no environment reads",
        "no network access",
        "no socket access",
        "no deployment",
        "no production execution",
        "no full workforce activation",
        "Next recommended build step: build supervised external API pilot.",
    ])
    require_not_contains(errors, V3_3_REPORT, README_FORBIDDEN)
    require_contains(errors, RUNTIME, REQUIRED_RUNTIME_STRINGS)
    require_contains(errors, V3_3_MODULE, REQUIRED_MODULE_STRINGS)
    require_not_contains(errors, V3_3_MODULE, FORBIDDEN_MODULE_STRINGS)


def check_scope(errors: list[str]) -> None:
    proc = run_command(["git", "status", "--short"])
    if proc.returncode != 0:
        add_error(errors, f"git status failed: {proc.stderr.strip()}")
        return
    diff = run_command(["git", "diff", "--name-only"])
    if diff.returncode != 0:
        add_error(errors, f"git diff --name-only failed: {diff.stderr.strip()}")
        return
    changed = [line.strip() for line in diff.stdout.splitlines() if line.strip()]
    allowed = set(EXPECTED_FILES) | {"10_runtime/station_chief_limited_external_tool_supervised_pilot.py"}
    for path in changed:
        if "__pycache__" in path:
            continue
        if path not in allowed:
            add_error(errors, f"unexpected changed file in diff: {path}")
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if "__pycache__" in path:
            continue
        if path not in allowed:
            add_error(errors, f"unexpected changed file in status: {path}")


def main() -> int:
    errors: list[str] = []

    for required in EXPECTED_FILES:
        if not (REPO_ROOT / required).exists():
            add_error(errors, f"missing required file: {required}")

    check_texts(errors)
    check_demo(errors)
    check_fixture(errors)
    check_schema(errors)
    check_default_and_token_paths(errors)
    check_next_layer(errors)
    check_write_limited(errors)
    check_write_artifacts(errors)
    check_regressions(errors)
    check_scope(errors)

    if errors:
        for error in errors:
            print(error)
        print("FAIL")
        return 1

    print("PASS: Station Chief Runtime v3.3 valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
