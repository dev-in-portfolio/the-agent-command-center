import json
import hashlib
import re
from pathlib import Path

TOOL_PERMISSION_BINDING_MODULE_VERSION = "3.5.0"
TOOL_PERMISSION_BINDING_STATUS = "SINGLE_WORKER_TOOL_PERMISSION_BINDING_ONLY"
TOOL_PERMISSION_BINDING_PHASE = "Single-Worker Tool Permission Binding"

TOOL_PERMISSION_APPROVAL_TOKENS = {
    "sandbox_noop": "YES_I_APPROVE_TOOL_SANDBOX_NOOP",
    "deterministic_summary": "YES_I_APPROVE_TOOL_DETERMINISTIC_SUMMARY",
    "runtime_state_read": "YES_I_APPROVE_TOOL_RUNTIME_STATE_READ",
    "local_json_artifact_write": "YES_I_APPROVE_TOOL_LOCAL_JSON_ARTIFACT_WRITE"
}

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_tool_permission_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "tool-permission-binding"

def generate_tool_permission_binding_id(command: str, worker_id: str, runtime_version: str = "3.5.0") -> str:
    normalized_worker_id = normalize_tool_permission_label(worker_id)
    hash_input = f"{runtime_version}:{command}:{worker_id}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"tool-permission-v3-4-{normalized_worker_id}-{hash_chars}"

