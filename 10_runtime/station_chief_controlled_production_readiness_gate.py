import json
import hashlib

CONTROLLED_PRODUCTION_READINESS_GATE_MODULE_VERSION = "3.6.0"
CONTROLLED_PRODUCTION_READINESS_GATE_STATUS = "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY"
CONTROLLED_PRODUCTION_READINESS_GATE_PHASE = "Controlled Production Readiness Gate"
CONTROLLED_PRODUCTION_READINESS_GATE_APPROVAL_TOKEN = "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_production_gate_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "controlled-production-readiness-gate"
    return normalized

def generate_controlled_production_readiness_gate_id(command: str, production_gate_label: str, runtime_version: str = "3.6.0") -> str:
    norm_label = normalize_production_gate_label(production_gate_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"controlled-production-readiness-gate-v3-6-{norm_label}-{digest}"

def create_controlled_production_readiness_gate_schema() -> dict:
    return {
        "controlled_production_readiness_gate_schema_version": "3.6.0",
        "schema_status": "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY",
        "required_sections": [
            "controlled_production_readiness_gate_approval_gate",
            "production_activation_denial_by_default",
            "final_human_approval_requirement",
            "production_capability_manifest",
            "supervised_pilot_eligibility_contract",
            "production_rollback_kill_switch_preview",
            "production_readiness_audit_proof",
            "production_readiness_ledger",
            "production_readiness_summary",
            "controlled_worker_hiring_activation_pilot_bridge"
        ],
        "allowed_gate_modes": [
            "schema_only",
            "local_production_readiness_gate_records",
            "approved_production_readiness_gate_records",
            "production_activation_denial_preview",
            "final_human_approval_requirement_preview",
            "production_capability_manifest_preview",
            "supervised_pilot_eligibility_preview",
            "rollback_kill_switch_preview",
            "production_readiness_audit_preview"
        ],
        "blocked_gate_modes": [
            "production_execution",
            "production_activation",
            "real_worker_hiring",
            "real_worker_activation",
            "live_worker_routing",
            "live_orchestration",
            "automatic_execution",
            "queued_action_execution",
            "auto_approval",
            "approval_bypass",
            "actual_replay_execution",
            "worker_action_reexecution",
            "external_tool_replay",
            "live_api_replay",
            "network_replay",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "repo_mutating_production_action",
            "deployment_production_action",
            "background_production_process",
            "autonomous_retry",
            "full_workforce_activation"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"
        ],
        "safety_invariants": [
            "production readiness records only",
            "no production execution",
            "no production activation",
            "no real worker hiring",
            "no real worker activation",
            "no live worker routing",
            "no live orchestration",
            "no automatic execution",
            "no queued action execution",
            "no auto-approval",
            "no approval bypass",
            "no actual replay execution",
            "no worker action re-execution",
            "no external tool replay",
            "no live-API replay",
            "no network access",
            "no socket access",
            "no credential use",
            "no secret reads",
            "no environment reads",
            "no shell commands",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "controlled production readiness gate does not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
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

def create_controlled_production_readiness_gate_approval_gate(
    production_gate_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE")
    gate_status = "APPROVED_FOR_CONTROLLED_PRODUCTION_READINESS_GATE_RECORDS" if token_valid else "BLOCKED_PENDING_CONTROLLED_PRODUCTION_READINESS_GATE_APPROVAL"
    return {
        "controlled_production_readiness_gate_approval_gate_version": "3.6.0",
        "production_gate_label": production_gate_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_production_readiness_gate_records_authorized": token_valid,
        "production_execution_authorized": False,
        "production_activation_authorized": False,
        "real_worker_hiring_authorized": False,
        "real_worker_activation_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "automatic_execution_authorized": False,
        "queued_action_execution_authorized": False,
        "auto_approval_authorized": False,
        "approval_bypass_authorized": False,
        "actual_replay_authorized": False,
        "worker_action_reexecution_authorized": False,
        "external_tool_replay_authorized": False,
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

def create_production_activation_denial_by_default(
    approval_gate: dict
) -> dict:
    denial_status = "PRODUCTION_ACTIVATION_DENIED_BY_DEFAULT" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    return {
        "production_activation_denial_by_default_version": "3.6.0",
        "denial_status": denial_status,
        "production_activation_default": "DENIED",
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "requires_future_explicit_human_production_activation_gate": True,
        "token_does_not_activate_production": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_final_human_approval_requirement(
    approval_gate: dict,
    required_approver_label: str | None = None
) -> dict:
    if required_approver_label is None:
        required_approver_label = "Devin O’Rourke / explicit human operator"
        
    requirement_status = "REQUIREMENT_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    return {
        "final_human_approval_requirement_version": "3.6.0",
        "requirement_status": requirement_status,
        "required_approver_label": required_approver_label,
        "future_final_human_approval_required": True,
        "current_human_approval_grants_execution": False,
        "production_activation_authorized": False,
        "production_execution_authorized": False,
        "approval_bypass_allowed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_production_capability_manifest(
    approval_gate: dict,
    capability_labels: list[str] | None = None
) -> dict:
    if capability_labels is None:
        capability_labels = [
            "command classification",
            "overlay loading",
            "deterministic artifact writing",
            "registry and resume",
            "approval handoff",
            "controlled execution profiles",
            "work order executor dry-run",
            "worker hiring registry preview",
            "department routing preview",
            "multi-agent orchestration sandbox",
            "operator console schema",
            "GitHub patch hardening preview",
            "deployment packaging preview",
            "controlled worker execution preview",
            "tool permission binding preview",
            "live telemetry abort preview",
            "post-run audit expansion",
            "multi-worker sandbox coordination",
            "controlled external tool adapter preview",
            "permissioned external API dry-run preview",
            "controlled multi-worker audit replay preview",
            "operator approval queue enforcement",
            "release candidate hardening",
            "controlled production readiness gate"
        ]
        
    manifest_status = "MANIFEST_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    capability_records = []
    for cap in capability_labels:
        cap_id = "".join(c if c.isalnum() else "_" for c in cap.lower()).strip("_")
        capability_records.append({
            "capability_id": cap_id,
            "capability_label": cap,
            "capability_status": "AVAILABLE_FOR_PREVIEW_RECORDS_ONLY",
            "production_execution_enabled": False,
            "live_external_actions_enabled": False
        })
        
    return {
        "production_capability_manifest_version": "3.6.0",
        "manifest_status": manifest_status,
        "capability_records": capability_records,
        "capability_count": len(capability_records),
        "manifest_digest": sha256_digest(capability_records),
        "production_execution_enabled": False,
        "live_external_actions_enabled": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_supervised_pilot_eligibility_contract(
    approval_gate: dict,
    pilot_label: str | None = None,
    pilot_worker_limit: int = 1
) -> dict:
    if pilot_label is None:
        pilot_label = "controlled worker hiring activation pilot"
        
    limit_valid = (1 <= pilot_worker_limit <= 3)
    eligibility_status = "ELIGIBLE_FOR_FUTURE_SUPERVISED_PILOT_RECORDS" if (approval_gate.get("confirmation_token_valid") and limit_valid) else "BLOCKED"
    
    return {
        "supervised_pilot_eligibility_contract_version": "3.6.0",
        "eligibility_status": eligibility_status,
        "pilot_label": pilot_label,
        "pilot_worker_limit": pilot_worker_limit,
        "future_supervised_pilot_allowed_for_review": approval_gate.get("confirmation_token_valid", False) and limit_valid,
        "pilot_started": False,
        "real_workers_hired": False,
        "real_workers_activated": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "requires_v3_1_controlled_worker_hiring_activation_pilot": True,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_production_rollback_kill_switch_preview(
    approval_gate: dict,
    rollback_labels: list[str] | None = None
) -> dict:
    if rollback_labels is None:
        rollback_labels = [
            "deny production activation",
            "disable supervised pilot eligibility",
            "require human operator review",
            "preserve audit ledger",
            "block live external actions",
            "block worker activation",
            "block deployment",
            "preserve locked baseline"
        ]
        
    preview_status = "ROLLBACK_KILL_SWITCH_PREVIEW_CREATED" if approval_gate.get("confirmation_token_valid") else "BLOCKED"
    
    rollback_records = []
    for rb in rollback_labels:
        rb_id = "".join(c if c.isalnum() else "_" for c in rb.lower()).strip("_")
        rollback_records.append({
            "rollback_id": rb_id,
            "rollback_label": rb,
            "rollback_status": "READY_FOR_PREVIEW_ONLY",
            "rollback_execution_performed": False
        })
        
    return {
        "production_rollback_kill_switch_preview_version": "3.6.0",
        "preview_status": preview_status,
        "rollback_records": rollback_records,
        "rollback_record_count": len(rollback_records),
        "kill_switch_preview_only": True,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rolled_back": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_production_readiness_audit_proof(
    approval_gate: dict,
    activation_denial: dict,
    human_approval_requirement: dict,
    capability_manifest: dict,
    pilot_eligibility_contract: dict,
    rollback_kill_switch_preview: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        activation_denial.get("denial_status") == "PRODUCTION_ACTIVATION_DENIED_BY_DEFAULT" and
        human_approval_requirement.get("requirement_status") == "REQUIREMENT_CREATED" and
        capability_manifest.get("manifest_status") == "MANIFEST_CREATED" and
        pilot_eligibility_contract.get("eligibility_status") == "ELIGIBLE_FOR_FUTURE_SUPERVISED_PILOT_RECORDS" and
        rollback_kill_switch_preview.get("preview_status") == "ROLLBACK_KILL_SWITCH_PREVIEW_CREATED"
    )
    audit_status = "PASS" if is_valid else "BLOCKED"
    
    gate_digest = sha256_digest(approval_gate)
    denial_digest = sha256_digest(activation_denial)
    human_digest = sha256_digest(human_approval_requirement)
    cap_digest = sha256_digest(capability_manifest)
    pilot_digest = sha256_digest(pilot_eligibility_contract)
    rollback_digest = sha256_digest(rollback_kill_switch_preview)
    
    combined_input = f"{gate_digest}:{denial_digest}:{human_digest}:{cap_digest}:{pilot_digest}:{rollback_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": approval_gate.get("confirmation_token_valid", False),
        "production_activation_denied_by_default": activation_denial.get("denial_status") == "PRODUCTION_ACTIVATION_DENIED_BY_DEFAULT",
        "final_human_approval_required": human_approval_requirement.get("requirement_status") == "REQUIREMENT_CREATED",
        "capability_manifest_created": capability_manifest.get("manifest_status") == "MANIFEST_CREATED",
        "supervised_pilot_eligibility_contract_created": pilot_eligibility_contract.get("eligibility_status") == "ELIGIBLE_FOR_FUTURE_SUPERVISED_PILOT_RECORDS",
        "rollback_kill_switch_preview_created": rollback_kill_switch_preview.get("preview_status") == "ROLLBACK_KILL_SWITCH_PREVIEW_CREATED",
        "no_production_execution": True,
        "no_production_activation": True,
        "no_real_worker_hiring": True,
        "no_real_worker_activation": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
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
        "production_readiness_audit_proof_version": "3.6.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "activation_denial_digest": denial_digest,
        "human_approval_requirement_digest": human_digest,
        "capability_manifest_digest": cap_digest,
        "pilot_eligibility_contract_digest": pilot_digest,
        "rollback_kill_switch_preview_digest": rollback_digest,
        "combined_production_readiness_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
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

def create_production_readiness_ledger(
    approval_gate: dict,
    activation_denial: dict,
    human_approval_requirement: dict,
    capability_manifest: dict,
    pilot_eligibility_contract: dict,
    rollback_kill_switch_preview: dict,
    audit_proof: dict
) -> dict:
    ledger_status = "CONTROLLED_PRODUCTION_READINESS_GATE_LEDGER" if audit_proof.get("audit_status") == "PASS" else "BLOCKED"
    
    entries = [
        {"type": "controlled_production_readiness_gate_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "production_activation_denial", "digest": sha256_digest(activation_denial)},
        {"type": "final_human_approval_requirement", "digest": sha256_digest(human_approval_requirement)},
        {"type": "production_capability_manifest", "digest": sha256_digest(capability_manifest)},
        {"type": "supervised_pilot_eligibility_contract", "digest": sha256_digest(pilot_eligibility_contract)},
        {"type": "production_rollback_kill_switch_preview", "digest": sha256_digest(rollback_kill_switch_preview)},
        {"type": "production_readiness_audit_proof", "digest": sha256_digest(audit_proof)}
    ]
    
    return {
        "production_readiness_ledger_version": "3.6.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_production_readiness_summary(
    approval_gate: dict,
    activation_denial: dict,
    audit_proof: dict,
    production_readiness_ledger: dict
) -> dict:
    is_ready = (
        approval_gate.get("confirmation_token_valid", False) and
        activation_denial.get("denial_status") == "PRODUCTION_ACTIVATION_DENIED_BY_DEFAULT" and
        audit_proof.get("audit_status") == "PASS" and
        production_readiness_ledger.get("ledger_status") == "CONTROLLED_PRODUCTION_READINESS_GATE_LEDGER"
    )
    
    return {
        "production_readiness_summary_version": "3.6.0",
        "readiness_status": "READY_FOR_NEXT_LAYER" if is_ready else "BLOCKED",
        "ready_for_controlled_worker_hiring_activation_pilot": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "activation_denial_status": activation_denial.get("denial_status", "BLOCKED"),
        "audit_status": audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": production_readiness_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "Controlled Worker Hiring Activation Pilot",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_worker_hiring_activation_pilot_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    is_ready = readiness_summary.get("ready_for_controlled_worker_hiring_activation_pilot", False)
    return {
        "controlled_worker_hiring_activation_pilot_bridge_version": "3.6.0",
        "current_layer": "Controlled Production Readiness Gate",
        "next_layer": "Controlled Worker Hiring Activation Pilot",
        "ready_for_controlled_worker_hiring_activation_pilot": is_ready,
        "required_next_capabilities": [
            "controlled worker hiring activation pilot schema",
            "one-to-three worker pilot limit",
            "worker identity activation contract",
            "task assignment denial by default",
            "human-supervised pilot approval gate",
            "pilot rollback and abort preview",
            "pilot audit proof",
            "still no broad workforce activation"
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no credential use",
            "no secret reads",
            "no automatic approval",
            "no queued action execution",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no unsupervised production orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_production_readiness_gate_bundle(
    result: dict,
    command: str | None = None,
    production_gate_label: str | None = None,
    confirmation_token: str | None = None,
    required_approver_label: str | None = None,
    capability_labels: list[str] | None = None,
    pilot_label: str | None = None,
    pilot_worker_limit: int = 1,
    rollback_labels: list[str] | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if production_gate_label is None:
        production_gate_label = "station-chief-controlled-production-readiness-gate"
        
    schema = create_controlled_production_readiness_gate_schema()
    gate = create_controlled_production_readiness_gate_approval_gate(production_gate_label, confirmation_token)
    denial = create_production_activation_denial_by_default(gate)
    human_req = create_final_human_approval_requirement(gate, required_approver_label)
    cap_manifest = create_production_capability_manifest(gate, capability_labels)
    pilot_eligibility = create_supervised_pilot_eligibility_contract(gate, pilot_label, pilot_worker_limit)
    rollback_preview = create_production_rollback_kill_switch_preview(gate, rollback_labels)
    audit = create_production_readiness_audit_proof(gate, denial, human_req, cap_manifest, pilot_eligibility, rollback_preview)
    ledger = create_production_readiness_ledger(gate, denial, human_req, cap_manifest, pilot_eligibility, rollback_preview, audit)
    summary = create_production_readiness_summary(gate, denial, audit, ledger)
    bridge = create_controlled_worker_hiring_activation_pilot_bridge(result, summary)
    
    return {
        "controlled_production_readiness_gate_bundle_version": "3.6.0",
        "controlled_production_readiness_gate_status": "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY",
        "controlled_production_readiness_gate_schema": schema,
        "controlled_production_readiness_gate_approval_gate": gate,
        "production_activation_denial_by_default": denial,
        "final_human_approval_requirement": human_req,
        "production_capability_manifest": cap_manifest,
        "supervised_pilot_eligibility_contract": pilot_eligibility,
        "production_rollback_kill_switch_preview": rollback_preview,
        "production_readiness_audit_proof": audit,
        "production_readiness_ledger": ledger,
        "production_readiness_summary": summary,
        "controlled_worker_hiring_activation_pilot_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "worker_processes_started": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
