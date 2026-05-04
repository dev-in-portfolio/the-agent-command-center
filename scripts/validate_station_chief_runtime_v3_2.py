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
        "10_runtime/station_chief_controlled_worker_hiring_activation_pilot.py",
        "10_runtime/station_chief_first_supervised_production_dry_run.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v3_2_report.md",
        "scripts/validate_station_chief_runtime_v3_2.py"
    ]
    
    for f in required_files:
        if not Path(f).exists():
            errors.append(f"Required file missing: {f}")
            
    runtime_content = Path("10_runtime/station_chief_runtime.py").read_text()
    runtime_required_strings = [
        'STATION_CHIEF_RUNTIME_VERSION = "3.2.0"',
        'attach_first_supervised_production_dry_run',
        'write_first_supervised_production_dry_run',
        '--first-supervised-production-dry-run-schema',
        '--first-supervised-production-dry-run',
        '--write-first-supervised-production-dry-run',
        '--dry-run-label',
        '--dry-run-confirm-token',
        '--dry-run-task-label',
        '--dry-run-production-context-label',
        '--dry-run-required-preflight-approver',
        '--dry-run-worker-label',
        '--dry-run-quarantine-label',
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
            
    dry_run_content = Path("10_runtime/station_chief_first_supervised_production_dry_run.py").read_text()
    dry_run_required_strings = [
        'FIRST_SUPERVISED_PRODUCTION_DRY_RUN_MODULE_VERSION = "3.2.0"',
        'FIRST_SUPERVISED_PRODUCTION_DRY_RUN_STATUS',
        'FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PHASE',
        'FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL_TOKEN',
        'canonical_json',
        'sha256_digest',
        'normalize_dry_run_label',
        'generate_first_supervised_production_dry_run_id',
        'create_first_supervised_production_dry_run_schema',
        'create_first_supervised_production_dry_run_approval_gate',
        'create_single_controlled_task_dry_run_envelope',
        'create_dry_run_only_production_context_contract',
        'create_human_preflight_approval_gate',
        'create_worker_task_simulation_contract',
        'create_external_action_denial_by_default',
        'create_dry_run_rollback_quarantine_preview',
        'create_dry_run_audit_proof',
        'create_dry_run_ledger',
        'create_dry_run_readiness_summary',
        'create_limited_external_tool_supervised_pilot_bridge',
        'create_first_supervised_production_dry_run_bundle'
    ]
    for s in dry_run_required_strings:
        if s not in dry_run_content:
            errors.append(f"Dry-run module missing string: {s}")
            
    adapter_content = Path("10_runtime/station_chief_adapters.py").read_text()
    adapter_required_strings = [
        'ADAPTER_MODULE_VERSION = "3.2.0"',
        'supports_first_supervised_production_dry_run',
        'first_supervised_production_dry_run_requires_specific_token',
        'real_production_execution_allowed',
        'production_activation_allowed',
        'real_task_execution_allowed',
        'live_task_assignment_allowed',
        'live_worker_routing_allowed',
        'live_orchestration_allowed',
        'external_tool_invocation_allowed',
        'live_api_call_allowed',
        'network_access_allowed',
        'socket_access_allowed',
        'credential_use_allowed',
        'secret_read_allowed',
        'environment_read_allowed',
        'YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN'
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
             
        if "station_chief_first_supervised_production_dry_run.py" in rm:
            pg_dangerous = [
                "eval(", "exec(", "compile(", "open(", "import socket", "from socket", "http.server", "socketserver",
                "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
                "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
                "__import__", "threading", "multiprocessing", "kill(", "terminate(", "getenv(", "os.getenv",
                "os.environ", "environ[", "datetime.now", "time.time"
            ]
            for s in pg_dangerous:
                if s in content:
                    errors.append(f"Dangerous code pattern '{s}' found in dry-run module")

    # Part 5 - Runtime Demo Checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"])
    if code != 0:
        errors.append(f"--demo failed with exit code {code}. Stderr: {stderr}")
    else:
        demo = parse_json_output(stdout, "--demo", errors)
        if demo:
            if demo.get("station_chief_runtime_version") != "3.2.0":
                errors.append(f"Demo version mismatch")
            if demo.get("runtime_status") != "first_supervised_production_dry_run":
                errors.append(f"Demo status mismatch")
            
            evidence = demo.get("evidence", {})
            required_evidence = {
                "baseline_preserved": True,
                "external_actions_taken": False,
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
                    errors.append(f"Evidence key '{k}' mismatch")

    # Part 6 - Fixture Tests
    for cmd_args in [["--fixture-test"], ["10_runtime/station_chief_fixture_tests.py"]]:
        if cmd_args[0] == "--fixture-test":
            full_cmd = ["python3", "10_runtime/station_chief_runtime.py"] + cmd_args
        else:
            full_cmd = ["python3"] + cmd_args
        code, stdout, stderr = run_command(full_cmd)
        if code != 0:
            errors.append(f"{' '.join(full_cmd)} failed")
        else:
            fix = parse_json_output(stdout, ' '.join(cmd_args), errors)
            if fix:
                if fix.get("fixture_test_status") != "PASS":
                    errors.append(f"{' '.join(cmd_args)}: status should be PASS")
                if fix.get("runtime_version") != "3.2.0":
                    errors.append(f"{' '.join(cmd_args)}: version mismatch")

    # Part 9 - Schema Checks
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--first-supervised-production-dry-run-schema"])
    if code != 0:
        errors.append(f"--first-supervised-production-dry-run-schema failed")
    else:
        schema = parse_json_output(stdout, "--first-supervised-production-dry-run-schema", errors)
        if schema:
            if schema.get("first_supervised_production_dry_run_schema_version") != "3.2.0":
                errors.append("Schema version mismatch")
            
            req_sections = schema.get("required_sections", [])
            expected_sections = [
                "first_supervised_production_dry_run_approval_gate", "single_controlled_task_dry_run_envelope",
                "dry_run_only_production_context_contract", "human_preflight_approval_gate",
                "worker_task_simulation_contract", "external_action_denial_by_default",
                "dry_run_rollback_quarantine_preview", "dry_run_audit_proof",
                "dry_run_ledger", "dry_run_readiness_summary", "limited_external_tool_supervised_pilot_bridge"
            ]
            for s in expected_sections:
                if s not in req_sections:
                    errors.append(f"Schema missing section: {s}")
            
            if schema.get("single_task_limit") != 1:
                errors.append("Schema task limit mismatch")

    # Part 10 - Default without token
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--first-supervised-production-dry-run", "--json"])
    if code != 0:
        errors.append(f"Default bundle run failed")
    else:
        res = parse_json_output(stdout, "Default bundle run", errors)
        if res:
            bundle = res.get("first_supervised_production_dry_run_bundle")
            if not bundle:
                errors.append("Bundle missing in default output")
            else:
                gate = bundle.get("first_supervised_production_dry_run_approval_gate", {})
                if gate.get("gate_status") != "BLOCKED_PENDING_FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL":
                    errors.append("Default: gate status mismatch")
                
                blocks = [
                    ("single_controlled_task_dry_run_envelope", "envelope_status", "BLOCKED"),
                    ("dry_run_only_production_context_contract", "contract_status", "BLOCKED"),
                    ("human_preflight_approval_gate", "preflight_status", "BLOCKED"),
                    ("worker_task_simulation_contract", "simulation_status", "BLOCKED"),
                    ("external_action_denial_by_default", "denial_status", "BLOCKED"),
                    ("dry_run_rollback_quarantine_preview", "preview_status", "BLOCKED"),
                    ("dry_run_audit_proof", "audit_status", "BLOCKED"),
                    ("dry_run_readiness_summary", "readiness_status", "BLOCKED")
                ]
                for key, field, val in blocks:
                    if bundle.get(key, {}).get(field) != val:
                        errors.append(f"Default: {key}.{field} mismatch")

    # Part 11 - Valid token
    code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--first-supervised-production-dry-run", "--dry-run-confirm-token", "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN", "--json"])
    if code != 0:
        errors.append(f"Valid token bundle run failed")
    else:
        res = parse_json_output(stdout, "Valid token run", errors)
        if res:
            bundle = res.get("first_supervised_production_dry_run_bundle")
            if bundle:
                if bundle.get("first_supervised_production_dry_run_approval_gate", {}).get("confirmation_token_valid") is not True:
                    errors.append("Valid token: token should be valid")
                if bundle.get("single_controlled_task_dry_run_envelope", {}).get("envelope_status") != "ENVELOPE_CREATED":
                    errors.append("Valid token: envelope status mismatch")
                if bundle.get("dry_run_audit_proof", {}).get("audit_status") != "PASS":
                    errors.append("Valid token: audit status mismatch")
                if bundle.get("dry_run_readiness_summary", {}).get("ready_for_limited_external_tool_supervised_pilot") is not True:
                    errors.append("Valid token: summary ready flag mismatch")

    # Part 15 - Write artifacts
    with tempfile.TemporaryDirectory() as tmp_dir:
        code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-first-supervised-production-dry-run", tmp_dir, "--dry-run-confirm-token", "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"])
        if code != 0:
            errors.append(f"Write dry-run failed")
        else:
            res = parse_json_output(stdout, "Write dry-run", errors)
            if res:
                summary = res.get("first_supervised_production_dry_run_write_summary")
                if not summary:
                    errors.append("Write summary missing")
                else:
                    mani_path = Path(summary.get("first_supervised_production_dry_run_dir")) / "first_supervised_production_dry_run_manifest.json"
                    if not mani_path.exists():
                        errors.append("Dry-run manifest missing")
                    else:
                        mani = json.loads(mani_path.read_text())
                        if mani.get("runtime_version") != "3.2.0":
                            errors.append("Manifest version mismatch")

    # Regression Checks
    with tempfile.TemporaryDirectory() as tmp_run_dir, tempfile.TemporaryDirectory() as tmp_reg_dir:
        code, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--write-artifacts", tmp_run_dir, "--registry-dir", tmp_reg_dir, "--first-supervised-production-dry-run", "--dry-run-confirm-token", "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"])
        if code == 0:
            res = parse_json_output(stdout, "Write artifacts with registry", errors)
            if res:
                summary = res.get("artifact_write_summary")
                if summary:
                    if not summary.get("run_id", "").startswith("station-chief-v3-2-check-please-"):
                        errors.append("Run ID prefix mismatch")
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

    # README/Report phrase checks
    for fpath in ["10_runtime/station_chief_runtime_readme.md", "09_exports/station_chief_runtime_skeleton_report.md", "09_exports/station_chief_runtime_v3_2_report.md"]:
        content = Path(fpath).read_text()
        if "Station Chief Runtime upgraded to v3.2.0." not in content:
            errors.append(f"{fpath} status missing")
        if "First supervised production dry-run added." not in content and "First Supervised Production Dry-Run added." not in content:
            errors.append(f"{fpath} layer title missing")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("FAIL")
        sys.exit(1)
    else:
        print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.2 runtime files.")
        print("PASS: Station Chief Runtime v3.2 valid.")

if __name__ == "__main__":
    main()
