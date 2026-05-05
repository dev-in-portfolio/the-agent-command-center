#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import runpy
import tempfile
from pathlib import Path

# --- Helper Functions (Part 1) ---

def require(errors, condition, message):
    if not condition:
        errors.append(message)

def require_equal(errors, actual, expected, message):
    if actual != expected:
        errors.append(f"{message} (Expected: {expected}, Actual: {actual})")

def require_true(errors, value, message):
    if value is not True:
        errors.append(f"{message} (Expected True, Actual: {value})")

def require_false(errors, value, message):
    if value is not False:
        errors.append(f"{message} (Expected False, Actual: {value})")

def require_in(errors, item, collection, message):
    if item not in collection:
        errors.append(f"{message} (Item {item} not in {collection})")

def require_all_false(errors, mapping, fields, message_prefix):
    for field in fields:
        require_false(errors, mapping.get(field), f"{message_prefix}: {field}")

def get_path(data, dotted_path, default=None):
    parts = dotted_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current

def parse_json_output(output, context, errors):
    try:
        start_idx_brace = output.find("{")
        start_idx_bracket = output.find("[")
        
        start_idx = -1
        if start_idx_brace != -1 and (start_idx_bracket == -1 or start_idx_brace < start_idx_bracket):
            start_idx = start_idx_brace
        elif start_idx_bracket != -1:
            start_idx = start_idx_bracket
            
        if start_idx == -1:
            errors.append(f"{context}: No JSON object or array found in output.")
            return None
            
        json_str = output[start_idx:]
        return json.loads(json_str)
    except Exception as e:
        errors.append(f"{context}: Failed to parse JSON output: {e}")
        errors.append(f"Raw output (partial): {output[:500]}...")
        return None

def run_command(cmd, context, errors):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            # Not necessarily an error if we expect failure, but we log it for context
            pass
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        errors.append(f"{context}: Command execution failed: {e}")
        return -1, "", str(e)

# --- Validation Tasks ---

def check_file_family(errors):
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
        "10_runtime/station_chief_limited_external_tool_supervised_pilot.py",
        "10_runtime/station_chief_supervised_external_api_pilot.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
        "09_exports/station_chief_runtime_v3_4_report.md",
        "scripts/validate_station_chief_runtime_v3_4.py"
    ]
    for f in required_files:
        require(errors, os.path.exists(f), f"Required file missing: {f}")

def check_static_content(errors):
    # Runtime checks
    runtime_path = "10_runtime/station_chief_runtime.py"
    if os.path.exists(runtime_path):
        with open(runtime_path, "r", encoding="utf-8") as f:
            content = f.read()
            require_in(errors, 'STATION_CHIEF_RUNTIME_VERSION = "3.4.0"', content, "Runtime version mismatch")
            for s in [
                "attach_supervised_external_api_pilot", "write_supervised_external_api_pilot",
                "--supervised-external-api-pilot-schema", "--supervised-external-api-pilot",
                "--write-supervised-external-api-pilot", "--api-pilot-label", "--api-pilot-confirm-token",
                "--api-category-label", "--api-pilot-required-preflight-approver", "--api-request-label",
                "--api-quarantine-label", "supervised_external_api_pilot_bundle", "supervised_external_api_pilot_schema",
                "supervised_external_api_pilot_approval_gate", "single_api_category_contract",
                "credential_denial_by_default", "secret_handling_denial_by_default", "network_socket_denial_by_default",
                "human_api_use_preflight_gate", "api_request_envelope_preview", "api_response_quarantine_preview",
                "api_audit_proof", "api_pilot_ledger", "api_pilot_readiness_summary",
                "monitored_rollback_recovery_drill_bridge", "station-chief-v3-4-", "registry_version", "index_version"
            ]:
                require_in(errors, s, content, f"Runtime missing required string: {s}")

    # Pilot module checks
    pilot_path = "10_runtime/station_chief_supervised_external_api_pilot.py"
    if os.path.exists(pilot_path):
        with open(pilot_path, "r", encoding="utf-8") as f:
            content = f.read()
            require_in(errors, 'SUPERVISED_EXTERNAL_API_PILOT_MODULE_VERSION = "3.4.0"', content, "Pilot module version mismatch")
            for s in [
                "SUPERVISED_EXTERNAL_API_PILOT_STATUS", "SUPERVISED_EXTERNAL_API_PILOT_PHASE",
                "SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT",
                "canonical_json", "sha256_digest", "normalize_api_pilot_label", "generate_supervised_external_api_pilot_id",
                "create_supervised_external_api_pilot_schema", "create_supervised_external_api_pilot_approval_gate",
                "create_single_api_category_contract", "create_credential_denial_by_default",
                "create_secret_handling_denial_by_default", "create_network_socket_denial_by_default",
                "create_human_api_use_preflight_gate", "create_api_request_envelope_preview",
                "create_api_response_quarantine_preview", "create_api_audit_proof", "create_api_pilot_ledger",
                "create_api_pilot_readiness_summary", "create_monitored_rollback_recovery_drill_bridge",
                "create_supervised_external_api_pilot_bundle", "local_api_pilot_records_authorized",
                "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY"
            ]:
                require_in(errors, s, content, f"Pilot module missing required string: {s}")

    # Adapter checks
    adapter_path = "10_runtime/station_chief_adapters.py"
    if os.path.exists(adapter_path):
        with open(adapter_path, "r", encoding="utf-8") as f:
            content = f.read()
            require_in(errors, 'ADAPTER_MODULE_VERSION = "3.4.0"', content, "Adapter module version mismatch")
            for s in [
                "supports_supervised_external_api_pilot", "supervised_external_api_pilot_requires_specific_token",
                "live_api_call_allowed", "network_access_allowed", "socket_access_allowed", "credential_use_allowed",
                "secret_read_allowed", "environment_read_allowed", "deployment_allowed",
                "real_external_tool_invocation_allowed", "production_execution_allowed", "production_activation_allowed",
                "real_task_execution_allowed", "live_task_assignment_allowed", "live_worker_routing_allowed",
                "live_orchestration_allowed", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT"
            ]:
                require_in(errors, s, content, f"Adapter missing required string: {s}")

