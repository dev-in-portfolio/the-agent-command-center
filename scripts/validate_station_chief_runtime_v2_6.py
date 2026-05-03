#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def fail(msg):
    print("FAIL")
    print(msg)
    sys.exit(1)

def require_true(condition, msg):
    if not condition:
        fail(msg)

def check_file_content(path, *strings, not_strings=None):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for s in strings:
        require_true(s in content, f"Missing '{s}' in {path}")
    if not_strings:
        for s in not_strings:
            require_true(s not in content, f"Found forbidden '{s}' in {path}")
            
def check_forbidden_strings(path):
    forbidden = [
        "requests", "urllib.request", "os.system", "pip install", "npm install",
        "API key", "import subprocess"
    ]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        import re
        for fbd in forbidden:
            require_true(fbd not in content, f"Found forbidden '{fbd}' in {path}")

def check_api_dry_run_forbidden(path):
    forbidden = [
        "eval(", "exec(", "compile(", "open(", "import socket", "http.server", "socketserver",
        "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
        "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", "os.getenv", "os.environ"
    ]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        for fbd in forbidden:
            require_true(fbd not in content, f"Found forbidden '{fbd}' in {path}")

def main():
    if Path("agent-command-center").exists():
        os.chdir("agent-command-center")
    
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
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v2_6_report.md",
        "scripts/validate_station_chief_runtime_v2_6.py"
    ]
    for f in required_files:
        require_true(Path(f).exists(), f"File missing: {f}")

    check_file_content("10_runtime/station_chief_runtime.py",
        'STATION_CHIEF_RUNTIME_VERSION = "2.6.0"',
        'attach_permissioned_external_api_dry_run_preview',
        'write_permissioned_external_api_dry_run_preview',
        '--external-api-dry-run-schema',
        '--permissioned-external-api-dry-run',
        '--write-permissioned-external-api-dry-run',
        '--external-api-label',
        '--external-api-endpoint-id',
        '--external-api-confirm-token',
        '--external-api-requested-endpoint',
        '--external-api-method',
        '--external-api-path-template',
        '--external-api-request-payload-json',
        '--external-api-credential-label',
        '--external-api-fixture-payload-json',
        'permissioned_external_api_dry_run_preview_bundle',
        'permissioned_external_api_dry_run_preview_schema',
        'external_api_dry_run_approval_gate',
        'api_endpoint_preview_registry',
        'request_envelope_validation',
        'credential_absence_proof',
        'outbound_call_prevention_proof',
        'dry_run_response_fixture_contract',
        'external_api_audit_proof',
        'external_api_dry_run_ledger',
        'external_api_dry_run_readiness_summary',
        'controlled_multi_worker_audit_replay_preview_readiness_bridge',
        'permissioned_external_api_dry_run_preview_only',
        'permissioned_external_api_dry_run_preview_requires_token',
        'permissioned_external_api_dry_run_does_not_call_live_apis',
        'permissioned_external_api_dry_run_does_not_use_network_access',
        'permissioned_external_api_dry_run_does_not_open_sockets',
        'permissioned_external_api_dry_run_does_not_use_credentials',
        'permissioned_external_api_dry_run_does_not_read_secrets',
        'permissioned_external_api_dry_run_does_not_read_environment',
        'permissioned_external_api_dry_run_does_not_modify_repo_files'
    )
    
    check_file_content("10_runtime/station_chief_permissioned_external_api_dry_run_preview.py",
        'PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_MODULE_VERSION = "2.6.0"',
        'PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_STATUS',
        'PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_PHASE',
        'PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_APPROVAL_TOKEN',
        'def canonical_json',
        'def sha256_digest',
        'def normalize_api_label',
        'def generate_external_api_dry_run_preview_id',
        'def create_permissioned_external_api_dry_run_preview_schema',
        'def create_external_api_dry_run_approval_gate',
        'def create_api_endpoint_preview_registry',
        'def create_request_envelope_validation',
        'def create_credential_absence_proof',
        'def create_outbound_call_prevention_proof',
        'def create_dry_run_response_fixture_contract',
        'def create_external_api_audit_proof',
        'def create_external_api_dry_run_ledger',
        'def create_external_api_dry_run_readiness_summary',
        'def create_controlled_multi_worker_audit_replay_preview_readiness_bridge',
        'def create_permissioned_external_api_dry_run_preview_bundle'
    )
    
    check_file_content("10_runtime/station_chief_adapters.py",
        'ADAPTER_MODULE_VERSION = "2.6.0"',
        '"supports_permissioned_external_api_dry_run_preview"',
        '"permissioned_external_api_dry_run_preview_requires_specific_token"',
        '"live_api_call_allowed": False',
        '"network_access_allowed": False',
        '"socket_access_allowed": False',
        '"credential_use_allowed": False',
        '"secret_read_allowed": False',
        '"environment_read_allowed": False',
        '"permissioned_external_api_dry_run_preview_requires_separate_gate": True',
        'YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW'
    )
    
    check_file_content("10_runtime/station_chief_runtime_readme.md",
        "Station Chief Runtime upgraded to v2.6.0.",
        "Permissioned external API dry-run preview added.",
        "permissioned external API dry-run preview schema",
        "external API dry-run approval gate",
        "API endpoint preview registry",
        "request envelope validation",
        "credential absence proof",
        "outbound call prevention proof",
        "dry-run response fixture contract",
        "external API audit proof",
        "external API dry-run ledger",
        "external API dry-run readiness summary",
        "controlled multi-worker audit replay preview readiness bridge",
        "no live API calls",
        "no credential use",
        "no secret reads",
        "no environment reads",
        "no network access",
        "no socket access",
        "no external tool invocation",
        "no shell command execution",
        "no arbitrary code execution",
        "no repo mutation",
        "no deployment",
        "Station Chief Runtime v2.6.0 adds Permissioned External API Dry-Run Preview without live API execution, credential use, secret reads, environment reads, network access, socket access, external tool invocation, deployment, or broad execution",
        not_strings=["Explain that", "Include:", "List:", "Write:"]
    )
    
    check_file_content("09_exports/station_chief_runtime_skeleton_report.md",
        "Station Chief Runtime upgraded to v2.6.0.",
        "Permissioned external API dry-run preview added.",
        "permissioned external API dry-run preview schema",
        "external API dry-run approval gate",
        "API endpoint preview registry",
        "request envelope validation",
        "credential absence proof",
        "outbound call prevention proof",
        "dry-run response fixture contract",
        "external API audit proof",
        "external API dry-run ledger",
        "external API dry-run readiness summary",
        "controlled multi-worker audit replay preview readiness bridge",
        "no live API calls",
        "no credential use",
        "no secret reads",
        "no environment reads",
        "no network access",
        "no socket access",
        "no external tool invocation",
        "no shell command execution",
        "no arbitrary code execution",
        "no repo mutation",
        "no deployment",
        not_strings=["Explain that", "Include:", "List:", "Write:"]
    )

    check_file_content("09_exports/station_chief_runtime_v2_6_report.md",
        "Station Chief Runtime v2.6.0 Report",
        "Station Chief Runtime upgraded to v2.6.0. Locked 175-family baseline preserved. Permissioned external API dry-run preview added.",
        "permissioned external API dry-run preview schema",
        "external API dry-run approval gate",
        "API endpoint preview registry",
        "request envelope validation",
        "credential absence proof",
        "outbound call prevention proof",
        "dry-run response fixture contract",
        "external API audit proof",
        "external API dry-run ledger",
        "external API dry-run readiness summary",
        "controlled multi-worker audit replay preview readiness bridge",
        "no baseline mutation",
        "no Devinization overlay mutation",
        "no live API calls",
        "no credential use",
        "no secret reads",
        "no environment reads",
        "no network access",
        "no socket access",
        "no external tool invocation",
        "no shell command execution",
        "no arbitrary code execution",
        "no full workforce animation",
        "no repo mutation",
        "Station Chief Runtime v2.6.0 adds Permissioned External API Dry-Run Preview without live API execution, credential use, secret reads, environment reads, network access, socket access, external tool invocation, deployment, or broad execution",
        "Next recommended build step"
    )

    modules_to_check = [
        "10_runtime/station_chief_runtime.py"
    ]
    for mod in modules_to_check:
        check_forbidden_strings(mod)
        
    check_api_dry_run_forbidden("10_runtime/station_chief_permissioned_external_api_dry_run_preview.py")

    cmds_to_run = [
        'python3 10_runtime/station_chief_runtime.py --demo',
        'python3 10_runtime/station_chief_runtime.py --fixture-test',
        'python3 10_runtime/station_chief_fixture_tests.py',
        'python3 10_runtime/station_chief_runtime.py --command "check please" --json',
        'python3 10_runtime/station_chief_runtime.py --command "build controlled multi-worker audit replay preview" --brief',
        'python3 10_runtime/station_chief_runtime.py --list-overlays',
        'python3 10_runtime/station_chief_runtime.py --list-adapters',
        'python3 10_runtime/station_chief_runtime.py --list-execution-profiles',
        'python3 10_runtime/station_chief_runtime.py --list-controlled-execution-profiles',
        'python3 10_runtime/station_chief_runtime.py --work-order-schema',
        'python3 10_runtime/station_chief_runtime.py --worker-role-schema',
        'python3 10_runtime/station_chief_runtime.py --department-routing-schema',
        'python3 10_runtime/station_chief_runtime.py --orchestration-schema',
        'python3 10_runtime/station_chief_runtime.py --operator-console-schema',
        'python3 10_runtime/station_chief_runtime.py --patch-hardening-schema',
        'python3 10_runtime/station_chief_runtime.py --deployment-artifact-schema',
        'python3 10_runtime/station_chief_runtime.py --controlled-worker-schema',
        'python3 10_runtime/station_chief_runtime.py --tool-permission-schema',
        'python3 10_runtime/station_chief_runtime.py --telemetry-abort-schema',
        'python3 10_runtime/station_chief_runtime.py --post-run-audit-schema',
        'python3 10_runtime/station_chief_runtime.py --multi-worker-coordination-schema',
        'python3 10_runtime/station_chief_runtime.py --external-tool-preview-schema',
        'python3 10_runtime/station_chief_runtime.py --external-api-dry-run-schema',
        'python3 10_runtime/station_chief_runtime.py --command "check please" --simulate-adapter'
    ]
    for c in cmds_to_run:
        res = run_cmd(c)
        require_true(res.returncode == 0, f"Command failed: {c}\n{res.stderr}")

    res_demo = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --demo').stdout)
    require_true(res_demo["station_chief_runtime_version"] == "2.6.0", "demo runtime version != 2.6.0")
    require_true(res_demo["runtime_status"] == "permissioned_external_api_dry_run_preview", "demo status mismatch")
    require_true(res_demo["release_status"] == "STABLE_LOCKED", "demo release status != STABLE_LOCKED")
    require_true(res_demo["command_type"] == "verification", "demo command type mismatch")
    ev = res_demo["evidence"]
    require_true(ev.get("baseline_preserved") == True, "baseline_preserved")
    require_true(ev.get("external_actions_taken") == False, "external_actions_taken")
    require_true(ev.get("live_worker_agents_activated") == False, "live_worker_agents_activated")
    require_true(ev.get("permissioned_external_api_dry_run_preview_available") == True, "dry_run_available")
    require_true(ev.get("permissioned_external_api_dry_run_preview_only") == True, "dry_run_only")
    require_true(ev.get("permissioned_external_api_dry_run_preview_requires_token") == True, "dry_run_requires_token")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_call_live_apis") == True, "does_not_call_live_apis")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_use_network_access") == True, "no_network")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_open_sockets") == True, "no_sockets")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_use_credentials") == True, "no_creds")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_read_secrets") == True, "no_secrets")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_read_environment") == True, "no_env")
    require_true(ev.get("permissioned_external_api_dry_run_does_not_modify_repo_files") == True, "no_modify_repo")
    require_true(ev.get("controlled_multi_worker_audit_replay_preview_not_yet_active") == True, "controlled_multi_not_yet")

    res_fix = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --fixture-test').stdout)
    require_true(res_fix["fixture_test_status"] == "PASS", "fixture_test_status")
    require_true(res_fix["runtime_version"] == "2.6.0", "fixture runtime version")
    require_true(res_fix["case_count"] == 5, "fixture case count")
    require_true(res_fix["failed"] == 0, "fixture failed")

    res_ov = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-overlays').stdout)
    require_true(len(res_ov) == 8, "exactly 8 overlays")
    for ov in res_ov:
        require_true(ov.get("exists") == True, "every overlay exists")
        require_true(ov.get("preserves_locked_baseline") == True, "baseline preserved")
        require_true("Devin O’Rourke" in ov.get("ownership_project_owner", ""), "ownership mismatch")

    res_ad = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-adapters').stdout)
    require_true(res_ad["adapter_module_version"] == "2.6.0", "adapter module version")
    require_true(res_ad.get("supports_permissioned_external_api_dry_run_preview") == True, "ad flag")
    require_true(res_ad.get("permissioned_external_api_dry_run_preview_requires_specific_token") == True, "ad flag2")
    require_true(res_ad.get("live_api_call_allowed") == False, "ad flag3")
    require_true(res_ad.get("network_access_allowed") == False, "ad flag4")
    require_true(res_ad.get("socket_access_allowed") == False, "ad flag5")
    require_true(res_ad.get("credential_use_allowed") == False, "ad flag6")
    require_true(res_ad.get("secret_read_allowed") == False, "ad flag7")
    require_true(res_ad.get("environment_read_allowed") == False, "ad flag8")
    sa = res_ad["supported_adapters"]
    require_true(sa["noop"]["supports_permissioned_external_api_dry_run_preview"] == True, "noop flag")
    require_true(sa["scoped_repo_patch"]["supports_permissioned_external_api_dry_run_preview"] == False, "repo patch flag")
    require_true(sa["scoped_repo_patch"]["permissioned_external_api_dry_run_preview_requires_separate_gate"] == True, "repo patch flag2")

    res_sch = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --external-api-dry-run-schema').stdout)
    require_true(res_sch["permissioned_external_api_dry_run_preview_schema_version"] == "2.6.0", "sch v")
    require_true(res_sch["schema_status"] == "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY", "sch st")
    req_sec = res_sch["required_sections"]
    require_true("external_api_dry_run_approval_gate" in req_sec, "sec")
    require_true("api_endpoint_preview_registry" in req_sec, "sec")
    require_true("request_envelope_validation" in req_sec, "sec")
    require_true("credential_absence_proof" in req_sec, "sec")
    require_true("outbound_call_prevention_proof" in req_sec, "sec")
    require_true("dry_run_response_fixture_contract" in req_sec, "sec")
    require_true("external_api_audit_proof" in req_sec, "sec")
    require_true("external_api_dry_run_ledger" in req_sec, "sec")
    require_true("external_api_dry_run_readiness_summary" in req_sec, "sec")
    require_true("controlled_multi_worker_audit_replay_preview_readiness_bridge" in req_sec, "sec")
    all_dm = res_sch["allowed_dry_run_modes"]
    require_true("local_api_dry_run_preview" in all_dm, "dm")
    require_true("approved_api_dry_run_records" in all_dm, "dm")
    blk_dm = res_sch["blocked_dry_run_modes"]
    require_true("live_external_api_execution" in blk_dm, "bdm")
    require_true("real_network_request" in blk_dm, "bdm")
    require_true("socket_connection" in blk_dm, "bdm")
    require_true("credential_use" in blk_dm, "bdm")
    require_true("secret_read" in blk_dm, "bdm")
    require_true("environment_variable_read" in blk_dm, "bdm")
    require_true("YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW" in res_sch["required_confirmation_tokens"], "tok")
    require_true(res_sch["baseline_preserved"] == True, "base")
    require_true(res_sch["external_actions_taken"] == False, "ea")
    require_true(res_sch["live_api_call_performed"] == False, "la")
    require_true(res_sch["network_access_performed"] == False, "na")
    require_true(res_sch["socket_opened"] == False, "so")
    require_true(res_sch["credentials_used"] == False, "cu")
    require_true(res_sch["secrets_read"] == False, "sr")
    require_true(res_sch["environment_read"] == False, "er")
    require_true(res_sch["repo_files_modified"] == False, "rf")
    require_true(res_sch["deployment_performed"] == False, "dp")
    require_true(res_sch["execution_authorized"] == False, "ea")

    # 13. Default without token
    res_def = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --json').stdout)
    require_true("permissioned_external_api_dry_run_preview_bundle" in res_def, "bundle")
    bundle = res_def["permissioned_external_api_dry_run_preview_bundle"]
    require_true(bundle["permissioned_external_api_dry_run_preview_bundle_version"] == "2.6.0", "v")
    require_true(res_def["external_api_dry_run_approval_gate"]["gate_status"] == "BLOCKED_PENDING_EXTERNAL_API_DRY_RUN_APPROVAL", "gate")
    require_true(res_def["external_api_dry_run_approval_gate"]["confirmation_token_valid"] == False, "tok val")
    require_true(res_def["api_endpoint_preview_registry"]["registry_status"] == "BLOCKED", "reg st")
    require_true(res_def["request_envelope_validation"]["validation_status"] == "BLOCKED", "req st")
    require_true(res_def["credential_absence_proof"]["proof_status"] == "BLOCKED", "cred st")
    require_true(res_def["outbound_call_prevention_proof"]["proof_status"] == "BLOCKED", "out st")
    require_true(res_def["dry_run_response_fixture_contract"]["contract_status"] == "BLOCKED", "fix st")
    require_true(res_def["external_api_audit_proof"]["audit_status"] == "BLOCKED", "aud st")
    require_true(res_def["external_api_dry_run_readiness_summary"]["readiness_status"] == "BLOCKED", "read st")
    require_true(bundle["external_actions_taken"] == False, "ea")
    require_true(bundle["live_api_call_performed"] == False, "la")
    require_true(bundle["network_access_performed"] == False, "na")
    require_true(bundle["socket_opened"] == False, "so")
    require_true(bundle["credentials_used"] == False, "cu")
    require_true(bundle["secrets_read"] == False, "sr")
    require_true(bundle["environment_read"] == False, "er")
    require_true(bundle["repo_files_modified"] == False, "rf")
    require_true(bundle["execution_authorized"] == False, "ea2")

    # 14. With valid token
    res_tok = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --json').stdout)
    require_true(res_tok["external_api_dry_run_approval_gate"]["gate_status"] == "APPROVED_FOR_PERMISSIONED_EXTERNAL_API_DRY_RUN_RECORDS", "gate2")
    require_true(res_tok["external_api_dry_run_approval_gate"]["confirmation_token_valid"] == True, "tok val2")
    require_true(res_tok["api_endpoint_preview_registry"]["registry_status"] == "REGISTRY_CREATED", "reg st2")
    require_true(res_tok["request_envelope_validation"]["validation_status"] == "PASS", "req st2")
    require_true(res_tok["credential_absence_proof"]["proof_status"] == "PROOF_CREATED", "cred st2")
    require_true(res_tok["outbound_call_prevention_proof"]["proof_status"] == "PROOF_CREATED", "out st2")
    require_true(res_tok["dry_run_response_fixture_contract"]["contract_status"] == "FIXTURE_CONTRACT_CREATED", "fix st2")
    require_true(res_tok["external_api_audit_proof"]["audit_status"] == "PASS", "aud st2")
    require_true(res_tok["external_api_dry_run_ledger"]["ledger_status"] == "PERMISSIONED_EXTERNAL_API_DRY_RUN_LEDGER", "ledg st2")
    require_true(res_tok["external_api_dry_run_readiness_summary"]["ready_for_controlled_multi_worker_audit_replay_preview"] == True, "read2")
    require_true(res_tok["controlled_multi_worker_audit_replay_preview_readiness_bridge"]["next_layer"] == "Controlled Multi-Worker Audit Replay Preview", "br")
    require_true(res_tok["controlled_multi_worker_audit_replay_preview_readiness_bridge"]["ready_for_controlled_multi_worker_audit_replay_preview"] == True, "br2")

    # 15. Unsafe request payload
    res_uns = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --external-api-request-payload-json \'{"bad":"api_key=123"}\' --json').stdout)
    require_true(res_uns["request_envelope_validation"]["validation_status"] == "BLOCKED", "req uns")
    require_true(len(res_uns["request_envelope_validation"]["blocked_payload_indicators"]) > 0, "req ind")
    require_true(res_uns["outbound_call_prevention_proof"]["proof_status"] == "BLOCKED", "out uns")
    require_true(res_uns["external_api_audit_proof"]["audit_status"] == "BLOCKED", "aud uns")
    require_true(res_uns["external_api_dry_run_readiness_summary"]["readiness_status"] == "BLOCKED", "read uns")

    # 16. Command for next layer
    res_nxt = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "build controlled multi-worker audit replay preview" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --json').stdout)
    require_true(res_nxt["controlled_multi_worker_audit_replay_preview_readiness_bridge"]["next_layer"] == "Controlled Multi-Worker Audit Replay Preview", "nxt")
    require_true(res_nxt["controlled_multi_worker_audit_replay_preview_readiness_bridge"]["ready_for_controlled_multi_worker_audit_replay_preview"] == True, "nxt2")
    require_true(res_nxt["external_api_dry_run_readiness_summary"]["next_layer"] == "Controlled Multi-Worker Audit Replay Preview", "nxt3")
    require_true(res_nxt["external_api_dry_run_readiness_summary"]["readiness_status"] == "READY_FOR_NEXT_LAYER", "nxt4")
    require_true(res_nxt["external_api_audit_proof"]["audit_status"] == "PASS", "nxt5")

    # 17. Write artifacts
    with tempfile.TemporaryDirectory() as td:
        res_wr = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-permissioned-external-api-dry-run {td} --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --json').stdout)
        require_true("permissioned_external_api_dry_run_preview_write_summary" in res_wr, "wr sum")
        pdir = res_wr["permissioned_external_api_dry_run_preview_write_summary"]["permissioned_external_api_dry_run_preview_dir"]
        require_true(Path(pdir).exists(), "pdir")
        fw = res_wr["permissioned_external_api_dry_run_preview_write_summary"]["files_written"]
        req_fw = [
            "permissioned_external_api_dry_run_preview_bundle.json",
            "permissioned_external_api_dry_run_preview_schema.json",
            "external_api_dry_run_approval_gate.json",
            "api_endpoint_preview_registry.json",
            "request_envelope_validation.json",
            "credential_absence_proof.json",
            "outbound_call_prevention_proof.json",
            "dry_run_response_fixture_contract.json",
            "external_api_audit_proof.json",
            "external_api_dry_run_ledger.json",
            "external_api_dry_run_readiness_summary.json",
            "controlled_multi_worker_audit_replay_preview_readiness_bridge.json",
            "permissioned_external_api_dry_run_preview_manifest.json"
        ]
        for r in req_fw:
            require_true(r in fw, f"r {r}")
        man = json.loads((Path(pdir) / "permissioned_external_api_dry_run_preview_manifest.json").read_text())
        require_true(man["runtime_version"] == "2.6.0", "man v")
        require_true(man["status"] == "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY", "man st")

    # 18. Artifact writing with registry
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "runs"
        reg_dir = Path(td) / "registry"
        res_ar = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts {run_dir} --registry-dir {reg_dir} --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --json').stdout)
        require_true("artifact_write_summary" in res_ar, "ar sum")
        rid = res_ar["artifact_write_summary"]["run_id"]
        require_true(rid.startswith("station-chief-v2-6-check-please-"), "rid str")
        adir = res_ar["artifact_write_summary"]["artifact_dir"]
        require_true(Path(adir).exists(), "adir")
        require_true(res_ar["artifact_write_summary"]["registry_updated"] == True, "reg up")
        man = json.loads((Path(adir) / "manifest.json").read_text())
        require_true(man["artifact_type"] == "station_chief_runtime_v2_6_artifacts", "art typ")
        require_true(man["runtime_version"] == "2.6.0", "art v")
        require_true(man.get("permissioned_external_api_dry_run_preview_schema") == True, "m 1")
        reg_ix = json.loads((reg_dir / "runtime_index.json").read_text())
        require_true(reg_ix["index_version"] == "2.6.0", "reg ix")

    # 19. Regression
    regressions = [
        ('--stable-release-manifest', 'stable_release_manifest', 'runtime_version', '2.6.0'),
        ('--release-lock', 'release_lock_bundle', None, None),
        ('--controlled-execution', 'controlled_execution_bundle', None, None),
        ('--work-order-executor', 'work_order_executor_bundle', None, None),
        ('--worker-hiring-registry', 'worker_hiring_registry_bundle', None, None),
        ('--department-routing', 'department_routing_bundle', None, None),
        ('--multi-agent-orchestration', 'multi_agent_orchestration_bundle', None, None),
        ('--operator-console', 'operator_console_bundle', None, None),
        ('--github-patch-hardening', 'github_patch_hardening_bundle', None, None),
        ('--deployment-packaging', 'deployment_packaging_bundle', None, None),
        ('--controlled-worker-execution', 'controlled_worker_execution_bundle', None, None),
        ('--tool-permission-binding', 'tool_permission_binding_bundle', None, None),
        ('--live-telemetry-abort', 'live_execution_telemetry_abort_bundle', None, None),
        ('--post-run-audit-expansion', 'post_run_audit_expansion_bundle', None, None),
        ('--multi-worker-sandbox-coordination', 'multi_worker_sandbox_coordination_bundle', None, None),
        ('--controlled-external-tool-preview', 'controlled_external_tool_adapter_preview_bundle', None, None),
        ('--approval-handoff', 'approval_handoff_packet', None, None),
        ('--plan-repo-patch --patch-root /tmp --allowed-patch-file runtime_patch_preview/station_chief_patch_output.txt --dry-run-bundle', 'dry_run_bundle', None, None),
        ('--plan-file-operation --execution-dir /tmp', 'file_operation_plan', None, None),
    ]
    for r in regressions:
        cmd = f'python3 10_runtime/station_chief_runtime.py --command "check please" {r[0]} --json'
        if r[0] == '--stable-release-manifest':
            cmd = f'python3 10_runtime/station_chief_runtime.py {r[0]} --json'
        res = json.loads(run_cmd(cmd).stdout)
        if r[1] == 'stable_release_manifest':
            # Check the manifest directly
            require_true(res.get(r[2]) == r[3], f"Regression check value mismatch: {r[2]}")
        else:
            require_true(r[1] in res, f"Regression check missed key: {r[1]}")
            if r[2]:
                require_true(res[r[1]][r[2]] == r[3], f"Regression check value mismatch: {r[1]}.{r[2]}")

    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v2.6 runtime files.")
    print("PASS: Station Chief Runtime v2.6 valid.")

if __name__ == "__main__":
    main()
