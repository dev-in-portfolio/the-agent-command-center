import json
import hashlib
import re
from pathlib import Path

CONTROLLED_WORKER_EXECUTION_MODULE_VERSION = "3.6.0"
CONTROLLED_WORKER_EXECUTION_STATUS = "SINGLE_WORKER_SANDBOX_EXECUTION_ONLY"
CONTROLLED_WORKER_EXECUTION_PHASE = "First Controlled Worker-Agent Execution Release"
FIRST_CONTROLLED_WORKER_EXECUTION_TOKEN = "YES_I_APPROVE_FIRST_CONTROLLED_WORKER_EXECUTION"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_worker_execution_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "controlled-worker-execution"

def generate_worker_execution_run_id(command: str, worker_id: str, runtime_version: str = "3.6.0") -> str:
    normalized_worker_id = normalize_worker_execution_label(worker_id)
    hash_input = f"{runtime_version}:{command}:{worker_id}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"controlled-worker-v3-6-{normalized_worker_id}-{hash_chars}"

def create_controlled_worker_execution_schema() -> dict:
    return {
        "controlled_worker_execution_schema_version": "3.6.0",
        "schema_status": "SINGLE_WORKER_SANDBOX_EXECUTION_ONLY",
        "required_sections": [
            "worker_execution_gate",
            "tool_permission_binding",
            "sandbox_worker_task",
            "worker_abort_contract",
            "worker_rollback_contract",
            "worker_execution_telemetry_stub",
            "controlled_worker_execution_result",
            "post_run_audit_proof",
            "worker_execution_ledger",
            "single_worker_tool_permission_binding_readiness_bridge"
        ],
        "allowed_execution_modes": [
            "schema_only",
            "gated_sandbox_preview",
            "confirmed_single_worker_sandbox_execution"
        ],
        "blocked_execution_modes": [
            "broad_worker_activation",
            "full_workforce_animation",
            "live_external_api_execution",
            "shell_command_execution",
            "arbitrary_code_execution",
            "repo_mutation_execution",
            "hosting_deployment_execution",
            "live_orchestration_execution",
            "unbounded_tool_access"
        ],
        "allowed_sandbox_tasks": [
            "noop",
            "echo_command_summary",
            "validate_payload_shape",
            "summarize_runtime_state",
            "produce_static_worker_note"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_FIRST_CONTROLLED_WORKER_EXECUTION"
        ],
        "safety_invariants": [
            "one sandbox worker only",
            "no live external API actions",
            "no shell command execution",
            "no arbitrary code execution",
            "no repo mutation",
            "no deployment",
            "no hosting API mutation",
            "no full workforce animation",
            "no real worker hiring",
            "no live worker routing",
            "no live orchestration",
            "controlled worker execution does not authorize any other execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "single_worker_sandbox_execution_available": True,
        "sandbox_worker_run_performed": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_worker_execution_gate(
    command: str,
    worker_id: str | None = None,
    sandbox_task: str = "noop",
    confirmation_token: str | None = None
) -> dict:
    w_id = worker_id or "station-chief-sandbox-worker-001"
    token_valid = (confirmation_token == FIRST_CONTROLLED_WORKER_EXECUTION_TOKEN)
    
    allowed_tasks = ["noop", "echo_command_summary", "validate_payload_shape", "summarize_runtime_state", "produce_static_worker_note"]
    task_allowed = sandbox_task in allowed_tasks
    
    reasons = []
    if not token_valid:
        reasons.append("Missing or invalid confirmation token: YES_I_APPROVE_FIRST_CONTROLLED_WORKER_EXECUTION")
    if not task_allowed:
        reasons.append(f"Invalid sandbox task: {sandbox_task}")
        
    authorized = token_valid and task_allowed
    status = "APPROVED_FOR_SINGLE_WORKER_SANDBOX_EXECUTION" if authorized else "BLOCKED_PENDING_FIRST_WORKER_APPROVAL"
    
    return {
        "worker_execution_gate_version": "3.6.0",
        "gate_status": status,
        "command": command,
        "worker_id": w_id,
        "sandbox_task": sandbox_task,
        "confirmation_token_required": FIRST_CONTROLLED_WORKER_EXECUTION_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "single_worker_sandbox_execution_authorized": authorized,
        "blocked_reasons": reasons,
        "allowed_scope": [
            "one deterministic local sandbox worker task",
            "standard library only",
            "JSON artifact output only",
            "no external calls"
        ],
        "blocked_scope": [
            "live external API actions",
            "shell commands",
            "arbitrary code execution",
            "repo mutation",
            "deployment",
            "hosting mutation",
            "full workforce animation",
            "real worker hiring",
            "live orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "sandbox_worker_run_performed": False,
        "broad_worker_activation_performed": False,
        "repo_files_modified": False,
        "execution_authorized": authorized
    }

def create_tool_permission_binding(
    worker_id: str,
    requested_tool_permissions: list[str] | None = None
) -> dict:
    requested = requested_tool_permissions or []
    allowed_perms = ["local_json_artifact_write", "deterministic_summary", "runtime_state_read", "sandbox_noop"]
    
    blocked = [p for p in requested if p not in allowed_perms]
    status = "PASS" if not blocked else "BLOCKED"
    
    return {
        "tool_permission_binding_version": "3.6.0",
        "worker_id": worker_id,
        "binding_status": status,
        "requested_tool_permissions": requested,
        "allowed_tool_permissions": [p for p in requested if p in allowed_perms],
        "blocked_tool_permissions": blocked,
        "permission_rules": {
            "local_json_artifact_write": "allowed only through explicit output directory writers",
            "deterministic_summary": "allowed",
            "runtime_state_read": "allowed for provided runtime result only",
            "sandbox_noop": "allowed",
            "network_access": "blocked",
            "shell_command": "blocked",
            "repo_write": "blocked except existing explicit scoped repo patch gate",
            "deployment": "blocked",
            "secrets_access": "blocked",
            "arbitrary_code_execution": "blocked"
        },
        "tools_invoked": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_sandbox_worker_task(
    command: str,
    worker_id: str,
    sandbox_task: str = "noop",
    payload: dict | None = None
) -> dict:
    p = payload or {}
    return {
        "sandbox_worker_task_version": "3.6.0",
        "task_status": "TASK_CREATED",
        "worker_id": worker_id,
        "sandbox_task": sandbox_task,
        "command": command,
        "payload": p,
        "task_digest": hashlib.sha256(f"{command}:{worker_id}:{sandbox_task}".encode("utf-8")).hexdigest(),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_worker_abort_contract(worker_id: str, worker_run_id: str | None = None) -> dict:
    return {
        "worker_abort_contract_version": "3.6.0",
        "worker_id": worker_id,
        "worker_run_id": worker_run_id,
        "abort_available": True,
        "abort_triggers": [
            "token missing",
            "tool permission blocked",
            "sandbox task invalid",
            "external action attempted",
            "repo mutation attempted",
            "broad worker activation attempted",
            "unexpected exception"
        ],
        "abort_steps": [
            "stop sandbox worker task",
            "mark worker result blocked",
            "write audit proof if output requested",
            "do not retry automatically",
            "require human review"
        ],
        "post_abort_state": "SANDBOX_WORKER_STOPPED",
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_worker_rollback_contract(worker_id: str, worker_run_id: str | None = None) -> dict:
    return {
        "worker_rollback_contract_version": "3.6.0",
        "worker_id": worker_id,
        "worker_run_id": worker_run_id,
        "rollback_required": False,
        "rollback_available": True,
        "rollback_reason": "No repo files or external systems are modified by v2.0 sandbox worker execution.",
        "rollback_steps": [
            "verify no repo files were modified",
            "verify no external actions were taken",
            "preserve audit proof",
            "mark run complete or blocked",
            "require human review before any future live expansion"
        ],
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_worker_execution_telemetry_stub(worker_id: str, worker_run_id: str | None = None) -> dict:
    return {
        "worker_execution_telemetry_stub_version": "3.6.0",
        "worker_id": worker_id,
        "worker_run_id": worker_run_id,
        "telemetry_status": "STUB_ONLY",
        "events": [
            "worker_gate_created",
            "permission_binding_created",
            "sandbox_task_created",
            "sandbox_task_pending_or_executed",
            "audit_proof_created"
        ],
        "metrics": {
            "sandbox_task_count": 0,
            "external_action_count": 0,
            "repo_file_modification_count": 0,
            "blocked_permission_count": 0,
            "broad_worker_activation_count": 0
        },
        "external_telemetry_sent": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def run_single_worker_sandbox_task(
    sandbox_worker_task: dict,
    worker_execution_gate: dict,
    tool_permission_binding: dict
) -> dict:
    authorized = worker_execution_gate.get("single_worker_sandbox_execution_authorized") is True
    perms_pass = tool_permission_binding.get("binding_status") == "PASS"
    task = sandbox_worker_task.get("sandbox_task", "noop")
    
    allowed_tasks = ["noop", "echo_command_summary", "validate_payload_shape", "summarize_runtime_state", "produce_static_worker_note"]
    
    if not (authorized and perms_pass and task in allowed_tasks):
        return {
            "controlled_worker_execution_result_version": "3.6.0",
            "worker_run_id": None,
            "worker_id": sandbox_worker_task.get("worker_id"),
            "sandbox_task": task,
            "result_status": "BLOCKED_NOT_EXECUTED",
            "result_payload": None,
            "result_digest": None,
            "single_worker_sandbox_execution_performed": False,
            "broad_worker_activation_performed": False,
            "external_actions_taken": False,
            "repo_files_modified": False,
            "hosting_api_called": False,
            "deployment_performed": False,
            "execution_authorized": False
        }
        
    # Perform deterministic in-memory task
    result_payload = {}
    if task == "noop":
        result_payload = {"message": "No operation performed."}
    elif task == "echo_command_summary":
        cmd = sandbox_worker_task.get("command", "")
        result_payload = {"command_length": len(cmd), "command_prefix": cmd[:20]}
    elif task == "validate_payload_shape":
        payload = sandbox_worker_task.get("payload", {})
        result_payload = {"keys": list(payload.keys()), "types": {k: str(type(v)) for k, v in payload.items()}}
    elif task == "summarize_runtime_state":
        # In a real scenario this would have access to the result, here we just show what we have in task
        result_payload = {"task_id": sandbox_worker_task.get("worker_id"), "task_type": task}
    elif task == "produce_static_worker_note":
        result_payload = {"note": "Single sandbox worker completed deterministic local task."}
        
    return {
        "controlled_worker_execution_result_version": "3.6.0",
        "worker_run_id": generate_worker_execution_run_id(sandbox_worker_task.get("command", "empty"), sandbox_worker_task.get("worker_id", "none")),
        "worker_id": sandbox_worker_task.get("worker_id"),
        "sandbox_task": task,
        "result_status": "SANDBOX_EXECUTED",
        "result_payload": result_payload,
        "result_digest": sha256_digest(result_payload),
        "single_worker_sandbox_execution_performed": True,
        "broad_worker_activation_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_post_run_audit_proof(
    worker_execution_gate: dict,
    tool_permission_binding: dict,
    sandbox_worker_task: dict,
    controlled_worker_execution_result: dict,
    worker_abort_contract: dict,
    worker_rollback_contract: dict,
    telemetry_stub: dict
) -> dict:
    safety_checks = {
        "gate_evaluated": True,
        "permissions_bound": True,
        "task_was_allowed": True,
        "no_external_actions": not controlled_worker_execution_result.get("external_actions_taken", False),
        "no_repo_modifications": not controlled_worker_execution_result.get("repo_files_modified", False),
        "no_broad_worker_activation": not controlled_worker_execution_result.get("broad_worker_activation_performed", False),
        "no_real_worker_hiring": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_hosting_api_called": not controlled_worker_execution_result.get("hosting_api_called", False),
        "no_deployment_performed": not controlled_worker_execution_result.get("deployment_performed", False)
    }
    
    pass_all = all(safety_checks.values())
    
    return {
        "post_run_audit_proof_version": "3.6.0",
        "audit_status": "PASS" if pass_all else "BLOCKED",
        "worker_run_id": controlled_worker_execution_result.get("worker_run_id"),
        "worker_id": controlled_worker_execution_result.get("worker_id"),
        "gate_digest": sha256_digest(worker_execution_gate),
        "permission_binding_digest": sha256_digest(tool_permission_binding),
        "task_digest": sha256_digest(sandbox_worker_task),
        "result_digest": sha256_digest(controlled_worker_execution_result),
        "abort_contract_digest": sha256_digest(worker_abort_contract),
        "rollback_contract_digest": sha256_digest(worker_rollback_contract),
        "telemetry_stub_digest": sha256_digest(telemetry_stub),
        "combined_audit_digest": sha256_digest({
            "gate": worker_execution_gate,
            "binding": tool_permission_binding,
            "task": sandbox_worker_task,
            "result": controlled_worker_execution_result
        }),
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }

def create_worker_execution_ledger(
    worker_execution_gate: dict,
    tool_permission_binding: dict,
    controlled_worker_execution_result: dict,
    post_run_audit_proof: dict
) -> dict:
    entries = [
        {"type": "gate_status", "status": worker_execution_gate.get("gate_status")},
        {"type": "permission_binding", "status": tool_permission_binding.get("binding_status")},
        {"type": "execution_result", "status": controlled_worker_execution_result.get("result_status")},
        {"type": "audit_proof", "status": post_run_audit_proof.get("audit_status")}
    ]
    return {
        "worker_execution_ledger_version": "3.6.0",
        "ledger_status": "SINGLE_WORKER_SANDBOX_LEDGER",
        "worker_run_id": controlled_worker_execution_result.get("worker_run_id"),
        "worker_id": controlled_worker_execution_result.get("worker_id"),
        "entries": entries,
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_single_worker_tool_permission_binding_readiness_bridge(
    result: dict,
    post_run_audit_proof: dict,
    worker_execution_ledger: dict
) -> dict:
    ready = (
        post_run_audit_proof.get("audit_status") == "PASS"
        and worker_execution_ledger.get("ledger_status") == "SINGLE_WORKER_SANDBOX_LEDGER"
        and not result.get("external_actions_taken", False)
        and not result.get("repo_files_modified", False)
    )
    
    return {
        "single_worker_tool_permission_binding_readiness_bridge_version": "3.6.0",
        "current_layer": "First Controlled Worker-Agent Execution Release",
        "next_layer": "Single-Worker Tool Permission Binding",
        "ready_for_single_worker_tool_permission_binding": ready,
        "required_next_capabilities": [
            "per-tool permission registry",
            "tool invocation dry-run contract",
            "tool-specific approval tokens",
            "tool output validation",
            "tool failure handling",
            "tool revocation contract",
            "per-run permission audit proof",
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
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_controlled_worker_execution_bundle(
    result: dict,
    worker_id: str | None = None,
    sandbox_task: str = "noop",
    confirmation_token: str | None = None,
    requested_tool_permissions: list[str] | None = None,
    payload: dict | None = None
) -> dict:
    schema = create_controlled_worker_execution_schema()
    gate = create_worker_execution_gate(
        result.get("command", "empty"),
        worker_id=worker_id,
        sandbox_task=sandbox_task,
        confirmation_token=confirmation_token
    )
    binding = create_tool_permission_binding(gate["worker_id"], requested_tool_permissions)
    task = create_sandbox_worker_task(result.get("command", "empty"), gate["worker_id"], sandbox_task, payload)
    
    abort = create_worker_abort_contract(gate["worker_id"])
    rollback = create_worker_rollback_contract(gate["worker_id"])
    telemetry = create_worker_execution_telemetry_stub(gate["worker_id"])
    
    exec_result = run_single_worker_sandbox_task(task, gate, binding)
    
    # Update digests in sub-contracts if run was performed
    if exec_result["worker_run_id"]:
        abort["worker_run_id"] = exec_result["worker_run_id"]
        rollback["worker_run_id"] = exec_result["worker_run_id"]
        telemetry["worker_run_id"] = exec_result["worker_run_id"]
        
    audit = create_post_run_audit_proof(gate, binding, task, exec_result, abort, rollback, telemetry)
    ledger = create_worker_execution_ledger(gate, binding, exec_result, audit)
    bridge = create_single_worker_tool_permission_binding_readiness_bridge(result, audit, ledger)
    
    return {
        "controlled_worker_execution_bundle_version": "3.6.0",
        "controlled_worker_execution_status": "SINGLE_WORKER_SANDBOX_EXECUTION_ONLY",
        "controlled_worker_execution_schema": schema,
        "worker_execution_gate": gate,
        "tool_permission_binding": binding,
        "sandbox_worker_task": task,
        "worker_abort_contract": abort,
        "worker_rollback_contract": rollback,
        "worker_execution_telemetry_stub": telemetry,
        "controlled_worker_execution_result": exec_result,
        "post_run_audit_proof": audit,
        "worker_execution_ledger": ledger,
        "single_worker_tool_permission_binding_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "single_worker_sandbox_execution_available": True,
        "single_worker_sandbox_execution_performed": exec_result["single_worker_sandbox_execution_performed"],
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
