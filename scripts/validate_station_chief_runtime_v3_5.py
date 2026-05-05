#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = ROOT / "10_runtime"
EXPORTS_DIR = ROOT / "09_exports"
SCRIPTS_DIR = ROOT / "scripts"


def require(errors, condition, message):
    if not condition:
        errors.append(message)


def require_equal(errors, actual, expected, message):
    if actual != expected:
        errors.append(f"{message}: expected {expected!r}, got {actual!r}")


def require_true(errors, value, message):
    if value is not True:
        errors.append(f"{message}: expected True, got {value!r}")


def require_false(errors, value, message):
    if value is not False:
        errors.append(f"{message}: expected False, got {value!r}")


def require_in(errors, item, collection, message):
    if item not in collection:
        errors.append(f"{message}: missing {item!r}")


def get_path(data, dotted_path, default=None):
    current = data
    for part in dotted_path.split('.'):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except Exception:
                return default
        else:
            return default
    return current


def parse_json_output(output, context, errors):
    start = -1
    for needle in ('{', '['):
        idx = output.find(needle)
        if idx != -1 and (start == -1 or idx < start):
            start = idx
    if start == -1:
        errors.append(f"{context}: no JSON found in output")
        return None
    try:
        return json.loads(output[start:])
    except Exception as exc:
        errors.append(f"{context}: failed to parse JSON: {exc}")
        return None


def run_command(cmd: list[str], context: str, errors: list[str]):
    try:
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    except Exception as exc:
        errors.append(f"{context}: command execution failed for {cmd!r}: {exc}")
        return -1, '', str(exc)
    if result.returncode != 0:
        errors.append(
            f"{context}: command failed rc={result.returncode} cmd={cmd!r} stderr={result.stderr.strip()!r}"
        )
    return result.returncode, result.stdout, result.stderr


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def check_exists(errors, path: Path):
    require(errors, path.exists(), f"Missing required file: {path.relative_to(ROOT)}")


def check_strings(errors, path: Path, required: list[str] | None = None, forbidden: list[str] | None = None):
    text = read_text(path)
    for item in required or []:
        require_in(errors, item, text, f"{path.relative_to(ROOT)} missing required text")
    for item in forbidden or []:
        require(errors, item not in text, f"{path.relative_to(ROOT)} contains forbidden text {item!r}")


def all_false(errors, data, fields, context):
    for field in fields:
        require_false(errors, get_path(data, field), f"{context}.{field}")


def all_true(errors, data, fields, context):
    for field in fields:
        require_true(errors, get_path(data, field), f"{context}.{field}")


def find_list(data, candidate_keys):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in candidate_keys:
            value = data.get(key)
            if isinstance(value, list):
                return value
    return None


def check_file_family(errors):
    required_files = [
        '10_runtime/station_chief_runtime.py',
        '10_runtime/station_chief_demo_cases.json',
        '10_runtime/station_chief_runtime_readme.md',
        '10_runtime/station_chief_fixture_tests.py',
        '10_runtime/station_chief_adapters.py',
        '10_runtime/station_chief_execution_profiles.py',
        '10_runtime/station_chief_approval_handoff.py',
        '10_runtime/station_chief_approval_records.py',
        '10_runtime/station_chief_approval_ledger.py',
        '10_runtime/station_chief_release_lock.py',
        '10_runtime/station_chief_controlled_execution.py',
        '10_runtime/station_chief_work_order_executor.py',
        '10_runtime/station_chief_worker_hiring_registry.py',
        '10_runtime/station_chief_department_routing.py',
        '10_runtime/station_chief_multi_agent_orchestration.py',
        '10_runtime/station_chief_operator_console.py',
        '10_runtime/station_chief_github_patch_hardening.py',
        '10_runtime/station_chief_deployment_packaging.py',
        '10_runtime/station_chief_controlled_worker_execution.py',
        '10_runtime/station_chief_tool_permission_binding.py',
        '10_runtime/station_chief_live_execution_telemetry_abort.py',
        '10_runtime/station_chief_post_run_audit_expansion.py',
        '10_runtime/station_chief_multi_worker_sandbox_coordination.py',
        '10_runtime/station_chief_controlled_external_tool_adapter_preview.py',
        '10_runtime/station_chief_permissioned_external_api_dry_run_preview.py',
        '10_runtime/station_chief_controlled_multi_worker_audit_replay_preview.py',
        '10_runtime/station_chief_operator_approval_queue_enforcement.py',
        '10_runtime/station_chief_release_candidate_hardening.py',
        '10_runtime/station_chief_controlled_production_readiness_gate.py',
        '10_runtime/station_chief_controlled_worker_hiring_activation_pilot.py',
        '10_runtime/station_chief_first_supervised_production_dry_run.py',
        '10_runtime/station_chief_limited_external_tool_supervised_pilot.py',
        '10_runtime/station_chief_supervised_external_api_pilot.py',
        '10_runtime/station_chief_monitored_rollback_recovery_drill.py',
        '09_exports/station_chief_runtime_skeleton_report.md',
        '09_exports/station_chief_runtime_v3_5_report.md',
        'scripts/validate_station_chief_runtime_v3_5.py',
    ]
    for rel in required_files:
        check_exists(errors, ROOT / rel)