def check_forbidden_strings(errors):
    forbidden_global = [
        "import requests", "from requests", "urllib.request", "import urllib.request",
        "os.system", "subprocess.run", "subprocess.Popen", "import subprocess",
        "pip install", "npm install", "API key"
    ]
    
    runtime_files = [f for f in os.listdir("10_runtime") if f.startswith("station_chief_") and f.endswith(".py")]
    for rf in runtime_files:
        path = os.path.join("10_runtime", rf)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            for s in forbidden_global:
                require(errors, s not in content, f"File {path} contains forbidden string: {s}")

    # Specific checks for pilot module
    pilot_path = "10_runtime/station_chief_supervised_external_api_pilot.py"
    forbidden_pilot = [
        "eval(", "exec(", "compile(", "open(", "import socket", "from socket",
        "http.server", "socketserver", "uvicorn", "streamlit", "netlify",
        "vercel", "cloudflare", "firebase", "railway", "render", "gh api",
        "git push", "create_deployment", "create_commit", "update_ref",
        "__import__", "threading", "multiprocessing", "kill(", "terminate(",
        "getenv(", "os.getenv", "os.environ", "environ[", "datetime.now", "time.time"
    ]
    with open(pilot_path, "r", encoding="utf-8") as f:
        content = f.read()
        for s in forbidden_pilot:
            require(errors, s not in content, f"File {pilot_path} contains strictly forbidden string: {s}")

