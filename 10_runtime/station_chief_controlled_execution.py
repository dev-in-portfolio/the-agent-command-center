import json
import hashlib
from pathlib import Path

CONTROLLED_EXECUTION_MODULE_VERSION = "3.0.0"
CONTROLLED_EXECUTION_PHASE = "Controlled Execution Engine and Worker Hiring Layer"
CONTROLLED_EXECUTION_STATUS = "PROFILE_EXPANSION_ONLY"

def create_controlled_execution_profile_catalog() -> dict:
    profiles = {
        "audit_only": {
            "profile_id": "audit_only",
            "name": "Audit Only",
            "risk_level": "low",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Read-only audit profile with no side effects."
        },
        "dry_run_patch": {
            "profile_id": "dry_run_patch",
            "name": "Dry-Run Patch",
            "risk_level": "low",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Generates patch previews and dry-run bundles without writing to the repo."
        },
        "sandbox_write": {
            "profile_id": "sandbox_write",
            "name": "Sandbox Write",
            "risk_level": "medium",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": True,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": True,
            "requires_release_lock": True,
            "description": "Allows confirmed writes inside an explicit sandbox execution directory."
        },
        "scoped_repo_patch": {
            "profile_id": "scoped_repo_patch",
            "name": "Scoped Repo Patch",
            "risk_level": "high",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": True,
            "requires_human_confirmation": True,
            "requires_release_lock": True,
            "description": "Allows confirmed patches to allowlisted files inside a patch root."
        },
        "work_order_preview": {
            "profile_id": "work_order_preview",
            "name": "Work Order Preview",
            "risk_level": "low",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Preview future executable work orders without performing execution."
        },
        "worker_hiring_preview": {
            "profile_id": "worker_hiring_preview",
            "name": "Worker Hiring Preview",
            "risk_level": "low",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Preview future worker registry needs without performing real hiring."
        },
        "department_routing_preview": {
            "profile_id": "department_routing_preview",
            "name": "Department Routing Preview",
            "risk_level": "low",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Preview future department routing paths without live execution."
        },
        "orchestration_sandbox_preview": {
            "profile_id": "orchestration_sandbox_preview",
            "name": "Orchestration Sandbox Preview",
            "risk_level": "medium",
            "allows_live_external_actions": False,
            "allows_worker_animation": False,
            "allows_real_worker_hiring": False,
            "allows_uncontrolled_repo_writes": False,
            "allows_sandbox_file_write": False,
            "allows_scoped_repo_patch": False,
            "requires_human_confirmation": False,
            "requires_release_lock": True,
            "description": "Preview future multi-agent orchestration topology in sandbox-only terms."
        }
    }
    return {
        "controlled_execution_profile_catalog_version": "3.0.0",
        "phase": CONTROLLED_EXECUTION_PHASE,
        "status": CONTROLLED_EXECUTION_STATUS,
        "profiles": profiles,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False
    }

def select_controlled_execution_profile(
    command_type: str,
    requested_profile: str | None = None
) -> dict:
    catalog = create_controlled_execution_profile_catalog()
    profiles = catalog["profiles"]
    
    if requested_profile:
        if requested_profile in profiles:
            selected_id = requested_profile
            reason = "Requested controlled execution profile accepted."
        else:
            selected_id = "audit_only"
            reason = f"Requested controlled execution profile '{requested_profile}' unavailable; defaulted to audit_only."
    else:
        mapping = {
            "verification": "audit_only",
            "remember_only": "audit_only",
            "strict_execution": "work_order_preview",
            "speed_racer": "work_order_preview",
            "build": "work_order_preview",
            "route": "department_routing_preview",
            "repair": "work_order_preview",
            "governance": "audit_only",
            "final_output": "audit_only",
            "unknown": "audit_only"
        }
        selected_id = mapping.get(command_type, "audit_only")
        reason = f"Selected default profile for command type '{command_type}'."
        
    return {
        "controlled_execution_selection_version": "3.0.0",
        "command_type": command_type,
        "requested_profile": requested_profile,
        "selected_profile_id": selected_id,
        "selected_profile": profiles[selected_id],
        "selection_reason": reason,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False
    }

