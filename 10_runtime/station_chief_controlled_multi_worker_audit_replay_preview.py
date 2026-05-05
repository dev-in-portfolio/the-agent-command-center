import json
import hashlib

CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_MODULE_VERSION = "3.6.0"
CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_STATUS = "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_ONLY"
CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_PHASE = "Controlled Multi-Worker Audit Replay Preview"
CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_APPROVAL_TOKEN = "YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_replay_label(label: str) -> str:
    normalized = "".join(c if c.isalnum() else "-" for c in label.lower())
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-")
    if not normalized:
        return "controlled-multi-worker-audit-replay-preview"
    return normalized

def generate_audit_replay_preview_id(command: str, replay_label: str, runtime_version: str = "3.6.0") -> str:
    norm_label = normalize_replay_label(replay_label)
    digest_input = f"{runtime_version}:{command}:{norm_label}"
    digest = sha256_digest(digest_input)[:12]
    return f"audit-replay-preview-v3-6-{norm_label}-{digest}"

def create_controlled_multi_worker_audit_replay_preview_schema() -> dict:
    return {
        "controlled_multi_worker_audit_replay_preview_schema_version": "3.6.0",
        "schema_status": "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_ONLY",
        "required_sections": [
            "audit_replay_preview_approval_gate",
            "replay_packet_registry",
            "deterministic_replay_plan_contract",
            "replay_safety_gate",
            "multi_worker_replay_comparison_proof",
            "replay_output_quarantine_contract",
            "replay_audit_proof",
            "replay_preview_ledger",
            "replay_readiness_summary",
            "operator_approval_queue_enforcement_readiness_bridge"
        ],
        "allowed_preview_modes": [
            "schema_only",
            "local_replay_preview_records",
            "approved_replay_preview_records",
            "replay_packet_registry_preview",
            "deterministic_replay_plan_preview",
            "replay_comparison_preview",
            "replay_quarantine_record_preview",
            "replay_audit_preview"
        ],
        "blocked_preview_modes": [
            "actual_replay_execution",
            "worker_action_reexecution",
            "external_tool_replay",
            "live_api_replay",
            "network_replay",
            "socket_connection",
            "credential_use",
            "secret_read",
            "environment_variable_read",
            "repo_mutating_replay",
            "deployment_replay",
            "background_replay_process",
            "autonomous_retry_replay",
            "production_replay_execution"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW"
        ],
        "safety_invariants": [
            "preview records only",
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
            "no live orchestration",
            "replay preview does not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
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

def create_audit_replay_preview_approval_gate(
    replay_label: str,
    confirmation_token: str | None = None
) -> dict:
    token_valid = (confirmation_token == "YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW")
    gate_status = "APPROVED_FOR_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_RECORDS" if token_valid else "BLOCKED_PENDING_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_APPROVAL"
    return {
        "audit_replay_preview_approval_gate_version": "3.6.0",
        "replay_label": replay_label,
        "gate_status": gate_status,
        "confirmation_token_required": "YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW",
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_replay_preview_records_authorized": token_valid,
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

def create_replay_packet_registry(
    approval_gate: dict,
    replay_packets: list[dict] | None = None,
    requested_worker_count: int = 3
) -> dict:
    if replay_packets is None:
        replay_packets = [
            {"replay_packet_id": "replay-packet-001", "worker_role": "planner", "replay_input_digest": "digest-1", "replay_expected_output_digest": "expected-1"},
            {"replay_packet_id": "replay-packet-002", "worker_role": "executor-preview", "replay_input_digest": "digest-2", "replay_expected_output_digest": "expected-2"},
            {"replay_packet_id": "replay-packet-003", "worker_role": "verifier", "replay_input_digest": "digest-3", "replay_expected_output_digest": "expected-3"}
        ]
    
    worker_count_valid = (1 <= requested_worker_count <= 5)
    registry_status = "REGISTRY_CREATED" if (approval_gate.get("confirmation_token_valid") and worker_count_valid) else "BLOCKED"
    
    registered_packets = []
    for packet in replay_packets:
        registered_packets.append({
            "replay_packet_id": packet.get("replay_packet_id"),
            "worker_role": packet.get("worker_role"),
            "packet_status": "REPLAY_PACKET_RECORD_ONLY",
            "replay_input_digest": packet.get("replay_input_digest"),
            "replay_expected_output_digest": packet.get("replay_expected_output_digest"),
            "replay_executed": False,
            "external_actions_taken": False
        })
        
    return {
        "replay_packet_registry_version": "3.6.0",
        "registry_status": registry_status,
        "requested_worker_count": requested_worker_count,
        "actual_packet_count": len(registered_packets),
        "replay_packets": registered_packets,
        "registry_digest": sha256_digest(registered_packets),
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_deterministic_replay_plan_contract(
    approval_gate: dict,
    replay_packet_registry: dict,
    replay_mode: str | None = None
) -> dict:
    if replay_mode is None:
        replay_mode = "PREVIEW_ONLY"
        
    allowed_modes = ["PREVIEW_ONLY", "COMPARISON_ONLY", "QUARANTINE_REVIEW_ONLY"]
    
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        replay_packet_registry.get("registry_status") == "REGISTRY_CREATED" and
        replay_mode in allowed_modes
    )
    
    plan_status = "PLAN_CONTRACT_CREATED" if is_valid else "BLOCKED"
    
    planned_steps = [
        "load replay packet registry records",
        "compare expected and observed digests",
        "produce comparison proof",
        "quarantine mismatched replay outputs",
        "require human review before any future replay execution",
        "do not execute replay automatically"
    ]
    
    return {
        "deterministic_replay_plan_contract_version": "3.6.0",
        "plan_status": plan_status,
        "replay_mode": replay_mode,
        "planned_packet_count": replay_packet_registry.get("actual_packet_count", 0),
        "planned_steps": planned_steps,
        "plan_digest": sha256_digest(planned_steps),
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_replay_safety_gate(
    approval_gate: dict,
    replay_plan_contract: dict
) -> dict:
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        replay_plan_contract.get("plan_status") == "PLAN_CONTRACT_CREATED"
    )
    safety_gate_status = "PASS" if is_valid else "BLOCKED"
    
    return {
        "replay_safety_gate_version": "3.6.0",
        "safety_gate_status": safety_gate_status,
        "preview_records_allowed": is_valid,
        "actual_replay_allowed": False,
        "worker_action_reexecution_allowed": False,
        "external_tool_replay_allowed": False,
        "live_api_replay_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "repo_mutation_allowed": False,
        "deployment_allowed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_multi_worker_replay_comparison_proof(
    approval_gate: dict,
    replay_packet_registry: dict,
    replay_safety_gate: dict,
    observed_digest_map: dict | None = None
) -> dict:
    if observed_digest_map is None:
        observed_digest_map = {}
        
    packet_comparisons = []
    mismatch_count = 0
    
    for packet in replay_packet_registry.get("replay_packets", []):
        pid = packet.get("replay_packet_id")
        expected = packet.get("replay_expected_output_digest")
        observed = observed_digest_map.get(pid)
        
        if observed is None:
            status = "NOT_OBSERVED_PREVIEW_ONLY"
        elif observed == expected:
            status = "MATCH"
        else:
            status = "MISMATCH"
            mismatch_count += 1
            
        packet_comparisons.append({
            "replay_packet_id": pid,
            "worker_role": packet.get("worker_role"),
            "expected_output_digest": expected,
            "observed_output_digest": observed,
            "comparison_status": status,
            "actual_replay_performed": False
        })
        
    is_valid = (
        approval_gate.get("confirmation_token_valid", False) and
        replay_safety_gate.get("safety_gate_status") == "PASS"
    )
    
    if not is_valid:
        overall_status = "BLOCKED"
    elif mismatch_count > 0:
        overall_status = "MISMATCHES_FOUND"
    else:
        overall_status = "CLEAR"
        
    return {
        "multi_worker_replay_comparison_proof_version": "3.6.0",
        "overall_comparison_status": overall_status,
        "packet_comparisons": packet_comparisons,
        "mismatch_count": mismatch_count,
        "comparison_digest": sha256_digest(packet_comparisons),
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_replay_output_quarantine_contract(
    approval_gate: dict,
    comparison_proof: dict,
    quarantine_reason: str | None = None
) -> dict:
    if quarantine_reason is None:
        quarantine_reason = "No replay output moved; quarantine contract prepared for preview records only."
        
    is_valid = (approval_gate.get("confirmation_token_valid", False))
    quarantine_status = "QUARANTINE_RECORD_READY" if is_valid else "BLOCKED"
    quarantine_recommended = (comparison_proof.get("overall_comparison_status") == "MISMATCHES_FOUND")
    
    quarantine_actions = [
        "mark mismatched replay preview packets for human review",
        "preserve replay packet registry",
        "preserve comparison proof",
        "block automatic retry",
        "do not execute replay",
        "require operator approval queue review"
    ]
    
    return {
        "replay_output_quarantine_contract_version": "3.6.0",
        "quarantine_status": quarantine_status,
        "quarantine_recommended": quarantine_recommended,
        "quarantine_reason": quarantine_reason,
        "quarantine_actions": quarantine_actions,
        "files_moved": False,
        "files_deleted": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_replay_audit_proof(
    approval_gate: dict,
    replay_packet_registry: dict,
    replay_plan_contract: dict,
    replay_safety_gate: dict,
    comparison_proof: dict,
    quarantine_contract: dict
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid", False)
    registry_created = (replay_packet_registry.get("registry_status") == "REGISTRY_CREATED")
    plan_created = (replay_plan_contract.get("plan_status") == "PLAN_CONTRACT_CREATED")
    safety_gate_passed = (replay_safety_gate.get("safety_gate_status") == "PASS")
    comparison_clear = (comparison_proof.get("overall_comparison_status") == "CLEAR")
    quarantine_ready = (quarantine_contract.get("quarantine_status") == "QUARANTINE_RECORD_READY")
    
    is_pass = (
        gate_valid and registry_created and plan_created and
        safety_gate_passed and comparison_clear and quarantine_ready
    )
    
    is_review = (gate_valid and comparison_proof.get("overall_comparison_status") == "MISMATCHES_FOUND")
    
    if is_pass:
        audit_status = "PASS"
    elif is_review:
        audit_status = "REVIEW_REQUIRED"
    else:
        audit_status = "BLOCKED"
        
    gate_digest = sha256_digest(approval_gate)
    registry_digest = sha256_digest(replay_packet_registry)
    plan_digest = sha256_digest(replay_plan_contract)
    safety_digest = sha256_digest(replay_safety_gate)
    comparison_digest = sha256_digest(comparison_proof)
    quarantine_digest = sha256_digest(quarantine_contract)
    
    combined_input = f"{gate_digest}:{registry_digest}:{plan_digest}:{safety_digest}:{comparison_digest}:{quarantine_digest}"
    combined_digest = sha256_digest(combined_input)
    
    safety_checks = {
        "approval_gate_valid": gate_valid,
        "replay_packet_registry_created": registry_created,
        "replay_plan_contract_created": plan_created,
        "replay_safety_gate_passed": safety_gate_passed,
        "comparison_clear": comparison_clear,
        "quarantine_contract_ready": quarantine_ready,
        "no_actual_replay": True,
        "no_worker_action_replay": True,
        "no_external_tool_replay": True,
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
        "replay_audit_proof_version": "3.6.0",
        "audit_status": audit_status,
        "approval_gate_digest": gate_digest,
        "replay_packet_registry_digest": registry_digest,
        "replay_plan_contract_digest": plan_digest,
        "replay_safety_gate_digest": safety_digest,
        "comparison_proof_digest": comparison_digest,
        "quarantine_contract_digest": quarantine_digest,
        "combined_replay_audit_digest": combined_digest,
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
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

def create_replay_preview_ledger(
    approval_gate: dict,
    replay_packet_registry: dict,
    replay_plan_contract: dict,
    replay_safety_gate: dict,
    comparison_proof: dict,
    quarantine_contract: dict,
    audit_proof: dict
) -> dict:
    audit_status = audit_proof.get("audit_status")
    if audit_status == "PASS":
        ledger_status = "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_LEDGER"
    elif audit_status == "REVIEW_REQUIRED":
        ledger_status = "REVIEW_REQUIRED"
    else:
        ledger_status = "BLOCKED"
        
    entries = [
        {"type": "replay_preview_approval_gate", "digest": sha256_digest(approval_gate)},
        {"type": "replay_packet_registry", "digest": sha256_digest(replay_packet_registry)},
        {"type": "deterministic_replay_plan_contract", "digest": sha256_digest(replay_plan_contract)},
        {"type": "replay_safety_gate", "digest": sha256_digest(replay_safety_gate)},
        {"type": "multi_worker_replay_comparison_proof", "digest": sha256_digest(comparison_proof)},
        {"type": "replay_output_quarantine_contract", "digest": sha256_digest(quarantine_contract)},
        {"type": "replay_audit_proof", "digest": sha256_digest(audit_proof)}
    ]
    
    return {
        "replay_preview_ledger_version": "3.6.0",
        "ledger_status": ledger_status,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
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
        "execution_authorized": False
    }

def create_replay_readiness_summary(
    approval_gate: dict,
    comparison_proof: dict,
    audit_proof: dict,
    replay_preview_ledger: dict
) -> dict:
    gate_valid = approval_gate.get("confirmation_token_valid", False)
    comparison_clear = (comparison_proof.get("overall_comparison_status") == "CLEAR")
    audit_pass = (audit_proof.get("audit_status") == "PASS")
    ledger_ready = (replay_preview_ledger.get("ledger_status") == "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_LEDGER")
    
    is_ready = (gate_valid and comparison_clear and audit_pass and ledger_ready)
    
    is_review = (gate_valid and (not comparison_clear or audit_proof.get("audit_status") == "REVIEW_REQUIRED"))
    
    if is_ready:
        readiness_status = "READY_FOR_NEXT_LAYER"
    elif is_review:
        readiness_status = "REVIEW_REQUIRED"
    else:
        readiness_status = "BLOCKED"
        
    return {
        "replay_readiness_summary_version": "3.6.0",
        "readiness_status": readiness_status,
        "ready_for_operator_approval_queue_enforcement": is_ready,
        "gate_status": approval_gate.get("gate_status", "BLOCKED"),
        "comparison_status": comparison_proof.get("overall_comparison_status", "BLOCKED"),
        "audit_status": audit_proof.get("audit_status", "BLOCKED"),
        "ledger_status": replay_preview_ledger.get("ledger_status", "BLOCKED"),
        "next_layer": "Operator Approval Queue Enforcement",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_operator_approval_queue_enforcement_readiness_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    is_ready = readiness_summary.get("ready_for_operator_approval_queue_enforcement", False)
    return {
        "operator_approval_queue_enforcement_readiness_bridge_version": "3.6.0",
        "current_layer": "Controlled Multi-Worker Audit Replay Preview",
        "next_layer": "Operator Approval Queue Enforcement",
        "ready_for_operator_approval_queue_enforcement": is_ready,
        "required_next_capabilities": [
            "operator approval queue schema",
            "queued action registry",
            "approval item priority classifier",
            "operator decision contract",
            "approval expiry and stale-item detector",
            "approval queue audit proof",
            "queue enforcement readiness summary",
            "still no automatic execution by default"
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no credential use",
            "no secret reads",
            "no actual replay execution",
            "no automatic approval",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no live production orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_multi_worker_audit_replay_preview_bundle(
    result: dict,
    command: str | None = None,
    replay_label: str | None = None,
    confirmation_token: str | None = None,
    replay_packets: list[dict] | None = None,
    requested_worker_count: int = 3,
    replay_mode: str | None = None,
    observed_digest_map: dict | None = None,
    quarantine_reason: str | None = None
) -> dict:
    if command is None:
        command = result.get("command", "")
    if replay_label is None:
        replay_label = "station-chief-controlled-multi-worker-audit-replay-preview"
        
    schema = create_controlled_multi_worker_audit_replay_preview_schema()
    gate = create_audit_replay_preview_approval_gate(replay_label, confirmation_token)
    registry = create_replay_packet_registry(gate, replay_packets, requested_worker_count)
    plan = create_deterministic_replay_plan_contract(gate, registry, replay_mode)
    safety_gate = create_replay_safety_gate(gate, plan)
    comparison = create_multi_worker_replay_comparison_proof(gate, registry, safety_gate, observed_digest_map)
    quarantine = create_replay_output_quarantine_contract(gate, comparison, quarantine_reason)
    audit = create_replay_audit_proof(gate, registry, plan, safety_gate, comparison, quarantine)
    ledger = create_replay_preview_ledger(gate, registry, plan, safety_gate, comparison, quarantine, audit)
    summary = create_replay_readiness_summary(gate, comparison, audit, ledger)
    bridge = create_operator_approval_queue_enforcement_readiness_bridge(result, summary)
    
    return {
        "controlled_multi_worker_audit_replay_preview_bundle_version": "3.6.0",
        "controlled_multi_worker_audit_replay_preview_status": "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_ONLY",
        "controlled_multi_worker_audit_replay_preview_schema": schema,
        "audit_replay_preview_approval_gate": gate,
        "replay_packet_registry": registry,
        "deterministic_replay_plan_contract": plan,
        "replay_safety_gate": safety_gate,
        "multi_worker_replay_comparison_proof": comparison,
        "replay_output_quarantine_contract": quarantine,
        "replay_audit_proof": audit,
        "replay_preview_ledger": ledger,
        "replay_readiness_summary": summary,
        "operator_approval_queue_enforcement_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
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
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