def check_required_text(errors):
    runtime = read_text(RUNTIME_DIR / 'station_chief_runtime.py')
    monitored = read_text(RUNTIME_DIR / 'station_chief_monitored_rollback_recovery_drill.py')
    adapters = read_text(RUNTIME_DIR / 'station_chief_adapters.py')
    release_lock = read_text(RUNTIME_DIR / 'station_chief_release_lock.py')
    readme = read_text(RUNTIME_DIR / 'station_chief_runtime_readme.md')
    skeleton = read_text(EXPORTS_DIR / 'station_chief_runtime_skeleton_report.md')
    report = read_text(EXPORTS_DIR / 'station_chief_runtime_v3_5_report.md')

    runtime_required = [
        'STATION_CHIEF_RUNTIME_VERSION = "3.5.0"',
        'attach_supervised_external_api_pilot',
        'write_supervised_external_api_pilot',
        'attach_monitored_rollback_recovery_drill',
        'write_monitored_rollback_recovery_drill',
        '--supervised-external-api-pilot-schema',
        '--supervised-external-api-pilot',
        '--write-supervised-external-api-pilot',
        '--monitored-rollback-recovery-drill-schema',
        '--monitored-rollback-recovery-drill',
        '--write-monitored-rollback-recovery-drill',
        '--api-pilot-label',
        '--api-pilot-confirm-token',
        '--api-category-label',
        '--api-pilot-required-preflight-approver',
        '--api-request-label',
        '--api-quarantine-label',
        '--recovery-drill-label',
        '--recovery-drill-confirm-token',
        '--simulated-failure-label',
        '--rollback-path-label',
        '--recovery-checkpoint-label',
        '--required-recovery-approver',
        '--recovery-quarantine-label',
        'supervised_external_api_pilot_bundle',
        'supervised_external_api_pilot_schema',
        'supervised_external_api_pilot_approval_gate',
        'single_api_category_contract',
        'credential_denial_by_default',
        'secret_handling_denial_by_default',
        'network_socket_denial_by_default',
        'human_api_use_preflight_gate',
        'api_request_envelope_preview',
        'api_response_quarantine_preview',
        'api_audit_proof',
        'api_pilot_ledger',
        'api_pilot_readiness_summary',
        'monitored_rollback_recovery_drill_bridge',
        'monitored_rollback_recovery_drill_bundle',
        'monitored_rollback_recovery_drill_schema',
        'monitored_rollback_recovery_drill_approval_gate',
        'simulated_failure_trigger_contract',
        'rollback_path_preview',
        'recovery_checkpoint_contract',
        'quarantine_freeze_preview',
        'human_recovery_approval_gate',
        'recovery_audit_proof',
        'rollback_recovery_drill_ledger',
        'recovery_readiness_summary',
        'supervised_production_pilot_readiness_review_bridge',
        'station-chief-v3-5-',
        'registry_version',
        'index_version',
    ]
    for item in runtime_required:
        require_in(errors, item, runtime, f'station_chief_runtime.py missing required text {item!r}')

    monitored_required = [
        'MONITORED_ROLLBACK_RECOVERY_DRILL_MODULE_VERSION = "3.5.0"',
        'MONITORED_ROLLBACK_RECOVERY_DRILL_STATUS',
        'MONITORED_ROLLBACK_RECOVERY_DRILL_PHASE',
        'MONITORED_ROLLBACK_RECOVERY_DRILL_APPROVAL_TOKEN',
        'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL',
        'canonical_json',
        'sha256_digest',
        'normalize_recovery_drill_label',
        'generate_monitored_rollback_recovery_drill_id',
        'create_monitored_rollback_recovery_drill_schema',
        'create_monitored_rollback_recovery_drill_approval_gate',
        'create_simulated_failure_trigger_contract',
        'create_rollback_path_preview',
        'create_recovery_checkpoint_contract',
        'create_quarantine_freeze_preview',
        'create_human_recovery_approval_gate',
        'create_recovery_audit_proof',
        'create_rollback_recovery_drill_ledger',
        'create_recovery_readiness_summary',
        'create_supervised_production_pilot_readiness_review_bridge',
        'create_monitored_rollback_recovery_drill_bundle',
    ]
    for item in monitored_required:
        require_in(errors, item, monitored, f'station_chief_monitored_rollback_recovery_drill.py missing required text {item!r}')

    adapters_required = [
        'ADAPTER_MODULE_VERSION = "3.5.0"',
        'supports_monitored_rollback_recovery_drill',
        'monitored_rollback_recovery_drill_requires_specific_token',
        'real_rollback_allowed',
        'real_recovery_allowed',
        'process_termination_allowed',
        'worker_termination_allowed',
        'production_state_change_allowed',
        'deployment_rollback_allowed',
        'deployment_allowed',
        'live_api_call_allowed',
        'network_access_allowed',
        'socket_access_allowed',
        'credential_use_allowed',
        'secret_read_allowed',
        'environment_read_allowed',
        'real_external_tool_invocation_allowed',
        'production_execution_allowed',
        'production_activation_allowed',
        'real_task_execution_allowed',
        'live_task_assignment_allowed',
        'live_worker_routing_allowed',
        'live_orchestration_allowed',
        'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL',
    ]
    for item in adapters_required:
        require_in(errors, item, adapters, f'station_chief_adapters.py missing required text {item!r}')

    release_required = [
        'STABLE_RUNTIME_VERSION = "3.5.0"',
        'current_phase": "Monitored Rollback and Recovery Drill"',
        'next_phase": "Supervised Production Pilot Readiness Review"',
        'v3.6 supervised production pilot readiness review',
        'v3.7 credential vault denial and secret handling proof',
        'v3.8 network/socket lockdown proof',
        'v3.9 live external action final preflight gate',
    ]
    for item in release_required:
        require_in(errors, item, release_lock, f'station_chief_release_lock.py missing required text {item!r}')

    readme_required = [
        'Station Chief Runtime upgraded to v3.5.0.',
        'Monitored rollback and recovery drill added.',
        'monitored rollback recovery drill schema',
        'monitored rollback recovery drill approval gate',
        'simulated failure trigger contract',
        'rollback path preview',
        'recovery checkpoint contract',
        'quarantine/freeze preview',
        'human recovery approval gate',
        'recovery audit proof',
        'rollback recovery drill ledger',
        'recovery readiness summary',
        'supervised production pilot readiness review bridge',
        'no real rollback',
        'no real recovery',
        'no process termination',
        'no worker termination',
        'no production state changes',
        'no deployment rollback',
        'no deployment',
        'no live API calls',
        'no credential use',
        'no secret reads',
        'no environment reads',
        'no network access',
        'no socket access',
        'no production execution',
        'no full workforce activation',
        'Station Chief Runtime v3.5.0 adds Monitored Rollback and Recovery Drill without real rollback, real recovery, process termination, worker termination, production state changes, deployment rollback, deployment, live API calls, network access, socket access, credential use, secret reads, environment reads, real external tool invocation, real production execution, production activation, real task execution, live task assignment, live worker routing, live orchestration, worker process starts, shell command execution, or broad workforce activation',
        'Next recommended step: build supervised production pilot readiness review.',
    ]
    for item in readme_required:
        require_in(errors, item, readme, f'station_chief_runtime_readme.md missing required text {item!r}')

    skeleton_required = [
        'Station Chief Runtime upgraded to v3.5.0.',
        'Monitored rollback and recovery drill added.',
        'monitored rollback recovery drill schema',
        'monitored rollback recovery drill approval gate',
        'simulated failure trigger contract',
        'rollback path preview',
        'recovery checkpoint contract',
        'quarantine/freeze preview',
        'human recovery approval gate',
        'recovery audit proof',
        'rollback recovery drill ledger',
        'recovery readiness summary',
        'supervised production pilot readiness review bridge',
        'no real rollback',
        'no real recovery',
        'no process termination',
        'no worker termination',
        'no production state changes',
        'no deployment rollback',
        'no deployment',
        'no live API calls',
        'no credential use',
        'no secret reads',
        'no environment reads',
        'no network access',
        'no socket access',
        'no production execution',
        'no production activation',
        'no live task assignment',
        'no live worker routing',
        'no live orchestration',
        'no shell command execution',
        'no arbitrary code execution',
        'no repo mutation',
        'python3 scripts/validate_station_chief_runtime_v3_5.py',
        'Next recommended build step: build supervised production pilot readiness review.',
    ]
    for item in skeleton_required:
        require_in(errors, item, skeleton, f'station_chief_runtime_skeleton_report.md missing required text {item!r}')

    report_required = [
        'Station Chief Runtime upgraded to v3.5.0.',
        'Monitored rollback and recovery drill added.',
        'monitored rollback recovery drill schema',
        'monitored rollback recovery drill approval gate',
        'simulated failure trigger contract',
        'rollback path preview',
        'recovery checkpoint contract',
        'quarantine/freeze preview',
        'human recovery approval gate',
        'recovery audit proof',
        'rollback recovery drill ledger',
        'recovery readiness summary',
        'supervised production pilot readiness review bridge',
        'no real rollback',
        'no real recovery',
        'no process termination',
        'no worker termination',
        'no production state changes',
        'no deployment rollback',
        'no deployment',
        'no live API calls',
        'no credential use',
        'no secret reads',
        'no environment reads',
        'no network access',
        'no socket access',
        'no production execution',
        'no full workforce activation',
    ]
    for item in report_required:
        require_in(errors, item, report, f'station_chief_runtime_v3_5_report.md missing required text {item!r}')

    for forbidden in ['Explain that', 'Include:', 'List:', 'Write:']:
        require(errors, forbidden not in readme, f'station_chief_runtime_readme.md contains forbidden scaffold text {forbidden!r}')
        require(errors, forbidden not in skeleton, f'station_chief_runtime_skeleton_report.md contains forbidden scaffold text {forbidden!r}')