def create_execution_permission_matrix(selected_profile: dict) -> dict:
    return {
        "execution_permission_matrix_version": "3.0.0",
        "selected_profile_id": selected_profile["profile_id"],
        "permissions": {
            "live_external_actions": False,
            "worker_animation": False,
            "real_worker_hiring": False,
            "uncontrolled_repo_writes": False,
            "sandbox_file_write": selected_profile["allows_sandbox_file_write"],
            "scoped_repo_patch": selected_profile["allows_scoped_repo_patch"],
            "dry_run_artifacts": True,
            "approval_artifacts": True,
            "release_lock_required": True
        },
        "confirmation_requirements": {
            "sandbox_file_write_token": "YES_I_APPROVE_SANDBOX_FILE_WRITE" if selected_profile["allows_sandbox_file_write"] else None,
            "scoped_repo_patch_token": "YES_I_APPROVE_SCOPED_REPO_PATCH" if selected_profile["allows_scoped_repo_patch"] else None,
            "approval_record_token": "YES_I_APPROVE_APPROVAL_HANDOFF_RECORD" if selected_profile["requires_human_confirmation"] else None
        },
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False
    }

def create_execution_mode_contract(selected_profile: dict, permission_matrix: dict) -> dict:
    allowed = [
        "command classification",
        "overlay selection",
        "command brief generation",
        "non-executing work order generation",
        "artifact writing to explicit output directories",
        "registry/index updates when explicitly requested"
    ]
    if permission_matrix["permissions"]["sandbox_file_write"]:
        allowed.append("confirmed sandbox file write")
    if permission_matrix["permissions"]["scoped_repo_patch"]:
        allowed.append("confirmed scoped repo patch inside patch root")
        
    blocked = [
        "live external API action",
        "uncontrolled repo write",
        "locked baseline mutation",
        "Devinization overlay mutation outside explicit scope",
        "full worker-agent animation",
        "real worker hiring",
        "shell command execution",
        "package installation"
    ]
    
    safeguards = [
        "locked baseline preservation",
        "Devinization overlay preservation",
        "validator pass before completion",
        "explicit output directory for artifact writes",
        "no external actions",
        "no worker animation"
    ]
    
    return {
        "execution_mode_contract_version": "3.0.0",
        "selected_profile_id": selected_profile["profile_id"],
        "mode_status": "CONTRACT_ONLY",
        "allowed_operations": allowed,
        "blocked_operations": blocked,
        "required_safeguards": safeguards,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_blocked_action_ledger(selected_profile: dict, attempted_actions: list[str] | None = None) -> dict:
    if attempted_actions is None:
        attempted_actions = []
        
    blocked_patterns = [
        "live_external_api_action",
        "uncontrolled_repo_write",
        "locked_baseline_mutation",
        "devinization_overlay_mutation",
        "full_worker_animation",
        "real_worker_hiring",
        "shell_command_execution",
        "package_installation"
    ]
    
    blocked = []
    review = []
    
    for action in attempted_actions:
        if action in blocked_patterns:
            blocked.append(action)
        else:
            review.append(action)
            
    status = "BLOCKED_ACTIONS_PRESENT" if blocked else "CLEAR"
    
    return {
        "blocked_action_ledger_version": "3.0.0",
        "selected_profile_id": selected_profile["profile_id"],
        "attempted_actions": attempted_actions,
        "blocked_actions": blocked,
        "review_required_actions": review,
        "blocked_action_status": status,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False
    }

def create_controlled_execution_preflight_contract(
    command_brief: dict,
    selected_profile: dict,
    permission_matrix: dict,
    release_lock_bundle: dict | None = None
) -> dict:
    release_lock_present = release_lock_bundle is not None
    baseline_preserved = True
    external_actions_taken = False
    live_worker_agents_activated = False
    real_worker_hiring_performed = False
    
    blocked_reasons = []
    if not release_lock_present:
        blocked_reasons.append("Stable release lock missing.")
        
    preflight_status = "PASS" if (release_lock_present and not external_actions_taken and not live_worker_agents_activated and not real_worker_hiring_performed) else "BLOCKED"
    
    return {
        "controlled_execution_preflight_contract_version": "3.0.0",
        "command_type": command_brief.get("command_type"),
        "selected_profile_id": selected_profile["profile_id"],
        "release_lock_present": release_lock_present,
        "preflight_status": preflight_status,
        "blocked_reasons": blocked_reasons,
        "baseline_preserved": baseline_preserved,
        "external_actions_taken": external_actions_taken,
        "live_worker_agents_activated": live_worker_agents_activated,
        "real_worker_hiring_performed": real_worker_hiring_performed,
        "execution_authorized": False
    }

def create_controlled_execution_readiness_summary(
    selected_profile: dict,
    preflight_contract: dict,
    blocked_action_ledger: dict
) -> dict:
    score = 0
    if preflight_contract["preflight_status"] == "PASS":
        score += 25
    if blocked_action_ledger["blocked_action_status"] == "CLEAR":
        score += 25
    score += 20 # baseline_preserved
    score += 15 # external_actions_taken false
    score += 15 # live_worker_agents_activated false
    
    status = "READY_FOR_NEXT_LAYER"
    if preflight_contract["preflight_status"] == "BLOCKED" or blocked_action_ledger["blocked_action_status"] == "BLOCKED_ACTIONS_PRESENT":
        status = "BLOCKED"
        
    return {
        "controlled_execution_readiness_summary_version": "3.0.0",
        "selected_profile_id": selected_profile["profile_id"],
        "readiness_status": status,
        "next_layer": "Work Order Executor Skeleton",
        "score": score,
        "max_score": 100,
        "components": {
            "preflight_pass": preflight_contract["preflight_status"] == "PASS",
            "no_blocked_actions": blocked_action_ledger["blocked_action_status"] == "CLEAR",
            "baseline_preserved": True,
            "no_external_actions": True,
            "no_worker_animation": True
        },
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_work_order_executor_readiness_bridge(
    result: dict,
    selected_profile: dict,
    readiness_summary: dict
) -> dict:
    ready = readiness_summary["readiness_status"] == "READY_FOR_NEXT_LAYER"
    
    return {
        "work_order_executor_readiness_bridge_version": "3.0.0",
        "current_layer": "Controlled Execution Profile Expansion",
        "next_layer": "Work Order Executor Skeleton",
        "selected_profile_id": selected_profile["profile_id"],
        "ready_for_work_order_executor_skeleton": ready,
        "required_next_capabilities": [
            "executable work order schema",
            "work order status lifecycle",
            "work order dependency mapping",
            "work order dry-run executor",
            "validator-backed work order completion proof",
            "no live worker animation"
        ],
        "non_goals_for_next_layer": [
            "no full workforce animation",
            "no live external API execution",
            "no uncontrolled repo edits",
            "no baseline mutation"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_controlled_execution_bundle(
    result: dict,
    requested_profile: str | None = None,
    release_lock_bundle: dict | None = None,
    attempted_actions: list[str] | None = None
) -> dict:
    command_brief = result.get("command_brief", {"command_type": "unknown"})
    selection = select_controlled_execution_profile(command_brief["command_type"], requested_profile)
    selected_profile = selection["selected_profile"]
    
    permission_matrix = create_execution_permission_matrix(selected_profile)
    mode_contract = create_execution_mode_contract(selected_profile, permission_matrix)
    ledger = create_blocked_action_ledger(selected_profile, attempted_actions)
    preflight = create_controlled_execution_preflight_contract(command_brief, selected_profile, permission_matrix, release_lock_bundle)
    readiness = create_controlled_execution_readiness_summary(selected_profile, preflight, ledger)
    bridge = create_work_order_executor_readiness_bridge(result, selected_profile, readiness)
    
    return {
        "controlled_execution_bundle_version": "3.0.0",
        "phase": CONTROLLED_EXECUTION_PHASE,
        "status": CONTROLLED_EXECUTION_STATUS,
        "controlled_execution_profile_catalog": create_controlled_execution_profile_catalog(),
        "controlled_execution_selection": selection,
        "execution_permission_matrix": permission_matrix,
        "execution_mode_contract": mode_contract,
        "blocked_action_ledger": ledger,
        "controlled_execution_preflight_contract": preflight,
        "controlled_execution_readiness_summary": readiness,
        "work_order_executor_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }
