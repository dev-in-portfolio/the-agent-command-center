import json
import hashlib

SUPERVISED_EXTERNAL_API_PILOT_MODULE_VERSION = "3.6.0"
SUPERVISED_EXTERNAL_API_PILOT_STATUS = "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY"
SUPERVISED_EXTERNAL_API_PILOT_PHASE = "Supervised External API Pilot"
SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN = "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_api_pilot_label(label: str) -> str:
    import re
    label = label.lower()
    label = re.sub(r"[^a-z0-9]+", "-", label)
    label = label.strip("-")
    return label if label else "supervised-external-api-pilot"

def generate_supervised_external_api_pilot_id(command: str, api_pilot_label: str, runtime_version: str = "3.6.0") -> str:
    norm_label = normalize_api_pilot_label(api_pilot_label)
    data = f"{runtime_version}:{command}:{norm_label}"
    hash_prefix = sha256_digest(data)[:12]
    return f"supervised-external-api-pilot-v3-6-{norm_label}-{hash_prefix}"

def create_supervised_external_api_pilot_schema() -> dict:
    return {
        "supervised_external_api_pilot_schema_version": "3.6.0",
        "schema_status": "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY",
        "required_sections": [
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
        ],
        "allowed_api_pilot_modes": [
            "schema_only",
            "local_api_pilot_records",
            "approved_api_pilot_records",
            "single_api_category_contract_preview",
            "credential_denial_preview",
            "secret_handling_denial_preview",
            "network_socket_denial_preview",
            "api_request_envelope_preview",
            "api_response_quarantine_preview",
            "api_audit_preview"
        ],
        "blocked_api_pilot_modes": [
            "live_api_call",
            "network_access",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "deployment",
            "real_external_tool_invocation",
            "production_execution",
            "production_activation",
            "real_task_execution",
            "live_task_assignment",
            "live_worker_routing",
            "live_orchestration",
            "worker_process_start",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "api_replay",
            "external_tool_replay",
            "full_workforce_activation"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT"
        ],
        "single_api_category_limit": 1,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_supervised_external_api_pilot_approval_gate(
    api_pilot_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = confirmation_token == SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN
    gate_status = "APPROVED_FOR_SUPERVISED_EXTERNAL_API_PILOT_RECORDS" if token_valid else "BLOCKED_PENDING_SUPERVISED_EXTERNAL_API_PILOT_APPROVAL"
    return {
        "supervised_external_api_pilot_approval_gate_version": "3.6.0",
        "api_pilot_label": api_pilot_label,
        "gate_status": gate_status,
        "confirmation_token_required": SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_api_pilot_records_authorized": token_valid,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "real_external_tool_invocation_authorized": False,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "real_task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "worker_process_start_authorized": False,
        "repo_mutation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_single_api_category_contract(
    approval_gate: dict,
    api_category_label: str | None = None
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False)
    status = "API_CATEGORY_CONTRACT_CREATED" if valid else "BLOCKED"
    return {
        "single_api_category_contract_version": "3.6.0",
        "contract_status": status,
        "api_category_label": api_category_label if api_category_label else "read-only-public-status-api-preview",
        "single_api_category_limit": 1,
        "api_category_count": 1 if valid else 0,
        "preview_only": True,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "execution_authorized": False
    }

def create_credential_denial_by_default(
    approval_gate: dict,
    api_category_contract: dict
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False) and api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED"
    status = "CREDENTIAL_USE_DENIED_BY_DEFAULT" if valid else "BLOCKED"
    return {
        "credential_denial_by_default_version": "3.6.0",
        "denial_status": status,
        "credential_use_default": "DENIED",
        "credential_use_allowed": False,
        "credentials_used": False,
        "api_keys_used": False,
        "tokens_used": False,
        "oauth_used": False,
        "service_account_used": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_secret_handling_denial_by_default(
    approval_gate: dict,
    api_category_contract: dict
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False) and api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED"
    status = "SECRET_HANDLING_DENIED_BY_DEFAULT" if valid else "BLOCKED"
    return {
        "secret_handling_denial_by_default_version": "3.6.0",
        "denial_status": status,
        "secret_read_default": "DENIED",
        "environment_read_default": "DENIED",
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "secrets_read": False,
        "environment_read": False,
        "environment_variables_read": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_network_socket_denial_by_default(
    approval_gate: dict,
    api_category_contract: dict
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False) and api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED"
    status = "NETWORK_SOCKET_DENIED_BY_DEFAULT" if valid else "BLOCKED"
    return {
        "network_socket_denial_by_default_version": "3.6.0",
        "denial_status": status,
        "network_access_default": "DENIED",
        "socket_access_default": "DENIED",
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "live_api_call_allowed": False,
        "live_api_call_performed": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_human_api_use_preflight_gate(
    approval_gate: dict,
    required_api_preflight_approver: str | None = None
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False)
    status = "API_USE_PREFLIGHT_REQUIREMENT_CREATED" if valid else "BLOCKED"
    return {
        "human_api_use_preflight_gate_version": "3.6.0",
        "preflight_status": status,
        "required_api_preflight_approver": required_api_preflight_approver if required_api_preflight_approver else "Devin O’Rourke / explicit human operator",
        "human_api_use_preflight_required": True,
        "current_preflight_grants_api_call": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "approval_bypass_allowed": False,
        "execution_authorized": False
    }

def create_api_request_envelope_preview(
    approval_gate: dict,
    api_category_contract: dict,
    api_request_label: str | None = None
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False) and api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED"
    status = "API_REQUEST_ENVELOPE_PREVIEW_CREATED" if valid else "BLOCKED"
    return {
        "api_request_envelope_preview_version": "3.6.0",
        "envelope_status": status,
        "api_request_label": api_request_label if api_request_label else "single supervised API request preview",
        "request_preview_only": True,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_api_response_quarantine_preview(
    approval_gate: dict,
    quarantine_labels: list[str] | None = None
) -> dict:
    valid = approval_gate.get("confirmation_token_valid", False)
    status = "API_RESPONSE_QUARANTINE_PREVIEW_CREATED" if valid else "BLOCKED"
    labels = quarantine_labels if quarantine_labels is not None else [
        "quarantine API request envelope",
        "deny live-API call",
        "deny network access",
        "deny socket access",
        "deny credential use",
        "deny secret reads",
        "deny environment reads",
        "require human review",
        "preserve API pilot audit ledger",
        "preserve locked baseline"
    ]
    return {
        "api_response_quarantine_preview_version": "3.6.0",
        "preview_status": status,
        "quarantine_records": labels,
        "quarantine_record_count": len(labels),
        "quarantine_preview_only": True,
        "real_api_response_received": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rolled_back": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_api_audit_proof(
    approval_gate: dict,
    api_category_contract: dict,
    credential_denial: dict,
    secret_denial: dict,
    network_socket_denial: dict,
    human_api_use_preflight_gate: dict,
    api_request_envelope_preview: dict,
    api_response_quarantine_preview: dict
) -> dict:
    checks = {
        "approval_gate_valid": approval_gate.get("confirmation_token_valid", False),
        "single_api_category_contract_created": api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED",
        "credential_use_denied_by_default": credential_denial.get("denial_status") == "CREDENTIAL_USE_DENIED_BY_DEFAULT",
        "secret_handling_denied_by_default": secret_denial.get("denial_status") == "SECRET_HANDLING_DENIED_BY_DEFAULT",
        "network_socket_denied_by_default": network_socket_denial.get("denial_status") == "NETWORK_SOCKET_DENIED_BY_DEFAULT",
        "human_api_use_preflight_required": human_api_use_preflight_gate.get("preflight_status") == "API_USE_PREFLIGHT_REQUIREMENT_CREATED",
        "api_request_envelope_preview_created": api_request_envelope_preview.get("envelope_status") == "API_REQUEST_ENVELOPE_PREVIEW_CREATED",
        "api_response_quarantine_preview_created": api_response_quarantine_preview.get("preview_status") == "API_RESPONSE_QUARANTINE_PREVIEW_CREATED",
        "no_live_api_call": True,
        "no_network_access": True,
        "no_socket_opened": True,
        "no_credentials_used": True,
        "no_secrets_read": True,
        "no_environment_read": True,
        "no_deployment": True,
        "no_real_external_tool_invocation": True,
        "no_production_execution": True,
        "no_production_activation": True,
        "no_real_task_execution": True,
        "no_live_task_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_repo_modifications": True
    }
    
    audit_status = "PASS" if all(checks.values()) else "BLOCKED"
    
    ag_digest = sha256_digest(approval_gate)
    acc_digest = sha256_digest(api_category_contract)
    cd_digest = sha256_digest(credential_denial)
    sd_digest = sha256_digest(secret_denial)
    nsd_digest = sha256_digest(network_socket_denial)
    hp_digest = sha256_digest(human_api_use_preflight_gate)
    arep_digest = sha256_digest(api_request_envelope_preview)
    arqp_digest = sha256_digest(api_response_quarantine_preview)
    
    combined = ag_digest + acc_digest + cd_digest + sd_digest + nsd_digest + hp_digest + arep_digest + arqp_digest
    combined_digest = sha256_digest(combined)

    return {
        "api_audit_proof_version": "3.6.0",
        "audit_status": audit_status,
        "approval_gate_digest": ag_digest,
        "api_category_contract_digest": acc_digest,
        "credential_denial_digest": cd_digest,
        "secret_handling_denial_digest": sd_digest,
        "network_socket_denial_digest": nsd_digest,
        "human_api_use_preflight_gate_digest": hp_digest,
        "api_request_envelope_preview_digest": arep_digest,
        "api_response_quarantine_preview_digest": arqp_digest,
        "combined_api_audit_digest": combined_digest,
        "safety_checks": checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_api_pilot_ledger(
    approval_gate: dict,
    api_category_contract: dict,
    credential_denial: dict,
    secret_denial: dict,
    network_socket_denial: dict,
    human_api_use_preflight_gate: dict,
    api_request_envelope_preview: dict,
    api_response_quarantine_preview: dict,
    api_audit_proof: dict
) -> dict:
    status = "SUPERVISED_EXTERNAL_API_PILOT_LEDGER" if api_audit_proof.get("audit_status") == "PASS" else "BLOCKED"
    entries = [
        approval_gate,
        api_category_contract,
        credential_denial,
        secret_denial,
        network_socket_denial,
        human_api_use_preflight_gate,
        api_request_envelope_preview,
        api_response_quarantine_preview,
        api_audit_proof
    ]
    ledger_digest = sha256_digest([sha256_digest(e) for e in entries])
    
    return {
        "api_pilot_ledger_version": "3.6.0",
        "ledger_status": status,
        "entries": entries,
        "ledger_digest": ledger_digest,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False
    }

def create_api_pilot_readiness_summary(
    approval_gate: dict,
    api_category_contract: dict,
    api_audit_proof: dict,
    api_pilot_ledger: dict
) -> dict:
    ready = (
        approval_gate.get("confirmation_token_valid", False) and
        api_category_contract.get("contract_status") == "API_CATEGORY_CONTRACT_CREATED" and
        api_audit_proof.get("audit_status") == "PASS" and
        api_pilot_ledger.get("ledger_status") == "SUPERVISED_EXTERNAL_API_PILOT_LEDGER"
    )
    status = "READY_FOR_NEXT_LAYER" if ready else "BLOCKED"
    
    return {
        "api_pilot_readiness_summary_version": "3.6.0",
        "readiness_status": status,
        "ready_for_monitored_rollback_recovery_drill": ready,
        "gate_status": approval_gate.get("gate_status", "UNKNOWN"),
        "api_category_contract_status": api_category_contract.get("contract_status", "UNKNOWN"),
        "audit_status": api_audit_proof.get("audit_status", "UNKNOWN"),
        "ledger_status": api_pilot_ledger.get("ledger_status", "UNKNOWN"),
        "next_layer": "Monitored Rollback and Recovery Drill",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False
    }

def create_monitored_rollback_recovery_drill_bridge(
    result: dict,
    api_pilot_readiness_summary: dict
) -> dict:
    return {
        "monitored_rollback_recovery_drill_bridge_version": "3.6.0",
        "current_layer": "Supervised External API Pilot",
        "next_layer": "Monitored Rollback and Recovery Drill",
        "ready_for_monitored_rollback_recovery_drill": api_pilot_readiness_summary.get("ready_for_monitored_rollback_recovery_drill", False),
        "required_next_capabilities": [
            "monitored rollback and recovery drill schema",
            "simulated failure trigger contract",
            "rollback path preview",
            "recovery checkpoint contract",
            "quarantine and freeze preview",
            "human recovery approval gate",
            "recovery audit proof",
            "rollback recovery drill ledger"
        ],
        "non_goals_for_next_layer": [
            "no real rollback execution",
            "no real production state changes",
            "no live deployment rollback",
            "no process termination",
            "no credential use",
            "no secret reads",
            "no unsupervised orchestration",
            "no full workforce activation"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False
    }

def create_supervised_external_api_pilot_bundle(
    result: dict,
    command: str | None = None,
    api_pilot_label: str | None = None,
    confirmation_token: str | None = None,
    api_category_label: str | None = None,
    required_api_preflight_approver: str | None = None,
    api_request_label: str | None = None,
    quarantine_labels: list[str] | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if api_pilot_label is None:
        api_pilot_label = "station-chief-supervised-external-api-pilot"
        
    schema = create_supervised_external_api_pilot_schema()
    gate = create_supervised_external_api_pilot_approval_gate(api_pilot_label, confirmation_token)
    contract = create_single_api_category_contract(gate, api_category_label)
    cd = create_credential_denial_by_default(gate, contract)
    sd = create_secret_handling_denial_by_default(gate, contract)
    nsd = create_network_socket_denial_by_default(gate, contract)
    hpg = create_human_api_use_preflight_gate(gate, required_api_preflight_approver)
    arep = create_api_request_envelope_preview(gate, contract, api_request_label)
    arqp = create_api_response_quarantine_preview(gate, quarantine_labels)
    proof = create_api_audit_proof(gate, contract, cd, sd, nsd, hpg, arep, arqp)
    ledger = create_api_pilot_ledger(gate, contract, cd, sd, nsd, hpg, arep, arqp, proof)
    summary = create_api_pilot_readiness_summary(gate, contract, proof, ledger)
    bridge = create_monitored_rollback_recovery_drill_bridge(result, summary)
    
    return {
        "supervised_external_api_pilot_bundle_version": "3.6.0",
        "supervised_external_api_pilot_status": "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY",
        "supervised_external_api_pilot_schema": schema,
        "supervised_external_api_pilot_approval_gate": gate,
        "single_api_category_contract": contract,
        "credential_denial_by_default": cd,
        "secret_handling_denial_by_default": sd,
        "network_socket_denial_by_default": nsd,
        "human_api_use_preflight_gate": hpg,
        "api_request_envelope_preview": arep,
        "api_response_quarantine_preview": arqp,
        "api_audit_proof": proof,
        "api_pilot_ledger": ledger,
        "api_pilot_readiness_summary": summary,
        "monitored_rollback_recovery_drill_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }
