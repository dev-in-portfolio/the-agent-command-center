import json
import hashlib

PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_MODULE_VERSION = "3.2.0"
PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_STATUS = "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY"
PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_PHASE = "Permissioned External API Dry-Run Preview"
PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_api_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "permissioned-external-api-dry-run-preview"
    return normalized

def generate_external_api_dry_run_preview_id(command: str, api_label: str, runtime_version: str = "3.2.0") -> str:
    norm_label = normalize_api_label(api_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"external-api-dry-run-v3-2-{norm_label}-{digest}"

def create_permissioned_external_api_dry_run_preview_schema() -> dict:
    return {
        "permissioned_external_api_dry_run_preview_schema_version": "3.2.0",
        "schema_status": "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY",
        "required_sections": [
            "external_api_dry_run_approval_gate",
            "api_endpoint_preview_registry",
            "request_envelope_validation",
            "credential_absence_proof",
            "outbound_call_prevention_proof",
            "dry_run_response_fixture_contract",
            "external_api_audit_proof",
            "external_api_dry_run_ledger",
            "external_api_dry_run_readiness_summary",
            "controlled_multi_worker_audit_replay_preview_readiness_bridge"
        ],
        "allowed_dry_run_modes": [
            "schema_only",
            "local_api_dry_run_preview",
            "approved_api_dry_run_records",
            "endpoint_registry_preview",
            "request_envelope_validation_preview",
            "fixture_response_contract_preview",
            "outbound_call_prevention_preview"
        ],
        "blocked_dry_run_modes": [
            "live_external_api_execution",
            "real_network_request",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "external_tool_invocation",
            "shell_command_api_adapter",
            "repo_mutating_api_adapter",
            "deployment_api_adapter",
            "background_api_process",
            "autonomous_external_retry",
            "production_api_execution"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW"
        ],
        "safety_invariants": [
            "dry-run records only",
            "no live API calls",
            "no network access",
            "no socket access",
            "no credential use",
            "no secret reads",
            "no environment reads",
            "no shell commands",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "no live orchestration",
            "API dry-run preview does not authorize external execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_external_api_dry_run_approval_gate(
    api_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW")
    gate_status = "APPROVED_FOR_PERMISSIONED_EXTERNAL_API_DRY_RUN_RECORDS" if token_valid else "BLOCKED_PENDING_EXTERNAL_API_DRY_RUN_APPROVAL"
    return {
        "external_api_dry_run_approval_gate_version": "3.2.0",
        "api_label": api_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_api_dry_run_records_authorized": token_valid,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_api_endpoint_preview_registry(
    approval_gate: dict,
    requested_endpoints: list[str] | None = None
) -> dict:
    if requested_endpoints is None:
        requested_endpoints = [
            "github_rest_preview",
            "gmail_api_preview",
            "calendar_api_preview",
            "file_search_preview",
            "web_search_preview"
        ]
    
    registry_status = "REGISTRY_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    endpoint_entries = []
    for endpoint in requested_endpoints:
        endpoint_entries.append({
            "endpoint_id": endpoint,
            "endpoint_status": "PREVIEW_ONLY",
            "live_call_allowed": False,
            "credentials_required_for_live_use": True,
            "credentials_present_in_dry_run": False,
            "external_actions_taken": False
        })
        
    return {
        "api_endpoint_preview_registry_version": "3.2.0",
        "registry_status": registry_status,
        "requested_endpoints": requested_endpoints,
        "endpoint_entries": endpoint_entries,
        "endpoint_count": len(requested_endpoints),
        "registry_digest": sha256_digest(endpoint_entries),
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_request_envelope_validation(
    approval_gate: dict,
    endpoint_id: str,
    method: str | None = None,
    path_template: str | None = None,
    request_payload: dict | None = None
) -> dict:
    if method is None:
        method = "GET"
    if path_template is None:
        path_template = "/dry-run/preview"
    if request_payload is None:
        request_payload = {}
        
    allowed_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    
    blocked_indicators = ["secret", "api_key", "token=", "password", "credential", "private key"]
    payload_str = canonical_json(request_payload).lower()
    found_blocked = [ind for ind in blocked_indicators if ind in payload_str]
    
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        method in allowed_methods and
        isinstance(path_template, str) and
        len(path_template) > 0 and
        len(found_blocked) == 0
    )
    
    validation_status = "PASS" if is_valid else "BLOCKED"
    
    return {
        "request_envelope_validation_version": "3.2.0",
        "endpoint_id": endpoint_id,
        "method": method,
        "path_template": path_template,
        "validation_status": validation_status,
        "request_payload_digest": sha256_digest(request_payload),
        "blocked_payload_indicators": found_blocked,
        "request_sent": False,
        "network_access_performed": False,
        "socket_opened": False,
        "live_api_call_performed": False,
        "credentials_used": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_credential_absence_proof(
    approval_gate: dict,
    credential_labels: list[str] | None = None
) -> dict:
    if credential_labels is None:
        credential_labels = [
            "api_key",
            "bearer_token",
            "oauth_token",
            "client_secret",
            "refresh_token"
        ]
        
    proof_status = "PROOF_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    credential_checks = []
    for label in credential_labels:
        credential_checks.append({
            "label": label,
            "checked_by_filesystem": False,
            "checked_by_environment": False,
            "credential_value_read": False,
            "credential_present_for_dry_run": False
        })
        
    return {
        "credential_absence_proof_version": "3.2.0",
        "proof_status": proof_status,
        "credential_labels": credential_labels,
        "credential_checks": credential_checks,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "filesystem_read": False,
        "credential_absence_digest": sha256_digest(credential_checks),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_outbound_call_prevention_proof(
    approval_gate: dict,
    endpoint_registry: dict,
    request_validation: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        endpoint_registry.get("registry_status") == "REGISTRY_CREATED" and
        request_validation.get("validation_status") == "PASS"
    )
    proof_status = "PROOF_CREATED" if is_valid else "BLOCKED"
    
    prevention_controls = [
        "no req-library import",
        "no urllib-request import",
        "no socket use",
        "no outbound request execution",
        "no credential read",
        "no live API invocation",
        "dry-run fixture response only"
    ]
    
    return {
        "outbound_call_prevention_proof_version": "3.2.0",
        "proof_status": proof_status,
        "prevention_controls": prevention_controls,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "request_sent": False,
        "external_tool_invoked": False,
        "outbound_prevention_digest": sha256_digest(prevention_controls),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_dry_run_response_fixture_contract(
    approval_gate: dict,
    endpoint_id: str,
    fixture_payload: dict | None = None
) -> dict:
    if fixture_payload is None:
        fixture_payload = {
            "fixture_status": "DRY_RUN_ONLY",
            "message": "No live API call was performed."
        }
        
    contract_status = "FIXTURE_CONTRACT_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    return {
        "dry_run_response_fixture_contract_version": "3.2.0",
        "endpoint_id": endpoint_id,
        "contract_status": contract_status,
        "fixture_payload": fixture_payload,
        "fixture_payload_digest": sha256_digest(fixture_payload),
        "fixture_source": "LOCAL_STATIC_DRY_RUN_FIXTURE",
        "fixture_fetched_from_network": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_external_api_audit_proof(
    approval_gate: dict,
    endpoint_registry: dict,
    request_validation: dict,
    credential_absence_proof: dict,
    outbound_call_prevention_proof: dict,
    fixture_contract: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        endpoint_registry.get("registry_status") == "REGISTRY_CREATED" and
        request_validation.get("validation_status") == "PASS" and
        credential_absence_proof.get("proof_status") == "PROOF_CREATED" and
        outbound_call_prevention_proof.get("proof_status") == "PROOF_CREATED" and
        fixture_contract.get("contract_status") == "FIXTURE_CONTRACT_CREATED"
    )
    audit_status = "PASS" if is_valid else "BLOCKED"
    
    gate_digest = sha256_digest(approval_gate)
    registry_digest = sha256_digest(endpoint_registry)
    validation_digest = sha256_digest(request_validation)
    cred_digest = sha256_digest(credential_absence_proof)
    outbound_digest = sha256_digest(outbound_call_prevention_proof)
    fixture_digest = sha256_digest(fixture_contract)
    
    combined_input = f"{gate_digest}:{registry_digest}:{validation_digest}:{cred_digest}:{outbound_digest}:{fixture_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": approval_gate.get("confirmation_token_valid", False),
        "endpoint_registry_created": endpoint_registry.get("registry_status") == "REGISTRY_CREATED",
        "request_envelope_valid": request_validation.get("validation_status") == "PASS",
        "credential_absence_proven": credential_absence_proof.get("proof_status") == "PROOF_CREATED",
        "outbound_call_prevented": outbound_call_prevention_proof.get("proof_status") == "PROOF_CREATED",
        "fixture_contract_created": fixture_contract.get("contract_status") == "FIXTURE_CONTRACT_CREATED",
        "no_external_actions": True,
        "no_live_api_call": True,
        "no_network_access": True,
        "no_socket_opened": True,
        "no_credentials_used": True,
        "no_secrets_read": True,
        "no_environment_read": True,
        "no_repo_modifications": True,
        "no_deployment": True
    }
    
    return {
        "external_api_audit_proof_version": "3.2.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "endpoint_registry_digest": registry_digest,
        "request_validation_digest": validation_digest,
        "credential_absence_digest": cred_digest,
        "outbound_call_prevention_digest": outbound_digest,
        "fixture_contract_digest": fixture_digest,
        "combined_external_api_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_external_api_dry_run_ledger(
    approval_gate: dict,
    endpoint_registry: dict,
    request_validation: dict,
    credential_absence_proof: dict,
    outbound_call_prevention_proof: dict,
    fixture_contract: dict,
    audit_proof: dict
) -> dict:
    ledger_status = "PERMISSIONED_EXTERNAL_API_DRY_RUN_LEDGER" if audit_proof.get("audit_status") == "PASS" else "BLOCKED"
    
    entries = [
        {"type": "external_api_dry_run_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "api_endpoint_preview_registry", "digest": sha256_digest(endpoint_registry)},
        {"type": "request_envelope_validation", "digest": sha256_digest(request_validation)},
        {"type": "credential_absence_proof", "digest": sha256_digest(credential_absence_proof)},
        {"type": "outbound_call_prevention_proof", "digest": sha256_digest(outbound_call_prevention_proof)},
        {"type": "dry_run_response_fixture_contract", "digest": sha256_digest(fixture_contract)},
        {"type": "external_api_audit_proof", "digest": sha256_digest(audit_proof)}
    ]
    
    return {
        "external_api_dry_run_ledger_version": "3.2.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_external_api_dry_run_readiness_summary(
    approval_gate: dict,
    audit_proof: dict,
    api_dry_run_ledger: dict
) -> dict:
    is_ready = (
        approval_gate.get("confirmation_token_valid", False) and
        audit_proof.get("audit_status") == "PASS" and
        api_dry_run_ledger.get("ledger_status") == "PERMISSIONED_EXTERNAL_API_DRY_RUN_LEDGER"
    )
    
    readiness_status = "READY_FOR_NEXT_LAYER" if is_ready else "BLOCKED"
    
    return {
        "external_api_dry_run_readiness_summary_version": "3.2.0",
        "readiness_status": readiness_status,
        "ready_for_controlled_multi_worker_audit_replay_preview": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "audit_status": audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": api_dry_run_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "Controlled Multi-Worker Audit Replay Preview",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_multi_worker_audit_replay_preview_readiness_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    is_ready = readiness_summary.get("ready_for_controlled_multi_worker_audit_replay_preview", False)
    return {
        "controlled_multi_worker_audit_replay_preview_readiness_bridge_version": "3.2.0",
        "current_layer": "Permissioned External API Dry-Run Preview",
        "next_layer": "Controlled Multi-Worker Audit Replay Preview",
        "ready_for_controlled_multi_worker_audit_replay_preview": is_ready,
        "required_next_capabilities": [
            "controlled multi-worker audit replay preview schema",
            "replay packet registry",
            "deterministic replay plan contract",
            "replay safety gate",
            "multi-worker replay comparison proof",
            "replay output quarantine contract",
            "replay audit proof",
            "still no actual replay execution by default"
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no credential use",
            "no secret reads",
            "no actual replay execution",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no live production orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_permissioned_external_api_dry_run_preview_bundle(
    result: dict,
    command: str | None = None,
    api_label: str | None = None,
    endpoint_id: str | None = None,
    confirmation_token: str | None = None,
    requested_endpoints: list[str] | None = None,
    method: str | None = None,
    path_template: str | None = None,
    request_payload: dict | None = None,
    credential_labels: list[str] | None = None,
    fixture_payload: dict | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if api_label is None:
        api_label = "station-chief-external-api-dry-run-preview"
    if endpoint_id is None:
        endpoint_id = "web_search_preview"
        
    schema = create_permissioned_external_api_dry_run_preview_schema()
    gate = create_external_api_dry_run_approval_gate(api_label, confirmation_token)
    registry = create_api_endpoint_preview_registry(gate, requested_endpoints)
    validation = create_request_envelope_validation(gate, endpoint_id, method, path_template, request_payload)
    cred_proof = create_credential_absence_proof(gate, credential_labels)
    outbound_proof = create_outbound_call_prevention_proof(gate, registry, validation)
    fixture = create_dry_run_response_fixture_contract(gate, endpoint_id, fixture_payload)
    audit = create_external_api_audit_proof(gate, registry, validation, cred_proof, outbound_proof, fixture)
    ledger = create_external_api_dry_run_ledger(gate, registry, validation, cred_proof, outbound_proof, fixture, audit)
    summary = create_external_api_dry_run_readiness_summary(gate, audit, ledger)
    bridge = create_controlled_multi_worker_audit_replay_preview_readiness_bridge(result, summary)
    
    return {
        "permissioned_external_api_dry_run_preview_bundle_version": "3.2.0",
        "permissioned_external_api_dry_run_preview_status": "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY",
        "permissioned_external_api_dry_run_preview_schema": schema,
        "external_api_dry_run_approval_gate": gate,
        "api_endpoint_preview_registry": registry,
        "request_envelope_validation": validation,
        "credential_absence_proof": cred_proof,
        "outbound_call_prevention_proof": outbound_proof,
        "dry_run_response_fixture_contract": fixture,
        "external_api_audit_proof": audit,
        "external_api_dry_run_ledger": ledger,
        "external_api_dry_run_readiness_summary": summary,
        "controlled_multi_worker_audit_replay_preview_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
