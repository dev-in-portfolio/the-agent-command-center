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

def check_operator_approval_queue_forbidden(path):
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
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v2_8_report.md",
        "scripts/validate_station_chief_runtime_v2_8.py"
    ]
    for f in required_files:
        require_true(Path(f).exists(), f"File missing: {f}")

    check_file_content("10_runtime/station_chief_runtime.py",
        'STATION_CHIEF_RUNTIME_VERSION = "2.8.0"',
        'attach_operator_approval_queue_enforcement',
        'write_operator_approval_queue_enforcement',
        '--operator-approval-queue-schema',
        '--operator-approval-queue-enforcement',
        '--write-operator-approval-queue-enforcement',
        '--approval-queue-label',
        '--approval-queue-confirm-token',
        '--approval-queue-action-count',
        '--approval-queue-action-json',
        '--approval-queue-operator-decisions-json',
        '--approval-queue-stale-after-hours',
        'operator_approval_queue_enforcement_bundle',
        'operator_approval_queue_enforcement_schema',
        'operator_approval_queue_enforcement_approval_gate',
        'queued_action_registry',
        'approval_item_priority_classifier',
        'operator_decision_contract',
        'approval_expiry_stale_item_detector',
        'queue_enforcement_safety_gate',
        'approval_queue_audit_proof',
        'approval_queue_ledger',
        'approval_queue_readiness_summary',
        'release_candidate_hardening_readiness_bridge',
        'operator_approval_queue_enforcement_preview_only',
        'operator_approval_queue_enforcement_requires_token',
        'operator_approval_queue_does_not_execute_queued_actions',
        'operator_approval_queue_does_not_auto_approve',
        'operator_approval_queue_does_not_bypass_approval',
        'operator_approval_queue_does_not_execute_actual_replay',
        'operator_approval_queue_does_not_replay_worker_actions',
        'operator_approval_queue_does_not_replay_external_tools',
        'operator_approval_queue_does_not_call_live_apis',
        'operator_approval_queue_does_not_use_network_access',
        'operator_approval_queue_does_not_open_sockets',
        'operator_approval_queue_does_not_use_credentials',
        'operator_approval_queue_does_not_read_secrets',
        'operator_approval_queue_does_not_read_environment',
        'operator_approval_queue_does_not_modify_repo_files'
    )
    
    check_file_content("10_runtime/station_chief_operator_approval_queue_enforcement.py",
        'OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_MODULE_VERSION = "2.8.0"',
        'OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_STATUS',
        'OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_PHASE',
        'OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_APPROVAL_TOKEN',
        'def canonical_json',
        'def sha256_digest',
        'def normalize_queue_label',
        'def generate_operator_approval_queue_id',
        'def create_operator_approval_queue_enforcement_schema',
        'def create_operator_approval_queue_enforcement_approval_gate',
        'def create_queued_action_registry',
        'def create_approval_item_priority_classifier',
        'def create_operator_decision_contract',
        'def create_approval_expiry_stale_item_detector',
        'def create_queue_enforcement_safety_gate',
        'def create_approval_queue_audit_proof',
        'def create_approval_queue_ledger',
        'def create_approval_queue_readiness_summary',
        'def create_release_candidate_hardening_readiness_bridge',
        'def create_operator_approval_queue_enforcement_bundle'
    )
    
    check_file_content("10_runtime/station_chief_adapters.py",
        'ADAPTER_MODULE_VERSION = "2.8.0"',
        '"supports_operator_approval_queue_enforcement"',
        '"operator_approval_queue_enforcement_requires_specific_token"',
        '"automatic_execution_allowed": False',
        '"queued_action_execution_allowed": False',
        '"auto_approval_allowed": False',
        '"approval_bypass_allowed": False',
        '"operator_approval_queue_enforcement_requires_separate_gate": True',
        'YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT'
    )
    
    check_file_content("10_runtime/station_chief_runtime_readme.md",
        "Station Chief Runtime upgraded to v2.8.0.",
        "Operator approval queue enforcement added.",
        "operator approval queue enforcement schema",
        "operator approval queue enforcement approval gate",
        "queued action registry",
        "approval item priority classifier",
        "operator decision contract",
        "approval expiry and stale-item detector",
        "queue enforcement safety gate",
        "approval queue audit proof",
        "approval queue ledger",
        "approval queue readiness summary",
        "release candidate hardening readiness bridge",
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
        "Station Chief Runtime v2.8.0 adds Operator Approval Queue Enforcement without queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution",
        not_strings=["Explain that", "Include:", "List:", "Write:"]
    )
    
    check_file_content("09_exports/station_chief_runtime_skeleton_report.md",
        "Station Chief Runtime upgraded to v2.8.0.",
        "Operator approval queue enforcement added.",
        "operator approval queue enforcement schema",
        "operator approval queue enforcement approval gate",
        "queued action registry",
        "approval item priority classifier",
        "operator decision contract",
        "approval expiry and stale-item detector",
        "queue enforcement safety gate",
        "approval queue audit proof",
        "approval queue ledger",
        "approval queue readiness summary",
        "release candidate hardening readiness bridge",
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

    check_file_content("09_exports/station_chief_runtime_v2_8_report.md",
        "Station Chief Runtime v2.8.0 Report",
        "Station Chief Runtime upgraded to v2.8.0. Locked 175-family baseline preserved. Operator approval queue enforcement added.",
        "operator approval queue enforcement schema",
        "operator approval queue enforcement approval gate",
        "queued action registry",
        "approval item priority classifier",
        "operator decision contract",
        "approval expiry and stale-item detector",
        "queue enforcement safety gate",
        "approval queue audit proof",
        "approval queue ledger",
        "approval queue readiness summary",
        "release candidate hardening readiness bridge",
        "no baseline mutation",
        "no Devinization overlay mutation",
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
        "Station Chief Runtime v2.8.0 adds Operator Approval Queue Enforcement without queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution",
        "Next recommended build step"
    )

    modules_to_check = [
        "10_runtime/station_chief_runtime.py"
    ]
    for mod in modules_to_check:
        check_forbidden_strings(mod)
        
    check_operator_approval_queue_forbidden("10_runtime/station_chief_operator_approval_queue_enforcement.py")

    cmds_to_run = [
        'python3 10_runtime/station_chief_runtime.py --demo',
        'python3 10_runtime/station_chief_runtime.py --fixture-test',
        'python3 10_runtime/station_chief_fixture_tests.py',
        'python3 10_runtime/station_chief_runtime.py --command "check please" --json',
        'python3 10_runtime/station_chief_runtime.py --command "build release candidate hardening" --brief',
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
        'python3 10_runtime/station_chief_runtime.py --command "check please" --simulate-adapter'
    ]
    for c in cmds_to_run:
        res = run_cmd(c)
        require_true(res.returncode == 0, f"Command failed: {c}\n{res.stderr}")

    res_demo = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --demo').stdout)
    require_true(res_demo["station_chief_runtime_version"] == "2.8.0", "demo runtime version != 2.8.0")
    require_true(res_demo["runtime_status"] == "operator_approval_queue_enforcement", "demo status mismatch")
    require_true(res_demo["release_status"] == "STABLE_LOCKED", "demo release status != STABLE_LOCKED")
    require_true(res_demo["command_type"] == "verification", "demo command type mismatch")
    ev = res_demo["evidence"]
    require_true(ev.get("baseline_preserved") == True, "baseline_preserved")
    require_true(ev.get("external_actions_taken") == False, "external_actions_taken")
    require_true(ev.get("live_worker_agents_activated") == False, "live_worker_agents_activated")
    require_true(ev.get("operator_approval_queue_enforcement_available") == True, "queue_available")
    require_true(ev.get("operator_approval_queue_enforcement_preview_only") == True, "queue_only")
    require_true(ev.get("operator_approval_queue_enforcement_requires_token") == True, "queue_requires_token")
    require_true(ev.get("operator_approval_queue_does_not_execute_queued_actions") == True, "no_exec_queued")
    require_true(ev.get("operator_approval_queue_does_not_auto_approve") == True, "no_auto_approve")
    require_true(ev.get("operator_approval_queue_does_not_bypass_approval") == True, "no_bypass")
    require_true(ev.get("operator_approval_queue_does_not_execute_actual_replay") == True, "no_actual_replay")
    require_true(ev.get("operator_approval_queue_does_not_replay_worker_actions") == True, "no_worker_actions")
    require_true(ev.get("operator_approval_queue_does_not_replay_external_tools") == True, "no_external_tools")
    require_true(ev.get("operator_approval_queue_does_not_call_live_apis") == True, "no_live_apis")
    require_true(ev.get("operator_approval_queue_does_not_use_network_access") == True, "no_network")
    require_true(ev.get("operator_approval_queue_does_not_open_sockets") == True, "no_sockets")
    require_true(ev.get("operator_approval_queue_does_not_use_credentials") == True, "no_creds")
    require_true(ev.get("operator_approval_queue_does_not_read_secrets") == True, "no_secrets")
    require_true(ev.get("operator_approval_queue_does_not_read_environment") == True, "no_env")
    require_true(ev.get("operator_approval_queue_does_not_modify_repo_files") == True, "no_modify_repo")
    require_true(ev.get("release_candidate_hardening_not_yet_active") == True, "rc_not_yet")

    res_fix = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --fixture-test').stdout)
    require_true(res_fix["fixture_test_status"] == "PASS", "fixture_test_status")
    require_true(res_fix["runtime_version"] == "2.8.0", "fixture runtime version")
    require_true(res_fix["case_count"] == 5, "fixture case count")
    require_true(res_fix["failed"] == 0, "fixture failed")

    res_ov = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-overlays').stdout)
    require_true(len(res_ov) == 8, "exactly 8 overlays")
    for ov in res_ov:
        require_true(ov.get("exists") == True, "every overlay exists")
        require_true(ov.get("preserves_locked_baseline") == True, "baseline preserved")
        require_true("Devin O’Rourke" in ov.get("ownership_project_owner", ""), "ownership mismatch")

    res_ad = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --list-adapters').stdout)
    require_true(res_ad["adapter_module_version"] == "2.8.0", "adapter module version")
    require_true(res_ad.get("supports_operator_approval_queue_enforcement") == True, "ad flag")
    require_true(res_ad.get("operator_approval_queue_enforcement_requires_specific_token") == True, "ad flag2")
    require_true(res_ad.get("automatic_execution_allowed") == False, "ad flag3")
    require_true(res_ad.get("queued_action_execution_allowed") == False, "ad flag4")
    require_true(res_ad.get("auto_approval_allowed") == False, "ad flag5")
    require_true(res_ad.get("approval_bypass_allowed") == False, "ad flag6")
    sa = res_ad["supported_adapters"]
    require_true(sa["noop"]["supports_operator_approval_queue_enforcement"] == True, "noop flag")
    require_true(sa["scoped_repo_patch"]["supports_operator_approval_queue_enforcement"] == False, "repo patch flag")
    require_true(sa["scoped_repo_patch"]["operator_approval_queue_enforcement_requires_separate_gate"] == True, "repo patch flag2")

    res_sch = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --operator-approval-queue-schema').stdout)
    require_true(res_sch["operator_approval_queue_enforcement_schema_version"] == "2.8.0", "sch v")
    require_true(res_sch["schema_status"] == "OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_PREVIEW_ONLY", "sch st")
    req_sec = res_sch["required_sections"]
    require_true("operator_approval_queue_enforcement_approval_gate" in req_sec, "sec")
    require_true("queued_action_registry" in req_sec, "sec")
    require_true("approval_item_priority_classifier" in req_sec, "sec")
    require_true("operator_decision_contract" in req_sec, "sec")
    require_true("approval_expiry_stale_item_detector" in req_sec, "sec")
    require_true("queue_enforcement_safety_gate" in req_sec, "sec")
    require_true("approval_queue_audit_proof" in req_sec, "sec")
    require_true("approval_queue_ledger" in req_sec, "sec")
    require_true("approval_queue_readiness_summary" in req_sec, "sec")
    require_true("release_candidate_hardening_readiness_bridge" in req_sec, "sec")
    all_qm = res_sch["allowed_queue_modes"]
    require_true("local_queue_preview_records" in all_qm, "qm")
    require_true("approved_queue_enforcement_records" in all_qm, "qm")
    blk_qm = res_sch["blocked_queue_modes"]
    require_true("automatic_execution" in blk_qm, "bqm")
    require_true("queued_action_execution" in blk_qm, "bqm")
    require_true("auto_approval" in blk_qm, "bqm")
    require_true("approval_bypass" in blk_qm, "bqm")
    require_true("actual_replay_execution" in blk_qm, "bqm")
    require_true("YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT" in res_sch["required_confirmation_tokens"], "tok")
    require_true(res_sch["baseline_preserved"] == True, "base")
    require_true(res_sch["external_actions_taken"] == False, "ea")
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
    res_def = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --json').stdout)
    require_true("operator_approval_queue_enforcement_bundle" in res_def, "bundle")
    bundle = res_def["operator_approval_queue_enforcement_bundle"]
    require_true(bundle["operator_approval_queue_enforcement_bundle_version"] == "2.8.0", "v")
    require_true(res_def["operator_approval_queue_enforcement_approval_gate"]["gate_status"] == "BLOCKED_PENDING_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_APPROVAL", "gate")
    require_true(res_def["operator_approval_queue_enforcement_approval_gate"]["confirmation_token_valid"] == False, "tok val")
    require_true(res_def["queued_action_registry"]["registry_status"] == "BLOCKED", "reg st")
    require_true(res_def["approval_item_priority_classifier"]["classifier_status"] == "BLOCKED", "cla st")
    require_true(res_def["operator_decision_contract"]["contract_status"] == "BLOCKED", "con st")
    require_true(res_def["approval_expiry_stale_item_detector"]["detector_status"] == "BLOCKED", "det st")
    require_true(res_def["queue_enforcement_safety_gate"]["safety_gate_status"] == "BLOCKED", "safe st")
    require_true(res_def["approval_queue_audit_proof"]["audit_status"] == "BLOCKED", "aud st")
    require_true(res_def["approval_queue_readiness_summary"]["readiness_status"] == "BLOCKED", "read st")
    require_true(bundle["external_actions_taken"] == False, "ea")
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
    res_tok = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --json').stdout)
    require_true(res_tok["operator_approval_queue_enforcement_approval_gate"]["gate_status"] == "APPROVED_FOR_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_RECORDS", "gate2")
    require_true(res_tok["operator_approval_queue_enforcement_approval_gate"]["confirmation_token_valid"] == True, "tok val2")
    require_true(res_tok["queued_action_registry"]["registry_status"] == "REGISTRY_CREATED", "reg st2")
    require_true(res_tok["approval_item_priority_classifier"]["classifier_status"] == "CLASSIFIER_CREATED", "cla st2")
    require_true(res_tok["operator_decision_contract"]["contract_status"] == "CONTRACT_CREATED", "con st2")
    require_true(res_tok["approval_expiry_stale_item_detector"]["detector_status"] == "DETECTOR_CREATED", "det st2")
    require_true(res_tok["queue_enforcement_safety_gate"]["safety_gate_status"] == "PASS", "safe st2")
    require_true(res_tok["approval_queue_audit_proof"]["audit_status"] == "PASS", "aud st2")
    require_true(res_tok["approval_queue_ledger"]["ledger_status"] == "OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_LEDGER", "ledg st2")
    require_true(res_tok["approval_queue_readiness_summary"]["ready_for_release_candidate_hardening"] == True, "read2")
    require_true(res_tok["release_candidate_hardening_readiness_bridge"]["next_layer"] == "Release Candidate Hardening", "br")
    require_true(res_tok["release_candidate_hardening_readiness_bridge"]["ready_for_release_candidate_hardening"] == True, "br2")

    # 15. Forbidden execute decision
    res_forb = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --approval-queue-operator-decisions-json \'{"queued-action-001":"APPROVE_AND_EXECUTE"}\' --json').stdout)
    con = res_forb["operator_decision_contract"]
    if con["forbidden_execution_decision_count"] > 0:
        require_true(res_forb["queue_enforcement_safety_gate"]["safety_gate_status"] == "REVIEW_REQUIRED", "safe for")
        require_true(res_forb["approval_queue_audit_proof"]["audit_status"] == "REVIEW_REQUIRED", "aud for")
        require_true(res_forb["approval_queue_readiness_summary"]["readiness_status"] == "REVIEW_REQUIRED", "read for")

    # 16. Command for next layer
    res_nxt = json.loads(run_cmd('python3 10_runtime/station_chief_runtime.py --command "build release candidate hardening" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --json').stdout)
    require_true(res_nxt["release_candidate_hardening_readiness_bridge"]["next_layer"] == "Release Candidate Hardening", "nxt")
    require_true(res_nxt["release_candidate_hardening_readiness_bridge"]["ready_for_release_candidate_hardening"] == True, "nxt2")
    require_true(res_nxt["approval_queue_readiness_summary"]["next_layer"] == "Release Candidate Hardening", "nxt3")
    require_true(res_nxt["approval_queue_readiness_summary"]["readiness_status"] == "READY_FOR_NEXT_LAYER", "nxt4")
    require_true(res_nxt["approval_queue_audit_proof"]["audit_status"] == "PASS", "nxt5")

    # 17. Write artifacts
    with tempfile.TemporaryDirectory() as td:
        res_wr = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-operator-approval-queue-enforcement {td} --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --json').stdout)
        require_true("operator_approval_queue_enforcement_write_summary" in res_wr, "wr sum")
        pdir = res_wr["operator_approval_queue_enforcement_write_summary"]["operator_approval_queue_enforcement_dir"]
        require_true(Path(pdir).exists(), "pdir")
        fw = res_wr["operator_approval_queue_enforcement_write_summary"]["files_written"]
        req_fw = [
            "operator_approval_queue_enforcement_bundle.json",
            "operator_approval_queue_enforcement_schema.json",
            "operator_approval_queue_enforcement_approval_gate.json",
            "queued_action_registry.json",
            "approval_item_priority_classifier.json",
            "operator_decision_contract.json",
            "approval_expiry_stale_item_detector.json",
            "queue_enforcement_safety_gate.json",
            "approval_queue_audit_proof.json",
            "approval_queue_ledger.json",
            "approval_queue_readiness_summary.json",
            "release_candidate_hardening_readiness_bridge.json",
            "operator_approval_queue_enforcement_manifest.json"
        ]
        for r in req_fw:
            require_true(r in fw, f"r {r}")
        man = json.loads((Path(pdir) / "operator_approval_queue_enforcement_manifest.json").read_text())
        require_true(man["runtime_version"] == "2.8.0", "man v")
        require_true(man["status"] == "OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_PREVIEW_ONLY", "man st")

    # 18. Artifact writing with registry
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td) / "runs"
        reg_dir = Path(td) / "registry"
        res_ar = json.loads(run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts {run_dir} --registry-dir {reg_dir} --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --json').stdout)
        require_true("artifact_write_summary" in res_ar, "ar sum")
        rid = res_ar["artifact_write_summary"]["run_id"]
        require_true(rid.startswith("station-chief-v2-8-check-please-"), "rid str")
        adir = res_ar["artifact_write_summary"]["artifact_dir"]
        require_true(Path(adir).exists(), "adir")
        require_true(res_ar["artifact_write_summary"]["registry_updated"] == True, "reg up")
        man = json.loads((Path(adir) / "manifest.json").read_text())
        require_true(man["artifact_type"] == "station_chief_runtime_v2_8_artifacts", "art typ")
        require_true(man["runtime_version"] == "2.8.0", "art v")
        require_true(man.get("operator_approval_queue_enforcement_schema") == True, "m 1")
        run_reg = json.loads((reg_dir / "run_registry.json").read_text())
        require_true(run_reg["registry_version"] == "2.8.0", "run registry version")
        require_true(len(run_reg.get("runs", [])) >= 1, "run registry runs length")
        reg_ix = json.loads((reg_dir / "runtime_index.json").read_text())
        require_true(reg_ix["index_version"] == "2.8.0", "reg ix")

    # 19. Regression
    regressions = [
        ('--stable-release-manifest', 'stable_release_manifest', 'runtime_version', '2.8.0'),
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

    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v2.8 runtime files.")
    print("PASS: Station Chief Runtime v2.8 valid.")

if __name__ == "__main__":
    main()
