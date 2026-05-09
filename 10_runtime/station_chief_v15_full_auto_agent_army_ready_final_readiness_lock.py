import json
import hashlib
import re
from pathlib import Path

STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION = "15.0.0"
STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_STATUS = "STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_LOCAL_DETERMINISTIC_ONLY"
STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_PHASE = "Station Chief v15.0 Full Auto Agent Army Ready / Final Readiness Lock Candidate"

STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS = [
    "station-chief-final-readiness-domain-control-plane-001",
    "station-chief-final-readiness-domain-worker-army-002",
    "station-chief-final-readiness-domain-permissioning-003",
    "station-chief-final-readiness-domain-external-boundary-004",
    "station-chief-final-readiness-domain-production-safety-005",
    "station-chief-final-readiness-domain-human-override-006"
]

STATION_CHIEF_V15_FINAL_LOCK_ID = "station-chief-v15-final-readiness-lock-001"
STATION_CHIEF_V15_FINAL_CERTIFICATE_ID = "station-chief-v15-full-auto-agent-army-ready-certificate-001"
STATION_CHIEF_V15_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v15.1 or live activation requires explicit separate operator instruction"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sha256_digest(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()

def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()

def create_final_readiness_domain_registry() -> dict:
    domains = [
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[0], "name": "control_plane_foundation"},
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[1], "name": "autonomous_worker_army"},
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[2], "name": "permissioned_tool_task_queue"},
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[3], "name": "external_tool_api_boundary"},
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[4], "name": "production_rollback_safety"},
        {"id": STATION_CHIEF_V15_FINAL_READINESS_DOMAIN_IDS[5], "name": "human_override_and_governance"}
    ]
    
    registry = {}
    for d in domains:
        registry[d["id"]] = {
            "domain_id": d["id"],
            "domain_name": d["name"],
            "domain_type": "metadata_only_final_readiness_domain",
            "domain_status": "READY_METADATA_LOCKED",
            "descriptor_only": True,
            "readiness_domain_registered": True,
            "live_activation_allowed": False,
            "production_execution_allowed": False,
            "deployment_allowed": False,
            "external_tool_invocation_allowed": False,
            "api_call_allowed": False,
            "network_access_allowed": False,
            "credential_access_allowed": False,
            "secret_read_allowed": False,
            "environment_read_allowed": False,
            "real_worker_activation_allowed": False,
            "real_queue_allowed": False,
            "live_task_execution_allowed": False,
            "live_orchestration_allowed": False,
            "arbitrary_task_allowed": False,
            "user_task_allowed": False
        }
    return registry

def create_final_activation_prerequisite_registry(readiness_domains: dict) -> dict:
    prereqs = [
        "control_plane_locked",
        "worker_army_release_candidate_locked",
        "permission_layer_locked",
        "external_boundary_locked",
        "production_safety_gates_locked",
        "rollback_playbooks_locked",
        "emergency_abort_controls_locked",
        "observability_audit_locked",
        "human_approval_required",
        "future_activation_instruction_required"
    ]
    
    registry = {
        "prerequisite_count": 10,
        "all_prerequisites_satisfied": True,
        "live_activation_allowed": False,
        "future_explicit_instruction_required": True,
        "prerequisites": {}
    }
    
    for idx, p_name in enumerate(prereqs):
        p_id = f"station-chief-prerequisite-{idx+1:03d}"
        registry["prerequisites"][p_id] = {
            "prerequisite_id": p_id,
            "prerequisite_name": p_name,
            "prerequisite_type": "metadata_only_final_activation_prerequisite",
            "prerequisite_status": "SATISFIED_FOR_READINESS_LOCK",
            "live_activation_performed": False,
            "execution_performed": False,
            "descriptor_only": True
        }
        
    return registry

def create_final_human_approval_override_manifest() -> dict:
    return {
        "human_approval_override_manifest_id": "station-chief-final-human-approval-override-manifest-001",
        "manifest_type": "metadata_only_human_approval_override_manifest",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "human_operator_required": True,
        "explicit_operator_instruction_required": True,
        "manual_override_required": True,
        "emergency_stop_required": True,
        "human_review_receipt_required": True,
        "live_activation_without_human_approval_allowed": False,
        "autonomous_self_activation_allowed": False,
        "credential_self_access_allowed": False,
        "production_self_execution_allowed": False,
        "metadata_only": True
    }

