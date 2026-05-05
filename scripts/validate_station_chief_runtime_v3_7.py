#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
MODULE = REPO_ROOT / "10_runtime" / "station_chief_credential_vault_denial_secret_handling_proof.py"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v3_7_report.md"

REQUIRED_FILES = [
    RUNTIME,
    MODULE,
    ADAPTERS,
    RELEASE_LOCK,
    README,
    SKELETON,
    REPORT,
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_7.py",
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


def check_demo(errors: list[str]) -> None:
    demo = run_json([sys.executable, str(RUNTIME), "--demo"])
    require(demo.get("station_chief_runtime_version") == "3.7.0", "demo runtime version is not 3.7.0", errors)
    require(demo.get("runtime_status") == "credential_vault_denial_secret_handling_proof", "demo runtime status incorrect", errors)
    require(demo.get("release_status") == "STABLE_LOCKED", "demo release status incorrect", errors)
    evidence = demo.get("evidence", {})
    for key in [
        "baseline_preserved",
        "credential_vault_denial_secret_handling_proof_available",
        "credential_vault_denial_secret_handling_proof_preview_only",
        "credential_vault_denial_secret_handling_proof_requires_token",
        "credential_vault_denial_secret_handling_proof_does_not_access_credentials",
        "credential_vault_denial_secret_handling_proof_does_not_read_secrets",
        "credential_vault_denial_secret_handling_proof_does_not_read_environment",
        "credential_vault_denial_secret_handling_proof_does_not_call_live_apis",
        "credential_vault_denial_secret_handling_proof_does_not_use_network_access",
        "credential_vault_denial_secret_handling_proof_does_not_open_sockets",
        "credential_vault_denial_secret_handling_proof_does_not_deploy",
        "credential_vault_denial_secret_handling_proof_does_not_execute_production",
        "credential_vault_denial_secret_handling_proof_does_not_modify_repo_files",
    ]:
        require(evidence.get(key) is True or demo.get(key) is True, f"demo missing true evidence: {key}", errors)
    require(evidence.get("external_actions_taken") is False, "demo external_actions_taken not false", errors)


def check_fixture_tests(errors: list[str]) -> None:
    fixture = run_json([sys.executable, str(RUNTIME), "--fixture-test"])
    require(fixture.get("fixture_test_status") == "PASS", "fixture tests failed", errors)
    require(fixture.get("runtime_version") == "3.7.0", "fixture runtime version incorrect", errors)
    require(fixture.get("case_count") == 5, "fixture case count incorrect", errors)
    require(fixture.get("failed") == 0, "fixture failed count not zero", errors)


def check_schema(errors: list[str]) -> None:
    schema = run_json([sys.executable, str(RUNTIME), "--credential-vault-denial-secret-handling-proof-schema"])
    require(schema.get("credential_vault_denial_secret_handling_proof_schema_version") == "3.7.0", "schema version incorrect", errors)
    require(schema.get("schema_status") == "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_PREVIEW_ONLY", "schema status incorrect", errors)
    for section in [
        "credential_vault_denial_secret_handling_proof_approval_gate",
        "credential_access_denial_contract",
        "secret_read_denial_contract",
        "environment_variable_denial_contract",
        "credential_vault_boundary_record",
        "secret_handling_boundary_record",
        "environment_read_boundary_record",
        "credential_secret_audit_proof",
        "credential_secret_denial_ledger",
        "credential_secret_readiness_summary",
        "network_socket_lockdown_proof_bridge",
    ]:
        require(section in set(schema.get("required_sections", [])), f"schema missing required section: {section}", errors)
    for mode in [
        "credential_vault_access",
        "credential_use",
        "secret_read",
        "environment_variable_read",
        "token_read",
        "api_key_read",
        "oauth_use",
        "service_account_use",
        "live_api_call",
        "network_access",
        "socket_connection",
        "deployment",
        "production_execution",
        "production_activation",
        "real_external_tool_invocation",
        "live_task_assignment",
        "live_worker_routing",
        "live_orchestration",
        "worker_process_start",
        "full_workforce_activation",
    ]:
        require(mode in set(schema.get("blocked_proof_modes", [])), f"schema missing blocked mode: {mode}", errors)
    require("YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF" in set(schema.get("required_confirmation_tokens", [])), "schema missing token requirement", errors)


def check_no_token_and_token_paths(errors: list[str]) -> None:
    base = [sys.executable, str(RUNTIME), "--command", "check please", "--credential-vault-denial-secret-handling-proof", "--json"]
    no_token = run_json(base)
    require("credential_vault_denial_secret_handling_proof_bundle" in no_token, "no-token result missing proof bundle", errors)
    gate = no_token.get("credential_vault_denial_secret_handling_proof_approval_gate", {})
    require(gate.get("gate_status") == "BLOCKED_PENDING_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_APPROVAL", "no-token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is False, "no-token validity incorrect", errors)
    require(gate.get("local_credential_secret_proof_records_authorized") is False, "no-token local authorization incorrect", errors)
    require(no_token.get("credential_access_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token credential access contract incorrect", errors)
    require(no_token.get("secret_read_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token secret read contract incorrect", errors)
    require(no_token.get("environment_variable_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token env contract incorrect", errors)
    require(no_token.get("credential_secret_audit_proof", {}).get("audit_status") == "BLOCKED", "no-token audit status incorrect", errors)
    require(no_token.get("credential_secret_denial_ledger", {}).get("ledger_status") == "BLOCKED", "no-token ledger status incorrect", errors)
    require(no_token.get("credential_secret_readiness_summary", {}).get("readiness_status") == "BLOCKED", "no-token readiness status incorrect", errors)
    require(no_token.get("network_socket_lockdown_proof_bridge", {}).get("ready_for_network_socket_lockdown_proof") is False, "no-token bridge readiness incorrect", errors)
    require(no_token.get("credential_secret_audit_proof", {}).get("baseline_preserved") is True, "no-token baseline not preserved", errors)

    token = run_json([sys.executable, str(RUNTIME), "--command", "check please", "--credential-vault-denial-secret-handling-proof", "--credential-secret-confirm-token", "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF", "--json"])
    gate = token.get("credential_vault_denial_secret_handling_proof_approval_gate", {})
    require(gate.get("gate_status") == "APPROVED_FOR_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_RECORDS", "token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is True, "token validity incorrect", errors)
    require(gate.get("local_credential_secret_proof_records_authorized") is True, "token local authorization incorrect", errors)
    require(token.get("credential_access_denial_contract", {}).get("contract_status") == "CREDENTIAL_ACCESS_DENIAL_CONTRACT_CREATED", "token credential access contract incorrect", errors)
    require(token.get("secret_read_denial_contract", {}).get("contract_status") == "SECRET_READ_DENIAL_CONTRACT_CREATED", "token secret read contract incorrect", errors)
    require(token.get("environment_variable_denial_contract", {}).get("contract_status") == "ENVIRONMENT_VARIABLE_DENIAL_CONTRACT_CREATED", "token env contract incorrect", errors)
    require(token.get("credential_secret_audit_proof", {}).get("audit_status") == "PASS", "token audit status incorrect", errors)
    require(token.get("credential_secret_denial_ledger", {}).get("ledger_status") == "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_LEDGER", "token ledger status incorrect", errors)
    require(token.get("credential_secret_readiness_summary", {}).get("readiness_status") == "READY_FOR_NEXT_LAYER", "token readiness status incorrect", errors)
    require(token.get("network_socket_lockdown_proof_bridge", {}).get("ready_for_network_socket_lockdown_proof") is True, "token bridge readiness incorrect", errors)
    for key in [
        "credential_vault_access_authorized",
        "credential_use_authorized",
        "secret_read_authorized",
        "environment_read_authorized",
        "token_read_authorized",
        "api_key_read_authorized",
        "oauth_use_authorized",
        "service_account_use_authorized",
        "live_api_call_authorized",
        "network_access_authorized",
        "socket_access_authorized",
        "deployment_authorized",
        "production_execution_authorized",
        "production_activation_authorized",
        "real_external_tool_invocation_authorized",
        "live_task_assignment_authorized",
        "live_worker_routing_authorized",
        "live_orchestration_authorized",
        "worker_process_start_authorized",
        "repo_mutation_authorized",
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
            "--write-credential-vault-denial-secret-handling-proof",
            tmpdir,
            "--credential-secret-confirm-token",
            "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF",
        ])
        summary = out.get("credential_vault_denial_secret_handling_proof_write_summary", {})
        require(bool(summary), "write proof summary missing", errors)
        proof_dir = Path(summary.get("credential_vault_denial_secret_handling_proof_dir", ""))
        require(proof_dir.exists(), "write proof directory missing", errors)
        expected = [
            "credential_vault_denial_secret_handling_proof_bundle.json",
            "credential_vault_denial_secret_handling_proof_schema.json",
            "credential_vault_denial_secret_handling_proof_approval_gate.json",
            "credential_access_denial_contract.json",
            "secret_read_denial_contract.json",
            "environment_variable_denial_contract.json",
            "credential_vault_boundary_record.json",
            "secret_handling_boundary_record.json",
            "environment_read_boundary_record.json",
            "credential_secret_audit_proof.json",
            "credential_secret_denial_ledger.json",
            "credential_secret_readiness_summary.json",
            "network_socket_lockdown_proof_bridge.json",
            "credential_vault_denial_secret_handling_proof_manifest.json",
        ]
        for filename in expected:
            require((proof_dir / filename).exists(), f"write proof missing file: {filename}", errors)
        manifest = json.loads((proof_dir / "credential_vault_denial_secret_handling_proof_manifest.json").read_text())
        require(manifest.get("runtime_version") == "3.7.0", "write proof manifest runtime version incorrect", errors)
        require(manifest.get("status") == "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_PREVIEW_ONLY", "write proof manifest status incorrect", errors)
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
            "--credential-vault-denial-secret-handling-proof",
            "--credential-secret-confirm-token",
            "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF",
        ])
        summary = out.get("artifact_write_summary", {})
        require(bool(summary), "artifact write summary missing", errors)
        run_id = summary.get("run_id", "")
        require(run_id.startswith("station-chief-v3-7-check-please-"), "artifact write run id prefix incorrect", errors)
        artifact_dir = Path(summary.get("artifact_dir", ""))
        require(artifact_dir.exists(), "artifact directory missing", errors)
        manifest = json.loads((artifact_dir / "manifest.json").read_text())
        require(manifest.get("artifact_type") == "station_chief_runtime_v3_7_artifacts", "artifact manifest type incorrect", errors)
        require(manifest.get("runtime_version") == "3.7.0", "artifact manifest runtime version incorrect", errors)
        registry = json.loads((Path(reg_dir) / "run_registry.json").read_text())
        index = json.loads((Path(reg_dir) / "runtime_index.json").read_text())
        require(registry.get("registry_version") == "3.7.0", "registry version incorrect", errors)
        require(index.get("index_version") == "3.7.0", "runtime index version incorrect", errors)
        require(summary.get("registry_updated") is True, "registry not updated", errors)


def check_docs(errors: list[str]) -> None:
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    for text, label in [
        (readme, "README"),
        (skeleton, "skeleton report"),
        (report, "v3.7 report"),
    ]:
        require("Station Chief Runtime upgraded to v3.7.0." in text, f"{label} missing v3.7 status", errors)
        require("Credential vault denial and secret handling proof added." in text or "credential vault denial and secret handling proof" in text, f"{label} missing v3.7 capability phrase", errors)
        require("Next recommended step: build network/socket lockdown proof." in text, f"{label} missing next-step text", errors)


def check_smoke(errors: list[str]) -> None:
    commands = [
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
        ["--approval-handoff"],
    ]
    for extra in commands:
        proc = run_command([sys.executable, str(RUNTIME), "--command", "check please", "--json", *extra])
        require(proc.returncode == 0, f"smoke command failed: {' '.join(extra)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)


def main() -> None:
    errors: list[str] = []
    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.7 runtime files.")

    for path in REQUIRED_FILES:
        require(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}", errors)

    check_strings(
        RUNTIME,
        [
            'STATION_CHIEF_RUNTIME_VERSION = "3.7.0"',
            "credential_vault_denial_secret_handling_proof",
            "attach_credential_vault_denial_secret_handling_proof",
            "write_credential_vault_denial_secret_handling_proof",
            "--credential-vault-denial-secret-handling-proof-schema",
            "--credential-vault-denial-secret-handling-proof",
            "--write-credential-vault-denial-secret-handling-proof",
            "--credential-secret-label",
            "--credential-secret-confirm-token",
            "--credential-boundary-label",
            "--secret-boundary-label",
            "--environment-boundary-label",
            "credential_vault_denial_secret_handling_proof_bundle",
            "credential_vault_denial_secret_handling_proof_schema",
            "credential_vault_denial_secret_handling_proof_approval_gate",
            "credential_access_denial_contract",
            "secret_read_denial_contract",
            "environment_variable_denial_contract",
            "credential_vault_boundary_record",
            "secret_handling_boundary_record",
            "environment_read_boundary_record",
            "credential_secret_audit_proof",
            "credential_secret_denial_ledger",
            "credential_secret_readiness_summary",
            "network_socket_lockdown_proof_bridge",
        ],
        ["import requests", "urllib.request", "os.system", "pip install", "npm install", "live API", "API key", "import subprocess"],
        errors,
    )
    check_strings(
        MODULE,
        [
            'CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_MODULE_VERSION = "3.7.0"',
            "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_STATUS",
            "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_PHASE",
            "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_APPROVAL_TOKEN",
            "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF",
            "canonical_json",
            "sha256_digest",
            "normalize_credential_secret_label",
            "generate_credential_vault_denial_secret_handling_proof_id",
            "create_credential_vault_denial_secret_handling_proof_schema",
            "create_credential_vault_denial_secret_handling_proof_approval_gate",
            "create_credential_access_denial_contract",
            "create_secret_read_denial_contract",
            "create_environment_variable_denial_contract",
            "create_credential_vault_boundary_record",
            "create_secret_handling_boundary_record",
            "create_environment_read_boundary_record",
            "create_credential_secret_audit_proof",
            "create_credential_secret_denial_ledger",
            "create_credential_secret_readiness_summary",
            "create_network_socket_lockdown_proof_bridge",
            "create_credential_vault_denial_secret_handling_proof_bundle",
        ],
        ["eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver", "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway", "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref", "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"],
        errors,
    )
    check_strings(
        ADAPTERS,
        [
            "ADAPTER_MODULE_VERSION = \"3.7.0\"",
            "supports_supervised_production_pilot_readiness_review",
            "supervised_production_pilot_readiness_review_requires_specific_token",
            "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF",
        ],
        [],
        errors,
    )
    check_strings(
        RELEASE_LOCK,
        [
            'STABLE_RUNTIME_VERSION = "3.7.0"',
            '"current_phase": "Credential Vault Denial and Secret Handling Proof"',
            '"next_phase": "Network/Socket Lockdown Proof"',
            "v3.8 network/socket lockdown proof",
            "v3.9 live external action final preflight gate",
            "v4.0 first tiny real-world supervised execution candidate",
        ],
        [],
        errors,
    )
    check_docs(errors)

    check_demo(errors)
    check_fixture_tests(errors)
    check_schema(errors)
    check_no_token_and_token_paths(errors)
    check_write_proof(errors)
    check_write_artifacts(errors)
    check_smoke(errors)

    if errors:
        print("FAIL")
        for message in errors:
            print(message)
        sys.exit(1)

    print("PASS: Station Chief Runtime v3.7 valid")


if __name__ == "__main__":
    main()