def check_forbidden_strings(errors):
    general_forbidden = [
        'import requests',
        'from requests',
        'urllib.request',
        'import urllib.request',
        'os.system',
        'subprocess.run',
        'subprocess.Popen',
        'import subprocess',
        'pip install',
        'npm install',
        'API key',
    ]
    monitored_extra = [
        'eval(',
        'exec(',
        'compile(',
        'open(',
        'import socket',
        'from socket',
        'http.server',
        'socketserver',
        'uvicorn',
        'streamlit',
        'netlify',
        'vercel',
        'cloudflare',
        'firebase',
        'railway',
        'render',
        'gh api',
        'git push',
        'create_deployment',
        'create_commit',
        'update_ref',
        '__import__',
        'threading',
        'multiprocessing',
        'kill(',
        'terminate(',
        'getenv(',
        'os.getenv',
        'os.environ',
        'environ[',
        'datetime.now',
        'time.time',
    ]

    for path in sorted(RUNTIME_DIR.glob('station_chief_*.py')):
        text = read_text(path)
        for item in general_forbidden:
            require(errors, item not in text, f'{path.relative_to(ROOT)} contains forbidden text {item!r}')
        if path.name == 'station_chief_monitored_rollback_recovery_drill.py':
            for item in monitored_extra:
                require(errors, item not in text, f'{path.relative_to(ROOT)} contains forbidden text {item!r}')


