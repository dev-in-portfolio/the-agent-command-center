import json
import hashlib
import re
from pathlib import Path

MULTI_AGENT_ORCHESTRATION_MODULE_VERSION = "1.6.0"
MULTI_AGENT_ORCHESTRATION_STATUS = "ORCHESTRATION_SANDBOX_ONLY"
MULTI_AGENT_ORCHESTRATION_PHASE = "Multi-Agent Orchestration Sandbox"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_orchestration_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "orchestration"

def generate_orchestration_id(command: str, label: str, index: int, runtime_version: str = "3.5.0") -> str:
    normalized_label = normalize_orchestration_label(label)
    hash_input = f"{runtime_version}:{command}:{label}:{index}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"orchestration-v3-4-{normalized_label}-{index:03d}-{hash_chars}"

def create_orchestration_topology_schema() -> dict:
    return {
        "orchestration_topology_schema_version": "3.5.0",
        "schema_status": "ORCHESTRATION_SANDBOX_ONLY",
        "required_fields": [
            "orchestration_id",
            "orchestration_title",
            "orchestration_type",
            "orchestration_status",
            "orchestration_mode",
            "source_route_id",
            "source_worker_id",
            "source_work_order_id",
            "target_department",
            "target_family",
            "coordination_role",
            "handoff_inputs",
            "expected_outputs",
            "safety_constraints"
        ],
        "optional_fields": [
            "upstream_node_ids",
            "downstream_node_ids",
            "priority",
            "estimated_complexity",
            "notes"
        ],
        "allowed_node_statuses": [
            "NODE_CANDIDATE_CREATED",
            "NODE_PREVIEW_READY",
            "NODE_COORDINATION_PLANNED",
            "NODE_HANDOFF_SIMULATED",
            "NODE_RECORDED",
            "ORCHESTRATION_CONFLICT_DETECTED",
            "BLOCKED",
            "FAILED_VALIDATION"
        ],
        "allowed_orchestration_modes": [
            "orchestration_sandbox_only",
            "dry_run_coordination_only",
            "artifact_only"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no live worker routing",
            "no live orchestration",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no shell command execution",
            "no package installation",
            "orchestration records are sandbox preview records only"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_orchestration_node(
    command: str,
    route_candidate: dict,
    index: int = 1
) -> dict:
    dept = (route_candidate.get("target_department") or "").lower()
    
    if "engineering" in dept or "automation" in dept:
        role = "implementation_node"
    elif "workflow" in dept or "routing" in dept:
        role = "routing_node"
    elif any(t in dept for t in ["quality", "risk", "compliance", "approval", "audit"]):
        role = "audit_node"
    elif any(t in dept for t in ["memory", "archive", "context"]):
        role = "memory_node"
    else:
        role = "general_coordination_node"
        
    orchestration_id = generate_orchestration_id(command, route_candidate.get("route_title", "coord"), index)
    
    return {
        "orchestration_node_version": "1.6.0",
        "orchestration_id": orchestration_id,
        "orchestration_title": f"Coordinate {route_candidate.get('route_title', 'Route')}",
        "orchestration_type": "department_route_coordination_preview",
        "orchestration_status": "NODE_CANDIDATE_CREATED",
        "orchestration_mode": "orchestration_sandbox_only",
        "source_route_id": route_candidate.get("route_id"),
        "source_worker_id": route_candidate.get("source_worker_id"),
        "source_work_order_id": route_candidate.get("source_work_order_id"),
        "target_department": route_candidate.get("target_department"),
        "target_family": route_candidate.get("target_family"),
        "coordination_role": role,
        "handoff_inputs": [
            route_candidate.get("route_id"),
            route_candidate.get("source_worker_id"),
            route_candidate.get("source_work_order_id"),
            route_candidate.get("target_department"),
            route_candidate.get("target_family")
        ],
        "expected_outputs": [
            "orchestration_node.json",
            "multi_worker_coordination_map.json",
            "task_handoff_simulation.json",
            "orchestration_completion_proof.json"
        ],
        "safety_constraints": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no live worker routing",
            "no live orchestration",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation"
        ],
        "upstream_node_ids": [],
        "downstream_node_ids": [],
        "priority": route_candidate.get("priority", "normal"),
        "estimated_complexity": route_candidate.get("estimated_complexity", "medium"),
        "notes": "",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_orchestration_nodes_from_department_routing(result: dict) -> list[dict]:
    command = result.get("command", "empty")
    route_candidates = result.get("department_route_candidates")
    if not route_candidates and "department_routing_bundle" in result:
        route_candidates = result["department_routing_bundle"].get("department_route_candidates")
        
    nodes = []
    if route_candidates:
        for idx, rc in enumerate(route_candidates, 1):
            nodes.append(create_orchestration_node(command, rc, idx))
    else:
        # Mock route candidate
        mock_rc = {
            "route_id": "route-mock-001",
            "route_title": "Mock Route",
            "source_worker_id": "worker-mock-001",
            "source_work_order_id": "WO-MOCK-001",
            "target_department": "Station Chief Operations",
            "target_family": "Agent Command"
        }
        nodes.append(create_orchestration_node(command, mock_rc, 1))
        
    return nodes

def create_multi_worker_coordination_map(orchestration_nodes: list[dict]) -> dict:
    by_dept = {}
    by_family = {}
    by_role = {}
    ready_ids = []
    blocked_ids = []
    
    for node in orchestration_nodes:
        nid = node["orchestration_id"]
        dept = node["target_department"]
        fam = node["target_family"]
        role = node["coordination_role"]
        wid = node["source_worker_id"]
        
        if dept not in by_dept: by_dept[dept] = []
        by_dept[dept].append(nid)
        
        if fam not in by_family: by_family[fam] = []
        by_family[fam].append(nid)
        
        if role not in by_role: by_role[role] = []
        by_role[role].append(nid)
        
        if not wid or not dept:
            blocked_ids.append(nid)
        else:
            ready_ids.append(nid)
            
    return {
        "multi_worker_coordination_map_version": "1.6.0",
        "map_status": "ORCHESTRATION_SANDBOX_ONLY",
        "node_count": len(orchestration_nodes),
        "coordination_by_department": by_dept,
        "coordination_by_family": by_family,
        "coordination_by_role": by_role,
        "ready_node_ids": ready_ids,
        "blocked_node_ids": blocked_ids,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_task_handoff_simulation(orchestration_nodes: list[dict], coordination_map: dict) -> dict:
    handoffs = []
    blocked_ids = []
    ready_ids = []
    
    for node in orchestration_nodes:
        nid = node["orchestration_id"]
        hid = f"handoff-{nid}"
        
        status = "SIMULATED_PREVIEW_ONLY"
        if nid in coordination_map["blocked_node_ids"]:
            status = "BLOCKED"
            blocked_ids.append(hid)
        else:
            ready_ids.append(hid)
            
        handoffs.append({
            "handoff_id": hid,
            "orchestration_id": nid,
            "source_worker_id": node["source_worker_id"],
            "source_work_order_id": node["source_work_order_id"],
            "target_department": node["target_department"],
            "coordination_role": node["coordination_role"],
            "handoff_status": status,
            "handoff_inputs": node["handoff_inputs"],
            "expected_outputs": node["expected_outputs"],
            "live_orchestration_performed": False
        })
        
    return {
        "task_handoff_simulation_version": "1.6.0",
        "simulation_status": "SANDBOX_PREVIEW_ONLY",
        "handoff_count": len(handoffs),
        "handoffs": handoffs,
        "blocked_handoff_ids": blocked_ids,
        "ready_handoff_ids": ready_ids,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_inter_worker_dependency_graph(orchestration_nodes: list[dict]) -> dict:
    graph = {}
    rev_graph = {}
    unresolved = {}
    ready_ids = []
    blocked_ids = []
    
    all_nids = [n["orchestration_id"] for n in orchestration_nodes]
    
    # Simple deterministic logic
    audit_nodes = [n["orchestration_id"] for n in orchestration_nodes if n["coordination_role"] == "audit_node"]
    non_audit_nodes = [n["orchestration_id"] for n in orchestration_nodes if n["coordination_role"] != "audit_node"]
    memory_nodes = [n["orchestration_id"] for n in orchestration_nodes if n["coordination_role"] == "memory_node"]
    routing_nodes = [n["orchestration_id"] for n in orchestration_nodes if n["coordination_role"] == "routing_node"]
    
    for node in orchestration_nodes:
        nid = node["orchestration_id"]
        deps = []
        
        if node["coordination_role"] == "audit_node":
            deps.extend(non_audit_nodes)
        elif node["coordination_role"] == "routing_node":
            deps.extend(memory_nodes)
            
        # Ensure no self-dependency
        if nid in deps: deps.remove(nid)
        
        graph[nid] = deps
        for d in deps:
            if d not in rev_graph: rev_graph[d] = []
            rev_graph[d].append(nid)
            
        missing = [d for d in deps if d not in all_nids]
        if missing:
            unresolved[nid] = missing
            blocked_ids.append(nid)
        else:
            ready_ids.append(nid)
            
    return {
        "inter_worker_dependency_graph_version": "1.6.0",
        "graph_status": "SANDBOX_PREVIEW_ONLY",
        "node_count": len(orchestration_nodes),
        "dependency_graph": graph,
        "reverse_dependency_graph": rev_graph,
        "unresolved_dependencies": unresolved,
        "ready_node_ids": ready_ids,
        "blocked_node_ids": blocked_ids,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def detect_orchestration_conflicts(
    orchestration_nodes: list[dict],
    coordination_map: dict,
    dependency_graph: dict
) -> dict:
    node_ids = [n["orchestration_id"] for n in orchestration_nodes]
    duplicates = [nid for nid in set(node_ids) if node_ids.count(nid) > 1]
    
    missing_source = [n["orchestration_id"] for n in orchestration_nodes if not n.get("source_worker_id")]
    missing_target = [n["orchestration_id"] for n in orchestration_nodes if not n.get("target_department")]
    
    unresolved = list(dependency_graph["unresolved_dependencies"].keys())
    
    worker_to_depts = {}
    for node in orchestration_nodes:
        wid = node["source_worker_id"]
        dept = node["target_department"]
        if wid and dept:
            if wid not in worker_to_depts: worker_to_depts[wid] = set()
            worker_to_depts[wid].add(dept)
    
    multi_dept = [wid for wid, depts in worker_to_depts.items() if len(depts) > 1]
    
    self_deps = []
    for nid, deps in dependency_graph["dependency_graph"].items():
        if nid in deps: self_deps.append(nid)
        
    conflict_count = len(duplicates) + len(missing_source) + len(missing_target) + len(unresolved) + len(multi_dept) + len(self_deps)
    status = "CLEAR" if conflict_count == 0 else "CONFLICTS_DETECTED"
    
    return {
        "orchestration_conflict_detector_version": "1.6.0",
        "conflict_status": status,
        "duplicate_orchestration_ids": duplicates,
        "missing_source_worker_node_ids": missing_source,
        "missing_target_department_node_ids": missing_target,
        "unresolved_dependency_node_ids": unresolved,
        "multi_department_worker_conflicts": multi_dept,
        "self_dependency_node_ids": self_deps,
        "conflict_count": conflict_count,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def dry_run_multi_agent_orchestration(
    orchestration_nodes: list[dict],
    conflict_detector: dict
) -> list[dict]:
    results = []
    
    blocked_nids = set(
        conflict_detector["duplicate_orchestration_ids"] +
        conflict_detector["missing_source_worker_node_ids"] +
        conflict_detector["missing_target_department_node_ids"] +
        conflict_detector["unresolved_dependency_node_ids"] +
        conflict_detector["self_dependency_node_ids"]
    )
    
    # Also block nodes for workers in multi-dept conflict
    multi_workers = set(conflict_detector["multi_department_worker_conflicts"])
    
    for node in orchestration_nodes:
        nid = node["orchestration_id"]
        wid = node["source_worker_id"]
        
        if nid in blocked_nids or wid in multi_workers:
            status = "BLOCKED"
            path = ["NODE_CANDIDATE_CREATED", "BLOCKED"]
        else:
            status = "PASS"
            path = ["NODE_CANDIDATE_CREATED", "NODE_PREVIEW_READY", "NODE_COORDINATION_PLANNED", "NODE_HANDOFF_SIMULATED", "NODE_RECORDED"]
            
        results.append({
            "orchestration_dry_run_result_version": "1.6.0",
            "orchestration_id": nid,
            "worker_id": wid,
            "target_department": node["target_department"],
            "coordination_role": node["coordination_role"],
            "dry_run_status": status,
            "simulated_status_path": path,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "real_worker_hiring_performed": False,
            "live_worker_routing_performed": False,
            "live_orchestration_performed": False,
            "repo_files_modified": False,
            "execution_authorized": False
        })
        
    return results

def create_orchestration_ledger(orchestration_nodes: list[dict], dry_run_results: list[dict]) -> dict:
    res_map = {r["orchestration_id"]: r for r in dry_run_results}
    entries = []
    pass_count = 0
    blocked_count = 0
    
    for node in orchestration_nodes:
        nid = node["orchestration_id"]
        res = res_map.get(nid)
        
        dstatus = res["dry_run_status"] if res else "UNKNOWN"
        if dstatus == "PASS":
            pass_count += 1
        else:
            blocked_count += 1
            
        entries.append({
            "orchestration_id": nid,
            "worker_id": node["source_worker_id"],
            "source_route_id": node["source_route_id"],
            "source_work_order_id": node["source_work_order_id"],
            "target_department": node["target_department"],
            "target_family": node["target_family"],
            "coordination_role": node["coordination_role"],
            "dry_run_status": dstatus,
            "live_orchestration_performed": False
        })
        
    return {
        "orchestration_ledger_version": "1.6.0",
        "ledger_status": "ORCHESTRATION_SANDBOX_ONLY",
        "node_count": len(orchestration_nodes),
        "dry_run_pass_count": pass_count,
        "blocked_count": blocked_count,
        "entries": entries,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_orchestration_completion_proof(orchestration_node: dict, dry_run_result: dict) -> dict:
    status = "PROOF_CREATED" if dry_run_result["dry_run_status"] == "PASS" else "BLOCKED"
    
    proof_data = {
        "orchestration_node": orchestration_node,
        "dry_run_result": dry_run_result,
        "proof_status": status
    }
    digest = sha256_digest(proof_data)
    
    return {
        "orchestration_completion_proof_version": "1.6.0",
        "orchestration_id": orchestration_node["orchestration_id"],
        "worker_id": orchestration_node["source_worker_id"],
        "proof_status": status,
        "dry_run_status": dry_run_result["dry_run_status"],
        "orchestration_constraints_met": dry_run_result["dry_run_status"] == "PASS",
        "safety_constraints_met": True,
        "completion_digest": digest,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }

def create_orchestration_completion_proofs(orchestration_nodes: list[dict], dry_run_results: list[dict]) -> list[dict]:
    res_map = {r["orchestration_id"]: r for r in dry_run_results}
    proofs = []
    for node in orchestration_nodes:
        res = res_map.get(node["orchestration_id"])
        if res:
            proofs.append(create_orchestration_completion_proof(node, res))
    return proofs

def create_orchestration_readiness_summary(
    orchestration_nodes: list[dict],
    conflict_detector: dict,
    orchestration_ledger: dict,
    completion_proofs: list[dict]
) -> dict:
    node_count = len(orchestration_nodes)
    pass_count = orchestration_ledger["dry_run_pass_count"]
    proof_count = len(completion_proofs)
    
    ready = (
        node_count >= 1
        and conflict_detector["conflict_count"] == 0
        and pass_count == node_count
        and proof_count == node_count
    )
    
    return {
        "orchestration_readiness_summary_version": "1.6.0",
        "orchestration_status": "ORCHESTRATION_SANDBOX_ONLY",
        "node_count": node_count,
        "dry_run_pass_count": pass_count,
        "blocked_count": orchestration_ledger["blocked_count"],
        "conflict_count": conflict_detector["conflict_count"],
        "completion_proof_count": proof_count,
        "ready_for_ui_operator_console_schema": ready,
        "next_layer": "UI / Operator Console Schema",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_ui_operator_console_readiness_bridge(
    result: dict,
    orchestration_nodes: list[dict],
    readiness_summary: dict
) -> dict:
    return {
        "ui_operator_console_readiness_bridge_version": "1.6.0",
        "current_layer": "Multi-Agent Orchestration Sandbox",
        "next_layer": "UI / Operator Console Schema",
        "ready_for_ui_operator_console_schema": readiness_summary["ready_for_ui_operator_console_schema"],
        "orchestration_node_count": len(orchestration_nodes),
        "required_next_capabilities": [
            "operator console screen schema",
            "runtime status panel schema",
            "approval queue panel schema",
            "work order panel schema",
            "worker registry panel schema",
            "department routing panel schema",
            "orchestration sandbox panel schema",
            "human control surface schema",
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
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_multi_agent_orchestration_bundle(result: dict) -> dict:
    schema = create_orchestration_topology_schema()
    nodes = create_orchestration_nodes_from_department_routing(result)
    coord_map = create_multi_worker_coordination_map(nodes)
    handoff_sim = create_task_handoff_simulation(nodes, coord_map)
    dep_graph = create_inter_worker_dependency_graph(nodes)
    conflicts = detect_orchestration_conflicts(nodes, coord_map, dep_graph)
    dr_results = dry_run_multi_agent_orchestration(nodes, conflicts)
    ledger = create_orchestration_ledger(nodes, dr_results)
    proofs = create_orchestration_completion_proofs(nodes, dr_results)
    summary = create_orchestration_readiness_summary(nodes, conflicts, ledger, proofs)
    bridge = create_ui_operator_console_readiness_bridge(result, nodes, summary)
    
    return {
        "multi_agent_orchestration_bundle_version": "1.6.0",
        "orchestration_status": MULTI_AGENT_ORCHESTRATION_STATUS,
        "orchestration_topology_schema": schema,
        "orchestration_nodes": nodes,
        "multi_worker_coordination_map": coord_map,
        "task_handoff_simulation": handoff_sim,
        "inter_worker_dependency_graph": dep_graph,
        "orchestration_conflict_detector": conflicts,
        "orchestration_dry_run_results": dr_results,
        "orchestration_ledger": ledger,
        "orchestration_completion_proofs": proofs,
        "orchestration_readiness_summary": summary,
        "ui_operator_console_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False
    }
