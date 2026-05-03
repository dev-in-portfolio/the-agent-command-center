import json
import subprocess
import sys
import tempfile
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
        '--production-gate-label',
        '--production-gate-confirm-token',
        '--production-gate-required-approver',
        '--production-gate-capability',
        '--production-gate-pilot-label',
        '--production-gate-pilot-worker-limit',
        '--production-gate-rollback-label',
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
        'create_controlled_production_readiness_gate_bundle'
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
        'YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE'
    ]
    for s in adapter_required_strings:
        if s not in adapter_content:
            errors.append(f"Adapter module missing string: {s}")
            
    forbidden_strings = ["requests", "urllib.request", "os.system", "pip install", "npm install", "live API", "API key", "import subprocess"]
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
        for fs in forbidden_strings:
            if fs in content:
                # Allow hyphenated versions in comments/docs
                if f"{fs}-" not in content and f"-{fs}" not in content:
                    errors.append(f"Forbidden string '{fs}' found in {rm}")
                    
    pg_forbidden = [
        "eval(", "exec(", "compile(", "open(", "socket", "http.server", "socketserver",
        "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
        "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv",
        "environ", "datetime.now", "time.time"
    ]
    for s in pg_forbidden:
        if s in pg_content:
            errors.append(f"Forbidden string '{s}' found in prod gate module")
            
    demo_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if not demo_output:
        errors.append("--demo failed")
    else:
        demo = json.loads(demo_output)
        if demo.get("station_chief_runtime_version") != "3.0.0":
            errors.append("Demo version mismatch")
        if demo.get("runtime_status") != "controlled_production_readiness_gate":
            errors.append("Demo status mismatch")
        if demo.get("release_status") != "STABLE_LOCKED":
            errors.append("Demo release status mismatch")
        if demo.get("command_type") != "verification":
            errors.append("Demo command type mismatch")
        evidence = demo.get("evidence", {})
        if evidence.get("baseline_preserved") is not True:
            errors.append("Demo baseline not preserved")
        if evidence.get("external_actions_taken") is not False:
            errors.append("Demo external actions taken")
        if evidence.get("controlled_production_readiness_gate_available") is not True:
            errors.append("Demo prod gate not available")
        if evidence.get("controlled_production_readiness_gate_preview_only") is not True:
            errors.append("Demo prod gate not preview only")
        if evidence.get("controlled_production_readiness_gate_requires_token") is not True:
            errors.append("Demo prod gate does not require token")
        if evidence.get("production_activation_denied_by_default") is not True:
            errors.append("Demo prod activation not denied")
            
    fixture_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--fixture-test"])
    if not fixture_output:
        errors.append("--fixture-test failed")
    else:
        fix = json.loads(fixture_output)
        if fix.get("fixture_test_status") != "PASS":
            errors.append("Fixture tests failed")
        if fix.get("runtime_version") != "3.0.0":
            errors.append("Fixture version mismatch")
        if fix.get("case_count") != 5:
            errors.append("Fixture case count mismatch")
        if fix.get("failed") != 0:
            errors.append("Fixture failed count mismatch")
            
    overlay_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-overlays"])
    if not overlay_output:
        errors.append("--list-overlays failed")
    else:
        overlays = json.loads(overlay_output)
        if len(overlays) != 8:
            errors.append("Overlay count mismatch")
        for o in overlays:
            if o.get("exists") is not True:
                errors.append(f"Overlay {o.get('id')} missing")
            if o.get("preserves_locked_baseline") is not True:
                errors.append(f"Overlay {o.get('id')} does not preserve baseline")
            if "Devin O’Rourke" not in o.get("ownership_project_owner", ""):
                errors.append(f"Overlay {o.get('id')} ownership mismatch")
                
    adapter_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-adapters"])
    if not adapter_output:
        errors.append("--list-adapters failed")
    else:
        adapters = json.loads(adapter_output)
        if adapters.get("adapter_module_version") != "3.0.0":
            errors.append("Adapter version mismatch")
        if adapters.get("supports_controlled_production_readiness_gate") is not True:
            errors.append("Adapters missing prod gate support")
        noop = adapters.get("supported_adapters", {}).get("noop", {})
        if noop.get("supports_controlled_production_readiness_gate") is not True:
            errors.append("Noop missing prod gate support")
        scoped = adapters.get("supported_adapters", {}).get("scoped_repo_patch", {})
        if scoped.get("supports_controlled_production_readiness_gate") is not False:
            errors.append("Scoped repo patch should not support prod gate directly")
            
    schema_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--production-readiness-gate-schema"])
    if not schema_output:
        errors.append("--production-readiness-gate-schema failed")
    else:
        schema = json.loads(schema_output)
        if schema.get("controlled_production_readiness_gate_schema_version") != "3.0.0":
            errors.append("Schema version mismatch")
        if schema.get("schema_status") != "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY":
            errors.append("Schema status mismatch")
        sections = schema.get("required_sections", [])
        if "controlled_production_readiness_gate_approval_gate" not in sections:
            errors.append("Schema missing approval gate section")
        if "production_readiness_summary" not in sections:
            errors.append("Schema missing summary section")
            
    bundle_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-production-readiness-gate"])
    if not bundle_output:
        errors.append("Default bundle check failed")
    else:
        bundle_res = json.loads(bundle_output)
        bundle = bundle_res.get("controlled_production_readiness_gate_bundle", {})
        if bundle.get("controlled_production_readiness_gate_bundle_version") != "3.0.0":
            errors.append("Bundle version mismatch")
        gate = bundle.get("controlled_production_readiness_gate_approval_gate", {})
        if gate.get("gate_status") != "BLOCKED_PENDING_CONTROLLED_PRODUCTION_READINESS_GATE_APPROVAL":
            errors.append("Bundle gate should be blocked without token")
        if gate.get("confirmation_token_valid") is not False:
            errors.append("Bundle gate token should be invalid")
            
    token_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--controlled-production-readiness-gate", "--production-gate-confirm-token", "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"])
    if not token_output:
        errors.append("Token bundle check failed")
    else:
        token_res = json.loads(token_output)
        bundle = token_res.get("controlled_production_readiness_gate_bundle", {})
        gate = bundle.get("controlled_production_readiness_gate_approval_gate", {})
        if gate.get("gate_status") != "APPROVED_FOR_CONTROLLED_PRODUCTION_READINESS_GATE_RECORDS":
            errors.append("Bundle gate should be approved with token")
        audit = bundle.get("production_readiness_audit_proof", {})
        if audit.get("audit_status") != "PASS":
            errors.append("Audit status should be PASS with token")
            
    with tempfile.TemporaryDirectory() as tmpdir:
        write_output = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-controlled-production-readiness-gate", tmpdir, "--production-gate-confirm-token", "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"])
        if not write_output:
            errors.append("--write-controlled-production-readiness-gate failed")
        else:
            wres = json.loads(write_output)
            if "controlled_production_readiness_gate_write_summary" not in wres:
                errors.append("Write summary missing in output")
            wdir = wres.get("controlled_production_readiness_gate_write_summary", {}).get("controlled_production_readiness_gate_dir")
            if not wdir or not Path(wdir).exists():
                errors.append("Prod gate directory missing")
            manifest_path = Path(wdir) / "controlled_production_readiness_gate_manifest.json"
            if not manifest_path.exists():
                errors.append("Prod gate manifest missing")
            else:
                m = json.loads(manifest_path.read_text())
                if m.get("runtime_version") != "3.0.0":
                    errors.append("Manifest runtime version mismatch")
                if m.get("status") != "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY":
                    errors.append("Manifest status mismatch")
                    
    readme_content = Path("10_runtime/station_chief_runtime_readme.md").read_text()
    if "Station Chief Runtime upgraded to v3.0.0." not in readme_content:
        errors.append("README status mismatch")
    if "controlled production readiness gate added" not in readme_content.lower():
        errors.append("README purpose mismatch")
        
    skeleton_report_content = Path("09_exports/station_chief_runtime_skeleton_report.md").read_text()
    if "Station Chief Runtime upgraded to v3.0.0." not in skeleton_report_content:
        errors.append("Skeleton report status mismatch")
        
    v3_report_content = Path("09_exports/station_chief_runtime_v3_0_report.md").read_text()
    if "Station Chief Runtime v3.0.0 Report" not in v3_report_content:
        errors.append("v3.0 report title mismatch")
        
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
