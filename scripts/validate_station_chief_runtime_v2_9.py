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
    if not Path(path).exists():
        fail(f"File missing: {path}")
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
        for fbd in forbidden:
            require_true(fbd not in content, f"Found forbidden '{fbd}' in {path}")

def check_release_candidate_hardening_forbidden(path):
    forbidden = [
        "eval(", "exec(", "compile(", "open(", "import socket", "http.server", "socketserver",
        "uvicorn", "streamlit", "netlify", "vercel", "cloudflare", "firebase", "railway",
        "render", "gh api", "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", "os.getenv", "os.environ",
        "datetime.now", "time.time"
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
        "10_runtime/station_chief_controlled_multi_worker_audit_replay_preview.py",
        "10_runtime/station_chief_operator_approval_queue_enforcement.py",
        "10_runtime/station_chief_release_candidate_hardening.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v2_9_report.md",
        "scripts/validate_station_chief_runtime_v2_9.py"
    ]
    for f in required_files:
        require_true(Path(f).exists(), f"File missing: {f}")

    check_file_content("10_runtime/station_chief_runtime.py",
        'STATION_CHIEF_RUNTIME_VERSION = "2.9.0"',
        'attach_release_candidate_hardening',
        'write_release_candidate_hardening',
        '--release-candidate-hardening-schema',
        '--release-candidate-hardening',
        '--write-release-candidate-hardening',
        '--release-candidate-label',
        '--release-candidate-confirm-token',
        '--release-candidate-invariant',
        '--release-candidate-validator',
        '--release-candidate-artifact-contract',
        '--release-candidate-known-issue-json',
        '--release-candidate-checklist-item',
        'release_candidate_hardening_bundle',
        'release_candidate_hardening_schema',
        'release_candidate_hardening_approval_gate',
        'full_runtime_invariant_scan',
        'validator_chain_lock_proof',
        'artifact_contract_freeze_manifest',
        'known_issue_register',
        'pre_v3_production_readiness_checklist',
        'release_candidate_safety_gate',
        'release_candidate_audit_proof',
        'release_candidate_ledger',
        'release_candidate_readiness_summary',
        'controlled_production_readiness_gate_bridge',
        'release_candidate_hardening_preview_only',
        'release_candidate_hardening_requires_token',
        'release_candidate_hardening_does_not_execute_production',
        'release_candidate_hardening_does_not_activate_production_readiness_gate',
        'release_candidate_hardening_does_not_execute_queued_actions',
        'release_candidate_hardening_does_not_auto_approve',
        'release_candidate_hardening_does_not_bypass_approval',
        'release_candidate_hardening_does_not_execute_actual_replay',
        'release_candidate_hardening_does_not_replay_worker_actions',
        'release_candidate_hardening_does_not_replay_external_tools',
        'release_candidate_hardening_does_not_call_live_apis',
        'release_candidate_hardening_does_not_use_network_access',
        'release_candidate_hardening_does_not_open_sockets',
        'release_candidate_hardening_does_not_use_credentials',
        'release_candidate_hardening_does_not_read_secrets',
        'release_candidate_hardening_does_not_read_environment',
        'release_candidate_hardening_does_not_modify_repo_files'
    )
    
    check_file_content("10_runtime/station_chief_release_candidate_hardening.py",
        'RELEASE_CANDIDATE_HARDENING_MODULE_VERSION = "2.9.0"',
        'RELEASE_CANDIDATE_HARDENING_STATUS',
        'RELEASE_CANDIDATE_HARDENING_PHASE',
        'RELEASE_CANDIDATE_HARDENING_APPROVAL_TOKEN',
        'def canonical_json',
        'def sha256_digest',
        'def normalize_release_candidate_label',
        'def generate_release_candidate_hardening_id',
        'def create_release_candidate_hardening_schema',
        'def create_release_candidate_hardening_approval_gate',
        'def create_full_runtime_invariant_scan',
        'def create_validator_chain_lock_proof',
        'def create_artifact_contract_freeze_manifest',
        'def create_known_issue_register',
        'def create_pre_v3_production_readiness_checklist',
        'def create_release_candidate_safety_gate',
        'def create_release_candidate_audit_proof',
        'def create_release_candidate_ledger',
        'def create_release_candidate_readiness_summary',
        'def create_controlled_production_readiness_gate_bridge',
        'def create_release_candidate_hardening_bundle'
    )
    
    check_file_content("10_runtime/station_chief_adapters.py",
        'ADAPTER_MODULE_VERSION = "2.9.0"',
        '"supports_release_candidate_hardening"',
        '"release_candidate_hardening_requires_specific_token"',
        '"production_execution_allowed": False',
        '"production_readiness_gate_activation_allowed": False',
        '"release_candidate_hardening_requires_separate_gate": True',
        'YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING'
    )
    
    check_file_content("10_runtime/station_chief_runtime_readme.md",
        "Station Chief Runtime upgraded to v2.9.0.",
        "Release candidate hardening added.",
        "release candidate hardening schema",
        "release candidate hardening approval gate",
        "full runtime invariant scan",
        "validator chain lock proof",
        "artifact contract freeze manifest",
        "known issue register",
        "pre-v3 production readiness checklist",
        "release candidate safety gate",
        "release candidate audit proof",
        "release candidate ledger",
        "release candidate readiness summary",
        "controlled production readiness gate bridge",
        "no production execution",
        "no production readiness gate activation",
        "no queued action execution",
        "no auto-approval",
        "no approval bypass",
        "no actual replay execution",
        "no worker action re-execution",
        "no external tool replay",
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
        "Station Chief Runtime v2.9.0 adds Release Candidate Hardening without production execution, production readiness gate activation, queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution",
        not_strings=["Explain that", "Include:", "List:", "Write:"]
    )
    
    check_file_content("09_exports/station_chief_runtime_skeleton_report.md",
        "Station Chief Runtime upgraded to v2.9.0.",
        "Release candidate hardening added.",
        "release candidate hardening schema",
        "release candidate hardening approval gate",
        "full runtime invariant scan",
        "validator chain lock proof",
        "artifact contract freeze manifest",
        "known issue register",
        "pre-v3 production readiness checklist",
        "release candidate safety gate",
        "release candidate audit proof",
        "release candidate ledger",
        "release candidate readiness summary",
        "controlled production readiness gate bridge",
        "no production execution",
        "no production readiness gate activation",
        "no queued action execution",
        "no automatic approval",
        "no approval bypass",
        "no actual replay execution",
        "no worker action re-execution",
        "no external tool replay",
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

    check_file_content("09_exports/station_chief_runtime_v2_9_report.md",
        "Station Chief Runtime v2.9.0 Report",
        "Station Chief Runtime upgraded to v2.9.0. Locked 175-family baseline preserved. Release candidate hardening added.",
        "release candidate hardening schema",
        "release candidate hardening approval gate",
        "full runtime invariant scan",
        "validator chain lock proof",
        "artifact contract freeze manifest",
        "known issue register",
        "pre-v3 production readiness checklist",
        "release candidate safety gate",
        "release candidate audit proof",
        "release candidate ledger",
        "release candidate readiness summary",
        "controlled production readiness gate bridge",
        "no baseline mutation",
        "no Devinization overlay mutation",
        "no production execution",
        "no production readiness gate activation",
        "no queued action execution",
        "no automatic approval",
        "no approval bypass",
        "no actual replay execution",
        "no worker action re-execution",
        "no external tool replay",
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
        "Station Chief Runtime v2.9.0 adds Release Candidate Hardening without production execution, production readiness gate activation, queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution",
        "Next recommended build step"
    )

    modules_to_check = [
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
        "10_runtime/station_chief_release_candidate_hardening.py"
    ]
    for mod in modules_to_check:
        check_forbidden_strings(mod)
        
    check_release_candidate_hardening_forbidden("10_runtime/station_chief_release_candidate_hardening.py")

    cmds_to_run = [
        'python3 10_runtime/station_chief_runtime.py --demo',
        'python3 10_runtime/station_chief_runtime.py --fixture-test',
        'python3 10_runtime/station_chief_fixture_tests.py',
        'python3 10_runtime/station_chief_runtime.py --command "check please" --json',
        'python3 10_runtime/station_chief_runtime.py --command "build controlled production readiness gate" --brief',
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
        'python3 10_runtime/station_chief_runtime.py --audit-replay-preview-schema',
        'python3 10_runtime/station_chief_runtime.py --operator-approval-queue-schema',
        'python3 10_runtime/station_chief_runtime.py --release-candidate-hardening-schema',
        'python3 10_runtime/station_chief_runtime.py --command "check please" --simulate-adapter'
    ]
    for c in cmds_to_run:
        res = run_cmd(c)
        require_true(res.returncode == 0, f"Command failed: {c}\n{res.stderr}")

    res_demo = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --demo').stdout)
    require_true(res_demo["station_chief_runtime_version"] == "2.9.0", "demo runtime version != 2.9.0")
    require_true(res_demo["runtime_status"] == "release_candidate_hardening", "demo status mismatch")
    require_true(res_demo["release_status"] == "STABLE_LOCKED", "demo release status != STABLE_LOCKED")
    require_true(res_demo["command_type"] == "verification", "demo command type mismatch")
    ev = res_demo["evidence"]
    require_true(ev.get("baseline_preserved") == True, "baseline_preserved")
    require_true(ev.get("external_actions_taken") == False, "external_actions_taken")
    require_true(ev.get("live_worker_agents_activated") == False, "live_worker_agents_activated")
    require_true(ev.get("release_candidate_hardening_available") == True, "rc_available")
    require_true(ev.get("release_candidate_hardening_preview_only") == True, "rc_only")
    require_true(ev.get("release_candidate_hardening_requires_token") == True, "rc_requires_token")
    require_true(ev.get("release_candidate_hardening_does_not_execute_production") == True, "no_exec_prod")
    require_true(ev.get("release_candidate_hardening_does_not_activate_production_readiness_gate") == True, "no_activate_prod")
    require_true(ev.get("release_candidate_hardening_does_not_execute_queued_actions") == True, "no_exec_queued")
    require_true(ev.get("release_candidate_hardening_does_not_auto_approve") == True, "no_auto_approve")
    require_true(ev.get("release_candidate_hardening_does_not_bypass_approval") == True, "no_bypass")
    require_true(ev.get("release_candidate_hardening_does_not_execute_actual_replay") == True, "no_actual_replay")
    require_true(ev.get("release_candidate_hardening_does_not_replay_worker_actions") == True, "no_worker_actions")
    require_true(ev.get("release_candidate_hardening_does_not_replay_external_tools") == True, "no_external_tools")
    require_true(ev.get("release_candidate_hardening_does_not_call_live_apis") == True, "no_live_apis")
    require_true(ev.get("release_candidate_hardening_does_not_use_network_access") == True, "no_network")
    require_true(ev.get("release_candidate_hardening_does_not_open_sockets") == True, "no_sockets")
    require_true(ev.get("release_candidate_hardening_does_not_use_credentials") == True, "no_creds")
    require_true(ev.get("release_candidate_hardening_does_not_read_secrets") == True, "no_secrets")
    require_true(ev.get("release_candidate_hardening_does_not_read_environment") == True, "no_env")
    require_true(ev.get("release_candidate_hardening_does_not_modify_repo_files") == True, "no_modify_repo")
    require_true(ev.get("controlled_production_readiness_gate_not_yet_active") == True, "prod_not_yet")

    res_fix = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --fixture-test').stdout)
    require_true(res_fix["fixture_test_status"] == "PASS", "fixture_test_status")
    require_true(res_fix["runtime_version"] == "2.9.0", "fixture runtime version")
    require_true(res_fix["case_count"] == 5, "fixture case count")
    require_true(res_fix["failed"] == 0, "fixture failed")

    res_ov = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-overlays').stdout)
    require_true(len(res_ov) == 8, "exactly 8 overlays")
    for ov in res_ov:
        require_true(ov.get("exists") == True, "every overlay exists")
        require_true(ov.get("preserves_locked_baseline") == True, "baseline preserved")
        require_true("Devin O’Rourke" in ov.get("ownership_project_owner", ""), "ownership mismatch")

    res_ad = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-adapters').stdout)
    require_true(res_ad["adapter_module_version"] == "2.9.0", "adapter module version")
    require_true(res_ad.get("supports_release_candidate_hardening") == True, "ad flag")
    require_true(res_ad.get("release_candidate_hardening_requires_specific_token") == True, "ad flag2")
    require_true(res_ad.get("production_execution_allowed") == False, "ad flag3")
    require_true(res_ad.get("production_readiness_gate_activation_allowed") == False, "ad flag4")
    sa = res_ad["supported_adapters"]
    require_true(sa["noop"]["supports_release_candidate_hardening"] == True, "noop flag")
    require_true(sa["scoped_repo_patch"]["supports_release_candidate_hardening"] == False, "repo patch flag")
    require_true(sa["scoped_repo_patch"]["release_candidate_hardening_requires_separate_gate"] == True, "repo patch flag2")

    res_sch = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --release-candidate-hardening-schema').stdout)
    require_true(res_sch["release_candidate_hardening_schema_version"] == "2.9.0", "sch v")
    require_true(res_sch["schema_status"] == "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY", "sch st")
    req_sec = res_sch["required_sections"]
    require_true("release_candidate_hardening_approval_gate" in req_sec, "sec")
    require_true("full_runtime_invariant_scan" in req_sec, "sec")
    require_true("validator_chain_lock_proof" in req_sec, "sec")
    require_true("artifact_contract_freeze_manifest" in req_sec, "sec")
    require_true("known_issue_register" in req_sec, "sec")
    require_true("pre_v3_production_readiness_checklist" in req_sec, "sec")
    require_true("release_candidate_safety_gate" in req_sec, "sec")
    require_true("release_candidate_audit_proof" in req_sec, "sec")
    require_true("release_candidate_ledger" in req_sec, "sec")
    require_true("release_candidate_readiness_summary" in req_sec, "sec")
    require_true("controlled_production_readiness_gate_bridge" in req_sec, "sec")
    all_hm = res_sch["allowed_hardening_modes"]
    require_true("local_release_candidate_hardening_records" in all_hm, "hm")
    require_true("approved_release_candidate_hardening_records" in all_hm, "hm")
    blk_hm = res_sch["blocked_hardening_modes"]
    require_true("production_execution" in blk_hm, "bhm")
    require_true("production_readiness_gate_activation" in blk_hm, "bhm")
    require_true("automatic_execution" in blk_hm, "bhm")
    require_true("queued_action_execution" in blk_hm, "bhm")
    require_true("YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING" in res_sch["required_confirmation_tokens"], "tok")
    require_true(res_sch["baseline_preserved"] == True, "base")
    require_true(res_sch["external_actions_taken"] == False, "ea")
    require_true(res_sch["production_execution_performed"] == False, "pe")
    require_true(res_sch["production_readiness_gate_activated"] == False, "pa")
    require_true(res_sch["automatic_execution_performed"] == False, "ae")
    require_true(res_sch["queued_action_executed"] == False, "qe")
    require_true(res_sch["auto_approval_performed"] == False, "aa")
    require_true(res_sch["actual_replay_performed"] == False, "rp")
    require_true(res_sch["live_api_call_performed"] == False, "la")
    require_true(res_sch["network_access_performed"] == False, "na")
    require_true(res_sch["socket_opened"] == False, "so")
    require_true(res_sch["credentials_used"] == False, "cu")
    require_true(res_sch["secrets_read"] == False, "sr")
    require_true(res_sch["environment_read"] == False, "er")
    require_true(res_sch["repo_files_modified"] == False, "rf")
    require_true(res_sch["deployment_performed"] == False, "dp")
    require_true(res_sch["execution_authorized"] == False, "ea2")

    # 13. Default without token
    res_def = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening --json').stdout)
    require_true("release_candidate_hardening_bundle" in res_def, "bundle")
    bundle = res_def["release_candidate_hardening_bundle"]
    require_true(bundle["release_candidate_hardening_bundle_version"] == "2.9.0", "v")
    require_true(res_def["release_candidate_hardening_approval_gate"]["gate_status"] == "BLOCKED_PENDING_RELEASE_CANDIDATE_HARDENING_APPROVAL", "gate")
    require_true(res_def["release_candidate_hardening_approval_gate"]["confirmation_token_valid"] == False, "tok val")
    require_true(res_def["full_runtime_invariant_scan"]["scan_status"] == "BLOCKED", "scan st")
    require_true(res_def["validator_chain_lock_proof"]["proof_status"] == "BLOCKED", "proof st")
    require_true(res_def["artifact_contract_freeze_manifest"]["freeze_status"] == "BLOCKED", "freeze st")
    require_true(res_def["known_issue_register"]["register_status"] == "BLOCKED", "reg st")
    require_true(res_def["pre_v3_production_readiness_checklist"]["checklist_status"] == "BLOCKED", "check st")
    require_true(res_def["release_candidate_safety_gate"]["safety_gate_status"] == "BLOCKED", "safe st")
    require_true(res_def["release_candidate_audit_proof"]["audit_status"] == "BLOCKED", "aud st")
    require_true(res_def["release_candidate_readiness_summary"]["readiness_status"] == "BLOCKED", "read st")
    require_true(bundle["external_actions_taken"] == False, "ea")
    require_true(bundle["production_execution_performed"] == False, "pe")
    require_true(bundle["production_readiness_gate_activated"] == False, "pa")
    require_true(bundle["automatic_execution_performed"] == False, "ae")
    require_true(bundle["queued_action_executed"] == False, "qe")
    require_true(bundle["auto_approval_performed"] == False, "aa")
    require_true(bundle["actual_replay_performed"] == False, "rp")
    require_true(bundle["live_api_call_performed"] == False, "la")
    require_true(bundle["network_access_performed"] == False, "na")
    require_true(bundle["socket_opened"] == False, "so")
    require_true(bundle["credentials_used"] == False, "cu")
    require_true(bundle["secrets_read"] == False, "sr")
    require_true(bundle["environment_read"] == False, "er")
    require_true(bundle["repo_files_modified"] == False, "rf")
    require_true(bundle["execution_authorized"] == False, "ea3")

    # 14. With valid token
    res_tok = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --json').stdout)
    require_true(res_tok["release_candidate_hardening_approval_gate"]["gate_status"] == "APPROVED_FOR_RELEASE_CANDIDATE_HARDENING_RECORDS", "gate2")
    require_true(res_tok["release_candidate_hardening_approval_gate"]["confirmation_token_valid"] == True, "tok val2")
    require_true(res_tok["full_runtime_invariant_scan"]["scan_status"] == "SCAN_CREATED", "scan st2")
    require_true(res_tok["full_runtime_invariant_scan"]["failed_invariant_count"] == 0, "scan fail")
    require_true(res_tok["validator_chain_lock_proof"]["proof_status"] == "PROOF_CREATED", "proof st2")
    require_true(res_tok["artifact_contract_freeze_manifest"]["freeze_status"] == "FREEZE_MANIFEST_CREATED", "freeze st2")
    require_true(res_tok["known_issue_register"]["register_status"] == "REGISTER_CREATED", "reg st2")
    require_true(res_tok["known_issue_register"]["blocking_issue_count"] == 0, "reg block")
    require_true(res_tok["pre_v3_production_readiness_checklist"]["checklist_status"] == "CHECKLIST_CREATED", "check st2")
    require_true(res_tok["release_candidate_safety_gate"]["safety_gate_status"] == "PASS", "safe st2")
    require_true(res_tok["release_candidate_audit_proof"]["audit_status"] == "PASS", "aud st2")
    require_true(res_tok["release_candidate_ledger"]["ledger_status"] == "RELEASE_CANDIDATE_HARDENING_LEDGER", "ledg st2")
    require_true(res_tok["release_candidate_readiness_summary"]["ready_for_controlled_production_readiness_gate"] == True, "read2")
    require_true(res_tok["controlled_production_readiness_gate_bridge"]["next_layer"] == "Controlled Production Readiness Gate", "br")
    require_true(res_tok["controlled_production_readiness_gate_bridge"]["ready_for_controlled_production_readiness_gate"] == True, "br2")

    # 15. Blocking known issue
    res_block = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --release-candidate-known-issue-json \'{"issue_label":"manual review required","issue_severity":"HIGH","blocks_release_candidate":true}\' --json').stdout)
    reg = res_block["known_issue_register"]
    if reg["blocking_issue_count"] > 0:
        require_true(res_block["release_candidate_safety_gate"]["safety_gate_status"] == "REVIEW_REQUIRED", "safe block")
        require_true(res_block["release_candidate_audit_proof"]["audit_status"] == "REVIEW_REQUIRED", "aud block")
        require_true(res_block["release_candidate_readiness_summary"]["readiness_status"] == "REVIEW_REQUIRED", "read block")

    # 16. Command for next layer
    res_nxt = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "build controlled production readiness gate" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --json').stdout)
    require_true(res_nxt["controlled_production_readiness_gate_bridge"]["next_layer"] == "Controlled Production Readiness Gate", "nxt")
    require_true(res_nxt["controlled_production_readiness_gate_bridge"]["ready_for_controlled_production_readiness_gate"] == True, "nxt2")
    require_true(res_nxt["release_candidate_readiness_summary"]["next_layer"] == "Controlled Production Readiness Gate", "nxt3")
    require_true(res_nxt["release_candidate_readiness_summary"]["readiness_status"] == "READY_FOR_NEXT_LAYER", "nxt4")
    require_true(res_nxt["release_candidate_audit_proof"]["audit_status"] == "PASS", "nxt5")

    # 17. Write artifacts
    with tempfile.TemporaryDirectory() as td:
        res_wr = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-release-candidate-hardening {td} --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --json').stdout)
        require_true("release_candidate_hardening_write_summary" in res_wr, "wr sum")
        pdir = res_wr["release_candidate_hardening_write_summary"]["release_candidate_hardening_dir"]
        require_true(Path(pdir).exists(), "pdir")
        fw = res_wr["release_candidate_hardening_write_summary"]["files_written"]
        req_fw = [
            "release_candidate_hardening_bundle.json",
            "release_candidate_hardening_schema.json",
            "release_candidate_hardening_approval_gate.json",
            "full_runtime_invariant_scan.json",
            "validator_chain_lock_proof.json",
            "artifact_contract_freeze_manifest.json",
            "known_issue_register.json",
            "pre_v3_production_readiness_checklist.json",
            "release_candidate_safety_gate.json",
            "release_candidate_audit_proof.json",
            "release_candidate_ledger.json",
            "release_candidate_readiness_summary.json",
            "controlled_production_readiness_gate_bridge.json",
            "release_candidate_hardening_manifest.json"
        ]
        for r in req_fw:
            require_true(r in fw, f"r {r}")
        man = json.loads((Path(pdir) / "release_candidate_hardening_manifest.json").read_text())
        require_true(man["runtime_version"] == "2.9.0", "man v")
        require_true(man["status"] == "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY", "man st")

    # 18. Artifact writing with registry
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "runs"
        reg_dir = Path(td) / "registry"
        res_ar = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts {run_dir} --registry-dir {reg_dir} --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --json').stdout)
        require_true("artifact_write_summary" in res_ar, "ar sum")
        rid = res_ar["artifact_write_summary"]["run_id"]
        require_true(rid.startswith("station-chief-v2-9-check-please-"), "rid str")
        adir = res_ar["artifact_write_summary"]["artifact_dir"]
        require_true(Path(adir).exists(), "adir")
        require_true(res_ar["artifact_write_summary"]["registry_updated"] == True, "reg up")
        man = json.loads((Path(adir) / "manifest.json").read_text())
        require_true(man["artifact_type"] == "station_chief_runtime_v2_9_artifacts", "art typ")
        require_true(man["runtime_version"] == "2.9.0", "art v")
        require_true(man.get("release_candidate_hardening_schema") == True, "m 1")
        run_reg = json.loads((reg_dir / "run_registry.json").read_text())
        require_true(run_reg["registry_version"] == "2.9.0", "run registry version")
        require_true(len(run_reg.get("runs", [])) >= 1, "run registry runs length")
        reg_ix = json.loads((reg_dir / "runtime_index.json").read_text())
        require_true(reg_ix["index_version"] == "2.9.0", "reg ix")

    # 19. Regression
    regressions = [
        ('--stable-release-manifest', 'stable_release_manifest', 'runtime_version', '2.9.0'),
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
        ('--permissioned-external-api-dry-run', 'permissioned_external_api_dry_run_preview_bundle', None, None),
        ('--controlled-multi-worker-audit-replay-preview', 'controlled_multi_worker_audit_replay_preview_bundle', None, None),
        ('--operator-approval-queue-enforcement', 'operator_approval_queue_enforcement_bundle', None, None),
        ('--approval-handoff', 'approval_handoff_packet', None, None),
        ('--plan-repo-patch --patch-root /tmp --allowed-patch-file runtime_patch_preview/station_chief_patch_output.txt --dry-run-bundle', 'dry_run_bundle', None, None),
        ('--plan-file-operation --execution-dir /tmp', 'file_operation_plan', None, None),
    ]
    for r in regressions:
        cmd = f'python3 10_runtime/station_chief_runtime.py --command "check please" {r[0]} --json'
        if r[0] == '--stable-release-manifest':
            cmd = f'python3 10_runtime/station_chief_runtime.py {r[0]} --json'
        res_json = run_cmd(cmd).stdout
        try:
            res = json.loads(res_json)
        except Exception as e:
            fail(f"Failed to parse JSON for {cmd}: {e}\n{res_json}")
            
        if r[1] == 'stable_release_manifest':
            # Check the manifest directly
            require_true(res.get(r[2]) == r[3], f"Regression check value mismatch: {r[2]}")
        else:
            require_true(r[1] in res, f"Regression check missed key: {r[1]}")
            if r[2]:
                require_true(res[r[1]][r[2]] == r[3], f"Regression check value mismatch: {r[1]}.{r[2]}")

    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v2.9 runtime files.")
    print("PASS: Station Chief Runtime v2.9 valid.")

if __name__ == "__main__":
    main()
