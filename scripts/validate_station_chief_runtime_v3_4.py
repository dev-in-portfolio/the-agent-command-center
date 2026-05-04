#!/usr/bin/env python3
import os
import sys
import subprocess
import json

ERRORS = []

def fail(msg):
    ERRORS.append(msg)

def require_file(path):
    if not os.path.exists(path):
        fail(f"Required file missing: {path}")

def check_file_contains(path, strings):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for s in strings:
        if s not in content:
            fail(f"File {path} missing required string: {s}")

def check_file_excludes(path, strings):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for s in strings:
        if s in content:
            fail(f"File {path} contains forbidden string: {s}")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    # 1. Required files
    required_files = [
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
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
        "10_runtime/station_chief_limited_external_tool_supervised_pilot.py",
        "10_runtime/station_chief_supervised_external_api_pilot.py",
        "09_exports/station_chief_runtime_v3_4_report.md",
        "scripts/validate_station_chief_runtime_v3_4.py"
    ]
    for f in required_files:
        require_file(f)

    # 2. Runtime script contains
    check_file_contains("10_runtime/station_chief_runtime.py", [
        'STATION_CHIEF_RUNTIME_VERSION = "3.4.0"',
        "attach_supervised_external_api_pilot",
        "write_supervised_external_api_pilot",
        "--supervised-external-api-pilot-schema",
        "--supervised-external-api-pilot",
        "--write-supervised-external-api-pilot",
        "--api-pilot-label",
        "--api-pilot-confirm-token",
        "--api-category-label",
        "--api-pilot-required-preflight-approver",
        "--api-request-label",
        "--api-quarantine-label",
        "supervised_external_api_pilot_bundle",
        "supervised_external_api_pilot_schema",
        "supervised_external_api_pilot_approval_gate",
        "single_api_category_contract",
        "credential_denial_by_default",
        "secret_handling_denial_by_default",
        "network_socket_denial_by_default",
        "human_api_use_preflight_gate",
        "api_request_envelope_preview",
        "api_response_quarantine_preview",
        "api_audit_proof",
        "api_pilot_ledger",
        "api_pilot_readiness_summary",
        "monitored_rollback_recovery_drill_bridge"
    ])

    # 3. Supervised external API pilot module contains
    check_file_contains("10_runtime/station_chief_supervised_external_api_pilot.py", [
        'SUPERVISED_EXTERNAL_API_PILOT_MODULE_VERSION = "3.4.0"',
        "SUPERVISED_EXTERNAL_API_PILOT_STATUS",
        "SUPERVISED_EXTERNAL_API_PILOT_PHASE",
        "SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN",
        "canonical_json",
        "sha256_digest",
        "normalize_api_pilot_label",
        "generate_supervised_external_api_pilot_id",
        "create_supervised_external_api_pilot_schema",
        "create_supervised_external_api_pilot_approval_gate",
        "create_single_api_category_contract",
        "create_credential_denial_by_default",
        "create_secret_handling_denial_by_default",
        "create_network_socket_denial_by_default",
        "create_human_api_use_preflight_gate",
        "create_api_request_envelope_preview",
        "create_api_response_quarantine_preview",
        "create_api_audit_proof",
        "create_api_pilot_ledger",
        "create_api_pilot_readiness_summary",
        "create_monitored_rollback_recovery_drill_bridge",
        "create_supervised_external_api_pilot_bundle"
    ])

    # 4. Adapter module contains
    check_file_contains("10_runtime/station_chief_adapters.py", [
        'ADAPTER_MODULE_VERSION = "3.4.0"',
        "supports_supervised_external_api_pilot",
        "supervised_external_api_pilot_requires_specific_token",
        "live_api_call_allowed",
        "network_access_allowed",
        "socket_access_allowed",
        "credential_use_allowed",
        "secret_read_allowed",
        "environment_read_allowed",
        "deployment_allowed",
        "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT"
    ])

    # 5. Runtime modules must not contain
    forbidden_global = [
        "requests", "urllib.request", "os.system", "pip install", "npm install", 
        "live API", "API key", "import subprocess"
    ]
    # Check all allowed runtime files except the validator itself
    for f in required_files:
        if f.startswith("10_runtime/") and f.endswith(".py"):
            check_file_excludes(f, forbidden_global)

    # 6. Supervised external API pilot module must also not contain
    forbidden_module = [
        "eval(", "exec(", "compile(", "open(", "import socket", "from socket", 
        "http.server", "socketserver", "uvicorn", "streamlit", "netlify", 
        "vercel", "cloudflare", "firebase", "railway", "render", "gh api", 
        "git push", "create_deployment", "create_commit", "update_ref", 
        "__import__", "threading", "multiprocessing", "kill(", "terminate(", 
        "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"
    ]
    check_file_excludes("10_runtime/station_chief_supervised_external_api_pilot.py", forbidden_module)

    # 7. Run command checks
    cmds = {
        "demo": 'python3 10_runtime/station_chief_runtime.py --demo',
        "fixture_test": 'python3 10_runtime/station_chief_runtime.py --fixture-test',
        "fixture_tests": 'python3 10_runtime/station_chief_fixture_tests.py',
        "check_please_json": 'python3 10_runtime/station_chief_runtime.py --command "check please" --json',
        "build_monitored": 'python3 10_runtime/station_chief_runtime.py --command "build monitored rollback and recovery drill" --brief',
        "list_overlays": 'python3 10_runtime/station_chief_runtime.py --list-overlays',
        "list_adapters": 'python3 10_runtime/station_chief_runtime.py --list-adapters',
        "schema": 'python3 10_runtime/station_chief_runtime.py --supervised-external-api-pilot-schema',
        "simulate": 'python3 10_runtime/station_chief_runtime.py --command "check please" --simulate-adapter'
    }

    # 8. Parse --demo
    out, err, rc = run_cmd(cmds["demo"])
    if rc != 0:
        fail(f"--demo failed: {err}")
    else:
        try:
            # The demo outputs a JSON blob at the end usually, or is just pure JSON if we ran it with --json?
            # Wait, the prompt says "Parse --demo output and require:". If it's not JSON, we just check for strings.
            # I will check for strings in the output since --demo without --json might print pretty text.
            # Actually, the runtime script typically prints formatted dict. Let's look for specific strings:
            if "'station_chief_runtime_version': '3.4.0'" not in out and '"station_chief_runtime_version": "3.4.0"' not in out:
                fail("--demo missing station_chief_runtime_version 3.4.0")
            if "'runtime_status': 'supervised_external_api_pilot'" not in out and '"runtime_status": "supervised_external_api_pilot"' not in out:
                fail("--demo missing runtime_status supervised_external_api_pilot")
            if "'release_status': 'STABLE_LOCKED'" not in out and '"release_status": "STABLE_LOCKED"' not in out:
                fail("--demo missing release_status STABLE_LOCKED")
            
            # Check evidence
            for k in [
                "baseline_preserved",
                "external_actions_taken",
                "supervised_external_api_pilot_available",
                "supervised_external_api_pilot_preview_only",
                "supervised_external_api_pilot_requires_token",
                "single_api_category_limit_is_one",
                "credential_use_denied_by_default",
                "secret_handling_denied_by_default",
                "network_socket_denied_by_default",
                "supervised_external_api_pilot_does_not_call_live_apis",
                "supervised_external_api_pilot_does_not_use_network_access",
                "supervised_external_api_pilot_does_not_open_sockets",
                "supervised_external_api_pilot_does_not_use_credentials",
                "supervised_external_api_pilot_does_not_read_secrets",
                "supervised_external_api_pilot_does_not_read_environment",
                "supervised_external_api_pilot_does_not_deploy",
                "supervised_external_api_pilot_does_not_invoke_external_tools",
                "supervised_external_api_pilot_does_not_execute_production",
                "supervised_external_api_pilot_does_not_modify_repo_files",
                "monitored_rollback_recovery_drill_not_yet_active"
            ]:
                if f"'{k}': True" not in out and f"'{k}': False" not in out and f'"{k}": true' not in out.lower() and f'"{k}": false' not in out.lower():
                    fail(f"--demo missing evidence key {k}")
        except Exception as e:
            fail(f"Failed parsing --demo: {e}")

    # 9. Parse fixture tests
    out, err, rc = run_cmd(cmds["fixture_test"])
    if rc != 0:
        fail(f"--fixture-test failed: {err}")
    if "PASS" not in out:
        fail("fixture_test missing PASS")
    if "3.4.0" not in out:
        fail("fixture_test missing 3.4.0")
    if "5" not in out:
        fail("fixture_test missing case_count 5")
    if "failed = 0" not in out and "Failed: 0" not in out and "failed': 0" not in out and "failed: 0" not in out.lower() and '"failed": 0' not in out:
        fail("fixture_test missing failed = 0")

    # 10. Parse schema
    out, err, rc = run_cmd(cmds["schema"])
    if rc != 0:
        fail(f"--supervised-external-api-pilot-schema failed: {err}")
    try:
        schema = json.loads(out)
        if schema.get("supervised_external_api_pilot_schema_version") != "3.4.0":
            fail("schema version != 3.4.0")
        if schema.get("schema_status") != "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY":
            fail("schema schema_status invalid")
        req_sec = schema.get("required_sections", [])
        for s in ["supervised_external_api_pilot_approval_gate", "single_api_category_contract", "monitored_rollback_recovery_drill_bridge"]:
            if s not in req_sec:
                fail(f"schema missing required section: {s}")
        blocked = schema.get("blocked_api_pilot_modes", [])
        for s in ["live_api_call", "network_access", "socket_connection", "credential_use", "secret_read", "environment_variable_read", "deployment", "real_external_tool_invocation", "production_execution", "full_workforce_activation"]:
            if s not in blocked:
                fail(f"schema missing blocked mode: {s}")
        if "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT" not in schema.get("required_confirmation_tokens", []):
            fail("schema missing YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT")
        if schema.get("single_api_category_limit") != 1:
            fail("schema limit != 1")
    except Exception as e:
        fail(f"Failed parsing schema: {e}")

    # 11. Default without token
    out, err, rc = run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --supervised-external-api-pilot --json')
    try:
        res = json.loads(out)
        if "supervised_external_api_pilot_bundle" not in res:
            fail("without token: supervised_external_api_pilot_bundle missing")
        else:
            bundle = res["supervised_external_api_pilot_bundle"]
            if bundle["supervised_external_api_pilot_approval_gate"]["gate_status"] != "BLOCKED_PENDING_SUPERVISED_EXTERNAL_API_PILOT_APPROVAL":
                fail("without token: gate_status not blocked")
            if bundle["supervised_external_api_pilot_approval_gate"]["confirmation_token_valid"] is not False:
                fail("without token: token valid != false")
            if bundle["single_api_category_contract"]["contract_status"] != "BLOCKED":
                fail("without token: contract not blocked")
            if bundle["api_audit_proof"]["audit_status"] != "BLOCKED":
                fail("without token: audit_status not blocked")
    except Exception as e:
        fail(f"Failed without token check: {e}")

    # 12. Valid token
    out, err, rc = run_cmd('python3 10_runtime/station_chief_runtime.py --command "check please" --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT --json')
    try:
        res = json.loads(out)
        bundle = res["supervised_external_api_pilot_bundle"]
        if bundle["supervised_external_api_pilot_approval_gate"]["gate_status"] != "APPROVED_FOR_SUPERVISED_EXTERNAL_API_PILOT_RECORDS":
            fail("with token: gate_status not approved")
        if bundle["single_api_category_contract"]["contract_status"] != "API_CATEGORY_CONTRACT_CREATED":
            fail("with token: contract not created")
        if bundle["api_audit_proof"]["audit_status"] != "PASS":
            fail("with token: audit_status not PASS")
        if not bundle["api_pilot_readiness_summary"]["ready_for_monitored_rollback_recovery_drill"]:
            fail("with token: ready_for_monitored_rollback_recovery_drill != true")
    except Exception as e:
        fail(f"Failed with token check: {e}")

    # 13. Next layer command
    out, err, rc = run_cmd('python3 10_runtime/station_chief_runtime.py --command "build monitored rollback and recovery drill" --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT --json')
    try:
        res = json.loads(out)
        bundle = res["supervised_external_api_pilot_bundle"]
        if bundle["monitored_rollback_recovery_drill_bridge"]["next_layer"] != "Monitored Rollback and Recovery Drill":
            fail("next layer: bridge next layer mismatch")
        if bundle["api_pilot_readiness_summary"]["readiness_status"] != "READY_FOR_NEXT_LAYER":
            fail("next layer: readiness status mismatch")
    except Exception as e:
        fail(f"Failed next layer check: {e}")

    # 14. Write supervised external API pilot
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out, err, rc = run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-supervised-external-api-pilot {td} --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT --json')
        try:
            res = json.loads(out)
            if "supervised_external_api_pilot_write_summary" not in res:
                fail("write API pilot missing summary")
            else:
                summary = res["supervised_external_api_pilot_write_summary"]
                out_dir = summary.get("supervised_external_api_pilot_dir")
                if not os.path.exists(out_dir):
                    fail("write API pilot dir missing")
                else:
                    mf = os.path.join(out_dir, "supervised_external_api_pilot_manifest.json")
                    if not os.path.exists(mf):
                        fail("manifest missing in write dir")
                    else:
                        with open(mf, "r") as f:
                            mdata = json.load(f)
                            if mdata.get("runtime_version") != "3.4.0":
                                fail("manifest runtime_version != 3.4.0")
                            if mdata.get("status") != "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY":
                                fail("manifest status mismatch")
        except Exception as e:
            fail(f"Failed write API pilot check: {e}")

    # 15. Artifact writing with registry
    with tempfile.TemporaryDirectory() as td_run, tempfile.TemporaryDirectory() as td_reg:
        out, err, rc = run_cmd(f'python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts {td_run} --registry-dir {td_reg} --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT --json')
        try:
            res = json.loads(out)
            if "artifact_write_summary" not in res:
                fail("write artifacts missing summary")
            else:
                aws = res["artifact_write_summary"]
                if not aws["run_id"].startswith("station-chief-v3-4-check-please-"):
                    fail(f"run_id mismatch: {aws['run_id']}")
                if not aws.get("registry_updated"):
                    fail("registry_updated != true")
                
                rr = os.path.join(td_reg, "run_registry.json")
                ri = os.path.join(td_reg, "runtime_index.json")
                if not os.path.exists(rr):
                    fail("run_registry missing")
                else:
                    with open(rr, "r") as f:
                        if json.load(f).get("registry_version") != "3.4.0":
                            fail("run_registry version != 3.4.0")
                if not os.path.exists(ri):
                    fail("runtime_index missing")
                else:
                    with open(ri, "r") as f:
                        if json.load(f).get("index_version") != "3.4.0":
                            fail("runtime_index version != 3.4.0")
        except Exception as e:
            fail(f"Failed write artifacts check: {e}")

    # 16. Check README and Reports
    for path in ["10_runtime/station_chief_runtime_readme.md", "09_exports/station_chief_runtime_skeleton_report.md", "09_exports/station_chief_runtime_v3_4_report.md"]:
        check_file_contains(path, [
            "Station Chief Runtime upgraded to v3.4.0.",
            "Supervised external API pilot added.",
            "supervised external API pilot schema",
            "supervised external API pilot approval gate",
            "single API category contract",
            "credential denial by default",
            "secret handling denial by default",
            "network/socket denial by default",
            "human API-use preflight gate",
            "API request envelope preview",
            "API response quarantine preview",
            "API audit proof",
            "API pilot ledger",
            "API pilot readiness summary",
            "monitored rollback and recovery drill bridge",
            "no live API calls",
            "no credential use",
            "no secret reads",
            "no environment reads",
            "no network access",
            "no socket access",
            "no deployment",
            "no production execution"
        ])
    for path in ["10_runtime/station_chief_runtime_readme.md", "09_exports/station_chief_runtime_skeleton_report.md"]:
        check_file_excludes(path, [
            "Explain that",
            "Include:",
            "List:",
            "Write:"
        ])

    # 18. Manual scope check print
    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.4 runtime files.")

    # 19. Print fail or pass
    if ERRORS:
        for err in ERRORS:
            print(f"ERROR: {err}")
        print("FAIL")
        sys.exit(1)
    else:
        print("PASS: Station Chief Runtime v3.4 valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