def create_tool_permission_binding_schema() -> dict:
    return {
        "tool_permission_binding_schema_version": "3.5.0",
        "schema_status": "SINGLE_WORKER_TOOL_PERMISSION_BINDING_ONLY",
        "required_sections": [
            "per_tool_permission_registry",
            "tool_permission_request_validation",
            "tool_specific_approval_binding",
            "tool_invocation_dry_run_contract",
            "tool_output_validation_schema",
            "tool_output_validation_result",
            "tool_failure_handling_contract",
            "tool_revocation_contract",
            "per_run_permission_audit_proof",
            "tool_permission_ledger",
            "tool_permission_readiness_summary",
            "live_execution_telemetry_abort_readiness_bridge"
        ],
        "allowed_tool_permissions": [
            "sandbox_noop",
            "deterministic_summary",
            "runtime_state_read",
            "local_json_artifact_write"
        ],
        "blocked_tool_permissions": [
            "network_access",
            "shell_command",
            "arbitrary_code_execution",
            "repo_write",
            "secret_read",
            "environment_variable_read",
            "git_push",
            "github_api_mutation",
            "deployment",
            "hosting_api_mutation",
            "broad_worker_activation",
            "live_orchestration"
        ],
        "required_tool_approval_tokens": TOOL_PERMISSION_APPROVAL_TOKENS,
        "safety_invariants": [
            "single sandbox worker only",
            "per-tool permission required",
            "tool-specific approval token required",
            "no network access",
            "no shell command execution",
            "no arbitrary code execution",
            "no repo mutation",
            "no secret access",
            "no deployment",
            "no hosting API mutation",
            "no broad workforce animation",
            "no live orchestration",
            "tool permission binding does not authorize broad execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "external_tool_invocations_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "execution_authorized": False
    }

def create_per_tool_permission_registry() -> dict:
    return {
        "per_tool_permission_registry_version": "3.5.0",
        "registry_status": "ACTIVE_CONTRACT",
        "allowed_tools": {
            "sandbox_noop": {
                "permission_id": "sandbox_noop",
                "permission_status": "ALLOWED_WITH_TOKEN",
                "required_token": "YES_I_APPROVE_TOOL_SANDBOX_NOOP",
                "description": "Allows deterministic no-op sandbox tool preview only.",
                "external_access": False,
                "repo_write": False
            },
            "deterministic_summary": {
                "permission_id": "deterministic_summary",
                "permission_status": "ALLOWED_WITH_TOKEN",
                "required_token": "YES_I_APPROVE_TOOL_DETERMINISTIC_SUMMARY",
                "description": "Allows deterministic local summary generation from already-provided runtime data.",
                "external_access": False,
                "repo_write": False
            },
            "runtime_state_read": {
                "permission_id": "runtime_state_read",
                "permission_status": "ALLOWED_WITH_TOKEN",
                "required_token": "YES_I_APPROVE_TOOL_RUNTIME_STATE_READ",
                "description": "Allows reading already-provided runtime result keys only, not filesystem, secrets, or environment.",
                "external_access": False,
                "repo_write": False
            },
            "local_json_artifact_write": {
                "permission_id": "local_json_artifact_write",
                "permission_status": "ALLOWED_WITH_TOKEN_AND_EXPLICIT_OUTPUT_WRITER",
                "required_token": "YES_I_APPROVE_TOOL_LOCAL_JSON_ARTIFACT_WRITE",
                "description": "Allows existing explicit output-directory artifact writers only; does not allow arbitrary file writes.",
                "external_access": False,
                "repo_write": False
            }
        },
        "blocked_tools": {
            "network_access": "BLOCKED",
            "shell_command": "BLOCKED",
            "arbitrary_code_execution": "BLOCKED",
            "repo_write": "BLOCKED",
            "secret_read": "BLOCKED",
            "environment_variable_read": "BLOCKED",
            "git_push": "BLOCKED",
            "github_api_mutation": "BLOCKED",
            "deployment": "BLOCKED",
            "hosting_api_mutation": "BLOCKED",
            "broad_worker_activation": "BLOCKED",
            "live_orchestration": "BLOCKED"
        },
        "default_policy": "deny_unless_explicitly_allowed_and_token_bound",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "execution_authorized": False
    }

def create_tool_permission_request_validation(
    worker_id: str,
    requested_tool_permissions: list[str] | None = None,
    provided_tool_tokens: dict | None = None,
    registry: dict | None = None
) -> dict:
    requested = requested_tool_permissions or []
    tokens = provided_tool_tokens or {}
    reg = registry or create_per_tool_permission_registry()
    
    allowed_reg = reg.get("allowed_tools", {})
    blocked_reg = reg.get("blocked_tools", {})
    
    permission_checks = []
    approved = []
    blocked = []
    missing_token = []
    invalid_token = []
    
    for p_id in requested:
        check = {
            "permission_id": p_id,
            "permission_status": "UNKNOWN",
            "required_token": None,
            "token_present": False,
            "token_valid": False,
            "external_access": False,
            "repo_write": False
        }
        
        if p_id in allowed_reg:
            tool_def = allowed_reg[p_id]
            req_token = tool_def["required_token"]
            check["required_token"] = req_token
            check["external_access"] = tool_def.get("external_access", False)
            check["repo_write"] = tool_def.get("repo_write", False)
            
            if p_id in tokens:
                check["token_present"] = True
                if tokens[p_id] == req_token:
                    check["token_valid"] = True
                    check["permission_status"] = "APPROVED"
                    approved.append(p_id)
                else:
                    check["permission_status"] = "INVALID_TOKEN"
                    invalid_token.append(p_id)
            else:
                check["permission_status"] = "MISSING_TOKEN"
                missing_token.append(p_id)
        elif p_id in blocked_reg:
            check["permission_status"] = "BLOCKED"
            blocked.append(p_id)
        else:
            check["permission_status"] = "UNKNOWN"
            blocked.append(p_id) # Unknown is blocked by default
            
        permission_checks.append(check)
        
    all_requested_approved = len(requested) > 0 and len(approved) == len(requested)
    validation_status = "PASS" if all_requested_approved else "BLOCKED"
    if not requested:
        validation_status = "BLOCKED" # Must request at least one to pass formal validation here
        
    return {
        "tool_permission_request_validation_version": "3.5.0",
        "worker_id": worker_id,
        "validation_status": validation_status,
        "requested_tool_permissions": requested,
        "approved_tool_permissions": approved,
        "blocked_tool_permissions": blocked,
        "missing_token_permissions": missing_token,
        "invalid_token_permissions": invalid_token,
        "permission_checks": permission_checks,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_specific_approval_binding(
    worker_id: str,
    validation_result: dict
) -> dict:
    status = "BOUND" if validation_result.get("validation_status") == "PASS" else "BLOCKED"
    
    # Create digest from worker_id + validation_result
    binding_data = {"worker_id": worker_id, "validation": validation_result}
    digest = sha256_digest(binding_data)
    
    return {
        "tool_specific_approval_binding_version": "3.5.0",
        "worker_id": worker_id,
        "binding_status": status,
        "approved_tool_permissions": validation_result.get("approved_tool_permissions", []),
        "blocked_tool_permissions": validation_result.get("blocked_tool_permissions", []),
        "approval_binding_digest": digest,
        "note": "Tool-specific approval binding is limited to the listed single-worker sandbox permissions and does not authorize external tools or broad execution.",
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_invocation_dry_run_contract(
    worker_id: str,
    approved_tool_permissions: list[str],
    sandbox_task: str = "noop"
) -> dict:
    reg = create_per_tool_permission_registry()
    allowed_tools = reg.get("allowed_tools", {})
    
    planned = []
    blocked = []
    
    for p_id in approved_tool_permissions:
        if p_id in allowed_tools:
            tool_def = allowed_tools[p_id]
            effect = f"Simulates {p_id} behavior in memory."
            if p_id == "local_json_artifact_write":
                effect = "Allows existing explicit output-directory artifact writers to record results; does not allow arbitrary file writes."
            
            planned.append({
                "permission_id": p_id,
                "invocation_mode": "DRY_RUN_CONTRACT_ONLY",
                "allowed_effect": effect,
                "blocked_effects": [
                    "network access",
                    "shell command execution",
                    "arbitrary code execution",
                    "repo mutation",
                    "secrets access",
                    "deployment",
                    "broad worker activation"
                ]
            })
        else:
            blocked.append(p_id)
            
    status = "PASS" if planned and not blocked else "BLOCKED"
    if not approved_tool_permissions:
        status = "BLOCKED"

    return {
        "tool_invocation_dry_run_contract_version": "3.5.0",
        "worker_id": worker_id,
        "sandbox_task": sandbox_task,
        "dry_run_status": status,
        "planned_invocations": planned,
        "blocked_invocations": blocked,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "external_tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_output_validation_schema() -> dict:
    return {
        "tool_output_validation_schema_version": "3.5.0",
        "schema_status": "VALIDATION_SCHEMA_ONLY",
        "required_output_fields": [
            "permission_id",
            "output_status",
            "output_payload",
            "output_digest",
            "external_actions_taken",
            "repo_files_modified",
            "execution_authorized"
        ],
        "blocked_output_content": [
            "secrets",
            "environment variables",
            "API-keys",
            "network response bodies",
            "filesystem listings",
            "shell command output",
            "deployment URLs from live deployment",
            "unbounded generated code execution output"
        ],
        "safety_checks": [
            "output has required fields",
            "output digest matches",
            "external actions false",
            "repo files modified false",
            "execution authorized false",
            "no blocked content indicators"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "execution_authorized": False
    }

def create_tool_output_validation_result(
    tool_outputs: list[dict] | None = None,
    validation_schema: dict | None = None
) -> dict:
    outputs = tool_outputs or []
    schema = validation_schema or create_tool_output_validation_schema()
    req_fields = schema.get("required_output_fields", [])
    
    blocked_indicators = ["secret", "api_key", "token=", "password", "BEGIN PRIVATE KEY", "shell output", "deployment_url"]
    
    output_checks = []
    blocked_outputs = []
    
    for i, out in enumerate(outputs):
        p_id = out.get("permission_id", "unknown")
        checks = {
            "required_fields_present": all(f in out for f in req_fields),
            "no_external_actions": out.get("external_actions_taken") is False,
            "no_repo_modifications": out.get("repo_files_modified") is False,
            "no_execution_authorized": out.get("execution_authorized") is False,
            "no_blocked_content": True
        }
        
        # Check payload content
        payload_str = json.dumps(out.get("output_payload", {}))
        for indicator in blocked_indicators:
            if indicator.lower() in payload_str.lower():
                checks["no_blocked_content"] = False
                break
                
        # Validate digest
        actual_digest = sha256_digest(out.get("output_payload", {}))
        checks["digest_matches"] = (out.get("output_digest") == actual_digest)
        
        pass_all = all(checks.values())
        output_checks.append({
            "index": i,
            "permission_id": p_id,
            "passed": pass_all,
            "checks": checks
        })
        
        if not pass_all:
            blocked_outputs.append(p_id)
            
    validation_status = "PASS" if not blocked_outputs else "BLOCKED"
    # An empty list of outputs is considered PASSing the validation phase (nothing to reject)
    
    return {
        "tool_output_validation_result_version": "3.5.0",
        "validation_status": validation_status,
        "output_count": len(outputs),
        "output_checks": output_checks,
        "blocked_outputs": blocked_outputs,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_failure_handling_contract(
    worker_id: str,
    validation_result: dict,
    output_validation_result: dict
) -> dict:
    ready = (
        validation_result.get("validation_status") == "PASS" and
        output_validation_result.get("validation_status") == "PASS"
    )
    
    return {
        "tool_failure_handling_contract_version": "3.5.0",
        "worker_id": worker_id,
        "failure_contract_status": "READY" if ready else "BLOCKED",
        "failure_triggers": [
            "permission request blocked",
            "missing tool token",
            "invalid tool token",
            "output validation blocked",
            "unexpected tool output",
            "external action attempted",
            "repo mutation attempted",
            "broad worker activation attempted"
        ],
        "failure_steps": [
            "stop current sandbox tool path",
            "mark permission binding blocked",
            "preserve audit evidence",
            "do not retry automatically",
            "require human review"
        ],
        "retry_policy": "NO_AUTOMATIC_RETRY",
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_revocation_contract(
    worker_id: str,
    approved_tool_permissions: list[str]
) -> dict:
    return {
        "tool_revocation_contract_version": "3.5.0",
        "worker_id": worker_id,
        "revocation_status": "REVOCABLE",
        "revocable_permissions": approved_tool_permissions,
        "revocation_triggers": [
            "human revocation",
            "permission violation",
            "failed output validation",
            "unexpected external action",
            "unexpected repo mutation",
            "safety policy update"
        ],
        "revocation_steps": [
            "mark permission as revoked",
            "block further dry-run invocation contracts",
            "preserve ledger",
            "require new token for future binding",
            "require human review"
        ],
        "post_revocation_state": "TOOLS_DISABLED_FOR_WORKER",
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_per_run_permission_audit_proof(
    worker_id: str,
    registry: dict,
    validation_result: dict,
    approval_binding: dict,
    dry_run_contract: dict,
    output_validation_schema: dict,
    output_validation_result: dict,
    failure_contract: dict,
    revocation_contract: dict
) -> dict:
    safety_checks = {
        "registry_available": registry is not None,
        "permissions_validated": validation_result.get("validation_status") == "PASS",
        "approvals_bound": approval_binding.get("binding_status") == "BOUND",
        "dry_run_contract_created": dry_run_contract.get("dry_run_status") == "PASS",
        "output_validation_passed": output_validation_result.get("validation_status") == "PASS",
        "failure_contract_available": failure_contract.get("failure_contract_status") == "READY",
        "revocation_contract_available": revocation_contract.get("revocation_status") == "REVOCABLE",
        "no_external_actions": True,
        "no_repo_modifications": True,
        "no_broad_worker_activation": True
    }
    
    pass_all = all(safety_checks.values())
    
    return {
        "per_run_permission_audit_proof_version": "3.5.0",
        "worker_id": worker_id,
        "audit_status": "PASS" if pass_all else "BLOCKED",
        "registry_digest": sha256_digest(registry),
        "validation_digest": sha256_digest(validation_result),
        "approval_binding_digest": sha256_digest(approval_binding),
        "dry_run_contract_digest": sha256_digest(dry_run_contract),
        "output_validation_schema_digest": sha256_digest(output_validation_schema),
        "output_validation_result_digest": sha256_digest(output_validation_result),
        "failure_contract_digest": sha256_digest(failure_contract),
        "revocation_contract_digest": sha256_digest(revocation_contract),
        "combined_permission_audit_digest": sha256_digest({
            "v": validation_result,
            "b": approval_binding,
            "d": dry_run_contract,
            "o": output_validation_result
        }),
        "safety_checks": safety_checks,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "external_tool_invocations_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "execution_authorized": False
    }

def create_tool_permission_ledger(
    worker_id: str,
    validation_result: dict,
    approval_binding: dict,
    dry_run_contract: dict,
    audit_proof: dict
) -> dict:
    entries = [
        {"type": "permission_validation", "status": validation_result.get("validation_status")},
        {"type": "approval_binding", "status": approval_binding.get("binding_status")},
        {"type": "dry_run_contract", "status": dry_run_contract.get("dry_run_status")},
        {"type": "audit_proof", "status": audit_proof.get("audit_status")}
    ]
    return {
        "tool_permission_ledger_version": "3.5.0",
        "ledger_status": "SINGLE_WORKER_TOOL_PERMISSION_LEDGER",
        "worker_id": worker_id,
        "entries": entries,
        "approved_tool_permissions": validation_result.get("approved_tool_permissions", []),
        "blocked_tool_permissions": validation_result.get("blocked_tool_permissions", []),
        "ledger_digest": sha256_digest(entries),
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_permission_readiness_summary(
    worker_id: str,
    validation_result: dict,
    audit_proof: dict,
    ledger: dict
) -> dict:
    ready = (
        validation_result.get("validation_status") == "PASS" and
        audit_proof.get("audit_status") == "PASS" and
        ledger.get("ledger_status") == "SINGLE_WORKER_TOOL_PERMISSION_LEDGER"
    )
    
    return {
        "tool_permission_readiness_summary_version": "3.5.0",
        "worker_id": worker_id,
        "readiness_status": "READY_FOR_NEXT_LAYER" if ready else "BLOCKED",
        "ready_for_live_execution_telemetry_abort_controls": ready,
        "approved_tool_permission_count": len(validation_result.get("approved_tool_permissions", [])),
        "blocked_tool_permission_count": len(validation_result.get("blocked_tool_permissions", [])),
        "audit_status": audit_proof.get("audit_status"),
        "ledger_status": ledger.get("ledger_status"),
        "next_layer": "Live Execution Telemetry and Abort Controls",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_live_execution_telemetry_abort_readiness_bridge(
    result: dict,
    readiness_summary: dict
) -> dict:
    ready = readiness_summary.get("ready_for_live_execution_telemetry_abort_controls") is True
    
    return {
        "live_execution_telemetry_abort_readiness_bridge_version": "3.5.0",
        "current_layer": "Single-Worker Tool Permission Binding",
        "next_layer": "Live Execution Telemetry and Abort Controls",
        "ready_for_live_execution_telemetry_abort_controls": ready,
        "required_next_capabilities": [
            "live execution telemetry event schema",
            "abort signal contract",
            "timeout contract",
            "partial-result capture",
            "failed-run quarantine",
            "post-abort audit proof",
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
        "tool_invocations_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_tool_permission_binding_bundle(
    result: dict,
    worker_id: str | None = None,
    requested_tool_permissions: list[str] | None = None,
    provided_tool_tokens: dict | None = None,
    sandbox_task: str = "noop",
    tool_outputs: list[dict] | None = None
) -> dict:
    w_id = worker_id or "station-chief-sandbox-worker-001"
    schema = create_tool_permission_binding_schema()
    registry = create_per_tool_permission_registry()
    
    validation = create_tool_permission_request_validation(
        w_id, requested_tool_permissions, provided_tool_tokens, registry
    )
    
    binding = create_tool_specific_approval_binding(w_id, validation)
    dry_run = create_tool_invocation_dry_run_contract(w_id, validation["approved_tool_permissions"], sandbox_task)
    
    out_schema = create_tool_output_validation_schema()
    out_result = create_tool_output_validation_result(tool_outputs, out_schema)
    
    failure = create_tool_failure_handling_contract(w_id, validation, out_result)
    revocation = create_tool_revocation_contract(w_id, validation["approved_tool_permissions"])
    
    audit = create_per_run_permission_audit_proof(
        w_id, registry, validation, binding, dry_run, out_schema, out_result, failure, revocation
    )
    
    ledger = create_tool_permission_ledger(w_id, validation, binding, dry_run, audit)
    summary = create_tool_permission_readiness_summary(w_id, validation, audit, ledger)
    bridge = create_live_execution_telemetry_abort_readiness_bridge(result, summary)
    
    return {
        "tool_permission_binding_bundle_version": "3.5.0",
        "tool_permission_binding_status": "SINGLE_WORKER_TOOL_PERMISSION_BINDING_ONLY",
        "tool_permission_binding_schema": schema,
        "per_tool_permission_registry": registry,
        "tool_permission_request_validation": validation,
        "tool_specific_approval_binding": binding,
        "tool_invocation_dry_run_contract": dry_run,
        "tool_output_validation_schema": out_schema,
        "tool_output_validation_result": out_result,
        "tool_failure_handling_contract": failure,
        "tool_revocation_contract": revocation,
        "per_run_permission_audit_proof": audit,
        "tool_permission_ledger": ledger,
        "tool_permission_readiness_summary": summary,
        "live_execution_telemetry_abort_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "external_tool_invocations_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False
    }
