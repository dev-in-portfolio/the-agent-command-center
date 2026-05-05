#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
MODULE = REPO_ROOT / "10_runtime" / "station_chief_network_socket_lockdown_proof.py"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v3_8_report.md"

REQUIRED_FILES = [
    RUNTIME,
    MODULE,
    ADAPTERS,
    RELEASE_LOCK,
    README,
    SKELETON,
    REPORT,
    REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_8.py",
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
    require(demo.get("station_chief_runtime_version") == "3.8.0", "demo runtime version is not 3.8.0", errors)
    require(demo.get("runtime_status") == "network_socket_lockdown_proof", "demo runtime status incorrect", errors)
    require(demo.get("release_status") == "STABLE_LOCKED", "demo release status incorrect", errors)
    evidence = demo.get("evidence", {})
    for key in [
        "baseline_preserved",
        "network_socket_lockdown_proof_available",
        "network_socket_lockdown_proof_preview_only",
        "network_socket_lockdown_proof_requires_token",
        "network_socket_lockdown_proof_does_not_perform_network_access",
        "network_socket_lockdown_proof_does_not_open_sockets",
        "network_socket_lockdown_proof_does_not_resolve_dns",
        "network_socket_lockdown_proof_does_not_make_outbound_connections",
        "network_socket_lockdown_proof_does_not_make_inbound_connections",
        "network_socket_lockdown_proof_does_not_call_live_apis",
        "network_socket_lockdown_proof_does_not_call_webhooks",
        "network_socket_lockdown_proof_does_not_invoke_external_tools",
    ]:
        require(evidence.get(key) is True or demo.get(key) is True, f"demo missing true evidence: {key}", errors)
    require(evidence.get("external_actions_taken") is False, "demo external_actions_taken not false", errors)


def check_fixture_tests(errors: list[str]) -> None:
    fixture = run_json([sys.executable, str(RUNTIME), "--fixture-test"])
    require(fixture.get("fixture_test_status") == "PASS", "fixture tests failed", errors)
    require(fixture.get("runtime_version") == "3.8.0", "fixture runtime version incorrect", errors)
    require(fixture.get("case_count") == 5, "fixture case count incorrect", errors)
    require(fixture.get("failed") == 0, "fixture failed count not zero", errors)


def check_schema(errors: list[str]) -> None:
    schema = run_json([sys.executable, str(RUNTIME), "--network-socket-lockdown-proof-schema"])
    require(schema.get("network_socket_lockdown_proof_schema_version") == "3.8.0", "schema version incorrect", errors)
    require(schema.get("schema_status") == "NETWORK_SOCKET_LOCKDOWN_PROOF_PREVIEW_ONLY", "schema status incorrect", errors)
    for section in [
        "network_socket_lockdown_proof_approval_gate",
        "network_access_denial_contract",
        "socket_access_denial_contract",
        "live_api_call_denial_contract",
        "dns_resolution_denial_contract",
        "outbound_connection_denial_contract",
        "network_boundary_record",
        "socket_boundary_record",
        "network_socket_audit_proof",
        "network_socket_lockdown_ledger",
        "network_socket_readiness_summary",
        "live_external_action_final_preflight_gate_bridge",
    ]:
        require(section in set(schema.get("required_sections", [])), f"schema missing required section: {section}", errors)
    for mode in [
        "network_access",
        "socket_connection",
        "dns_resolution",
        "outbound_connection",
        "inbound_connection",
        "live_api_call",
        "webhook_call",
        "external_tool_invocation",
        "credential_use",
        "secret_read",
        "environment_variable_read",
        "deployment",
        "production_execution",
        "production_activation",
        "live_task_assignment",
        "live_worker_routing",
        "live_orchestration",
        "worker_process_start",
        "full_workforce_activation",
    ]:
        require(mode in set(schema.get("blocked_proof_modes", [])), f"schema missing blocked mode: {mode}", errors)
    require("YES_I_APPROVE_NETWORK_SOCKET_LOCKDOWN_PROOF" in set(schema.get("required_confirmation_tokens", [])), "schema missing token requirement", errors)


def check_no_token_and_token_paths(errors: list[str]) -> None:
    base = [sys.executable, str(RUNTIME), "--command", "check please", "--network-socket-lockdown-proof", "--json"]
    no_token = run_json(base)
    require("network_socket_lockdown_proof_bundle" in no_token, "no-token result missing proof bundle", errors)
    gate = no_token.get("network_socket_lockdown_proof_approval_gate", {})
    require(gate.get("gate_status") == "BLOCKED_PENDING_NETWORK_SOCKET_LOCKDOWN_PROOF_APPROVAL", "no-token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is False, "no-token validity incorrect", errors)
    require(gate.get("local_network_socket_proof_records_authorized") is False, "no-token local authorization incorrect", errors)
    require(no_token.get("network_access_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token network access contract incorrect", errors)
    require(no_token.get("socket_access_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token socket read contract incorrect", errors)
    require(no_token.get("live_api_call_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token live API call contract incorrect", errors)
    require(no_token.get("dns_resolution_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token DNS resolution contract incorrect", errors)
    require(no_token.get("outbound_connection_denial_contract", {}).get("contract_status") == "BLOCKED", "no-token outbound connection contract incorrect", errors)
    require(no_token.get("network_socket_audit_proof", {}).get("audit_status") == "BLOCKED", "no-token audit status incorrect", errors)
    require(no_token.get("network_socket_lockdown_ledger", {}).get("ledger_status") == "BLOCKED", "no-token ledger status incorrect", errors)
    require(no_token.get("network_socket_readiness_summary", {}).get("readiness_status") == "BLOCKED", "no-token readiness status incorrect", errors)
    require(no_token.get("live_external_action_final_preflight_gate_bridge", {}).get("ready_for_live_external_action_final_preflight_gate") is False, "no-token bridge readiness incorrect", errors)
    require(no_token.get("network_socket_audit_proof", {}).get("baseline_preserved") is True, "no-token baseline not preserved", errors)

    token = run_json([sys.executable, str(RUNTIME), "--command", "check please", "--network-socket-lockdown-proof", "--network-socket-confirm-token", "YES_I_APPROVE_NETWORK_SOCKET_LOCKDOWN_PROOF", "--json"])
    gate = token.get("network_socket_lockdown_proof_approval_gate", {})
    require(gate.get("gate_status") == "APPROVED_FOR_NETWORK_SOCKET_LOCKDOWN_PROOF_RECORDS", "token gate status incorrect", errors)
    require(gate.get("confirmation_token_valid") is True, "token validity incorrect", errors)
    require(gate.get("local_network_socket_proof_records_authorized") is True, "token local authorization incorrect", errors)
    require(token.get("network_access_denial_contract", {}).get("contract_status") == "NETWORK_ACCESS_DENIAL_CONTRACT_CREATED", "token network access contract incorrect", errors)
    require(token.get("socket_access_denial_contract", {}).get("contract_status") == "SOCKET_ACCESS_DENIAL_CONTRACT_CREATED", "token socket read contract incorrect", errors)
    require(token.get("live_api_call_denial_contract", {}).get("contract_status") == "LIVE_API_CALL_DENIAL_CONTRACT_CREATED", "token live API call contract incorrect", errors)
    require(token.get("dns_resolution_denial_contract", {}).get("contract_status") == "DNS_RESOLUTION_DENIAL_CONTRACT_CREATED", "token DNS resolution contract incorrect", errors)
    require(token.get("outbound_connection_denial_contract", {}).get("contract_status") == "OUTBOUND_CONNECTION_DENIAL_CONTRACT_CREATED", "token outbound connection contract incorrect", errors)
    require(token.get("network_socket_audit_proof", {}).get("audit_status") == "PASS", "token audit status incorrect", errors)
    require(token.get("network_socket_lockdown_ledger", {}).get("ledger_status") == "NETWORK_SOCKET_LOCKDOWN_PROOF_LEDGER", "token ledger status incorrect", errors)
    require(token.get("network_socket_readiness_summary", {}).get("readiness_status") == "READY_FOR_NEXT_LAYER", "token readiness status incorrect", errors)
    require(token.get("live_external_action_final_preflight_gate_bridge", {}).get("ready_for_live_external_action_final_preflight_gate") is True, "token bridge readiness incorrect", errors)
    for key in [
        "network_access_authorized",
        "socket_access_authorized",
        "dns_resolution_authorized",
        "outbound_connection_authorized",
        "inbound_connection_authorized",
        "live_api_call_authorized",
        "webhook_call_authorized",
        "external_tool_invocation_authorized",
        "credential_use_authorized",
        "secret_read_authorized",
        "environment_read_authorized",
        "deployment_authorized",
        "production_execution_authorized",
        "production_activation_authorized",
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
            "--write-network-socket-lockdown-proof",
            tmpdir,
            "--network-socket-confirm-token",
            "YES_I_APPROVE_NETWORK_SOCKET_LOCKDOWN_PROOF",
        ])
        summary = out.get("network_socket_lockdown_proof_write_summary", {})
        require(bool(summary), "write proof summary missing", errors)
        proof_dir = Path(summary.get("network_socket_lockdown_proof_dir", ""))
        require(proof_dir.exists(), "write proof directory missing", errors)
        expected = [
            "network_socket_lockdown_proof_bundle.json",
            "network_socket_lockdown_proof_schema.json",
            "network_socket_lockdown_proof_approval_gate.json",
            "network_access_denial_contract.json",
            "socket_access_denial_contract.json",
            "live_api_call_denial_contract.json",
            "dns_resolution_denial_contract.json",
            "outbound_connection_denial_contract.json",
            "network_boundary_record.json",
            "socket_boundary_record.json",
            "network_socket_audit_proof.json",
            "network_socket_lockdown_ledger.json",
            "network_socket_readiness_summary.json",
            "live_external_action_final_preflight_gate_bridge.json",
            "network_socket_lockdown_proof_manifest.json",
        ]
        for filename in expected:
            require((proof_dir / filename).exists(), f"write proof missing file: {filename}", errors)
        manifest = json.loads((proof_dir / "network_socket_lockdown_proof_manifest.json").read_text())
        require(manifest.get("runtime_version") == "3.8.0", "write proof manifest runtime version incorrect", errors)
        require(manifest.get("status") == "NETWORK_SOCKET_LOCKDOWN_PROOF_PREVIEW_ONLY", "write proof manifest status incorrect", errors)
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
            "--network-socket-lockdown-proof",
            "--network-socket-confirm-token",
            "YES_I_APPROVE_NETWORK_SOCKET_LOCKDOWN_PROOF",
        ])
        summary = out.get("artifact_write_summary", {})
        require(bool(summary), "artifact write summary missing", errors)
        run_id = summary.get("run_id", "")
        require(run_id.startswith("station-chief-v3-8-check-please-"), "artifact write run id prefix incorrect", errors)
        artifact_dir = Path(summary.get("artifact_dir", ""))
        require(artifact_dir.exists(), "artifact directory missing", errors)
        manifest = json.loads((artifact_dir / "manifest.json").read_text())
        require(manifest.get("artifact_type") == "station_chief_runtime_v3_8_artifacts", "artifact manifest type incorrect", errors)
        require(manifest.get("runtime_version") == "3.8.0", "artifact manifest runtime version incorrect", errors)
        registry = json.loads((Path(reg_dir) / "run_registry.json").read_text())
        index = json.loads((Path(reg_dir) / "runtime_index.json").read_text())
        require(registry.get("registry_version") == "3.8.0", "registry version incorrect", errors)
        require(index.get("index_version") == "3.8.0", "runtime index version incorrect", errors)
        require(summary.get("registry_updated") is True, "registry not updated", errors)


def check_docs(errors: list[str]) -> None:
    readme = README.read_text(encoding="utf-8")
    skeleton = SKELETON.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    for text, label in [
        (readme, "README"),
        (skeleton, "skeleton report"),
        (report, "v3.8 report"),
    ]:
        require("Station Chief Runtime upgraded to v3.8.0." in text, f"{label} missing v3.8 status", errors)
        require("Network/socket lockdown proof added." in text or "network/socket lockdown proof" in text, f"{label} missing v3.8 capability phrase", errors)
        require("Next recommended step: build live external action final preflight gate." in text, f"{label} missing next-step text", errors)


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
        ["--network-socket-lockdown-proof"],
        ["--approval-handoff"],
    ]
    for extra in commands:
        proc = run_command([sys.executable, str(RUNTIME), "--command", "check please", "--json", *extra])
        require(proc.returncode == 0, f"smoke command failed: {' '.join(extra)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", errors)


def main() -> None:
    errors: list[str] = []
    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.8 runtime files.")

    for path in REQUIRED_FILES:
        require(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}", errors)

    check_strings(
        RUNTIME,
        [
            'STATION_CHIEF_RUNTIME_VERSION = "3.8.0"',
            "network_socket_lockdown_proof",
            "attach_network_socket_lockdown_proof",
            "write_network_socket_lockdown_proof",
            "--network-socket-lockdown-proof-schema",
            "--network-socket-lockdown-proof",
            "--write-network-socket-lockdown-proof",
            "--network-socket-label",
            "--network-socket-confirm-token",
            "--network-boundary-label",
            "--socket-boundary-label",
            "network_socket_lockdown_proof_bundle",
            "network_socket_lockdown_proof_schema",
            "network_socket_lockdown_proof_approval_gate",
            "network_access_denial_contract",
            "socket_access_denial_contract",
            "live_api_call_denial_contract",
            "dns_resolution_denial_contract",
            "outbound_connection_denial_contract",
            "network_boundary_record",
            "socket_boundary_record",
            "network_socket_audit_proof",
            "network_socket_lockdown_ledger",
            "network_socket_readiness_summary",
            "live_external_action_final_preflight_gate_bridge",
        ],
        ["import requests", "urllib.request", "os.system", "pip install", "npm install", "API key", "import subprocess"],
        errors,
    )
    check_strings(
        MODULE,
        [
            'NETWORK_SOCKET_LOCKDOWN_PROOF_MODULE_VERSION = "3.8.0"',
            "NETWORK_SOCKET_LOCKDOWN_PROOF_STATUS",
            "NETWORK_SOCKET_LOCKDOWN_PROOF_PHASE",
            "NETWORK_SOCKET_LOCKDOWN_PROOF_APPROVAL_TOKEN",
            "YES_I_APPROVE_NETWORK_SOCKET_LOCKDOWN_PROOF",
            "canonical_json",
            "sha256_digest",
            "normalize_network_socket_label",
            "generate_network_socket_lockdown_proof_id",
            "create_network_socket_lockdown_proof_schema",
            "create_network_socket_lockdown_proof_approval_gate",
            "create_network_access_denial_contract",
            "create_socket_access_denial_contract",
            "create_live_api_call_denial_contract",
            "create_dns_resolution_denial_contract",
            "create_outbound_connection_denial_contract",
            "create_network_boundary_record",
            "create_socket_boundary_record",
            "create_network_socket_audit_proof",
            "create_network_socket_lockdown_ledger",
            "create_network_socket_readiness_summary",
            "create_live_external_action_final_preflight_gate_bridge",
            "create_network_socket_lockdown_proof_bundle",
        ],
        ["eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver", "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway", "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref", "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"],
        errors,
    )
    check_strings(
        ADAPTERS,
        [
            "ADAPTER_MODULE_VERSION = \"3.8.0\"",
        ],
        [],
        errors,
    )
    check_strings(
        RELEASE_LOCK,
        [
            'STABLE_RUNTIME_VERSION = "3.8.0"',
            '"current_phase": "Network/Socket Lockdown Proof"',
            '"next_phase": "Live External Action Final Preflight Gate"',
            "v3.9 live external action final preflight gate",
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

    print("PASS: Station Chief Runtime v3.8 valid")


if __name__ == "__main__":
    main()