def check_demo_output(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--demo'], 'demo run', errors)
    data = parse_json_output(stdout, 'demo run', errors)
    if rc == 0 and data is not None:
        require_equal(errors, get_path(data, 'station_chief_runtime_version'), '3.5.0', 'demo runtime version')
        require_equal(errors, get_path(data, 'runtime_status'), 'monitored_rollback_recovery_drill', 'demo runtime status')
        require_equal(errors, get_path(data, 'release_status'), 'STABLE_LOCKED', 'demo release status')
        require_equal(errors, get_path(data, 'command_type'), 'verification', 'demo command type')
        evidence = data.get('evidence', {})
        require_true(errors, evidence.get('baseline_preserved'), 'demo evidence baseline_preserved')
        require_false(errors, evidence.get('external_actions_taken'), 'demo evidence external_actions_taken')
        require_false(errors, evidence.get('live_worker_agents_activated'), 'demo evidence live_worker_agents_activated')
        for field in [
            'monitored_rollback_recovery_drill_available',
            'monitored_rollback_recovery_drill_preview_only',
            'monitored_rollback_recovery_drill_requires_token',
            'simulated_failure_trigger_preview_only',
            'rollback_path_preview_only',
            'recovery_checkpoint_preview_only',
            'quarantine_freeze_preview_only',
            'monitored_rollback_recovery_drill_does_not_perform_real_rollback',
            'monitored_rollback_recovery_drill_does_not_perform_real_recovery',
            'monitored_rollback_recovery_drill_does_not_terminate_processes',
            'monitored_rollback_recovery_drill_does_not_terminate_workers',
            'monitored_rollback_recovery_drill_does_not_change_production_state',
            'monitored_rollback_recovery_drill_does_not_rollback_deployments',
            'monitored_rollback_recovery_drill_does_not_deploy',
            'monitored_rollback_recovery_drill_does_not_call_live_apis',
            'monitored_rollback_recovery_drill_does_not_use_network_access',
            'monitored_rollback_recovery_drill_does_not_open_sockets',
            'monitored_rollback_recovery_drill_does_not_use_credentials',
            'monitored_rollback_recovery_drill_does_not_read_secrets',
            'monitored_rollback_recovery_drill_does_not_read_environment',
            'monitored_rollback_recovery_drill_does_not_execute_production',
            'monitored_rollback_recovery_drill_does_not_modify_repo_files',
            'supervised_production_pilot_readiness_review_not_yet_active',
        ]:
            require_true(errors, evidence.get(field), f'demo evidence {field}')


def check_fixture_outputs(errors):
    commands = [
        (['python3', '10_runtime/station_chief_runtime.py', '--fixture-test'], 'runtime fixture test'),
        (['python3', '10_runtime/station_chief_fixture_tests.py'], 'fixture test script'),
    ]
    for cmd, context in commands:
        rc, stdout, stderr = run_command(cmd, context, errors)
        data = parse_json_output(stdout, context, errors)
        if rc == 0 and data is not None:
            require_equal(errors, get_path(data, 'fixture_test_status'), 'PASS', f'{context} fixture status')
            require_equal(errors, get_path(data, 'runtime_version'), '3.5.0', f'{context} runtime version')
            require_equal(errors, get_path(data, 'case_count'), 5, f'{context} case count')
            require_equal(errors, get_path(data, 'failed'), 0, f'{context} failed count')


def check_overlays(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--list-overlays'], 'list overlays', errors)
    data = parse_json_output(stdout, 'list overlays', errors)
    if rc == 0 and data is not None:
        overlays = find_list(data, ['overlays', 'overlay_stack_summary', 'overlay_stack', 'items'])
        require(errors, overlays is not None, 'list overlays output missing overlay list')
        if overlays is not None:
            require_equal(errors, len(overlays), 8, 'overlay count')
            for overlay in overlays:
                require_true(errors, overlay.get('exists'), f"overlay {overlay.get('id') or overlay.get('name')} exists")
                require_true(errors, overlay.get('preserves_locked_baseline'), f"overlay {overlay.get('id') or overlay.get('name')} baseline preservation")
                owner = overlay.get('ownership_project_owner', '')
                require_in(errors, 'Devin O’Rourke', owner, f"overlay {overlay.get('id') or overlay.get('name')} owner")


def check_adapters(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--list-adapters'], 'list adapters', errors)
    data = parse_json_output(stdout, 'list adapters', errors)
    if rc == 0 and data is not None:
        require_equal(errors, get_path(data, 'adapter_module_version'), '3.5.0', 'adapter module version')
        adapter_fields = [
            'supports_monitored_rollback_recovery_drill',
            'monitored_rollback_recovery_drill_requires_specific_token',
            'real_rollback_allowed',
            'real_recovery_allowed',
            'process_termination_allowed',
            'worker_termination_allowed',
            'production_state_change_allowed',
            'deployment_rollback_allowed',
            'deployment_allowed',
            'live_api_call_allowed',
            'network_access_allowed',
            'socket_access_allowed',
            'credential_use_allowed',
            'secret_read_allowed',
            'environment_read_allowed',
            'real_external_tool_invocation_allowed',
            'production_execution_allowed',
            'production_activation_allowed',
            'real_task_execution_allowed',
            'live_task_assignment_allowed',
            'live_worker_routing_allowed',
            'live_orchestration_allowed',
        ]
        for field in adapter_fields:
            require_true(errors, field in data, f'list adapters missing field {field}')
        supported = data.get('supported_adapters', {})
        noop = supported.get('noop', {})
        scoped = supported.get('scoped_repo_patch', {})
        require_true(errors, noop.get('supports_monitored_rollback_recovery_drill'), 'noop adapter monitored drill support')
        require_false(errors, noop.get('live_api_call_allowed'), 'noop live_api_call_allowed')
        require_false(errors, noop.get('network_access_allowed'), 'noop network_access_allowed')
        require_false(errors, noop.get('socket_access_allowed'), 'noop socket_access_allowed')
        require_false(errors, noop.get('credential_use_allowed'), 'noop credential_use_allowed')
        require_false(errors, noop.get('secret_read_allowed'), 'noop secret_read_allowed')
        require_false(errors, noop.get('deployment_allowed'), 'noop deployment_allowed')
        require_false(errors, scoped.get('supports_monitored_rollback_recovery_drill'), 'scoped adapter monitored drill support')
        require_true(errors, scoped.get('monitored_rollback_recovery_drill_requires_separate_gate'), 'scoped adapter separate gate')


def check_schema(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--monitored-rollback-recovery-drill-schema'], 'monitored drill schema', errors)
    data = parse_json_output(stdout, 'monitored drill schema', errors)
    if rc == 0 and data is not None:
        require_equal(errors, get_path(data, 'monitored_rollback_recovery_drill_schema_version'), '3.5.0', 'monitored drill schema version')
        require_equal(errors, get_path(data, 'schema_status'), 'MONITORED_ROLLBACK_RECOVERY_DRILL_PREVIEW_ONLY', 'monitored drill schema status')
        required_sections = get_path(data, 'required_sections', [])
        for item in [
            'monitored_rollback_recovery_drill_approval_gate',
            'simulated_failure_trigger_contract',
            'rollback_path_preview',
            'recovery_checkpoint_contract',
            'quarantine_freeze_preview',
            'human_recovery_approval_gate',
            'recovery_audit_proof',
            'rollback_recovery_drill_ledger',
            'recovery_readiness_summary',
            'supervised_production_pilot_readiness_review_bridge',
        ]:
            require_in(errors, item, required_sections, f'schema required sections')
        blocked = get_path(data, 'blocked_recovery_drill_modes', [])
        for item in [
            'real_rollback_execution',
            'real_recovery_execution',
            'process_termination',
            'worker_termination',
            'production_state_change',
            'deployment_rollback',
            'live_api_call',
            'network_access',
            'socket_connection',
            'credential_use',
            'secret_read',
            'environment_variable_read',
            'production_execution',
            'full_workforce_activation',
        ]:
            require_in(errors, item, blocked, f'schema blocked modes')
        required_tokens = get_path(data, 'required_confirmation_tokens', [])
        require_in(errors, 'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL', required_tokens, 'schema confirmation tokens')
        require_true(errors, get_path(data, 'baseline_preserved'), 'schema baseline preserved')
        safety_fields = [
            'external_actions_taken', 'real_rollback_performed', 'real_recovery_performed',
            'processes_terminated', 'workers_terminated', 'production_state_changed', 'deployment_rollback_performed',
            'deployment_performed', 'live_api_call_performed', 'network_access_performed', 'socket_opened',
            'credentials_used', 'secrets_read', 'environment_read', 'real_external_tool_invocation_performed',
            'production_execution_performed', 'production_activation_performed', 'real_task_execution_performed',
            'live_task_assignment_performed', 'live_worker_routing_performed', 'live_orchestration_performed',
            'worker_processes_started', 'repo_files_modified', 'execution_authorized',
        ]
        all_false(errors, data, safety_fields, 'schema')


def check_default_blocked(errors):
    rc, stdout, stderr = run_command(
        ['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--monitored-rollback-recovery-drill', '--json'],
        'default monitored drill',
        errors,
    )
    data = parse_json_output(stdout, 'default monitored drill', errors)
    if rc == 0 and data is not None:
        require_true(errors, 'monitored_rollback_recovery_drill_bundle' in data, 'default monitored drill bundle present')
        require_true(errors, 'supervised_external_api_pilot_bundle' in data, 'default monitored drill supervised bundle present')
        gate = get_path(data, 'monitored_rollback_recovery_drill_bundle.monitored_rollback_recovery_drill_approval_gate')
        contract = get_path(data, 'monitored_rollback_recovery_drill_bundle.simulated_failure_trigger_contract')
        rollback = get_path(data, 'monitored_rollback_recovery_drill_bundle.rollback_path_preview')
        checkpoint = get_path(data, 'monitored_rollback_recovery_drill_bundle.recovery_checkpoint_contract')
        quarantine = get_path(data, 'monitored_rollback_recovery_drill_bundle.quarantine_freeze_preview')
        human = get_path(data, 'monitored_rollback_recovery_drill_bundle.human_recovery_approval_gate')
        audit = get_path(data, 'monitored_rollback_recovery_drill_bundle.recovery_audit_proof')
        ledger = get_path(data, 'monitored_rollback_recovery_drill_bundle.rollback_recovery_drill_ledger')
        readiness = get_path(data, 'monitored_rollback_recovery_drill_bundle.recovery_readiness_summary')
        bridge = get_path(data, 'monitored_rollback_recovery_drill_bundle.supervised_production_pilot_readiness_review_bridge')
        require_equal(errors, get_path(gate, 'gate_status'), 'BLOCKED_PENDING_MONITORED_ROLLBACK_RECOVERY_DRILL_APPROVAL', 'default gate status')
        require_false(errors, get_path(gate, 'confirmation_token_valid'), 'default gate token valid')
        require_false(errors, get_path(gate, 'local_recovery_drill_records_authorized'), 'default gate local records')
        require_equal(errors, get_path(contract, 'contract_status'), 'BLOCKED', 'default simulated failure contract status')
        require_equal(errors, get_path(rollback, 'preview_status'), 'BLOCKED', 'default rollback preview status')
        require_equal(errors, get_path(checkpoint, 'contract_status'), 'BLOCKED', 'default checkpoint contract status')
        require_equal(errors, get_path(quarantine, 'preview_status'), 'BLOCKED', 'default quarantine preview status')
        require_equal(errors, get_path(human, 'recovery_approval_status'), 'BLOCKED', 'default human approval status')
        require_equal(errors, get_path(audit, 'audit_status'), 'BLOCKED', 'default audit status')
        require_equal(errors, get_path(ledger, 'ledger_status'), 'BLOCKED', 'default ledger status')
        require_equal(errors, get_path(readiness, 'readiness_status'), 'BLOCKED', 'default readiness status')
        require_false(errors, get_path(bridge, 'ready_for_supervised_production_pilot_readiness_review'), 'default bridge readiness')
        for field in [
            'external_actions_taken', 'live_api_call_performed', 'network_access_performed', 'socket_opened',
            'credentials_used', 'secrets_read', 'environment_read', 'deployment_performed',
            'real_external_tool_invocation_performed', 'production_execution_performed',
            'production_activation_performed', 'real_task_execution_performed', 'live_task_assignment_performed',
            'live_worker_routing_performed', 'live_orchestration_performed', 'worker_processes_started',
            'repo_files_modified', 'execution_authorized',
        ]:
            require_false(errors, get_path(data, field), f'default monitored drill field {field}')


def check_valid_token(errors):
    rc, stdout, stderr = run_command(
        [
            'python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--monitored-rollback-recovery-drill',
            '--recovery-drill-confirm-token', 'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL', '--json'
        ],
        'valid monitored drill',
        errors,
    )
    data = parse_json_output(stdout, 'valid monitored drill', errors)
    if rc == 0 and data is not None:
        bundle = get_path(data, 'monitored_rollback_recovery_drill_bundle')
        gate = get_path(bundle, 'monitored_rollback_recovery_drill_approval_gate')
        contract = get_path(bundle, 'simulated_failure_trigger_contract')
        rollback = get_path(bundle, 'rollback_path_preview')
        checkpoint = get_path(bundle, 'recovery_checkpoint_contract')
        quarantine = get_path(bundle, 'quarantine_freeze_preview')
        human = get_path(bundle, 'human_recovery_approval_gate')
        audit = get_path(bundle, 'recovery_audit_proof')
        ledger = get_path(bundle, 'rollback_recovery_drill_ledger')
        readiness = get_path(bundle, 'recovery_readiness_summary')
        bridge = get_path(bundle, 'supervised_production_pilot_readiness_review_bridge')
        require_equal(errors, get_path(gate, 'gate_status'), 'APPROVED_FOR_MONITORED_ROLLBACK_RECOVERY_DRILL_RECORDS', 'valid gate status')
        require_true(errors, get_path(gate, 'confirmation_token_valid'), 'valid gate token valid')
        require_true(errors, get_path(gate, 'local_recovery_drill_records_authorized'), 'valid gate local records')
        for field in [
            'real_rollback_authorized', 'real_recovery_authorized', 'process_termination_authorized',
            'worker_termination_authorized', 'production_state_change_authorized', 'deployment_rollback_authorized',
            'deployment_authorized', 'live_api_call_authorized', 'network_access_authorized', 'socket_access_authorized',
            'credential_use_authorized', 'secret_read_authorized', 'environment_read_authorized',
            'real_external_tool_invocation_authorized', 'production_execution_authorized',
            'production_activation_authorized', 'real_task_execution_authorized', 'live_task_assignment_authorized',
            'live_worker_routing_authorized', 'live_orchestration_authorized', 'worker_process_start_authorized',
            'repo_mutation_authorized', 'external_actions_taken', 'repo_files_modified', 'execution_authorized',
        ]:
            require_false(errors, get_path(gate, field), f'valid gate dangerous auth {field}')
        require_equal(errors, get_path(contract, 'contract_status'), 'SIMULATED_FAILURE_TRIGGER_CONTRACT_CREATED', 'valid simulated failure contract status')
        require_equal(errors, get_path(rollback, 'preview_status'), 'ROLLBACK_PATH_PREVIEW_CREATED', 'valid rollback preview status')
        require_equal(errors, get_path(checkpoint, 'contract_status'), 'RECOVERY_CHECKPOINT_CONTRACT_CREATED', 'valid checkpoint status')
        require_equal(errors, get_path(quarantine, 'preview_status'), 'QUARANTINE_FREEZE_PREVIEW_CREATED', 'valid quarantine preview status')
        require_equal(errors, get_path(human, 'recovery_approval_status'), 'HUMAN_RECOVERY_APPROVAL_REQUIREMENT_CREATED', 'valid human approval status')
        require_equal(errors, get_path(audit, 'audit_status'), 'PASS', 'valid audit status')
        require_equal(errors, get_path(ledger, 'ledger_status'), 'MONITORED_ROLLBACK_RECOVERY_DRILL_LEDGER', 'valid ledger status')
        require_true(errors, get_path(readiness, 'ready_for_supervised_production_pilot_readiness_review'), 'valid readiness flag')
        require_equal(errors, get_path(bridge, 'next_layer'), 'Supervised Production Pilot Readiness Review', 'valid bridge next layer')
        require_true(errors, get_path(bridge, 'ready_for_supervised_production_pilot_readiness_review'), 'valid bridge readiness')
        for field in [
            'external_actions_taken', 'live_api_call_performed', 'network_access_performed', 'socket_opened',
            'credentials_used', 'secrets_read', 'environment_read', 'deployment_performed',
            'real_external_tool_invocation_performed', 'production_execution_performed',
            'production_activation_performed', 'real_task_execution_performed', 'live_task_assignment_performed',
            'live_worker_routing_performed', 'live_orchestration_performed', 'worker_processes_started',
            'repo_files_modified', 'execution_authorized',
        ]:
            require_false(errors, get_path(bundle, field), f'valid monitored drill field {field}')


def check_next_layer_command(errors):
    rc, stdout, stderr = run_command(
        [
            'python3', '10_runtime/station_chief_runtime.py', '--command', 'build supervised production pilot readiness review',
            '--monitored-rollback-recovery-drill', '--recovery-drill-confirm-token', 'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL', '--json'
        ],
        'next layer command',
        errors,
    )
    data = parse_json_output(stdout, 'next layer command', errors)
    if rc == 0 and data is not None:
        readiness = get_path(data, 'monitored_rollback_recovery_drill_bundle.recovery_readiness_summary')
        bridge = get_path(data, 'monitored_rollback_recovery_drill_bundle.supervised_production_pilot_readiness_review_bridge')
        audit = get_path(data, 'monitored_rollback_recovery_drill_bundle.recovery_audit_proof')
        require_equal(errors, get_path(bridge, 'next_layer'), 'Supervised Production Pilot Readiness Review', 'next layer bridge')
        require_true(errors, get_path(bridge, 'ready_for_supervised_production_pilot_readiness_review'), 'next layer bridge ready')
        require_equal(errors, get_path(readiness, 'next_layer'), 'Supervised Production Pilot Readiness Review', 'next layer readiness')
        require_equal(errors, get_path(readiness, 'readiness_status'), 'READY_FOR_NEXT_LAYER', 'next layer readiness status')
        require_equal(errors, get_path(audit, 'audit_status'), 'PASS', 'next layer audit status')
        for field in [
            'external_actions_taken', 'live_api_call_performed', 'network_access_performed', 'socket_opened',
            'credentials_used', 'secrets_read', 'environment_read', 'deployment_performed',
            'real_external_tool_invocation_performed', 'production_execution_performed',
            'production_activation_performed', 'execution_authorized',
        ]:
            require_false(errors, get_path(data, field), f'next layer field {field}')


def check_write_monitored_drill(errors):
    with tempfile.TemporaryDirectory() as tmpdir:
        rc, stdout, stderr = run_command(
            [
                'python3', '10_runtime/station_chief_runtime.py', '--command', 'check please',
                '--write-monitored-rollback-recovery-drill', tmpdir,
                '--recovery-drill-confirm-token', 'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL'
            ],
            'write monitored drill',
            errors,
        )
        data = parse_json_output(stdout, 'write monitored drill', errors)
        if rc == 0 and data is not None:
            summary = data.get('monitored_rollback_recovery_drill_write_summary')
            require(errors, summary is not None, 'write monitored drill summary missing')
            drill_dir = Path(get_path(summary, 'monitored_rollback_recovery_drill_dir', ''))
            require(errors, drill_dir.exists(), 'monitored rollback recovery drill dir missing')
            run_id = get_path(summary, 'run_id')
            require(errors, isinstance(run_id, str) and run_id.startswith('station-chief-v3-5-check-please-'), 'write monitored drill run id prefix')
            expected_files = [
                'monitored_rollback_recovery_drill_bundle.json',
                'monitored_rollback_recovery_drill_schema.json',
                'monitored_rollback_recovery_drill_approval_gate.json',
                'simulated_failure_trigger_contract.json',
                'rollback_path_preview.json',
                'recovery_checkpoint_contract.json',
                'quarantine_freeze_preview.json',
                'human_recovery_approval_gate.json',
                'recovery_audit_proof.json',
                'rollback_recovery_drill_ledger.json',
                'recovery_readiness_summary.json',
                'supervised_production_pilot_readiness_review_bridge.json',
                'monitored_rollback_recovery_drill_manifest.json',
            ]
            files_written = get_path(summary, 'files_written', [])
            for item in expected_files:
                require_in(errors, item, files_written, 'write monitored drill files written')
                require(errors, (drill_dir / item).exists(), f'write monitored drill missing file {item}')
            manifest = json.loads((drill_dir / 'monitored_rollback_recovery_drill_manifest.json').read_text(encoding='utf-8'))
            require_equal(errors, get_path(manifest, 'runtime_version'), '3.5.0', 'write monitored drill manifest version')
            require_equal(errors, get_path(manifest, 'status'), 'MONITORED_ROLLBACK_RECOVERY_DRILL_PREVIEW_ONLY', 'write monitored drill manifest status')
            require_true(errors, get_path(manifest, 'baseline_preserved'), 'write monitored drill manifest baseline preserved')
            manifest_false_fields = [
                'external_actions_taken', 'real_rollback_performed', 'real_recovery_performed',
                'processes_terminated', 'workers_terminated', 'production_state_changed', 'deployment_rollback_performed',
                'deployment_performed', 'live_api_call_performed', 'network_access_performed', 'socket_opened',
                'credentials_used', 'secrets_read', 'environment_read', 'real_external_tool_invocation_performed',
                'production_execution_performed', 'production_activation_performed', 'real_task_execution_performed',
                'live_task_assignment_performed', 'live_worker_routing_performed', 'live_orchestration_performed',
                'worker_processes_started', 'repo_files_modified', 'execution_authorized',
            ]
            all_false(errors, manifest, manifest_false_fields, 'write monitored drill manifest')


def check_write_artifacts_and_registry(errors):
    with tempfile.TemporaryDirectory() as run_tmp, tempfile.TemporaryDirectory() as registry_tmp:
        rc, stdout, stderr = run_command(
            [
                'python3', '10_runtime/station_chief_runtime.py', '--command', 'check please',
                '--write-artifacts', run_tmp, '--registry-dir', registry_tmp,
                '--monitored-rollback-recovery-drill', '--recovery-drill-confirm-token', 'YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL'
            ],
            'write artifacts and registry',
            errors,
        )
        data = parse_json_output(stdout, 'write artifacts and registry', errors)
        if rc == 0 and data is not None:
            summary = data.get('artifact_write_summary')
            require(errors, summary is not None, 'artifact write summary missing')
            run_id = get_path(summary, 'run_id')
            require(errors, isinstance(run_id, str) and run_id.startswith('station-chief-v3-5-check-please-'), 'artifact run id prefix')
            artifact_dir = Path(get_path(summary, 'artifact_dir', ''))
            require(errors, artifact_dir.exists(), 'artifact directory missing')
            require_true(errors, get_path(summary, 'registry_updated'), 'registry updated flag')
            files_written = get_path(summary, 'files_written', [])
            for item in [
                'monitored_rollback_recovery_drill_bundle.json',
                'monitored_rollback_recovery_drill_schema.json',
                'monitored_rollback_recovery_drill_approval_gate.json',
                'simulated_failure_trigger_contract.json',
                'rollback_path_preview.json',
                'recovery_checkpoint_contract.json',
                'quarantine_freeze_preview.json',
                'human_recovery_approval_gate.json',
                'recovery_audit_proof.json',
                'rollback_recovery_drill_ledger.json',
                'recovery_readiness_summary.json',
                'supervised_production_pilot_readiness_review_bridge.json',
                'manifest.json',
                'full_result.json',
            ]:
                require_in(errors, item, files_written, 'artifact files written')
                require(errors, (artifact_dir / item).exists(), f'artifact missing file {item}')
            manifest = json.loads((artifact_dir / 'manifest.json').read_text(encoding='utf-8'))
            require_equal(errors, get_path(manifest, 'artifact_type'), 'station_chief_runtime_v3_5_artifacts', 'artifact manifest type')
            require_equal(errors, get_path(manifest, 'runtime_version'), '3.5.0', 'artifact manifest version')
            for field in [
                'supervised_external_api_pilot_schema', 'supervised_external_api_pilot_approval_gate', 'single_api_category_contract',
                'credential_denial_by_default', 'secret_handling_denial_by_default', 'network_socket_denial_by_default',
                'human_api_use_preflight_gate', 'api_request_envelope_preview', 'api_response_quarantine_preview',
                'api_audit_proof', 'api_pilot_ledger', 'api_pilot_readiness_summary', 'monitored_rollback_recovery_drill_bridge',
                'monitored_rollback_recovery_drill_schema', 'monitored_rollback_recovery_drill_approval_gate',
                'simulated_failure_trigger_contract', 'rollback_path_preview', 'recovery_checkpoint_contract',
                'quarantine_freeze_preview', 'human_recovery_approval_gate', 'recovery_audit_proof',
                'rollback_recovery_drill_ledger', 'recovery_readiness_summary', 'supervised_production_pilot_readiness_review_bridge',
                'monitored_rollback_recovery_drill_preview_only', 'monitored_rollback_recovery_drill_requires_token',
                'simulated_failure_trigger_preview_only', 'rollback_path_preview_only', 'recovery_checkpoint_preview_only',
                'quarantine_freeze_preview_only', 'monitored_rollback_recovery_drill_does_not_perform_real_rollback',
                'monitored_rollback_recovery_drill_does_not_perform_real_recovery', 'monitored_rollback_recovery_drill_does_not_terminate_processes',
                'monitored_rollback_recovery_drill_does_not_terminate_workers', 'monitored_rollback_recovery_drill_does_not_change_production_state',
                'monitored_rollback_recovery_drill_does_not_rollback_deployments', 'monitored_rollback_recovery_drill_does_not_deploy',
                'monitored_rollback_recovery_drill_does_not_call_live_apis', 'monitored_rollback_recovery_drill_does_not_use_network_access',
                'monitored_rollback_recovery_drill_does_not_open_sockets', 'monitored_rollback_recovery_drill_does_not_use_credentials',
                'monitored_rollback_recovery_drill_does_not_read_secrets', 'monitored_rollback_recovery_drill_does_not_read_environment',
                'monitored_rollback_recovery_drill_does_not_execute_production', 'monitored_rollback_recovery_drill_does_not_modify_repo_files',
            ]:
                require_true(errors, get_path(manifest, field), f'artifact manifest field {field}')
            registry = json.loads((Path(registry_tmp) / 'run_registry.json').read_text(encoding='utf-8'))
            index = json.loads((Path(registry_tmp) / 'runtime_index.json').read_text(encoding='utf-8'))
            require_equal(errors, get_path(registry, 'registry_version'), '3.5.0', 'registry version')
            require_true(errors, isinstance(get_path(registry, 'runs', []), list) and len(get_path(registry, 'runs', [])) >= 1, 'registry runs')
            require_equal(errors, get_path(index, 'index_version'), '3.5.0', 'runtime index version')
            require_true(errors, get_path(index, 'run_count') >= 1, 'runtime index run count')


def check_stable_release_manifest(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--stable-release-manifest'], 'stable release manifest', errors)
    data = parse_json_output(stdout, 'stable release manifest', errors)
    if rc == 0 and data is not None:
        manifest = get_path(data, 'stable_release_manifest') if isinstance(data, dict) else None
        if get_path(data, 'runtime_version') is None and manifest is not None:
            require_equal(errors, get_path(manifest, 'runtime_version'), '3.5.0', 'nested stable manifest version')
        else:
            require_equal(errors, get_path(data, 'runtime_version'), '3.5.0', 'stable manifest version')
        if get_path(data, 'release_status') is None and manifest is not None:
            require_equal(errors, get_path(manifest, 'release_status'), 'STABLE_LOCKED', 'nested stable manifest status')
        else:
            require_equal(errors, get_path(data, 'release_status'), 'STABLE_LOCKED', 'stable manifest status')
        if manifest:
            require_equal(errors, get_path(manifest, 'runtime_version'), '3.5.0', 'nested stable manifest version')
            require_equal(errors, get_path(manifest, 'release_status'), 'STABLE_LOCKED', 'nested stable manifest status')


def check_command_regressions(errors):
    commands = [
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--release-lock'], 'release lock', 'release_lock_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-execution'], 'controlled execution', 'controlled_execution_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--work-order-executor'], 'work order executor', 'work_order_executor_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--worker-hiring-registry'], 'worker hiring registry', 'worker_hiring_registry_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--department-routing'], 'department routing', 'department_routing_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--multi-agent-orchestration'], 'multi agent orchestration', 'multi_agent_orchestration_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--operator-console'], 'operator console', 'operator_console_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--github-patch-hardening'], 'github patch hardening', 'github_patch_hardening_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--deployment-packaging'], 'deployment packaging', 'deployment_packaging_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-worker-execution'], 'controlled worker execution', 'controlled_worker_execution_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--tool-permission-binding'], 'tool permission binding', 'tool_permission_binding_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--live-telemetry-abort'], 'live telemetry abort', 'live_execution_telemetry_abort_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--post-run-audit-expansion'], 'post run audit expansion', 'post_run_audit_expansion_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--multi-worker-sandbox-coordination'], 'multi worker sandbox coordination', 'multi_worker_sandbox_coordination_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-external-tool-preview'], 'controlled external tool preview', 'controlled_external_tool_adapter_preview_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--permissioned-external-api-dry-run'], 'permissioned external api dry run', 'permissioned_external_api_dry_run_preview_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-multi-worker-audit-replay-preview'], 'controlled multi worker audit replay preview', 'controlled_multi_worker_audit_replay_preview_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--operator-approval-queue-enforcement'], 'operator approval queue enforcement', 'operator_approval_queue_enforcement_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--release-candidate-hardening'], 'release candidate hardening', 'release_candidate_hardening_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-production-readiness-gate'], 'controlled production readiness gate', 'controlled_production_readiness_gate_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--controlled-worker-hiring-activation-pilot'], 'controlled worker hiring activation pilot', 'controlled_worker_hiring_activation_pilot_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--first-supervised-production-dry-run'], 'first supervised production dry run', 'first_supervised_production_dry_run_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--limited-external-tool-supervised-pilot'], 'limited external tool supervised pilot', 'limited_external_tool_supervised_pilot_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--supervised-external-api-pilot'], 'supervised external api pilot', 'supervised_external_api_pilot_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--monitored-rollback-recovery-drill'], 'monitored rollback recovery drill', 'monitored_rollback_recovery_drill_bundle'),
        (['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--approval-handoff'], 'approval handoff', 'approval_handoff_packet'),
    ]
    for cmd, context, expected_key in commands:
        rc, stdout, stderr = run_command(cmd, context, errors)
        data = parse_json_output(stdout, context, errors)
        if rc == 0 and data is not None:
            require_true(errors, expected_key in data, f'{context} expected key {expected_key}')
            if 'station_chief_runtime_version' in data:
                require_equal(errors, data['station_chief_runtime_version'], '3.5.0', f'{context} runtime version')
            if 'external_actions_taken' in data:
                require_false(errors, data['external_actions_taken'], f'{context} external actions')
            evidence = data.get('evidence')
            if isinstance(evidence, dict):
                if 'external_actions_taken' in evidence:
                    require_false(errors, evidence.get('external_actions_taken'), f'{context} evidence external actions')
                if 'baseline_preserved' in evidence:
                    require_true(errors, evidence.get('baseline_preserved'), f'{context} evidence baseline preserved')
            bad_flags = [
                'live_api_call_performed', 'network_access_performed', 'socket_opened', 'credentials_used',
                'secrets_read', 'environment_read', 'deployment_performed', 'real_external_tool_invocation_performed',
                'production_execution_performed', 'production_activation_performed', 'real_task_execution_performed',
                'live_task_assignment_performed', 'live_worker_routing_performed', 'live_orchestration_performed',
                'worker_processes_started',
            ]
            for field in bad_flags:
                if field in data:
                    require_false(errors, data.get(field), f'{context} field {field}')


def check_brief_and_simulate(errors):
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--command', 'build supervised production pilot readiness review', '--brief'], 'brief command', errors)
    data = parse_json_output(stdout, 'brief command', errors)
    if rc == 0 and data is not None:
        if 'station_chief_runtime_version' in data:
            require_equal(errors, data['station_chief_runtime_version'], '3.5.0', 'brief runtime version')
    rc, stdout, stderr = run_command(['python3', '10_runtime/station_chief_runtime.py', '--command', 'check please', '--simulate-adapter'], 'simulate adapter', errors)
    data = parse_json_output(stdout, 'simulate adapter', errors)
    if rc == 0 and data is not None:
        require_equal(errors, data.get('station_chief_runtime_version'), '3.5.0', 'simulate adapter runtime version')
        require_false(errors, data.get('external_actions_taken'), 'simulate adapter external actions')
        adapter_result = data.get('adapter_result', {})
        require_equal(errors, adapter_result.get('execution_mode'), 'controlled_noop', 'simulate adapter execution mode')
        require_true(errors, adapter_result.get('adapter_available'), 'simulate adapter available')
        require_equal(errors, data.get('runtime_status'), 'monitored_rollback_recovery_drill', 'simulate adapter runtime status')


def check_markdown_artifacts(errors):
    required = [
        'Station Chief Runtime upgraded to v3.5.0.',
        'Monitored rollback and recovery drill added.',
        'monitored rollback recovery drill schema',
        'monitored rollback recovery drill approval gate',
        'simulated failure trigger contract',
        'rollback path preview',
        'recovery checkpoint contract',
        'quarantine/freeze preview',
        'human recovery approval gate',
        'recovery audit proof',
        'rollback recovery drill ledger',
        'recovery readiness summary',
        'supervised production pilot readiness review bridge',
        'no real rollback',
        'no real recovery',
        'no process termination',
        'no worker termination',
        'no production state changes',
        'no deployment rollback',
        'no deployment',
        'no live API calls',
        'no credential use',
        'no secret reads',
        'no environment reads',
        'no network access',
        'no socket access',
        'no production execution',
        'no full workforce activation',
    ]
    readme = read_text(RUNTIME_DIR / 'station_chief_runtime_readme.md')
    skeleton = read_text(EXPORTS_DIR / 'station_chief_runtime_skeleton_report.md')
    report = read_text(EXPORTS_DIR / 'station_chief_runtime_v3_5_report.md')
    for item in required:
        require_in(errors, item, readme, f'readme missing phrase {item!r}')
        require_in(errors, item, skeleton, f'skeleton report missing phrase {item!r}')
        require_in(errors, item, report, f'v3.5 report missing phrase {item!r}')
    for forbidden in ['Explain that', 'Include:', 'List:', 'Write:']:
        require(errors, forbidden not in readme, f'readme contains scaffold text {forbidden!r}')
        require(errors, forbidden not in skeleton, f'skeleton report contains scaffold text {forbidden!r}')


def check_wrapped_files(errors):
    # Ensure older validators now delegate to the v3.5 validator.
    validator_files = sorted(SCRIPTS_DIR.glob('validate_station_chief_runtime_*.py'))
    for path in validator_files:
        if path.name == 'validate_station_chief_runtime_v3_5.py':
            continue
        text = read_text(path)
        require_in(errors, 'validate_station_chief_runtime_v3_5.py', text, f'{path.name} missing delegation to v3.5')
        require_in(errors, 'runpy.run_path', text, f'{path.name} missing runpy delegation')


def check_stable_runtime_files(errors):
    runtime = read_text(RUNTIME_DIR / 'station_chief_runtime.py')
    for item in ['STATION_CHIEF_RUNTIME_VERSION = "3.5.0"', 'station-chief-v3-5-', 'monitored_rollback_recovery_drill_bundle', 'write_monitored_rollback_recovery_drill', 'attach_monitored_rollback_recovery_drill']:
        require_in(errors, item, runtime, f'station_chief_runtime.py missing required text {item!r}')


def main():
    errors = []
    check_file_family(errors)
    check_stable_runtime_files(errors)
    check_required_text(errors)
    check_forbidden_strings(errors)
    check_demo_output(errors)
    check_fixture_outputs(errors)
    check_overlays(errors)
    check_adapters(errors)
    check_schema(errors)
    check_default_blocked(errors)
    check_valid_token(errors)
    check_next_layer_command(errors)
    check_write_monitored_drill(errors)
    check_write_artifacts_and_registry(errors)
    check_stable_release_manifest(errors)
    check_brief_and_simulate(errors)
    check_command_regressions(errors)
    check_markdown_artifacts(errors)
    check_wrapped_files(errors)

    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        print('FAIL')
        sys.exit(1)

    print('Manual scope check required: confirm git diff contains only the allowed Station Chief v3.5 runtime files.')
    print('PASS: Station Chief Runtime v3.5 valid.')


if __name__ == '__main__':
    main()