def check_demo_runtime(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--demo"], "Demo runtime", errors)
    require_equal(errors, rc, 0, "--demo exit code mismatch")
    data = parse_json_output(stdout, "Demo runtime JSON", errors)
    if data:
        require_equal(errors, data.get("station_chief_runtime_version"), "3.4.0", "Demo version mismatch")
        require_equal(errors, data.get("runtime_status"), "supervised_external_api_pilot", "Demo status mismatch")
        require_equal(errors, data.get("release_status"), "STABLE_LOCKED", "Demo release status mismatch")
        require_equal(errors, data.get("command_type"), "verification", "Demo command type mismatch")
        
        evidence = data.get("evidence", {})
        expected_evidence = {
            "baseline_preserved": True,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "supervised_external_api_pilot_available": True,
            "supervised_external_api_pilot_preview_only": True,
            "supervised_external_api_pilot_requires_token": True,
            "single_api_category_limit_is_one": True,
            "credential_use_denied_by_default": True,
            "secret_handling_denied_by_default": True,
            "network_socket_denied_by_default": True,
            "supervised_external_api_pilot_does_not_call_live_apis": True,
            "supervised_external_api_pilot_does_not_use_network_access": True,
            "supervised_external_api_pilot_does_not_open_sockets": True,
            "supervised_external_api_pilot_does_not_use_credentials": True,
            "supervised_external_api_pilot_does_not_read_secrets": True,
            "supervised_external_api_pilot_does_not_read_environment": True,
            "supervised_external_api_pilot_does_not_deploy": True,
            "supervised_external_api_pilot_does_not_invoke_external_tools": True,
            "supervised_external_api_pilot_does_not_execute_production": True,
            "supervised_external_api_pilot_does_not_activate_production": True,
            "supervised_external_api_pilot_does_not_execute_real_tasks": True,
            "supervised_external_api_pilot_does_not_assign_live_tasks": True,
            "supervised_external_api_pilot_does_not_route_live_workers": True,
            "supervised_external_api_pilot_does_not_perform_live_orchestration": True,
            "supervised_external_api_pilot_does_not_modify_repo_files": True,
            "monitored_rollback_recovery_drill_not_yet_active": True
        }
        for k, v in expected_evidence.items():
            require_equal(errors, evidence.get(k), v, f"Demo evidence mismatch: {k}")

def check_fixture_tests(errors):
    # Command 1
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--fixture-test"], "Fixture test command", errors)
    require_equal(errors, rc, 0, "--fixture-test exit code mismatch")
    data = parse_json_output(stdout, "Fixture test JSON", errors)
    if data:
        require_equal(errors, data.get("fixture_test_status"), "PASS", "Fixture test status mismatch")
        require_equal(errors, data.get("runtime_version"), "3.4.0", "Fixture test runtime version mismatch")
        require_equal(errors, data.get("case_count"), 5, "Fixture test case count mismatch")
        require_equal(errors, data.get("failed"), 0, "Fixture test failure count mismatch")

    # Command 2
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_fixture_tests.py"], "Fixture tests direct", errors)
    require_equal(errors, rc, 0, "fixture_tests.py exit code mismatch")
    data = parse_json_output(stdout, "Fixture tests direct JSON", errors)
    if data:
        require_equal(errors, data.get("fixture_test_status"), "PASS", "Direct fixture test status mismatch")
        require_equal(errors, data.get("runtime_version"), "3.4.0", "Direct fixture test runtime version mismatch")
        require_equal(errors, data.get("case_count"), 5, "Direct fixture test case count mismatch")
        require_equal(errors, data.get("failed"), 0, "Direct fixture test failure count mismatch")

def check_overlays(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-overlays"], "List overlays", errors)
    require_equal(errors, rc, 0, "--list-overlays exit code mismatch")
    data = parse_json_output(stdout, "List overlays JSON", errors)
    if data:
        # data might be a list or a dict with "overlay_stack_summary"
        overlays = data if isinstance(data, list) else data.get("overlay_stack_summary", [])
        require_equal(errors, len(overlays), 8, "Overlay count mismatch")
        for ov in overlays:
            require_true(errors, ov.get("exists"), f"Overlay {ov.get('id')} reported as non-existent")
            require_true(errors, ov.get("preserves_locked_baseline"), f"Overlay {ov.get('id')} does not preserve baseline")
            require(errors, "Devin O’Rourke" in str(ov.get("ownership_project_owner")), f"Overlay {ov.get('id')} owner mismatch")

def check_adapters(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--list-adapters"], "List adapters", errors)
    require_equal(errors, rc, 0, "--list-adapters exit code mismatch")
    data = parse_json_output(stdout, "List adapters JSON", errors)
    if data:
        expected_top = {
            "adapter_module_version": "3.4.0",
            "supports_supervised_external_api_pilot": True,
            "supervised_external_api_pilot_requires_specific_token": True,
            "live_api_call_allowed": False,
            "network_access_allowed": False,
            "socket_access_allowed": False,
            "credential_use_allowed": False,
            "secret_read_allowed": False,
            "environment_read_allowed": False,
            "deployment_allowed": False,
            "real_external_tool_invocation_allowed": False,
            "production_execution_allowed": False,
            "production_activation_allowed": False,
            "real_task_execution_allowed": False,
            "live_task_assignment_allowed": False,
            "live_worker_routing_allowed": False,
            "live_orchestration_allowed": False
        }
        for k, v in expected_top.items():
            require_equal(errors, data.get(k), v, f"Top-level adapter metadata mismatch: {k}")
        
        adapters = data.get("supported_adapters", {})
        require_true(errors, adapters.get("noop", {}).get("supports_supervised_external_api_pilot"), "noop adapter should support pilot")
        require_false(errors, adapters.get("scoped_repo_patch", {}).get("supports_supervised_external_api_pilot"), "scoped_repo_patch should NOT support pilot")
        require_true(errors, adapters.get("scoped_repo_patch", {}).get("supervised_external_api_pilot_requires_separate_gate"), "scoped_repo_patch should require separate gate")

def check_schema(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--supervised-external-api-pilot-schema"], "Schema command", errors)
    require_equal(errors, rc, 0, "--supervised-external-api-pilot-schema exit code mismatch")
    data = parse_json_output(stdout, "Schema JSON", errors)
    if data:
        require_equal(errors, data.get("supervised_external_api_pilot_schema_version"), "3.4.0", "Schema version mismatch")
        require_equal(errors, data.get("schema_status"), "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY", "Schema status mismatch")
        require_equal(errors, data.get("single_api_category_limit"), 1, "Schema limit mismatch")
        
        for k in [
            "baseline_preserved", "external_actions_taken", "live_api_call_performed", "network_access_performed",
            "socket_opened", "credentials_used", "secrets_read", "environment_read", "deployment_performed",
            "real_external_tool_invocation_performed", "production_execution_performed", "production_activation_performed",
            "real_task_execution_performed", "live_task_assignment_performed", "live_worker_routing_performed",
            "live_orchestration_performed", "worker_processes_started", "repo_files_modified", "execution_authorized"
        ]:
            if k == "baseline_preserved":
                require_true(errors, data.get(k), f"Schema {k} mismatch")
            else:
                require_false(errors, data.get(k), f"Schema {k} mismatch")

        req_sections = data.get("required_sections", [])
        for s in [
            "supervised_external_api_pilot_approval_gate", "single_api_category_contract", "credential_denial_by_default",
            "secret_handling_denial_by_default", "network_socket_denial_by_default", "human_api_use_preflight_gate",
            "api_request_envelope_preview", "api_response_quarantine_preview", "api_audit_proof", "api_pilot_ledger",
            "api_pilot_readiness_summary", "monitored_rollback_recovery_drill_bridge"
        ]:
            require_in(errors, s, req_sections, f"Schema missing required section: {s}")

        blocked = data.get("blocked_api_pilot_modes", [])
        for s in [
            "live_api_call", "network_access", "socket_connection", "credential_use", "secret_read",
            "environment_variable_read", "deployment", "real_external_tool_invocation", "production_execution",
            "production_activation", "real_task_execution", "live_task_assignment", "live_worker_routing",
            "live_orchestration", "worker_process_start", "automatic_execution", "queued_action_execution",
            "auto_approval", "approval_bypass", "actual_replay_execution", "api_replay", "external_tool_replay",
            "full_workforce_activation"
        ]:
            require_in(errors, s, blocked, f"Schema missing blocked mode: {s}")

        tokens = data.get("required_confirmation_tokens", [])
        require_in(errors, "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT", tokens, "Schema missing confirmation token")

def check_default_closed(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", "--supervised-external-api-pilot", "--json"], "Default closed check", errors)
    data = parse_json_output(stdout, "Default closed JSON", errors)
    if data:
        require(errors, "supervised_external_api_pilot_bundle" in data, "Default closed: bundle missing")
        require_false(errors, data.get("external_actions_taken"), "Default closed: external_actions_taken should be false")
        require_false(errors, data.get("execution_authorized"), "Default closed: execution_authorized should be false")
        
        bundle = data.get("supervised_external_api_pilot_bundle", {})
        require_equal(errors, bundle.get("supervised_external_api_pilot_bundle_version"), "3.4.0", "Bundle version mismatch")
        require_equal(errors, bundle.get("supervised_external_api_pilot_status"), "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY", "Bundle status mismatch")
        
        gate = bundle.get("supervised_external_api_pilot_approval_gate", {})
        require_equal(errors, gate.get("gate_status"), "BLOCKED_PENDING_SUPERVISED_EXTERNAL_API_PILOT_APPROVAL", "Gate status mismatch")
        require_false(errors, gate.get("confirmation_token_valid"), "Token should be invalid")
        require_false(errors, gate.get("local_api_pilot_records_authorized"), "Records should not be authorized")
        
        contract = bundle.get("single_api_category_contract", {})
        require_equal(errors, contract.get("contract_status"), "BLOCKED", "Contract status mismatch")
        require_equal(errors, contract.get("api_category_count"), 0, "Default closed: api_category_count should be 0")
        require_false(errors, contract.get("preview_only") is False, "Default closed: preview_only should remain true")
        require_all_false(errors, contract, [
            "live_api_call_allowed", "network_access_allowed", "socket_access_allowed",
            "credential_use_allowed", "secret_read_allowed", "environment_read_allowed",
            "deployment_allowed", "execution_authorized"
        ], "Default closed contract safety")

        cred_denial = bundle.get("credential_denial_by_default", {})
        require_equal(errors, cred_denial.get("denial_status"), "BLOCKED", "Default closed: credential denial should be blocked")
        require_false(errors, cred_denial.get("credential_use_allowed"), "Default closed: credential use should be denied")
        require_false(errors, cred_denial.get("credentials_used"), "Default closed: credentials should not be used")

        secret_denial = bundle.get("secret_handling_denial_by_default", {})
        require_equal(errors, secret_denial.get("denial_status"), "BLOCKED", "Default closed: secret handling should be blocked")
        require_false(errors, secret_denial.get("secret_read_allowed"), "Default closed: secret read should be denied")
        require_false(errors, secret_denial.get("environment_read_allowed"), "Default closed: environment read should be denied")
        require_false(errors, secret_denial.get("secrets_read"), "Default closed: secrets should not be read")
        require_false(errors, secret_denial.get("environment_read"), "Default closed: environment should not be read")
        require_false(errors, secret_denial.get("environment_variables_read"), "Default closed: environment variables should not be read")

        net_denial = bundle.get("network_socket_denial_by_default", {})
        require_equal(errors, net_denial.get("denial_status"), "BLOCKED", "Default closed: network/socket denial should be blocked")
        require_false(errors, net_denial.get("network_access_allowed"), "Default closed: network access should be denied")
        require_false(errors, net_denial.get("socket_access_allowed"), "Default closed: socket access should be denied")
        require_false(errors, net_denial.get("network_access_performed"), "Default closed: network access should not be performed")
        require_false(errors, net_denial.get("socket_opened"), "Default closed: socket should not be opened")

        preflight = bundle.get("human_api_use_preflight_gate", {})
        require_equal(errors, preflight.get("preflight_status"), "BLOCKED", "Default closed: human API preflight should be blocked")
        require_true(errors, preflight.get("human_api_use_preflight_required"), "Default closed: preflight should remain required")
        require_false(errors, preflight.get("current_preflight_grants_api_call"), "Default closed: preflight must not grant api call")

        request_preview = bundle.get("api_request_envelope_preview", {})
        require_equal(errors, request_preview.get("envelope_status"), "BLOCKED", "Default closed: request envelope preview should be blocked")
        require_false(errors, request_preview.get("live_api_call_performed"), "Default closed: live API call should not be performed")
        require_false(errors, request_preview.get("network_access_performed"), "Default closed: network access should not be performed")
        require_false(errors, request_preview.get("socket_opened"), "Default closed: socket should not be opened")

        response_preview = bundle.get("api_response_quarantine_preview", {})
        require_equal(errors, response_preview.get("preview_status"), "BLOCKED", "Default closed: response quarantine should be blocked")
        require_false(errors, response_preview.get("real_api_response_received"), "Default closed: no API response should be received")
        require_false(errors, response_preview.get("processes_terminated"), "Default closed: no processes should be terminated")
        require_false(errors, response_preview.get("workers_terminated"), "Default closed: no workers should be terminated")
        require_false(errors, response_preview.get("production_state_changed"), "Default closed: production state should not change")
        require_false(errors, response_preview.get("deployment_rolled_back"), "Default closed: deployment should not roll back")
        
        audit = bundle.get("api_audit_proof", {})
        require_equal(errors, audit.get("audit_status"), "BLOCKED", "Audit status mismatch")
        require_true(errors, audit.get("baseline_preserved"), "Default closed: baseline must be preserved")
        
        # Check safety booleans in bundle and top-level
        for target in [data, bundle]:
            for k in [
                "external_actions_taken", "live_api_call_performed", "network_access_performed", "socket_opened",
                "credentials_used", "secrets_read", "environment_read", "deployment_performed",
                "real_external_tool_invocation_performed", "production_execution_performed",
                "production_activation_performed", "real_task_execution_performed", "live_task_assignment_performed",
                "live_worker_routing_performed", "live_orchestration_performed", "worker_processes_started",
                "repo_files_modified", "execution_authorized"
            ]:
                if k in target:
                    require_false(errors, target.get(k), f"Safety boolean {k} should be false in default path")

def check_valid_token(errors):
    cmd = [
        "python3", "10_runtime/station_chief_runtime.py", "--command", "check please",
        "--supervised-external-api-pilot", "--api-pilot-confirm-token", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT", "--json"
    ]
    rc, stdout, stderr = run_command(cmd, "Valid token check", errors)
    data = parse_json_output(stdout, "Valid token JSON", errors)
    if data:
        bundle = data.get("supervised_external_api_pilot_bundle", {})
        require_equal(errors, bundle.get("supervised_external_api_pilot_status"), "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY", "Valid token: status mismatch")
        
        gate = bundle.get("supervised_external_api_pilot_approval_gate", {})
        require_equal(errors, gate.get("gate_status"), "APPROVED_FOR_SUPERVISED_EXTERNAL_API_PILOT_RECORDS", "Valid token: gate status mismatch")
        require_true(errors, gate.get("confirmation_token_valid"), "Valid token: token valid mismatch")
        require_true(errors, gate.get("local_api_pilot_records_authorized"), "Valid token: records authorized mismatch")
        
        # All dangerous auth fields remain false
        dangerous_fields = [
            "live_api_call_authorized", "network_access_authorized", "socket_access_authorized",
            "credential_use_authorized", "secret_read_authorized", "environment_read_authorized",
            "deployment_authorized", "real_external_tool_invocation_authorized", "production_execution_authorized",
            "production_activation_authorized", "real_task_execution_authorized", "live_task_assignment_authorized",
            "live_worker_routing_authorized", "live_orchestration_authorized", "worker_process_start_authorized",
            "repo_mutation_authorized", "external_actions_taken", "repo_files_modified", "execution_authorized"
        ]
        for f in dangerous_fields:
            require_false(errors, gate.get(f), f"Dangerous field {f} should be false even with valid token")
            
        contract = bundle.get("single_api_category_contract", {})
        require_equal(errors, contract.get("contract_status"), "API_CATEGORY_CONTRACT_CREATED", "Contract status mismatch")
        require_equal(errors, contract.get("single_api_category_limit"), 1, "Contract limit mismatch")
        require_equal(errors, contract.get("api_category_count"), 1, "Contract count mismatch")
        require_true(errors, contract.get("preview_only"), "Contract should be preview only")
        
        denial_fields = ["live_api_call_allowed", "network_access_allowed", "socket_access_allowed", "credential_use_allowed", "secret_read_allowed", "environment_read_allowed", "deployment_allowed"]
        for f in denial_fields:
            require_false(errors, contract.get(f), f"Contract field {f} should be false")

        cred_denial = bundle.get("credential_denial_by_default", {})
        require_equal(errors, cred_denial.get("denial_status"), "CREDENTIAL_USE_DENIED_BY_DEFAULT", "Credential denial status mismatch")
        require_false(errors, cred_denial.get("credential_use_allowed"), "Credential use should be denied")
        require_false(errors, cred_denial.get("credentials_used"), "Credentials should not be used")
        
        secret_denial = bundle.get("secret_handling_denial_by_default", {})
        require_equal(errors, secret_denial.get("denial_status"), "SECRET_HANDLING_DENIED_BY_DEFAULT", "Secret handling denial status mismatch")
        require_false(errors, secret_denial.get("secret_read_allowed"), "Secret read should be denied")
        require_false(errors, secret_denial.get("environment_read"), "Environment read should be denied")
        
        net_denial = bundle.get("network_socket_denial_by_default", {})
        require_equal(errors, net_denial.get("denial_status"), "NETWORK_SOCKET_DENIED_BY_DEFAULT", "Network socket denial status mismatch")
        require_false(errors, net_denial.get("network_access_performed"), "Network access should not be performed")
        require_false(errors, net_denial.get("socket_opened"), "Socket should not be opened")

        preflight = bundle.get("human_api_use_preflight_gate", {})
        require_equal(errors, preflight.get("preflight_status"), "API_USE_PREFLIGHT_REQUIREMENT_CREATED", "Preflight status mismatch")
        require_true(errors, preflight.get("human_api_use_preflight_required"), "Preflight should be required")
        require_false(errors, preflight.get("current_preflight_grants_api_call"), "Preflight should not grant api call")

        audit = bundle.get("api_audit_proof", {})
        require_equal(errors, audit.get("audit_status"), "PASS", "Audit status mismatch")
        safety = audit.get("safety_checks", {})
        require_true(errors, safety.get("approval_gate_valid"), "Audit: approval gate invalid")
        require_true(errors, safety.get("single_api_category_contract_created"), "Audit: contract not created")
        require_true(errors, safety.get("no_live_api_call"), "Audit: live api call detected")
        require_true(errors, safety.get("no_network_access"), "Audit: network access detected")
        
        readiness = bundle.get("api_pilot_readiness_summary", {})
        require_equal(errors, readiness.get("readiness_status"), "READY_FOR_NEXT_LAYER", "Readiness status mismatch")
        require_true(errors, readiness.get("ready_for_monitored_rollback_recovery_drill"), "Ready for next drill mismatch")
        
        bridge = bundle.get("monitored_rollback_recovery_drill_bridge", {})
        require_equal(errors, bridge.get("next_layer"), "Monitored Rollback and Recovery Drill", "Bridge next layer mismatch")
        require_true(errors, bridge.get("ready_for_monitored_rollback_recovery_drill"), "Bridge readiness mismatch")

        # Bundle-level safety booleans
        for k in [
            "external_actions_taken", "live_api_call_performed", "network_access_performed", "socket_opened",
            "credentials_used", "secrets_read", "environment_read", "deployment_performed",
            "real_external_tool_invocation_performed", "production_execution_performed",
            "production_activation_performed", "real_task_execution_performed", "live_task_assignment_performed",
            "live_worker_routing_performed", "live_orchestration_performed", "worker_processes_started",
            "repo_files_modified", "execution_authorized"
        ]:
            require_false(errors, bundle.get(k), f"Safety boolean {k} should be false in valid token path")
            require_false(errors, data.get(k), f"Top-level safety boolean {k} should be false in valid token path")

def check_bridge_command(errors):
    cmd = [
        "python3", "10_runtime/station_chief_runtime.py", "--command", "build monitored rollback and recovery drill",
        "--supervised-external-api-pilot", "--api-pilot-confirm-token", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT", "--json"
    ]
    rc, stdout, stderr = run_command(cmd, "Bridge command check", errors)
    data = parse_json_output(stdout, "Bridge command JSON", errors)
    if data:
        bundle = data.get("supervised_external_api_pilot_bundle", {})
        require_equal(errors, get_path(bundle, "monitored_rollback_recovery_drill_bridge.next_layer"), "Monitored Rollback and Recovery Drill", "Bridge next layer mismatch")
        require_true(errors, get_path(bundle, "monitored_rollback_recovery_drill_bridge.ready_for_monitored_rollback_recovery_drill"), "Bridge readiness mismatch")
        require_equal(errors, get_path(bundle, "api_pilot_readiness_summary.next_layer"), "Monitored Rollback and Recovery Drill", "Readiness next layer mismatch")
        require_equal(errors, get_path(bundle, "api_pilot_readiness_summary.readiness_status"), "READY_FOR_NEXT_LAYER", "Readiness status mismatch")
        require_equal(errors, get_path(bundle, "api_audit_proof.audit_status"), "PASS", "Audit status mismatch")
        require_false(errors, data.get("external_actions_taken"), "external_actions_taken should be false")
        require_false(errors, data.get("execution_authorized"), "execution_authorized should be false")

def check_write_api_pilot(errors):
    with tempfile.TemporaryDirectory() as td:
        cmd = [
            "python3", "10_runtime/station_chief_runtime.py", "--command", "check please",
            "--write-supervised-external-api-pilot", td, "--api-pilot-confirm-token", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT", "--json"
        ]
        rc, stdout, stderr = run_command(cmd, "Write API pilot check", errors)
        data = parse_json_output(stdout, "Write API pilot JSON", errors)
        if data:
            write_summary = data.get("supervised_external_api_pilot_write_summary", {})
            require(errors, write_summary, "write_summary missing")
            out_dir = write_summary.get("supervised_external_api_pilot_dir")
            require(errors, out_dir and os.path.exists(out_dir), "API pilot dir missing")
            
            expected_files = [
                "supervised_external_api_pilot_bundle.json", "supervised_external_api_pilot_schema.json",
                "supervised_external_api_pilot_approval_gate.json", "single_api_category_contract.json",
                "credential_denial_by_default.json", "secret_handling_denial_by_default.json",
                "network_socket_denial_by_default.json", "human_api_use_preflight_gate.json",
                "api_request_envelope_preview.json", "api_response_quarantine_preview.json",
                "api_audit_proof.json", "api_pilot_ledger.json", "api_pilot_readiness_summary.json",
                "monitored_rollback_recovery_drill_bridge.json", "supervised_external_api_pilot_manifest.json"
            ]
            files_written = write_summary.get("files_written", [])
            for ef in expected_files:
                require_in(errors, ef, files_written, f"Expected file not in files_written: {ef}")
                require(errors, os.path.exists(os.path.join(out_dir, ef)), f"File not on disk: {ef}")
                
            manifest_path = os.path.join(out_dir, "supervised_external_api_pilot_manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    m = json.load(f)
                    require_equal(errors, m.get("supervised_external_api_pilot_manifest_version"), "3.4.0", "Manifest version mismatch")
                    require_equal(errors, m.get("runtime_version"), "3.4.0", "Manifest runtime version mismatch")
                    require_equal(errors, m.get("status"), "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY", "Manifest status mismatch")
                    for k in [
                        "baseline_preserved", "external_actions_taken", "live_api_call_performed", "network_access_performed",
                        "socket_opened", "credentials_used", "secrets_read", "environment_read", "deployment_performed",
                        "real_external_tool_invocation_performed", "production_execution_performed", "production_activation_performed",
                        "real_task_execution_performed", "live_task_assignment_performed", "live_worker_routing_performed",
                        "live_orchestration_performed", "worker_processes_started", "repo_files_modified", "execution_authorized"
                    ]:
                        if k == "baseline_preserved":
                            require_true(errors, m.get(k), f"Manifest {k} mismatch")
                        else:
                            require_false(errors, m.get(k), f"Manifest {k} mismatch")

def check_write_artifacts(errors):
    with tempfile.TemporaryDirectory() as td_run, tempfile.TemporaryDirectory() as td_reg:
        cmd = [
            "python3", "10_runtime/station_chief_runtime.py", "--command", "check please",
            "--write-artifacts", td_run, "--registry-dir", td_reg,
            "--supervised-external-api-pilot", "--api-pilot-confirm-token", "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT", "--json"
        ]
        rc, stdout, stderr = run_command(cmd, "Write artifacts check", errors)
        data = parse_json_output(stdout, "Write artifacts JSON", errors)
        if data:
            summary = data.get("artifact_write_summary", {})
            run_id = summary.get("run_id", "")
            require(errors, run_id.startswith("station-chief-v3-4-check-please-"), f"run_id mismatch: {run_id}")
            require_true(errors, summary.get("registry_updated"), "registry_updated mismatch")
            
            run_dir = os.path.join(td_run, run_id)
            require(errors, os.path.exists(run_dir), f"Artifact run directory missing: {run_dir}")
            
            expected_files = [
                "supervised_external_api_pilot_bundle.json", "supervised_external_api_pilot_schema.json",
                "supervised_external_api_pilot_approval_gate.json", "single_api_category_contract.json",
                "credential_denial_by_default.json", "secret_handling_denial_by_default.json",
                "network_socket_denial_by_default.json", "human_api_use_preflight_gate.json",
                "api_request_envelope_preview.json", "api_response_quarantine_preview.json",
                "api_audit_proof.json", "api_pilot_ledger.json", "api_pilot_readiness_summary.json",
                "monitored_rollback_recovery_drill_bridge.json", "manifest.json", "full_result.json"
            ]
            files_written = summary.get("files_written", [])
            for ef in expected_files:
                require_in(errors, ef, files_written, f"Expected artifact file not in files_written: {ef}")
                require(errors, os.path.exists(os.path.join(run_dir, ef)), f"Artifact file not on disk: {ef}")
            
            manifest_path = os.path.join(run_dir, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    m = json.load(f)
                    require_equal(errors, m.get("artifact_type"), "station_chief_runtime_v3_4_artifacts", "Artifact type mismatch")
                    require_equal(errors, m.get("runtime_version"), "3.4.0", "Artifact runtime version mismatch")
                    for k in [
                        "supervised_external_api_pilot_schema", "supervised_external_api_pilot_approval_gate",
                        "single_api_category_contract", "credential_denial_by_default", "secret_handling_denial_by_default",
                        "network_socket_denial_by_default", "human_api_use_preflight_gate", "api_request_envelope_preview",
                        "api_response_quarantine_preview", "api_audit_proof", "api_pilot_ledger",
                        "api_pilot_readiness_summary", "monitored_rollback_recovery_drill_bridge",
                        "supervised_external_api_pilot_preview_only", "supervised_external_api_pilot_requires_token",
                        "single_api_category_limit_is_one", "credential_use_denied_by_default",
                        "secret_handling_denied_by_default", "network_socket_denied_by_default",
                        "supervised_external_api_pilot_does_not_call_live_apis",
                        "supervised_external_api_pilot_does_not_use_network_access",
                        "supervised_external_api_pilot_does_not_open_sockets",
                        "supervised_external_api_pilot_does_not_use_credentials",
                        "supervised_external_api_pilot_does_not_read_secrets",
                        "supervised_external_api_pilot_does_not_read_environment",
                        "supervised_external_api_pilot_does_not_deploy",
                        "supervised_external_api_pilot_does_not_invoke_external_tools",
                        "supervised_external_api_pilot_does_not_execute_production",
                        "supervised_external_api_pilot_does_not_modify_repo_files"
                    ]:
                        require_true(errors, m.get(k), f"Manifest boolean mismatch: {k}")
                    for k in [
                        "baseline_preserved", "external_actions_taken", "live_api_call_performed", "network_access_performed",
                        "socket_opened", "credentials_used", "secrets_read", "environment_read", "deployment_performed",
                        "real_external_tool_invocation_performed", "production_execution_performed", "production_activation_performed",
                        "real_task_execution_performed", "live_task_assignment_performed", "live_worker_routing_performed",
                        "live_orchestration_performed", "worker_processes_started", "repo_files_modified", "execution_authorized"
                    ]:
                        if k == "baseline_preserved":
                            require_true(errors, m.get(k), f"Artifact manifest {k} mismatch")
                        else:
                            require_false(errors, m.get(k), f"Artifact manifest {k} mismatch")

            # Registry and Index
            registry_path = os.path.join(td_reg, "run_registry.json")
            index_path = os.path.join(td_reg, "runtime_index.json")
            
            if os.path.exists(registry_path):
                with open(registry_path, "r") as f:
                    r = json.load(f)
                    require_equal(errors, r.get("registry_version"), "3.4.0", "Registry version mismatch")
                    require(errors, len(r.get("runs", [])) >= 1, "Registry runs missing")
            else:
                errors.append("run_registry.json missing")

            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    i = json.load(f)
                    require_equal(errors, i.get("index_version"), "3.4.0", "Index version mismatch")
                    require(errors, i.get("run_count", 0) >= 1, "Index run count mismatch")
            else:
                errors.append("runtime_index.json missing")

def check_stable_manifest(errors):
    rc, stdout, stderr = run_command(["python3", "10_runtime/station_chief_runtime.py", "--stable-release-manifest"], "Stable manifest check", errors)
    data = parse_json_output(stdout, "Stable manifest JSON", errors)
    if data:
        # Might be nested
        m = data.get("stable_release_manifest") if data.get("stable_release_manifest") else data
        require_equal(errors, m.get("runtime_version"), "3.4.0", "Stable manifest version mismatch")
        require_equal(errors, m.get("release_status"), "STABLE_LOCKED", "Stable manifest status mismatch")

def check_prior_layer_regressions(errors):
    regression_cmds = [
        ("--release-lock", "release_lock_bundle"),
        ("--controlled-execution", "controlled_execution_bundle"),
        ("--work-order-executor", "work_order_executor_bundle"),
        ("--worker-hiring-registry", "worker_hiring_registry_bundle"),
        ("--department-routing", "department_routing_bundle"),
        ("--multi-agent-orchestration", "multi_agent_orchestration_bundle"),
        ("--operator-console", "operator_console_bundle"),
        ("--github-patch-hardening", "github_patch_hardening_bundle"),
        ("--deployment-packaging", "deployment_packaging_bundle"),
        ("--controlled-worker-execution", "controlled_worker_execution_bundle"),
        ("--tool-permission-binding", "tool_permission_binding_bundle"),
        ("--live-telemetry-abort", "live_execution_telemetry_abort_bundle"),
        ("--post-run-audit-expansion", "post_run_audit_expansion_bundle"),
        ("--multi-worker-sandbox-coordination", "multi_worker_sandbox_coordination_bundle"),
        ("--controlled-external-tool-preview", "controlled_external_tool_adapter_preview_bundle"),
        ("--permissioned-external-api-dry-run", "permissioned_external_api_dry_run_preview_bundle"),
        ("--controlled-multi-worker-audit-replay-preview", "controlled_multi_worker_audit_replay_preview_bundle"),
        ("--operator-approval-queue-enforcement", "operator_approval_queue_enforcement_bundle"),
        ("--release-candidate-hardening", "release_candidate_hardening_bundle"),
        ("--controlled-production-readiness-gate", "controlled_production_readiness_gate_bundle"),
        ("--controlled-worker-hiring-activation-pilot", "controlled_worker_hiring_activation_pilot_bundle"),
        ("--first-supervised-production-dry-run", "first_supervised_production_dry_run_bundle"),
        ("--limited-external-tool-supervised-pilot", "limited_external_tool_supervised_pilot_bundle"),
        ("--supervised-external-api-pilot", "supervised_external_api_pilot_bundle"),
        ("--approval-handoff", "approval_handoff_packet")
    ]
    
    for flag, bundle_key in regression_cmds:
        cmd = ["python3", "10_runtime/station_chief_runtime.py", "--command", "check please", flag, "--json"]
        rc, stdout, stderr = run_command(cmd, f"Regression check: {flag}", errors)
        require_equal(errors, rc, 0, f"Regression {flag} exit code mismatch")
        data = parse_json_output(stdout, f"Regression {flag} JSON", errors)
        if data:
            require(errors, bundle_key in data, f"Regression {flag}: bundle {bundle_key} missing")
            require_equal(errors, data.get("station_chief_runtime_version"), "3.4.0", f"Regression {flag}: version mismatch")
            require_false(errors, data.get("external_actions_taken"), f"Regression {flag}: external_actions_taken should be false")
            evidence = data.get("evidence", {})
            if evidence:
                require_true(errors, evidence.get("baseline_preserved"), f"Regression {flag}: baseline_preserved mismatch")
                require_false(errors, evidence.get("external_actions_taken"), f"Regression {flag}: evidence external_actions_taken mismatch")

def check_phrases(errors):
    targets = [
        ("10_runtime/station_chief_runtime_readme.md", [
            "Station Chief Runtime upgraded to v3.4.0.", "Supervised external API pilot added.",
            "supervised external API pilot schema", "supervised external API pilot approval gate",
            "single API category contract", "credential denial by default", "secret handling denial by default",
            "network/socket denial by default", "human API-use preflight gate", "API request envelope preview",
            "API response quarantine preview", "API audit proof", "API pilot ledger", "API pilot readiness summary",
            "monitored rollback and recovery drill bridge", "no live API calls", "no credential use",
            "no secret reads", "no environment reads", "no network access", "no socket access", "no deployment",
            "no real external tool invocation", "no production execution", "no production activation",
            "no live task assignment", "no live worker routing", "no live orchestration", "no full workforce activation",
            "Station Chief Runtime v3.4.0 adds Supervised External API Pilot without live API calls, network access, socket access, credential use, secret reads, environment reads, deployment, real external tool invocation, real production execution, production activation, real task execution, live task assignment, live worker routing, live orchestration, worker process starts, shell command execution, or broad workforce activation",
            "Next recommended step: build monitored rollback and recovery drill."
        ], []),
        ("09_exports/station_chief_runtime_skeleton_report.md", [
            "Station Chief Runtime upgraded to v3.4.0.", "Supervised external API pilot added.",
            "supervised external API pilot schema", "supervised external API pilot approval gate",
            "single API category contract", "credential denial by default", "secret handling denial by default",
            "network/socket denial by default", "human API-use preflight gate", "API request envelope preview",
            "API response quarantine preview", "API audit proof", "API pilot ledger", "API pilot readiness summary",
            "monitored rollback and recovery drill bridge", "no live API calls", "no credential use",
            "no secret reads", "no environment reads", "no network access", "no socket access", "no deployment",
            "no real external tool invocation", "no production execution", "no production activation",
            "no live task assignment", "no live worker routing", "no live orchestration", "no shell command execution",
            "no arbitrary code execution", "no repo mutation", "Next recommended build step: build monitored rollback and recovery drill."
        ], []),
        ("09_exports/station_chief_runtime_v3_4_report.md", [
            "Station Chief Runtime v3.4.0 Report",
            "Station Chief Runtime upgraded to v3.4.0. Locked 175-family baseline preserved. Supervised external API pilot added.",
            "supervised external API pilot schema", "supervised external API pilot approval gate",
            "single API category contract", "credential denial by default", "secret handling denial by default",
            "network/socket denial by default", "human API-use preflight gate", "API request envelope preview",
            "API response quarantine preview", "API audit proof", "API pilot ledger", "API pilot readiness summary",
            "monitored rollback and recovery drill bridge", "no baseline mutation", "no Devinization overlay mutation",
            "no live API calls", "no network access", "no socket access", "no credential use", "no secret reads",
            "no environment reads", "no deployment", "no real external tool invocation", "no production execution",
            "no production activation", "no real task execution", "no live task assignment", "no live worker routing",
            "no live orchestration", "no worker process starts", "no shell command execution",
            "no arbitrary code execution", "no full workforce activation", "deterministic API pilot records only",
            "Next recommended build step: build monitored rollback and recovery drill."
        ], [])
    ]
    
    forbidden = ["Explain that", "Include:", "List:", "Write:"]
    
    for path, required_phrases, forbidden_phrases in targets:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                for p in required_phrases:
                    require_in(errors, p, content, f"File {path} missing phrase: {p}")
                for p in forbidden:
                    require(errors, p not in content, f"File {path} contains forbidden phrase: {p}")

def check_delegation(errors):
    validators = [
        "scripts/validate_station_chief_runtime_skeleton.py", "scripts/validate_station_chief_runtime_v0_2.py",
        "scripts/validate_station_chief_runtime_v0_3.py", "scripts/validate_station_chief_runtime_v0_4.py",
        "scripts/validate_station_chief_runtime_v0_5.py", "scripts/validate_station_chief_runtime_v0_6.py",
        "scripts/validate_station_chief_runtime_v0_7.py", "scripts/validate_station_chief_runtime_v0_8.py",
        "scripts/validate_station_chief_runtime_v0_9.py", "scripts/validate_station_chief_runtime_v1_0.py",
        "scripts/validate_station_chief_runtime_v1_1.py", "scripts/validate_station_chief_runtime_v1_2.py",
        "scripts/validate_station_chief_runtime_v1_3.py", "scripts/validate_station_chief_runtime_v1_4.py",
        "scripts/validate_station_chief_runtime_v1_5.py", "scripts/validate_station_chief_runtime_v1_6.py",
        "scripts/validate_station_chief_runtime_v1_7.py", "scripts/validate_station_chief_runtime_v1_8.py",
        "scripts/validate_station_chief_runtime_v2_0.py", "scripts/validate_station_chief_runtime_v2_1.py",
        "scripts/validate_station_chief_runtime_v2_2.py", "scripts/validate_station_chief_runtime_v2_3.py",
        "scripts/validate_station_chief_runtime_v2_4.py", "scripts/validate_station_chief_runtime_v2_5.py",
        "scripts/validate_station_chief_runtime_v2_6.py", "scripts/validate_station_chief_runtime_v2_7.py",
        "scripts/validate_station_chief_runtime_v2_8.py", "scripts/validate_station_chief_runtime_v2_9.py",
        "scripts/validate_station_chief_runtime_v3_0.py", "scripts/validate_station_chief_runtime_v3_1.py",
        "scripts/validate_station_chief_runtime_v3_2.py", "scripts/validate_station_chief_runtime_v3_3.py"
    ]
    for v in validators:
        if os.path.exists(v):
            with open(v, "r", encoding="utf-8") as f:
                content = f.read()
                require_in(errors, "validate_station_chief_runtime_v3_4.py", content, f"Validator {v} missing delegation to v3.4")
                require_in(errors, "runpy.run_path", content, f"Validator {v} missing runpy.run_path")

def main():
    errors = []
    
    # Execution
    check_file_family(errors)
    check_static_content(errors)
    check_forbidden_strings(errors)
    check_demo_runtime(errors)
    check_fixture_tests(errors)
    check_overlays(errors)
    check_adapters(errors)
    check_schema(errors)
    check_default_closed(errors)
    check_valid_token(errors)
    check_bridge_command(errors)
    check_write_api_pilot(errors)
    check_write_artifacts(errors)
    check_stable_manifest(errors)
    check_prior_layer_regressions(errors)
    check_phrases(errors)
    check_delegation(errors)
    
    # Reporting
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print("FAIL")
        sys.exit(1)
    
    print("Manual scope check required: confirm git diff contains only the allowed Station Chief v3.4 validator hotfix files.")
    print("PASS: Station Chief Runtime v3.4 valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
