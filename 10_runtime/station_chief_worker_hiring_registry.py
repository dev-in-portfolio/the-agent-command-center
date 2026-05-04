import json
import hashlib
import re
from pathlib import Path

WORKER_HIRING_REGISTRY_MODULE_VERSION = "1.6.0"
WORKER_HIRING_REGISTRY_STATUS = "REGISTRY_PREVIEW_ONLY"
WORKER_HIRING_REGISTRY_PHASE = "Worker Hiring Registry"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_worker_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "worker"

def generate_worker_id(command: str, role_label: str, index: int, runtime_version: str = "3.3.0") -> str:
    normalized_label = normalize_worker_label(role_label)
    hash_input = f"{runtime_version}:{command}:{role_label}:{index}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"worker-v3-3-{normalized_label}-{index:03d}-{hash_chars}"

def create_worker_role_schema() -> dict:
    return {
        "worker_role_schema_version": "3.3.0",
        "schema_status": "REGISTRY_PREVIEW_ONLY",
        "required_fields": [
            "worker_id",
            "worker_role_title",
            "worker_role_type",
            "worker_status",
            "worker_mode",
            "source_work_order_id",
            "responsibilities",
            "required_inputs",
            "expected_outputs",
            "safety_constraints",
            "assignment_scope"
        ],
        "optional_fields": [
            "assigned_department",
            "assigned_family",
            "assigned_unit",
            "assigned_team",
            "priority",
            "estimated_complexity",
            "notes"
        ],
        "allowed_worker_statuses": [
            "CANDIDATE_CREATED",
            "PREVIEW_READY",
            "ASSIGNMENT_PLANNED",
            "BLOCKED",
            "REGISTRY_RECORDED",
            "FAILED_VALIDATION"
        ],
        "allowed_worker_modes": [
            "registry_preview_only",
            "dry_run_assignment_only",
            "artifact_only"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no shell command execution",
            "no package installation",
            "worker records are registry previews only"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_candidate(
    command: str,
    source_work_order: dict,
    role_title: str,
    role_type: str = "executor_preview",
    index: int = 1,
    responsibilities: list[str] | None = None,
    required_inputs: list[str] | None = None,
    expected_outputs: list[str] | None = None,
    safety_constraints: list[str] | None = None,
    assignment_scope: str = "single_work_order_preview",
    worker_mode: str = "registry_preview_only",
    assigned_department: str | None = None,
    assigned_family: str | None = None,
    assigned_unit: str | None = None,
    assigned_team: str | None = None,
    priority: str = "normal",
    estimated_complexity: str = "medium",
    notes: str | None = None
) -> dict:
    if responsibilities is None:
        responsibilities = [
            "Review source work order.",
            "Prepare dry-run-only execution plan.",
            "Produce artifact expectations without live execution."
        ]
    if required_inputs is None:
        required_inputs = [
            source_work_order.get("work_order_id"),
            source_work_order.get("title"),
            source_work_order.get("acceptance_criteria")
        ]
    if expected_outputs is None:
        expected_outputs = [
            "worker_candidate.json",
            "worker_assignment_plan.json",
            "worker_registry_entry.json"
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
    
    worker_id = generate_worker_id(command, role_title, index)
    
    return {
        "worker_candidate_version": "1.6.0",
        "worker_id": worker_id,
        "worker_role_title": role_title,
        "worker_role_type": role_type,
        "worker_status": "CANDIDATE_CREATED",
        "worker_mode": worker_mode,
        "source_work_order_id": source_work_order.get("work_order_id"),
        "source_work_order_title": source_work_order.get("title"),
        "responsibilities": responsibilities,
        "required_inputs": required_inputs,
        "expected_outputs": expected_outputs,
        "safety_constraints": safety_constraints,
        "assignment_scope": assignment_scope,
        "assigned_department": assigned_department,
        "assigned_family": assigned_family,
        "assigned_unit": assigned_unit,
        "assigned_team": assigned_team,
        "priority": priority,
        "estimated_complexity": estimated_complexity,
        "notes": notes or "",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_candidates_from_work_orders(result: dict) -> list[dict]:
    command = result.get("command", "empty")
    raw_work_orders = result.get("work_orders_executable") or result.get("work_orders", [])
    candidates = []
    
    if not raw_work_orders:
        mock_wo = {"work_order_id": "WO-GENERIC", "title": "Generic Command Task"}
        candidates.append(create_worker_candidate(command, mock_wo, f"Dry-Run Executor for {command}"))
    else:
        for idx, wo in enumerate(raw_work_orders, 1):
            candidates.append(create_worker_candidate(
                command, 
                wo, 
                f"Dry-Run Executor for {wo.get('title', 'Unknown Task')}",
                role_type="work_order_executor_preview",
                index=idx,
                assigned_department=wo.get("assigned_department")
            ))
            
    return candidates

def create_worker_registry_status_lifecycle() -> dict:
    return {
        "worker_registry_status_lifecycle_version": "1.6.0",
        "statuses": {
            "CANDIDATE_CREATED": {"description": "Worker candidate record exists."},
            "PREVIEW_READY": {"description": "Worker candidate passed registry preflight."},
            "ASSIGNMENT_PLANNED": {"description": "Worker assignment plan was created."},
            "BLOCKED": {"description": "Worker candidate cannot proceed due to safety or dependency issue."},
            "REGISTRY_RECORDED": {"description": "Worker candidate was recorded in the preview registry."},
            "FAILED_VALIDATION": {"description": "Worker candidate failed validation."}
        },
        "allowed_transitions": [
            "CANDIDATE_CREATED -> PREVIEW_READY",
            "CANDIDATE_CREATED -> BLOCKED",
            "PREVIEW_READY -> ASSIGNMENT_PLANNED",
            "ASSIGNMENT_PLANNED -> REGISTRY_RECORDED",
            "PREVIEW_READY -> BLOCKED",
            "ASSIGNMENT_PLANNED -> FAILED_VALIDATION"
        ],
        "terminal_statuses": [
            "BLOCKED",
            "REGISTRY_RECORDED",
            "FAILED_VALIDATION"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_assignment_plan(worker_candidates: list[dict]) -> dict:
    assignments = []
    blocked_ids = []
    ready_ids = []
    
    for candidate in worker_candidates:
        wid = candidate.get("worker_id")
        source_wo_id = candidate.get("source_work_order_id")
        
        status = "PLANNED_PREVIEW_ONLY"
        if not source_wo_id:
            status = "BLOCKED"
            blocked_ids.append(wid)
        else:
            ready_ids.append(wid)
            
        assignments.append({
            "worker_id": wid,
            "source_work_order_id": source_wo_id,
            "assignment_status": status,
            "assignment_scope": candidate.get("assignment_scope"),
            "worker_mode": candidate.get("worker_mode"),
            "real_worker_hiring_performed": False,
            "live_worker_agents_activated": False
        })
        
    assignment_status = "BLOCKED" if blocked_ids else "PLANNED_PREVIEW_ONLY"
    
    return {
        "worker_assignment_plan_version": "1.6.0",
        "assignment_status": assignment_status,
        "worker_count": len(worker_candidates),
        "assignments": assignments,
        "blocked_worker_ids": blocked_ids,
        "ready_worker_ids": ready_ids,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_registry_ledger(worker_candidates: list[dict], assignment_plan: dict) -> dict:
    assignments_map = {a["worker_id"]: a for a in assignment_plan.get("assignments", [])}
    entries = []
    ready_count = 0
    planned_count = 0
    blocked_count = 0
    
    for candidate in worker_candidates:
        wid = candidate["worker_id"]
        assignment = assignments_map.get(wid, {})
        
        astatus = assignment.get("assignment_status", "UNKNOWN")
        if astatus == "PLANNED_PREVIEW_ONLY":
            planned_count += 1
            ready_count += 1
        elif astatus == "BLOCKED":
            blocked_count += 1
            
        entries.append({
            "worker_id": wid,
            "worker_role_title": candidate["worker_role_title"],
            "worker_role_type": candidate["worker_role_type"],
            "source_work_order_id": candidate["source_work_order_id"],
            "assignment_status": astatus,
            "worker_mode": candidate["worker_mode"],
            "real_worker_hiring_performed": False,
            "live_worker_agents_activated": False
        })
        
    return {
        "worker_registry_ledger_version": "1.6.0",
        "ledger_status": "REGISTRY_PREVIEW_ONLY",
        "worker_count": len(worker_candidates),
        "preview_ready_count": ready_count,
        "assignment_planned_count": planned_count,
        "blocked_count": blocked_count,
        "entries": entries,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_hiring_preview_record(worker_candidate: dict, assignment_entry: dict | None = None) -> dict:
    wid = worker_candidate["worker_id"]
    status = "PREVIEW_CREATED" if worker_candidate.get("source_work_order_id") else "BLOCKED"
    
    preview_data = {
        "worker_candidate": worker_candidate,
        "assignment_entry": assignment_entry,
        "preview_status": status
    }
    digest = sha256_digest(preview_data)
    
    return {
        "worker_hiring_preview_record_version": "1.6.0",
        "worker_id": wid,
        "preview_status": status,
        "worker_role_title": worker_candidate.get("worker_role_title"),
        "source_work_order_id": worker_candidate.get("source_work_order_id"),
        "assignment_status": assignment_entry.get("assignment_status") if assignment_entry else None,
        "hiring_digest": digest,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_worker_hiring_preview_records(worker_candidates: list[dict], assignment_plan: dict) -> list[dict]:
    assignments_map = {a["worker_id"]: a for a in assignment_plan.get("assignments", [])}
    records = []
    for candidate in worker_candidates:
        records.append(create_worker_hiring_preview_record(candidate, assignments_map.get(candidate["worker_id"])))
    return records

def create_worker_hiring_readiness_summary(
    worker_candidates: list[dict],
    assignment_plan: dict,
    registry_ledger: dict,
    preview_records: list[dict]
) -> dict:
    worker_count = len(worker_candidates)
    planned = registry_ledger["assignment_planned_count"]
    blocked = registry_ledger["blocked_count"]
    preview_count = len(preview_records)
    
    ready = (
        worker_count >= 1
        and blocked == 0
        and planned == worker_count
        and preview_count == worker_count
    )
    
    return {
        "worker_hiring_readiness_summary_version": "1.6.0",
        "registry_status": "REGISTRY_PREVIEW_ONLY",
        "worker_count": worker_count,
        "assignment_planned_count": planned,
        "blocked_count": blocked,
        "preview_record_count": preview_count,
        "ready_for_department_routing_runtime": ready,
        "next_layer": "Department Routing Runtime",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }

def create_department_routing_readiness_bridge(
    result: dict,
    worker_candidates: list[dict],
    readiness_summary: dict
) -> dict:
    return {
        "department_routing_readiness_bridge_version": "1.6.0",
        "current_layer": "Worker Hiring Registry",
        "next_layer": "Department Routing Runtime",
        "ready_for_department_routing_runtime": readiness_summary["ready_for_department_routing_runtime"],
        "worker_count": len(worker_candidates),
        "required_next_capabilities": [
            "department routing schema",
            "family-to-department routing map",
            "worker-to-department assignment map",
            "routing dry-run engine",
            "routing conflict detector",
            "routing completion proof",
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

def create_worker_hiring_registry_bundle(result: dict) -> dict:
    schema = create_worker_role_schema()
    candidates = create_worker_candidates_from_work_orders(result)
    lifecycle = create_worker_registry_status_lifecycle()
    plan = create_worker_assignment_plan(candidates)
    ledger = create_worker_registry_ledger(candidates, plan)
    previews = create_worker_hiring_preview_records(candidates, plan)
    summary = create_worker_hiring_readiness_summary(candidates, plan, ledger, previews)
    bridge = create_department_routing_readiness_bridge(result, candidates, summary)
    
    return {
        "worker_hiring_registry_bundle_version": "1.6.0",
        "registry_status": WORKER_HIRING_REGISTRY_STATUS,
        "worker_role_schema": schema,
        "worker_candidates": candidates,
        "worker_registry_status_lifecycle": lifecycle,
        "worker_assignment_plan": plan,
        "worker_registry_ledger": ledger,
        "worker_hiring_preview_records": previews,
        "worker_hiring_readiness_summary": summary,
        "department_routing_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False
    }