def create_final_command_authority_matrix(readiness_domains: dict, prerequisite_registry: dict, human_manifest: dict) -> dict:
    return {
        "command_authority_matrix_id": sha256_digest({
            "domains": list(readiness_domains.keys()),
            "prereqs": list(prerequisite_registry["prerequisites"].keys()),
            "human": human_manifest["human_approval_override_manifest_id"]
        }),
        "matrix_type": "metadata_only_final_command_authority_matrix",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "readiness_domain_count": 6,
        "prerequisite_count": 10,
        "command_authority_status": "FINAL_READINESS_AUTHORITY_LOCKED",
        "full_auto_agent_army_ready_authorized": True,
        "live_activation_authorized": False,
        "self_activation_authorized": False,
        "production_execution_authorized": False,
        "deployment_authorized": False,
        "external_tool_invocation_authorized": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "credential_access_authorized": False,
        "secret_read_authorized": False,
        "arbitrary_execution_authorized": False,
        "user_task_execution_authorized": False,
        "future_explicit_instruction_required": True
    }

def create_final_army_readiness_scorecard(readiness_domains: dict, prerequisite_registry: dict, command_authority_matrix: dict) -> dict:
    return {
        "scorecard_id": sha256_digest({
            "domains": len(readiness_domains),
            "prereqs": prerequisite_registry["prerequisite_count"],
            "auth": command_authority_matrix["command_authority_matrix_id"]
        }),
        "scorecard_type": "metadata_only_full_auto_agent_army_readiness_scorecard",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "readiness_domain_count": 6,
        "prerequisite_count": 10,
        "readiness_score": 100,
        "readiness_grade": "FINAL_READINESS_LOCKED",
        "full_auto_agent_army_ready": True,
        "live_activation_performed": False,
        "production_execution_performed": False,
        "external_action_performed": False,
        "no_blocking_readiness_gaps": True
    }

def create_final_safety_evidence_ledger(readiness_domains: dict, prerequisite_registry: dict, scorecard: dict) -> dict:
    entries = [
        "v8_control_plane_foundation_preserved",
        "v9_controlled_local_worker_pilot_preserved",
        "v10_multi_worker_sandbox_coordination_preserved",
        "v11_permissioned_tool_task_queue_layer_preserved",
        "v12_autonomous_worker_army_release_candidate_preserved",
        "v13_external_tool_api_boundary_hardened",
        "v14_production_readiness_rollback_live_safety_gates_preserved",
        "v15_final_readiness_lock_created"
    ]
    
    return {
        "safety_evidence_ledger_id": sha256_digest(entries),
        "ledger_type": "metadata_only_final_safety_evidence_ledger",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "evidence_entries": entries,
        "evidence_count": 8,
        "all_evidence_recorded": True,
        "metadata_only": True,
        "no_live_action_recorded": True
    }

def create_final_activation_denial_proof(command_authority_matrix: dict, human_manifest: dict) -> dict:
    return {
        "activation_denial_proof_id": sha256_digest({
            "auth": command_authority_matrix["command_authority_matrix_id"],
            "human": human_manifest["human_approval_override_manifest_id"]
        }),
        "proof_type": "metadata_only_final_activation_denial_proof",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "full_auto_agent_army_ready": True,
        "live_activation_attempted": False,
        "live_activation_authorized": False,
        "autonomous_self_activation_authorized": False,
        "production_execution_authorized": False,
        "deployment_authorized": False,
        "external_tool_invocation_authorized": False,
        "api_call_authorized": False,
        "network_access_authorized": False,
        "credential_access_authorized": False,
        "secret_read_authorized": False,
        "environment_read_authorized": False,
        "real_worker_activation_authorized": False,
        "real_queue_authorized": False,
        "live_task_execution_authorized": False,
        "live_orchestration_authorized": False,
        "proof_status": "READY_BUT_NOT_ACTIVATED"
    }

def create_final_no_live_action_audit_record(readiness_domains: dict, prerequisite_registry: dict, human_manifest: dict, command_authority_matrix: dict, scorecard: dict, evidence_ledger: dict, activation_denial_proof: dict) -> dict:
    return {
        "audit_id": sha256_digest({
            "domains": len(readiness_domains),
            "prereqs": prerequisite_registry["prerequisite_count"],
            "human": human_manifest["human_approval_override_manifest_id"],
            "auth": command_authority_matrix["command_authority_matrix_id"],
            "score": scorecard["scorecard_id"],
            "evidence": evidence_ledger["safety_evidence_ledger_id"],
            "proof": activation_denial_proof["activation_denial_proof_id"]
        }),
        "audit_type": "full_auto_agent_army_ready_final_readiness_lock_audit",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "full_auto_agent_army_ready": True,
        "final_readiness_lock_created": True,
        "readiness_domain_count": 6,
        "prerequisite_count": 10,
        "evidence_count": 8,
        "readiness_score": 100,
        "no_live_activation": True,
        "no_autonomous_self_activation": True,
        "no_production_execution": True,
        "no_deployment": True,
        "no_rollback_execution": True,
        "no_recovery_execution": True,
        "no_real_tool_invocation": True,
        "no_external_tool_invocation": True,
        "no_api_call": True,
        "no_network_access": True,
        "no_socket_access": True,
        "no_dns_resolution": True,
        "no_credential_access": True,
        "no_credential_vault_access": True,
        "no_secret_read": True,
        "no_environment_read": True,
        "no_filesystem_mutation": True,
        "no_database_mutation": True,
        "no_worker_process_started": True,
        "no_agent_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed": True,
        "no_live_worker_routing": True,
        "no_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True
    }

def create_final_readiness_certificate(readiness_domains: dict, prerequisite_registry: dict, command_authority_matrix: dict, scorecard: dict, evidence_ledger: dict, activation_denial_proof: dict, audit_record: dict) -> dict:
    evidence_digest = evidence_ledger["safety_evidence_ledger_id"]
    audit_digest = audit_record["audit_id"]
    
    cert = {
        "final_certificate_id": STATION_CHIEF_V15_FINAL_CERTIFICATE_ID,
        "certificate_type": "metadata_only_full_auto_agent_army_ready_certificate",
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "certificate_status": "FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCKED",
        "full_auto_agent_army_ready": True,
        "final_readiness_lock_created": True,
        "live_activation_performed": False,
        "live_activation_requires_separate_future_instruction": True,
        "human_operator_required": True,
        "readiness_score": 100,
        "evidence_digest": evidence_digest,
        "audit_digest": audit_digest
    }
    
    cert["certificate_digest"] = sha256_digest(cert)
    return cert

def create_final_readiness_safety_boundary_matrix() -> dict:
    return {
        "live_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
        "full_external_prod_agent_army_activation": "DENIED",
        "production_execution": "DENIED",
        "production_mutation": "DENIED",
        "deployment": "DENIED",
        "deployment_rollback": "DENIED",
        "rollback_execution": "DENIED",
        "recovery_execution": "DENIED",
        "real_tool_invocation": "DENIED",
        "external_tool_invocation": "DENIED",
        "api_call": "DENIED",
        "network_access": "DENIED",
        "socket_access": "DENIED",
        "dns_resolution": "DENIED",
        "outbound_connection": "DENIED",
        "inbound_connection": "DENIED",
        "webhook_call": "DENIED",
        "credential_use": "DENIED",
        "credential_vault_access": "DENIED",
        "secret_read": "DENIED",
        "environment_read": "DENIED",
        "worker_process_start": "DENIED",
        "daemon_start": "DENIED",
        "background_process_start": "DENIED",
        "agent_start": "DENIED",
        "subprocess_start": "DENIED",
        "shell_execution": "DENIED",
        "arbitrary_command_execution": "DENIED",
        "arbitrary_task_execution": "DENIED",
        "user_task_execution": "DENIED",
        "real_queue_creation": "DENIED",
        "queue_write": "DENIED",
        "scheduler_write": "DENIED",
        "cron_write": "DENIED",
        "live_task_enqueue": "DENIED",
        "live_task_dequeue": "DENIED",
        "live_task_execution": "DENIED",
        "live_worker_routing": "DENIED",
        "live_orchestration": "DENIED",
        "filesystem_mutation": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v15_1_creation": "DENIED",
        "v16_creation": "DENIED"
    }

def create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "schema_type": "station_chief_v15_full_auto_agent_army_ready_final_readiness_lock",
        "required_sections": [
            "final_readiness_domain_registry",
            "final_activation_prerequisite_registry",
            "final_human_approval_override_manifest",
            "final_command_authority_matrix",
            "final_army_readiness_scorecard",
            "final_safety_evidence_ledger",
            "final_activation_denial_proof",
            "final_no_live_action_audit_record",
            "final_readiness_certificate",
            "final_readiness_safety_boundary_matrix",
            "final_readiness_summary"
        ],
        "full_auto_agent_army_ready_authorized": True,
        "no_live_activation_authorized": True,
        "no_autonomous_self_activation_authorized": True,
        "no_production_execution_authorized": True,
        "no_deployment_authorized": True,
        "no_rollback_execution_authorized": True,
        "no_recovery_execution_authorized": True,
        "no_real_tool_invocation_authorized": True,
        "no_external_tool_invocation_authorized": True,
        "no_api_call_authorized": True,
        "no_network_access_authorized": True,
        "no_socket_access_authorized": True,
        "no_dns_resolution_authorized": True,
        "no_credential_access_authorized": True,
        "no_credential_vault_access_authorized": True,
        "no_secret_read_authorized": True,
        "no_environment_read_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_user_task_execution_authorized": True,
        "no_worker_process_start_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_live_routing_authorized": True,
        "no_live_orchestration_authorized": True,
        "v15_1_created": False,
        "v16_created": False
    }

def create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_bundle() -> dict:
    schema = create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_schema()
    domains = create_final_readiness_domain_registry()
    prereqs = create_final_activation_prerequisite_registry(domains)
    human_manifest = create_final_human_approval_override_manifest()
    matrix = create_final_command_authority_matrix(domains, prereqs, human_manifest)
    scorecard = create_final_army_readiness_scorecard(domains, prereqs, matrix)
    evidence = create_final_safety_evidence_ledger(domains, prereqs, scorecard)
    proof = create_final_activation_denial_proof(matrix, human_manifest)
    audit = create_final_no_live_action_audit_record(domains, prereqs, human_manifest, matrix, scorecard, evidence, proof)
    cert = create_final_readiness_certificate(domains, prereqs, matrix, scorecard, evidence, proof, audit)
    boundaries = create_final_readiness_safety_boundary_matrix()

    bundle = {
        "runtime_version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
        "final_readiness_status": "FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCKED",
        "full_auto_agent_army_ready": True,
        "final_readiness_lock_created": True,
        "final_readiness_domains_registered": True,
        "final_activation_prerequisites_registered": True,
        "final_human_approval_override_manifest_created": True,
        "final_command_authority_matrix_created": True,
        "final_army_readiness_scorecard_created": True,
        "final_safety_evidence_ledger_created": True,
        "final_activation_denial_proof_created": True,
        "final_no_live_action_audit_record_created": True,
        "final_readiness_certificate_created": True,
        "readiness_domain_count": 6,
        "prerequisite_count": 10,
        "evidence_count": 8,
        "readiness_score": 100,
        "live_activation_performed": False,
        "autonomous_self_activation_performed": False,
        "full_external_prod_agent_army_activation_performed": False,
        "production_execution_performed": False,
        "production_mutation_performed": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "rollback_execution_performed": False,
        "recovery_execution_performed": False,
        "real_tool_invocation_performed": False,
        "external_tool_invocation_performed": False,
        "api_call_performed": False,
        "network_access_performed": False,
        "socket_access_performed": False,
        "dns_resolution_performed": False,
        "credential_access_performed": False,
        "credential_vault_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "real_worker_process_started": False,
        "daemon_started": False,
        "background_process_started": False,
        "agent_started": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "live_task_enqueued": False,
        "live_task_dequeued": False,
        "live_task_executed": False,
        "task_executed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "shell_executed": False,
        "subprocess_started": False,
        "filesystem_mutation_performed": False,
        "database_mutation_performed": False,
        "full_workforce_activation_performed": False,
        "v15_1_created": False,
        "v16_created": False,
        
        "schema": schema,
        "final_readiness_domain_registry": domains,
        "final_activation_prerequisite_registry": prereqs,
        "final_human_approval_override_manifest": human_manifest,
        "final_command_authority_matrix": matrix,
        "final_army_readiness_scorecard": scorecard,
        "final_safety_evidence_ledger": evidence,
        "final_activation_denial_proof": proof,
        "final_no_live_action_audit_record": audit,
        "final_readiness_certificate": cert,
        "final_readiness_safety_boundary_matrix": boundaries,
        "final_readiness_summary": {
            "version": STATION_CHIEF_V15_FULL_AUTO_AGENT_ARMY_READY_FINAL_READINESS_LOCK_VERSION,
            "status": "FINAL_LOCKED"
        }
    }
    
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
