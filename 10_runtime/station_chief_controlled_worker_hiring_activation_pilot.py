import json
import hashlib

CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_MODULE_VERSION = "3.6.0"
CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_STATUS = "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY"
CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PHASE = "Controlled Worker Hiring Activation Pilot"
CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL_TOKEN = "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_pilot_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "controlled-worker-hiring-activation-pilot"
    return normalized

def generate_controlled_worker_hiring_activation_pilot_id(command: str, pilot_label: str, runtime_version: str = "3.6.0") -> str:
    norm_label = normalize_pilot_label(pilot_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"controlled-worker-hiring-activation-pilot-v3-6-{norm_label}-{digest}"

def create_controlled_worker_hiring_activation_pilot_schema() -> dict:
    return {
        "controlled_worker_hiring_activation_pilot_schema_version": "3.6.0",
        "schema_status": "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY",
        "required_sections": [
            "controlled_worker_hiring_activation_pilot_approval_gate",
            "pilot_worker_limit_contract",
            "worker_identity_activation_contract",
            "task_assignment_denial_by_default",
            "human_supervised_pilot_gate",
            "pilot_rollback_abort_preview",
            "pilot_audit_proof",
            "pilot_ledger",
            "pilot_readiness_summary",
            "first_supervised_production_dry_run_bridge"
        ],
        "allowed_pilot_modes": [
            "schema_only",
            "local_pilot_records",
            "approved_pilot_records",
            "worker_identity_contract_preview",
            "task_assignment_denial_preview",
            "rollback_abort_preview",
            "pilot_audit_preview"
        ],
        "blocked_pilot_modes": [
            "real_worker_hiring",
            "real_worker_activation",
            "worker_process_start",
            "live_task_assignment",
            "live_worker_routing",
            "live_orchestration",
            "production_execution",
            "production_activation",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "external_tool_replay",
            "live_api_call",
            "network_access",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "deployment",
            "full_workforce_activation"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"
        ],
        "pilot_worker_limit_min": 1,
        "pilot_worker_limit_max": 3,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "actual_replay_performed": False,
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

def create_controlled_worker_hiring_activation_pilot_approval_gate(
    pilot_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT")
    gate_status = "APPROVED_FOR_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_RECORDS" if token_valid else "BLOCKED_PENDING_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL"
    return {
        "controlled_worker_hiring_activation_pilot_approval_gate_version": "3.6.0",
        "pilot_label": pilot_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_pilot_records_authorized": token_valid,
        "real_worker_hiring_authorized": False,
        "real_worker_activation_authorized": False,
        "worker_process_start_authorized": False,
        "live_task_assignment_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "external_tool_invocation_authorized": False,
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

def create_pilot_worker_limit_contract(
    approval_gate: dict,
    pilot_worker_limit: int = 1
) -> dict:
    limit_valid = (1 <= pilot_worker_limit <= 3)
    contract_status = "PILOT_LIMIT_ACCEPTED" if (approval_gate.get("confirmation_token_valid") and limit_valid) else "BLOCKED"
    return {
        "pilot_worker_limit_contract_version": "3.6.0",
        "contract_status": contract_status,
        "pilot_worker_limit": pilot_worker_limit,
        "minimum_allowed": 1,
        "maximum_allowed": 3,
        "limit_valid": limit_valid,
        "broad_workforce_activation_allowed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "execution_authorized": False
    }

def create_worker_identity_activation_contract(
    approval_gate: dict,
    pilot_worker_limit_contract: dict,
    worker_labels: list[str] | None = None
) -> dict:
    limit = pilot_worker_limit_contract.get("pilot_worker_limit", 1)
    if worker_labels is None:
        worker_labels = [f"pilot-worker-{i+1:03}" for i in range(limit)]
    
    label_valid = (1 <= len(worker_labels) <= 3 and len(worker_labels) <= limit)
    contract_status = "IDENTITY_CONTRACTS_CREATED" if (approval_gate.get("confirmation_token_valid") and pilot_worker_limit_contract.get("contract_status") == "PILOT_LIMIT_ACCEPTED" and label_valid) else "BLOCKED"
    
    worker_identity_records = []
    if contract_status == "IDENTITY_CONTRACTS_CREATED":
        for label in worker_labels:
            worker_identity_records.append({
                "worker_id": f"pilot-{label}",
                "worker_label": label,
                "identity_status": "CONTRACT_ONLY",
                "real_worker_created": False,
                "worker_process_started": False,
                "live_task_assignment_allowed": False,
                "external_actions_taken": False
            })
            
    return {
        "worker_identity_activation_contract_version": "3.6.0",
        "contract_status": contract_status,
        "worker_identity_records": worker_identity_records,
        "worker_identity_count": len(worker_identity_records),
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "execution_authorized": False
    }

def create_task_assignment_denial_by_default(
    approval_gate: dict,
    worker_identity_contract: dict
) -> dict:
    denial_status = "TASK_ASSIGNMENT_DENIED_BY_DEFAULT" if (approval_gate.get("confirmation_token_valid") and worker_identity_contract.get("contract_status") == "IDENTITY_CONTRACTS_CREATED") else "BLOCKED"
    return {
        "task_assignment_denial_by_default_version": "3.6.0",
        "denial_status": denial_status,
        "task_assignment_default": "DENIED",
        "live_task_assignment_allowed": False,
        "queued_action_execution_allowed": False,
        "worker_execution_allowed": False,
        "production_execution_allowed": False,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "execution_authorized": False
    }

def create_human_supervised_pilot_gate(
    approval_gate: dict,
    required_supervisor_label: str | None = None
) -> dict:
    if required_supervisor_label is None:
        required_supervisor_label = "Devin O’Rourke / explicit human operator"
        
    supervision_status = "SUPERVISION_REQUIREMENT_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    return {
        "human_supervised_pilot_gate_version": "3.6.0",
        "supervision_status": supervision_status,
        "required_supervisor_label": required_supervisor_label,
        "human_supervision_required": True,
        "pilot_execution_authorized": False,
        "worker_execution_authorized": False,
        "production_execution_authorized": False,
        "approval_bypass_allowed": False,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_pilot_rollback_abort_preview(
    approval_gate: dict,
    rollback_labels: list[str] | None = None
) -> dict:
    if rollback_labels is None:
        rollback_labels = [
            "deny worker activation",
            "deny task assignment",
            "deny production execution",
            "require human operator review",
            "preserve audit ledger",
            "quarantine pilot records",
            "block external actions",
            "preserve locked baseline"
        ]
        
    preview_status = "PILOT_ROLLBACK_ABORT_PREVIEW_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    rollback_records = []
    for label in rollback_labels:
        rb_id = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        rollback_records.append({
            "rollback_id": rb_id,
            "rollback_label": label,
            "rollback_status": "PILOT_ABORT_PREVIEW_ONLY",
            "rollback_execution_performed": False
        })
        
    return {
        "pilot_rollback_abort_preview_version": "3.6.0",
        "preview_status": preview_status,
        "rollback_records": rollback_records,
        "rollback_record_count": len(rollback_records),
        "abort_preview_only": True,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rolled_back": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_pilot_audit_proof(
    approval_gate: dict,
    pilot_worker_limit_contract: dict,
    worker_identity_contract: dict,
    task_assignment_denial: dict,
    human_supervised_pilot_gate: dict,
    pilot_rollback_abort_preview: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        pilot_worker_limit_contract.get("contract_status") == "PILOT_LIMIT_ACCEPTED" and
        worker_identity_contract.get("contract_status") == "IDENTITY_CONTRACTS_CREATED" and
        task_assignment_denial.get("denial_status") == "TASK_ASSIGNMENT_DENIED_BY_DEFAULT" and
        human_supervised_pilot_gate.get("supervision_status") == "SUPERVISION_REQUIREMENT_CREATED" and
        pilot_rollback_abort_preview.get("preview_status") == "PILOT_ROLLBACK_ABORT_PREVIEW_CREATED"
    )
    audit_status = "PASS" if is_valid else "BLOCKED"
    
    gate_digest = sha256_digest(approval_gate)
    limit_digest = sha256_digest(pilot_worker_limit_contract)
    identity_digest = sha256_digest(worker_identity_contract)
    denial_digest = sha256_digest(task_assignment_denial)
    supervision_digest = sha256_digest(human_supervised_pilot_gate)
    rollback_digest = sha256_digest(pilot_rollback_abort_preview)
    
    combined_input = f"{gate_digest}:{limit_digest}:{identity_digest}:{denial_digest}:{supervision_digest}:{rollback_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": approval_gate.get("confirmation_token_valid", False),
        "pilot_worker_limit_accepted": pilot_worker_limit_contract.get("contract_status") == "PILOT_LIMIT_ACCEPTED",
        "worker_identity_contracts_created": worker_identity_contract.get("contract_status") == "IDENTITY_CONTRACTS_CREATED",
        "task_assignment_denied_by_default": task_assignment_denial.get("denial_status") == "TASK_ASSIGNMENT_DENIED_BY_DEFAULT",
        "human_supervision_required": human_supervised_pilot_gate.get("supervision_status") == "SUPERVISION_REQUIREMENT_CREATED",
        "rollback_abort_preview_created": pilot_rollback_abort_preview.get("preview_status") == "PILOT_ROLLBACK_ABORT_PREVIEW_CREATED",
        "no_real_worker_hiring": True,
        "no_real_worker_activation": True,
        "no_worker_processes_started": True,
        "no_live_task_assignment": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_production_execution": True,
        "no_production_activation": True,
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
        "pilot_audit_proof_version": "3.6.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "pilot_worker_limit_contract_digest": limit_digest,
        "worker_identity_activation_contract_digest": identity_digest,
        "task_assignment_denial_digest": denial_digest,
        "human_supervised_pilot_gate_digest": supervision_digest,
        "pilot_rollback_abort_preview_digest": rollback_digest,
        "combined_pilot_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
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

def create_pilot_ledger(
    approval_gate: dict,
    pilot_worker_limit_contract: dict,
    worker_identity_contract: dict,
    task_assignment_denial: dict,
    human_supervised_pilot_gate: dict,
    pilot_rollback_abort_preview: dict,
    pilot_audit_proof: dict
) -> dict:
    ledger_status = "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_LEDGER" if pilot_audit_proof.get("audit_status") == "PASS" else "BLOCKED"
    
    entries = [
        {"type": "controlled_worker_hiring_activation_pilot_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "pilot_worker_limit_contract", "digest": sha256_digest(pilot_worker_limit_contract)},
        {"type": "worker_identity_activation_contract", "digest": sha256_digest(worker_identity_contract)},
        {"type": "task_assignment_denial_by_default", "digest": sha256_digest(task_assignment_denial)},
        {"type": "human_supervised_pilot_gate", "digest": sha256_digest(human_supervised_pilot_gate)},
        {"type": "pilot_rollback_abort_preview", "digest": sha256_digest(pilot_rollback_abort_preview)},
        {"type": "pilot_audit_proof", "digest": sha256_digest(pilot_audit_proof)}
    ]
    
    return {
        "pilot_ledger_version": "3.6.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "execution_authorized": False
    }

def create_pilot_readiness_summary(
    approval_gate: dict,
    pilot_worker_limit_contract: dict,
    worker_identity_contract: dict,
    pilot_audit_proof: dict,
    pilot_ledger: dict
) -> dict:
    is_ready = (
        approval_gate.get("confirmation_token_valid", False) and
        pilot_worker_limit_contract.get("contract_status") == "PILOT_LIMIT_ACCEPTED" and
        worker_identity_contract.get("contract_status") == "IDENTITY_CONTRACTS_CREATED" and
        pilot_audit_proof.get("audit_status") == "PASS" and
        pilot_ledger.get("ledger_status") == "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_LEDGER"
    )
    
    return {
        "pilot_readiness_summary_version": "3.6.0",
        "readiness_status": "READY_FOR_NEXT_LAYER" if is_ready else "BLOCKED",
        "ready_for_first_supervised_production_dry_run": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "pilot_worker_limit_contract_status": pilot_worker_limit_contract.get("contract_status", "BLOCKED"),
        "worker_identity_contract_status": worker_identity_contract.get("contract_status", "BLOCKED"),
        "audit_status": pilot_audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": pilot_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "First Supervised Production Dry-Run",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "execution_authorized": False
    }

def create_first_supervised_production_dry_run_bridge(
    result: dict,
    pilot_readiness_summary: dict
) -> dict:
    is_ready = pilot_readiness_summary.get("ready_for_first_supervised_production_dry_run", False)
    return {
        "first_supervised_production_dry_run_bridge_version": "3.6.0",
        "current_layer": "Controlled Worker Hiring Activation Pilot",
        "next_layer": "First Supervised Production Dry-Run",
        "ready_for_first_supervised_production_dry_run": is_ready,
        "required_next_capabilities": [
            "first supervised production dry-run schema",
            "single controlled task dry-run envelope",
            "dry-run-only production context contract",
            "human preflight approval gate",
            "worker task simulation contract",
            "external action denial by default",
            "dry-run rollback and quarantine preview",
            "dry-run audit proof"
        ],
        "non_goals_for_next_layer": [
            "no real production execution",
            "no live external API execution",
            "no credential use",
            "no secret reads",
            "no full workforce activation",
            "no broad worker routing",
            "no autonomous deployment",
            "no unsupervised orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "execution_authorized": False
    }

def create_controlled_worker_hiring_activation_pilot_bundle(
    result: dict,
    command: str | None = None,
    pilot_label: str | None = None,
    confirmation_token: str | None = None,
    pilot_worker_limit: int = 1,
    worker_labels: list[str] | None = None,
    required_supervisor_label: str | None = None,
    rollback_labels: list[str] | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if pilot_label is None:
        pilot_label = "station-chief-controlled-worker-hiring-activation-pilot"
        
    schema = create_controlled_worker_hiring_activation_pilot_schema()
    gate = create_controlled_worker_hiring_activation_pilot_approval_gate(pilot_label, confirmation_token)
    limit_contract = create_pilot_worker_limit_contract(gate, pilot_worker_limit)
    identity_contract = create_worker_identity_activation_contract(gate, limit_contract, worker_labels)
    task_denial = create_task_assignment_denial_by_default(gate, identity_contract)
    human_gate = create_human_supervised_pilot_gate(gate, required_supervisor_label)
    rollback_preview = create_pilot_rollback_abort_preview(gate, rollback_labels)
    audit = create_pilot_audit_proof(gate, limit_contract, identity_contract, task_denial, human_gate, rollback_preview)
    ledger = create_pilot_ledger(gate, limit_contract, identity_contract, task_denial, human_gate, rollback_preview, audit)
    summary = create_pilot_readiness_summary(gate, limit_contract, identity_contract, audit, ledger)
    bridge = create_first_supervised_production_dry_run_bridge(result, summary)
    
    return {
        "controlled_worker_hiring_activation_pilot_bundle_version": "3.6.0",
        "controlled_worker_hiring_activation_pilot_status": "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY",
        "controlled_worker_hiring_activation_pilot_schema": schema,
        "controlled_worker_hiring_activation_pilot_approval_gate": gate,
        "pilot_worker_limit_contract": limit_contract,
        "worker_identity_activation_contract": identity_contract,
        "task_assignment_denial_by_default": task_denial,
        "human_supervised_pilot_gate": human_gate,
        "pilot_rollback_abort_preview": rollback_preview,
        "pilot_audit_proof": audit,
        "pilot_ledger": ledger,
        "pilot_readiness_summary": summary,
        "first_supervised_production_dry_run_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "external_tool_replay_performed": False,
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
