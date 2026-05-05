#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
REVIEW_MODULE = REPO_ROOT / "10_runtime" / "station_chief_supervised_production_pilot_readiness_review.py"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON_REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT_V36 = REPO_ROOT / "09_exports" / "station_chief_runtime_v3_6_report.md"
REQUIRED_FILES = [
    RUNTIME,
    REVIEW_MODULE,
    ADAPTERS,
    RELEASE_LOCK,
    README,
    SKELETON_REPORT,
    REPORT_V36,
]


def errors_list(message: str, errors: list[str]) -> None:
    print(message)
    for error in errors:
        print(error)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_json_command(args: list[str]) -> dict:
    proc = run_command(args)
    if proc.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(args)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid json from {' '.join(args)}: {exc}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}") from exc


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.6 runtime files.")

    for path in REQUIRED_FILES:
        assert_true(path.exists(), f"missing required file: {path.relative_to(REPO_ROOT)}", errors)

    runtime_text = RUNTIME.read_text(encoding="utf-8")
    module_text = REVIEW_MODULE.read_text(encoding="utf-8")
    adapters_text = ADAPTERS.read_text(encoding="utf-8")
    release_text = RELEASE_LOCK.read_text(encoding="utf-8")
    readme_text = README.read_text(encoding="utf-8")
    skeleton_text = SKELETON_REPORT.read_text(encoding="utf-8")
    report_text = REPORT_V36.read_text(encoding="utf-8")

    runtime_required = [
        'STATION_CHIEF_RUNTIME_VERSION = "3.6.0"',
        'attach_supervised_production_pilot_readiness_review',
        'write_supervised_production_pilot_readiness_review',
        '--supervised-production-pilot-readiness-review-schema',
        '--supervised-production-pilot-readiness-review',
        '--write-supervised-production-pilot-readiness-review',
        '--production-readiness-label',
        '--production-readiness-confirm-token',
        '--candidate-label',
        '--required-production-pilot-reviewer',
        '--blast-radius-label',
        'supervised_production_pilot_readiness_review_bundle',
        'supervised_production_pilot_readiness_review_schema',
        'supervised_production_pilot_readiness_review_approval_gate',
        'minimum_viable_production_candidate_contract',
        'human_production_pilot_review_gate',
        'production_blast_radius_analysis',
        'live_action_denial_review',
        'rollback_availability_review',
        'credential_secret_readiness_denial_proof',
        'network_socket_readiness_denial_proof',
        'production_pilot_audit_proof',
        'production_pilot_readiness_ledger',
        'production_pilot_readiness_summary',
        'credential_vault_denial_secret_handling_proof_bridge',
    ]
    for token in runtime_required:
        assert_true(token in runtime_text, f'runtime missing token: {token}', errors)

    module_required = [
        'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_MODULE_VERSION = "3.6.0"',
        'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_STATUS',
        'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PHASE',
        'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN',
        'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW',
        'canonical_json',
        'sha256_digest',
        'normalize_production_readiness_label',
        'generate_supervised_production_pilot_readiness_review_id',
        'create_supervised_production_pilot_readiness_review_schema',
        'create_supervised_production_pilot_readiness_review_approval_gate',
        'create_minimum_viable_production_candidate_contract',
        'create_human_production_pilot_review_gate',
        'create_production_blast_radius_analysis',
        'create_live_action_denial_review',
        'create_rollback_availability_review',
        'create_credential_secret_readiness_denial_proof',
        'create_network_socket_readiness_denial_proof',
        'create_production_pilot_audit_proof',
        'create_production_pilot_readiness_ledger',
        'create_production_pilot_readiness_summary',
        'create_credential_vault_denial_secret_handling_proof_bridge',
        'create_supervised_production_pilot_readiness_review_bundle',
    ]
    for token in module_required:
        assert_true(token in module_text, f'module missing token: {token}', errors)

    adapter_required = [
        'ADAPTER_MODULE_VERSION = "3.6.0"',
        'supports_supervised_production_pilot_readiness_review',
        'supervised_production_pilot_readiness_review_requires_specific_token',
        'production_execution_allowed',
        'production_activation_allowed',
        'deployment_allowed',
        'deployment_rollback_allowed',
        'live_api_call_allowed',
        'network_access_allowed',
        'socket_access_allowed',
        'credential_use_allowed',
        'secret_read_allowed',
        'environment_read_allowed',
        'real_external_tool_invocation_allowed',
        'real_task_execution_allowed',
        'live_task_assignment_allowed',
        'live_worker_routing_allowed',
        'live_orchestration_allowed',
        'worker_process_start_allowed',
        'full_workforce_activation_allowed',
        'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW',
    ]
    for token in adapter_required:
        assert_true(token in adapters_text, f'adapters missing token: {token}', errors)

    assert_true('STABLE_RUNTIME_VERSION = "3.6.0"' in release_text, 'release lock missing stable runtime version 3.6.0', errors)
    assert_true('current_phase": "Supervised Production Pilot Readiness Review"' in release_text, 'release lock missing v3.6 current phase', errors)
    assert_true('next_phase": "Credential Vault Denial and Secret Handling Proof"' in release_text, 'release lock missing v3.7 next phase', errors)
    for token in ['v3.7 credential vault denial and secret handling proof', 'v3.8 network/socket lockdown proof', 'v3.9 live external action final preflight gate', 'v4.0 first tiny real-world supervised execution candidate']:
        assert_true(token in release_text, f'release lock missing recommended build token: {token}', errors)

    readme_required = [
        'Station Chief Runtime upgraded to v3.6.0. Locked 175-family baseline preserved. Supervised production pilot readiness review added.',
        'supervised production pilot readiness review schema',
        'minimum viable production candidate contract',
        'human production pilot review gate',
        'production blast-radius analysis',
        'live action denial review',
        'rollback availability review',
        'credential/secret readiness denial proof',
        'network/socket readiness denial proof',
        'production pilot audit proof',
        'production pilot readiness ledger',
        'production pilot readiness summary',
        'credential vault denial and secret handling proof bridge',
        'Next recommended step: build credential vault denial and secret handling proof.',
    ]
    for token in readme_required:
        assert_true(token in readme_text, f'readme missing token: {token}', errors)
    assert_true('Explain that' not in readme_text, 'readme still contains scaffold wording: Explain that', errors)
    assert_true('Include:' not in readme_text, 'readme still contains scaffold wording: Include:', errors)
    assert_true('List:' not in readme_text, 'readme still contains scaffold wording: List:', errors)
    assert_true('Write:' not in readme_text, 'readme still contains scaffold wording: Write:', errors)

    skeleton_required = [
        'Station Chief Runtime upgraded to v3.6.0. Locked 175-family baseline preserved. Supervised production pilot readiness review added.',
        'supervised production pilot readiness review schema',
        'minimum viable production candidate contract',
        'human production pilot review gate',
        'production blast-radius analysis',
        'live action denial review',
        'rollback availability review',
        'credential/secret readiness denial proof',
        'network/socket readiness denial proof',
        'production pilot audit proof',
        'production pilot readiness ledger',
        'production pilot readiness summary',
        'credential vault denial and secret handling proof bridge',
        'python3 scripts/validate_station_chief_runtime_v3_6.py',
    ]
    for token in skeleton_required:
        assert_true(token in skeleton_text, f'skeleton report missing token: {token}', errors)
    assert_true('Explain that' not in skeleton_text, 'skeleton report still contains scaffold wording: Explain that', errors)
    assert_true('Include:' not in skeleton_text, 'skeleton report still contains scaffold wording: Include:', errors)
    assert_true('List:' not in skeleton_text, 'skeleton report still contains scaffold wording: List:', errors)
    assert_true('Write:' not in skeleton_text, 'skeleton report still contains scaffold wording: Write:', errors)

    report_required = [
        'Station Chief Runtime v3.6.0 Report',
        'Station Chief Runtime upgraded to v3.6.0. Locked 175-family baseline preserved. Supervised production pilot readiness review added.',
        'Project owner, system architect, and operating-doctrine author: Devin O’Rourke.',
        'supervised production pilot readiness review schema',
        'minimum viable production candidate contract',
        'human production pilot review gate',
        'production blast-radius analysis',
        'live action denial review',
        'rollback availability review',
        'credential/secret readiness denial proof',
        'network/socket readiness denial proof',
        'production pilot audit proof',
        'production pilot readiness ledger',
        'production pilot readiness summary',
        'credential vault denial and secret handling proof bridge',
        'no production execution',
    ]
    for token in report_required:
        assert_true(token in report_text, f'v3.6 report missing token: {token}', errors)

    demo = run_json_command([sys.executable, str(RUNTIME), '--demo'])
    assert_true(demo.get('station_chief_runtime_version') == '3.6.0', 'demo runtime version is not 3.6.0', errors)
    assert_true(demo.get('runtime_status') == 'supervised_production_pilot_readiness_review', 'demo runtime status incorrect', errors)
    assert_true(demo.get('release_status') == 'STABLE_LOCKED', 'demo release status incorrect', errors)
    evidence = demo.get('evidence', {})
    expected_true = [
        'baseline_preserved',
        'supervised_production_pilot_readiness_review_available',
        'supervised_production_pilot_readiness_review_preview_only',
        'supervised_production_pilot_readiness_review_requires_token',
        'minimum_viable_production_candidate_preview_only',
        'production_blast_radius_analysis_preview_only',
        'live_action_denied_by_default',
        'rollback_availability_review_only',
        'credential_secret_readiness_denied',
        'network_socket_readiness_denied',
        'supervised_production_pilot_readiness_review_does_not_execute_production',
        'supervised_production_pilot_readiness_review_does_not_activate_production',
        'supervised_production_pilot_readiness_review_does_not_deploy',
        'supervised_production_pilot_readiness_review_does_not_call_live_apis',
        'supervised_production_pilot_readiness_review_does_not_use_network_access',
        'supervised_production_pilot_readiness_review_does_not_open_sockets',
        'supervised_production_pilot_readiness_review_does_not_use_credentials',
        'supervised_production_pilot_readiness_review_does_not_read_secrets',
        'supervised_production_pilot_readiness_review_does_not_read_environment',
        'supervised_production_pilot_readiness_review_does_not_assign_live_tasks',
        'supervised_production_pilot_readiness_review_does_not_route_live_workers',
        'supervised_production_pilot_readiness_review_does_not_perform_live_orchestration',
        'supervised_production_pilot_readiness_review_does_not_modify_repo_files',
        'credential_vault_denial_secret_handling_proof_not_yet_active',
    ]
    for key in expected_true:
        assert_true(evidence.get(key) is True or demo.get(key) is True, f'demo evidence missing true {key}', errors)
    assert_true(evidence.get('external_actions_taken') is False, 'demo external_actions_taken not false', errors)

    fixture = run_json_command([sys.executable, str(RUNTIME), '--fixture-test'])
    assert_true(fixture.get('fixture_test_status') == 'PASS', 'fixture tests did not pass', errors)
    assert_true(fixture.get('runtime_version') == '3.6.0', 'fixture runtime version incorrect', errors)
    assert_true(fixture.get('case_count') == 5, 'fixture test case_count incorrect', errors)
    assert_true(fixture.get('failed') == 0, 'fixture tests failed count not zero', errors)

    schema = run_json_command([sys.executable, str(RUNTIME), '--supervised-production-pilot-readiness-review-schema'])
    assert_true(schema.get('supervised_production_pilot_readiness_review_schema_version') == '3.6.0', 'schema version incorrect', errors)
    assert_true(schema.get('schema_status') == 'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PREVIEW_ONLY', 'schema status incorrect', errors)
    required_sections = set(schema.get('required_sections', []))
    for token in [
        'supervised_production_pilot_readiness_review_approval_gate',
        'minimum_viable_production_candidate_contract',
        'human_production_pilot_review_gate',
        'production_blast_radius_analysis',
        'live_action_denial_review',
        'rollback_availability_review',
        'credential_secret_readiness_denial_proof',
        'network_socket_readiness_denial_proof',
        'production_pilot_audit_proof',
        'production_pilot_readiness_ledger',
        'production_pilot_readiness_summary',
        'credential_vault_denial_secret_handling_proof_bridge',
    ]:
        assert_true(token in required_sections, f'schema missing required section: {token}', errors)
    blocked_modes = set(schema.get('blocked_production_readiness_modes', []))
    for token in ['production_execution', 'production_activation', 'live_deployment', 'live_api_call', 'network_access', 'socket_connection', 'credential_use', 'secret_read', 'environment_variable_read', 'full_workforce_activation']:
        assert_true(token in blocked_modes, f'schema missing blocked mode: {token}', errors)
    assert_true('YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW' in set(schema.get('required_confirmation_tokens', [])), 'schema missing token requirement', errors)
    for key, value in schema.items():
        if isinstance(value, bool):
            assert_true(value is False or key in {'baseline_preserved', 'external_actions_taken', 'production_execution_performed', 'production_activation_performed', 'deployment_performed', 'deployment_rollback_performed', 'real_rollback_performed', 'real_recovery_performed', 'processes_terminated', 'workers_terminated', 'production_state_changed', 'live_api_call_performed', 'network_access_performed', 'socket_opened', 'credentials_used', 'secrets_read', 'environment_read', 'real_external_tool_invocation_performed', 'real_task_execution_performed', 'live_task_assignment_performed', 'live_worker_routing_performed', 'live_orchestration_performed', 'worker_processes_started', 'repo_files_modified', 'execution_authorized'}, f'schema safety boolean unexpectedly true: {key}', errors)

    no_token = run_json_command([sys.executable, str(RUNTIME), '--command', 'check please', '--supervised-production-pilot-readiness-review', '--json'])
    assert_true('supervised_production_pilot_readiness_review_bundle' in no_token, 'no-token result missing bundle', errors)
    gate = no_token.get('supervised_production_pilot_readiness_review_approval_gate', {})
    assert_true(gate.get('gate_status') == 'BLOCKED_PENDING_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL', 'no-token gate status incorrect', errors)
    assert_true(gate.get('confirmation_token_valid') is False, 'no-token validity incorrect', errors)
    assert_true(gate.get('local_production_readiness_records_authorized') is False, 'no-token authorization incorrect', errors)
    assert_true(no_token.get('minimum_viable_production_candidate_contract', {}).get('contract_status') == 'BLOCKED', 'no-token candidate status incorrect', errors)
    assert_true(no_token.get('human_production_pilot_review_gate', {}).get('review_gate_status') == 'BLOCKED', 'no-token human review gate status incorrect', errors)
    assert_true(no_token.get('production_blast_radius_analysis', {}).get('analysis_status') == 'BLOCKED', 'no-token blast radius status incorrect', errors)
    assert_true(no_token.get('live_action_denial_review', {}).get('review_status') == 'BLOCKED', 'no-token live action denial status incorrect', errors)
    assert_true(no_token.get('rollback_availability_review', {}).get('review_status') == 'BLOCKED', 'no-token rollback review status incorrect', errors)
    assert_true(no_token.get('credential_secret_readiness_denial_proof', {}).get('proof_status') == 'BLOCKED', 'no-token credential proof status incorrect', errors)
    assert_true(no_token.get('network_socket_readiness_denial_proof', {}).get('proof_status') == 'BLOCKED', 'no-token network proof status incorrect', errors)
    assert_true(no_token.get('production_pilot_audit_proof', {}).get('audit_status') == 'BLOCKED', 'no-token audit status incorrect', errors)
    assert_true(no_token.get('production_pilot_readiness_ledger', {}).get('ledger_status') == 'BLOCKED', 'no-token ledger status incorrect', errors)
    assert_true(no_token.get('production_pilot_readiness_summary', {}).get('readiness_status') == 'BLOCKED', 'no-token readiness status incorrect', errors)
    assert_true(no_token.get('credential_vault_denial_secret_handling_proof_bridge', {}).get('ready_for_credential_vault_denial_secret_handling_proof') is False, 'no-token bridge readiness incorrect', errors)

    token = run_json_command([sys.executable, str(RUNTIME), '--command', 'check please', '--supervised-production-pilot-readiness-review', '--production-readiness-confirm-token', 'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW', '--json'])
    gate = token.get('supervised_production_pilot_readiness_review_approval_gate', {})
    assert_true(gate.get('gate_status') == 'APPROVED_FOR_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_RECORDS', 'token gate status incorrect', errors)
    assert_true(gate.get('confirmation_token_valid') is True, 'token validity incorrect', errors)
    assert_true(gate.get('local_production_readiness_records_authorized') is True, 'token local authorization incorrect', errors)
    assert_true(token.get('minimum_viable_production_candidate_contract', {}).get('contract_status') == 'MINIMUM_VIABLE_PRODUCTION_CANDIDATE_CONTRACT_CREATED', 'token candidate status incorrect', errors)
    assert_true(token.get('human_production_pilot_review_gate', {}).get('review_gate_status') == 'HUMAN_PRODUCTION_PILOT_REVIEW_REQUIREMENT_CREATED', 'token human review gate incorrect', errors)
    assert_true(token.get('production_blast_radius_analysis', {}).get('analysis_status') == 'PRODUCTION_BLAST_RADIUS_ANALYSIS_CREATED', 'token blast radius status incorrect', errors)
    assert_true(token.get('live_action_denial_review', {}).get('review_status') == 'LIVE_ACTION_DENIAL_REVIEW_CREATED', 'token live action review incorrect', errors)
    assert_true(token.get('rollback_availability_review', {}).get('review_status') == 'ROLLBACK_AVAILABILITY_REVIEW_CREATED', 'token rollback review incorrect', errors)
    assert_true(token.get('credential_secret_readiness_denial_proof', {}).get('proof_status') == 'CREDENTIAL_SECRET_READINESS_DENIAL_PROOF_CREATED', 'token credential proof incorrect', errors)
    assert_true(token.get('network_socket_readiness_denial_proof', {}).get('proof_status') == 'NETWORK_SOCKET_READINESS_DENIAL_PROOF_CREATED', 'token network proof incorrect', errors)
    assert_true(token.get('production_pilot_audit_proof', {}).get('audit_status') == 'PASS', 'token audit status incorrect', errors)
    assert_true(token.get('production_pilot_readiness_ledger', {}).get('ledger_status') == 'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_LEDGER', 'token ledger status incorrect', errors)
    assert_true(token.get('production_pilot_readiness_summary', {}).get('readiness_status') == 'READY_FOR_NEXT_LAYER', 'token readiness status incorrect', errors)
    assert_true(token.get('credential_vault_denial_secret_handling_proof_bridge', {}).get('next_layer') == 'Credential Vault Denial and Secret Handling Proof', 'token bridge next layer incorrect', errors)

    next_layer = run_json_command([sys.executable, str(RUNTIME), '--command', 'build credential vault denial and secret handling proof', '--supervised-production-pilot-readiness-review', '--production-readiness-confirm-token', 'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW', '--json'])
    assert_true(next_layer.get('credential_vault_denial_secret_handling_proof_bridge', {}).get('next_layer') == 'Credential Vault Denial and Secret Handling Proof', 'next layer bridge next layer incorrect', errors)
    assert_true(next_layer.get('credential_vault_denial_secret_handling_proof_bridge', {}).get('ready_for_credential_vault_denial_secret_handling_proof') is True, 'next layer bridge readiness incorrect', errors)
    assert_true(next_layer.get('production_pilot_readiness_summary', {}).get('readiness_status') == 'READY_FOR_NEXT_LAYER', 'next layer readiness incorrect', errors)

    with tempfile.TemporaryDirectory() as tmpdir:
        out = run_json_command([sys.executable, str(RUNTIME), '--command', 'check please', '--write-supervised-production-pilot-readiness-review', tmpdir, '--production-readiness-confirm-token', 'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW'])
        summary = out.get('supervised_production_pilot_readiness_review_write_summary', {})
        assert_true(summary, 'write-supervised summary missing', errors)
        review_dir = Path(summary.get('supervised_production_pilot_readiness_review_dir', ''))
        assert_true(review_dir.exists(), 'write-supervised review dir missing', errors)
        expected_files = [
            'supervised_production_pilot_readiness_review_bundle.json',
            'supervised_production_pilot_readiness_review_schema.json',
            'supervised_production_pilot_readiness_review_approval_gate.json',
            'minimum_viable_production_candidate_contract.json',
            'human_production_pilot_review_gate.json',
            'production_blast_radius_analysis.json',
            'live_action_denial_review.json',
            'rollback_availability_review.json',
            'credential_secret_readiness_denial_proof.json',
            'network_socket_readiness_denial_proof.json',
            'production_pilot_audit_proof.json',
            'production_pilot_readiness_ledger.json',
            'production_pilot_readiness_summary.json',
            'credential_vault_denial_secret_handling_proof_bridge.json',
            'supervised_production_pilot_readiness_review_manifest.json',
        ]
        for filename in expected_files:
            assert_true((review_dir / filename).exists(), f'write-supervised missing file: {filename}', errors)
        manifest = json.loads((review_dir / 'supervised_production_pilot_readiness_review_manifest.json').read_text())
        assert_true(manifest.get('runtime_version') == '3.6.0', 'write-supervised manifest runtime version incorrect', errors)
        assert_true(manifest.get('status') == 'SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PREVIEW_ONLY', 'write-supervised manifest status incorrect', errors)
        assert_true(manifest.get('baseline_preserved') is True, 'write-supervised manifest baseline incorrect', errors)
        assert_true(manifest.get('external_actions_taken') is False, 'write-supervised manifest external actions incorrect', errors)

    with tempfile.TemporaryDirectory() as run_dir, tempfile.TemporaryDirectory() as reg_dir:
        out = run_json_command([sys.executable, str(RUNTIME), '--command', 'check please', '--write-artifacts', run_dir, '--registry-dir', reg_dir, '--supervised-production-pilot-readiness-review', '--production-readiness-confirm-token', 'YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW'])
        summary = out.get('artifact_write_summary', {})
        assert_true(summary, 'artifact write summary missing', errors)
        run_id = summary.get('run_id', '')
        assert_true(run_id.startswith('station-chief-v3-6-check-please-'), 'artifact write run_id prefix incorrect', errors)
        artifact_dir = Path(summary.get('artifact_dir', ''))
        assert_true(artifact_dir.exists(), 'artifact directory missing', errors)
        manifest = json.loads((artifact_dir / 'manifest.json').read_text())
        assert_true(manifest.get('artifact_type') == 'station_chief_runtime_v3_6_artifacts', 'artifact manifest type incorrect', errors)
        assert_true(manifest.get('runtime_version') == '3.6.0', 'artifact manifest runtime version incorrect', errors)
        registry = json.loads((Path(reg_dir) / 'run_registry.json').read_text())
        index = json.loads((Path(reg_dir) / 'runtime_index.json').read_text())
        assert_true(registry.get('registry_version') == '3.6.0', 'registry version incorrect', errors)
        assert_true(index.get('index_version') == '3.6.0', 'runtime index version incorrect', errors)
        assert_true(summary.get('registry_updated') is True, 'registry was not updated', errors)

    smoke_commands = [
        ['--stable-release-manifest'],
        ['--release-lock'],
        ['--controlled-execution'],
        ['--work-order-executor'],
        ['--worker-hiring-registry'],
        ['--department-routing'],
        ['--multi-agent-orchestration'],
        ['--operator-console'],
        ['--github-patch-hardening'],
        ['--deployment-packaging'],
        ['--controlled-worker-execution'],
        ['--tool-permission-binding'],
        ['--live-telemetry-abort'],
        ['--post-run-audit-expansion'],
        ['--multi-worker-sandbox-coordination'],
        ['--controlled-external-tool-preview'],
        ['--permissioned-external-api-dry-run'],
        ['--controlled-multi-worker-audit-replay-preview'],
        ['--operator-approval-queue-enforcement'],
        ['--release-candidate-hardening'],
        ['--controlled-production-readiness-gate'],
        ['--controlled-worker-hiring-activation-pilot'],
        ['--first-supervised-production-dry-run'],
        ['--limited-external-tool-supervised-pilot'],
        ['--supervised-external-api-pilot'],
        ['--monitored-rollback-recovery-drill'],
        ['--supervised-production-pilot-readiness-review'],
        ['--approval-handoff'],
    ]
    for extra in smoke_commands:
        proc = run_command([sys.executable, str(RUNTIME), '--command', 'check please', '--json', *extra])
        assert_true(proc.returncode == 0, f'smoke command failed: {" ".join(extra)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}', errors)
        parsed = json.loads(proc.stdout)
        stable_manifest = parsed.get('stable_release_manifest', {}) if isinstance(parsed.get('stable_release_manifest'), dict) else {}
        assert_true(
            parsed.get('baseline_preserved') is True
            or stable_manifest.get('baseline_preserved') is True
            or parsed.get('evidence', {}).get('baseline_preserved') is True,
            f'smoke command missing baseline preservation: {" ".join(extra)}',
            errors,
        )
        if 'evidence' in parsed:
            assert_true(parsed['evidence'].get('external_actions_taken') is False, f'smoke command external_actions_taken not false: {" ".join(extra)}', errors)

    list_overlays_proc = run_command([sys.executable, str(RUNTIME), '--list-overlays'])
    assert_true(list_overlays_proc.returncode == 0, f'list-overlays command failed\\nstdout:\\n{list_overlays_proc.stdout}\\nstderr:\\n{list_overlays_proc.stderr}', errors)
    try:
        list_overlays = json.loads(list_overlays_proc.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f'list-overlays output was not valid json: {exc}')
        list_overlays = []
    assert_true(isinstance(list_overlays, list), 'list-overlays output is not a list', errors)
    assert_true(len(list_overlays) > 0, 'list-overlays output is empty', errors)
    assert_true(any(item.get('id') == 'family_007_devinized_engineering_overload' for item in list_overlays if isinstance(item, dict)), 'list-overlays missing expected overlay id', errors)
    list_adapters = run_json_command([sys.executable, str(RUNTIME), '--list-adapters'])
    assert_true(list_adapters.get('adapter_module_version') == '3.6.0', 'list-adapters module version incorrect', errors)
    simulate = run_json_command([sys.executable, str(RUNTIME), '--command', 'check please', '--simulate-adapter'])
    assert_true(simulate.get('adapter_result', {}).get('external_actions_taken') is False, 'simulate adapter external actions not false', errors)
    assert_true(simulate.get('adapter_result', {}).get('live_api_call_performed') is False, 'simulate adapter live api not false', errors)

    if errors:
        errors_list('FAIL', errors)
        raise SystemExit(1)

    print('PASS: Station Chief Runtime v3.6 valid')


if __name__ == '__main__':
    main()
