import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_command(command: list[str]) -> tuple[int, str, str]:
    """Runs a command and returns (returncode, stdout, stderr)."""
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def parse_json_output(output: str, context: str, errors: list[str]) -> dict | list | None:
    """Locates and parses JSON from command output."""
    start_idx = -1
    for i, char in enumerate(output):
        if char in ('{', '['):
            start_idx = i
            break
    
    if start_idx == -1:
        errors.append(f"No JSON object found in output for context: {context}")
        return None
    
    try:
        return json.loads(output[start_idx:])
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse failure for context: {context}. Error: {e}")
        return None

def main():
    errors = []
    
    # PART 4 — Required file check
    required_files = [
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_demo_cases.json",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_fixture_tests.py",
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
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v3_2_report.md",
        "scripts/validate_station_chief_runtime_v3_2.py"
    ]
    
    for f in required_files:
        if not Path(f).exists():
            errors.append(f"Required file missing: {f}")

    # Runtime and module string checks
    if Path("10_runtime/station_chief_runtime.py").exists():
        runtime_content = Path("10_runtime/station_chief_runtime.py").read_text()
        runtime_required_strings = [
            'STATION_CHIEF_RUNTIME_VERSION = "3.2.0"',
            'attach_first_supervised_production_dry_run',
            'write_first_supervised_production_dry_run',
            '--first-supervised-production-dry-run-schema',
            '--first-supervised-production-dry-run',
            '--write-first-supervised-production-dry-run',
            '--dry-run-confirm-token',
            'first_supervised_production_dry_run_bundle',
            'first_supervised_production_dry_run_schema',
            'first_supervised_production_dry_run_approval_gate',
            'single_controlled_task_dry_run_envelope',
            'dry_run_only_production_context_contract',
            'human_preflight_approval_gate',
            'worker_task_simulation_contract',
            'external_action_denial_by_default',
            'dry_run_rollback_quarantine_preview',
            'dry_run_audit_proof',
            'dry_run_ledger',
            'dry_run_readiness_summary',
            'limited_external_tool_supervised_pilot_bridge'
        ]
        for s in runtime_required_strings:
            if s not in runtime_content:
                errors.append(f"Runtime script missing string: {s}")

    if Path("10_runtime/station_chief_first_supervised_production_dry_run.py").exists():
        dry_run_content = Path("10_runtime/station_chief_first_supervised_production_dry_run.py").read_text()
        dry_run_required_strings = [
            'FIRST_SUPERVISED_PRODUCTION_DRY_RUN_MODULE_VERSION = "3.2.0"',
            'create_first_supervised_production_dry_run_bundle'
        ]
        for s in dry_run_required_strings:
            if s not in dry_run_content:
                errors.append(f"Dry-run module missing string: {s}")

    if Path("10_runtime/station_chief_adapters.py").exists():
        adapter_content = Path("10_runtime/station_chief_adapters.py").read_text()
        if 'ADAPTER_MODULE_VERSION = "3.2.0"' not in adapter_content:
            errors.append("Adapter module version mismatch")
        if 'YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN' not in adapter_content:
            errors.append("Adapter module missing confirmation token")

    # PART 5 — Runtime demo checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if code != 0:
        errors.append(f"--demo failed: {stderr}")
    else:
        demo = parse_json_output(stdout, "--demo", errors)
        if demo:
            if demo.get("station_chief_runtime_version") != "3.2.0":
                errors.append("Demo version mismatch")
            if demo.get("runtime_status") != "first_supervised_production_dry_run":
                errors.append("Demo status mismatch")
            if demo.get("release_status") != "STABLE_LOCKED":
                errors.append("Demo release status mismatch")
            if demo.get("command_type") != "verification":
                errors.append("Demo command type mismatch")
            
            evidence = demo.get("evidence", {})
            required_evidence = {
                "baseline_preserved": True,
                "external_actions_taken": False,
                "live_worker_agents_activated": False,
                "first_supervised_production_dry_run_available": True,
                "first_supervised_production_dry_run_preview_only": True,
                "first_supervised_production_dry_run_requires_token": True,
                "single_controlled_task_dry_run_limit_is_one": True,
                "external_actions_denied_by_default": True,
                "first_supervised_production_dry_run_does_not_execute_production": True,
                "first_supervised_production_dry_run_does_not_activate_production": True,
                "first_supervised_production_dry_run_does_not_execute_real_tasks": True,
                "first_supervised_production_dry_run_does_not_assign_live_tasks": True,
                "first_supervised_production_dry_run_does_not_route_live_workers": True,
                "first_supervised_production_dry_run_does_not_perform_live_orchestration": True,
                "first_supervised_production_dry_run_does_not_invoke_external_tools": True,
                "first_supervised_production_dry_run_does_not_call_live_apis": True,
                "first_supervised_production_dry_run_does_not_use_network_access": True,
                "first_supervised_production_dry_run_does_not_open_sockets": True,
                "first_supervised_production_dry_run_does_not_use_credentials": True,
                "first_supervised_production_dry_run_does_not_read_secrets": True,
                "first_supervised_production_dry_run_does_not_read_environment": True,
                "first_supervised_production_dry_run_does_not_modify_repo_files": True,
                "first_supervised_production_dry_run_does_not_deploy": True,
                "limited_external_tool_supervised_pilot_not_yet_active": True
            }
            for k, v in required_evidence.items():
                if evidence.get(k) != v:
                    errors.append(f"Demo evidence mismatch: {k} should be {v}")

    # PART 6 — Fixture tests
    for cmd in [["python3", "10_runtime/station_chief_runtime.py", "--fixture-test"], ["python3", "10_runtime/station_chief_fixture_tests.py"]]:
        code, stdout, stderr = run_command(cmd)
        if code != 0:
            errors.append(f"{' '.join(cmd)} failed: {stderr}")
        else:
            fix = parse_json_output(stdout, ' '.join(cmd), errors)
            if fix:
                if fix.get("fixture_test_status") != "PASS":
                    errors.append(f"{' '.join(cmd)} status mismatch")
                if fix.get("runtime_version") != "3.2.0":
                    errors.append(f"{' '.join(cmd)} version mismatch")
                if fix.get("case_count") != 5:
                    errors.append(f"{' '.join(cmd)} case count mismatch")
                if fix.get("failed") != 0:
                    errors.append(f"{' '.join(cmd)} failure count mismatch")

    # PART 7 — Overlay list regression
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-overlays"])
    if code != 0:
        errors.append(f"--list-overlays failed: {stderr}")
    else:
        overlays = parse_json_output(stdout, "--list-overlays", errors)
        if overlays:
            if len(overlays) != 8:
                errors.append(f"Overlay count mismatch: expected 8, got {len(overlays)}")
            for ov in overlays:
                if ov.get("exists") is not True:
                    errors.append(f"Overlay {ov.get('id')} missing")
                if ov.get("preserves_locked_baseline") is not True:
                    errors.append(f"Overlay {ov.get('id')} does not preserve baseline")
                if "Devin O’Rourke" not in ov.get("ownership_project_owner", ""):
                    errors.append(f"Overlay {ov.get('id')} project owner mismatch")

    # PART 8 — Adapter checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-adapters"])
    if code != 0:
        errors.append(f"--list-adapters failed: {stderr}")
    else:
        adapters = parse_json_output(stdout, "--list-adapters", errors)
        if adapters:
            if adapters.get("adapter_module_version") != "3.2.0":
                errors.append("Adapter version mismatch")
            checks = {
                "supports_first_supervised_production_dry_run": True,
                "first_supervised_production_dry_run_requires_specific_token": True,
                "real_production_execution_allowed": False,
                "production_activation_allowed": False,
                "real_task_execution_allowed": False,
                "live_task_assignment_allowed": False,
                "live_worker_routing_allowed": False,
                "live_orchestration_allowed": False,
                "external_tool_invocation_allowed": False,
                "live_api_call_allowed": False,
                "network_access_allowed": False,
                "socket_access_allowed": False,
                "credential_use_allowed": False,
                "secret_read_allowed": False,
                "environment_read_allowed": False,
                "deployment_allowed": False
            }
            for k, v in checks.items():
                if adapters.get(k) != v:
                    errors.append(f"Adapter check {k} failed")
            
            noop = adapters.get("supported_adapters", {}).get("noop", {})
            if noop.get("supports_first_supervised_production_dry_run") is not True:
                errors.append("noop adapter should support dry-run")
            
            srp = adapters.get("supported_adapters", {}).get("scoped_repo_patch", {})
            if srp.get("supports_first_supervised_production_dry_run") is not False:
                errors.append("scoped_repo_patch adapter should NOT support dry-run")
            if srp.get("first_supervised_production_dry_run_requires_separate_gate") is not True:
                errors.append("scoped_repo_patch should require separate gate for dry-run")

    # PART 9 — Schema checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--first-supervised-production-dry-run-schema"])
    if code != 0:
        errors.append(f"--first-supervised-production-dry-run-schema failed: {stderr}")
    else:
        schema = parse_json_output(stdout, "--first-supervised-production-dry-run-schema", errors)
        if schema:
            if schema.get("first_supervised_production_dry_run_schema_version") != "3.2.0":
                errors.append("Schema version mismatch")
            if schema.get("schema_status") != "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY":
                errors.append("Schema status mismatch")
            
            expected_sections = [
                "first_supervised_production_dry_run_approval_gate", "single_controlled_task_dry_run_envelope",
                "dry_run_only_production_context_contract", "human_preflight_approval_gate",
                "worker_task_simulation_contract", "external_action_denial_by_default",
                "dry_run_rollback_quarantine_preview", "dry_run_audit_proof",
                "dry_run_ledger", "dry_run_readiness_summary", "limited_external_tool_supervised_pilot_bridge"
            ]
            for s in expected_sections:
                if s not in schema.get("required_sections", []):
                    errors.append(f"Schema missing required section: {s}")
            
            blocked = [
                "real_production_execution", "production_activation", "real_task_execution",
                "live_task_assignment", "live_worker_routing", "live_orchestration",
                "external_tool_invocation", "live_api_call", "network_access", "socket_connection",
                "credential_use", "secret_read", "environment_variable_read", "deployment",
                "worker_process_start", "automatic_execution", "queued_action_execution",
                "auto_approval", "approval_bypass", "actual_replay_execution", "full_workforce_activation"
            ]
            for b in blocked:
                if b not in schema.get("blocked_dry_run_modes", []):
                    errors.append(f"Schema missing blocked mode: {b}")
            
            if "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN" not in schema.get("required_confirmation_tokens", []):
                errors.append("Schema missing required confirmation token")
            if schema.get("single_task_limit") != 1:
                errors.append("Schema single task limit mismatch")
            
            checks = {
                "baseline_preserved": True, "external_actions_taken": False,
                "real_production_execution_performed": False, "production_activation_performed": False,
                "real_task_execution_performed": False, "live_task_assignment_performed": False,
                "live_worker_routing_performed": False, "live_orchestration_performed": False,
                "external_tool_invocation_performed": False, "live_api_call_performed": False,
                "network_access_performed": False, "socket_opened": False, "credentials_used": False,
                "secrets_read": False, "environment_read": False, "deployment_performed": False,
                "worker_processes_started": False, "repo_files_modified": False, "execution_authorized": False
            }
            for k, v in checks.items():
                if schema.get(k) != v:
                    errors.append(f"Schema safety boolean mismatch: {k}")

    # PART 10 — Default without token
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--first-supervised-production-dry-run", "--json"])
    if code != 0:
        errors.append(f"Default run failed: {stderr}")
    else:
        res = parse_json_output(stdout, "Default no-token run", errors)
        if res:
            bundle = res.get("first_supervised_production_dry_run_bundle")
            if not bundle:
                errors.append("Bundle missing in default output")
            else:
                gate = bundle.get("first_supervised_production_dry_run_approval_gate", {})
                if gate.get("gate_status") != "BLOCKED_PENDING_FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL":
                    errors.append("Default gate status mismatch")
                if gate.get("confirmation_token_valid") is not False:
                    errors.append("Default token should be invalid")
                if gate.get("local_dry_run_records_authorized") is not False:
                    errors.append("Default records should be unauthorized")
                
                blocks = [
                    ("single_controlled_task_dry_run_envelope", "envelope_status", "BLOCKED"),
                    ("dry_run_only_production_context_contract", "contract_status", "BLOCKED"),
                    ("human_preflight_approval_gate", "preflight_status", "BLOCKED"),
                    ("worker_task_simulation_contract", "simulation_status", "BLOCKED"),
                    ("external_action_denial_by_default", "denial_status", "BLOCKED"),
                    ("dry_run_rollback_quarantine_preview", "preview_status", "BLOCKED"),
                    ("dry_run_audit_proof", "audit_status", "BLOCKED"),
                    ("dry_run_ledger", "ledger_status", "BLOCKED"),
                    ("dry_run_readiness_summary", "readiness_status", "BLOCKED")
                ]
                for key, field, val in blocks:
                    if bundle.get(key, {}).get(field) != val:
                        errors.append(f"Default block mismatch: {key}.{field}")
                
                if bundle.get("dry_run_readiness_summary", {}).get("ready_for_limited_external_tool_supervised_pilot") is not False:
                    errors.append("Default summary ready flag mismatch")
                if bundle.get("limited_external_tool_supervised_pilot_bridge", {}).get("ready_for_limited_external_tool_supervised_pilot") is not False:
                    errors.append("Default bridge ready flag mismatch")
                
                checks = ["external_actions_taken", "real_production_execution_performed", "production_activation_performed", "real_task_execution_performed", "live_task_assignment_performed", "live_worker_routing_performed", "live_orchestration_performed", "external_tool_invocation_performed", "live_api_call_performed", "network_access_performed", "socket_opened", "credentials_used", "secrets_read", "environment_read", "deployment_performed", "worker_processes_started", "repo_files_modified", "execution_authorized"]
                for k in checks:
                    if bundle.get(k) is not False:
                        errors.append(f"Default safety boolean {k} should be False")

    # PART 11 — Valid token
    token = "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--first-supervised-production-dry-run", "--dry-run-confirm-token", token, "--json"])
    if code != 0:
        errors.append(f"Valid token run failed: {stderr}")
    else:
        res = parse_json_output(stdout, "Valid token run", errors)
        if res:
            bundle = res.get("first_supervised_production_dry_run_bundle")
            if bundle:
                gate = bundle.get("first_supervised_production_dry_run_approval_gate", {})
                if gate.get("gate_status") != "APPROVED_FOR_FIRST_SUPERVISED_PRODUCTION_DRY_RUN_RECORDS":
                    errors.append("Valid token gate status mismatch")
                if gate.get("confirmation_token_valid") is not True:
                    errors.append("Valid token should be valid")
                if gate.get("local_dry_run_records_authorized") is not True:
                    errors.append("Valid token records should be authorized")
                
                forbidden_auths = ["real_production_execution_authorized", "production_activation_authorized", "external_tool_invocation_authorized", "live_api_call_authorized", "network_access_authorized", "socket_access_authorized", "credential_use_authorized", "secret_read_authorized", "environment_read_authorized", "deployment_authorized"]
                for fa in forbidden_auths:
                    if gate.get(fa) is not False:
                        errors.append(f"Valid token authorized forbidden action: {fa}")
                
                if bundle.get("single_controlled_task_dry_run_envelope", {}).get("envelope_status") != "ENVELOPE_CREATED":
                    errors.append("Valid token envelope status mismatch")
                if bundle.get("dry_run_only_production_context_contract", {}).get("contract_status") != "CONTRACT_CREATED":
                    errors.append("Valid token contract status mismatch")
                if bundle.get("human_preflight_approval_gate", {}).get("preflight_status") != "PREFLIGHT_REQUIREMENT_CREATED":
                    errors.append("Valid token preflight status mismatch")
                if bundle.get("worker_task_simulation_contract", {}).get("simulation_status") != "SIMULATION_CONTRACT_CREATED":
                    errors.append("Valid token simulation status mismatch")
                if bundle.get("external_action_denial_by_default", {}).get("denial_status") != "EXTERNAL_ACTIONS_DENIED_BY_DEFAULT":
                    errors.append("Valid token denial status mismatch")
                if bundle.get("dry_run_rollback_quarantine_preview", {}).get("preview_status") != "ROLLBACK_QUARANTINE_PREVIEW_CREATED":
                    errors.append("Valid token rollback preview mismatch")
                if bundle.get("dry_run_audit_proof", {}).get("audit_status") != "PASS":
                    errors.append("Valid token audit status mismatch")
                if bundle.get("dry_run_ledger", {}).get("ledger_status") != "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_LEDGER":
                    errors.append("Valid token ledger status mismatch")
                if bundle.get("dry_run_readiness_summary", {}).get("ready_for_limited_external_tool_supervised_pilot") is not True:
                    errors.append("Valid token readiness flag mismatch")
                if bundle.get("limited_external_tool_supervised_pilot_bridge", {}).get("ready_for_limited_external_tool_supervised_pilot") is not True:
                    errors.append("Valid token bridge flag mismatch")
                
                audit = bundle.get("dry_run_audit_proof", {}).get("safety_checks", {})
                for k in audit:
                    if audit.get(k) is not True:
                        errors.append(f"Audit safety check failed: {k}")
                
                checks = ["external_actions_taken", "real_production_execution_performed", "production_activation_performed", "real_task_execution_performed", "live_task_assignment_performed", "live_worker_routing_performed", "live_orchestration_performed", "external_tool_invocation_performed", "live_api_call_performed", "network_access_performed", "socket_opened", "credentials_used", "secrets_read", "environment_read", "deployment_performed", "worker_processes_started", "repo_files_modified", "execution_authorized"]
                for k in checks:
                    if bundle.get(k) is not False:
                        errors.append(f"Valid token safety boolean {k} should be False")

    # PART 12 — Next layer command
    cmd_next = ["python3", "10_runtime/station_chief_runtime.py", "--command", "build limited external tool supervised pilot", "--first-supervised-production-dry-run", "--dry-run-confirm-token", token, "--json"]
    code, stdout, stderr = run_command(cmd_next)
    if code != 0:
        errors.append(f"Next layer command failed: {stderr}")
    else:
        res = parse_json_output(stdout, "Next layer command", errors)
        if res:
            bundle = res.get("first_supervised_production_dry_run_bundle", {})
            if bundle.get("limited_external_tool_supervised_pilot_bridge", {}).get("next_layer") != "Limited External Tool Supervised Pilot":
                errors.append("Next layer bridge name mismatch")
            if bundle.get("dry_run_readiness_summary", {}).get("next_layer") != "Limited External Tool Supervised Pilot":
                errors.append("Next layer summary name mismatch")
            if bundle.get("dry_run_readiness_summary", {}).get("readiness_status") != "READY_FOR_NEXT_LAYER":
                errors.append("Next layer readiness status mismatch")
            if bundle.get("external_actions_taken") is not False:
                errors.append("Next layer command took external actions")

    # PART 13 — Write dry-run
    with tempfile.TemporaryDirectory() as tmp_dir:
        code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-first-supervised-production-dry-run", tmp_dir, "--dry-run-confirm-token", token])
        if code != 0:
            errors.append(f"Write dry-run failed: {stderr}")
        else:
            res = parse_json_output(stdout, "Write dry-run", errors)
            if res:
                summary = res.get("first_supervised_production_dry_run_write_summary")
                if not summary:
                    errors.append("Write summary missing")
                else:
                    dry_run_dir = Path(summary.get("first_supervised_production_dry_run_dir"))
                    if not dry_run_dir.exists():
                        errors.append("Dry-run directory missing")
                    
                    files = ["first_supervised_production_dry_run_bundle.json", "first_supervised_production_dry_run_schema.json", "first_supervised_production_dry_run_approval_gate.json", "single_controlled_task_dry_run_envelope.json", "dry_run_only_production_context_contract.json", "human_preflight_approval_gate.json", "worker_task_simulation_contract.json", "external_action_denial_by_default.json", "dry_run_rollback_quarantine_preview.json", "dry_run_audit_proof.json", "dry_run_ledger.json", "dry_run_readiness_summary.json", "limited_external_tool_supervised_pilot_bridge.json", "first_supervised_production_dry_run_manifest.json"]
                    for f in files:
                        if not (dry_run_dir / f).exists():
                            errors.append(f"Dry-run file missing: {f}")
                    
                    mani_path = dry_run_dir / "first_supervised_production_dry_run_manifest.json"
                    if mani_path.exists():
                        mani = json.loads(mani_path.read_text())
                        if mani.get("first_supervised_production_dry_run_manifest_version") != "3.2.0":
                            errors.append("Manifest version mismatch")
                        if mani.get("runtime_version") != "3.2.0":
                            errors.append("Manifest runtime version mismatch")
                        if mani.get("status") != "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY":
                            errors.append("Manifest status mismatch")
                        if mani.get("baseline_preserved") is not True:
                            errors.append("Manifest baseline mismatch")

    # PART 14 — Artifact writing with registry
    with tempfile.TemporaryDirectory() as tmp_run_dir, tempfile.TemporaryDirectory() as tmp_reg_dir:
        cmd_art = ["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-artifacts", tmp_run_dir, "--registry-dir", tmp_reg_dir, "--first-supervised-production-dry-run", "--dry-run-confirm-token", token]
        code, stdout, stderr = run_command(cmd_art)
        if code != 0:
            errors.append(f"Write artifacts failed: {stderr}")
        else:
            res = parse_json_output(stdout, "Write artifacts", errors)
            if res:
                summary = res.get("artifact_write_summary")
                if not summary:
                    errors.append("Artifact summary missing")
                else:
                    if not summary.get("run_id", "").startswith("station-chief-v3-2-check-please-"):
                        errors.append("Run ID prefix mismatch")
                    if summary.get("registry_updated") is not True:
                        errors.append("Registry not updated")
                    
                    art_dir = Path(summary.get("artifact_dir"))
                    if not art_dir.exists():
                        errors.append("Artifact directory missing")
                    
                    mani_path = art_dir / "manifest.json"
                    if mani_path.exists():
                        mani = json.loads(mani_path.read_text())
                        if mani.get("artifact_type") != "station_chief_runtime_v3_2_artifacts":
                            errors.append("Artifact type mismatch")
                        if mani.get("runtime_version") != "3.2.0":
                            errors.append("Artifact runtime version mismatch")
                    
                    reg_path = Path(tmp_reg_dir) / "run_registry.json"
                    if reg_path.exists():
                        reg = json.loads(reg_path.read_text())
                        if reg.get("registry_version") != "3.2.0":
                            errors.append("Registry version mismatch")
                    
                    idx_path = Path(tmp_reg_dir) / "runtime_index.json"
                    if idx_path.exists():
                        idx = json.loads(idx_path.read_text())
                        if idx.get("index_version") != "3.2.0":
                            errors.append("Index version mismatch")

    # PART 15 — Regression commands
    reg_cmds = [
        ("--stable-release-manifest", "stable_release_manifest"),
        ("--command 'check please' --release-lock", "release_lock_bundle"),
        ("--command 'check please' --controlled-execution", "controlled_execution_bundle"),
        ("--command 'check please' --work-order-executor", "work_order_executor_bundle"),
        ("--command 'check please' --worker-hiring-registry", "worker_hiring_registry_bundle"),
        ("--command 'check please' --department-routing", "department_routing_bundle"),
        ("--command 'check please' --multi-agent-orchestration", "multi_agent_orchestration_bundle"),
        ("--command 'check please' --operator-console", "operator_console_bundle"),
        ("--command 'check please' --github-patch-hardening", "github_patch_hardening_bundle"),
        ("--command 'check please' --deployment-packaging", "deployment_packaging_bundle"),
        ("--command 'check please' --controlled-worker-execution", "controlled_worker_execution_bundle"),
        ("--command 'check please' --tool-permission-binding", "tool_permission_binding_bundle"),
        ("--command 'check please' --live-telemetry-abort", "live_execution_telemetry_abort_bundle"),
        ("--command 'check please' --post-run-audit-expansion", "post_run_audit_expansion_bundle"),
        ("--command 'check please' --multi-worker-sandbox-coordination", "multi_worker_sandbox_coordination_bundle"),
        ("--command 'check please' --controlled-external-tool-preview", "controlled_external_tool_adapter_preview_bundle"),
        ("--command 'check please' --permissioned-external-api-dry-run", "permissioned_external_api_dry_run_preview_bundle"),
        ("--command 'check please' --controlled-multi-worker-audit-replay-preview", "controlled_multi_worker_audit_replay_preview_bundle"),
        ("--command 'check please' --operator-approval-queue-enforcement", "operator_approval_queue_enforcement_bundle"),
        ("--command 'check please' --release-candidate-hardening", "release_candidate_hardening_bundle"),
        ("--command 'check please' --controlled-production-readiness-gate", "controlled_production_readiness_gate_bundle"),
        ("--command 'check please' --controlled-worker-hiring-activation-pilot", "controlled_worker_hiring_activation_pilot_bundle"),
        ("--command 'check please' --first-supervised-production-dry-run", "first_supervised_production_dry_run_bundle"),
        ("--command 'check please' --approval-handoff", "approval_handoff_packet")
    ]
    for cstr, key in reg_cmds:
        full_cmd = ["python3", "10_runtime/station_chief_runtime.py"] + cstr.split()
        if "--command" in full_cmd:
             # fix split for quoted command
             idx = full_cmd.index("--command")
             full_cmd[idx+1] = "check please"
             if "'check" in full_cmd:
                 full_cmd.remove("'check")
             if "please'" in full_cmd:
                 full_cmd.remove("please'")

        code, stdout, stderr = run_command(full_cmd)
        if code != 0:
            errors.append(f"Regression command failed: {cstr}")
        else:
            res = parse_json_output(stdout, cstr, errors)
            if res:
                if key == "stable_release_manifest":
                    if res.get("runtime_version") != "3.2.0":
                        errors.append(f"Regression {cstr} version mismatch")
                elif key not in res:
                    errors.append(f"Regression {cstr} missing bundle key {key}")
                else:
                    bundle = res.get(key)
                    if bundle and isinstance(bundle, dict):
                        if bundle.get("external_actions_taken") is True:
                             errors.append(f"Regression {cstr} took external actions in bundle")
                
                if res.get("external_actions_taken") is True:
                    errors.append(f"Regression {cstr} took external actions at top level")

    # PART 16 — README/report/skeleton content
    readme_path = "10_runtime/station_chief_runtime_readme.md"
    skel_path = "09_exports/station_chief_runtime_skeleton_report.md"
    v32_path = "09_exports/station_chief_runtime_v3_2_report.md"
    
    for p in [readme_path, skel_path, v32_path]:
        if Path(p).exists():
            content = Path(p).read_text()
            phrases = ["Station Chief Runtime upgraded to v3.2.0.", "First supervised production dry-run added.", "first supervised production dry-run schema", "first supervised production dry-run approval gate", "single controlled task dry-run envelope", "dry-run-only production context contract", "human preflight approval gate", "worker task simulation contract", "external action denial by default", "dry-run rollback and quarantine preview", "dry-run audit proof", "dry-run ledger", "dry-run readiness summary", "limited external tool supervised pilot bridge", "no real production execution", "no production activation", "no real task execution", "no live task assignment", "no live worker routing", "no live orchestration", "no external tool invocation", "no live API calls", "no credential use", "no secret reads", "no environment reads", "no network access", "no socket access", "no deployment"]
            for ph in phrases:
                if ph not in content:
                    errors.append(f"Phrase '{ph}' missing in {p}")
            
            negative = ["Explain that", "Include:", "List:", "Write:"]
            if p in [readme_path, skel_path]:
                for neg in negative:
                    if neg in content:
                        errors.append(f"Forbidden phrase '{neg}' found in {p}")

    # PART 17 — Forbidden implementation patterns
    forbidden_implementation = ["import requests", "from requests", "urllib.request", "import urllib.request", "os.system", "subprocess.run", "subprocess.Popen", "import subprocess", "pip install", "npm install", "API key"]
    runtime_modules = list(Path("10_runtime").glob("station_chief_*.py"))
    for rm_path in runtime_modules:
        content = rm_path.read_text()
        rm = str(rm_path)
        for fi in forbidden_implementation:
            if fi in content:
                errors.append(f"Forbidden pattern '{fi}' in {rm}")
        
        if "station_chief_first_supervised_production_dry_run.py" in rm:
            dangerous = ["eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver", "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway", "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref", "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"]
            for d in dangerous:
                if d in content:
                    errors.append(f"Dangerous pattern '{d}' in dry-run module")

    # PART 18 — Older validator delegation
    scripts_dir = Path(__file__).parent
    v_files = list(scripts_dir.glob("validate_station_chief_runtime_v*.py")) + [scripts_dir / "validate_station_chief_runtime_skeleton.py"]
    for vf in v_files:
        if "v3_2" in vf.name: continue
        if not vf.exists(): continue
        content = vf.read_text()
        if "validate_station_chief_runtime_v3_2.py" not in content or "runpy.run_path" not in content:
            errors.append(f"Validator {vf.name} missing delegation to v3.2")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("FAIL")
        sys.exit(1)
    else:
        print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.2 validator hotfix files.")
        print("PASS: Station Chief Runtime v3.2 valid.")

if __name__ == "__main__":
    main()
