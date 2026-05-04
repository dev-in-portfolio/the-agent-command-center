import json
import hashlib
import re
from pathlib import Path

LIVE_EXECUTION_TELEMETRY_ABORT_MODULE_VERSION = "3.3.0"
LIVE_EXECUTION_TELEMETRY_ABORT_STATUS = "SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS_ONLY"
LIVE_EXECUTION_TELEMETRY_ABORT_PHASE = "Live Execution Telemetry and Abort Controls"
LIVE_EXECUTION_TELEMETRY_ABORT_APPROVAL_TOKEN = "YES_I_APPROVE_SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_telemetry_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "live-telemetry-abort"

def generate_telemetry_abort_id(command: str, worker_id: str, runtime_version: str = "3.3.0") -> str:
    normalized_worker_id = normalize_telemetry_label(worker_id)
    hash_input = f"{runtime_version}:{command}:{worker_id}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"telemetry-abort-v3-3-{normalized_worker_id}-{hash_chars}"

def create_live_execution_telemetry_abort_schema() -> dict:
    return {
        "live_execution_telemetry_abort_schema_version": "3.3.0",
        "schema_status": "SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS_ONLY",
        "required_sections": [
            "telemetry_event_schema",
            "execution_state_model",
            "telemetry_approval_gate",
            "heartbeat_stub",
            "abort_signal_contract",
            "timeout_contract",
            "partial_result_capture",
            "failed_run_quarantine_contract",
            "post_abort_audit_proof",
            "telemetry_ledger",
            "telemetry_readiness_summary",
            "post_run_audit_expansion_readiness_bridge"
        ],
        "allowed_control_modes": [
            "schema_only",
            "local_telemetry_preview",
            "approved_single_worker_telemetry_records",
            "abort_contract_preview",
            "timeout_contract_preview",
            "quarantine_contract_preview"
        ],
        "blocked_control_modes": [
            "external_telemetry_stream",
            "process_kill",
            "shell_abort",
            "network_abort",
            "broad_worker_shutdown",
            "live_orchestration_abort",
            "repo_mutating_recovery",
            "deployment_rollback",
            "background_monitoring",
            "autonomous_retry"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS"
        ],
        "safety_invariants": [
            "single sandbox worker only",
            "local telemetry records only",
            "no external telemetry service",
            "no process termination",
            "no shell commands",
            "no network calls",
            "no repo mutation",
            "no deployment",
            "no broad workforce animation",
            "no live orchestration",
            "abort controls are contract records only",
            "timeout controls are deterministic records only",
            "telemetry and abort controls do not authorize broad execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "telemetry_events_emitted": False,
        "external_telemetry_sent": False,
        "abort_signal_executed": False,
        "processes_terminated": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "execution_authorized": False
    }

def create_telemetry_event_schema() -> dict:
    return {
        "telemetry_event_schema_version": "3.3.0",
        "schema_status": "LOCAL_EVENT_SCHEMA_ONLY",
        "required_event_fields": [
            "event_id",
            "event_type",
            "worker_id",
            "event_sequence",
            "event_status",
            "event_payload",
            "event_digest",
            "external_actions_taken",
            "repo_files_modified",
            "execution_authorized"
        ],
        "allowed_event_types": [
            "telemetry_gate_created",
            "execution_state_created",
            "heartbeat_stub_created",
            "abort_contract_created",
            "timeout_contract_created",
            "partial_result_captured",
            "quarantine_contract_created",
            "post_abort_audit_created",
            "telemetry_ledger_created"
        ],
        "blocked_event_types": [
            "external_telemetry_sent",
            "shell_command_started",
            "process_killed",
            "network_call_started",
            "repo_file_modified",
            "deployment_started",
            "broad_worker_activation_started"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_telemetry_sent": False,
        "execution_authorized": False
    }

def create_execution_state_model(
    worker_id: str,
    command: str,
    state: str = "PENDING_TELEMETRY_APPROVAL"
) -> dict:
    allowed_states = [
        "PENDING_TELEMETRY_APPROVAL",
        "TELEMETRY_APPROVED",
        "SANDBOX_RUNNING_SIMULATED",
        "ABORT_REQUESTED_CONTRACT_ONLY",
        "TIMEOUT_RECORDED_CONTRACT_ONLY",
        "PARTIAL_RESULT_CAPTURED",
        "QUARANTINED_CONTRACT_ONLY",
        "COMPLETED_WITH_AUDIT",
        "BLOCKED"
    ]
    if state not in allowed_states:
        state = "BLOCKED"
        
    return {
        "execution_state_model_version": "3.3.0",
        "worker_id": worker_id,
        "command": command,
        "state": state,
        "allowed_states": allowed_states,
        "state_digest": hashlib.sha256(f"{worker_id}:{state}".encode("utf-8")).hexdigest(),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_telemetry_approval_gate(
    worker_id: str,
    confirmation_token: str | None = None
) -> dict:
    valid = (confirmation_token == LIVE_EXECUTION_TELEMETRY_ABORT_APPROVAL_TOKEN)
    status = "APPROVED_FOR_SINGLE_WORKER_TELEMETRY_ABORT_RECORDS" if valid else "BLOCKED_PENDING_TELEMETRY_ABORT_APPROVAL"
    
    return {
        "telemetry_approval_gate_version": "3.3.0",
        "worker_id": worker_id,
        "gate_status": status,
        "confirmation_token_required": LIVE_EXECUTION_TELEMETRY_ABORT_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": valid,
        "local_telemetry_records_authorized": valid,
        "external_telemetry_authorized": False,
        "process_abort_authorized": False,
        "shell_abort_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "broad_worker_activation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_heartbeat_stub(
    worker_id: str,
    telemetry_gate: dict,
    sequence_count: int = 3
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    status = "LOCAL_HEARTBEAT_STUB_CREATED" if valid else "BLOCKED"
    
    heartbeat_events = []
    if valid:
        for i in range(1, sequence_count + 1):
            payload = {"sequence": i, "status": "ALIVE"}
            heartbeat_events.append({
                "event_type": "heartbeat_stub_created",
                "event_sequence": i,
                "event_status": "RECORDED_LOCAL_ONLY",
                "event_payload": payload,
                "event_digest": sha256_digest(payload)
            })
            
    return {
        "heartbeat_stub_version": "3.3.0",
        "worker_id": worker_id,
        "heartbeat_status": status,
        "heartbeat_events": heartbeat_events,
        "heartbeat_count": len(heartbeat_events),
        "background_monitoring_started": False,
        "external_telemetry_sent": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_abort_signal_contract(
    worker_id: str,
    telemetry_gate: dict,
    abort_reason: str | None = None
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    status = "READY" if valid else "BLOCKED"
    reason = abort_reason or "No abort requested; contract prepared."
    
    return {
        "abort_signal_contract_version": "3.3.0",
        "worker_id": worker_id,
        "contract_status": status,
        "abort_reason": reason,
        "abort_signal_available": valid,
        "abort_signal_executed": False,
        "processes_terminated": False,
        "shell_commands_run": False,
        "abort_triggers": [
            "human abort request",
            "timeout contract triggered",
            "permission violation",
            "unsafe output validation",
            "unexpected external action attempt",
            "repo mutation attempt",
            "broad worker activation attempt"
        ],
        "abort_steps": [
            "mark local telemetry state as abort requested",
            "stop further local sandbox records",
            "capture partial result record",
            "quarantine failed run record",
            "create post-abort audit proof",
            "require human review before any future run"
        ],
        "post_abort_state": "SANDBOX_WORKER_STOPPED_CONTRACT_ONLY",
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_timeout_contract(
    worker_id: str,
    telemetry_gate: dict,
    timeout_limit_steps: int = 5,
    observed_steps: int = 0
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    status = "READY" if valid else "BLOCKED"
    triggered = observed_steps > timeout_limit_steps
    
    return {
        "timeout_contract_version": "3.3.0",
        "worker_id": worker_id,
        "contract_status": status,
        "timeout_limit_steps": timeout_limit_steps,
        "observed_steps": observed_steps,
        "timeout_triggered": triggered,
        "timeout_action": "RECORD_TIMEOUT_ONLY" if triggered else "NONE",
        "timers_started": False,
        "background_monitoring_started": False,
        "processes_terminated": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_partial_result_capture(
    worker_id: str,
    telemetry_gate: dict,
    partial_payload: dict | None = None
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    payload = partial_payload or {}
    status = "CAPTURED_LOCAL_ONLY" if valid else "BLOCKED"
    
    return {
        "partial_result_capture_version": "3.3.0",
        "worker_id": worker_id,
        "capture_status": status,
        "partial_payload": payload,
        "partial_payload_digest": sha256_digest(payload),
        "filesystem_read": False,
        "environment_read": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_failed_run_quarantine_contract(
    worker_id: str,
    telemetry_gate: dict,
    failure_reason: str | None = None
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    status = "QUARANTINE_RECORD_READY" if valid else "BLOCKED"
    reason = failure_reason or "No failure recorded; contract prepared."
    
    return {
        "failed_run_quarantine_contract_version": "3.3.0",
        "worker_id": worker_id,
        "quarantine_status": status,
        "failure_reason": reason,
        "quarantine_actions": [
            "mark run as quarantined in local artifact record",
            "preserve telemetry ledger",
            "preserve partial result capture",
            "block automatic retry",
            "require human review"
        ],
        "files_moved": False,
        "processes_terminated": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_post_abort_audit_proof(
    worker_id: str,
    telemetry_gate: dict,
    heartbeat_stub: dict,
    abort_contract: dict,
    timeout_contract: dict,
    partial_capture: dict,
    quarantine_contract: dict
) -> dict:
    valid = telemetry_gate.get("confirmation_token_valid") is True
    
    safety_checks = {
        "telemetry_gate_valid": valid,
        "heartbeat_local_only": not heartbeat_stub.get("background_monitoring_started", True),
        "abort_contract_record_only": not abort_contract.get("abort_signal_executed", True),
        "timeout_contract_record_only": not timeout_contract.get("timers_started", True),
        "partial_capture_local_only": not partial_capture.get("filesystem_read", True),
        "quarantine_record_only": not quarantine_contract.get("files_moved", True),
        "no_external_telemetry": not heartbeat_stub.get("external_telemetry_sent", True),
        "no_process_termination": not abort_contract.get("processes_terminated", True),
        "no_shell_commands": not abort_contract.get("shell_commands_run", True),
        "no_repo_modifications": not partial_capture.get("repo_files_modified", True),
        "no_deployment": not partial_capture.get("deployment_performed", True)
    }
    
    audit_pass = all(safety_checks.values())
    
    return {
        "post_abort_audit_proof_version": "3.3.0",
        "worker_id": worker_id,
        "audit_status": "PASS" if audit_pass else "BLOCKED",
        "telemetry_gate_digest": sha256_digest(telemetry_gate),
        "heartbeat_stub_digest": sha256_digest(heartbeat_stub),
        "abort_contract_digest": sha256_digest(abort_contract),
        "timeout_contract_digest": sha256_digest(timeout_contract),
        "partial_capture_digest": sha256_digest(partial_capture),
        "quarantine_contract_digest": sha256_digest(quarantine_contract),
        "combined_post_abort_audit_digest": sha256_digest({
            "gate": telemetry_gate,
            "abort": abort_contract,
            "timeout": timeout_contract
        }),
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_telemetry_sent": False,
        "abort_signal_executed": False,
        "processes_terminated": False,
        "shell_commands_run": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_telemetry_ledger(
    worker_id: str,
    telemetry_gate: dict,
    heartbeat_stub: dict,
    abort_contract: dict,
    timeout_contract: dict,
    partial_capture: dict,
    quarantine_contract: dict,
    post_abort_audit_proof: dict
) -> dict:
    entries = [
        {"type": "telemetry_approval_gate", "status": telemetry_gate.get("gate_status")},
        {"type": "heartbeat_stub", "status": heartbeat_stub.get("heartbeat_status")},
        {"type": "abort_contract", "status": abort_contract.get("contract_status")},
        {"type": "timeout_contract", "status": timeout_contract.get("contract_status")},
        {"type": "partial_result_capture", "status": partial_capture.get("capture_status")},
        {"type": "quarantine_contract", "status": quarantine_contract.get("quarantine_status")},
        {"type": "post_abort_audit_proof", "status": post_abort_audit_proof.get("audit_status")}
    ]
    
    return {
        "telemetry_ledger_version": "3.3.0",
        "ledger_status": "SINGLE_WORKER_TELEMETRY_ABORT_LEDGER",
        "worker_id": worker_id,
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "external_telemetry_sent": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_telemetry_readiness_summary(
    worker_id: str,
    telemetry_gate: dict,
    post_abort_audit_proof: dict,
    telemetry_ledger: dict
) -> dict:
    approved = telemetry_gate.get("confirmation_token_valid") is True
    audit_pass = post_abort_audit_proof.get("audit_status") == "PASS"
    ledger_ready = telemetry_ledger.get("ledger_status") == "SINGLE_WORKER_TELEMETRY_ABORT_LEDGER"
    
    ready = approved and audit_pass and ledger_ready
    
    return {
        "telemetry_readiness_summary_version": "3.3.0",
        "worker_id": worker_id,
        "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED",
        "ready_for_post_run_audit_proof_expansion": ready,
        "telemetry_gate_status": telemetry_gate.get("gate_status"),
        "post_abort_audit_status": post_abort_audit_proof.get("audit_status"),
        "ledger_status": telemetry_ledger.get("ledger_status"),
        "next_layer": "Post-Run Audit Proof Expansion",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_telemetry_sent": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_post_run_audit_expansion_readiness_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    ready = readiness_summary.get("ready_for_post_run_audit_proof_expansion") is True
    
    return {
        "post_run_audit_expansion_readiness_bridge_version": "3.3.0",
        "current_layer": "Live Execution Telemetry and Abort Controls",
        "next_layer": "Post-Run Audit Proof Expansion",
        "ready_for_post_run_audit_proof_expansion": ready,
        "required_next_capabilities": [
            "expanded post-run audit evidence schema",
            "before/after run comparison proof",
            "validator-backed audit artifact index",
            "audit replay record",
            "failure-class taxonomy",
            "human review packet",
            "still single-worker scoped",
            "still no broad workforce animation"
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_telemetry_sent": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_live_execution_telemetry_abort_bundle(
    result: dict,
    worker_id: str | None = None,
    command: str | None = None,
    confirmation_token: str | None = None,
    abort_reason: str | None = None,
    failure_reason: str | None = None,
    timeout_limit_steps: int = 5,
    observed_steps: int = 0,
    partial_payload: dict | None = None
) -> dict:
    w_id = worker_id or "station-chief-sandbox-worker-001"
    cmd = command or result.get("command", "")
    
    schema = create_live_execution_telemetry_abort_schema()
    event_schema = create_telemetry_event_schema()
    state_model = create_execution_state_model(w_id, cmd)
    gate = create_telemetry_approval_gate(w_id, confirmation_token)
    heartbeat = create_heartbeat_stub(w_id, gate)
    abort = create_abort_signal_contract(w_id, gate, abort_reason)
    timeout = create_timeout_contract(w_id, gate, timeout_limit_steps, observed_steps)
    partial = create_partial_result_capture(w_id, gate, partial_payload)
    quarantine = create_failed_run_quarantine_contract(w_id, gate, failure_reason)
    
    audit = create_post_abort_audit_proof(w_id, gate, heartbeat, abort, timeout, partial, quarantine)
    ledger = create_telemetry_ledger(w_id, gate, heartbeat, abort, timeout, partial, quarantine, audit)
    summary = create_telemetry_readiness_summary(w_id, gate, audit, ledger)
    bridge = create_post_run_audit_expansion_readiness_bridge(result, summary)
    
    return {
        "live_execution_telemetry_abort_bundle_version": "3.3.0",
        "live_execution_telemetry_abort_status": "SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS_ONLY",
        "live_execution_telemetry_abort_schema": schema,
        "telemetry_event_schema": event_schema,
        "execution_state_model": state_model,
        "telemetry_approval_gate": gate,
        "heartbeat_stub": heartbeat,
        "abort_signal_contract": abort,
        "timeout_contract": timeout,
        "partial_result_capture": partial,
        "failed_run_quarantine_contract": quarantine,
        "post_abort_audit_proof": audit,
        "telemetry_ledger": ledger,
        "telemetry_readiness_summary": summary,
        "post_run_audit_expansion_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "telemetry_events_emitted": len(heartbeat["heartbeat_events"]) > 0,
        "external_telemetry_sent": False,
        "abort_signal_executed": False,
        "processes_terminated": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
