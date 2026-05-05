import json
import hashlib

FIRST_SUPERVISED_PRODUCTION_DRY_RUN_MODULE_VERSION = "3.5.0"
FIRST_SUPERVISED_PRODUCTION_DRY_RUN_STATUS = "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY"
FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PHASE = "First Supervised Production Dry-Run"
FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL_TOKEN = "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_dry_run_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "first-supervised-production-dry-run"
    return normalized

def generate_first_supervised_production_dry_run_id(command: str, dry_run_label: str, runtime_version: str = "3.5.0") -> str:
    norm_label = normalize_dry_run_label(dry_run_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"first-supervised-production-dry-run-v3-5-{norm_label}-{digest}"

def create_first_supervised_production_dry_run_schema() -> dict:
    return {
        "first_supervised_production_dry_run_schema_version": "3.5.0",
        "schema_status": "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY",
        "required_sections": [
            "first_supervised_production_dry_run_approval_gate",
            "single_controlled_task_dry_run_envelope",
            "dry_run_only_production_context_contract",
            "human_preflight_approval_gate",
            "worker_task_simulation_contract",
            "external_action_denial_by_default",
            "dry_run_rollback_quarantine_preview",
            "dry_run_audit_proof",
            "dry_run_ledger",
            "dry_run_readiness_summary",
            "limited_external_tool_supervised_pilot_bridge"
        ],
        "allowed_dry_run_modes": [
            "schema_only",
            "local_dry_run_records",
            "approved_dry_run_records",
            "single_task_envelope_preview",
            "production_context_contract_preview",
            "worker_task_simulation_preview",
            "external_action_denial_preview",
            "rollback_quarantine_preview",
            "dry_run_audit_preview"
        ],
        "blocked_dry_run_modes": [
            "real_production_execution",
            "production_activation",
            "real_task_execution",
            "live_task_assignment",
            "live_worker_routing",
            "live_orchestration",
            "external_tool_invocation",
            "live_api_call",
            "network_access",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "deployment",
            "worker_process_start",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "full_workforce_activation"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"
        ],
        "single_task_limit": 1,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_first_supervised_production_dry_run_approval_gate(
    dry_run_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN")
    gate_status = "APPROVED_FOR_FIRST_SUPERVISED_PRODUCTION_DRY_RUN_RECORDS" if token_valid else "BLOCKED_PENDING_FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL"
    return {
        "first_supervised_production_dry_run_approval_gate_version": "3.5.0",
        "dry_run_label": dry_run_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_dry_run_records_authorized": token_valid,
        "real_production_execution_authorized": False,
        "production_activation_authorized": False,
        "real_task_execution_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "external_tool_invocation_authorized": False,
        "live_api_call_authorized": False,
        "network_access_authorized": False,
        "socket_access_authorized": False,
        "credential_use_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "deployment_authorized": False,
        "worker_process_start_authorized": False,
        "repo_mutation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_single_controlled_task_dry_run_envelope(
    approval_gate: dict,
    dry_run_task_label: str | None = None
) -> dict:
    if dry_run_task_label is None:
        dry_run_task_label = "single controlled production dry-run task"
    
    is_valid = approval_gate.get("confirmation_token_valid", False)
    envelope_status = "ENVELOPE_CREATED" if is_valid else "BLOCKED"
    
    return {
        "single_controlled_task_dry_run_envelope_version": "3.5.0",
        "envelope_status": envelope_status,
        "dry_run_task_label": dry_run_task_label,
        "single_task_limit": 1,
        "task_count": 1 if is_valid else 0,
        "dry_run_only": True,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "production_execution_performed": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_dry_run_only_production_context_contract(
    approval_gate: dict,
    task_envelope: dict,
    production_context_label: str | None = None
) -> dict:
    if production_context_label is None:
        production_context_label = "production-like context, dry-run only"
    
    is_valid = (approval_gate.get("confirmation_token_valid", False) and 
                task_envelope.get("envelope_status") == "ENVELOPE_CREATED")
    contract_status = "CONTRACT_CREATED" if is_valid else "BLOCKED"
    
    return {
        "dry_run_only_production_context_contract_version": "3.5.0",
        "contract_status": contract_status,
        "production_context_label": production_context_label,
        "production_like_context_allowed_for_preview": is_valid,
        "real_production_execution_allowed": False,
        "production_activation_allowed": False,
        "live_external_actions_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "deployment_allowed": False,
        "execution_authorized": False
    }

def create_human_preflight_approval_gate(
    approval_gate: dict,
    required_preflight_approver: str | None = None
) -> dict:
    if required_preflight_approver is None:
        required_preflight_approver = "Devin O’Rourke / explicit human operator"
    
    is_valid = approval_gate.get("confirmation_token_valid", False)
    preflight_status = "PREFLIGHT_REQUIREMENT_CREATED" if is_valid else "BLOCKED"
    
    return {
        "human_preflight_approval_gate_version": "3.5.0",
        "preflight_status": preflight_status,
        "required_preflight_approver": required_preflight_approver,
        "human_preflight_required": True,
        "current_preflight_grants_execution": False,
        "production_execution_authorized": False,
        "live_external_action_authorized": False,
        "approval_bypass_allowed": False,
        "execution_authorized": False
    }

def create_worker_task_simulation_contract(
    approval_gate: dict,
    task_envelope: dict,
    worker_label: str | None = None
) -> dict:
    if worker_label is None:
        worker_label = "simulated-pilot-worker-001"
    
    is_valid = (approval_gate.get("confirmation_token_valid", False) and 
                task_envelope.get("envelope_status") == "ENVELOPE_CREATED")
    simulation_status = "SIMULATION_CONTRACT_CREATED" if is_valid else "BLOCKED"
    
    return {
        "worker_task_simulation_contract_version": "3.5.0",
        "simulation_status": simulation_status,
        "worker_label": worker_label,
        "simulated_task_assignment_created": is_valid,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "task_execution_performed": False,
        "production_execution_performed": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_external_action_denial_by_default(
    approval_gate: dict
) -> dict:
    is_valid = approval_gate.get("confirmation_token_valid", False)
    denial_status = "EXTERNAL_ACTIONS_DENIED_BY_DEFAULT" if is_valid else "BLOCKED"
    
    return {
        "external_action_denial_by_default_version": "3.5.0",
        "denial_status": denial_status,
        "external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "shell_command_allowed": False,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_dry_run_rollback_quarantine_preview(
    approval_gate: dict,
    quarantine_labels: list[str] | None = None
) -> dict:
    if quarantine_labels is None:
        quarantine_labels = [
            "quarantine dry-run task envelope",
            "deny external actions",
            "deny production execution",
            "require human review",
            "preserve dry-run audit ledger",
            "preserve locked baseline"
        ]
    
    is_valid = approval_gate.get("confirmation_token_valid", False)
    preview_status = "ROLLBACK_QUARANTINE_PREVIEW_CREATED" if is_valid else "BLOCKED"
    
    quarantine_records = []
    for label in quarantine_labels:
        rec_id = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        quarantine_records.append({
            "record_id": rec_id,
            "label": label,
            "status": "PREVIEW_ONLY"
        })
    
    return {
        "dry_run_rollback_quarantine_preview_version": "3.5.0",
        "preview_status": preview_status,
        "quarantine_records": quarantine_records,
        "quarantine_record_count": len(quarantine_records),
        "quarantine_preview_only": True,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rolled_back": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_dry_run_audit_proof(
    approval_gate: dict,
    task_envelope: dict,
    production_context_contract: dict,
    human_preflight_gate: dict,
    worker_task_simulation_contract: dict,
    external_action_denial: dict,
    rollback_quarantine_preview: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        task_envelope.get("envelope_status") == "ENVELOPE_CREATED" and
        production_context_contract.get("contract_status") == "CONTRACT_CREATED" and
        human_preflight_gate.get("preflight_status") == "PREFLIGHT_REQUIREMENT_CREATED" and
        worker_task_simulation_contract.get("simulation_status") == "SIMULATION_CONTRACT_CREATED" and
        external_action_denial.get("denial_status") == "EXTERNAL_ACTIONS_DENIED_BY_DEFAULT" and
        rollback_quarantine_preview.get("preview_status") == "ROLLBACK_QUARANTINE_PREVIEW_CREATED"
    )
    audit_status = "PASS" if is_valid else "BLOCKED"
    
    gate_digest = sha256_digest(approval_gate)
    envelope_digest = sha256_digest(task_envelope)
    context_digest = sha256_digest(production_context_contract)
    preflight_digest = sha256_digest(human_preflight_gate)
    simulation_digest = sha256_digest(worker_task_simulation_contract)
    denial_digest = sha256_digest(external_action_denial)
    rollback_digest = sha256_digest(rollback_quarantine_preview)
    
    combined_input = f"{gate_digest}:{envelope_digest}:{context_digest}:{preflight_digest}:{simulation_digest}:{denial_digest}:{rollback_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": approval_gate.get("confirmation_token_valid", False),
        "single_controlled_task_envelope_created": task_envelope.get("envelope_status") == "ENVELOPE_CREATED",
        "dry_run_only_production_context_contract_created": production_context_contract.get("contract_status") == "CONTRACT_CREATED",
        "human_preflight_required": human_preflight_gate.get("preflight_status") == "PREFLIGHT_REQUIREMENT_CREATED",
        "worker_task_simulation_contract_created": worker_task_simulation_contract.get("simulation_status") == "SIMULATION_CONTRACT_CREATED",
        "external_actions_denied_by_default": external_action_denial.get("denial_status") == "EXTERNAL_ACTIONS_DENIED_BY_DEFAULT",
        "rollback_quarantine_preview_created": rollback_quarantine_preview.get("preview_status") == "ROLLBACK_QUARANTINE_PREVIEW_CREATED",
        "no_real_production_execution": True,
        "no_production_activation": True,
        "no_real_task_execution": True,
        "no_live_task_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_external_tool_invocation": True,
        "no_live_api_call": True,
        "no_network_access": True,
        "no_socket_opened": True,
        "no_credentials_used": True,
        "no_secrets_read": True,
        "no_environment_read": True,
        "no_deployment": True,
        "no_repo_modifications": True
    }
    
    return {
        "dry_run_audit_proof_version": "3.5.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "task_envelope_digest": envelope_digest,
        "production_context_contract_digest": context_digest,
        "human_preflight_gate_digest": preflight_digest,
        "worker_task_simulation_contract_digest": simulation_digest,
        "external_action_denial_digest": denial_digest,
        "rollback_quarantine_preview_digest": rollback_digest,
        "combined_dry_run_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_dry_run_ledger(
    approval_gate: dict,
    task_envelope: dict,
    production_context_contract: dict,
    human_preflight_gate: dict,
    worker_task_simulation_contract: dict,
    external_action_denial: dict,
    rollback_quarantine_preview: dict,
    dry_run_audit_proof: dict
) -> dict:
    is_valid = dry_run_audit_proof.get("audit_status") == "PASS"
    ledger_status = "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_LEDGER" if is_valid else "BLOCKED"
    
    entries = [
        {"type": "first_supervised_production_dry_run_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "single_controlled_task_dry_run_envelope", "digest": sha256_digest(task_envelope)},
        {"type": "dry_run_only_production_context_contract", "digest": sha256_digest(production_context_contract)},
        {"type": "human_preflight_approval_gate", "digest": sha256_digest(human_preflight_gate)},
        {"type": "worker_task_simulation_contract", "digest": sha256_digest(worker_task_simulation_contract)},
        {"type": "external_action_denial_by_default", "digest": sha256_digest(external_action_denial)},
        {"type": "dry_run_rollback_quarantine_preview", "digest": sha256_digest(rollback_quarantine_preview)},
        {"type": "dry_run_audit_proof", "digest": sha256_digest(dry_run_audit_proof)}
    ]
    
    return {
        "dry_run_ledger_version": "3.5.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_dry_run_readiness_summary(
    approval_gate: dict,
    task_envelope: dict,
    dry_run_audit_proof: dict,
    dry_run_ledger: dict
) -> dict:
    is_ready = (
        approval_gate.get("confirmation_token_valid", False) and
        task_envelope.get("envelope_status") == "ENVELOPE_CREATED" and
        dry_run_audit_proof.get("audit_status") == "PASS" and
        dry_run_ledger.get("ledger_status") == "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_LEDGER"
    )
    
    return {
        "dry_run_readiness_summary_version": "3.5.0",
        "readiness_status": "READY_FOR_NEXT_LAYER" if is_ready else "BLOCKED",
        "ready_for_limited_external_tool_supervised_pilot": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "task_envelope_status": task_envelope.get("envelope_status", "BLOCKED"),
        "audit_status": dry_run_audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": dry_run_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "Limited External Tool Supervised Pilot",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_limited_external_tool_supervised_pilot_bridge(
    result: dict,
    dry_run_readiness_summary: dict
) -> dict:
    is_ready = dry_run_readiness_summary.get("ready_for_limited_external_tool_supervised_pilot", False)
    
    return {
        "limited_external_tool_supervised_pilot_bridge_version": "3.5.0",
        "current_layer": "First Supervised Production Dry-Run",
        "next_layer": "Limited External Tool Supervised Pilot",
        "ready_for_limited_external_tool_supervised_pilot": is_ready,
        "required_next_capabilities": [
            "limited external tool supervised pilot schema",
            "single approved external tool category",
            "tool invocation denied by default",
            "human tool-use preflight gate",
            "tool request envelope preview",
            "tool response quarantine preview",
            "tool audit proof",
            "tool pilot ledger"
        ],
        "non_goals_for_next_layer": [
            "no uncontrolled external tool access",
            "no live-API credentials",
            "no secret reads",
            "no broad worker routing",
            "no autonomous deployment",
            "no unsupervised orchestration",
            "no full workforce activation"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_first_supervised_production_dry_run_bundle(
    result: dict,
    command: str | None = None,
    dry_run_label: str | None = None,
    confirmation_token: str | None = None,
    dry_run_task_label: str | None = None,
    production_context_label: str | None = None,
    required_preflight_approver: str | None = None,
    worker_label: str | None = None,
    quarantine_labels: list[str] | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if dry_run_label is None:
        dry_run_label = "station-chief-first-supervised-production-dry-run"
        
    schema = create_first_supervised_production_dry_run_schema()
    gate = create_first_supervised_production_dry_run_approval_gate(dry_run_label, confirmation_token)
    envelope = create_single_controlled_task_dry_run_envelope(gate, dry_run_task_label)
    context = create_dry_run_only_production_context_contract(gate, envelope, production_context_label)
    preflight = create_human_preflight_approval_gate(gate, required_preflight_approver)
    simulation = create_worker_task_simulation_contract(gate, envelope, worker_label)
    denial = create_external_action_denial_by_default(gate)
    rollback = create_dry_run_rollback_quarantine_preview(gate, quarantine_labels)
    audit = create_dry_run_audit_proof(gate, envelope, context, preflight, simulation, denial, rollback)
    ledger = create_dry_run_ledger(gate, envelope, context, preflight, simulation, denial, rollback, audit)
    summary = create_dry_run_readiness_summary(gate, envelope, audit, ledger)
    bridge = create_limited_external_tool_supervised_pilot_bridge(result, summary)
    
    return {
        "first_supervised_production_dry_run_bundle_version": "3.5.0",
        "first_supervised_production_dry_run_status": "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY",
        "first_supervised_production_dry_run_schema": schema,
        "first_supervised_production_dry_run_approval_gate": gate,
        "single_controlled_task_dry_run_envelope": envelope,
        "dry_run_only_production_context_contract": context,
        "human_preflight_approval_gate": preflight,
        "worker_task_simulation_contract": simulation,
        "external_action_denial_by_default": denial,
        "dry_run_rollback_quarantine_preview": rollback,
        "dry_run_audit_proof": audit,
        "dry_run_ledger": ledger,
        "dry_run_readiness_summary": summary,
        "limited_external_tool_supervised_pilot_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }
