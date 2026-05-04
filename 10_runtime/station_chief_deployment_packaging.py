import json
import hashlib
import re
from pathlib import Path

DEPLOYMENT_PACKAGING_MODULE_VERSION = "3.3.0"
DEPLOYMENT_PACKAGING_STATUS = "PACKAGING_BRIDGE_ONLY"
DEPLOYMENT_PACKAGING_PHASE = "Deployment / Portfolio Packaging Bridge"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_packaging_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "deployment-packaging"

def generate_deployment_packaging_id(command: str, label: str, runtime_version: str = "3.3.0") -> str:
    normalized_label = normalize_packaging_label(label)
    hash_input = f"{runtime_version}:{command}:{label}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"deployment-packaging-v3-3-{normalized_label}-{hash_chars}"

def make_deployment_artifact_schema() -> dict:
    return {
        "deployment_artifact_schema_version": "3.3.0",
        "schema_status": "PACKAGING_BRIDGE_ONLY",
        "required_sections": [
            "portfolio_packaging_manifest",
            "runtime_export_bundle",
            "release_notes",
            "deployment_readiness_proof",
            "deployment_safety_contract",
            "packaging_audit_bundle",
            "portfolio_handoff_summary",
            "first_controlled_worker_execution_readiness_bridge"
        ],
        "allowed_packaging_modes": [
            "read_only_packaging_review",
            "artifact_export_preview",
            "portfolio_handoff_preview",
            "deployment_readiness_review"
        ],
        "blocked_packaging_modes": [
            "live_deployment_execution",
            "external_hosting_interface_mutation",
            "external_service_update",
            "production_publish",
            "direct_push",
            "uncontrolled_repo_edit",
            "baseline_file_patch",
            "Devinization_overlay_patch",
            "generated_artifact_mutation",
            "unconfirmed_deployment"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no external hosting interface mutation",
            "no live deployment action",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no protected path writes",
            "no shell command execution",
            "no package installation",
            "deployment packaging contracts do not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "repo_patch_applied": False,
        "execution_authorized": False
    }

def create_portfolio_packaging_manifest(result: dict) -> dict:
    return {
        "portfolio_packaging_manifest_version": "3.3.0",
        "manifest_status": "PORTFOLIO_HANDOFF_PREVIEW_ONLY",
        "project_name": "Agent Command Center",
        "project_owner": "Devin O’Rourke",
        "runtime_version": result.get("station_chief_runtime_version"),
        "runtime_status": result.get("runtime_status"),
        "release_status": result.get("release_status"),
        "portfolio_summary": "Station Chief Runtime is a layered, safety-gated command runtime for the Agent Command Center architecture. This packaging manifest is a portfolio handoff preview only.",
        "packaging_sections": [
            "runtime overview",
            "locked baseline preservation",
            "Devinization overlay stack",
            "controlled execution doctrine",
            "work order executor",
            "worker hiring registry preview",
            "department routing preview",
            "multi_agent_orchestration sandbox",
            "operator console schema",
            "GitHub patch hardening",
            "deployment packaging bridge",
            "next controlled execution milestone"
        ],
        "artifact_groups": [
            "runtime JSON artifacts",
            "validator reports",
            "safety contracts",
            "readiness bridges",
            "review manifests",
            "portfolio summary records"
        ],
        "presentation_ready_claims": [
            "deterministic runtime skeleton exists",
            "layered safety contracts exist",
            "dry-run artifact writing exists",
            "review-only packaging bridge exists",
            "baseline preservation is enforced by validators"
        ],
        "non_claims": [
            "not a live production deployment",
            "not full workforce animation",
            "not real worker hiring",
            "not live external API execution",
            "not live GitHub patch mutation",
            "not live hosting deployment"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def create_runtime_export_bundle(result: dict) -> dict:
    available_layers = {
        "controlled_execution": result.get("controlled_execution_bundle") is not None,
        "work_order_executor": result.get("work_order_executor_bundle") is not None,
        "worker_hiring_registry": result.get("worker_hiring_registry_bundle") is not None,
        "department_routing": result.get("department_routing_bundle") is not None,
        "multi_agent_orchestration": result.get("multi_agent_orchestration_bundle") is not None,
        "operator_console": result.get("operator_console_bundle") is not None,
        "github_patch_hardening": result.get("github_patch_hardening_bundle") is not None,
        "deployment_packaging": True
    }
    
    artifact_keys = list(result.keys())
    
    return {
        "runtime_export_bundle_version": "3.3.0",
        "export_status": "EXPORT_PREVIEW_ONLY",
        "runtime_version": result.get("station_chief_runtime_version"),
        "runtime_status": result.get("runtime_status"),
        "available_layers": available_layers,
        "artifact_keys_present": artifact_keys,
        "recommended_export_files": [
            "full_result.json",
            "manifest.json",
            "stable_release_manifest.json",
            "release_notes.json",
            "portfolio_packaging_manifest.json",
            "deployment_readiness_proof.json",
            "deployment_safety_contract.json"
        ],
        "export_digest": sha256_digest(available_layers),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def create_release_notes(result: dict) -> dict:
    return {
        "release_notes_version": "3.3.0",
        "release_title": "Station Chief Runtime v2.5.0 — Deployment / Portfolio Packaging Bridge",
        "release_status": "PACKAGING_BRIDGE_ONLY",
        "summary": "v2.5.0 packages the Station Chief runtime for review and portfolio handoff without performing deployment or live execution.",
        "new_capabilities": [
            "deployment artifact schema",
            "portfolio packaging manifest",
            "runtime export bundle",
            "release notes generator",
            "deployment readiness proof",
            "deployment safety contract",
            "packaging audit bundle",
            "portfolio handoff summary",
            "first controlled worker execution readiness bridge"
        ],
        "preserved_capabilities": [
            "GitHub patch hardening",
            "UI / operator console schema",
            "multi-agent orchestration sandbox",
            "department routing preview",
            "worker hiring registry",
            "work order executor",
            "controlled execution profiles",
            "stable release lock"
        ],
        "safety_boundaries": [
            "no live deployment",
            "no external hosting interface calls",
            "no external service mutation",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no worker animation",
            "no live orchestration",
            "no uncontrolled repo edits"
        ],
        "known_limitations": [
            "no live deployment adapter",
            "no hosting integration",
            "no production UI",
            "no live worker execution",
            "no real agent hiring",
            "no external API connection"
        ],
        "next_recommended_build": "v2.0 first controlled worker-agent execution release",
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def make_deployment_safety_contract(result: dict) -> dict:
    return {
        "deployment_safety_contract_version": "3.3.0",
        "contract_status": "DEPLOYMENT_BLOCKED_BY_DEFAULT",
        "blocked_actions": [
            "deploy_to_external_platform_001",
            "deploy_to_external_platform_002",
            "deploy_to_external_platform_003",
            "deploy_to_external_platform_004",
            "deploy_to_external_platform_005",
            "deploy_to_external_platform_006",
            "deploy_to_external_platform_007",
            "deploy_to_external_platform_008",
            "mutate_external_hosting_config",
            "publish_production_runtime",
            "expose_runtime_publicly",
            "execute_live_worker_agents"
        ],
        "required_future_approvals": [
            "explicit deployment target approval",
            "explicit artifact list approval",
            "explicit environment variable approval",
            "explicit secrets review",
            "explicit rollback plan approval",
            "explicit production approval"
        ],
        "required_future_evidence": [
            "validator pass report",
            "scope check report",
            "protected path report",
            "release lock report",
            "deployment preview manifest",
            "rollback preview",
            "human approval record"
        ],
        "deployment_allowed_now": False,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def make_deployment_readiness_proof(
    result: dict,
    portfolio_manifest: dict,
    runtime_export_bundle: dict,
    deployment_safety_contract: dict
) -> dict:
    checks = {
        "portfolio_manifest_available": portfolio_manifest is not None,
        "runtime_export_bundle_available": runtime_export_bundle is not None,
        "deployment_safety_contract_available": deployment_safety_contract is not None,
        "deployment_blocked_by_default": deployment_safety_contract.get("deployment_allowed_now") is False,
        "no_hosting_api_called": not result.get("hosting_api_called", False),
        "no_external_actions_taken": not result.get("external_actions_taken", False),
        "no_execution_authorized": not result.get("execution_authorized", False)
    }
    
    ready = all(checks.values())
    
    return {
        "deployment_readiness_proof_version": "3.3.0",
        "proof_status": "READY_FOR_REVIEW_PACKAGING" if ready else "BLOCKED",
        "readiness_checks": checks,
        "proof_digest": sha256_digest(checks),
        "deployment_allowed_now": False,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def create_portfolio_handoff_summary(
    result: dict,
    portfolio_manifest: dict,
    release_notes: dict,
    deployment_readiness_proof: dict
) -> dict:
    return {
        "portfolio_handoff_summary_version": "3.3.0",
        "handoff_status": "READY_FOR_PORTFOLIO_REVIEW",
        "project_name": "Agent Command Center",
        "project_owner": "Devin O’Rourke",
        "headline": "Station Chief Runtime: safety-gated command runtime for a large-scale agent command architecture.",
        "short_description": "A deterministic, validator-backed runtime skeleton that turns one command into structured review artifacts, dry-run execution plans, worker registry previews, routing previews, orchestration sandbox records, operator console schemas, patch hardening contracts, and deployment packaging records.",
        "technical_summary": "v2.5.0 is a review-only packaging bridge that prepares the runtime for portfolio presentation without deploying, exposing, or executing live systems.",
        "safe_demo_positioning": [
            "demonstrate command classification",
            "demonstrate dry-run artifacts",
            "demonstrate work order executor preview",
            "demonstrate worker registry preview",
            "demonstrate department routing preview",
            "demonstrate orchestration sandbox",
            "demonstrate operator console schemas",
            "demonstrate patch hardening contracts",
            "demonstrate deployment packaging artifacts",
            "do not claim live autonomous production execution"
        ],
        "reviewer_notes": [
            "artifacts are deterministic",
            "validators enforce scope and safety",
            "baseline remains locked",
            "deployment is intentionally blocked",
            "next milestone is first controlled worker-agent execution release"
        ],
        "handoff_digest": sha256_digest(release_notes),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def create_packaging_audit_bundle(
    result: dict,
    portfolio_manifest: dict,
    runtime_export_bundle: dict,
    release_notes: dict,
    deployment_safety_contract: dict,
    deployment_readiness_proof: dict,
    portfolio_handoff_summary: dict
) -> dict:
    return {
        "packaging_audit_bundle_version": "3.3.0",
        "audit_status": "PACKAGING_REVIEW_READY",
        "portfolio_manifest_digest": sha256_digest(portfolio_manifest),
        "runtime_export_bundle_digest": sha256_digest(runtime_export_bundle),
        "release_notes_digest": sha256_digest(release_notes),
        "deployment_safety_contract_digest": sha256_digest(deployment_safety_contract),
        "deployment_readiness_proof_digest": sha256_digest(deployment_readiness_proof),
        "portfolio_handoff_summary_digest": sha256_digest(portfolio_handoff_summary),
        "combined_packaging_digest": sha256_digest({
            "manifest": portfolio_manifest,
            "notes": release_notes,
            "proof": deployment_readiness_proof
        }),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def create_first_controlled_worker_execution_readiness_bridge(
    result: dict,
    packaging_audit_bundle: dict,
    deployment_readiness_proof: dict
) -> dict:
    ready = (
        packaging_audit_bundle["audit_status"] == "PACKAGING_REVIEW_READY"
        and deployment_readiness_proof["proof_status"] == "READY_FOR_REVIEW_PACKAGING"
        and not result.get("deployment_performed", False)
        and not result.get("hosting_api_called", False)
        and not result.get("execution_authorized", False)
    )
    
    return {
        "first_controlled_worker_execution_readiness_bridge_version": "3.3.0",
        "current_layer": "Deployment / Portfolio Packaging Bridge",
        "next_layer": "First Controlled Worker-Agent Execution Release",
        "ready_for_first_controlled_worker_execution_release": ready,
        "required_next_capabilities": [
            "first live worker execution gate",
            "single-worker sandbox execution contract",
            "explicit tool permission binding",
            "human approval token for first worker run",
            "rollback/abort contract",
            "live execution telemetry stub",
            "post-run audit proof",
            "no broad workforce animation"
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
        "deployment_performed": False,
        "hosting_api_called": False,
        "execution_authorized": False
    }

def make_deployment_packaging_bundle(result: dict) -> dict:
    schema = make_deployment_artifact_schema()
    portfolio_manifest = create_portfolio_packaging_manifest(result)
    runtime_export_bundle = create_runtime_export_bundle(result)
    release_notes = create_release_notes(result)
    deployment_safety_contract = make_deployment_safety_contract(result)
    deployment_readiness_proof = make_deployment_readiness_proof(
        result, portfolio_manifest, runtime_export_bundle, deployment_safety_contract
    )
    portfolio_summary = create_portfolio_handoff_summary(
        result, portfolio_manifest, release_notes, deployment_readiness_proof
    )
    audit_bundle = create_packaging_audit_bundle(
        result, portfolio_manifest, runtime_export_bundle, release_notes, 
        deployment_safety_contract, deployment_readiness_proof, portfolio_summary
    )
    bridge = create_first_controlled_worker_execution_readiness_bridge(
        result, audit_bundle, deployment_readiness_proof
    )
    
    return {
        "deployment_packaging_bundle_version": "3.3.0",
        "deployment_packaging_status": "PACKAGING_BRIDGE_ONLY",
        "deployment_artifact_schema": schema,
        "portfolio_packaging_manifest": portfolio_manifest,
        "runtime_export_bundle": runtime_export_bundle,
        "release_notes": release_notes,
        "deployment_safety_contract": deployment_safety_contract,
        "deployment_readiness_proof": deployment_readiness_proof,
        "portfolio_handoff_summary": portfolio_summary,
        "packaging_audit_bundle": audit_bundle,
        "first_controlled_worker_execution_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "repo_patch_applied": False,
        "execution_authorized": False
    }
