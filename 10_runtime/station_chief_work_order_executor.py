import json
import hashlib
import re
from pathlib import Path

WORK_ORDER_EXECUTOR_MODULE_VERSION = "3.4.0"
WORK_ORDER_EXECUTOR_STATUS = "SKELETON_DRY_RUN_ONLY"
WORK_ORDER_EXECUTOR_PHASE = "Work Order Executor Skeleton"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_work_order_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "work-order"

def generate_work_order_id(command: str, label: str, index: int, runtime_version: str = "3.4.0") -> str:
    normalized_label = normalize_work_order_label(label)
    hash_input = f"{runtime_version}:{command}:{label}:{index}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"work-order-v3-4-{normalized_label}-{index:03d}-{hash_chars}"

def create_executable_work_order_schema() -> dict:
    return {
        "executable_work_order_schema_version": "3.4.0",
        "schema_status": WORK_ORDER_EXECUTOR_STATUS,
        "required_fields": [
            "work_order_id",
            "title",
            "description",
            "work_order_type",
            "status",
            "execution_mode",
            "dependencies",
            "acceptance_criteria",
            "safety_constraints",
            "artifact_expectations"
        ],
        "optional_fields": [
            "assigned_department",
            "assigned_family",
            "assigned_role",
            "priority",
            "estimated_complexity",
            "notes"
        ],
        "allowed_statuses": [
            "CREATED",
            "READY",
            "BLOCKED",
            "DRY_RUN_STARTED",
            "DRY_RUN_COMPLETE",
            "COMPLETION_PROOF_CREATED",
            "FAILED_VALIDATION"
        ],
        "allowed_execution_modes": [
            "dry_run_only",
            "artifact_only",
            "sandbox_preview"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no shell command execution",
            "no package installation"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_work_order(
    command: str,
    title: str,
    description: str,
    work_order_type: str = "general",
    index: int = 1,
    dependencies: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    safety_constraints: list[str] | None = None,
    artifact_expectations: list[str] | None = None,
    execution_mode: str = "dry_run_only",
    assigned_department: str | None = None,
    assigned_family: str | None = None,
    assigned_role: str | None = None,
    priority: str = "normal",
    estimated_complexity: str = "medium",
    notes: str | None = None
) -> dict:
    if dependencies is None:
        dependencies = []
    if acceptance_criteria is None:
        acceptance_criteria = [
            "Dry-run completes without live execution.",
            "Baseline remains preserved.",
            "No external actions are taken."
        ]
    if safety_constraints is None:
        safety_constraints = [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation"
        ]
    if artifact_expectations is None:
        artifact_expectations = [
            "work_order.json",
            "work_order_dry_run_result.json",
            "work_order_completion_proof.json"
        ]
    
    work_order_id = generate_work_order_id(command, title, index)
    
    return {
        "work_order_schema_version": "3.4.0",
        "work_order_id": work_order_id,
        "title": title,
        "description": description,
        "work_order_type": work_order_type,
        "status": "CREATED",
        "execution_mode": execution_mode,
        "dependencies": dependencies,
        "acceptance_criteria": acceptance_criteria,
        "safety_constraints": safety_constraints,
        "artifact_expectations": artifact_expectations,
        "assigned_department": assigned_department,
        "assigned_family": assigned_family,
        "assigned_role": assigned_role,
        "priority": priority,
        "estimated_complexity": estimated_complexity,
        "notes": notes or "",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_work_orders_from_runtime_result(result: dict) -> list[dict]:
    command = result.get("command", "empty")
    raw_work_orders = result.get("work_orders", [])
    work_orders = []
    
    if isinstance(raw_work_orders, list) and len(raw_work_orders) > 0:
        for idx, rwo in enumerate(raw_work_orders, 1):
            title = rwo.get("purpose") or rwo.get("task") or f"Work Order {idx}"
            description = rwo.get("task") or rwo.get("purpose") or "Execute task through dry-run skeleton."
            wo = create_work_order(
                command,
                title=title,
                description=description,
                work_order_type=result.get("command_type", "general"),
                index=idx,
                assigned_department=rwo.get("overlay_id")
            )
            work_orders.append(wo)
    else:
        wo = create_work_order(
            command,
            title="Review and execute command through dry-run skeleton",
            description="Create a dry-run-only executable work order skeleton for the Station Chief command.",
            work_order_type=result.get("command_type", "general"),
            index=1
        )
        work_orders.append(wo)
        
    return work_orders

def create_work_order_status_lifecycle() -> dict:
    return {
        "work_order_status_lifecycle_version": "3.4.0",
        "statuses": {
            "CREATED": {"description": "Work order skeleton exists."},
            "READY": {"description": "Work order passed dry-run preflight."},
            "BLOCKED": {"description": "Work order cannot proceed due to dependency or safety issue."},
            "DRY_RUN_STARTED": {"description": "Dry-run simulation began."},
            "DRY_RUN_COMPLETE": {"description": "Dry-run simulation completed without side effects."},
            "COMPLETION_PROOF_CREATED": {"description": "Completion proof artifact was created."},
            "FAILED_VALIDATION": {"description": "Work order failed validation."}
        },
        "allowed_transitions": [
            "CREATED -> READY",
            "CREATED -> BLOCKED",
            "READY -> DRY_RUN_STARTED",
            "DRY_RUN_STARTED -> DRY_RUN_COMPLETE",
            "DRY_RUN_COMPLETE -> COMPLETION_PROOF_CREATED",
            "READY -> BLOCKED",
            "DRY_RUN_STARTED -> FAILED_VALIDATION",
            "DRY_RUN_COMPLETE -> FAILED_VALIDATION"
        ],
        "terminal_statuses": [
            "BLOCKED",
            "COMPLETION_PROOF_CREATED",
            "FAILED_VALIDATION"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_work_order_dependency_map(work_orders: list[dict]) -> dict:
    all_ids = [wo["work_order_id"] for wo in work_orders]
    dependency_map = {}
    unresolved = {}
    ready_ids = []
    blocked_ids = []
    
    for wo in work_orders:
        wid = wo["work_order_id"]
        deps = wo["dependencies"]
        dependency_map[wid] = deps
        
        missing = [d for d in deps if d not in all_ids]
        if missing:
            unresolved[wid] = missing
            blocked_ids.append(wid)
        else:
            ready_ids.append(wid)
            
    status = "UNRESOLVED_DEPENDENCIES" if unresolved else "CLEAR"
    
    return {
        "work_order_dependency_map_version": "3.4.0",
        "work_order_count": len(work_orders),
        "dependency_map": dependency_map,
        "unresolved_dependencies": unresolved,
        "ready_work_order_ids": ready_ids,
        "blocked_work_order_ids": blocked_ids,
        "dependency_status": status,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def dry_run_execute_work_order(work_order: dict, dependency_map: dict) -> dict:
    wid = work_order["work_order_id"]
    if wid in dependency_map["blocked_work_order_ids"]:
        dr_status = "BLOCKED"
        f_status = "BLOCKED"
        path = ["CREATED", "BLOCKED"]
    else:
        dr_status = "PASS"
        f_status = "DRY_RUN_COMPLETE"
        path = ["CREATED", "READY", "DRY_RUN_STARTED", "DRY_RUN_COMPLETE"]
        
    return {
        "work_order_dry_run_result_version": "3.4.0",
        "work_order_id": wid,
        "dry_run_status": dr_status,
        "initial_status": "CREATED",
        "final_status": f_status,
        "simulated_status_path": path,
        "acceptance_criteria_checked": work_order["acceptance_criteria"],
        "safety_constraints_checked": work_order["safety_constraints"],
        "artifacts_expected": work_order["artifact_expectations"],
        "artifacts_created": [],
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def dry_run_execute_work_orders(work_orders: list[dict], dependency_map: dict) -> list[dict]:
    results = []
    for wo in work_orders:
        results.append(dry_run_execute_work_order(wo, dependency_map))
    return results

def create_work_order_execution_ledger(work_orders: list[dict], dry_run_results: list[dict]) -> dict:
    results_map = {res["work_order_id"]: res for res in dry_run_results}
    entries = []
    pass_count = 0
    blocked_count = 0
    failed_count = 0
    
    for wo in work_orders:
        wid = wo["work_order_id"]
        res = results_map.get(wid)
        
        dr_status = res["dry_run_status"] if res else "UNKNOWN"
        f_status = res["final_status"] if res else "UNKNOWN"
        
        if dr_status == "PASS":
            pass_count += 1
        elif dr_status == "BLOCKED":
            blocked_count += 1
        else:
            failed_count += 1
            
        entries.append({
            "work_order_id": wid,
            "title": wo["title"],
            "dry_run_status": dr_status,
            "final_status": f_status,
            "execution_mode": wo["execution_mode"],
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "repo_files_modified": False
        })
        
    return {
        "work_order_execution_ledger_version": "3.4.0",
        "ledger_status": "DRY_RUN_ONLY",
        "work_order_count": len(work_orders),
        "dry_run_pass_count": pass_count,
        "blocked_count": blocked_count,
        "failed_count": failed_count,
        "entries": entries,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_work_order_completion_proof(work_order: dict, dry_run_result: dict) -> dict:
    wid = work_order["work_order_id"]
    status = "PROOF_CREATED" if dry_run_result["dry_run_status"] == "PASS" else "BLOCKED"
    
    proof_data = {
        "work_order": work_order,
        "dry_run_result": dry_run_result,
        "proof_status": status
    }
    digest = sha256_digest(proof_data)
    
    return {
        "work_order_completion_proof_version": "3.4.0",
        "work_order_id": wid,
        "proof_status": status,
        "dry_run_status": dry_run_result["dry_run_status"],
        "final_status": dry_run_result["final_status"],
        "acceptance_criteria_met": dry_run_result["dry_run_status"] == "PASS",
        "safety_constraints_met": True,
        "completion_digest": digest,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_work_order_completion_proofs(work_orders: list[dict], dry_run_results: list[dict]) -> list[dict]:
    results_map = {res["work_order_id"]: res for res in dry_run_results}
    proofs = []
    for wo in work_orders:
        res = results_map.get(wo["work_order_id"])
        if res:
            proofs.append(create_work_order_completion_proof(wo, res))
    return proofs

def create_work_order_executor_summary(
    work_orders: list[dict],
    dependency_map: dict,
    dry_run_results: list[dict],
    execution_ledger: dict,
    completion_proofs: list[dict]
) -> dict:
    wo_count = len(work_orders)
    dr_pass = execution_ledger["dry_run_pass_count"]
    cp_count = len(completion_proofs)
    
    ready_for_next = (
        dependency_map["dependency_status"] == "CLEAR"
        and wo_count >= 1
        and dr_pass == wo_count
        and cp_count == wo_count
    )
    
    return {
        "work_order_executor_summary_version": "3.4.0",
        "executor_status": "DRY_RUN_ONLY",
        "work_order_count": wo_count,
        "ready_count": len(dependency_map["ready_work_order_ids"]),
        "blocked_count": len(dependency_map["blocked_work_order_ids"]),
        "dry_run_pass_count": dr_pass,
        "completion_proof_count": cp_count,
        "ready_for_worker_hiring_registry": ready_for_next,
        "next_layer": "Worker Hiring Registry",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_work_order_executor_bundle(result: dict) -> dict:
    schema = create_executable_work_order_schema()
    work_orders = create_work_orders_from_runtime_result(result)
    lifecycle = create_work_order_status_lifecycle()
    dep_map = create_work_order_dependency_map(work_orders)
    dr_results = dry_run_execute_work_orders(work_orders, dep_map)
    ledger = create_work_order_execution_ledger(work_orders, dr_results)
    proofs = create_work_order_completion_proofs(work_orders, dr_results)
    summary = create_work_order_executor_summary(work_orders, dep_map, dr_results, ledger, proofs)
    
    return {
        "work_order_executor_bundle_version": "3.4.0",
        "executor_status": WORK_ORDER_EXECUTOR_STATUS,
        "executable_work_order_schema": schema,
        "work_orders": work_orders,
        "work_order_status_lifecycle": lifecycle,
        "work_order_dependency_map": dep_map,
        "work_order_dry_run_results": dr_results,
        "work_order_execution_ledger": ledger,
        "work_order_completion_proofs": proofs,
        "work_order_executor_summary": summary,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }
