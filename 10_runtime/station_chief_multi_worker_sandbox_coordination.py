#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re

MULTI_WORKER_SANDBOX_COORDINATION_MODULE_VERSION = "3.4.0"
MULTI_WORKER_SANDBOX_COORDINATION_STATUS = "MULTI_WORKER_SANDBOX_COORDINATION_PREVIEW_ONLY"
MULTI_WORKER_SANDBOX_COORDINATION_PHASE = "Multi-Worker Sandbox Coordination"
MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL_TOKEN = "YES_I_APPROVE_MULTI_WORKER_SANDBOX_COORDINATION"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = canonical_json(data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_coordination_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "multi-worker-sandbox-coordination"


def generate_multi_worker_coordination_id(command: str, roster_label: str, runtime_version: str = "3.4.0") -> str:
    normalized_roster_label = normalize_coordination_label(roster_label)
    digest = hashlib.sha256(f"{runtime_version}:{command}:{roster_label}".encode("utf-8")).hexdigest()
    return f"multi-worker-v3-4-{normalized_roster_label}-{digest[:12]}"


def create_multi_worker_sandbox_coordination_schema() -> dict:
    return {
        "multi_worker_sandbox_coordination_schema_version": "3.4.0",
        "schema_status": MULTI_WORKER_SANDBOX_COORDINATION_STATUS,
        "required_sections": [
            "multi_worker_coordination_approval_gate",
            "sandbox_worker_roster",
            "worker_coordination_graph",
            "inter_worker_handoff_contract",
            "multi_worker_dry_run_ledger",
            "coordination_conflict_detector",
            "coordination_abort_contract",
            "coordination_quarantine_contract",
            "coordination_audit_proof",
            "coordination_readiness_summary",
            "controlled_external_tool_adapter_preview_readiness_bridge",
        ],
        "allowed_coordination_modes": [
            "schema_only",
            "local_coordination_preview",
            "approved_multi_worker_sandbox_coordination_records",
            "handoff_contract_preview",
            "conflict_detection_preview",
            "dry_run_ledger_preview",
        ],
        "blocked_coordination_modes": [
            "full_workforce_animation",
            "real_worker_hiring",
            "live_worker_routing",
            "live_orchestration",
            "external_api_coordination",
            "shell_command_coordination",
            "repo_mutating_coordination",
            "deployment_coordination",
            "background_worker_processes",
            "autonomous_retry",
            "production_swarm_execution",
        ],
        "required_confirmation_tokens": [
            MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL_TOKEN,
        ],
        "safety_invariants": [
            "sandbox roster only",
            "deterministic local records only",
            "no real worker hiring",
            "no worker processes started",
            "no full workforce animation",
            "no live worker routing",
            "no live orchestration",
            "no external API calls",
            "no shell commands",
            "no repo mutation",
            "no deployment",
            "coordination records do not authorize broad execution",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "execution_authorized": False,
    }


def create_multi_worker_coordination_approval_gate(
    roster_label: str,
    confirmation_token: str | None = None,
) -> dict:
    token_valid = confirmation_token == MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL_TOKEN
    return {
        "multi_worker_coordination_approval_gate_version": "3.4.0",
        "roster_label": roster_label,
        "gate_status": (
            "APPROVED_FOR_MULTI_WORKER_SANDBOX_COORDINATION_RECORDS"
            if token_valid
            else "BLOCKED_PENDING_MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL"
        ),
        "confirmation_token_required": MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL_TOKEN,
        "confirmation_token_present": confirmation_token is not None,
        "confirmation_token_valid": token_valid,
        "local_coordination_records_authorized": token_valid,
        "real_worker_hiring_authorized": False,
        "worker_process_start_authorized": False,
        "live_worker_routing_authorized": False,
        "live_orchestration_authorized": False,
        "repo_mutation_authorized": False,
        "deployment_authorized": False,
        "broad_worker_activation_authorized": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def _sanitize_role(role: str) -> str:
    return normalize_coordination_label(role)


def create_sandbox_worker_roster(
    command: str,
    audit_gate: dict,
    requested_worker_count: int = 3,
    worker_roles: list[str] | None = None,
) -> dict:
    token_valid = audit_gate.get("confirmation_token_valid") is True
    valid_count = 1 <= requested_worker_count <= 5
    workers: list[dict] = []
    roster_status = "BLOCKED"
    if token_valid and valid_count:
        roles = list(worker_roles or ["planner", "executor-preview", "verifier"])
        roles = roles[:requested_worker_count]
        while len(roles) < requested_worker_count:
            roles.append(f"sandbox-worker-{len(roles) + 1}")
        for index, role in enumerate(roles, start=1):
            normalized_role = _sanitize_role(role)
            workers.append(
                {
                    "worker_id": f"sandbox-worker-v3-4-{index:03d}-{normalized_role}",
                    "worker_index": index,
                    "worker_role": role,
                    "worker_status": "SANDBOX_RECORD_ONLY",
                    "real_worker_hired": False,
                    "process_started": False,
                    "external_actions_taken": False,
                }
            )
        roster_status = "ROSTER_CREATED"
    roster = {
        "sandbox_worker_roster_version": "3.4.0",
        "roster_status": roster_status,
        "command": command,
        "requested_worker_count": requested_worker_count,
        "actual_worker_count": len(workers),
        "workers": workers,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    roster["roster_digest"] = sha256_digest({k: v for k, v in roster.items() if k != "roster_digest"})
    return roster


def create_worker_coordination_graph(
    command: str,
    audit_gate: dict,
    roster: dict,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    roster_created = roster.get("roster_status") == "ROSTER_CREATED"
    nodes: list[dict] = []
    edges: list[dict] = []
    graph_status = "BLOCKED"
    if gate_valid and roster_created:
        workers = roster.get("workers", [])
        for worker in workers:
            nodes.append(
                {
                    "node_id": worker["worker_id"],
                    "node_role": worker["worker_role"],
                    "node_status": "SANDBOX_COORDINATION_RECORD_ONLY",
                }
            )
        for index in range(max(len(nodes) - 1, 0)):
            from_node = nodes[index]
            to_node = nodes[index + 1]
            edges.append(
                {
                    "from_worker_id": from_node["node_id"],
                    "to_worker_id": to_node["node_id"],
                    "handoff_type": "SANDBOX_HANDOFF_CONTRACT_ONLY",
                    "handoff_status": "PLANNED_NOT_EXECUTED",
                }
            )
        graph_status = "GRAPH_CREATED"
    graph = {
        "worker_coordination_graph_version": "3.4.0",
        "graph_status": graph_status,
        "command": command,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    graph["graph_digest"] = sha256_digest({k: v for k, v in graph.items() if k != "graph_digest"})
    return graph


def create_inter_worker_handoff_contract(
    audit_gate: dict,
    coordination_graph: dict,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    graph_created = coordination_graph.get("graph_status") == "GRAPH_CREATED"
    handoff_contracts: list[dict] = []
    contract_status = "BLOCKED"
    if gate_valid and graph_created:
        for index, edge in enumerate(coordination_graph.get("edges", []), start=1):
            handoff_contracts.append(
                {
                    "handoff_id": f"handoff-v2-5-{index:03d}-{sha256_digest(edge)[:12]}",
                    "from_worker_id": edge["from_worker_id"],
                    "to_worker_id": edge["to_worker_id"],
                    "handoff_payload_contract": "DIGESTED_SUMMARY_ONLY",
                    "handoff_status": "CONTRACT_ONLY",
                    "handoff_executed": False,
                }
            )
        contract_status = "CONTRACT_CREATED"
    contract = {
        "inter_worker_handoff_contract_version": "3.4.0",
        "contract_status": contract_status,
        "handoff_contracts": handoff_contracts,
        "handoff_count": len(handoff_contracts),
        "handoffs_executed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    contract["handoff_contract_digest"] = sha256_digest({k: v for k, v in contract.items() if k != "handoff_contract_digest"})
    return contract


def create_multi_worker_dry_run_ledger(
    audit_gate: dict,
    roster: dict,
    coordination_graph: dict,
    handoff_contract: dict,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    created = (
        roster.get("roster_status") == "ROSTER_CREATED"
        and coordination_graph.get("graph_status") == "GRAPH_CREATED"
        and handoff_contract.get("contract_status") == "CONTRACT_CREATED"
    )
    status = "MULTI_WORKER_SANDBOX_DRY_RUN_LEDGER" if gate_valid and created else "BLOCKED"
    ledger = {
        "multi_worker_dry_run_ledger_version": "3.4.0",
        "ledger_status": status,
        "entries": [
            {"entry_type": "sandbox_worker_roster", "entry_digest": sha256_digest(roster)},
            {"entry_type": "worker_coordination_graph", "entry_digest": sha256_digest(coordination_graph)},
            {"entry_type": "inter_worker_handoff_contract", "entry_digest": sha256_digest(handoff_contract)},
        ],
        "real_workers_hired": False,
        "worker_processes_started": False,
        "handoffs_executed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    ledger["ledger_digest"] = sha256_digest({k: v for k, v in ledger.items() if k != "ledger_digest"})
    return ledger


def create_coordination_conflict_detector(
    audit_gate: dict,
    roster: dict,
    coordination_graph: dict,
    requested_shared_resources: list[str] | None = None,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    requested_shared_resources = requested_shared_resources or []
    conflicts: list[dict] = []
    if not gate_valid:
        conflict_status = "BLOCKED"
    else:
        workers = roster.get("workers", []) if roster.get("roster_status") == "ROSTER_CREATED" else []
        worker_ids = [worker.get("worker_id") for worker in workers]
        worker_roles = [worker.get("worker_role") for worker in workers]
        for value, label in ((worker_ids, "worker_id"), (worker_roles, "worker_role"), (requested_shared_resources, "requested_shared_resource")):
            seen = set()
            for item in value:
                if item in seen:
                    conflicts.append(
                        {
                            "conflict_type": f"duplicate_{label}",
                            "conflict_detail": f"Duplicate {label} detected: {item}",
                            "auto_repaired": False,
                        }
                    )
                seen.add(item)
        worker_id_set = set(worker_ids)
        for edge in coordination_graph.get("edges", []) if coordination_graph.get("graph_status") == "GRAPH_CREATED" else []:
            if edge.get("from_worker_id") not in worker_id_set or edge.get("to_worker_id") not in worker_id_set:
                conflicts.append(
                    {
                        "conflict_type": "unknown_worker_reference",
                        "conflict_detail": f"Edge references unknown worker(s): {edge.get('from_worker_id')} -> {edge.get('to_worker_id')}",
                        "auto_repaired": False,
                    }
                )
        conflict_status = "CLEAR" if not conflicts else "CONFLICTS_FOUND"
    detector = {
        "coordination_conflict_detector_version": "3.4.0",
        "conflict_status": conflict_status,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "auto_repair_performed": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    detector["conflict_detector_digest"] = sha256_digest({k: v for k, v in detector.items() if k != "conflict_detector_digest"})
    return detector


def create_coordination_abort_contract(
    audit_gate: dict,
    conflict_detector: dict,
    abort_reason: str | None = None,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    abort_reason = abort_reason or "No abort requested; coordination abort contract prepared."
    abort_contract = {
        "coordination_abort_contract_version": "3.4.0",
        "contract_status": "READY" if gate_valid else "BLOCKED",
        "abort_recommended": conflict_detector.get("conflict_status") == "CONFLICTS_FOUND",
        "abort_reason": abort_reason,
        "abort_steps": [
            "stop creating new sandbox coordination records",
            "preserve roster, graph, handoff, and conflict records",
            "mark coordination as blocked if conflicts remain",
            "require human review",
            "do not retry automatically",
        ],
        "abort_executed": False,
        "processes_terminated": False,
        "worker_processes_started": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    abort_contract["abort_contract_digest"] = sha256_digest({k: v for k, v in abort_contract.items() if k != "abort_contract_digest"})
    return abort_contract


def create_coordination_quarantine_contract(
    audit_gate: dict,
    conflict_detector: dict,
    failure_reason: str | None = None,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    failure_reason = failure_reason or "No failure recorded; quarantine contract prepared."
    quarantine_contract = {
        "coordination_quarantine_contract_version": "3.4.0",
        "quarantine_status": "QUARANTINE_RECORD_READY" if gate_valid else "BLOCKED",
        "quarantine_recommended": conflict_detector.get("conflict_status") == "CONFLICTS_FOUND",
        "failure_reason": failure_reason,
        "quarantine_actions": [
            "mark coordination record as quarantined if conflicts remain",
            "preserve coordination ledger",
            "preserve conflict detector output",
            "block automatic retry",
            "require human review",
        ],
        "files_moved": False,
        "worker_processes_started": False,
        "processes_terminated": False,
        "external_actions_taken": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    quarantine_contract["quarantine_contract_digest"] = sha256_digest({k: v for k, v in quarantine_contract.items() if k != "quarantine_contract_digest"})
    return quarantine_contract


def create_coordination_audit_proof(
    audit_gate: dict,
    roster: dict,
    coordination_graph: dict,
    handoff_contract: dict,
    dry_run_ledger: dict,
    conflict_detector: dict,
    abort_contract: dict,
    quarantine_contract: dict,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    roster_created = roster.get("roster_status") == "ROSTER_CREATED"
    graph_created = coordination_graph.get("graph_status") == "GRAPH_CREATED"
    contract_created = handoff_contract.get("contract_status") == "CONTRACT_CREATED"
    ledger_created = dry_run_ledger.get("ledger_status") == "MULTI_WORKER_SANDBOX_DRY_RUN_LEDGER"
    conflicts_clear = conflict_detector.get("conflict_status") == "CLEAR"
    abort_available = abort_contract.get("contract_status") == "READY"
    quarantine_available = quarantine_contract.get("quarantine_status") == "QUARANTINE_RECORD_READY"
    no_external_actions = not any(
        item.get("external_actions_taken")
        for item in [roster, coordination_graph, handoff_contract, dry_run_ledger, conflict_detector, abort_contract, quarantine_contract]
    )
    no_repo_modifications = not any(
        item.get("repo_files_modified")
        for item in [roster, coordination_graph, handoff_contract, dry_run_ledger, conflict_detector, abort_contract, quarantine_contract]
    )
    no_worker_processes = not any(
        item.get("worker_processes_started") or item.get("real_workers_hired")
        for item in [roster, dry_run_ledger, abort_contract, quarantine_contract]
    )
    no_live_routing = not any(
        item.get("live_worker_routing_performed")
        for item in [coordination_graph, dry_run_ledger]
    )
    no_live_orchestration = not any(
        item.get("live_orchestration_performed")
        for item in [coordination_graph, dry_run_ledger]
    )
    if not gate_valid:
        audit_status = "BLOCKED"
    elif not (roster_created and graph_created and contract_created and ledger_created and abort_available and quarantine_available):
        audit_status = "BLOCKED"
    elif conflicts_clear and no_external_actions and no_repo_modifications and no_worker_processes and no_live_routing and no_live_orchestration:
        audit_status = "PASS"
    else:
        audit_status = "REVIEW_REQUIRED"
    proof = {
        "coordination_audit_proof_version": "3.4.0",
        "audit_status": audit_status,
        "roster_digest": sha256_digest(roster),
        "coordination_graph_digest": sha256_digest(coordination_graph),
        "handoff_contract_digest": sha256_digest(handoff_contract),
        "dry_run_ledger_digest": sha256_digest(dry_run_ledger),
        "conflict_detector_digest": sha256_digest(conflict_detector),
        "abort_contract_digest": sha256_digest(abort_contract),
        "quarantine_contract_digest": sha256_digest(quarantine_contract),
        "combined_coordination_audit_digest": sha256_digest(
            {
                "roster": roster,
                "coordination_graph": coordination_graph,
                "handoff_contract": handoff_contract,
                "dry_run_ledger": dry_run_ledger,
                "conflict_detector": conflict_detector,
                "abort_contract": abort_contract,
                "quarantine_contract": quarantine_contract,
            }
        ),
        "safety_checks": {
            "gate_valid": gate_valid,
            "roster_created": roster_created,
            "graph_created": graph_created,
            "handoff_contract_created": contract_created,
            "dry_run_ledger_created": ledger_created,
            "conflicts_clear": conflicts_clear,
            "abort_contract_available": abort_available,
            "quarantine_contract_available": quarantine_available,
            "no_external_actions": no_external_actions,
            "no_repo_modifications": no_repo_modifications,
            "no_worker_processes": no_worker_processes,
            "no_live_routing": no_live_routing,
            "no_live_orchestration": no_live_orchestration,
        },
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }
    return proof


def create_coordination_readiness_summary(
    audit_gate: dict,
    conflict_detector: dict,
    coordination_audit_proof: dict,
) -> dict:
    gate_valid = audit_gate.get("confirmation_token_valid") is True
    conflict_status = conflict_detector.get("conflict_status")
    audit_status = coordination_audit_proof.get("audit_status")
    if gate_valid and conflict_status == "CLEAR" and audit_status == "PASS":
        readiness_status = "READY_FOR_NEXT_LAYER"
        ready = True
    elif gate_valid and conflict_status == "CONFLICTS_FOUND":
        readiness_status = "REVIEW_REQUIRED"
        ready = False
    else:
        readiness_status = "BLOCKED"
        ready = False
    return {
        "coordination_readiness_summary_version": "3.4.0",
        "readiness_status": readiness_status,
        "ready_for_controlled_external_tool_adapter_preview": ready,
        "gate_status": audit_gate.get("gate_status"),
        "conflict_status": conflict_status,
        "coordination_audit_status": audit_status,
        "next_layer": "Controlled External Tool Adapter Preview",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_controlled_external_tool_adapter_preview_readiness_bridge(
    result: dict,
    readiness_summary: dict,
) -> dict:
    ready = readiness_summary.get("ready_for_controlled_external_tool_adapter_preview") is True
    return {
        "controlled_external_tool_adapter_preview_readiness_bridge_version": "3.4.0",
        "current_layer": "Multi-Worker Sandbox Coordination",
        "next_layer": "Controlled External Tool Adapter Preview",
        "ready_for_controlled_external_tool_adapter_preview": ready,
        "required_next_capabilities": [
            "controlled external tool adapter schema",
            "external tool dry-run adapter registry",
            "per-tool external permission gate",
            "external request preview contract",
            "external response validation schema",
            "external tool abort contract",
            "external tool audit proof",
            "still no external API execution by default",
        ],
        "non_goals_for_next_layer": [
            "no full 47,250 worker activation",
            "no uncontrolled external API execution",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no unbounded tool access",
            "no autonomous deployment",
            "no live production orchestration",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
    }


def create_multi_worker_sandbox_coordination_bundle(
    result: dict,
    command: str | None = None,
    roster_label: str | None = None,
    confirmation_token: str | None = None,
    requested_worker_count: int = 3,
    worker_roles: list[str] | None = None,
    requested_shared_resources: list[str] | None = None,
    abort_reason: str | None = None,
    failure_reason: str | None = None,
) -> dict:
    command = command if command is not None else result.get("command", "")
    roster_label = roster_label or "station-chief-multi-worker-sandbox-roster"
    schema = create_multi_worker_sandbox_coordination_schema()
    gate = create_multi_worker_coordination_approval_gate(roster_label, confirmation_token=confirmation_token)
    roster = create_sandbox_worker_roster(command, gate, requested_worker_count=requested_worker_count, worker_roles=worker_roles)
    graph = create_worker_coordination_graph(command, gate, roster)
    handoff = create_inter_worker_handoff_contract(gate, graph)
    ledger = create_multi_worker_dry_run_ledger(gate, roster, graph, handoff)
    conflict_detector = create_coordination_conflict_detector(gate, roster, graph, requested_shared_resources=requested_shared_resources)
    abort_contract = create_coordination_abort_contract(gate, conflict_detector, abort_reason=abort_reason)
    quarantine_contract = create_coordination_quarantine_contract(gate, conflict_detector, failure_reason=failure_reason)
    audit_proof = create_coordination_audit_proof(gate, roster, graph, handoff, ledger, conflict_detector, abort_contract, quarantine_contract)
    readiness_summary = create_coordination_readiness_summary(gate, conflict_detector, audit_proof)
    bridge = create_controlled_external_tool_adapter_preview_readiness_bridge(result, readiness_summary)
    bundle = {
        "multi_worker_sandbox_coordination_bundle_version": "3.4.0",
        "multi_worker_sandbox_coordination_status": MULTI_WORKER_SANDBOX_COORDINATION_STATUS,
        "command": command,
        "multi_worker_sandbox_coordination_schema": schema,
        "multi_worker_coordination_approval_gate": gate,
        "sandbox_worker_roster": roster,
        "worker_coordination_graph": graph,
        "inter_worker_handoff_contract": handoff,
        "multi_worker_dry_run_ledger": ledger,
        "coordination_conflict_detector": conflict_detector,
        "coordination_abort_contract": abort_contract,
        "coordination_quarantine_contract": quarantine_contract,
        "coordination_audit_proof": audit_proof,
        "coordination_readiness_summary": readiness_summary,
        "controlled_external_tool_adapter_preview_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "handoffs_executed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
    }
    bundle["multi_worker_sandbox_coordination_bundle_digest"] = sha256_digest({k: v for k, v in bundle.items() if k != "multi_worker_sandbox_coordination_bundle_digest"})
    return bundle
