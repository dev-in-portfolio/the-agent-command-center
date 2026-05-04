import json
import subprocess
import sys
import tempfile
import os
import shlex
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
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v3_1_report.md",
        "scripts/validate_station_chief_runtime_v3_1.py"
    ]
    
    for f in required_files:
        if not Path(f).exists():
            errors.append(f"Required file missing: {f}")
            
    runtime_content = Path("10_runtime/station_chief_runtime.py").read_text()
    runtime_required_strings = [
        'STATION_CHIEF_RUNTIME_VERSION = "3.1.0"',
        'attach_controlled_worker_hiring_activation_pilot',
        'write_controlled_worker_hiring_activation_pilot',
        '--worker-hiring-activation-pilot-schema',
        '--controlled-worker-hiring-activation-pilot',
        '--write-controlled-worker-hiring-activation-pilot',
        '--pilot-label',
        '--pilot-confirm-token',
        '--pilot-worker-limit',
        '--pilot-worker-label',
        '--pilot-required-supervisor',
        '--pilot-rollback-label',
        'controlled_worker_hiring_activation_pilot_bundle',
        'controlled_worker_hiring_activation_pilot_schema',
        'controlled_worker_hiring_activation_pilot_approval_gate',
        'pilot_worker_limit_contract',
        'worker_identity_activation_contract',
        'task_assignment_denial_by_default',
        'human_supervised_pilot_gate',
        'pilot_rollback_abort_preview',
        'pilot_audit_proof',
        'pilot_ledger',
        'pilot_readiness_summary',
        'first_supervised_production_dry_run_bridge'
    ]
    for s in runtime_required_strings:
        if s not in runtime_content:
            errors.append(f"Runtime script missing string: {s}")
            
    pilot_content = Path("10_runtime/station_chief_controlled_worker_hiring_activation_pilot.py").read_text()
    pilot_required_strings = [
        'CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_MODULE_VERSION = "3.1.0"',
        'CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_STATUS',
        'CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PHASE',
        'CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL_TOKEN',
        'canonical_json',
        'sha256_digest',
        'normalize_pilot_label',
        'generate_controlled_worker_hiring_activation_pilot_id',
        'create_controlled_worker_hiring_activation_pilot_schema',
        'create_controlled_worker_hiring_activation_pilot_approval_gate',
        'create_pilot_worker_limit_contract',
        'create_worker_identity_activation_contract',
        'create_task_assignment_denial_by_default',
        'create_human_supervised_pilot_gate',
        'create_pilot_rollback_abort_preview',
        'create_pilot_audit_proof',
        'create_pilot_ledger',
        'create_pilot_readiness_summary',
        'create_first_supervised_production_dry_run_bridge',
        'create_controlled_worker_hiring_activation_pilot_bundle'
    ]
    for s in pilot_required_strings:
        if s not in pilot_content:
            errors.append(f"Pilot module missing string: {s}")
            
    adapter_content = Path("10_runtime/station_chief_adapters.py").read_text()
    adapter_required_strings = [
        'ADAPTER_MODULE_VERSION = "3.1.0"',
        'supports_controlled_worker_hiring_activation_pilot',
        'controlled_worker_hiring_activation_pilot_requires_specific_token',
        'real_worker_hiring_allowed',
        'real_worker_activation_allowed',
        'worker_process_start_allowed',
        'live_task_assignment_allowed',
        'live_worker_routing_allowed',
        'live_orchestration_allowed',
        'YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT'
    ]
    for s in adapter_required_strings:
        if s not in adapter_content:
            errors.append(f"Adapter module missing string: {s}")
            
    forbidden_implementation = [
        "import requests", "from requests", "urllib.request", "os.system",
        "subprocess.run", "subprocess.Popen", "import subprocess", "pip install", "npm install"
    ]
    runtime_modules = [f for f in Path("10_runtime").glob("station_chief_*.py")]
    for rm_path in runtime_modules:
        content = rm_path.read_text()
        rm = str(rm_path)
        for fi in forbidden_implementation:
            if fi in content:
                errors.append(f"Forbidden implementation pattern '{fi}' found in {rm}")
        if "API key" in content and "API-key" not in content:
             errors.append(f"Forbidden string 'API key' found in {rm}")
             
        if "station_chief_controlled_worker_hiring_activation_pilot.py" in rm:
            pilot_dangerous = [
                "eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver",
                "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
                "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
                "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv",
                "os.environ", "environ[", "datetime.now", "time.time"
            ]
            for s in pilot_dangerous:
                if s in content:
                    errors.append(f"Dangerous code pattern '{s}' found in pilot module")

    # Part 5 - Runtime Demo Checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if code != 0:
        errors.append(f"--demo failed with exit code {code}. Stderr: {stderr}")
    else:
        demo = parse_json_output(stdout, "--demo", errors)
        if demo:
            if demo.get("station_chief_runtime_version") != "3.1.0":
                errors.append(f"Demo version mismatch: expected 3.1.0, got {demo.get('station_chief_runtime_version')}")
            if demo.get("runtime_status") != "controlled_worker_hiring_activation_pilot":
                errors.append(f"Demo status mismatch: expected controlled_worker_hiring_activation_pilot, got {demo.get('runtime_status')}")
            if demo.get("release_status") != "STABLE_LOCKED":
                errors.append(f"Demo release status mismatch: expected STABLE_LOCKED, got {demo.get('release_status')}")
            if demo.get("command_type") != "verification":
                errors.append(f"Demo command_type mismatch: expected verification, got {demo.get('command_type')}")
            
            evidence = demo.get("evidence", {})
            required_evidence = {
                "baseline_preserved": True,
                "external_actions_taken": False,
                "live_worker_agents_activated": False,
                "controlled_worker_hiring_activation_pilot_available": True,
                "controlled_worker_hiring_activation_pilot_preview_only": True,
                "controlled_worker_hiring_activation_pilot_requires_token": True,
                "pilot_worker_limit_maximum_is_three": True,
                "task_assignment_denied_by_default": True,
                "controlled_worker_hiring_activation_pilot_does_not_hire_real_workers": True,
                "controlled_worker_hiring_activation_pilot_does_not_activate_real_workers": True,
                "controlled_worker_hiring_activation_pilot_does_not_start_worker_processes": True,
                "controlled_worker_hiring_activation_pilot_does_not_assign_live_tasks": True,
                "controlled_worker_hiring_activation_pilot_does_not_route_live_workers": True,
                "controlled_worker_hiring_activation_pilot_does_not_perform_live_orchestration": True,
                "controlled_worker_hiring_activation_pilot_does_not_execute_production": True,
                "controlled_worker_hiring_activation_pilot_does_not_activate_production": True,
                "controlled_worker_hiring_activation_pilot_does_not_call_live_apis": True,
                "controlled_worker_hiring_activation_pilot_does_not_use_network_access": True,
                "controlled_worker_hiring_activation_pilot_does_not_open_sockets": True,
                "controlled_worker_hiring_activation_pilot_does_not_use_credentials": True,
                "controlled_worker_hiring_activation_pilot_does_not_read_secrets": True,
                "controlled_worker_hiring_activation_pilot_does_not_read_environment": True,
                "controlled_worker_hiring_activation_pilot_does_not_modify_repo_files": True,
                "first_supervised_production_dry_run_not_yet_active": True
            }
            for k, v in required_evidence.items():
                if evidence.get(k) != v:
                    errors.append(f"Evidence key '{k}' mismatch: expected {v}, got {evidence.get(k)}")

    # Part 6 - Fixture Tests
    for cmd_args in [["--fixture-test"], ["python3", "10_runtime/station_chief_fixture_tests.py"]]:
        if cmd_args[0] == "--fixture-test":
            full_cmd = ["python3", "10_runtime/station_chief_runtime.py"] + cmd_args
        else:
            full_cmd = cmd_args
        code, stdout, stderr = run_command(full_cmd)
        
        fix = parse_json_output(stdout, ' '.join(cmd_args), errors)
        if fix:
            if fix.get("fixture_test_status") != "PASS":
                errors.append(f"{' '.join(cmd_args)}: status should be PASS")
            if fix.get("runtime_version") != "3.1.0":
                errors.append(f"{' '.join(cmd_args)}: version should be 3.1.0")
            if fix.get("case_count") != 5 or fix.get("failed") != 0:
                errors.append(f"{' '.join(cmd_args)}: case count/failed mismatch")

    # Part 7 - Overlay List Regression
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-overlays"])
    if code != 0:
        errors.append(f"--list-overlays failed. Stderr: {stderr}")
    else:
        overlays = parse_json_output(stdout, "--list-overlays", errors)
        if overlays and isinstance(overlays, list):
            if len(overlays) != 8:
                errors.append(f"Expected exactly 8 overlays, got {len(overlays)}")
            for o in overlays:
                if not o.get("exists"):
                    errors.append(f"Overlay {o.get('id')} reported as not exists")
                if not o.get("preserves_locked_baseline"):
                    errors.append(f"Overlay {o.get('id')} does not preserve baseline")
                if "Devin O’Rourke" not in o.get("ownership_project_owner", ""):
                    errors.append(f"Overlay {o.get('id')} owner mismatch")

    # Part 8 - Adapter Checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-adapters"])
    if code != 0:
        errors.append(f"--list-adapters failed. Stderr: {stderr}")
    else:
        adapters = parse_json_output(stdout, "--list-adapters", errors)
        if adapters:
            if adapters.get("adapter_module_version") != "3.1.0":
                errors.append("Adapter module version mismatch")
            if adapters.get("supports_controlled_worker_hiring_activation_pilot") is not True:
                errors.append("Adapter list: pilot support missing")
            
            # Check false flags
            false_flags = [
                "real_worker_hiring_allowed", "real_worker_activation_allowed", "worker_process_start_allowed",
                "live_task_assignment_allowed", "live_worker_routing_allowed", "live_orchestration_allowed",
                "production_execution_allowed", "production_activation_allowed", "external_tool_invocation_allowed",
                "live_api_call_allowed", "network_access_allowed", "socket_access_allowed",
                "credential_use_allowed", "secret_read_allowed", "environment_read_allowed"
            ]
            for ff in false_flags:
                if adapters.get(ff) is not False:
                    errors.append(f"Adapter list: {ff} must be False")
            
            supported = adapters.get("supported_adapters", {})
            noop = supported.get("noop", {})
            if noop.get("supports_controlled_worker_hiring_activation_pilot") is not True:
                errors.append("noop adapter: pilot support missing")
            
            patch = supported.get("scoped_repo_patch", {})
            if patch.get("supports_controlled_worker_hiring_activation_pilot") is not False:
                errors.append("scoped_repo_patch: pilot support should be False")
            if patch.get("controlled_worker_hiring_activation_pilot_requires_separate_gate") is not True:
                errors.append("scoped_repo_patch: separate gate requirement missing")

    # Part 9 - Schema Checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--worker-hiring-activation-pilot-schema"])
    if code != 0:
        errors.append(f"--worker-hiring-activation-pilot-schema failed. Stderr: {stderr}")
    else:
        schema = parse_json_output(stdout, "--worker-hiring-activation-pilot-schema", errors)
        if schema:
            if schema.get("controlled_worker_hiring_activation_pilot_schema_version") != "3.1.0":
                errors.append("Schema version mismatch")
            if schema.get("schema_status") != "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY":
                errors.append("Schema status mismatch")
            
            req_sections = schema.get("required_sections", [])
            expected_sections = [
                "controlled_worker_hiring_activation_pilot_approval_gate", "pilot_worker_limit_contract",
                "worker_identity_activation_contract", "task_assignment_denial_by_default",
                "human_supervised_pilot_gate", "pilot_rollback_abort_preview", "pilot_audit_proof",
                "pilot_ledger", "pilot_readiness_summary", "first_supervised_production_dry_run_bridge"
            ]
            for s in expected_sections:
                if s not in req_sections:
                    errors.append(f"Schema missing required section: {s}")
            
            blocked_modes = schema.get("blocked_pilot_modes", [])
            expected_blocked = [
                "real_worker_hiring", "real_worker_activation", "worker_process_start",
                "live_task_assignment", "live_worker_routing", "live_orchestration",
                "production_execution", "production_activation", "live_api_call",
                "credential_use", "secret_read", "environment_variable_read"
            ]
            for bm in expected_blocked:
                if bm not in blocked_modes:
                    errors.append(f"Schema missing blocked mode: {bm}")
            
            if schema.get("pilot_worker_limit_min") != 1 or schema.get("pilot_worker_limit_max") != 3:
                errors.append("Schema worker limits mismatch")
            
            # Check schema false flags
            schema_false_flags = [
                "external_actions_taken", "real_worker_hiring_performed", "real_worker_activation_performed",
                "worker_processes_started", "live_task_assignment_performed", "live_worker_routing_performed",
                "live_orchestration_performed", "production_execution_performed", "production_activation_performed",
                "live_api_call_performed", "network_access_performed", "socket_opened",
                "credentials_used", "secrets_read", "environment_read", "repo_files_modified",
                "deployment_performed", "execution_authorized"
            ]
            for sff in schema_false_flags:
                if schema.get(sff) is not False:
                    errors.append(f"Schema: {sff} must be False")

    # Part 10 - Default Without Token
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--json"])
    if code != 0:
        errors.append(f"Default bundle run failed. Stderr: {stderr}")
    else:
        res = parse_json_output(stdout, "Default bundle run", errors)
        if res:
            bundle = res.get("controlled_worker_hiring_activation_pilot_bundle")
            if not bundle:
                errors.append("Bundle missing in default output")
            else:
                gate = bundle.get("controlled_worker_hiring_activation_pilot_approval_gate", {})
                if gate.get("gate_status") != "BLOCKED_PENDING_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL":
                    errors.append("Default: gate status should be BLOCKED")
                if gate.get("confirmation_token_valid") is not False:
                    errors.append("Default: token should be invalid")
                
                # Check all contracts blocked
                blocks = [
                    ("pilot_worker_limit_contract", "contract_status", "BLOCKED"),
                    ("worker_identity_activation_contract", "contract_status", "BLOCKED"),
                    ("task_assignment_denial_by_default", "denial_status", "BLOCKED"),
                    ("human_supervised_pilot_gate", "supervision_status", "BLOCKED"),
                    ("pilot_rollback_abort_preview", "preview_status", "BLOCKED"),
                    ("pilot_audit_proof", "audit_status", "BLOCKED"),
                    ("pilot_ledger", "ledger_status", "BLOCKED"),
                    ("pilot_readiness_summary", "readiness_status", "BLOCKED")
                ]
                for key, field, val in blocks:
                    if bundle.get(key, {}).get(field) != val:
                        errors.append(f"Default: {key}.{field} should be {val}, got {bundle.get(key, {}).get(field)}")
                
                summary = bundle.get("pilot_readiness_summary", {})
                if summary.get("ready_for_first_supervised_production_dry_run") is not False:
                    errors.append("Default: summary ready flag should be False")
                
                bridge = bundle.get("first_supervised_production_dry_run_bridge", {})
                if bridge.get("ready_for_first_supervised_production_dry_run") is not False:
                    errors.append("Default: bridge ready flag should be False")

    # Part 11 - Valid Token
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT", "--json"])
    if code != 0:
        errors.append(f"Valid token bundle run failed. Stderr: {stderr}")
    else:
        res = parse_json_output(stdout, "Valid token run", errors)
        if res:
            bundle = res.get("controlled_worker_hiring_activation_pilot_bundle")
            if bundle:
                gate = bundle.get("controlled_worker_hiring_activation_pilot_approval_gate", {})
                if gate.get("gate_status") != "APPROVED_FOR_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_RECORDS":
                    errors.append("Valid token: gate status should be APPROVED")
                if gate.get("confirmation_token_valid") is not True:
                    errors.append("Valid token: token should be valid")
                
                limit = bundle.get("pilot_worker_limit_contract", {})
                if limit.get("contract_status") != "PILOT_LIMIT_ACCEPTED":
                    errors.append("Valid token: limit contract should be ACCEPTED")
                if limit.get("pilot_worker_limit") != 1:
                    errors.append("Valid token: limit should be 1")
                if limit.get("maximum_allowed") != 3:
                    errors.append("Valid token: max allowed should be 3")
                
                identity = bundle.get("worker_identity_activation_contract", {})
                if identity.get("contract_status") != "IDENTITY_CONTRACTS_CREATED":
                    errors.append("Valid token: identity contract should be CREATED")
                if identity.get("worker_identity_count") != 1:
                    errors.append("Valid token: identity count should be 1")
                
                task = bundle.get("task_assignment_denial_by_default", {})
                if task.get("denial_status") != "TASK_ASSIGNMENT_DENIED_BY_DEFAULT":
                    errors.append("Valid token: task denial status should be DENIED_BY_DEFAULT")
                
                audit = bundle.get("pilot_audit_proof", {})
                if audit.get("audit_status") != "PASS":
                    errors.append("Valid token: audit status should be PASS")
                
                ledger = bundle.get("pilot_ledger", {})
                if ledger.get("ledger_status") != "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_LEDGER":
                    errors.append("Valid token: ledger status mismatch")
                
                summary = bundle.get("pilot_readiness_summary", {})
                if summary.get("ready_for_first_supervised_production_dry_run") is not True:
                    errors.append("Valid token: summary ready flag should be True")
                
                bridge = bundle.get("first_supervised_production_dry_run_bridge", {})
                if bridge.get("next_layer") != "First Supervised Production Dry-Run":
                    errors.append("Valid token: bridge next layer mismatch")
                if bridge.get("ready_for_first_supervised_production_dry_run") is not True:
                    errors.append("Valid token: bridge ready flag should be True")

    # Part 12 - Valid 2-worker pilot labels
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT", "--pilot-worker-limit", "2", "--pilot-worker-label", "pilot-worker-alpha", "--pilot-worker-label", "pilot-worker-beta", "--json"])
    if code != 0:
        errors.append(f"2-worker label run failed. Stderr: {stderr}")
    else:
        res = parse_json_output(stdout, "2-worker label run", errors)
        if res:
            bundle = res.get("controlled_worker_hiring_activation_pilot_bundle")
            if bundle:
                limit = bundle.get("pilot_worker_limit_contract", {})
                if limit.get("pilot_worker_limit") != 2:
                    errors.append("2-worker: limit mismatch")
                
                identity = bundle.get("worker_identity_activation_contract", {})
                if identity.get("worker_identity_count") != 2:
                    errors.append("2-worker: identity count mismatch")
                
                records = identity.get("worker_identity_records", [])
                labels = [r.get("worker_label") for r in records]
                if "pilot-worker-alpha" not in labels or "pilot-worker-beta" not in labels:
                    errors.append("2-worker: labels missing")
                
                for r in records:
                    if r.get("identity_status") != "CONTRACT_ONLY":
                        errors.append(f"2-worker: identity {r.get('worker_id')} status should be CONTRACT_ONLY")
                    if r.get("real_worker_created") is not False:
                        errors.append(f"2-worker: identity {r.get('worker_id')} real worker should be False")

    # Part 13 - Invalid Pilot Worker Limit
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT", "--pilot-worker-limit", "999", "--json"])
    if code != 0:
        errors.append(f"Invalid limit run failed. Stderr: {stderr}")
    else:
        res = parse_json_output(stdout, "Invalid limit run", errors)
        if res:
            bundle = res.get("controlled_worker_hiring_activation_pilot_bundle")
            if bundle:
                limit = bundle.get("pilot_worker_limit_contract", {})
                if limit.get("contract_status") != "BLOCKED":
                    errors.append("Invalid limit: status should be BLOCKED")
                if limit.get("limit_valid") is not False:
                    errors.append("Invalid limit: limit_valid should be False")
                
                identity = bundle.get("worker_identity_activation_contract", {})
                if identity.get("contract_status") != "BLOCKED":
                    errors.append("Invalid limit: identity contract should be BLOCKED")
                
                audit = bundle.get("pilot_audit_proof", {})
                if audit.get("audit_status") != "BLOCKED":
                    errors.append("Invalid limit: audit should be BLOCKED")

    # Part 14 - First Supervised Production Dry-Run bridge command
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "build first supervised production dry-run", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT", "--json"])
    if code != 0:
        errors.append(f"Bridge command run failed. Stderr: {stderr}")
    else:
        res = parse_json_output(stdout, "Bridge command run", errors)
        if res:
            bundle = res.get("controlled_worker_hiring_activation_pilot_bundle")
            if bundle:
                bridge = bundle.get("first_supervised_production_dry_run_bridge", {})
                if bridge.get("next_layer") != "First Supervised Production Dry-Run":
                    errors.append("Bridge command: next layer mismatch")
                if bridge.get("ready_for_first_supervised_production_dry_run") is not True:
                    errors.append("Bridge command: ready flag should be True")

    # Part 15 - Write controlled worker hiring activation pilot
    with tempfile.TemporaryDirectory() as tmp_pilot_dir:
        code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-controlled-worker-hiring-activation-pilot", tmp_pilot_dir, "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"])
        if code != 0:
            errors.append(f"Write pilot run failed. Stderr: {stderr}")
        else:
            res = parse_json_output(stdout, "Write pilot run", errors)
            if res:
                summary = res.get("controlled_worker_hiring_activation_pilot_write_summary")
                if not summary:
                    errors.append("Write summary missing in output")
                else:
                    pilot_dir = Path(summary.get("controlled_worker_hiring_activation_pilot_dir"))
                    if not pilot_dir.exists():
                        errors.append(f"Pilot dir {pilot_dir} does not exist")
                    
                    manifest_path = pilot_dir / "controlled_worker_hiring_activation_pilot_manifest.json"
                    if not manifest_path.exists():
                        errors.append("Pilot manifest missing")
                    else:
                        mani = json.loads(manifest_path.read_text())
                        if mani.get("controlled_worker_hiring_activation_pilot_manifest_version") != "3.1.0":
                            errors.append("Pilot manifest version mismatch")
                        if mani.get("status") != "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY":
                            errors.append("Pilot manifest status mismatch")
                        if mani.get("baseline_preserved") is not True:
                            errors.append("Pilot manifest baseline flag mismatch")

    # Part 16 - Artifact Writing with Registry
    with tempfile.TemporaryDirectory() as tmp_run_dir, tempfile.TemporaryDirectory() as tmp_reg_dir:
        code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-artifacts", tmp_run_dir, "--registry-dir", tmp_reg_dir, "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"])
        if code != 0:
            errors.append(f"Write artifacts run failed. Stderr: {stderr}")
        else:
            res = parse_json_output(stdout, "Write artifacts run", errors)
            if res:
                summary = res.get("artifact_write_summary")
                if not summary:
                    errors.append("Artifact summary missing in output")
                else:
                    if not summary.get("run_id", "").startswith("station-chief-v3-1-check-please-"):
                        errors.append(f"Run ID mismatch: {summary.get('run_id')}")
                    if summary.get("registry_updated") is not True:
                        errors.append("Registry not updated")
                    
                    artifact_dir = Path(summary.get("artifact_dir"))
                    manifest_path = artifact_dir / "manifest.json"
                    if not manifest_path.exists():
                        errors.append("Artifact manifest missing")
                    else:
                        mani = json.loads(manifest_path.read_text())
                        if mani.get("artifact_type") != "station_chief_runtime_v3_1_artifacts":
                            errors.append("Artifact type mismatch")
                        if mani.get("runtime_version") != "3.1.0":
                            errors.append("Artifact manifest version mismatch")
                        
                        v3_1_caps = [
                            "controlled_worker_hiring_activation_pilot_schema", "controlled_worker_hiring_activation_pilot_approval_gate",
                            "pilot_worker_limit_contract", "worker_identity_activation_contract", "task_assignment_denial_by_default",
                            "human_supervised_pilot_gate", "pilot_rollback_abort_preview", "pilot_audit_proof",
                            "pilot_ledger", "pilot_readiness_summary", "first_supervised_production_dry_run_bridge"
                        ]
                        for cap in v3_1_caps:
                            if mani.get(cap) is not True:
                                errors.append(f"Artifact manifest missing cap: {cap}")
                    
                    reg_path = Path(tmp_reg_dir) / "run_registry.json"
                    if not reg_path.exists():
                        errors.append("run_registry.json missing")
                    else:
                        reg = json.loads(reg_path.read_text())
                        if reg.get("registry_version") != "3.1.0":
                            errors.append("Registry version mismatch")
                    
                    idx_path = Path(tmp_reg_dir) / "runtime_index.json"
                    if not idx_path.exists():
                        errors.append("runtime_index.json missing")
                    else:
                        idx = json.loads(idx_path.read_text())
                        if idx.get("index_version") != "3.1.0":
                            errors.append("Index version mismatch")

    # Part 17 - Regression Commands
    regression_cmds = [
        ("--stable-release-manifest", "stable_release_manifest"),
        ("--command \"check please\" --release-lock", "release_lock_bundle"),
        ("--command \"check please\" --controlled-execution", "controlled_execution_bundle"),
        ("--command \"check please\" --work-order-executor", "work_order_executor_bundle"),
        ("--command \"check please\" --worker-hiring-registry", "worker_hiring_registry_bundle"),
        ("--command \"check please\" --department-routing", "department_routing_bundle"),
        ("--command \"check please\" --multi-agent-orchestration", "multi_agent_orchestration_bundle"),
        ("--command \"check please\" --operator-console", "operator_console_bundle"),
        ("--command \"check please\" --github-patch-hardening", "github_patch_hardening_bundle"),
        ("--command \"check please\" --deployment-packaging", "deployment_packaging_bundle"),
        ("--command \"check please\" --controlled-worker-execution", "controlled_worker_execution_bundle"),
        ("--command \"check please\" --tool-permission-binding", "tool_permission_binding_bundle"),
        ("--command \"check please\" --live-telemetry-abort", "live_execution_telemetry_abort_bundle"),
        ("--command \"check please\" --post-run-audit-expansion", "post_run_audit_expansion_bundle"),
        ("--command \"check please\" --multi-worker-sandbox-coordination", "multi_worker_sandbox_coordination_bundle"),
        ("--command \"check please\" --controlled-external-tool-preview", "controlled_external_tool_adapter_preview_bundle"),
        ("--command \"check please\" --permissioned-external-api-dry-run", "permissioned_external_api_dry_run_preview_bundle"),
        ("--command \"check please\" --controlled-multi-worker-audit-replay-preview", "controlled_multi_worker_audit_replay_preview_bundle"),
        ("--command \"check please\" --operator-approval-queue-enforcement", "operator_approval_queue_enforcement_bundle"),
        ("--command \"check please\" --release-candidate-hardening", "release_candidate_hardening_bundle"),
        ("--command \"check please\" --controlled-production-readiness-gate", "controlled_production_readiness_gate_bundle"),
        ("--command \"check please\" --controlled-worker-hiring-activation-pilot", "controlled_worker_hiring_activation_pilot_bundle"),
        ("--command \"check please\" --approval-handoff", "approval_handoff_packet")
    ]
    for cmd_str, bundle_key in regression_cmds:
        full_cmd = ["python3", "10_runtime/station_chief_runtime.py"] + shlex.split(cmd_str) + ["--json"]
        code, stdout, stderr = run_command(full_cmd)
        if code != 0:
            errors.append(f"Regression command {' '.join(full_cmd)} failed. Stderr: {stderr}")
        else:
            res = parse_json_output(stdout, cmd_str, errors)
            if res:
                if cmd_str == "--stable-release-manifest":
                    if res.get("runtime_version") != "3.1.0":
                        errors.append("Stable manifest version mismatch")
                else:
                    if bundle_key not in res:
                        errors.append(f"Regression {cmd_str}: bundle {bundle_key} missing")
                
                # Global safety checks for regressions
                if res.get("external_actions_taken", False) is not False:
                    errors.append(f"Regression {cmd_str}: external_actions_taken must be False")
                if res.get("production_execution_performed", False) is not False:
                    errors.append(f"Regression {cmd_str}: production_execution_performed must be False")

    # Part 18 - README/Report/Skeleton Content
    readme_path = Path("10_runtime/station_chief_runtime_readme.md")
    skeleton_report_path = Path("09_exports/station_chief_runtime_skeleton_report.md")
    v3_1_report_path = Path("09_exports/station_chief_runtime_v3_1_report.md")

    required_phrases = [
        "Station Chief Runtime upgraded to v3.1.0.",
        "Controlled worker hiring activation pilot added.",
        "controlled worker hiring activation pilot schema",
        "controlled worker hiring activation pilot approval gate",
        "one-to-three worker pilot limit contract",
        "worker identity activation contract",
        "task assignment denial by default",
        "human-supervised pilot gate",
        "pilot rollback and abort preview",
        "pilot audit proof",
        "pilot ledger",
        "pilot readiness summary",
        "first supervised production dry-run bridge",
        "- no real worker hiring",
        "- no real worker activation",
        "- no worker process starts",
        "- no live task assignment",
        "- no live worker routing",
        "- no live orchestration",
        "- no production execution",
        "- no production activation",
        "- no live API calls",
        "- no credential use",
        "- no secret reads",
        "- no environment reads",
        "- no network access",
        "- no socket access",
        "- no deployment",
        "- no shell command execution",
        "- no arbitrary code execution",
        "- no full workforce activation"
    ]

    for p in [readme_path, skeleton_report_path, v3_1_report_path]:
        content = p.read_text()
        for phrase in required_phrases:
            if phrase not in content:
                errors.append(f"Required phrase missing in {p}: {phrase}")
        
        # Skeleton and README must not contain scaffold
        if p != v3_1_report_path:
            for scaffold in ["Explain that", "Include:", "List:", "Write:"]:
                if scaffold in content:
                    errors.append(f"Scaffold wording '{scaffold}' remains in {p}")

    doctrine_para = "Station Chief Runtime v3.1.0 adds Controlled Worker Hiring Activation Pilot without real worker hiring, real worker activation, worker process starts, live task assignment, live worker routing, live orchestration, production execution, production activation, queued action execution, automatic approval, approval bypass, actual replay execution, external tool replay, live API calls, credential use, secret reads, environment reads, network access, socket access, deployment, shell command execution, or broad workforce activation."
    if doctrine_para not in readme_path.read_text():
        errors.append("Doctrine paragraph missing in README")
    
    if "Next recommended step: build first supervised production dry-run." not in readme_path.read_text():
        errors.append("Next step missing in README")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("FAIL")
        sys.exit(1)
    else:
        print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.1 validator hotfix files.")
        print("PASS: Station Chief Runtime v3.1 valid.")

if __name__ == "__main__":
    main()
