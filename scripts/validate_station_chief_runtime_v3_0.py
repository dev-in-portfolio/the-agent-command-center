import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_command(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(command)}")
        print(result.stderr)
        return ""
    return result.stdout

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
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v3_0_report.md",
        "scripts/validate_station_chief_runtime_v3_0.py"
    ]
    
    for f in required_files:
        if not Path(f).exists():
            errors.append(f"Required file missing: {f}")
            
    runtime_content = Path("10_runtime/station_chief_runtime.py").read_text()
    runtime_required_strings = [
        'STATION_CHIEF_RUNTIME_VERSION = "3.0.0"',
        'attach_controlled_production_readiness_gate',
        'write_controlled_production_readiness_gate',
        '--production-readiness-gate-schema',
        '--controlled-production-readiness-gate',
        '--write-controlled-production-readiness-gate',
        'controlled_production_readiness_gate_bundle',
        'controlled_production_readiness_gate_schema',
        'controlled_production_readiness_gate_approval_gate',
        'production_activation_denial_by_default',
        'final_human_approval_requirement',
        'production_capability_manifest',
        'supervised_pilot_eligibility_contract',
        'production_rollback_kill_switch_preview',
        'production_readiness_audit_proof',
        'production_readiness_ledger',
        'production_readiness_summary',
        'controlled_worker_hiring_activation_pilot_bridge',
        'controlled_production_readiness_gate_preview_only',
        'controlled_production_readiness_gate_requires_token',
        'production_activation_denied_by_default',
        'controlled_production_readiness_gate_does_not_execute_production',
        'controlled_production_readiness_gate_does_not_activate_production',
        'controlled_production_readiness_gate_does_not_hire_real_workers',
        'controlled_production_readiness_gate_does_not_activate_real_workers',
        'controlled_production_readiness_gate_does_not_route_live_workers',
        'controlled_production_readiness_gate_does_not_perform_live_orchestration',
        'controlled_production_readiness_gate_does_not_execute_queued_actions',
        'controlled_production_readiness_gate_does_not_auto_approve',
        'controlled_production_readiness_gate_does_not_bypass_approval',
        'controlled_production_readiness_gate_does_not_execute_actual_replay',
        'controlled_production_readiness_gate_does_not_replay_worker_actions',
        'controlled_production_readiness_gate_does_not_replay_external_tools',
        'controlled_production_readiness_gate_does_not_call_live_apis',
        'controlled_production_readiness_gate_does_not_use_network_access',
        'controlled_production_readiness_gate_does_not_open_sockets',
        'controlled_production_readiness_gate_does_not_use_credentials',
        'controlled_production_readiness_gate_does_not_read_secrets',
        'controlled_production_readiness_gate_does_not_read_environment',
        'controlled_production_readiness_gate_does_not_modify_repo_files'
    ]
    for s in runtime_required_strings:
        if s not in runtime_content:
            errors.append(f"Runtime script missing string: {s}")
            
    pg_content = Path("10_runtime/station_chief_controlled_production_readiness_gate.py").read_text()
    pg_required_strings = [
        'CONTROLLED_PRODUCTION_READINESS_GATE_MODULE_VERSION = "3.0.0"',
        'CONTROLLED_PRODUCTION_READINESS_GATE_STATUS',
        'CONTROLLED_PRODUCTION_READINESS_GATE_PHASE',
        'CONTROLLED_PRODUCTION_READINESS_GATE_APPROVAL_TOKEN',
        'canonical_json',
        'sha256_digest',
        'normalize_production_gate_label',
        'generate_controlled_production_readiness_gate_id',
        'create_controlled_production_readiness_gate_schema',
        'create_controlled_production_readiness_gate_approval_gate',
        'create_production_activation_denial_by_default',
        'create_final_human_approval_requirement',
        'create_production_capability_manifest',
        'create_supervised_pilot_eligibility_contract',
        'create_production_rollback_kill_switch_preview',
        'create_production_readiness_audit_proof',
        'create_production_readiness_ledger',
        'create_production_readiness_summary',
        'create_controlled_worker_hiring_activation_pilot_bridge',
        'create_controlled_production_readiness_gate_bundle',
        'socket_opened',
        'environment_read',
        'socket_access_authorized',
        'environment_read_authorized',
        'socket_connection',
        'environment_variable_read'
    ]
    for s in pg_required_strings:
        if s not in pg_content:
            errors.append(f"Prod gate module missing string: {s}")
            
    adapter_content = Path("10_runtime/station_chief_adapters.py").read_text()
    adapter_required_strings = [
        'ADAPTER_MODULE_VERSION = "3.0.0"',
        'supports_controlled_production_readiness_gate',
        'controlled_production_readiness_gate_requires_specific_token',
        'production_execution_allowed',
        'production_activation_allowed',
        'real_worker_hiring_allowed',
        'real_worker_activation_allowed',
        'live_worker_routing_allowed',
        'live_orchestration_allowed',
        'controlled_production_readiness_gate_requires_separate_gate',
        'YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE',
        'socket_access_allowed',
        'environment_read_allowed'
    ]
    for s in adapter_required_strings:
        if s not in adapter_content:
            errors.append(f"Adapter module missing string: {s}")
            
    # Targeted forbidden implementation checks
    forbidden_implementation = [
        "import requests", "from requests", "urllib.request", "os.system",
        "subprocess.run", "subprocess.Popen", "import subprocess", "pip install", "npm install"
    ]
    runtime_modules = [
        "10_runtime/station_chief_runtime.py",
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
        "10_runtime/station_chief_controlled_production_readiness_gate.py"
    ]
    for rm in runtime_modules:
        content = Path(rm).read_text()
        for fi in forbidden_implementation:
            if fi in content:
                errors.append(f"Forbidden implementation pattern '{fi}' found in {rm}")
        if "API key" in content and "API-key" not in content:
             errors.append(f"Forbidden string 'API key' found in {rm}")
             
    pg_dangerous = [
        "eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver",
        "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
        "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv",
        "os.environ", "environ[", "datetime.now", "time.time"
    ]
    for s in pg_dangerous:
        if s in pg_content:
            errors.append(f"Dangerous code pattern '{s}' found in prod gate module")
            
    # Drifted keys check
    drifted_keys = [
        "sock_opened", "env_read", "sock_access_authorized", "env_read_authorized",
        "sock_connection", "env_var_read", "sock_access_allowed", "env_read_allowed",
        "no_sock_opened", "no_env_read"
    ]
    for rm in runtime_modules:
        content = Path(rm).read_text()
        for dk in drifted_keys:
            if dk in content:
                errors.append(f"Drifted contract key '{dk}' remains in {rm}")

    demo_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if not demo_output:
        errors.append("--demo failed")
    else:
        demo = json.loads(demo_output)
        evidence = demo.get("evidence", {})
        if evidence.get("controlled_production_readiness_gate_does_not_open_sockets") is not True:
            errors.append("Evidence: socket protection missing")
        if evidence.get("controlled_production_readiness_gate_does_not_read_environment") is not True:
            errors.append("Evidence: environment protection missing")
            
    schema_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--production-readiness-gate-schema"])
    if not schema_output:
        errors.append("--production-readiness-gate-schema failed")
    else:
        schema = json.loads(schema_output)
        if schema.get("socket_opened") is not False:
            errors.append("Schema: socket_opened must be False")
        if schema.get("environment_read") is not False:
            errors.append("Schema: environment_read must be False")
        blocked = schema.get("blocked_gate_modes", [])
        if "socket_connection" not in blocked:
            errors.append("Schema: socket_connection must be blocked")
        if "environment_variable_read" not in blocked:
            errors.append("Schema: environment_variable_read must be blocked")
            
    bundle_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-production-readiness-gate", "--production-gate-confirm-token", "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"])
    if not bundle_output:
        errors.append("Bundle check failed")
    else:
        res = json.loads(bundle_output)
        bundle = res.get("controlled_production_readiness_gate_bundle", {})
        gate = bundle.get("controlled_production_readiness_gate_approval_gate", {})
        if gate.get("socket_access_authorized") is not False:
            errors.append("Approval gate: socket_access_authorized must be False")
        if gate.get("environment_read_authorized") is not False:
            errors.append("Approval gate: environment_read_authorized must be False")
            
        audit = bundle.get("production_readiness_audit_proof", {})
        if audit.get("socket_opened") is not False:
            errors.append("Audit: socket_opened must be False")
        if audit.get("environment_read") is not False:
            errors.append("Audit: environment_read must be False")
        checks = audit.get("safety_checks", {})
        if checks.get("no_socket_opened") is not True:
            errors.append("Audit checks: no_socket_opened must be True")
        if checks.get("no_environment_read") is not True:
            errors.append("Audit checks: no_environment_read must be True")
            
        summary = bundle.get("production_readiness_summary", {})
        if summary.get("socket_opened") is not False:
            errors.append("Summary: socket_opened must be False")
            
        bridge = bundle.get("controlled_worker_hiring_activation_pilot_bridge", {})
        if bridge.get("socket_opened") is not False:
            errors.append("Bridge: socket_opened must be False")

    adapter_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-adapters"])
    if not adapter_output:
        errors.append("--list-adapters failed")
    else:
        adapters = json.loads(adapter_output)
        if adapters.get("socket_access_allowed") is not False:
            errors.append("Adapters: socket_access_allowed must be False")
        if adapters.get("environment_read_allowed") is not False:
            errors.append("Adapters: environment_read_allowed must be False")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("FAIL")
        sys.exit(1)
    else:
        print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.0 runtime files.")
        print("PASS: Station Chief Runtime v3.0 valid.")

if __name__ == "__main__":
    main()
