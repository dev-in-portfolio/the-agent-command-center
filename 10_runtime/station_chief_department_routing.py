import json
import hashlib
import re
from pathlib import Path

DEPARTMENT_ROUTING_MODULE_VERSION = "1.5.0"
DEPARTMENT_ROUTING_STATUS = "ROUTING_PREVIEW_ONLY"
DEPARTMENT_ROUTING_PHASE = "Department Routing Runtime"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_route_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "route"

def generate_route_id(command: str, route_label: str, index: int, runtime_version: str = "2.9.0") -> str:
    normalized_label = normalize_route_label(route_label)
    hash_input = f"{runtime_version}:{command}:{route_label}:{index}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"route-v2-9-{normalized_label}-{index:03d}-{hash_chars}"

def create_department_routing_schema() -> dict:
    return {
        "department_routing_schema_version": "2.9.0",
        "schema_status": "ROUTING_PREVIEW_ONLY",
        "required_fields": [
            "route_id",
            "route_title",
            "route_type",
            "route_status",
            "route_mode",
            "source_worker_id",
            "source_work_order_id",
            "target_department",
            "target_family",
            "routing_reason",
            "routing_inputs",
            "expected_outputs",
            "safety_constraints"
        ],
        "optional_fields": [
            "target_unit",
            "target_team",
            "target_role",
            "priority",
            "estimated_complexity",
            "notes"
        ],
        "allowed_route_statuses": [
            "ROUTE_CANDIDATE_CREATED",
            "ROUTE_PREVIEW_READY",
            "ROUTE_PLANNED",
            "ROUTE_CONFLICT_DETECTED",
            "ROUTE_RECORDED",
            "BLOCKED",
            "FAILED_VALIDATION"
        ],
        "allowed_route_modes": [
            "routing_preview_only",
            "dry_run_routing_only",
            "artifact_only"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no live worker routing",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no shell command execution",
            "no package installation",
            "department routes are preview records only"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def infer_target_department(worker_candidate: dict, command_type: str | None = None) -> dict:
    assigned = worker_candidate.get("assigned_department")
    if assigned:
        # Simple mapping for assigned department to family if needed, but here we just use it
        return {
            "target_department": assigned,
            "target_family": worker_candidate.get("assigned_family") or "Agent Command",
            "routing_reason": "Requested department assignment preserved."
        }
    
    role_type = (worker_candidate.get("worker_role_type") or "").lower()
    role_title = (worker_candidate.get("worker_role_title") or "").lower()
    wo_title = (worker_candidate.get("source_work_order_title") or "").lower()
    
    engineering_terms = ["build", "repair", "engineering", "automation", "executor"]
    workflow_terms = ["route", "routing", "department", "workflow"]
    compliance_terms = ["governance", "compliance", "approval", "audit"]
    memory_terms = ["memory", "archive", "context", "architecture"]
    
    text = f"{role_type} {role_title} {wo_title}"
    
    if any(t in text for t in engineering_terms):
        return {
            "target_department": "Engineering & Automation",
            "target_family": "Engineering & Automation",
            "routing_reason": "Inferred from engineering-related terms."
        }
    if any(t in text for t in workflow_terms):
        return {
            "target_department": "Workflow Control Tower",
            "target_family": "Workflow Control Tower",
            "routing_reason": "Inferred from workflow-related terms."
        }
    if any(t in text for t in compliance_terms):
        return {
            "target_department": "Quality, Risk & Compliance",
            "target_family": "Quality, Risk & Compliance",
            "routing_reason": "Inferred from compliance-related terms."
        }
    if any(t in text for t in memory_terms):
        return {
            "target_department": "Memory Engineering & Context Architecture",
            "target_family": "Memory Engineering & Context Architecture",
            "routing_reason": "Inferred from memory-related terms."
        }
        
    return {
        "target_department": "Station Chief Operations",
        "target_family": "Agent Command",
        "routing_reason": "Defaulted to Station Chief Operations."
    }

def create_department_route_candidate(
    command: str,
    worker_candidate: dict,
    command_type: str | None = None,
    index: int = 1
) -> dict:
    target = infer_target_department(worker_candidate, command_type)
    route_id = generate_route_id(command, worker_candidate.get("worker_role_title", "route"), index)
    
    return {
        "department_route_candidate_version": "1.5.0",
        "route_id": route_id,
        "route_title": f"Route {worker_candidate.get('worker_role_title')}",
        "route_type": "worker_to_department_preview",
        "route_status": "ROUTE_CANDIDATE_CREATED",
        "route_mode": "routing_preview_only",
        "source_worker_id": worker_candidate.get("worker_id"),
        "source_work_order_id": worker_candidate.get("source_work_order_id"),
        "target_department": target["target_department"],
        "target_family": target["target_family"],
        "routing_reason": target["routing_reason"],
        "routing_inputs": [
            worker_candidate.get("worker_id"),
            worker_candidate.get("source_work_order_id"),
            worker_candidate.get("worker_role_title"),
            worker_candidate.get("worker_role_type")
        ],
        "expected_outputs": [
            "department_route_candidate.json",
            "worker_to_department_assignment_map.json",
            "routing_completion_proof.json"
        ],
        "safety_constraints": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no live worker routing",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation"
        ],
        "priority": worker_candidate.get("priority", "normal"),
        "estimated_complexity": worker_candidate.get("estimated_complexity", "medium"),
        "notes": "",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_department_route_candidates_from_worker_registry(result: dict) -> list[dict]:
    command = result.get("command", "empty")
    command_type = result.get("command_type")
    
    worker_candidates = result.get("worker_candidates")
    if not worker_candidates and "worker_hiring_registry_bundle" in result:
        worker_candidates = result["worker_hiring_registry_bundle"].get("worker_candidates")
        
    routes = []
    if worker_candidates:
        for idx, wc in enumerate(worker_candidates, 1):
            routes.append(create_department_route_candidate(command, wc, command_type, idx))
    else:
        # Mock worker candidate
        mock_wc = {
            "worker_id": "worker-mock-001",
            "worker_role_title": "Mock Preview Executor",
            "worker_role_type": "executor_preview",
            "source_work_order_id": "WO-MOCK-001"
        }
        routes.append(create_department_route_candidate(command, mock_wc, command_type, 1))
        
    return routes

def create_family_to_department_routing_map(route_candidates: list[dict]) -> dict:
    by_department = {}
    by_family = {}
    
    for rc in route_candidates:
        dept = rc["target_department"]
        fam = rc["target_family"]
        rid = rc["route_id"]
        
        if dept not in by_department:
            by_department[dept] = []
        by_department[dept].append(rid)
        
        if fam not in by_family:
            by_family[fam] = []
        by_family[fam].append(rid)
        
    return {
        "family_to_department_routing_map_version": "1.5.0",
        "map_status": "ROUTING_PREVIEW_ONLY",
        "department_count": len(by_department),
        "family_count": len(by_family),
        "routes_by_department": by_department,
        "routes_by_family": by_family,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_worker_to_department_assignment_map(route_candidates: list[dict]) -> dict:
    assignments = []
    blocked_ids = []
    ready_ids = []
    
    for rc in route_candidates:
        rid = rc["route_id"]
        wid = rc["source_worker_id"]
        dept = rc["target_department"]
        
        status = "PLANNED_PREVIEW_ONLY"
        if not wid or not dept:
            status = "BLOCKED"
            blocked_ids.append(wid or rid)
        else:
            ready_ids.append(wid)
            
        assignments.append({
            "route_id": rid,
            "worker_id": wid,
            "source_work_order_id": rc["source_work_order_id"],
            "target_department": dept,
            "target_family": rc["target_family"],
            "assignment_status": status,
            "live_worker_routing_performed": False
        })
        
    return {
        "worker_to_department_assignment_map_version": "1.5.0",
        "assignment_status": "ROUTING_PREVIEW_ONLY",
        "worker_route_count": len(route_candidates),
        "assignments": assignments,
        "blocked_worker_ids": blocked_ids,
        "ready_worker_ids": ready_ids,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def detect_department_routing_conflicts(route_candidates: list[dict]) -> dict:
    route_ids = [rc["route_id"] for rc in route_candidates]
    duplicates = [rid for rid in set(route_ids) if route_ids.count(rid) > 1]
    
    missing_target = [rc["route_id"] for rc in route_candidates if not rc.get("target_department")]
    missing_source = [rc["route_id"] for rc in route_candidates if not rc.get("source_worker_id")]
    
    worker_to_depts = {}
    for rc in route_candidates:
        wid = rc["source_worker_id"]
        dept = rc["target_department"]
        if wid and dept:
            if wid not in worker_to_depts:
                worker_to_depts[wid] = set()
            worker_to_depts[wid].add(dept)
            
    multi_dept = [wid for wid, depts in worker_to_depts.items() if len(depts) > 1]
    
    conflict_count = len(duplicates) + len(missing_target) + len(missing_source) + len(multi_dept)
    status = "CLEAR" if conflict_count == 0 else "CONFLICTS_DETECTED"
    
    return {
        "department_routing_conflict_detector_version": "1.5.0",
        "conflict_status": status,
        "duplicate_route_ids": duplicates,
        "missing_target_department_route_ids": missing_target,
        "missing_source_worker_route_ids": missing_source,
        "multi_department_worker_conflicts": multi_dept,
        "conflict_count": conflict_count,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def dry_run_department_routing(route_candidates: list[dict], conflict_detector: dict) -> list[dict]:
    results = []
    blocked_rids = set(conflict_detector["duplicate_route_ids"] + 
                       conflict_detector["missing_target_department_route_ids"] + 
                       conflict_detector["missing_source_worker_route_ids"])
    
    # Also block routes for workers in multi-dept conflict
    multi_workers = set(conflict_detector["multi_department_worker_conflicts"])
    
    for rc in route_candidates:
        rid = rc["route_id"]
        wid = rc["source_worker_id"]
        
        if rid in blocked_rids or wid in multi_workers:
            status = "BLOCKED"
            path = ["ROUTE_CANDIDATE_CREATED", "BLOCKED"]
        else:
            status = "PASS"
            path = ["ROUTE_CANDIDATE_CREATED", "ROUTE_PREVIEW_READY", "ROUTE_PLANNED", "ROUTE_RECORDED"]
            
        results.append({
            "department_routing_dry_run_result_version": "1.5.0",
            "route_id": rid,
            "worker_id": wid,
            "target_department": rc["target_department"],
            "dry_run_status": status,
            "simulated_status_path": path,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "real_worker_hiring_performed": False,
            "live_worker_routing_performed": False,
            "repo_files_modified": False,
            "execution_authorized": False
        })
        
    return results

def create_department_routing_ledger(route_candidates: list[dict], dry_run_results: list[dict]) -> dict:
    res_map = {r["route_id"]: r for r in dry_run_results}
    entries = []
    pass_count = 0
    blocked_count = 0
    
    for rc in route_candidates:
        rid = rc["route_id"]
        res = res_map.get(rid)
        
        dstatus = res["dry_run_status"] if res else "UNKNOWN"
        if dstatus == "PASS":
            pass_count += 1
        else:
            blocked_count += 1
            
        entries.append({
            "route_id": rid,
            "worker_id": rc["source_worker_id"],
            "source_work_order_id": rc["source_work_order_id"],
            "target_department": rc["target_department"],
            "target_family": rc["target_family"],
            "dry_run_status": dstatus,
            "live_worker_routing_performed": False
        })
        
    return {
        "department_routing_ledger_version": "1.5.0",
        "ledger_status": "ROUTING_PREVIEW_ONLY",
        "route_count": len(route_candidates),
        "dry_run_pass_count": pass_count,
        "blocked_count": blocked_count,
        "entries": entries,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_department_routing_completion_proof(route_candidate: dict, dry_run_result: dict) -> dict:
    status = "PROOF_CREATED" if dry_run_result["dry_run_status"] == "PASS" else "BLOCKED"
    
    proof_data = {
        "route_candidate": route_candidate,
        "dry_run_result": dry_run_result,
        "proof_status": status
    }
    digest = sha256_digest(proof_data)
    
    return {
        "department_routing_completion_proof_version": "1.5.0",
        "route_id": route_candidate["route_id"],
        "worker_id": route_candidate["source_worker_id"],
        "proof_status": status,
        "dry_run_status": dry_run_result["dry_run_status"],
        "routing_constraints_met": dry_run_result["dry_run_status"] == "PASS",
        "safety_constraints_met": True,
        "completion_digest": digest,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_department_routing_completion_proofs(route_candidates: list[dict], dry_run_results: list[dict]) -> list[dict]:
    res_map = {r["route_id"]: r for r in dry_run_results}
    proofs = []
    for rc in route_candidates:
        res = res_map.get(rc["route_id"])
        if res:
            proofs.append(create_department_routing_completion_proof(rc, res))
    return proofs

def create_department_routing_readiness_summary(
    route_candidates: list[dict],
    conflict_detector: dict,
    routing_ledger: dict,
    completion_proofs: list[dict]
) -> dict:
    rc_count = len(route_candidates)
    pass_count = routing_ledger["dry_run_pass_count"]
    proof_count = len(completion_proofs)
    
    ready = (
        rc_count >= 1
        and conflict_detector["conflict_count"] == 0
        and pass_count == rc_count
        and proof_count == rc_count
    )
    
    return {
        "department_routing_readiness_summary_version": "1.5.0",
        "routing_status": "ROUTING_PREVIEW_ONLY",
        "route_count": rc_count,
        "dry_run_pass_count": pass_count,
        "blocked_count": routing_ledger["blocked_count"],
        "conflict_count": conflict_detector["conflict_count"],
        "completion_proof_count": proof_count,
        "ready_for_multi_agent_orchestration_sandbox": ready,
        "next_layer": "Multi-Agent Orchestration Sandbox",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_multi_agent_orchestration_readiness_bridge(
    result: dict,
    route_candidates: list[dict],
    readiness_summary: dict
) -> dict:
    return {
        "multi_agent_orchestration_readiness_bridge_version": "1.5.0",
        "current_layer": "Department Routing Runtime",
        "next_layer": "Multi-Agent Orchestration Sandbox",
        "ready_for_multi_agent_orchestration_sandbox": readiness_summary["ready_for_multi_agent_orchestration_sandbox"],
        "route_count": len(route_candidates),
        "required_next_capabilities": [
            "orchestration topology schema",
            "multi-worker dry-run coordination map",
            "task handoff simulation",
            "inter-worker dependency graph",
            "orchestration conflict detector",
            "orchestration completion proof",
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
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_department_routing_bundle(result: dict) -> dict:
    schema = create_department_routing_schema()
    candidates = create_department_route_candidates_from_worker_registry(result)
    fam_map = create_family_to_department_routing_map(candidates)
    assign_map = create_worker_to_department_assignment_map(candidates)
    conflicts = detect_department_routing_conflicts(candidates)
    dr_results = dry_run_department_routing(candidates, conflicts)
    ledger = create_department_routing_ledger(candidates, dr_results)
    proofs = create_department_routing_completion_proofs(candidates, dr_results)
    summary = create_department_routing_readiness_summary(candidates, conflicts, ledger, proofs)
    bridge = create_multi_agent_orchestration_readiness_bridge(result, candidates, summary)
    
    return {
        "department_routing_bundle_version": "1.5.0",
        "routing_status": DEPARTMENT_ROUTING_STATUS,
        "department_routing_schema": schema,
        "department_route_candidates": candidates,
        "family_to_department_routing_map": fam_map,
        "worker_to_department_assignment_map": assign_map,
        "department_routing_conflict_detector": conflicts,
        "department_routing_dry_run_results": dr_results,
        "department_routing_ledger": ledger,
        "department_routing_completion_proofs": proofs,
        "department_routing_readiness_summary": summary,
        "multi_agent_orchestration_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }
