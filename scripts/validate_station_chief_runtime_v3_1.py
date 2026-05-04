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
        "10_runtime/station_chief_controlled_production_readiness_gate.py",
        "10_runtime/station_chief_controlled_worker_hiring_activation_pilot.py"
    ]
    for rm in runtime_modules:
        content = Path(rm).read_text()
        for fi in forbidden_implementation:
            if fi in content:
                errors.append(f"Forbidden implementation pattern '{fi}' found in {rm}")
        if "API key" in content and "API-key" not in content:
             errors.append(f"Forbidden string 'API key' found in {rm}")
             
    pilot_dangerous = [
        "eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver",
        "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
        "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv",
        "os.environ", "environ[", "datetime.now", "time.time"
    ]
    for s in pilot_dangerous:
        if s in pilot_content:
            errors.append(f"Dangerous code pattern '{s}' found in pilot module")
            
    demo_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if not demo_output:
        errors.append("--demo failed")
    else:
        demo = json.loads(demo_output)
        if demo.get("station_chief_runtime_version") != "3.1.0":
            errors.append("Demo version mismatch")
        if demo.get("runtime_status") != "controlled_worker_hiring_activation_pilot":
            errors.append("Demo status mismatch")
        evidence = demo.get("evidence", {})
        if evidence.get("controlled_worker_hiring_activation_pilot_available") is not True:
            errors.append("Evidence: pilot missing")
        if evidence.get("pilot_worker_limit_maximum_is_three") is not True:
            errors.append("Evidence: pilot limit check missing")
        if evidence.get("task_assignment_denied_by_default") is not True:
            errors.append("Evidence: task denial missing")
            
    fixture_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--fixture-test"])
    if not fixture_output:
        errors.append("--fixture-test failed")
    else:
        fix = json.loads(fixture_output)
        if fix.get("fixture_test_status") != "PASS":
            errors.append("Fixture tests failed")
        if fix.get("runtime_version") != "3.1.0":
            errors.append("Fixture version mismatch")
            
    schema_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--worker-hiring-activation-pilot-schema"])
    if not schema_output:
        errors.append("--worker-hiring-activation-pilot-schema failed")
    else:
        schema = json.loads(schema_output)
        if schema.get("controlled_worker_hiring_activation_pilot_schema_version") != "3.1.0":
            errors.append("Schema version mismatch")
        sections = schema.get("required_sections", [])
        if "pilot_worker_limit_contract" not in sections:
            errors.append("Schema missing limit section")
        if "first_supervised_production_dry_run_bridge" not in sections:
            errors.append("Schema missing bridge section")
            
    bundle_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot"])
    if not bundle_output:
        errors.append("Default bundle check failed")
    else:
        res = json.loads(bundle_output)
        bundle = res.get("controlled_worker_hiring_activation_pilot_bundle", {})
        gate = bundle.get("controlled_worker_hiring_activation_pilot_approval_gate", {})
        if gate.get("gate_status") != "BLOCKED_PENDING_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL":
            errors.append("Bundle gate should be blocked without token")
            
    token_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"])
    if not token_output:
        errors.append("Token bundle check failed")
    else:
        res = json.loads(token_output)
        bundle = res.get("controlled_worker_hiring_activation_pilot_bundle", {})
        audit = bundle.get("pilot_audit_proof", {})
        if audit.get("audit_status") != "PASS":
            errors.append("Audit status should be PASS with token")
        summary = bundle.get("pilot_readiness_summary", {})
        if summary.get("ready_for_first_supervised_production_dry_run") is not True:
            errors.append("Pilot readiness summary mismatch")
            
    label_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-worker-hiring-activation-pilot", "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT", "--pilot-worker-limit", "2", "--pilot-worker-label", "pilot-worker-alpha", "--pilot-worker-label", "pilot-worker-beta"])
    if not label_output:
        errors.append("Label check failed")
    else:
        res = json.loads(label_output)
        bundle = res.get("controlled_worker_hiring_activation_pilot_bundle", {})
        identity = bundle.get("worker_identity_activation_contract", {})
        if identity.get("worker_identity_count") != 2:
            errors.append("Worker identity count mismatch")
        labels = [r["worker_label"] for r in identity.get("worker_identity_records", [])]
        if "pilot-worker-alpha" not in labels or "pilot-worker-beta" not in labels:
            errors.append("Worker labels missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        write_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-controlled-worker-hiring-activation-pilot", tmpdir, "--pilot-confirm-token", "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"])
        if not write_output:
            errors.append("--write-controlled-worker-hiring-activation-pilot failed")
        else:
            wres = json.loads(write_output)
            if "controlled_worker_hiring_activation_pilot_write_summary" not in wres:
                errors.append("Write summary missing in output")
                
    readme_content = Path("10_runtime/station_chief_runtime_readme.md").read_text()
    if "Station Chief Runtime upgraded to v3.1.0." not in readme_content:
        errors.append("README status mismatch")
        
    v3_1_report_content = Path("09_exports/station_chief_runtime_v3_1_report.md").read_text()
    if "Station Chief Runtime v3.1.0 Report" not in v3_1_report_content:
        errors.append("v3.1 report title mismatch")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("FAIL")
        sys.exit(1)
    else:
        print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.1 runtime files.")
        print("PASS: Station Chief Runtime v3.1 valid.")

if __name__ == "__main__":
    main()
